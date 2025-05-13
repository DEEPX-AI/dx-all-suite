#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}")

pushd $SCRIPT_DIR

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

main() {
    # arciving dx-com
    echo -e "=== Archiving dx-compiler ... ${TAG_START} ==="

    ARCHIVE_COMPILER_CMD="$SCRIPT_DIR/dx-compiler/install.sh --archive_mode=y"
    echo "$ARCHIVE_COMPILER_CMD"

    $ARCHIVE_COMPILER_CMD
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Archiving dx-compiler failed!"
        exit 1
    fi
    echo -e "=== Archiving dx-compiler ... ${TAG_DONE} ==="
}

main

popd
exit 0

