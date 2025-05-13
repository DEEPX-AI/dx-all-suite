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
source ${SCRIPT_DIR}/color_env.sh


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
        echo "${ACTION_TYPE} to --symlink_target_path: $ARCHIVE_TARGET_PATH"
    else
        ARCHIVE_TARGET_DIR="$OUTPUT_DIR/download"
        ARCHIVE_TARGET_PATH="$ARCHIVE_TARGET_DIR/$FILENAME"
        OUTPUT_TARGET_PATH="$OUTPUT_DIR/$TARGET_DIR_NAME"
        echo "${ACTION_TYPE} to output path: $ARCHIVE_TARGET_PATH"
    fi
}

# Function to display help message
show_help() {
  echo "Usage: $(basename "$0") --src_path=<source_path> --output=<dir> [--symlink_target_path=<dir>] [--extract] [--force]"
  echo "Example: $0 --src_path=modelzoo/onnx/MobileNetV2-1.onnx --output=../getting-start/modelzoo/json -symlink_target_path=../workspace/modelzoo/json"
  echo "Options:"
  echo "  --src_path=<path>                Set source path for file server endpoint"
  echo "  --output=<path>                  Set output path (example: ./assets)"
  echo "  [--extract]                      Choose whether to extract the compressed file"
  echo "  [--symlink_target_path=<path>]   Set symlink target path for output path"
  echo "  [--force]                        Force overwrite if the file already exists"
  echo "  [--help]                         Show this help message"

  if [ "$1" == "error" ]; then
    echo "Error: Invalid or missing arguments."
    exit 1
  fi
  exit 0
}

download() {
    echo -e "=== Download Start ==="
    set_archive_target_path

    DOWNLOAD_PATH=$DOWNLOAD_DIR/$FILENAME
    echo "--- Download path: $DOWNLOAD_PATH ---"
    echo "--- Download real path: $(readlink -f "$DOWNLOAD_PATH") ---"
    echo "--- ARCHIVE_TARGET_PATH($ARCHIVE_TARGET_PATH) ---"

    if [ -e "$ARCHIVE_TARGET_PATH" ] && [ "$USE_FORCE" -eq 0 ]; then
        echo "archive file downloaded path($ARCHIVE_TARGET_PATH) is already exist. so, skip to download file to output path"
        if [ ! -e "$DOWNLOAD_PATH" ]; then
            echo "make symlink '$ARCHIVE_TARGET_PATH' -> '$DOWNLOAD_PATH'"
            mkdir -p "$DOWNLOAD_DIR"
            ln -s $(readlink -f "$ARCHIVE_TARGET_PATH") $(readlink -f "$DOWNLOAD_PATH")
        fi
        echo -e "${TAG_INFO} === Download SKIP ==="
        return 0
    elif [ -L "${ARCHIVE_TARGET_PATH}" ] && [ ! -e "${ARCHIVE_TARGET_PATH}" ]; then
        echo "archive file target path($ARCHIVE_TARGET_PATH) is symlink. but, it is broken. so, recreate symlink."
        rm -rf "$ARCHIVE_TARGET_PATH"
    fi
    
    if [ "$USE_FORCE" -eq 1 ]; then
        echo "'--force' option is set. so remove Downloaded file($DOWNLOAD_PATH)"
        rm -rf $DOWNLOAD_PATH
    fi

    if [ -L "${DOWNLOAD_PATH}" ] && [ ! -e "${DOWNLOAD_PATH}" ]; then
        echo "downloaded path($DOWNLOAD_PATH) is symlink. but, it is broken. so, recreate symlink."
        rm -rf $DOWNLOAD_PATH
    fi
        
    URL="${BASE_URL}${SOURCE_PATH}"

    # check curl and install curl
    if ! command -v curl &> /dev/null; then
        echo "curl is not installed. Installing..."
        sudo apt update && sudo apt install -y curl

        # curl install failed
        if ! command -v curl &> /dev/null; then
            echo -e "${TAG_ERROR} Failed to install curl. Exiting."
            exit 1
        fi
    fi

    mkdir -p "$DOWNLOAD_DIR"

    # download file
    echo "Downloading $FILENAME from $URL..."
    curl -o "$DOWNLOAD_PATH" "$URL"

    # download failed check
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Download failed($DOWNLOAD_PATH)!"
        rm -rf "$DOWNLOAD_PATH"
        exit 1
    fi
    echo -e "=== ${TAG_SUCC} Download Complete ==="
}

extract_tar() {
    local TAR_FILE="$1"
    local TARGET_DIR="$2"

    # Check the internal structure of the tar file
    local FIRST_ENTRY
    FIRST_ENTRY=$(tar tf "$TAR_FILE" | head -n 1)

    # Determine if a top-level directory exists
    if [[ "$FIRST_ENTRY" == */* ]]; then
        echo "Detected top-level directory: Using --strip-components=1"
        EXTRACT_CMD="tar xvfz "$TAR_FILE" --strip-components=1 -C "$TARGET_DIR""
    else
        echo "No top-level directory detected: Extracting as is"
        EXTRACT_CMD="tar xvfz "$TAR_FILE" -C "$TARGET_DIR""
    fi
    echo "EXTRACT_CMD: ${EXTRACT_CMD}"
    ${EXTRACT_CMD}
    if [ $? -ne 0 ]; then
        return 1
    fi
}

generate_output() {
    echo -e "=== Generate output Start ==="

    set_archive_target_path

    if [ "$USE_EXTRACT" -eq 0 ]; then
        ACTION_TYPE="Move"
    else
        ACTION_TYPE="Move and Extract"
    fi

    if [ -e "$ARCHIVE_TARGET_PATH" ] && [ "$USE_FORCE" -eq 0 ]; then
        echo "archive file downloaded path($ARCHIVE_TARGET_PATH) is already exist. so, skip to move downloaded file to output path"
        echo -e "${TAG_INFO} === MOVE SKIP ==="
    else
        echo "Move $DOWNLOAD_PATH to $ARCHIVE_TARGET_PATH"
        mkdir -p $ARCHIVE_TARGET_DIR
        mv "$DOWNLOAD_PATH" "$ARCHIVE_TARGET_PATH"
        # failed check
        if [ $? -ne 0 ]; then
            echo -e "${TAG_ERROR} ${ACTION_TYPE} failed! Please try installing again with the '--force' option."
            rm -rf "$DOWNLOAD_PATH"
            rm -rf "$ARCHIVE_TARGET_PATH"
            echo -e "${TAG_ERROR} === MOVE FAIL ==="
            exit 1
        fi
        ln -s $(readlink -f "$ARCHIVE_TARGET_PATH") $(readlink -f "$DOWNLOAD_PATH")
        # failed check
        if [ $? -ne 0 ]; then
            echo -e "${TAG_ERROR} ${ACTION_TYPE} failed! Please try installing again with the '--force' option."
            rm -rf "$DOWNLOAD_PATH"
            rm -rf "$ARCHIVE_TARGET_PATH"
            echo -e "${TAG_ERROR} === MAKE SYMLINK FAIL ==="
            exit 1
        fi
        echo -e "${TAG_SUCC} === MAKE SYMLINK SUCC ==="
    fi
    
    # extract tar.gz or move tar.gz
    if [ "$USE_EXTRACT" -eq 0 ]; then
        echo "Skip to extract file($ARCHIVE_TARGET_PATH)"
    else
        if [ -e "$OUTPUT_TARGET_PATH" ] && [ "$USE_FORCE" -eq 0 ]; then
            echo "Output file($OUTPUT_TARGET_PATH) is already exist. so, skip to extract downloaded file to output path"
            echo -e "${TAG_INFO} === EXTRACT SKIP ==="
            return 0
        fi
        
        echo "Extract file($ARCHIVE_TARGET_PATH) to '$OUTPUT_TARGET_PATH'"

        # Create a directory
        rm -rf $OUTPUT_TARGET_PATH      # clean
        mkdir -p $OUTPUT_TARGET_PATH

        # and extract the contents into the created directory.
        extract_tar "$ARCHIVE_TARGET_PATH" "$OUTPUT_TARGET_PATH"
        
        # failed check
        if [ $? -ne 0 ]; then
            echo -e "${TAG_ERROR} ${ACTION_TYPE} failed! Please try installing again with the '--force' option."
            rm -rf "$DOWNLOAD_PATH"
            rm -rf "$ARCHIVE_TARGET_PATH"
            echo -e "${TAG_ERROR} === EXTRACT FAIL ==="
            exit 1
        fi
        echo -e "${TAG_SUCC} === EXTRACT SUCC ==="
    fi
    
    echo "${ACTION_TYPE} complete."
    echo -e "${TAG_SUCC} === Generate output Complete ==="
}

make_symlink() {
    echo -e "=== Make Symbolic Link Start ==="
    URL="${BASE_URL}${SOURCE_PATH}"
    FILENAME=$(basename "$URL")

    # if '--symlink_target_path' option is exist, make symbolic link
    if [ -n "$SYMLINK_TARGET_PATH" ]; then
        if [ "$USE_EXTRACT" -eq 0 ]; then
            OUTPUT_PATH=${OUTPUT_DIR}/${FILENAME}
            if [ -e "${OUTPUT_PATH}" ] && [ "$USE_FORCE" -eq 0 ]; then
                MSG="Output file(${OUTPUT_PATH}) is already exist. so, skip to copy downloaded file to output path"
            else
                mkdir -p "$(dirname "$OUTPUT_PATH")"
                CMD="cp ${ARCHIVE_TARGET_PATH} ${OUTPUT_PATH}"
                MSG="Copy file: ${ARCHIVE_TARGET_PATH} -> ${OUTPUT_PATH}"
            fi
        else
            if [ -L "$OUTPUT_DIR" ] && [ -e "$OUTPUT_DIR" ] && [ "$USE_FORCE" -eq 0 ]; then
                MSG="Symbolic link($OUTPUT_DIR) is already exist. so, skip to create symlink"
            else
                if [ -L "$OUTPUT_DIR" ] || [ -d "$OUTPUT_DIR" ]; then
                    echo "Output directory($OUTPUT_DIR) is already exist. so, remove dir and then create symlink"
                    rm -rf $OUTPUT_DIR
                fi

                mkdir -p "$(dirname "$OUTPUT_DIR")"
                OUTPUT_TARGET_REAL_PATH=$(readlink -f "$OUTPUT_TARGET_PATH")
                CMD="ln -s $OUTPUT_TARGET_REAL_PATH $OUTPUT_DIR"
                MSG="Created symbolic link: $OUTPUT_DIR -> $OUTPUT_TARGET_REAL_PATH"
            fi
        fi
        
        if [ "$CMD" != "" ]; then
            echo "CMD: ${CMD}"
            ${CMD}
        fi             
        echo "$MSG"
        
    else
        echo "the --symlink_target_path option is not set. so, skip to make symlink."
    fi
    echo -e "${TAG_SUCC} === Make Symbolic Link Complete ==="
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
                echo "'--output' is the same as the current directory. Please specify a different directory."
                exit 1
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
            echo "Unknown option: $1"
            show_help "error"
            ;;
    esac
    shift
done

echo "USE_EXTRACT($USE_EXTRACT)"
echo "USE_FORCE($USE_FORCE)"

# usage
if [ -z "$SOURCE_PATH" ] || [ -z "$OUTPUT_DIR" ]; then
    echo -e "${TAG_ERROR} SOURCE_PATH(${SOURCE_PATH}) or OUTPUT_DIR(${OUTPUT_DIR}) does not exist."
    show_help "error"
fi

download
generate_output
make_symlink

exit 0

