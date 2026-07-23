#!/usr/bin/env bash
# Six-language copy + runtime lang-hook audit gate.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Prefer the project venv (inherited from run_ci.sh via VENV_PYTHON); fall back to python3.
PY="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY=python3

OUT_DIR="${TMPDIR:-/tmp}/dx-i18n-audit-$$"
mkdir -p "$OUT_DIR"

"$PY" -m tools.i18n_audit \
  --repo "$ROOT" \
  --output-json "$OUT_DIR/i18n.json" \
  --output-md "$OUT_DIR/i18n.md" \
  --fail-on-findings \
  --fail-on-runtime-gaps

"$PY" -m pytest tests/i18n_audit/ -q --tb=short

echo "i18n audit gate PASSED (report: $OUT_DIR/i18n.md)"
