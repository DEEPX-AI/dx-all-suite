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
#   agentic-e2e-copilot-cli-autopilot  - Run agentic E2E tests via Copilot CLI (fully autonomous, CI/CD)
#   agentic-e2e-cursor-cli-autopilot   - Run agentic E2E tests via Cursor CLI (fully autonomous)
#   agentic-e2e-copilot-cli-manual    - Run agentic E2E interactively via Copilot CLI (shell-based, no pytest)
#   agentic-e2e-cursor-cli-manual      - Run agentic E2E interactively via Cursor CLI (shell-based, no pytest)
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
GENERATE_JSON=0
JSON_ARGS=()
CAPTURE_ARGS=()
COLLECT_ONLY_ARGS=()
K_EXPR=""
K_ARGS=()
M_EXPR=""
M_ARGS=()
EXCLUDE_FW=0
DEBUG_MODE=0
LIST_MODE=0
CACHE_CLEAR=0
INTERNAL_MODE=0

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
    echo -e "  ${GREEN}--html=<file>${NC}    - Generate HTML report to specific file"
    echo -e "  ${GREEN}--json-report${NC}    - Generate JSON report to timestamped file"
    echo -e "  ${GREEN}--json=<file>${NC}    - Generate JSON report to specific file"
    echo -e "  ${GREEN}--exclude-fw${NC}     - Exclude firmware installation in runtime install"
    echo -e "  ${GREEN}--debug${NC}          - Enable live stdout output (sets DX_TEST_VERBOSE=1)"
    echo -e "  ${GREEN}--list${NC}           - List tests without running them (--collect-only)"
    echo -e "  ${GREEN}--cache-clear${NC}    - Clear pytest cache before running tests"
    echo -e "  ${GREEN}--internal${NC}       - Use internal network settings (sets USE_INTRANET=true)"
    echo -e "  ${GREEN}-k <expr>${NC}        - Pytest keyword expression filter (e.g., \"ubuntu and 24.04\")"
    echo -e "  ${GREEN}-m <expr>${NC}        - Pytest marker expression filter (e.g., \"local and sanity\")"
    echo -e ""
    echo -e "Common Commands:"
    echo -e "  ${GREEN}sanity${NC}          - Run only sanity checks (quick validation)"
    echo -e "  ${GREEN}all${NC}             - Run all tests"
    echo -e ""
    echo -e "Target-Specific Commands:"
    echo -e "  ${GREEN}local_install${NC}   - Run only local installation tests"
    echo -e "  ${GREEN}docker_install${NC}  - Run only docker installation tests"
    echo -e "  ${GREEN}getting_started${NC} - Run only getting-started tests"
    echo -e "  ${GREEN}agentic-e2e-copilot-cli-autopilot${NC}  - Run agentic E2E via Copilot CLI (fully autonomous, CI/CD)"
    echo -e "  ${GREEN}agentic-e2e-cursor-cli-autopilot${NC}   - Run agentic E2E via Cursor CLI (fully autonomous)"
    echo -e "  ${GREEN}agentic-e2e-copilot-cli-manual${NC}    - Run agentic E2E interactively via Copilot CLI (shell-based)"
    echo -e "  ${GREEN}agentic-e2e-cursor-cli-manual${NC}      - Run agentic E2E interactively via Cursor CLI (shell-based)"
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
    echo -e "  ./test.sh local_install"
    echo -e "  ./test.sh docker_install"
    echo -e "  ./test.sh getting_started"
    echo -e "  ./test.sh --report sanity"
    echo -e "  ./test.sh --debug local_install"
    echo -e "  ./test.sh agentic-e2e-copilot-cli-autopilot"
    echo -e "  ./test.sh agentic-e2e-copilot-cli-manual"
    echo -e "  ./test.sh agentic-e2e-cursor-cli-manual"
    echo -e "  ./test.sh agentic-e2e-copilot-cli-autopilot -k dx_app"
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
        --json-report)
            GENERATE_JSON=1
            shift
            ;;
        --html=*)
            REPORT_FILE="${1#*=}"
            if [ -z "${REPORT_FILE}" ]; then
                echo -e "Missing filename for --html option"
                echo -e ""
                print_usage
                exit 1
            fi
            GENERATE_REPORT=1
            REPORT_ARGS=("--html=${REPORT_FILE}" --self-contained-html)
            shift
            ;;
        --json=*)
            JSON_FILE="${1#*=}"
            if [ -z "${JSON_FILE}" ]; then
                echo -e "Missing filename for --json option"
                echo -e ""
                print_usage
                exit 1
            fi
            GENERATE_JSON=1
            JSON_ARGS=(--json-report --json-report-file="${JSON_FILE}")
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
        --list)
            LIST_MODE=1
            shift
            ;;
        --cache-clear)
            CACHE_CLEAR=1
            shift
            ;;
        --internal)
            INTERNAL_MODE=1
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

# Clear pytest cache if requested
if [ $CACHE_CLEAR -eq 1 ]; then
    CACHE_DIR="${SCRIPT_DIR}/.pytest_cache"
    if [ -d "${CACHE_DIR}" ]; then
        print_info "Clearing pytest cache at ${CACHE_DIR}..."
        rm -rf "${CACHE_DIR}"
        print_success "Pytest cache cleared"
    else
        print_info "No pytest cache found to clear"
    fi
fi

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

# Enable list mode (collect only)
if [ $LIST_MODE -eq 1 ]; then
    COLLECT_ONLY_ARGS=(--collect-only)
    print_info "List mode enabled (--collect-only)"
fi

# Export internal mode environment variables for docker-compose
if [ $INTERNAL_MODE -eq 1 ]; then
    export DX_TEST_INTERNAL=1
    export USE_INTRANET="true"
    export CA_FILE_NAME="intranet_CA_SSL.crt"
    print_info "Internal mode enabled (DX_TEST_INTERNAL=1, USE_INTRANET=true, CA_FILE_NAME=intranet_CA_SSL.crt)"
fi

# Setup report if requested
if [ $GENERATE_REPORT -eq 1 ]; then
    if [ -z "${REPORT_FILE}" ]; then
        REPORT_DIR="${SCRIPT_DIR}/reports"
        mkdir -p "${REPORT_DIR}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        REPORT_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.html"
        REPORT_ARGS=("--html=${REPORT_FILE}" --self-contained-html)
    fi
fi

# Setup JSON report if requested
if [ $GENERATE_JSON -eq 1 ]; then
    if [ -z "${JSON_FILE}" ]; then
        REPORT_DIR="${SCRIPT_DIR}/reports"
        mkdir -p "${REPORT_DIR}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        JSON_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.json"
        JSON_ARGS=(--json-report --json-report-file="${JSON_FILE}")
    fi
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
        pytest "${SANITY_M_ARGS[@]}" -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    all)
        print_info "Running all tests..."
        pytest -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    local_install)
        print_info "Running local tests only..."
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "local_install and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m local_install)
        fi
        pytest -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    docker_install)
        print_info "Running docker tests only..."
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "docker_install and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m docker_install)
        fi
        pytest -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    getting_started)
        print_info "Running getting-started tests only..."
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "getting_started and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m getting_started)
        fi
        pytest -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    agentic-e2e-copilot-cli-autopilot)
        print_info "Running agentic E2E tests via Copilot CLI (autopilot, fully autonomous)..."
        if ! command -v copilot &> /dev/null; then
            print_error "Copilot CLI (copilot) not found on PATH. Install it first."
            exit 1
        fi
        export DX_AGENTIC_E2E_MODE=autopilot
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "agentic_e2e_copilot_cli_autopilot and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m agentic_e2e_copilot_cli_autopilot)
        fi
        pytest -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    agentic-e2e-cursor-cli-autopilot)
        print_info "Running agentic E2E tests via Cursor CLI (autopilot, fully autonomous)..."
        if ! command -v agent &> /dev/null; then
            print_error "Cursor CLI (agent) not found on PATH. Install it first:"
            print_error "  curl https://cursor.com/install -fsS | bash"
            exit 1
        fi
        export DX_AGENTIC_E2E_MODE=autopilot
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "agentic_e2e_cursor_cli_autopilot and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m agentic_e2e_cursor_cli_autopilot)
        fi
        pytest -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    agentic-e2e-copilot-cli-manual)
        # ---------------------------------------------------------------
        # Shell-based interactive mode — runs Copilot CLI directly (no pytest)
        # User interacts with copilot TUI, then shell validates output.
        # ---------------------------------------------------------------
        if ! command -v copilot &> /dev/null; then
            print_error "Copilot CLI (copilot) not found on PATH. Install it first."
            exit 1
        fi

        # Model and artifact settings
        AGENTIC_MODEL="${DX_AGENTIC_E2E_MODEL:-claude-sonnet-4.6}"
        KEEP_ARTIFACTS="${DX_AGENTIC_E2E_KEEP_ARTIFACTS:-0}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        # ARTIFACTS_BASE is computed per-scenario inside the loop (based on workdir)
        declare -A SCENARIO_ARTIFACTS
        GLOBAL_SUMMARY_BASE="${SCRIPT_DIR}/../dx-agentic-dev/e2e-tests/copilot_cli/manual/${TIMESTAMP}"

        # Scenario definitions (index → name, workdir, timeout, prompt)
        SCENARIO_KEYS=(compiler dx_app dx_stream runtime suite)

        declare -A SCENARIO_LABELS
        SCENARIO_LABELS[compiler]="Download yolo26n, compile to DXNN"
        SCENARIO_LABELS[dx_app]="Build yolo26n person detection app"
        SCENARIO_LABELS[dx_stream]="Build detection pipeline with tracking"
        SCENARIO_LABELS[runtime]="Route to dx_app + dx_stream via runtime builder"
        SCENARIO_LABELS[suite]="Cross-project compile + app generation"

        declare -A SCENARIO_WORKDIRS
        SCENARIO_WORKDIRS[compiler]="${SCRIPT_DIR}/../dx-compiler"
        SCENARIO_WORKDIRS[dx_app]="${SCRIPT_DIR}/../dx-runtime/dx_app"
        SCENARIO_WORKDIRS[dx_stream]="${SCRIPT_DIR}/../dx-runtime/dx_stream"
        SCENARIO_WORKDIRS[runtime]="${SCRIPT_DIR}/../dx-runtime"
        SCENARIO_WORKDIRS[suite]="${SCRIPT_DIR}/.."

        declare -A SCENARIO_TIMEOUTS
        SCENARIO_TIMEOUTS[compiler]=1200
        SCENARIO_TIMEOUTS[dx_app]=600
        SCENARIO_TIMEOUTS[dx_stream]=300
        SCENARIO_TIMEOUTS[runtime]=600
        SCENARIO_TIMEOUTS[suite]=900

        # Prompts from each component's Agentic Development guide (User Scenarios)
        # No output_dir directive — copilot-instructions.md enforces Output Isolation
        # (auto-creates dx-agentic-dev/<session_id>/ in the target sub-project).

        declare -A SCENARIO_PROMPTS
        SCENARIO_PROMPTS[compiler]="Compile yolo26n model to dxnn"
        SCENARIO_PROMPTS[dx_app]="Build a yolo26n detection app"
        SCENARIO_PROMPTS[dx_stream]="Build a real-time detection pipeline with yolo26n"
        SCENARIO_PROMPTS[runtime]="Build a yolo26n standalone detection app and a real-time streaming pipeline for it"
        SCENARIO_PROMPTS[suite]="Compile yolo26n and build an inference app"

        # Extra validation flags (scenarios that should produce model files)
        declare -A SCENARIO_CHECK_MODELS
        SCENARIO_CHECK_MODELS[compiler]=1
        SCENARIO_CHECK_MODELS[dx_app]=0
        SCENARIO_CHECK_MODELS[dx_stream]=0
        SCENARIO_CHECK_MODELS[runtime]=0
        SCENARIO_CHECK_MODELS[suite]=1

        # Search paths for dx-agentic-dev/ session auto-detection.
        # Each scenario may write to one or more sub-project directories.
        # Values are space-separated lists of dx-agentic-dev/ parent dirs.
        declare -A SCENARIO_SEARCH_PATHS
        SCENARIO_SEARCH_PATHS[compiler]="${SCRIPT_DIR}/../dx-compiler/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[dx_app]="${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[dx_stream]="${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[runtime]="${SCRIPT_DIR}/../dx-runtime/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[suite]="${SCRIPT_DIR}/../dx-agentic-dev ${SCRIPT_DIR}/../dx-compiler/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx-agentic-dev"

        # --- Session auto-detection helpers ---
        # Snapshot existing session dirs under the search paths
        snapshot_sessions() {
            local search_paths="$1"
            local snapshot_file="$2"
            > "$snapshot_file"
            for sp in $search_paths; do
                local sp_real
                sp_real="$(realpath "$sp" 2>/dev/null)" || continue
                if [ -d "$sp_real" ]; then
                    for d in "$sp_real"/*/; do
                        [ -d "$d" ] && echo "$d" >> "$snapshot_file"
                    done
                fi
            done
        }

        # Detect new session dirs created after the snapshot
        detect_new_sessions() {
            local search_paths="$1"
            local snapshot_file="$2"
            local new_dirs=()
            for sp in $search_paths; do
                local sp_real
                sp_real="$(realpath "$sp" 2>/dev/null)" || continue
                if [ -d "$sp_real" ]; then
                    for d in "$sp_real"/*/; do
                        if [ -d "$d" ] && ! grep -qxF "$d" "$snapshot_file" 2>/dev/null; then
                            new_dirs+=("$d")
                        fi
                    done
                fi
            done
            # Return space-separated list (empty if none)
            echo "${new_dirs[*]}"
        }

        # --- Validation function ---
        # Usage: validate_scenario <scenario_key> <exit_code> <dir1> [dir2] ...
        # Validates output across one or more auto-detected session directories.
        validate_scenario() {
            local scenario_key="$1"
            local exit_code="$2"
            shift 2
            local output_dirs=("$@")
            local check_models="${SCENARIO_CHECK_MODELS[$scenario_key]}"
            local pass_count=0
            local fail_count=0
            local total_checks=0

            echo ""
            echo -e "${BLUE}=== Validation Results: ${scenario_key} ===${NC}"

            # Check 1: Exit code
            total_checks=$((total_checks + 1))
            if [ "$exit_code" -eq 0 ]; then
                echo -e "  ${GREEN}[PASS]${NC} Exit code: 0"
                pass_count=$((pass_count + 1))
            else
                echo -e "  ${RED}[FAIL]${NC} Exit code: ${exit_code}"
                fail_count=$((fail_count + 1))
            fi

            # Check 1b: Session directories detected
            total_checks=$((total_checks + 1))
            if [ ${#output_dirs[@]} -gt 0 ]; then
                echo -e "  ${GREEN}[PASS]${NC} Session dirs detected: ${#output_dirs[@]}"
                for _d in "${output_dirs[@]}"; do
                    echo -e "         ${_d}"
                done
                pass_count=$((pass_count + 1))
            else
                echo -e "  ${RED}[FAIL]${NC} No session directories detected in dx-agentic-dev/"
                fail_count=$((fail_count + 1))
                # Can't validate further without dirs
                echo ""
                echo -e "  ${YELLOW}Summary: ${pass_count}/${total_checks} passed, ${fail_count} failed${NC}"
                echo ""
                return "$fail_count"
            fi

            # Check 2: Files generated (across all dirs)
            total_checks=$((total_checks + 1))
            local file_count=0
            for _d in "${output_dirs[@]}"; do
                local _fc
                _fc=$(find "$_d" -type f 2>/dev/null | wc -l)
                file_count=$((file_count + _fc))
            done
            if [ "$file_count" -gt 0 ]; then
                echo -e "  ${GREEN}[PASS]${NC} Files generated: ${file_count}"
                pass_count=$((pass_count + 1))
            else
                echo -e "  ${RED}[FAIL]${NC} No files generated in detected session dirs"
                fail_count=$((fail_count + 1))
            fi

            # Check 3: JSON validity (across all dirs)
            local json_files=""
            for _d in "${output_dirs[@]}"; do
                local _jf
                _jf=$(find "$_d" -name "*.json" -not -name "copilot-session.md" 2>/dev/null)
                [ -n "$_jf" ] && json_files="${json_files}${_jf}"$'\n'
            done
            json_files=$(echo "$json_files" | sed '/^$/d')
            if [ -n "$json_files" ]; then
                local json_ok=1
                local json_count=0
                while IFS= read -r jf; do
                    json_count=$((json_count + 1))
                    if ! python3 -c "import json; json.load(open('$jf'))" 2>/dev/null; then
                        json_ok=0
                        echo -e "  ${RED}[FAIL]${NC} Invalid JSON: $(basename "$jf")"
                    fi
                done <<< "$json_files"
                total_checks=$((total_checks + 1))
                if [ "$json_ok" -eq 1 ]; then
                    echo -e "  ${GREEN}[PASS]${NC} JSON valid (${json_count} files)"
                    pass_count=$((pass_count + 1))
                else
                    fail_count=$((fail_count + 1))
                fi
            fi

            # Check 4: Python syntax (across all dirs)
            local py_files=""
            for _d in "${output_dirs[@]}"; do
                local _pf
                _pf=$(find "$_d" -name "*.py" 2>/dev/null)
                [ -n "$_pf" ] && py_files="${py_files}${_pf}"$'\n'
            done
            py_files=$(echo "$py_files" | sed '/^$/d')
            if [ -n "$py_files" ]; then
                local py_ok=1
                local py_count=0
                while IFS= read -r pf; do
                    py_count=$((py_count + 1))
                    if ! python3 -c "import ast; ast.parse(open('$pf').read())" 2>/dev/null; then
                        py_ok=0
                        echo -e "  ${RED}[FAIL]${NC} Syntax error: $(basename "$pf")"
                    fi
                done <<< "$py_files"
                total_checks=$((total_checks + 1))
                if [ "$py_ok" -eq 1 ]; then
                    echo -e "  ${GREEN}[PASS]${NC} Python syntax OK (${py_count} files)"
                    pass_count=$((pass_count + 1))
                else
                    fail_count=$((fail_count + 1))
                fi
            fi

            # Check 5: Mandatory artifacts (compiler/suite only, across all dirs)
            if [ "$check_models" -eq 1 ]; then
                for artifact_name in setup.sh run.sh verify.py session.log; do
                    total_checks=$((total_checks + 1))
                    local artifact_found=0
                    for _d in "${output_dirs[@]}"; do
                        if [ -f "$_d/$artifact_name" ]; then
                            artifact_found=1
                            break
                        fi
                    done
                    if [ "$artifact_found" -eq 1 ]; then
                        echo -e "  ${GREEN}[PASS]${NC} Mandatory artifact: ${artifact_name}"
                        pass_count=$((pass_count + 1))
                    else
                        echo -e "  ${RED}[FAIL]${NC} Missing mandatory artifact: ${artifact_name}"
                        fail_count=$((fail_count + 1))
                    fi
                done
            fi

            # Check 6: Model files (compiler/suite only, across all dirs)
            if [ "$check_models" -eq 1 ]; then
                total_checks=$((total_checks + 1))
                local model_count=0
                for _d in "${output_dirs[@]}"; do
                    local _mc
                    _mc=$(find "$_d" \( -name "*.onnx" -o -name "*.pt" -o -name "*.pth" \) 2>/dev/null | wc -l)
                    model_count=$((model_count + _mc))
                done
                if [ "$model_count" -gt 0 ]; then
                    echo -e "  ${GREEN}[PASS]${NC} Model files acquired (${model_count})"
                    pass_count=$((pass_count + 1))
                else
                    echo -e "  ${RED}[FAIL]${NC} No model files (.onnx/.pt/.pth) found"
                    fail_count=$((fail_count + 1))
                fi

                total_checks=$((total_checks + 1))
                local dxnn_count=0
                for _d in "${output_dirs[@]}"; do
                    local _dc
                    _dc=$(find "$_d" -name "*.dxnn" 2>/dev/null | wc -l)
                    dxnn_count=$((dxnn_count + _dc))
                done
                if [ "$dxnn_count" -gt 0 ]; then
                    echo -e "  ${GREEN}[PASS]${NC} DXNN compiled (${dxnn_count})"
                    pass_count=$((pass_count + 1))
                else
                    echo -e "  ${RED}[FAIL]${NC} No .dxnn files found"
                    fail_count=$((fail_count + 1))
                fi
            fi

            echo ""
            if [ "$fail_count" -eq 0 ]; then
                echo -e "  ${GREEN}Summary: ${pass_count}/${total_checks} checks passed${NC}"
            else
                echo -e "  ${YELLOW}Summary: ${pass_count}/${total_checks} passed, ${fail_count} failed${NC}"
            fi
            echo ""

            return "$fail_count"
        }

        # --- Scenario selection ---
        # If -k filter matches a scenario key, auto-select it
        SELECTED_SCENARIOS=()

        if [ -n "${K_EXPR}" ]; then
            for key in "${SCENARIO_KEYS[@]}"; do
                if echo "$key" | grep -qi "${K_EXPR}"; then
                    SELECTED_SCENARIOS+=("$key")
                fi
            done
            if [ ${#SELECTED_SCENARIOS[@]} -eq 0 ]; then
                print_error "No scenario matches filter: ${K_EXPR}"
                print_info "Available: ${SCENARIO_KEYS[*]}"
                exit 1
            fi
            print_info "Auto-selected by -k filter: ${SELECTED_SCENARIOS[*]}"
        else
            # Show interactive menu
            echo ""
            echo -e "${YELLOW}Agentic E2E Manual Mode — Interactive Copilot CLI${NC}"
            echo ""
            echo -e "Available scenarios:"
            for i in "${!SCENARIO_KEYS[@]}"; do
                _key="${SCENARIO_KEYS[$i]}"
                printf "  ${GREEN}%d)${NC} %-12s — %s\n" "$((i+1))" "$_key" "${SCENARIO_LABELS[$_key]}"
            done
            echo -e "  ${GREEN}a)${NC} all          — Run all scenarios sequentially"
            echo ""
            read -p "Select scenario [1-${#SCENARIO_KEYS[@]}/a]: " CHOICE

            case "$CHOICE" in
                a|A|all)
                    SELECTED_SCENARIOS=("${SCENARIO_KEYS[@]}")
                    ;;
                [1-9])
                    _idx=$((CHOICE - 1))
                    if [ "$_idx" -ge 0 ] && [ "$_idx" -lt "${#SCENARIO_KEYS[@]}" ]; then
                        SELECTED_SCENARIOS=("${SCENARIO_KEYS[$_idx]}")
                    else
                        print_error "Invalid selection: ${CHOICE}"
                        exit 1
                    fi
                    ;;
                *)
                    print_error "Invalid selection: ${CHOICE}"
                    exit 1
                    ;;
            esac
        fi

        # --- Execute selected scenarios ---
        TOTAL_PASS=0
        TOTAL_FAIL=0
        declare -A SCENARIO_RESULTS
        declare -A SCENARIO_DIRS

        for scenario_key in "${SELECTED_SCENARIOS[@]}"; do
            _workdir="$(realpath "${SCENARIO_WORKDIRS[$scenario_key]}")"
            _search_paths="${SCENARIO_SEARCH_PATHS[$scenario_key]}"
            _prompt="${SCENARIO_PROMPTS[$scenario_key]}"

            # Per-scenario artifact base: under each scenario's workdir
            ARTIFACTS_BASE="${_workdir}/dx-agentic-dev/e2e-tests/copilot_cli/manual/${TIMESTAMP}"
            SCENARIO_ARTIFACTS[$scenario_key]="$ARTIFACTS_BASE"

            # Create artifact base (session-logs subdir created later with UUID)
            mkdir -p "$ARTIFACTS_BASE"

            echo ""
            echo -e "${BLUE}================================================================${NC}"
            echo -e "${BLUE}=== Scenario: ${scenario_key}${NC}"
            echo -e "${BLUE}=== Workdir:  ${_workdir}${NC}"
            echo -e "${BLUE}=== Search:   ${_search_paths}${NC}"
            echo -e "${BLUE}=== Prompt:   ${_prompt}${NC}"
            echo -e "${BLUE}================================================================${NC}"
            echo ""
            print_info "Starting copilot session..."
            print_info "Exit manually with /exit or Ctrl+C when done"
            echo ""

            # Pre-snapshot: record existing session dirs
            _snapshot_file=$(mktemp)
            snapshot_sessions "$_search_paths" "$_snapshot_file"

            # Record start timestamp for session log parsing
            _start_ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

            # Run copilot session (direct TUI)
            _timeout="${SCENARIO_TIMEOUTS[$scenario_key]}"
            (cd "$_workdir" && copilot -i "$_prompt" \
                --yolo \
                --model "$AGENTIC_MODEL")
            _copilot_exit=$?

            # Record end timestamp
            _end_ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

            # Post-detection: find new session directories
            _detected_dirs=$(detect_new_sessions "$_search_paths" "$_snapshot_file")
            rm -f "$_snapshot_file"

            # Sentinel-based detection: extract output-dir from Copilot session logs
            # This supplements filesystem-based detection with the agent's own report.
            _sentinel_dirs=$(python3 "${SCRIPT_DIR}/parse_copilot_session.py" \
                --cwd "$_workdir" \
                --after "$_start_ts" \
                --before "$_end_ts" \
                --extract-output-dir 2>/dev/null || true)
            if [ -n "$_sentinel_dirs" ]; then
                while IFS= read -r _sdir; do
                    # Resolve relative path from workdir
                    _abs_sdir="$(cd "$_workdir" && realpath -m "$_sdir" 2>/dev/null || echo "$_workdir/$_sdir")"
                    # Add trailing slash for consistency with detect_new_sessions output
                    [[ "$_abs_sdir" != */ ]] && _abs_sdir="${_abs_sdir}/"
                    # Only add if it exists and is not already detected
                    if [ -d "$_abs_sdir" ] && ! echo "$_detected_dirs" | grep -qF "$_abs_sdir"; then
                        _detected_dirs="${_detected_dirs:+$_detected_dirs }${_abs_sdir}"
                        print_info "Sentinel detected additional dir: $_abs_sdir"
                    fi
                done <<< "$_sentinel_dirs"
            fi

            # Convert to array and deduplicate by realpath
            read -r -a _detected_arr <<< "$_detected_dirs"
            if [ ${#_detected_arr[@]} -gt 1 ]; then
                declare -A _seen_dirs
                _deduped=()
                for _dd in "${_detected_arr[@]}"; do
                    _dd_real="$(realpath "$_dd" 2>/dev/null || echo "$_dd")"
                    [[ "$_dd_real" != */ ]] && _dd_real="${_dd_real}/"
                    if [ -z "${_seen_dirs[$_dd_real]+x}" ]; then
                        _seen_dirs[$_dd_real]=1
                        _deduped+=("$_dd_real")
                    fi
                done
                _detected_arr=("${_deduped[@]}")
                unset _seen_dirs _deduped
            fi

            if [ ${#_detected_arr[@]} -gt 0 ]; then
                print_info "Detected ${#_detected_arr[@]} new session dir(s):"
                for _dd in "${_detected_arr[@]}"; do
                    echo "  -> $_dd"
                done
            else
                echo -e "  ${YELLOW}[WARN]${NC} No new session directories detected"
            fi

            # Phase C: UUID extraction + session artifact generation
            # Extract copilot CLI session UUID and state directory (fast, no event parsing)
            _session_uuid=$(python3 "${SCRIPT_DIR}/parse_copilot_session.py" \
                --cwd "$_workdir" --after "$_start_ts" --before "$_end_ts" \
                --extract-session-id 2>/dev/null | head -1 || true)
            _session_state_dir=$(python3 "${SCRIPT_DIR}/parse_copilot_session.py" \
                --cwd "$_workdir" --after "$_start_ts" --before "$_end_ts" \
                --extract-session-dir 2>/dev/null | head -1 || true)
            _uuid_suffix="${_session_uuid:-unknown}"

            if [ -n "$_session_uuid" ]; then
                print_info "Copilot session UUID: ${_session_uuid}"
            else
                echo -e "  ${YELLOW}[WARN]${NC} Could not extract copilot session UUID (using 'unknown')"
            fi

            # Session-logs directory with UUID
            _session_logs_dir="${ARTIFACTS_BASE}/session-logs-${_uuid_suffix}"
            mkdir -p "$_session_logs_dir"

            if [ ${#_detected_arr[@]} -gt 0 ]; then
                # C1: Generate session HTML from events.jsonl
                _session_html="${_session_logs_dir}/${scenario_key}-session-${_uuid_suffix}.html"
                if python3 "${SCRIPT_DIR}/parse_copilot_session.py" \
                    --cwd "$_workdir" \
                    --after "$_start_ts" \
                    --before "$_end_ts" \
                    --format html \
                    --output "$_session_html" 2>/dev/null; then
                    print_info "Session HTML generated: $_session_html"
                else
                    echo -e "  ${YELLOW}[WARN]${NC} Failed to generate session HTML (non-fatal)"
                fi

                # Copy events.jsonl for traceability
                if [ -n "$_session_state_dir" ] && [ -f "${_session_state_dir}/events.jsonl" ]; then
                    cp "${_session_state_dir}/events.jsonl" \
                       "${ARTIFACTS_BASE}/${scenario_key}-copilot-events-${_uuid_suffix}.jsonl"
                    print_info "Events log copied: ${scenario_key}-copilot-events-${_uuid_suffix}.jsonl"
                fi

                # C2: Collect /share html output
                # Brief wait for async file writes to complete after copilot exit
                sleep 2
                _share_html=""
                for _search_dir in "$_workdir" "${_detected_arr[@]}" "$ARTIFACTS_BASE" "$HOME"; do
                    for _pattern in copilot-session-*.html copilot-session-*.htm; do
                        for _hf in "${_search_dir}"/${_pattern}; do
                            if [ -f "$_hf" ]; then
                                _share_html="$_hf"
                                break 3
                            fi
                        done
                    done
                done
                # Fallback: recursive find under workdir
                if [ -z "$_share_html" ]; then
                    _share_html=$(find "$_workdir" -maxdepth 3 -name "copilot-session-*.html" \
                        -print -quit 2>/dev/null || true)
                fi
                if [ -n "$_share_html" ]; then
                    cp "$_share_html" "${ARTIFACTS_BASE}/${scenario_key}-copilot-shared-${_uuid_suffix}.html" 2>/dev/null
                    print_info "Copilot /share html saved: ${ARTIFACTS_BASE}/${scenario_key}-copilot-shared-${_uuid_suffix}.html"
                else
                    echo -e "  ${YELLOW}[WARN]${NC} No copilot-session-*.html found in: $_workdir (+ ${#_detected_arr[@]} detected dirs)"
                fi
            fi

            # Symlinks: create in ARTIFACTS_BASE for ALL scenarios (not just suite)
            if [ ${#_detected_arr[@]} -gt 0 ]; then
                for _dd in "${_detected_arr[@]}"; do
                    _session_name=$(basename "$_dd")
                    # Determine parent sub-project name (e.g. dx-compiler, dx_app)
                    _parent_dir=$(dirname "$_dd")         # .../dx-compiler/dx-agentic-dev
                    _parent_name=$(basename "$(dirname "$_parent_dir")")  # dx-compiler
                    _link_name="${_parent_name}_${_session_name}"
                    ln -sfn "$(realpath "$_dd")" "${ARTIFACTS_BASE}/${_link_name}"
                    print_info "Symlink: ${ARTIFACTS_BASE}/${_link_name} -> $(realpath "$_dd")"
                done
            fi

            # Parse Copilot CLI session logs (events.jsonl) into Markdown
            # Best-effort: failure does not block validation
            _session_logs_md="${_session_logs_dir}/${scenario_key}-session_logs-${_uuid_suffix}.md"
            if python3 "${SCRIPT_DIR}/parse_copilot_session.py" \
                --cwd "$_workdir" \
                --after "$_start_ts" \
                --before "$_end_ts" \
                --output "$_session_logs_md" 2>/dev/null; then
                print_info "Session logs parsed: $_session_logs_md"
            else
                echo -e "  ${YELLOW}[WARN]${NC} Failed to parse Copilot session logs (non-fatal)"
            fi

            # Validate results using detected dirs
            validate_scenario "$scenario_key" "$_copilot_exit" "${_detected_arr[@]}"
            _val_failures=$?
            if [ "$_val_failures" -eq 0 ]; then
                TOTAL_PASS=$((TOTAL_PASS + 1))
                SCENARIO_RESULTS[$scenario_key]="PASS"
            else
                TOTAL_FAIL=$((TOTAL_FAIL + 1))
                SCENARIO_RESULTS[$scenario_key]="FAIL"
            fi
            SCENARIO_DIRS[$scenario_key]="${_detected_arr[*]}"

            # --- Per-scenario README.md ---
            _readme="${ARTIFACTS_BASE}/README.md"
            {
                echo "# Agentic E2E Manual — ${scenario_key} Results"
                echo ""
                echo "- **Date:** $(date '+%Y-%m-%d %H:%M:%S')"
                echo "- **Model:** ${AGENTIC_MODEL}"
                echo "- **Scenario:** ${scenario_key}"
                echo "- **Workdir:** ${_workdir}"
                echo "- **Result:** ${SCENARIO_RESULTS[$scenario_key]}"
                echo ""
                echo "## Session Directories"
                echo ""
                if [ ${#_detected_arr[@]} -gt 0 ]; then
                    for _dd in "${_detected_arr[@]}"; do
                        _dd_short=$(echo "$_dd" | sed "s|$(realpath "${SCRIPT_DIR}/..")/||g")
                        echo "- \`${_dd_short}\`"
                    done
                else
                    echo "- (none detected)"
                fi
                echo ""
                echo "## Artifacts"
                echo ""
                echo "- **Session logs:** \`session-logs-${_uuid_suffix}/\`"
                echo "- **Events log:** \`${scenario_key}-copilot-events-${_uuid_suffix}.jsonl\`"
                echo "- **Symlinks:** Point to actual \`dx-agentic-dev/\` session directories"
                echo "- **Copilot /share html:** \`${scenario_key}-copilot-shared-${_uuid_suffix}.html\` (exported via \`/share html\` in Copilot CLI only)"
                echo "- **Copilot session UUID:** \`${_uuid_suffix}\`"
            } > "$_readme"
        done

        # --- Global summary README.md (when running multiple scenarios) ---
        if [ ${#SELECTED_SCENARIOS[@]} -gt 1 ]; then
            mkdir -p "$GLOBAL_SUMMARY_BASE"
            _global_readme="${GLOBAL_SUMMARY_BASE}/README.md"
            {
                echo "# Agentic E2E Manual — Global Summary"
                echo ""
                echo "- **Date:** $(date '+%Y-%m-%d %H:%M:%S')"
                echo "- **Model:** ${AGENTIC_MODEL}"
                echo "- **Scenarios:** ${#SELECTED_SCENARIOS[@]}"
                echo "- **Passed:** ${TOTAL_PASS}"
                echo "- **Failed:** ${TOTAL_FAIL}"
                echo ""
                echo "## Scenario Results"
                echo ""
                echo "| Scenario | Result | Artifacts Base | Session Directories |"
                echo "|----------|--------|----------------|---------------------|"
                for _key in "${SELECTED_SCENARIOS[@]}"; do
                    _result="${SCENARIO_RESULTS[$_key]:-SKIP}"
                    _ab="${SCENARIO_ARTIFACTS[$_key]}"
                    _ab_short=$(echo "$_ab" | sed "s|$(realpath "${SCRIPT_DIR}/..")/||g")
                    _dirs="${SCENARIO_DIRS[$_key]:-none}"
                    _dirs_short=$(echo "$_dirs" | sed "s|$(realpath "${SCRIPT_DIR}/..")/||g")
                    echo "| ${_key} | ${_result} | \`${_ab_short}\` | ${_dirs_short} |"
                done
                echo ""
                echo "## Per-Scenario Artifacts"
                echo ""
                for _key in "${SELECTED_SCENARIOS[@]}"; do
                    _ab="${SCENARIO_ARTIFACTS[$_key]}"
                    _ab_short=$(echo "$_ab" | sed "s|$(realpath "${SCRIPT_DIR}/..")/||g")
                    echo "- **${_key}:** \`${_ab_short}/\`"
                done
            } > "$_global_readme"
        fi

        # --- Summary (console) ---
        echo ""
        echo -e "${BLUE}================================================================${NC}"
        echo -e "${BLUE}=== Agentic E2E Manual — Final Summary${NC}"
        echo -e "${BLUE}================================================================${NC}"
        echo -e "  Scenarios run:    ${#SELECTED_SCENARIOS[@]}"
        echo -e "  ${GREEN}Passed:${NC}           ${TOTAL_PASS}"
        if [ "$TOTAL_FAIL" -gt 0 ]; then
            echo -e "  ${RED}Failed:${NC}           ${TOTAL_FAIL}"
        fi
        echo -e "  Artifacts (per-scenario):"
        for _key in "${SELECTED_SCENARIOS[@]}"; do
            _ab="${SCENARIO_ARTIFACTS[$_key]}"
            _ab_short=$(echo "$_ab" | sed "s|$(realpath "${SCRIPT_DIR}/..")/||g")
            echo -e "    ${GREEN}${_key}:${NC}  ${_ab_short}/"
        done
        if [ ${#SELECTED_SCENARIOS[@]} -gt 1 ]; then
            _gs_short=$(echo "$GLOBAL_SUMMARY_BASE" | sed "s|$(realpath "${SCRIPT_DIR}/..")/||g")
            echo -e "  Global summary:   ${_gs_short}/README.md"
        fi
        echo ""

        # Cleanup session logs unless kept (generated files are in dx-agentic-dev/)
        if [ "$KEEP_ARTIFACTS" != "1" ] && [ "$TOTAL_FAIL" -eq 0 ]; then
            print_info "Cleaning up artifacts (set DX_AGENTIC_E2E_KEEP_ARTIFACTS=1 to keep)"
            for _ab in "${SCENARIO_ARTIFACTS[@]}"; do
                rm -rf "$_ab"
            done
            if [ ${#SELECTED_SCENARIOS[@]} -gt 1 ]; then
                rm -rf "$GLOBAL_SUMMARY_BASE"
            fi
        fi

        if [ "$TOTAL_FAIL" -gt 0 ]; then
            exit 1
        fi
        exit 0
        ;;

    agentic-e2e-cursor-cli-manual)
        # ---------------------------------------------------------------
        # Shell-based interactive mode — runs Cursor CLI directly (no pytest)
        # User interacts with Cursor agent, then shell validates output.
        # ---------------------------------------------------------------
        if ! command -v agent &> /dev/null; then
            print_error "Cursor CLI (agent) not found on PATH. Install it first:"
            print_error "  curl https://cursor.com/install -fsS | bash"
            exit 1
        fi

        AGENTIC_MODEL="${DX_AGENTIC_E2E_CURSOR_MODEL:-claude-4.6-sonnet-medium}"
        KEEP_ARTIFACTS="${DX_AGENTIC_E2E_KEEP_ARTIFACTS:-0}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        declare -A SCENARIO_ARTIFACTS
        GLOBAL_SUMMARY_BASE="${SCRIPT_DIR}/../dx-agentic-dev/e2e-tests/cursor_cli/manual/${TIMESTAMP}"

        SCENARIO_KEYS=(compiler dx_app dx_stream runtime suite)

        declare -A SCENARIO_LABELS
        SCENARIO_LABELS[compiler]="Download yolo26n, compile to DXNN"
        SCENARIO_LABELS[dx_app]="Build yolo26n person detection app"
        SCENARIO_LABELS[dx_stream]="Build detection pipeline with tracking"
        SCENARIO_LABELS[runtime]="Route to dx_app + dx_stream via runtime builder"
        SCENARIO_LABELS[suite]="Cross-project compile + app generation"

        declare -A SCENARIO_WORKDIRS
        SCENARIO_WORKDIRS[compiler]="${SCRIPT_DIR}/../dx-compiler"
        SCENARIO_WORKDIRS[dx_app]="${SCRIPT_DIR}/../dx-runtime/dx_app"
        SCENARIO_WORKDIRS[dx_stream]="${SCRIPT_DIR}/../dx-runtime/dx_stream"
        SCENARIO_WORKDIRS[runtime]="${SCRIPT_DIR}/../dx-runtime"
        SCENARIO_WORKDIRS[suite]="${SCRIPT_DIR}/.."

        declare -A SCENARIO_PROMPTS
        SCENARIO_PROMPTS[compiler]="Compile yolo26n model to dxnn"
        SCENARIO_PROMPTS[dx_app]="Build a yolo26n detection app"
        SCENARIO_PROMPTS[dx_stream]="Build a real-time detection pipeline with yolo26n"
        SCENARIO_PROMPTS[runtime]="Build a yolo26n standalone detection app and a real-time streaming pipeline for it"
        SCENARIO_PROMPTS[suite]="Compile yolo26n and build an inference app"

        declare -A SCENARIO_SEARCH_PATHS
        SCENARIO_SEARCH_PATHS[compiler]="${SCRIPT_DIR}/../dx-compiler/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[dx_app]="${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[dx_stream]="${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[runtime]="${SCRIPT_DIR}/../dx-runtime/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agentic-dev"
        SCENARIO_SEARCH_PATHS[suite]="${SCRIPT_DIR}/../dx-agentic-dev ${SCRIPT_DIR}/../dx-compiler/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agentic-dev ${SCRIPT_DIR}/../dx-runtime/dx-agentic-dev"

        declare -A SCENARIO_CHECK_MODELS
        SCENARIO_CHECK_MODELS[compiler]=1
        SCENARIO_CHECK_MODELS[dx_app]=0
        SCENARIO_CHECK_MODELS[dx_stream]=0
        SCENARIO_CHECK_MODELS[runtime]=0
        SCENARIO_CHECK_MODELS[suite]=1

        # Reuse snapshot/detect/validate helpers from copilot-manual (already defined above)
        # They persist in the same shell process.

        # --- Scenario selection ---
        SELECTED_SCENARIOS=()

        if [ -n "${K_EXPR}" ]; then
            for key in "${SCENARIO_KEYS[@]}"; do
                if echo "$key" | grep -qi "${K_EXPR}"; then
                    SELECTED_SCENARIOS+=("$key")
                fi
            done
            if [ ${#SELECTED_SCENARIOS[@]} -eq 0 ]; then
                print_error "No scenario matches filter: ${K_EXPR}"
                print_info "Available: ${SCENARIO_KEYS[*]}"
                exit 1
            fi
            print_info "Auto-selected by -k filter: ${SELECTED_SCENARIOS[*]}"
        else
            echo ""
            echo -e "${YELLOW}Agentic E2E Manual Mode — Interactive Cursor CLI${NC}"
            echo ""
            echo -e "Available scenarios:"
            for i in "${!SCENARIO_KEYS[@]}"; do
                _key="${SCENARIO_KEYS[$i]}"
                printf "  ${GREEN}%d)${NC} %-12s — %s\n" "$((i+1))" "$_key" "${SCENARIO_LABELS[$_key]}"
            done
            echo -e "  ${GREEN}a)${NC} all          — Run all scenarios sequentially"
            echo ""
            read -p "Select scenario [1-${#SCENARIO_KEYS[@]}/a]: " CHOICE

            case "$CHOICE" in
                a|A|all)
                    SELECTED_SCENARIOS=("${SCENARIO_KEYS[@]}")
                    ;;
                [1-9])
                    _idx=$((CHOICE - 1))
                    if [ "$_idx" -ge 0 ] && [ "$_idx" -lt "${#SCENARIO_KEYS[@]}" ]; then
                        SELECTED_SCENARIOS=("${SCENARIO_KEYS[$_idx]}")
                    else
                        print_error "Invalid selection: ${CHOICE}"
                        exit 1
                    fi
                    ;;
                *)
                    print_error "Invalid selection: ${CHOICE}"
                    exit 1
                    ;;
            esac
        fi

        # --- Execute selected scenarios ---
        TOTAL_PASS=0
        TOTAL_FAIL=0
        declare -A SCENARIO_RESULTS
        declare -A SCENARIO_DIRS

        for scenario_key in "${SELECTED_SCENARIOS[@]}"; do
            _workdir="$(realpath "${SCENARIO_WORKDIRS[$scenario_key]}")"
            _search_paths="${SCENARIO_SEARCH_PATHS[$scenario_key]}"
            _prompt="${SCENARIO_PROMPTS[$scenario_key]}"

            ARTIFACTS_BASE="${_workdir}/dx-agentic-dev/e2e-tests/cursor_cli/manual/${TIMESTAMP}"
            SCENARIO_ARTIFACTS[$scenario_key]="$ARTIFACTS_BASE"
            mkdir -p "$ARTIFACTS_BASE"

            echo ""
            echo -e "${BLUE}================================================================${NC}"
            echo -e "${BLUE}=== Scenario: ${scenario_key}${NC}"
            echo -e "${BLUE}=== Workdir:  ${_workdir}${NC}"
            echo -e "${BLUE}=== Model:    ${AGENTIC_MODEL}${NC}"
            echo -e "${BLUE}=== Prompt:   ${_prompt}${NC}"
            echo -e "${BLUE}================================================================${NC}"
            echo ""
            print_info "Starting Cursor CLI session..."
            print_info "Exit manually with Ctrl+C when done"
            echo ""

            _snapshot_file=$(mktemp)
            snapshot_sessions "$_search_paths" "$_snapshot_file"

            # Run Cursor agent session (interactive TUI)
            (cd "$_workdir" && agent \
                --model "$AGENTIC_MODEL" \
                "$_prompt")
            _cursor_exit=$?

            # Post-detection: find new session directories
            _detected_dirs=$(detect_new_sessions "$_search_paths" "$_snapshot_file")
            rm -f "$_snapshot_file"

            read -r -a _detected_arr <<< "$_detected_dirs"
            if [ ${#_detected_arr[@]} -gt 1 ]; then
                declare -A _seen_dirs
                _deduped=()
                for _dd in "${_detected_arr[@]}"; do
                    _dd_real="$(realpath "$_dd" 2>/dev/null || echo "$_dd")"
                    [[ "$_dd_real" != */ ]] && _dd_real="${_dd_real}/"
                    if [ -z "${_seen_dirs[$_dd_real]+x}" ]; then
                        _seen_dirs[$_dd_real]=1
                        _deduped+=("$_dd_real")
                    fi
                done
                _detected_arr=("${_deduped[@]}")
                unset _seen_dirs _deduped
            fi

            if [ ${#_detected_arr[@]} -gt 0 ]; then
                print_info "Detected ${#_detected_arr[@]} new session dir(s):"
                for _dd in "${_detected_arr[@]}"; do
                    echo "  -> $_dd"
                done
            else
                echo -e "  ${YELLOW}[WARN]${NC} No new session directories detected"
            fi

            validate_scenario "$scenario_key" "$_cursor_exit" "${_detected_arr[@]}"
            _val_failures=$?
            if [ "$_val_failures" -eq 0 ]; then
                TOTAL_PASS=$((TOTAL_PASS + 1))
                SCENARIO_RESULTS[$scenario_key]="PASS"
            else
                TOTAL_FAIL=$((TOTAL_FAIL + 1))
                SCENARIO_RESULTS[$scenario_key]="FAIL"
            fi
            SCENARIO_DIRS[$scenario_key]="${_detected_arr[*]}"
        done

        # --- Summary ---
        echo ""
        echo -e "${BLUE}================================================================${NC}"
        echo -e "${BLUE}=== Agentic E2E Cursor Manual — Final Summary${NC}"
        echo -e "${BLUE}================================================================${NC}"
        echo -e "  Model:            ${AGENTIC_MODEL}"
        echo -e "  Scenarios run:    ${#SELECTED_SCENARIOS[@]}"
        echo -e "  ${GREEN}Passed:${NC}           ${TOTAL_PASS}"
        if [ "$TOTAL_FAIL" -gt 0 ]; then
            echo -e "  ${RED}Failed:${NC}           ${TOTAL_FAIL}"
        fi
        echo ""

        if [ "$TOTAL_FAIL" -gt 0 ]; then
            exit 1
        fi
        exit 0
        ;;

    list)
        print_info "Listing all available tests..."
        pytest --collect-only "${K_ARGS[@]}" "${M_ARGS[@]}" "$@"
        ;;

    report)
        print_info "Running all tests with HTML report generation..."
        REPORT_DIR="${SCRIPT_DIR}/reports"
        mkdir -p "${REPORT_DIR}"
        TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
        REPORT_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.html"

        pytest -v "${K_ARGS[@]}" "${M_ARGS[@]}" --html="${REPORT_FILE}" --self-contained-html "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?

        if [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    json)
        print_info "Running all tests with JSON report generation..."
        if [ -z "${JSON_FILE}" ]; then
            REPORT_DIR="${SCRIPT_DIR}/reports"
            mkdir -p "${REPORT_DIR}"
            TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
            JSON_FILE="${REPORT_DIR}/test_report_${TIMESTAMP}.json"
        fi

        pytest -v "${K_ARGS[@]}" "${M_ARGS[@]}" --json-report --json-report-file="${JSON_FILE}" "$@"
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