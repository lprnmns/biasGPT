import pytest

from services.api.llm.client import GroqClient
from services.api.llm.service import LLMAnalysisService


@pytest.mark.asyncio
async def test_llm_analysis_returns_results():
    client = GroqClient()
    service = LLMAnalysisService(client)
    events = [
        {"tx_hash": "0xabc", "event_type": "deposit_cex"},
        {"tx_hash": "0xdef", "event_type": "swap"},
    ]

    results = await service.analyze_events(events)
    assert len(results) == 2
    assert results[0]["event"]["tx_hash"] == "0xabc"
    assert "mocked" in results[0]["analysis"]
