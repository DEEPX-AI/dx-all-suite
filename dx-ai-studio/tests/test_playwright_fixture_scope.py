"""No test may keep Playwright started for the whole session.

A session-scoped fixture that calls sync_playwright().start() stays running until the session ends, and every
later file that starts its own Playwright fails with "using Playwright Sync API inside the asyncio loop" — in a
full run that turned ~700 passing zoom/visual tests red. Scope such fixtures to the module (or package)."""
import ast
from pathlib import Path

TESTS = Path(__file__).resolve().parent


def _session_fixtures_starting_playwright(src: str):
    for node in ast.walk(ast.parse(src)):
        if not isinstance(node, ast.FunctionDef):
            continue
        session = any(isinstance(d, ast.Call) and any(k.arg == "scope" and getattr(k.value, "value", None) == "session"
                                                      for k in d.keywords) for d in node.decorator_list)
        if session and "sync_playwright" in ast.unparse(node):
            yield node.name


def test_no_session_scoped_playwright_fixture():
    bad = {str(p.relative_to(TESTS)): names for p in sorted(TESTS.rglob("*.py"))
           if (names := list(_session_fixtures_starting_playwright(p.read_text(encoding="utf-8"))))}
    assert not bad, bad


def test_the_check_catches_the_old_pattern():
    old = ('import pytest\n@pytest.fixture(scope="session")\ndef browser():\n'
           '    pw = sync_playwright().start()\n    yield pw\n')
    assert list(_session_fixtures_starting_playwright(old)) == ["browser"]
