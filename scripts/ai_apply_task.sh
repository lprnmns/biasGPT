#!/usr/bin/env bash
set -euo pipefail
ID="${1:?usage: ai_apply_task.sh <SUBTASK_ID>}"
BR="ai/$ID"
git checkout -b "$BR" 2>/dev/null || git checkout "$BR"
CTX="$(mktemp)"
yq ".subtasks[] | select(.id==\"$ID\")" planning/subtasks.yaml > "$CTX"
# ADAPT: sadece unified diff üreten codex çağrısı
codex --input "$CTX" docs/API.md docs/Architecture.md \
      --prompt prompts/codex_apply_task.txt \
      --diff > /tmp/patch.diff
git apply --whitespace=fix /tmp/patch.diff
python -m pip install -U pip pytest >/dev/null 2>&1 || true
[ -f requirements.txt ] && pip install -r requirements.txt || true
pytest -q || true
git add -A
git commit -m "feat($ID): implement + tests"
gh pr create -f -t "$ID" -b "Auto by Codex" -l auto-merge
