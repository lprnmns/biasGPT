#!/usr/bin/env bash
set -euo pipefail

PYTHONPATH=.:$PYTHONPATH python -m pytest -q
