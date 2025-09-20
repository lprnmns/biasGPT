from services.api.monitoring.llm_budget import LLMBudgetManager


def test_budget_allows_within_limit():
    manager = LLMBudgetManager(daily_limit=10.0)
    assert manager.can_call(1.0) is True
    manager.track_usage(9.0)
    assert manager.can_call(1.0) is False


def test_budget_alert(monkeypatch):
    alert_messages = []
    manager = LLMBudgetManager(daily_limit=10.0, alert_sender=alert_messages.append)
    manager.track_usage(7.0)
    assert alert_messages == []
    manager.track_usage(1.5)
    assert alert_messages != []
    assert "LLM budget" in alert_messages[0]
