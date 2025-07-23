#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

pushd "$DX_AS_PATH"

OUTPUT_DIR="$DX_AS_PATH/archives"
UBUNTU_VERSION=""

DEV_MODE=0
INTEL_GPU_HW_ACC=0

# Function to display help message
show_help() {
    echo "Usage: $(basename "$0") OPTIONS(--all | target=<environment_name>) --ubuntu_version=<version> [--help]"
    echo "Example:1) $0 --all --ubuntu_version=24.04"
    echo "Example 2) $0 --target=dx-compiler --ubuntu_version=24.04"
    echo "Example 3) $0 --target=dx-runtime --ubuntu_version=24.04"
    echo "Example 3) $0 --target=dx-modelzoo --ubuntu_version=24.04"
    echo "Options:"
    echo "  --all                          : Install DXNN® Software Stack (dx-compiler & dx-runtime & dx-modelzoo)"
    echo "  --target=<environment_name>    : Install specify target DXNN® environment (ex> dx-compiler | dx-runtime | dx-modelzoo)"
    echo "  --ubuntu_version=<version>     : Specify Ubuntu version (ex> 24.04)"
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

docker_down_impl()
{
    local target=$1
    local config_file_args=${2:--f docker/docker-compose.yml}

    if [ ${DEV_MODE} -eq 1 ]; then
        config_file_args="${config_file_args} -f docker/docker-compose.dev.yml"
    fi

    # Run Docker Container
    export COMPOSE_BAKE=true
    export UBUNTU_VERSION=${UBUNTU_VERSION}
    DUMMY_XAUTHORITY=""
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

    CMD="docker compose ${config_file_args} down dx-${target}"
    echo "${CMD}"

    ${CMD}
}

docker_down_all() 
{
    docker_down_dx-compiler
    docker_down_dx-runtime
    docker_down_dx-modelzoo
}

docker_down_dx-compiler() 
{
    docker_down_impl "compiler"
}

docker_down_dx-runtime()
{
    local docker_compose_args="-f docker/docker-compose.yml"

    if [ ${INTEL_GPU_HW_ACC} -eq 1 ]; then
        docker_compose_args="${docker_compose_args} -f docker/docker-compose.intel_gpu_hw_acc.yml"
    fi

    docker_down_impl "runtime" "${docker_compose_args}"
}

docker_down_dx-modelzoo()
{
    local docker_compose_args="-f docker/docker-compose.yml"
    docker_down_impl "modelzoo" "${docker_compose_args}"
}

main() {
    # usage
    if [ -z "$UBUNTU_VERSION" ]; then
        show_help "error" "--ubuntu_version ($UBUNTU_VERSION) does not exist."
    else
        echo -e "${TAG_INFO} UBUNTU_VERSSION($UBUNTU_VERSION) is set."
        echo -e "${TAG_INFO} TARGET_ENV($TARGET_ENV) is set."
    fi

    case $TARGET_ENV in
        dx-compiler)
            echo "Stopping and removing dx-compiler"
            docker_down_dx-compiler
            ;;
        dx-runtime)
            echo "Stopping and removing dx-runtime"
            docker_down_dx-runtime
            ;;
        dx-modelzoo)
            echo "Stopping and removing dx-modelzoo"
            docker_down_dx-modelzoo
            ;;
        all)
            echo "Stopping and removing all DXNN® environments"
            docker_down_all
            ;;
        *)
            echo -e "${TAG_ERROR} Unknown '--target' option '$TARGET_ENV'"
            show_help "error" "${TAG_INFO} (Hint) Please specify either the '--all' option or the '--target=<dx-compiler | dx-runtime>' option."
            ;;
    esac
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
        --help)
            show_help
            exit 0
            ;;
        --dev)
            DEV_MODE=1
            ;;
        --intel_gpu_hw_acc)
            INTEL_GPU_HW_ACC=1
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
