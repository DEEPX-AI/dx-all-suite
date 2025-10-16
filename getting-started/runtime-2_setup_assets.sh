#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}/../dx-runtime")
DX_AS_PATH=$(realpath -s "${RUNTIME_PATH}/..")

DX_APP_PATH="${RUNTIME_PATH}/dx_app"
DX_STREAM_PATH="${RUNTIME_PATH}/dx_stream"

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "RUNTIME_PATH($RUNTIME_PATH)"
echo "DX_AS_PATH($DX_AS_PATH)"
echo "DX_APP_PATH($DX_APP_PATH)"
echo "DX_STREAM_PATH($DX_STREAM_PATH)"
echo -e "============================"

CONTAINER_MODE=false
COMPILED_MODEL_PATH="$SCRIPT_DIR/dxnn"

setup_assets() {
    local target_path=$1
    echo -e "=== Setup ${target_path} assets ${TAG_START} ==="

    pushd ${target_path}
    ./setup.sh
    popd

    echo -e "=== Setup ${target_path} assets '${COMPILED_MODEL_PATH}' ${TAG_DONE} ==="
}

setup_assets "${DX_APP_PATH}"
setup_assets "${DX_STREAM_PATH}"

exit 0

