from datetime import datetime
from decimal import Decimal

import pytest

from packages.queue import InMemoryQueueProducer
from services.api.routes import events as events_route
from services.api.schemas.events import EventIngestRequest, EventPayload


@pytest.mark.asyncio
async def test_event_ingest_enqueues_and_returns_status():
    queue = InMemoryQueueProducer()
    request = EventIngestRequest(
        source="webhook",
        events=[
            EventPayload(
                tx_hash="0xabc",
                wallet="0x123",
                category="transfer",
                timestamp=datetime.fromisoformat("2025-01-01T00:00:00+00:00"),
                asset="ETH",
                amount=Decimal("12.5"),
                notional_usd=Decimal("24000"),
            )
        ],
    )

    response = await events_route.ingest_events(request, queue)

    assert response.success is True
    assert response.enqueued == 1
    assert len(queue.items) == 1
    envelope = queue.items[0]
    assert envelope.metadata["source"] == "webhook"
    assert envelope.payload["tx_hash"] == "0xabc"


@pytest.mark.asyncio
async def test_event_ingest_missing_fields_returns_error():
    queue = InMemoryQueueProducer()
    request = EventIngestRequest(
        events=[
            EventPayload(
                tx_hash="",
                wallet="",
                category="swap",
                timestamp=datetime.fromisoformat("2025-01-01T00:00:00+00:00"),
            )
        ]
    )

    with pytest.raises(events_route.HTTPException) as exc:
        await events_route.ingest_events(request, queue)

    assert exc.value.status_code == events_route.status.HTTP_400_BAD_REQUEST
    assert "missing" in exc.value.detail.lower()


def test_event_ingest_requires_events():
    with pytest.raises(ValueError):
        EventIngestRequest(events=[])
