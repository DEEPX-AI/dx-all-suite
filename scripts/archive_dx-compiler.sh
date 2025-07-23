#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

pushd $DX_AS_PATH

FORCE_ARGS=""

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

# Function to display help message
show_help() {
    echo "Usage: $(basename "$0") [--help] [--force]"
    echo "Options:"
    echo "  [--force]                      : Force overwrite if the file already exists"
    echo "  [--help]                       : Show this help message"

    if [ "$1" == "error" ] && [[ ! -n "$2" ]]; then
        echo -e "${TAG_ERROR} Invalid or missing arguments."
        exit 1
    elif [ "$1" == "error" ] && [[ -n "$2" ]]; then
        echo -e "${TAG_ERROR} $2"
        exit 1
    elif [[ "$1" == "warn" ]] && [[ -n "$2" ]]; then
        echo -e "${TAG_WARN} $2"
        return 0
    fi
    exit 0
}

main() {
    # arciving dx-com
    echo -e "=== Archiving dx-compiler ... ${TAG_START} ==="

    ARCHIVE_COMPILER_CMD="$DX_AS_PATH/dx-compiler/install.sh --archive_mode=y $FORCE_ARGS"
    echo "$ARCHIVE_COMPILER_CMD"

    $ARCHIVE_COMPILER_CMD
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Archiving dx-compiler failed!"
        exit 1
    fi
    echo -e "=== Archiving dx-compiler ... ${TAG_DONE} ==="
}

# parse args
for i in "$@"; do
    case "$1" in
        --help)
            show_help
            exit 0
            ;;
        --force)
            FORCE_ARGS="--force"
            ;;
        *)
            echo -e "${TAG_ERROR}: Invalid option '$1'"
            show_help
            exit 1
            ;;
    esac
    shift
done

main

popd
exit 0

