#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
RUNTIME_PATH=$(realpath -s "${SCRIPT_DIR}/../dx-runtime")
DX_AS_PATH=$(realpath -s "${RUNTIME_PATH}/..")

DX_APP_PATH="${RUNTIME_PATH}/dx_app"

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh
source ${DX_AS_PATH}/scripts/common_util.sh

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
    local cp_mobilenetv2_async_cmd="cp -dp ${DX_APP_PATH}/bin/mobilenetv2_async ${FORK_PATH}/bin/."
    local cp_yolov5_async_cmd="cp -dp ${DX_APP_PATH}/bin/yolov5s_async ${FORK_PATH}/bin/."
    local cp_yolov5face_async_cmd="cp -dp ${DX_APP_PATH}/bin/yolov5s_face_async ${FORK_PATH}/bin/."
    local err_msg_mobilenetv2_async="Failed to copy 'mobilenetv2_async' binary executable file."
    local err_msg_yolov5_async="Failed to copy 'yolov5s_async' binary executable file."
    local err_msg_yolov5face_async="Failed to copy 'yolov5s_face_async' binary executable file."
    local hint_msg="Please build dx_app first. using command"
    local suggested_action_cmd="${RUNTIME_PATH}/install.sh --target=dx_app"

    eval "$cp_mobilenetv2_async_cmd" || {
        # handle_cmd_failure function arguments
        #   - local error_message=$1
        #   - local hint_message=$2
        #   - local origin_cmd=$3
        #   - local suggested_action_cmd=$4
        handle_cmd_failure "$err_msg_mobilenetv2_async" "$hint_msg" "$cp_mobilenetv2_async_cmd" "$suggested_action_cmd"
    }

    eval "$cp_yolov5_async_cmd" || {
        # handle_cmd_failure function arguments
        #   - local error_message=$1
        #   - local hint_message=$2
        #   - local origin_cmd=$3
        #   - local suggested_action_cmd=$4
        handle_cmd_failure "$err_msg_yolov5_async" "$hint_msg" "$cp_yolov5_async_cmd" "$suggested_action_cmd"
    }

    eval "$cp_yolov5face_async_cmd" || {
        # handle_cmd_failure function arguments
        #   - local error_message=$1
        #   - local hint_message=$2
        #   - local origin_cmd=$3
        #   - local suggested_action_cmd=$4
        handle_cmd_failure "$err_msg_yolov5face_async" "$hint_msg" "$cp_yolov5face_async_cmd" "$suggested_action_cmd"
    }

    # copy input image sample for Image Classification Model
    # for Object Detection (YOLOV5S-1)
    mkdir -p ${FORK_PATH}/sample
    cp -dp ${DX_APP_PATH}/sample/img/sample_kitchen.jpg ${FORK_PATH}/sample/.
    # for Face Detection (YOLOV5S_Face-1)
    cp -dp ${DX_APP_PATH}/sample/img/sample_face.jpg ${FORK_PATH}/sample/.
    # for Image Classification (MobileNetV2-1-1)
    mkdir -p ${FORK_PATH}/sample/ILSVRC2012
    cp -dpR ${DX_APP_PATH}/sample/ILSVRC2012 ${FORK_PATH}/sample/.

    echo -e "=== fork dx_app examples to '${FORK_PATH}' ${TAG_DONE} ==="
}

run_example() {
    local exe_file_path=$1
    local dxnn_file_path=$2
    local image_path=$3
    local save_log=$4
    local loop=${5:-300}
    local additional_args=""

    echo -e "=== run_example ${TAG_START} ==="
    pushd ${FORK_PATH}

    if [ "${save_log}" = "y" ]; then
        SAVE_LOG_ARG=" > result-app.log"
    fi

    if [ ! -f /deepx/tty_flag ]; then
        echo -e "${TAG_INFO} <hint> Press ${COLOR_BRIGHT_GREEN_ON_BLACK}'q' or 'Ctrl+C'${COLOR_RESET} to exit result viewing"
    else
        if [ "${exe_file_path}" != "./bin/mobilenetv2_async" ]; then
            additional_args+=" --no-display"
        fi
    fi

    RUN_CMD="${exe_file_path} -m ${dxnn_file_path} -i ${image_path} ${SAVE_LOG_ARG} -l ${loop} ${additional_args}"
    echo "$RUN_CMD"
    eval "$RUN_CMD"
    if [ $? -ne 0 ]; then
        echo -e "${TAG_ERROR} Run example failed!"
        exit 1
    fi

    popd
    echo -e "=== run_example ${TAG_DONE} ==="
}

show_result() {
    local result_path=$1
    local result_real_path=$(realpath -s "${result_path}")

    if [ ! -f /deepx/tty_flag ]; then
        ## legacy code backup
        # echo -e "${TAG_INFO} <hint> Use the ${COLOR_BRIGHT_GREEN_ON_BLACK}'Page Up/Down'${COLOR_RESET} keys to view previous/next results"
        # echo -e "${TAG_INFO} <hint> Press ${COLOR_BRIGHT_GREEN_ON_BLACK}'q'${COLOR_RESET} to exit result viewing"
        # fim ${result_path}
        # rm -rf ${result_path}
       
        # temporary code: dx_app v3.0.0 is not supported save image files
        echo -e -n "${TAG_INFO} ${COLOR_BRIGHT_GREEN_ON_BLACK}Press any key and hit Enter to continue. ${COLOR_RESET}"
        read -r answer
    else
        echo -e "${TAG_WARN} ${COLOR_BRIGHT_YELLOW_ON_BLACK}You are currently running in a **tty session**, which does not support GUI. In such environments, it is not possible to visually confirm the results of example code execution via GUI. (Note): ${COLOR_RESET}"
        echo -e "${TAG_INFO} ${COLOR_BRIGHT_CYAN_ON_BLACK}The result has been saved at **${result_path}**. Please use the **docker cp** command or similar method to copy the file and check the result on your host. ${COLOR_RESET}"
        ## temporary disable code: dx_app v3.0.0 is not supported save image files
        # echo -e "${TAG_INFO} ${COLOR_BRIGHT_CYAN_ON_BLACK}(e.g.) 'docker cp <container_name>:${result_real_path} .' ${COLOR_RESET}"
        echo -e -n "${TAG_INFO} ${COLOR_BRIGHT_GREEN_ON_BLACK}Press any key and hit Enter to continue. ${COLOR_RESET}"
        read -r answer
    fi
}

main() {
    YOLO_FACE_TARGET_STR="${DX_AS_PATH}/getting-started/dxnn/YOLOV5S_Face-1.dxnn" #YOLOv5s_Face
    YOLO_V5S_TARGET_STR="${DX_AS_PATH}/getting-started/dxnn/YOLOV5S-1.dxnn" #YOLOV5S
    MOBILENET_V2_TARGET_STR="${DX_AS_PATH}/getting-started/dxnn/MobileNetV2-1.dxnn" #MobileNetV2

    # Check if the *.dxnn files were successfully generated using 'getting-started/compiler-4_model_compile.sh'
    DXNN_CHECK_LIST=("${YOLO_FACE_TARGET_STR}" "${YOLO_V5S_TARGET_STR}" "${MOBILENET_V2_TARGET_STR}")
    for i in "${!DXNN_CHECK_LIST[@]}"; do
        if [ ! -f ${DXNN_CHECK_LIST[$i]} ]; then
            echo -e "${TAG_ERROR} ${DXNN_CHECK_LIST[$i]} does not exist."
            echo -e "${TAG_INFO} (HINT) In the dx-compiler environment, use 'getting-started/compiler-4_model_compile.sh' to compile 'getting-started/modelzoo/onnx/*.onnx' into 'getting-started/dxnn/*.dxnn'."
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

    # yolo_face example
    echo -e "${TAG_START} === Yolov5 Face ==="
    rm -rf ${FORK_PATH}/result*.jpg
    run_example "./bin/yolov5s_face_async" "${YOLO_FACE_TARGET_STR}" "./sample/sample_face.jpg" "n" "30"
    show_result "${FORK_PATH}/result*.jpg"
    echo -e "${TAG_DONE} === YOLOV5 Face ==="

    # yolov5s example
    echo -e "${TAG_START} === Yolov5S ==="
    rm -rf ${FORK_PATH}/result*.jpg
    run_example "./bin/yolov5s_async" "${YOLO_V5S_TARGET_STR}" "./sample/sample_kitchen.jpg" "n" "300"
    show_result "${FORK_PATH}/result*.jpg"
    echo -e "${TAG_DONE} === Yolov5s ==="

    # mobilenetv2 example
    echo -e "${TAG_START} === MobileNetV2 ==="    
    rm -rf ${FORK_PATH}/result*.log
    run_example "./bin/mobilenetv2_async" "${MOBILENET_V2_TARGET_STR}" "./sample/ILSVRC2012/1.jpeg" "y" "300"
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

