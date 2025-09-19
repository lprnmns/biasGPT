"""Data models for the scoring engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional


@dataclass(slots=True)
class TradeSnapshot:
    pnl: float
    entry_timestamp: float
    exit_timestamp: float
    duration_minutes: float


@dataclass(slots=True)
class WalletStats:
    wallet_id: str
    trades: List[TradeSnapshot] = field(default_factory=list)
    recent_events: int = 0
    liquidity_utilization: float = 0.0
    avg_size_usd: float = 0.0
    false_signal_rate: float = 0.0


@dataclass(slots=True)
class ScoreComponents:
    historical_performance: float
    trading_sophistication: float
    consistency: float
    timing_quality: float
    risk_management: float

    def weighted_sum(self, weights: Dict[str, float]) -> float:
        return sum(getattr(self, key) * weights[key] for key in weights)


__all__ = ["TradeSnapshot", "WalletStats", "ScoreComponents"]
