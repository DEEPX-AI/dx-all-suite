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

    # Only _setOrbStatus writes health state to the screen.
    for function_name in ("_setOrbStatus",):
        body = _function_body(js, function_name)
        assert "if (el && el.className !== targetClass)" in body
        assert "el.className = targetClass" in body


def test_home_does_not_relayout_module_cards_on_resize():
    """Resizing the home must cost nothing.

    The ring recomputed eight card positions and eight SVG connector lines on
    every resize, debounced at 120ms and watched by a ResizeObserver. A grid
    reflows in the compositor, so all of that machinery is gone — and this test
    is what keeps it from coming back.
    """
    js = _read_all_launcher_js()

    assert "scheduleOrbitalLayout" not in js
    assert "initOrbital(" not in js
    assert "orbital-ready" not in js
    assert "ensureStudioReady" in js
    # The hover tooltip existed because a ring card had nowhere to put its
    # detail — the panel had to float and be positioned by script. A grid card
    # has room underneath, so the listeners and the tooltip layer went too.
    assert "_handleOrbitalCardMouseEnter" not in js
    assert "_orbitalTooltipEl" not in js


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
