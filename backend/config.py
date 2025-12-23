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
    nomba_client_id: str
    nomba_private_key: str
    nomba_account_id: str
    nomba_base_url: str
    nomba_webhook_secret: str
    sendgrid_api_key: str
    sendgrid_from_email: str
    upload_dir: str
    max_file_size: int
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
