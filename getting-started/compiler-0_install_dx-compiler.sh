#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"

echo -e "=== Installing dx-compiler ${TAG_START} ==="

# Navigate to dx-compiler directory
cd "${DX_AS_PATH}/dx-compiler" || {
    echo -e "${TAG_ERROR} Failed to navigate to dx-compiler directory"
    exit 1
}

# Execute the install script
echo "Executing ./install.sh ..."
./install.sh

INSTALL_EXIT_CODE=$?

if [ $INSTALL_EXIT_CODE -eq 0 ]; then
    echo -e "=== Installing dx-compiler ${TAG_DONE} ==="
    exit 0
else
    echo -e "${TAG_ERROR} dx-compiler installation failed with exit code: $INSTALL_EXIT_CODE"
    exit $INSTALL_EXIT_CODE
fi
