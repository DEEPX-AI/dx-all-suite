"""DX App ModelZoo tab — every catalog task name shows in the chosen language.

The public catalog names tasks slightly differently from the label table: 'Face Attribute
Recognition' vs face_attribute, 'Image De-noising' vs image_denoising, 'Zero Shot Image
Classification' vs zero_shot_image_classification. Unless those names are mapped, their chips
and badges stay English on every non-English screen.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','ko')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    pg.wait_for_function("() => typeof S !== 'undefined' && S.catLabels && Object.keys(S.catLabels).length > 10", timeout=20000)
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


def test_every_catalog_task_has_a_korean_label(page):
    data = json.loads((ROOT / "dx_app/scripts/modelzoo_catalog_public.json").read_text(encoding="utf-8"))
    catalog = data.get("models", []) if isinstance(data, dict) else data
    tasks = sorted({m["task"] for m in catalog if isinstance(m, dict) and m.get("task")})
    assert len(tasks) > 20, tasks
    shown = page.evaluate("ts => ts.map(t => [t, catText(t)])", tasks)
    untranslated = [t for t, label in shown if label == t or all(ord(ch) < 128 for ch in label)]
    assert not untranslated, untranslated
    assert page.evaluate("catText('Image De-noising')") != "Image De-noising"   # the live catalog spells it so


def test_lab_home_tiles_form_a_grid(page):
    """class="grid" needs CSS; without it #lab-home is display:block and the six tiles stack at
    ragged widths at every screen size."""
    page.evaluate("nav('lab')")
    page.wait_for_timeout(400)
    got = page.evaluate("""() => { const g = document.getElementById('lab-home');
        const rows = new Set([...g.children].map(c => Math.round(c.getBoundingClientRect().top)));
        const widths = new Set([...g.children].map(c => Math.round(c.getBoundingClientRect().width)));
        return {display: getComputedStyle(g).display, rows: rows.size, widths: widths.size}; }""")
    assert got["display"] == "grid", got
    assert got["rows"] < 6 and got["widths"] == 1, got      # side by side, equal widths at 1440
