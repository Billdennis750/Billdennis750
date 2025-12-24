from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from database import get_db
from utils.auth import get_current_user
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
