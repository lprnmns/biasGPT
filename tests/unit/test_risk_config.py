from pathlib import Path

import pytest

from services.api.risk.config_loader import load_risk_config


def test_load_risk_config(tmp_path: Path):
    sample = tmp_path / "risk.yaml"
    sample.write_text("single_position: {max_size_percent: 0.5}")
    config = load_risk_config(sample)
    assert config["single_position"]["max_size_percent"] == 0.5


def test_load_risk_config_invalid(tmp_path: Path):
    sample = tmp_path / "risk.yaml"
    sample.write_text("[]")
    with pytest.raises(ValueError):
        load_risk_config(sample)
