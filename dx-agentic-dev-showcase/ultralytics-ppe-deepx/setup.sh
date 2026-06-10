#!/usr/bin/env bash
# Environment setup for the YOLO26n construction-PPE retrain -> DeepX 4-way benchmark.
# Reuses dx-runtime/venv-dx-runtime, which already carries the full stack
# (ultralytics + torch-cuda + dx_com + dx_engine). No system pip installs (PEP 668 safe).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Auto-detect the suite root (dx-runtime/ and dx-compiler/ siblings) — never hardcode ../../
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
echo "[setup] SUITE_ROOT=$SUITE_ROOT"
echo "[setup] VENV=$VENV"

# 1. venv presence — it is built by dx-runtime/install.sh (provides dx_engine too)
if [ ! -x "$VENV/bin/python" ]; then
    echo "ERROR: $VENV not found. Build it with:"
    echo "  bash $RUNTIME_DIR/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse"
    exit 1
fi
PY="$VENV/bin/python"

# 2. dependency check — ultralytics (train/export/eval) + dx_com (compile) + dx_engine (NPU)
echo "[setup] checking ML stack ..."
"$PY" - <<'PYEOF'
import importlib, sys
mods = {"ultralytics": "ultralytics", "torch": "torch",
        "dx_com": "dx_com (DeepX compiler)", "dx_engine": "dx_engine (NPU runtime)"}
ok = True
for m, label in mods.items():
    try:
        mod = importlib.import_module(m)
        ver = getattr(mod, "__version__", "?")
        print(f"  [OK] {label} {ver}")
    except Exception as e:
        print(f"  [MISSING] {label}: {e}"); ok = False
import torch
print(f"  [INFO] CUDA available: {torch.cuda.is_available()} "
      f"({torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu only'})")
sys.exit(0 if ok else 1)
PYEOF

# 3. DeepX runtime / NPU sanity (needed for the INT8 .dxnn evaluation)
# NOTE: sanity_check.sh returns a non-zero exit code even on PASS, so judge by the
# TEXT OUTPUT (per suite CLAUDE.md), never by exit status / a pipefail-carried code.
echo "[setup] dx_rt sanity check (NPU) ..."
bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt > "$SCRIPT_DIR/sanity_check.log" 2>&1 || true
if grep -q "Sanity check PASSED!" "$SCRIPT_DIR/sanity_check.log"; then
    echo "[setup] NPU sanity: PASS"
else
    echo "[setup] WARNING: NPU sanity check did not report PASS — INT8 .dxnn eval may fail."
    echo "        See sanity_check.log; a cold boot may be required for NPU init."
fi

echo "[setup] done. Run ./run.sh to reproduce the benchmark."
