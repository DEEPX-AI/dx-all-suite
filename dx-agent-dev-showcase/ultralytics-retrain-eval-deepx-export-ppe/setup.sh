#!/usr/bin/env bash
# setup.sh — environment setup for the YOLO26n construction-PPE retrain + DeepX 4-way benchmark.
# Resolves a FULL-STACK venv (ultralytics[deepx] + dx_com + dx_engine + torch+cuda) and persists
# the resolved interpreter to .venv_path for run.sh / verify.py to reuse.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Auto-detect suite root (walks up until dx-runtime/ and dx-compiler/ siblings are found)
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: Cannot find dx-all-suite root (expected dx-runtime/ and dx-compiler/ siblings)"
    exit 1
fi
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"

echo "==== Setup: YOLO26n construction-PPE retrain + DeepX 4-way benchmark ===="
echo "SUITE_ROOT = $SUITE_ROOT"

echo "---- dx_rt sanity check (judge by TEXT OUTPUT, not exit code) ----"
bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt 2>&1 | grep -Ei "PASS|FAIL|ERROR|device-id|Driver Version|Firmware" || true

# Candidate full-stack venvs (first that imports the whole stack wins).
CANDIDATES=(
    "$RUNTIME_DIR/venv-dx-runtime/bin/python"
    "$SUITE_ROOT/.deepx/e2e/venv/bin/python"
    "$SUITE_ROOT/dx-compiler/venv-dx-compiler-local/bin/python"
)

PY=""
for cand in "${CANDIDATES[@]}"; do
    [ -x "$cand" ] || continue
    if "$cand" - <<'PYEOF' >/dev/null 2>&1
import importlib
for m in ("ultralytics","dx_com","dx_engine","torch"):
    importlib.import_module(m)
import torch; assert torch.cuda.is_available()
PYEOF
    then PY="$cand"; break; fi
done

if [ -z "$PY" ]; then
    echo "ERROR: No full-stack venv found (need ultralytics + dx_com + dx_engine + torch+cuda)."
    echo "Build dx-runtime full stack, e.g.:"
    echo "  bash $RUNTIME_DIR/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse"
    exit 1
fi

echo "$PY" > "$SCRIPT_DIR/.venv_path"
echo "Resolved full-stack interpreter: $PY"

echo "---- Dependency import check (full stack) ----"
"$PY" - <<'PYEOF'
import importlib, torch
ok = True
for m in ("ultralytics","dx_com","dx_engine"):
    try:
        mod = importlib.import_module(m)
        print(f"  {m}: OK {getattr(mod,'__version__','?')}")
    except Exception as e:
        print(f"  {m}: MISSING {e!r}"); ok = False
print(f"  torch: {torch.__version__} cuda={torch.cuda.is_available()} "
      f"{torch.cuda.get_device_name(0) if torch.cuda.is_available() else ''}")
import sys; sys.exit(0 if ok else 1)
PYEOF

echo "==== Setup complete ===="
