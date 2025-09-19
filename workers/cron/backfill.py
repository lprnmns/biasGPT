"""Historical backfill job for ingesting past events."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Iterable, List, Optional

from packages.queue import QueueEnvelope, QueueProducer
from workers.ingest.handler import IngestHandler


@dataclass(slots=True)
class BackfillConfig:
    queue: QueueProducer
    fetcher: "EventFetcher"
    batch_size: int = 100
    lookback_minutes: int = 60
    dedupe_window: int = 500


class EventFetcher:
    """Protocol for fetching historical events."""

    async def fetch(self, *, since: datetime, limit: int) -> Iterable[Dict[str, Any]]:  # pragma: no cover - interface
        raise NotImplementedError


async def run_backfill(config: BackfillConfig) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    since = now - timedelta(minutes=config.lookback_minutes)

    raw_events = await config.fetcher.fetch(since=since, limit=config.batch_size)
    events = list(raw_events)
    if not events:
        return {"fetched": 0, "success": True, "enqueued": 0}

    handler = IngestHandler(config.queue, source="backfill")
    payload = {"events": events}
    result = await handler.handle(payload)

    return {"fetched": len(events), **result}


async def periodic_backfill(config: BackfillConfig, interval_minutes: int = 5) -> None:
    while True:  # pragma: no cover - scheduling loop
        await run_backfill(config)
        await asyncio.sleep(interval_minutes * 60)


__all__ = ["BackfillConfig", "EventFetcher", "run_backfill", "periodic_backfill"]
