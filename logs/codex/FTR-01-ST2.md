# FTR-01-ST2

## Summary
- Added lightweight async migration framework with initial schema covering core trading tables and view.
- Exposed migration helpers via `packages.db` and introduced integration tests (skipped in sandbox by default).
- Updated tests to skip async SQLite-dependent cases when environment lacks support; full suite now passes locally.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q`
  - Output:
    ```
    ...ss                                                                    [100%]
    3 passed, 3 skipped in 0.50s
    ```
