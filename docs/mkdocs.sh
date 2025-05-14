#!/bin/bash

SCRIPT_DIR=$(realpath "$(dirname "$0")")
PROJECT_ROOT=$(realpath -s "${SCRIPT_DIR}/..")

# color env settings
source ${PROJECT_ROOT}/scripts/color_env.sh

pushd $SCRIPT_DIR

USE_BUILD=1
USE_SERVE=0

# Function to display help message
show_help() {
  echo "Usage: $(basename "$0") [--build] [--serve]"
  echo "Example: $0 --serve"
  echo "Options:"
  echo "  [--build]             Make PDF guide document file (default: on)"
  echo "  [--serve]             Make PDF guide document file and Serve Web site"
  echo "  [--help]              Show this help message"

  if [ "$1" == "error" ]; then
    echo "Error: Invalid or missing arguments."
    exit 1
  fi
  exit 0
}

main() {
    VERSION=$(head -n 1 ${PROJECT_ROOT}/release.ver | tr -d '\r\n')
    echo "VERSION=${VERSION}"

    export PDF_FILE_PATH=../DX-AS_${VERSION}.pdf
    echo "PDF_FILE_PATH=${PDF_FILE_PATH}"

    # Create a temporary yml from a template with the version
    envsubst < mkdocs-template.yml > mkdocs.yml

    unset PDF_FILE_PATH

    if [ $USE_SERVE -eq 1 ]; then
        # Run mkdocs build
        mkdocs serve
    else
        # Run mkdocs build
        mkdocs build
    fi

    # Clean up
    rm mkdocs.yml
}

# parse args
for i in "$@"; do
    case "$1" in
        --build)
            USE_BUILD=1
            ;;
        --serve)
            USE_SERVE=1
            ;;
        --help)
            show_help
            ;;
        *)
            echo "Unknown option: $1"
            show_help "error"
            ;;
    esac
    shift
done

main

popd

exit 0
