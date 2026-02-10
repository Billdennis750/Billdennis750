from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import get_settings
import logging
import asyncio

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db = Database()

async def connect_db():
    """Connect to MongoDB with retry logic for production deployments"""
    settings = get_settings()
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Connecting to MongoDB (attempt {attempt + 1}/{max_retries})...")
            
            # Connection options optimized for Atlas
            db.client = AsyncIOMotorClient(
                settings.mongo_url,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=30000,
                maxPoolSize=10,
                minPoolSize=1
            )
            db.db = db.client[settings.db_name]
            
            # Test the connection
            await db.client.admin.command('ping')
            
            # Create indexes (with error handling for existing indexes)
            try:
                await db.db.users.create_index("email", unique=True)
            except Exception:
                pass  # Index might already exist
            
            try:
                await db.db.applications.create_index("application_id", unique=True)
            except Exception:
                pass
            
            try:
                await db.db.applications.create_index("user_id")
            except Exception:
                pass
            
            try:
                await db.db.transactions.create_index("order_reference", unique=True)
            except Exception:
                pass
            
            logger.info("Connected to MongoDB successfully")
            return
            
        except Exception as e:
            logger.error(f"MongoDB connection attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay)
                retry_delay *= 2
            else:
                logger.error("All MongoDB connection attempts failed")
                raise

async def close_db():
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")

def get_db():
    return db.db
