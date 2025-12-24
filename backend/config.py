from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache
from typing import List, Union

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
    debug: bool = False
    allowed_origins: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000"
    ]

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra='ignore')

    @model_validator(mode='after')
    def assemble_cors_origins(self) -> 'Settings':
        if isinstance(self.allowed_origins, str):
            self.allowed_origins = [i.strip() for i in self.allowed_origins.split(",")]
        return self
    
    # Company Info
    company_name: str = "School Copy Manufacturing"
    company_address: str = "123 Business Street, Karachi, Pakistan"
    company_phone: str = "+92 300 1234567"
    company_email: str = "info@schoolcopy.com"
    
    # File Uploads
    invoice_dir: str = "./invoices"
    max_upload_size: int = 10485760

@lru_cache()
def get_settings():
    return Settings()
# from pydantic_settings import BaseSettings
# from pydantic import model_validator
# from functools import lru_cache
# import os

# class Settings(BaseSettings):
#     # Database
#     database_url: str
    
#     # JWT
#     secret_key: str = "your-secret-key-change-this-in-production"
#     algorithm: str = "HS256"
#     access_token_expire_minutes: int = 30
    
#     # Google Sheets
#     google_credentials_file: str = "credentials.json"
#     google_sheet_id: str = ""
    
#     # Redis
#     redis_url: str = "redis://localhost:6379/0"
    
#     # Application
#     debug: bool = True
#     environment: str = "development"
#     frontend_url: str = "http://localhost:5173"
#     allowed_origins: list[str] = []

#     @model_validator(mode='after')
#     def assemble_cors_origins(self):
#         """Dynamic CORS origins based on environment"""
#         defaults = [
#             "http://localhost:5173",
#             "http://localhost:5174",
#             "http://127.0.0.1:5173",
#             "http://127.0.0.1:5174",
#             "http://localhost:3000"
#         ]
        
#         # Add defaults if not present
#         for origin in defaults:
#             if origin not in self.allowed_origins:
#                 self.allowed_origins.append(origin)
        
#         # Add production frontend URL if set
#         if self.frontend_url and self.frontend_url not in self.allowed_origins:
#             self.allowed_origins.append(self.frontend_url)
        
#         # Add Railway/Render URLs if present
#         if os.getenv("RAILWAY_STATIC_URL"):
#             railway_url = f"https://{os.getenv('RAILWAY_STATIC_URL')}"
#             if railway_url not in self.allowed_origins:
#                 self.allowed_origins.append(railway_url)
        
#         return self
    
#     # Company Info
#     company_name: str = "School Copy Manufacturing"
#     company_address: str = "123 Business Street, Karachi, Pakistan"
#     company_phone: str = "+92 300 1234567"
#     company_email: str = "info@schoolcopy.com"
    
#     # File Uploads
#     invoice_dir: str = "./invoices"
#     max_upload_size: int = 10485760
    
#     class Config:
#         env_file = ".env"
#         case_sensitive = False

# @lru_cache()
# def get_settings():
#     return Settings()

# def is_production() -> bool:
#     """Check if running in production environment"""
#     settings = get_settings()
#     return settings.environment.lower() == "production"
