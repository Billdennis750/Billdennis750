from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    mongo_url: str
    db_name: str
    cors_origins: str
    backend_url: str
    jwt_secret: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    # Xixapay Payment Gateway
    xixapay_api_key: str
    xixapay_public_key: str
    xixapay_merchant_id: str
    xixapay_base_url: str = "https://api.xixapay.com"
    xixapay_webhook_secret: str = ""
    # SendGrid Email
    sendgrid_api_key: str
    sendgrid_from_email: str
    # File Upload
    upload_dir: str
    max_file_size: int
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
