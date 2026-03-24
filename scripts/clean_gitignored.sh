#!/bin/bash
# clean_gitignored.sh
# Finds and removes files/directories listed in .gitignore
#
# Usage:
#   ./scripts/clean_gitignored.sh                        # dry-run (list targets without deleting)
#   ./scripts/clean_gitignored.sh --delete               # delete with confirmation prompt
#   ./scripts/clean_gitignored.sh --yes                  # non-interactive delete (for CI, etc.)
#   ./scripts/clean_gitignored.sh --repo <path>          # target a specific repo root
#   ./scripts/clean_gitignored.sh --recursive            # also clean all nested submodules

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEFAULT_REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REPO_ROOT="${DEFAULT_REPO_ROOT}"

source "${SCRIPT_DIR}/color_env.sh"
source "${SCRIPT_DIR}/common_util.sh"

# ── Argument parsing ────────────────────────────────────────────────────────
DRY_RUN=true
AUTO_YES=false
RECURSIVE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --delete) DRY_RUN=false ;;
        --yes|-y) AUTO_YES=true ;;
        --recursive|-r) RECURSIVE=true ;;
        --repo)
            if [[ -z "${2:-}" ]]; then
                print_colored "--repo requires a path argument" "ERROR"
                exit 1
            fi
            REPO_ROOT="$(cd "$2" && pwd)" || { print_colored "Invalid repo path: $2" "ERROR"; exit 1; }
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--delete] [--yes] [--repo <path>] [--recursive]"
            echo ""
            echo "  (no args)        List .gitignore targets without deleting (dry-run)"
            echo "  --delete         Delete the listed files/directories"
            echo "  --yes, -y        Skip confirmation prompt (use with --delete)"
            echo "  --repo <path>    Target repo root (default: parent of this script)"
            echo "  --recursive, -r  Also clean all nested submodules"
            exit 0
            ;;
        *)
            print_colored "Unknown option: $1" "ERROR"
            exit 1
            ;;
    esac
    shift
done

# ── Build list of repos to process ──────────────────────────────────────────
# Each entry is "absolute_path|display_label"
REPO_LIST=()
REPO_LIST+=("${REPO_ROOT}|root (${REPO_ROOT})")

if [[ "${RECURSIVE}" == "true" ]]; then
    while IFS= read -r subpath; do
        [[ -z "$subpath" ]] && continue
        REPO_LIST+=("${REPO_ROOT}/${subpath}|submodule: ${subpath}")
    done < <(cd "${REPO_ROOT}" && git submodule foreach --recursive --quiet 'echo "$displaypath"' 2>/dev/null)
fi

# ── Scan phase: collect and print targets per repo ──────────────────────────
TOTAL_TARGETS=0

scan_repo() {
    local repo_path="$1"
    local label="$2"

    pushd "${repo_path}" > /dev/null
    mapfile -t targets < <(git clean -Xdn 2>/dev/null | sed 's/^Would remove //')
    popd > /dev/null

    if [[ ${#targets[@]} -eq 0 ]]; then
        return 0
    fi

    print_colored "[${label}] ${#targets[@]} target(s):" "INFO"
    for t in "${targets[@]}"; do
        printf "  ${COLOR_BRIGHT_YELLOW}%s${COLOR_RESET}\n" "$t"
    done

    TOTAL_TARGETS=$(( TOTAL_TARGETS + ${#targets[@]} ))
}

for entry in "${REPO_LIST[@]}"; do
    path="${entry%%|*}"
    label="${entry#*|}"
    scan_repo "${path}" "${label}"
done

echo ""

if [[ ${TOTAL_TARGETS} -eq 0 ]]; then
    print_colored "No targets found matching .gitignore patterns." "INFO"
    exit 0
fi

# ── Exit here if dry-run ─────────────────────────────────────────────────────
if [[ "${DRY_RUN}" == "true" ]]; then
    print_colored "Dry-run mode: no files were deleted. (total: ${TOTAL_TARGETS} item(s))" "WARNING"
    print_colored "Add --delete to actually remove the listed targets." "HINT"
    exit 0
fi

# ── Confirm before deleting ─────────────────────────────────────────────────
if [[ "${AUTO_YES}" == "false" ]]; then
    read -rp "Delete the above ${TOTAL_TARGETS} item(s) across ${#REPO_LIST[@]} repo(s)? [y/N] " confirm
    case "$confirm" in
        [yY][eE][sS]|[yY]) ;;
        *)
            print_colored "Deletion cancelled." "WARNING"
            exit 0
            ;;
    esac
fi

# ── Delete phase ─────────────────────────────────────────────────────────────
for entry in "${REPO_LIST[@]}"; do
    path="${entry%%|*}"
    label="${entry#*|}"

    pushd "${path}" > /dev/null
    mapfile -t targets < <(git clean -Xdn 2>/dev/null | sed 's/^Would remove //')
    if [[ ${#targets[@]} -gt 0 ]]; then
        print_colored "Deleting [${label}]..." "INFO"
        git clean -Xdf
        print_colored "Clean complete [${label}]." "SUCCESS"
    fi
    popd > /dev/null
done
