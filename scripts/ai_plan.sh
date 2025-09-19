#!/usr/bin/env bash
set -euo pipefail
# ADAPT: codex CLI argümanlarını kendi sürümüne göre düzenle
codex --input docs/PRD.md docs/Architecture.md docs/API.md docs/TestStrategy.md \
      --prompt prompts/codex_split_tasks.txt \
      --output planning/tasks.yaml,planning/subtasks.yaml
