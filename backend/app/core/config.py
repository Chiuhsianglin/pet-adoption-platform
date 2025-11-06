"""
Core configuration module for Pet Adoption Platform
"""
from typing import List, Optional
from functools import lru_cache

from pydantic import EmailStr, field_validator
from pydantic_settings import BaseSettings
from decouple import config


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """
    
    # Application settings
    APP_NAME: str = "Pet Adoption Platform API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")
    DEBUG: bool = config("DEBUG", default=True, cast=bool)
    
    # Security settings
    SECRET_KEY: str = config("SECRET_KEY", default="your-secret-key")
    JWT_SECRET_KEY: str = config("JWT_SECRET_KEY", default="your-jwt-secret-key")
    JWT_ALGORITHM: str = config("JWT_ALGORITHM", default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = config("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", default=15, cast=int)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = config("JWT_REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)
    PASSWORD_HASH_ROUNDS: int = config("PASSWORD_HASH_ROUNDS", default=12, cast=int)
    
    # Database settings
    DATABASE_URL: str = config(
        "DATABASE_URL", 
        default="mysql+aiomysql://pet_user:pet_password@localhost:3306/pet_adoption"
    )
    DATABASE_POOL_SIZE: int = config("DATABASE_POOL_SIZE", default=20, cast=int)
    DATABASE_MAX_OVERFLOW: int = config("DATABASE_MAX_OVERFLOW", default=30, cast=int)
    DATABASE_POOL_TIMEOUT: int = config("DATABASE_POOL_TIMEOUT", default=30, cast=int)
    DATABASE_POOL_RECYCLE: int = config("DATABASE_POOL_RECYCLE", default=3600, cast=int)
    
    # Redis settings
    REDIS_URL: str = config("REDIS_URL", default="redis://localhost:6379")
    
    # CORS settings
    CORS_ORIGINS: str = config("CORS_ORIGINS", default="http://localhost:3000")
    CORS_CREDENTIALS: bool = config("CORS_CREDENTIALS", default=True, cast=bool)
    CORS_METHODS: str = config("CORS_METHODS", default="GET,POST,PUT,DELETE,OPTIONS")
    CORS_HEADERS: str = config("CORS_HEADERS", default="*")
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
    
    # File upload settings
    AWS_ACCESS_KEY_ID: Optional[str] = config("AWS_ACCESS_KEY_ID", default=None)
    AWS_SECRET_ACCESS_KEY: Optional[str] = config("AWS_SECRET_ACCESS_KEY", default=None)
    AWS_S3_BUCKET: str = config("AWS_S3_BUCKET", default="pet-adoption-files")
    AWS_REGION: str = config("AWS_REGION", default="us-east-1")
    MAX_FILE_SIZE: int = config("MAX_FILE_SIZE", default=10485760, cast=int)  # 10MB
    MAX_PHOTO_SIZE: int = config("MAX_PHOTO_SIZE", default=5242880, cast=int)  # 5MB
    
    # Email settings
    EMAIL_SMTP_HOST: str = config("EMAIL_SMTP_HOST", default="smtp.gmail.com")
    EMAIL_SMTP_PORT: int = config("EMAIL_SMTP_PORT", default=587, cast=int)
    EMAIL_SMTP_USER: Optional[str] = config("EMAIL_SMTP_USER", default=None)
    EMAIL_SMTP_PASSWORD: Optional[str] = config("EMAIL_SMTP_PASSWORD", default=None)
    EMAIL_FROM_ADDRESS: str = config("EMAIL_FROM_ADDRESS", default="noreply@petadoption.com")
    EMAIL_FROM_NAME: str = config("EMAIL_FROM_NAME", default="Pet Adoption Platform")
    EMAIL_USE_TLS: bool = config("EMAIL_USE_TLS", default=True, cast=bool)
    
    # Logging settings
    LOG_LEVEL: str = config("LOG_LEVEL", default="INFO")
    LOG_FORMAT: str = config("LOG_FORMAT", default="json")
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = config("RATE_LIMIT_ENABLED", default=True, cast=bool)
    RATE_LIMIT_REQUESTS: int = config("RATE_LIMIT_REQUESTS", default=100, cast=int)
    RATE_LIMIT_WINDOW: int = config("RATE_LIMIT_WINDOW", default=3600, cast=int)
    
    # WebSocket settings
    WEBSOCKET_MAX_CONNECTIONS: int = config("WEBSOCKET_MAX_CONNECTIONS", default=1000, cast=int)
    WEBSOCKET_PING_INTERVAL: int = config("WEBSOCKET_PING_INTERVAL", default=25, cast=int)
    WEBSOCKET_PING_TIMEOUT: int = config("WEBSOCKET_PING_TIMEOUT", default=5, cast=int)
    
    @field_validator("ENVIRONMENT")
    @classmethod
    def validate_environment(cls, v):
        if v not in ["development", "testing", "production"]:
            raise ValueError("ENVIRONMENT must be one of: development, testing, production")
        return v
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_testing(self) -> bool:
        return self.ENVIRONMENT == "testing"
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    class Config:
        case_sensitive = True
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Global settings instance
settings = get_settings()