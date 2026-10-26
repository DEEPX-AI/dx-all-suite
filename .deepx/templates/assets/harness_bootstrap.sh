#!/usr/bin/env bash
# harness_bootstrap.sh — acquire the dx-all-suite harness for a STANDALONE sub-repo
# checkout, so the real verification loop can run locally instead of only in CI.
#
# Why this exists: a standalone clone of dx_app / dx_stream / dx-runtime / dx-compiler
# has no .deepx/tools/ (the dx-agent-gen generator), no .deepx/templates/fragments/ and
# no .deepx/tests/ — those live only in dx-all-suite. Yet this repo's generated
# CLAUDE.md / AGENTS.md tell the agent to run `dx-agent-gen generate|check`. Without a
# suite those commands fail, and edits to .deepx/ ship as drift that only CI catches.
#
# Usage: bash .deepx/scripts/harness_bootstrap.sh [--check] [--suite-dir DIR]
#                                                 [--subrepo-path PATH] [--print-suite-dir]
#   --check             after resolving a suite, run the SAME verification CI's
#                       subrepo-gate runs: drift check + this repo's validate_framework.py
#   --suite-dir DIR     use this dx-all-suite checkout (also: $DX_SUITE_DIR)
#   --subrepo-path P    canonical nested path (default: inferred from the directory name)
#   --print-suite-dir   print "<resolved-dir><TAB><source>" and exit
#
# Resolution order: --suite-dir/$DX_SUITE_DIR -> parent-walk -> .dx-harness/suite cache
#                   -> shallow clone -> STOP(3)
# Scope note: --check deliberately does NOT run the suite conformance suite; those ~600
# checks are cross-level (they compare all 5 levels against each other) and cannot be
# satisfied when the other sub-repos are absent. Matching subrepo-gate exactly means
# "local green => CI green".
#
# Exit: 0 ok · 1 verification failed · 2 usage/config error · 3 no suite could be
#       acquired (HARD GATE — do not edit .deepx/ until this succeeds)
set -euo pipefail
PROG=harness-bootstrap
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
REPO_DIR="$(cd "$HERE/../.." && pwd -P)"      # <subrepo>/.deepx/scripts -> <subrepo>
CACHE="$REPO_DIR/.dx-harness"
SUITE_DIR="${DX_SUITE_DIR:-}"
SUBREPO_PATH=""
DO_CHECK=0
PRINT_ONLY=0

die2() { printf '[%s] ERROR: %s\n' "$PROG" "$*" >&2; exit 2; }
log()  { printf '[%s] %s\n' "$PROG" "$*"; }
usage() { sed -n '2,/^set -euo pipefail/p' "${BASH_SOURCE[0]}" | sed '$d' | sed 's/^# \{0,1\}//'; }

while [ $# -gt 0 ]; do
  case "$1" in
    --check) DO_CHECK=1; shift ;;
    --print-suite-dir) PRINT_ONLY=1; shift ;;
    --suite-dir) [ $# -ge 2 ] || die2 "--suite-dir needs a value"; SUITE_DIR="$2"; shift 2 ;;
    --subrepo-path) [ $# -ge 2 ] || die2 "--subrepo-path needs a value"; SUBREPO_PATH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) die2 "unknown argument '$1'" ;;
  esac
done

# A directory is a usable suite only if it has BOTH halves the generator needs.
is_suite() {
  [ -d "$1/.deepx/templates/fragments" ] &&
  [ -f "$1/.deepx/tools/src/dx_agent_dev_gen/cli.py" ]
}

if [ -z "$SUBREPO_PATH" ]; then
  case "$(basename "$REPO_DIR")" in
    dx_app)      SUBREPO_PATH="dx-runtime/dx_app" ;;
    dx_stream)   SUBREPO_PATH="dx-runtime/dx_stream" ;;
    dx-runtime)  SUBREPO_PATH="dx-runtime" ;;
    dx-compiler) SUBREPO_PATH="dx-compiler" ;;
    *) die2 "cannot infer the canonical sub-repo path from '$(basename "$REPO_DIR")' — pass --subrepo-path" ;;
  esac
fi

SOURCE=""

# 1. Explicit override — the documented escape hatch, works fully offline.
if [ -n "$SUITE_DIR" ]; then
  SUITE_DIR="$(cd "$SUITE_DIR" 2>/dev/null && pwd -P)" ||
    die2 "--suite-dir / \$DX_SUITE_DIR is not a directory"
  is_suite "$SUITE_DIR" ||
    die2 "$SUITE_DIR is not a dx-all-suite checkout (needs .deepx/templates/fragments and .deepx/tools/src/dx_agent_dev_gen/cli.py)"
  SOURCE="explicit"
fi

# 2. Parent-walk — the normal nested-submodule case: zero download.
if [ -z "$SOURCE" ]; then
  d="$REPO_DIR"
  while [ "$d" != "/" ]; do
    if is_suite "$d"; then SUITE_DIR="$d"; SOURCE="local"; break; fi
    d="$(dirname "$d")"
  done
fi

# 3. Previously acquired cache — second and later runs are offline and instant.
if [ -z "$SOURCE" ] && is_suite "$CACHE/suite"; then
  SUITE_DIR="$(cd "$CACHE/suite" && pwd -P)"
  SOURCE="cache"
fi

# 4. Shallow clone — the true standalone case.
if [ -z "$SOURCE" ] && [ "${DX_HARNESS_NO_CLONE:-0}" != "1" ]; then
  origin="$(git -C "$REPO_DIR" config --get remote.origin.url 2>/dev/null || true)"
  if [ -z "$origin" ]; then
    log "no remote.origin.url in $REPO_DIR — cannot derive a suite url to clone; pass --suite-dir or set DX_SUITE_DIR"
  else
    # swap the last path component for dx-all-suite, preserving any .git suffix. (Plain string ops:
    # the former sed `[^/:]+(\.git)?$` was greedy and swallowed the suffix, so `…/dx-all-suite.git`
    # became `…/dx-all-suite` and was cloned instead of being recognised as unchanged — PR #91 review.)
    suffix=""; case "$origin" in *.git) suffix=".git" ;; esac
    base="${origin%.git}"
    case "$base" in */*) suite_url="${base%/*}/dx-all-suite$suffix" ;; *) suite_url="" ;; esac
    ref="$(git -C "$REPO_DIR" rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
    if [ -z "$suite_url" ] || [ "$suite_url" = "$origin" ]; then
      # Nothing to rewrite: origin already points at dx-all-suite (running from the suite itself) or has
      # no path component to swap. Say so — a silent skip reads as "no suite".
      log "cannot derive a suite url from origin '$origin' (rewrite left it unchanged) — not cloning; pass --suite-dir or set DX_SUITE_DIR"
    else
      log "no suite found locally — acquiring: $suite_url (ref $ref)"
      mkdir -p "$CACHE"
      rm -rf "$CACHE/suite.tmp"
      if git clone --depth 1 --no-recurse-submodules --branch "$ref" \
              "$suite_url" "$CACHE/suite.tmp" >/dev/null 2>&1 ||
         git clone --depth 1 --no-recurse-submodules \
              "$suite_url" "$CACHE/suite.tmp" >/dev/null 2>&1; then
        rm -rf "$CACHE/suite"
        mv "$CACHE/suite.tmp" "$CACHE/suite"
        if is_suite "$CACHE/suite"; then
          SUITE_DIR="$(cd "$CACHE/suite" && pwd -P)"
          SOURCE="clone"
        else
          log "WARNING: cloned tree is not a usable suite — ignoring it"
          rm -rf "$CACHE/suite"
        fi
      else
        rm -rf "$CACHE/suite.tmp"
      fi
    fi
  fi
fi

# 5. HARD GATE — nothing worked.
if [ -z "$SOURCE" ]; then
  cat >&2 <<EOF
[$PROG] ================ HARNESS BOOTSTRAP FAILED ================
[$PROG] Could not acquire a dx-all-suite checkout. Tried, in order:
[$PROG]   1. --suite-dir / \$DX_SUITE_DIR      (not set, or not a suite)
[$PROG]   2. parent directories of this repo   (no suite above $REPO_DIR)
[$PROG]   3. cache $CACHE/suite                (absent)
[$PROG]   4. shallow clone of the derived dx-all-suite URL (failed or disabled)
[$PROG]
[$PROG] HARD GATE: do NOT edit any file under **/.deepx/** in this checkout until
[$PROG] this succeeds. The generator and the shared fragments live only in
[$PROG] dx-all-suite, so without them you cannot regenerate CLAUDE.md / AGENTS.md /
[$PROG] .claude / .github / .cursor / .opencode — every edit ships as drift.
[$PROG]
[$PROG] In particular, do NOT "fix" an error of the form
[$PROG]   unresolved template variables ['{{FRAGMENT:...}}', ...]
[$PROG] by editing the templates or renaming fragments. The fragments are MISSING
[$PROG] from this checkout, not wrong. Editing them creates a second, worse drift.
[$PROG]
[$PROG] Ways out:
[$PROG]   bash .deepx/scripts/harness_bootstrap.sh --check --suite-dir /path/to/dx-all-suite
[$PROG]   DX_SUITE_DIR=/path/to/dx-all-suite bash .deepx/scripts/harness_bootstrap.sh --check
[$PROG]   ...or do the harness work from a full dx-all-suite checkout instead.
[$PROG] ==========================================================
EOF
  exit 3
fi

# Record provenance so a later run can report a stale cache instead of trusting it blindly.
if mkdir -p "$CACHE" 2>/dev/null; then
  printf '{"suite_dir":"%s","source":"%s","subrepo_path":"%s","acquired_at":"%s"}\n' \
    "$SUITE_DIR" "$SOURCE" "$SUBREPO_PATH" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    > "$CACHE/state.json" 2>/dev/null || true
fi

if [ "$PRINT_ONLY" -eq 1 ]; then
  printf '%s\t%s\n' "$SUITE_DIR" "$SOURCE"
  exit 0
fi

log "suite: $SUITE_DIR (source=$SOURCE)"
log "sub-repo path: $SUBREPO_PATH"

if [ "$DO_CHECK" -eq 1 ]; then
  CHECKER="$SUITE_DIR/.deepx/tools/scripts/subrepo_check.sh"
  [ -f "$CHECKER" ] || die2 "acquired suite has no subrepo_check.sh at $CHECKER"
  log "running the CI-identical check (drift + validate_framework.py)"
  exec bash "$CHECKER" \
    --subrepo-path "$SUBREPO_PATH" \
    --repo-dir "$REPO_DIR" \
    --suite-dir "$SUITE_DIR" \
    --mode worktree
fi

log "next: bash .deepx/scripts/harness_bootstrap.sh --check"
