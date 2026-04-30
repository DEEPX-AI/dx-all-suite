"""Forbidden Test Pattern Guard — Prevent self-improvement loop from re-adding banned tests.

The self-improvement loop sometimes re-introduces hallucinated test functions
that were deliberately removed. These tests verify that banned test names and
patterns do NOT appear in the e2e test suite.

If a test here fails, a banned pattern has been re-added by the loop.
Remove the offending test function from the e2e test file.

Banned patterns and why they were removed:
- test_compilation_used_fast_calibration: tested for SingleImageCalibDataset usage,
  which is a hallucinated class that does not exist in the dx_com SDK.
- test_calibration_self_check_passed: tested for CALIBRATION_OK log marker,
  which is a hallucinated log line that does not appear in real dx_com output.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
E2E_TEST_DIR = REPO_ROOT / "tests" / "test_agentic_e2e_scenarios"

# Banned test function names — these were deliberately removed from the e2e suite
# because they tested hallucinated SDK behavior. The loop must NOT re-add them.
BANNED_TEST_FUNCTION_NAMES = [
    "test_compilation_used_fast_calibration",
    "test_calibration_self_check_passed",
]

# Banned class/symbol names that must not appear in e2e test files
BANNED_SYMBOLS_IN_TESTS = [
    "SingleImageCalibDataset",
    "CALIBRATION_OK",
]


def _get_e2e_test_files() -> list[Path]:
    if not E2E_TEST_DIR.exists():
        return []
    return [f for f in E2E_TEST_DIR.glob("test_*.py")]


E2E_TEST_FILES = _get_e2e_test_files()


def _scan_test_files(pattern: str) -> list[tuple[Path, int, str]]:
    hits: list[tuple[Path, int, str]] = []
    rx = re.compile(pattern)
    for path in E2E_TEST_FILES:
        try:
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if rx.search(line):
                    hits.append((path, i, line.strip()))
        except OSError:
            pass
    return hits


class TestForbiddenTestFunctions:
    """Banned test function names must not appear in any e2e test file."""

    @pytest.mark.parametrize("name", BANNED_TEST_FUNCTION_NAMES)
    def test_banned_function_not_present(self, name: str):
        """This function was removed because it tested hallucinated SDK behavior."""
        # Match `def <name>` as a function definition
        hits = _scan_test_files(rf"\bdef\s+{re.escape(name)}\b")
        assert not hits, (
            f"BANNED test function '{name}' was re-added to an e2e test file.\n"
            f"This test was removed because it tested hallucinated SDK behavior.\n"
            f"Remove it from:\n"
            + "\n".join(f"  {p}:{n}: {line}" for p, n, line in hits)
        )


class TestForbiddenSymbolsInTests:
    """Hallucinated SDK symbols must not appear in e2e test files."""

    @pytest.mark.parametrize("symbol", BANNED_SYMBOLS_IN_TESTS)
    def test_banned_symbol_not_in_e2e_tests(self, symbol: str):
        hits = _scan_test_files(re.escape(symbol))
        assert not hits, (
            f"Hallucinated symbol '{symbol}' found in e2e test files "
            f"(this symbol does not exist in the real SDK):\n"
            + "\n".join(f"  {p}:{n}: {line}" for p, n, line in hits)
        )
