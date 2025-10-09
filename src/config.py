"""
Configuration management module
Handles all environment variables and settings
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # WhatsApp API Provider Selection
    whatsapp_provider: str = Field(default="twilio", env="WHATSAPP_PROVIDER")  # "twilio" or "meta"
    
    # Twilio WhatsApp API
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_whatsapp_number: str = Field(..., env="TWILIO_WHATSAPP_NUMBER")
    
    # Meta WhatsApp Business API (legacy support)
    whatsapp_phone_number_id: Optional[str] = Field(None, env="WHATSAPP_PHONE_NUMBER_ID")
    whatsapp_business_account_id: Optional[str] = Field(None, env="WHATSAPP_BUSINESS_ACCOUNT_ID")
    whatsapp_access_token: Optional[str] = Field(None, env="WHATSAPP_ACCESS_TOKEN")
    verify_token: str = Field(..., env="VERIFY_TOKEN")

    # Legacy API keys (no longer used - kept for backward compatibility)
    google_places_api_key: Optional[str] = Field("not_required", env="GOOGLE_PLACES_API_KEY")
    facebook_access_token: Optional[str] = Field("not_required", env="FACEBOOK_ACCESS_TOKEN")

    # OpenAI API
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo", env="OPENAI_MODEL")

    # Application Settings
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")

    # Cache Settings
    cache_default_ttl_days: int = Field(default=7, env="CACHE_DEFAULT_TTL_DAYS")
    cache_hot_doctor_ttl_days: int = Field(default=7, env="CACHE_HOT_DOCTOR_TTL_DAYS")
    cache_cold_doctor_ttl_days: int = Field(default=3, env="CACHE_COLD_DOCTOR_TTL_DAYS")

    # Rate Limiting
    rate_limit_per_user_daily: int = Field(default=50, env="RATE_LIMIT_PER_USER_DAILY")
    rate_limit_per_minute: int = Field(default=10, env="RATE_LIMIT_PER_MINUTE")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")

    # Optional: Redis
    redis_url: Optional[str] = Field(None, env="REDIS_URL")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Create global settings instance
settings = Settings()
