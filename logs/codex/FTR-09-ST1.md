# FTR-09-ST1

## Summary
- Added Makefile test target, CI workflow, and script to run pytest in CI.
- Unit test ensures workflow and make target are present.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_ci_config.py`
