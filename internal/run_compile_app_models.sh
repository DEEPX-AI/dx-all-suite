#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/../")
COMPILER_PATH="${DX_AS_PATH}/dx-compiler"
RUNTIME_PATH="${DX_AS_PATH}/dx-runtime"
MODELZOO_PATH="${DX_AS_PATH}/dx-modelzoo"

# Default VENV_PATH, can be overridden by --venv_path option
VENV_PATH_DEFAULT="${DX_AS_PATH}/internal/venv-dx-as-internal"
VENV_PATH="${VENV_PATH_DEFAULT}" # Initialize with default

# variables for venv options
VENV_PATH_ARG="" # Stores user-provided venv path
VENV_FORCE_REMOVE="n"
VENV_REUSE="n"

ENABLE_DEBUG_LOGS=0
ENABLE_DEV_MODE=0

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh
source ${DX_AS_PATH}/scripts/common_util.sh

OUTPUT_DIR="$DX_AS_PATH/app_models"
AWS_CONFIG_FILE_PATH="${DX_AS_PATH}/internal/config/aws_config.properties"
COM_BIN_PATH=${COMPILER_PATH}/dx_com/dx_com/dx_com
COM_VERSION=""
USE_FORCE=0

# Function to display help message
show_help() {
    print_colored "Usage: $(basename "$0") --com_version=<version> [--help ]" "YELLOW"
    print_colored "Options:" "GREEN"
    print_colored "  --com_version=<version>        : Specify version (e.g., 1.60.1)" "GREEN"
    print_colored "  [--force]                      : Force overwrite if the file already exists" "GREEN"
    print_colored "  [--venv_path=<PATH>]           : Specify the path for the virtual environment (default: ${VENV_PATH_DEFAULT})" "GREEN"
    print_colored "  [--venv-force-remove]          : Force remove existing virtual environment at --venv_path before creation." "GREEN"
    print_colored "  [--venv-reuse]                 : Reuse existing virtual environment at --venv_path if it's valid, skipping creation." "GREEN"
    print_colored "  [--verbose]                    : Enable verbose (debug) logging." "GREEN"
    print_colored "  [--help]                       : Show this help message" "GREEN"

    if [ "$1" == "error" ] && [[ ! -n "$2" ]]; then
        print_colored "Invalid or missing arguments." "ERROR"
        exit 1
    elif [ "$1" == "error" ] && [[ -n "$2" ]]; then
        print_colored "$2" "ERROR"
        exit 1
    elif [[ "$1" == "warn" ]] && [[ -n "$2" ]]; then
        print_colored "$2" "WARNING"
        return 0
    fi
    exit 0
}

install_dx_compiler() {
    print_colored_v2 "INFO" "--- dx-compiler is installing ---"
    DX_COM_INSTALL_CMD="${COMPILER_PATH}/install.sh"
    echo "CMD : $DX_COM_INSTALL_CMD"
    $DX_COM_INSTALL_CMD || { print_colored "Install dx-compiler failed." "ERROR"; exit 1; }
    print_colored_v2 "INFO" "[OK] dx-compiler is installed."
}

download_app_models() {
    print_colored_v2 "INFO" "--- app models(onnx, json) files are downloading ---"
    
    PATTERN_ARGS="--include-pattern res/onnx/*.onnx --include-pattern res/json/*.json"
    
    # for testing
    # PATTERN_ARGS="--include-pattern res/onnx/YoloV7*.onnx --include-pattern res/json/YoloV7*.json"

    if [[ "$USE_FORCE" -eq 1 ]]; then
        print_colored_v2 "INFO" "Force option is enabled. Overwriting existing files."
        FORCE_ARGS="--force"
    fi

    DOWNLOAD_ONNX_CMD="dx-aws-s3 --config-file-path ${AWS_CONFIG_FILE_PATH} download --s3-path res --save-location ${OUTPUT_DIR} ${PATTERN_ARGS} ${FORCE_ARGS}" 
    
    echo "CMD : $DOWNLOAD_ONNX_CMD"
    $DOWNLOAD_ONNX_CMD || { print_colored "Download failed for app models(onnx, json)." "ERROR"; rm -rf ${OUTPUT_DIR}; exit 1; }
    print_colored_v2 "INFO" "[OK] app models(onnx, json) files are downloaded"
    tree ${OUTPUT_DIR}/onnx ${OUTPUT_DIR}/json
}

run_compile_app_models() {
    print_colored_v2 "INFO" "--- app models(onnx, json) are compiling ---"

    local calibration_dataset="${COMPILER_PATH}/dx_com/calibration_dataset"
    if [ -e "$calibration_dataset" ]; then
        rm -rf ./calibration_dataset || true
        ln -s $calibration_dataset ./calibration_dataset || { print_colored "Create Symlink failed for calibration_dataset" "ERROR"; exit 1; }
    else
        print_colored_v2 "ERROR" "${calibration_dataset} is not existed"
        exit 1
    fi

    COM_BIN_PATH_ARGS="--dx_com_bin_path ${COM_BIN_PATH}"
    MODEL_DIR_ARGS="--model_dir ${OUTPUT_DIR}"
    GEN_HTML_REPORT_ARGS="--gen_html_report"

    if [[ "$USE_FORCE" -eq 1 ]]; then
        print_colored_v2 "INFO" "Force option is enabled. Overwriting existing files."
        FORCE_ARGS="--force"
    fi

    COMPILER_APP_MODEL_CMD="python ${MODELZOO_PATH}/internal/run_compile.py ${COM_BIN_PATH_ARGS} ${MODEL_DIR_ARGS} ${GEN_HTML_REPORT_ARGS} ${FORCE_ARGS}"
    echo "CMD : $COMPILER_APP_MODEL_CMD"
    $COMPILER_APP_MODEL_CMD || { print_colored "Compile failed for app models(onnx, json)." "ERROR"; exit 1; }
    rm -rf ./calibration_dataset || true

    print_colored_v2 "INFO" "[OK] app models(onnx, json) are compiled"
}

upload_dxnn_to_aws_s3() {
    print_colored_v2 "INFO" "--- DXNN files uploading to s3://<your-bucket>/res/dxnn/${com_ver_dirname} ---"

    print_colored_v2 "INFO" "Get dx_com version to create s3 path"
    # 'DX-COM Version: 1.60.1'와 같은 출력에서 버전 문자열을 가져옴
    local com_version_str=$(${COM_BIN_PATH} -v | grep 'DX-COM Version:')
    if [[ -z "$com_version_str" ]]; then
        print_colored_v2 "ERROR" "Failed to get dx_com version from '${COM_BIN_PATH} -v'"
        exit 1
    fi

    # '1.60.1' 버전을 추출하고 '.'을 '_'로 변경하여 '1_60_1' 형식으로 만듬
    local com_ver_dirname=$(echo "$com_version_str" | sed -e 's/DX-COM Version: //' -e 's/\./_/g')
    print_colored_v2 "INFO" "DX-COM version for S3 path: ${com_ver_dirname}"

    local PATTERN_ARGS="--include-pattern ${OUTPUT_DIR}/dxnn/*.dxnn"
    local S3_UPLOAD_CMD="dx-aws-s3 --config-file-path ${AWS_CONFIG_FILE_PATH} upload --s3-path res/dxnn/${com_ver_dirname} --local-path ${OUTPUT_DIR}/dxnn ${PATTERN_ARGS}"

    print_colored_v2 "INFO" "Uploading dxnn files to S3..."
    echo "CMD: ${S3_UPLOAD_CMD}"
    ${S3_UPLOAD_CMD} || { print_colored_v2 "ERROR" "Upload dxnn files to S3 failed."; exit 1; }

    print_colored_v2 "INFO" "[OK] DXNN files uploaded to s3://<your-bucket>/res/dxnn/${com_ver_dirname}"
}

setup_venv() {
    print_colored_v2 "INFO" "--- setup python venv... ---"

    local VENV_CMD_ARGS="--venv_path=${VENV_PATH}"
    if [ "${VENV_FORCE_REMOVE}" = "y" ]; then
        VENV_CMD_ARGS+=" --venv-force-remove"
    fi
    if [ "${VENV_REUSE}" = "y" ]; then
        VENV_CMD_ARGS+=" --venv-reuse"
    fi

    # Pass the determined VENV_PATH and new options to install_python_and_venv.sh
    "${RUNTIME_PATH}/scripts/install_python_and_venv.sh" ${VENV_CMD_ARGS}
    if [ $? -ne 0 ]; then
        print_colored "Python and Virtual environment setup failed. Exiting." "ERROR"
        exit 1
    fi

    # Activate the venv for subsequent commands in this script
    . "${VENV_PATH}/bin/activate" || { print_colored "Failed to activate venv ${VENV_PATH}" "ERROR"; exit 1; }

    # for '--dev' mode
    if [ $ENABLE_DEV_MODE -eq 1 ]; then
        pip install -e ${SCRIPT_DIR}/.[test] || { print_colored "Install dx-aws-s3 failed." "ERROR"; exit 1; }
        print_colored_v2 "DEBUG" "ENABLE_DEV_MODE ON"

        DEV_CONFIG_FILE_PATH="${DX_AS_PATH}/internal/config/dev_config.properties"
        if [ -f ${DEV_CONFIG_FILE_PATH} ]; then
            source ${DEV_CONFIG_FILE_PATH}
            export DX_USERNAME
            export DX_PASSWORD
            export AWS_ACCESS_KEY
            export AWS_SECRET_KEY
            print_colored_v2 "DEBUG" "dev config properties file $DEV_CONFIG_FILE_PATH is loadded."
        else
            print_colored_v2 "DEBUG" "dev config properties file $DEV_CONFIG_FILE_PATH is not found."
        fi
    else
        pip install ${SCRIPT_DIR}/. || { print_colored "Install dx-aws-s3 failed." "ERROR"; exit 1; }
    fi
    
    print_colored_v2 "INFO" "[OK] Completed to setup python venv to '${VENV_PATH}'"
}

main() {
    setup_venv
    install_dx_compiler
    download_app_models
    run_compile_app_models
    upload_dxnn_to_aws_s3
}

# parse args
for i in "$@"; do
    case "$1" in
        --com_version=*)
            COM_VERSION="${1#*=}"
            ;;
        --force)
            USE_FORCE=1
            exit 0
            ;;
        --venv_path=*)
            VENV_PATH_ARG="${1#*=}"
            ;;
        --venv-force-remove)
            VENV_FORCE_REMOVE="y"
            ;;
        --venv-reuse)
            VENV_REUSE="y"
            ;;
        --verbose)
            ENABLE_DEBUG_LOGS=1
            ;;
        --dev)
            ENABLE_DEBUG_LOGS=1
            ENABLE_DEV_MODE=1
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            print_colored "${TAG_ERROR}: Invalid option '$1'" "ERROR"
            show_help
            exit 1
            ;;
    esac
    shift
done

# If user provided --venv_path, override the default VENV_PATH
if [ -n "${VENV_PATH_ARG}" ]; then
    VENV_PATH="${VENV_PATH_ARG}"
fi

if [ -n "${COM_VERSION}" ]; then
    print_colored "Specify dx_com version(${COM_VERSION}) is set." "INFO"
else
    print_colored "Specify dx_com version is not set. So, using compiler.properties" "INFO"
    # Properties file path
    VERSION_FILE="$COMPILER_PATH/compiler.properties"

    # read 'COM_VERSION' from properties file
    if [[ -f "$VERSION_FILE" ]]; then
        # load varialbles
        source "$VERSION_FILE"

        if [ -n "${COM_VERSION}" ]; then
            print_colored "'dx_com' version(${COM_VERSION}) is specified in ${VERSION_FILE}." "INFO"
        else
            print_colored "'dx_com' version is not specified in ${VERSION_FILE}." "ERROR"
            exit 1
        fi
    else
        print_colored "Version file '$VERSION_FILE' not found." "ERROR"
        print_colored "${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}" "INFO"
        exit 1
    fi
fi


main

exit 0
