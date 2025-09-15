#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")

BASE_URL="https://sdk.deepx.ai/"

# default value
SOURCE_PATH=""
DOWNLOAD_DIR=$(realpath -s "${SCRIPT_DIR}/../download")
OUTPUT_DIR=""
SYMLINK_TARGET_PATH=""
USE_FORCE=0
USE_EXTRACT=0

# color env settings
source "${SCRIPT_DIR}/color_env.sh"
source "${SCRIPT_DIR}/common_util.sh"

# Function to exit with an error message and hint
exit_with_message() {
    local error_message="$1"
    print_colored_v2 "ERROR" "$error_message"
    exit 1
}

set_archive_target_path() {
    # setting extract location
    FILENAME=$(basename "${SOURCE_PATH}")

    # Get extract target dir name without extension
    # Remove .tar.gz or .tgz explicitly, otherwise remove only the last extension
    if [[ "$FILENAME" == *.tar.gz ]]; then
        TARGET_DIR_NAME="${FILENAME%.tar.gz}"
    elif [[ "$FILENAME" == *.tgz ]]; then
        TARGET_DIR_NAME="${FILENAME%.tgz}"
    else
        TARGET_DIR_NAME="${FILENAME%.*}"
    fi

    if [ "$USE_EXTRACT" -eq 0 ]; then
        ACTION_TYPE="Move"
    else
        ACTION_TYPE="Move and Extract"
    fi

    if [ -n "$SYMLINK_TARGET_PATH" ]; then
        # if '--symlink_target_path' option is exist.
        ARCHIVE_TARGET_DIR="$SYMLINK_TARGET_PATH/download"
        ARCHIVE_TARGET_PATH="$ARCHIVE_TARGET_DIR/$FILENAME"
        OUTPUT_TARGET_PATH="$SYMLINK_TARGET_PATH/$TARGET_DIR_NAME"
        print_colored "${ACTION_TYPE} to --symlink_target_path: $ARCHIVE_TARGET_PATH"
    else
        ARCHIVE_TARGET_DIR="$OUTPUT_DIR/download"
        ARCHIVE_TARGET_PATH="$ARCHIVE_TARGET_DIR/$FILENAME"
        OUTPUT_TARGET_PATH="$OUTPUT_DIR/$TARGET_DIR_NAME"
        print_colored "${ACTION_TYPE} to output path: $ARCHIVE_TARGET_PATH"
    fi
}

# Function to display help message
show_help() {
    print_colored_v2 "INFO" "Usage: $(basename "$0") --src_path=<source_path> --output=<dir> [--symlink_target_path=<dir>] [--extract] [--force]"
    print_colored_v2 "INFO" "Example: $0 --src_path=modelzoo/onnx/MobileNetV2-1.onnx --output=../getting-start/modelzoo/json -symlink_target_path=../workspace/modelzoo/json"
    print_colored_v2 "INFO" "Options:"
    print_colored_v2 "INFO" "  --src_path=<path>                Set source path for file server endpoint"
    print_colored_v2 "INFO" "  --output=<path>                  Set output path (example: ./assets)"
    print_colored_v2 "INFO" "  [--extract]                      Choose whether to extract the compressed file"
    print_colored_v2 "INFO" "  [--symlink_target_path=<path>]   Set symlink target path for output path"
    print_colored_v2 "INFO" "  [--force]                        Force overwrite if the file already exists"
    print_colored_v2 "INFO" "  [--help]                         Show this help message"

    if [ "$1" == "error" ]; then
        exit_with_message "Invalid or missing arguments."
    fi
    exit 0
}

download() {
    print_colored_v2 "INFO" "=== Download Start ==="
    set_archive_target_path

    DOWNLOAD_PATH=$DOWNLOAD_DIR/$FILENAME
    print_colored "--- Download path: $DOWNLOAD_PATH ---"
    print_colored "--- Download real path: $(readlink -f "$DOWNLOAD_PATH") ---"
    print_colored "--- ARCHIVE_TARGET_PATH($ARCHIVE_TARGET_PATH) ---"

    if [ -e "$ARCHIVE_TARGET_PATH" ] && [ "$USE_FORCE" -eq 0 ]; then
        print_colored "archive file downloaded path($ARCHIVE_TARGET_PATH) is already exist. so, skip to download file to output path"
        if [ ! -e "$DOWNLOAD_PATH" ]; then
            print_colored "make symlink '$ARCHIVE_TARGET_PATH' -> '$DOWNLOAD_PATH'"
            mkdir -p "$DOWNLOAD_DIR" || exit_with_message "Failed to create directory '$DOWNLOAD_DIR'. Check permissions."
            ln -s "$(readlink -f "$ARCHIVE_TARGET_PATH")" "$(readlink -f "$DOWNLOAD_PATH")"
            if [ $? -ne 0 ]; then
                exit_with_message "Failed to create symlink '$ARCHIVE_TARGET_PATH' -> '$DOWNLOAD_PATH'. Check permissions."
            fi
        fi
        print_colored_v2 "INFO" "=== Download SKIP ==="
        return 0
    elif [ -L "${ARCHIVE_TARGET_PATH}" ] && [ ! -e "${ARCHIVE_TARGET_PATH}" ]; then
        print_colored "archive file target path($ARCHIVE_TARGET_PATH) is symlink. but, it is broken. so, recreate symlink."
        rm -rf "$ARCHIVE_TARGET_PATH"
        if [ $? -ne 0 ]; then
            exit_with_message "Failed to remove broken symlink '$ARCHIVE_TARGET_PATH'. Check permissions."
        fi
    fi

    if [ "$USE_FORCE" -eq 1 ]; then
        print_colored "'--force' option is set. so remove Downloaded file($DOWNLOAD_PATH)"
        rm -rf "$DOWNLOAD_PATH"
        if [ $? -ne 0 ]; then
            exit_with_message "Failed to remove file '$DOWNLOAD_PATH'. Check permissions."
        fi
    fi

    if [ -L "${DOWNLOAD_PATH}" ] && [ ! -e "${DOWNLOAD_PATH}" ]; then
        print_colored "downloaded path($DOWNLOAD_PATH) is symlink. but, it is broken. so, recreate symlink."
        rm -rf "$DOWNLOAD_PATH"
        if [ $? -ne 0 ]; then
            exit_with_message "Failed to remove broken symlink '$DOWNLOAD_PATH'. Check permissions."
        fi
    fi

    URL="${BASE_URL}${SOURCE_PATH}"

    # check curl and install curl
    if ! command -v curl &> /dev/null; then
        print_colored "curl is not installed. Installing..."
        sudo apt update && sudo apt install -y curl
        # curl install failed
        if ! command -v curl &> /dev/null; then
            exit_with_message "Failed to install curl."
        fi
    fi

    mkdir -p "$DOWNLOAD_DIR" || exit_with_message "Failed to create directory '$DOWNLOAD_DIR'. Check permissions."

    # download file
    print_colored "Downloading $FILENAME from $URL..."
    curl -o "$DOWNLOAD_PATH" "$URL"

    # download failed check
    if [ $? -ne 0 ]; then
        rm -rf "$DOWNLOAD_PATH"
        exit_with_message "Download failed($DOWNLOAD_PATH)! Check URL or network connection."
    fi
    print_colored_v2 "GREEN" "[OK] Download Complete"
}

extract_tar() {
    local TAR_FILE="$1"
    local TARGET_DIR="$2"

    # Check the internal structure of the tar file
    local FIRST_ENTRY
    FIRST_ENTRY=$(tar tf "$TAR_FILE" | head -n 1)

    # Determine if a top-level directory exists
    if [[ "$FIRST_ENTRY" == */* ]]; then
        print_colored "Detected top-level directory: Using --strip-components=1"
        EXTRACT_CMD="tar xvfz "$TAR_FILE" --strip-components=1 -C "$TARGET_DIR""
    else
        print_colored "No top-level directory detected: Extracting as is"
        EXTRACT_CMD="tar xvfz "$TAR_FILE" -C "$TARGET_DIR""
    fi
    print_colored "EXTRACT_CMD: ${EXTRACT_CMD}"
    ${EXTRACT_CMD}
    if [ $? -ne 0 ]; then
        return 1 # Return 1 to indicate failure to the caller (generate_output)
    fi
}

generate_output() {
    print_colored_v2 "INFO" "=== Generate output Start ==="

    set_archive_target_path

    if [ "$USE_EXTRACT" -eq 0 ]; then
        ACTION_TYPE="Move"
    else
        ACTION_TYPE="Move and Extract"
    fi

    if [ -e "$ARCHIVE_TARGET_PATH" ] && [ "$USE_FORCE" -eq 0 ]; then
        print_colored "archive file downloaded path($ARCHIVE_TARGET_PATH) is already exist. so, skip to move downloaded file to output path"
        print_colored_v2 "INFO" "=== MOVE SKIP ==="
    else
        print_colored "Move $DOWNLOAD_PATH to $ARCHIVE_TARGET_PATH"
        mkdir -p "$ARCHIVE_TARGET_DIR" || exit_with_message "Failed to create directory '$ARCHIVE_TARGET_DIR'. Check permissions."
        mv "$DOWNLOAD_PATH" "$ARCHIVE_TARGET_PATH"
        # failed check
        if [ $? -ne 0 ]; then
            rm -rf "$DOWNLOAD_PATH"
            rm -rf "$ARCHIVE_TARGET_PATH"
            exit_with_message "${ACTION_TYPE} failed! Failed to move file to '$ARCHIVE_TARGET_PATH'. Check permissions."
        fi
        ln -s "$(readlink -f "$ARCHIVE_TARGET_PATH")" "$(readlink -f "$DOWNLOAD_PATH")"
        # failed check
        if [ $? -ne 0 ]; then
            rm -rf "$DOWNLOAD_PATH"
            rm -rf "$ARCHIVE_TARGET_PATH"
            exit_with_message "${ACTION_TYPE} failed! Failed to create symlink. Check permissions."
        fi
        print_colored_v2 "GREEN" "[OK] === MAKE SYMLINK SUCC ==="
    fi

    # extract tar.gz or move tar.gz
    if [ "$USE_EXTRACT" -eq 0 ]; then
        print_colored "Skip to extract file($ARCHIVE_TARGET_PATH)"
    else
        if [ -e "$OUTPUT_TARGET_PATH" ] && [ "$USE_FORCE" -eq 0 ]; then
            print_colored "Output file($OUTPUT_TARGET_PATH) is already exist. so, skip to extract downloaded file to output path"
            print_colored_v2 "INFO" "=== EXTRACT SKIP ==="
            return 0
        fi

        print_colored "Extract file($ARCHIVE_TARGET_PATH) to '$OUTPUT_TARGET_PATH'"

        # Create a directory
        rm -rf "$OUTPUT_TARGET_PATH"     # clean
        if [ $? -ne 0 ]; then
            exit_with_message "Failed to remove directory '$OUTPUT_TARGET_PATH'. Check permissions."
        fi
        mkdir -p "$OUTPUT_TARGET_PATH" || exit_with_message "Failed to create directory '$OUTPUT_TARGET_PATH'. Check permissions."

        # and extract the contents into the created directory.
        extract_tar "$ARCHIVE_TARGET_PATH" "$OUTPUT_TARGET_PATH"
        # failed check
        if [ $? -ne 0 ]; then
            rm -rf "$DOWNLOAD_PATH"
            rm -rf "$ARCHIVE_TARGET_PATH"
            exit_with_message "${ACTION_TYPE} failed! Failed to extract file. Check file integrity or permissions."
        fi
        print_colored_v2 "GREEN" "[OK] === EXTRACT SUCC ==="
    fi

    print_colored "${ACTION_TYPE} complete."
    print_colored_v2 "GREEN" "[OK] === Generate output Complete ==="
}

make_symlink() {
    print_colored_v2 "INFO" "=== Make Symbolic Link Start ==="
    URL="${BASE_URL}${SOURCE_PATH}"
    FILENAME=$(basename "$URL")

    # if '--symlink_target_path' option is exist, make symbolic link
    if [ -n "$SYMLINK_TARGET_PATH" ]; then
        if [ "$USE_EXTRACT" -eq 0 ]; then
            OUTPUT_PATH=${OUTPUT_DIR}/${FILENAME}
            if [ -e "${OUTPUT_PATH}" ] && [ "$USE_FORCE" -eq 0 ]; then
                MSG="Output file(${OUTPUT_PATH}) is already exist. so, skip to copy downloaded file to output path"
            else
                mkdir -p "$(dirname "$OUTPUT_PATH")" || exit_with_message "Failed to create directory '$(dirname "$OUTPUT_PATH")'. Check permissions."
                CMD="cp ${ARCHIVE_TARGET_PATH} ${OUTPUT_PATH}"
                MSG="Copy file: ${ARCHIVE_TARGET_PATH} -> ${OUTPUT_PATH}"
            fi
        else
            if [ -L "$OUTPUT_DIR" ] && [ -e "$OUTPUT_DIR" ] && [ "$USE_FORCE" -eq 0 ]; then
                MSG="Symbolic link($OUTPUT_DIR) is already exist. so, skip to create symlink"
            else
                if [ -L "$OUTPUT_DIR" ] || [ -d "$OUTPUT_DIR" ]; then
                    print_colored "Output directory($OUTPUT_DIR) is already exist. so, remove dir and then create symlink"
                    rm -rf "$OUTPUT_DIR"
                    if [ $? -ne 0 ]; then
                        exit_with_message "Failed to remove directory '$OUTPUT_DIR'. Check permissions."
                    fi
                fi

                mkdir -p "$(dirname "$OUTPUT_DIR")" || exit_with_message "Failed to create directory '$(dirname "$OUTPUT_DIR")'. Check permissions."
                OUTPUT_TARGET_REAL_PATH=$(readlink -f "$OUTPUT_TARGET_PATH")
                CMD="ln -s $OUTPUT_TARGET_REAL_PATH $OUTPUT_DIR"
                MSG="Created symbolic link: $OUTPUT_DIR -> $OUTPUT_TARGET_REAL_PATH"
            fi
        fi

        if [ "$CMD" != "" ]; then
            print_colored "CMD: ${CMD}"
            eval "${CMD}"
            if [ $? -ne 0 ]; then
                exit_with_message "Command failed: '$CMD'. Check permissions."
            fi
        fi
        print_colored "$MSG"

    else
        print_colored "the --symlink_target_path option is not set. so, skip to make symlink."
    fi
    print_colored_v2 "GREEN" "[OK] === Make Symbolic Link Complete ==="
}

# parse args
for i in "$@"; do
    case "$1" in
        --src_path=*)
            SOURCE_PATH="${1#*=}"
            ;;
        --output=*)
            OUTPUT_DIR="${1#*=}"

            # Symbolic link cannot be created when output_dir is the current directory.
            OUTPUT_REAL_DIR=$(readlink -f "$OUTPUT_DIR")
            CURRENT_REAL_DIR=$(readlink -f "./")
            if [ "$OUTPUT_REAL_DIR" == "$CURRENT_REAL_DIR" ]; then
                exit_with_message "'--output' is the same as the current directory. Please specify a different directory."
            fi
            ;;
        --extract)
            USE_EXTRACT=1
            ;;
        --symlink_target_path=*)
            SYMLINK_TARGET_PATH="${1#*=}"
            SYMLINK_TARGET_REAL_PATH=$(readlink -f "$SYMLINK_TARGET_PATH")
            ;;
        --force)
            USE_FORCE=1
            ;;
        --help)
            show_help
            ;;
        *)
            print_colored "Unknown option: $1"
            show_help "error"
            ;;
    esac
    shift
done

print_colored "USE_EXTRACT($USE_EXTRACT)"
print_colored "USE_FORCE($USE_FORCE)"

# usage
if [ -z "$SOURCE_PATH" ] || [ -z "$OUTPUT_DIR" ]; then
    exit_with_message "SOURCE_PATH(${SOURCE_PATH}) or OUTPUT_DIR(${OUTPUT_DIR}) does not exist."
fi

download
generate_output
make_symlink

exit 0
