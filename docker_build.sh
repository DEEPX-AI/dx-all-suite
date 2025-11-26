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
BASE_IMAGE_NAME=""
OS_VERSION=""

NVIDIA_GPU_MODE=0
INTERNAL_MODE=0
RE_ARCHIVE_ARGS=""

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

# Initialize file paths (will be set dynamically during archive)
FILE_DXCOM=""
FILE_DXTRON=""
HOST_UID=$(id -u)
HOST_GID=$(id -g)
TARGET_USER=deepx
TARGET_HOME=/deepx

# Function to display help message
show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--all${COLOR_RESET} ${COLOR_YELLOW}--ubuntu_version=<version>${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--target=<dx-compiler>${COLOR_RESET} ${COLOR_YELLOW}--ubuntu_version=<version>${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--target=<dx-runtime | dx-modelzoo>${COLOR_RESET} ${COLOR_YELLOW}(--ubuntu_version=<version> | --debian_version=<version>)${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Required (choose one target option):${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}--all${COLOR_RESET}                          Run all DXNN® containers (dx-compiler & dx-runtime & dx-modelzoo)"
    echo -e "  ${COLOR_GREEN}--target=<environment_name>${COLOR_RESET}    Run specific DXNN® container"
    echo -e "                                   Available: ${COLOR_CYAN}dx-compiler${COLOR_RESET} | ${COLOR_CYAN}dx-runtime${COLOR_RESET} | ${COLOR_CYAN}dx-modelzoo${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Required (choose one OS option):${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}--ubuntu_version=<version>${COLOR_RESET}     Specify Ubuntu version (ex: 24.04, 22.04, 20.04)"
    echo -e "  ${COLOR_YELLOW}--debian_version=<version>${COLOR_RESET}     Specify Debian version (ex: 12)"
    echo -e "                                   Note: ${COLOR_CYAN}dx-compiler${COLOR_RESET} only supports Ubuntu ${COLOR_RED}(Debian is not supported)${COLOR_RESET}"
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
        export DOCKER_BUILDKIT=0
    fi

    if [ "$NO_CACHE" = "y" ]; then
        no_cache_arg="--no-cache"
    fi

    # Build Docker image
    export COMPOSE_BAKE=true
    export BASE_IMAGE_NAME=${BASE_IMAGE_NAME}
    export OS_VERSION=${OS_VERSION}
    export FILE_DXCOM=${FILE_DXCOM}
    export FILE_DXTRON=${FILE_DXTRON}
    export HOST_UID=${HOST_UID}
    export HOST_GID=${HOST_GID}
    export TARGET_USER=${TARGET_USER}
    export TARGET_HOME=${TARGET_HOME}
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
    print_colored_v2 "INFO" "Archiving dx-compiler"
    # this function is defined in scripts/common_util.sh
    # Usage: os_check "supported_os_names" "ubuntu_versions" "debian_versions"
    os_check "ubuntu" "20.04 22.04 24.04" "" || {
        print_colored_v2 "SKIP" "Current OS is not supported. Skip and continue to next target."
        return 0
    }

    # this function is defined in scripts/common_util.sh
    # Usage: arch_check "supported_arch_names"
    arch_check "amd64 x86_64" || {
        print_colored_v2 "SKIP" "Current architecture is not supported. Skip and continue to next target."
        return 0
    }

    # Run archive script and capture output
    ARCHIVE_OUTPUT=$(${DX_AS_PATH}/scripts/archive_dx-compiler.sh ${RE_ARCHIVE_ARGS} 2>&1)
    if [ $? -ne 0 ]; then
        print_colored_v2 "ERROR" "Archiving dx-compiler failed."
        return 1
    fi
    
    # Extract archived file paths from the archive script's output
    ARCHIVED_COM=$(echo "$ARCHIVE_OUTPUT" | grep "ARCHIVED_COM_FILE=" | cut -d'=' -f2)
    ARCHIVED_TRON=$(echo "$ARCHIVE_OUTPUT" | grep "ARCHIVED_TRON_FILE=" | cut -d'=' -f2)
    
    # Set FILE_DXCOM and FILE_DXTRON if archived files were created
    # Convert absolute paths to relative paths for Docker build context
    if [ -n "$ARCHIVED_COM" ] && [ -f "$ARCHIVED_COM" ]; then
        # Convert to relative path from DX_AS_PATH
        FILE_DXCOM="${ARCHIVED_COM#${DX_AS_PATH}/}"
        print_colored_v2 "INFO" "Using archived dx_com file: $FILE_DXCOM"
    else
        # Fallback to default pattern if archive output not captured
        FILE_DXCOM="archives/dx_com_M1_v${COM_VERSION}.tar.gz"
        print_colored_v2 "WARNING" "Could not detect archived dx_com file, using default: $FILE_DXCOM"
    fi
    
    if [ -n "$ARCHIVED_TRON" ] && [ -f "$ARCHIVED_TRON" ]; then
        # Convert to relative path from DX_AS_PATH
        FILE_DXTRON="${ARCHIVED_TRON#${DX_AS_PATH}/}"
        print_colored_v2 "INFO" "Using archived dx_tron file: $FILE_DXTRON"
    else
        # Fallback to default pattern if archive output not captured
        FILE_DXTRON="archives/DXTron-${TRON_VERSION}.AppImage"
        print_colored_v2 "WARNING" "Could not detect archived dx_tron file, using default: $FILE_DXTRON"
    fi

    print_colored_v2 "SUCCESS" "Archiving dx-compiler is done."
    return 0
}

docker_build_dx-compiler() 
{
    # dx-compiler only supports ubuntu
    if [ "${BASE_IMAGE_NAME}" != "ubuntu" ]; then
        print_colored_v2 "ERROR" "dx-compiler only supports Ubuntu. Please use --ubuntu_version option."
        exit 1
    fi

    # this function is defined in scripts/common_util.sh
    # Usage: os_check "supported_os_names" "ubuntu_versions" "debian_versions"
    os_check "ubuntu" "20.04 22.04 24.04" "" || {
        print_colored_v2 "SKIP" "Current OS is not supported. Skip and continue to next target."
        return 0
    }

    # this function is defined in scripts/common_util.sh
    # Usage: arch_check "supported_arch_names"
    arch_check "amd64 x86_64" || {
        print_colored_v2 "SKIP" "Current architecture is not supported. Skip and continue to next target."
        return 0
    }

    local docker_compose_args="-f docker/docker-compose.yml"
    docker_build_impl "compiler" "${docker_compose_args}"
    return 0
}

docker_build_dx-runtime()
{
    local docker_compose_args="-f docker/docker-compose.yml"
    docker_build_impl "runtime" "${docker_compose_args}"
}

docker_build_dx-modelzoo()
{
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

    # Validate OS version options
    if [ -n "$UBUNTU_VERSION" ] && [ -n "$DEBIAN_VERSION" ]; then
        show_help "error" "Cannot specify both --ubuntu_version and --debian_version. Please choose one."
    fi

    if [ -z "$UBUNTU_VERSION" ] && [ -z "$DEBIAN_VERSION" ]; then
        show_help "error" "Either --ubuntu_version or --debian_version option must be specified."
    fi

    # Set BASE_IMAGE_NAME and OS_VERSION based on input
    if [ -n "$UBUNTU_VERSION" ]; then
        BASE_IMAGE_NAME="ubuntu"
        OS_VERSION="$UBUNTU_VERSION"
    elif [ -n "$DEBIAN_VERSION" ]; then
        BASE_IMAGE_NAME="debian"
        OS_VERSION="$DEBIAN_VERSION"
    fi

    print_colored_v2 "INFO" "BASE_IMAGE_NAME($BASE_IMAGE_NAME) is set."
    print_colored_v2 "INFO" "OS_VERSION($OS_VERSION) is set."
    print_colored_v2 "INFO" "TARGET_ENV($TARGET_ENV) is set."
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
                # Set default file paths if not set by archive
                if [ -z "$FILE_DXCOM" ]; then
                    FILE_DXCOM="archives/dx_com_M1_v${COM_VERSION}.tar.gz"
                fi
                if [ -z "$FILE_DXTRON" ]; then
                    FILE_DXTRON="archives/DXTron-${TRON_VERSION}.AppImage"
                fi
            else
                archive_dx-compiler || { exit 1; }
            fi
            print_colored_v2 "INFO" "FILE_DXCOM($FILE_DXCOM) is set."
            print_colored_v2 "INFO" "FILE_DXTRON($FILE_DXTRON) is set."
            docker_build_dx-compiler
            ;;
        dx-runtime)
            if [ "$SKIP_ARCHIVE" = "y" ]; then
                print_colored_v2 "INFO" "SKIP_ARCHIVE($SKIP_ARCHIVE) is set. so, skip archiving $TARGET_ENV."
            else
                echo "Archiving dx-runtime"
                ${DX_AS_PATH}/scripts/archive_git_repos.sh --target=dx-runtime || { print_colored_v2 "ERROR" "Archiving dx-runtime failed.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"; exit 1; }
            fi
            # Set default file paths if not set
            if [ -z "$FILE_DXCOM" ]; then
                FILE_DXCOM="archives/dx_com_M1_v${COM_VERSION}.tar.gz"
            fi
            if [ -z "$FILE_DXTRON" ]; then
                FILE_DXTRON="archives/DXTron-${TRON_VERSION}.AppImage"
            fi
            print_colored_v2 "INFO" "FILE_DXCOM($FILE_DXCOM) is set."
            print_colored_v2 "INFO" "FILE_DXTRON($FILE_DXTRON) is set."
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
            # Set default file paths if not set
            if [ -z "$FILE_DXCOM" ]; then
                FILE_DXCOM="archives/dx_com_M1_v${COM_VERSION}.tar.gz"
            fi
            if [ -z "$FILE_DXTRON" ]; then
                FILE_DXTRON="archives/DXTron-${TRON_VERSION}.AppImage"
            fi
            print_colored_v2 "INFO" "FILE_DXCOM($FILE_DXCOM) is set."
            print_colored_v2 "INFO" "FILE_DXTRON($FILE_DXTRON) is set."
            docker_build_dx-modelzoo
            ;;
        all)
            if [ "$SKIP_ARCHIVE" = "y" ]; then
                print_colored_v2 "INFO" "SKIP_ARCHIVE($SKIP_ARCHIVE) is set. so, skip archiving $TARGET_ENV."
                # Set default file paths if not set by archive
                if [ -z "$FILE_DXCOM" ]; then
                    FILE_DXCOM="archives/dx_com_M1_v${COM_VERSION}.tar.gz"
                fi
                if [ -z "$FILE_DXTRON" ]; then
                    FILE_DXTRON="archives/DXTron-${TRON_VERSION}.AppImage"
                fi
            else
                echo "Archiving all DXNN® environments"
                archive_dx-compiler || { exit 1; }

                ${DX_AS_PATH}/scripts/archive_git_repos.sh --all || {
                    print_colored_v2 "ERROR" "Archiving dx-runtime or dx-modelzoo failed."
                    echo -e "${TAG_HINT} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"
                    exit 1
                }
            fi
            
            print_colored_v2 "INFO" "FILE_DXCOM($FILE_DXCOM) is set."
            print_colored_v2 "INFO" "FILE_DXTRON($FILE_DXTRON) is set."
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
for i in "$@"; do
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
        *)
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

main

popd >&2

exit 0
