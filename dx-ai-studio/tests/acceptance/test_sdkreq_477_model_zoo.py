"""SDKREQ-477 [Model Zoo] browse and run models — DX Model Zoo inside a real ./launcher.sh studio.

Run Inference goes through DX App (the launcher's DX App) to the board's NPU.
"""
from __future__ import annotations

import json

from tests.acceptance.conftest import http_get, module_frame, wait_home
from tests.acceptance.hardware import need

SECTIONS = ["sectionQuickFacts", "sectionSpec", "sectionCompile", "sectionUseCase", "sectionExample", "demoSection",
            "sectionLegal"]


def _zoo(pages, path="", lang="en"):
    page = pages.new("/", lang=lang)
    wait_home(page)
    page.evaluate("(h) => DXLauncher.launch('zoo', h ? { hash: h } : undefined)", path)
    frame = module_frame(page, "zoo", ready="#searchInput")
    if path:
        frame.evaluate("(h) => { if (location.hash !== h) location.hash = h; }", path)
    return page, frame


def _catalog(studio):
    d = json.loads(http_get(studio.base + "/zoo/api/catalog", headers={"Sec-Fetch-Dest": "empty"})[2])
    return d.get("models", d) if isinstance(d, dict) else d


def _downloaded_detector(studio) -> dict:
    ms = [m for m in _catalog(studio) if (m.get("downloaded_qlite") or m.get("downloaded"))
          and m.get("category") == "object_detection"]
    assert ms, "no downloaded object detection model in the Model Zoo"
    for pref in ("yolov8n", "yolo26n", "yolov5s"):
        for m in ms:
            if m.get("id") == pref:
                return m
    return ms[0]


def _ids(frame):
    return frame.locator("[data-model-id]").evaluate_all("els => [...new Set(els.map(e => e.dataset.modelId))]")


def test_explorer_views_category_search_sort_and_reset(pages):
    page, frame = _zoo(pages)
    frame.locator(".mz-card").first.wait_for(timeout=30000)
    frame.locator("#btnListView").click()
    frame.locator("table.mz-list-table").wait_for(timeout=10000)
    frame.locator("#btnCardView").click()
    frame.locator(".mz-card").first.wait_for(timeout=10000)
    first = _ids(frame)[:5]
    frame.select_option("#sortSelect", "fps")
    frame.wait_for_function("(a) => JSON.stringify([...new Set([...document.querySelectorAll('[data-model-id]')]"
                            ".map(e => e.dataset.modelId))].slice(0, 5)) !== JSON.stringify(a)", arg=first, timeout=10000)
    assert set(frame.locator("#sortSelect option").evaluate_all("els => els.map(e => e.value)")) >= {"name", "category", "fps"}
    frame.locator("#searchInput").fill("yolov8")
    frame.wait_for_function("() => [...document.querySelectorAll('.mz-card')].every(c => /yolov8/i.test(c.textContent))",
                            timeout=10000)
    frame.locator("#resetFiltersBtn").click()
    frame.wait_for_function("() => document.getElementById('searchInput').value === '' &&"
                            " document.getElementById('sortSelect').value === 'name'", timeout=10000)
    cat = frame.locator("#categoryChips input[data-cat]").nth(1)
    wanted = cat.get_attribute("data-cat")
    cat.check(force=True)
    frame.wait_for_function("(c) => [...document.querySelectorAll('.mz-card .mz-card-cat')].length > 0", arg=wanted,
                            timeout=10000)


def test_the_explorer_keeps_showing_models_as_you_scroll(pages):
    page, frame = _zoo(pages)
    frame.locator(".mz-card").first.wait_for(timeout=30000)
    seen = set(_ids(frame))
    for _ in range(12):
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(150)
    frame.evaluate("() => { const s = document.scrollingElement; s.scrollTop = s.scrollHeight;"
                   " document.querySelectorAll('*').forEach(e => { if (e.scrollHeight > e.clientHeight + 400) e.scrollTop = e.scrollHeight; }); }")
    page.wait_for_timeout(500)
    later = set(_ids(frame))
    assert later - seen, "scrolling brings models the top did not show"


def test_model_detail_has_its_sections_code_tabs_and_downloads(pages, studio):
    model = _downloaded_detector(studio)
    page, frame = _zoo(pages, f"#model={model['id']}")
    frame.locator("#sectionSpec").wait_for(timeout=30000)
    for sec in SECTIONS:
        assert frame.locator(f"#{sec}").count() == 1, sec
    spec = frame.locator("#sectionSpec").inner_text().lower()
    assert "accuracy matrix" in spec and "runtime performance" in spec
    assert "how to compile dxnn" in frame.locator("#sectionCompile").inner_text().lower()
    tabs = [t.strip() for t in frame.locator("#demoSection .mz-code-tab").all_inner_texts()]
    assert any("C++" in t for t in tabs) and any("Python" in t for t in tabs), tabs
    badges = " ".join(frame.locator(".mz-download-badge").all_inner_texts())
    assert "Q-Lite" in badges and "Q-Pro" in badges, badges
    rows = frame.locator(".mz-artifact-table tbody tr")
    assert rows.count() >= 5
    href = frame.locator("a.mz-artifact-link").first.get_attribute("href")
    if href.startswith("/"):     # local bytes (200), the CDN (302) or not published yet (404) — never an error page
        url = studio.base + ("/zoo" + href if href.startswith("/api") else href)
        status = http_get(url, timeout=30, headers={"Sec-Fetch-Dest": "empty"}, follow=False)[0]
        assert status in (200, 302, 404), status
    assert frame.locator('[data-quant="qlite"]').count() >= 1, "DX App is running, so Download Q-Lite is offered"


def test_run_inference_with_the_default_image_on_the_npu(pages, studio):
    need("npu")
    model = _downloaded_detector(studio)
    page, frame = _zoo(pages, f"#model={model['id']}")
    frame.locator("#sectionExample").wait_for(timeout=30000)
    frame.evaluate("() => document.querySelectorAll('#sectionExample details').forEach(d => d.open = true)")
    btn = frame.locator("#btnRunDefault")
    btn.wait_for(state="visible", timeout=30000)
    frame.wait_for_function("() => !document.getElementById('btnRunDefault').disabled", timeout=30000)
    btn.click()
    frame.wait_for_function(
        "() => [...document.querySelectorAll('#inferenceResult img, #inferenceResultUpload img')]"
        ".some(i => i.complete && i.naturalWidth > 0)", timeout=180000)


def test_without_dx_app_run_inference_is_disabled_with_a_reason(pages, studio):
    model = _downloaded_detector(studio)
    page = pages.new(None)
    def health(route):
        if "/zoo/" in (route.request.headers.get("referer") or ""):    # Model Zoo's own health, not the launcher's
            route.fulfill(status=200, content_type="application/json",
                          body=json.dumps({"ok": True, "dx_app_alive": False}))
        else:
            route.continue_()

    page.route("**/api/health", health)
    page.goto(pages.studio.base + "/", wait_until="domcontentloaded")
    wait_home(page)
    page.evaluate("() => DXLauncher.launch('zoo')")
    frame = module_frame(page, "zoo", ready="#searchInput")
    frame.evaluate("(h) => { location.hash = h; }", f"#model={model['id']}")
    frame.locator("#sectionExample").wait_for(timeout=30000)
    frame.evaluate("() => document.querySelectorAll('#sectionExample details').forEach(d => d.open = true)")
    frame.wait_for_function("() => { const b = document.getElementById('btnRunDefault'); return b && b.disabled; }",
                            timeout=30000)
    assert "DX App is not running" in frame.locator("#inferencePanel").inner_text()


def test_save_as_html_downloads_the_model_card(pages, studio):
    model = _downloaded_detector(studio)
    page, frame = _zoo(pages, f"#model={model['id']}")
    btn = frame.locator('button[onclick^="exportModelCardHtml"]')
    btn.wait_for(timeout=30000)
    with page.expect_download(timeout=60000) as dl:
        btn.click()
    path = dl.value.path()
    html = open(path, encoding="utf-8").read()
    assert "<html" in html.lower() and len(html) > 1000
