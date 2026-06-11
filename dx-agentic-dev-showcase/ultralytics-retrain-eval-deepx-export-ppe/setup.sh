#!/usr/bin/env bash
# setup.sh — environment setup + sanity check for the PPE retrain/export/eval session.
# Uses the suite's prebuilt venv-dx-runtime (full stack: ultralytics + torch+cuda +
# dx_com + dx_engine). Does NOT pip-install dx_engine (a dx_rt build artifact).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Cross-project path resolution: auto-detect suite root (SUITE_ROOT pattern) ---
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

echo "=== PPE retrain/export/eval — setup ==="
echo "SUITE_ROOT = $SUITE_ROOT"
echo "VENV       = $VENV"

if [ ! -x "$VENV/bin/python" ]; then
    echo "ERROR: venv-dx-runtime not found at $VENV"
    echo "Build dx_rt first: bash $RUNTIME_DIR/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse"
    exit 1
fi
PY="$VENV/bin/python"

echo "--- Stack sanity ---"
"$PY" - <<'PYEOF'
import sys
def chk(label, fn):
    try:
        print(f"[OK] {label}: {fn()}")
    except Exception as e:
        print(f"[ERROR] {label}: {e}"); raise
chk("python", lambda: sys.version.split()[0])
import ultralytics; chk("ultralytics", lambda: ultralytics.__version__)
import torch; chk("torch", lambda: f"{torch.__version__} cuda={torch.cuda.is_available()} dev={torch.cuda.get_device_name(0) if torch.cuda.is_available() else '-'}")
import dx_com; chk("dx_com", lambda: getattr(dx_com,'__version__','?'))
import dx_engine; chk("dx_engine", lambda: "import OK")
import os
p = os.path.join(os.path.dirname(ultralytics.__file__), "cfg", "datasets", "construction-ppe.yaml")
chk("construction-ppe.yaml", lambda: ("found" if os.path.exists(p) else (_ for _ in ()).throw(FileNotFoundError(p))))
PYEOF

echo "--- NPU sanity check (dx_rt) ---"
bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt 2>&1 | grep -E "Sanity check (PASSED|FAILED)" || true

echo "=== setup complete ==="
