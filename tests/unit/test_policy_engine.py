from services.api.risk.policy import PolicyEngine, ProposedTrade


CONFIG = {
    "single_position": {
        "max_size_percent": 0.25,
        "max_leverage": 3,
        "min_rr_ratio": 1.5,
    },
    "drawdown_limits": {
        "daily": 3.0,
    },
}


def make_trade(**kwargs):
    data = {
        "trading_mode": "demo",
        "asset": "BTCUSDT",
        "side": "LONG",
        "size_percent": 0.1,
        "leverage": 2,
        "rr_ratio": 2.0,
        "wallet_credibility": 5.0,
    }
    data.update(kwargs)
    return ProposedTrade(**data)


def test_policy_engine_success():
    engine = PolicyEngine(CONFIG)
    trade = make_trade()
    passed, results = engine.validate(trade)
    assert passed is True
    assert all(result["passed"] for result in results.values())


def test_policy_engine_size_limit():
    engine = PolicyEngine(CONFIG)
    trade = make_trade(size_percent=0.5)
    passed, results = engine.validate(trade)
    assert passed is False
    assert results["risk_limit"]["passed"] is False


def test_policy_engine_wallet_credibility():
    engine = PolicyEngine(CONFIG)
    trade = make_trade(wallet_credibility=2.0)
    passed, results = engine.validate(trade)
    assert passed is False
    assert results["wallet_credibility"]["reason"] == "low_wallet_credibility"
