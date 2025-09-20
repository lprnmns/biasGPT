from services.api.risk.monitor import PositionSnapshot, RiskMonitor
from services.order_manager.killswitch import KillSwitch


def make_position(**kwargs):
    data = {
        "asset": "BTCUSDT",
        "side": "LONG",
        "size": 0.2,
        "risk": 0.05,
        "pnl": 1000.0,
        "drawdown": 1.0,
        "correlation_bucket": "btc",
    }
    data.update(kwargs)
    return PositionSnapshot(**data)


def test_risk_monitor_alerts():
    monitor = RiskMonitor(drawdown_limits={"daily": 2.0}, correlation_limit=0.5, risk_limit=0.1)
    positions = [
        make_position(size=0.6, risk=0.06, drawdown=3.0),
        make_position(asset="ETHUSDT", size=0.5, risk=0.07, correlation_bucket="btc_same"),
    ]
    metrics = monitor.get_metrics(positions)
    assert metrics.open_positions == 2
    assert any(alert[0] == "CRITICAL" for alert in metrics.alerts)


def test_kill_switch_activation():
    killswitch = KillSwitch()
    assert killswitch.is_active() is False
    killswitch.activate("manual")
    assert killswitch.is_active() is True
    killswitch.deactivate("manual")
    assert killswitch.is_active() is False
