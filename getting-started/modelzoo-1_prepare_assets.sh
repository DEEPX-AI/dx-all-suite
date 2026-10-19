#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
DX_AS_PATH=$(realpath -s "${SCRIPT_DIR}/..")
MODELZOO_PATH="${DX_AS_PATH}/dx-modelzoo"
WORKSPACE_LINK="${SCRIPT_DIR}/modelzoo"

# color env settings
source "${DX_AS_PATH}/scripts/color_env.sh"

show_help() {
    cat << EOF2
Usage: $(basename "$0") [OPTIONS]

Prepare the DX-ModelZoo workspace used by 'modelzoo-2_run_first_npu_model.sh'.

OPTIONS:
  --source PATH     DX-ModelZoo source directory (default: <dx-all-suite>/dx-modelzoo)
  -h, --help        Display this help message and exit

DESCRIPTION:
  Creates 'getting-started/modelzoo' (models/, datasets/, result/) as a symbolic link:
    - host mode      : <dx-all-suite>/workspace/modelzoo
    - container mode : \${DOCKER_VOLUME_PATH}/modelzoo
  Also copies 'dx-modelzoo/.env.example' to 'dx-modelzoo/.env' if '.env' does not exist.
EOF2
}

is_container() {
    [ "${DX_CONTAINER_MODE}" = "true" ] && return 0
    [ "${DX_CONTAINER_MODE}" = "false" ] && return 1
    grep -qE "/docker|/lxc|/containerd" /proc/1/cgroup 2>/dev/null || [ -f /.dockerenv ]
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --source) MODELZOO_PATH="${2:?--source requires a path}"; shift ;;
        -h|--help|help) show_help; exit 0 ;;
        *) echo -e "${TAG_ERROR} Unknown option: $1"; show_help; exit 1 ;;
    esac
    shift
done

if is_container; then
    echo "(container mode detected)"
    if [ -z "${DOCKER_VOLUME_PATH}" ]; then
        echo -e "${TAG_ERROR} DOCKER_VOLUME_PATH must be set in container mode."
        exit 1
    fi
    SYMLINK_TARGET_PATH="${DOCKER_VOLUME_PATH}/modelzoo"
else
    echo "(host mode detected)"
    SYMLINK_TARGET_PATH="${DX_AS_PATH}/workspace/modelzoo"
fi

echo -e "======== PATH INFO ========="
echo "DX_AS_PATH($DX_AS_PATH)"
echo "MODELZOO_PATH($MODELZOO_PATH)"
echo "WORKSPACE_LINK($WORKSPACE_LINK) -> ($SYMLINK_TARGET_PATH)"
echo -e "============================"

echo -e "=== Setup ModelZoo workspace ${TAG_START} ==="
mkdir -p "${SYMLINK_TARGET_PATH}/models" "${SYMLINK_TARGET_PATH}/datasets" "${SYMLINK_TARGET_PATH}/result" || {
    echo -e "${TAG_ERROR} Failed to create '${SYMLINK_TARGET_PATH}'"
    exit 1
}
if [ -L "${WORKSPACE_LINK}" ] && [ "$(readlink -f "${WORKSPACE_LINK}")" != "$(readlink -f "${SYMLINK_TARGET_PATH}")" ]; then
    rm "${WORKSPACE_LINK}"
fi
if [ -e "${WORKSPACE_LINK}" ] && [ ! -L "${WORKSPACE_LINK}" ]; then
    echo -e "${TAG_ERROR} ${WORKSPACE_LINK} exists as a non-symlink. Remove it manually."
    exit 1
fi
if [ ! -L "${WORKSPACE_LINK}" ]; then
    ln -s "${SYMLINK_TARGET_PATH}" "${WORKSPACE_LINK}" || { echo -e "${TAG_ERROR} Failed to create symlink"; exit 1; }
    echo "Created symlink: ${WORKSPACE_LINK} -> ${SYMLINK_TARGET_PATH}"
fi
echo -e "=== Setup ModelZoo workspace ${TAG_DONE} ==="

echo -e "=== Setup DX-ModelZoo .env ${TAG_START} ==="
if [ -f "${MODELZOO_PATH}/.env" ]; then
    echo -e "${TAG_INFO} Keeping existing '${MODELZOO_PATH}/.env'"
elif [ -f "${MODELZOO_PATH}/.env.example" ]; then
    cp "${MODELZOO_PATH}/.env.example" "${MODELZOO_PATH}/.env"
    echo -e "${TAG_INFO} Created '${MODELZOO_PATH}/.env'. Edit DXMZ_MODEL_URL if your network uses a mirror."
else
    echo -e "${TAG_WARN} '${MODELZOO_PATH}/.env.example' not found. Skipping .env setup."
fi
echo -e "=== Setup DX-ModelZoo .env ${TAG_DONE} ==="

echo -e "${TAG_INFO} Place evaluation datasets under '${WORKSPACE_LINK}/datasets' (e.g. ILSVRC2012/val for resnet50_224x224)."
exit 0
