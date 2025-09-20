# FTR-05-ST1

## Summary
- Implemented lightweight OKX demo client with HMAC signing and configurable in-memory transport.
- Added unit tests covering signature generation and request payload construction.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q tests/unit/test_okx_client.py`
  - Output:
    ```
    ..                                                                       [100%]
    2 passed in 0.02s
    ```
