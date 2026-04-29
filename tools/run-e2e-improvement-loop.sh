#!/usr/bin/env bash
# tools/run-e2e-improvement-loop.sh
#
# Self-improving Agentic E2E test loop.
#
# Each iteration:
#   1. Run all 4 autopilot E2E tests (copilot / cursor / opencode / claude)
#   2. Collect results + artifacts into context
#   3. Call Claude to generate a comparison report
#   4. Call Claude to extract and apply improvements
#   5. Read result JSON → continue or stop
#
# Usage:
#   bash tools/run-e2e-improvement-loop.sh [options]
#
# Options:
#   --max-iterations N    Max loop iterations (default: 5)
#   --scenario KEY        Scenario key filter for pytest (default: dx_stream)
#   --suite-root PATH     Path to dx-all-suite root (default: auto-detect)
#   --orchestrator TYPE   Orchestrator for report+improve steps: claude (default), copilot, cursor, or opencode
#   --claude-bin PATH     Claude binary path (default: claude)
#   --copilot-bin PATH    Copilot binary path (default: copilot)
#   --cursor-bin PATH     Cursor CLI binary path (default: agent)
#   --opencode-bin PATH   OpenCode binary path (default: opencode)
#   --model MODEL         Model for report generation and improvements (default: claude-sonnet-4-6)
#   --run-dir PATH        Use specific run directory instead of auto-timestamped
#   --resume              Resume from latest timestamped run in doc/reports/e2e-loop/
#   --dry-run             Print commands without executing
#   -h, --help            Show this help
#
# Results are stored in: doc/reports/e2e-loop/YYYYMMDD-HHMMSS/

set -euo pipefail

# ── Colour helpers ────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

log()  { echo -e "${CYAN}[loop]${NC} $*"; }
ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
warn() { echo -e "${YELLOW}[!]${NC} $*"; }
fail() { echo -e "${RED}[✗]${NC} $*"; }
sep()  { echo -e "${BOLD}──────────────────────────────────────────────────────${NC}"; }

# ── Claude quota helpers ───────────────────────────────────────────────────────
_is_claude_quota_error() {
    local text="${1,,}"   # to lowercase
    [[ "$text" == *"usage limit"* ]] || [[ "$text" == *"rate limit"* ]] \
        || [[ "$text" == *"hit your limit"* ]] || [[ "$text" == *"hit our limit"* ]] \
        || [[ "$text" == *"hit the limit"* ]] || [[ "$text" == *"you've hit"* ]]
}

# Poll every CLAUDE_QUOTA_POLL_INTERVAL seconds until quota clears or max polls exceeded.
# Returns 0 when quota cleared, 1 when max polls reached.
_wait_for_claude_quota() {
    local poll=0
    while [ "$poll" -lt "$CLAUDE_QUOTA_MAX_POLLS" ]; do
        poll=$(( poll + 1 ))
        log "[quota-wait] Poll $poll/$CLAUDE_QUOTA_MAX_POLLS — sleeping ${CLAUDE_QUOTA_POLL_INTERVAL}s ($(( CLAUDE_QUOTA_POLL_INTERVAL / 60 )) min) ..."
        sleep "$CLAUDE_QUOTA_POLL_INTERVAL"
        local probe
        probe=$( "$CLAUDE_BIN" --output-format text -p "echo ok" 2>&1 ) || true
        if ! _is_claude_quota_error "$probe"; then
            ok "[quota-wait] Quota cleared at poll $poll — resuming."
            return 0
        fi
        warn "[quota-wait] Still over quota (poll $poll)."
    done
    fail "[quota-wait] Max polls ($CLAUDE_QUOTA_MAX_POLLS) exceeded — aborting loop."
    return 1
}

# Claude CLI wrapper: detects quota errors and polls until cleared, then retries.
# Usage: run_claude <log_file> [claude args...]
run_claude() {
    local log_file="$1"; shift
    while true; do
        local out rc
        out=$( "$CLAUDE_BIN" "$@" 2>&1 )
        rc=$?
        printf '%s\n' "$out" >> "$log_file"
        if [ "$rc" -ne 0 ] && _is_claude_quota_error "$out"; then
            warn "[quota-wait] Claude usage limit hit."
            _wait_for_claude_quota || return 1
            log "[quota-wait] Retrying claude call ..."
            continue
        fi
        return "$rc"
    done
}

# ── Copilot quota helpers ─────────────────────────────────────────────────────
_is_copilot_quota_error() {
    local text="${1,,}"
    [[ "$text" == *"out of usage"* ]] || [[ "$text" == *"switch to auto"* ]] \
        || [[ "$text" == *"rate limit"* ]] || [[ "$text" == *"usage limit"* ]]
}

_wait_for_copilot_quota() {
    local poll=0
    while [ "$poll" -lt "$CLAUDE_QUOTA_MAX_POLLS" ]; do
        poll=$(( poll + 1 ))
        log "[quota-wait] Poll $poll/$CLAUDE_QUOTA_MAX_POLLS — sleeping ${CLAUDE_QUOTA_POLL_INTERVAL}s ($(( CLAUDE_QUOTA_POLL_INTERVAL / 60 )) min) ..."
        sleep "$CLAUDE_QUOTA_POLL_INTERVAL"
        local probe
        probe=$( (cd "$SUITE_ROOT" && "$COPILOT_BIN" -i "echo ok" --yolo) 2>&1 ) || true
        if ! _is_copilot_quota_error "$probe"; then
            ok "[quota-wait] Copilot quota cleared at poll $poll — resuming."
            return 0
        fi
        warn "[quota-wait] Copilot still over quota (poll $poll)."
    done
    fail "[quota-wait] Max polls ($CLAUDE_QUOTA_MAX_POLLS) exceeded — aborting loop."
    return 1
}

# Copilot CLI wrapper: runs a prompt non-interactively with --yolo.
# Usage: run_copilot <log_file> <prompt>
run_copilot() {
    local log_file="$1"
    local prompt="$2"
    while true; do
        local out rc
        out=$( (cd "$SUITE_ROOT" && "$COPILOT_BIN" -i "$prompt" --yolo --model "$MODEL") 2>&1 )
        rc=$?
        printf '%s\n' "$out" >> "$log_file"
        if [ "$rc" -ne 0 ] && _is_copilot_quota_error "$out"; then
            warn "[quota-wait] Copilot usage limit hit."
            _wait_for_copilot_quota || return 1
            log "[quota-wait] Retrying copilot call ..."
            continue
        fi
        return "$rc"
    done
}

# ── Cursor quota helpers ──────────────────────────────────────────────────────
_is_cursor_quota_error() {
    local text="${1,,}"
    [[ "$text" == *"out of usage"* ]] || [[ "$text" == *"switch to auto"* ]]
}

_wait_for_cursor_quota() {
    local poll=0
    while [ "$poll" -lt "$CLAUDE_QUOTA_MAX_POLLS" ]; do
        poll=$(( poll + 1 ))
        log "[quota-wait] Poll $poll/$CLAUDE_QUOTA_MAX_POLLS — sleeping ${CLAUDE_QUOTA_POLL_INTERVAL}s ($(( CLAUDE_QUOTA_POLL_INTERVAL / 60 )) min) ..."
        sleep "$CLAUDE_QUOTA_POLL_INTERVAL"
        local probe
        probe=$( (cd "$SUITE_ROOT" && "$CURSOR_BIN" -p --force --output-format stream-json "echo ok") 2>&1 ) || true
        if ! _is_cursor_quota_error "$probe"; then
            ok "[quota-wait] Cursor quota cleared at poll $poll — resuming."
            return 0
        fi
        warn "[quota-wait] Cursor still over quota (poll $poll)."
    done
    fail "[quota-wait] Max polls ($CLAUDE_QUOTA_MAX_POLLS) exceeded — aborting loop."
    return 1
}

# Cursor CLI wrapper: runs a prompt non-interactively with -p --force.
# Usage: run_cursor <log_file> <prompt>
run_cursor() {
    local log_file="$1"
    local prompt="$2"
    while true; do
        local out rc
        out=$( (cd "$SUITE_ROOT" && "$CURSOR_BIN" -p --force --output-format stream-json --model "$MODEL" "$prompt") 2>&1 )
        rc=$?
        printf '%s\n' "$out" >> "$log_file"
        if [ "$rc" -ne 0 ] && _is_cursor_quota_error "$out"; then
            warn "[quota-wait] Cursor usage limit hit."
            _wait_for_cursor_quota || return 1
            log "[quota-wait] Retrying cursor call ..."
            continue
        fi
        return "$rc"
    done
}

# ── OpenCode quota helpers ────────────────────────────────────────────────────
_is_opencode_quota_error() {
    local text="${1,,}"
    [[ "$text" == *"rate limit"* ]] || [[ "$text" == *"usage limit"* ]] \
        || [[ "$text" == *"quota exceeded"* ]] || [[ "$text" == *"too many requests"* ]]
}

_wait_for_opencode_quota() {
    local poll=0
    while [ "$poll" -lt "$CLAUDE_QUOTA_MAX_POLLS" ]; do
        poll=$(( poll + 1 ))
        log "[quota-wait] Poll $poll/$CLAUDE_QUOTA_MAX_POLLS — sleeping ${CLAUDE_QUOTA_POLL_INTERVAL}s ($(( CLAUDE_QUOTA_POLL_INTERVAL / 60 )) min) ..."
        sleep "$CLAUDE_QUOTA_POLL_INTERVAL"
        local probe
        probe=$( (cd "$SUITE_ROOT" && "$OPENCODE_BIN" run --format json "echo ok") 2>&1 ) || true
        if ! _is_opencode_quota_error "$probe"; then
            ok "[quota-wait] OpenCode quota cleared at poll $poll — resuming."
            return 0
        fi
        warn "[quota-wait] OpenCode still over quota (poll $poll)."
    done
    fail "[quota-wait] Max polls ($CLAUDE_QUOTA_MAX_POLLS) exceeded — aborting loop."
    return 1
}

# OpenCode wrapper: runs a prompt non-interactively via `opencode run --format json`.
# Usage: run_opencode <log_file> <prompt>
run_opencode() {
    local log_file="$1"
    local prompt="$2"
    while true; do
        local out rc
        out=$( (cd "$SUITE_ROOT" && "$OPENCODE_BIN" run --format json --model "$MODEL" "$prompt") 2>&1 )
        rc=$?
        printf '%s\n' "$out" >> "$log_file"
        if [ "$rc" -ne 0 ] && _is_opencode_quota_error "$out"; then
            warn "[quota-wait] OpenCode usage limit hit."
            _wait_for_opencode_quota || return 1
            log "[quota-wait] Retrying opencode call ..."
            continue
        fi
        return "$rc"
    done
}

# ── Orchestrator dispatcher ───────────────────────────────────────────────────
# Routes report/improve/translate calls to claude/copilot/cursor/opencode based on $ORCHESTRATOR.
# Usage: run_orchestrator <log_file> <prompt>
run_orchestrator() {
    local log_file="$1"
    local prompt="$2"
    case "$ORCHESTRATOR" in
        copilot)  run_copilot  "$log_file" "$prompt" ;;
        cursor)   run_cursor   "$log_file" "$prompt" ;;
        opencode) run_opencode "$log_file" "$prompt" ;;
        *)        run_claude "$log_file" \
                      --dangerously-skip-permissions \
                      --model "$MODEL" \
                      --output-format text \
                      -p "$prompt" ;;
    esac
}

# ── Defaults ──────────────────────────────────────────────────────────────────
MAX_ITERATIONS=5
SCENARIO="dx_stream"
ORCHESTRATOR="${ORCHESTRATOR:-claude}"   # claude|copilot|cursor|opencode
CLAUDE_BIN="${CLAUDE_BIN:-claude}"
COPILOT_BIN="${COPILOT_BIN:-copilot}"
CURSOR_BIN="${CURSOR_BIN:-agent}"
OPENCODE_BIN="${OPENCODE_BIN:-opencode}"
MODEL="${CLAUDE_MODEL:-claude-sonnet-4-6}"
RESUME=0
DRY_RUN=0
RUN_DIR=""   # explicit run directory (overrides auto-timestamped dir)
CLAUDE_QUOTA_POLL_INTERVAL="${CLAUDE_QUOTA_POLL_INTERVAL:-3600}"  # 60 min between polls
CLAUDE_QUOTA_MAX_POLLS="${CLAUDE_QUOTA_MAX_POLLS:-8}"             # max 8 h wait total

# ── Path resolution ───────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUITE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# ── Arg parsing ───────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --max-iterations) MAX_ITERATIONS="$2"; shift 2 ;;
        --scenario)       SCENARIO="$2";       shift 2 ;;
        --suite-root)     SUITE_ROOT="$2";     shift 2 ;;
        --orchestrator)   ORCHESTRATOR="$2";   shift 2 ;;
        --claude-bin)     CLAUDE_BIN="$2";     shift 2 ;;
        --copilot-bin)    COPILOT_BIN="$2";    shift 2 ;;
        --cursor-bin)     CURSOR_BIN="$2";     shift 2 ;;
        --opencode-bin)   OPENCODE_BIN="$2";   shift 2 ;;
        --model)          MODEL="$2";          shift 2 ;;
        --run-dir)        RUN_DIR="$2";        shift 2 ;;
        --resume)         RESUME=1;            shift ;;
        --dry-run)        DRY_RUN=1;           shift ;;
        -h|--help)
            sed -n '/^# tools\//,/^$/{/^set -/q; s/^# \?//; p}' "$0" | head -30
            exit 0
            ;;
        *) fail "Unknown argument: $1"; exit 1 ;;
    esac
done

TESTS_DIR="$SUITE_ROOT/tests"
RUN_BASE="$SUITE_ROOT/doc/reports/e2e-loop"

# Resolve STATE_DIR: explicit --run-dir > --resume (latest) > new timestamped dir
if [ -n "$RUN_DIR" ]; then
    STATE_DIR="$RUN_DIR"
elif [ "$RESUME" -eq 1 ]; then
    _latest=$(ls -d "$RUN_BASE"/[0-9]*/state.json 2>/dev/null | sort -r | head -1)
    if [ -z "$_latest" ]; then
        fail "--resume: no existing timestamped run found in $RUN_BASE"; exit 1
    fi
    STATE_DIR=$(dirname "$_latest")
    log "Resuming run: $STATE_DIR"
else
    STATE_DIR="$RUN_BASE/$(date +%Y%m%d-%H%M%S)"
fi
STATE_FILE="$STATE_DIR/state.json"

# ── Pre-flight checks ─────────────────────────────────────────────────────────
preflight() {
    local ok=1

    command -v python3 &>/dev/null || { fail "python3 not found"; ok=0; }
    [ -f "$TESTS_DIR/test.sh" ]    || { fail "tests/test.sh not found at $TESTS_DIR"; ok=0; }

    case "$ORCHESTRATOR" in
        copilot)
            if ! command -v "$COPILOT_BIN" &>/dev/null; then
                fail "copilot binary not found: $COPILOT_BIN"
                warn "Set COPILOT_BIN env var or use --copilot-bin"
                ok=0
            fi ;;
        cursor)
            if ! command -v "$CURSOR_BIN" &>/dev/null; then
                fail "cursor binary (agent) not found: $CURSOR_BIN"
                warn "Set CURSOR_BIN env var or use --cursor-bin"
                ok=0
            fi ;;
        opencode)
            if ! command -v "$OPENCODE_BIN" &>/dev/null; then
                fail "opencode binary not found: $OPENCODE_BIN"
                warn "Set OPENCODE_BIN env var or use --opencode-bin"
                ok=0
            fi ;;
        *)
            if ! command -v "$CLAUDE_BIN" &>/dev/null; then
                fail "claude binary not found: $CLAUDE_BIN"
                warn "Set CLAUDE_BIN env var or use --claude-bin"
                ok=0
            fi ;;
    esac

    [ "$ok" -eq 1 ] || exit 1
}

# ── State management ──────────────────────────────────────────────────────────
state_init() {
    mkdir -p "$STATE_DIR"
    python3 - <<EOF
import json, datetime
state = {
    "iteration":       0,
    "max_iterations":  $MAX_ITERATIONS,
    "scenario":        "$SCENARIO",
    "started_at":      datetime.datetime.now().isoformat(),
    "status":          "running",
    "stop_reason":     None,
    "improvements_applied": []
}
with open("$STATE_FILE", "w") as f:
    json.dump(state, f, indent=2)
print("State initialised: $STATE_FILE")
EOF
}

state_get() {
    # Usage: state_get <key>
    python3 -c "import json; s=json.load(open('$STATE_FILE')); print(s.get('$1',''))"
}

state_update() {
    # Usage: state_update <python-expression-on-s>
    # e.g.: state_update "s['status'] = 'done'"
    python3 -c "
import json
path = '$STATE_FILE'
with open(path) as f: s = json.load(f)
$1
with open(path, 'w') as f: json.dump(s, f, indent=2)
"
}

# ── Test runner ───────────────────────────────────────────────────────────────
# Runs one tool's E2E suite; captures output + JSON report.
# Returns 0 even on test failure (failures are expected and reported).
run_tool_test() {
    local tool="$1"     # copilot|cursor|opencode|claude_code
    local iter="$2"
    local suite_name=""
    local timeout_env=""

    case "$tool" in
        copilot)    suite_name="agentic-e2e-copilot-cli-autopilot" ;;
        cursor)     suite_name="agentic-e2e-cursor-cli-autopilot" ;;
        opencode)   suite_name="agentic-e2e-opencode-cli-autopilot" ;;
        claude_code) suite_name="agentic-e2e-claude-code-autopilot" ;;
        *) fail "Unknown tool: $tool"; return 1 ;;
    esac

    local out_log="$STATE_DIR/iteration-${iter}-${tool}-pytest.log"
    local json_file="$STATE_DIR/iteration-${iter}-${tool}-pytest.json"

    log "Running $tool ($suite_name) ..."

    if [ "$DRY_RUN" -eq 1 ]; then
        warn "[dry-run] would run: bash tests/test.sh $suite_name -k $SCENARIO"
        echo '{"summary":{"total":0},"exitcode":0}' > "$json_file"
        return 0
    fi

    local start
    start=$(date +%s)

    set +e
    (
        cd "$SUITE_ROOT"
        bash "$TESTS_DIR/test.sh" \
            "$suite_name" \
            -k "$SCENARIO" \
            --json-report \
            2>&1
    ) | tee "$out_log"
    local rc=${PIPESTATUS[0]}
    set -e

    local end
    end=$(date +%s)
    local duration=$(( end - start ))

    # Always synthesise JSON from the log (most reliable across test.sh versions)
    python3 -c "
import json, re
log = open('$out_log').read()

# pytest summary line: e.g. '17 passed, 1 failed in 268.4s'
passed  = sum(int(m) for m in re.findall(r'(\d+) passed',  log))
failed  = sum(int(m) for m in re.findall(r'(\d+) failed',  log))
skipped = sum(int(m) for m in re.findall(r'(\d+) skipped', log))
# Use only the final summary line to avoid 3x overcounting (header + Interrupted + summary)
_err_m  = re.search(r'(\d+) error[s]? in \d', log)
errors  = int(_err_m.group(1)) if _err_m else 0

# Duration from summary line
dur_match = re.search(r'in (\d+\.?\d*)s', log)
duration = float(dur_match.group(1)) if dur_match else $duration

# Quota / usage-limit detection
quota_error = 'out of usage' in log.lower() or 'switch to auto' in log.lower()
claude_quota_error = 'usage limit' in log.lower() or 'rate limit' in log.lower()
timeout_error = 'TIMEOUT after' in log
auth_error = $rc == 77 or ('not authenticated' in log.lower() and 'claude auth login' in log.lower())

d = {
    'exitcode': $rc,
    'duration': duration,
    'summary': {
        'passed': passed, 'failed': failed,
        'error': errors, 'skipped': skipped,
        'total': passed + failed + errors + skipped
    },
    'tool': '$tool',
    'log_file': '$out_log',
    'quota_error': quota_error,
    'claude_quota_error': claude_quota_error,
    'timeout_error': timeout_error,
    'auth_error': auth_error,
}
print(json.dumps(d, indent=2))
" > "$json_file"

    if [ "$rc" -eq 0 ]; then
        ok "$tool: PASS (${duration}s)"
    else
        warn "$tool: FAIL (exit $rc, ${duration}s) — see $out_log"
    fi
    return 0   # always succeed; failures are analysed by Claude
}

# ── Artifact collector ────────────────────────────────────────────────────────
collect_artifacts() {
    local iter="$1"
    local out="$STATE_DIR/iteration-${iter}-artifacts.txt"

    log "Collecting artifact listings ..."
    {
        echo "# Artifact Listings — Iteration ${iter}"
        echo "# Generated: $(date -Iseconds)"
        echo ""

        for tool_dir in \
            "$SUITE_ROOT/dx-runtime/dx_stream/dx-agentic-dev" \
            "$SUITE_ROOT/dx-runtime/dx_app/dx-agentic-dev"
        do
            [ -d "$tool_dir" ] || continue
            echo "## $tool_dir"
            find "$tool_dir" -maxdepth 2 -newer "$STATE_FILE" \
                \( -type f -o -type d \) \
                | sort \
                | while read -r p; do
                    if [ -f "$p" ]; then
                        wc -l < "$p" | tr -d ' '
                        echo "L  $p"
                    else
                        echo "D  $p"
                    fi
                done 2>/dev/null || true
            echo ""
        done
    } > "$out"
    ok "Artifacts → $out"
}

# ── Claude: generate report ───────────────────────────────────────────────────
generate_report() {
    local iter="$1"
    local report_file="$STATE_DIR/iteration-${iter}-report.md"

    log "Generating comparison report (iteration $iter) ..."

    if [ "$DRY_RUN" -eq 1 ]; then
        warn "[dry-run] would call claude to generate report"
        echo "# Dry-run report placeholder" > "$report_file"
        return 0
    fi

    # Write context JSON to a file (avoids ARG_MAX when passing to claude)
    local context_file="$STATE_DIR/iteration-${iter}-context.json"
    python3 - <<EOF
import json, pathlib

iter      = $iter
state_dir = pathlib.Path("$STATE_DIR")
summaries = {}
for tool in ("copilot", "cursor", "opencode", "claude_code"):
    jf = state_dir / f"iteration-{iter}-{tool}-pytest.json"
    try:    summaries[tool] = json.loads(jf.read_text()) if jf.exists() else {"error": "not found"}
    except: summaries[tool] = {"error": "parse error"}

state = json.loads(pathlib.Path("$STATE_FILE").read_text())
ctx = {
    "iteration":  iter,
    "scenario":   "$SCENARIO",
    "suite_root": "$SUITE_ROOT",
    "report_out":  str(state_dir / f"iteration-{iter}-report.md"),
    "changes_out": str(state_dir / f"iteration-{iter}-changes.md"),
    "result_out":  str(state_dir / f"iteration-{iter}-result.json"),
    "pytest_json_files":    [str(state_dir / f"iteration-{iter}-{t}-pytest.json")
                             for t in ("copilot","cursor","opencode","claude_code")],
    "pytest_log_files":     [str(state_dir / f"iteration-{iter}-{t}-pytest.log")
                             for t in ("copilot","cursor","opencode","claude_code")],
    "artifact_listing_file": str(state_dir / f"iteration-{iter}-artifacts.txt"),
    "state_file":            "$STATE_FILE",
    "test_summaries":        summaries,
    "improvements_applied_so_far": state.get("improvements_applied", []),
}
pathlib.Path("$context_file").write_text(json.dumps(ctx, indent=2))
print("Context written to $context_file")
EOF

    # Short prompt — Claude reads all large data via its tools (Read/Bash)
    local prompt="You are an automated analysis agent for the Agentic E2E test suite.

Read the context from this file first: $context_file

Then read the pytest log files and artifact listing referenced in that context.

Write a comparison report to the path in context['report_out'].

The report must:
1. Summarise pass/fail/skip for each of the 4 tools with duration
2. Compare generated artifact files (file list, line counts) for each tool
3. Assess code quality where artifacts exist (pipeline.py, session.json fields, README)
4. Root-cause analysis for any failures (quota, timeout, code bug)
5. A Recommendations section — tag each item with one of:
   [timeout] [test_coverage] [runner_code] [skill_md] [tooling]
   (tooling = account/quota issues NOT fixable in code)

Previous reports for reference style: $SUITE_ROOT/doc/reports/"

    run_orchestrator "$STATE_DIR/iteration-${iter}-report-gen.log" "$prompt" || true

    if [ -f "$report_file" ]; then
        ok "Report → $report_file"
        translate_to_korean "$report_file"
    else
        warn "Report file not created — check $STATE_DIR/iteration-${iter}-report-gen.log"
    fi
}

# ── Claude: apply improvements ────────────────────────────────────────────────
apply_improvements() {
    local iter="$1"
    local report_file="$STATE_DIR/iteration-${iter}-report.md"
    local result_file="$STATE_DIR/iteration-${iter}-result.json"
    local changes_file="$STATE_DIR/iteration-${iter}-changes.md"

    log "Applying improvements (iteration $iter) ..."

    if [ "$DRY_RUN" -eq 1 ]; then
        warn "[dry-run] would call claude to apply improvements"
        echo '{"done":false,"stop_reason":null,"applied":[]}' > "$result_file"
        return 0
    fi

    if [ ! -f "$report_file" ]; then
        fail "Report file missing: $report_file — skipping improvement step, will retry next iteration"
        echo '{"done":false,"stop_reason":"report_missing","applied":[]}' > "$result_file"
        return 0
    fi

    # Write already-applied list to a file (avoids ARG_MAX)
    local applied_file="$STATE_DIR/iteration-${iter}-applied.json"
    python3 -c "
import json
s = json.load(open('$STATE_FILE'))
import pathlib
pathlib.Path('$applied_file').write_text(json.dumps(s.get('improvements_applied', []), indent=2))
"

    # Short prompt — Claude reads report and applied list via its tools
    local prompt="You are an automated improvement agent for the Agentic E2E test suite.
Suite root: $SUITE_ROOT

## Files to read first
- Comparison report: $report_file
- Already applied improvements: $applied_file

## Task
1. Read both files above.
2. Extract recommendations tagged [timeout], [test_coverage], [runner_code], [skill_md].
   Skip [tooling] items (account/quota — not fixable in code).
3. Skip improvements already in the applied list.
4. If nothing new remains → write result JSON with done=true.
5. Apply each new improvement (edit the relevant source files).
   Rule: edits under .deepx/ MUST be followed by: dx-agentic-gen generate
6. Write a changes log (one section per change) to: $changes_file
7. FINAL action: write this JSON to $result_file
   {\"done\": bool, \"stop_reason\": str|null, \"applied\": [{\"category\": \"...\", \"description\": \"...\"}]}
   IMPORTANT: set done=true ONLY when you applied zero improvements (applied list is empty).
   If you applied any improvements, set done=false so tests are re-run to verify them.

Begin now."

    run_orchestrator "$STATE_DIR/iteration-${iter}-improve.log" "$prompt" || true

    if [ -f "$result_file" ]; then
        ok "Result JSON → $result_file"
    else
        warn "Result JSON not written — treating iteration as inconclusive"
        echo '{"done":false,"stop_reason":"result_not_written","applied":[]}' > "$result_file"
    fi
}

# ── Post-iteration: read result + update state ────────────────────────────────
process_result() {
    # Returns "done" or "continue" via stdout; never exits non-zero.
    local iter="$1"
    local result_file="$STATE_DIR/iteration-${iter}-result.json"

    if [ ! -f "$result_file" ]; then
        warn "No result JSON for iteration $iter — assuming not done"
        echo "continue"
        return 0
    fi

    python3 - "$iter" "$result_file" "$STATE_FILE" <<'PYEOF'
import json, sys

iter        = int(sys.argv[1])
result_file = sys.argv[2]
state_file  = sys.argv[3]

try:
    with open(result_file) as f:
        result = json.load(f)
except Exception as e:
    print(f"continue  # could not parse result JSON: {e}", file=sys.stderr)
    print("continue")
    sys.exit(0)

with open(state_file) as f:
    state = json.load(f)

raw_applied = result.get("applied", [])
# Normalise: Claude sometimes writes strings (e.g. ["R56", "R57"]) instead of dicts
applied_this = []
for item in raw_applied:
    if isinstance(item, dict):
        applied_this.append(item)
    else:
        applied_this.append({"category": "", "description": str(item)})

for item in applied_this:
    state["improvements_applied"].append({"iteration": iter, **item})

# If improvements were applied, always continue to re-run tests — even if Claude
# set done=true (Claude means "I found nothing MORE", but tests must re-run to verify).
done   = bool(result.get("done", False)) and not applied_this
reason = result.get("stop_reason")
state["iteration"] = iter + 1

if done:
    state["status"]      = "done"
    state["stop_reason"] = reason or "no_actionable_improvements"

with open(state_file, "w") as f:
    json.dump(state, f, indent=2)

print("done" if done else "continue")
for a in applied_this:
    print(f"  [{a.get('category','')}] {a.get('description','')}")
PYEOF
}

# ── Korean translation helper ─────────────────────────────────────────────────
# Translates a markdown file to Korean and writes a *-KO.md sibling.
translate_to_korean() {
    local src="$1"
    local dst="${src%.md}-KO.md"

    if [ "$DRY_RUN" -eq 1 ]; then
        warn "[dry-run] would translate $src → $dst"
        return 0
    fi
    [ -f "$src" ] || { warn "translate_to_korean: source not found: $src"; return 0; }

    log "Translating to Korean: $(basename "$src") → $(basename "$dst")"
    local prompt="Translate the following Markdown document into Korean.
Rules:
- Preserve all Markdown structure (headings, lists, code blocks, bold, italic, tables).
- Keep technical terms, file paths, code identifiers, and proper nouns in English.
- Output ONLY the translated Markdown — no preamble, no explanation.

Source file: $src

Write the translated content directly to: $dst"

    local _ko_log="${dst%.md}.log"
    run_orchestrator "$_ko_log" "$prompt" || true

    if [ -f "$dst" ]; then
        ok "KO → $dst"
    else
        warn "KO translation not written: $dst"
    fi
}

# ── Final summary ─────────────────────────────────────────────────────────────
write_summary() {
    local summary_file="$STATE_DIR/LOOP_SUMMARY.md"
    log "Writing final summary → $summary_file"

    python3 - <<EOF
import json, datetime, pathlib

state = json.load(open("$STATE_FILE"))
lines = []
lines.append("# Agentic E2E Improvement Loop — Final Summary")
lines.append("")
lines.append(f"**Started:** {state.get('started_at','?')}")
lines.append(f"**Finished:** {datetime.datetime.now().isoformat()}")
lines.append(f"**Iterations run:** {state.get('iteration', 0)}")
lines.append(f"**Stop reason:** {state.get('stop_reason','?')}")
lines.append("")
lines.append("## Improvements Applied")
lines.append("")
applied = state.get("improvements_applied", [])
if applied:
    for i, a in enumerate(applied, 1):
        lines.append(f"{i}. **[{a.get('category','')}]** {a.get('description','')} *(iter {a.get('iteration','?')})*")
else:
    lines.append("*(none)*")
lines.append("")
lines.append("## Per-Iteration Reports")
lines.append("")
state_dir = pathlib.Path("$STATE_DIR")
for rpt in sorted(state_dir.glob("iteration-*-report.md")):
    lines.append(f"- [{rpt.name}]({rpt.name})")

pathlib.Path("$summary_file").write_text("\\n".join(lines) + "\\n")
print("Summary written.")
EOF
    ok "Summary → $summary_file"
    translate_to_korean "$summary_file"
}

# ── Main loop ─────────────────────────────────────────────────────────────────
main() {
    sep
    log "Agentic E2E Self-Improvement Loop"
    log "Suite root   : $SUITE_ROOT"
    log "Scenario     : $SCENARIO"
    log "Max iter     : $MAX_ITERATIONS"
    case "$ORCHESTRATOR" in
        copilot)  log "Orchestrator : copilot ($COPILOT_BIN, model=$MODEL)" ;;
        cursor)   log "Orchestrator : cursor ($CURSOR_BIN, model=$MODEL)" ;;
        opencode) log "Orchestrator : opencode ($OPENCODE_BIN, model=$MODEL)" ;;
        *)        log "Orchestrator : claude ($CLAUDE_BIN, model=$MODEL)" ;;
    esac
    log "State dir    : $STATE_DIR"
    sep

    preflight

    if [ "$RESUME" -eq 1 ] && [ -f "$STATE_FILE" ]; then
        log "Resuming from existing state: $STATE_FILE"
        state_update "s['status'] = 'running'; s['max_iterations'] = $MAX_ITERATIONS; s['stop_reason'] = None"
    else
        state_init
    fi

    local iter
    iter=$(state_get "iteration")

    while true; do
        iter=$(state_get "iteration")
        sep
        log "ITERATION $((iter + 1)) / $MAX_ITERATIONS"
        sep

        # Stop: max iterations
        if [ "$iter" -ge "$MAX_ITERATIONS" ]; then
            warn "Max iterations ($MAX_ITERATIONS) reached — stopping."
            state_update "s['status'] = 'done'; s['stop_reason'] = 'max_iterations_reached'"
            break
        fi

        # Step 1: Run all 4 E2E tests in parallel
        sep; log "Step 1/4 — Running E2E tests (parallel)"
        local _pids=()
        for tool in copilot cursor opencode claude_code; do
            log "  → starting $tool ..."
            run_tool_test "$tool" "$iter" >/dev/null &
            _pids+=($!)
        done
        log "All 4 tool tests running in parallel — waiting ..."
        for _pid in "${_pids[@]}"; do
            wait "$_pid" || true
        done
        # Print per-tool summary from JSON files
        for tool in copilot cursor opencode claude_code; do
            local _jf="$STATE_DIR/iteration-${iter}-${tool}-pytest.json"
            if [ -f "$_jf" ]; then
                local _rc _dur
                _rc=$(python3 -c "import json; d=json.load(open('$_jf')); print(d.get('exitcode','?'))")
                _dur=$(python3 -c "import json; d=json.load(open('$_jf')); print(int(d.get('duration',0)))")
                if [ "$_rc" = "0" ]; then
                    ok "$tool: PASS (${_dur}s)"
                else
                    warn "$tool: FAIL (exit $_rc, ${_dur}s) — see $_jf"
                fi
            fi
        done

        # Step 2: Collect artifact listings
        sep; log "Step 2/4 — Collecting artifacts"
        collect_artifacts "$iter"

        # Step 3: Generate comparison report
        sep; log "Step 3/4 — Generating report"
        generate_report "$iter"

        # Step 4: Apply improvements
        sep; log "Step 4/4 — Applying improvements"
        apply_improvements "$iter"

        # Guard: regenerate all platform outputs after improvements to fix any generator drift
        # (claude -p subprocess may bypass PreToolUse hooks and directly edit .github/ outputs)
        log "Post-improvement: running dx-agentic-gen generate to sync all platform outputs ..."
        for _repo in dx-runtime/dx_stream dx-runtime/dx_app; do
            if [ -d "$SUITE_ROOT/$_repo/.deepx" ]; then
                ( cd "$SUITE_ROOT" && dx-agentic-gen generate --repo "$_repo" 2>&1 ) \
                    | grep -E "CHANGED|UNCHANGED|ERROR|Generated|error" || true
            fi
        done

        # Process result → decide whether to continue
        local decision=""
        decision=$(process_result "$iter")

        if echo "$decision" | grep -q "^done"; then
            ok "No new improvements — loop complete."
            break
        fi

        log "Improvements applied this iteration. Continuing ..."
        echo ""
    done

    write_summary

    sep
    local status
    status=$(state_get "status")
    local stop
    stop=$(state_get "stop_reason")
    ok "Loop finished — status: $status | reason: $stop"
    log "Results in: $STATE_DIR"
    sep
}

main "$@"
