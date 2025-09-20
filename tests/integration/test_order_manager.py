import pytest

from services.api.risk.monitor import PositionSnapshot, RiskMonitor
from services.api.risk.policy import PolicyEngine, PortfolioState
from services.order_manager.killswitch import KillSwitch
from services.order_manager.okx_client import MemoryTransport, OKXClient, OKXCredentials
from services.order_manager.service import OrderManager, TradeSignal

def make_signal(**kwargs):
    data = {
        "trading_mode": "demo",
        "asset": "BTC-USDT",
        "side": "buy",
        "size_percent": 0.1,
        "leverage": 2.0,
        "rr_ratio": 2.0,
        "wallet_credibility": 6.0,
        "quantity": 0.01,
    }
    data.update(kwargs)
    return TradeSignal(**data)


def make_portfolio(**kwargs):
    data = {
        "open_positions": 1,
        "daily_trades": 1,
        "total_risk": 0.4,
        "correlation_risk": 0.3,
        "drawdown_daily": 1.0,
        "drawdown_weekly": 2.0,
        "drawdown_monthly": 5.0,
    }
    data.update(kwargs)
    return PortfolioState(**data)


def make_positions():
    return {
        "btc": PositionSnapshot(
            asset="BTC-USDT",
            side="long",
            size=0.2,
            risk=0.05,
            pnl=500,
            drawdown=1.0,
            correlation_bucket="btc",
        )
    }


def build_dependencies():
    creds = OKXCredentials(api_key="key", secret_key="secret", passphrase="pass")
    transport = MemoryTransport(response={"state": "ok"})
    okx_client = OKXClient(creds, transport=transport)

    config = {
        "single_position": {"max_size_percent": 0.25, "max_leverage": 3, "min_rr_ratio": 1.5},
        "drawdown_limits": {"daily": 3.0},
        "portfolio": {"max_open_positions": 5, "max_daily_trades": 10, "max_total_risk": 1.0, "max_correlation_risk": 0.7},
        "correlation_limits": {"same_direction": 0.7},
    }
    policy = PolicyEngine(config)

    risk_monitor = RiskMonitor(drawdown_limits={"daily": 3.0}, correlation_limit=0.7, risk_limit=1.0)
    kill_switch = KillSwitch()

    manager = OrderManager(okx_client, policy, risk_monitor, kill_switch)
    return manager, transport, kill_switch


@pytest.mark.asyncio
async def test_order_manager_submits_order():
    manager, transport, kill_switch = build_dependencies()
    signal = make_signal()
    portfolio = make_portfolio()
    positions = make_positions()

    result = await manager.submit_order(signal, portfolio, positions)
    assert result["success"] is True
    assert transport.last_call is not None


@pytest.mark.asyncio
async def test_order_manager_respects_kill_switch():
    manager, _transport, kill_switch = build_dependencies()
    kill_switch.activate("manual")
    signal = make_signal()
    portfolio = make_portfolio()
    positions = make_positions()

    result = await manager.submit_order(signal, portfolio, positions)
    assert result["success"] is False
    assert result["reason"] == "kill_switch_active"


@pytest.mark.asyncio
async def test_order_manager_policy_reject():
    manager, _transport, kill_switch = build_dependencies()
    signal = make_signal(size_percent=0.9)
    portfolio = make_portfolio()
    positions = make_positions()

    result = await manager.submit_order(signal, portfolio, positions)
    assert result["success"] is False
    assert result["reason"] == "policy_rejected"


@pytest.mark.asyncio
async def test_order_manager_risk_alert():
    manager, _transport, kill_switch = build_dependencies()
    signal = make_signal()
    portfolio = make_portfolio()
    positions = {
        "btc": PositionSnapshot(
            asset="BTC-USDT",
            side="long",
            size=0.2,
            risk=0.5,
            pnl=500,
            drawdown=4.0,
            correlation_bucket="btc",
        )
    }

    result = await manager.submit_order(signal, portfolio, positions)
    assert result["success"] is False
    assert result["reason"] == "risk_alert"
