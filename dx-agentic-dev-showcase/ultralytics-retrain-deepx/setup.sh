#!/usr/bin/env bash
# setup.sh — environment setup + sanity for the YOLO26n African-wildlife DeepX showcase.
# Reuses dx-runtime/venv-dx-runtime (carries ultralytics[deepx fork] + dx_com + dx_engine + torch+cuda).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Auto-detect suite root (walks up until dx-runtime/ and dx-compiler/ siblings exist) ---
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: cannot find dx-all-suite root (expected dx-runtime/ and dx-compiler/ siblings)"
    exit 1
fi
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
VENV="$RUNTIME_DIR/venv-dx-runtime"
PYBIN="$VENV/bin/python"

echo "==== Showcase setup ===="
echo "SUITE_ROOT = $SUITE_ROOT"
echo "VENV       = $VENV"

if [ ! -x "$PYBIN" ]; then
    echo "ERROR: $PYBIN not found. The dx-runtime venv must be built first:"
    echo "  bash $RUNTIME_DIR/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse"
    exit 1
fi

echo "==== Dependency import asserts ===="
"$PYBIN" - <<'PY'
import sys
ok = True
def chk(name, fn):
    global ok
    try:
        v = fn()
        print(f"[OK] {name}: {v}")
    except Exception as e:
        ok = False
        print(f"[FAIL] {name}: {e}")

def _ultra():
    import ultralytics, os
    p = os.path.dirname(ultralytics.__file__)
    assert os.path.exists(os.path.join(p, "utils", "export", "deepx.py")), "deepx exporter missing"
    from ultralytics.engine.exporter import export_formats
    assert "deepx" in list(export_formats()["Argument"]), "deepx not in export formats"
    return f"{ultralytics.__version__} (deepx export present)"

chk("ultralytics[deepx]", _ultra)
chk("dx_com", lambda: __import__("dx_com").__file__)
chk("dx_engine", lambda: __import__("dx_engine").__file__)
def _torch():
    import torch
    assert torch.cuda.is_available(), "CUDA not available"
    return f"{torch.__version__} cuda={torch.cuda.get_device_name(0)}"
chk("torch+cuda", _torch)
sys.exit(0 if ok else 1)
PY

echo "==== NPU sanity check (dx_rt) ===="
# Judge PASS/FAIL by TEXT OUTPUT, not exit code (do not pipe through tail/head/grep for the verdict).
SANITY_OUT="$("$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt 2>&1)"
echo "$SANITY_OUT"
if echo "$SANITY_OUT" | grep -q "Sanity check PASSED!"; then
    echo "[OK] NPU sanity PASSED"
else
    echo "[FAIL] NPU sanity did not PASS — NPU measurement cannot proceed (cold boot may be required)."
    exit 1
fi

echo "==== setup.sh complete ===="
