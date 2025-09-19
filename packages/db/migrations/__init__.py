"""Lightweight async migration runner."""

from __future__ import annotations

from typing import Iterable, List, Set

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from .models import Migration
from .v0001_initial import migration as migration_0001

MIGRATIONS: List[Migration] = [migration_0001]


async def _ensure_versions_table(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
        )


async def _fetch_applied(engine: AsyncEngine) -> Set[str]:
    async with engine.begin() as conn:
        result = await conn.execute(text("SELECT id FROM schema_migrations"))
        return {row[0] for row in result}


async def _record_applied(engine: AsyncEngine, migration: Migration) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text("INSERT INTO schema_migrations (id, name) VALUES (:id, :name)"),
            {"id": migration.id, "name": migration.name},
        )


async def _remove_applied(engine: AsyncEngine, migration: Migration) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text("DELETE FROM schema_migrations WHERE id = :id"),
            {"id": migration.id},
        )


async def apply_migrations(engine: AsyncEngine, *, target_ids: Iterable[str] | None = None) -> None:
    """Apply pending migrations in order."""

    await _ensure_versions_table(engine)
    applied = await _fetch_applied(engine)

    selected: Iterable[Migration]
    if target_ids is not None:
        target_set = set(target_ids)
        selected = [m for m in MIGRATIONS if m.id in target_set]
    else:
        selected = MIGRATIONS

    for migration in selected:
        if migration.id in applied:
            continue
        await migration.upgrade(engine)
        await _record_applied(engine, migration)


async def rollback_last(engine: AsyncEngine) -> None:
    """Rollback the most recently applied migration, if any."""

    await _ensure_versions_table(engine)
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                """
                SELECT id FROM schema_migrations
                ORDER BY applied_at DESC
                LIMIT 1
                """
            )
        )
        row = result.first()

    if row is None:
        return

    migration = next((m for m in MIGRATIONS if m.id == row[0]), None)
    if migration is None:
        return

    await migration.downgrade(engine)
    await _remove_applied(engine, migration)


__all__ = ["apply_migrations", "rollback_last", "MIGRATIONS"]
