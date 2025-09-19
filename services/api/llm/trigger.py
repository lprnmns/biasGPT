"""LLM trigger decision logic following budget constraints."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Optional

from packages.cache import TTLCache


@dataclass(slots=True)
class EventContext:
    tx_hash: str
    wallet_credibility: float
    size_frac: float
    notional_usd: float
    event_type: str


PATTERN_LIBRARY: Dict[str, Dict[str, object]] = {
    "whale_cex_deposit": {
        "conditions": {
            "event_type": "deposit_cex",
            "size_frac": 0.25,
            "wallet_credibility": 6.0,
        },
        "decision": False,
        "ttl": 3600,
    }
}


class RateLimiter:
    def __init__(self, limit_per_minute: int = 20) -> None:
        self.limit_per_minute = limit_per_minute
        self.calls: list[float] = []

    def record(self) -> None:
        now = time.time()
        self.calls.append(now)
        self.calls = [ts for ts in self.calls if now - ts < 60]

    def exceeds(self) -> bool:
        now = time.time()
        self.calls = [ts for ts in self.calls if now - ts < 60]
        return len(self.calls) >= self.limit_per_minute


class LLMTrigger:
    def __init__(self, cache: Optional[TTLCache] = None, rate_limiter: Optional[RateLimiter] = None) -> None:
        self.cache = cache or TTLCache()
        self.rate_limiter = rate_limiter or RateLimiter()

    def should_trigger(self, event: EventContext) -> bool:
        if not self._passes_basic_filters(event):
            return False
        cached = self.cache.get(event.tx_hash)
        if cached is not None:
            return cached
        pattern_hit = self._matches_pattern(event)
        if pattern_hit is False:
            self.cache.set(event.tx_hash, False, ttl=300)
            return False
        critical = event.size_frac > 0.30
        if self.rate_limiter.exceeds() and not critical:
            return False
        expected_value = self._expected_value(event)
        decision = expected_value > 0.05
        self.cache.set(event.tx_hash, decision, ttl=300)
        if decision:
            self.rate_limiter.record()
        return decision

    def _passes_basic_filters(self, event: EventContext) -> bool:
        return event.size_frac >= 0.10 and event.wallet_credibility >= 3.0 and event.notional_usd >= 50_000

    def _matches_pattern(self, event: EventContext) -> Optional[bool]:
        pattern = PATTERN_LIBRARY.get("whale_cex_deposit")
        if not pattern:
            return None
        conditions = pattern.get("conditions", {})
        if (
            event.event_type == conditions.get("event_type")
            and event.size_frac > conditions.get("size_frac", 0)
            and event.wallet_credibility > conditions.get("wallet_credibility", 0)
        ):
            decision = bool(pattern.get("decision", False))
            self.cache.set(event.tx_hash, decision, ttl=float(pattern.get("ttl", 3600)))
            return decision
        return None

    def _expected_value(self, event: EventContext) -> float:
        base = min(1.0, event.size_frac * (event.wallet_credibility / 10))
        return base


__all__ = ["LLMTrigger", "EventContext", "RateLimiter"]
