from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from models.application import (
    LoanApplication, ApplicationStatusUpdate, ApplicationStatus,
    calculate_repayment
)
from utils.auth import get_current_user, get_password_hash
from utils.email import email_service
from database import get_db
from datetime import datetime, timezone, timedelta
from config import get_settings
import os
import aiofiles
import logging
from typing import Optional

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/api/applications", tags=["applications"])

# Ensure upload directory exists
os.makedirs(settings.upload_dir, exist_ok=True)

@router.post("/submit", response_model=dict)
async def submit_application(
    # Personal Information
    full_name: str = Form(...),
    date_of_birth: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    secondary_phone: str = Form(""),
    relative_phone: str = Form(...),
    home_town: str = Form(...),
    flat_house_number: str = Form(...),
    residential_address: str = Form(...),
    # Employment & Income
    place_of_work: str = Form(...),
    employment_status: str = Form(...),
    employment_details: str = Form(...),
    monthly_income: float = Form(...),
    loan_reason: str = Form(...),
    # Bank Account Details
    bank_name: str = Form(...),
    account_name: str = Form(...),
    account_number: str = Form(...),
    # Loan & Repayment Preferences
    loan_amount: float = Form(...),
    repayment_duration: str = Form(...),
    repayment_frequency: str = Form(...),
    # Identity
    nin: str = Form(...),
    bvn: str = Form(...),
    # Account Password
    password: str = Form(...),
    # Files
    id_card: UploadFile = File(...),
    passport: UploadFile = File(...),
    db=Depends(get_db)
):
    """
    Submit a new loan application with account creation.
    Status will be: pending_payment (₦2,500 not paid yet)
    """
    try:
        # Check if email already exists
        existing_user = await db.users.find_one({"email": email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="An account with this email already exists. Please login instead."
            )
        
        # Generate application ID
        app_count = await db.applications.count_documents({})
        application_id = f"LOAN-2025-{app_count + 1:03d}"
        
        # Create directory for application files
        app_upload_dir = os.path.join(settings.upload_dir, application_id)
        os.makedirs(app_upload_dir, exist_ok=True)
        
        # Save files
        id_card_path = os.path.join(app_upload_dir, f"id_card_{id_card.filename}")
        passport_path = os.path.join(app_upload_dir, f"passport_{passport.filename}")
        
        async with aiofiles.open(id_card_path, 'wb') as f:
            content = await id_card.read()
            await f.write(content)
        
        async with aiofiles.open(passport_path, 'wb') as f:
            content = await passport.read()
            await f.write(content)
        
        # Calculate estimated repayment
        repayment_info = calculate_repayment(loan_amount, repayment_duration, repayment_frequency)
        
        # Create user account
        user_doc = {
            "email": email,
            "full_name": full_name,
            "phone": phone,
            "password_hash": get_password_hash(password),
            "role": "user",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        user_result = await db.users.insert_one(user_doc)
        user_id = str(user_result.inserted_id)
        
        # Create application document
        application_doc = {
            "application_id": application_id,
            "user_id": user_id,
            # Personal Information
            "full_name": full_name,
            "date_of_birth": datetime.fromisoformat(date_of_birth),
            "email": email,
            "phone": phone,
            "home_town": home_town,
            "residential_address": residential_address,
            # Employment & Income
            "place_of_work": place_of_work,
            "employment_status": employment_status,
            "employment_details": employment_details,
            "monthly_income": monthly_income,
            "loan_reason": loan_reason,
            # Bank Account Details
            "bank_name": bank_name,
            "account_name": account_name,
            "account_number": account_number,
            # Loan & Repayment
            "loan_amount": loan_amount,
            "approved_amount": None,
            "repayment_duration": repayment_duration,
            "repayment_frequency": repayment_frequency,
            "estimated_repayment": repayment_info["payment_amount"],
            "total_repayment": repayment_info["total_amount"],
            "total_payments": repayment_info["total_payments"],
            # Identity
            "nin": nin,
            "bvn": bvn,
            "id_card_url": id_card_path,
            "passport_url": passport_path,
            # Status
            "status": ApplicationStatus.PENDING_PAYMENT.value,
            "payment_status": "pending",
            "processing_fee_paid": False,
            "processing_fee_paid_at": None,
            "deposit_paid": False,
            "deposit_paid_at": None,
            # Disbursement
            "disbursed": False,
            "disbursed_at": None,
            "disbursement_reference": None,
            # Repayment tracking
            "repayment_schedule": None,
            "total_repaid": 0.0,
            "outstanding_balance": None,
            "next_repayment_date": None,
            "next_repayment_amount": None,
            # Admin
            "admin_notes": None,
            "approved_by": None,
            "approved_at": None,
            # Timestamps
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.applications.insert_one(application_doc)
        
        # Send application received email with payment request
        try:
            await email_service.send_application_received_pending_payment(
                email, full_name, application_id, loan_amount,
                repayment_duration, repayment_frequency, repayment_info["payment_amount"]
            )
        except Exception as email_error:
            logger.error(f"Failed to send application email: {email_error}")
        
        return {
            "application_id": application_id,
            "user_id": user_id,
            "status": ApplicationStatus.PENDING_PAYMENT.value,
            "message": "Application submitted successfully. Please pay ₦2,500 processing fee to proceed.",
            "repayment_info": repayment_info
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Application submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit application: {str(e)}"
        )

@router.get("/user/my-applications", response_model=dict)
async def get_user_applications(token_data=Depends(get_current_user), db=Depends(get_db)):
    """Get all applications for the logged-in user"""
    try:
        user = await db.users.find_one({"email": token_data.email})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        applications = await db.applications.find(
            {"email": token_data.email},
            {"_id": 0}
        ).to_list(100)
        
        # Convert datetime objects
        for app in applications:
            for key, value in app.items():
                if isinstance(value, datetime):
                    app[key] = value.isoformat()
        
        return {"applications": applications}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user applications error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get applications"
        )

@router.get("/{application_id}", response_model=dict)
async def get_application(application_id: str, db=Depends(get_db)):
    try:
        application = await db.applications.find_one(
            {"application_id": application_id},
            {"_id": 0}
        )
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Convert datetime objects to ISO format
        for key, value in application.items():
            if isinstance(value, datetime):
                application[key] = value.isoformat()
        
        return application
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get application error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get application"
        )

@router.get("/", response_model=dict)
async def get_all_applications(
    status_filter: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    db=Depends(get_db)
):
    try:
        query = {}
        if status_filter:
            query["status"] = status_filter
        
        skip = (page - 1) * limit
        
        applications = await db.applications.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
        total = await db.applications.count_documents(query)
        
        # Convert datetime objects
        for app in applications:
            for key, value in app.items():
                if isinstance(value, datetime):
                    app[key] = value.isoformat()
        
        return {
            "applications": applications,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Get applications error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get applications"
        )

@router.put("/{application_id}/status", response_model=dict)
async def update_application_status(
    application_id: str,
    status_update: ApplicationStatusUpdate,
    db=Depends(get_db)
):
    """Update application status (Admin action)"""
    try:
        application = await db.applications.find_one({"application_id": application_id})
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        update_data = {
            "status": status_update.status,
            "admin_notes": status_update.notes,
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Handle approval
        if status_update.status == ApplicationStatus.APPROVED.value:
            update_data["approved_amount"] = status_update.approved_amount or application["loan_amount"]
            update_data["approved_at"] = datetime.now(timezone.utc)
            
            # Send approval email requesting ₦3,000 deposit
            try:
                await email_service.send_loan_approved(
                    application["email"],
                    application["full_name"],
                    application_id,
                    update_data["approved_amount"],
                    application["repayment_duration"],
                    application["repayment_frequency"],
                    application["bank_name"],
                    application["account_number"]
                )
            except Exception as email_error:
                logger.error(f"Failed to send approval email: {email_error}")
        
        # Handle rejection
        elif status_update.status == ApplicationStatus.REJECTED.value:
            try:
                await email_service.send_application_rejected(
                    application["email"],
                    application["full_name"],
                    application_id,
                    status_update.notes or "Application did not meet our requirements"
                )
            except Exception as email_error:
                logger.error(f"Failed to send rejection email: {email_error}")
        
        # Handle disbursement
        elif status_update.status == ApplicationStatus.DISBURSED.value:
            update_data["disbursed"] = True
            update_data["disbursed_at"] = datetime.now(timezone.utc)
            update_data["outstanding_balance"] = application.get("total_repayment", application["loan_amount"])
            
            # Generate repayment schedule
            repayment_schedule = generate_repayment_schedule(
                application["approved_amount"] or application["loan_amount"],
                application["repayment_duration"],
                application["repayment_frequency"]
            )
            update_data["repayment_schedule"] = repayment_schedule
            if repayment_schedule:
                update_data["next_repayment_date"] = repayment_schedule[0]["due_date"]
                update_data["next_repayment_amount"] = repayment_schedule[0]["amount"]
            
            # Send disbursement email
            try:
                await email_service.send_loan_disbursed(
                    application["email"],
                    application["full_name"],
                    application_id,
                    application["approved_amount"] or application["loan_amount"],
                    application["bank_name"],
                    application["account_number"],
                    repayment_schedule
                )
            except Exception as email_error:
                logger.error(f"Failed to send disbursement email: {email_error}")
        
        await db.applications.update_one(
            {"application_id": application_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Application status updated successfully",
            "application_id": application_id,
            "status": status_update.status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update status error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update application status"
        )

@router.post("/{application_id}/record-repayment", response_model=dict)
async def record_repayment(
    application_id: str,
    amount: float,
    db=Depends(get_db)
):
    """Record a repayment for an application"""
    try:
        application = await db.applications.find_one({"application_id": application_id})
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Update repayment tracking
        total_repaid = application.get("total_repaid", 0) + amount
        outstanding = application.get("outstanding_balance", 0) - amount
        
        update_data = {
            "total_repaid": total_repaid,
            "outstanding_balance": max(0, outstanding),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Check if fully repaid
        if outstanding <= 0:
            update_data["status"] = ApplicationStatus.FULLY_REPAID.value
        
        await db.applications.update_one(
            {"application_id": application_id},
            {"$set": update_data}
        )
        
        return {
            "message": "Repayment recorded successfully",
            "total_repaid": total_repaid,
            "outstanding_balance": max(0, outstanding)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Record repayment error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record repayment"
        )

def generate_repayment_schedule(loan_amount: float, duration: str, frequency: str) -> list:
    """Generate repayment schedule based on loan details"""
    from models.application import calculate_repayment
    
    repayment_info = calculate_repayment(loan_amount, duration, frequency)
    schedule = []
    
    # Calculate interval between payments
    if frequency == "weekly":
        interval_days = 7
    elif frequency == "bi_weekly":
        interval_days = 14
    else:  # monthly
        interval_days = 30
    
    start_date = datetime.now(timezone.utc).date()
    
    for i in range(repayment_info["total_payments"]):
        due_date = start_date + timedelta(days=interval_days * (i + 1))
        schedule.append({
            "payment_number": i + 1,
            "due_date": due_date.isoformat(),
            "amount": repayment_info["payment_amount"],
            "status": "pending"
        })
    
    return schedule
