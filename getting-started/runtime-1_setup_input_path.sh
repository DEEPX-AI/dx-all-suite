#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}/../dx-runtime")
DX_AS_PATH=$(realpath -s "${RUNTIME_PATH}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "RUNTIME_PATH($RUNTIME_PATH)"
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"

CONTAINER_MODE=false
COMPILED_MODEL_PATH="$SCRIPT_DIR/dxnn"

setup_compiled_model_path() {
    echo -e "=== Setup 'compiled_model_path' to '${COMPILED_MODEL_PATH}' ${TAG_START} ==="

    # Check if running in a container
    if grep -qE "/docker|/lxc|/containerd" /proc/1/cgroup || [ -f /.dockerenv ]; then
        CONTAINER_MODE=true
        echo "(container mode detected)"
        
        if [ -z "$DOCKER_VOLUME_PATH" ]; then
            echo "Error: --docker_volume_path must be provided in container mode."
            show_help "error"
            exit 1
        fi
        SYMLINK_TARGET_PATH="${DOCKER_VOLUME_PATH}/dxnn"
    else
        echo "(host mode detected)"
        SYMLINK_TARGET_PATH="${DX_AS_PATH}/workspace/dxnn"
    fi

    # create symbolic link('${COMPILED_MODEL_PATH}') and link to workspace path('${SYMLINK_TARGET_PATH}')
    if [ -e "${SYMLINK_TARGET_PATH}" ] && [ -e "${COMPILED_MODEL_PATH}" ]; then
        echo "symlink target path(${SYMLINK_TARGET_PATH}) and output path(${COMPILED_MODEL_PATH})is already exist. so, skip to setup output path."
        echo -e "=== ${TAG_INFO} SETUP SKIP ==="
        return 0
    else
        echo "COMPILED_MODEL_PATH(${COMPILED_MODEL_PATH})"
        if [ -L "${COMPILED_MODEL_PATH}" ] && [ ! -e "${COMPILED_MODEL_PATH}" ]; then
            echo "output path(${COMPILED_MODEL_PATH}) is a broken symbolic link. removing and recreating the symbolic link."
            rm -rf ${COMPILED_MODEL_PATH}
        fi

        mkdir -p ${SYMLINK_TARGET_PATH}

        CMD="ln -s ${SYMLINK_TARGET_PATH} ${COMPILED_MODEL_PATH}"
        echo "$CMD"

        $CMD
        if [ $? -ne 0 ]; then
            echo -e "${TAG_ERROR} Setup 'compiled_model_path' to '${COMPILED_MODEL_PATH}' failed!"
            exit 1
        fi
        echo -e "${TAG_SUCC} created symbolic link '${COMPILED_MODEL_PATH}' -> '${SYMLINK_TARGET_PATH}'"
    fi

    echo -e "=== Setup 'compiled_model_path' to '${COMPILED_MODEL_PATH}' ${TAG_DONE} ==="
}

# setup compiled model path to '${COMPILED_MODEL_PATH}'
# create symbolic link '${COMPILED_MODEL_PATH}' and link to workspace path
#   - `workspace path`
#     - CONTAINER_MODE: ${DOCKER_VOLUME_PATH}/dxnn'
#     - HOST_MODE: '${DX_AS_PATH}/workspace/dxnn'
setup_compiled_model_path

exit 0

