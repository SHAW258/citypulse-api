"""Centralized, environment-driven application configuration."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote_plus

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Settings read from `.env` locally and environment variables in deployment."""

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "CityPulse API"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    mysql_host: str = "localhost"
    mysql_port: int = Field(default=3306, ge=1, le=65535)
    mysql_database: str = "citypulse"
    mysql_username: str = "root"
    mysql_password: SecretStr = SecretStr("root")

    secret_key: SecretStr = Field(min_length=32)
    jwt_algorithm: Literal["HS256", "HS384", "HS512"] = "HS256"
    access_token_expire_minutes: int = Field(default=15, ge=5, le=60)
    refresh_token_expire_days: int = Field(default=7, ge=1, le=30)
    jwt_issuer: str = "citypulse-api"
    jwt_audience: str = "citypulse-mobile"

    database_url_override: str | None = Field(default=None, validation_alias="DATABASE_URL")
    cors_origins: list[str] = ["*"]
    allowed_hosts: list[str] = ["*"]
    force_https: bool = False
    max_request_size_bytes: int = Field(default=1_048_576, ge=1_024, le=10_485_760)
    general_rate_limit_per_minute: int = Field(default=120, ge=10, le=1_000)
    login_rate_limit_per_minute: int = Field(default=10, ge=3, le=100)

    @field_validator("cors_origins", "allowed_hosts")
    @classmethod
    def reject_empty_values(cls, values: list[str]) -> list[str]:
        if not values or any(not value.strip() for value in values):
            raise ValueError("must contain at least one non-empty value")
        return values

    @model_validator(mode="after")
    def enforce_production_safety(self) -> Settings:
        insecure_secret = self.secret_key.get_secret_value().startswith("replace-with")
        local_root_account = (
            self.mysql_username == "root" and self.mysql_password.get_secret_value() == "root"
        )
        if self.environment == "production":
            if self.debug:
                raise ValueError("DEBUG must be false in production")
            if insecure_secret:
                raise ValueError("SECRET_KEY must be replaced in production")
            if not self.database_url_override and local_root_account:
                raise ValueError("root/root MySQL credentials are prohibited in production")
        return self

    @property
    def database_url(self) -> str:
        if self.database_url_override:
            url = self.database_url_override.strip()
            # Standardize postgres scheme to asyncpg dialect
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
            elif url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+asyncpg://", 1)
            return url

        username = quote_plus(self.mysql_username)
        password = quote_plus(self.mysql_password.get_secret_value())
        return (
            f"mysql+asyncmy://{username}:{password}@{self.mysql_host}:"
            f"{self.mysql_port}/{self.mysql_database}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    """Return one immutable configuration instance per process."""

    return Settings()
