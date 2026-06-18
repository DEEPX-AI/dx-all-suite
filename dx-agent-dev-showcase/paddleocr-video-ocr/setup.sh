#!/bin/bash
# =============================================================================
# setup.sh — PP-OCRv5 video/webcam OCR app on the DEEPX DX-M1 NPU
#
# Creates a self-contained session venv, installs the two missing pure-Python
# deps (shapely, pyclipper), bridges dx_engine/numpy/cv2/PIL from the shared
# dx-runtime venv (non-invasive — no shared-venv mutation), and ensures the
# prebuilt PP-OCRv5 .dxnn models are present (downloads them if absent).
#
# Re-runnable: skips work that is already done.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"

# --- Locate the suite root (dx-runtime/ + dx-compiler/ siblings) -------------
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
VENV_DX_RUNTIME="$RUNTIME_DIR/venv-dx-runtime"
echo "[setup] SUITE_ROOT      = $SUITE_ROOT"
echo "[setup] venv-dx-runtime = $VENV_DX_RUNTIME"

# --- 1. Sanity check (NPU must be operational) -------------------------------
# Judge PASS/FAIL by the TEXT OUTPUT (never by a piped exit code). Write to a log
# file first, then grep it — piping into `grep -q` under pipefail can surface a
# spurious SIGPIPE failure from `tee`.
echo "[setup] === NPU sanity check ==="
bash "$RUNTIME_DIR/scripts/sanity_check.sh" --dx_rt > /tmp/_ocr_sanity.log 2>&1 || true
if grep -q "Sanity check PASSED!" /tmp/_ocr_sanity.log && ! grep -q "\[ERROR\]" /tmp/_ocr_sanity.log; then
    echo "[setup] NPU sanity check: PASS"
else
    echo "[setup] WARNING: NPU sanity check did not report PASS — inference may fail."
    echo "[setup] If device init failed, a cold boot (full power cycle) is required."
fi

# --- 2. Session venv ---------------------------------------------------------
VENV="$SCRIPT_DIR/venv"
if [ ! -x "$VENV/bin/python" ]; then
    echo "[setup] Creating session venv at $VENV"
    python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --quiet --upgrade pip >/dev/null 2>&1 || true

# --- 3. Pure-Python deps (shapely + pyclipper). numpy/cv2/PIL come from the
#        bridge below, so install --no-deps to avoid pulling a 2nd numpy. ------
echo "[setup] Installing shapely + pyclipper (--no-deps)"
python -m pip install --quiet --no-deps shapely pyclipper

# --- 4. dx_engine bridge: expose venv-dx-runtime site-packages (dx_engine,
#        numpy, cv2, PIL, tqdm) to this venv via a .pth file. -----------------
RT_SP="$("$VENV_DX_RUNTIME/bin/python" -c 'import site,sys; print(site.getsitepackages()[0])' 2>/dev/null || true)"
if [ -z "$RT_SP" ] || [ ! -d "$RT_SP" ]; then
    RT_SP="$(ls -d "$VENV_DX_RUNTIME"/lib/python*/site-packages 2>/dev/null | head -1)"
fi
if [ -z "$RT_SP" ] || [ ! -d "$RT_SP" ]; then
    echo "ERROR: could not locate venv-dx-runtime site-packages (dx_engine source)."
    echo "       Build the runtime: cd $RUNTIME_DIR && ./install.sh ..."
    exit 1
fi
SESSION_SP="$(python -c 'import site; print(site.getsitepackages()[0])')"
echo "$RT_SP" > "$SESSION_SP/dxengine_bridge.pth"
echo "[setup] Wrote bridge: $SESSION_SP/dxengine_bridge.pth -> $RT_SP"

# --- 5. Verify the full import surface ---------------------------------------
echo "[setup] Verifying imports (dx_engine, numpy, cv2, PIL, shapely, pyclipper)"
python - <<'PY'
import dx_engine, numpy, cv2, PIL, shapely, pyclipper
print("  dx_engine:", getattr(dx_engine, "__file__", "ok"))
print("  numpy", numpy.__version__, "| cv2", cv2.__version__,
      "| shapely", shapely.__version__, "| pyclipper ok | PIL ok")
PY

# --- 6. Models (prebuilt PP-OCRv5 .dxnn) -------------------------------------
MODEL_DIR="$SCRIPT_DIR/engine/model_files/server"
NEED=(det_v5_640.dxnn det_v5_960.dxnn textline_ori.dxnn \
      rec_v5_ratio_3.dxnn rec_v5_ratio_5.dxnn rec_v5_ratio_10.dxnn \
      rec_v5_ratio_15.dxnn rec_v5_ratio_25.dxnn rec_v5_ratio_35.dxnn ppocrv5_dict.txt)
missing=0
for m in "${NEED[@]}"; do [ -f "$MODEL_DIR/$m" ] || missing=1; done
if [ "$missing" -eq 0 ]; then
    echo "[setup] PP-OCRv5 NPU models already present in $MODEL_DIR"
else
    echo "[setup] Downloading PP-OCRv5 server models from sdk.deepx.ai (~302 MB)"
    DL="$SCRIPT_DIR/engine/model_files/download"
    mkdir -p "$DL" "$MODEL_DIR"
    # Resilient download: the CDN intermittently resets large transfers — plain
    # `curl -fsSL` fails the whole 302 MB pull on a single reset. Retry + resume (-C -).
    curl -fSL --retry 15 --retry-all-errors --retry-delay 4 -C - \
        "https://sdk.deepx.ai/res/assets/dx_baidu_PPOCR/server.tar.gz" -o "$DL/server.tar.gz"
    tar -xzf "$DL/server.tar.gz" -C "$MODEL_DIR"
    echo "[setup] Extracted models to $MODEL_DIR"
fi
ls -1 "$MODEL_DIR" | sed 's/^/[setup]   /'

echo "[setup] DONE. Activate with: source venv/bin/activate ; then ./run.sh"
