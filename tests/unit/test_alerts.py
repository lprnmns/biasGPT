import json
from pathlib import Path

import pytest

from services.reporter.alerts import build_payload, load_routes, route


def test_load_routes(tmp_path: Path):
    config = tmp_path / "alerts.json"
    config.write_text(json.dumps({"critical": [{"type": "slack"}]}))
    routes = load_routes(config)
    assert "critical" in routes


def test_build_payload_classifies():
    payload = build_payload("critical", "system down", trace_id="abc")
    assert payload["level"] == "CRITICAL"
    assert payload["context"]["trace_id"] == "abc"


def test_route_returns_targets(tmp_path: Path):
    config = {"warning": [{"type": "email", "target": "ops"}]}
    results = route("warning", "budget high", routes=config, usage=0.9)
    assert results[0]["payload"]["message"] == "budget high"
    assert results[0]["payload"]["context"]["usage"] == 0.9
