#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"

# Parse command line arguments
INSTALL_ARGS="--all"
for arg in "$@"; do
    if [ "$arg" == "--exclude-fw" ]; then
        INSTALL_ARGS="--exclude-fw"
        break
    fi
done

echo -e "=== Installing dx-runtime ${TAG_START} ==="

# Navigate to dx-runtime directory
cd "${DX_AS_PATH}/dx-runtime" || {
    echo -e "${TAG_ERROR} Failed to navigate to dx-runtime directory"
    exit 1
}

# Execute the install script with appropriate arguments
echo "Executing ./install.sh ${INSTALL_ARGS} ..."
./install.sh ${INSTALL_ARGS}

INSTALL_EXIT_CODE=$?

if [ $INSTALL_EXIT_CODE -eq 0 ]; then
    echo -e "=== Installing dx-runtime ${TAG_DONE} ==="
    exit 0
else
    echo -e "${TAG_ERROR} dx-runtime installation failed with exit code: $INSTALL_EXIT_CODE"
    exit $INSTALL_EXIT_CODE
fi
