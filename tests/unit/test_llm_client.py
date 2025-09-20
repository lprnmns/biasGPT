import pytest

from services.api.llm.client import GroqClient, LLMRequest


@pytest.mark.asyncio
async def test_llm_client_caches_responses():
    client = GroqClient()
    request = LLMRequest(prompt="Analyze event", tier="simple")

    first = await client.generate(request)
    second = await client.generate(request)
    assert first.text == second.text
    assert first.model == "llama-3.2-3b-preview"


@pytest.mark.asyncio
async def test_llm_client_batch_generation():
    client = GroqClient()
    requests = [LLMRequest(prompt=f"Event {i}", tier="standard") for i in range(3)]

    responses = await client.batch_generate(requests)
    assert len(responses) == 3
    assert all(resp.model == "llama-3.3-70b-versatile" for resp in responses)
