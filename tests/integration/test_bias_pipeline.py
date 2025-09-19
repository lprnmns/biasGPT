from datetime import datetime, timezone

import pytest

from packages.scoring.models import TradeSnapshot, WalletStats
from services.api.bias.calculator import BiasCalculator
from services.api.bias.repository import BiasRepository
from services.api.routes.bias import get_bias


def make_stats(wallet_id: str, pnl_values: list[float]) -> WalletStats:
    trades = [
        TradeSnapshot(
            pnl=pnl,
            entry_timestamp=0.0,
            exit_timestamp=60.0,
            duration_minutes=60.0,
        )
        for pnl in pnl_values
    ]
    return WalletStats(
        wallet_id=wallet_id,
        trades=trades,
        liquidity_utilization=0.8,
        avg_size_usd=750_000,
        false_signal_rate=0.15,
    )


@pytest.mark.asyncio
async def test_bias_calculation_and_route_response():
    calculator = BiasCalculator()
    stats = [make_stats("wallet-a", [5000, -1000, 2000]), make_stats("wallet-b", [3000, 2500])]
    result = calculator.calculate("BTC", "1h", stats)

    repo = BiasRepository()
    await repo.store(result)

    response = await get_bias(repo)
    assert response["success"] is True
    assert len(response["data"]) == 1
    entry = response["data"][0]
    assert entry["asset"] == "BTC"
    assert entry["timeframe"] == "1h"
    assert isinstance(entry["value"], float)
    datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))


@pytest.mark.asyncio
async def test_bias_calculator_handles_empty_wallets():
    calculator = BiasCalculator()
    result = calculator.calculate("ETH", "4h", [])
    assert result.value == 0.0
    assert result.confidence == 0.0
