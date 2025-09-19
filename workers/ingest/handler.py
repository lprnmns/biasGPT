"""Core logic for the ingest worker (shared with Cloudflare deployment)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Sequence

from packages.queue import QueueEnvelope, QueueProducer


@dataclass(slots=True)
class NormalizedEvent:
    """Minimal event representation sent to downstream services."""

    tx_hash: str
    wallet_address: str
    event_type: str
    timestamp: str
    asset: str | None
    amount: float | None
    notional_usd: float | None
    raw: Dict[str, Any]

    def to_payload(self) -> Dict[str, Any]:
        return {
            "tx_hash": self.tx_hash,
            "wallet_address": self.wallet_address,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "asset": self.asset,
            "amount": self.amount,
            "notional_usd": self.notional_usd,
            "raw": self.raw,
        }


class IngestHandler:
    """Processes webhook payloads and enqueues normalized events."""

    def __init__(self, queue: QueueProducer, *, source: str = "alchemy") -> None:
        self.queue = queue
        self.source = source

    async def handle(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        events = list(_extract_events(payload))
        if not events:
            return {"success": True, "enqueued": 0}

        dedup: set[str] = set()
        enqueued = 0
        received_at = datetime.now(timezone.utc).isoformat()

        for raw_event in events:
            normalized = _normalize_event(raw_event)
            if normalized.tx_hash in dedup:
                continue
            dedup.add(normalized.tx_hash)

            metadata = {
                "source": self.source,
                "received_at": received_at,
                "schema": "event.v1",
            }
            envelope = QueueEnvelope(payload=normalized.to_payload(), metadata=metadata)
            await self.queue.enqueue(envelope)
            enqueued += 1

        return {"success": True, "enqueued": enqueued}


def _extract_events(payload: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    if "events" in payload and isinstance(payload["events"], Sequence):
        return (e for e in payload["events"] if isinstance(e, dict))
    if "data" in payload and isinstance(payload["data"], Sequence):
        return (e for e in payload["data"] if isinstance(e, dict))
    return []


def _normalize_event(event: Dict[str, Any]) -> NormalizedEvent:
    tx_hash = str(event.get("txHash") or event.get("tx_hash") or "").lower()
    wallet = str(event.get("wallet") or event.get("fromAddress") or event.get("address") or "").lower()
    if not tx_hash or not wallet:
        raise ValueError("Event missing tx hash or wallet address")

    timestamp = _coerce_timestamp(event.get("timestamp"))
    amount = _coerce_decimal(event.get("amount") or event.get("value") or event.get("quantities"))
    notional = _coerce_decimal(event.get("notionalUsd"))
    asset = event.get("asset") or event.get("tokenSymbol")
    event_type = str(event.get("category") or event.get("type") or "unknown")

    return NormalizedEvent(
        tx_hash=tx_hash,
        wallet_address=wallet,
        event_type=event_type,
        timestamp=timestamp,
        asset=asset,
        amount=amount,
        notional_usd=notional,
        raw=event,
    )


def _coerce_timestamp(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    if isinstance(value, (int, float)):
        return datetime.fromtimestamp(float(value), tz=timezone.utc).isoformat()
    if isinstance(value, str) and value:
        try:
            # Attempt ISO parse
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            return parsed.astimezone(timezone.utc).isoformat()
        except ValueError:
            pass
    return datetime.now(timezone.utc).isoformat()


def _coerce_decimal(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(Decimal(value))
        except (ArithmeticError, ValueError):
            return None
    if isinstance(value, (list, tuple)) and value:
        return _coerce_decimal(value[0])
    return None


__all__ = ["IngestHandler", "NormalizedEvent"]
