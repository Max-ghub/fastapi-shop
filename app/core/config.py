from typing import Literal

from pydantic import AnyUrl, RedisDsn
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
    database_dsn: AnyUrl
    redis_dsn: RedisDsn
    rabbitmq_dsn: AnyUrl
    minio_dsn: AnyUrl
    celery_broker_dsn: AnyUrl
    celery_result_dsn: AnyUrl
    sentry_dsn: AnyUrl | None = None

    # JWT
    jwt_secret: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

settings = Settings()
