from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from utils.auth import get_current_user
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin", tags=["admin"])

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
