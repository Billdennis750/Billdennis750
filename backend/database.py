from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()

async def connect_db():
    try:
        db.client = AsyncIOMotorClient(settings.mongo_url)
        db.db = db.client[settings.db_name]
        
        # Create indexes
        await db.db.users.create_index("email", unique=True)
        await db.db.applications.create_index("application_id", unique=True)
        await db.db.applications.create_index("user_id")
        await db.db.transactions.create_index("order_reference", unique=True)
        
        logger.info("Connected to MongoDB successfully")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

async def close_db():
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")

def get_db():
    return db.db
