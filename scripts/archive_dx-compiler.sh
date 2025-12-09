#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

pushd $DX_AS_PATH

FORCE_ARGS=""

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

# Function to display help message
show_help() {
    echo "Usage: $(basename "$0") [--help] [--re-archive=<true|false>]"
    echo "Options:"
    echo "  [--re-archive=<true|false>]    : Force rebuild archive for dx-compiler (default: true)"
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

    # Create a temporary file to capture archived file paths
    TEMP_OUTPUT=$(mktemp)
    export ARCHIVE_OUTPUT_FILE="$TEMP_OUTPUT"

    ARCHIVE_COMPILER_CMD="$DX_AS_PATH/dx-compiler/install.sh --archive_mode=y $FORCE_ARGS"
    echo "$ARCHIVE_COMPILER_CMD"

    # Run command directly - stdin/stdout/stderr remain connected to terminal
    $ARCHIVE_COMPILER_CMD
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -ne 0 ]; then
        rm -f "$TEMP_OUTPUT"
        echo -e "${TAG_ERROR} Archiving dx-compiler failed!"
        exit 1
    fi
    
    # Read archived file paths from the temp file
    if [ -f "$TEMP_OUTPUT" ]; then
        ARCHIVED_COM_FILE=$(grep "ARCHIVED_COM_FILE=" "$TEMP_OUTPUT" | tail -1 | cut -d'=' -f2)
        ARCHIVED_TRON_FILE=$(grep "ARCHIVED_TRON_FILE=" "$TEMP_OUTPUT" | tail -1 | cut -d'=' -f2)
    fi
    
    # Clean up temp file
    rm -f "$TEMP_OUTPUT"
    
    # Export for parent script
    if [ -n "$ARCHIVED_COM_FILE" ]; then
        export ARCHIVED_COM_FILE
        echo "ARCHIVED_COM_FILE=${ARCHIVED_COM_FILE}"
    fi
    if [ -n "$ARCHIVED_TRON_FILE" ]; then
        export ARCHIVED_TRON_FILE
        echo "ARCHIVED_TRON_FILE=${ARCHIVED_TRON_FILE}"
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
        --re-archive)
            FORCE_ARGS="--force"
            ;;
        --re-archive=*)
            FORCE_VALUE="${1#*=}"
            if [ "$FORCE_VALUE" = "false" ]; then
                FORCE_ARGS="--force=false"
            else
                FORCE_ARGS="--force"
            fi
            ;;
        *)
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

main

popd
exit 0

