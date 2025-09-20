from services.api.risk.policy import PolicyEngine, PortfolioState, ProposedTrade


CONFIG = {
    "single_position": {
        "max_size_percent": 0.25,
        "max_leverage": 3,
        "min_rr_ratio": 1.5,
    },
    "drawdown_limits": {
        "daily": 3.0,
    },
    "portfolio": {
        "max_open_positions": 5,
        "max_daily_trades": 10,
        "max_total_risk": 1.0,
        "max_correlation_risk": 0.7,
    },
    "correlation_limits": {
        "same_direction": 0.7,
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


def make_portfolio(**kwargs):
    data = {
        "open_positions": 2,
        "daily_trades": 3,
        "total_risk": 0.4,
        "correlation_risk": 0.3,
        "drawdown_daily": 1.0,
        "drawdown_weekly": 2.0,
        "drawdown_monthly": 5.0,
    }
    data.update(kwargs)
    return PortfolioState(**data)


def test_policy_engine_success():
    engine = PolicyEngine(CONFIG)
    trade = make_trade()
    portfolio = make_portfolio()
    passed, results = engine.validate(trade, portfolio, exposures={})
    assert passed is True
    assert all(result["passed"] for result in results.values())


def test_policy_engine_size_limit():
    engine = PolicyEngine(CONFIG)
    trade = make_trade(size_percent=0.5)
    portfolio = make_portfolio()
    passed, results = engine.validate(trade, portfolio, exposures={})
    assert passed is False
    assert results["risk_limit"]["passed"] is False


def test_policy_engine_wallet_credibility():
    engine = PolicyEngine(CONFIG)
    trade = make_trade(wallet_credibility=2.0)
    portfolio = make_portfolio()
    passed, results = engine.validate(trade, portfolio, exposures={})
    assert passed is False
    assert results["wallet_credibility"]["reason"] == "low_wallet_credibility"


def test_policy_engine_frequency_limits():
    engine = PolicyEngine(CONFIG)
    trade = make_trade()
    portfolio = make_portfolio(open_positions=5, daily_trades=10, total_risk=1.2)
    passed, results = engine.validate(trade, portfolio, exposures={})
    assert passed is False
    assert results["frequency"]["passed"] is False


def test_policy_engine_correlation_limits():
    engine = PolicyEngine(CONFIG)
    trade = make_trade()
    portfolio = make_portfolio(correlation_risk=0.9)
    exposures = {"btc_same": 0.9}
    passed, results = engine.validate(trade, portfolio, exposures=exposures)
    assert passed is False
    assert results["correlation"]["passed"] is False
