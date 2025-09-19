"""Bias endpoints returning latest bias vectors."""

from __future__ import annotations

from datetime import datetime
from typing import List

try:  # pragma: no cover - optional FastAPI dependency
    from fastapi import APIRouter, Depends, status
except ModuleNotFoundError:  # pragma: no cover - fallback for test environment without FastAPI
    class APIRouter:  # type: ignore
        def __init__(self, *_, **__):
            pass

        def get(self, *_args, **_kwargs):
            def decorator(func):
                return func

            return decorator

    class _Status:
        HTTP_200_OK = 200

    status = _Status()  # type: ignore

    def Depends(factory):  # type: ignore
        return factory

from services.api.bias.repository import BiasRepository

router = APIRouter(prefix="/v1", tags=["bias"])


async def _serialize(result) -> dict:
    return {
        "asset": result.asset,
        "timeframe": result.timeframe,
        "value": result.value,
        "confidence": result.confidence,
        "timestamp": result.timestamp.isoformat(),
        "components": result.components,
    }


@router.get("/bias", status_code=status.HTTP_200_OK)
async def get_bias(repo: BiasRepository = Depends(BiasRepository)) -> dict:
    results = await repo.latest()
    data = [await _serialize(result) for result in results]
    return {"success": True, "data": data}


__all__ = ["router"]
