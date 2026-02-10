from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

class Settings(BaseSettings):
    mongo_url: str
    db_name: str
    cors_origins: str
    backend_url: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
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
    sendgrid_from_email: str = ""
    # Resend Email
    resend_api_key: str = ""
    email_provider: str = "resend"
    # File Upload
    upload_dir: str
    max_file_size: int
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
