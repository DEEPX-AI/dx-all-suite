"""The NPU-monitor float must be injected into a module's top-level shell page
ONLY — never into HTML fragments (XHR partials spliced in with innerHTML) nor
into nested sub-iframes (e.g. the compiler's sandboxed quant-diagnosis report),
which would render a duplicate float. See launcher._should_inject_widget.
"""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent


def _load_launcher_module():
    spec = importlib.util.spec_from_file_location(
        "dx_launcher_widget_gate_test",
        ROOT / "launcher" / "launcher.py",
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_injects_into_module_shell_navigation():
    m = _load_launcher_module()
    # iframe navigation (module shell load) and top-level document nav both inject.
    assert m._should_inject_widget(True, True, "iframe", False) is True
    assert m._should_inject_widget(True, True, "document", False) is True
    # Some browsers omit Sec-Fetch-Dest — fall back to injecting the shell page.
    assert m._should_inject_widget(True, True, "", False) is True


def test_suppresses_for_fetch_fragments():
    m = _load_launcher_module()
    # XHR/fetch partials (progress.html etc.) arrive as empty/cors — never inject.
    assert m._should_inject_widget(True, True, "empty", False) is False
    assert m._should_inject_widget(True, True, "cors", False) is False
    assert m._should_inject_widget(True, True, "EMPTY", False) is False  # case-insensitive


def test_suppresses_when_module_marks_no_widget():
    m = _load_launcher_module()
    # Nested <iframe src> report is a navigation (dest=iframe) but stamped X-DX-No-Widget.
    assert m._should_inject_widget(True, True, "iframe", True) is False


def test_suppresses_for_non_widget_and_non_html():
    m = _load_launcher_module()
    assert m._should_inject_widget(False, True, "iframe", False) is False   # dx_monitor
    assert m._should_inject_widget(True, False, "iframe", False) is False   # non-HTML body
