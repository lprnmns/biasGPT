from pathlib import Path

import configparser


def test_coverage_config_has_threshold():
    config_path = Path("coverage.ini")
    assert config_path.exists(), "coverage.ini missing"

    parser = configparser.ConfigParser()
    parser.read(config_path)
    fail_under = parser.getfloat("report", "fail_under", fallback=0.0)
    assert fail_under >= 80, "Coverage threshold should be at least 80%"
