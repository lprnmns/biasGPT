import pytest

from packages.queue import InMemoryQueueProducer
from workers.ingest.handler import IngestHandler


@pytest.mark.asyncio
async def test_ingest_handler_enqueues_events():
    queue = InMemoryQueueProducer()
    handler = IngestHandler(queue)
    payload = {
        "events": [
            {
                "txHash": "0xabc",
                "wallet": "0x123",
                "category": "transfer",
                "timestamp": "2025-01-01T00:00:00Z",
                "asset": "ETH",
                "amount": "10.5",
                "notionalUsd": "20000",
            }
        ],
    }

    result = await handler.handle(payload)

    assert result == {"success": True, "enqueued": 1}
    assert len(queue.items) == 1
    envelope = queue.items[0]
    assert envelope.metadata["source"] == "alchemy"
    assert envelope.metadata["schema"] == "event.v1"
    assert envelope.payload["tx_hash"] == "0xabc"
    assert envelope.payload["wallet_address"] == "0x123"


@pytest.mark.asyncio
async def test_ingest_handler_deduplicates_tx():
    queue = InMemoryQueueProducer()
    handler = IngestHandler(queue)
    payload = {
        "data": [
            {"txHash": "0xdup", "wallet": "0x123", "timestamp": 1700000000, "category": "swap"},
            {"txHash": "0xdup", "wallet": "0x123", "timestamp": 1700000001, "category": "swap"},
        ]
    }

    result = await handler.handle(payload)

    assert result["enqueued"] == 1
    assert len(queue.items) == 1


@pytest.mark.asyncio
async def test_ingest_handler_handles_empty_payload():
    queue = InMemoryQueueProducer()
    handler = IngestHandler(queue)
    result = await handler.handle({"data": []})
    assert result == {"success": True, "enqueued": 0}
    assert queue.items == []
