"""Contract tests for the ModelZoo image optimizer and frontend virtualization."""

import importlib.util
import json
import re
from pathlib import Path

import pytest

_requires_pil = pytest.mark.skipif(
    importlib.util.find_spec("PIL") is None,
    reason="Pillow is required for image optimizer tests",
)

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "dx_modelzoo" / "scripts" / "optimize_images.py"
MODELZOO_JS = ROOT / "dx_modelzoo" / "static" / "js"


def load_optimizer():
    spec = importlib.util.spec_from_file_location(
        "modelzoo_optimize_images_under_test", SCRIPT
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def test_legal_merge_prefers_generated_over_empty_legacy():
    """When a legacy legal field is empty, the generated catalog value is shown."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dx_modelzoo'))
    from core.catalog import _enrich_model_entry

    base = {'id': 'fixture', 'legal': {'license': '', 'source_url': ''}}
    enriched = {'id': 'fixture', 'legal': {'license': 'Apache-2.0', 'source_url': 'https://example.com'}}
    _enrich_model_entry(base, enriched)
    assert base.get('legal', {}).get('license') == 'Apache-2.0'


def test_legal_merge_does_not_overwrite_real_legacy_values():
    """When a legacy legal field has a real value, it is kept."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dx_modelzoo'))
    from core.catalog import _enrich_model_entry

    base = {'id': 'fixture', 'legal': {'license': 'BSD-3-Clause'}}
    enriched = {'id': 'fixture', 'legal': {'license': 'Apache-2.0', 'source_url': 'https://example.com'}}
    _enrich_model_entry(base, enriched)
    assert base.get('legal', {}).get('license') == 'BSD-3-Clause'


@pytest.mark.requires_pillow
@_requires_pil
def test_optimizer_dry_run_does_not_write_outputs(tmp_path):
    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    thumb_dir = source_root / "thumbnails"
    thumb_dir.mkdir(parents=True)
    Image.new("RGB", (800, 600), "red").save(thumb_dir / "sample.jpg", quality=95)
    out_root = source_root / "optimized"

    report = optimizer.optimize_images(source_root, out_root, write=False)

    assert report["processed"] == 1
    assert not out_root.exists()


@pytest.mark.requires_pillow
@_requires_pil
def test_optimizer_writes_webp_jpg_and_manifest(tmp_path):
    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    thumb_dir = source_root / "thumbnails"
    thumb_dir.mkdir(parents=True)
    Image.new("RGB", (1200, 800), "blue").save(thumb_dir / "sample.jpg", quality=95)
    out_root = source_root / "optimized"

    report = optimizer.optimize_images(source_root, out_root, write=True)

    assert report["processed"] == 1
    # The original extension is part of the stem, to avoid collisions
    assert (out_root / "thumbnails" / "sample-jpg.webp").exists()
    assert (out_root / "thumbnails" / "sample-jpg.jpg").exists()
    manifest = json.loads((out_root / "manifest.json").read_text())
    assert manifest["images"]
    assert manifest["images"][0]["source"].endswith("thumbnails/sample.jpg")


@pytest.mark.requires_pillow
@_requires_pil
def test_dryrun_reports_skipped_when_outputs_exist(tmp_path):
    """Even in dry-run, an existing output file is reported as skipped."""
    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    thumb_dir = source_root / "thumbnails"
    thumb_dir.mkdir(parents=True)
    Image.new("RGB", (800, 600), "red").save(thumb_dir / "sample.jpg", quality=95)
    out_root = source_root / "optimized"

    # First create the output file in write mode
    optimizer.optimize_images(source_root, out_root, write=True)

    # dry-run (write=False) detects the existing output
    report = optimizer.optimize_images(source_root, out_root, write=False, force=False)
    assert report["skipped"] == 1
    assert report["processed"] == 0


@pytest.mark.requires_pillow
@_requires_pil
def test_stem_collision_produces_distinct_outputs(tmp_path):
    """Images with the same stem and different extensions do not overwrite each other."""
    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    thumb_dir = source_root / "thumbnails"
    thumb_dir.mkdir(parents=True)
    Image.new("RGB", (800, 600), "red").save(thumb_dir / "dup.jpg", quality=95)
    Image.new("RGB", (800, 600), "blue").save(thumb_dir / "dup.png")
    out_root = source_root / "optimized"

    report = optimizer.optimize_images(source_root, out_root, write=True)

    assert report["written"] == 2
    out_dir = out_root / "thumbnails"
    assert (out_dir / "dup-jpg.webp").exists()
    assert (out_dir / "dup-jpg.jpg").exists()
    assert (out_dir / "dup-png.webp").exists()
    assert (out_dir / "dup-png.jpg").exists()
    # There must be 4 distinct files in total
    output_files = sorted(f.name for f in out_dir.iterdir())
    assert len(output_files) == 4


@pytest.mark.requires_pillow
@_requires_pil
def test_cli_summary_zero_source_bytes(tmp_path, monkeypatch, capsys):
    """The percentage output must not raise ZeroDivisionError when source_bytes is 0.

    An empty source tree is a FileNotFoundError by contract — running without the original
    images must not silently succeed (tests/dx_modelzoo/test_optimize_images_needs_sources.py).
    So source_bytes = 0 is produced with a `--model` filter that matches nothing instead.
    """
    import sys

    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    (source_root / "thumbnails").mkdir(parents=True)
    (source_root / "examples").mkdir(parents=True)
    Image.new("RGB", (8, 8), (7, 7, 7)).save(source_root / "thumbnails" / "present.jpg")
    out_root = tmp_path / "output"

    monkeypatch.setattr(sys, "argv", [
        "optimize_images.py",
        "--source-root", str(source_root),
        "--output-root", str(out_root),
        "--model", "matches-nothing",
    ])

    optimizer.main()

    captured = capsys.readouterr().out
    assert "DRY-RUN" in captured
    assert "처리" in captured


@pytest.mark.requires_pillow
@_requires_pil
def test_rgba_composites_on_white_background(tmp_path):
    """An RGBA PNG is composited onto a white background (not black)."""
    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    thumb_dir = source_root / "thumbnails"
    thumb_dir.mkdir(parents=True)

    # Create a fully transparent (alpha=0) RGBA image
    rgba = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    rgba.save(thumb_dir / "transparent.png")
    out_root = source_root / "optimized"

    report = optimizer.optimize_images(source_root, out_root, write=True)
    assert report["written"] == 1

    # Open the resulting JPG and check the background is white
    result_jpg = out_root / "thumbnails" / "transparent-png.jpg"
    result_img = Image.open(result_jpg)
    pixels = list(result_img.getdata())
    # Every pixel must be close to white (255,255,255)
    avg_r = sum(p[0] for p in pixels) / len(pixels)
    avg_g = sum(p[1] for p in pixels) / len(pixels)
    avg_b = sum(p[2] for p in pixels) / len(pixels)
    assert avg_r > 250 and avg_g > 250 and avg_b > 250, (
        f"투명 이미지가 흰 배경이 아닌 검은 배경으로 합성됨: ({avg_r}, {avg_g}, {avg_b})"
    )



def read_text(path):
    """Read and return a UTF-8 text file."""
    return path.read_text(encoding="utf-8")


def modelzoo_i18n_sources():
    """Return the split ModelZoo i18n dictionary fragment together with the bootstrap source."""
    files = [MODELZOO_JS / "i18n.js", *sorted(MODELZOO_JS.glob("i18n-dict-*.js"))]
    return "\n".join(read_text(path) for path in files)


def test_modelzoo_layout_uses_full_width_workspace():
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert ".mz-explorer-shell" in css
    assert re.search(r"max-width\s*:\s*1480px", css) is None
    assert re.search(r"max-width\s*:\s*1400px", css) is None
    assert re.search(r"max-width\s*:\s*960px", css) is None
    assert re.search(r"\.mz-explorer-shell\s*\{[^}]*width:\s*100%", css, re.DOTALL)
    assert re.search(r"\.mz-main\s*\{[^}]*max-width:\s*none", css, re.DOTALL)
    assert re.search(r"\.mz-detail-view\s*\{[^}]*max-width:\s*none", css, re.DOTALL)
    assert re.search(
        r"\.mz-card-grid\s*\{[^}]*grid-template-columns:\s*repeat\(auto-fill,\s*minmax\(280px,\s*1fr\)\)",
        css,
        re.DOTALL,
    )


def test_catalog_uses_category_checkbox_list_contract():
    html = read_text(ROOT / "dx_modelzoo" / "templates" / "index.html")
    js = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert 'data-section="category"' in html
    assert "mz-category-list" in js
    assert 'type="checkbox"' in js
    assert ".mz-category-option" in css


def test_catalog_js_has_dynamic_heading_tokens():
    js = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "updateCatalogHeading" in js
    assert "catalogTitle" in js
    assert "model variants" in js
    assert "unique models" in js


def test_detail_js_renders_sticky_action_bar():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert "renderDetailActionBar" in detail
    assert "mz-detail-action-bar" in detail
    assert ".mz-detail-action-bar" in css
    assert "position:sticky" in css


def test_detail_layout_uses_top_block_with_two_by_two_panels():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert "mz-detail-two-by-two" in detail
    assert "mz-detail-panel-a" in detail
    assert "mz-detail-panel-b" in detail
    assert "mz-detail-panel-c" in detail
    assert "mz-detail-panel-d" in detail
    assert "mz-detail-side-sticky" in detail
    assert "sectionQuickFacts" in detail
    assert re.search(
        r"\.mz-detail-two-by-two\s*\{[^}]*grid-template-columns:[^;]*minmax\(0,\s*0\.9fr\)[^;]*minmax\(0,\s*1\.1fr\)",
        css,
        re.DOTALL,
    )
    assert 'class="mz-detail-header"' in detail


def test_detail_spec_layout_uses_horizontal_keyfacts_and_split_spec_blocks():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert "mz-spec-metrics-grid" in detail
    assert "mz-spec-columns" in detail
    assert "Model Inputs & Core Metrics" in detail
    assert "Runtime & Deployment Metadata" in detail
    assert re.search(r"\.mz-detail-side-section\s+\.mz-key-facts\s*\{[^}]*grid-template-columns:\s*repeat\(6", css, re.DOTALL)
    assert re.search(r"\.mz-spec-metrics-grid\s*\{[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)", css, re.DOTALL)
    assert re.search(r"\.mz-spec-columns\s*\{[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)", css, re.DOTALL)
    # Legal section should remain full-width below 2x2 panel region
    assert detail.index('class="mz-detail-two-by-two"') < detail.index('id="sectionLegal"')


def test_detail_two_by_two_uses_narrow_left_and_wide_right_and_lifts_spec_block():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert "mz-detail-col-left" in detail
    assert "mz-detail-col-right" in detail
    assert re.search(
        r"\.mz-detail-two-by-two\s*\{[^}]*grid-template-columns:\s*minmax\(0,\s*0\.9fr\)\s*minmax\(0,\s*1\.1fr\)",
        css,
        re.DOTALL,
    )
    assert re.search(r"\.mz-detail-col-left\s*\{[^}]*grid-row:\s*1", css, re.DOTALL)
    assert re.search(r"\.mz-detail-col-right\s*\{[^}]*grid-row:\s*1", css, re.DOTALL)
    assert detail.index('id="sectionSpec"') < detail.index('id="demoSection"')


def test_detail_legal_information_uses_horizontal_grid_layout():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    legal_body = js_function_body(detail, "renderLegal")
    assert "mz-legal-grid" in legal_body
    assert "mz-legal-item" in legal_body
    assert re.search(r"\.mz-legal-grid\s*\{[^}]*grid-template-columns:\s*repeat\(3,\s*minmax\(0,\s*1fr\)\)", css, re.DOTALL)


def test_detail_compile_section_moves_to_right_column():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert detail.index('id="sectionCompile"') < detail.index('mz-detail-col-left')
    assert detail.index('id="sectionCompile"') < detail.index('id="demoSection"')


def test_detail_compile_guide_has_expanded_right_panel_content():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(detail, "renderCompileGuide")
    for token in (
        "Compile Checklist",
        "Expected Outputs",
        "Quick Compile Steps",
        "mz-compile-checklist",
        "mz-compile-outputs",
        "mz-compile-steps",
    ):
        assert token in body


def test_modelzoo_state_labels_cover_stale_suspect_legal():
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    catalog = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    i18n = modelzoo_i18n_sources()
    combined = detail + "\n" + catalog + "\n" + i18n
    for key in (
        "Using cached data after refresh failed",
        "Suspect value: source verification required",
        "License text not provided by source",
    ):
        assert key in i18n
        assert key in combined


def js_function_body(src, name):
    """Extract a JS function body with simple brace matching."""
    pattern = rf"function\s+{name}\s*\([^)]*\)\s*\{{"
    match = re.search(pattern, src)
    if not match:
        pattern = rf"\b{name}\s*\([^)]*\)\s*\{{"
        match = re.search(pattern, src)
    assert match, f"{name} 함수를 찾을 수 없습니다"
    start = match.end()
    depth = 1
    i = start
    while i < len(src) and depth > 0:
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
        i += 1
    assert depth == 0, f"{name} 함수 본문을 끝까지 파싱하지 못했습니다"
    return src[start:i - 1]


def test_catalog_js_defines_virtualized_catalog_contract():
    """catalog.js defines ModelZooVirtualCatalog and its core API.

    **This test is no evidence that virtualization works.** It only checks that names exist;
    virtualization can be dead (e.g. a scroll listener attached to nothing) with every token
    in place.

    tests/test_catalog_virtual_scroll_browser.py guards the behavior. This one only catches
    names disappearing.
    """
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    for token in (
        "ModelZooVirtualCatalog",
        "renderViewport",
        "loadPage",
        "getVisibleRange",
        "renderCardItem",
        "renderListRow",
        "MAX_CACHED_PAGES",
        # Finds the scroll root. Without it, a layout where an ancestor scrolls stalls
        # on the first screen.
        "_scrollRoot",
    ):
        assert token in src, f"catalog.js에 '{token}'이 없습니다"


def test_catalog_js_no_longer_full_maps_models_for_card_or_list():
    """renderCardView/renderListView do not render every model at once."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")

    def function_body(name):
        # Find the function start and extract the body by brace matching
        pattern = rf"function\s+{name}\s*\([^)]*\)\s*\{{"
        match = re.search(pattern, src)
        assert match, f"{name} 함수를 찾을 수 없습니다"
        start = match.end()
        depth = 1
        i = start
        while i < len(src) and depth > 0:
            if src[i] == "{":
                depth += 1
            elif src[i] == "}":
                depth -= 1
            i += 1
        return src[start:i - 1]

    card_body = function_body("renderCardView")
    assert "models.map" not in card_body, (
        "renderCardView에서 models.map 사용이 발견됨 — 가상화 위반"
    )

    list_body = function_body("renderListView")
    assert "models.forEach" not in list_body, (
        "renderListView에서 models.forEach 사용이 발견됨 — 가상화 위반"
    )


def test_catalog_and_detail_images_use_lazy_async_and_optimized_fallbacks():
    """catalog.js and detail.js follow the optimized image fallback policy."""
    catalog = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    combined = catalog + "\n" + detail
    assert 'loading="lazy"' in combined, "lazy loading 미적용"
    assert 'decoding="async"' in combined, "async decoding 미적용"
    assert "/data/optimized/" in combined, "optimized 경로 미사용"
    assert (
        "onerror = null" in combined or "onerror=null" in combined
        or ".onerror = null" in combined
    ), "onerror 종료 처리 누락"
    # Collision-safe naming policy: the safeStem pattern must exist in JS
    assert "safeStem" in combined, "collision-safe safeStem 헬퍼 누락"


def test_catalog_js_has_loading_error_and_scroll_restore_contracts():
    """catalog.js has the loading placeholder, error and scroll restore contracts."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "mz-placeholder" in src, "로딩 placeholder 클래스 누락"
    assert "mz-catalog-error" in src, "에러 placeholder 클래스 누락"
    assert "sessionStorage" in src, "sessionStorage 사용 누락"
    assert "modelzooCatalogState" in src, "상태 키 modelzooCatalogState 누락"


def test_catalog_js_scroll_listener_with_raf_throttle():
    """The scroll listener calls renderViewport with rAF throttling."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "addEventListener" in src and "'scroll'" in src, (
        "scroll 이벤트 리스너가 없습니다 — 가상화가 스크롤 시 업데이트되지 않음"
    )
    assert "requestAnimationFrame" in src, (
        "requestAnimationFrame 스로틀링이 없습니다 — 스크롤 리렌더 폭풍 위험"
    )
    assert "renderViewport" in src, "renderViewport 호출이 필요합니다"


def test_catalog_js_preserves_scroll_position_on_rerender():
    """Replacing innerHTML preserves scrollTop."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    # Both _renderCardViewport and _renderListViewport preserve scrollTop
    assert "savedScrollTop" in src or "saved_scroll" in src, (
        "scrollTop 보존 변수가 없습니다 — innerHTML이 스크롤 위치를 초기화할 수 있음"
    )
    assert re.search(r"container\.scrollTop\s*=\s*savedScrollTop", src), (
        "container.scrollTop = savedScrollTop 복원이 없습니다"
    )


def test_catalog_js_list_header_click_resets_viewport():
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    body = js_function_body(src, "onListHeaderClick")
    assert "resetCatalogViewport()" in body


def test_catalog_js_filter_change_invalidates_measured_card_height():
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    reset_body = js_function_body(src, "resetAndRender")
    assert "_measuredCardHeight = null" in reset_body


def test_catalog_js_measurement_triggers_rerender():
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    measure_body = js_function_body(src, "_measureCardHeight")
    assert "renderViewport()" in measure_body


def test_catalog_js_measurement_ignores_detached_containers():
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    measure_body = js_function_body(src, "_measureCardHeight")
    assert "container.isConnected" in measure_body


def test_catalog_js_measurement_is_idempotent_after_height_is_known():
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    measure_body = js_function_body(src, "_measureCardHeight")
    assert "this._measuredCardHeight" in measure_body
    assert re.search(r"if\s*\(\s*this\._measuredCardHeight\s*\)\s*return", measure_body)


def test_catalog_js_view_mode_change_invalidates_measured_card_height():
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert re.search(
        r"setViewMode\s*\(\s*mode\s*\)\s*\{[^}]*this\._measuredCardHeight\s*=\s*null",
        src,
        re.DOTALL,
    )


def test_catalog_js_view_mode_change_resets_viewport():
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    body = js_function_body(src, "setViewMode")
    assert "resetCatalogViewport()" in body


def test_catalog_js_conditional_scrolltop_restore():
    """scrollTop restore is conditional — avoids needless scroll events."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    # Both viewport renderers must have the conditional restore pattern
    # A conditional restore that includes _isContainerScrollable() is also allowed
    conditional_pattern = re.compile(
        r"if\s*\(.*container\.scrollTop\s*!==\s*savedScrollTop"
    )
    matches = conditional_pattern.findall(src)
    assert len(matches) >= 2, (
        f"조건부 scrollTop 복원(if ... container.scrollTop !== savedScrollTop)이 "
        f"card/list 두 렌더러 모두에 있어야 합니다 (발견: {len(matches)}개)"
    )


def test_detail_js_escape_html_handles_quotes():
    """detail.js escapeHtml also escapes quotes."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "&quot;" in src, (
        "detail.js escapeHtml에 큰따옴표 이스케이프(&quot;)가 없습니다"
    )
    assert "&#39;" in src, (
        "detail.js escapeHtml에 작은따옴표 이스케이프(&#39;)가 없습니다"
    )



def test_detail_js_error_path_escapes_model_id():
    """The renderDetailPage error path escapes modelId with escapeHtml."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    # The catch block must not insert modelId raw
    assert "escapeHtml(modelId)" in src, (
        "detail.js 에러 경로에서 escapeHtml(modelId)를 사용해야 합니다 — XSS 위험"
    )
    # A raw ${modelId} must not go into innerHTML directly
    # Fails if innerHTML in the catch block has a raw modelId
    catch_match = re.search(r"catch\s*\([^)]*\)\s*\{(.*?)\}", src, re.DOTALL)
    if catch_match:
        catch_body = catch_match.group(1)
        assert "${modelId}" not in catch_body or "escapeHtml(modelId)" in catch_body, (
            "catch 블록에서 raw ${modelId}가 innerHTML에 사용됨 — Reflected XSS"
        )



def test_detail_js_escapes_model_name_in_title():
    """renderDetail escapes model.name with escapeHtml."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "escapeHtml(model.name)" in src, (
        "detail.js에서 model.name이 escapeHtml 없이 렌더링됨"
    )


def test_detail_js_escapes_category_label():
    """renderDetail escapes catLabel with escapeHtml."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "escapeHtml(catLabel)" in src, (
        "detail.js에서 catLabel이 escapeHtml 없이 렌더링됨"
    )


def test_detail_js_escapes_legal_fields():
    """renderLegal escapes license/copyright with escapeHtml."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "escapeHtml(legal.license)" in src, (
        "detail.js에서 legal.license가 escapeHtml 없이 렌더링됨"
    )
    assert "escapeHtml(legal.copyright)" in src, (
        "detail.js에서 legal.copyright가 escapeHtml 없이 렌더링됨"
    )


def test_detail_js_escapes_error_messages():
    """detail.js escapes e.message when inserting it into innerHTML."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    # loadDemoCode's catch block must not use e.message raw
    assert "escapeHtml(e.message)" in src, (
        "detail.js에서 e.message가 escapeHtml 없이 innerHTML에 삽입됨"
    )


def test_detail_js_escapes_remaining_detail_content_fields():
    """Security: description/spec/compile/legal URLs are escaped in HTML/attribute context too."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "<p>${escapeHtml(text)}</p>" in src, (
        "description/compile guide text가 escapeHtml 없이 <p>에 삽입됨"
    )
    assert "escapeHtml(String(v))" in src, (
        "specification 값이 escapeHtml 없이 <td>에 삽입됨"
    )
    assert 'href="${escapeHtml(legal.source_url)}"' in src, (
        "legal.source_url이 href 속성에서 escapeHtml 없이 사용됨"
    )
    assert "isValidOnnxUrl" in src and "_artifactEndpoint(model.id, 'onnx')" in src, (
        "compile guide ONNX 링크는 raw URL 대신 backend artifact endpoint를 사용해야 함"
    )


def test_detail_js_escapes_download_error_messages():
    """Security: API error strings are escaped before going into status HTML."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "escapeHtml(data.error || '')" in src, (
        "downloadModel data.error가 escapeHtml 없이 innerHTML에 삽입됨"
    )
    assert "escapeHtml(sd.error || '')" in src, (
        "download status sd.error가 escapeHtml 없이 innerHTML에 삽입됨"
    )
    assert src.count("escapeHtml(e.message)") >= 2, (
        "detail.js catch error message들이 모두 escapeHtml 처리되어야 함"
    )


def test_detail_js_download_buttons_avoid_inline_model_id_handlers():
    """Security: model.id is never inserted directly into an inline onclick JS string."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "onclick=\"downloadModel(event, '${model.id}'" not in src
    assert "data-model-id=\"${escapeHtml(model.id)}\"" in src
    assert "initDownloadButtons(container)" in src
    assert "downloadModel(event, btn.dataset.modelId || '', btn.dataset.quant || '')" in src


def test_detail_js_cancel_download_avoids_inline_model_id_handler():
    """Security: the cancel button does not insert modelId/quantType into an inline onclick either."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "onclick=\"cancelDownload('${modelId}','${quantType}')\"" not in src
    assert "data-cancel-download" in src
    assert "cancelDownload(modelId, quantType)" in src


def test_catalog_and_detail_image_src_attributes_are_escaped():
    """Security: optimized image src candidates are escaped in attribute context too."""
    catalog = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert 'src="${_escapeAttr(first)}"' in catalog, (
        "catalog.js imageTagWithFallback의 src가 _escapeAttr 없이 삽입됨"
    )
    assert 'src="${escapeHtml(first)}"' in detail, (
        "detail.js _detailImageTag의 src가 escapeHtml 없이 삽입됨"
    )


def test_catalog_js_avoids_inline_model_id_navigation_handlers():
    """Security: catalog cards/list never put the model id into an inline onclick JS string."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "onclick=\"location.hash='model=${m.id}'\"" not in src
    assert "data-model-id=\"${_escapeAttr(m.id)}\"" in src
    assert "_bindModelNavigation" in src
    assert "location.hash = 'model=' + encodeURIComponent(modelId)" in src


def test_modelzoo_encoded_hashes_decode_before_detail_render():
    """Correctness: the encoded model hash is decoded to the original model id before API calls."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    i18n = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "i18n.js")
    assert "function getModelIdFromHash" in app
    assert "decodeURIComponent(raw)" in app
    assert "getModelIdFromHash(location.hash)" in app
    assert "getModelIdFromHash(location.hash)" in i18n
    assert "location.hash.replace('#model=', '')" not in app
    assert "location.hash.replace('#model=', '')" not in i18n


def test_modelzoo_waits_for_health_check_before_initial_route_render():
    """The detail view renders after the DX App status check, to avoid false "inactive" states."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    assert "await checkDxAppHealth();" in app
    assert app.index("await checkDxAppHealth();") < app.index("route();")


def test_modelzoo_rerenders_detail_when_dx_app_health_changes():
    """When health changes on the detail view, the Run Demo/download controls follow."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    assert "const changed = previousAlive !== _dxAppAlive;" in app
    assert "if (changed && location.hash.startsWith('#model='))" in app
    assert "renderDetailPage(getModelIdFromHash(location.hash));" in app


def test_modelzoo_api_urls_are_proxy_prefix_aware():
    """Through the launcher's /zoo, the ModelZoo API does not collide with the launcher's /api/health."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    assert "function modelzooApiUrl(path)" in app
    assert "fetch(modelzooApiUrl('/api/health'))" in app
    assert "fetch(modelzooApiUrl('/api/catalog'))" in app


def test_modelzoo_client_api_calls_use_proxy_prefix_helper():
    """ModelZoo client API calls keep the launcher's /zoo prefix."""
    for rel_path in (
        "dx_modelzoo/static/js/catalog.js",
        "dx_modelzoo/static/js/detail.js",
        "dx_modelzoo/static/js/inference.js",
    ):
        src = read_text(ROOT / rel_path)
        assert "fetch('/api" not in src
        assert 'fetch("/api' not in src
        assert "fetch(`/api" not in src
        assert 'src="/api/sample-image' not in src
        assert "preview.src = `/api/sample-image/" not in src


def test_inference_handles_dx_app_unavailable_error_payload_shape():
    """The DX-App-not-running state shows correctly even when the proxy returns an error field instead of code."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "inference.js")
    assert "data.error === 'DX_APP_UNAVAILABLE'" in src


def test_detail_run_demo_button_opens_inference_panel_explicitly():
    """The Run Demo button opens and scrolls to the inference panel, so the user sees where it runs."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "openInferencePanelFromDemo" in src
    assert "onclick=\"openInferencePanelFromDemo()\"" in src


def test_detail_example_images_have_no_inline_width_caps():
    """Every Example type uses the detail box width and is not capped by an inline max-width."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    assert "max-width:640px" not in src
    assert "max-width:320px" not in src
    assert "max-width:200px" not in src
    assert "mz-example-image" in src
    assert "mz-example-overlay" in src
    assert "mz-classified-example" in src
    assert "mz-example-gallery" in src
    assert ".mz-example-image{display:block;width:100%" in css
    assert ".mz-example-overlay{position:relative;width:100%" in css
    assert ".mz-classified-example{display:flex;flex-direction:column" in css
    assert ".mz-example-gallery{display:grid" in css
    assert ".mz-ba-container{position:relative;overflow:hidden;border-radius:var(--radius);width:100%}" in css


def test_catalog_js_avoids_inline_category_handlers():
    """Security: the category id is not put into an inline onclick JS string either."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "onclick=\"toggleCategory('${id}')\"" not in src
    assert "onclick=\"toggleCategory('__unknown__')\"" not in src
    assert "data-cat=\"${_escapeAttr(id)}\"" in src
    assert "_bindCategoryChipEvents(container)" in src


def test_catalog_js_escapes_spec_fields_in_card_and_list():
    """Security: catalog card/list specification fields are escaped before HTML insertion."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "_escapeAttr(m.specification.fps)" in src, (
        "card fps가 _escapeAttr 없이 렌더링됨"
    )
    assert "_escapeAttr(m.specification?.fps || '-')" in src, (
        "list fps가 _escapeAttr 없이 렌더링됨"
    )
    assert "resolution ? _escapeAttr(resolution) : _missingLabel('Not provided by source')" in src, (
        "list input_resolution이 escape/missing-label 처리 없이 렌더링됨"
    )
    assert "accuracyText ? _escapeAttr(String(accuracyText)) : _missingLabel('Not provided by source')" in src, (
        "list accuracy가 escape/missing-label 처리 없이 렌더링됨"
    )


def test_catalog_js_avoids_inline_sort_header_handlers():
    """Security: list sort headers delegate via data attributes, without inline onclick."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "onclick=\"onListHeaderClick('${h.key}')\"" not in src
    assert "data-sort-key=\"${_escapeAttr(h.key)}\"" in src
    assert "${_escapeAttr(h.label)}${arrow}" in src
    assert "_bindListSortEvents" in src
    assert "onListHeaderClick(target.dataset.sortKey || '')" in src



def test_catalog_js_window_scroll_listener():
    """catalog.js also binds the window scroll event."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "window.addEventListener" in src and "'scroll'" in src, (
        "window scroll 리스너가 없습니다 — container가 스크롤 컨테이너가 아닐 때 가상화 미동작"
    )


def test_catalog_js_effective_scroll_uses_window():
    """catalog.js computes the effective scroll with window.scrollY/getBoundingClientRect."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    has_window_scroll = "window.scrollY" in src or "window.pageYOffset" in src
    has_bounding_rect = "getBoundingClientRect" in src
    assert has_window_scroll and has_bounding_rect, (
        "window.scrollY와 getBoundingClientRect를 사용한 effective scroll 계산이 필요합니다"
    )



def test_catalog_js_processor_placeholder_removed_from_release():
    """catalog.js and style.css carry no processor placeholder (release contract)."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    css = read_text(ROOT / "dx_modelzoo" / "static" / "css" / "style.css")
    i18n = modelzoo_i18n_sources()
    for token in (
        "AI Processor",
        "DX-M1",
        "DX-M2",
        "mz-processor-notice",
        "Processor compatibility metadata is being prepared",
        "PROCESSOR_OPTIONS",
    ):
        assert token not in src, f"processor token '{token}' should be removed from catalog.js"
        assert token not in css, f"processor token '{token}' should be removed from style.css"
    for token in (
        "AI Processor",
        "Processor compatibility metadata is being prepared",
    ):
        assert token not in i18n, f"processor token '{token}' should be removed from i18n dictionaries"


def test_modelzoo_i18n_defines_explorer_redesign_keys():
    """i18n.js defines the keys the Explorer layout needs."""
    src = modelzoo_i18n_sources()
    for key in (
        "DX Model Zoo Explorer",
        "Reset filters",
        "Active filters",
        "View as cards",
        "View as list",
        "Categories",
        "Sort by",
        "models found",
    ):
        assert f"'{key}'" in src or f'"{key}"' in src, key


def test_modelzoo_i18n_new_keys_have_five_language_coverage():
    src = modelzoo_i18n_sources()
    required_locales = ("ko", "ja", "zh-CN", "zh-TW")
    for key in (
        "model variants",
        "unique models",
        "All Models",
        "Selected categories",
        "Using cached data after refresh failed",
        "Suspect value: source verification required",
        "License text",
        "License text not provided by source",
        "Sample not available for this model",
    ):
        block_match = re.search(rf"['\"]{re.escape(key)}['\"]\s*:\s*\{{(.*?)\n\s*\}}", src, re.DOTALL)
        assert block_match, key
        block = block_match.group(1)
        for locale in required_locales:
            has_quoted = f"'{locale}'" in block or f'"{locale}"' in block
            has_unquoted = "-" not in locale and re.search(rf"\b{re.escape(locale)}\s*:", block)
            assert has_quoted or has_unquoted, f"{key}: {locale}"


def test_modelzoo_processor_filter_not_exposed_in_release_ui():
    """The release UI does not show the AI Processor filter (M2 is not released)."""
    html = read_text(ROOT / 'dx_modelzoo/templates/index.html')
    js = read_text(ROOT / 'dx_modelzoo/static/js/catalog.js')
    css = read_text(ROOT / 'dx_modelzoo/static/css/style.css')
    assert 'data-section="processor"' not in html
    assert 'processorFilters' not in html
    assert 'DX-M2' not in html
    assert 'renderProcessorFilters' not in js
    assert 'setProcessorFilter' not in js
    assert '.mz-processor-notice' not in css


def test_detail_js_preserves_reference_section_ids():
    """detail.js keeps the existing section IDs."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    for section_id in (
        "sectionUseCase",
        "sectionExample",
        "sectionSpec",
        "sectionCompile",
        "demoSection",
        "sectionLegal",
    ):
        assert section_id in src, section_id


def test_catalog_js_declares_bounded_card_and_list_targets():
    """catalog.js has the bounded DOM rendering constants and the list row class."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert re.search(r"CARD_DOM_LIMIT\s*=\s*50\b", src), \
        "CARD_DOM_LIMIT must be assigned the value 50"
    assert re.search(r"LIST_ROW_DOM_LIMIT\s*=\s*100\b", src), \
        "LIST_ROW_DOM_LIMIT must be assigned the value 100"
    assert "mz-list-row" in src
    assert "getVisibleRange" in src
    assert "renderViewport" in src


def test_catalog_js_resets_viewport_when_filters_change():
    """Changing filter/search/sort while scrolled deep never leaves an empty viewport."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "function resetCatalogViewport" in src
    for handler in ("toggleCategory", "onSearchInput", "onSortChange", "resetFilters"):
        match = re.search(rf"function\s+{handler}\s*\([^)]*\)\s*\{{(.*?)\n\}}", src, re.DOTALL)
        assert match, f"{handler} 함수를 찾을 수 없습니다"
        assert "resetCatalogViewport()" in match.group(1), (
            f"{handler}에서 필터 변경 전 viewport scroll을 초기화해야 합니다"
        )


def test_catalog_js_clamps_visible_range_after_result_shrink():
    """The visible range stays valid even when the saved/current scrollTop exceeds the result count."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "totalRows" in src, "카드 visible range는 전체 row 수 기준으로 clamp해야 합니다"
    assert "maxStartRow" in src, "visible range 시작 row를 최대 유효 row로 clamp해야 합니다"
    assert re.search(r"Math\.min\(\s*rawStartRow\s*,\s*maxStartRow\s*\)", src)


def test_catalog_js_card_visible_range_clamps_in_row_space():
    """Card virtualization clamps the tail in row space, so the last models are not dropped."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "const totalRows = Math.ceil(models.length / cols);" in src
    assert "const rowsByLimit = Math.max(1, Math.floor(CARD_DOM_LIMIT / cols));" in src
    assert "const windowRows = Math.min(visibleRows, rowsByLimit);" in src
    assert "const maxStartRow = Math.max(0, totalRows - windowRows);" in src
    assert re.search(r"const\s+startRow\s*=\s*Math\.min\(\s*rawStartRow\s*,\s*maxStartRow\s*\)", src)
    assert "const endIdx = Math.min(models.length, startIdx + windowRows * cols, startIdx + CARD_DOM_LIMIT);" in src


def test_catalog_js_restored_unknown_filter_requires_unknown_models():
    """A restored __unknown__ filter is kept only when unknown models actually exist."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "function hasUnknownCategoryModels" in src
    restore_match = re.search(r"_restoreState\(\)\s*\{(.*?)\n  \},", src, re.DOTALL)
    assert restore_match, "_restoreState body를 찾을 수 없습니다"
    restore_body = restore_match.group(1)
    assert "isValidCategoryFilter(c, { requireUnknownModels: true })" in restore_body


def test_catalog_js_populates_active_summary_on_initial_render():
    """Right after the first render, the subtitle/active summary is not empty."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    init_match = re.search(r"init\(dataOrMeta\)\s*\{(.*?)\n  \},", src, re.DOTALL)
    assert init_match, "ModelZooVirtualCatalog.init body를 찾을 수 없습니다"
    init_body = init_match.group(1)
    assert "this.resetAndRender();" in init_body
    assert "updateActiveFilterSummary();" in init_body


def test_catalog_js_syncs_restored_sort_and_view_controls():
    """Restored sort/view state shows in the visible controls, not only in internal state."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "function syncCatalogControls" in src
    assert "sortSelect.value = _sortField" in src
    assert "btnCardView" in src and "btnListView" in src
    init_match = re.search(r"init\(dataOrMeta\)\s*\{(.*?)\n  \},", src, re.DOTALL)
    assert init_match, "ModelZooVirtualCatalog.init body를 찾을 수 없습니다"
    assert "syncCatalogControls();" in init_match.group(1)


def test_catalog_js_renders_enriched_card_and_missing_states():
    """Catalog cards/list show generated metadata and empty-value states."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    for token in ("performance", "Benchmark required", "input_resolution", "artifacts", "missing"):
        assert token in src


def test_detail_js_renders_hybrid_datasheet_sections():
    """The detail view keeps both the Hybrid Datasheet sections and the existing anchor IDs."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    for token in (
        "mz-key-facts",
        "mz-artifact-table",
        "mz-accuracy-matrix",
        "mz-runtime-performance",
        "Not provided by source",
        "Metadata pending",
    ):
        assert token in src
    for section_id in (
        "sectionUseCase",
        "sectionExample",
        "sectionSpec",
        "sectionCompile",
        "demoSection",
        "sectionLegal",
    ):
        assert section_id in src


def test_frontend_does_not_directly_link_internal_artifact_urls():
    """The frontend links only to the backend artifact endpoint, never to raw artifact URLs."""
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    catalog = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    combined = detail + catalog
    assert "modelzoo-api.devops.dpx.ai" not in combined
    assert "/api/catalog/${" in combined or "/artifacts/" in combined


def test_catalog_list_uses_explicit_missing_accuracy_label():
    """Missing list accuracy/resolution values show an explicit source-missing label, not '-'."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    body = js_function_body(src, "renderListRow")
    assert "let accuracy = '';" in body
    assert "let accuracy = '-'" not in body
    assert "legacyAccuracy" not in body
    assert "legacyResolution" not in body
    assert "const resolution = _modelInputResolution(m);" in body
    assert "_missingLabel('Not provided by source')" in body


def test_detail_legal_source_rows_render_explicit_missing_metadata():
    """The legal/source area always renders the provenance row and an explicit missing state."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderLegal")
    for token in (
        "T('Source profile')",
        "T('Last metadata sync')",
        "_detailStatus('Not provided by source')",
        "_detailStatus('Metadata pending')",
        'rel="noopener"',
    ):
        assert token in body
    assert "Legal information coming soon." not in body


def test_detail_specification_uses_enriched_resolution_and_explicit_missing_rows():
    """The specification table uses the enriched resolution fallback and explicit missing states."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderSpecification")
    assert "['Input Resolution', _inputResolution(model)" in body
    assert "performance.fps ?? spec.fps" in body
    assert "performance.fps_per_watt ?? spec.fps_per_watt" in body
    assert "Specification data coming soon." not in body
    assert "Not provided by source" in body


def test_detail_artifact_table_renders_last_checked_status():
    """The artifact table shows the last checked/sync state."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderArtifactTable")
    assert "T('Last metadata sync')" in body
    assert "Metadata pending" in body


def test_detail_artifact_table_uses_remote_url_as_source_when_present():
    """With an artifact remote_url, the Source cell must not fall back to Not provided."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    helper = js_function_body(src, "_artifactSourceCell")
    body = js_function_body(src, "renderArtifactTable")
    assert "data.remote_url" in helper
    assert "target=\"_blank\"" in helper
    assert "rel=\"noopener noreferrer\"" in helper
    assert "https?:\\\\/\\\\/" not in helper
    assert "^https:" in helper
    assert "_artifactSourceCell(data)" in body
    assert "data.source || ''" not in body




def test_detail_accuracy_matrix_shows_suspect_label():
    """detail.js renderAccuracyMatrix shows a warning when source_status is suspect."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderAccuracyMatrix")
    assert "source_status" in body
    assert "Suspect value: source verification required" in body


def test_detail_accuracy_matrix_does_not_render_absent_onnx_accuracy_row():
    """Raw ONNX on the homepage is an artifact link, so it is not a fixed ONNX row in the accuracy matrix."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderAccuracyMatrix")
    assert "['ONNX', evaluation.onnx]" not in body
    assert ".filter" in body
    assert "evaluation.onnx" not in body


def test_catalog_best_accuracy_skips_suspect():
    """catalog.js _bestAccuracyValue skips entries whose source_status is suspect."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    body = js_function_body(src, "_bestAccuracyValue")
    assert "source_status" in body
    assert "suspect" in body




def test_modelzoo_inference_sends_no_save_output_flag():
    js = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "inference.js")
    assert "save_output: false" in js


def test_modelzoo_inference_clears_all_result_containers_before_run():
    js = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "inference.js")
    assert "clearInferenceResults" in js
    assert "getElementById('inferenceResult')" in js
    assert "getElementById('inferenceResultUpload')" in js
    assert "clearInferenceResults();" in js
    assert js.index("clearInferenceResults();") < js.index("resultDiv.innerHTML = `<div")


def test_modelzoo_inference_escapes_server_rendered_text():
    js = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "inference.js")
    body = js_function_body(js, "runInference")
    assert "escapeHtml(String(data.error" in body
    assert "escapeHtml(String(data.fps" in body
    assert "escapeHtml(String(data.latency" in body
    assert "escapeHtml(String(data.task_tags" in body
    assert "escapeHtml(String(e.message" in body


def test_modelzoo_sample_image_loader_escapes_error_message():
    js = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "inference.js")
    body = js_function_body(js, "loadSampleImages")
    assert "escapeHtml(String(e.message" in body


def test_modelzoo_sample_selection_clears_upload_result_container():
    js = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "inference.js")
    body = js_function_body(js, "_selectSampleThumb")
    assert "clearInferenceResults();" in body
    assert "inferenceResultUpload" not in body


def test_catalog_js_card_height_uses_measurement_not_only_fixed_constant():
    """Card height estimation measures, rather than relying on a fixed 300px.

    A fixed CARD_ESTIMATED_HEIGHT=300 causes scroll jumps when card heights differ.
    catalog.js must have _measuredCardHeight or a dynamic measuring helper.
    """
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert '_measuredCardHeight' in src, (
        "catalog.js must define _measuredCardHeight for dynamic card height measurement "
        "instead of relying solely on fixed CARD_ESTIMATED_HEIGHT=300"
    )


def test_js_class_name_reads_display_class_name():
    """detail.js reads model.display?.class_name first."""
    import os
    detail_js = open(os.path.join(
        os.path.dirname(__file__), '..', 'dx_modelzoo', 'static', 'js', 'detail.js'
    )).read()
    assert 'display?.class_name' in detail_js, (
        "detail.js should read model.display?.class_name before model.class_name"
    )


def test_catalog_js_resize_invalidates_measured_card_height():
    """A window resize invalidates _measuredCardHeight, so scrolling does not jump.

    Card height changes with the window size, so on resize the measurement is reset
    to null and taken again.
    """
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    # The resize handler must reset _measuredCardHeight to null
    assert re.search(
        r'resize.*_measuredCardHeight\s*=\s*null|_measuredCardHeight\s*=\s*null.*resize',
        src, re.DOTALL
    ), (
        "catalog.js must invalidate _measuredCardHeight on window resize "
        "so card heights are remeasured after viewport changes"
    )
