import os
from pathlib import Path

import pytest
from sqlalchemy import inspect

SKIP_ASYNC_SQLITE = os.environ.get("SKIP_ASYNC_SQLITE", "1") != "0"

if SKIP_ASYNC_SQLITE:
    pytest.skip(
        "Async SQLite unavailable in sandbox; migration tests skipped",
        allow_module_level=True,
    )

from packages.db import (
    apply_migrations,
    dispose_engine,
    get_database_settings,
    init_engine,
    init_sessionmaker,
    rollback_last,
    reset_database_settings_cache,
)


@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    reset_database_settings_cache()
    yield
    reset_database_settings_cache()


@pytest.mark.asyncio
async def test_apply_migrations_creates_schema(tmp_path: Path, monkeypatch):
    db_file = tmp_path / "schema.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    settings = get_database_settings()
    engine = init_engine(settings, force=True)
    init_sessionmaker(engine, force=True)

    try:
        await apply_migrations(engine)

        async with engine.begin() as conn:
            def check(connection):
                inspector = inspect(connection)
                tables = set(inspector.get_table_names())
                expected = {
                    "users",
                    "wallets",
                    "wallet_scores",
                    "events",
                    "event_analysis",
                    "bias",
                    "orders",
                    "positions",
                    "reports",
                    "audit_logs",
                    "schema_migrations",
                }
                assert expected.issubset(tables)
                assert "active_positions_view" in inspector.get_view_names()

            await conn.run_sync(check)

        # Running migrations twice should be idempotent
        await apply_migrations(engine)
    finally:
        await dispose_engine()


@pytest.mark.asyncio
async def test_rollback_last_drops_schema(tmp_path: Path, monkeypatch):
    db_file = tmp_path / "rollback.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_file}")
    settings = get_database_settings()
    engine = init_engine(settings, force=True)
    init_sessionmaker(engine, force=True)

    try:
        await apply_migrations(engine)
        await rollback_last(engine)

        async with engine.begin() as conn:
            def verify(connection):
                inspector = inspect(connection)
                assert "users" not in inspector.get_table_names()
            await conn.run_sync(verify)
    finally:
        await dispose_engine()
