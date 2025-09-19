# FTR-01-ST4

## Summary
- Implemented async repository layer with shared CRUD helper and domain-specific repositories for users, wallets, events, and orders.
- Added reusable async DB fixture and integration tests (skipped in sandbox) plus updated session disposal logic to work with SQLAlchemy 2.
- Full test suite continues to pass with async-SQLite-dependent cases skipped by default.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q`
  - Output:
    ```
    .sss..ss................                                                 [100%]
    19 passed, 6 skipped in 0.64s
    ```
