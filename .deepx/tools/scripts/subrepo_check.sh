#!/usr/bin/env bash
#
# subrepo_check.sh — sub-repo standalone drift gate (Phase 2, Task 1)
#
# The dx-agent-dev generator (dx_agent_dev_gen) and the shared fragments it
# renders from (.deepx/templates/fragments) exist ONLY at the dx-all-suite
# root. `Generator(repo)._find_fragments_dir()` walks up at most 5 parent
# directories looking for `.deepx/templates/fragments`, so a sub-repo
# (dx-compiler, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream) can only
# be checked for drift when it sits at its CANONICAL position inside a suite
# tree. A bare `dx-agent-gen check` run from inside a standalone sub-repo
# checkout (as CI sees it) can never find the fragments on its own.
#
# This script bridges that gap: it acquires a suite (an existing checkout via
# --suite-dir, or a fresh shallow clone), then builds a lightweight "shell"
# suite tree under $WORK/suite (ALWAYS freshly wiped and recreated on every
# run — see C1 below):
#
#   $WORK/suite/.deepx  -> symlink to <real suite>/.deepx   (tools + fragments)
#   $WORK/suite/<subrepo-path>  = a COPY of --repo-dir (committed HEAD via
#                                 `git archive`, or the raw working tree)
#
# `dx-agent-gen check --repo $WORK/suite/<subrepo-path>` then resolves() its
# --repo argument to a real (non-symlink) directory, and the parent-walk in
# _find_fragments_dir() reaches $WORK/suite within its 5-level budget, finds
# `.deepx/templates/fragments` THROUGH the `.deepx` symlink (is_dir() follows
# symlinks, so this works transparently), and checks the copy against the
# real suite's current fragments/templates.
#
# The shell approach is used uniformly whether the suite came from --suite-dir
# or from a fresh clone — this avoids ever writing into a real suite checkout
# (which would be unsafe with --suite-dir) and sidesteps the case where a
# freshly cloned suite's own submodule placeholder at <suite>/<subrepo-path>
# already exists (clone uses --no-recurse-submodules, so it may be an empty
# directory) — we never touch that path, only $WORK/suite/<subrepo-path>.
#
# IMPORTANT (C1, fixed): $WORK/suite is UNCONDITIONALLY `rm -rf`'d and
# recreated before the `.deepx` symlink is (re-)created. A prior finding: if
# --work is reused across invocations and this step only did a plain
# `ln -s "$REAL_SUITE_DIR/.deepx" "$SHELL_DIR/.deepx"`, and $SHELL_DIR/.deepx
# already existed as a symlink to a real suite's .deepx from a PRIOR run, `ln
# -s` resolves through that existing symlink and would create a NEW symlink
# INSIDE the real suite's .deepx directory instead of replacing the shell's
# own link — silently writing into the real suite. Always wiping $SHELL_DIR
# first, plus `ln -sn` (treat the destination as a plain path, never descend
# into it even if it still resolved to a directory) as defense-in-depth,
# closes this.
#
# Usage:
#   subrepo_check.sh --subrepo-path <dx-compiler|dx-runtime|dx-runtime/dx_app|dx-runtime/dx_stream>
#                     [--repo-dir DIR]           # sub-repo checkout to check (default: $PWD)
#                     [--suite-dir DIR]          # existing suite checkout (skips clone); must
#                                                #   contain .deepx/tools/src/dx_agent_dev_gen/cli.py
#                                                #   AND .deepx/templates/fragments
#                     [--suite-url URL]          # default: origin URL of --repo-dir, last
#                                                #   path component swapped for dx-all-suite(.git)
#                     [--suite-ref REF]          # default: current branch of --repo-dir
#                                                #   (detached HEAD -> remote default branch)
#                     [--mode archive|worktree]  # archive (default) = committed HEAD via
#                                                #   `git archive` (requires --repo-dir to be a
#                                                #   git repo); worktree = working tree incl.
#                                                #   uncommitted changes, .git excluded
#                     [--work DIR]               # scratch dir (default: fresh mktemp -d). A
#                                                #   user-supplied --work dir is NEVER deleted
#                                                #   by this script, regardless of --keep.
#                     [--keep]                   # keep the mktemp'd scratch dir (only relevant
#                                                #   when --work is NOT given — a user-supplied
#                                                #   --work dir is already never deleted)
#                     [--strict-validator]       # validate_framework.py failures become fatal
#                     [--print-suite-url]        # print the derived/given suite URL and exit 0
#                                                #   (does not require --subrepo-path)
#                     [--help|-h]                # print this usage and exit 0
#
# Exit codes: 0 = clean; 1 = drift detected (or --strict-validator failure);
#             2 = setup/usage/tool error (bad --subrepo-path, missing suite,
#             missing python3 or python3 < 3.8, unreachable suite URL, or the
#             generator itself crashed — a Traceback / rc >= 2 is NOT drift).

set -euo pipefail

PROG_TAG="[subrepo-check]"

log() { printf '%s %s\n' "$PROG_TAG" "$*"; }
err() { printf '%s ERROR: %s\n' "$PROG_TAG" "$*" >&2; }

print_usage() {
  cat <<'USAGE'
subrepo_check.sh --subrepo-path <dx-compiler|dx-runtime|dx-runtime/dx_app|dx-runtime/dx_stream>
                  [--repo-dir DIR]            # sub-repo checkout to check (default: $PWD)
                  [--suite-dir DIR]           # existing suite checkout (skips clone)
                  [--suite-url URL]           # default: derived from --repo-dir's origin remote
                  [--suite-ref REF]           # default: current branch of --repo-dir
                  [--mode archive|worktree]   # archive (default, committed HEAD) | worktree
                  [--work DIR] [--keep] [--strict-validator] [--print-suite-url] [--help|-h]

Exit codes: 0 = clean; 1 = drift detected (or --strict-validator failure);
            2 = setup/usage/tool error (incl. python3 < 3.8 or a generator crash — NOT drift).
USAGE
}

ALLOWED_SUBREPO_PATHS="dx-compiler dx-runtime dx-runtime/dx_app dx-runtime/dx_stream"

SUBREPO_PATH=""
REPO_DIR="$PWD"
SUITE_DIR=""
SUITE_URL=""
SUITE_REF=""
MODE="archive"
WORK=""
WORK_USER_SUPPLIED=0
KEEP=0
STRICT_VALIDATOR=0
PRINT_SUITE_URL=0
SHOW_HELP=0

need_val() {  # need_val <flag-name> <remaining-arg-count-including-flag>
  if [ "$2" -lt 2 ]; then
    err "$1 requires a value"
    exit 2
  fi
}

while [ $# -gt 0 ]; do
  case "$1" in
    --subrepo-path)
      need_val "$1" "$#"
      SUBREPO_PATH="$2"
      shift 2
      ;;
    --repo-dir)
      need_val "$1" "$#"
      REPO_DIR="$2"
      shift 2
      ;;
    --suite-dir)
      need_val "$1" "$#"
      SUITE_DIR="$2"
      shift 2
      ;;
    --suite-url)
      need_val "$1" "$#"
      SUITE_URL="$2"
      shift 2
      ;;
    --suite-ref)
      need_val "$1" "$#"
      SUITE_REF="$2"
      shift 2
      ;;
    --mode)
      need_val "$1" "$#"
      MODE="$2"
      shift 2
      ;;
    --work)
      need_val "$1" "$#"
      WORK="$2"
      WORK_USER_SUPPLIED=1
      shift 2
      ;;
    --keep)
      KEEP=1
      shift
      ;;
    --strict-validator)
      STRICT_VALIDATOR=1
      shift
      ;;
    --print-suite-url)
      PRINT_SUITE_URL=1
      shift
      ;;
    --help|-h)
      SHOW_HELP=1
      shift
      ;;
    *)
      err "unknown argument: $1"
      exit 2
      ;;
  esac
done

if [ "$SHOW_HELP" -eq 1 ]; then
  print_usage
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  err "python3 not found in PATH"
  exit 2
fi
# The GHES self-hosted pool includes Ubuntu 20.04 runners (Python 3.8): 3.8 is the
# generator's floor. Refuse anything older up front instead of crashing inside it.
PY_VERSION="$(python3 --version 2>&1 | head -n1)"
if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
  err "Python >= 3.8 required for the generator (found: $PY_VERSION at $(command -v python3))"
  exit 2
fi

if [ ! -d "$REPO_DIR" ]; then
  err "--repo-dir does not exist: $REPO_DIR"
  exit 2
fi
REPO_DIR="$(cd "$REPO_DIR" && pwd -P)"

derive_suite_url() {
  # Derive dx-all-suite's clone URL from --repo-dir's `origin` remote by
  # swapping the last path component for dx-all-suite(.git), preserving the
  # scheme/host/org prefix (works for both SSH-style git@host:org/name.git
  # and https://host/org/name.git forms).
  local origin base dir
  # The CONFIGURED value, not `remote get-url`: the latter applies url.<base>.insteadOf
  # rewrites (present on CI images / credential-manager hosts) and would silently turn
  # git@host:org/... into https://host/org/... .
  # Dev checkouts may follow the ghes/mirror naming convention instead of `origin`.
  local r
  for r in origin mirror ghes; do
    origin="$(git -C "$REPO_DIR" config --get "remote.$r.url" 2>/dev/null || true)"
    [ -n "$origin" ] && break
  done
  if [ -z "$origin" ]; then
    err "cannot derive --suite-url: no 'origin', 'mirror' or 'ghes' remote configured in $REPO_DIR"
    exit 2
  fi
  base="${origin%.git}"
  dir="$(dirname "$base")"
  if [[ "$origin" == *.git ]]; then
    printf '%s/dx-all-suite.git\n' "$dir"
  else
    printf '%s/dx-all-suite\n' "$dir"
  fi
}

# --print-suite-url is a standalone utility mode: it does not require
# --subrepo-path (and does not perform any suite acquisition or checking).
if [ "$PRINT_SUITE_URL" -eq 1 ]; then
  if [ -z "$SUITE_URL" ]; then
    SUITE_URL="$(derive_suite_url)"
  fi
  echo "$SUITE_URL"
  exit 0
fi

# Validate --subrepo-path against the 4 canonical positions.
subrepo_path_ok=0
for p in $ALLOWED_SUBREPO_PATHS; do
  if [ "$p" = "$SUBREPO_PATH" ]; then
    subrepo_path_ok=1
    break
  fi
done
if [ "$subrepo_path_ok" -ne 1 ]; then
  err "--subrepo-path must be one of: $ALLOWED_SUBREPO_PATHS (got: '$SUBREPO_PATH')"
  exit 2
fi

if [ "$MODE" != "archive" ] && [ "$MODE" != "worktree" ]; then
  err "--mode must be 'archive' or 'worktree' (got: '$MODE')"
  exit 2
fi

# Scratch workspace.
if [ -z "$WORK" ]; then
  WORK="$(mktemp -d "${TMPDIR:-/tmp}/subrepo-check.XXXXXX")"
else
  mkdir -p "$WORK"
  WORK="$(cd "$WORK" && pwd -P)"
fi

cleanup() {
  if [ "$KEEP" -ne 1 ] && [ "$WORK_USER_SUPPLIED" -ne 1 ]; then
    rm -rf "$WORK"
  fi
}
# bash also runs the EXIT trap on SIGINT/SIGTERM; trapping INT/TERM explicitly
# would RESUME execution after the handler and exit 0 on an interrupted run.
trap cleanup EXIT

# ---------------------------------------------------------------------------
# 1. Acquire a real suite checkout (existing --suite-dir, or a fresh clone).
# ---------------------------------------------------------------------------
REAL_SUITE_DIR=""

if [ -n "$SUITE_DIR" ]; then
  if [ ! -d "$SUITE_DIR" ]; then
    err "--suite-dir does not exist: $SUITE_DIR"
    exit 2
  fi
  SUITE_DIR="$(cd "$SUITE_DIR" && pwd -P)"
  if [ ! -f "$SUITE_DIR/.deepx/tools/src/dx_agent_dev_gen/cli.py" ]; then
    err "--suite-dir $SUITE_DIR does not contain .deepx/tools/src/dx_agent_dev_gen/cli.py"
    exit 2
  fi
  if [ ! -d "$SUITE_DIR/.deepx/templates/fragments" ]; then
    err "--suite-dir $SUITE_DIR does not contain .deepx/templates/fragments"
    exit 2
  fi
  REAL_SUITE_DIR="$SUITE_DIR"
  log "using existing suite checkout: $REAL_SUITE_DIR"
else
  if [ -z "$SUITE_URL" ]; then
    SUITE_URL="$(derive_suite_url)"
  fi

  REQUESTED_REF="$SUITE_REF"
  if [ -z "$SUITE_REF" ]; then
    # Detached HEAD in --repo-dir yields an empty string here (with -q, no error).
    SUITE_REF="$(git -C "$REPO_DIR" symbolic-ref --short -q HEAD || true)"
  fi

  # Distinguish "branch not found" (empty match, rc 0) from an unreachable
  # suite repo (auth/network failure, rc != 0) — the latter must be a hard
  # error, not silently fall through to the default-branch lookup.
  set +e
  heads_match="$(git ls-remote --heads "$SUITE_URL" "$SUITE_REF" 2>/dev/null)"
  heads_rc=$?
  set -e
  if [ "$heads_rc" -ne 0 ]; then
    err "cannot reach suite repo $SUITE_URL (auth/network?)"
    exit 2
  fi

  REF_USED=""
  if [ -n "$heads_match" ]; then
    REF_USED="$SUITE_REF"
    log "suite ref: $REF_USED"
  else
    # `|| true` here (not inside the substitution) is what makes a failing
    # pipeline non-fatal under `set -e` while still letting the `-z` check
    # below detect it — a stray `|| true` INSIDE `$(...)` would always make
    # the pipeline itself report rc 0, so a separately-captured `$?` would be
    # dead code. Rely solely on `[ -z "$REF_USED" ]`: it is empty both when
    # the pipeline fails and when it legitimately finds no symref.
    set +e
    REF_USED="$(git ls-remote --symref "$SUITE_URL" HEAD 2>/dev/null | awk '/^ref:/{sub("refs/heads/","",$2); print $2}')"
    set -e
    if [ -z "$REF_USED" ]; then
      err "cannot resolve a usable ref for suite $SUITE_URL (requested: '${REQUESTED_REF:-<detached HEAD>}')"
      exit 2
    fi
    if [ -n "$REQUESTED_REF" ]; then
      log "suite ref: $REF_USED (fallback from $REQUESTED_REF)"
    else
      log "suite ref: $REF_USED (fallback from <detached HEAD>)"
    fi
  fi

  CLONE_DIR="$WORK/_suite_src"
  # Wipe before cloning (mirrors the $SHELL_DIR wipe below): `git clone`
  # refuses a non-empty destination, so a --work dir reused across
  # invocations would otherwise fail on the second run.
  rm -rf "$CLONE_DIR"
  log "cloning suite: $SUITE_URL @ $REF_USED"
  git clone -q --depth 1 --no-recurse-submodules --branch "$REF_USED" "$SUITE_URL" "$CLONE_DIR"
  REAL_SUITE_DIR="$CLONE_DIR"

  if [ ! -f "$REAL_SUITE_DIR/.deepx/tools/src/dx_agent_dev_gen/cli.py" ]; then
    err "cloned suite at $REAL_SUITE_DIR does not contain .deepx/tools/src/dx_agent_dev_gen/cli.py"
    exit 2
  fi
  if [ ! -d "$REAL_SUITE_DIR/.deepx/templates/fragments" ]; then
    err "cloned suite at $REAL_SUITE_DIR does not contain .deepx/templates/fragments"
    exit 2
  fi
fi

# ---------------------------------------------------------------------------
# 2. Build the shell suite tree: $WORK/suite/.deepx (symlink) + copy of repo.
#    $SHELL_DIR is ALWAYS wiped and recreated fresh (C1) — never reused as-is
#    across invocations, even when --work points at a directory from a prior
#    run, so `ln -sn` never resolves through a stale symlink into the real
#    suite's .deepx tree.
# ---------------------------------------------------------------------------
SHELL_DIR="$WORK/suite"
rm -rf "$SHELL_DIR"
mkdir -p "$SHELL_DIR"
ln -sn "$REAL_SUITE_DIR/.deepx" "$SHELL_DIR/.deepx" || {
  err "cannot create .deepx symlink"
  exit 2
}

NESTED="$SHELL_DIR/$SUBREPO_PATH"
if [ -e "$NESTED" ]; then
  err "nested target already exists (safety check failed): $NESTED"
  exit 2
fi
mkdir -p "$(dirname "$NESTED")"
mkdir -p "$NESTED"

case "$MODE" in
  archive)
    if ! git -C "$REPO_DIR" rev-parse --git-dir >/dev/null 2>&1; then
      err "--repo-dir $REPO_DIR is not a git repository (required for --mode archive; use --mode worktree for a non-git directory)"
      exit 2
    fi
    log "copying $REPO_DIR (committed HEAD via git archive) -> $NESTED"
    git -C "$REPO_DIR" archive --format=tar HEAD | tar -x -C "$NESTED"
    ;;
  worktree)
    log "copying $REPO_DIR (working tree, .git excluded) -> $NESTED"
    tar -C "$REPO_DIR" --exclude=.git -cf - . | tar -xf - -C "$NESTED"
    ;;
esac

# ---------------------------------------------------------------------------
# 3. Run the drift check. NEVER interpolate paths into the python -c source
#    string (I3) — pass them as argv, exactly like run_all.sh's `gen()` does.
# ---------------------------------------------------------------------------
RC=0

set +e
CHECK_OUT="$(PYTHONPATH="$REAL_SUITE_DIR/.deepx/tools/src${PYTHONPATH:+:$PYTHONPATH}" \
  python3 -c "import sys; from dx_agent_dev_gen.cli import main; sys.exit(main(sys.argv[1:]))" \
  check --repo "$NESTED" 2>&1)"
CHECK_RC=$?
set -e

printf '%s\n' "$CHECK_OUT"

# rc 0 = clean; rc 1 without a traceback = drift (the cli's contract); anything
# else (rc >= 2 — cli.py's "internal failure" — or an uncaught Traceback, e.g. an
# import-time error the cli never got to handle) is a TOOL failure, NOT drift:
# never tell the user to regenerate for it.
if [ "$CHECK_RC" -eq 0 ]; then
  :
elif [ "$CHECK_RC" -eq 1 ] && ! printf '%s\n' "$CHECK_OUT" | grep -q '^Traceback (most recent call last)'; then
  RC=1
  cat <<EOF
$PROG_TAG Generated files are out of date in $SUBREPO_PATH.
$PROG_TAG Fix from a suite checkout on the SAME branch: \`bash .deepx/tools/scripts/run_all.sh generate\` (all levels), then commit the regenerated files in this repo.
$PROG_TAG Never hand-edit CLAUDE.md/AGENTS.md/.claude/.github/.cursor/.opencode.
EOF
else
  err "the generator failed to run (rc=$CHECK_RC) — this is NOT drift; see the output above. python3: $PY_VERSION at $(command -v python3)"
  err "Nothing to regenerate: fix the tool/runner (python3 >= 3.8 with jinja2 + pyyaml importable) and re-run."
  exit 2
fi

# ---------------------------------------------------------------------------
# 4. Optional non-blocking (unless --strict-validator) framework validation.
#    Run with cwd = the NESTED copy (I5) — dx-runtime's validate_framework.py
#    resolves its checks relative to the current working directory.
# ---------------------------------------------------------------------------
VALIDATOR_REL=".deepx/scripts/validate_framework.py"
if [ -f "$NESTED/$VALIDATOR_REL" ]; then
  set +e
  VALIDATOR_OUT="$(cd "$NESTED" && python3 "$VALIDATOR_REL" 2>&1)"
  VALIDATOR_RC=$?
  set -e
  printf '%s\n' "$VALIDATOR_OUT"
  if [ "$VALIDATOR_RC" -ne 0 ]; then
    if [ "$STRICT_VALIDATOR" -eq 1 ]; then
      err "validate_framework.py reported failures (--strict-validator set)"
      RC=1
    else
      log "WARNING: validate_framework.py reported failures (non-blocking; pass --strict-validator to enforce)"
    fi
  fi
fi

exit $RC
