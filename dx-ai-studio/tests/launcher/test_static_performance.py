import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LAUNCHER_STATIC = ROOT / "launcher/static"
INDEX_HTML = ROOT / "launcher/static/index.html"


def _read_all_launcher_js() -> str:
    return "\n".join(
        (LAUNCHER_STATIC / name).read_text(encoding="utf-8")
        for name in (
            "launcher-state.js",
            "launcher-language.js",
            "launcher-splash.js",
            "platform-info.js",
            "launcher-app-frame.js",
            "launcher.js",
        )
    )


def _function_body(source: str, name: str) -> str:
    start = source.index(f"function {name}(")
    brace = source.index("{", start)
    depth = 0
    for pos in range(brace, len(source)):
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1:pos]
    raise AssertionError(f"Could not parse function body for {name}")


def test_health_status_writes_only_when_class_changes():
    js = _read_all_launcher_js()

    for function_name in ("setDot", "setStatus", "_setOrbStatus"):
        body = _function_body(js, function_name)
        assert "if (el && el.className !== targetClass)" in body
        assert "el.className = targetClass" in body


def test_orbital_resize_is_debounced_and_does_not_stack_hover_listeners():
    js = _read_all_launcher_js()

    assert "window.addEventListener('resize', scheduleOrbitalLayout)" in js
    assert "setTimeout(initOrbital, 120)" in js
    assert "orbital-ready" in js
    assert "ensureStudioReady" in js
    assert "ResizeObserver" in js
    assert "mouseenter', _handleOrbitalCardMouseEnter" in js
    assert "mouseleave', _handleOrbitalCardMouseLeave" in js
    body = _function_body(js, "initOrbital")
    assert "rect.width < 80" in body
    assert "card.addEventListener('mouseenter', () =>" not in body
    assert "card.addEventListener('mouseleave', () =>" not in body


def test_nav_tabs_are_built_once_and_then_only_toggle_active_classes():
    js = _read_all_launcher_js()
    body = _function_body(js, "updateNavTabs")

    assert "if (!container.dataset.built)" in body
    assert "querySelectorAll('.nav-tab[data-app]')" in body
    assert "tab.classList.toggle" in body
    assert "container.innerHTML = `" not in body


def test_hidden_platform_overlay_images_are_lazy_loaded():
    html = INDEX_HTML.read_text(encoding="utf-8")
    overlay_start = html.index('<div class="platform-info-overlay"')
    overlay_end = html.index("<!-- ── About DEEPX View ── -->", overlay_start)
    overlay = html[overlay_start:overlay_end]

    images = re.findall(r"<img\s+[^>]*>", overlay)
    assert images
    assert all('loading="lazy"' in image for image in images)


def test_launcher_uses_single_global_click_handler_for_passive_closers():
    js = _read_all_launcher_js()

    assert "function handleDocumentClick(" in js
    assert js.count("document.addEventListener('click',") == 1
