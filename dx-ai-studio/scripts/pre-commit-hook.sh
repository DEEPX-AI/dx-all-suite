#!/usr/bin/env bash
# DX AI Studio pre-commit hook — the Node-free stand-in for the ticket's Husky step.
#
# A hook has one job: be fast enough that nobody reaches for --no-verify. It runs
# only checks whose cost is proportional to the STAGED diff, plus the contract
# suites that catch the mistakes this repo actually makes (a missing pytest.ini,
# a workflow that stopped matching its contract, a quarantine entry sneaking in).
#
# The full gate stays where it belongs: scripts/run_ci.sh, in CI.
#
# Install:  bash scripts/install-hooks.sh
# Bypass :  git commit --no-verify
set -uo pipefail

# The hook is installed as a SYMLINK into .git/hooks, so BASH_SOURCE points at the
# link, not at this file. Resolving it is what keeps ROOT on the studio (without
# it ROOT becomes .git/, the venv is never found, and every staged path silently
# fails its -f test — the hook then passes everything).
_SELF="$(readlink -f "${BASH_SOURCE[0]}")"
ROOT="$(cd "$(dirname "$_SELF")/.." && pwd)"
cd "$ROOT"

PY="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY="$(command -v python3 || true)"
if [ -z "$PY" ]; then
  echo "pre-commit: no python3 found — skipping (commit allowed)" >&2
  exit 0
fi

fail=0
note() { printf '  %s\n' "$1"; }

# Staged files, relative to the studio root. Deleted files are excluded (ACMR).
mapfile -t staged < <(git diff --cached --name-only --diff-filter=ACMR -z \
  | tr '\0' '\n' | sed -n 's|^dx-ai-studio/||p')

if [ "${#staged[@]}" -eq 0 ]; then
  exit 0
fi

echo "pre-commit: checking ${#staged[@]} staged file(s) under dx-ai-studio/"

for f in "${staged[@]}"; do
  [ -f "$f" ] || continue
  case "$f" in
    *.py)
      if ! "$PY" -c "import py_compile,sys; py_compile.compile(sys.argv[1], doraise=True)" "$f" 2>/dev/null; then
        note "SYNTAX  $f"
        "$PY" -c "import py_compile,sys; py_compile.compile(sys.argv[1], doraise=True)" "$f" 2>&1 | tail -3
        fail=1
      fi
      ;;
    *.json)
      if ! "$PY" -c "import json,sys; json.load(open(sys.argv[1]))" "$f" 2>/dev/null; then
        note "JSON    $f"
        fail=1
      fi
      ;;
    *.sh)
      if ! bash -n "$f" 2>/dev/null; then
        note "BASH    $f"
        bash -n "$f" 2>&1 | tail -3
        fail=1
      fi
      ;;
  esac
done

# Contract suites: ~4s, and they are what actually breaks when someone edits
# run_ci.sh, pytest.ini or a workflow without updating its ledger.
if "$PY" -c "import pytest" 2>/dev/null; then
  if ! "$PY" -m pytest -q --tb=line -p no:cacheprovider \
      tests/test_pytest_infra_contract.py \
      tests/shared/test_ci_contracts.py > /tmp/dx-precommit-$$.log 2>&1; then
    note "CONTRACT tests/test_pytest_infra_contract.py or tests/shared/test_ci_contracts.py"
    tail -15 /tmp/dx-precommit-$$.log
    fail=1
  fi
  rm -f /tmp/dx-precommit-$$.log
else
  note "pytest not installed in $PY — contract checks skipped"
fi

if [ "$fail" -ne 0 ]; then
  echo ""
  echo "pre-commit FAILED. Fix the above, or bypass with: git commit --no-verify"
  exit 1
fi

echo "pre-commit OK"
exit 0
