#!/usr/bin/env bash
# Install the DX AI Studio git hooks into this clone.
#
# dx-ai-studio lives INSIDE the dx-all-suite repo (a plain directory, not a
# submodule), so the hooks belong to the suite's .git — resolved via rev-parse
# rather than assumed, which also keeps this working from a worktree.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

HOOK_DIR="$(git rev-parse --git-path hooks)"
HOOK_DIR="$(cd "$HOOK_DIR" && pwd)"
mkdir -p "$HOOK_DIR"

TARGET="$HOOK_DIR/pre-commit"
SOURCE_REL="$(realpath --relative-to="$HOOK_DIR" "$ROOT/scripts/pre-commit-hook.sh")"

if [ -e "$TARGET" ] && [ ! -L "$TARGET" ]; then
  echo "refusing to overwrite an existing non-symlink hook: $TARGET" >&2
  echo "move it aside first, then re-run." >&2
  exit 1
fi

ln -sfn "$SOURCE_REL" "$TARGET"
echo "installed: $TARGET -> $SOURCE_REL"
echo "bypass a single commit with: git commit --no-verify"
