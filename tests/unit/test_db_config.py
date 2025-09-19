import os
from pathlib import Path

import pytest
import pytest_asyncio
from sqlalchemy import text

from packages.db import (
    DatabaseURLValidationError,
    check_database_health,
    dispose_engine,
    get_database_settings,
    get_session,
    init_engine,
    init_sessionmaker,
    reset_database_settings_cache,
)

SKIP_ASYNC_SQLITE = os.environ.get("SKIP_ASYNC_SQLITE", "1") != "0"

ENV_KEYS = [
    "DATABASE_URL",
    "DATABASE_ECHO",
    "DATABASE_POOL_SIZE",
    "DATABASE_MAX_OVERFLOW",
    "DATABASE_POOL_TIMEOUT",
    "DATABASE_POOL_RECYCLE",
]


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)
    reset_database_settings_cache()
    yield
    reset_database_settings_cache()


@pytest_asyncio.fixture(autouse=True)
async def cleanup_engine():
    yield
    await dispose_engine()


def test_settings_load_from_env(monkeypatch):
    url = "sqlite+aiosqlite:///./test.db"
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("DATABASE_POOL_SIZE", "10")
    settings = get_database_settings()
    assert settings.database_url == url
    assert settings.pool_size == 10
    assert settings.sqlalchemy_options["pool_pre_ping"] is True


def test_invalid_scheme_raises(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "mysql://user:pass@localhost:3306/db")
    with pytest.raises(DatabaseURLValidationError):
        get_database_settings()


@pytest.mark.skipif(SKIP_ASYNC_SQLITE, reason="Async sqlite blocked in sandbox")
@pytest.mark.asyncio
async def test_health_check_sqlite(tmp_path: Path, monkeypatch):
    db_file = tmp_path / "health.db"
    url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", url)
    reset_database_settings_cache()

    settings = get_database_settings()
    engine = init_engine(settings, force=True)
    init_sessionmaker(engine, force=True)

    assert str(engine.url) == url
    assert await check_database_health(engine) is True


@pytest.mark.skipif(SKIP_ASYNC_SQLITE, reason="Async sqlite blocked in sandbox")
@pytest.mark.asyncio
async def test_get_session_commits(tmp_path: Path, monkeypatch):
    db_file = tmp_path / "commit.db"
    url = f"sqlite+aiosqlite:///{db_file}"
    monkeypatch.setenv("DATABASE_URL", url)
    reset_database_settings_cache()

    engine = init_engine(get_database_settings(), force=True)
    session_factory = init_sessionmaker(engine, force=True)

    async with get_session(session_factory) as session:
        await session.execute(text("CREATE TABLE sample (id INTEGER PRIMARY KEY, value TEXT)"))
        await session.execute(text("INSERT INTO sample (value) VALUES ('bias')"))

    async with get_session(session_factory) as session:
        result = await session.execute(text("SELECT COUNT(*) FROM sample"))
        assert result.scalar() == 1
