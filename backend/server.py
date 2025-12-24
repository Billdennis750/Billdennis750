from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path
import logging
from contextlib import asynccontextmanager
from database import connect_db, close_db, get_db
from routers import auth, applications, payments, admin
from utils.email import email_service
from datetime import datetime, timezone, timedelta
import os
import asyncio

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Background task for payment reminders
async def send_payment_reminders():
    """Send payment reminders every 24 hours for pending payments"""
    while True:
        try:
            logger.info("Running payment reminder task...")
            from motor.motor_asyncio import AsyncIOMotorClient
            from config import get_settings
            
            settings = get_settings()
            client = AsyncIOMotorClient(settings.mongo_url)
            db = client[settings.db_name]
            
            now = datetime.now(timezone.utc)
            
            # Get applications with pending payment (processing fee)
            pending_processing = await db.applications.find({
                "status": "pending_payment",
                "processing_fee_paid": False
            }).to_list(1000)
            
            for app in pending_processing:
                # Check if created more than 24 hours ago
                created = app.get("created_at")
                if created:
                    # Make created timezone aware if it's naive
                    if created.tzinfo is None:
                        created = created.replace(tzinfo=timezone.utc)
                    if (now - created) > timedelta(hours=24):
                        await email_service.send_payment_reminder(
                            app["email"],
                            app["full_name"],
                            app["application_id"],
                            "processing_fee",
                            2500
                        )
                        logger.info(f"Sent processing fee reminder to {app['email']}")
            
            # Get applications with pending deposit
            pending_deposit = await db.applications.find({
                "status": "approved",
                "deposit_paid": False
            }).to_list(1000)
            
            for app in pending_deposit:
                approved_at = app.get("approved_at")
                if approved_at:
                    # Make approved_at timezone aware if it's naive
                    if approved_at.tzinfo is None:
                        approved_at = approved_at.replace(tzinfo=timezone.utc)
                    if (now - approved_at) > timedelta(hours=24):
                        await email_service.send_payment_reminder(
                            app["email"],
                            app["full_name"],
                            app["application_id"],
                            "deposit",
                            3000
                        )
                        logger.info(f"Sent deposit reminder to {app['email']}")
            
            client.close()
            logger.info("Payment reminder task completed successfully")
            
        except Exception as e:
            logger.error(f"Payment reminder task error: {str(e)}")
        
        # Wait 24 hours before next run
        await asyncio.sleep(86400)  # 24 hours in seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Cashflow MFB API")
    await connect_db()
    
    # Start background task for payment reminders
    reminder_task = asyncio.create_task(send_payment_reminders())
    
    yield
    
    # Shutdown
    logger.info("Shutting down Cashflow MFB API")
    reminder_task.cancel()
    await close_db()

# Create FastAPI app
app = FastAPI(
    title="Cashflow MFB API",
    description="Backend API for Cashflow Microfinance Bank",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(applications.router)
app.include_router(payments.router)
app.include_router(admin.router)

# Mount uploads directory
upload_dir = os.environ.get('UPLOAD_DIR', '/app/backend/uploads')
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=upload_dir), name="uploads")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "cashflow-mfb-api",
        "version": "1.0.0"
    }

@app.post("/api/admin/send-reminders")
async def trigger_reminders():
    """Manually trigger payment reminders (admin only)"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        from config import get_settings
        
        settings = get_settings()
        client = AsyncIOMotorClient(settings.mongo_url)
        db = client[settings.db_name]
        
        reminders_sent = 0
        
        # Send to pending processing fee
        pending_processing = await db.applications.find({
            "status": "pending_payment",
            "processing_fee_paid": False
        }).to_list(100)
        
        for app in pending_processing:
            result = await email_service.send_payment_reminder(
                app["email"],
                app["full_name"],
                app["application_id"],
                "processing_fee",
                2500
            )
            if result:
                reminders_sent += 1
        
        # Send to pending deposit
        pending_deposit = await db.applications.find({
            "status": "approved",
            "deposit_paid": False
        }).to_list(100)
        
        for app in pending_deposit:
            result = await email_service.send_payment_reminder(
                app["email"],
                app["full_name"],
                app["application_id"],
                "deposit",
                3000
            )
            if result:
                reminders_sent += 1
        
        client.close()
        
        return {
            "success": True,
            "reminders_sent": reminders_sent
        }
    except Exception as e:
        logger.error(f"Manual reminder trigger error: {str(e)}")
        return {"success": False, "error": str(e)}