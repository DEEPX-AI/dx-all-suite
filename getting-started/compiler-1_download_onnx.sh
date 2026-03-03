#!/bin/bash
# =============================================================================
# [Getting Started] Download Sample ONNX Models
#
# This script delegates model downloading to dx-compiler/example/1-download_sample_models.sh
# and creates a symlink so that getting-started/sample_models points to the
# downloaded models in dx-compiler/example/sample_models/.
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
# [Step 1] Delegate to dx-compiler/example/1-download_sample_models.sh
# -----------------------------------------------------------------------------
echo -e "=== Delegating to dx-compiler/example/1-download_sample_models.sh ${TAG_START} ==="
"${COMPILER_EXAMPLE_DIR}/1-download_sample_models.sh" ${PASSTHROUGH_ARGS}
if [ $? -ne 0 ]; then
    echo -e "${TAG_ERROR} Model download failed!"
    exit 1
fi
echo -e "=== Delegating to dx-compiler/example/1-download_sample_models.sh ${TAG_DONE} ==="

# -----------------------------------------------------------------------------
# [Step 2] Create symlink: getting-started/sample_models -> dx-compiler/example/sample_models
#
#   Other getting-started scripts (compiler-2, compiler-4) reference
#   ${SCRIPT_DIR}/sample_models, so we create a symlink here for compatibility.
# -----------------------------------------------------------------------------
SAMPLE_MODELS_SYMLINK="${SCRIPT_DIR}/sample_models"
SAMPLE_MODELS_REAL="${DX_AS_PATH}/dx-compiler/dx_com/sample_models"

if [ -L "${SAMPLE_MODELS_SYMLINK}" ]; then
    rm "${SAMPLE_MODELS_SYMLINK}"
elif [ -e "${SAMPLE_MODELS_SYMLINK}" ]; then
    echo -e "${TAG_ERROR} ${SAMPLE_MODELS_SYMLINK} exists as a non-symlink. Remove it manually."
    exit 1
fi

ln -s "${SAMPLE_MODELS_REAL}" "${SAMPLE_MODELS_SYMLINK}"
if [ $? -ne 0 ]; then
    echo -e "${TAG_ERROR} Failed to create symlink: ${SAMPLE_MODELS_SYMLINK} -> ${SAMPLE_MODELS_REAL}"
    exit 1
fi
echo "Created symlink: ${SAMPLE_MODELS_SYMLINK} -> ${SAMPLE_MODELS_REAL}"

exit 0