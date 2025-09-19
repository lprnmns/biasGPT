import asyncio
import pytest

from packages.cache import TTLCache
from services.api.llm.trigger import EventContext, LLMTrigger, RateLimiter


def make_event(**kwargs):
    defaults = {
        "tx_hash": "0xabc",
        "wallet_credibility": 5.0,
        "size_frac": 0.2,
        "notional_usd": 100_000,
        "event_type": "transfer",
    }
    defaults.update(kwargs)
    return EventContext(**defaults)


def test_basic_filters_block_low_values():
    trigger = LLMTrigger()
    event = make_event(size_frac=0.05)
    assert trigger.should_trigger(event) is False


def test_pattern_cache_prevents_trigger():
    cache = TTLCache()
    trigger = LLMTrigger(cache=cache)
    event = make_event(event_type="deposit_cex", size_frac=0.3, wallet_credibility=7.0)
    assert trigger.should_trigger(event) is False  # matches pattern returning False
    assert trigger.should_trigger(event) is False  # cached


def test_rate_limit_allows_critical():
    limiter = RateLimiter(limit_per_minute=1)
    trigger = LLMTrigger(rate_limiter=limiter)
    event = make_event(size_frac=0.35)
    assert trigger.should_trigger(event) is True
    event2 = make_event(tx_hash="0xdef", size_frac=0.2)
    assert trigger.should_trigger(event2) is False


def test_expected_value_threshold():
    trigger = LLMTrigger()
    event = make_event(wallet_credibility=8.0, size_frac=0.15)
    assert trigger.should_trigger(event) is True


def test_cache_hit_shortcircuits():
    cache = TTLCache()
    cache.set("0xabc", True)
    trigger = LLMTrigger(cache=cache)
    event = make_event()
    assert trigger.should_trigger(event) is True
