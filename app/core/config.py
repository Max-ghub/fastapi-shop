from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="forbid",
    )

    # App
    app_env: Literal["development", "staging", "production"] = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    log_level: Literal["debug", "info", "warning", "error"] = "info"

    # DSN
    database_dsn: str
    redis_dsn: str
    rabbitmq_dsn: str
    minio_dsn: str
    celery_broker_dsn: str
    celery_result_dsn: str
    sentry_dsn: str | None = None

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()
