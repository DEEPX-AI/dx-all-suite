"""ModelZoo 이미지 옵티마이저 및 프론트엔드 가상화 계약 테스트."""

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
    """legacy legal 필드가 비어 있으면 generated catalog 값이 표시되어야 한다."""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dx_modelzoo'))
    from core.catalog import _enrich_model_entry

    base = {'id': 'fixture', 'legal': {'license': '', 'source_url': ''}}
    enriched = {'id': 'fixture', 'legal': {'license': 'Apache-2.0', 'source_url': 'https://example.com'}}
    _enrich_model_entry(base, enriched)
    assert base.get('legal', {}).get('license') == 'Apache-2.0'


def test_legal_merge_does_not_overwrite_real_legacy_values():
    """legacy legal 필드에 실제 값이 있으면 유지되어야 한다."""
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
    # I-4: 충돌 방지를 위해 원본 확장자를 stem에 포함
    assert (out_root / "thumbnails" / "sample-jpg.webp").exists()
    assert (out_root / "thumbnails" / "sample-jpg.jpg").exists()
    manifest = json.loads((out_root / "manifest.json").read_text())
    assert manifest["images"]
    assert manifest["images"][0]["source"].endswith("thumbnails/sample.jpg")


@pytest.mark.requires_pillow
@_requires_pil
def test_dryrun_reports_skipped_when_outputs_exist(tmp_path):
    """I-2: dry-run에서도 기존 출력 파일이 있으면 skipped로 보고해야 합니다."""
    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    thumb_dir = source_root / "thumbnails"
    thumb_dir.mkdir(parents=True)
    Image.new("RGB", (800, 600), "red").save(thumb_dir / "sample.jpg", quality=95)
    out_root = source_root / "optimized"

    # 먼저 write 모드로 출력 파일 생성
    optimizer.optimize_images(source_root, out_root, write=True)

    # dry-run(write=False)에서 기존 출력 감지
    report = optimizer.optimize_images(source_root, out_root, write=False, force=False)
    assert report["skipped"] == 1
    assert report["processed"] == 0


@pytest.mark.requires_pillow
@_requires_pil
def test_stem_collision_produces_distinct_outputs(tmp_path):
    """I-4: 동일 stem, 다른 확장자 이미지가 서로 덮어쓰지 않아야 합니다."""
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
    # 총 4개의 고유 파일이 존재해야 함
    output_files = sorted(f.name for f in out_dir.iterdir())
    assert len(output_files) == 4


@pytest.mark.requires_pillow
@_requires_pil
def test_cli_summary_zero_source_bytes(tmp_path, monkeypatch, capsys):
    """I-1: source_bytes가 0일 때 퍼센트 출력에서 ZeroDivisionError가 발생하지 않아야 합니다."""
    import sys

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    (source_root / "thumbnails").mkdir(parents=True)
    (source_root / "examples").mkdir(parents=True)
    out_root = tmp_path / "output"

    monkeypatch.setattr(sys, "argv", [
        "optimize_images.py",
        "--source-root", str(source_root),
        "--output-root", str(out_root),
    ])

    optimizer.main()

    captured = capsys.readouterr().out
    assert "DRY-RUN" in captured
    assert "처리" in captured


@pytest.mark.requires_pillow
@_requires_pil
def test_rgba_composites_on_white_background(tmp_path):
    """M-1: RGBA PNG가 흰 배경 위에 합성되어야 합니다 (검은 배경 아님)."""
    from PIL import Image

    optimizer = load_optimizer()
    source_root = tmp_path / "data"
    thumb_dir = source_root / "thumbnails"
    thumb_dir.mkdir(parents=True)

    # 완전 투명(alpha=0) RGBA 이미지 생성
    rgba = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    rgba.save(thumb_dir / "transparent.png")
    out_root = source_root / "optimized"

    report = optimizer.optimize_images(source_root, out_root, write=True)
    assert report["written"] == 1

    # 결과 JPG를 열어서 흰 배경인지 확인
    result_jpg = out_root / "thumbnails" / "transparent-png.jpg"
    result_img = Image.open(result_jpg)
    pixels = list(result_img.getdata())
    # 모든 픽셀이 흰색(255,255,255)에 가까워야 함
    avg_r = sum(p[0] for p in pixels) / len(pixels)
    avg_g = sum(p[1] for p in pixels) / len(pixels)
    avg_b = sum(p[2] for p in pixels) / len(pixels)
    assert avg_r > 250 and avg_g > 250 and avg_b > 250, (
        f"투명 이미지가 흰 배경이 아닌 검은 배경으로 합성됨: ({avg_r}, {avg_g}, {avg_b})"
    )



def read_text(path):
    """UTF-8 텍스트 파일을 읽어 반환합니다."""
    return path.read_text(encoding="utf-8")


def modelzoo_i18n_sources():
    """분리된 ModelZoo i18n dictionary fragment와 bootstrap source를 함께 반환합니다."""
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
    """간단한 brace matching으로 JS 함수 본문을 추출합니다."""
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
    """catalog.js에 ModelZooVirtualCatalog와 핵심 API가 존재해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    for token in (
        "ModelZooVirtualCatalog",
        "renderViewport",
        "loadPage",
        "getVisibleRange",
        "renderCardItem",
        "renderListRow",
        "MAX_CACHED_PAGES",
    ):
        assert token in src, f"catalog.js에 '{token}'이 없습니다"


def test_catalog_js_no_longer_full_maps_models_for_card_or_list():
    """renderCardView/renderListView가 더 이상 전체 모델을 한번에 렌더링하지 않아야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")

    def function_body(name):
        # 함수 시작을 찾고, 중괄호 매칭으로 body를 추출
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
    """catalog.js와 detail.js가 최적화 이미지 fallback 정책을 준수해야 합니다."""
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
    # 충돌 방지 naming 정책: safeStem 패턴이 JS에 존재해야 함
    assert "safeStem" in combined, "collision-safe safeStem 헬퍼 누락"


def test_catalog_js_has_loading_error_and_scroll_restore_contracts():
    """catalog.js에 로딩 placeholder, 에러, 스크롤 복원 계약이 존재해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "mz-placeholder" in src, "로딩 placeholder 클래스 누락"
    assert "mz-catalog-error" in src, "에러 placeholder 클래스 누락"
    assert "sessionStorage" in src, "sessionStorage 사용 누락"
    assert "modelzooCatalogState" in src, "상태 키 modelzooCatalogState 누락"


def test_catalog_js_scroll_listener_with_raf_throttle():
    """C-1: 스크롤 이벤트 리스너가 rAF 스로틀링과 함께 renderViewport를 호출해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "addEventListener" in src and "'scroll'" in src, (
        "scroll 이벤트 리스너가 없습니다 — 가상화가 스크롤 시 업데이트되지 않음"
    )
    assert "requestAnimationFrame" in src, (
        "requestAnimationFrame 스로틀링이 없습니다 — 스크롤 리렌더 폭풍 위험"
    )
    assert "renderViewport" in src, "renderViewport 호출이 필요합니다"


def test_catalog_js_preserves_scroll_position_on_rerender():
    """C-2: innerHTML 교체 시 scrollTop을 보존해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    # _renderCardViewport와 _renderListViewport 모두에서 scrollTop 보존 확인
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
    """C-3: scrollTop 복원이 조건부여야 합니다 — 불필요한 scroll 이벤트 방지."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    # 조건부 복원 패턴이 두 viewport 렌더러 모두에 존재해야 함
    # _isContainerScrollable()를 포함한 조건부 복원도 허용
    conditional_pattern = re.compile(
        r"if\s*\(.*container\.scrollTop\s*!==\s*savedScrollTop"
    )
    matches = conditional_pattern.findall(src)
    assert len(matches) >= 2, (
        f"조건부 scrollTop 복원(if ... container.scrollTop !== savedScrollTop)이 "
        f"card/list 두 렌더러 모두에 있어야 합니다 (발견: {len(matches)}개)"
    )


def test_detail_js_escape_html_handles_quotes():
    """I-2: detail.js escapeHtml이 따옴표도 이스케이프해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "&quot;" in src, (
        "detail.js escapeHtml에 큰따옴표 이스케이프(&quot;)가 없습니다"
    )
    assert "&#39;" in src, (
        "detail.js escapeHtml에 작은따옴표 이스케이프(&#39;)가 없습니다"
    )



def test_detail_js_error_path_escapes_model_id():
    """C-1: renderDetailPage 에러 경로에서 modelId를 escapeHtml로 이스케이프해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    # catch 블록에서 modelId를 raw로 삽입하면 안 됨
    assert "escapeHtml(modelId)" in src, (
        "detail.js 에러 경로에서 escapeHtml(modelId)를 사용해야 합니다 — XSS 위험"
    )
    # raw ${modelId} 패턴이 innerHTML에 직접 사용되면 안 됨
    # catch 블록 내 innerHTML에 raw modelId가 있으면 실패
    catch_match = re.search(r"catch\s*\([^)]*\)\s*\{(.*?)\}", src, re.DOTALL)
    if catch_match:
        catch_body = catch_match.group(1)
        assert "${modelId}" not in catch_body or "escapeHtml(modelId)" in catch_body, (
            "catch 블록에서 raw ${modelId}가 innerHTML에 사용됨 — Reflected XSS"
        )



def test_detail_js_escapes_model_name_in_title():
    """I-2: renderDetail에서 model.name이 escapeHtml으로 이스케이프되어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "escapeHtml(model.name)" in src, (
        "detail.js에서 model.name이 escapeHtml 없이 렌더링됨"
    )


def test_detail_js_escapes_category_label():
    """I-2: renderDetail에서 catLabel이 escapeHtml으로 이스케이프되어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "escapeHtml(catLabel)" in src, (
        "detail.js에서 catLabel이 escapeHtml 없이 렌더링됨"
    )


def test_detail_js_escapes_legal_fields():
    """I-2: renderLegal에서 license/copyright가 escapeHtml으로 이스케이프되어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "escapeHtml(legal.license)" in src, (
        "detail.js에서 legal.license가 escapeHtml 없이 렌더링됨"
    )
    assert "escapeHtml(legal.copyright)" in src, (
        "detail.js에서 legal.copyright가 escapeHtml 없이 렌더링됨"
    )


def test_detail_js_escapes_error_messages():
    """I-2: detail.js에서 e.message가 innerHTML에 삽입될 때 이스케이프되어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    # loadDemoCode의 catch 블록에서 e.message를 raw로 사용하면 안 됨
    assert "escapeHtml(e.message)" in src, (
        "detail.js에서 e.message가 escapeHtml 없이 innerHTML에 삽입됨"
    )


def test_detail_js_escapes_remaining_detail_content_fields():
    """Security: description/spec/compile/legal URL도 HTML/속성 문맥에서 escape해야 합니다."""
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
    """Security: API error 문자열은 상태 HTML에 삽입되기 전에 escape해야 합니다."""
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
    """Security: model.id를 inline onclick JS 문자열에 직접 삽입하지 않아야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "onclick=\"downloadModel(event, '${model.id}'" not in src
    assert "data-model-id=\"${escapeHtml(model.id)}\"" in src
    assert "initDownloadButtons(container)" in src
    assert "downloadModel(event, btn.dataset.modelId || '', btn.dataset.quant || '')" in src


def test_detail_js_cancel_download_avoids_inline_model_id_handler():
    """Security: cancel button도 modelId/quantType을 inline onclick에 삽입하지 않아야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "onclick=\"cancelDownload('${modelId}','${quantType}')\"" not in src
    assert "data-cancel-download" in src
    assert "cancelDownload(modelId, quantType)" in src


def test_catalog_and_detail_image_src_attributes_are_escaped():
    """Security: optimized image src 후보도 attribute 문맥에서 escape해야 합니다."""
    catalog = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert 'src="${_escapeAttr(first)}"' in catalog, (
        "catalog.js imageTagWithFallback의 src가 _escapeAttr 없이 삽입됨"
    )
    assert 'src="${escapeHtml(first)}"' in detail, (
        "detail.js _detailImageTag의 src가 escapeHtml 없이 삽입됨"
    )


def test_catalog_js_avoids_inline_model_id_navigation_handlers():
    """Security: catalog card/list는 model id를 inline onclick JS 문자열에 넣지 않아야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "onclick=\"location.hash='model=${m.id}'\"" not in src
    assert "data-model-id=\"${_escapeAttr(m.id)}\"" in src
    assert "_bindModelNavigation" in src
    assert "location.hash = 'model=' + encodeURIComponent(modelId)" in src


def test_modelzoo_encoded_hashes_decode_before_detail_render():
    """Correctness: encoded model hash는 API 호출 전 원래 model id로 decode해야 합니다."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    i18n = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "i18n.js")
    assert "function getModelIdFromHash" in app
    assert "decodeURIComponent(raw)" in app
    assert "getModelIdFromHash(location.hash)" in app
    assert "getModelIdFromHash(location.hash)" in i18n
    assert "location.hash.replace('#model=', '')" not in app
    assert "location.hash.replace('#model=', '')" not in i18n


def test_modelzoo_waits_for_health_check_before_initial_route_render():
    """DX App 상태 확인이 끝난 뒤 상세 화면을 렌더링해야 비활성 오탐을 줄일 수 있습니다."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    assert "await checkDxAppHealth();" in app
    assert app.index("await checkDxAppHealth();") < app.index("route();")


def test_modelzoo_rerenders_detail_when_dx_app_health_changes():
    """상세 화면에서 health 상태가 바뀌면 Run Demo/다운로드 제어도 동기화되어야 합니다."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    assert "const changed = previousAlive !== _dxAppAlive;" in app
    assert "if (changed && location.hash.startsWith('#model='))" in app
    assert "renderDetailPage(getModelIdFromHash(location.hash));" in app


def test_modelzoo_api_urls_are_proxy_prefix_aware():
    """런처 /zoo 경유에서도 ModelZoo API가 런처 /api/health와 충돌하지 않아야 합니다."""
    app = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "app.js")
    assert "function modelzooApiUrl(path)" in app
    assert "fetch(modelzooApiUrl('/api/health'))" in app
    assert "fetch(modelzooApiUrl('/api/catalog'))" in app


def test_modelzoo_client_api_calls_use_proxy_prefix_helper():
    """ModelZoo 클라이언트 API 호출은 런처 /zoo prefix를 보존해야 합니다."""
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
    """프록시가 code 대신 error 필드로 반환해도 DX App 미실행 상태를 정확히 표시해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "inference.js")
    assert "data.error === 'DX_APP_UNAVAILABLE'" in src


def test_detail_run_demo_button_opens_inference_panel_explicitly():
    """Run Demo 버튼은 추론 패널을 열고 스크롤해야 사용자가 즉시 실행 위치를 볼 수 있습니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    assert "openInferencePanelFromDemo" in src
    assert "onclick=\"openInferencePanelFromDemo()\"" in src


def test_detail_example_images_have_no_inline_width_caps():
    """모든 Example 타입은 상세 박스 폭을 활용해야 하며 inline max-width cap에 묶이면 안 됩니다."""
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
    """Security: category id도 inline onclick JS 문자열에 넣지 않아야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "onclick=\"toggleCategory('${id}')\"" not in src
    assert "onclick=\"toggleCategory('__unknown__')\"" not in src
    assert "data-cat=\"${_escapeAttr(id)}\"" in src
    assert "_bindCategoryChipEvents(container)" in src


def test_catalog_js_escapes_spec_fields_in_card_and_list():
    """Security: catalog card/list specification 필드는 HTML 삽입 전 escape해야 합니다."""
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
    """Security: list sort header도 inline onclick 없이 data attribute로 위임해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "onclick=\"onListHeaderClick('${h.key}')\"" not in src
    assert "data-sort-key=\"${_escapeAttr(h.key)}\"" in src
    assert "${_escapeAttr(h.label)}${arrow}" in src
    assert "_bindListSortEvents" in src
    assert "onListHeaderClick(target.dataset.sortKey || '')" in src



def test_catalog_js_window_scroll_listener():
    """I-1: catalog.js가 window scroll 이벤트도 바인딩해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "window.addEventListener" in src and "'scroll'" in src, (
        "window scroll 리스너가 없습니다 — container가 스크롤 컨테이너가 아닐 때 가상화 미동작"
    )


def test_catalog_js_effective_scroll_uses_window():
    """I-1: catalog.js가 window.scrollY/getBoundingClientRect를 사용한 effective scroll을 계산해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    has_window_scroll = "window.scrollY" in src or "window.pageYOffset" in src
    has_bounding_rect = "getBoundingClientRect" in src
    assert has_window_scroll and has_bounding_rect, (
        "window.scrollY와 getBoundingClientRect를 사용한 effective scroll 계산이 필요합니다"
    )



def test_catalog_js_processor_placeholder_removed_from_release():
    """catalog.js와 style.css에서 프로세서 플레이스홀더가 제거되었어야 합니다 (릴리스 계약)."""
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
    """i18n.js에 Explorer 리디자인에 필요한 키가 정의되어 있어야 합니다."""
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
    """릴리스 UI에 AI Processor 필터가 노출되지 않아야 합니다 (M2 미출시)."""
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
    """detail.js에 기존 섹션 ID가 보존되어야 합니다."""
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
    """catalog.js에 bounded DOM 렌더링 상수와 리스트 행 클래스가 존재해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert re.search(r"CARD_DOM_LIMIT\s*=\s*50\b", src), \
        "CARD_DOM_LIMIT must be assigned the value 50"
    assert re.search(r"LIST_ROW_DOM_LIMIT\s*=\s*100\b", src), \
        "LIST_ROW_DOM_LIMIT must be assigned the value 100"
    assert "mz-list-row" in src
    assert "getVisibleRange" in src
    assert "renderViewport" in src


def test_catalog_js_resets_viewport_when_filters_change():
    """Filter/search/sort 변경 시 깊은 스크롤 상태에서 빈 viewport가 나오지 않아야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "function resetCatalogViewport" in src
    for handler in ("toggleCategory", "onSearchInput", "onSortChange", "resetFilters"):
        match = re.search(rf"function\s+{handler}\s*\([^)]*\)\s*\{{(.*?)\n\}}", src, re.DOTALL)
        assert match, f"{handler} 함수를 찾을 수 없습니다"
        assert "resetCatalogViewport()" in match.group(1), (
            f"{handler}에서 필터 변경 전 viewport scroll을 초기화해야 합니다"
        )


def test_catalog_js_clamps_visible_range_after_result_shrink():
    """저장/현재 scrollTop이 결과 수를 넘어서도 visible range가 유효 범위에 머물러야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "totalRows" in src, "카드 visible range는 전체 row 수 기준으로 clamp해야 합니다"
    assert "maxStartRow" in src, "visible range 시작 row를 최대 유효 row로 clamp해야 합니다"
    assert re.search(r"Math\.min\(\s*rawStartRow\s*,\s*maxStartRow\s*\)", src)


def test_catalog_js_card_visible_range_clamps_in_row_space():
    """카드 가상화는 마지막 모델들이 누락되지 않도록 row-space에서 tail clamp해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "const totalRows = Math.ceil(models.length / cols);" in src
    assert "const rowsByLimit = Math.max(1, Math.floor(CARD_DOM_LIMIT / cols));" in src
    assert "const windowRows = Math.min(visibleRows, rowsByLimit);" in src
    assert "const maxStartRow = Math.max(0, totalRows - windowRows);" in src
    assert re.search(r"const\s+startRow\s*=\s*Math\.min\(\s*rawStartRow\s*,\s*maxStartRow\s*\)", src)
    assert "const endIdx = Math.min(models.length, startIdx + windowRows * cols, startIdx + CARD_DOM_LIMIT);" in src


def test_catalog_js_restored_unknown_filter_requires_unknown_models():
    """복원된 __unknown__ 필터는 실제 unknown 모델이 있을 때만 유지되어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "function hasUnknownCategoryModels" in src
    restore_match = re.search(r"_restoreState\(\)\s*\{(.*?)\n  \},", src, re.DOTALL)
    assert restore_match, "_restoreState body를 찾을 수 없습니다"
    restore_body = restore_match.group(1)
    assert "isValidCategoryFilter(c, { requireUnknownModels: true })" in restore_body


def test_catalog_js_populates_active_summary_on_initial_render():
    """초기 렌더 직후 subtitle/active summary가 비어 있지 않아야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    init_match = re.search(r"init\(dataOrMeta\)\s*\{(.*?)\n  \},", src, re.DOTALL)
    assert init_match, "ModelZooVirtualCatalog.init body를 찾을 수 없습니다"
    init_body = init_match.group(1)
    assert "this.resetAndRender();" in init_body
    assert "updateActiveFilterSummary();" in init_body


def test_catalog_js_syncs_restored_sort_and_view_controls():
    """복원된 sort/view 상태는 내부 상태뿐 아니라 visible controls에도 반영되어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert "function syncCatalogControls" in src
    assert "sortSelect.value = _sortField" in src
    assert "btnCardView" in src and "btnListView" in src
    init_match = re.search(r"init\(dataOrMeta\)\s*\{(.*?)\n  \},", src, re.DOTALL)
    assert init_match, "ModelZooVirtualCatalog.init body를 찾을 수 없습니다"
    assert "syncCatalogControls();" in init_match.group(1)


def test_catalog_js_renders_enriched_card_and_missing_states():
    """Catalog card/list는 generated metadata와 빈 값 상태를 표시해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    for token in ("performance", "Benchmark required", "input_resolution", "artifacts", "missing"):
        assert token in src


def test_detail_js_renders_hybrid_datasheet_sections():
    """Detail 화면은 Hybrid Datasheet 섹션과 기존 anchor ID를 함께 유지해야 합니다."""
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
    """Frontend는 raw artifact URL이 아니라 backend artifact endpoint만 링크해야 합니다."""
    detail = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    catalog = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    combined = detail + catalog
    assert "modelzoo-api.devops.dpx.ai" not in combined
    assert "/api/catalog/${" in combined or "/artifacts/" in combined


def test_catalog_list_uses_explicit_missing_accuracy_label():
    """List accuracy/resolution 누락 값은 '-' 대신 명시적인 source-missing 라벨이어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    body = js_function_body(src, "renderListRow")
    assert "let accuracy = '';" in body
    assert "let accuracy = '-'" not in body
    assert "legacyAccuracy" not in body
    assert "legacyResolution" not in body
    assert "const resolution = _modelInputResolution(m);" in body
    assert "_missingLabel('Not provided by source')" in body


def test_detail_legal_source_rows_render_explicit_missing_metadata():
    """Legal/source 영역은 provenance row와 명시적 missing state를 항상 렌더링해야 합니다."""
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
    """Specification table은 enriched resolution fallback과 explicit missing states를 사용해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderSpecification")
    assert "['Input Resolution', _inputResolution(model)" in body
    assert "performance.fps ?? spec.fps" in body
    assert "performance.fps_per_watt ?? spec.fps_per_watt" in body
    assert "Specification data coming soon." not in body
    assert "Not provided by source" in body


def test_detail_artifact_table_renders_last_checked_status():
    """Artifact table은 last checked/sync 상태를 표시해야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderArtifactTable")
    assert "T('Last metadata sync')" in body
    assert "Metadata pending" in body


def test_detail_artifact_table_uses_remote_url_as_source_when_present():
    """artifact remote_url이 있으면 Source 칸이 Not provided로 떨어지면 안 됩니다."""
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
    """detail.js renderAccuracyMatrix는 suspect source_status일 때 경고 문구를 표시해야 한다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderAccuracyMatrix")
    assert "source_status" in body
    assert "Suspect value: source verification required" in body


def test_detail_accuracy_matrix_does_not_render_absent_onnx_accuracy_row():
    """홈페이지의 Raw ONNX는 artifact 링크이므로 accuracy matrix의 고정 ONNX 행이 아니어야 합니다."""
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "detail.js")
    body = js_function_body(src, "renderAccuracyMatrix")
    assert "['ONNX', evaluation.onnx]" not in body
    assert ".filter" in body
    assert "evaluation.onnx" not in body


def test_catalog_best_accuracy_skips_suspect():
    """catalog.js _bestAccuracyValue는 source_status가 suspect인 항목을 건너뛰어야 한다."""
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
    """카드 높이 추정이 고정 300px만 사용하지 않고, 측정 메커니즘이 있어야 한다.

    고정 CARD_ESTIMATED_HEIGHT=300은 카드 높이가 다를 때 스크롤 점프를 유발한다.
    _measuredCardHeight 또는 동적 측정 헬퍼가 catalog.js에 존재해야 한다.
    """
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    assert '_measuredCardHeight' in src, (
        "catalog.js must define _measuredCardHeight for dynamic card height measurement "
        "instead of relying solely on fixed CARD_ESTIMATED_HEIGHT=300"
    )


def test_js_class_name_reads_display_class_name():
    """detail.js가 model.display?.class_name을 우선 읽어야 한다."""
    import os
    detail_js = open(os.path.join(
        os.path.dirname(__file__), '..', 'dx_modelzoo', 'static', 'js', 'detail.js'
    )).read()
    assert 'display?.class_name' in detail_js, (
        "detail.js should read model.display?.class_name before model.class_name"
    )


def test_catalog_js_resize_invalidates_measured_card_height():
    """window resize 시 _measuredCardHeight를 무효화해야 스크롤 점프가 발생하지 않는다.

    카드 높이는 창 크기에 따라 변하므로, resize 이벤트 시 측정값을
    null로 리셋하고 다시 측정해야 한다.
    """
    src = read_text(ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js")
    # resize 핸들러 내부에서 _measuredCardHeight를 null로 리셋하는 코드가 있어야 한다
    assert re.search(
        r'resize.*_measuredCardHeight\s*=\s*null|_measuredCardHeight\s*=\s*null.*resize',
        src, re.DOTALL
    ), (
        "catalog.js must invalidate _measuredCardHeight on window resize "
        "so card heights are remeasured after viewport changes"
    )
