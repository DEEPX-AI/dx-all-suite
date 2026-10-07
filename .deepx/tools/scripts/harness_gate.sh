#!/usr/bin/env bash
#
# harness_gate.sh — the dx-agent-dev harness gate, one entry point for CI AND
# developers. The suite gate workflows (.github/workflows/dx-agent-dev-gate-ghes.yml
# and -cloud.yml, job `harness-gate`) call exactly these stages, so a green
# `harness_gate.sh all` on your machine means a green gate in CI (same commands,
# same working directory = suite root, resolved from this script's location).
#
# Usage:
#   harness_gate.sh <stage> [--python PY]
#
#   deps     python is >= 3.8 and has jinja2 + pyyaml + pytest + rich (prints a hint if not)
#   check    bash .deepx/tools/scripts/run_all.sh check        (drift, all 5 levels)
#   lint     bash .deepx/tools/scripts/run_all.sh lint         (EN/KO fragment parity)
#   tests    python -m pytest --rootdir=<suite> .deepx/tests/conformance .deepx/tools/tests .deepx/e2e/tests
#   e2e-sh   bash .deepx/e2e/tests/test_run_model_eval.sh      (run_model_eval.sh dry-run tests)
#   all      deps, then check, lint, tests, e2e-sh — keeps going after a failure,
#            prints a summary, exits 1 if any stage failed
#
#   --python PY   interpreter to use (default: $DX_GATE_PYTHON, else python3). When PY
#                 is a path, its bin dir is prepended to PATH so run_all.sh's `python3`
#                 resolves to the same interpreter.
#
# Exit codes: 0 pass · 1 a stage failed · 2 usage / setup error
set -uo pipefail

SUITE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd -P)"
PY="${DX_GATE_PYTHON:-python3}"
STAGE=""

usage() {
    sed -n '2,/^set -uo pipefail/p' "${BASH_SOURCE[0]}" | sed '$d' | sed 's/^# \{0,1\}//'
}

while [ $# -gt 0 ]; do
    case "$1" in
        --python)
            [ $# -ge 2 ] || { echo "Usage error: --python needs a value" >&2; exit 2; }
            PY="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        deps|check|lint|tests|e2e-sh|all)
            [ -z "$STAGE" ] || { echo "Usage error: only one stage allowed" >&2; usage >&2; exit 2; }
            STAGE="$1"; shift ;;
        *) echo "Usage error: unknown argument '$1'" >&2; usage >&2; exit 2 ;;
    esac
done
[ -n "$STAGE" ] || { echo "Usage error: a stage is required" >&2; usage >&2; exit 2; }

if [[ "$PY" == */* ]]; then
    [ -x "$PY" ] || { echo "Setup error: python '$PY' is not executable" >&2; exit 2; }
    PATH="$(cd "$(dirname "$PY")" && pwd -P):$PATH"
    export PATH
fi
cd "$SUITE_ROOT" || exit 2
echo "[harness-gate] suite=$SUITE_ROOT python=$("$PY" -c 'import sys; print(sys.executable)' 2>/dev/null || echo "$PY")"

stage_deps() {
    # Floor: Python 3.8 (the GHES self-hosted pool includes Ubuntu 20.04 runners).
    # Decided from `--version` so a python that cannot even start still reaches
    # the module hint below instead of a misleading "too old".
    local ver; ver="$("$PY" --version 2>&1 | head -n1)"
    case "$ver" in
        Python\ [12].*|Python\ 3.[0-7]|Python\ 3.[0-7].*)
            echo "[harness-gate] python too old: $ver ($PY) — the gate needs Python >= 3.8" >&2
            echo "  pass a newer interpreter: $0 $STAGE --python /path/to/python3.8+  (or set DX_GATE_PYTHON)" >&2
            return 1 ;;
    esac
    if "$PY" -c "import jinja2, yaml, pytest, rich" 2>/dev/null; then
        "$PY" -c "import jinja2, yaml, pytest, rich, sys; from importlib.metadata import version; print(f'[harness-gate] deps OK: python {sys.version.split()[0]}, jinja2 {jinja2.__version__}, pyyaml {yaml.__version__}, pytest {pytest.__version__}, rich {version(\"rich\")}')"
        return 0
    fi
    echo "[harness-gate] deps MISSING for $PY — need jinja2, pyyaml (module 'yaml'), pytest, rich" >&2
    echo "  install:  $PY -m pip install 'jinja2>=3.1' 'pyyaml>=6.0' 'pytest>=8,<9' 'rich>=13'" >&2
    echo "  or (PEP 668 hosts): python3 -m venv .gate-venv && .gate-venv/bin/pip install 'jinja2>=3.1' 'pyyaml>=6.0' 'pytest>=8,<9' 'rich>=13' && $0 $STAGE --python .gate-venv/bin/python" >&2
    return 1
}
stage_check()  { bash .deepx/tools/scripts/run_all.sh check; }
stage_lint()   { bash .deepx/tools/scripts/run_all.sh lint; }
stage_tests()  { "$PY" -m pytest --rootdir=. .deepx/tests/conformance .deepx/tools/tests .deepx/e2e/tests -q --no-header -p no:cacheprovider; }
stage_e2e_sh() { bash .deepx/e2e/tests/test_run_model_eval.sh; }

run_stage() {  # run_stage <name>
    echo "=== [harness-gate] $1 ==="
    case "$1" in
        deps)   stage_deps ;;
        check)  stage_check ;;
        lint)   stage_lint ;;
        tests)  stage_tests ;;
        e2e-sh) stage_e2e_sh ;;
    esac
}

if [ "$STAGE" != "all" ]; then
    run_stage "$STAGE"
    exit $?
fi

run_stage deps || exit 1
declare -A RESULT=()
FAILED=0
for s in check lint tests e2e-sh; do
    if run_stage "$s"; then RESULT[$s]=PASS; else RESULT[$s]=FAIL; FAILED=1; fi
done
echo "=== [harness-gate] summary ==="
for s in check lint tests e2e-sh; do printf '  %-7s %s\n' "$s" "${RESULT[$s]}"; done
if [ "$FAILED" -ne 0 ]; then
    echo "[harness-gate] FAILED — drift? run: bash .deepx/tools/scripts/run_all.sh generate && bash .deepx/tools/scripts/run_all.sh check" >&2
    exit 1
fi
echo "[harness-gate] PASS"
