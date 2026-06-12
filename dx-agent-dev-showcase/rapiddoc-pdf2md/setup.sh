#!/bin/bash
# =============================================================================
# setup.sh — Provision the RapidDoc PDF->Markdown app on the DX-M1 NPU
#
# Steps (idempotent; safe to re-run):
#   1. Auto-detect the dx-all-suite root (SUITE_ROOT).
#   2. Clone DEEPX-AI/RapidDoc @ rapid_doc_deepx FRESH into ./RapidDoc.
#   3. Create a session-local venv and bridge dx_engine (the DX-M1 NPU binding)
#      from dx-runtime/venv-dx-runtime via a .pth file (no shared-venv mutation).
#   4. pip install the fork's requirements + editable package.
#   5. Run the fork's own ./setup.sh in the FOREGROUND to download the prebuilt
#      onnx_models/ + dxnn_models/ (NEVER hand-compile with dxcom; NEVER background).
#   6. Pick a bundled sample PDF as sample_input.pdf.
#
# Per KB (paddleocr-rapiddoc-app.md): RapidDoc ships its OWN NPU pipeline, so this
# is a standalone app (NOT IFactory/SyncRunner). Models come from ./setup.sh.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"

# --- 1. Auto-detect suite root (dx-runtime/ + dx-compiler/ siblings) ----------
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
RUNTIME_VENV="$RUNTIME_DIR/venv-dx-runtime"
echo "[setup] SUITE_ROOT = $SUITE_ROOT"

# --- 0. Sanity: NPU must be present ------------------------------------------
echo "[setup] Checking NPU (dxrt-cli -s) ..."
if command -v dxrt-cli >/dev/null 2>&1; then
    dxrt-cli -s | head -5 || true
else
    echo "[setup] WARNING: dxrt-cli not on PATH; assuming DX-RT installed system-wide."
fi

# --- 2. Clone RapidDoc fork (idempotent) -------------------------------------
FORK_DIR="$SCRIPT_DIR/RapidDoc"
FORK_BRANCH="rapid_doc_deepx"
if [ -d "$FORK_DIR/.git" ]; then
    echo "[setup] RapidDoc already cloned -> $FORK_DIR"
else
    echo "[setup] Cloning DEEPX-AI/RapidDoc @ $FORK_BRANCH ..."
    git clone --depth 1 -b "$FORK_BRANCH" https://github.com/DEEPX-AI/RapidDoc.git "$FORK_DIR"
fi

# --- 3. Session venv + dx_engine bridge --------------------------------------
VENV="$SCRIPT_DIR/venv"
if [ ! -x "$VENV/bin/python" ]; then
    echo "[setup] Creating session venv -> $VENV"
    python3 -m venv "$VENV"
fi
# shellcheck disable=SC1091
source "$VENV/bin/activate"
python -m pip install --upgrade pip wheel setuptools >/dev/null

# Bridge dx_engine (NPU binding) from the shared runtime venv. Appended to the
# END of sys.path, so locally-installed fork deps always take precedence; only
# dx_engine (absent locally) resolves from the runtime venv.
if [ -d "$RUNTIME_VENV" ]; then
    RT_SP="$("$RUNTIME_VENV/bin/python" -c 'import site,sys; print(site.getsitepackages()[0])')"
    SESS_SP="$(python -c 'import site,sys; print(site.getsitepackages()[0])')"
    echo "$RT_SP" > "$SESS_SP/dxengine_bridge.pth"
    echo "[setup] dx_engine bridge: $SESS_SP/dxengine_bridge.pth -> $RT_SP"
else
    echo "[setup] WARNING: $RUNTIME_VENV not found; dx_engine may be unavailable."
fi

# --- 4. Install fork requirements + editable package -------------------------
echo "[setup] Installing RapidDoc requirements (CPU; this can take a few minutes) ..."
pip install -r "$FORK_DIR/requirements.deepx.txt"
pip install -e "$FORK_DIR"

# Verify the NPU binding is importable in this venv.
python -c "import dx_engine; from dx_engine import InferenceEngine, InferenceOption; print('[setup] dx_engine OK:', dx_engine.__file__)"

# --- 5. Provision models via the fork's OWN setup.sh (FOREGROUND) ------------
# Downloads onnx_models/ + dxnn_models/ from sdk.deepx.ai. Foreground only.
# The fork's setup.sh invokes ./setup_sample_models.sh directly, so ensure the
# fork's shell scripts carry the execute bit (git clone may drop it).
chmod +x "$FORK_DIR"/*.sh "$FORK_DIR"/deepx_scripts/*.sh 2>/dev/null || true
if [ -d "$FORK_DIR/dxnn_models" ] && [ -n "$(ls -A "$FORK_DIR/dxnn_models" 2>/dev/null)" ]; then
    echo "[setup] dxnn_models/ already present; skipping model download."
else
    echo "[setup] Downloading prebuilt models via RapidDoc/setup.sh (foreground) ..."
    ( cd "$FORK_DIR" && bash ./setup.sh )
fi

echo "[setup] dxnn_models:"; ls -1 "$FORK_DIR/dxnn_models" 2>/dev/null | head -20 || echo "  (missing)"
echo "[setup] onnx_models:"; ls -1 "$FORK_DIR/onnx_models" 2>/dev/null | head -20 || echo "  (missing)"

# --- 6. Pick a bundled sample PDF -------------------------------------------
# Default to the financial report: it exercises the full pipeline — headings +
# multiple tables (rendered as HTML) + multilingual OCR (ch_PP-OCRv5) on the NPU.
SAMPLE_SRC="$FORK_DIR/demo/pdfs/比亚迪财报_origin.pdf"
if [ ! -f "$SAMPLE_SRC" ]; then
    SAMPLE_SRC="$FORK_DIR/demo/pdfs/BVRC_Meeting_Minutes_2024-04_origin.pdf"
fi
if [ ! -f "$SAMPLE_SRC" ]; then
    SAMPLE_SRC="$(find "$FORK_DIR/demo/pdfs" "$FORK_DIR/test_files" -name '*.pdf' 2>/dev/null | head -1)"
fi
if [ -n "${SAMPLE_SRC:-}" ] && [ -f "$SAMPLE_SRC" ]; then
    cp -f "$SAMPLE_SRC" "$SCRIPT_DIR/sample_input.pdf"
    echo "[setup] sample_input.pdf <- $(basename "$SAMPLE_SRC")"
fi

echo "[setup] DONE. Next: ./run.sh --parse-method auto"
