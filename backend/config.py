import secrets
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from functools import lru_cache
from typing import List, Union

# Development-only CORS origins. In production these are removed automatically;
# production origins must be provided explicitly via ALLOWED_ORIGINS.
DEV_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:3000",
]

# Known placeholder value that must never be used as a production secret.
PLACEHOLDER_SECRET = "your-secret-key-change-this-in-production"


class Settings(BaseSettings):
    # Database
    database_url: str

    # Application environment: "development" (default) or "production".
    # Production enables fail-safe validation for secrets, CORS and docs.
    environment: str = "development"

    # JWT
    # No insecure default: required in production, ephemeral auto-generated
    # value in development (see validate_production_secrets).
    secret_key: str = ""
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Self-registration policy. Disabled by default in production
    # (see apply_registration_policy); enable explicitly with
    # ALLOW_PUBLIC_REGISTRATION=true only if self-signup is really needed.
    allow_public_registration: bool = True

    # SQLAlchemy SQL logging. Disabled by default; set DB_ECHO=true only for
    # local debugging (it logs every SQL statement, including customer data).
    db_echo: bool = False

    # Google Sheets
    google_credentials_file: str = "credentials.json"
    google_sheet_id: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Application
    debug: bool = False
    allowed_origins: Union[List[str], str] = DEV_ORIGINS

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra='ignore')

    @model_validator(mode='after')
    def assemble_cors_origins(self) -> 'Settings':
        if isinstance(self.allowed_origins, str):
            if self.allowed_origins.strip() == "*":
                self.allowed_origins = ["*"]
            else:
                # Normalize: trim whitespace and trailing slashes so origins
                # match the browser Origin header exactly.
                self.allowed_origins = [
                    i.strip().rstrip('/') for i in self.allowed_origins.split(',') if i.strip()
                ]

        if self.environment == "production":
            # Production: reject wildcard origins (incompatible with
            # allow_credentials=True) and non-HTTPS/localhost origins.
            if "*" in self.allowed_origins:
                raise ValueError(
                    'Wildcard CORS origin ("*") is not allowed in production because '
                    'allow_credentials=True. Set ALLOWED_ORIGINS to explicit https:// origins.'
                )
            localhost_origins = [
                o for o in self.allowed_origins
                if o.startswith("http://localhost") or o.startswith("http://127.0.0.1")
            ]
            if localhost_origins:
                raise ValueError(
                    f'Localhost CORS origins are not allowed in production: {localhost_origins}. '
                    'Set ALLOWED_ORIGINS to the production frontend origin(s) only.'
                )
            insecure = [o for o in self.allowed_origins if not o.startswith("https://")]
            if insecure:
                raise ValueError(
                    f'Production CORS origins must use https://: {insecure}'
                )
            if not self.allowed_origins:
                raise ValueError(
                    'ENVIRONMENT=production requires ALLOWED_ORIGINS to list at least one '
                    'https:// frontend origin (e.g. https://your-app.vercel.app).'
                )
        else:
            # Development: keep the localhost origins available for the Vite dev server.
            for origin in DEV_ORIGINS:
                if origin not in self.allowed_origins:
                    self.allowed_origins.append(origin)

        return self

    @model_validator(mode='after')
    def validate_production_secrets(self) -> 'Settings':
        if self.environment == "production":
            if not self.secret_key:
                raise ValueError(
                    "SECRET_KEY is required when ENVIRONMENT=production. "
                    "Generate one with: openssl rand -hex 32"
                )
            if self.secret_key == PLACEHOLDER_SECRET:
                raise ValueError(
                    "SECRET_KEY still uses the documented placeholder value. "
                    "Generate a real secret with: openssl rand -hex 32"
                )
            if len(self.secret_key) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters in production. "
                    "Generate one with: openssl rand -hex 32"
                )
        elif not self.secret_key:
            # Development-only fallback: ephemeral per-process secret so local
            # development works without any configuration. Tokens are invalidated
            # when the dev server restarts. Never used in production.
            self.secret_key = "dev-only-ephemeral-" + secrets.token_urlsafe(24)

        return self

    @model_validator(mode='after')
    def apply_registration_policy(self) -> 'Settings':
        # Fail safe: public self-registration is off by default in production
        # unless explicitly enabled via ALLOW_PUBLIC_REGISTRATION=true.
        if (
            self.environment == "production"
            and "allow_public_registration" not in self.model_fields_set
        ):
            self.allow_public_registration = False
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

# ---------------------------------------------------------------------------
# Legacy (commented-out) configuration kept for reference. See the active
# Settings class above for the enforced production validation rules.
# ---------------------------------------------------------------------------
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
