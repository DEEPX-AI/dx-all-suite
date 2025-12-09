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

NVIDIA_GPU_MODE=0
DEV_MODE=0
INTEL_GPU_HW_ACC=0

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
    # echo -e "  ${COLOR_GREEN}[--nvidia_gpu]${COLOR_RESET}                 Enable NVIDIA GPU support"
    # echo -e "  ${COLOR_GREEN}[--dev]${COLOR_RESET}                        Enable development mode"
    # echo -e "  ${COLOR_GREEN}[--intel_gpu_hw_acc]${COLOR_RESET}           Enable Intel GPU hardware acceleration"
    echo -e "  ${COLOR_GREEN}[--help]${COLOR_RESET}                       Show this help message"
    echo -e ""
    echo -e "${COLOR_BOLD}Examples:${COLOR_RESET}"
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

check_xdg_sesstion_type()
{
    print_colored_v2 "INFO" "XDG_SESSION_TYPE: $XDG_SESSION_TYPE"
    if [ "$XDG_SESSION_TYPE" == "tty" ]; then
        print_colored_v2 "WARNING" "You are currently running in a **tty session**, which does not support GUI. In such environments, it is not possible to visually confirm the results of example code execution via GUI. (Note): "
        echo -e -n "${TAG_INFO} ${COLOR_BRIGHT_GREEN_ON_BLACK}Press any key and hit Enter to continue. ${COLOR_RESET}"
        read -r answer
        print_colored_v2 "INFO" "Start docker run ..."

    elif [ "$XDG_SESSION_TYPE" != "x11" ]; then
        print_colored_v2 "WARNING" "it is recommended to use an **X11 session (with .Xauthority support)** when working with the 'dx-all-suite' container."
        print_colored_v2 "WARNING" "For more details, please refer to the [FAQ section of the dx-all-suite documentation](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/faq.md)."

        echo -e "${COLOR_BRIGHT_GREEN_ON_BLACK}if the user's host environment is not based on **X11 (with .Xauthority)** but instead uses **Xwayland** or similar, the 'xauth' data may be lost after a system reboot or session logout. As a result, the authentication file mount between the host and the container may fail, making it impossible to restart or reuse the container.${COLOR_RESET}"
        echo -e -n "${COLOR_RED_ON_BLACK}This may cause issues. Do you still want to continue? (y/n): ${COLOR_RESET}"
        read -r answer
        if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
            print_colored_v2 "INFO" "Start docker run ..."
        else
            print_colored_v2 "INFO" "Docker run has been canceled."
            exit 1
        fi
    fi
}

docker_run_impl()
{
    local target=$1
    local config_file_args=${2:--f docker/docker-compose.yml}

    # Check if Docker image exists before running
    local image_name="dx-${target}:${BASE_IMAGE_NAME}-${OS_VERSION}"
    if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${image_name}$"; then
        print_colored_v2 "WARNING" "Docker image '${image_name}' not found."
        print_colored_v2 "HINT" "Please build the image first using:"
        echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** './docker_build.sh --target=${target} --ubuntu_version=${OS_VERSION}'${COLOR_RESET} **"
        echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   or './docker_build.sh --all --ubuntu_version=${OS_VERSION}'${COLOR_RESET} **"
        return 1
    fi

    if [ ${NVIDIA_GPU_MODE} -eq 1 ]; then
        config_file_args="${config_file_args} -f docker/docker-compose.nvidia_gpu.yml"
    fi

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
        DUMMY_XAUTHORITY="${DX_AS_PATH}/dummy_xauthority"
        rm -rf ${DUMMY_XAUTHORITY}
        touch ${DUMMY_XAUTHORITY}
        export XAUTHORITY=${DUMMY_XAUTHORITY}
        export XAUTHORITY_TARGET=${DUMMY_XAUTHORITY}
    else
        print_colored_v2 "INFO" "XAUTHORITY(${XAUTHORITY}) is set"
        export XAUTHORITY_TARGET="/tmp/.docker.xauth"
    fi

    # Dynamically set the project name based on the Ubuntu
    export COMPOSE_PROJECT_NAME="dx-all-suite-$(echo "${BASE_IMAGE_NAME}-${OS_VERSION}" | sed 's/\./-/g')"
    CMD="docker compose ${config_file_args} -p ${COMPOSE_PROJECT_NAME} up -d --remove-orphans dx-${target}"
    echo "${CMD}"

    ${CMD} || { print_colored_v2 "ERROR" "docker run 'dx-${target}' failed. "; exit 1; }

    if [ "$XDG_SESSION_TYPE" == "tty" ]; then
        local DOCKER_EXEC_CMD="docker exec -it dx-${target}-${BASE_IMAGE_NAME}-${OS_VERSION} touch /deepx/tty_flag"

        echo -e "${DOCKER_EXEC_CMD}"
        ${DOCKER_EXEC_CMD}
    elif [ -n "${DUMMY_XAUTHORITY}" ]; then
        print_colored_v2 "INFO" "Adding xauth into docker container"

        # remove 'localhost' or 'LOCALHOST' in DISPLAY env var
        if [[ "$DISPLAY" == localhost:* ]]; then
            export DISPLAY=${DISPLAY#localhost}
        elif [[ "$DISPLAY" == LOCALHOST:* ]]; then
            export DISPLAY=${DISPLAY#LOCALHOST}
        fi

        XAUTHORITY=~/.Xauthority
        export XAUTHORITY
        XAUTH=$(xauth list "$DISPLAY")
        XAUTH_ADD_CMD="xauth add $XAUTH"
        
        local DOCKER_EXEC_CMD1="docker exec -it dx-${target}-${BASE_IMAGE_NAME}-${OS_VERSION} touch /tmp/.docker.xauth"
        local DOCKER_EXEC_CMD2="docker exec -it dx-${target}-${BASE_IMAGE_NAME}-${OS_VERSION} ${XAUTH_ADD_CMD}"

        echo -e "${DOCKER_EXEC_CMD1}"
        echo -e "${DOCKER_EXEC_CMD2}"
        ${DOCKER_EXEC_CMD1}
        ${DOCKER_EXEC_CMD2}
    fi
}

docker_run_all() 
{
    local results=()
    local failed_count=0
    local success_count=0
    local skip_count=0
    
    # Run dx-compiler
    local output
    output=$(docker_run_dx-compiler 2>&1)
    local ret=$?
    if [ $ret -eq 0 ]; then
        results+=("✅ dx-compiler: Success")
        ((success_count++))
    elif [ $ret -eq 5 ]; then
        local reason=$(echo "$output" | grep -oP '(?<=\[SKIP\]|\[INFO\]).+' | head -1 | sed 's/^ *//')
        results+=("⏭️  dx-compiler: Skipped - ${reason}")
        ((skip_count++))
    else
        local reason=$(echo "$output" | grep -oP '(?<=\[ERROR\]|\[WARNING\]).+' | head -1 | sed 's/^ *//')
        if [ -z "$reason" ]; then
            reason="Unknown error"
        fi
        results+=("❌ dx-compiler: Failed - ${reason}")
        ((failed_count++))
    fi
    
    # Run dx-runtime
    output=$(docker_run_dx-runtime 2>&1)
    ret=$?
    if [ $ret -eq 0 ]; then
        results+=("✅ dx-runtime: Success")
        ((success_count++))
    elif [ $ret -eq 5 ]; then
        local reason=$(echo "$output" | grep -oP '(?<=\[SKIP\]|\[INFO\]).+' | head -1 | sed 's/^ *//')
        results+=("⏭️  dx-runtime: Skipped - ${reason}")
        ((skip_count++))
    else
        local reason=$(echo "$output" | grep -oP '(?<=\[ERROR\]|\[WARNING\]).+' | head -1 | sed 's/^ *//')
        if [ -z "$reason" ]; then
            reason="Unknown error"
        fi
        results+=("❌ dx-runtime: Failed - ${reason}")
        ((failed_count++))
    fi
    
    # Run dx-modelzoo
    output=$(docker_run_dx-modelzoo 2>&1)
    ret=$?
    if [ $ret -eq 0 ]; then
        results+=("✅ dx-modelzoo: Success")
        ((success_count++))
    elif [ $ret -eq 5 ]; then
        local reason=$(echo "$output" | grep -oP '(?<=\[SKIP\]|\[INFO\]).+' | head -1 | sed 's/^ *//')
        results+=("⏭️  dx-modelzoo: Skipped - ${reason}")
        ((skip_count++))
    else
        local reason=$(echo "$output" | grep -oP '(?<=\[ERROR\]|\[WARNING\]).+' | head -1 | sed 's/^ *//')
        if [ -z "$reason" ]; then
            reason="Unknown error"
        fi
        results+=("❌ dx-modelzoo: Failed - ${reason}")
        ((failed_count++))
    fi
    
    # Display summary
    echo ""
    echo "======================================"
    echo "    Container Execution Summary"
    echo "======================================"
    for result in "${results[@]}"; do
        echo "$result"
    done
    echo "======================================"
    echo "Total: $((success_count + failed_count + skip_count)) | Success: ${success_count} | Failed: ${failed_count} | Skipped: ${skip_count}"
    echo "======================================"
}

docker_run_dx-compiler() 
{
    # dx-compiler only supports ubuntu
    if [ "${BASE_IMAGE_NAME}" != "ubuntu" ]; then
        print_colored_v2 "SKIP" "dx-compiler only supports Ubuntu. Skipping run for ${BASE_IMAGE_NAME}."
        return 5
    fi

    # this function is defined in scripts/common_util.sh
    # Usage: os_check "supported_os_names" "ubuntu_versions" "debian_versions"
    os_check "ubuntu" "20.04 22.04 24.04" "" || {
        print_colored_v2 "SKIP" "Current OS is not supported. Skip and continue to next target."
        return 5
    }

    # this function is defined in scripts/common_util.sh
    # Usage: arch_check "supported_arch_names"
    arch_check "amd64 x86_64" || {
        print_colored_v2 "SKIP" "Current architecture is not supported. Skip and continue to next target."
        return 5
    }

    local docker_compose_args="-f docker/docker-compose.yml"
    docker_run_impl "compiler" "${docker_compose_args}" || return 1
    return 0
}

check_dxrtd_process()
{
    echo "=== Checking dxrtd location ===" >&2

    # 1. Check if running on host (systemd)
    if systemctl is-active --quiet dxrt.service 2>/dev/null; then
        echo "⚠️ dxrtd is running as HOST systemd service" >&2
        systemctl status dxrt.service --no-pager -l >&2
        echo "HOST"
        return 0
    fi

    # 2. Find the actual container that owns the dxrtd process
    local PID=$(pgrep dxrtd)
    if [ -n "$PID" ]; then
        echo "=== dxrtd Process Details ===" >&2
        echo "PID: $PID" >&2
        echo "Parent PID: $(ps -o ppid= -p $PID | tr -d ' ')" >&2
        echo "Command line: $(cat /proc/$PID/cmdline | tr '\0' ' ')" >&2
        
        # Find actual container ID using cgroup
        local CONTAINER_ID=$(cat /proc/$PID/cgroup 2>/dev/null | grep -o 'docker-[a-f0-9]\{64\}' | head -1 | sed 's/docker-//' | cut -c1-12)
        if [ -n "$CONTAINER_ID" ]; then
            local CONTAINER_NAME=$(docker ps --format 'table {{.Names}}\t{{.ID}}' | grep $CONTAINER_ID | awk '{print $1}')
            echo "⚠️ dxrtd is running in Docker container: $CONTAINER_NAME (ID: $CONTAINER_ID)" >&2
            
            # Check the container configuration
            echo "--- Container Configuration ---" >&2
            docker inspect $CONTAINER_NAME --format 'Entrypoint: {{.Config.Entrypoint}}' >&2
            docker inspect $CONTAINER_NAME --format 'Command: {{.Config.Cmd}}' >&2
            echo "--- Container dxrtd Process ---" >&2
            docker exec $CONTAINER_NAME ps aux | grep dxrtd | grep -v grep >&2
            echo "$CONTAINER_NAME"
            return 0
        else
            echo "⚠️ Could not determine container (possibly running on HOST)" >&2
            echo "UNKNOWN"
            return 0
        fi
    else
        echo "✅ No dxrtd process found" >&2
        echo "NONE"
        return 0
    fi

    echo "=== All Container Entrypoint Summary ===" >&2
    for container in $(docker ps --format '{{.Names}}'); do
        entrypoint=$(docker inspect $container --format '{{.Config.Entrypoint}}')
        echo "$container: $entrypoint" >&2
    done
}

# Check if entrypoint/command override is configured in docker-compose.yml for dx-runtime
check_runtime_entrypoint_override() {
    local compose_file="${DX_AS_PATH}/docker/docker-compose.yml"
    
    # Check if docker-compose.yml file exists
    if [ ! -f "$compose_file" ]; then
        return 1
    fi
    
    # Extract dx-runtime section: from dx-runtime to the next service (dx-modelzoo)
    local in_runtime=0
    local runtime_section=""
    
    while IFS= read -r line; do
        # Start of dx-runtime section
        if [[ "$line" =~ ^[[:space:]]*dx-runtime:[[:space:]]*$ ]]; then
            in_runtime=1
            runtime_section+="$line"$'\n'
            continue
        fi
        
        # Exit when next top-level service is found (lines ending with : without indentation)
        if [[ $in_runtime -eq 1 ]] && [[ "$line" =~ ^[[:space:]]{0,2}[a-zA-Z0-9_-]+:[[:space:]]*$ ]] && [[ ! "$line" =~ dx-runtime ]]; then
            break
        fi
        
        # Collect dx-runtime section content
        if [[ $in_runtime -eq 1 ]]; then
            runtime_section+="$line"$'\n'
        fi
    done < "$compose_file"
    
    # Check for uncommented entrypoint
    local has_entrypoint=$(echo "$runtime_section" | grep -E "^[[:space:]]+entrypoint:" | grep -v "^[[:space:]]*#")
    # Check for uncommented command
    local has_command=$(echo "$runtime_section" | grep -E "^[[:space:]]+command:" | grep -v "^[[:space:]]*#")
    
    if [[ -n "$has_entrypoint" ]] || [[ -n "$has_command" ]]; then
        return 0  # entrypoint/command is configured
    else
        return 1  # not configured
    fi
}

docker_run_dx-runtime()
{
    local which_dxrtd=$(check_dxrtd_process)
    
    if [ "$which_dxrtd" == "NONE" ]; then
        print_colored_v2 "INFO" "No existing dxrtd (DX-RT Service) process found. Proceeding to start dx-runtime container."
    else
        # Check if entrypoint/command is already configured in docker-compose.yml
        if check_runtime_entrypoint_override; then
            print_colored_v2 "INFO" "dxrtd service is running externally (on ${which_dxrtd}), but docker-compose.yml has entrypoint/command override configured."
            print_colored_v2 "INFO" "Proceeding to start dx-runtime container without starting dxrtd service inside the container."
        else
            # Display existing warning message logic
            if [[ "$which_dxrtd" == "HOST" || "$which_dxrtd" == "UNKNOWN" ]]; then
                print_colored_v2 "WARNING" "dxrtd (DX-RT Service) is already running on the ${which_dxrtd}."
                print_colored_v2 "WARNING" "Please stop the dxrtd service on the ${which_dxrtd} before running the dx-runtime container."
                print_colored_v2 "WARNING" "(By default, the dxrtd service runs within the dx-runtime container)"
                print_colored_v2 "HINT" "1) If you want to run the dxrtd service in a different container or host"
                
                echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** please uncomment the 'entrypoint' and 'command' lines in the docker-compose.yml file."
                echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** For more details, please refer to the (https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/faq.md) **"
                
                print_colored_v2 "HINT" "2) or stop the dxrtd service on the ${which_dxrtd} before running the dx-runtime container."
                print_colored_v2 "HINT" "   You can stop the dxrtd service on the ${which_dxrtd} by running the following command:"

                if [ "$which_dxrtd" == "HOST" ]; then
                    echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** 'sudo systemctl stop dxrt.service'${COLOR_RESET} **"
                else
                    local PID=$(pgrep dxrtd)
                    echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** 'sudo kill -9 ${PID}'${COLOR_RESET} **"
                fi
                return 1
            else
                print_colored_v2 "WARNING" "dxrtd (DX-RT Service) is already running on the container '${which_dxrtd}'."
                print_colored_v2 "WARNING" "Please stop the dxrtd service on the container '${which_dxrtd}' before running the dx-runtime container."
                print_colored_v2 "WARNING" "(By default, the dxrtd service runs within the dx-runtime container)"
                print_colored_v2 "HINT" "1) If you want to run the dxrtd service in a different container or host"
                
                echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** please uncomment the 'entrypoint' and 'command' lines in the docker-compose.yml file."
                echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** For more details, please refer to the (https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/faq.md) **"
                
                print_colored_v2 "HINT" "2) or stop the dxrtd service on the container '${which_dxrtd}' before running the dx-runtime container."
                print_colored_v2 "HINT" "   You can stop the dxrtd service on the container '${which_dxrtd}' by running the following command:"
                
                echo -e "${COLOR_BOLD}${COLOR_CYAN}[HINT]   ** 'sudo docker stop ${which_dxrtd}'${COLOR_RESET} **"
                return 1
            fi
        fi
    fi

    local docker_compose_args="-f docker/docker-compose.yml"

    if [ ${INTEL_GPU_HW_ACC} -eq 1 ]; then
        docker_compose_args="${docker_compose_args} -f docker-compose.intel_gpu_hw_acc.yml"
    fi

    docker_run_impl "runtime" "${docker_compose_args}" || return 1
}

docker_run_dx-modelzoo()
{
    local docker_compose_args="-f docker/docker-compose.yml"
    docker_run_impl "modelzoo" "${docker_compose_args}" || return 1
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

    check_xdg_sesstion_type

    case $TARGET_ENV in
        dx-compiler)
            echo "Installing dx-compiler"
            docker_run_dx-compiler || print_colored_v2 "SKIP" "Failed to run dx-compiler container."
            ;;
        dx-runtime)
            echo "Installing dx-runtime"
            docker_run_dx-runtime || print_colored_v2 "SKIP" "Failed to run dx-runtime container."
            ;;
        dx-modelzoo)
            echo "Installing dx-modelzoo"
            docker_run_dx-modelzoo || print_colored_v2 "SKIP" "Failed to run dx-modelzoo container."
            ;;
        all)
            echo "Installing all DXNN® environments"
            docker_run_all
            ;;
        *)
            show_help "error" "(Hint) Please specify either the '--all' option or the '--target=<dx-compiler | dx-runtime | dx-modelzoo>' option."
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
        --nvidia_gpu)
            NVIDIA_GPU_MODE=1
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
