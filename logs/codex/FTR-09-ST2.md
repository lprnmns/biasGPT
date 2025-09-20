# FTR-09-ST2

## Summary
- Added `coverage.ini` with fail-under 80% threshold and pytest-cov dependency.
- Created coverage test to ensure configuration exists and enforces threshold.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/coverage/test_thresholds.py`
