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
#   version_compatibility - Run version compatibility tests
#   install_option  - Run install.sh option tests (local, no Docker)
#   list            - List all available tests
#   report          - Run all tests and generate HTML report
#   json            - Run all tests and generate JSON report
#   help            - Show this help message
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LOCAL_SCRIPT="${SCRIPT_DIR}/test_local/test_local.sh"
DOCKER_SCRIPT="${SCRIPT_DIR}/test_docker/test_docker.sh"
VENV_DIR="${SCRIPT_DIR}/venv"
REQUIREMENTS_FILE="${SCRIPT_DIR}/requirements.txt"

# Run pytest from tests/ so discovery stays scoped to this tree.
cd "${SCRIPT_DIR}" || exit 1

# Restore permission-only git changes caused by container-side chmod.
restore_git_permissions() {
    [ -d "$REPO_ROOT/.git" ] || return 0
    git -C "$REPO_ROOT" diff --raw 2>/dev/null | while IFS= read -r line; do
        old_mode=$(echo "$line" | sed 's/^:\([0-9]*\) .*/\1/')
        new_mode=$(echo "$line" | sed 's/^:[0-9]* \([0-9]*\) .*/\1/')
        filepath=$(echo "$line" | sed 's/.*\t//')
        [ -z "$filepath" ] && continue
        [ "$old_mode" = "$new_mode" ] && continue
        if [ "$old_mode" = "100644" ]; then
            chmod 644 "$REPO_ROOT/$filepath" 2>/dev/null
        elif [ "$old_mode" = "100755" ]; then
            chmod 755 "$REPO_ROOT/$filepath" 2>/dev/null
        fi
    done
}

trap restore_git_permissions EXIT

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

# Parallel execution and host-resource locking
pytest-xdist>=3.5.0
filelock>=3.13.0
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
    echo -e "  ${GREEN}version_compatibility${NC} - Run version compatibility tests"
    echo -e "  ${GREEN}install_option${NC}  - Run install.sh option tests (local, no Docker)"
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
    echo -e "  ${GREEN}OS version keywords${NC} - 26.04 | 24.04 | 22.04 | 20.04 | 12 | 13 (e.g. -k \"debian and 12\")"
    echo -e ""
    echo -e "Examples:"
    echo -e "  ./test.sh sanity"
    echo -e "  ./test.sh local_install"
    echo -e "  ./test.sh docker_install"
    echo -e "  ./test.sh getting_started"
    echo -e "  ./test.sh version_compatibility"
    echo -e "  ./test.sh install_option"
    echo -e "  ./test.sh --report sanity"
    echo -e "  ./test.sh --debug local_install"
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

# =============================================================================
# MANUAL_SHARED — shared definitions for all 4 manual E2E test sections.
# Defined before case statement so all sections always have access,
# regardless of execution order (eliminates the guard pattern dependency).
# =============================================================================

SCENARIO_KEYS=(compiler dx_app dx_stream cascaded runtime suite)

declare -A SCENARIO_LABELS
SCENARIO_LABELS[compiler]="Download yolo26n, compile to DXNN"
SCENARIO_LABELS[dx_app]="Build yolo26n person detection app"
SCENARIO_LABELS[dx_stream]="Build detection pipeline with tracking"
SCENARIO_LABELS[cascaded]="Build cascaded detection pipeline"
SCENARIO_LABELS[runtime]="Route to dx_app + dx_stream via runtime builder"
SCENARIO_LABELS[suite]="Cross-project compile + app generation"

declare -A SCENARIO_WORKDIRS
SCENARIO_WORKDIRS[compiler]="${SCRIPT_DIR}/../dx-compiler"
SCENARIO_WORKDIRS[dx_app]="${SCRIPT_DIR}/../dx-runtime/dx_app"
SCENARIO_WORKDIRS[dx_stream]="${SCRIPT_DIR}/../dx-runtime/dx_stream"
SCENARIO_WORKDIRS[cascaded]="${SCRIPT_DIR}/../dx-runtime/dx_stream"
SCENARIO_WORKDIRS[runtime]="${SCRIPT_DIR}/../dx-runtime"
SCENARIO_WORKDIRS[suite]="${SCRIPT_DIR}/.."

declare -A SCENARIO_TIMEOUTS
SCENARIO_TIMEOUTS[compiler]=1200
SCENARIO_TIMEOUTS[dx_app]=600
SCENARIO_TIMEOUTS[dx_stream]=300
SCENARIO_TIMEOUTS[cascaded]=900
SCENARIO_TIMEOUTS[runtime]=600
SCENARIO_TIMEOUTS[suite]=900

# Prompts from each component's Agent-Driven Development guide (User Scenarios).
# No output_dir directive — copilot-instructions.md enforces Output Isolation
# (auto-creates dx-agent-dev/<session_id>/ in the target sub-project).
declare -A SCENARIO_PROMPTS
SCENARIO_PROMPTS[compiler]="Compile yolo26n model to dxnn"
SCENARIO_PROMPTS[dx_app]="Build a yolo26n detection app"
SCENARIO_PROMPTS[dx_stream]="Build a real-time detection pipeline with yolo26n"
SCENARIO_PROMPTS[cascaded]="Build a cascaded pipeline using yolo26n for primary object detection and a secondary classification stage for detected objects"
SCENARIO_PROMPTS[runtime]="Build a yolo26n standalone detection app and a real-time streaming pipeline for it"
SCENARIO_PROMPTS[suite]="Compile yolo26n and build an inference app"

# Extra validation flags (scenarios that should produce model files)
declare -A SCENARIO_CHECK_MODELS
SCENARIO_CHECK_MODELS[compiler]=1
SCENARIO_CHECK_MODELS[dx_app]=0
SCENARIO_CHECK_MODELS[dx_stream]=0
SCENARIO_CHECK_MODELS[cascaded]=0
SCENARIO_CHECK_MODELS[runtime]=0
SCENARIO_CHECK_MODELS[suite]=1

# Search paths for dx-agent-dev/ session auto-detection.
# Each scenario may write to one or more sub-project directories.
# Values are space-separated lists of dx-agent-dev/ parent dirs.
declare -A SCENARIO_SEARCH_PATHS
SCENARIO_SEARCH_PATHS[compiler]="${SCRIPT_DIR}/../dx-compiler/dx-agent-dev"
SCENARIO_SEARCH_PATHS[dx_app]="${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agent-dev"
SCENARIO_SEARCH_PATHS[dx_stream]="${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agent-dev"
SCENARIO_SEARCH_PATHS[cascaded]="${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agent-dev"
SCENARIO_SEARCH_PATHS[runtime]="${SCRIPT_DIR}/../dx-runtime/dx-agent-dev ${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agent-dev ${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agent-dev"
SCENARIO_SEARCH_PATHS[suite]="${SCRIPT_DIR}/../dx-agent-dev ${SCRIPT_DIR}/../dx-compiler/dx-agent-dev ${SCRIPT_DIR}/../dx-runtime/dx_app/dx-agent-dev ${SCRIPT_DIR}/../dx-runtime/dx_stream/dx-agent-dev ${SCRIPT_DIR}/../dx-runtime/dx-agent-dev"

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
    local agent_filter="${3:-}"
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
    # Agent filter: only return dirs whose name contains the agent string
    # (mirrors autopilot conftest.py _detect_new_sessions agent_filter)
    if [ -n "$agent_filter" ]; then
        local filtered=()
        for d in "${new_dirs[@]}"; do
            [[ "$d" == *"$agent_filter"* ]] && filtered+=("$d")
        done
        new_dirs=("${filtered[@]}")
    fi
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
        echo -e "  ${RED}[FAIL]${NC} No session directories detected in dx-agent-dev/"
        fail_count=$((fail_count + 1))
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

    # Ensure .sh files are executable (agents may create them without +x)
    for _d in "${output_dirs[@]}"; do
        find "$_d" -name "*.sh" -type f -exec chmod +x {} + 2>/dev/null
    done

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
            if ! python3 -c "import json,sys; json.load(open(sys.argv[1]))" "$jf" 2>/dev/null; then
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
            if ! python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$pf" 2>/dev/null; then
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

# =============================================================================

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

    version_compatibility)
        print_info "Running version compatibility tests..."
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "version_compatibility and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m version_compatibility)
        fi
        pytest "${SCRIPT_DIR}/test_version_compatibility" -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    version_compatibility)
        print_info "Running version compatibility tests..."
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "version_compatibility and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m version_compatibility)
        fi
        pytest "${SCRIPT_DIR}/test_version_compatibility" -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
        ;;

    install_option)
        print_info "Running install.sh option tests (local, no Docker)..."
        if [ -n "${M_EXPR}" ]; then
            COMBINED_M_ARGS=(-m "install_option and (${M_EXPR})")
        else
            COMBINED_M_ARGS=(-m install_option)
        fi
        pytest -v "${CAPTURE_ARGS[@]}" "${COLLECT_ONLY_ARGS[@]}" "${COMBINED_M_ARGS[@]}" "${K_ARGS[@]}" "${REPORT_ARGS[@]}" "${JSON_ARGS[@]}" "$@"
        EXIT_CODE=$?
        if [ $GENERATE_REPORT -eq 1 ] && [ $EXIT_CODE -eq 0 ]; then
            print_success "HTML report generated: ${REPORT_FILE}"
        fi
        exit $EXIT_CODE
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

        pytest -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" --html="${REPORT_FILE}" --self-contained-html "${JSON_ARGS[@]}" "$@"
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

        pytest -v "${CAPTURE_ARGS[@]}" "${K_ARGS[@]}" "${M_ARGS[@]}" --json-report --json-report-file="${JSON_FILE}" "$@"
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