"""DX Agent Dev server path constants and defaults.

Follows the dx_monitor/core/config.py pattern.
Path chain: SCRIPT_DIR (dx_agent_dev/) -> STUDIO_DIR (dx-ai-studio/) -> SUITE_ROOT (dx-all-suite/)
"""
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent     # dx_agent_dev/
STUDIO_DIR = SCRIPT_DIR.parent                          # dx-ai-studio/

from shared.paths import SUITE_ROOT, var_dir

# Server directories
STATIC_DIR = SCRIPT_DIR / "static"
TEMPLATES_DIR = SCRIPT_DIR / "templates"

DEFAULT_PORT = 8099
SERVER_NAME = "DX Agent Dev"

# Agent session working directory (gitignored)
WORKSPACE_ROOT = var_dir("dx_agent_dev", "sessions")

# Input / stream limits
PROMPT_MAX_LEN = 8000
KEEPALIVE_SEC = 15   # keepalive ping interval: while idle (no events) a ping holds the SSE connection open.
# Wall-clock cap (s) for one generation, so a stuck or hung run cannot hold the single concurrency
# slot forever. Adjustable through the environment.
GENERATION_TIMEOUT_SEC = int(os.environ.get("DX_AGENT_GENERATION_TIMEOUT", "900"))


# Target workdirs the agent can run in — mirrors the original SCENARIO_WORKDIRS
# (.deepx/e2e/test.sh). The agent's cwd becomes one of these so it discovers that
# project's CLAUDE.md + .claude/skills.
TARGET_WORKDIRS = {
    "suite": SUITE_ROOT,
    "dx-runtime": SUITE_ROOT / "dx-runtime",
    "dx_app": SUITE_ROOT / "dx-runtime" / "dx_app",
    "dx_stream": SUITE_ROOT / "dx-runtime" / "dx_stream",
    "dx-compiler": SUITE_ROOT / "dx-compiler",
}


def resolve_target(name):
    """Map a target name to an absolute workdir under the suite root.

    Whitelist-based: unknown names, empty, or traversal attempts fall back to the
    suite root and can never escape it.
    """
    root = SUITE_ROOT.resolve()
    path = TARGET_WORKDIRS.get((name or "").strip())
    if path is None:
        return root
    resolved = path.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return root
    return resolved


def harness_search_paths():
    """Harness directory candidates: env override -> dx-all-suite root -> dx-agent-dev."""
    candidates = []
    env = os.environ.get("DX_HARNESS_ROOT")
    if env:
        candidates.append(Path(env))
    candidates.append(SUITE_ROOT)
    candidates.append(SUITE_ROOT / "dx-agent-dev")
    return candidates
