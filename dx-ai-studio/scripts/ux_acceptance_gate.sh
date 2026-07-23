#!/usr/bin/env bash
# UX acceptance gate — automated overlay/i18n/visual checks (headless).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SESSION="${ROOT}/dx-agent-dev/20260630-ux-acceptance"
mkdir -p "$SESSION"

PY="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
if [ ! -x "$PY" ]; then
  PY=python3
fi

echo "== 1/5 Static i18n gate =="
bash scripts/i18n_audit_gate.sh 2>&1 | tee "$SESSION/i18n-gate.log" | tail -3

echo ""
echo "== 2/5 Tutorial contracts =="
python3 -m pytest tests/*/test_tutorial.py -q \
  --tb=line 2>&1 | tee "$SESSION/tutorial-contracts.log" | tail -3

echo ""
echo "== 3/5 Tutorial copy locale/tone =="
python3 -m pytest tests/test_tutorial_copy_quality.py -q --tb=short \
  2>&1 | tee "$SESSION/copy-quality.log" | tail -3

if ! "$PY" -c "import playwright" 2>/dev/null; then
  echo "SKIP browser UX audits (playwright not in $PY)"
  exit 0
fi

echo ""
echo "== 4/5 iframe lang sync + tutorial lang refresh =="
"$PY" -m pytest tests/test_iframe_lang_sync_browser.py -q --tb=line \
  2>&1 | tee "$SESSION/iframe-lang.log" | tail -3

echo ""
echo "== 5/5 Tutorial E2E journey =="
"$PY" -m pytest tests/test_tutorial_e2e_journey.py -q --tb=line \
  2>&1 | tee "$SESSION/tutorial-e2e.log" | tail -3

if [ "${UX_RUN_PHASE2:-0}" = "1" ]; then
  echo ""
  echo "== Optional Phase2 full visual matrix =="
  "$PY" dx-agent-dev/20260625-094846_cursor_gpt55_tutorial_audit/run_phase2_visual_audit.py \
    --parallel 4 2>&1 | tee "$SESSION/phase2-run.log" | tail -5
  "$PY" -m pytest tests/test_ux_visual_gate.py::test_phase2_visual_audit_zero_p0_defects -q \
    --tb=short 2>&1 | tee "$SESSION/phase2-gate.log" | tail -3
fi

echo ""
echo "UX acceptance gate PASSED (artifacts: $SESSION)"
