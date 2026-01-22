#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/../../")
DX_AS_TESTS_PATH="${DX_AS_PATH}/tests"

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh
source ${DX_AS_PATH}/scripts/common_util.sh

pushd "$DX_AS_TESTS_PATH" >&2

UBUNTU_VERSION=""
DEBIAN_VERSION=""

NVIDIA_GPU_MODE=0
INTERNAL_MODE=0

HOST_UID=$(id -u)
HOST_GID=$(id -g)
TARGET_USER=deepx
TARGET_HOME=/deepx

# Function to display help message
show_help() {
    echo "Usage: $(basename "$0") --ubuntu_version=<version> [--help | --no-cache | --driver_update | --rt_update]"
    echo "Example 1) $0 --ubuntu_version=24.04"
    echo "Example 2) $0 --ubuntu_version=24.04 --driver_update"
    echo "Example 3) $0 --ubuntu_version=24.04 --no-cache"
    echo "Example 4) $0 --ubuntu_version=24.04 --rt_update"
    echo "Options:"
    echo "  --ubuntu_version=<version>     : Specify Ubuntu version (ex> 24.04)"
    echo "  --debian_version=<version>     : Specify Debian version (ex> 12)"
    echo "  [--driver_update]              : Install 'dx_rt_npu_linux_driver' in the host environment"
    echo "  [--rt_update]                  : Install 'dx_rt' in the host environment"
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
    local config_file_args=${1:--f docker/docker-compose.yml}
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
    export HOST_UID=${HOST_UID}
    export HOST_GID=${HOST_GID}
    export TARGET_USER=${TARGET_USER}
    export TARGET_HOME=${TARGET_HOME}
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

    CMD="docker compose ${config_file_args} build ${no_cache_arg} dx-local-install-test"
    echo "${CMD}"

    ${CMD} || { echo -e "${TAG_ERROR} docker build 'dx-local-install-test' failed. "; exit 1; }
}

docker_build() 
{
    local docker_compose_args="-f docker/docker-compose.local.install.test.yml"
    docker_build_impl "${docker_compose_args}"
}

install_dx_rt_npu_linux_driver() 
{
    CMD="./dx-runtime/install.sh --target=dx_rt_npu_linux_driver"
    echo "${CMD}"

    ${CMD}
}

install_dx_rt()
{
    CMD="./dx-runtime/install.sh --target=dx_rt"
    echo "${CMD}"

    ${CMD}
}

main() {
    # usage
    if [ -z "$UBUNTU_VERSION" ]; then
        show_help "error" "--ubuntu_version ($UBUNTU_VERSION) does not exist."
    else
        echo -e "${TAG_INFO} UBUNTU_VERSSION($UBUNTU_VERSION) is set."
        echo -e "${TAG_INFO} HOST_UID($HOST_UID) is set."
        echo -e "${TAG_INFO} HOST_GID($HOST_GID) is set."
        echo -e "${TAG_INFO} TARGET_USER($TARGET_USER) is set."
        echo -e "${TAG_INFO} TARGET_HOME($TARGET_HOME) is set."
        if [ "$DRIVER_UPDATE" = "y" ]; then
            echo -e "${TAG_INFO} DRIVER_UPDATE($DRIVER_UPDATE) is set."
        fi
        if [ "$NO_CACHE" = "y" ]; then
            echo -e "${TAG_INFO} NO_CACHE($NO_CACHE) is set."
        fi
    fi

    docker_build
    if [ "$DRIVER_UPDATE" = "y" ]; then
        install_dx_rt_npu_linux_driver
    fi
    if [ "$RT_UPDATE" = "y" ]; then
        install_dx_rt
    fi
}

# parse args
for i in "$@"; do
    case "$1" in
        --ubuntu_version=*)
            UBUNTU_VERSION="${1#*=}"
            ;;
        --debian_version=*)
            DEBIAN_VERSION="${1#*=}"
            ;;
        --driver_update)
            DRIVER_UPDATE=y
            ;;
        --rt_update)
            RT_UPDATE=y
            ;;
        --no-cache)
            NO_CACHE=y
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
        *)
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

main

popd >&2

exit 0
