#!/bin/sh
SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)
DX_AS_PATH=$(cd "${SCRIPT_DIR}/../"; pwd)

printf "SCRIPT_DIR(%b)\n" "${SCRIPT_DIR}"
printf "DX_AS_PATH(%b)\n" "${DX_AS_PATH}"

# color env settings
. "${DX_AS_PATH}/scripts/color_env.sh"

OLD_DIR=$(pwd)
cd "${SCRIPT_DIR}"

modelzoo_clean() {
    find "${SCRIPT_DIR}"/* -depth ! -name "modelzoo-*.sh" -delete
    if [ $? -ne 0 ]; then
        printf "%b Failed to remove 'getting-started' artifacts\n" "${TAG_ERROR}"
        exit 1
    fi

    printf "=== remove 'getting-started' artifacts %b ===\n" "${TAG_DONE}"
}

main() {
    if [ "${DX_CONTAINER_MODE}" = "true" ] || { [ "${DX_CONTAINER_MODE}" != "false" ] && { grep -qE "/docker|/lxc|/containerd" /proc/1/cgroup 2>/dev/null || [ -f /.dockerenv ]; }; }; then
        printf "(container mode detected)\n"
        modelzoo_clean
    else
        printf "(host mode detected)\n"
        printf "%b Please use 'modelzoo-clean.sh' only inside the Docker container.%b\n" "${TAG_WARN} ${COLOR_BRIGHT_YELLOW_ON_BLACK}" "${COLOR_RESET}"
    fi
}

main

cd "${OLD_DIR}"

exit 0
