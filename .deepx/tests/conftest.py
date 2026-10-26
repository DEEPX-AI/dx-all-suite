# SPDX-License-Identifier: Apache-2.0
"""
Shared configuration for agent-driven test suites (.deepx/tests/).

Registers agent-driven-specific pytest markers and prevents pytest from crawling
into sub-project test directories that have unrelated dependencies.
"""

import sys
from pathlib import Path

# Make dx_agent_dev_gen importable without an editable install — test_kb_counts.py
# reuses its counts.py as the single source of truth for model/task counts.
# Mirrors .deepx/tools/tests/conftest.py's sys.path insert for the same package.
_SRC = Path(__file__).resolve().parents[1] / "tools" / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

# Prevent pytest from descending into sub-project test directories when
# running from .deepx/tests/.  These directories belong to their respective
# sub-projects and have their own dependency trees.
collect_ignore_glob = [
    "../../dx-modelzoo/tests/*",
    "../../dx-runtime/dx_rt/extern/*",
    "../../dx-runtime/dx_app/tests/*",
    "../../dx-runtime/dx_stream/test/*",
]


def pytest_configure(config):
    """Register agent-driven-specific custom markers."""
    markers = [
        "agent_e2e_copilot_cli_autopilot: Agent-Driven E2E tests via Copilot CLI autopilot (fully autonomous, CI/CD)",
        "agent_e2e_cursor_cli_autopilot: Agent-Driven E2E tests via Cursor CLI autopilot (fully autonomous)",
        "agent_e2e_opencode_cli_autopilot: Agent-Driven E2E tests via OpenCode CLI autopilot (fully autonomous)",
        "agent_e2e_claude_code_autopilot: Agent-Driven E2E tests via Claude Code CLI autopilot (fully autonomous)",
        "agent_e2e_codex_cli_autopilot: Agent-Driven E2E tests via Codex CLI autopilot (fully autonomous)",
    ]
    for marker in markers:
        config.addinivalue_line("markers", marker)
