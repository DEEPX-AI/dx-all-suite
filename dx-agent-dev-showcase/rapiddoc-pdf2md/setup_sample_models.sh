#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")

# color env settings
source ${SCRIPT_DIR}/deepx_scripts/color_env.sh
source ${SCRIPT_DIR}/deepx_scripts/common_util.sh

BASE_URL="https://sdk.deepx.ai/"

# default value
DXNN_SOURCE_PATH="res/assets/dx_RapidDoc/dxnn_models.tar.gz"
ONNX_SOURCE_PATH="res/assets/dx_RapidDoc/onnx_models.tar.gz"
OUTPUT_DIR="$SCRIPT_DIR"
SYMLINK_TARGET_PATH=""
SYMLINK_ARGS=""
FORCE_ARGS=""
CUSTOM_SOURCE_PATH=""

# Function to display help message
show_help() {
  
  echo "Usage: $(basename "$0") [OPTIONS]"
  echo "Options:"
    echo "  [--output=<dir>]            Output directory (default: RapidDoc root)"
    echo "  [--symlink_target_path=<d>] Optional symlink target path"
    echo "  [--src_path=<path>]         Download only the given source path instead of defaults"
  echo "  [--force]                  Force overwrite if the file already exists"
  echo "  [--help]                   Show this help message"

  if [ "$1" == "error" ]; then
    echo "Error: Invalid or missing arguments."
    exit 1
  fi
  exit 0
}

main() {
    SCRIPT_DIR=$(realpath "$(dirname "$0")")
    local sources=()
    if [ -n "$CUSTOM_SOURCE_PATH" ]; then
        sources=("$CUSTOM_SOURCE_PATH")
    else
        sources=("$DXNN_SOURCE_PATH" "$ONNX_SOURCE_PATH")
    fi

    echo "Get Resources from remote server ..."
    for SOURCE_PATH in "${sources[@]}"; do
        local get_res_cmd="bash $SCRIPT_DIR/deepx_scripts/get_resource.sh --src_path=$SOURCE_PATH --output=$OUTPUT_DIR $SYMLINK_ARGS $FORCE_ARGS --extract"
        echo "$get_res_cmd"

        $get_res_cmd || {
            local error_msg="Get resource failed!"
            local hint_msg="If the issue persists, please try again with sudo and the --force option, like this: 'sudo ./setup_sample_models.sh --force'."
            local origin_cmd="" # no need to run origin command
            local suggested_action_cmd="sudo $get_res_cmd --force"

            # handle_cmd_failure function arguments
            #   - local error_message=$1
            #   - local hint_message=$2
            #   - local origin_cmd=$3
            #   - local suggested_action_cmd=$4
            handle_cmd_failure "$error_msg" "$hint_msg" "$origin_cmd" "$suggested_action_cmd"
        }
    done
}

# parse args
for i in "$@"; do
    case "$1" in
        --src_path=*)
            CUSTOM_SOURCE_PATH="${1#*=}"
            ;;
        --output=*)
            OUTPUT_DIR="${1#*=}"

            # Symbolic link cannot be created when output_dir is the current directory.
            OUTPUT_REAL_DIR=$(readlink -f "$OUTPUT_DIR")
            CURRENT_REAL_DIR=$(readlink -f "./")
            if [ "$OUTPUT_REAL_DIR" == "$CURRENT_REAL_DIR" ]; then
                echo "'--output' points to the current directory. Symlink creation will be skipped."
            fi
            ;;
        --symlink_target_path=*)
            SYMLINK_TARGET_PATH="${1#*=}"
            SYMLINK_ARGS="--symlink_target_path=$SYMLINK_TARGET_PATH"
            ;;
        --force)
            FORCE_ARGS="--force"
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

main

exit 0
