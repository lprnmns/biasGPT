"""Database settings loader shared across services."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./biasgpt.db"
SUPPORTED_SCHEMES = {
    "postgresql+asyncpg",
    "postgresql+psycopg",
    "sqlite+aiosqlite",
}


class DatabaseURLValidationError(ValueError):
    """Raised when the configured DATABASE_URL does not meet requirements."""


class EngineTuning(BaseModel):
    echo: bool = Field(False, alias="DATABASE_ECHO")
    pool_size: int = Field(5, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(5, alias="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(30, alias="DATABASE_POOL_TIMEOUT")
    pool_recycle: int = Field(1800, alias="DATABASE_POOL_RECYCLE")

    @classmethod
    def from_env(cls) -> "EngineTuning":
        data: Dict[str, str] = {}
        for field in cls.model_fields.values():
            env_key = field.alias
            if env_key and env_key in os.environ:
                data[env_key] = os.environ[env_key]
        return cls(**data)


class DatabaseSettings(BaseSettings):
    """Application database configuration derived from environment."""

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=(
            ".env",
            ".env.development",
            ".env.local",
            ".env.staging",
            ".env.production",
        ),
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = Field(
        default=DEFAULT_DATABASE_URL,
        alias="DATABASE_URL",
        description="SQLAlchemy-compatible async connection string.",
    )
    echo: bool = Field(False, alias="DATABASE_ECHO")
    pool_size: int = Field(5, alias="DATABASE_POOL_SIZE")
    max_overflow: int = Field(5, alias="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(30, alias="DATABASE_POOL_TIMEOUT")
    pool_recycle: int = Field(1800, alias="DATABASE_POOL_RECYCLE")

    @field_validator("database_url")
    @classmethod
    def _validate_url(cls, value: str) -> str:
        scheme = value.split(":", 1)[0]
        if scheme not in SUPPORTED_SCHEMES:
            raise DatabaseURLValidationError(
                f"Unsupported database scheme '{scheme}'. Supported: {', '.join(sorted(SUPPORTED_SCHEMES))}."
            )
        return value

    @property
    def sqlalchemy_options(self) -> Dict[str, Any]:
        """Keyword arguments forwarded to SQLAlchemy engine factory."""

        base_options: Dict[str, Any] = {
            "echo": self.echo,
            "pool_pre_ping": True,
        }
        if self.database_url.startswith("sqlite+"):
            return base_options
        return {
            **base_options,
            "pool_size": self.pool_size,
            "max_overflow": self.max_overflow,
            "pool_timeout": self.pool_timeout,
            "pool_recycle": self.pool_recycle,
        }


@lru_cache(maxsize=1)
def get_database_settings() -> DatabaseSettings:
    """Return cached database settings."""

    tuning = EngineTuning.from_env()
    try:
        base = DatabaseSettings()
    except ValidationError as exc:  # pragma: no cover - validation message captured by caller
        raise DatabaseURLValidationError(str(exc)) from exc

    overrides = {
        field_name: getattr(tuning, field_name)
        for field_name in ("echo", "pool_size", "max_overflow", "pool_timeout", "pool_recycle")
        if DatabaseSettings.model_fields[field_name].alias in os.environ
    }
    if overrides:
        return base.model_copy(update=overrides)
    return base


def reset_database_settings_cache() -> None:
    """Clear cached settings (useful for tests)."""

    get_database_settings.cache_clear()  # type: ignore[attr-defined]
