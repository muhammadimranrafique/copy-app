from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    database_url: str
    
    # JWT
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google Sheets
    google_credentials_file: str = "credentials.json"
    google_sheet_id: str = ""
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Application
    debug: bool = True
    allowed_origins: list = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000"
    ]
    
    # Company Info
    company_name: str = "School Copy Manufacturing"
    company_address: str = "123 Business Street, Karachi, Pakistan"
    company_phone: str = "+92 300 1234567"
    company_email: str = "info@schoolcopy.com"
    
    # File Uploads
    invoice_dir: str = "./invoices"
    max_upload_size: int = 10485760
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
