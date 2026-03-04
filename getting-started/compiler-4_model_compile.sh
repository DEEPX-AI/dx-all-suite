#!/bin/bash
# =============================================================================
# [Getting Started] Compile Sample Models
#
# This script delegates model compilation to
# dx-compiler/example/3-compile_sample_models.sh
# and creates a symlink so that getting-started/dxnn points to the
# compiled output in dx-compiler/example/output/.
#
# This design allows dx-compiler to be used both:
#   - As part of dx-all-suite (via this getting-started wrapper)
#   - Standalone after cloning the dx-compiler repository alone
# =============================================================================

SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")
COMPILER_EXAMPLE_DIR="${DX_AS_PATH}/dx-compiler/example"

# color env settings
source "${DX_AS_PATH}/scripts/color_env.sh"
source "${DX_AS_PATH}/scripts/common_util.sh"

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo "COMPILER_EXAMPLE_DIR($COMPILER_EXAMPLE_DIR)"
echo -e "============================"

# Parse --force-install argument and pass it through
PASSTHROUGH_ARGS=""
for arg in "$@"; do
    case "$arg" in
        --force-install) PASSTHROUGH_ARGS="--force-install" ;;
        --help) PASSTHROUGH_ARGS="--help" ;;
    esac
done

# -----------------------------------------------------------------------------
# [Step 1] Delegate to dx-compiler/example/3-compile_sample_models.sh
# -----------------------------------------------------------------------------
echo -e "=== Delegating to dx-compiler/example/3-compile_sample_models.sh ${TAG_START} ==="
"${COMPILER_EXAMPLE_DIR}/3-compile_sample_models.sh" ${PASSTHROUGH_ARGS}
if [ $? -ne 0 ]; then
    echo -e "${TAG_ERROR} Model compilation failed!"
    exit 1
fi
echo -e "=== Delegating to dx-compiler/example/3-compile_sample_models.sh ${TAG_DONE} ==="

# -----------------------------------------------------------------------------
# [Step 2] Create symlink: getting-started/dxnn -> dx-compiler/example/output
#
#   Creates/updates the getting-started/dxnn symlink so that compiled .dxnn
#   files are accessible at the conventional getting-started path.
# -----------------------------------------------------------------------------
DXNN_SYMLINK="${SCRIPT_DIR}/dxnn"
OUTPUT_REAL="${DX_AS_PATH}/dx-compiler/dx_com/output"

if [ -L "${DXNN_SYMLINK}" ]; then
    rm "${DXNN_SYMLINK}"
elif [ -e "${DXNN_SYMLINK}" ]; then
    echo -e "${TAG_ERROR} ${DXNN_SYMLINK} exists as a non-symlink. Remove it manually."
    exit 1
fi

ln -s "${OUTPUT_REAL}" "${DXNN_SYMLINK}"
if [ $? -ne 0 ]; then
    echo -e "${TAG_ERROR} Failed to create symlink: ${DXNN_SYMLINK} -> ${OUTPUT_REAL}"
    exit 1
fi
echo "Created symlink: ${DXNN_SYMLINK} -> ${OUTPUT_REAL}"

exit 0