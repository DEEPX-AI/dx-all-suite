#!/usr/bin/env bash
# Optional Playwright browser copy audit (records JSON artifacts + denylist gate).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

ARTIFACT_DIR="${DX_I18N_AUDIT_ARTIFACT_DIR:-${TMPDIR:-/tmp}/dx-i18n-browser-$$}"
export DX_I18N_AUDIT_ARTIFACT_DIR="$ARTIFACT_DIR"
mkdir -p "$ARTIFACT_DIR"

if ! python3 -c "import playwright" 2>/dev/null; then
  echo "SKIP: playwright not installed (pip install playwright && playwright install chromium)"
  exit 0
fi

VENV_PYTHON="${VENV_PYTHON:-$ROOT/.venv-i18n-audit/bin/python}"
if [ ! -x "$VENV_PYTHON" ]; then
  python3 -m venv "$ROOT/.venv-i18n-audit"
  VENV_PYTHON="$ROOT/.venv-i18n-audit/bin/python"
  "$VENV_PYTHON" -m pip install -q pytest playwright jinja2 numpy onnx
  NODE_OPTIONS=--use-system-ca "$VENV_PYTHON" -m playwright install chromium
fi

NODE_OPTIONS=--use-system-ca "$VENV_PYTHON" -m pytest tests/i18n_audit/test_browser_copy_audit.py -m smoke -q --tb=short
NODE_OPTIONS=--use-system-ca "$VENV_PYTHON" -m pytest tests/i18n_audit/test_browser_denylist.py::test_load_browser_evidence_denylist_gate -q --tb=short

echo "Browser copy audit PASSED (artifacts: $ARTIFACT_DIR)"
