"""Shared graph canvas in a browser: connect by dragging, refuse an illegal edge with its reason, undo/redo, keyboard,
copy/paste, palette drop, accessibility and a theme repaint.

The component is mounted on a bare page (the launcher server only serves the shared static files), so these tests
hold for any page that uses it, not only the Graph Composer.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

PAGE = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="/static/shared/dx-tokens.css"><link rel="stylesheet" href="/static/shared/dx-semantic.css">
<link rel="stylesheet" href="/static/shared/dx-theme-light.css"><link rel="stylesheet" href="/static/shared/dx-base.css">
<link rel="stylesheet" href="/static/shared/dx-graph-canvas.css">
<script src="/static/shared/dx-theme.js"></script><script src="/static/shared/dx-icon.js"></script>
<script src="/static/shared/dx-graph-core.js"></script><script src="/static/shared/dx-graph-canvas.js"></script>
</head><body style="margin:0"><div id="host" style="width:900px;height:500px"></div>
<button id="after">after</button></body></html>"""

MOUNT = """() => {
  window.__changes = []; window.__sel = null; window.__activated = null;
  window.cv = DXGraphCanvas.create(document.getElementById('host'), {
    categories: {source: {slot: 1}, model: {slot: 3, icon: 'cpu'}},
    canConnect: (f, t) => t.noInput ? {ok: false, reason: 'needs a full frame'} : {ok: true, kind: 'frame', label: ''},
    onChange: (g, info) => window.__changes.push(info.reason),
    onSelect: s => { window.__sel = s; },
    onActivate: item => { window.__activated = item; },
    onDrop: p => ({id: p.id, label: p.id, sub: 'dropped', category: 'model'}),
  });
  cv.setGraph({nodes: [
      {id: 'cam', label: 'cam', sub: 'Source', category: 'source', icon: 'camera', noInput: true, x: 40, y: 120},
      {id: 'od', label: 'od', sub: 'yolo26-n_640x640', category: 'model', icon: 'cpu', x: 340, y: 120}],
    edges: []}, {fit: false});
}"""


@pytest.fixture(scope="module")
def port():
    server, port = start_module_server("launcher")
    yield port
    server.shutdown()


@pytest.fixture(scope="module")
def browser():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    yield br
    br.close()
    pw.stop()


@pytest.fixture
def page(browser, port):
    ctx = browser.new_context(viewport={"width": 1100, "height": 700})
    ctx.add_init_script("try { localStorage.setItem('dx-theme', 'dark'); } catch (e) {}")
    pg = ctx.new_page()
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.route(f"http://127.0.0.1:{port}/__graph", lambda r: r.fulfill(status=200, content_type="text/html", body=PAGE))
    pg.goto(f"http://127.0.0.1:{port}/__graph", wait_until="load")
    pg.evaluate(MOUNT)
    pg.wait_for_timeout(100)
    yield pg
    assert not errors, errors
    ctx.close()


def _drag(page, a, b):
    page.mouse.move(*a)
    page.mouse.down()
    page.mouse.move((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    page.mouse.move(*b)
    page.mouse.up()


def test_dragging_from_an_output_port_to_an_input_port_connects(page):
    # cam's output port is at its right edge (40 + 160, 120 + 56 / 2); od's input port at its left edge.
    _drag(page, (200, 148), (340, 148))
    assert page.evaluate("cv.getGraph().edges.map(e => e.id)") == ["cam->od"]
    assert page.evaluate("window.__changes") == ["connect"]
    assert page.inner_text(".dxg-live") == "Connected cam to od"


def test_a_refused_connection_says_why_and_adds_nothing(page):
    _drag(page, (500, 148), (100, 148))     # od -> cam: a source takes no input
    assert page.evaluate("cv.getGraph().edges") == []
    assert page.inner_text(".dxg-live") == "Cannot connect: needs a full frame"


def test_a_cycle_is_refused(page):
    page.evaluate("cv.connect('cam', 'od')")
    page.evaluate("cv.addNode({id: 'x', label: 'x', category: 'model'}, {x: 720, y: 148})")
    page.evaluate("cv.connect('od', 'x')")
    r = page.evaluate("cv.connect('x', 'od')")
    assert r == {"ok": False, "reason": "This would create a cycle"}
    assert page.evaluate("cv.getGraph().edges.length") == 2


def test_undo_and_redo_with_the_keyboard(page):
    page.evaluate("cv.addNode({id: 'seg', label: 'seg', category: 'model'})")
    page.focus(".dxg-canvas")
    page.keyboard.press("Control+z")
    assert "seg" not in page.evaluate("cv.getGraph().nodes.map(n => n.id)")
    page.keyboard.press("Control+y")
    assert "seg" in page.evaluate("cv.getGraph().nodes.map(n => n.id)")
    assert page.evaluate("cv.canUndo()") and not page.evaluate("cv.canRedo()")


def test_tab_arrows_and_delete(page):
    page.focus(".dxg-canvas")
    page.keyboard.press("Tab")
    assert page.evaluate("window.__sel") == {"nodes": ["cam"], "edge": None}
    assert page.inner_text(".dxg-live") == "Selected cam, Source"
    page.keyboard.press("ArrowRight")
    assert page.evaluate("cv.getGraph().nodes[0].x") == 60
    page.keyboard.press("Enter")
    assert page.evaluate("window.__activated") == {"type": "node", "id": "cam"}
    page.keyboard.press("Tab")
    assert page.evaluate("window.__sel.nodes") == ["od"]
    page.keyboard.press("Delete")
    assert page.evaluate("cv.getGraph().nodes.map(n => n.id)") == ["cam"]
    page.keyboard.press("Tab")     # nothing focused after a delete: Tab starts again at the first node
    assert page.evaluate("window.__sel.nodes") == ["cam"]
    page.keyboard.press("Tab")     # past the last node: focus leaves the canvas
    assert page.evaluate("document.activeElement.className") != "dxg-canvas"


def test_copy_paste_gives_new_ids(page):
    page.evaluate("cv.select({nodes: ['od']})")
    page.focus(".dxg-canvas")
    page.keyboard.press("Control+c")
    page.keyboard.press("Control+v")
    assert page.evaluate("cv.getGraph().nodes.map(n => n.id)") == ["cam", "od", "od_2"]
    assert page.evaluate("cv.selection().nodes") == ["od_2"]


def test_a_palette_drop_adds_a_node_where_it_lands(page):
    page.evaluate("""() => {
      const dt = new DataTransfer();
      dt.setData(DXGraphCanvas.DND_TYPE, JSON.stringify({id: 'depth'}));
      document.getElementById('host').dispatchEvent(new DragEvent('drop', {dataTransfer: dt, clientX: 600, clientY: 400, bubbles: true, cancelable: true}));
    }""")
    node = page.evaluate("cv.getGraph().nodes.find(n => n.id === 'depth')")
    assert node and node["sub"] == "dropped"
    assert (node["x"], node["y"]) == (520, 380)     # centred on the drop point, on the grid


def test_the_canvas_is_an_accessible_application(page):
    assert page.get_attribute(".dxg-canvas", "role") == "application"
    assert "Tab moves between nodes" in page.get_attribute(".dxg-canvas", "aria-label")
    labels = page.eval_on_selector_all(".dxg-tbtn", "els => els.map(e => e.getAttribute('aria-label'))")
    assert labels == ["Zoom out", "Zoom in", "Fit view", "Auto layout", "Undo", "Redo"]
    assert page.get_attribute(".dxg-minimap", "role") != "img", "the minimap is clickable, so it is not an image"
    page.evaluate("cv.select({nodes: ['od']})")
    page.focus(".dxg-canvas")
    page.keyboard.press("Shift+F10")
    items = page.eval_on_selector_all(".dxg-menu [role=menuitem]", "els => els.map(e => e.textContent)")
    assert items[0].startswith("Delete")
    assert page.evaluate("document.activeElement.getAttribute('role')") == "menuitem"
    page.keyboard.press("Escape")
    assert page.locator(".dxg-menu").count() == 0


def test_badges_tints_labels_and_zoom_paint_without_errors(page):
    page.evaluate("cv.connect('cam', 'od')")
    page.evaluate("""() => {
      cv.updateEdge('cam->od', {label: 'ROI · person'}, {commit: false});
      cv.setBadges({od: [{kind: 'error', text: 'error'}, {kind: 'mem', text: '118 MB'}, {kind: 'ms', text: '3.2 ms'}]});
      cv.setTints({od: 0.7});
      cv.setEdgeStatus({'cam->od': 'error'});
    }""")
    page.mouse.move(450, 300)
    page.mouse.wheel(0, -200)
    page.wait_for_timeout(100)
    assert page.inner_text(".dxg-zoom") != "100%"
    page.click(".dxg-tbtn[aria-label='Fit view']")
    page.wait_for_timeout(50)


def test_the_canvas_repaints_when_the_theme_changes(page):
    def background():
        page.wait_for_timeout(120)
        return page.evaluate("""() => {
          const d = document.querySelector('.dxg-canvas').getContext('2d').getImageData(2, 2, 1, 1).data;
          return 0.299 * d[0] + 0.587 * d[1] + 0.114 * d[2];
        }""")
    dark = background()
    page.evaluate("DXTheme.setTheme('light')")
    light = background()
    assert dark < 80 < light, (dark, light)


def _pixel(page, x, y):
    return page.evaluate("""([x, y]) => {
      const c = document.querySelector('.dxg-canvas'), r = c.getBoundingClientRect(), k = c.width / r.width;
      return Array.from(c.getContext('2d').getImageData(Math.round(x * k), Math.round(y * k), 1, 1).data.slice(0, 3));
    }""", [x, y])


def test_the_arrowhead_shows_left_of_the_input_port(page):
    page.evaluate("cv.connect('cam', 'od')")
    page.wait_for_timeout(100)
    # od's input port is at world (340, 148); the arrow tip sits just outside the 6 px port, so 6 px further left and
    # 2 px below the line the arrowhead is drawn, where the bare canvas would show only the background.
    tip, bg = _pixel(page, 327, 150), _pixel(page, 327, 190)
    assert sum(abs(a - b) for a, b in zip(tip, bg)) > 60, (tip, bg)


def test_a_node_without_an_icon_draws_its_category_icon(page):
    page.evaluate("""() => {
      window.__icons = [];
      const draw = DXIcon.draw;
      DXIcon.draw = function (ctx, name) { window.__icons.push(name); return draw.apply(this, arguments); };
      cv.setGraph({nodes: [{id: 'm', label: 'm', category: 'model', x: 0, y: 0},
                           {id: 'q', label: 'q', category: 'nowhere', x: 300, y: 0}], edges: []}, {fit: false});
    }""")
    page.wait_for_timeout(100)
    icons = page.evaluate("window.__icons")
    assert "cpu" in icons and "circle" not in icons, icons


def test_the_minimap_shows_the_whole_viewport_rectangle(page):
    page.wait_for_timeout(100)
    r = page.evaluate("""() => {
      const m = document.querySelector('.dxg-minimap'), mm = m._map, v = cv.view(), c = document.querySelector('.dxg-canvas');
      const x = (-v.offsetX / v.zoom - mm.ox) * mm.s, y = (-v.offsetY / v.zoom - mm.oy) * mm.s;
      return {x: x, y: y, w: c.clientWidth / v.zoom * mm.s, h: c.clientHeight / v.zoom * mm.s, mw: m.clientWidth, mh: m.clientHeight};
    }""")
    assert r["x"] >= -0.5 and r["y"] >= -0.5, r
    assert r["x"] + r["w"] <= r["mw"] + 0.5 and r["y"] + r["h"] <= r["mh"] + 0.5, r


def test_the_minimap_moves_the_view_by_touch_too(page):
    before = page.evaluate("cv.view()")
    box = page.locator(".dxg-minimap").bounding_box()
    page.evaluate("""([x, y]) => {
      const m = document.querySelector('.dxg-minimap');
      const t = new Touch({identifier: 1, target: m, clientX: x, clientY: y});
      m.dispatchEvent(new TouchEvent('touchstart', {touches: [t], changedTouches: [t], bubbles: true, cancelable: true}));
    }""", [box["x"] + 10, box["y"] + 10])
    page.wait_for_timeout(50)
    assert page.evaluate("cv.view()") != before


def test_the_edge_hit_area_stays_eight_screen_pixels_at_any_zoom(page):
    page.evaluate("cv.connect('cam', 'od')")
    # The edge runs from world (200, 148) to (340, 148). At 300 % its middle (270, 148) lands on screen (450, 250).
    page.evaluate("cv.setView({zoom: 3, offsetX: 450 - 270 * 3, offsetY: 250 - 148 * 3}); cv.select({})")
    page.mouse.click(450, 265)       # 15 screen px off the line: 5 world px, inside a world-sized 8 px threshold
    assert page.evaluate("cv.selection().edge") is None
    page.mouse.click(450, 254)
    assert page.evaluate("cv.selection().edge") == "cam->od"


def test_a_right_drag_opens_the_menu_and_does_not_pan(page):
    before = page.evaluate("cv.view()")
    page.mouse.move(700, 400)
    page.mouse.down(button="right")
    page.mouse.move(760, 440)
    page.mouse.up(button="right")
    assert page.evaluate("cv.view()") == before
    assert page.locator(".dxg-menu").count() == 1


def test_menu_separators_and_empty_text(page):
    page.mouse.click(700, 400, button="right")
    assert page.eval_on_selector_all(".dxg-menu hr", "els => els.map(e => e.getAttribute('role'))") == ["separator", "separator"]
    page.keyboard.press("Escape")
    page.evaluate("""() => {
      cv.destroy();
      window.__texts = [];
      const fill = CanvasRenderingContext2D.prototype.fillText;
      CanvasRenderingContext2D.prototype.fillText = function (s) { window.__texts.push(s); return fill.apply(this, arguments); };
      window.cv = DXGraphCanvas.create(document.getElementById('host'), {emptyText: 'Pick a template'});
    }""")
    assert "Pick a template" in page.evaluate("window.__texts")


def test_destroy_removes_every_listener_and_pending_work(page):
    leaks = page.evaluate("""() => {
      cv.destroy();
      const host = document.getElementById('host'), live = new Map(), frames = new Set();
      const key = (t, type, fn) => (t === window ? 'window' : t === document ? 'document' : 'host') + ':' + type;
      const add = EventTarget.prototype.addEventListener, remove = EventTarget.prototype.removeEventListener;
      EventTarget.prototype.addEventListener = function (type, fn, o) {
        if (this === window || this === document || this === host) live.set(fn, key(this, type));
        return add.call(this, type, fn, o);
      };
      EventTarget.prototype.removeEventListener = function (type, fn, o) { live.delete(fn); return remove.call(this, type, fn, o); };
      const raf = window.requestAnimationFrame, caf = window.cancelAnimationFrame;
      window.requestAnimationFrame = fn => { const id = raf(() => { frames.delete(id); fn(); }); frames.add(id); return id; };
      window.cancelAnimationFrame = id => { frames.delete(id); caf(id); };
      let themeHooks = 0;
      const hook = DXTheme.onThemeChange;
      DXTheme.onThemeChange = function () { themeHooks++; return hook.apply(this, arguments); };
      const c = DXGraphCanvas.create(host, {});
      c.setGraph({nodes: [{id: 'a', x: 0, y: 0}], edges: []});
      c.repaint();
      c.destroy();
      EventTarget.prototype.addEventListener = add; EventTarget.prototype.removeEventListener = remove;
      window.requestAnimationFrame = raf; window.cancelAnimationFrame = caf; DXTheme.onThemeChange = hook;
      return {listeners: Array.from(live.values()), frames: frames.size, themeHooks: themeHooks};
    }""")
    assert leaks == {"listeners": [], "frames": 0, "themeHooks": 0}


def test_a_destroyed_canvas_ignores_drops(page):
    page.evaluate("""() => {
      cv.destroy();
      window.__changes = []; window.__changes2 = [];
      window.cv2 = DXGraphCanvas.create(document.getElementById('host'), {onChange: (g, i) => window.__changes2.push(i.reason)});
      const dt = new DataTransfer();
      dt.setData(DXGraphCanvas.DND_TYPE, JSON.stringify({id: 'depth'}));
      document.getElementById('host').dispatchEvent(new DragEvent('drop', {dataTransfer: dt, clientX: 600, clientY: 400, bubbles: true, cancelable: true}));
    }""")
    assert page.evaluate("window.__changes") == []
    assert page.evaluate("window.__changes2") == ["add"]


def test_the_theme_repaint_follows_the_theme_event(page):
    page.evaluate("""() => {
      window.__paints = 0;
      const ctx = document.querySelector('.dxg-canvas').getContext('2d'), fill = ctx.fillRect;
      ctx.fillRect = function () { window.__paints++; return fill.apply(this, arguments); };
      window.dispatchEvent(new CustomEvent('dx-theme-applied', {detail: {theme: 'light'}}));
    }""")
    page.wait_for_timeout(150)
    assert page.evaluate("window.__paints") > 0


def test_brackets_walk_the_focused_nodes_edges_and_delete_removes_one(page):
    page.evaluate("cv.addNode({id: 'x', label: 'x', category: 'model'}, {x: 720, y: 300})")
    page.evaluate("cv.connect('cam', 'od'); cv.connect('od', 'x')")
    page.evaluate("cv.updateEdge('od->x', {label: 'ROI · person'}); cv.setEdgeStatus({'od->x': 'error'})")
    page.evaluate("cv.select({nodes: ['od']})")
    page.focus(".dxg-canvas")
    page.keyboard.press("]")
    assert page.evaluate("window.__sel") == {"nodes": [], "edge": "cam->od"}
    assert page.inner_text(".dxg-live") == "Edge cam to od"
    page.keyboard.press("]")
    assert page.evaluate("window.__sel.edge") == "od->x"
    assert page.inner_text(".dxg-live") == "Edge od to x, ROI · person, Error"
    page.keyboard.press("]")
    assert page.evaluate("window.__sel.edge") == "cam->od", "wraps around"
    page.keyboard.press("[")
    assert page.evaluate("window.__sel.edge") == "od->x"
    page.keyboard.press("Delete")
    assert page.evaluate("cv.getGraph().edges.map(e => e.id)") == ["cam->od"]
    assert [n["id"] for n in page.evaluate("cv.getGraph().nodes")] == ["cam", "od", "x"]


def test_a_selection_announces_its_badges(page):
    page.evaluate("cv.setBadges({od: [{kind: 'error', text: 'MODEL_LOAD'}, {kind: 'missing', text: 'not installed'}, {kind: 'mem', text: '118 MB'}, {kind: 'ms', text: '3.2 ms'}]})")
    page.focus(".dxg-canvas")
    page.keyboard.press("Tab")
    page.keyboard.press("Tab")
    assert page.inner_text(".dxg-live") == "Selected od, yolo26-n_640x640, MODEL_LOAD, not installed, 118 MB, 3.2 ms"


def test_align_and_distribute_from_the_menu_and_the_keyboard(page):
    page.evaluate("cv.addNode({id: 'x', label: 'x', category: 'model'}, {x: 720, y: 330})")
    page.evaluate("cv.select({nodes: ['cam', 'od', 'x']})")
    page.focus(".dxg-canvas")
    page.keyboard.press("Shift+F10")
    items = page.eval_on_selector_all(".dxg-menu [role=menuitem]", "els => els.map(e => e.firstChild.textContent)")
    for name in ("Align left", "Align center", "Align top", "Align middle", "Distribute horizontally", "Distribute vertically"):
        assert name in items, items
    page.click(".dxg-menu [role=menuitem]:has-text('Align top')")
    assert {n["y"] for n in page.evaluate("cv.getGraph().nodes")} == {120}
    assert page.evaluate("window.__changes")[-1] == "align"
    page.keyboard.press("Alt+KeyA")         # align left
    assert {n["x"] for n in page.evaluate("cv.getGraph().nodes")} == {40}
    page.keyboard.press("Control+z")
    page.keyboard.press("Alt+Shift+KeyH")   # distribute horizontally: 40 .. 640, the middle one at 340
    assert sorted(n["x"] for n in page.evaluate("cv.getGraph().nodes")) == [40, 340, 640]
    for key in ("Align left", "Align center", "Align top", "Align middle", "Distribute horizontally", "Distribute vertically"):
        assert page.evaluate("k => DXGraphCanvas.STRINGS.includes(k)", key), key
