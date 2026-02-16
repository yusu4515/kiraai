"""Configuration management using Pydantic Settings"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # General
    app_name: str = "KiraAI"
    app_env: str = "development"
    debug: bool = True

    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # Claude API
    claude_api_key: str
    claude_model_sonnet: str = "claude-sonnet-4-5-20250929"
    claude_model_haiku: str = "claude-haiku-4-5-20251001"
    claude_max_tokens: int = 4096
    claude_temperature: float = 0.7

    # Indeed API
    indeed_publisher_id: str = ""
    indeed_api_url: str = "https://api.indeed.com/ads/apisearch"

    # CORS
    cors_origins: str = "http://localhost:3000"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: str = "*"

    # Rate Limiting
    rate_limit_per_minute: int = 60
    rate_limit_per_hour: int = 1000

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    # Security
    secure_cookies: bool = False
    https_only: bool = False

    # File Upload
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 10
    allowed_extensions: str = "pdf,docx,jpg,jpeg,png"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]


# Global settings instance
settings = Settings()
