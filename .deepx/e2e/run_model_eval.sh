#!/usr/bin/env bash
# run_model_eval.sh — one-command model-eval orchestration wrapper
#
# Chains the documented model-eval cycle:
#   run OLD model → run NEW model → analyze each → build_comparison → bundle raw → append registry row
#
# Usage:
#   .deepx/e2e/run_model_eval.sh --old-model <id> --new-model <id> [options]
#
# Required:
#   --old-model <id>       Model ID for the "old" / baseline run
#   --new-model <id>       Model ID for the "new" / candidate run
#
# Optional:
#   --tool <name>          Coding tool (default: claude-code)
#                          Supported: claude-code, copilot-cli, codex-cli, opencode-cli, cursor-cli
#   --rounds <N>           Number of rounds per model (default: 5)
#   --thinking             Enable thinking / high-reasoning mode (default: off = NTH)
#   --label <str>          Archive sub-label (default: <date>_<old>_vs_<new>_<TH|NTH>)
#   --reuse-run-ids <csv>  Comma-separated extra prior run_ids to include in OLD analyze step
#   --archive <dir>        Durable archive root
#                          (default: ${DX_MODEL_EVAL_ARCHIVE:-$HOME/shared/coding_agent_diff_report})
#   --dry-run              Print every command it WOULD run (prefixed [dry-run]), execute nothing

set -euo pipefail

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
TOOL="claude-code"
OLD_MODEL=""
NEW_MODEL=""
ROUNDS=5
THINKING=0
LABEL=""
REUSE_RUN_IDS=""
ARCHIVE="${DX_MODEL_EVAL_ARCHIVE:-$HOME/shared/coding_agent_diff_report}"
DRY_RUN=0

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        --tool)          TOOL="$2";         shift 2 ;;
        --old-model)     OLD_MODEL="$2";    shift 2 ;;
        --new-model)     NEW_MODEL="$2";    shift 2 ;;
        --rounds)        ROUNDS="$2";       shift 2 ;;
        --thinking)      THINKING=1;        shift   ;;
        --label)         LABEL="$2";        shift 2 ;;
        --reuse-run-ids) REUSE_RUN_IDS="$2";shift 2 ;;
        --archive)       ARCHIVE="$2";      shift 2 ;;
        --dry-run)       DRY_RUN=1;         shift   ;;
        *)
            echo "ERROR: Unknown argument: $1" >&2
            echo "Usage: $0 --old-model <id> --new-model <id> [--tool <name>] [--rounds N] [--thinking] [--label <str>] [--reuse-run-ids <csv>] [--archive <dir>] [--dry-run]" >&2
            exit 1
            ;;
    esac
done

# ---------------------------------------------------------------------------
# Validate required args
# ---------------------------------------------------------------------------
if [[ -z "$OLD_MODEL" ]]; then
    echo "ERROR: --old-model is required" >&2
    exit 1
fi
if [[ -z "$NEW_MODEL" ]]; then
    echo "ERROR: --new-model is required" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Resolve SUITE_ROOT by walking up until dx-runtime/ and dx-compiler/ exist
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
SUITE_ROOT="$SCRIPT_DIR"
while [[ "$SUITE_ROOT" != "/" ]]; do
    if [[ -d "$SUITE_ROOT/dx-runtime" && -d "$SUITE_ROOT/dx-compiler" ]]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [[ "$SUITE_ROOT" == "/" ]]; then
    echo "ERROR: Cannot find suite root (expected dx-runtime/ and dx-compiler/ siblings)" >&2
    exit 1
fi

# ---------------------------------------------------------------------------
# Paths relative to SUITE_ROOT
# ---------------------------------------------------------------------------
E2E_DIR="$SUITE_ROOT/.deepx/e2e"
RUNNER="$E2E_DIR/e2e_runner.py"
RESILIENT_RUNNER="$E2E_DIR/e2e_resilient_run.py"
ANALYZE="$E2E_DIR/agent_analyzer/analyze.py"
BUILD_COMPARISON="$E2E_DIR/agent_analyzer/build_comparison.py"
BUNDLE="$E2E_DIR/bundle_raw_results.py"
RESULTS_ROOT="$SUITE_ROOT/dx-agent-dev/e2e-tests/results"

# ---------------------------------------------------------------------------
# Map --tool to e2e_runner model flag name
# ---------------------------------------------------------------------------
case "$TOOL" in
    claude-code)   MODEL_FLAG="--claude-model"   ;;
    copilot-cli)   MODEL_FLAG="--copilot-model"  ;;
    codex-cli)     MODEL_FLAG="--codex-model"    ;;
    opencode-cli)  MODEL_FLAG="--opencode-model" ;;
    cursor-cli)    MODEL_FLAG="--cursor-model"   ;;
    *)
        echo "ERROR: Unknown tool: $TOOL. Supported: claude-code, copilot-cli, codex-cli, opencode-cli, cursor-cli" >&2
        exit 1
        ;;
esac

# ---------------------------------------------------------------------------
# Derive label
# ---------------------------------------------------------------------------
if [[ -z "$LABEL" ]]; then
    TODAY="$(date +%Y%m%d)"
    # Sanitize model ids: replace non-alphanum with '_', collapse runs
    OLD_SLUG="$(echo "$OLD_MODEL" | tr -cs 'a-zA-Z0-9' '_' | sed 's/__*/_/g; s/^_//; s/_$//')"
    NEW_SLUG="$(echo "$NEW_MODEL" | tr -cs 'a-zA-Z0-9' '_' | sed 's/__*/_/g; s/^_//; s/_$//')"
    TH_SUFFIX="NTH"
    if [[ "$THINKING" -eq 1 ]]; then
        TH_SUFFIX="TH"
    fi
    LABEL="${TODAY}_${OLD_SLUG}_vs_${NEW_SLUG}_${TH_SUFFIX}"
fi

# ---------------------------------------------------------------------------
# Thinking flag for runner
# ---------------------------------------------------------------------------
THINKING_ARG=""
if [[ "$THINKING" -eq 1 ]]; then
    THINKING_ARG="--thinking"
fi

# ---------------------------------------------------------------------------
# Helper: run or dry-run a command
# ---------------------------------------------------------------------------
_run() {
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] $*"
    else
        "$@"
    fi
}

# ---------------------------------------------------------------------------
# Helper: capture run_id from e2e_runner stdout (real run only)
# ---------------------------------------------------------------------------
_run_and_capture_run_id() {
    local log_file="$1"
    shift
    if [[ "$DRY_RUN" -eq 1 ]]; then
        echo "[dry-run] $*"
        return 0
    fi
    # Tee stdout+stderr to log and to terminal; capture into variable
    local output
    output="$("$@" 2>&1 | tee "$log_file")"
    echo "$output"
    # Extract run_id from output
    local rid
    rid="$(echo "$output" | grep -oP 'run_id=\K[^ ]+' | tail -1)"
    if [[ -z "$rid" ]]; then
        echo "ERROR: Could not capture run_id from e2e_runner output. Check $log_file" >&2
        exit 1
    fi
    echo "$rid"
}

# ---------------------------------------------------------------------------
# Dry-run: print all planned commands then exit
# ---------------------------------------------------------------------------
if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "=== run_model_eval.sh DRY-RUN ==="
    echo "  SUITE_ROOT : $SUITE_ROOT"
    echo "  TOOL       : $TOOL  ($MODEL_FLAG)"
    echo "  OLD_MODEL  : $OLD_MODEL"
    echo "  NEW_MODEL  : $NEW_MODEL"
    echo "  ROUNDS     : $ROUNDS"
    echo "  THINKING   : $([ "$THINKING" -eq 1 ] && echo TH || echo NTH)"
    echo "  LABEL      : $LABEL"
    echo "  ARCHIVE    : $ARCHIVE"
    echo ""

    # Step 1: Run OLD model (via resilient controller)
    echo "--- Step 1: Run OLD model ---"
    _run python3 "$RESILIENT_RUNNER" \
        --tool "$TOOL" \
        --model "$OLD_MODEL" \
        --rounds "$ROUNDS" \
        $THINKING_ARG

    # Step 2: Run NEW model (via resilient controller)
    echo "--- Step 2: Run NEW model ---"
    _run python3 "$RESILIENT_RUNNER" \
        --tool "$TOOL" \
        --model "$NEW_MODEL" \
        --rounds "$ROUNDS" \
        $THINKING_ARG

    # Placeholder run IDs for dry-run
    RID_OLD="<RID_OLD>"
    RID_NEW="<RID_NEW>"

    # Build reuse list for OLD analyze
    OLD_RUN_IDS_ARGS="--run-id $RID_OLD"
    if [[ -n "$REUSE_RUN_IDS" ]]; then
        for rid in ${REUSE_RUN_IDS//,/ }; do
            OLD_RUN_IDS_ARGS="$OLD_RUN_IDS_ARGS --run-id $rid"
        done
    fi

    # Step 3: Analyze OLD
    echo "--- Step 3: Analyze OLD set ---"
    _run python3 "$ANALYZE" \
        $OLD_RUN_IDS_ARGS \
        --output-dir "$ARCHIVE/$LABEL/old"

    # Step 4: Analyze NEW
    echo "--- Step 4: Analyze NEW set ---"
    _run python3 "$ANALYZE" \
        --run-id "$RID_NEW" \
        --output-dir "$ARCHIVE/$LABEL/new"

    # Step 5: build_comparison.py
    echo "--- Step 5: Build comparison report ---"
    _run python3 "$BUILD_COMPARISON" \
        --non-thinking-dir "$ARCHIVE/$LABEL/old" \
        --thinking-dir "$ARCHIVE/$LABEL/new" \
        --non-thinking-run-id "$RID_OLD" \
        --thinking-run-id "$RID_NEW" \
        --output "$ARCHIVE/$LABEL/comparison.html"

    # Step 6: Bundle raw results
    echo "--- Step 6: Bundle raw results ---"
    _run python3 "$BUNDLE" \
        --results-dir "$RESULTS_ROOT/$RID_OLD" \
        --out "$ARCHIVE/$LABEL/raw/$RID_OLD" \
        --suite-root "$SUITE_ROOT"

    _run python3 "$BUNDLE" \
        --results-dir "$RESULTS_ROOT/$RID_NEW" \
        --out "$ARCHIVE/$LABEL/raw/$RID_NEW" \
        --suite-root "$SUITE_ROOT"

    # Step 7: Registry append
    echo "--- Step 7: Append registry row ---"
    _run bash -c "mkdir -p '$ARCHIVE' && \
        ([ -f '$ARCHIVE/MODEL_EVAL_REGISTRY.md' ] || printf '| date | purpose | comparison | tool_scope | run_ids | rounds | overall_delta | cost | report | notes |\n|------|---------|------------|------------|---------|--------|---------------|------|--------|-------|\n' > '$ARCHIVE/MODEL_EVAL_REGISTRY.md') && \
        printf '| %s | model | %s vs %s (%s) | %s | OLD=%s NEW=%s | 1-%s | TBD | TBD | ./%s/comparison.html | auto-generated |\n' \
            \"\$(date +%Y-%m-%d)\" '$OLD_MODEL' '$NEW_MODEL' '$([ "$THINKING" -eq 1 ] && echo TH || echo NTH)' '$TOOL' '$RID_OLD' '$RID_NEW' '$ROUNDS' '$LABEL' \
        >> '$ARCHIVE/MODEL_EVAL_REGISTRY.md'"

    echo ""
    echo "=== DRY-RUN complete. No commands executed. ==="
    exit 0
fi

# ---------------------------------------------------------------------------
# Real run
# ---------------------------------------------------------------------------

echo "=== run_model_eval.sh START ==="
echo "  SUITE_ROOT : $SUITE_ROOT"
echo "  TOOL       : $TOOL  ($MODEL_FLAG)"
echo "  OLD_MODEL  : $OLD_MODEL"
echo "  NEW_MODEL  : $NEW_MODEL"
echo "  ROUNDS     : $ROUNDS"
echo "  THINKING   : $([ "$THINKING" -eq 1 ] && echo TH || echo NTH)"
echo "  LABEL      : $LABEL"
echo "  ARCHIVE    : $ARCHIVE"
echo ""

mkdir -p "$ARCHIVE/$LABEL/raw"

# --- Step 1: Run OLD model (via resilient controller) ---
echo "=== Step 1: Run OLD model ($OLD_MODEL) ==="
OLD_LOG="$ARCHIVE/$LABEL/runner_old.log"
RID_OLD_OUT="$(
    python3 "$RESILIENT_RUNNER" \
        --tool "$TOOL" \
        --model "$OLD_MODEL" \
        --rounds "$ROUNDS" \
        $THINKING_ARG 2>&1 | tee "$OLD_LOG"
)"
RID_OLD="$(echo "$RID_OLD_OUT" | grep -oP 'run_id=\K[^ ]+' | tail -1 || true)"
if [[ -z "$RID_OLD" ]]; then
    echo "ERROR: Could not capture RID_OLD from runner output. Check $OLD_LOG" >&2
    exit 1
fi
echo "  RID_OLD=$RID_OLD"

# --- Step 2: Run NEW model (via resilient controller) ---
echo "=== Step 2: Run NEW model ($NEW_MODEL) ==="
NEW_LOG="$ARCHIVE/$LABEL/runner_new.log"
RID_NEW_OUT="$(
    python3 "$RESILIENT_RUNNER" \
        --tool "$TOOL" \
        --model "$NEW_MODEL" \
        --rounds "$ROUNDS" \
        $THINKING_ARG 2>&1 | tee "$NEW_LOG"
)"
RID_NEW="$(echo "$RID_NEW_OUT" | grep -oP 'run_id=\K[^ ]+' | tail -1 || true)"
if [[ -z "$RID_NEW" ]]; then
    echo "ERROR: Could not capture RID_NEW from runner output. Check $NEW_LOG" >&2
    exit 1
fi
echo "  RID_NEW=$RID_NEW"

# --- Step 3: Analyze OLD set (RID_OLD + any --reuse-run-ids) ---
echo "=== Step 3: Analyze OLD set ==="
OLD_ANALYZE_ARGS=("--run-id" "$RID_OLD")
if [[ -n "$REUSE_RUN_IDS" ]]; then
    for rid in ${REUSE_RUN_IDS//,/ }; do
        OLD_ANALYZE_ARGS+=("--run-id" "$rid")
    done
fi
python3 "$ANALYZE" \
    "${OLD_ANALYZE_ARGS[@]}" \
    --output-dir "$ARCHIVE/$LABEL/old"

# --- Step 4: Analyze NEW set ---
echo "=== Step 4: Analyze NEW set ==="
python3 "$ANALYZE" \
    --run-id "$RID_NEW" \
    --output-dir "$ARCHIVE/$LABEL/new"

# --- Step 5: Build comparison report ---
echo "=== Step 5: Build comparison report ==="
python3 "$BUILD_COMPARISON" \
    --non-thinking-dir "$ARCHIVE/$LABEL/old" \
    --thinking-dir "$ARCHIVE/$LABEL/new" \
    --non-thinking-run-id "$RID_OLD" \
    --thinking-run-id "$RID_NEW" \
    --output "$ARCHIVE/$LABEL/comparison.html"

# --- Step 6: Bundle raw results ---
echo "=== Step 6: Bundle raw results ==="
python3 "$BUNDLE" \
    --results-dir "$RESULTS_ROOT/$RID_OLD" \
    --out "$ARCHIVE/$LABEL/raw/$RID_OLD" \
    --suite-root "$SUITE_ROOT"

python3 "$BUNDLE" \
    --results-dir "$RESULTS_ROOT/$RID_NEW" \
    --out "$ARCHIVE/$LABEL/raw/$RID_NEW" \
    --suite-root "$SUITE_ROOT"

# --- Step 7: Append registry row ---
echo "=== Step 7: Append registry row ==="
TODAY="$(date +%Y-%m-%d)"
TH_LABEL="$([ "$THINKING" -eq 1 ] && echo TH || echo NTH)"

if [[ ! -f "$ARCHIVE/MODEL_EVAL_REGISTRY.md" ]]; then
    mkdir -p "$ARCHIVE"
    printf '| date | purpose | comparison | tool_scope | run_ids | rounds | overall_delta | cost | report | notes |\n' \
        > "$ARCHIVE/MODEL_EVAL_REGISTRY.md"
    printf '|------|---------|------------|------------|---------|--------|---------------|------|--------|-------|\n' \
        >> "$ARCHIVE/MODEL_EVAL_REGISTRY.md"
fi

printf '| %s | model | %s vs %s (%s) | %s | OLD=%s NEW=%s | 1-%s | TBD | TBD | ./%s/comparison.html | auto-generated |\n' \
    "$TODAY" "$OLD_MODEL" "$NEW_MODEL" "$TH_LABEL" "$TOOL" \
    "$RID_OLD" "$RID_NEW" "$ROUNDS" "$LABEL" \
    >> "$ARCHIVE/MODEL_EVAL_REGISTRY.md"

# ---------------------------------------------------------------------------
# Final summary
# ---------------------------------------------------------------------------
echo ""
echo "=== run_model_eval.sh COMPLETE ==="
echo ""
echo "  Label          : $LABEL"
echo "  RID_OLD        : $RID_OLD"
echo "  RID_NEW        : $RID_NEW"
echo ""
echo "  Archive paths:"
echo "    OLD analyze  : $ARCHIVE/$LABEL/old/"
echo "    NEW analyze  : $ARCHIVE/$LABEL/new/"
echo "    Comparison   : $ARCHIVE/$LABEL/comparison.html"
echo "    Raw bundles  : $ARCHIVE/$LABEL/raw/"
echo "    Registry     : $ARCHIVE/MODEL_EVAL_REGISTRY.md"
echo ""
