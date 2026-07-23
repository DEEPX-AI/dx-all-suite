#!/usr/bin/env bash
# DX AI Studio CI runner — dx_app/run_tc.sh 패턴 (폐쇄망 self-hosted PR gate).
#
# Usage:
#   bash scripts/run_ci.sh              # blocking PR gate (default)
#   bash scripts/run_ci.sh --coverage # + Python coverage report (non-blocking threshold)
#   bash scripts/run_ci.sh --browser    # + Playwright browser/UX audits (needs chromium)
#   bash scripts/run_ci.sh --ux         # + full UX acceptance gate (slow, release only)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RUN_COVERAGE=0
RUN_BROWSER=0
RUN_UX=0

for arg in "$@"; do
  case "$arg" in
    --coverage) RUN_COVERAGE=1 ;;
    --browser) RUN_BROWSER=1 ;;
    --ux) RUN_UX=1 ;;
    -h|--help)
      sed -n '2,9p' "$0"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

# Prefer the project venv's interpreter if present (so no `source activate` needed);
# fall back to system python3. Test deps must already be installed there — this gate
# never pip-installs (air-gapped-safe). Export so sub-gate scripts inherit the choice.
PY="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY=python3
export VENV_PYTHON="$PY"
if ! "$PY" -c "import pytest" 2>/dev/null; then
  echo "pytest not found in: $PY" >&2
  echo "Install test deps first (once):  $PY -m pip install -r requirements-ci.txt" >&2
  echo "(or create the venv:  python3 -m venv .venv && ./.venv/bin/pip install -r requirements-ci.txt)" >&2
  exit 1
fi

# Playwright browser suites — excluded from default PR gate (install + chromium cost).
BROWSER_TESTS=(
  tests/test_iframe_lang_sync_browser.py
  tests/test_tutorial_e2e_journey.py
  tests/i18n_audit/test_browser_copy_audit.py
)
IGNORE_BROWSER=()
for _bt in "${BROWSER_TESTS[@]}"; do
  IGNORE_BROWSER+=(--ignore="$_bt")
done

echo "== 0/6 Infra + release contracts =="
"$PY" -m pytest \
  tests/test_pytest_infra_contract.py \
  tests/shared/test_ci_contracts.py \
  tests/shared/test_studio_version_contracts.py \
  tests/release/ \
  -q --tb=short

echo ""
echo "== 1/6 Collection gate =="
"$PY" -m pytest tests/ --collect-only -q \
  --ignore=tests/dx_stream/benchmark \
  "${IGNORE_BROWSER[@]}"

echo ""
echo "== 2/6 Launcher suite (isolated — port collision) =="
"$PY" -m pytest tests/launcher/ -q --tb=short

echo ""
echo "== 3/6 Agent Dev suite (isolated — port collision) =="
"$PY" -m pytest tests/dx_agent_dev/ -q --tb=short

echo ""
echo "== 4/6 i18n audit gate =="
bash scripts/i18n_audit_gate.sh

echo ""
echo "== 5/6 Module + shared + root contract suites (no browser) =="
"$PY" -m pytest \
  tests/dx_app/ \
  tests/dx_stream/ \
  tests/dx_compiler/ \
  tests/dx_modelzoo/ \
  tests/dx_planner/ \
  tests/dx_benchmark/ \
  tests/dx_monitor/ \
  tests/shared/ \
  tests/i18n_audit/ \
  tests/test_*.py \
  -q \
  --ignore=tests/dx_stream/benchmark \
  "${IGNORE_BROWSER[@]}" \
  --tb=short

if [ "$RUN_COVERAGE" = "1" ]; then
  echo ""
  echo "== Optional: Python coverage =="
  "$PY" -m pytest tests/shared/ tests/launcher/ \
    --cov=shared --cov=launcher \
    --cov-config=.coveragerc \
    --cov-report=term-missing:skip-covered \
    --cov-report=xml:coverage.xml \
    -q --tb=short
fi

if [ "$RUN_BROWSER" = "1" ]; then
  echo ""
  echo "== Optional: Playwright browser suites =="
  if ! "$PY" -c "import playwright" 2>/dev/null; then
    echo "SKIP browser (playwright not installed)" >&2
    exit 1
  fi
  bash scripts/i18n_browser_audit.sh
  "$PY" -m pytest "${BROWSER_TESTS[@]}" -q --tb=short
fi

if [ "$RUN_UX" = "1" ]; then
  echo ""
  echo "== Optional: UX acceptance gate =="
  bash scripts/ux_acceptance_gate.sh
fi

echo ""
echo "run_ci.sh PASSED"
