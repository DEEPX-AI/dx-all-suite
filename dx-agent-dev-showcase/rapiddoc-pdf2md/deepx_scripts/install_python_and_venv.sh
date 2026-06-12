#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")

# color env settings
source "${SCRIPT_DIR}/color_env.sh"
source "${SCRIPT_DIR}/common_util.sh"

# Global variables for script configuration
DEFAULT_MIN_PY_VERSION="3.8.10"

# ---
## Usage Information
# ---
usage() {
    echo -e "Usage: ${COLOR_CYAN}$0 [OPTIONS]${COLOR_RESET}"
    echo -e "Install a specified Python version and optionally set up a virtual environment."
    echo -e ""
    echo -e "${COLOR_BOLD}Options:${COLOR_RESET}"
    echo -e "  ${COLOR_GREEN}--python_version=<VERSION>${COLOR_RESET}  Specify the Python version to install (e.g., 3.10.4)."
    echo -e "                                Default Minimum supported version: ${DEFAULT_MIN_PY_VERSION}."
    echo -e "                                If not specified:"
    echo -e "                                  - For Ubuntu 20.04+, the OS default Python 3 will be used."
    echo -e "                                  - For Ubuntu 18.04, Python ${DEFAULT_MIN_PY_VERSION} "
    echo -e "                                    (or the value specified by the '--min_py_version' option) will be source-built."
    echo -e ""
    echo -e "  ${COLOR_GREEN}--min_py_version=<VERSION>${COLOR_RESET}  Specify the minimum Python version. (default: ${DEFAULT_MIN_PY_VERSION})"
    echo -e ""
    echo -e "  ${COLOR_GREEN}--venv_path=<PATH>${COLOR_RESET}          Specify the path for the virtual environment."
    echo -e "                                  - If this option is omitted, no virtual environment will be created."
    echo -e ""
    echo -e "  ${COLOR_GREEN}--symlink_target_path=<PATH>${COLOR_RESET} Specify the actual path where the virtual environment will be created."
    echo -e "                                  - If specified, a symbolic link will be created at --venv_path pointing to this path."
    echo -e "                                  - Only works when --venv_path is also specified."
    echo -e ""
    echo -e "  ${COLOR_GREEN}--system-site-packages${COLOR_RESET}      Set venv '--system-site-packages' option."    
    echo -e "                                  - This option is applied only when venv is created. If you use '-venv-reuse', it is ignored. "
    echo -e ""
    echo -e "  ${COLOR_GREEN}-f | --venv-force-remove${COLOR_RESET}    If specified, force remove existing virtual environment at --venv_path before creation."
    echo -e "  ${COLOR_GREEN}-r | --venv-reuse${COLOR_RESET}           If specified, reuse existing virtual environment at --venv_path if it's valid, skipping creation."
    echo -e ""
    echo -e "  ${COLOR_GREEN}--help${COLOR_RESET}                      Display this help message and exit."
    echo -e ""
    echo -e "${COLOR_BOLD}Examples:${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 # Installs default Python, but no venv${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --python_version=3.10.4 --venv_path=./my_venv${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --python_version=3.9.18  # Installs Python, but no venv${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --venv_path=./my_venv # Installs default Python, creates venv${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --venv_path=./existing_venv --venv-reuse # Reuse existing venv${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --venv_path=./old_venv --venv-force-remove # Force remove and recreate venv${COLOR_RESET}"
    echo -e "  ${COLOR_YELLOW}$0 --venv_path=./my_venv --symlink_target_path=/tmp/actual_venv # Create venv at /tmp/actual_venv with symlink at ./my_venv${COLOR_RESET}"
    echo -e ""
    exit 0
}

# ---
## Check if Python version is already installed and usable, or if a higher suitable version exists.
# Returns 0 if installed and usable, 1 otherwise.
# Outputs the executable path to stdout if found and usable.
# Logs to stderr.
# Arguments:
#   $1: OS_ID - The operating system ID (ubuntu, debian, etc.)
#   $2: OS_VERSION - Current OS release version (e.g., "20.04" for Ubuntu, "12" for Debian)
#   $3: REQUESTED_PY_VERSION (optional) - The specific Python version requested (e.g., "3.8.2").
#                                         If empty, means OS default/MIN_PY_VERSION is implied.
#   $4: MIN_REQUIRED_PY_VERSION - The absolute minimum Python version required by the script.
# ---
is_python_installed() {
    local OS_ID="${1}"
    local OS_VERSION="${2}"
    local REQUESTED_PY_VERSION="${3}"
    local MIN_REQUIRED_PY_VERSION="${4}"
    local PYTHON_EXECUTABLES=("python3.12" "python3.11" "python3.10" "python3.9" "python3.8" "python3") # Order matters: higher to lower

    local REQ_VER_NUM=0
    if [ -n "${REQUESTED_PY_VERSION}" ]; then
        REQ_VER_NUM=$(printf "%02d%02d%02d" $(echo "${REQUESTED_PY_VERSION}" | tr '.' ' '))
    fi
    local MIN_REQ_VER_NUM=$(printf "%02d%02d%02d" $(echo "${MIN_REQUIRED_PY_VERSION}" | tr '.' ' '))

    echo -e "${TAG_INFO} Checking for existing Python installations that meet requirements..." >&2

    for cmd in "${PYTHON_EXECUTABLES[@]}"; do
        local check_path="/usr/bin/${cmd}" # Default apt path
        local source_path="/usr/local/bin/${cmd}" # Default source path

        local current_exec=""
        local current_version_full=""
        local current_version_num=0

        # Check standard paths and PATH
        if [ -x "${check_path}" ]; then
            current_exec="${check_path}"
            current_version_full=$("${current_exec}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "unknown")
        elif command -v "${cmd}" &>/dev/null; then
            current_exec=$(command -v "${cmd}")
            current_version_full=$("${current_exec}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "unknown")
        fi

        # If not found via apt-like paths or command, try source-built path explicitly
        if [ -z "${current_exec}" ] && [ -x "${source_path}" ]; then
            current_exec="${source_path}"
            current_version_full=$("${current_exec}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "unknown")
        fi

        if [ -n "${current_exec}" ] && [ "${current_version_full}" != "unknown" ]; then
            current_version_num=$(printf "%02d%02d%02d" $(echo "${current_version_full}" | tr '.' ' '))
            echo -e "${TAG_INFO} Detected Python ${current_version_full} at ${current_exec}." >&2

            # Check if detected version meets the minimum script requirement
            if [ "${current_version_num}" -ge "${MIN_REQ_VER_NUM}" ]; then
                # If a specific version was requested (--python_version), check if the detected one is suitable.
                # Suitable means:
                # 1. Detected version's major.minor matches requested major.minor AND detected version >= requested version (e.g., 3.8.10 for 3.8.2)
                # 2. Or, if requested version is empty (meaning "any suitable"), then this detected higher version is fine.
                # (disabled condition) 3. Or, if requested version is explicitly provided, and detected is a higher major.minor version.
                
                local current_major_minor=$(echo "${current_version_full}" | cut -d. -f1,2)
                local requested_major_minor=$(echo "${REQUESTED_PY_VERSION}" | cut -d. -f1,2)

                if [ -z "${REQUESTED_PY_VERSION}" ]; then # No specific version requested, any valid is fine
                    echo -e "${TAG_INFO} Python ${current_version_full} is suitable as no specific version was requested. Using this version." >&2
                    echo "${current_exec}" # Output the usable executable path
                    return 0
                elif [ "${current_major_minor}" = "${requested_major_minor}" ] && [ "${current_version_num}" -ge "${REQ_VER_NUM}" ]; then
                    echo -e "${TAG_INFO} Python ${current_version_full} matches requested major.minor and is compatible (>= requested ${REQUESTED_PY_VERSION}). Using this version." >&2
                    echo "${current_exec}" # Output the usable executable path
                    return 0
                # (disabled condition)
                # elif [ "${current_version_num}" -ge "${REQ_VER_NUM}" ]; then # Detected version is higher than requested, even if major.minor differs
                #     echo -e "${TAG_INFO} Python ${current_version_full} is a higher version than requested (${REQUESTED_PY_VERSION}) and meets minimums. Using this version." >&2
                #     echo "${current_exec}" # Output the usable executable path
                #     return 0
                fi
            else
                echo -e "${TAG_WARN} Python ${current_version_full} found, but it is below the minimum required version (${MIN_REQUIRED_PY_VERSION})." >&2
            fi
        fi
    done

    echo -e "${TAG_INFO} No suitable Python installation found on the system." >&2
    return 1 # No suitable Python found
}

# ---
## Add deadsnakes PPA safely with prerequisite checks (Ubuntu only)
# Returns 0 on success, 1 on failure
# ---
add_deadsnakes_ppa_if_needed() {
    local OS_ID="${1}"
    
    # Only for Ubuntu
    if [ "$OS_ID" != "ubuntu" ]; then
        return 0
    fi
    
    # Check if PPA is already added
    if grep -q "^deb.*deadsnakes" /etc/apt/sources.list /etc/apt/sources.list.d/* 2>/dev/null; then
        echo -e "${TAG_INFO} deadsnakes PPA already added. Skipping." >&2
        return 0
    fi
    
    echo -e "${TAG_INFO} Adding deadsnakes PPA for Ubuntu..." >&2
    
    # Install prerequisites
    if ! dpkg -s software-properties-common >/dev/null 2>&1; then
        if ! sudo apt-get install -y software-properties-common 2>&1 | tee -a /tmp/ppa_setup.log >&2; then
            echo -e "${TAG_WARN} Failed to install software-properties-common" >&2
            return 1
        fi
    fi
    
    # Install GPG tools and CA certificates
    if ! sudo apt-get install -y gnupg gpg-agent ca-certificates 2>&1 | tee -a /tmp/ppa_setup.log >&2; then
        echo -e "${TAG_WARN} Failed to install GPG tools or CA certificates" >&2
        return 1
    fi
    
    # Add PPA
    if ! sudo add-apt-repository -y ppa:deadsnakes/ppa 2>&1 | tee /tmp/ppa_add.log >&2; then
        echo -e "${TAG_WARN} Failed to add deadsnakes PPA" >&2
        return 1
    fi
    
    # Update apt cache
    if ! sudo apt-get update 2>&1 | tee /tmp/apt_update.log >&2; then
        echo -e "${TAG_WARN} apt-get update failed after adding PPA" >&2
        return 1
    fi
    
    echo -e "${TAG_INFO} deadsnakes PPA added successfully" >&2
    sudo rm -f /tmp/ppa_add.log /tmp/apt_update.log /tmp/ppa_setup.log
    return 0
}

# ---
## Check if Python packages are available via apt
# Returns 0 if available, 1 otherwise
# ---
check_python_apt_availability() {
    local PY_MAJOR_MINOR="${1}"
    
    echo -e "${TAG_INFO} Checking if python${PY_MAJOR_MINOR} packages are available via apt..." >&2
    
    # Check if the main package and dev/venv packages are available
    local MAIN_PKG=$(apt-cache search "^python${PY_MAJOR_MINOR}$" 2>/dev/null | grep -c "^python${PY_MAJOR_MINOR} ")
    local DEV_PKG=$(apt-cache search "^python${PY_MAJOR_MINOR}-dev$" 2>/dev/null | grep -c "^python${PY_MAJOR_MINOR}-dev ")
    local VENV_PKG=$(apt-cache search "^python${PY_MAJOR_MINOR}-venv$" 2>/dev/null | grep -c "^python${PY_MAJOR_MINOR}-venv ")
    
    if [ "$MAIN_PKG" -gt 0 ] && [ "$DEV_PKG" -gt 0 ] && [ "$VENV_PKG" -gt 0 ]; then
        echo -e "${TAG_INFO} python${PY_MAJOR_MINOR} packages are available via apt" >&2
        return 0
    else
        echo -e "${TAG_INFO} python${PY_MAJOR_MINOR} packages are NOT available via apt (main:$MAIN_PKG, dev:$DEV_PKG, venv:$VENV_PKG)" >&2
        return 1
    fi
}

# ---
## Install Python via apt
# Returns 0 on success, 1 on failure
# ---
install_python_via_apt() {
    local PY_MAJOR_MINOR="${1}"
    
    echo -e "${TAG_INFO} Installing python${PY_MAJOR_MINOR} via apt..." >&2
    
    # Check if already installed
    if command -v "python${PY_MAJOR_MINOR}" &>/dev/null && \
       dpkg -s "python${PY_MAJOR_MINOR}-dev" >/dev/null 2>&1 && \
       dpkg -s "python${PY_MAJOR_MINOR}-venv" >/dev/null 2>&1; then
        echo -e "${TAG_SKIP} python${PY_MAJOR_MINOR} and dependencies are already installed" >&2
        return 0
    fi
    
    # Install packages
    if sudo apt-get install -y python${PY_MAJOR_MINOR} python${PY_MAJOR_MINOR}-dev python${PY_MAJOR_MINOR}-venv 2>&1 | tee /tmp/apt_install.log >&2; then
        # Verify installation
        if command -v "python${PY_MAJOR_MINOR}" &>/dev/null; then
            echo -e "${TAG_INFO} python${PY_MAJOR_MINOR} installed successfully via apt" >&2
            sudo rm -f /tmp/apt_install.log
            return 0
        else
            echo -e "${TAG_WARN} apt install completed but python${PY_MAJOR_MINOR} command not found" >&2
            return 1
        fi
    else
        echo -e "${TAG_WARN} apt installation failed for python${PY_MAJOR_MINOR}" >&2
        return 1
    fi
}

# ---
## Install Python via source build
# Returns 0 on success, 1 on failure
# ---
install_python_via_source() {
    local TARGET_INSTALL_PY_VERSION="${1}"
    local PY_MAJOR_MINOR="${2}"
    
    echo -e "${TAG_INFO} Installing python ${TARGET_INSTALL_PY_VERSION} via source build..." >&2
    
    # Install build dependencies
    if ! sudo apt-get update; then
        echo -e "${TAG_ERROR} Failed to update apt repositories for source build" >&2
        return 1
    fi
    
    if ! sudo apt-get install -y --no-install-recommends \
        build-essential \
        wget \
        curl \
        ca-certificates \
        libssl-dev \
        zlib1g-dev \
        libncurses5-dev \
        libncursesw5-dev \
        libreadline-dev \
        libsqlite3-dev \
        libgdbm-dev \
        libdb5.3-dev \
        libbz2-dev \
        libexpat1-dev \
        liblzma-dev \
        tk-dev \
        libffi-dev \
        uuid-dev 2>&1 | tee /tmp/build_deps.log >&2; then
        echo -e "${TAG_ERROR} Failed to install build dependencies" >&2
        return 1
    fi
    
    # Build Python from source
    local BUILD_DIR="/tmp/python_build_$$"
    mkdir -p "${BUILD_DIR}"
    
    if ! (cd "${BUILD_DIR}" && \
        wget --no-check-certificate "https://www.python.org/ftp/python/${TARGET_INSTALL_PY_VERSION}/Python-${TARGET_INSTALL_PY_VERSION}.tgz" && \
        tar xzf "Python-${TARGET_INSTALL_PY_VERSION}.tgz" && \
        cd "Python-${TARGET_INSTALL_PY_VERSION}" && \
        ./configure --enable-optimizations && \
        make -j$(nproc) && \
        sudo make altinstall) 2>&1 | tee /tmp/source_build.log >&2; then
        echo -e "${TAG_ERROR} Source build failed for Python ${TARGET_INSTALL_PY_VERSION}" >&2
        sudo rm -rf "${BUILD_DIR}"
        return 1
    fi
    
    sudo rm -rf "${BUILD_DIR}"
    
    # Verify installation
    if command -v "python${PY_MAJOR_MINOR}" &>/dev/null; then
        local INSTALLED_VERSION=$("python${PY_MAJOR_MINOR}" --version 2>&1 | awk '{print $2}')
        echo -e "${TAG_INFO} Python ${INSTALLED_VERSION} installed successfully via source build" >&2
        sudo rm -f /tmp/source_build.log /tmp/build_deps.log
        return 0
    else
        echo -e "${TAG_ERROR} Source build completed but python${PY_MAJOR_MINOR} command not found" >&2
        return 1
    fi
}

# ---
## Install generic python3 dev/venv packages as fallback
# Returns 0 on success, 1 on failure
# ---
install_generic_python3_dev_venv() {
    echo -e "${TAG_INFO} Installing generic python3 dev/venv packages as fallback..." >&2
    if sudo apt-get install -y python3-dev python3-venv 2>&1 | tee /tmp/apt_install_devvenv_fallback.log >&2; then
        echo -e "${TAG_INFO} Successfully installed generic python3 dev/venv packages" >&2
        sudo rm -f /tmp/apt_install_devvenv_fallback.log
        return 0
    else
        echo -e "${TAG_ERROR} Failed to install generic python3 dev/venv packages" >&2
        sudo rm -f /tmp/apt_install_devvenv_fallback.log
        return 1
    fi
}

# ---
## Ensure dev and venv packages are installed for a given Python version
# Returns 0 on success, 1 on failure
# Arguments:
#   $1: PYTHON_EXEC - Python executable path (e.g., python3.10, /usr/bin/python3.11)
#   $2: OS_ID - The operating system ID (ubuntu, debian, etc.)
# ---
ensure_python_dev_venv_packages() {
    local PYTHON_EXEC="${1}"
    local OS_ID="${2}"
    
    # Only for Ubuntu/Debian with apt-based Python
    if [ "$OS_ID" != "ubuntu" ] && [ "$OS_ID" != "debian" ]; then
        return 0
    fi
    
    # Extract version from Python executable
    local PYTHON_VERSION_FOR_PKG=$(echo "${PYTHON_EXEC}" | sed -n 's/.*python\([0-9]\.[0-9]\+\).*/\1/p')
    
    # If it's a standard python command without version, try to get version
    if [ -z "${PYTHON_VERSION_FOR_PKG}" ]; then
        PYTHON_VERSION_FOR_PKG=$("${PYTHON_EXEC}" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "")
    fi
    
    if [ -z "${PYTHON_VERSION_FOR_PKG}" ]; then
        echo -e "${TAG_WARN} Could not determine Python version for dev/venv package check" >&2
        return 0
    fi
    
    # Step 1: Always install generic python3-dev and python3-venv first (base requirement)
    echo -e "${TAG_INFO} Installing generic python3-dev and python3-venv packages..." >&2
    install_generic_python3_dev_venv || {
        echo -e "${TAG_WARN} Failed to install generic python3 dev/venv packages" >&2
        return 1
    }
    
    # Step 2: Check if version-specific packages are needed
    local NEED_VERSION_SPECIFIC=0
    if ! dpkg -s "python${PYTHON_VERSION_FOR_PKG}-dev" >/dev/null 2>&1; then
        echo -e "${TAG_INFO} python${PYTHON_VERSION_FOR_PKG}-dev is not installed" >&2
        NEED_VERSION_SPECIFIC=1
    fi
    if ! dpkg -s "python${PYTHON_VERSION_FOR_PKG}-venv" >/dev/null 2>&1; then
        echo -e "${TAG_INFO} python${PYTHON_VERSION_FOR_PKG}-venv is not installed" >&2
        NEED_VERSION_SPECIFIC=1
    fi
    
    # Step 3: Install version-specific packages if available
    if [ $NEED_VERSION_SPECIFIC -eq 1 ]; then
        echo -e "${TAG_INFO} Attempting to install version-specific dev/venv packages for python${PYTHON_VERSION_FOR_PKG}..." >&2
        
        # Update apt and add PPA if needed
        sudo apt-get update >/dev/null 2>&1
        
        if [ "$OS_ID" = "ubuntu" ]; then
            add_deadsnakes_ppa_if_needed "$OS_ID"
        fi
        
        # Try to install version-specific packages
        if check_python_apt_availability "$PYTHON_VERSION_FOR_PKG"; then
            if sudo apt-get install -y python${PYTHON_VERSION_FOR_PKG}-dev python${PYTHON_VERSION_FOR_PKG}-venv 2>&1 | tee /tmp/apt_install_devvenv.log >&2; then
                echo -e "${TAG_INFO} Successfully installed python${PYTHON_VERSION_FOR_PKG} dev/venv packages" >&2
                sudo rm -f /tmp/apt_install_devvenv.log
            else
                echo -e "${TAG_WARN} Failed to install python${PYTHON_VERSION_FOR_PKG} dev/venv packages, but generic packages are already installed" >&2
            fi
        else
            echo -e "${TAG_INFO} python${PYTHON_VERSION_FOR_PKG} dev/venv packages not available via apt, using generic packages" >&2
        fi
    else
        echo -e "${TAG_SKIP} python${PYTHON_VERSION_FOR_PKG}-dev and python${PYTHON_VERSION_FOR_PKG}-venv are already installed" >&2
    fi
    
    return 0
}

# ---
## Install Python and its dependencies (dev, venv)
# ---
# Arguments:
#   $1: TARGET_INSTALL_PY_VERSION (optional) - The specific Python version to install.
#         If empty, the OS default Python 3 version will be installed for Ubuntu 20.04+ and Debian 11+.
#         For Ubuntu 18.04, MIN_PY_VERSION will be used if TARGET_INSTALL_PY_VERSION is empty.
#   $2: OS_ID - The operating system ID (ubuntu, debian, etc.)
#   $3: OS_VERSION - The current OS release version (e.g., "20.04" for Ubuntu, "12" for Debian)
#   $4: MIN_PY_VERSION - The minimum Python version required
install_python_and_dependencies() {
    local TARGET_INSTALL_PY_VERSION="${1}"
    local OS_ID="${2}"
    local OS_VERSION="${3}"
    local MIN_PY_VERSION="${4}"

    # Temporarily disable 'set -e' for controlled error handling and 'set -x' for cleaner output capture
    local OPT_E_STATE="$-"
    local OPT_X_STATE="$-"
    case "${OPT_E_STATE}" in *e*) set +e;; esac
    case "${OPT_X_STATE}" in *x*) set +x;; esac

    exec 3>&1 # Save stdout to fd 3
    exec >&2  # Redirect stdout to stderr

    echo -e "${TAG_INFO} Starting Python installation/dependency checks for ${TARGET_INSTALL_PY_VERSION:-default} on ${OS_ID} ${OS_VERSION}..."

    # Store the originally requested version for is_python_installed check
    local REQUESTED_PY_VERSION_FOR_CHECK="${TARGET_INSTALL_PY_VERSION}"
    
    # If no specific version is requested, compare system Python with MIN_PY_VERSION
    if [ -z "${TARGET_INSTALL_PY_VERSION}" ]; then
        echo -e "${TAG_INFO} No specific version requested, checking system Python version..."
        SYSTEM_PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")' 2>/dev/null || echo "0.0.0")
        echo -e "${TAG_INFO} System Python version: ${SYSTEM_PY_VERSION}"
        echo -e "${TAG_INFO} Minimum required version: ${MIN_PY_VERSION}"
        SYSTEM_VER_NUM=$(printf "%02d%02d%02d" $(echo "${SYSTEM_PY_VERSION}" | tr '.' ' '))
        MIN_VER_NUM=$(printf "%02d%02d%02d" $(echo "${MIN_PY_VERSION}" | tr '.' ' '))
        if [ "${SYSTEM_VER_NUM}" -ge "${MIN_VER_NUM}" ]; then
            echo -e "${TAG_INFO} System Python (${SYSTEM_PY_VERSION}) meets minimum requirement. Using system Python."
            TARGET_INSTALL_PY_VERSION="${SYSTEM_PY_VERSION}"
        else
            echo -e "${TAG_INFO} System Python (${SYSTEM_PY_VERSION}) is below minimum requirement. Will install ${MIN_PY_VERSION}."
            TARGET_INSTALL_PY_VERSION="${MIN_PY_VERSION}"
        fi
    fi

    local DX_PYTHON_EXEC_OUT="" # This will hold the command to execute the installed python
    local INSTALL_STATUS=0
    local PY_MAJOR_MINOR=""

    if [ -n "${TARGET_INSTALL_PY_VERSION}" ]; then
        PY_MAJOR_MINOR=$(echo "${TARGET_INSTALL_PY_VERSION}" | cut -d. -f1,2)
    fi

    # Check if Python is already installed OR if a higher suitable version exists
    # Pass empty string if no specific version was originally requested, so any version >= MIN_PY_VERSION is accepted
    local IS_INSTALLED_RESULT
    IS_INSTALLED_RESULT=$(is_python_installed "${OS_ID}" "${OS_VERSION}" "${REQUESTED_PY_VERSION_FOR_CHECK}" "${MIN_PY_VERSION}")
    
    if [ -n "${IS_INSTALLED_RESULT}" ]; then
        DX_PYTHON_EXEC_OUT="${IS_INSTALLED_RESULT}"
        echo -e "${TAG_SKIP} A suitable Python installation is already present (${DX_PYTHON_EXEC_OUT})."
        
        # Ensure dev/venv packages are installed
        ensure_python_dev_venv_packages "${DX_PYTHON_EXEC_OUT}" "${OS_ID}"
    else
        echo -e "${TAG_INFO} No suitable Python installation found. Proceeding with installation..."
        
        # Unified installation process for all supported OS versions
        if { [ "$OS_ID" = "ubuntu" ] && { [ "$OS_VERSION" = "24.04" ] || [ "$OS_VERSION" = "22.04" ] || [ "$OS_VERSION" = "20.04" ] || [ "$OS_VERSION" = "18.04" ]; }; } || \
           { [ "$OS_ID" = "debian" ] && { [ "$OS_VERSION" = "12" ] || [ "$OS_VERSION" = "11" ]; }; }; then
            
            # Step 1: Update apt cache
            echo -e "${TAG_INFO} Updating apt repositories..." >&2
            if ! sudo apt-get update 2>&1 | tee /tmp/apt_update_initial.log >&2; then
                echo -e "${TAG_WARN} Initial apt-get update had warnings/errors, continuing..." >&2
            fi
            
            # Step 2: Add deadsnakes PPA if Ubuntu
            if [ "$OS_ID" = "ubuntu" ]; then
                add_deadsnakes_ppa_if_needed "$OS_ID"
                # PPA failure is not critical, we'll try apt anyway and fall back to source build
            fi
            
            # Step 3: Check if Python packages are available via apt
            if check_python_apt_availability "$PY_MAJOR_MINOR"; then
                # Step 4: Try apt installation
                if install_python_via_apt "$PY_MAJOR_MINOR"; then
                    DX_PYTHON_EXEC_OUT="python${PY_MAJOR_MINOR}"
                    echo -e "${TAG_INFO} Successfully installed python${PY_MAJOR_MINOR} via apt" >&2
                else
                    echo -e "${TAG_WARN} apt installation failed, will try source build..." >&2
                fi
            else
                echo -e "${TAG_INFO} Python${PY_MAJOR_MINOR} not available via apt, will try source build..." >&2
            fi
            
            # Step 5: If apt installation failed or not available, try source build
            if [ -z "${DX_PYTHON_EXEC_OUT}" ]; then
                if install_python_via_source "$TARGET_INSTALL_PY_VERSION" "$PY_MAJOR_MINOR"; then
                    DX_PYTHON_EXEC_OUT="python${PY_MAJOR_MINOR}"
                    echo -e "${TAG_INFO} Successfully installed python${PY_MAJOR_MINOR} via source build" >&2
                else
                    echo -e "${TAG_ERROR} Both apt and source build failed for python${PY_MAJOR_MINOR}" >&2
                    INSTALL_STATUS=1
                fi
            fi
            
            # Step 6: Ensure dev/venv packages are installed after successful Python installation
            if [ -n "${DX_PYTHON_EXEC_OUT}" ]; then
                ensure_python_dev_venv_packages "${DX_PYTHON_EXEC_OUT}" "${OS_ID}"
            fi
        else
            print_colored "Unsupported OS version: $OS_ID $OS_VERSION" "ERROR"
            INSTALL_STATUS=1
        fi
    fi

    if [ ${INSTALL_STATUS} -eq 0 ] && [ -n "${DX_PYTHON_EXEC_OUT}" ]; then
        echo -e "${TAG_INFO} Python installation/dependency checks done. Resolved Python executable: ${DX_PYTHON_EXEC_OUT}"
        echo "${DX_PYTHON_EXEC_OUT}" >&3 # Output the python executable path to original stdout (fd 3)
    else
        echo "" >&3 # Output empty string on failure
        INSTALL_STATUS=1
    fi

    # Restore original stdout and stderr
    exec 1>&3- # Restore stdout from fd 3 and close fd 3

    # Restore 'set -e' and 'set -x' if they were enabled originally
    case "${OPT_E_STATE}" in *e*) set -e;; esac
    case "${OPT_X_STATE}" in *x*) set -x;; esac

    return ${INSTALL_STATUS}
}

# ---
## Check Virtual Environment Validity
# Returns 0 if valid, 1 otherwise.
# Arguments:
#   $1: VENV_PATH_TO_CHECK - The path to the virtual environment.
# ---
function check_venv_validity() {
    local VENV_PATH_TO_CHECK="${1}"
    echo -e "${TAG_INFO} Checking virtual environment validity at ${VENV_PATH_TO_CHECK}..." >&2

    if [ ! -d "${VENV_PATH_TO_CHECK}" ]; then
        echo -e "${TAG_WARN} Venv path ${VENV_PATH_TO_CHECK} does not exist." >&2
        return 1
    fi

    if [ ! -f "${VENV_PATH_TO_CHECK}/bin/activate" ]; then
        echo -e "${TAG_WARN} Venv activate script not found: ${VENV_PATH_TO_CHECK}/bin/activate." >&2
        return 1
    fi

    if [ ! -x "${VENV_PATH_TO_CHECK}/bin/python" ]; then
        echo -e "${TAG_WARN} Venv python executable not found or not executable: ${VENV_PATH_TO_CHECK}/bin/python." >&2
        return 1
    fi

    # Test if the python executable works
    if ! "${VENV_PATH_TO_CHECK}/bin/python" -c "import sys; print('Python in venv is working!')" >/dev/null 2>&1; then
        echo -e "${TAG_WARN} Python executable in venv (${VENV_PATH_TO_CHECK}/bin/python) is not functional." >&2
        return 1
    fi

    echo -e "${TAG_SUCC} Virtual environment at ${VENV_PATH_TO_CHECK} appears to be valid." >&2
    return 0
}


# ---
## Setup Virtual Environment
# ---
# Arguments:
#   $1: DX_PYTHON_EXEC - The command to execute the installed Python (e.g., python3.10).
#   $2: VENV_PATH - The desired path for the virtual environment.
#   $3: SKIP_VENV_CREATION_FLAG - 'y' to skip venv creation, 'n' otherwise.
#   $4: VENV_MAKE_ARGS
#   $5: VENV_SYMLINK_TARGET_PATH - Optional path where the actual venv will be created (if set, VENV_PATH becomes a symlink)
setup_venv() {
    local DX_PYTHON_EXEC="${1}"
    local VENV_PATH="${2}"
    local SKIP_VENV_CREATION_FLAG="${3}"
    local VENV_MAKE_ARGS="${4}"
    local VENV_SYMLINK_TARGET_PATH="${5}"

    # Temporarily disable 'set -x' for cleaner output during venv setup steps
    local OPT_X_STATE="$-"
    case "${OPT_X_STATE}" in *x*) set +x;; esac

    if [ -z "${DX_PYTHON_EXEC}" ]; then
        print_colored "Python executable not provided to setup_venv." "ERROR" >&2
        return 1
    fi
    if [ -z "${VENV_PATH}" ]; then
        print_colored "Virtual environment path not provided to setup_venv." "ERROR" >&2
        return 1
    fi

    # Determine actual venv creation path
    local VENV_ORIGIN_DIR="${VENV_PATH}"
    
    # Convert relative path to absolute path
    if [[ "${VENV_ORIGIN_DIR}" != /* ]]; then
        VENV_ORIGIN_DIR="$(pwd)/${VENV_ORIGIN_DIR}"
    fi
    
    if [ -n "${VENV_SYMLINK_TARGET_PATH}" ]; then
        VENV_ORIGIN_DIR="${VENV_SYMLINK_TARGET_PATH}"
        echo -e "${TAG_INFO} Creating python venv to symlink target path: ${VENV_ORIGIN_DIR}"
    else
        echo -e "${TAG_INFO} Creating python venv to this path: ${VENV_ORIGIN_DIR}"
    fi

    if [ "${SKIP_VENV_CREATION_FLAG}" != "y" ]; then
        echo -e "${TAG_INFO} Setting up Virtual Environment at ${VENV_ORIGIN_DIR} using ${DX_PYTHON_EXEC}..."
        if ! "${DX_PYTHON_EXEC}" -m venv "${VENV_ORIGIN_DIR}" ${VENV_MAKE_ARGS}; then
            print_colored "Failed to create virtual environment at ${VENV_ORIGIN_DIR}." >&2
            case "${OPT_X_STATE}" in *x*) set -x;; esac # Restore set -x before returning
            return 1
        fi
    else
        echo -e "${TAG_INFO} Skipping virtual environment creation as --venv-reuse was specified and venv is valid."
    fi

    # Create symbolic link if needed
    if [ -n "${VENV_SYMLINK_TARGET_PATH}" ]; then
        echo -e "${TAG_INFO} Creating symbolic link from ${VENV_PATH} to ${VENV_ORIGIN_DIR}..."
        
        # Remove any existing symlink or directory at VENV_PATH
        if [ -e "${VENV_PATH}" ]; then
            sudo rm -rf "${VENV_PATH}"
        fi
        
        # Ensure the parent directory exists
        mkdir -p "$(dirname "${VENV_PATH}")"
        
        # Create the symbolic link using absolute path
        local VENV_SYMLINK_TARGET_REAL_PATH
        VENV_SYMLINK_TARGET_REAL_PATH=$(readlink -f "${VENV_ORIGIN_DIR}")
        if ! ln -s "${VENV_SYMLINK_TARGET_REAL_PATH}" "${VENV_PATH}"; then
            print_colored "Failed to create symbolic link: ${VENV_PATH} -> ${VENV_SYMLINK_TARGET_REAL_PATH}" "ERROR" >&2
            case "${OPT_X_STATE}" in *x*) set -x;; esac # Restore set -x before returning
            return 1
        fi
        echo -e "${TAG_INFO} Created symbolic link: ${VENV_PATH} -> ${VENV_SYMLINK_TARGET_REAL_PATH}"
    fi

    # Activate the venv temporarily for pip operations
    echo -e "${TAG_INFO} Activating virtual environment for package upgrades..."
    if ! source "${VENV_PATH}/bin/activate"; then # Use 'source' or '.' here
        print_colored "Failed to activate virtual environment." >&2
        case "${OPT_X_STATE}" in *x*) set -x;; esac # Restore set -x before returning
        return 1
    fi

    echo -e "${TAG_INFO} Upgrading pip, wheel, and setuptools..."
    
    # Get OS information
    local OS_ID=""
    local OS_VERSION=""
    
    if [ -f /etc/os-release ]; then
        OS_ID=$(grep "^ID=" /etc/os-release | sed 's/^ID=//' | tr -d '"')
    fi
    OS_VERSION=$(lsb_release -rs)
    
    echo -e "${TAG_INFO} *** OS: ${OS_ID} ${OS_VERSION} ***"

    local PIP_INSTALL_STATUS=0
    
    # For Ubuntu 24.04 - only upgrade setuptools
    if [ "$OS_ID" = "ubuntu" ] && [ "$OS_VERSION" = "24.04" ]; then
      if ! pip install --upgrade setuptools; then PIP_INSTALL_STATUS=1; fi
    # For Ubuntu 22.04, 20.04, 18.04 and Debian 11 - upgrade pip, wheel, setuptools
    elif { [ "$OS_ID" = "ubuntu" ] && { [ "$OS_VERSION" = "22.04" ] || [ "$OS_VERSION" = "20.04" ] || [ "$OS_VERSION" = "18.04" ]; }; } || \
         { [ "$OS_ID" = "debian" ] && { [ "$OS_VERSION" = "11" ] || [ "$OS_VERSION" = "12" ]; }; }; then
      if ! pip install --upgrade pip wheel setuptools; then PIP_INSTALL_STATUS=1; fi
    else
      echo -e "${TAG_WARN} Unsupported OS version for specific pip upgrade rules: ${OS_ID} ${OS_VERSION}" >&2
      if ! pip install --upgrade pip wheel setuptools; then PIP_INSTALL_STATUS=1; fi # Fallback to general upgrade
    fi

    if [ ${PIP_INSTALL_STATUS} -ne 0 ]; then
        echo -e "${TAG_WARN} Pip/wheel/setuptools upgrade failed. Proceeding..." >&2
    fi

    echo -e "${TAG_INFO} Virtual environment setup complete."
    # Deactivate the venv so the script doesn't leave the current shell in the venv
    deactivate || true

    # Restore 'set -x' if it was enabled originally
    case "${OPT_X_STATE}" in *x*) set -x;; esac
    return 0
}

# ---
## Main Function
# ---
main() {
    local PYTHON_VERSION=""
    local MIN_PY_VERSION=$DEFAULT_MIN_PY_VERSION
    local VENV_PATH="" # Initialize as empty string
    local VENV_SYMLINK_TARGET_PATH=""
    local FORCE_REMOVE_VENV="n"
    local REUSE_VENV="n"
    local VENV_SYSTEM_SITE_PACKAGES_ARGS=""
    local SKIP_VENV_CREATION="n" # Flag to control venv creation in setup_venv

    # Get OS information using lsb_release (supports both Ubuntu and Debian)
    local OS_ID=""
    local OS_VERSION=""
    
    # Extract OS ID from /etc/os-release
    if [ -f /etc/os-release ]; then
        OS_ID=$(grep "^ID=" /etc/os-release | sed 's/^ID=//' | tr -d '"')
    fi
    
    # Get OS version using lsb_release
    OS_VERSION=$(lsb_release -rs)
    
    echo -e "${TAG_INFO} Detected OS: ${OS_ID} ${OS_VERSION}"

    # Parse command-line arguments
    for i in "$@"; do
        case $i in
            --python_version=*)
                PYTHON_VERSION="${i#*=}"
                ;;
            --min_py_version=*)
                MIN_PY_VERSION="${i#*=}"
                ;;
            --venv_path=*)
                VENV_PATH="${i#*=}"
                ;;
            --symlink_target_path=*)
                VENV_SYMLINK_TARGET_PATH="${i#*=}"
                ;;
            -f|--venv-force-remove)
                FORCE_REMOVE_VENV="y"
                ;;
            -r|--venv-reuse)
                REUSE_VENV="y"
                ;;
            --system-site-packages)
                VENV_SYSTEM_SITE_PACKAGES_ARGS="--system-site-packages"
                ;;
            --help)
                usage
                ;;
            *)
                print_colored "Unknown option: $i" "ERROR" >&2
                usage
                ;;
        esac
    done

    # Validate PYTHON_VERSION against MIN_PY_VERSION if specified
    # Also handles the case where PYTHON_VERSION is empty, implying MIN_PY_VERSION as the effective target for checks.
    local EFFECTIVE_TARGET_PY_VERSION="${PYTHON_VERSION:-${MIN_PY_VERSION}}"
    local REQ_VER_NUM=$(printf "%02d%02d%02d" $(echo "${EFFECTIVE_TARGET_PY_VERSION}" | tr '.' ' '))
    local MIN_VER_NUM=$(printf "%02d%02d%02d" $(echo "${MIN_PY_VERSION}" | tr '.' ' '))

    if [ "${REQ_VER_NUM}" -lt "${MIN_VER_NUM}" ]; then
        print_colored "Requested Python version (${PYTHON_VERSION:-default}) is lower than the minimum required version (${MIN_PY_VERSION}). Aborting." "ERROR" >&2
        exit 1
    fi

    # Validate symlink_target_path requires venv_path
    if [ -n "${VENV_SYMLINK_TARGET_PATH}" ] && [ -z "${VENV_PATH}" ]; then
        print_colored "--symlink_target_path can only be used when --venv_path is also specified." "ERROR" >&2
        exit 1
    fi

    # Handle --venv-force-remove and --venv-reuse conflicts
    if [ "${FORCE_REMOVE_VENV}" = "y" ] && [ "${REUSE_VENV}" = "y" ]; then
        print_colored "Cannot use both --venv-force-remove and --venv-reuse simultaneously. Please choose one." "ERROR" >&2
        exit 1
    fi

    # Check if venv_path exists and handle based on options
    if [ -n "$VENV_PATH" ]; then # Only proceed if VENV_PATH was provided
        # Also check symlink target path if specified
        local CHECK_PATHS=("${VENV_PATH}")
        if [ -n "${VENV_SYMLINK_TARGET_PATH}" ]; then
            CHECK_PATHS+=("${VENV_SYMLINK_TARGET_PATH}")
        fi
        
        for CHECK_PATH in "${CHECK_PATHS[@]}"; do
            if [ -e "$CHECK_PATH" ]; then # Path exists
                if [ "${FORCE_REMOVE_VENV}" = "y" ]; then
                    echo -e "${TAG_INFO} --venv-force-remove specified. Removing existing path at ${CHECK_PATH}..." >&2
                    if ! sudo rm -rf "${CHECK_PATH}"; then
                        print_colored "Failed to remove existing path at ${CHECK_PATH}. Aborting." "ERROR" >&2
                        exit 1
                    fi
                elif [ "${REUSE_VENV}" = "y" ]; then
                    # For reuse, only check the final venv path (VENV_PATH), not the symlink target
                    if [ "${CHECK_PATH}" = "${VENV_PATH}" ]; then
                        if check_venv_validity "${VENV_PATH}"; then
                            echo -e "${TAG_INFO} --venv-reuse specified and existing virtual environment is valid. Skipping venv creation." >&2
                            SKIP_VENV_CREATION="y"
                        else
                            echo -e "${TAG_WARN} --venv-reuse specified, but existing virtual environment at ${VENV_PATH} is invalid. Attempting to recreate it." >&2
                            # Remove both paths if invalid
                            for REMOVE_PATH in "${CHECK_PATHS[@]}"; do
                                if [ -e "${REMOVE_PATH}" ]; then
                                    if ! sudo rm -rf "${REMOVE_PATH}"; then
                                        print_colored "Failed to remove invalid path at ${REMOVE_PATH}. Aborting." "ERROR" >&2
                                        exit 1
                                    fi
                                fi
                            done
                        fi
                    fi
                else
                    print_colored "Path already exists: ${CHECK_PATH}. Please remove it or choose a different path, or use --venv-force-remove to force recreation, or --venv-reuse to reuse it." "HINT" >&2
                    exit 1
                fi
            fi
        done
    fi

    echo -e "${TAG_INFO} Starting Python installation and environment setup..."
    echo -e "${TAG_INFO} Requested Python Version: ${PYTHON_VERSION:-OS Default/Min (${MIN_PY_VERSION})}"

    # Call install_python_and_dependencies and capture its output (the python executable path)
    local INSTALLED_PYTHON_EXEC
    INSTALLED_PYTHON_EXEC=$(install_python_and_dependencies "${PYTHON_VERSION}" "${OS_ID}" "${OS_VERSION}" "${MIN_PY_VERSION}")
    local INSTALL_PY_STATUS=$? # Capture the exit status of install_python_and_dependencies

    if [ ${INSTALL_PY_STATUS} -ne 0 ]; then
        print_colored "Python and Virtual environment setup failed. Exiting." "ERROR" >&2
        exit 1
    fi

    # Ensure INSTALLED_PYTHON_EXEC is not empty (it would be if installation failed or was skipped due to an error)
    if [ -z "${INSTALLED_PYTHON_EXEC}" ]; then
        print_colored "Could not determine installed Python executable or Python installation failed. Exiting." "ERROR" >&2
        exit 1
    fi

    # Conditionally call setup_venv based on VENV_PATH
    if [ -n "${VENV_PATH}" ]; then
        echo -e "${TAG_INFO} Virtual Environment Path: ${VENV_PATH}"

        setup_venv "${INSTALLED_PYTHON_EXEC}" "${VENV_PATH}" "${SKIP_VENV_CREATION}" "${VENV_SYSTEM_SITE_PACKAGES_ARGS}" "${VENV_SYMLINK_TARGET_PATH}"
        if [ $? -ne 0 ]; then
            print_colored "Virtual environment setup failed. Exiting." "ERROR" >&2
            exit 1
        fi
        echo -e "${TAG_SUCC} Script execution completed successfully."
        if [ -n "${VENV_SYMLINK_TARGET_PATH}" ]; then
            echo -e "${TAG_INFO} Virtual environment created at: ${VENV_SYMLINK_TARGET_PATH}"
            echo -e "${TAG_INFO} Symbolic link created at: ${VENV_PATH}"
        fi
        echo -e "${TAG_INFO} To activate the virtual environment, run:"
        echo -e "${COLOR_BRIGHT_YELLOW_ON_BLACK}  source ${VENV_PATH}/bin/activate ${COLOR_RESET}"
    else
        echo -e "${TAG_INFO} No --venv_path specified. Skipping virtual environment creation."
        echo -e "${TAG_SUCC} Script execution completed successfully (Python installed)."
    fi
}

# Call the main function with all script arguments
main "$@"
