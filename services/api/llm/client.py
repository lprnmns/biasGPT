"""Groq client wrapper with tiered model selection and batching hooks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from packages.cache import TTLCache


GROQ_MODEL_TIERS: Dict[str, Dict[str, Any]] = {
    "critical": {"model": "llama-4-maverick-17b-128e-instruct", "temperature": 0.1, "max_tokens": 500},
    "standard": {"model": "llama-3.3-70b-versatile", "temperature": 0.3, "max_tokens": 200},
    "simple": {"model": "llama-3.2-3b-preview", "temperature": 0.5, "max_tokens": 100},
}


@dataclass(slots=True)
class LLMRequest:
    prompt: str
    tier: str = "standard"
    metadata: Optional[Dict[str, Any]] = None


@dataclass(slots=True)
class LLMResponse:
    text: str
    tokens_used: int
    model: str


class GroqClient:
    def __init__(self, cache: Optional[TTLCache] = None, *, daily_budget: float = 10.0) -> None:
        self.cache = cache or TTLCache(default_ttl=3600)
        self.daily_budget = daily_budget
        self.spend = 0.0

    async def generate(self, request: LLMRequest) -> LLMResponse:
        cached = self.cache.get(request.prompt)
        if cached:
            return cached
        tier = GROQ_MODEL_TIERS.get(request.tier, GROQ_MODEL_TIERS["standard"])
        mock_text = f"[mocked-{tier['model']}] {request.prompt[:50]}"
        response = LLMResponse(text=mock_text, tokens_used=tier["max_tokens"], model=tier["model"])
        self.cache.set(request.prompt, response)
        return response

    async def batch_generate(self, requests: Iterable[LLMRequest]) -> List[LLMResponse]:
        return [await self.generate(req) for req in requests]


__all__ = ["GroqClient", "LLMRequest", "LLMResponse"]
