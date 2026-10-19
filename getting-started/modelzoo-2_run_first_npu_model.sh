#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")
WORKSPACE_LINK="${SCRIPT_DIR}/modelzoo"
MODEL_ROOT="${MODEL_ROOT:-${WORKSPACE_LINK}/models}"
DATA_ROOT="${DATA_ROOT:-${WORKSPACE_LINK}/datasets}"

# color env settings
source "${DX_AS_PATH}/scripts/color_env.sh"

show_help() {
    cat << EOF2
Usage: $(basename "$0") [OPTIONS]

Run the DX-ModelZoo first-model flow: info -> ONNX eval -> compile -> NPU eval.

OPTIONS:
  --model NAME          Model name or YAML path (default: resnet50_224x224)
  --profile NAME        DXNN profile: c-lite | q-lite | q-pro (default: q-lite)
  --venv PATH           Python environment with dxmz
                        (default: host 'dx-runtime/venv-dx-runtime', container '/venv-dxnn')
  --dx-com-wheel PATH   local dx_com wheel to install instead of the pip package
                        (optional; by default dx_com is installed with pip)
  --skip-onnx           Skip ONNX baseline evaluation
  --skip-compile        Skip compilation (evaluate an existing or downloaded .dxnn)
  -h, --help            Display this help message and exit

DESCRIPTION:
  ONNX evaluation runs first and downloads the ONNX model through DXMZ_MODEL_URL
  when it is missing. 'dxmz compile' does not download models, so it reuses
  that ONNX file. Results are saved under 'getting-started/modelzoo/result'.

  'dxmz eval --profile <c-lite|q-lite|q-pro>' also downloads a prebuilt .dxnn
  from DXMZ_MODEL_URL, so '--skip-onnx --skip-compile' runs NPU evaluation
  alone, without dx_com and without the ONNX baseline.

  DATA_ROOT and MODEL_ROOT can be overridden with environment variables, e.g.
  'DATA_ROOT=/deepx/datasets $(basename "$0")' to use a dataset directory
  mounted into the container (see DX_DATASETS_PATH in docker_run.sh).
EOF2
}

is_container() {
    [ "${DX_CONTAINER_MODE}" = "true" ] && return 0
    [ "${DX_CONTAINER_MODE}" = "false" ] && return 1
    grep -qE "/docker|/lxc|/containerd" /proc/1/cgroup 2>/dev/null || [ -f /.dockerenv ]
}

MODEL="resnet50_224x224"
PROFILE="q-lite"
VENV_PATH=""
DX_COM_WHEEL=""
SKIP_ONNX=false
SKIP_COMPILE=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --model)        MODEL="${2:?--model requires a name}"; shift ;;
        --profile)      PROFILE="${2:?--profile requires a name}"; shift ;;
        --venv)         VENV_PATH="${2:?--venv requires a path}"; shift ;;
        --dx-com-wheel) DX_COM_WHEEL="${2:?--dx-com-wheel requires a path}"; shift ;;
        --skip-onnx)    SKIP_ONNX=true ;;
        --skip-compile) SKIP_COMPILE=true ;;
        -h|--help|help) show_help; exit 0 ;;
        *) echo -e "${TAG_ERROR} Unknown option: $1"; show_help; exit 1 ;;
    esac
    shift
done

if [ -z "${VENV_PATH}" ]; then
    if is_container; then VENV_PATH="/venv-dxnn"; else VENV_PATH="${DX_AS_PATH}/dx-runtime/venv-dx-runtime"; fi
fi

# resolve user paths before 'cd' into the workspace (dxmz treats '/' or '.yaml/.yml' as a YAML path)
if [ -n "${DX_COM_WHEEL}" ]; then
    DX_COM_WHEEL=$(realpath -m "${DX_COM_WHEEL}")
    if [ ! -f "${DX_COM_WHEEL}" ]; then
        echo -e "${TAG_ERROR} dx_com wheel not found: ${DX_COM_WHEEL}"
        exit 1
    fi
fi
case "${MODEL}" in
    */*|*.yaml|*.yml) MODEL=$(realpath -m "${MODEL}") ;;
esac

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo "VENV_PATH($VENV_PATH)"
echo "MODEL_ROOT($MODEL_ROOT)"
echo "DATA_ROOT($DATA_ROOT)"
echo -e "============================"

if [ ! -f "${VENV_PATH}/bin/activate" ]; then
    echo -e "${TAG_ERROR} Python environment not found: ${VENV_PATH}. Run 'modelzoo-0_install_dx-modelzoo.sh' first."
    exit 1
fi
source "${VENV_PATH}/bin/activate"
if ! command -v dxmz &>/dev/null; then
    echo -e "${TAG_ERROR} dxmz not found in ${VENV_PATH}. Run 'modelzoo-0_install_dx-modelzoo.sh' first."
    exit 1
fi
if [ ! -d "${WORKSPACE_LINK}" ]; then
    echo -e "${TAG_ERROR} '${WORKSPACE_LINK}' not found. Run 'modelzoo-1_prepare_assets.sh' first."
    exit 1
fi

run_step() {
    local title=$1; shift
    echo -e "=== ${title} ${TAG_START} ==="
    echo "$*"
    "$@" || { echo -e "${TAG_ERROR} ${title} failed"; exit 1; }
    echo -e "=== ${title} ${TAG_DONE} ==="
}

# 'dxmz --save' writes result/ under the current directory
cd "${WORKSPACE_LINK}" || exit 1
# exported values win over dx-modelzoo/.env, so 'dxmz info' shows the same paths eval/compile use
export DATA_ROOT MODEL_ROOT
ROOT_ARGS=(--model-root "${MODEL_ROOT}" --data-root "${DATA_ROOT}")

run_step "[1] Model info" dxmz info "${MODEL}"

if [ "${SKIP_ONNX}" = false ]; then
    run_step "[2] ONNX evaluation" dxmz eval "${MODEL}" --profile onnx "${ROOT_ARGS[@]}" --save
fi

if [ "${SKIP_COMPILE}" = false ]; then
    if ! python -c "import dx_com" &>/dev/null; then
        # keep DX-ModelZoo's numpy<2.0 requirement while resolving dx_com dependencies
        if [ -n "${DX_COM_WHEEL}" ]; then
            run_step "[3-0] Install dx_com (wheel)" pip install "${DX_COM_WHEEL}" "numpy>=1.20,<2.0"
        else
            # same source as 'dx-compiler/install.sh': version pinned by dx-compiler/compiler.properties,
            # with the published PyPI package as fallback.
            COM_VERSION=$(sed -n 's/^COM_VERSION=//p' "${DX_AS_PATH}/dx-compiler/compiler.properties" 2>/dev/null | tr -d '[:space:]')
            echo -e "=== [3-0] Install dx_com ${TAG_START} ==="
            if [ -n "${COM_VERSION}" ] && pip install "dx-com==${COM_VERSION}" \
                    -f "https://sdk.deepx.ai/release/dxcom/v${COM_VERSION}/index.html" "numpy>=1.20,<2.0"; then
                echo -e "${TAG_INFO} dx_com ${COM_VERSION} installed (dx-compiler pinned version)"
            elif pip install "dx-com" "numpy>=1.20,<2.0"; then
                echo -e "${TAG_INFO} dx_com installed (latest from PyPI)"
            else
                echo -e "${TAG_ERROR} Failed to install dx_com. Pass --dx-com-wheel /path/to/dx_com-*.whl or use --skip-compile."
                exit 1
            fi
            echo -e "=== [3-0] Install dx_com ${TAG_DONE} ==="
        fi
    fi
    run_step "[3] Compile (${PROFILE})" dxmz compile "${MODEL}" --profile "${PROFILE}" "${ROOT_ARGS[@]}"
fi

if ! python -c "import dx_engine" &>/dev/null; then
    echo -e "${TAG_ERROR} dx_engine is not installed in ${VENV_PATH}. Run './getting-started/runtime-0_install_dx-runtime.sh'."
    exit 1
fi
run_step "[4] NPU evaluation (${PROFILE})" dxmz eval "${MODEL}" --profile "${PROFILE}" "${ROOT_ARGS[@]}" --save

echo -e "${TAG_INFO} Results: ${WORKSPACE_LINK}/result"
exit 0
