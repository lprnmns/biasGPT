import asyncio
from datetime import datetime, timedelta, timezone

import pytest

from packages.queue import InMemoryQueueProducer
from workers.cron.backfill import BackfillConfig, EventFetcher, run_backfill


class DummyFetcher(EventFetcher):
    def __init__(self, events):
        self.events = events

    async def fetch(self, *, since: datetime, limit: int):  # type: ignore[override]
        return [event for event in self.events if event["timestamp"] > since.isoformat()][:limit]


@pytest.mark.asyncio
async def test_run_backfill_enqueues_events():
    queue = InMemoryQueueProducer()
    now = datetime.now(timezone.utc)
    events = [
        {"txHash": "0xabc", "wallet": "0x1", "timestamp": (now - timedelta(minutes=10)).isoformat(), "category": "transfer"},
        {"txHash": "0xdef", "wallet": "0x2", "timestamp": (now - timedelta(minutes=30)).isoformat(), "category": "swap"},
    ]
    fetcher = DummyFetcher(events)

    config = BackfillConfig(queue=queue, fetcher=fetcher, lookback_minutes=40, batch_size=10)

    result = await run_backfill(config)

    assert result["fetched"] == 2
    assert result["enqueued"] == 2
    assert len(queue.items) == 2


@pytest.mark.asyncio
async def test_run_backfill_handles_empty():
    queue = InMemoryQueueProducer()
    fetcher = DummyFetcher([])
    config = BackfillConfig(queue=queue, fetcher=fetcher)

    result = await run_backfill(config)

    assert result == {"fetched": 0, "success": True, "enqueued": 0}
    assert queue.items == []
