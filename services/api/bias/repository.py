"""Bias persistence helpers using the database layer."""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Sequence

from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession

from packages.db.models import BiasSnapshot
from services.api.bias.calculator import BiasResult


class BiasRepository:
    """Persist and retrieve bias snapshots."""

    def __init__(self, session: Optional[AsyncSession] = None) -> None:
        self.session = session
        self._memory: List[BiasResult] = [] if session is None else []

    async def store(self, result: BiasResult) -> None:
        if self.session is None:
            self._memory.append(result)
            return

        stmt = insert(BiasSnapshot).values(
            timestamp=result.timestamp,
            asset=result.asset,
            timeframe=result.timeframe,
            value=result.value,
            components=result.components,
            confidence=result.confidence,
        )
        await self.session.execute(stmt)

    async def latest(self, assets: Optional[Sequence[str]] = None) -> List[BiasResult]:
        if self.session is None:
            return list(_dedupe_results(self._memory, assets))

        stmt = select(BiasSnapshot).order_by(BiasSnapshot.asset, BiasSnapshot.timeframe, BiasSnapshot.timestamp.desc())
        if assets:
            stmt = stmt.where(BiasSnapshot.asset.in_(list(assets)))
        result = await self.session.execute(stmt)
        snapshots = result.scalars().all()
        return list(_dedupe_results([_from_snapshot(s) for s in snapshots], assets))


def _dedupe_results(results: Sequence[BiasResult], assets: Optional[Sequence[str]]):
    filtered: Dict[tuple[str, str], BiasResult] = {}
    for result in results:
        if assets and result.asset not in assets:
            continue
        key = (result.asset, result.timeframe)
        if key not in filtered:
            filtered[key] = result
    return filtered.values()


def _from_snapshot(snapshot: BiasSnapshot) -> BiasResult:
    return BiasResult(
        asset=snapshot.asset,
        timeframe=snapshot.timeframe,
        value=float(snapshot.value or 0.0),
        confidence=float(snapshot.confidence or 0.0),
        components=dict(snapshot.components or {}),
        timestamp=snapshot.timestamp or datetime.utcnow(),
    )


__all__ = ["BiasRepository"]
