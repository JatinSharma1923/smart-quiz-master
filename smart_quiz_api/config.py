from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Any

class Settings(BaseSettings):
    # App metadata
    app_name: str = Field(default="Smart Quiz Master API", alias="APP_NAME")
    app_version: str = Field(default="2.0.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    # Database
    database_url: str = Field(default="sqlite:///./smart_quiz.db", alias="DATABASE_URL")
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")

    # Feature flags
    enable_ai_features: bool = Field(default=True, alias="ENABLE_AI_FEATURES")
    enable_websockets: bool = Field(default=True, alias="ENABLE_WEBSOCKETS")
    enable_caching: bool = Field(default=True, alias="ENABLE_CACHING")
    enable_rate_limiting: bool = Field(default=True, alias="ENABLE_RATE_LIMITING")

    # API Keys and Service URLs
    # Provide sensible defaults so integration tests don't fail if env vars are missing.
    # These can (and should) be overridden by real env variables in production.
    openai_api_key: str = Field(default="dummy-openai-key", alias="OPENAI_API_KEY")
    admin_api_key: str = Field(default="dummy-admin-key", alias="ADMIN_API_KEY")
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    firebase_cred_path: str = Field(default="firebase-credentials.json", alias="FIREBASE_CRED_PATH")
    scraper_model: str = Field(default="gpt-3.5-turbo", alias="SCRAPER_MODEL")
    google_application_credentials: str = Field(default="dummy-gcp-key", alias="GOOGLE_APPLICATION_CREDENTIALS")
    api_key_header: str = Field(default="x-api-key", alias="API_KEY_HEADER")

    cors_allowed_origins: list[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOWED_ORIGINS")
    cors_allowed_methods: list[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOWED_METHODS")
    cors_allowed_headers: list[str] = Field(default_factory=lambda: ["*"], alias="CORS_ALLOWED_HEADERS")
    cors_allow_credentials: bool = Field(default=True, alias="CORS_ALLOW_CREDENTIALS")

    def model_post_init(self, __context: Any):
        for field in ["cors_allowed_origins", "cors_allowed_methods", "cors_allowed_headers"]:
            value = getattr(self, field)
            if isinstance(value, str):
                setattr(self, field, [v.strip() for v in value.split(",") if v.strip()])

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings() 