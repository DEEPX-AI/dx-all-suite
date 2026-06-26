"""Single source of truth for showcase defaults."""
from __future__ import annotations

# The recommended coding agent + model for showcases (verified in `verify`).
DEFAULT_TOOL = "claude"
DEFAULT_MODEL = "claude-opus-4-8"

# GIF encoding policy (GitHub inline cap is ~10MB).
GIF_TARGET_SECS = 20          # timelapse target length
GIF_WIDTH = 760              # default scale width (px)
GIF_FPS = 9
GIF_MAX_COLORS = 64
GIF_MAX_BYTES = 10 * 1024 * 1024
GIF_REDUCE_WIDTH = 700        # fallback when first pass > GIF_MAX_BYTES
GIF_REDUCE_FPS = 7
GIF_REDUCE_COLORS = 48

# Default capture screen geometry (override per host).
SCREEN_W = 1920
SCREEN_H = 1080

# Repo-relative locations.
SHOWCASE_ROOT = "dx-agent-dev-showcase"
IMG_DIR = "docs/source/img"
SUITE_README = "README.md"
SUITE_README_KO = "README-KO.md"
DOCS_OVERVIEW = "docs/source/00_Agent_Driven_Development.md"
DOCS_OVERVIEW_KO = "docs/source/00_Agent_Driven_Development_kor.md"

# Transcript filenames inside a showcase dir (matches squat/stretch convention).
TRANSCRIPT_PREFIX = "claude-code-session"   # -> claude-code-session.{md,html,jsonl}

# Window title used for the recorded build terminal.
BUILD_WINDOW_TITLE = "DEEPXBUILDREC"
