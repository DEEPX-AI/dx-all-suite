#!/usr/bin/env bash
# setup.sh — environment setup for the YOLO26n african-wildlife retrain + DeepX benchmark.
# Uses dx-runtime/venv-dx-runtime which bundles the full stack (ultralytics[deepx] +
# dx_com + dx_engine + torch+cuda) — no separate install needed.
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
VENV="$RUNTIME_DIR/venv-dx-runtime"
PY="$VENV/bin/python"

echo "==== Setup: YOLO26n african-wildlife retrain + DeepX benchmark ===="
echo "SUITE_ROOT = $SUITE_ROOT"
echo "VENV       = $VENV"

if [ ! -x "$PY" ]; then
    echo "ERROR: $PY not found. Build dx-runtime first:"
    echo "  bash $RUNTIME_DIR/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse"
    exit 1
fi

echo "---- dx_rt sanity check (judge by TEXT OUTPUT) ----"
bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt || true

echo "---- Dependency import check (full stack) ----"
"$PY" - <<'PYEOF'
import importlib, torch
ok = True
for m in ["ultralytics", "dx_com", "dx_engine"]:
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
