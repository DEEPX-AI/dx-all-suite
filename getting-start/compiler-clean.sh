#!/bin/sh
SCRIPT_DIR=$(cd "$(dirname "$0")"; pwd)
DX_AS_PATH=$(cd "${SCRIPT_DIR}/../"; pwd)
WORKSPACE_PATH="${DX_AS_PATH}/workspace"

printf "SCRIPT_DIR(%b)\n" "${SCRIPT_DIR}"
printf "DX_AS_PATH(%b)\n" "${DX_AS_PATH}"
printf "WORKSPACE_PATH(%b)\n" "${WORKSPACE_PATH}"

# color env settings
. "${DX_AS_PATH}/scripts/color_env.sh"

OLD_DIR=$(pwd)
cd "${SCRIPT_DIR}"

compiler_clean() {
    find "${SCRIPT_DIR}"/* -depth ! -name "compiler-*.sh" -delete
    if [ $? -ne 0 ]; then
        printf "%b Failed to remove 'getting-start' artifacts\n" "${TAG_ERROR}"
        exit 1
    fi

    printf "=== remove 'getting-start' artifacts %b ===\n" "${TAG_DONE}"

    if [ -e "${WORKSPACE_PATH}/dxnn" ]; then
        rm -rf ${WORKSPACE_PATH}/dxnn/*
        if [ $? -ne 0 ]; then
            printf "%b Failed to remove 'workspace/dxnn/*.dxnn' artifacts\n" "${TAG_ERROR}"
            printf "%b Please try again with 'sudo' command\n" "${TAG_INFO}"
            exit 1
        fi
        printf "=== remove 'workspace/dxnn/*.dxnn' artifacts %b ===\n" "${TAG_DONE}"
    fi
}

main() {
    CONTAINER_MODE=false

    if grep -qE "/docker|/lxc|/containerd" /proc/1/cgroup || [ -f /.dockerenv ] || [ "${DX_CONTAINER_MODE}" = "true" ]; then
        CONTAINER_MODE=true
        printf "(container mode detected)\n"
        compiler_clean
    else
        printf "(host mode detected)\n"
        printf "%b Please use 'runtime-clean.sh' only inside the Docker container.%b\n" "${TAG_WARN} ${COLOR_BRIGHT_YELLOW_ON_BLACK}" "${COLOR_RESET}"
    fi
}

main

cd "${OLD_DIR}"

exit 0
