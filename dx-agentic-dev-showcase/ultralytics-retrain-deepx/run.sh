#!/usr/bin/env bash
# run.sh — re-run the NPU measurement for both DeepX models and refresh the metric JSONs.
# Reuses dx-runtime/venv-dx-runtime. Requires the exported *_deepx_model/ dirs to exist
# (produce them with export_deepx.py, or re-run the full build: setup.sh -> acquire.py ->
#  train.py -> export_deepx.py x2 -> this script).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# --- Auto-detect suite root (dx-runtime/ + dx-compiler/ siblings) ---
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
PYBIN="$SUITE_ROOT/dx-runtime/venv-dx-runtime/bin/python"
if [ ! -x "$PYBIN" ]; then
    echo "ERROR: venv python not found at $PYBIN — run setup.sh / build the dx-runtime venv first."
    exit 1
fi

cd "$SCRIPT_DIR"
for pair in "yolo26n_baseline_deepx_model:metrics_baseline.json:baseline" \
            "yolo26n_improved_deepx_model:metrics_improved.json:improved"; do
    DIR="${pair%%:*}"; rest="${pair#*:}"; OUT="${rest%%:*}"; TAG="${rest#*:}"
    if [ ! -d "$DIR" ]; then
        echo "ERROR: missing DeepX model dir '$DIR' — export it first (export_deepx.py)."
        exit 1
    fi
    echo "==== Measuring $TAG ($DIR) on NPU ===="
    "$PYBIN" measure.py "$DIR" "$OUT" "$TAG"
done

echo "==== verify ===="
"$PYBIN" verify.py
