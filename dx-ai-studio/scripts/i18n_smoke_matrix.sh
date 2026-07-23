#!/usr/bin/env bash
# Full i18n smoke: static/runtime gates + matrix coverage + optional browser audit.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PY="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY=python3

echo "== Static + runtime i18n gate =="
bash scripts/i18n_audit_gate.sh

echo ""
echo "== Module runtime refresh contracts =="
"$PY" -m pytest \
  tests/dx_app/test_runtime_lang_refresh.py \
  tests/dx_stream/test_runtime_lang_refresh.py \
  tests/dx_compiler/test_runtime_lang_refresh.py \
  tests/dx_modelzoo/test_runtime_lang_refresh.py \
  tests/dx_benchmark/test_runtime_lang_refresh.py \
  tests/dx_planner/test_runtime_lang_refresh.py \
  tests/dx_agent_dev/test_runtime_lang_refresh.py \
  tests/launcher/test_runtime_lang_refresh_contracts.py \
  tests/shared/test_lang_refresh_contracts.py \
  tests/shared/test_chat_runtime_lang_refresh.py \
  tests/i18n_audit/test_smoke_matrix_coverage.py \
  -q --tb=short

echo ""
echo "== Optional Playwright browser audit =="
bash scripts/i18n_browser_audit.sh

echo ""
echo "Manual checklist: tools/i18n_audit/browser_matrix.py::COPY_AUDIT_STATES"
echo "  13 states × 6 locales = 78 UI spot-checks"
