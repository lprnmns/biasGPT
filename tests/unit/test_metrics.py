import pytest

from services.api.monitoring.metrics import registry, get_metrics


def test_registry_gauge_and_export():
    registry.gauge("llm_requests", 5)
    registry.gauge("positions_open", 2)
    exported = registry.export()
    assert exported["llm_requests"] == 5
    assert exported["positions_open"] == 2


@pytest.mark.asyncio
async def test_get_metrics_async():
    registry.gauge("dummy", 1)
    metrics = await get_metrics()
    assert "dummy" in metrics
