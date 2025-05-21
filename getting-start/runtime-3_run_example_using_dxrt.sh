#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}/../dx-runtime")
DX_AS_PATH=$(realpath -s "${RUNTIME_PATH}/..")

DX_APP_PATH="${RUNTIME_PATH}/dx_app"

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

echo -e "======== PATH INFO ========="
echo "RUNTIME_PATH($RUNTIME_PATH)"
echo "DX_AS_PATH($DX_AS_PATH)"
echo "DX_APP_PATH($DX_APP_PATH)"
echo -e "============================"

pushd ${SCRIPT_DIR}

FORK_PATH="./forked_dx_app_example"

# fork dx_app example application binary executable files and input images
fork_examples() {
    echo -e "=== fork dx_app examples to '${FORK_PATH}' ${TAG_START} ==="
    
    # copy dx_app example application binary executable files
    mkdir -p  ${FORK_PATH}/bin
    cp -dp ${DX_APP_PATH}/bin/run_detector ${FORK_PATH}/bin/.
    cp -dp ${DX_APP_PATH}/bin/run_classifier ${FORK_PATH}/bin/.

    # copy dx_app example application configration(json) files
    mkdir -p ${FORK_PATH}/example/run_detector
    mkdir -p ${FORK_PATH}/example/run_classifier
    # for Object Detection (YOLOV5S-1)
    cp -dp ${DX_APP_PATH}/example/run_detector/yolov5s3_example.json ${FORK_PATH}/example/run_detector/.
    # for Face Detection (YOLOV5S_Face-1)
    cp -dp ${DX_APP_PATH}/example/run_detector/yolo_face_example.json ${FORK_PATH}/example/run_detector/.
    # for Image Classification (MobileNetV2-1-1)
    cp -dp ${DX_APP_PATH}/example/run_classifier/imagenet_example.json ${FORK_PATH}/example/run_classifier/.
    

    # copy input image sample for Image Classification Model
    # for Object Detection (YOLOV5S-1)
    mkdir -p ${FORK_PATH}/sample
    cp -dp ${DX_APP_PATH}/sample/1.jpg ${FORK_PATH}/sample/.
    cp -dp ${DX_APP_PATH}/sample/2.jpg ${FORK_PATH}/sample/.
    cp -dp ${DX_APP_PATH}/sample/3.jpg ${FORK_PATH}/sample/.
    cp -dp ${DX_APP_PATH}/sample/4.jpg ${FORK_PATH}/sample/.
    cp -dp ${DX_APP_PATH}/sample/5.jpg ${FORK_PATH}/sample/.
    # for Face Detection (YOLOV5S_Face-1)
    cp -dp ${DX_APP_PATH}/sample/face_sample.jpg ${FORK_PATH}/sample/.
    # for Image Classification (MobileNetV2-1-1)
    mkdir -p ${FORK_PATH}/sample/ILSVRC2012
    cp -dpR ${DX_APP_PATH}/sample/ILSVRC2012 ${FORK_PATH}/sample/.

    # Initialize a Git repository and make the initial commit to enable diff checking
    pushd ${FORK_PATH}
    git init && git config user.email "you@example.com" && git config user.name "Your Name"
    git add . && git commit -m "initial commit"
    popd

    echo -e "=== fork dx_app examples to '${FORK_PATH}' ${TAG_DONE} ==="
}

replace_all() {
    local example_file_path=$1
    local source_str=$2
    local target_str=$3

    HIJACK_CMD="sed -i \
    -e 's|${source_str}|${target_str}|g' \
    ${TARGET_FILE}"

    echo "$HIJACK_CMD"
    eval "$HIJACK_CMD"
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Hijack example failed!"
        exit 1
    fi
}

show_diff() {
    local commit_msg=$1
    echo -e "---------------- ${TAG_INFO} show hijacking diff [BEGIN] ----------------"

    pushd ${FORK_PATH}
    # Make a commit for diff comparison
    # rm -rf ./result*.*
    git add . && git commit -m "hijack: ${commit_msg}" && git --no-pager diff HEAD~1
    echo -e -n "${TAG_INFO} ${COLOR_BRIGHT_GREEN_ON_BLACK}Press any key and hit Enter to continue. ${COLOR_RESET}"
    read -r answer
    popd

    echo -e "---------------- ${TAG_INFO} show hijacking diff  [END]  ----------------"
}

hijack_example() {
    local example_file_path=$1
    local source_str=$2
    local target_str=$3
    local commit_msg=$4

    echo -e "=== hijack example ${TAG_START} ==="

    # backup file
    TARGET_FILE="${FORK_PATH}/${example_file_path}"

    # hijack
    replace_all "${TARGET_FILE}" ${source_str} ${target_str}

    # show diff
    show_diff "${commit_msg}"
    echo -e "=== hijack example path ${TAG_DONE} ==="
}

run_hijacked_example() {
    local exe_file_path=$1
    local example_file_path=$2
    local save_log=$3

    echo -e "=== run_hijacked_example ${TAG_START} ==="
    pushd ${FORK_PATH}

    if [ "${save_log}" = "y" ]; then
        SAVE_LOG_ARG=" > result-app.log"
    fi
    
    RUN_CMD="${exe_file_path} -c ${example_file_path} ${SAVE_LOG_ARG}"
    echo "$RUN_CMD"
    eval "$RUN_CMD"
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Run hijacked example failed!"
        exit 1
    fi

    popd
    echo -e "=== run_hijacked_example ${TAG_DONE} ==="
}

show_result() {
    local result_path=$1
    local result_real_path=$(realpath -s "${result_path}")

    if [ ! -f /deepx/tty_flag ]; then
        echo -e "${TAG_INFO} <hint> Use the ${COLOR_BRIGHT_GREEN_ON_BLACK}'Page Up/Down'${COLOR_RESET} keys to view previous/next results"
        echo -e "${TAG_INFO} <hint> Press ${COLOR_BRIGHT_GREEN_ON_BLACK}'q'${COLOR_RESET} to exit result viewing"
        fim ${result_path}
        rm -rf ${result_path}
    else
        echo -e "${TAG_WARN} ${COLOR_BRIGHT_YELLOW_ON_BLACK}You are currently running in a **tty session**, which does not support GUI. In such environments, it is not possible to visually confirm the results of example code execution via GUI. (Note): ${COLOR_RESET}"
        echo -e "${TAG_INFO} ${COLOR_BRIGHT_CYAN_ON_BLACK}The result has been saved at **${result_path}**. Please use the **docker cp** command or similar method to copy the file and check the result on your host. ${COLOR_RESET}"
        echo -e "${TAG_INFO} ${COLOR_BRIGHT_CYAN_ON_BLACK}(e.g.) 'docker cp <container_name>:${result_real_path} .' ${COLOR_RESET}"
        echo -e -n "${TAG_INFO} ${COLOR_BRIGHT_GREEN_ON_BLACK}Press any key and hit Enter to continue. ${COLOR_RESET}"
        read -r answer
    fi
}

main() {
    YOLO_FACE_TARGET_STR="${DX_AS_PATH}/getting-start/dxnn/YOLOV5S_Face-1.dxnn"
    YOLO_V5S_TARGET_STR="${DX_AS_PATH}/getting-start/dxnn/YOLOV5S-1.dxnn"
    MOBILENET_V2_TARGET_STR="${DX_AS_PATH}/getting-start/dxnn/MobileNetV2-1.dxnn"

    # Check if the *.dxnn files were successfully generated using 'getting-start/compiler-4_model_compile.sh'
    DXNN_CHECK_LIST=("${YOLO_FACE_TARGET_STR}" "${YOLO_V5S_TARGET_STR}" "${MOBILENET_V2_TARGET_STR}")
    for i in "${!DXNN_CHECK_LIST[@]}"; do
        if [ ! -f ${DXNN_CHECK_LIST[$i]} ]; then
            echo -e "${TAG_ERROR} ${DXNN_CHECK_LIST[$i]} does not exist."
            echo -e "${TAG_INFO} (HINT) In the dx-compiler environment, use 'getting-start/compiler-4_model_compile.sh' to compile 'getting-start/modelzoo/onnx/*.onnx' into 'getting-start/dxnn/*.dxnn'."
            exit 1
        fi
    done

    # Check if 'fim' is installed
    if ! command -v fim &> /dev/null; then
        echo -e "${TAG_INFO} 'fim' is not installed. Installing now..."

        sudo apt update && \
        sudo apt install -y fim

        # Check if installation was successful
        if command -v fim &> /dev/null; then
            echo -e "${TAG_INFO} 'fim' has been successfully installed."
        else
            echo -e "${TAG_ERROR} Failed to install 'fim'. Please check your sources or try installing manually."
        fi
    else
        echo -e "${TAG_INFO} 'fim' is already installed."
    fi

    if [ -d "${FORK_PATH}" ]; then
        echo "forked example (${FORK_PATH}) already exists. It will be removed and recreated."
        rm -rf ${FORK_PATH}
    fi
    mkdir -p ${FORK_PATH}

    # fork dx_app example (yolo_face, yolov5s, mobilenetv2)
    fork_examples


    echo -e "${TAG_START} === Yolov5 Face ==="
    COMMIT_MSG="Updated to use '*.dxnn' files compiled by the user with 'dx_com'"

    # hijack yolo_face example
    YOLO_FACE_EXAMPLE_PATH="example/run_detector/yolo_face_example.json"
    YOLO_FACE_SOURCE_STR="./assets/models/YOLOV5S_Face-1.dxnn"
    hijack_example "${YOLO_FACE_EXAMPLE_PATH}" "${YOLO_FACE_SOURCE_STR}" "${YOLO_FACE_TARGET_STR}" "${COMMIT_MSG}"

    # run yolo_face hijakced example
    rm -rf ${FORK_PATH}/result*.jpg
    run_hijacked_example "./bin/run_detector" "${YOLO_FACE_EXAMPLE_PATH}"
    show_result "${FORK_PATH}/result*.jpg"
    echo -e "${TAG_DONE} === YOLOV5 Face ==="


    echo -e "${TAG_START} === Yolov5S ==="
    # hijack yolov5s example
    YOLO_V5S_EXAMPLE_PATH="example/run_detector/yolov5s3_example.json"
    YOLO_V5S_SOURCE_STR="./assets/models/YOLOV5S_3.dxnn"
    hijack_example "${YOLO_V5S_EXAMPLE_PATH}" "${YOLO_V5S_SOURCE_STR}" "${YOLO_V5S_TARGET_STR}" "${COMMIT_MSG}"

    # run yolov5s hijakced example
    rm -rf ${FORK_PATH}/result*.jpg
    run_hijacked_example "./bin/run_detector" "${YOLO_V5S_EXAMPLE_PATH}"
    show_result "${FORK_PATH}/result*.jpg"
    echo -e "${TAG_DONE} === Yolov5s ==="


    # hijack mobilenetv2 example
    echo -e "${TAG_START} === MobileNetV2 ==="
    MOBILENET_V2_EXAMPLE_PATH="example/run_classifier/imagenet_example.json"
    MOBILENET_V2_SOURCE_STR="./assets/models/EfficientNetB0_4.dxnn"
    hijack_example "${MOBILENET_V2_EXAMPLE_PATH}" "${MOBILENET_V2_SOURCE_STR}" "${MOBILENET_V2_TARGET_STR}" "${COMMIT_MSG}"

    # run mobilenetv2 hijakced example
    rm -rf ${FORK_PATH}/result*.log
    run_hijacked_example "./bin/run_classifier" "${MOBILENET_V2_EXAMPLE_PATH}" "y"
    echo -e "${TAG_INFO} -------- [Result of MobileNetV2 example] --------"
    echo -e -n "${COLOR_BRIGHT_YELLOW_ON_BLACK}"
    cat ${FORK_PATH}/result-app.log
    echo -e -n "${COLOR_RESET}"
    echo -e "${TAG_INFO} -------------------------------------------------"
    echo -e -n "${TAG_INFO} ${COLOR_BRIGHT_GREEN_ON_BLACK}Press any key and hit Enter to continue. ${COLOR_RESET}"
    read -r answer
    rm -rf ${FORK_PATH}/result*.log
    echo -e "${TAG_DONE} === MobileNetV2 ==="
}

main

popd

exit 0

