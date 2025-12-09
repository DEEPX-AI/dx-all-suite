#!/bin/bash
SCRIPT_DIR=$(realpath "$(dirname "$0")")
PROJECT_ROOT=$(realpath "$SCRIPT_DIR")
DOWNLOAD_DIR="$SCRIPT_DIR/download"
PROJECT_NAME=$(basename "$SCRIPT_DIR")
VENV_PATH="$PROJECT_ROOT/venv-$PROJECT_NAME"

pushd "$PROJECT_ROOT" >&2

# color env settings
source ${PROJECT_ROOT}/scripts/color_env.sh
source ${PROJECT_ROOT}/scripts/common_util.sh

ENABLE_DEBUG_LOGS=0

# Global variables for tracking uninstall results
declare -A UNINSTALL_RESULTS

# Function to record uninstall result
record_result() {
    local module_name="$1"
    local result="$2"  # "success", "fail", or "skip"
    UNINSTALL_RESULTS["$module_name"]="$result"
}

# Function to print final results summary
print_results_summary() {
    echo -e "${COLOR_BOLD}${COLOR_CYAN}=========== Uninstall Results Summary ==========${COLOR_RESET}"
    
    # Define the desired order
    local ordered_modules="dx-compiler dx-runtime dx-runtime/dx_rt dx-runtime/dx_app dx-runtime/dx_stream dx-runtime/dx_fw dx-runtime/dx_rt_npu_linux_driver dx-modelzoo"
    
    local has_results=false
    
    # Print results in the specified order
    for module in $ordered_modules; do
        if [[ -n "${UNINSTALL_RESULTS[$module]}" ]]; then
            has_results=true
            local result="${UNINSTALL_RESULTS[$module]}"
            case "$result" in
                "success")
                    echo -e "  $module: ${COLOR_GREEN}SUCCESS${COLOR_RESET}"
                    ;;
                "fail")
                    echo -e "  $module: ${COLOR_RED}FAILED${COLOR_RESET}"
                    ;;
                "skip")
                    echo -e "  $module: ${COLOR_YELLOW}SKIPPED${COLOR_RESET}"
                    ;;
            esac
        fi
    done
    
    # Print any additional modules not in the ordered list
    for module in "${!UNINSTALL_RESULTS[@]}"; do
        local found=false
        for ordered_module in $ordered_modules; do
            if [[ "$module" == "$ordered_module" ]]; then
                found=true
                break
            fi
        done
        
        if [[ "$found" == false ]]; then
            has_results=true
            local result="${UNINSTALL_RESULTS[$module]}"
            case "$result" in
                "success")
                    echo -e "  $module: ${COLOR_GREEN}SUCCESS${COLOR_RESET}"
                    ;;
                "fail")
                    echo -e "  $module: ${COLOR_RED}FAILED${COLOR_RESET}"
                    ;;
                "skip")
                    echo -e "  $module: ${COLOR_YELLOW}SKIPPED${COLOR_RESET}"
                    ;;
            esac
        fi
    done
    
    if [ "$has_results" = false ]; then
        print_colored_v2 "INFO" "  No submodules were processed."
    fi
    
    echo -e "${COLOR_BOLD}${COLOR_CYAN}================================================${COLOR_RESET}"
}

# Function to load results from dx-runtime
load_dx_runtime_results() {
    local results_file="$1"
    
    if [ -f "$results_file" ]; then
        while IFS=':' read -r module result; do
            if [ -n "$module" ] && [ -n "$result" ]; then
                record_result "$module" "$result"
            fi
        done < "$results_file"
        rm -f "$results_file"  # Clean up temporary file
    fi
}

# Main function to uninstall submodules
# Usage: uninstall_submodules "dx-compiler dx-runtime dx-modelzoo"
uninstall_submodules() {
    local submodules="$1"
    
    print_colored_v2 "INFO" "Starting submodule uninstallation..."
    
    for module in $submodules; do
        local uninstall_script="$module/uninstall.sh"
        
        if [ -f "$uninstall_script" ]; then
            print_colored_v2 "INFO" "Uninstalling $module..."
            
            # Special handling for dx-runtime to capture submodule results
            if [ "$module" = "dx-runtime" ]; then
                local temp_results_file="/tmp/dx_runtime_results_$$"
                
                # Execute dx-runtime uninstall with results file
                if (cd "$module" && DX_UNINSTALL_RESULTS_FILE="$temp_results_file" ./uninstall.sh); then
                    print_colored_v2 "INFO" "$module uninstall completed successfully"
                    record_result "$module" "success"
                    
                    # Load dx-runtime submodule results
                    load_dx_runtime_results "$temp_results_file"
                else
                    print_colored_v2 "ERROR" "$module uninstall failed"
                    record_result "$module" "fail"
                    
                    # Still try to load partial results
                    load_dx_runtime_results "$temp_results_file"
                fi
            else
                # Regular submodule uninstall
                if (cd "$module" && ./uninstall.sh); then
                    print_colored_v2 "INFO" "$module uninstall completed successfully"
                    record_result "$module" "success"
                else
                    print_colored_v2 "ERROR" "$module uninstall failed"
                    record_result "$module" "fail"
                fi
            fi
        else
            print_colored_v2 "WARNING" "$module: uninstall.sh not found, skipping"
            record_result "$module" "skip"
        fi
    done
    
    # Print final results
    print_results_summary
}

show_help() {
    echo -e "Usage: ${COLOR_CYAN}$(basename "$0") [OPTIONS]${COLOR_RESET}"
    echo -e ""
    echo -e "Options:"
    echo -e "  ${COLOR_GREEN}[-v|--verbose]${COLOR_RESET}                        Enable verbose (debug) logging"
    echo -e "  ${COLOR_GREEN}[-h|--help]${COLOR_RESET}                           Display this help message and exit"
    echo -e ""
    echo -e "${COLOR_BOLD}Description:${COLOR_RESET}"
    echo -e "  This script uninstalls dx-all-suite and all its submodules."
    echo -e "  It will automatically process: dx-compiler, dx-runtime, dx-modelzoo"
    echo -e "  All results including dx-runtime submodules will be shown in a unified summary."
    echo -e ""
    
    if [ "$1" == "error" ] && [[ ! -n "$2" ]]; then
        print_colored_v2 "ERROR" "Invalid or missing arguments."
        exit 1
    elif [ "$1" == "error" ] && [[ -n "$2" ]]; then
        print_colored_v2 "ERROR" "$2"
        exit 1
    elif [[ "$1" == "warn" ]] && [[ -n "$2" ]]; then
        print_colored_v2 "WARNING" "$2"
        return 0
    fi
    exit 0
}

uninstall_common_files() {
    print_colored_v2 "INFO" "Uninstalling common files..."
    delete_symlinks "$DOWNLOAD_DIR"
    delete_symlinks "$PROJECT_ROOT"
    delete_symlinks "${VENV_PATH}"
    delete_symlinks "${VENV_PATH}-local"
    delete_dir "${VENV_PATH}"
    delete_dir "${VENV_PATH}-local"
    delete_dir "${DOWNLOAD_DIR}" 
}

uninstall_project_specific_files() {
    print_colored_v2 "INFO" "Uninstalling ${PROJECT_NAME} specific files..."
    delete_symlinks "getting-started"
    delete_dir "getting-started/forked_dx_app_example/"
    delete_dir "getting-started/modelzoo/"
    delete_dir "workspace"
    delete_dir "archives"
}

main() {
    echo "Uninstalling ${PROJECT_NAME} ..."

    # Uninstall all submodules first
    print_colored_v2 "INFO" "=== Uninstalling Submodules ==="
    uninstall_submodules "dx-compiler dx-runtime dx-modelzoo"
    
    print_colored_v2 "INFO" "=== Uninstalling dx-all-suite Project ==="
    
    # Remove symlinks from DOWNLOAD_DIR and PROJECT_ROOT for 'Common' Rules
    uninstall_common_files

    # Uninstall the project specific files
    uninstall_project_specific_files

    echo "Uninstalling ${PROJECT_NAME} done"
}

# parse args
for i in "$@"; do
    case "$1" in
        -v|--verbose)
            ENABLE_DEBUG_LOGS=1
            ;;
        -h|--help)
            show_help
            ;;
        *)
            show_help "error" "Invalid option '$1'"
            ;;
    esac
    shift
done

main

popd >&2

exit 0
