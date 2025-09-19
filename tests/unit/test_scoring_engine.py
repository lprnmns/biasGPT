from datetime import timedelta

import pytest

from packages.scoring.engine import CredibilityUpdater, WalletScoringEngine
from packages.scoring.models import TradeSnapshot, WalletStats


def make_trade(pnl, minutes):
    return TradeSnapshot(pnl=pnl, entry_timestamp=0, exit_timestamp=minutes * 60, duration_minutes=minutes)


@pytest.mark.parametrize(
    "trades, expected_range",
    [
        ([make_trade(5000, 120), make_trade(-2000, 90), make_trade(3000, 60)], (0, 10)),
        ([], (4.9, 5.1)),
    ],
)
def test_score_wallet_returns_expected_range(trades, expected_range):
    engine = WalletScoringEngine()
    stats = WalletStats(
        wallet_id="wallet",
        trades=trades,
        recent_events=10,
        liquidity_utilization=0.7,
        avg_size_usd=500_000,
        false_signal_rate=0.2,
    )
    result = engine.score_wallet(stats)
    assert expected_range[0] <= result.credibility <= expected_range[1]


def test_scoring_components_sensible():
    engine = WalletScoringEngine()
    trades = [make_trade(1000, 60), make_trade(500, 80), make_trade(-200, 45)]
    stats = WalletStats(
        wallet_id="abc",
        trades=trades,
        liquidity_utilization=0.9,
        avg_size_usd=2_000_000,
        false_signal_rate=0.1,
    )
    result = engine.score_wallet(stats)
    comps = result.components
    assert 0 <= comps.historical_performance <= 10
    assert comps.trading_sophistication > comps.risk_management
    assert comps.consistency >= 3


def test_credibility_updater_adjusts_scores():
    updater = CredibilityUpdater(alpha=0.2)
    updated = updater.update(current_score=6.0, predicted=0.8, actual=0.9)
    assert updated > 6.0
    updated_down = updater.update(current_score=updated, predicted=0.9, actual=0.2)
    assert updated_down < updated
