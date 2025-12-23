from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from pathlib import Path
import logging
from contextlib import asynccontextmanager
from database import connect_db, close_db
from routers import auth, applications, payments, admin
import os

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Cashflow MFB API")
    await connect_db()
    yield
    # Shutdown
    logger.info("Shutting down Cashflow MFB API")
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
if os.path.exists(upload_dir):
    app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "cashflow-mfb-api",
        "version": "1.0.0"
    }