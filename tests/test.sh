#!/bin/bash
#
# Quick Test Command Wrapper
#
# This script provides convenient shortcuts for common test scenarios.
#
# Usage:
#   ./test.sh <command> [additional_args...]
#
# Commands:
#   sanity          - Run only sanity checks (quick validation)
#   all             - Run all tests
#   local           - Run only local installation tests
#   docker          - Run only docker installation tests
#   getting_started - Run only getting-started tests
#   list            - List all available tests
#   report          - Run all tests and generate HTML report
#   json            - Run all tests and generate JSON report
#   help            - Show this help message
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_SCRIPT="${SCRIPT_DIR}/test_local/test_local.sh"
DOCKER_SCRIPT="${SCRIPT_DIR}/test_docker/test_docker.sh"
VENV_DIR="${SCRIPT_DIR}/venv"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"

# Color codes
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Report generation flag
GENERATE_REPORT=0
REPORT_ARGS=()
SHOW_CAPTURE=0
CAPTURE_ARGS=()
K_EXPR=""
K_ARGS=()
N_WORKERS=""
N_ARGS=()
M_EXPR=""
M_ARGS=()
EXCLUDE_FW=0
DEBUG_MODE=0

print_info() {
    echo -e "${BLUE}[INFO]${NC} $@"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $@"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $@"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $@"
}

# Check if Python 3 is available
check_python() {
    if ! command -v python3 &> /dev/null; then
        print_error "python3 not found. Please install Python 3.8 or later."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_info "Found Python ${PYTHON_VERSION}"
}

# Create or activate virtual environment
setup_venv() {
    if [ -d "${VENV_DIR}" ]; then
        print_info "Virtual environment exists at ${VENV_DIR}"
    else
        print_info "Creating virtual environment at ${VENV_DIR}..."
        python3 -m venv "${VENV_DIR}"
        print_success "Virtual environment created"
    fi

    print_info "Activating virtual environment..."
    source "${VENV_DIR}/bin/activate"
    print_success "Virtual environment activated"
}

# Install/upgrade pip and required packages
install_dependencies() {
    print_info "Upgrading pip..."
    pip install --upgrade pip > /dev/null

    print_info "Installing test dependencies..."

    # Create requirements.txt if it doesn't exist
    if [ ! -f "${REQUIREMENTS_FILE}" ]; then
        cat > "${REQUIREMENTS_FILE}" << 'EOF'
# Test framework
pytest>=7.4.3
pytest-html>=4.1.1
pytest-json-report>=1.5.0

# Additional utilities
pytest-timeout>=2.2.0
pytest-xdist>=3.5.0
EOF
        print_info "Created ${REQUIREMENTS_FILE}"
    fi

    pip install -r "${REQUIREMENTS_FILE}"
    print_success "Dependencies installed"
}

print_usage() {
    echo -e "${YELLOW}Quick Test Command Wrapper${NC}"
    echo -e ""
    echo -e "Usage: ./test.sh [OPTIONS] <command> [additional_args...]"
    echo -e ""
    echo -e "Options:"
    echo -e "  ${GREEN}--report${NC}         - Generate HTML report for test results"
    echo -e "  ${GREEN}--show-capture${NC}   - Show captured stdout/stderr output during test execution"
    echo -e "  ${GREEN}--exclude-fw${NC}     - Exclude firmware installation in runtime install (getting-started tests)"
    echo -e "  ${GREEN}--debug${NC}          - Enable verbose debug output (sets DX_TEST_VERBOSE=1)"
    echo -e "  ${GREEN}-k <expr>${NC}        - Pytest keyword expression filter (e.g., \"ubuntu and 24.04\")"
    echo -e "  ${GREEN}-m <expr>${NC}        - Pytest marker expression filter (e.g., \"local and sanity\")"
    echo -e "  ${GREEN}-n <num>${NC}         - Pytest-xdist workers (e.g., 4 or auto)"
    echo -e ""
    echo -e "Common Commands:"
    echo -e "  ${GREEN}sanity${NC}          - Run only sanity checks (quick validation)"
    echo -e "  ${GREEN}all${NC}             - Run all tests"
    echo -e ""
    echo -e "Target-Specific Commands:"
    echo -e "  ${GREEN}local${NC}           - Run only local installation tests"
    echo -e "  ${GREEN}docker${NC}          - Run only docker installation tests"
    echo -e "  ${GREEN}getting_started${NC} - Run only getting-started tests"
    echo -e "  ${GREEN}getting_started_skip_install${NC} - Run getting-started tests, skipping install steps"
    echo -e ""
    echo -e "Utility Commands:"
    echo -e "  ${GREEN}list${NC}            - List all available tests"
    echo -e "  ${GREEN}report${NC}          - Run all tests and generate HTML report"
    echo -e "  ${GREEN}json${NC}            - Run all tests and generate JSON report"
    echo -e "  ${GREEN}help${NC}            - Show this help message"
    echo -e ""
    echo -e "Keyword Filters:"
    echo -e "  ${GREEN}Target keywords${NC}     - compiler | modelzoo | runtime (e.g. -k \"compiler\") "
    echo -e "  ${GREEN}OS type keywords${NC}    - ubuntu | debian (e.g. -k \"ubuntu\")"
    echo -e "  ${GREEN}OS version keywords${NC} - 24.04 | 22.04 | 20.04 | 18.04 | 12 | 13 (e.g. -k \"debian and 12\")"
    echo -e ""
    echo -e "Examples:"
    echo -e "  ./test.sh sanity"
    echo -e "  ./test.sh local"
    echo -e "  ./test.sh docker"
    echo -e "  ./test.sh getting_started"
    echo -e "  ./test.sh --report sanity"
    echo -e "  ./test.sh --show-capture runtime"
    echo -e "  ./test.sh --report --show-capture compiler -vv"
    echo -e "  ./test.sh report"
}

if [ $# -eq 0 ]; then
    print_usage
    exit 0
fi

COMMAND=""
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        help|--help|-h)
            print_usage
            exit 0
            ;;
        --report)
            GENERATE_REPORT=1
            shift
            ;;
        --show-capture)
            SHOW_CAPTURE=1
            CAPTURE_ARGS=(-s --capture=no)
            shift
            ;;
        --exclude-fw)
            EXCLUDE_FW=1
            shift
            ;;
        --debug)
            DEBUG_MODE=1
            shift
            ;;
        -k)
            if [ -z "$2" ]; then
                echo -e "Missing argument for -k"
                echo -e ""
                print_usage
                exit 1
            fi
            K_EXPR="$2"
            K_ARGS=(-k "$K_EXPR")
            shift 2
            ;;
        -m)
            if [ -z "$2" ]; then
                echo -e "Missing argument for -m"
                echo -e ""
                print_usage
                exit 1
            fi
            M_EXPR="$2"
            M_ARGS=(-m "$M_EXPR")
            shift 2
            ;;
        -n)
            if [ -z "$2" ]; then
                echo -e "Missing argument for -n"
                echo -e ""
                print_usage
                exit 1
            fi
            N_WORKERS="$2"
            N_ARGS=(-n "$N_WORKERS")
            shift 2
            ;;
        --)
            shift
            while [[ $# -gt 0 ]]; do
                EXTRA_ARGS+=("$1")
                shift
            done
            ;;
        *)
            if [ -z "${COMMAND}" ] && [[ "$1" != -* ]]; then
                COMMAND="$1"
            else
                EXTRA_ARGS+=("$1")
            fi
            shift
            ;;
    esac
done

if [ -z "${COMMAND}" ]; then
    if [ -n "${M_EXPR}" ] || [ -n "${K_EXPR}" ]; then
        COMMAND="all"
    else
        print_usage
        exit 0
    fi
fi

# Setup venv and dependencies
check_python
setup_venv
install_dependencies

# Export exclude-fw flag as environment variable
if [ $EXCLUDE_FW -eq 1 ]; then
    export DX_EXCLUDE_FW=1
fi

# Export debug mode as environment variable
if [ $DEBUG_MODE -eq 1 ]; then
    export DX_TEST_VERBOSE=1
    print_info "Debug mode enabled (DX_TEST_VERBOSE=1)"
    # Disable pytest output capturing to allow live streaming
    CAPTURE_ARGS=(-s)
fi

# Setup report if requested
if [ $GENERATE_REPORT -eq 1 ]; then
    REPORT_DIR="${SCRIPT_DIR}/reports"
    mkdir -p "${REPORT_DIR}"
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    REPORT_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.html"
    REPORT_ARGS=("--html=${REPORT_FILE}" --self-contained-html)
fi

set -- "${EXTRA_ARGS[@]}"

case "$COMMAND" in
    sanity)
        print_info "Running sanity checks only..."
        if [ -n "${M_EXPR}" ]; then
            SANITY_M_ARGS=(-m "sanity and (${M_EXPR})")
        else
            SANITY_M_ARGS=(-m sanity)
        fi
        pytest "${SANITY_M_ARGS[@]}" -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${N_ARGS[@]}" "${REPORT_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    all)
        print_info "Running all tests..."
        pytest -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" "${REPORT_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    local)
        print_info "Running local tests only..."
        pytest -m local -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" "${REPORT_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    docker)
        print_info "Running docker tests only..."
        pytest -m docker -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" "${REPORT_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    getting_started)
        print_info "Running getting-started tests only..."
        pytest -m getting_started -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" "${REPORT_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    getting_started_skip_install)
        print_info "Running getting-started tests (skipping install steps)..."
        pytest -m getting_started -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" "${REPORT_ARGS[@]}" --ignore=test_getting-started/test_compiler_0_install_dx-compiler.py --ignore=test_getting-started/test_runtime_0_install_dx-runtime.py "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;
    
    list)
        print_info "Listing all available tests..."
        pytest --collect-only "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" "$@"
        ;;
    
    report)
        print_info "Running all tests with HTML report generation..."
        REPORT_DIR="${SCRIPT_DIR}/reports"
        mkdir -p "${REPORT_DIR}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        REPORT_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.html"
        
        pytest -v "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" --html="${REPORT_FILE}" --self-contained-html "$@"
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
        
        pytest -v "${K_ARGS[@]}" "${M_ARGS[@]}" "${N_ARGS[@]}" --json-report --json-report-file="${JSON_FILE}" "$@"
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