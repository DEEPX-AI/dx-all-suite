"""Home's effects: contracts on how things move.

What is visible on screen is the browser tests' job. This file checks the rules: transform and opacity only,
the Web Animations API for JS, reduced motion respected, and the shared script only in documents that opt in.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "launcher" / "static"
SHARED = ROOT / "shared" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
CSS = (STATIC / "home-stage.css").read_text(encoding="utf-8")


def _effects() -> str:
    path = STATIC / "home-effects.js"
    assert path.is_file(), "launcher/static/home-effects.js 가 없다"
    return path.read_text(encoding="utf-8")


def _rule(selector: str) -> str:
    m = re.search(r"(?:^|\n)" + re.escape(selector) + r"\s*\{([^}]*)\}", CSS)
    assert m, f"{selector} 규칙이 없다"
    return m.group(1)


def test_the_effects_script_is_served_and_loaded():
    launcher = (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert 'path == "/home-effects.js"' in launcher
    assert 'src="/home-effects.js"' in HTML


def test_js_effects_respect_reduced_motion():
    js = _effects()
    assert "prefers-reduced-motion: reduce" in js


def test_js_effects_use_web_animations_not_class_reinsertion():
    """Removing a class, forcing reflow with offsetWidth and adding it back triggers layout on every keystroke."""
    js = _effects()
    assert ".animate(" in js
    assert "offsetWidth" not in js and "offsetHeight" not in js


def test_the_stage_background_belongs_to_the_home_only():
    frame = (STATIC / "launcher-app-frame.js").read_text(encoding="utf-8")
    assert "classList.toggle('home-visible', viewName === 'home')" in frame
    body = _rule("body.home-visible")
    assert "radial-gradient" in body and "background-attachment: fixed" in body


def test_the_input_glow_is_a_grid_item_not_a_positioned_layer():
    assert "display: grid" in _rule(".ask-box")
    glow = _rule(".ask-box::after")
    assert "grid-row: 1 / -1" in glow and "pointer-events: none" in glow
    assert "opacity: 0" in glow


def test_the_input_glow_is_driven_on_its_pseudo_element():
    js = _effects()
    assert "pseudoElement: '::after'" in js
    assert "240" in js, "키 입력 빛은 240ms 에 가라앉는다 (spec §7 #3)"


def test_book_hover_tilts_the_cover_with_transform():
    hover = re.search(r"\.about-book-card:is\(:hover, :focus-visible\) \.orbital-icon\s*\{([^}]*)\}", CSS)
    assert hover and "rotateY(-8deg)" in hover.group(1)


def test_the_poster_thumbnail_grows_on_hover():
    hover = re.search(r"\.stage-film:is\(:hover, :focus-visible\) img\s*\{([^}]*)\}", CSS)
    assert hover and "scale(1.06)" in hover.group(1)


def test_theme_and_language_fade_only_where_a_page_opts_in():
    """It is a shared script: the document opts in, so not all nine modules get the cross-fade."""
    for name in ("dx-theme.js", "i18n.js"):
        js = (SHARED / name).read_text(encoding="utf-8")
        assert "startViewTransition" in js, name
        assert "dxFade" in js, f"{name} 가 opt-in 을 보지 않는다"
        assert "prefers-reduced-motion: reduce" in js, name
    assert re.search(r"<html [^>]*data-dx-fade", HTML), "launcher 가 opt-in 하지 않았다"


def test_the_fade_lengths_are_the_spec_ones():
    for kind, ms in (("theme", 600), ("lang", 200)):
        pat = (r'html\[data-dx-fading="' + kind + r'"\]::view-transition-old\(root\),\s*'
               r'html\[data-dx-fading="' + kind + r'"\]::view-transition-new\(root\)\s*\{[^}]*'
               r"animation-duration:\s*" + str(ms) + "ms")
        assert re.search(pat, CSS), kind


# ── continuous effects ────────────────────────────────────────────────────

WIDGETS = (STATIC / "home-widgets.js").read_text(encoding="utf-8")


def test_the_placeholder_types_the_cycle_at_the_spec_pace():
    js = _effects()
    assert "DXHomePlaceholders" in js
    for name, ms in (("TYPE_MS", 45), ("HOLD_MS", 1800), ("ERASE_MS", 20)):
        assert re.search(name + r"\s*=\s*" + str(ms) + r"\b", js), name
    assert "'focus'" in js and "'blur'" in js, "포커스하면 멈추고 떠나면 다시"
    assert "document.hidden" in js, "가려진 탭에서는 멈춘다"


def test_core_bars_move_by_transform_and_smooth_over_300ms():
    bar = _rule(".dev-core i")
    assert "scaleY(" in bar and "height:" not in bar.replace("height: 100%", "")
    assert re.search(r"transition:\s*transform 300ms", bar)


def test_an_idle_device_breathes_every_four_seconds():
    assert re.search(r"\.stage-device\.is-idle \.dev-core i\s*\{[^}]*animation:\s*dev-breathe 4s", CSS)
    assert "@keyframes dev-breathe" in CSS
    assert "is-idle" in WIDGETS


def test_a_missing_device_dims_over_800ms():
    assert re.search(r"transition:\s*opacity 800ms", _rule(".stage-device"))


def test_the_headline_counts_up_over_700ms():
    assert re.search(r"COUNT_MS\s*=\s*700\b", WIDGETS)
    assert "requestAnimationFrame" in WIDGETS
    assert "prefers-reduced-motion: reduce" in WIDGETS


def test_the_cursor_light_is_a_grid_item_moved_by_transform():
    light = re.search(r'<div class="stage-light"[^>]*>', HTML)
    assert light and 'aria-hidden="true"' in light.group(0)
    assert HTML.index('class="stage-light"') < HTML.index('id="homeTour"'), "무대의 첫 층"
    wrap = _rule(".stage-light")
    assert "grid-row: 1 / -1" in wrap and "grid-column: 1 / -1" in wrap
    assert "z-index: -1" in wrap and "pointer-events: none" in wrap and "overflow: clip" in wrap
    assert "will-change: transform" in _rule(".stage-light > i")
    js = _effects()
    assert "translate3d(" in js and "requestAnimationFrame" in js


# ── motion ────────────────────────────────────────────────────────────────

def test_the_movement_constants_are_the_spec_ones():
    js = _effects()
    for name, value in (("STAGGER_MS", "60"), ("SWEEP_MS", "900"), ("FLY_MS", "600"),
                        ("NEAR_PX", "120"), ("MAX_SCALE", "1.18"), ("PRESS_SCALE", ".96")):
        assert re.search(name + r"\s*=\s*" + re.escape(value) + r"\b", js), name


def test_the_first_entry_plays_once_a_session():
    js = _effects()
    assert "dx-home-entered" in js and "sessionStorage" in js
    assert "MutationObserver" in js and "launcher-boot-pending" in js


def test_a_return_to_the_home_is_a_short_fade():
    body = _rule(".landing.home-stage.view-slide-in")
    assert re.search(r"animation:\s*stage-fade-in 200ms", body)
    assert re.search(r"@keyframes stage-fade-in\s*\{\s*from\s*\{\s*opacity:\s*0;\s*\}", CSS), "fade 는 opacity 만"


def test_the_answer_announces_where_it_routed():
    answer = (STATIC / "home-answer.js").read_text(encoding="utf-8")
    render = answer[answer.index("function render("):answer.index("function ask(")]
    assert "dx-home-routed" in render
    assert "'dx-home-routed'" in _effects()


def test_the_orb_and_the_sweep_live_in_the_stage_light():
    light = re.search(r'<div class="stage-light"[^>]*>(.*?)</div>', HTML, re.S).group(1)
    assert 'class="stage-sweep"' in light and 'class="stage-orb"' in light


def test_a_running_module_lights_its_glyph_by_opacity():
    """The glyph is a shared sprite (<use>), so the face brightness comes from the inherited variable
    --ico-fill-o, a registered (@property) number, which lets it transition over 400 ms."""
    assert "--ico-fill-o: 1" in _rule(".stage-deck .orbital-card.is-up .mod-glyph")
    assert re.search(r"transition:\s*--ico-fill-o 400ms", _rule(".stage-deck .mod-glyph"))
    assert re.search(r"@property --ico-fill-o\s*\{[^}]*syntax:\s*'<number>'", CSS)


def test_the_cursor_light_stays_off_without_gpu_acceleration():
    """Light passing under glass (backdrop-filter) makes the glass re-blur every frame. On a machine without a GPU
    (software rasterizer, headless included) frames take 50–85 ms; with the light off, none do.
    With a GPU it stays on. localStorage['dx-fx'] = 'full' | 'lite' chooses explicitly."""
    js = _effects()
    assert "failIfMajorPerformanceCaveat" in js
    assert "swiftshader" in js.lower() and "llvmpipe" in js, "ANGLE 위의 SwiftShader 는 caveat 로 걸리지 않는다"
    assert "'dx-fx'" in js
    light = js[js.index("function cursorLight()"):]
    light = light[:light.index("\n  }\n")]
    assert "lite()" in light, "커서 조명이 가벼운 모드를 보지 않는다"
