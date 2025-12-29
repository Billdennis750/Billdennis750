from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
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
import traceback

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Store last errors for debugging
last_errors = []

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

# CORS middleware - Allow all origins for compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler to capture errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "path": str(request.url.path),
        "method": request.method,
        "error": str(exc),
        "traceback": traceback.format_exc()
    }
    last_errors.append(error_detail)
    # Keep only last 10 errors
    while len(last_errors) > 10:
        last_errors.pop(0)
    
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Check /api/debug/last-errors for details."}
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

@app.get("/api/debug/last-errors")
async def get_last_errors():
    """Get the last 10 errors for debugging"""
    return {
        "error_count": len(last_errors),
        "errors": last_errors
    }

@app.post("/api/debug/test-file-upload")
async def test_file_upload(
    test_file: UploadFile = File(...)
):
    """Test endpoint for file upload debugging"""
    import os
    import aiofiles
    from config import get_settings
    
    settings = get_settings()
    results = {
        "filename": test_file.filename,
        "content_type": test_file.content_type,
        "steps": []
    }
    
    try:
        # Step 1: Read file content
        content = await test_file.read()
        results["steps"].append(f"1. Read file: {len(content)} bytes")
        results["file_size"] = len(content)
        
        # Step 2: Create test directory
        test_dir = os.path.join(settings.upload_dir, "TEST-DEBUG")
        os.makedirs(test_dir, exist_ok=True)
        results["steps"].append(f"2. Created directory: {test_dir}")
        
        # Step 3: Write file using aiofiles
        test_path = os.path.join(test_dir, f"test_{test_file.filename}")
        async with aiofiles.open(test_path, 'wb') as f:
            await f.write(content)
        results["steps"].append(f"3. Wrote file: {test_path}")
        
        # Step 4: Verify file exists
        if os.path.exists(test_path):
            results["steps"].append(f"4. File verified, size: {os.path.getsize(test_path)}")
        
        # Step 5: Clean up
        os.remove(test_path)
        os.rmdir(test_dir)
        results["steps"].append("5. Cleanup successful")
        
        results["success"] = True
        
    except Exception as e:
        import traceback
        results["error"] = str(e)
        results["traceback"] = traceback.format_exc()
        results["success"] = False
    
    return results

@app.get("/api/debug/server-status")
async def server_status():
    """Debug endpoint to check server configuration and state"""
    import os
    from config import get_settings
    
    settings = get_settings()
    upload_dir = settings.upload_dir
    
    # Check upload directory
    upload_exists = os.path.exists(upload_dir)
    upload_writable = os.access(upload_dir, os.W_OK) if upload_exists else False
    
    # Try to actually write a test file
    write_test = "not_tested"
    if upload_exists and upload_writable:
        test_file = os.path.join(upload_dir, "test_write.txt")
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            os.remove(test_file)
            write_test = "success"
        except Exception as e:
            write_test = f"failed: {str(e)}"
    
    # Check disk space
    try:
        import shutil
        total, used, free = shutil.disk_usage(upload_dir if upload_exists else "/app")
        disk_info = {
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2)
        }
    except Exception as e:
        disk_info = {"error": str(e)}
    
    # Count existing applications using the correct db reference
    try:
        from database import db as database
        if database.db:
            app_count = await database.db.applications.count_documents({})
            user_count = await database.db.users.count_documents({})
        else:
            app_count = "Database not connected"
            user_count = "Database not connected"
    except Exception as e:
        app_count = f"Error: {e}"
        user_count = f"Error: {e}"
    
    # Check aiofiles availability
    try:
        import aiofiles
        aiofiles_version = aiofiles.__version__
    except Exception as e:
        aiofiles_version = f"Error: {e}"
    
    return {
        "upload_dir": upload_dir,
        "upload_exists": upload_exists,
        "upload_writable": upload_writable,
        "write_test": write_test,
        "disk_info": disk_info,
        "application_count": app_count,
        "user_count": user_count,
        "backend_url": settings.backend_url,
        "cors_origins": settings.cors_origins,
        "aiofiles_version": aiofiles_version
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