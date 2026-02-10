from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import os

class Settings(BaseSettings):
    # Database - Required (Emergent auto-populates these)
    mongo_url: str = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
    db_name: str = os.environ.get("DB_NAME", "cashflow_mfb")
    
    # CORS and URLs
    cors_origins: str = "*"
    backend_url: str = os.environ.get("BACKEND_URL", "http://localhost:8001")
    
    # JWT Authentication
    jwt_secret: str = os.environ.get("JWT_SECRET", "default_jwt_secret_change_in_production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    
    # BudPay Payment Gateway (Primary)
    budpay_secret_key: str = ""
    budpay_public_key: str = ""
    budpay_base_url: str = "https://api.budpay.com/api/v2"
    budpay_webhook_ips: str = ""
    budpay_webhook_secret: str = ""
    
    # Legacy OTPay (deprecated)
    otpay_api_key: str = ""
    otpay_secret_key: str = ""
    otpay_business_code: str = ""
    otpay_base_url: str = "https://otpay.ng/api/v1"
    otpay_webhook_ips: str = ""
    
    # Legacy Xixapay (deprecated)
    xixapay_api_key: Optional[str] = ""
    xixapay_public_key: Optional[str] = ""
    xixapay_merchant_id: Optional[str] = ""
    xixapay_base_url: str = "https://api.xixapay.com"
    xixapay_webhook_secret: str = ""
    
    # SendGrid Email
    sendgrid_api_key: str = ""
    sendgrid_from_email: str = "noreply@cashflowsmfb.com"
    
    # Resend Email
    resend_api_key: str = ""
    email_provider: str = "resend"
    
    # File Upload
    upload_dir: str = "/app/backend/uploads"
    max_file_size: int = 5242880
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra env vars

@lru_cache()
def get_settings():
    return Settings()
