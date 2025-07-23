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
