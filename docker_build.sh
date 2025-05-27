#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}")
COMPILER_PATH="${DX_AS_PATH}/dx-compiler"

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

pushd "$SCRIPT_DIR"

OUTPUT_DIR="$SCRIPT_DIR/archives"
UBUNTU_VERSION=""

INTERNAL_MODE=0
FORCE_ARGS=""

# Properties file path
VERSION_FILE="$COMPILER_PATH/compiler.properties"

# read 'COM_VERSION', 'SIM_VERSION' from properties file
if [[ -f "$VERSION_FILE" ]]; then
    # load varialbles
    source "$VERSION_FILE"
else
    echo -e "${TAG_ERROR} Version file '$VERSION_FILE' not found.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"
    exit 1
fi

if [ -n "${COM_VERSION}" ] && [ -n "${SIM_VERSION}" ]; then
    echo -e "${TAG_INFO} dx_com version(${COM_VERSION}) is set."
    echo -e "${TAG_INFO} dx_simulator version(${SIM_VERSION}) is set."
else
    echo -e "${TAG_ERROR} 'dx_com' or 'dx_sim' version is not specified in ${VERSION_FILE}."
    exit 1
fi

FILE_DXCOM="archives/dx_com_M1A_v${COM_VERSION}.tar.gz"
FILE_DXSIM="archives/dx_simulator_v${SIM_VERSION}.tar.gz"

# Function to display help message
show_help() {
    echo "Usage: $(basename "$0") OPTIONS(--all | target=<environment_name>) --ubuntu_version=<version> [--help]"
    echo "Example:1) $0 --all --ubuntu_version=24.04"
    echo "Example 2) $0 --target=dx-compiler --ubuntu_version=24.04"
    echo "Example 3) $0 --target=dx-runtime --ubuntu_version=24.04 --driver_update"
    echo "Example 3) $0 --target=dx-modelzoo --ubuntu_version=24.04 --driver_update"
    echo "Options:"
    echo "  --all                          : Install DXNN® Software Stack (dx-compiler & dx-runtime & dx-modelzoo)"
    echo "  --target=<environment_name>    : Install specify target DXNN® environment (ex> dx-compiler | dx-runtime | dx-modelzoo)"
    echo "  --ubuntu_version=<version>     : Specify Ubuntu version (ex> 24.04)"
    echo "  [--driver_update]              : Install 'dx_rt_npu_linux_driver' in the host environment"
    echo "  [--no-cache]                   : Build Docker images freshly without cache"
    echo "  [--help]                       : Show this help message"

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

docker_build_impl()
{
    local target=$1
    local config_file_args=${2:--f docker/docker-compose.yml}
    local no_cache_arg=""

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
    export FILE_DXSIM=${FILE_DXSIM}
    if [ ! -n "${XAUTHORITY}" ]; then
        echo -e "${TAG_INFO} XAUTHORITY env is not set. so, try to set automatically."
        DUMMY_XAUTHORITY="/tmp/dummy"
        touch ${DUMMY_XAUTHORITY}
        export XAUTHORITY=${DUMMY_XAUTHORITY}
        export XAUTHORITY_TARGET=${DUMMY_XAUTHORITY}
        
    else
        echo -e "${TAG_INFO} XAUTHORITY(${XAUTHORITY}) is set"
        export XAUTHORITY_TARGET="/tmp/.docker.xauth"
    fi

    CMD="docker compose ${config_file_args} build ${no_cache_arg} dx-${target}"
    echo "${CMD}"

    ${CMD} || { echo -e "${TAG_ERROR} docker build '${target} failed. "; exit 1; }
}

docker_build_all() 
{
    docker_build_dx-compiler
    docker_build_dx-runtime
    docker_build_dx-modelzoo
}

docker_build_dx-compiler() 
{
    docker_build_impl "compiler"
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

main() {
    # usage
    if [ -z "$UBUNTU_VERSION" ]; then
        show_help "error" "--ubuntu_version ($UBUNTU_VERSION) does not exist."
    else
        echo -e "${TAG_INFO} UBUNTU_VERSSION($UBUNTU_VERSION) is set."
        echo -e "${TAG_INFO} TARGET_ENV($TARGET_ENV) is set."
        echo -e "${TAG_INFO} FILE_DXCOM($FILE_DXCOM) is set."
        echo -e "${TAG_INFO} FILE_DXSIM($FILE_DXSIM) is set."
        if [ "$DRIVER_UPDATE" = "y" ]; then
            echo -e "${TAG_INFO} DRIVER_UPDATE($DRIVER_UPDATE) is set."
        fi
        if [ "$NO_CACHE" = "y" ]; then
            echo -e "${TAG_INFO} NO_CACHE($NO_CACHE) is set."
        fi
    fi

    case $TARGET_ENV in
        dx-compiler)
            echo "Archiving dx-compiler"
            ./archive_dx-compiler.sh $FORCE_ARGS || { echo -e "${TAG_ERROR} Archiving dx-compiler failed."; exit 1; }
            docker_build_dx-compiler
            ;;
        dx-runtime)
            echo "Archiving dx-runtime"
            ./archive_git_repos.sh --target=dx-runtime || { echo -e "${TAG_ERROR} Archiving dx-runtime failed.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"; exit 1; }
            docker_build_dx-runtime
            if [ "$DRIVER_UPDATE" = "y" ]; then
                install_dx_rt_npu_linux_driver
            fi
            ;;
        dx-modelzoo)
            echo "Archiving dx-modelzoo"
            ./archive_git_repos.sh --target=dx-modelzoo || { echo -e "${TAG_ERROR} Archiving dx-modelzoo failed.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"; exit 1; }
            docker_build_dx-modelzoo
            ;;
        all)
            echo "Archiving all DXNN® environments"
            ./archive_dx-compiler.sh || { echo -e "${TAG_ERROR} Archiving dx-compiler failed."; exit 1; }
            ./archive_git_repos.sh --all || { echo -e "${TAG_ERROR} Archiving dx-runtime or dx-modelzoo failed.\n${TAG_INFO} ${COLOR_BRIGHT_YELLOW_ON_BLACK}Please try running 'git submodule update --init --recursive --force' and then try again.${COLOR_RESET}"; exit 1; }
            docker_build_all
            if [ "$DRIVER_UPDATE" = "y" ]; then
                install_dx_rt_npu_linux_driver
            fi
            ;;
        *)
            echo -e "${TAG_ERROR} Unknown '--target' option '$TARGET_ENV'"
            show_help "error" "${TAG_INFO} (Hint) Please specify either the '--all' option or the '--target=<dx-compiler | dx-runtime>' option."
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
            echo -e "${TAG_ERROR}: Invalid option '$1'"
            show_help
            exit 1
            ;;
    esac
    shift
done

main

popd

exit 0
