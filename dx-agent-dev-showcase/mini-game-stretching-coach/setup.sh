#!/bin/bash
# Environment setup for Stretch Arcade (yolo26n-pose) — DX Agent-Driven Dev
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- 1. Virtual environment detection & activation ---
# Prefer the shared dx-runtime venv (has dx_engine + GUI opencv). Search upward,
# checking both the direct-child and dx-runtime/ sibling layouts (relocatable).
RUNTIME_VENV=""
_search="$SCRIPT_DIR"
for _i in 1 2 3 4 5 6 7; do
    _search="$(dirname "$_search")"
    if [ -d "$_search/venv-dx-runtime" ]; then
        RUNTIME_VENV="$_search/venv-dx-runtime"; break
    fi
    if [ -d "$_search/dx-runtime/venv-dx-runtime" ]; then
        RUNTIME_VENV="$_search/dx-runtime/venv-dx-runtime"; break
    fi
done

LOCAL_VENV="$SCRIPT_DIR/.venv"

if [ -n "$RUNTIME_VENV" ] && [ -d "$RUNTIME_VENV" ]; then
    echo "[INFO] Activating dx-runtime venv: $RUNTIME_VENV"
    source "$RUNTIME_VENV/bin/activate"
elif [ -d "$LOCAL_VENV" ]; then
    echo "[INFO] Activating local venv: $LOCAL_VENV"
    source "$LOCAL_VENV/bin/activate"
else
    echo "[INFO] Creating local venv at $LOCAL_VENV ..."
    python3 -m venv "$LOCAL_VENV"
    source "$LOCAL_VENV/bin/activate"
    pip install --upgrade pip
    # Bridge dx_engine from the shared dx-runtime venv into this local venv so
    # `import dx_engine` works WITHOUT rebuilding it here (relocated-showcase safe).
    _rtsp=""; _d="$SCRIPT_DIR"
    while [ "$_d" != / ]; do
        for _cand in "$_d/dx-runtime/venv-dx-runtime" "$_d/venv-dx-runtime"; do
            _sp="$(ls -d "$_cand"/lib/python*/site-packages 2>/dev/null | head -1)"
            if [ -n "$_sp" ] && [ -d "$_sp/dx_engine" ]; then _rtsp="$_sp"; break; fi
        done
        [ -n "$_rtsp" ] && break; _d="$(dirname "$_d")"
    done
    _venvsp="$(ls -d "$LOCAL_VENV"/lib/python*/site-packages | head -1)"
    if [ -n "$_rtsp" ] && [ -n "$_venvsp" ]; then
        echo "$_rtsp" > "$_venvsp/dx_runtime_bridge.pth"
        echo "[INFO] bridged dx_engine: $_rtsp"
    fi
fi

# --- 2. Install dependencies (GUI OpenCV — never headless) ---
pip uninstall -y opencv-python-headless >/dev/null 2>&1 || true
pip install opencv-python numpy >/dev/null 2>&1 || pip install opencv-python numpy

# --- 2b. Vendor the shared framework so the app is PORTABLE ---
if [ ! -d "$SCRIPT_DIR/common" ]; then
    _vsrc=""; _vd="$SCRIPT_DIR"
    while [ "$_vd" != / ]; do
        if [ -d "$_vd/src/python_example/common" ]; then _vsrc="$_vd/src/python_example/common"; break; fi
        if [ -d "$_vd/dx-runtime/dx_app/src/python_example/common" ]; then _vsrc="$_vd/dx-runtime/dx_app/src/python_example/common"; break; fi
        _vd="$(dirname "$_vd")"
    done
    if [ -n "$_vsrc" ]; then
        echo "[setup] vendoring framework: $_vsrc -> ./common"
        cp -r "$_vsrc" "$SCRIPT_DIR/common"
        find "$SCRIPT_DIR/common" -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
    else
        echo "[setup] WARN: ./common absent and dx_app framework not found — 'common' imports may fail."
    fi
fi

# --- 3. Verify dx_engine ---
if ! python -c "import dx_engine" 2>/dev/null; then
    echo "[FATAL] dx_engine not available in the active venv."
    echo "  Fix: cd $(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd) && ./install.sh && ./build.sh"
    echo "  Then re-run: bash setup.sh"
    exit 1
fi
echo "[OK] dx_engine available"
echo "[INFO] Setup complete. Run: bash run.sh"
