from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from models.application import LoanApplicationCreate, LoanApplication, ApplicationStatusUpdate
from utils.auth import get_current_user
from utils.email import email_service
from database import get_db
from datetime import datetime, date
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
    full_name: str = Form(...),
    date_of_birth: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    home_town: str = Form(...),
    residential_address: str = Form(...),
    place_of_work: str = Form(...),
    employment_status: str = Form(...),
    employment_details: str = Form(...),
    monthly_income: float = Form(...),
    loan_amount: float = Form(...),
    loan_reason: str = Form(...),
    nin: str = Form(...),
    bvn: str = Form(...),
    id_card: UploadFile = File(...),
    passport: UploadFile = File(...),
    db=Depends(get_db)
):
    try:
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
        
        # Create application document
        application_doc = {
            "application_id": application_id,
            "user_id": None,
            "full_name": full_name,
            "date_of_birth": datetime.fromisoformat(date_of_birth),
            "email": email,
            "phone": phone,
            "home_town": home_town,
            "residential_address": residential_address,
            "place_of_work": place_of_work,
            "employment_status": employment_status,
            "employment_details": employment_details,
            "monthly_income": monthly_income,
            "loan_amount": loan_amount,
            "loan_reason": loan_reason,
            "nin": nin,
            "bvn": bvn,
            "id_card_url": id_card_path,
            "passport_url": passport_path,
            "status": "pending_payment",
            "payment_status": "pending",
            "admin_notes": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.applications.insert_one(application_doc)
        
        return {
            "application_id": application_id,
            "status": "pending_payment",
            "message": "Application submitted successfully. Please proceed to payment."
        }
    except Exception as e:
        logger.error(f"Application submission error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit application"
        )

@router.get("/{application_id}", response_model=dict)
async def get_application(application_id: str, db=Depends(get_db)):
    try:
        application = await db.applications.find_one({"application_id": application_id})
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Convert ObjectId to string and datetime to ISO format
        application["_id"] = str(application["_id"])
        application["created_at"] = application["created_at"].isoformat()
        application["updated_at"] = application["updated_at"].isoformat()
        application["date_of_birth"] = application["date_of_birth"].isoformat()
        
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
        
        # Define projection to limit fields returned
        projection = {
            '_id': 1,
            'application_id': 1,
            'full_name': 1,
            'email': 1,
            'phone': 1,
            'loan_amount': 1,
            'status': 1,
            'payment_status': 1,
            'employment_status': 1,
            'monthly_income': 1,
            'created_at': 1,
            'updated_at': 1
        }
        
        applications = await db.applications.find(query, projection).skip(skip).limit(limit).to_list(limit)
        total = await db.applications.count_documents(query)
        
        # Convert ObjectIds and dates
        for app in applications:
            app["_id"] = str(app["_id"])
            app["created_at"] = app["created_at"].isoformat()
            app["updated_at"] = app["updated_at"].isoformat()
        
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
    try:
        application = await db.applications.find_one({"application_id": application_id})
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        # Update application
        update_data = {
            "status": status_update.status,
            "admin_notes": status_update.notes,
            "updated_at": datetime.utcnow()
        }
        
        await db.applications.update_one(
            {"application_id": application_id},
            {"$set": update_data}
        )
        
        # Send email notifications
        if status_update.status == "approved":
            await email_service.send_application_approved(
                application["email"],
                application["full_name"],
                application_id,
                application["loan_amount"]
            )
        elif status_update.status == "rejected":
            await email_service.send_application_rejected(
                application["email"],
                application["full_name"],
                application_id,
                status_update.notes or "Application did not meet requirements"
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
