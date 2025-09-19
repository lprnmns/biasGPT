"""Database configuration utilities for the API service."""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from packages.db import (
    check_database_health,
    get_database_settings,
    init_engine,
    init_sessionmaker,
)

_settings = get_database_settings()
_engine = init_engine(_settings)
_session_factory = init_sessionmaker(_engine)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return _session_factory


async def database_healthcheck() -> dict:
    healthy = await check_database_health(_engine)
    return {"healthy": healthy}
