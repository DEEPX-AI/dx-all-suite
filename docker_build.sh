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

NVIDIA_GPU_MODE=0
INTERNAL_MODE=0
FORCE_ARGS=""

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
FILE_DXTRON="archives/DXTron-${TRON_VERSION}.AppImage"
HOST_UID=$(id -u)
HOST_GID=$(id -g)
TARGET_USER=deepx
TARGET_HOME=/deepx

# Function to display help message
show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") OPTIONS(--all | target=<environment_name>)${COLOR_RESET} --ubuntu_version=<version>${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Required:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}--all${COLOR_RESET}                          Install DXNN® Software Stack (dx-compiler & dx-runtime & dx-modelzoo)"
    echo -e "  ${COLOR_BOLD}or${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}--target=<environment_name>${COLOR_RESET}    Install specify target DXNN® environment (ex> dx-compiler | dx-runtime | dx-modelzoo)"
    echo -e "  ${COLOR_GREEN}--ubuntu_version=<version>${COLOR_RESET}     Specify Ubuntu version (ex> 24.04)"
    echo -e ""
    echo -e "${COLOR_BOLD}Optional:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}[--driver_update]${COLOR_RESET}              Install 'dx_rt_npu_linux_driver' in the host environment"
    echo -e "  ${COLOR_GREEN}[--no-cache]${COLOR_RESET}                   Build Docker images freshly without cache"
    echo -e "  ${COLOR_GREEN}[--skip-archive]${COLOR_RESET}               Skip archiving dx-compiler or dx-runtime or dx-modelzoo before building"
    echo -e "  ${COLOR_GREEN}[--help]${COLOR_RESET}                       Show this help message"
    echo -e ""
    echo -e "${COLOR_BOLD}Examples:${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-runtime --ubuntu_version=24.04 --driver_update${COLOR_RESET}"
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

    # Build Docker image
    export COMPOSE_BAKE=true
    export UBUNTU_VERSION=${UBUNTU_VERSION}
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

docker_build_dx-compiler() 
{
    local docker_compose_args="-f docker/docker-compose.yml"
    docker_build_impl "compiler" "${docker_compose_args}"
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

    # usage
    if [ -z "$UBUNTU_VERSION" ]; then
        show_help "error" "--ubuntu_version option does not exist."
    else
        print_colored_v2 "INFO" "UBUNTU_VERSSION($UBUNTU_VERSION) is set."
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
    fi

    case $TARGET_ENV in
        dx-compiler)
            if [ "$SKIP_ARCHIVE" = "y" ]; then
                print_colored_v2 "INFO" "SKIP_ARCHIVE($SKIP_ARCHIVE) is set. so, skip archiving $TARGET_ENV."
            else
                echo "Archiving dx-compiler"
                ${DX_AS_PATH}/scripts/archive_dx-compiler.sh $FORCE_ARGS || { print_colored_v2 "ERROR" "Archiving dx-compiler failed."; exit 1; }
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
                ${DX_AS_PATH}/scripts/archive_dx-compiler.sh || { print_colored_v2 "ERROR" "Archiving dx-compiler failed."; exit 1; }
                ${DX_AS_PATH}/scripts/archive_git_repos.sh --all || { print_colored_v2 "ERROR" "Archiving dx-runtime or dx-modelzoo failed.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"; exit 1; }
            fi
            docker_build_all
            if [ "$DRIVER_UPDATE" = "y" ]; then
                install_dx_rt_npu_linux_driver
            fi
            ;;
        *)
            show_help "error" "(Hint) Please specify either the '--all' option or the '--target=<dx-compiler | dx-runtime>' option."
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
        --force)
            FORCE_ARGS="--force"
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
