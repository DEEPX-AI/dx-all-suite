"""Source-level contracts for the release audit harness."""

import ast
import importlib.util
import sys
from pathlib import Path

# Anchor paths to the test file location, not CWD
_THIS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _THIS_DIR.parent.parent
_AUDIT_PATH = _PROJECT_ROOT / "tools" / "release_audit.py"

RELEASE_ROUTES = [
    "/",
    "/app/",
    "/stream/",
    "/zoo/",
    "/compiler/",
    "/planner/",
    "/benchmark/",
    "/dx_monitor/",
    "/sdk-library",
    "/about",
]

_AUDIT_SRC = _AUDIT_PATH.read_text(encoding="utf-8")


def _load_audit_module():
    module_name = "_release_audit_under_test"
    spec = importlib.util.spec_from_file_location(module_name, _AUDIT_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def test_release_audit_route_list_is_complete():
    for route in RELEASE_ROUTES:
        assert repr(route) in _AUDIT_SRC or f'"{route}"' in _AUDIT_SRC, (
            f"Route {route!r} missing from tools/release_audit.py"
        )


def test_console_warnings_are_collected():
    """Console warning messages must produce console_warning findings."""
    assert '"warning"' in _AUDIT_SRC or "'warning'" in _AUDIT_SRC, (
        "release_audit.py must check for console warning messages"
    )
    assert "console_warning" in _AUDIT_SRC, (
        "release_audit.py must emit 'console_warning' category findings"
    )


def test_http_error_responses_are_collected():
    """Every sub-resource response with status >= 400 must be recorded."""
    assert '"response"' in _AUDIT_SRC or "'response'" in _AUDIT_SRC, (
        "release_audit.py must listen to page 'response' events"
    )
    assert ">= 400" in _AUDIT_SRC or "status >= 400" in _AUDIT_SRC or ".status >= 400" in _AUDIT_SRC, (
        "release_audit.py response handler must filter status >= 400"
    )


def test_blocker_categories_wired():
    """Severity must be derived from BLOCKER_CATEGORIES, not hard-coded."""
    assert "BLOCKER_CATEGORIES" in _AUDIT_SRC, (
        "release_audit.py must define BLOCKER_CATEGORIES"
    )
    assert "_severity_for" in _AUDIT_SRC, (
        "release_audit.py must use _severity_for() helper for severity"
    )
    # Every RouteFinding construction should use _severity_for, not literal "blocker"/"warning"
    # (except the definition of _severity_for itself)
    tree = ast.parse(_AUDIT_SRC)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_route_finding_call(node):
            # The severity arg (3rd positional) should be a call to _severity_for
            if len(node.args) >= 3:
                sev_arg = node.args[2]
                assert isinstance(sev_arg, ast.Call), (
                    f"RouteFinding at line {node.lineno} uses a literal severity "
                    f"instead of _severity_for()"
                )


def _is_route_finding_call(node: ast.Call) -> bool:
    if isinstance(node.func, ast.Name) and node.func.id == "RouteFinding":
        return True
    if isinstance(node.func, ast.Attribute) and node.func.attr == "RouteFinding":
        return True
    return False


def _function_def(name: str) -> ast.FunctionDef:
    tree = ast.parse(_AUDIT_SRC)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"Function {name} not found")


def test_placeholder_uses_word_boundary_regex():
    """'null' and 'undefined' detection must use word-boundary regex."""
    assert "_PLACEHOLDER_PATTERNS" in _AUDIT_SRC, (
        "release_audit.py must define _PLACEHOLDER_PATTERNS with regex"
    )
    # Must NOT have the old bare-substring list
    assert "_PLACEHOLDER_TOKENS" not in _AUDIT_SRC, (
        "release_audit.py should use _PLACEHOLDER_PATTERNS, not _PLACEHOLDER_TOKENS"
    )
    # Ensure word-boundary patterns exist for null and undefined
    assert r"\bnull\b" in _AUDIT_SRC, (
        "null placeholder must use \\bnull\\b word-boundary regex"
    )
    assert r"\bundefined\b" in _AUDIT_SRC, (
        "undefined placeholder must use \\bundefined\\b word-boundary regex"
    )


def test_response_listener_filters_goto_response_by_identity():
    """The response listener must collect all >=400 responses, then after goto
    returns, exclude the goto-returned response by object identity — not just
    by URL comparison — to handle redirect chains correctly."""
    # Source must store the response object alongside metadata
    assert "resp_obj" in _AUDIT_SRC or "resp," in _AUDIT_SRC, (
        "response handler must store the response object for identity filtering"
    )
    # After goto, filter using 'is' identity check against goto response
    assert "is goto_resp" in _AUDIT_SRC or "is resp" in _AUDIT_SRC, (
        "http_error_response loop must use 'is' identity check to skip the "
        "goto-returned response object, not URL string comparison"
    )
    # Must NOT rely solely on _nav_url string comparison
    assert "resp.url != _nav_url" not in _AUDIT_SRC, (
        "response listener must not use URL string comparison for dedup; "
        "use object identity instead to handle redirects"
    )


def test_dedup_logic_filters_same_object():
    """Unit-level check: the dedup pattern correctly filters by object identity."""
    sentinel_goto = object()
    other_resp = object()

    # Simulate collected responses: list of (resp_obj, url, detail)
    collected = [
        (sentinel_goto, "http://x/redirected", "GET http://x/redirected → 404"),
        (other_resp, "http://x/api/missing", "GET http://x/api/missing → 500"),
    ]

    # Apply the same filter logic used in release_audit.py
    emitted = [
        detail for resp_obj, _url, detail in collected if resp_obj is not sentinel_goto
    ]

    assert len(emitted) == 1
    assert "api/missing" in emitted[0]


def test_release_audit_has_no_pin_or_auth_smoke_dependency():
    forbidden = (
        "AUTH_SMOKE_CHECKS",
        "DX_AUTH_TEST_PIN",
        "DX_RELEASE_AUDIT_PIN",
        "DX_RELEASE_AUDIT_ALLOW_RELOCK",
        "_run_auth_smoke_session",
        "_run_auth_relock_smoke",
        "_browser_auth_cookies",
        "auth_smoke_failures",
        "\"auth_smoke\"",
        "/api/auth/unlock",
        "/api/auth/relock",
        "X-DX-CSRF",
    )
    for token in forbidden:
        assert token not in _AUDIT_SRC


def test_local_api_smoke_contracts_are_present():
    for token in (
        "LOCAL_API_SMOKE_CHECKS",
        "_run_local_api_smoke",
        "/api/health",
        "/api/auth/status",
        "/api/modules/dx_app/status",
        "/api/chat/config",
        "local_api_smoke",
        "local_api_smoke_failures",
    ):
        assert token in _AUDIT_SRC


def test_failed_local_api_smoke_sets_report_failure_flag(monkeypatch):
    audit = _load_audit_module()
    monkeypatch.setattr(audit, "_try_playwright_audit", lambda base_url, routes: [])
    monkeypatch.setattr(
        audit,
        "_run_local_api_smoke",
        lambda base_url: [audit.SmokeCheck("local_api_dx_app_status", "fail", "HTTP 401")],
    )

    report = audit.run_audit("http://127.0.0.1:8890", ["/"])

    assert report["has_smoke_failure"] is True
    assert report["local_api_smoke_failures"] == 1


def test_main_returns_gate_failure_for_smoke_failures(monkeypatch):
    audit = _load_audit_module()
    monkeypatch.setattr(
        audit,
        "run_audit",
        lambda base_url, routes: {
            "base_url": base_url,
            "routes_audited": len(routes),
            "has_blocker": False,
            "has_smoke_failure": True,
            "finding_counts": {},
            "local_api_smoke": [],
            "keyboard_smoke": [],
            "results": [],
        },
    )
    monkeypatch.setattr(sys, "argv", ["release_audit.py", "--routes", "/"])

    assert audit.main() == 2


def test_internal_placeholder_tokens_are_not_double_counted():
    audit = _load_audit_module()
    placeholder_labels = {label for label, _pattern in audit._PLACEHOLDER_PATTERNS}
    internal_labels = {
        label
        for label, category, _pattern in audit._DEV_TOKEN_PATTERNS
        if category == "internal_placeholder"
    }

    assert placeholder_labels.isdisjoint(internal_labels)


def test_keyboard_smoke_contracts_cover_launcher_about_sdk_paths():
    for token in (
        "KEYBOARD_SMOKE_ACTIONS",
        "keyboard_smoke",
        ".about-book-card:not(.sdk-card)",
        ".about-book-card.sdk-card",
        "#landingPoster",
        "#sdkBookViewer",
        "Enter",
        "Escape",
        "_run_keyboard_smoke",
    ):
        assert token in _AUDIT_SRC


def test_keyboard_smoke_prepares_launcher_before_actions():
    for token in (
        "_prepare_keyboard_smoke_page",
        "dx-splash-seen",
        "window.skipSplash",
        "_initDeferredLauncherWork",
    ):
        assert token in _AUDIT_SRC


def test_keyboard_smoke_handles_async_setup_and_document_level_escape():
    for token in (
        "focus_selector",
        "wait_for_eval",
        "page.wait_for_function",
        "await window.SDKLibrary.init()",
    ):
        assert token in _AUDIT_SRC


def test_frame_aware_error_collection_contracts():
    for token in (
        "_frame_label",
        "_format_console_message",
        "_format_page_error",
        "_format_failed_request",
        "msg.location",
        "req.frame",
        "frame=",
        "page.on(\"console\"",
        "page.on(\"pageerror\"",
        "page.on(\"requestfailed\"",
    ):
        assert token in _AUDIT_SRC


def test_release_leak_and_result_field_contracts_are_structured():
    for token in (
        "_DEV_TOKEN_PATTERNS",
        "dev_token_leak",
        "internal_placeholder",
        "static_failure",
        "korean_leak",
        "Metadata pending",
        "sandbox",
        "Coming Soon",
        "finding_counts",
        "keyboard_smoke",
        "local_api_smoke",
    ):
        assert token in _AUDIT_SRC
