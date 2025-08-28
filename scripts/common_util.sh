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
        "SUCCESS") printf "${COLOR_BG_GREEN}[SUCCESS]${COLOR_RESET}${COLOR_BRIGHT_GREEN} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "OK") printf "${COLOR_BG_GREEN}[OK]${COLOR_RESET}${COLOR_BRIGHT_GREEN} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "FAIL") printf "${COLOR_BG_RED}[FAIL]${COLOR_RESET}${COLOR_BRIGHT_RED} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "INFO") printf "${COLOR_BG_BLUE}[INFO]${COLOR_RESET}${COLOR_BRIGHT_BLUE} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "WARNING") printf "${COLOR_BG_YELLOW}[WARNING]${COLOR_RESET}${COLOR_BRIGHT_YELLOW} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "DEBUG") printf "${COLOR_BG_YELLOW}[DEBUG]${COLOR_RESET}${COLOR_BRIGHT_YELLOW} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "HINT") printf "${COLOR_BG_GREEN}[HINT]${COLOR_RESET}${COLOR_BRIGHT_GREEN_ON_BLACK} %s ${COLOR_RESET}\n" "$message" >&2 ;;
        "SKIP") printf "${COLOR_WHITE_ON_GRAY}[SKIP]${COLOR_RESET}${COLOR_BRIGHT_WHITE_ON_GRAY} %s ${COLOR_RESET}\n" "$message" >&2 ;;

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

# OS Check function
# Usage: os_check "supported_os_names" "ubuntu_versions" "debian_versions"
# Example: os_check "ubuntu debian" "20.04 22.04 24.04" "11 12"
os_check() {
    print_colored "--- OS Check..... ---" "INFO"
    
    # Parse function arguments with default values
    local supported_os_names="${1}"
    local supported_ubuntu_versions="${2}"
    local supported_debian_versions="${3}"

    print_colored "supported_os_names: $supported_os_names" "DEBUG"
    print_colored "supported_ubuntu_versions: $supported_ubuntu_versions" "DEBUG"
    print_colored "supported_debian_versions: $supported_debian_versions" "DEBUG"
    
    # Check if /etc/os-release exists
    if [ ! -f /etc/os-release ]; then
        print_colored "/etc/os-release file not found. Cannot determine OS information." "ERROR"
        popd >&2
        exit 1
    fi
    
    # Get OS information from /etc/os-release using grep and sed
    local OS_ID=""
    local OS_VERSION_ID=""
    
    # Extract OS information without sourcing the file
    OS_ID=$(grep "^ID=" /etc/os-release | sed 's/^ID=//' | tr -d '"')
    OS_VERSION_ID=$(grep "^VERSION_ID=" /etc/os-release | sed 's/^VERSION_ID=//' | tr -d '"')
    
    print_colored "Detected OS: $OS_ID $OS_VERSION_ID" "INFO"
    
    # Check if OS is supported using supported_os_names parameter
    local os_supported=false
    local detected_os=""
    
    # Loop through supported OS names and check compatibility
    for supported_os in $supported_os_names; do
        if grep -q "ID=${supported_os}\|ID_LIKE=.*${supported_os}" /etc/os-release; then
            os_supported=true
            detected_os="$supported_os"
            print_colored "Detected $supported_os or $supported_os-compatible OS" "DEBUG"
            break
        fi
    done
    
    # detected_os will be used directly for version checking
    
    if [ "$os_supported" = false ]; then
        print_colored "Unsupported operating system: $OS_ID" "ERROR"
        print_colored "Supported operating systems: $supported_os_names and their compatible distributions" "HINT"
        popd >&2
        exit 1
    fi
    
    # Check OS version support based on detected OS
    local version_supported=false
    local supported_versions=""
    
    case "$detected_os" in
        ubuntu)
            supported_versions="$supported_ubuntu_versions"
            for version in $supported_ubuntu_versions; do
                if [ "$OS_VERSION_ID" = "$version" ]; then
                    version_supported=true
                    break
                fi
            done
            ;;
        debian)
            supported_versions="$supported_debian_versions"
            for version in $supported_debian_versions; do
                if [ "$OS_VERSION_ID" = "$version" ]; then
                    version_supported=true
                    break
                fi
            done
            ;;
        *)
            print_colored "Internal error: Unsupported OS in version check" "ERROR"
            popd >&2
            exit 1
            ;;
    esac
    
    if [ "$version_supported" = false ]; then
        print_colored "Unsupported $detected_os version: $OS_VERSION_ID" "ERROR"
        print_colored "Supported $detected_os versions: $supported_versions" "HINT"
        print_colored "Please upgrade to a supported $detected_os version." "HINT"
        popd >&2
        exit 1
    fi
    
    print_colored "$detected_os $OS_VERSION_ID is supported." "INFO"
    print_colored "[OK] OS check completed successfully." "INFO"
}

# Architecture Check function
# Usage: arch_check "supported_arch_names"
# Example: 
#   only x86: arch_check "amd64 x86_64"
#   only ARM: arch_check "arm64 aarch64 arm64 armv7l"
#   both ARM and x86: arch_check "amd64 x86_64 arm64 aarch64 armv7l"
arch_check() {
    print_colored "--- Arch Check..... ---" "INFO"
    local supported_arch_names="${1}"

    print_colored "supported_arch_names: $supported_arch_names" "DEBUG"
    
    # Note: amd64 and x86_64 are treated as compatible (both represent 64-bit x86 architecture)
    # - amd64: Debian/Ubuntu package architecture naming convention
    # - x86_64: Kernel/System architecture naming convention
    
    # Get system architecture using uname -m (POSIX standard, available on all Linux systems)
    local SYSTEM_ARCH=""
    SYSTEM_ARCH=$(uname -m 2>/dev/null)
    
    if [ -z "$SYSTEM_ARCH" ]; then
        print_colored "Failed to determine system architecture using uname -m" "ERROR"
        popd >&2
        exit 1
    fi
    
    print_colored "Detected architecture: $SYSTEM_ARCH" "INFO"
    
    # Check if architecture is supported
    local arch_supported=false
    
    # Loop through supported architecture names
    for supported_arch in $supported_arch_names; do
        # Direct match
        if [ "$SYSTEM_ARCH" = "$supported_arch" ]; then
            arch_supported=true
            print_colored "Architecture $SYSTEM_ARCH is supported" "DEBUG"
            break
        fi
    done
    
    if [ "$arch_supported" = false ]; then
        print_colored "Unsupported architecture: $SYSTEM_ARCH" "ERROR"
        print_colored "Supported architectures: $supported_arch_names" "HINT"
        popd >&2
        exit 1
    fi
    
    print_colored "Architecture $SYSTEM_ARCH is supported." "INFO"
    print_colored "[OK] Architecture check completed successfully." "INFO"
}

delete_dir() {
    local path="$1"
    
    # Use shell globbing to expand wildcards
    # This will handle patterns like "build_*", "*.log", etc.
    for expanded_path in $path; do
        if [ -e "$expanded_path" ]; then
            print_colored_v2 "INFO" "Deleting path: $expanded_path"
            
            # First attempt: try to delete without sudo
            rm -rf "$expanded_path" 2>&1
            local exit_code=$?
            
            if [ $exit_code -ne 0 ]; then
                # Check if it's a permission denied error
                if [[ "$(rm -rf "$expanded_path" 2>&1)" == *"Permission denied"* ]] || [ $exit_code -eq 1 ]; then
                    print_colored_v2 "WARNING" "Permission denied when deleting: $expanded_path"
                    print_colored_v2 "INFO" "Retrying with sudo..."
                    
                    # Second attempt: try to delete with sudo
                    sudo rm -rf "$expanded_path" 2>&1
                    local sudo_exit_code=$?
                    
                    if [ $sudo_exit_code -eq 0 ]; then
                        print_colored_v2 "SUCCESS" "Successfully deleted with sudo: $expanded_path"
                    else
                        print_colored_v2 "ERROR" "Failed to delete even with sudo: $expanded_path"
                        exit 1
                    fi
                else
                    print_colored_v2 "ERROR" "Failed to delete: $expanded_path (exit code: $exit_code)"
                    exit 1
                fi
            fi
        else
            print_colored_v2 "DEBUG" "Skip to delete path, because it does not exist: $expanded_path"
        fi
    done
    
    # If no files matched the pattern, show appropriate message
    if [ ! -e "$path" ] && [[ "$path" == *"*"* ]]; then
        print_colored_v2 "DEBUG" "No paths found matching pattern: $path"
    fi
}

# Function to delete symlinks and their target files
delete_symlinks() {
    local dir="$1"
    for symlink in "$dir"/*; do
        if [ -L "$symlink" ]; then  # Check if the file is a symbolic link
            real_file=$(readlink -f "$symlink")  # Get the actual file path the symlink points to

            # If the original file exists, delete it
            if [ -e "$real_file" ]; then
                print_colored_v2 "INFO" "Deleting original file: $real_file"
                
                # First attempt: try to delete without sudo
                rm -rf "$real_file" 2>&1
                local exit_code=$?
                
                if [ $exit_code -ne 0 ]; then
                    # Check if it's a permission denied error
                    if [[ "$(rm -rf "$real_file" 2>&1)" == *"Permission denied"* ]] || [ $exit_code -eq 1 ]; then
                        print_colored_v2 "WARNING" "Permission denied when deleting original file: $real_file"
                        print_colored_v2 "INFO" "Retrying with sudo..."
                        
                        # Second attempt: try to delete with sudo
                        sudo rm -rf "$real_file" 2>&1
                        local sudo_exit_code=$?
                        
                        if [ $sudo_exit_code -eq 0 ]; then
                            print_colored_v2 "SUCCESS" "Successfully deleted original file with sudo: $real_file"
                        else
                            print_colored_v2 "ERROR" "Failed to delete original file even with sudo: $real_file"
                            exit 1
                        fi
                    else
                        print_colored_v2 "ERROR" "Failed to delete original file: $real_file (exit code: $exit_code)"
                        exit 1
                    fi
                fi
            fi

            # Delete the symbolic link
            print_colored_v2 "INFO" "Deleting symlink: $symlink"
            
            # First attempt: try to delete without sudo
            rm -rf "$symlink" 2>&1
            local exit_code=$?
            
            if [ $exit_code -ne 0 ]; then
                # Check if it's a permission denied error
                if [[ "$(rm -rf "$symlink" 2>&1)" == *"Permission denied"* ]] || [ $exit_code -eq 1 ]; then
                    print_colored_v2 "WARNING" "Permission denied when deleting symlink: $symlink"
                    print_colored_v2 "INFO" "Retrying with sudo..."
                    
                    # Second attempt: try to delete with sudo
                    sudo rm -rf "$symlink" 2>&1
                    local sudo_exit_code=$?
                    
                    if [ $sudo_exit_code -eq 0 ]; then
                        print_colored_v2 "SUCCESS" "Successfully deleted symlink with sudo: $symlink"
                    else
                        print_colored_v2 "ERROR" "Failed to delete symlink even with sudo: $symlink"
                        exit 1
                    fi
                else
                    print_colored_v2 "ERROR" "Failed to delete symlink: $symlink (exit code: $exit_code)"
                    exit 1
                fi
            fi
        else
            print_colored_v2 "DEBUG" "Skip to delete symlink, because it is not a symlink: $symlink"
        fi
    done
}
