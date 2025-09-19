"""Queue dependency injection helpers."""

from __future__ import annotations

from functools import lru_cache

from packages.queue import InMemoryQueueProducer, QueueProducer


@lru_cache(maxsize=1)
def _default_queue() -> QueueProducer:
    return InMemoryQueueProducer()


def get_queue() -> QueueProducer:
    return _default_queue()


__all__ = ["get_queue"]
