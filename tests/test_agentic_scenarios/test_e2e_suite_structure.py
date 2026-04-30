# SPDX-License-Identifier: Apache-2.0
"""
R17: Cross-file structural consistency check for suite E2E test files.

Verifies that all four suite test files (copilot, cursor, opencode, claude_code)
have matching fixture structure:
- Each file parses without SyntaxError (ast.parse)
- Each file declares a ``scenario`` module-scoped fixture
- Each file declares a ``TestExecution`` class
- Each file declares a ``TestMandatoryArtifacts`` class

This test catches the class of regression introduced in iteration 2 (R11),
where missing closing parentheses caused collection-time SyntaxErrors that
blocked all four tools from running.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from .conftest import SUITE_ROOT

# ---------------------------------------------------------------------------
# Suite test files to check
# ---------------------------------------------------------------------------

E2E_DIR = SUITE_ROOT / "tests" / "test_agentic_e2e_scenarios"

SUITE_TEST_FILES = {
    "copilot":     E2E_DIR / "test_suite_agentic_e2e.py",
    "cursor":      E2E_DIR / "test_cursor_suite_agentic_e2e.py",
    "opencode":    E2E_DIR / "test_opencode_suite_agentic_e2e.py",
    "claude_code": E2E_DIR / "test_claude_code_suite_agentic_e2e.py",
}

REQUIRED_CLASSES = ["TestExecution", "TestMandatoryArtifacts"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_file(path: Path) -> ast.Module:
    """Parse a Python file; raise AssertionError with a clear message on failure."""
    source = path.read_text(encoding="utf-8")
    try:
        return ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise AssertionError(
            f"SyntaxError in {path.name}: {exc}\n"
            "This prevents pytest from collecting the file at all."
        ) from exc


def _top_level_names(tree: ast.Module) -> set[str]:
    """Return the set of top-level names (function defs, class defs) in a module."""
    names: set[str] = set()
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
    return names


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestSuiteFileExists:
    """All four suite test files must be present on disk."""

    @pytest.mark.parametrize("tool,path", list(SUITE_TEST_FILES.items()))
    def test_file_exists(self, tool: str, path: Path):
        """Suite test file exists for the given tool."""
        assert path.exists(), (
            f"Suite test file missing for {tool}: {path}\n"
            "Each tool (copilot/cursor/opencode/claude_code) must have a dedicated "
            "suite E2E test file."
        )


class TestSuiteFileSyntax:
    """All four suite test files must be parseable Python."""

    @pytest.mark.parametrize("tool,path", list(SUITE_TEST_FILES.items()))
    def test_no_syntax_error(self, tool: str, path: Path):
        """File parses without SyntaxError (ast.parse)."""
        if not path.exists():
            pytest.skip(f"{path.name} does not exist")
        _parse_file(path)  # raises AssertionError on SyntaxError


class TestSuiteFileStructure:
    """Each suite test file must declare the required classes."""

    @pytest.mark.parametrize("tool,path", list(SUITE_TEST_FILES.items()))
    @pytest.mark.parametrize("class_name", REQUIRED_CLASSES)
    def test_required_class_present(self, tool: str, path: Path, class_name: str):
        """Required class is declared at module level."""
        if not path.exists():
            pytest.skip(f"{path.name} does not exist")
        tree = _parse_file(path)
        top_names = _top_level_names(tree)
        assert class_name in top_names, (
            f"{path.name} is missing top-level class '{class_name}'.\n"
            f"Top-level names found: {sorted(top_names)}\n"
            "All suite test files must have matching class structure."
        )

    @pytest.mark.parametrize("tool,path", list(SUITE_TEST_FILES.items()))
    def test_scenario_fixture_present(self, tool: str, path: Path):
        """Module-scoped 'scenario' fixture function is declared."""
        if not path.exists():
            pytest.skip(f"{path.name} does not exist")
        tree = _parse_file(path)
        top_names = _top_level_names(tree)
        assert "scenario" in top_names, (
            f"{path.name} is missing top-level 'scenario' fixture.\n"
            f"Top-level names found: {sorted(top_names)}"
        )


# ---------------------------------------------------------------------------
# R37: conftest.py symbol coverage — catches missing helper functions that
# cause NameError at runtime (invisible to py_compile and --collect-only).
# ---------------------------------------------------------------------------

class TestConftestSymbols:
    """conftest.py must define all expected helper functions at module scope."""

    @pytest.mark.parametrize("symbol", [
        "_snapshot_sessions",
        "_detect_new_sessions",
        "_wait_for_background_compilation",
    ])
    def test_conftest_has_symbol(self, symbol: str):
        """conftest.py defines the expected helper function at module scope."""
        from test_agentic_e2e_scenarios import conftest
        assert hasattr(conftest, symbol), (
            f"conftest.py missing symbol: {symbol}\n"
            "This causes NameError at fixture setup time, blocking all tests.\n"
            "Ensure the function is defined at module scope (not nested inside another function)."
        )

    def test_opencode_runner_session_uuid_initialized(self):
        """REC-X7: Verify session_uuid has a default value before the conditional JSON parse.

        Regression test for the UnboundLocalError introduced in iter-19 where session_uuid
        was referenced in _save_opencode_session_log() in the success path before being
        assigned. The fix (REC-X1) adds a _parse_opencode_stream_json() call immediately
        after subprocess.run() to guarantee session_uuid is always bound.
        """
        import ast
        import inspect
        from test_agentic_e2e_scenarios.conftest import OpenCodeRunnerAutopilot
        src = inspect.getsource(OpenCodeRunnerAutopilot.run)
        # Split on the first conditional block to check initialization order.
        # session_uuid must be assigned (via parse) before any 'if' or 'for' branch
        # in the success path that leads to _save_opencode_session_log.
        assert "_parse_opencode_stream_json" in src, (
            "OpenCodeRunnerAutopilot.run() does not call _parse_opencode_stream_json — "
            "session_uuid and assistant_text will be unbound in the success path "
            "(UnboundLocalError regression from iter-19, REC-X1)."
        )
        # Verify the parse call appears before _save_opencode_session_log in the source
        parse_pos = src.index("_parse_opencode_stream_json")
        save_pos = src.index("_save_opencode_session_log")
        assert parse_pos < save_pos, (
            "_parse_opencode_stream_json must appear before _save_opencode_session_log "
            "to ensure session_uuid is initialized. "
            f"Found parse at offset {parse_pos}, save at offset {save_pos}. "
            "(REC-X7 regression guard)"
        )
