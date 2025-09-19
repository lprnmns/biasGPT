"""Wallet scoring engine implementing multi-factor model and EWMA updates."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, pstdev
from typing import Dict, Iterable, List, Sequence

from .models import ScoreComponents, TradeSnapshot, WalletStats

DEFAULT_WEIGHTS: Dict[str, float] = {
    "historical_performance": 0.35,
    "trading_sophistication": 0.25,
    "consistency": 0.15,
    "timing_quality": 0.15,
    "risk_management": 0.10,
}


@dataclass(slots=True)
class ScoringResult:
    wallet_id: str
    credibility: float
    components: ScoreComponents


class WalletScoringEngine:
    """Calculates credibility scores for whale wallets."""

    def __init__(self, weights: Dict[str, float] | None = None) -> None:
        self.weights = weights or DEFAULT_WEIGHTS

    def score_wallet(self, stats: WalletStats) -> ScoringResult:
        components = ScoreComponents(
            historical_performance=_score_historical(stats.trades),
            trading_sophistication=_score_sophistication(stats),
            consistency=_score_consistency(stats.trades),
            timing_quality=_score_timing_quality(stats.trades),
            risk_management=_score_risk_management(stats),
        )
        credibility = components.weighted_sum(self.weights)
        return ScoringResult(wallet_id=stats.wallet_id, credibility=float(round(credibility, 2)), components=components)


class CredibilityUpdater:
    """Bayesian-style credibility updater using EWMA."""

    def __init__(self, alpha: float = 0.1) -> None:
        self.alpha = alpha

    def update(self, current_score: float, predicted: float, actual: float) -> float:
        accuracy = max(0.0, min(1.0, 1 - abs(predicted - actual)))
        updated = (self.alpha * accuracy * 10) + ((1 - self.alpha) * current_score)
        return float(round(updated, 2))


# Individual factor calculations ------------------------------------------------

def _score_historical(trades: Sequence[TradeSnapshot]) -> float:
    if not trades:
        return 5.0
    positive = [t.pnl for t in trades if t.pnl > 0]
    negative = [abs(t.pnl) for t in trades if t.pnl < 0]
    if not positive:
        return 2.0
    if not negative:
        return 9.0
    win_rate = len(positive) / len(trades)
    expectancy = (win_rate * mean(positive)) - ((1 - win_rate) * mean(negative))
    return float(max(0.0, min(10.0, expectancy * 2)))


def _score_sophistication(stats: WalletStats) -> float:
    if not stats.trades:
        return 5.0
    diversity = min(1.0, stats.liquidity_utilization)
    size_factor = min(1.0, stats.avg_size_usd / 1_000_000)
    base = 3.5 + diversity * 3 + size_factor * 2.5
    return float(round(min(9.0, base), 2))


def _score_consistency(trades: Sequence[TradeSnapshot]) -> float:
    if len(trades) < 2:
        return 5.0
    durations = [t.duration_minutes for t in trades]
    volatility = pstdev(durations) if len(durations) > 1 else 0.0
    return float(max(3.0, 8.0 - min(volatility / 30, 3.0)))


def _score_timing_quality(trades: Sequence[TradeSnapshot]) -> float:
    if not trades:
        return 5.0
    holding_times = sorted(t.duration_minutes for t in trades)
    n = len(holding_times)
    if n < 4:
        return 5.0
    q1_index = max(0, int(0.25 * (n - 1)))
    q3_index = min(n - 1, int(0.75 * (n - 1)))
    spread = max(1.0, holding_times[q3_index] - holding_times[q1_index])
    return float(round(min(10.0, 7.5 / (spread / 30)), 2))


def _score_risk_management(stats: WalletStats) -> float:
    penalty_false_signals = stats.false_signal_rate * 3
    penalty_liquidity = max(0.0, (1 - stats.liquidity_utilization)) * 1.5
    score = 7.0 - (penalty_false_signals + penalty_liquidity)
    return float(round(max(2.0, min(8.0, score)), 2))


__all__ = ["WalletScoringEngine", "CredibilityUpdater", "ScoringResult"]
