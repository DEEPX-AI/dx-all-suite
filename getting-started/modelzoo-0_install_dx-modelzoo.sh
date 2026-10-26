#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")
MODELZOO_PATH="${DX_AS_PATH}/dx-modelzoo"

# color env settings
source "${DX_AS_PATH}/scripts/color_env.sh"

# Display help message
show_help() {
    cat << EOF2
Usage: $(basename "$0") [OPTIONS]

Install DX-ModelZoo (dxmz CLI) into the DX-Runtime Python environment.

OPTIONS:
  --source PATH     DX-ModelZoo source directory (default: <dx-all-suite>/dx-modelzoo)
  --venv PATH       Python virtual environment to install into
                    (default: host 'dx-runtime/venv-dx-runtime', container '/venv-dxnn')
  --extra NAME      pip extra to install: cpu | gpu (default: cpu)
  -f, --force       Reinstall even if dxmz is already working
  -h, --help        Display this help message and exit

DESCRIPTION:
  NPU (dxnn) evaluation needs 'dx_engine' (DX-RT Python API) in the same
  environment as DX-ModelZoo, so DX-ModelZoo is installed into the DX-Runtime
  environment created by 'runtime-0_install_dx-runtime.sh'. If dxmz already
  works there with the requested extra, installation is skipped. Use --force
  to reinstall. Switching between cpu and gpu removes the other ONNX Runtime
  package (onnxruntime / onnxruntime-gpu) because they cannot coexist.

EXAMPLES:
  $(basename "$0")                 # Install (skip if already working)
  $(basename "$0") --extra gpu     # Install/switch to ONNX Runtime GPU
  $(basename "$0") --force         # Force reinstall
EOF2
}

is_container() {
    [ "${DX_CONTAINER_MODE}" = "true" ] && return 0
    [ "${DX_CONTAINER_MODE}" = "false" ] && return 1
    grep -qE "/docker|/lxc|/containerd" /proc/1/cgroup 2>/dev/null || [ -f /.dockerenv ]
}

# Parse command line arguments
FORCE_INSTALL=false
EXTRA="cpu"
VENV_PATH=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --source) MODELZOO_PATH="${2:?--source requires a path}"; shift ;;
        --venv)   VENV_PATH="${2:?--venv requires a path}"; shift ;;
        --extra)  EXTRA="${2:?--extra requires a name}"; shift ;;
        -f|--force) FORCE_INSTALL=true ;;
        -h|--help|help) show_help; exit 0 ;;
        *) echo -e "${TAG_ERROR} Unknown option: $1"; show_help; exit 1 ;;
    esac
    shift
done

# onnxruntime and onnxruntime-gpu provide the same 'onnxruntime' module; only one may be installed.
case "${EXTRA}" in
    cpu) ORT_PKG="onnxruntime";     ORT_CONFLICT_PKG="onnxruntime-gpu" ;;
    gpu) ORT_PKG="onnxruntime-gpu"; ORT_CONFLICT_PKG="onnxruntime" ;;
    *) echo -e "${TAG_ERROR} Unsupported --extra '${EXTRA}' (use cpu or gpu)"; exit 1 ;;
esac

if [ -z "${VENV_PATH}" ]; then
    if is_container; then
        VENV_PATH="/venv-dxnn"
    else
        VENV_PATH="${DX_AS_PATH}/dx-runtime/venv-dx-runtime"
    fi
fi

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo "MODELZOO_PATH($MODELZOO_PATH)"
echo "VENV_PATH($VENV_PATH)"
echo -e "============================"

if [ ! -f "${VENV_PATH}/bin/activate" ]; then
    echo -e "${TAG_ERROR} Python environment not found: ${VENV_PATH}"
    echo -e "${TAG_INFO} Run './getting-started/runtime-0_install_dx-runtime.sh' first, or pass --venv <path>."
    exit 1
fi
source "${VENV_PATH}/bin/activate"

check_dx_engine() {
    if ! python -c "import dx_engine" &>/dev/null; then
        echo -e "${TAG_WARN} 'dx_engine' is not importable in ${VENV_PATH}."
        echo -e "${TAG_INFO} ONNX evaluation works, but NPU (dxnn) evaluation needs DX-RT. Run './getting-started/runtime-0_install_dx-runtime.sh'."
    fi
}

# Skip if dxmz is already working (skip check bypassed with --force)
if [ "$FORCE_INSTALL" = false ] && command -v dxmz &>/dev/null && python -c "import dx_modelzoo" &>/dev/null \
    && pip show "${ORT_PKG}" &>/dev/null && ! pip show "${ORT_CONFLICT_PKG}" &>/dev/null; then
    echo -e "${TAG_INFO} dxmz is already available in ${VENV_PATH}"
    check_dx_engine
    echo -e "${TAG_DONE} Skipping DX-ModelZoo installation"
    exit 0
fi

if [ ! -f "${MODELZOO_PATH}/pyproject.toml" ]; then
    echo -e "${TAG_ERROR} DX-ModelZoo source not found: ${MODELZOO_PATH}"
    echo -e "${TAG_INFO} Run 'git submodule update --init --recursive' or pass --source <path>."
    exit 1
fi

echo -e "=== Installing DX-ModelZoo ${TAG_START} ==="
if pip show "${ORT_CONFLICT_PKG}" &>/dev/null; then
    echo "Removing '${ORT_CONFLICT_PKG}' (conflicts with '${ORT_PKG}') ..."
    pip uninstall -y "${ORT_CONFLICT_PKG}" || { echo -e "${TAG_ERROR} Failed to remove ${ORT_CONFLICT_PKG}"; exit 1; }
fi
echo "Executing pip install -e \"${MODELZOO_PATH}[${EXTRA}]\" ..."
if ! pip install -e "${MODELZOO_PATH}[${EXTRA}]"; then
    echo -e "${TAG_ERROR} DX-ModelZoo installation failed"
    exit 1
fi
if ! dxmz --help >/dev/null; then
    echo -e "${TAG_ERROR} 'dxmz --help' failed after installation"
    exit 1
fi
check_dx_engine
if [ "${EXTRA}" = "gpu" ]; then
    echo -e "${TAG_INFO} For GPU inference, add the NVIDIA library paths (e.g. to ~/.bashrc) after activating ${VENV_PATH}:"
    echo '  export LD_LIBRARY_PATH=$(python -c "import nvidia.cublas.lib; print(nvidia.cublas.lib.__path__[0])"):$LD_LIBRARY_PATH'
    echo '  export LD_LIBRARY_PATH=$(python -c "import nvidia.cudnn.lib; print(nvidia.cudnn.lib.__path__[0])"):$LD_LIBRARY_PATH'
fi
echo -e "=== Installing DX-ModelZoo ${TAG_DONE} ==="
exit 0
