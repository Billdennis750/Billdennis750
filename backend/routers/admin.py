from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from database import get_db
from utils.auth import get_current_user, get_password_hash
from utils.email import email_service
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timezone
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

class SendReminderRequest(BaseModel):
    user_emails: List[str]  # List of email addresses to send reminders to
    reminder_type: str = "all"  # "processing_fee", "deposit", or "all"
    custom_message: Optional[str] = None

class SetupAdminRequest(BaseModel):
    secret_key: str
    email: str
    password: str
    full_name: str

class DeleteUserRequest(BaseModel):
    secret_key: str
    email: str

# Setup endpoint (use a secret key for security)
SETUP_SECRET = "cashflow_setup_2025_secret"

@router.post("/setup-admin", response_model=dict)
async def setup_admin(request: SetupAdminRequest, db=Depends(get_db)):
    """Create admin user (protected by secret key)"""
    if request.secret_key != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    # Check if admin already exists
    existing = await db.users.find_one({"email": request.email})
    if existing:
        # Update password
        await db.users.update_one(
            {"email": request.email},
            {"$set": {
                "password_hash": get_password_hash(request.password),
                "role": "admin",
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        return {"message": "Admin password updated", "email": request.email}
    
    # Create new admin
    admin_data = {
        "email": request.email,
        "password_hash": get_password_hash(request.password),
        "full_name": request.full_name,
        "phone": "08000000000",
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    await db.users.insert_one(admin_data)
    return {"message": "Admin created successfully", "email": request.email}

@router.post("/list-all-users", response_model=dict)
async def list_all_users_setup(request: dict, db=Depends(get_db)):
    """List all users (protected by secret key)"""
    if request.get("secret_key") != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    users = await db.users.find({}, {"_id": 0, "email": 1, "full_name": 1, "role": 1, "created_at": 1}).to_list(100)
    applications = await db.applications.find({}, {"_id": 0, "email": 1, "full_name": 1, "application_id": 1, "status": 1}).to_list(100)
    
    return {
        "users": users,
        "applications": applications,
        "total_users": len(users),
        "total_applications": len(applications)
    }

@router.post("/delete-user-data", response_model=dict)
async def delete_user_data(request: DeleteUserRequest, db=Depends(get_db)):
    """Delete user and all related data (protected by secret key)"""
    if request.secret_key != SETUP_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret key")
    
    email = request.email
    
    # Delete from all collections
    user_result = await db.users.delete_many({"email": email})
    app_result = await db.applications.delete_many({"email": email})
    reset_result = await db.password_resets.delete_many({"email": email})
    txn_result = await db.transactions.delete_many({"email": email})
    
    return {
        "message": f"Deleted all data for {email}",
        "deleted": {
            "users": user_result.deleted_count,
            "applications": app_result.deleted_count,
            "password_resets": reset_result.deleted_count,
            "transactions": txn_result.deleted_count
        }
    }

@router.delete("/users/{email}", response_model=dict)
async def admin_delete_user(email: str, token_data=Depends(get_current_user), db=Depends(get_db)):
    """Delete a user and all their data (Admin only)"""
    try:
        # Verify admin role
        admin = await db.users.find_one({"email": token_data.email})
        if not admin or admin.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Prevent admin from deleting themselves
        if email == token_data.email:
            raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
        
        # Check if user exists
        user = await db.users.find_one({"email": email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prevent deleting other admins
        if user.get("role") == "admin":
            raise HTTPException(status_code=400, detail="Cannot delete admin accounts")
        
        # Delete from all collections
        user_result = await db.users.delete_many({"email": email})
        app_result = await db.applications.delete_many({"email": email})
        reset_result = await db.password_resets.delete_many({"email": email})
        txn_result = await db.transactions.delete_many({"email": email})
        
        logger.info(f"Admin {token_data.email} deleted user {email}")
        
        return {
            "message": f"Successfully deleted user {email} and all associated data",
            "deleted": {
                "user": user_result.deleted_count,
                "applications": app_result.deleted_count,
                "password_resets": reset_result.deleted_count,
                "transactions": txn_result.deleted_count
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete user error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )

@router.get("/users/{email}/details", response_model=dict)
async def get_user_details(email: str, token_data=Depends(get_current_user), db=Depends(get_db)):
    """Get detailed information about a user (Admin only)"""
    try:
        # Verify admin role
        admin = await db.users.find_one({"email": token_data.email})
        if not admin or admin.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        # Get user
        user = await db.users.find_one({"email": email}, {"_id": 0, "password_hash": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's applications
        applications = await db.applications.find(
            {"email": email}, 
            {"_id": 0}
        ).to_list(100)
        
        # Get user's transactions
        transactions = await db.transactions.find(
            {"email": email},
            {"_id": 0}
        ).to_list(100)
        
        return {
            "user": user,
            "applications": applications,
            "transactions": transactions,
            "summary": {
                "total_applications": len(applications),
                "total_transactions": len(transactions)
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get user details error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user details"
        )

@router.get("/stats", response_model=dict)
async def get_admin_stats(db=Depends(get_db)):
    try:
        # Use aggregation pipeline for efficient counting
        pipeline = [
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "pending_review": [
                        {"$match": {"status": "under_review"}},
                        {"$count": "count"}
                    ],
                    "approved": [
                        {"$match": {"status": "approved"}},
                        {"$count": "count"}
                    ],
                    "rejected": [
                        {"$match": {"status": "rejected"}},
                        {"$count": "count"}
                    ],
                    "total_disbursed": [
                        {"$match": {"status": "approved"}},
                        {"$group": {"_id": None, "total": {"$sum": "$loan_amount"}}}
                    ]
                }
            }
        ]
        
        result = await db.applications.aggregate(pipeline).to_list(1)
        stats = result[0] if result else {}
        
        return {
            "total_applications": stats.get("total", [{}])[0].get("count", 0),
            "pending_review": stats.get("pending_review", [{}])[0].get("count", 0),
            "approved": stats.get("approved", [{}])[0].get("count", 0),
            "rejected": stats.get("rejected", [{}])[0].get("count", 0),
            "total_disbursed": stats.get("total_disbursed", [{}])[0].get("total", 0) if stats.get("total_disbursed") else 0
        }
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )

@router.get("/transactions", response_model=dict)
async def get_transactions(db=Depends(get_db)):
    """Get all payment transactions"""
    try:
        transactions = await db.transactions.find({}, {"_id": 0}).to_list(1000)
        
        # Convert datetime objects
        for txn in transactions:
            for key, value in txn.items():
                if isinstance(value, datetime):
                    txn[key] = value.isoformat()
        
        return {"transactions": transactions}
    except Exception as e:
        logger.error(f"Get transactions error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get transactions"
        )

@router.get("/users", response_model=dict)
async def get_users(db=Depends(get_db)):
    """Get all registered users"""
    try:
        users = await db.users.find({}, {"_id": 0, "password_hash": 0}).to_list(1000)
        
        # Convert datetime objects
        for user in users:
            for key, value in user.items():
                if isinstance(value, datetime):
                    user[key] = value.isoformat()
        
        return {"users": users}
    except Exception as e:
        logger.error(f"Get users error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get users"
        )

@router.get("/activity-logs", response_model=dict)
async def get_activity_logs(db=Depends(get_db)):
    """Get recent activity logs"""
    try:
        # Get recent applications as activity
        applications = await db.applications.find(
            {}, 
            {"_id": 0, "application_id": 1, "full_name": 1, "email": 1, "status": 1, "created_at": 1, "updated_at": 1}
        ).sort("updated_at", -1).to_list(50)
        
        activities = []
        for app in applications:
            activities.append({
                "type": "application",
                "user": app.get("full_name"),
                "email": app.get("email"),
                "action": f"Application {app.get('application_id')} - {app.get('status')}",
                "timestamp": app.get("updated_at", app.get("created_at")).isoformat() if app.get("updated_at") or app.get("created_at") else None
            })
        
        return {"activities": activities}
    except Exception as e:
        logger.error(f"Get activity logs error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get activity logs"
        )


@router.post("/send-reminders", response_model=dict)
async def send_email_reminders(request: SendReminderRequest, db=Depends(get_db)):
    """Send payment reminder emails to selected users"""
    try:
        sent_count = 0
        failed_count = 0
        results = []
        
        for email in request.user_emails:
            # Find the user's application
            application = await db.applications.find_one({"email": email})
            
            if not application:
                results.append({"email": email, "status": "failed", "reason": "No application found"})
                failed_count += 1
                continue
            
            # Determine what reminder to send based on application status
            reminder_sent = False
            
            # Check if processing fee reminder needed
            if request.reminder_type in ["processing_fee", "all"]:
                if not application.get("processing_fee_paid", False):
                    try:
                        await email_service.send_payment_reminder(
                            email,
                            application["full_name"],
                            application["application_id"],
                            "processing_fee",
                            2500
                        )
                        reminder_sent = True
                        results.append({"email": email, "status": "sent", "type": "processing_fee"})
                    except Exception as e:
                        results.append({"email": email, "status": "failed", "reason": str(e)})
                        failed_count += 1
                        continue
            
            # Check if deposit reminder needed
            if request.reminder_type in ["deposit", "all"]:
                if application.get("processing_fee_paid", False) and not application.get("deposit_paid", False) and application.get("status") == "approved":
                    try:
                        await email_service.send_payment_reminder(
                            email,
                            application["full_name"],
                            application["application_id"],
                            "deposit",
                            3000
                        )
                        reminder_sent = True
                        results.append({"email": email, "status": "sent", "type": "deposit"})
                    except Exception as e:
                        results.append({"email": email, "status": "failed", "reason": str(e)})
                        failed_count += 1
                        continue
            
            if reminder_sent:
                sent_count += 1
            elif not any(r["email"] == email for r in results):
                results.append({"email": email, "status": "skipped", "reason": "No pending payment"})
        
        return {
            "message": f"Sent {sent_count} reminders, {failed_count} failed",
            "sent": sent_count,
            "failed": failed_count,
            "results": results
        }
    except Exception as e:
        logger.error(f"Send reminders error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reminders"
        )


@router.post("/send-reminder-all", response_model=dict)
async def send_reminder_to_all_pending(db=Depends(get_db)):
    """Send payment reminders to ALL users with pending payments"""
    try:
        sent_count = 0
        
        # Get all applications with pending processing fee
        pending_processing = await db.applications.find({
            "processing_fee_paid": False
        }).to_list(1000)
        
        for app in pending_processing:
            try:
                await email_service.send_payment_reminder(
                    app["email"],
                    app["full_name"],
                    app["application_id"],
                    "processing_fee",
                    2500
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send reminder to {app['email']}: {e}")
        
        # Get all approved applications with pending deposit
        pending_deposit = await db.applications.find({
            "processing_fee_paid": True,
            "deposit_paid": False,
            "status": "approved"
        }).to_list(1000)
        
        for app in pending_deposit:
            try:
                await email_service.send_payment_reminder(
                    app["email"],
                    app["full_name"],
                    app["application_id"],
                    "deposit",
                    3000
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send reminder to {app['email']}: {e}")
        
        return {
            "message": f"Successfully sent {sent_count} reminder emails",
            "sent": sent_count
        }
    except Exception as e:
        logger.error(f"Send all reminders error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send reminders"
        )


@router.get("/applications/{application_id}/documents", response_model=dict)
async def get_application_documents(application_id: str, db=Depends(get_db)):
    """Get document URLs for an application"""
    try:
        application = await db.applications.find_one(
            {"application_id": application_id},
            {"_id": 0, "id_card_url": 1, "passport_url": 1, "full_name": 1}
        )
        
        if not application:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        
        return {
            "application_id": application_id,
            "applicant_name": application.get("full_name"),
            "documents": {
                "id_card": application.get("id_card_url"),
                "passport": application.get("passport_url")
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get documents error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get documents"
        )


@router.get("/document/{doc_type}/{filename}")
async def serve_document(doc_type: str, filename: str):
    """Serve uploaded document files"""
    try:
        # Construct file path
        upload_dir = os.environ.get("UPLOAD_DIR", "/app/backend/uploads")
        file_path = os.path.join(upload_dir, doc_type, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        return FileResponse(file_path)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Serve document error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to serve document"
        )
