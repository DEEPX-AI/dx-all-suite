#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh
source ${DX_AS_PATH}/scripts/common_util.sh

pushd "$DX_AS_PATH" >&2

OUTPUT_DIR="$DX_AS_PATH/archives"
UBUNTU_VERSION=""
DEBIAN_VERSION=""
BASE_IMAGE_NAME=""
OS_VERSION=""

DEV_MODE=0
INTEL_GPU_MODE=0

get_compose_project_name() {
    local use_intel_suffix="${1:-0}"
    local suffix=""

    if [ "${use_intel_suffix}" -eq 1 ]; then
        suffix="-intel-gpu"
    fi

    local sanitized_os=$(echo "${BASE_IMAGE_NAME}-${OS_VERSION}" | sed 's/\./-/g')
    echo "dx-all-suite${suffix}-${sanitized_os}"
}

get_compose_project_from_container() {
    local container_name=$1
    local fallback=$2

    if [ -z "$container_name" ]; then
        echo "$fallback"
        return
    fi

    local project=$(docker inspect -f '{{index .Config.Labels "com.docker.compose.project"}}' "$container_name" 2>/dev/null | tr -d '\r')

    if [ -n "$project" ] && [ "$project" != "<no value>" ]; then
        echo "$project"
    else
        echo "$fallback"
    fi
}

# Function to display help message
show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--all${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--all${COLOR_RESET} ${COLOR_YELLOW}(--ubuntu_version=<version> | --debian_version=<version>)${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--target=<dx-compiler>${COLOR_RESET} ${COLOR_YELLOW}--ubuntu_version=<version>${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--target=<dx-runtime | dx-modelzoo>${COLOR_RESET} ${COLOR_YELLOW}(--ubuntu_version=<version> | --debian_version=<version>)${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Required (choose one target option):${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}--all${COLOR_RESET}                          Stop all DXNN® containers(dx-compiler & dx-runtime & dx-modelzoo) for All OS version"
    echo -e "  ${COLOR_GREEN}--all (--ubuntu_version=<version> | --debian_version=<version>)${COLOR_RESET}"
    echo -e "                                 Stop all DXNN® containers(dx-compiler & dx-runtime & dx-modelzoo) for specified OS version"
    echo -e "  ${COLOR_GREEN}--target=<environment_name>${COLOR_RESET}    Stop specific DXNN® container"
    echo -e "                                   Available: ${COLOR_CYAN}dx-compiler${COLOR_RESET} | ${COLOR_CYAN}dx-runtime${COLOR_RESET} | ${COLOR_CYAN}dx-modelzoo${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Required (choose one OS option):${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}--ubuntu_version=<version>${COLOR_RESET}     Specify Ubuntu version (ex: 24.04, 22.04, 20.04)"
    echo -e "  ${COLOR_YELLOW}--debian_version=<version>${COLOR_RESET}     Specify Debian version (ex: 12)"
    echo -e "                                   Note: ${COLOR_CYAN}dx-compiler${COLOR_RESET} only supports Ubuntu ${COLOR_RED}(Debian is not supported)${COLOR_RESET}"
    echo -e ""
    echo -e "${COLOR_BOLD}Optional:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}[--intel_gpu]${COLOR_RESET}                 Stop Intel GPU acceleration variant (dx-runtime)"
    echo -e "  ${COLOR_GREEN}[--help]${COLOR_RESET}                       Show this help message"
    echo -e ""
    echo -e "${COLOR_BOLD}Examples:${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-runtime --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-runtime --debian_version=12${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-modelzoo --ubuntu_version=24.04${COLOR_RESET}"
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

docker_down_impl()
{
    local target=$1
    local config_file_args=${2:--f docker/docker-compose.yml}
    local use_intel_suffix=${3:-$INTEL_GPU_MODE}
    local explicit_project_name=${4:-}

    if [ ${DEV_MODE} -eq 1 ]; then
        config_file_args="${config_file_args} -f docker/docker-compose.dev.yml"
    fi

    # Run Docker Container
    export COMPOSE_BAKE=true
    export BASE_IMAGE_NAME=${BASE_IMAGE_NAME}
    export OS_VERSION=${OS_VERSION}
    DUMMY_XAUTHORITY=""
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

    # Dynamically set the project name based on the Ubuntu or Debian version
    if [ -n "${explicit_project_name}" ]; then
        export COMPOSE_PROJECT_NAME="${explicit_project_name}"
    else
        export COMPOSE_PROJECT_NAME="$(get_compose_project_name ${use_intel_suffix})"
    fi
    CMD="docker compose ${config_file_args} -p ${COMPOSE_PROJECT_NAME} down dx-${target}"
    echo "${CMD}"

    ${CMD} || { print_colored_v2 "ERROR" "docker down 'dx-${target}' failed. "; exit 1; }
}

run_compose_down_command()
{
    local cmd="$1"
    local success_msg="$2"
    local failure_msg="$3"

    echo "  ${cmd}"

    ${cmd} 2>&1 | while IFS= read -r line; do
        echo "  $line"
    done

    if [ ${PIPESTATUS[0]} -eq 0 ]; then
        print_colored_v2 "SUCCESS" "${success_msg}"
    else
        print_colored_v2 "WARNING" "${failure_msg}"
    fi
}

docker_down_all_without_os_versions()
{
    # Stop all containers regardless of OS version
    print_colored_v2 "INFO" "Stopping all DXNN® containers (all OS versions)"
    
    # Get all running dx-compiler, dx-runtime (default/intel), dx-modelzoo containers
    local containers=$(docker ps -a --format "{{.Names}}" 2>/dev/null | grep -E "^(dx-compiler|dx-runtime|dx-runtime_intel-hw-acc|dx-modelzoo)-")
    
    if [ -z "$containers" ]; then
        print_colored_v2 "INFO" "No DXNN® containers found."
        return 0
    fi
    
    echo "Found containers:"
    echo "$containers"
    
    # Extract unique OS combinations from container names
    # Container name format: dx-{service}-{os_name}-{os_version}
    local unique_os_combinations=$(printf '%s\n' "$containers" | sed -E 's/^dx-(compiler|runtime|runtime_intel-hw-acc|modelzoo)-//' | sort -u)
    
    echo ""
    echo "Detected OS combinations:"
    echo "$unique_os_combinations"
    echo ""
    
    # Process each unique OS combination
    for os_combo in $unique_os_combinations; do
        # Parse OS name and version from the combination
        # Format: ubuntu-20.04 or debian-12
        local os_name=$(echo "$os_combo" | cut -d'-' -f1)
        local os_version=$(echo "$os_combo" | cut -d'-' -f2-)

        print_colored_v2 "INFO" "Processing ${os_name}-${os_version} containers..."

        # Set environment variables for docker-compose
        export BASE_IMAGE_NAME="$os_name"
        export OS_VERSION="$os_version"

        # Set XAUTHORITY for compose
        local DUMMY_XAUTHORITY=""
        if [ ! -n "${XAUTHORITY}" ]; then
            DUMMY_XAUTHORITY="/tmp/dummy"
            touch ${DUMMY_XAUTHORITY}
            export XAUTHORITY=${DUMMY_XAUTHORITY}
            export XAUTHORITY_TARGET=${DUMMY_XAUTHORITY}
        else
            export XAUTHORITY_TARGET="/tmp/.docker.xauth"
        fi

        # Default stack services (dx-compiler, dx-runtime, dx-modelzoo)
        local base_services=""
        if printf '%s\n' "$containers" | grep -Fxq "dx-compiler-${os_combo}"; then
            base_services="${base_services} dx-compiler"
        fi
        if printf '%s\n' "$containers" | grep -Fxq "dx-runtime-${os_combo}"; then
            base_services="${base_services} dx-runtime"
        fi
        if printf '%s\n' "$containers" | grep -Fxq "dx-modelzoo-${os_combo}"; then
            base_services="${base_services} dx-modelzoo"
        fi

        if [ -n "$base_services" ]; then
            local sample_container=""
            if printf '%s\n' "$containers" | grep -Fxq "dx-runtime-${os_combo}"; then
                sample_container="dx-runtime-${os_combo}"
            elif printf '%s\n' "$containers" | grep -Fxq "dx-compiler-${os_combo}"; then
                sample_container="dx-compiler-${os_combo}"
            elif printf '%s\n' "$containers" | grep -Fxq "dx-modelzoo-${os_combo}"; then
                sample_container="dx-modelzoo-${os_combo}"
            fi

            local base_project=$(get_compose_project_name 0)
            if [ -n "$sample_container" ]; then
                base_project=$(get_compose_project_from_container "$sample_container" "$base_project")
            fi

            local CMD="docker compose -f docker/docker-compose.yml -p ${base_project} down${base_services}"
            run_compose_down_command "${CMD}" "✓ Successfully stopped and removed default ${os_name}-${os_version} containers" "✗ Failed to stop some default ${os_name}-${os_version} containers"
        fi

        # Intel runtime stack
        if printf '%s\n' "$containers" | grep -Fxq "dx-runtime_intel-hw-acc-${os_combo}"; then
            local intel_project=$(get_compose_project_name 1)
            intel_project=$(get_compose_project_from_container "dx-runtime_intel-hw-acc-${os_combo}" "$intel_project")
            local CMD="docker compose -f docker/docker-compose.yml -f docker/docker-compose.intel_gpu_hw_acc.yml -p ${intel_project} down dx-runtime"
            run_compose_down_command "${CMD}" "✓ Successfully stopped and removed intel ${os_name}-${os_version} runtime containers" "✗ Failed to stop intel ${os_name}-${os_version} runtime containers"
        fi

        echo ""
    done
    
    print_colored_v2 "SUCCESS" "All DXNN® containers have been processed."
}

docker_down_all_with_os_version() 
{
    # Stop all containers regardless of OS version
    print_colored_v2 "INFO" "Stopping all DXNN® containers (Specific OS versions: ${BASE_IMAGE_NAME}-${OS_VERSION})"
    docker_down_dx-compiler
    docker_down_dx-runtime 0
    docker_down_dx-modelzoo

    local intel_container_name="dx-runtime_intel-hw-acc-${BASE_IMAGE_NAME}-${OS_VERSION}"
    if docker ps -a --format "{{.Names}}" | grep -Fxq "${intel_container_name}"; then
        docker_down_dx-runtime 1
    fi
}

docker_down_dx-compiler() 
{
    docker_down_impl "compiler"
}

docker_down_dx-runtime()
{
    local intel_mode=${1:-$INTEL_GPU_MODE}
    local docker_compose_args="-f docker/docker-compose.yml"
    local container_name="dx-runtime-${BASE_IMAGE_NAME}-${OS_VERSION}"

    if [ ${intel_mode} -eq 1 ]; then
        docker_compose_args="${docker_compose_args} -f docker/docker-compose.intel_gpu_hw_acc.yml"
        container_name="dx-runtime_intel-hw-acc-${BASE_IMAGE_NAME}-${OS_VERSION}"
    fi

    local project_name=$(get_compose_project_name ${intel_mode})
    if docker ps -a --format "{{.Names}}" | grep -Fxq "${container_name}"; then
        project_name=$(get_compose_project_from_container "${container_name}" "${project_name}")
    fi

    docker_down_impl "runtime" "${docker_compose_args}" "${intel_mode}" "${project_name}"
}

docker_down_dx-modelzoo()
{
    local docker_compose_args="-f docker/docker-compose.yml"
    docker_down_impl "modelzoo" "${docker_compose_args}"
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

    # Special case: --all without OS version should stop all containers
    if [ "$TARGET_ENV" == "all" ] && [ -z "$UBUNTU_VERSION" ] && [ -z "$DEBIAN_VERSION" ]; then
        docker_down_all_without_os_versions
        return 0
    fi

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
            docker_down_all_with_os_version
            ;;
        *)
            show_help "error" "(Hint) Please specify either the '--all' option or the '--target=<dx-compiler | dx-runtime>' option."
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
        --debian_version=*)
            DEBIAN_VERSION="${1#*=}"
            ;;
        --help)
            show_help
            exit 0
            ;;
        --dev)
            DEV_MODE=1
            ;;
        --intel_gpu)
            INTEL_GPU_MODE=1
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
