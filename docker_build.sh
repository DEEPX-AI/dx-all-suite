#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}")
COMPILER_PATH="${DX_AS_PATH}/dx-compiler"

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh
source ${DX_AS_PATH}/scripts/common_util.sh

pushd "$DX_AS_PATH" >&2

OUTPUT_DIR="$DX_AS_PATH/archives"
UBUNTU_VERSION=""
DEBIAN_VERSION=""
FEDORA_VERSION=""
RHEL_VERSION=""
CENTOS_VERSION=""
BASE_IMAGE_NAME=""
OS_VERSION=""

NVIDIA_GPU_MODE=0
INTERNAL_MODE=0
RE_ARCHIVE_ARGS=""
PYPI_ARGS=""

# Properties file path
VERSION_FILE="$COMPILER_PATH/compiler.properties"

# read 'COM_VERSION' from properties file
if [[ -f "$VERSION_FILE" ]]; then
    # load varialbles
    source "$VERSION_FILE"
else
    print_colored_v2 "ERROR" "Version file '$VERSION_FILE' not found.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"
    exit 1
fi

if [ -n "${COM_VERSION}" ]; then
    print_colored_v2 "INFO" "dx_com version(${COM_VERSION}) is set."
else
    print_colored_v2 "ERROR" "'dx_com' version is not specified in ${VERSION_FILE}."
    exit 1
fi

if [ -n "${TRON_VERSION}" ]; then
    print_colored_v2 "INFO" "dx_tron version(${TRON_VERSION}) is set."
else
    print_colored_v2 "ERROR" "'dx_tron' version is not specified in ${VERSION_FILE}."
    exit 1
fi

FILE_DXCOM="archives/dx_com_M1_v${COM_VERSION}.tar.gz"
FILE_DXTRON="archives/dxtron_${TRON_VERSION}.tar.gz"
HOST_UID=$(id -u)
HOST_GID=$(id -g)
TARGET_USER=deepx
TARGET_HOME=/deepx

# Function to display help message
show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--all${COLOR_RESET} ${COLOR_YELLOW}--ubuntu_version=<version>${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--target=<dx-compiler>${COLOR_RESET} ${COLOR_YELLOW}(--ubuntu_version=<version> | --fedora_version=<version> | --rhel_version=<version> | --centos_version=<version>)${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--target=<dx-runtime | dx-modelzoo>${COLOR_RESET} ${COLOR_YELLOW}(--ubuntu_version=<version> | --debian_version=<version>)${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Required (choose one target option):${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}--all${COLOR_RESET}                          Run all DXNN® containers (dx-compiler & dx-runtime & dx-modelzoo)"
    echo -e "  ${COLOR_GREEN}--target=<environment_name>${COLOR_RESET}    Run specific DXNN® container"
    echo -e "                                   Available: ${COLOR_CYAN}dx-compiler${COLOR_RESET} | ${COLOR_CYAN}dx-runtime${COLOR_RESET} | ${COLOR_CYAN}dx-modelzoo${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Required (choose one OS option):${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}--ubuntu_version=<version>${COLOR_RESET}     Specify Ubuntu version (ex: 26.04, 24.04, 22.04, 20.04)"
    echo -e "  ${COLOR_YELLOW}--debian_version=<version>${COLOR_RESET}     Specify Debian version (ex: 12)"
    echo -e "  ${COLOR_YELLOW}--fedora_version=<version>${COLOR_RESET}     Specify Fedora version (ex: 42, 43, 44, 45) ${COLOR_RED}(dx-compiler only)${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}--rhel_version=<version>${COLOR_RESET}       Specify RHEL/UBI version (ex: 9, 10) ${COLOR_RED}(dx-compiler only)${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}--centos_version=<version>${COLOR_RESET}     Specify CentOS Stream version (ex: stream9, stream10) ${COLOR_RED}(dx-compiler only)${COLOR_RESET}"
    echo -e "                                   Note: ${COLOR_CYAN}dx-compiler${COLOR_RESET} supports Ubuntu, Fedora, RHEL, and CentOS Stream"
    echo -e "                                   Note: ${COLOR_CYAN}dx-runtime${COLOR_RESET} and ${COLOR_CYAN}dx-modelzoo${COLOR_RESET} support Ubuntu and Debian only"
    echo -e ""
    echo -e "${COLOR_BOLD}Optional:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}[--driver_update]${COLOR_RESET}              Install 'dx_rt_npu_linux_driver' in the host environment"
    echo -e "  ${COLOR_GREEN}[--no-cache]${COLOR_RESET}                   Build Docker images freshly without cache"
    echo -e "  ${COLOR_GREEN}[--skip-archive]${COLOR_RESET}               Skip archiving dx-compiler or dx-runtime or dx-modelzoo before building"
    echo -e "  ${COLOR_GREEN}[--re-archive=<true|false>]${COLOR_RESET}    Force rebuild archive for dx-compiler (default: true)"
    echo -e "  ${COLOR_GREEN}[--help]${COLOR_RESET}                       Show this help message"
    echo -e ""
    echo -e "${COLOR_BOLD}Examples:${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --fedora_version=42${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --rhel_version=9${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --centos_version=stream9${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-runtime --ubuntu_version=24.04 --driver_update${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-runtime --debian_version=12 --driver_update${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-modelzoo --ubuntu_version=24.04 --driver_update${COLOR_RESET}"
    echo -e ""

    if [ "$1" == "error" ] && [[ ! -n "$2" ]]; then
        print_colored_v2 "ERROR" "Invalid or missing arguments."
        exit 1
    elif [ "$1" == "error" ] && [[ -n "$2" ]]; then
        print_colored_v2 "ERROR" "$2"
        exit 1
    elif [[ "$1" == "warn" ]] && [[ -n "$2" ]]; then
        print_colored_v2 "WARNING" "$2"
        return 0
    fi
    exit 0
}

docker_build_impl()
{
    local target=$1
    local config_file_args=${2:--f docker/docker-compose.yml}
    local no_cache_arg=""

    if [ ${NVIDIA_GPU_MODE} -eq 1 ]; then
        config_file_args="${config_file_args} -f docker/docker-compose.nvidia_gpu.yml"
    fi

    if [ ${INTERNAL_MODE} -eq 1 ]; then
        config_file_args="${config_file_args} -f docker/docker-compose.internal.yml"
    fi

    if [ "$NO_CACHE" = "y" ]; then
        no_cache_arg="--no-cache"
    fi

    # Build Docker image variables ...
    export DOCKER_BUILDKIT=1
    export COMPOSE_BAKE=true
    export BASE_IMAGE_NAME=${BASE_IMAGE_NAME}
    export OS_VERSION=${OS_VERSION}
    export TAG_NAME=${TAG_NAME:-${OS_VERSION}}
    export IMAGE_TAG_SUFFIX=${IMAGE_TAG_SUFFIX:-${BASE_IMAGE_NAME}-${OS_VERSION}}
    export FILE_DXCOM=${FILE_DXCOM}
    export FILE_DXTRON=${FILE_DXTRON}
    export HOST_UID=${HOST_UID}
    export HOST_GID=${HOST_GID}
    export TARGET_USER=${TARGET_USER}
    export TARGET_HOME=${TARGET_HOME}

    # Timezone mount: only mount /etc/timezone if it exists on the host
    if [ -f /etc/timezone ]; then
        export TIMEZONE_MOUNT="/etc/timezone"
        export TIMEZONE_MOUNT_TARGET="/etc/timezone"
    else
        export TIMEZONE_MOUNT="/dev/null"
        export TIMEZONE_MOUNT_TARGET="/dev/null"
    fi

    # XAUTHORITY setup ...
    if [ ! -n "${XAUTHORITY}" ]; then
        print_colored_v2 "INFO" "XAUTHORITY env is not set. so, try to set automatically."
        DUMMY_XAUTHORITY="/tmp/dummy"
        touch ${DUMMY_XAUTHORITY}
        export XAUTHORITY=${DUMMY_XAUTHORITY}
        export XAUTHORITY_TARGET=${DUMMY_XAUTHORITY}
    else
        print_colored_v2 "INFO" "XAUTHORITY(${XAUTHORITY}) is set"
        export XAUTHORITY_TARGET="/tmp/.docker.xauth"
    fi

    docker buildx use default
    CMD="docker compose ${config_file_args} build ${no_cache_arg} dx-${target}"
    echo "${CMD}"

    ${CMD} || { print_colored_v2 "ERROR" "docker build 'dx-${target}' failed. "; exit 1; }
}

docker_build_all() 
{
    docker_build_dx-compiler
    docker_build_dx-runtime
    docker_build_dx-modelzoo
}

archive_dx-compiler()
{
    # dx-compiler supports ubuntu, fedora, rhel, centos
    if [ "${BASE_IMAGE_NAME}" != "ubuntu" ] && [ "${BASE_IMAGE_NAME}" != "fedora" ] && \
       [ "${BASE_IMAGE_NAME}" != "redhat/ubi9" ] && [ "${BASE_IMAGE_NAME}" != "redhat/ubi10" ] && \
       [ "${BASE_IMAGE_NAME}" != "quay.io/centos/centos" ]; then
        print_colored_v2 "SKIP" "dx-compiler does not support ${BASE_IMAGE_NAME}. Skipping archive."
        return 0
    fi

    print_colored_v2 "INFO" "Archiving dx-compiler"

    # Internal mode: archive runs pip/requests on the HOST (venv setup upgrades
    # setuptools/wheel from PyPI; downloader.py fetches dx-tron tarball). pip uses
    # certifi (not the OS trust store), so it can't verify the FortiGate MITM cert
    # on inspected hosts (pypi.org). But some hosts are NOT MITM'd and serve a real
    # public cert (sdk.deepx.ai -> Amazon CA), so pointing at the lone FortiGate cert
    # breaks those. The OS trust bundle already contains BOTH the FortiGate CA (IT
    # installed it) and the public roots, so build a combined bundle from the OS
    # bundle + the intranet CA and point pip/requests at that.
    if [ "${INTERNAL_MODE}" -eq 1 ]; then
        local INTRANET_CA="${DX_AS_PATH}/intranet_CA_SSL.crt"
        local OS_CA_BUNDLE=""
        for c in /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt; do
            [ -f "$c" ] && { OS_CA_BUNDLE="$c"; break; }
        done
        if [ -f "${INTRANET_CA}" ] && [ -n "${OS_CA_BUNDLE}" ]; then
            local COMBINED_CA="${OUTPUT_DIR}/.intranet_ca_bundle.crt"
            mkdir -p "${OUTPUT_DIR}"
            cat "${OS_CA_BUNDLE}" "${INTRANET_CA}" > "${COMBINED_CA}"
            print_colored_v2 "INFO" "Internal mode: using combined CA bundle for host pip/requests (${COMBINED_CA})"
            export PIP_CERT="${COMBINED_CA}"
            export REQUESTS_CA_BUNDLE="${COMBINED_CA}"
            export CURL_CA_BUNDLE="${COMBINED_CA}"
        else
            print_colored_v2 "WARNING" "Internal mode but intranet CA (${INTRANET_CA}) or OS CA bundle not found. Host pip/requests may fail SSL verification."
        fi
    fi

    # Architecture check (archive downloads x86_64 binaries only)
    arch_check "amd64 x86_64" || {
        print_colored_v2 "SKIP" "Current architecture is not supported. Skip and continue to next target."
        return 0
    }

    # Determine default Python version based on OS version
    local PYTHON_VERSION_ARG=""
    case "${BASE_IMAGE_NAME}" in
        ubuntu)
            case "${OS_VERSION}" in
                20.04) PYTHON_VERSION_ARG="--python_version=3.8" ;;
                22.04) PYTHON_VERSION_ARG="--python_version=3.10" ;;
                24.04) PYTHON_VERSION_ARG="--python_version=3.12" ;;
                26.04) PYTHON_VERSION_ARG="--python_version=3.14" ;;
                *)
                    print_colored_v2 "ERROR" "Unsupported OS version: ${BASE_IMAGE_NAME} ${OS_VERSION}. Supported versions: Ubuntu 20.04, 22.04, 24.04, 26.04"
                    return 1
                    ;;
            esac
            ;;
        fedora)
            case "${OS_VERSION}" in
                42) PYTHON_VERSION_ARG="--python_version=3.13" ;;
                43) PYTHON_VERSION_ARG="--python_version=3.14" ;;
                44) PYTHON_VERSION_ARG="--python_version=3.14" ;;
                45) PYTHON_VERSION_ARG="--python_version=3.14" ;;
                *)
                    print_colored_v2 "ERROR" "Unsupported Fedora version: ${OS_VERSION}. Supported: 42, 43, 44, 45"
                    return 1
                    ;;
            esac
            ;;
        redhat/ubi9)
            PYTHON_VERSION_ARG="--python_version=3.9"
            ;;
        redhat/ubi10)
            PYTHON_VERSION_ARG="--python_version=3.12"
            ;;
        quay.io/centos/centos)
            case "${OS_VERSION}" in
                stream9) PYTHON_VERSION_ARG="--python_version=3.9" ;;
                stream10) PYTHON_VERSION_ARG="--python_version=3.12" ;;
                *)
                    print_colored_v2 "ERROR" "Unsupported CentOS Stream version: ${OS_VERSION}. Supported: stream9, stream10"
                    return 1
                    ;;
            esac
            ;;
    esac
    print_colored_v2 "INFO" "Using Python version for ${BASE_IMAGE_NAME} ${OS_VERSION}: ${PYTHON_VERSION_ARG:-default}"

    # Capture output from archive script
    ARCHIVE_OUTPUT=$(${DX_AS_PATH}/scripts/archive_dx-compiler.sh ${RE_ARCHIVE_ARGS} ${PYTHON_VERSION_ARG} ${PYPI_ARGS})
    ARCHIVE_EXIT_CODE=$?
    
    if [ $ARCHIVE_EXIT_CODE -ne 0 ]; then
        print_colored_v2 "ERROR" "Archiving dx-compiler failed."
        return 1
    fi
    
    # Extract archived file paths from output
    ARCHIVED_COM=$(echo "$ARCHIVE_OUTPUT" | grep "^ARCHIVED_COM_FILE=" | tail -1 | cut -d'=' -f2)
    ARCHIVED_TRON=$(echo "$ARCHIVE_OUTPUT" | grep "^ARCHIVED_TRON_FILE=" | tail -1 | cut -d'=' -f2)
    
    # Update FILE_DXCOM and FILE_DXTRON if archived files were found
    if [ -n "$ARCHIVED_COM" ] && [ -f "$ARCHIVED_COM" ]; then
        FILE_DXCOM="${ARCHIVED_COM#${DX_AS_PATH}/}"  # Remove DX_AS_PATH prefix for relative path
        print_colored_v2 "INFO" "Updated FILE_DXCOM to: $FILE_DXCOM"
    fi
    
    if [ -n "$ARCHIVED_TRON" ] && [ -f "$ARCHIVED_TRON" ]; then
        FILE_DXTRON="${ARCHIVED_TRON#${DX_AS_PATH}/}"  # Remove DX_AS_PATH prefix for relative path
        print_colored_v2 "INFO" "Updated FILE_DXTRON to: $FILE_DXTRON"
    fi

    print_colored_v2 "SUCCESS" "Archiving dx-compiler is done."
    return 0
}

docker_build_dx-compiler() 
{
    # dx-compiler supports ubuntu, fedora, rhel, centos
    if [ "${BASE_IMAGE_NAME}" != "ubuntu" ] && [ "${BASE_IMAGE_NAME}" != "fedora" ] && \
       [ "${BASE_IMAGE_NAME}" != "redhat/ubi9" ] && [ "${BASE_IMAGE_NAME}" != "redhat/ubi10" ] && \
       [ "${BASE_IMAGE_NAME}" != "quay.io/centos/centos" ]; then
        print_colored_v2 "SKIP" "dx-compiler does not support ${BASE_IMAGE_NAME}. Skipping build."
        return 0
    fi

    # Architecture check (x86_64 only)
    arch_check "amd64 x86_64" || {
        print_colored_v2 "SKIP" "Current architecture is not supported. Skip and continue to next target."
        return 0
    }

    # Validate that archive files exist before building
    if [ ! -f "${DX_AS_PATH}/${FILE_DXCOM}" ]; then
        print_colored_v2 "ERROR" "Archive file not found: ${FILE_DXCOM}. Please run archive step first."
        return 1
    fi
    if [ ! -f "${DX_AS_PATH}/${FILE_DXTRON}" ]; then
        # For non-Debian (Fedora/RHEL/CentOS), DX-Tron .deb is not supported.
        # Create a dummy empty archive so Docker ADD doesn't fail.
        if [ "${BASE_IMAGE_NAME}" != "ubuntu" ] && [ "${BASE_IMAGE_NAME}" != "debian" ]; then
            print_colored_v2 "INFO" "DX-Tron not supported on ${BASE_IMAGE_NAME}. Creating dummy archive."
            mkdir -p "$(dirname "${DX_AS_PATH}/${FILE_DXTRON}")"
            tar czf "${DX_AS_PATH}/${FILE_DXTRON}" -T /dev/null
        else
            print_colored_v2 "ERROR" "Archive file not found: ${FILE_DXTRON}. Please run archive step first."
            return 1
        fi
    fi

    local docker_compose_args="-f docker/docker-compose.yml"
    docker_build_impl "compiler" "${docker_compose_args}"
    return 0
}

docker_build_dx-runtime()
{
    # dx-runtime supports ubuntu and debian only
    if [ "${BASE_IMAGE_NAME}" == "fedora" ] || \
       [ "${BASE_IMAGE_NAME}" == "redhat/ubi9" ] || [ "${BASE_IMAGE_NAME}" == "redhat/ubi10" ] || \
       [ "${BASE_IMAGE_NAME}" == "quay.io/centos/centos" ]; then
        print_colored_v2 "ERROR" "dx-runtime does not support '${BASE_IMAGE_NAME}'. Only Ubuntu and Debian are supported for dx-runtime."
        exit 1
    fi

    local docker_compose_args="-f docker/docker-compose.yml"
    docker_build_impl "runtime" "${docker_compose_args}"
}

docker_build_dx-modelzoo()
{
    # dx-modelzoo supports ubuntu and debian only
    if [ "${BASE_IMAGE_NAME}" == "fedora" ] || \
       [ "${BASE_IMAGE_NAME}" == "redhat/ubi9" ] || [ "${BASE_IMAGE_NAME}" == "redhat/ubi10" ] || \
       [ "${BASE_IMAGE_NAME}" == "quay.io/centos/centos" ]; then
        print_colored_v2 "ERROR" "dx-modelzoo does not support '${BASE_IMAGE_NAME}'. Only Ubuntu and Debian are supported for dx-modelzoo."
        exit 1
    fi

    local docker_compose_args="-f docker/docker-compose.yml"
    docker_build_impl "modelzoo" "${docker_compose_args}"
}

install_dx_rt_npu_linux_driver() 
{
    CMD="./dx-runtime/install.sh --target=dx_rt_npu_linux_driver"
    echo "${CMD}"

    ${CMD}
}

check_docker_compose_command() {
    check_docker_compose || {
        local message="Docker compose command not found."
        local hint_message="Please install docker compose first. Visit https://docs.docker.com/compose/install"
        local origin_cmd=""
        local suggested_action_cmd="${DX_AS_PATH}/scripts/install_docker.sh"
        local suggested_action_message="Do you want to install docker compose now?"
        local message_type="WARNING"

        handle_cmd_interactive "$message" "$hint_message" "$origin_cmd" "$suggested_action_cmd" "$suggested_action_message" "$message_type" || {
            show_help "error" "(Hint) User declined to install docker compose. Please install docker compose first. Visit https://docs.docker.com/compose/install"
        }
    }
}

main() {
    # check docker compose command
    check_docker_compose_command

    # Validate OS version options - only one can be specified
    local OS_OPTIONS_COUNT=0
    [ -n "$UBUNTU_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$DEBIAN_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$FEDORA_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$RHEL_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$CENTOS_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))

    if [ "$OS_OPTIONS_COUNT" -gt 1 ]; then
        show_help "error" "Cannot specify multiple OS version options. Please choose one of: --ubuntu_version, --debian_version, --fedora_version, --rhel_version, --centos_version."
    fi

    if [ "$OS_OPTIONS_COUNT" -eq 0 ]; then
        show_help "error" "An OS version option must be specified (--ubuntu_version, --debian_version, --fedora_version, --rhel_version, or --centos_version)."
    fi

    # Set BASE_IMAGE_NAME and OS_VERSION based on input
    if [ -n "$UBUNTU_VERSION" ]; then
        BASE_IMAGE_NAME="ubuntu"
        OS_VERSION="$UBUNTU_VERSION"
    elif [ -n "$DEBIAN_VERSION" ]; then
        BASE_IMAGE_NAME="debian"
        OS_VERSION="$DEBIAN_VERSION"
    elif [ -n "$FEDORA_VERSION" ]; then
        BASE_IMAGE_NAME="fedora"
        OS_VERSION="$FEDORA_VERSION"
    elif [ -n "$RHEL_VERSION" ]; then
        case "$RHEL_VERSION" in
            9)  BASE_IMAGE_NAME="redhat/ubi9"; OS_VERSION="9"; TAG_NAME="latest" ;;
            10) BASE_IMAGE_NAME="redhat/ubi10"; OS_VERSION="10"; TAG_NAME="latest" ;;
            *)  show_help "error" "Unsupported RHEL version: $RHEL_VERSION. Supported: 9, 10" ;;
        esac
        IMAGE_TAG_SUFFIX="redhat-ubi${RHEL_VERSION}"
    elif [ -n "$CENTOS_VERSION" ]; then
        BASE_IMAGE_NAME="quay.io/centos/centos"
        OS_VERSION="$CENTOS_VERSION"
        IMAGE_TAG_SUFFIX="centos-${CENTOS_VERSION}"
    fi

    print_colored_v2 "INFO" "BASE_IMAGE_NAME($BASE_IMAGE_NAME) is set."
    print_colored_v2 "INFO" "OS_VERSION($OS_VERSION) is set."
    print_colored_v2 "INFO" "TARGET_ENV($TARGET_ENV) is set."
    print_colored_v2 "INFO" "FILE_DXCOM($FILE_DXCOM) is set."
    print_colored_v2 "INFO" "FILE_DXTRON($FILE_DXTRON) is set."
    print_colored_v2 "INFO" "HOST_UID($HOST_UID) is set."
    print_colored_v2 "INFO" "HOST_GID($HOST_GID) is set."
    print_colored_v2 "INFO" "TARGET_USER($TARGET_USER) is set."
    print_colored_v2 "INFO" "TARGET_HOME($TARGET_HOME) is set."
    if [ "$DRIVER_UPDATE" = "y" ]; then
        print_colored_v2 "INFO" "DRIVER_UPDATE($DRIVER_UPDATE) is set."
    fi
    if [ "$NO_CACHE" = "y" ]; then
        print_colored_v2 "INFO" "NO_CACHE($NO_CACHE) is set."
    fi

    case $TARGET_ENV in
        dx-compiler)
            if [ "$SKIP_ARCHIVE" = "y" ]; then
                print_colored_v2 "INFO" "SKIP_ARCHIVE($SKIP_ARCHIVE) is set. so, skip archiving $TARGET_ENV."
            else
                archive_dx-compiler || { exit 1; }
            fi
            docker_build_dx-compiler
            ;;
        dx-runtime)
            if [ "$SKIP_ARCHIVE" = "y" ]; then
                print_colored_v2 "INFO" "SKIP_ARCHIVE($SKIP_ARCHIVE) is set. so, skip archiving $TARGET_ENV."
            else
                echo "Archiving dx-runtime"
                ${DX_AS_PATH}/scripts/archive_git_repos.sh --target=dx-runtime || { print_colored_v2 "ERROR" "Archiving dx-runtime failed.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"; exit 1; }
            fi
            docker_build_dx-runtime
            if [ "$DRIVER_UPDATE" = "y" ]; then
                install_dx_rt_npu_linux_driver
            fi
            ;;
        dx-modelzoo)
            if [ "$SKIP_ARCHIVE" = "y" ]; then
                print_colored_v2 "INFO" "SKIP_ARCHIVE($SKIP_ARCHIVE) is set. so, skip archiving $TARGET_ENV."
            else
                echo "Archiving dx-modelzoo"
                ${DX_AS_PATH}/scripts/archive_git_repos.sh --target=dx-modelzoo || { print_colored_v2 "ERROR" "Archiving dx-modelzoo failed.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"; exit 1; }
            fi
            docker_build_dx-modelzoo
            ;;
        all)
            if [ "$SKIP_ARCHIVE" = "y" ]; then
                print_colored_v2 "INFO" "SKIP_ARCHIVE($SKIP_ARCHIVE) is set. so, skip archiving $TARGET_ENV."
            else
                echo "Archiving all DXNN® environments"
                archive_dx-compiler || { exit 1; }

                ${DX_AS_PATH}/scripts/archive_git_repos.sh --all || {
                    print_colored_v2 "ERROR" "Archiving dx-runtime or dx-modelzoo failed."
                    echo -e "${TAG_HINT} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"
                    exit 1
                }
            fi

            docker_build_all
            if [ "$DRIVER_UPDATE" = "y" ]; then
                install_dx_rt_npu_linux_driver
            fi
            ;;
        *)
            show_help "error" "(Hint) Please specify either the '--all' option or the '--target=<dx-compiler | dx-runtime | dx-modelzoo>' option."
            ;;
    esac

    # remove archives
    # if [[ -d "$OUTPUT_DIR" ]]; then
    #     echo "Removing archive directory: $OUTPUT_DIR"
    #     rm -rf "$OUTPUT_DIR"
    # fi
}

# parse args
while [ $# -gt 0 ]; do
    case "$1" in
        --all)
            TARGET_ENV=all
            ;;
        --target=*)
            TARGET_ENV="${1#*=}"
            ;;
        --ubuntu_version=*)
            UBUNTU_VERSION="${1#*=}"
            ;;
        --debian_version=*)
            DEBIAN_VERSION="${1#*=}"
            ;;
        --fedora_version=*)
            FEDORA_VERSION="${1#*=}"
            ;;
        --rhel_version=*)
            RHEL_VERSION="${1#*=}"
            ;;
        --centos_version=*)
            CENTOS_VERSION="${1#*=}"
            ;;
        --driver_update)
            DRIVER_UPDATE=y
            ;;
        --no-cache)
            NO_CACHE=y
            ;;
        --skip-archive)
            SKIP_ARCHIVE=y
            ;;
        --nvidia_gpu)
            NVIDIA_GPU_MODE=1
            ;;
        --help)
            show_help
            exit 0
            ;;
        --internal)
            INTERNAL_MODE=1
            ;;
        --re-archive)
            RE_ARCHIVE_ARGS="--re-archive"
            ;;
        --re-archive=*)
            FORCE_VALUE="${1#*=}"
            if [ "$FORCE_VALUE" = "false" ]; then
                RE_ARCHIVE_ARGS="--re-archive=false"
            else
                RE_ARCHIVE_ARGS="--re-archive"
            fi
            ;;
        --pypi=*)
            # Select dx-com/dx-tron source: true=public PyPI (default), false=DEEPX
            # release index (e.g. for staging versions not yet published to PyPI).
            PYPI_ARGS="--pypi=${1#*=}"
            ;;
        *)
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

main

popd >&2

exit 0
