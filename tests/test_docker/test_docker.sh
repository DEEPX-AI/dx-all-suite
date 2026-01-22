#!/bin/bash
#
# Quick Test Docker Command Wrapper
#
# This script provides convenient shortcuts for common test scenarios.
#
# Usage:
#   ./test_docker.sh <command> [additional_args...]
#
# Commands:
#   sanity          - Run only sanity checks (quick validation)
#   all             - Run all tests
#   runtime         - Run only dx-runtime tests
#   modelzoo        - Run only dx-modelzoo tests
#   compiler        - Run only dx-compiler tests
#   ubuntu          - Run tests for Ubuntu images only
#   debian          - Run tests for Debian images only
#   ubuntu-24.04    - Run tests for Ubuntu 24.04 only
#   ubuntu-22.04    - Run tests for Ubuntu 22.04 only
#   ubuntu-20.04    - Run tests for Ubuntu 20.04 only
#   ubuntu-18.04    - Run tests for Ubuntu 18.04 only
#   debian-12       - Run tests for Debian 12 only
#   debian-13       - Run tests for Debian 13 only
#   runtime-ubuntu-24.04    - Run dx-runtime tests for Ubuntu 24.04
#   runtime-ubuntu-22.04    - Run dx-runtime tests for Ubuntu 22.04
#   runtime-ubuntu-20.04    - Run dx-runtime tests for Ubuntu 20.04
#   runtime-ubuntu-18.04    - Run dx-runtime tests for Ubuntu 18.04
#   runtime-debian-12       - Run dx-runtime tests for Debian 12
#   runtime-debian-13       - Run dx-runtime tests for Debian 13
#   modelzoo-ubuntu-24.04   - Run dx-modelzoo tests for Ubuntu 24.04
#   modelzoo-ubuntu-22.04   - Run dx-modelzoo tests for Ubuntu 22.04
#   modelzoo-ubuntu-20.04   - Run dx-modelzoo tests for Ubuntu 20.04
#   modelzoo-ubuntu-18.04   - Run dx-modelzoo tests for Ubuntu 18.04
#   modelzoo-debian-12      - Run dx-modelzoo tests for Debian 12
#   modelzoo-debian-13      - Run dx-modelzoo tests for Debian 13
#   compiler-ubuntu-24.04   - Run dx-compiler tests for Ubuntu 24.04
#   compiler-ubuntu-22.04   - Run dx-compiler tests for Ubuntu 22.04
#   compiler-ubuntu-20.04   - Run dx-compiler tests for Ubuntu 20.04
#   list            - List all available tests
#   report          - Run all tests and generate HTML report
#   json            - Run all tests and generate JSON report
#   help            - Show this help message
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNNER_SCRIPT="${SCRIPT_DIR}/docker_build_tests.sh"

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Report generation flag
GENERATE_REPORT=0
REPORT_ARGS=""
SHOW_CAPTURE=0
CAPTURE_ARGS=""

print_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@"
}

print_usage() {
    echo -e "${YELLOW}Quick Test Docker Command Wrapper${NC}"
    echo -e ""
    echo -e "Usage: ./test_docker.sh [OPTIONS] <command> [additional_args...]"
    echo -e ""
    echo -e "Options:"
    echo -e "  ${GREEN}--report${NC}        - Generate HTML report for test results"
    echo -e "  ${GREEN}--show-capture${NC}  - Show captured stdout/stderr output during test execution"
    echo -e ""
    echo -e "Common Commands:"
    echo -e "  ${GREEN}sanity${NC}          - Run only sanity checks (quick validation)"
    echo -e "  ${GREEN}all${NC}             - Run all tests"
    echo -e ""
    echo -e "Target-Specific Commands:"
    echo -e "  ${GREEN}runtime${NC}         - Run only dx-runtime tests"
    echo -e "  ${GREEN}modelzoo${NC}        - Run only dx-modelzoo tests"
    echo -e "  ${GREEN}compiler${NC}        - Run only dx-compiler tests"
    echo -e ""
    echo -e "OS-Specific Commands:"
    echo -e "  ${GREEN}ubuntu${NC}          - Run tests for Ubuntu images only"
    echo -e "  ${GREEN}debian${NC}          - Run tests for Debian images only"
    echo -e "  ${GREEN}ubuntu-24.04${NC}    - Run tests for Ubuntu 24.04 only"
    echo -e "  ${GREEN}ubuntu-22.04${NC}    - Run tests for Ubuntu 22.04 only"
    echo -e "  ${GREEN}ubuntu-20.04${NC}    - Run tests for Ubuntu 20.04 only"
    echo -e "  ${GREEN}ubuntu-18.04${NC}    - Run tests for Ubuntu 18.04 only"
    echo -e "  ${GREEN}debian-12${NC}       - Run tests for Debian 12 only"
    echo -e "  ${GREEN}debian-13${NC}       - Run tests for Debian 12 only"
    echo -e ""
    echo -e "Target + OS Specific Commands:"
    echo -e "  ${GREEN}runtime-ubuntu-24.04${NC}    - Run dx-runtime tests for Ubuntu 24.04"
    echo -e "  ${GREEN}runtime-ubuntu-22.04${NC}    - Run dx-runtime tests for Ubuntu 22.04"
    echo -e "  ${GREEN}runtime-ubuntu-20.04${NC}    - Run dx-runtime tests for Ubuntu 20.04"
    echo -e "  ${GREEN}runtime-ubuntu-18.04${NC}    - Run dx-runtime tests for Ubuntu 18.04"
    echo -e "  ${GREEN}runtime-debian-12${NC}       - Run dx-runtime tests for Debian 12"
    echo -e "  ${GREEN}runtime-debian-13${NC}       - Run dx-runtime tests for Debian 12"
    echo -e "  ${GREEN}modelzoo-ubuntu-24.04${NC}   - Run dx-modelzoo tests for Ubuntu 24.04"
    echo -e "  ${GREEN}modelzoo-ubuntu-22.04${NC}   - Run dx-modelzoo tests for Ubuntu 22.04"
    echo -e "  ${GREEN}modelzoo-ubuntu-20.04${NC}   - Run dx-modelzoo tests for Ubuntu 20.04"
    echo -e "  ${GREEN}modelzoo-ubuntu-18.04${NC}   - Run dx-modelzoo tests for Ubuntu 18.04"
    echo -e "  ${GREEN}modelzoo-debian-12${NC}      - Run dx-modelzoo tests for Debian 12"
    echo -e "  ${GREEN}modelzoo-debian-13${NC}      - Run dx-modelzoo tests for Debian 12"
    echo -e "  ${GREEN}compiler-ubuntu-24.04${NC}   - Run dx-compiler tests for Ubuntu 24.04"
    echo -e "  ${GREEN}compiler-ubuntu-22.04${NC}   - Run dx-compiler tests for Ubuntu 22.04"
    echo -e "  ${GREEN}compiler-ubuntu-20.04${NC}   - Run dx-compiler tests for Ubuntu 20.04"
    echo -e ""
    echo -e "Utility Commands:"
    echo -e "  ${GREEN}list${NC}            - List all available tests"
    echo -e "  ${GREEN}report${NC}          - Run all tests and generate HTML report"
    echo -e "  ${GREEN}json${NC}            - Run all tests and generate JSON report"
    echo -e "  ${GREEN}help${NC}            - Show this help message"
    echo -e ""
    echo -e "Examples:"
    echo -e "  ./test_docker.sh sanity"
    echo -e "  ./test_docker.sh runtime -v -s"
    echo -e "  ./test_docker.sh ubuntu-24.04"
    echo -e "  ./test_docker.sh runtime-ubuntu-18.04"
    echo -e "  ./test_docker.sh compiler-ubuntu-24.04"
    echo -e "  ./test_docker.sh --report sanity"
    echo -e "  ./test_docker.sh --show-capture runtime"
    echo -e "  ./test_docker.sh --report --show-capture compiler -vv"
    echo -e "  ./test_docker.sh report"
}

if [ $# -eq 0 ] || [ "$1" == "help" ] || [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    print_usage
    exit 0
fi

# Parse option before processing command
while [[ $# -gt 0 ]]; do
    case "$1" in
        --report)
            GENERATE_REPORT=1
            shift
            ;;
        --show-capture)
            SHOW_CAPTURE=1
            CAPTURE_ARGS="-s --capture=no"
            shift
            ;;
        *)
            break
            ;;
    esac
done

# Setup report if requested
if [ $GENERATE_REPORT -eq 1 ]; then
    REPORT_DIR="${SCRIPT_DIR}/reports"
    mkdir -p "${REPORT_DIR}"
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    REPORT_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.html"
    REPORT_ARGS="--html=${REPORT_FILE} --self-contained-html"
fi

COMMAND=$1
shift

case "$COMMAND" in
    sanity)
        print_info "Running sanity checks only..."
        "${RUNNER_SCRIPT}" -m sanity ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    all)
        print_info "Running all tests..."
        "${RUNNER_SCRIPT}" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    runtime)
        print_info "Running dx-runtime tests only..."
        "${RUNNER_SCRIPT}" -k "runtime" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    modelzoo)
        print_info "Running dx-modelzoo tests only..."
        "${RUNNER_SCRIPT}" -k "modelzoo" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    compiler)
        print_info "Running dx-compiler tests only..."
        "${RUNNER_SCRIPT}" -k "compiler" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    ubuntu)
        print_info "Running tests for Ubuntu images only..."
        "${RUNNER_SCRIPT}" -k "ubuntu" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    debian)
        print_info "Running tests for Debian images only..."
        "${RUNNER_SCRIPT}" -k "debian" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    ubuntu-24.04)
        print_info "Running tests for Ubuntu 24.04 only..."
        "${RUNNER_SCRIPT}" -k "ubuntu and 24.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    ubuntu-22.04)
        print_info "Running tests for Ubuntu 22.04 only..."
        "${RUNNER_SCRIPT}" -k "ubuntu and 22.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    ubuntu-20.04)
        print_info "Running tests for Ubuntu 20.04 only..."
        "${RUNNER_SCRIPT}" -k "ubuntu and 20.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    ubuntu-18.04)
        print_info "Running tests for Ubuntu 18.04 only..."
        "${RUNNER_SCRIPT}" -k "ubuntu and 18.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    debian-12)
        print_info "Running tests for Debian 12 only..."
        "${RUNNER_SCRIPT}" -k "debian and 12" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    debian-13)
        print_info "Running tests for Debian 13 only..."
        "${RUNNER_SCRIPT}" -k "debian and 13" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    runtime-ubuntu-24.04)
        print_info "Running dx-runtime tests for Ubuntu 24.04 only..."
        "${RUNNER_SCRIPT}" -k "runtime and ubuntu and 24.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    runtime-ubuntu-22.04)
        print_info "Running dx-runtime tests for Ubuntu 22.04 only..."
        "${RUNNER_SCRIPT}" -k "runtime and ubuntu and 22.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    runtime-ubuntu-20.04)
        print_info "Running dx-runtime tests for Ubuntu 20.04 only..."
        "${RUNNER_SCRIPT}" -k "runtime and ubuntu and 20.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    runtime-ubuntu-18.04)
        print_info "Running dx-runtime tests for Ubuntu 18.04 only..."
        "${RUNNER_SCRIPT}" -k "runtime and ubuntu and 18.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    runtime-debian-12)
        print_info "Running dx-runtime tests for Debian 12 only..."
        "${RUNNER_SCRIPT}" -k "runtime and debian and 12" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    runtime-debian-13)
        print_info "Running dx-runtime tests for Debian 13 only..."
        "${RUNNER_SCRIPT}" -k "runtime and debian and 13" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    modelzoo-ubuntu-24.04)
        print_info "Running dx-modelzoo tests for Ubuntu 24.04 only..."
        "${RUNNER_SCRIPT}" -k "modelzoo and ubuntu and 24.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    modelzoo-ubuntu-22.04)
        print_info "Running dx-modelzoo tests for Ubuntu 22.04 only..."
        "${RUNNER_SCRIPT}" -k "modelzoo and ubuntu and 22.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    modelzoo-ubuntu-20.04)
        print_info "Running dx-modelzoo tests for Ubuntu 20.04 only..."
        "${RUNNER_SCRIPT}" -k "modelzoo and ubuntu and 20.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    modelzoo-ubuntu-18.04)
        print_info "Running dx-modelzoo tests for Ubuntu 18.04 only..."
        "${RUNNER_SCRIPT}" -k "modelzoo and ubuntu and 18.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    modelzoo-debian-12)
        print_info "Running dx-modelzoo tests for Debian 12 only..."
        "${RUNNER_SCRIPT}" -k "modelzoo and debian and 12" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    modelzoo-debian-13)
        print_info "Running dx-modelzoo tests for Debian 13 only..."
        "${RUNNER_SCRIPT}" -k "modelzoo and debian and 13" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    compiler-ubuntu-24.04)
        print_info "Running dx-compiler tests for Ubuntu 24.04 only..."
        "${RUNNER_SCRIPT}" -k "compiler and ubuntu and 24.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    compiler-ubuntu-22.04)
        print_info "Running dx-compiler tests for Ubuntu 22.04 only..."
        "${RUNNER_SCRIPT}" -k "compiler and ubuntu and 22.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    compiler-ubuntu-20.04)
        print_info "Running dx-compiler tests for Ubuntu 20.04 only..."
        "${RUNNER_SCRIPT}" -k "compiler and ubuntu and 20.04" ${CAPTURE_ARGS} ${REPORT_ARGS} "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    list)
        print_info "Listing all available tests..."
        exec "${RUNNER_SCRIPT}" --collect-only "$@"
        ;;
    
    report)
        print_info "Running all tests with HTML report generation..."
        REPORT_DIR="${SCRIPT_DIR}/reports"
        mkdir -p "${REPORT_DIR}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        REPORT_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.html"
        
        "${RUNNER_SCRIPT}" -v --html="${REPORT_FILE}" --self-contained-html "$@"
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    json)
        print_info "Running all tests with JSON report generation..."
        REPORT_DIR="${SCRIPT_DIR}/reports"
        mkdir -p "${REPORT_DIR}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        JSON_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.json"
        
        "${RUNNER_SCRIPT}" -v --json-report --json-report-file="${JSON_FILE}" "$@"
        EXIT_CODE=$?
        
        if [ $EXIT_CODE -eq 0 ]; then
            print_success "JSON report generated: ${JSON_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    *)
        echo -e "Unknown command: $COMMAND"
        echo -e ""
        print_usage
        exit 1
        ;;
esac
