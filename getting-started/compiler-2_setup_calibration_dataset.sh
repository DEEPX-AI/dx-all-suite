#!/bin/bash
# =============================================================================
# [Getting Started] Setup Calibration Dataset
#
# This script delegates calibration dataset downloading to
# dx-compiler/example/2-download_sample_calibration_dataset.sh
# and creates a symlink so that getting-started/calibration_dataset points to
# the dataset in dx-compiler/example/calibration_dataset/.
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

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo "COMPILER_EXAMPLE_DIR($COMPILER_EXAMPLE_DIR)"
echo -e "============================"

# Parse --force argument and pass it through
PASSTHROUGH_ARGS=""
for arg in "$@"; do
    case "$arg" in
        --force) PASSTHROUGH_ARGS="--force" ;;
        --help) PASSTHROUGH_ARGS="--help" ;;
    esac
done

# -----------------------------------------------------------------------------
# [Step 1] Delegate to dx-compiler/example/2-download_sample_calibration_dataset.sh
# -----------------------------------------------------------------------------
echo -e "=== Delegating to dx-compiler/example/2-download_sample_calibration_dataset.sh ${TAG_START} ==="
"${COMPILER_EXAMPLE_DIR}/2-download_sample_calibration_dataset.sh" ${PASSTHROUGH_ARGS}
if [ $? -ne 0 ]; then
    echo -e "${TAG_ERROR} Calibration dataset setup failed!"
    exit 1
fi
echo -e "=== Delegating to dx-compiler/example/2-download_sample_calibration_dataset.sh ${TAG_DONE} ==="

# -----------------------------------------------------------------------------
# [Step 2] Create symlink: getting-started/calibration_dataset -> dx-compiler/example/calibration_dataset
#
#   compiler-4_model_compile.sh runs dxcom from getting-started/ directory,
#   and JSON configs reference "./calibration_dataset". This symlink ensures
#   the dataset is found at that path.
# -----------------------------------------------------------------------------
CALIBRATION_SYMLINK="${SCRIPT_DIR}/calibration_dataset"
CALIBRATION_REAL="${DX_AS_PATH}/dx-compiler/dx_com/calibration_dataset"

if [ -L "${CALIBRATION_SYMLINK}" ]; then
    rm "${CALIBRATION_SYMLINK}"
elif [ -e "${CALIBRATION_SYMLINK}" ]; then
    echo -e "${TAG_ERROR} ${CALIBRATION_SYMLINK} exists as a non-symlink. Remove it manually."
    exit 1
fi

ln -s "${CALIBRATION_REAL}" "${CALIBRATION_SYMLINK}"
if [ $? -ne 0 ]; then
    echo -e "${TAG_ERROR} Failed to create symlink: ${CALIBRATION_SYMLINK} -> ${CALIBRATION_REAL}"
    exit 1
fi
echo "Created symlink: ${CALIBRATION_SYMLINK} -> ${CALIBRATION_REAL}"

exit 0