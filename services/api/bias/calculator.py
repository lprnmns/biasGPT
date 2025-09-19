"""Bias calculation utilities combining wallet scores and events."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Iterable

from packages.scoring.engine import WalletScoringEngine
from packages.scoring.models import WalletStats


@dataclass(slots=True)
class BiasResult:
    asset: str
    timeframe: str
    value: float
    confidence: float
    components: Dict[str, float]
    timestamp: datetime


class BiasCalculator:
    def __init__(self, scoring_engine: WalletScoringEngine | None = None) -> None:
        self.scoring_engine = scoring_engine or WalletScoringEngine()

    def calculate(self, asset: str, timeframe: str, wallets: Iterable[WalletStats]) -> BiasResult:
        scores = [self.scoring_engine.score_wallet(stats) for stats in wallets]
        if not scores:
            return BiasResult(
                asset=asset,
                timeframe=timeframe,
                value=0.0,
                confidence=0.0,
                components={},
                timestamp=datetime.now(timezone.utc),
            )

        weights = [max(0.1, result.credibility / 10) for result in scores]
        total_weight = sum(weights)
        weighted_bias = sum((result.credibility - 5) / 5 * w for result, w in zip(scores, weights)) / total_weight
        confidence = min(1.0, total_weight / len(scores))
        components = {result.wallet_id: result.credibility for result in scores}

        return BiasResult(
            asset=asset,
            timeframe=timeframe,
            value=float(round(weighted_bias, 3)),
            confidence=float(round(confidence, 2)),
            components=components,
            timestamp=datetime.now(timezone.utc),
        )


__all__ = ["BiasCalculator", "BiasResult"]
