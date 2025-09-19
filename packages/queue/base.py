"""Queue producer protocol and message definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol


@dataclass(slots=True)
class QueueEnvelope:
    """Container passed to queue implementations."""

    payload: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class QueueProducer(Protocol):
    """Async interface for producing messages to a queue."""

    async def enqueue(self, envelope: QueueEnvelope) -> None:  # pragma: no cover - interface only
        ...


__all__ = ["QueueEnvelope", "QueueProducer"]
