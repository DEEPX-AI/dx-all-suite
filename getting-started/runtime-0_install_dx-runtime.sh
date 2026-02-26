#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")

# color env settings
source ${DX_AS_PATH}/scripts/color_env.sh

# Display help message
show_help() {
    cat << EOF
Usage: $(basename "$0") [OPTIONS]

Install dx-runtime component.

OPTIONS:
  --exclude-fw      Exclude firmware installation
  -f, --force       Force installation even if sanity check passes
  -h, --help        Display this help message and exit

DESCRIPTION:
  This script installs dx-runtime by executing the install.sh script in the
  dx-runtime directory. By default, it checks if dx-runtime is already installed
  and working via sanity_check.sh. If so, it skips installation. Use --force to
  override this check.

EXAMPLES:
  $(basename "$0")                    # Install dx-runtime (skip if already working)
  $(basename "$0") --exclude-fw       # Install without firmware
  $(basename "$0") --force            # Force reinstall dx-runtime
  $(basename "$0") -h                 # Show this help message

EOF
}

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo -e "============================"

# Parse command line arguments
INSTALL_ARGS="--all"
FORCE_INSTALL=false
for arg in "$@"; do
    case $arg in
        -h|--help|help)
            show_help
            exit 0
            ;;
        -f|--force)
            FORCE_INSTALL=true
            ;;
        --exclude-fw)
            INSTALL_ARGS+=" --exclude-fw"
            ;;
    esac
done

# Check if dx-runtime is already installed and working (skip if --force is used)
if [ "$FORCE_INSTALL" = false ]; then
    SANITY_CHECK_SCRIPT="${DX_AS_PATH}/dx-runtime/scripts/sanity_check.sh"
    if [ -f "${SANITY_CHECK_SCRIPT}" ]; then
        echo -e "${TAG_INFO} Checking dx-runtime installation via sanity check..."
        if "${SANITY_CHECK_SCRIPT}" &>/dev/null; then
            echo -e "${TAG_INFO} dx-runtime sanity check passed"
            echo -e "${TAG_DONE} Skipping dx-runtime installation"
            exit 0
        else
            echo -e "${TAG_INFO} dx-runtime sanity check failed. Proceeding with installation..."
        fi
    else
        echo -e "${TAG_INFO} dx-runtime sanity check script not found. Proceeding with installation..."
    fi
else
    echo -e "${TAG_INFO} Force install mode enabled. Proceeding with installation..."
fi

echo -e "=== Installing dx-runtime ${TAG_START} ==="

# Navigate to dx-runtime directory
pushd "${DX_AS_PATH}/dx-runtime" || {
    echo -e "${TAG_ERROR} Failed to navigate to dx-runtime directory"
    exit 1
}

# Execute the install script with appropriate arguments
echo "Executing ./install.sh ${INSTALL_ARGS} ..."
./install.sh ${INSTALL_ARGS}

INSTALL_EXIT_CODE=$?

popd

if [ $INSTALL_EXIT_CODE -eq 0 ]; then
    echo -e "=== Installing dx-runtime ${TAG_DONE} ==="
    exit 0
else
    echo -e "${TAG_ERROR} dx-runtime installation failed with exit code: $INSTALL_EXIT_CODE"
    exit $INSTALL_EXIT_CODE
fi
