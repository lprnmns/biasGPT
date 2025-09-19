"""Database fixtures for integration tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import pytest_asyncio

from packages.db import (
    apply_migrations,
    dispose_engine,
    get_database_settings,
    get_session,
    init_engine,
    init_sessionmaker,
    reset_database_settings_cache,
)

SKIP_ASYNC_SQLITE = os.environ.get("SKIP_ASYNC_SQLITE", "1") != "0"


@pytest_asyncio.fixture
async def db_session(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    if SKIP_ASYNC_SQLITE:
        pytest.skip("Async SQLite unavailable in sandbox; repository tests skipped")

    db_file = tmp_path / "repo.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    reset_database_settings_cache()

    settings = get_database_settings()
    engine = init_engine(settings, force=True)
    session_factory = init_sessionmaker(engine, force=True)

    await apply_migrations(engine)

    try:
        async with get_session(session_factory) as session:
            yield session
    finally:
        await dispose_engine()
