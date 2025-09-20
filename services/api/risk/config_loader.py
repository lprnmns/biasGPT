"""Load risk configuration from YAML-like input."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

DEFAULT_RISK_CONFIG_PATH = Path("config/risk-limits.yaml")


def _parse_raw(content: str) -> Dict[str, Any]:
    try:
        return json.loads(content)
    except json.JSONDecodeError as json_err:
        simple = _parse_simple_mapping(content)
        if simple:
            return simple
        raise ValueError("Invalid risk configuration: %s" % json_err) from json_err


def _parse_simple_mapping(content: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("{") and value.endswith("}"):
            inner = value[1:-1]
            sub: Dict[str, Any] = {}
            if inner:
                for pair in inner.split(","):
                    if ":" not in pair:
                        continue
                    sub_key, sub_val = pair.split(":", 1)
                    sub_key = sub_key.strip().strip("'\"")
                    sub_val = sub_val.strip()
                    try:
                        sub[sub_key] = float(sub_val)
                    except ValueError:
                        sub[sub_key] = sub_val
            result[key] = sub
        else:
            try:
                result[key] = float(value)
            except ValueError:
                result[key] = value
    return result


def load_risk_config(path: Path | None = None) -> Dict[str, Any]:
    target = path or DEFAULT_RISK_CONFIG_PATH
    content = target.read_text(encoding="utf-8")
    data = _parse_raw(content)
    if not isinstance(data, dict):
        raise ValueError("Risk configuration must be a mapping")
    return data


__all__ = ["load_risk_config"]
