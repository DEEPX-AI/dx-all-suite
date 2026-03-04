#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh
source ${DX_AS_PATH}/scripts/common_util.sh

# Display help message
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Install dx-compiler component.

OPTIONS:
  -f, --force       Force installation even if dxcom is already working
  -h, --help        Display this help message and exit

DESCRIPTION:
  This script installs dx-compiler by executing the install.sh script in the
  dx-compiler directory. By default, it checks if dxcom is already installed
  and working. If so, it skips installation. Use --force to override this check.

EXAMPLES:
  $(basename "$0")              # Install dx-compiler (skip if already working)
  $(basename "$0") --force      # Force reinstall dx-compiler
  $(basename "$0") -h           # Show this help message

EOF
}

# Parse command line arguments
FORCE_INSTALL=false
for arg in "$@"; do
    case $arg in
        -h|--help|help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE_INSTALL=true
            shift
            ;;
    esac
done

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"

# Check if dxcom is already installed and working (skip if --force is used)
if [ "$FORCE_INSTALL" = false ]; then
    COMPILER_PATH="${DX_AS_PATH}/dx-compiler"
    PROJECT_NAME="dx-compiler"

    _check_dxcom_working() {
        if command -v dxcom &>/dev/null; then
            echo -e "${TAG_INFO} dxcom is already available in PATH and working:"
            dxcom -v
            return 0
        fi

        echo -e "${TAG_INFO} dxcom not found in PATH. Checking venv..."
        if check_container_mode; then
            VENV_PATH="${COMPILER_PATH}/venv-${PROJECT_NAME}"
        else
            VENV_PATH="${COMPILER_PATH}/venv-${PROJECT_NAME}-local"
        fi

        if [ -f "${VENV_PATH}/bin/activate" ]; then
            echo -e "${TAG_INFO} Activating venv: ${VENV_PATH}"
            source "${VENV_PATH}/bin/activate"
            if command -v dxcom &>/dev/null; then
                echo -e "${TAG_INFO} dxcom is available in venv and working:"
                dxcom -v
                return 0
            else
                echo -e "${TAG_INFO} dxcom found in venv but not working. Proceeding with installation..."
                return 1
            fi
        else
            echo -e "${TAG_INFO} venv not found at: ${VENV_PATH}. Proceeding with installation..."
            return 1
        fi
    }

    if _check_dxcom_working; then
        echo -e "${TAG_DONE} Skipping dx-compiler installation"
        exit 0
    fi
else
    echo -e "${TAG_INFO} Force install mode enabled. Proceeding with installation..."
fi

echo -e "=== Installing dx-compiler ${TAG_START} ==="

# Navigate to dx-compiler directory
pushd "${DX_AS_PATH}/dx-compiler" || {
    echo -e "${TAG_ERROR} Failed to navigate to dx-compiler directory"
    exit 1
}

# Execute the install script
echo "Executing ./install.sh ..."
./install.sh

INSTALL_EXIT_CODE=$?

popd

if [ $INSTALL_EXIT_CODE -eq 0 ]; then
    echo -e "=== Installing dx-compiler ${TAG_DONE} ==="
    exit 0
else
    echo -e "${TAG_ERROR} dx-compiler installation failed with exit code: $INSTALL_EXIT_CODE"
    exit $INSTALL_EXIT_CODE
fi
