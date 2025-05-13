#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"


# Function to display help message
show_help() {
    echo "Usage: $(basename "$0") [OPTIONS]"
    echo "Options:"
    echo "  [--force]     : Force overwrite if the file already exists"
    echo "  [--help]      : Show this help message"

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

download() {
    local model_name=$1
    local ext_name=$2

    echo -e "=== [#$i] Download : ${model_name}.${ext_name} ${TAG_START} ==="

    SOURCE_PATH="modelzoo/${ext_name}/${model_name}.${ext_name}"
    OUTPUT_DIR="${SCRIPT_DIR}/modelzoo/${ext_name}"
    EXTRACT_ARGS=""

    SYMLINK_TARGET_PATH="${DX_AS_PATH}/workspace/modelzoo/${ext_name}"
    SYMLINK_ARGS="--symlink_target_path=$SYMLINK_TARGET_PATH"

    GET_RES_CMD="${DX_AS_PATH}/scripts/get_resource.sh --src_path=$SOURCE_PATH --output=$OUTPUT_DIR $EXTRACT_ARGS $SYMLINK_ARGS $FORCE_ARGS"
    echo "Get Resources from remote server ..."
    echo "$GET_RES_CMD"

    $GET_RES_CMD
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Get model failed!"
        exit 1
    fi
    echo -e "=== [#$i] Download : ${model_name}.${ext_name} ${TAG_DONE} ==="
}

main() {
    FORCE_ARGS=""
    # parse args
    for i in "$@"; do
        case "$1" in
            --force)
                FORCE_ARGS="--force"
                ;;
            --help)
                show_help
                ;;
            *)
                show_help "error" "Invalid option '$1'"
                ;;
        esac
        shift
    done

    # usage
    BASE_URL="https://sdk.deepx.ai/"

    # default value
    MODEL_NAME_LIST=("YOLOV5S-1" "YOLOV5S_Face-1" "MobileNetV2-1")
    EXT_LIST=("onnx" "json")
    for i in "${!MODEL_NAME_LIST[@]}"; do
        for j in "${!EXT_LIST[@]}"; do
            download ${MODEL_NAME_LIST[$i]} ${EXT_LIST[$j]}
        done
    done
}

main

exit 0

