"""
Configuration management module
Handles all environment variables and settings
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # .env file takes priority over environment variables
        env_ignore_empty=True,
        extra="ignore"
    )

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # Twilio WhatsApp API
    twilio_account_sid: str = Field(..., env="TWILIO_ACCOUNT_SID")
    twilio_auth_token: str = Field(..., env="TWILIO_AUTH_TOKEN")
    twilio_whatsapp_number: str = Field(..., env="TWILIO_WHATSAPP_NUMBER")
    verify_token: str = Field(..., env="VERIFY_TOKEN")

    # Legacy API keys (no longer used - kept for backward compatibility)
    google_places_api_key: Optional[str] = Field("not_required", env="GOOGLE_PLACES_API_KEY")
    facebook_access_token: Optional[str] = Field("not_required", env="FACEBOOK_ACCESS_TOKEN")

    # OpenAI API
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4-turbo", env="OPENAI_MODEL")

    # Google Custom Search API
    google_search_api_key: Optional[str] = Field(None, env="GOOGLE_SEARCH_API_KEY")
    google_search_engine_id: Optional[str] = Field(None, env="GOOGLE_SEARCH_ENGINE_ID")

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
    rate_limit_per_user_monthly: int = Field(default=50, env="RATE_LIMIT_PER_USER_MONTHLY")  # Monthly limit for regular users
    rate_limit_admin_monthly: int = Field(default=500, env="RATE_LIMIT_ADMIN_MONTHLY")  # Monthly limit for admin
    rate_limit_per_minute: int = Field(default=10, env="RATE_LIMIT_PER_MINUTE")

    # User Access Control
    admin_phone_number: str = Field(..., env="ADMIN_PHONE_NUMBER")  # Your WhatsApp number
    require_approval: bool = Field(default=False, env="REQUIRE_APPROVAL")  # Enable/disable approval system

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    sentry_dsn: Optional[str] = Field(None, env="SENTRY_DSN")

    # Optional: Redis
    redis_url: Optional[str] = Field(None, env="REDIS_URL")


# Create global settings instance
# Force reload from .env by clearing the bad env var first
import os
if 'OPENAI_API_KEY' in os.environ and ' ' in os.environ['OPENAI_API_KEY']:
    # Clear corrupted environment variable
    del os.environ['OPENAI_API_KEY']

settings = Settings()
