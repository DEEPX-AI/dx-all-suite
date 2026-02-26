#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

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
    DXCOM_PATH="${DX_AS_PATH}/dx-compiler/venv-dx-compiler-local/bin/dxcom"
    if [ -f "${DXCOM_PATH}" ]; then
        echo -e "${TAG_INFO} Checking existing dxcom installation..."
        if "${DXCOM_PATH}" -v &>/dev/null; then
            echo -e "${TAG_INFO} dxcom is already installed and working:"
            "${DXCOM_PATH}" -v
            echo -e "${TAG_DONE} Skipping dx-compiler installation"
            exit 0
        else
            echo -e "${TAG_INFO} Existing dxcom installation found but not working. Proceeding with installation..."
        fi
    else
        echo -e "${TAG_INFO} dxcom not found. Proceeding with installation..."
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
