#!/bin/bash
#
# Docker Build Test Runner
# 
# This script sets up a Python virtual environment and runs pytest
# for Docker build validation tests.
#
# Usage:
#   ./docker_build_tests.sh [pytest_args...]
#
# Examples:
#   ./docker_build_tests.sh                          # Run all tests
#   ./docker_build_tests.sh -k sanity                # Run only sanity tests
#   ./docker_build_tests.sh -k "runtime and 24.04"   # Run specific tests
#   ./docker_build_tests.sh --collect-only           # List all tests
#   ./docker_build_tests.sh -v                       # Verbose output
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
TESTS_DIR="${PROJECT_ROOT}/tests"
VENV_DIR="${TESTS_DIR}/venv"
REQUIREMENTS_FILE="${TESTS_DIR}/requirements.txt"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored message
print_msg() {
    local color=$1
    shift
    echo -e "${color}$@${NC}"
}

print_info() {
    print_msg "${BLUE}" "[INFO]" "$@"
}

print_success() {
    print_msg "${GREEN}" "[SUCCESS]" "$@"
}

print_warning() {
    print_msg "${YELLOW}" "[WARNING]" "$@"
}

print_error() {
    print_msg "${RED}" "[ERROR]" "$@"
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

# Run pytest with provided arguments
run_tests() {
    print_info "Running pytest..."
    echo ""
    echo "========================================================================"
    echo "Test Command: pytest $@"
    echo "Working Directory: ${SCRIPT_DIR}"
    echo "========================================================================"
    echo ""
    
    cd "${SCRIPT_DIR}"
    
    # Run pytest with provided arguments
    pytest "$@"
    
    PYTEST_EXIT_CODE=$?
    
    echo ""
    echo "========================================================================"
    if [ $PYTEST_EXIT_CODE -eq 0 ]; then
        print_success "All tests passed!"
    else
        print_error "Some tests failed (exit code: $PYTEST_EXIT_CODE)"
    fi
    echo "========================================================================"
    
    return $PYTEST_EXIT_CODE
}

# Main execution
main() {
    print_info "Docker Build Test Runner"
    echo ""
    
    # Check prerequisites
    check_python
    
    # Setup environment
    setup_venv
    install_dependencies
    
    # Run tests with all provided arguments
    run_tests "$@"
    
    TEST_EXIT_CODE=$?
    
    # Deactivate virtual environment
    deactivate
    
    exit $TEST_EXIT_CODE
}

# Run main with all script arguments
main "$@"
