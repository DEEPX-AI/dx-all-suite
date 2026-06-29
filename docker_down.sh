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
FEDORA_VERSION=""
RHEL_VERSION=""
CENTOS_VERSION=""
BASE_IMAGE_NAME=""
OS_VERSION=""

DEV_MODE=0
INTEL_GPU_HW_ACC=0

# Function to display help message
show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--all${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--all${COLOR_RESET} ${COLOR_YELLOW}(--ubuntu_version=<version> | --debian_version=<version>)${COLOR_RESET}"
    echo -e "   or: ${COLOR_CYAN}$(basename "$0") ${COLOR_GREEN}--target=<dx-compiler>${COLOR_RESET} ${COLOR_YELLOW}(--ubuntu_version=<version> | --fedora_version=<version> | --rhel_version=<version> | --centos_version=<version>)${COLOR_RESET}"
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
    echo -e "  ${COLOR_YELLOW}--fedora_version=<version>${COLOR_RESET}     Specify Fedora version (ex: 42, 43, 44, 45) ${COLOR_RED}(dx-compiler only)${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}--rhel_version=<version>${COLOR_RESET}       Specify RHEL/UBI version (ex: 9, 10) ${COLOR_RED}(dx-compiler only)${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}--centos_version=<version>${COLOR_RESET}     Specify CentOS Stream version (ex: stream9, stream10) ${COLOR_RED}(dx-compiler only)${COLOR_RESET}"
    echo -e "                                   Note: ${COLOR_CYAN}dx-compiler${COLOR_RESET} supports Ubuntu, Fedora, RHEL, and CentOS Stream"
    echo -e "                                   Note: ${COLOR_CYAN}dx-runtime${COLOR_RESET} and ${COLOR_CYAN}dx-modelzoo${COLOR_RESET} support Ubuntu and Debian only"
    echo -e ""
    echo -e "${COLOR_BOLD}Optional:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}[--help]${COLOR_RESET}                       Show this help message"
    echo -e ""
    echo -e "${COLOR_BOLD}Examples:${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --all --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --ubuntu_version=24.04${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --fedora_version=42${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --rhel_version=9${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --target=dx-compiler --centos_version=stream9${COLOR_RESET}"
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
    export COMPOSE_PROJECT_NAME="dx-all-suite-$(echo "${IMAGE_TAG_SUFFIX:-${BASE_IMAGE_NAME}-${OS_VERSION}}" | sed 's/[\.\/]/-/g')"
    CMD="docker compose ${config_file_args} -p ${COMPOSE_PROJECT_NAME} down dx-${target}"
    echo "${CMD}"

    ${CMD} || { print_colored_v2 "ERROR" "docker down 'dx-${target}' failed. "; exit 1; }
}

docker_down_all_without_os_versions()
{
    # Stop all containers regardless of OS version
    print_colored_v2 "INFO" "Stopping all DXNN® containers (all OS versions)"
    
    # Get all running dx-compiler, dx-runtime, dx-modelzoo containers
    local containers=$(docker ps -a --format "{{.Names}}" 2>/dev/null | grep -E "^(dx-compiler|dx-runtime|dx-modelzoo)-")
    
    if [ -z "$containers" ]; then
        print_colored_v2 "INFO" "No DXNN® containers found."
        return 0
    fi
    
    echo "Found containers:"
    echo "$containers"
    
    # Extract unique OS combinations from container names
    # Container name format: dx-{service}-{os_name}-{os_version}
    local unique_os_combinations=$(echo "$containers" | sed -E 's/^dx-(compiler|runtime|modelzoo)-//' | sort -u)
    
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
        export COMPOSE_PROJECT_NAME="dx-all-suite-$(echo "${os_name}-${os_version}" | sed 's/\./-/g')"
        
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
        
        # Find which services exist for this OS combination
        local services_to_down=""
        if echo "$containers" | grep -q "^dx-compiler-${os_combo}$"; then
            services_to_down="${services_to_down} dx-compiler"
        fi
        if echo "$containers" | grep -q "^dx-runtime-${os_combo}$"; then
            services_to_down="${services_to_down} dx-runtime"
        fi
        if echo "$containers" | grep -q "^dx-modelzoo-${os_combo}$"; then
            services_to_down="${services_to_down} dx-modelzoo"
        fi
        
        if [ -n "$services_to_down" ]; then
            local CMD="docker compose -f docker/docker-compose.yml -p ${COMPOSE_PROJECT_NAME} down${services_to_down}"
            echo "  ${CMD}"
            
            ${CMD} 2>&1 | while IFS= read -r line; do
                echo "  $line"
            done
            
            if [ ${PIPESTATUS[0]} -eq 0 ]; then
                print_colored_v2 "SUCCESS" "✓ Successfully stopped and removed ${os_name}-${os_version} containers"
            else
                print_colored_v2 "WARNING" "✗ Failed to stop some ${os_name}-${os_version} containers"
            fi
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
    if [ "$TARGET_ENV" == "all" ] && [ -z "$UBUNTU_VERSION" ] && [ -z "$DEBIAN_VERSION" ] && \
       [ -z "$FEDORA_VERSION" ] && [ -z "$RHEL_VERSION" ] && [ -z "$CENTOS_VERSION" ]; then
        docker_down_all_without_os_versions
        return 0
    fi

    # Validate OS version options - only one can be specified
    local OS_OPTIONS_COUNT=0
    [ -n "$UBUNTU_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$DEBIAN_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$FEDORA_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$RHEL_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))
    [ -n "$CENTOS_VERSION" ] && OS_OPTIONS_COUNT=$((OS_OPTIONS_COUNT + 1))

    if [ "$OS_OPTIONS_COUNT" -gt 1 ]; then
        show_help "error" "Cannot specify multiple OS version options. Please choose one."
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
            9)  BASE_IMAGE_NAME="redhat/ubi9"; OS_VERSION="9" ;;
            10) BASE_IMAGE_NAME="redhat/ubi10"; OS_VERSION="10" ;;
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
        --fedora_version=*)
            FEDORA_VERSION="${1#*=}"
            ;;
        --rhel_version=*)
            RHEL_VERSION="${1#*=}"
            ;;
        --centos_version=*)
            CENTOS_VERSION="${1#*=}"
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
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

main

popd >&2

exit 0
