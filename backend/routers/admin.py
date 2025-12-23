from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.get("/stats", response_model=dict)
async def get_admin_stats(db=Depends(get_db)):
    try:
        # Get statistics
        total_applications = await db.applications.count_documents({})
        pending_review = await db.applications.count_documents({"status": "under_review"})
        approved = await db.applications.count_documents({"status": "approved"})
        rejected = await db.applications.count_documents({"status": "rejected"})
        
        # Calculate total disbursed (sum of approved loan amounts)
        pipeline = [
            {"$match": {"status": "approved"}},
            {"$group": {"_id": None, "total": {"$sum": "$loan_amount"}}}
        ]
        result = await db.applications.aggregate(pipeline).to_list(1)
        total_disbursed = result[0]["total"] if result else 0
        
        return {
            "total_applications": total_applications,
            "pending_review": pending_review,
            "approved": approved,
            "rejected": rejected,
            "total_disbursed": total_disbursed
        }
    except Exception as e:
        logger.error(f"Get stats error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )
