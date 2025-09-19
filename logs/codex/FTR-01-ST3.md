# FTR-01-ST3

## Summary
- Added typed SQLAlchemy ORM models covering users, wallets, trading records, and supporting entities.
- Mapped relationships and indexes to align with migration schema and surfaced exports via `packages.db.models`.
- Added unit tests validating table metadata, primary keys, indexes, and relationship configuration.

## Commands
- `PYTHONPATH=. .venv/bin/pytest -q`
  - Output:
    ```
    ...ss................                                                    [100%]
    19 passed, 3 skipped in 0.64s
    ```
