# FTR-05-ST2

## Summary
- Added order manager orchestrator integrating policy checks, risk monitoring, kill switch, and OKX client.
- Wrote integration tests covering successful submissions, kill switch blocks, policy rejections, and risk alerts.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_okx_client.py tests/integration/test_order_manager.py`
  - Output:
    ```
    ......                                                                   [100%]
    6 passed in 1.10s
    ```
