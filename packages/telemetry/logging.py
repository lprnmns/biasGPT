"""Structured logging helper."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict


def log(level: str, message: str, **fields: Any) -> str:
    record: Dict[str, Any] = {
        "timestamp": datetime.utcnow().isoformat(),
        "level": level.upper(),
        "message": message,
        **fields,
    }
    line = json.dumps(record, sort_keys=True)
    print(line)
    return line


__all__ = ["log"]
