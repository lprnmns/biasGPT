"""Testing-friendly in-memory queue producer."""

from __future__ import annotations

from collections import deque
from typing import Deque, List

from .base import QueueEnvelope, QueueProducer


class InMemoryQueueProducer(QueueProducer):
    """Stores envelopes in memory for assertions."""

    def __init__(self) -> None:
        self._items: Deque[QueueEnvelope] = deque()

    async def enqueue(self, envelope: QueueEnvelope) -> None:
        self._items.append(envelope)

    def drain(self) -> List[QueueEnvelope]:
        items = list(self._items)
        self._items.clear()
        return items

    @property
    def items(self) -> List[QueueEnvelope]:
        return list(self._items)


__all__ = ["InMemoryQueueProducer"]
