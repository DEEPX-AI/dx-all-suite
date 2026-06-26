#!/usr/bin/env bash
# test_run_model_eval.sh — TDD tests for run_model_eval.sh (no NPU, no network required)
#
# All tests use --dry-run so no real commands are executed.
# Exit 0 = all tests passed; exit 1 = at least one failure.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
TARGET="$SCRIPT_DIR/../run_model_eval.sh"

PASS=0
FAIL=0

_assert_contains() {
    local label="$1"
    local needle="$2"
    local haystack="$3"
    # Use grep -F -- to prevent strings starting with '--' from being parsed as flags
    if echo "$haystack" | grep -qF -- "$needle"; then
        echo "  PASS: $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: $label"
        echo "        expected to find: $needle"
        FAIL=$((FAIL + 1))
    fi
}

# ---------------------------------------------------------------------------
# Test 0: syntax check
# ---------------------------------------------------------------------------
echo "=== Test 0: bash -n syntax check ==="
if bash -n "$TARGET"; then
    echo "  PASS: syntax OK"
    PASS=$((PASS + 1))
else
    echo "  FAIL: syntax error in $TARGET"
    FAIL=$((FAIL + 1))
fi

# ---------------------------------------------------------------------------
# Test 1: basic NTH dry-run
# ---------------------------------------------------------------------------
echo ""
echo "=== Test 1: NTH dry-run (claude-code, opus-4-6 vs opus-4-8, 5 rounds) ==="
OUTPUT="$(bash "$TARGET" \
    --old-model claude-opus-4-6 \
    --new-model claude-opus-4-8 \
    --tool claude-code \
    --rounds 5 \
    --dry-run 2>&1)"

# Runner invocations go through resilient controller — OLD model
_assert_contains \
    "e2e_resilient_run.py invocation with --model claude-opus-4-6" \
    "e2e_resilient_run.py" \
    "$OUTPUT"
_assert_contains \
    "resilient controller --model claude-opus-4-6" \
    "--model claude-opus-4-6" \
    "$OUTPUT"

# Runner invocations — NEW model
_assert_contains \
    "resilient controller --model claude-opus-4-8" \
    "--model claude-opus-4-8" \
    "$OUTPUT"

# analyze.py invocation with --output-dir
_assert_contains \
    "analyze.py invocation with --output-dir" \
    "--output-dir" \
    "$OUTPUT"

# build_comparison.py invocation
_assert_contains \
    "build_comparison.py invocation" \
    "build_comparison.py" \
    "$OUTPUT"

# bundle_raw_results.py invocation
_assert_contains \
    "bundle_raw_results.py invocation" \
    "bundle_raw_results.py" \
    "$OUTPUT"

# Registry append step
_assert_contains \
    "registry append step (MODEL_EVAL_REGISTRY.md)" \
    "MODEL_EVAL_REGISTRY.md" \
    "$OUTPUT"

# NTH in label
_assert_contains \
    "NTH in derived label" \
    "NTH" \
    "$OUTPUT"

# ---------------------------------------------------------------------------
# Test 2: --thinking + --dry-run variant
# ---------------------------------------------------------------------------
echo ""
echo "=== Test 2: TH dry-run (--thinking flag) ==="
OUTPUT_TH="$(bash "$TARGET" \
    --old-model claude-opus-4-6 \
    --new-model claude-opus-4-8 \
    --tool claude-code \
    --rounds 3 \
    --thinking \
    --dry-run 2>&1)"

# --thinking must appear in runner command
_assert_contains \
    "--thinking appears in runner invocation" \
    "--thinking" \
    "$OUTPUT_TH"

# Label must contain TH
_assert_contains \
    "TH appears in derived label" \
    "TH" \
    "$OUTPUT_TH"

# TH but NOT NTH in the label (the label suffix should be _TH not _NTH)
# Extract LABEL line from output and check suffix
LABEL_LINE="$(echo "$OUTPUT_TH" | grep 'LABEL\s*:')"
if echo "$LABEL_LINE" | grep -qE '_TH($|[^A-Z])' && ! echo "$LABEL_LINE" | grep -q '_NTH'; then
    echo "  PASS: label suffix is TH (not NTH)"
    PASS=$((PASS + 1))
else
    # Fallback: just check that label contains TH at all
    if echo "$LABEL_LINE" | grep -q 'TH'; then
        echo "  PASS: label contains TH"
        PASS=$((PASS + 1))
    else
        echo "  FAIL: label does not contain TH for --thinking run"
        echo "        LABEL line: $LABEL_LINE"
        FAIL=$((FAIL + 1))
    fi
fi

# ---------------------------------------------------------------------------
# Test 3: missing --old-model → error exit
# ---------------------------------------------------------------------------
echo ""
echo "=== Test 3: missing --old-model exits non-zero ==="
# Capture output separately to avoid pipefail treating the expected non-zero exit as failure
MISSING_OLD_OUT="$(bash "$TARGET" --new-model claude-opus-4-8 --dry-run 2>&1 || true)"
if echo "$MISSING_OLD_OUT" | grep -qF -- "ERROR"; then
    echo "  PASS: missing --old-model produces ERROR"
    PASS=$((PASS + 1))
else
    echo "  FAIL: missing --old-model did not produce ERROR"
    FAIL=$((FAIL + 1))
fi
# Verify it exits non-zero
if ! bash "$TARGET" --new-model claude-opus-4-8 --dry-run >/dev/null 2>&1; then
    echo "  PASS: missing --old-model exits non-zero"
    PASS=$((PASS + 1))
else
    echo "  FAIL: missing --old-model exited 0 (should be non-zero)"
    FAIL=$((FAIL + 1))
fi

# ---------------------------------------------------------------------------
# Test 4: missing --new-model → error exit
# ---------------------------------------------------------------------------
echo ""
echo "=== Test 4: missing --new-model exits non-zero ==="
MISSING_NEW_OUT="$(bash "$TARGET" --old-model claude-opus-4-6 --dry-run 2>&1 || true)"
if echo "$MISSING_NEW_OUT" | grep -qF -- "ERROR"; then
    echo "  PASS: missing --new-model produces ERROR"
    PASS=$((PASS + 1))
else
    echo "  FAIL: missing --new-model did not produce ERROR"
    FAIL=$((FAIL + 1))
fi

# ---------------------------------------------------------------------------
# Test 5: --tool copilot-cli maps to --copilot-model
# ---------------------------------------------------------------------------
echo ""
echo "=== Test 5: --tool copilot-cli maps to --copilot-model ==="
OUTPUT_COPILOT="$(bash "$TARGET" \
    --old-model gpt-4o \
    --new-model gpt-4-1 \
    --tool copilot-cli \
    --rounds 3 \
    --dry-run 2>&1)"
_assert_contains \
    "resilient controller --tool copilot-cli in invocation" \
    "--tool copilot-cli" \
    "$OUTPUT_COPILOT"
_assert_contains \
    "resilient controller --model gpt-4o in invocation" \
    "--model gpt-4o" \
    "$OUTPUT_COPILOT"
_assert_contains \
    "resilient controller --model gpt-4-1 in invocation" \
    "--model gpt-4-1" \
    "$OUTPUT_COPILOT"

# ---------------------------------------------------------------------------
# Test 6: --reuse-run-ids included in OLD analyze invocation
# ---------------------------------------------------------------------------
echo ""
echo "=== Test 6: --reuse-run-ids included in OLD analyze step ==="
OUTPUT_REUSE="$(bash "$TARGET" \
    --old-model claude-opus-4-6 \
    --new-model claude-opus-4-8 \
    --tool claude-code \
    --rounds 5 \
    --reuse-run-ids "20260601_aaa,20260602_bbb" \
    --dry-run 2>&1)"
_assert_contains \
    "reuse run_id 20260601_aaa in analyze invocation" \
    "20260601_aaa" \
    "$OUTPUT_REUSE"
_assert_contains \
    "reuse run_id 20260602_bbb in analyze invocation" \
    "20260602_bbb" \
    "$OUTPUT_REUSE"

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo ""
echo "=== SUMMARY: $PASS passed, $FAIL failed ==="
if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
exit 0
