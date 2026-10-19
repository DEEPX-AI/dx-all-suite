"""Enabled text meets WCAG AA in explicit and system themes."""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.browser_support import resolve_chromium_executable  # noqa: E402
from tests.server_helpers import start_module_server  # noqa: E402

THEMES = (("light", "dark"), ("dark", "light"), ("system", "light"), ("system", "dark"))

_MEASURE = """
selector => {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = 1;
  const context = canvas.getContext('2d', {willReadFrequently: true});
  function rgba(value) {
    if (!CSS.supports('color', value)) throw new Error('Unsupported color: ' + value);
    context.clearRect(0, 0, 1, 1);
    context.fillStyle = value;
    context.fillRect(0, 0, 1, 1);
    const pixel = context.getImageData(0, 0, 1, 1).data;
    return [pixel[0], pixel[1], pixel[2], pixel[3] / 255];
  }
  function blend(fg, bg) {
    return fg.slice(0, 3).map((v, i) => v * fg[3] + bg[i] * (1 - fg[3])).concat(1);
  }
  function luminance(color) {
    const rgb = color.slice(0, 3).map(v => {
      v /= 255;
      return v <= 0.04045 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return rgb[0] * 0.2126 + rgb[1] * 0.7152 + rgb[2] * 0.0722;
  }
  return [...document.querySelectorAll(selector)].map(el => {
    if (!el.getBoundingClientRect().width || !el.getBoundingClientRect().height)
      throw new Error('Contrast target is not rendered: ' + el.outerHTML);
    const backgrounds = [];
    for (let node = el; node; node = node.parentElement) {
      const style = getComputedStyle(node);
      if (style.backgroundImage !== 'none')
        throw new Error('Image/gradient background requires pixel measurement');
      const color = rgba(style.backgroundColor);
      backgrounds.push(color);
      if (color[3] === 1) break;
    }
    let bg = [255, 255, 255, 1];
    backgrounds.reverse().forEach(color => { bg = blend(color, bg); });
    const fg = blend(rgba(getComputedStyle(el).color), bg);
    const a = luminance(fg), b = luminance(bg);
    return {text: el.textContent.trim(), classes: el.className,
            ratio: (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05)};
  });
}
"""


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        br = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
        yield br
        br.close()


@pytest.fixture(scope="module", params=["dx_app", "dx_stream", "dx_compiler", "dx_benchmark", "dx_monitor"])
def module_server(request):
    srv, port = start_module_server(request.param)
    yield request.param, port
    srv.shutdown()
    srv.server_close()


def _assert_aa(page, selector, theme):
    measurements = page.evaluate(_MEASURE, selector)
    assert measurements, selector
    failures = [item for item in measurements if item["ratio"] < 4.5]
    assert not failures, (theme, failures)


@pytest.mark.parametrize(("theme", "os_theme"), THEMES)
def test_affected_text_meets_aa(browser, module_server, theme, os_theme):
    module, port = module_server
    ctx = browser.new_context(color_scheme=os_theme, viewport={"width": 1440, "height": 900})
    ctx.add_init_script(
        "localStorage.setItem('dx-tutorial-mode','off');"
        f"localStorage.setItem('dx-theme','{theme}');"
    )
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
        page.wait_for_function("!!window.DXTheme")
        assert page.evaluate("DXTheme.resolved()") == (os_theme if theme == "system" else theme)
        page.evaluate("""module => {
          const fixture = document.createElement('div');
          fixture.id = 'contrast-fixture';
          fixture.style.cssText = 'position:fixed;top:100px;left:16px;z-index:99999;background:var(--surface-raised)';
          fixture.innerHTML = '<span class="badge b-cat">Category</span>' +
            '<span class="badge b-blue">Async</span><span class="badge b-red">Messaging</span>' +
            '<span class="txt-dim">Muted text</span><span class="badge b-ok">Installed</span>';
          if (module === 'dx_app') {
            fixture.innerHTML += '<button class="chip active">All</button>' +
              '<a class="txt-link">dxnn</a><button class="m-action-btn m-action-detail">Detail</button>' +
              '<button class="m-action-btn m-action-dl">Download</button>' +
              // 2026-10-11 axe: accent text on grey/tinted grounds, the A/B slot badge, the active chip's count
              '<button class="m-action-btn m-action-run">Run</button>' +
              '<div class="radio-group"><label><input type="radio" checked><span>Image</span></label></div>' +
              '<div class="run-tab-bar"><button class="run-tab active"><span>Single</span></button></div>' +
              '<span class="ab-slot-badge">A</span>' +
              '<button class="out-filter-chip active">All <span class="chip-count">3</span></button>' +
              '<div class="ref-cat-title">Getting started</div>';
          } else if (module === 'dx_stream') {
            fixture.innerHTML += '<button class="chip active">All</button>' +
              '<div class="element-card-props">11 properties</div>' +
              '<div class="card-grid"><div class="card"><span class="card-badge">Custom</span></div></div>' +
              '<div class="playback-mode-bar"><button class="btn btn-ghost btn-sm active"><span>Local (WebRTC)</span></button></div>';
          } else if (module === 'dx_compiler') {
            fixture.innerHTML += '<div class="resume-card"><span class="rc-badge">Re-quantize</span></div>' +
              '<div class="viewer-tabs"><button class="viewer-tab active">Input</button></div>' +
              '<div class="viewer-empty" style="position:static"><span>Load a model to visualize</span></div>';
          } else if (module === 'dx_benchmark') {
            fixture.innerHTML += '<table><thead><tr><th>Benchmark</th></tr></thead></table>' +
              '<p class="eyebrow"><span>DX-M1</span></p><button class="dashboard-tab active">E2E FPS Overview</button>';
          } else if (module === 'dx_monitor') {
            fixture.innerHTML += '<div class="btn-group"><button class="active"><span>Realtime</span></button></div>';
          }
          document.body.appendChild(fixture);
        }""", module)
        _assert_aa(page, "#contrast-fixture span, #contrast-fixture button, #contrast-fixture a,"
                   " #contrast-fixture th, #contrast-fixture .element-card-props, #contrast-fixture .ref-cat-title",
                   (module, theme, os_theme))
        if module == "dx_app":
            page.evaluate("nav('graph')")
            page.wait_for_selector("#gc-palette-list .gc-group-head")
            _assert_aa(page, "#gc-toolbar .btn-ghost, #gc-toolbar .btn-neutral, #gc-palette-list .gc-group-title,"
                       " [data-group='sources'] .gc-item-sub, .dxg-toolbar .dxg-zoom", (module, theme, os_theme))
        elif module == "dx_stream":
            page.evaluate("DXStream.nav('pipeline')")
            page.wait_for_selector("#palette-list .palette-group-title")
            _assert_aa(page, "#palette-list .palette-group-title > span:not(.palette-cat-icon)",
                       (module, theme, os_theme))
    finally:
        ctx.close()


@pytest.mark.parametrize(("theme", "os_theme"), THEMES)
def test_chat_status_line_and_settings_meet_aa(browser, theme, os_theme):
    """Chat settings: the status line, its Change link and the three choice cards."""
    import json
    srv, port = start_module_server("dx_planner")
    ctx = browser.new_context(color_scheme=os_theme, viewport={"width": 1440, "height": 900})
    ctx.add_init_script("localStorage.setItem('dx-tutorial-mode','off');"
                        f"localStorage.setItem('dx-theme','{theme}');")
    status = {"configured": False,
              "agents": [{"name": "claude", "installed": True, "authenticated": True, "login_hint": "claude"}],
              "source": {"kind": "auto", "provider": "agent-cli", "agent": "claude", "model": None}}
    ctx.route("**/api/chat/config", lambda r: r.fulfill(status=200, content_type="application/json",
                                                        body=json.dumps(status)))
    page = ctx.new_page()
    try:
        page.goto(f"http://127.0.0.1:{port}/", wait_until="load")
        page.wait_for_function("typeof DXChat !== 'undefined'")
        page.evaluate("DXChat.toggle()")
        page.wait_for_selector(".dx-chat-source button", state="visible")
        _assert_aa(page, ".dx-chat-source-text, .dx-chat-source-change", (theme, os_theme))
        page.click(".dx-chat-source button")
        page.wait_for_selector(".dx-chat-settings-panel.open")
        _assert_aa(page, ".dx-chat-kind-card b, .dx-chat-kind-card small, .dx-chat-settings-kind legend",
                   (theme, os_theme))
    finally:
        ctx.close()
        srv.shutdown()
        srv.server_close()
