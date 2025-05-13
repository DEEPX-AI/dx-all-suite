#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
COMPILER_PATH=$(realpath -s "${SCRIPT_DIR}/../dx-compiler")
DX_SIMULATOR_PATH=$(realpath -s "${COMPILER_PATH}/dx_simulator")
DX_AS_PATH=$(realpath -s "${COMPILER_PATH}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "DX_SIMULATOR_PATH($DX_SIMULATOR_PATH)"
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"

pushd ${SCRIPT_DIR}

main() {
    echo -e "=== Setup simulator dependancies ${TAG_START} ==="
    CMD=${DX_SIMULATOR_PATH}/scripts/install.sh
    echo "$CMD"
    $CMD
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Failed to setup simulator dependancies"
        exit 1
    fi
    echo -e "=== Setup simulator dependancies ${TAG_DONE} ==="
}

main

popd

exit 0

