"""Alert routing utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ALERTS_CONFIG_PATH = Path("config/alerts/routes.json")


def load_routes(path: Path | None = None) -> Dict[str, List[Dict[str, Any]]]:
    target = path or ALERTS_CONFIG_PATH
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Alerts configuration must be a mapping")
    return data


def classify(level: str, message: str) -> str:
    return level.upper()


def build_payload(level: str, message: str, **context: Any) -> Dict[str, Any]:
    payload = {"level": classify(level, message), "message": message, "context": context}
    return payload


def route(level: str, message: str, *, routes: Dict[str, List[Dict[str, Any]]] | None = None, **context: Any) -> List[Dict[str, Any]]:
    config = routes or load_routes()
    payload = build_payload(level, message, **context)
    return [{**target, "payload": payload} for target in config.get(level, [])]


__all__ = ["load_routes", "route", "build_payload"]
