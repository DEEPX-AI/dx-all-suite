#!/bin/bash

# Function to get colored output (simplified for shell)
print_colored() {
    local message="$1"
    local level="$2" # "INFO", "DEBUG", "ERROR" etc.
    local enable_debug_logs=${ENABLE_DEBUG_LOGS:-0} # Default to 0 (false) if not provided

    # Suppress DEBUG messages unless enable_debug_logs is 1
    if [[ "$level" == "DEBUG" ]] && [[ "$enable_debug_logs" -ne 1 ]]; then
        return 0 # Do not print DEBUG message
    fi

    case "$level" in
        # TAG
        "ERROR") printf "${COLOR_BG_RED}[ERROR]${COLOR_RESET}${COLOR_BRIGHT_RED} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "FAIL") printf "${COLOR_BG_RED}[FAIL]${COLOR_RESET}${COLOR_BRIGHT_RED} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "INFO") printf "${COLOR_BG_BLUE}[INFO]${COLOR_RESET}${COLOR_BRIGHT_BLUE} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "WARNING") printf "${COLOR_BG_YELLOW}[WARNING]${COLOR_RESET}${COLOR_BRIGHT_YELLOW} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "DEBUG") printf "${COLOR_BG_YELLOW}[DEBUG]${COLOR_RESET}${COLOR_BRIGHT_YELLOW} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "HINT") printf "${COLOR_BG_GREEN}[HINT]${COLOR_RESET}${COLOR_BRIGHT_GREEN_ON_BLACK} %s ${COLOR_RESET}\n" "$message" >&2 ;;

        # COLOR
        "RED") printf "${COLOR_BRIGHT_RED} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "BLUE") printf "${COLOR_BRIGHT_BLUE} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "YELLOW") printf "${COLOR_BRIGHT_YELLOW} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "GREEN") printf "${COLOR_BRIGHT_GREEN} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        *) printf "%s\n" "$message" >&2 ;;
    esac
}

print_colored_v2() {
    print_colored "$2" "$1"
}


check_container_mode() {
    # Check if running in a container
    if grep -qE "/docker|/lxc|/containerd" /proc/1/cgroup || [ -f /.dockerenv ]; then
        print_colored_v2 "INFO" "(container mode detected)"
        return 0
    else
        print_colored_v2 "INFO" "(host mode detected)"
        return 1
    fi
}

check_virtualenv() {
    if [ -n "$VIRTUAL_ENV" ]; then
        venv_name=$(basename "$VIRTUAL_ENV")
        print_colored_v2 "✅ Virtual environment '$venv_name' is currently active."
        return 0
    else
        print_colored_v2 "❌ No virtual environment is currently active."
        return 1
    fi
}


# Handle command failure with user confirmation and suggested action
handle_cmd_failure() {
    local error_message=$1
    local hint_message=$2
    local origin_cmd=$3
    local suggested_action_cmd=$4
    
    print_colored_v2 "ERROR" "${error_message}"
    print_colored_v2 "HINT" "${hint_message}"
    print_colored_v2 "YELLOW" "Would you like to perform the suggested action now? [Y/n] (Default is 'y' after 10 seconds of no input. This process will be aborted if you enter 'n')"
    read -t 10 -p ">> " user_input
    user_input=${user_input:-Y}
    if [[ "${user_input,,}" == "n" ]]; then
        print_colored_v2 "INFO" "This process aborted by user."
        exit 1
    else
        if [ -n "$suggested_action_cmd" ]; then
            print_colored_v2 "INFO" "Suggested action will be performed."
            eval "$suggested_action_cmd" || {
                print_colored_v2 "ERROR" "Failed to perform suggested action."
                exit 1
            }
        fi

        if [ -n "$origin_cmd" ]; then
            eval "$origin_cmd" || {
                print_colored_v2 "ERROR" "${error_message}"
                exit 1
            }
        fi
    fi
}
