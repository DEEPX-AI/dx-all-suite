#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
COMPILER_PATH=$(realpath -s "${SCRIPT_DIR}/../dx-compiler")
DX_COM_PATH=$(realpath -s "${COMPILER_PATH}/dx_com")
DX_AS_PATH=$(realpath -s "${COMPILER_PATH}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "COMPILER_PATH($COMPILER_PATH)"
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"

OUTPUT_PATH="${SCRIPT_DIR}/dxnn"

compile() {
    local model_name=$1
    echo -e "=== Compile model('${model_name}') ${TAG_START} ==="

    CMD="\
    ${DX_COM_PATH}/dx_com/dx_com \
        -m ${SCRIPT_DIR}/modelzoo/onnx/${model_name}.onnx \
        -c ${SCRIPT_DIR}/modelzoo/json/${model_name}.json \
        -o ${OUTPUT_PATH}/"

    echo "$CMD"

    $CMD
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Compile model('${model_name}') failed!"
        exit 1
    fi
    echo -e "=== Compile model('${model_name}') ${TAG_DONE} ==="
}

main() {
    MODEL_NAME_LIST=("YOLOV5S-1" "YOLOV5S_Face-1" "MobileNetV2-1")
    for i in "${!MODEL_NAME_LIST[@]}"; do
        compile ${MODEL_NAME_LIST[$i]}
    done
}

main

exit 0

