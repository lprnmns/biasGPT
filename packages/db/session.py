"""Async SQLAlchemy session utilities."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .settings import DatabaseSettings, get_database_settings


_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def init_engine(settings: Optional[DatabaseSettings] = None, *, force: bool = False) -> AsyncEngine:
    """Initialise (or return existing) async SQLAlchemy engine."""

    global _engine
    if _engine is not None and not force:
        return _engine

    settings = settings or get_database_settings()
    # Debugging hook helpful during testing; consider structured logging later.
    # print(f"init_engine using URL: {settings.database_url}")
    _engine = create_async_engine(settings.database_url, **settings.sqlalchemy_options)
    return _engine


def init_sessionmaker(
    engine: Optional[AsyncEngine] = None,
    *,
    force: bool = False,
) -> async_sessionmaker[AsyncSession]:
    """Initialise session factory bound to the shared engine."""

    global _session_factory
    if _session_factory is not None and not force:
        return _session_factory

    engine = engine or init_engine()
    _session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return _session_factory


@asynccontextmanager
async def get_session(
    session_factory: Optional[async_sessionmaker[AsyncSession]] = None,
) -> AsyncIterator[AsyncSession]:
    """Yield a managed async session instance."""

    factory = session_factory or init_sessionmaker()
    session = factory()
    try:
        yield session
        await session.commit()
    except Exception:  # pragma: no cover - reraised for caller handling
        await session.rollback()
        raise
    finally:
        await session.close()


async def check_database_health(engine: Optional[AsyncEngine] = None) -> bool:
    """Execute a trivial query to confirm connectivity."""

    engine = engine or init_engine()
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        value = result.scalar()
    return value == 1


async def dispose_engine() -> None:
    """Dispose engine and reset cached factories (primarily for tests)."""

    global _engine, _session_factory
    _session_factory = None
    if _engine is not None:
        await _engine.dispose()
        _engine = None
