"""DX Planner server unit tests."""

import json
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def test_dx_planner_create_server_returns_http_server():
    """create_server(port) returns a usable HTTP server with expected attributes."""
    from dx_planner.server import create_server
    srv = create_server(port=28096)
    try:
        assert hasattr(srv, "serve_forever")
        assert hasattr(srv, "shutdown")
        assert hasattr(srv, "server_close")
        host, port = srv.server_address
        assert port == 28096
    finally:
        srv.server_close()


def _start_server(port=18096):
    from dx_planner.server import DXPlannerHandler

    srv = ThreadingHTTPServer(("127.0.0.1", port), DXPlannerHandler)
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    time.sleep(1)
    return srv


@pytest.fixture(scope="module")
def server():
    srv = _start_server(18096)
    yield srv
    srv.shutdown()
    srv.server_close()


def _get_json(path, port=18096):
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return json.loads(resp.read())


def _get_raw(path, port=18096):
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode(), resp.status


def _get_bytes(path, port=18096):
    url = f"http://127.0.0.1:{port}{path}"
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read(), resp.status, resp.headers.get("Content-Type", "")


def test_index_serves_html(server):
    body, status = _get_raw("/")
    assert status == 200
    assert "<!DOCTYPE html>" in body
    assert "DX EdgeGuide" in body


def test_index_html_serves_html(server):
    body, status = _get_raw("/index.html")
    assert status == 200
    assert "DX EdgeGuide" in body


def test_local_css_served(server):
    body, status = _get_raw("/static/css/style.css")
    assert status == 200
    assert ".planner-topbar" in body


def test_shared_foundation_css_served(server):
    body, status = _get_raw("/static/shared/dx-fonts.css")
    assert status == 200
    assert "/static/shared/fonts/inter-v20-latin-regular.woff2" in body


def test_shared_font_served(server):
    data, status, content_type = _get_bytes("/static/shared/fonts/inter-v20-latin-regular.woff2")
    assert status == 200
    assert data[:4] == b"wOF2"
    assert len(data) > 100
    assert "font" in content_type or content_type == "application/octet-stream"


def test_hb(server):
    data = _get_json("/api/hb")
    assert data["ok"] is True


def test_unknown_path_404(server):
    with pytest.raises(urllib.error.HTTPError) as exc_info:
        _get_json("/api/nonexistent")
    assert exc_info.value.code == 404


_PLANNER_ROOT = Path(__file__).resolve().parents[2] / "dx_planner"


def _read_planner_file(relative_path):
    return (_PLANNER_ROOT / relative_path).read_text(encoding="utf-8")


def test_edgeguide_progressive_workspace_contracts():
    """워크스페이스 패널 구조, 스크립트, CSS 계약을 검증한다."""
    index_html = _read_planner_file("templates/index.html")
    style_css = _read_planner_file("static/css/style.css")
    planner_js = _read_planner_file("static/js/planner.js")
    workspace_js = _read_planner_file("static/js/workspace.js")
    explorer_js = _read_planner_file("static/js/explorer.js")

    # 워크스페이스 패널 요소 ID는 반드시 index.html에 존재해야 함
    for element_id in [
        "plannerWorkspace",
        "requirementsPanel",
        "recommendationsPanel",
        "detailPanel",
    ]:
        assert element_id in index_html

    # 초기 상태는 HTML에, 모든 전환 상태 이름은 workspace.js에 존재해야 함
    assert "workspace-state-empty" in index_html
    for state_token in [
        "workspace-state-empty",
        "workspace-state-recommended",
        "workspace-state-detailed",
    ]:
        assert state_token in workspace_js

    for token in [
        ".planner-workspace",
        ".workspace-panel",
        ".requirements-panel",
        ".recommendations-panel",
        ".detail-panel",
    ]:
        assert token in style_css

    assert '<script src="/static/js/workspace.js?m=dx_planner"></script>' in index_html
    # PlannerWorkspace는 workspace.js에서 정의되고 planner.js에서 사용
    assert "PlannerWorkspace" in workspace_js
    assert "PlannerWorkspace" in planner_js
    assert ".detail-empty[hidden]" in style_css

    # 구 step-wizard 흔적이 남아 있으면 안 됨
    assert 'id="step-indicator"' not in index_html
    assert 'id="step-1"' not in index_html
    assert 'id="step-2"' not in index_html
    assert 'id="step-3"' not in index_html
    assert "btnBackToStep2" not in index_html
    assert "btnBackToStep2" not in explorer_js
    assert "goToStep" not in planner_js


def test_edgeguide_wizard_no_longer_owns_step_navigation():
    """WizardController는 입력 수집만 담당하고 제거된 step DOM을 조작하지 않아야 한다."""
    wizard_js = _read_planner_file("static/js/wizard.js")

    for obsolete_token in [
        "goToStep",
        "_currentStep",
        "step-indicator",
        "step-${i}",
        "step-1",
        "step-2",
        "step-3",
    ]:
        assert obsolete_token not in wizard_js


def test_edgeguide_workspace_css_removes_obsolete_step_contracts():
    """워크스페이스 CSS는 제거된 step/back/checkbox UI를 스타일링하지 않아야 한다."""
    style_css = _read_planner_file("static/css/style.css")

    for obsolete_selector in [
        ".step-indicator",
        ".step-item",
        ".step-circle",
        ".step-label",
        ".step-connector",
        ".wizard-step",
        ".btn-back",
        ".compare-label",
        ".compare-check",
    ]:
        assert obsolete_selector not in style_css


def test_edgeguide_workspace_layout_fills_screen_without_rail_overflow():
    """1분할은 전체 폭을 쓰고, 2/3분할 rail 내부 요소는 좁은 폭에서 접혀야 한다."""
    style_css = _read_planner_file("static/css/style.css")

    for required in [
        "width: 100%;",
        "grid-template-columns: minmax(0, 1fr);",
        "justify-content: stretch;",
        "container-type: inline-size",
        "container-name: req-panel",
        "@container req-panel",
        ".planner-workspace.workspace-state-recommended",
        "grid-template-columns: minmax(360px, .42fr) minmax(0, 1fr);",
        ".planner-workspace.workspace-state-detailed",
        "minmax(440px, .95fr)",
        "minmax(480px, 1.15fr)",
        ".workspace-state-recommended .task-grid",
        ".workspace-state-detailed .task-grid",
        "grid-template-columns: repeat(2, minmax(0, 1fr));",
        ".workspace-state-recommended .size-btn-row",
        ".workspace-state-detailed .size-btn-row",
        "flex-wrap: wrap;",
        ".workspace-state-detailed .rec-card",
        ".workspace-state-detailed .card-metrics",
    ]:
        assert required in style_css


def test_edgeguide_deeplink_prefill_auto_recommend_contract():
    """딥링크는 입력 프리필 후 즉시 추천을 실행한다 (Benchmark → EdgeGuide 연동)."""
    planner_js = _read_planner_file("static/js/planner.js")
    index_html = _read_planner_file("templates/index.html")

    assert "new URLSearchParams(window.location.search)" in planner_js
    assert "WizardController.setInputs" in planner_js
    assert "triggerInitialRecommendationFromUrl" in planner_js
    assert "PlannerWorkspace.showRecommendations" in planner_js
    assert "runRecommendation" in planner_js
    assert "WizardController.goToStep" not in planner_js
    assert not re.search(r"if\s*\(\s*preTask\s*\|\|\s*preSize\s*\)\s*\{\s*setTimeout\s*\(", planner_js)

    for element_id in [
        "scopeBanner",
        "workflowSteps",
        "scenarioChips",
        "recommendationVerdict",
        "commercePanel",
        "ortToggle",
        "fpsHeadroom",
        "maxLatencyPreset",
        "maxLatencyMs",
        "methodologyDialog",
        "detailSubtitle",
        "requirementsWizardStage",
        "requirementsStep1",
        "requirementsStep2",
        "btnSetupNext",
        "btnSetupBack",
    ]:
        assert element_id in index_html

    assert "methodology.js" in index_html
    assert "methodology-disclaimer" in index_html
    assert "deepx.ai/contact" in index_html
    assert "btn-methodology-icon" in index_html
    assert "MethodologyDialog" in _read_planner_file("static/js/methodology.js")
    assert "MethodologyDialog.init" in planner_js
    assert "_topologyLabel" in _read_planner_file("static/js/recommend.js")
    assert "goToSetupStep" in _read_planner_file("static/js/wizard.js")
    assert "maxLatencyPreset" in _read_planner_file("templates/index.html")
    assert "_syncMaxLatencyControls" in _read_planner_file("static/js/wizard.js")
    assert "requirements-row-3" in _read_planner_file("templates/index.html")
    assert "requirements-priority-drawer" in _read_planner_file("templates/index.html")
    assert "is-priority-open" in _read_planner_file("static/js/wizard.js")


def test_edgeguide_dense_detail_renderer_contracts():
    """추천 카드와 차트는 우측 dense detail 패널을 직접 열어야 한다."""
    cards_js = _read_planner_file("static/js/cards.js")
    charts_js = _read_planner_file("static/js/charts.js")
    explorer_js = _read_planner_file("static/js/explorer.js")

    # 비교 체크박스 플로우 대신 카드 자체가 선택 가능한 버튼 역할을 해야 함
    assert "compare-check" not in cards_js
    assert "compare-label" not in cards_js
    assert "tabIndex = 0" in cards_js
    assert "setAttribute('role', 'button')" in cards_js
    assert "addEventListener('keydown'" in cards_js
    assert "event.key === 'Enter' || event.key === ' '" in cards_js

    # overview chart는 DOM 버튼을 찾아 누르지 않고 콜백으로 detail을 열어야 함
    assert "function getCanvasParentContentWidth" in charts_js
    assert "parseFloat(style.paddingLeft)" in charts_js
    assert "draw(canvas, results, onBarClick)" in charts_js
    assert "getCanvasParentContentWidth(canvas, 500)" in charts_js
    assert "onBarClick(results[idx].platform.id)" in charts_js
    assert ".btn-detail[data-platform-id=" not in charts_js

    # explorer는 선택 결과 기반의 dense detail, 비교 요약, multi-stream 근거를 렌더링해야 함
    assert "open(platformId, inputs, results)" in explorer_js
    assert "const result = (results || []).find" in explorer_js
    for token in [
        "_renderTitle(platform)",
        "_renderFacts(platform, inputs, result)",
        "_renderComparisonSummary(platform, null, inputs, result)",
        "_renderMultiStreamEvidence(platform, inputs)",
        "_renderCommerce(platform, inputs, result)",
        "recommendation-facts",
        "comparison-summary",
        "multi-stream-evidence",
    ]:
        assert token in explorer_js
    assert "_renderComparisonSummary(platform, comparePlatform, inputs, result)" in explorer_js
    assert "_comparisonCopy" in explorer_js
    assert "comparison-summary-head" in explorer_js


def test_edgeguide_overview_chart_redraws_on_workspace_resize():
    """workspace 분할 변경으로 차트 컨테이너 폭이 바뀌면 canvas를 다시 그려야 한다."""
    planner_js = _read_planner_file("static/js/planner.js")

    for token in [
        "function drawOverviewChart()",
        "function scheduleOverviewChartRedraw()",
        "ResizeObserver",
        "overview-chart-container",
        "scheduleOverviewChartRedraw();",
    ]:
        assert token in planner_js

    assert re.search(
        r"function\s+openDetail\(platformId\)\s*\{\s*PlannerWorkspace\.showDetail\(platformId\);\s*ExplorerView\.open",
        planner_js,
        re.DOTALL,
    )


def test_aggregator_multi_stream_passes_operational_fields(tmp_path):
    """multi_stream 집계 시 운영 한계 판단용 필드를 보존해야 한다."""
    from dx_planner.core.aggregator import aggregate_benchmarks
    from tests.dx_planner.test_aggregator import (
        _make_environment,
        _make_model_results,
        _make_multi_stream,
        _make_npu_catalog,
    )

    results_dir = tmp_path / "results"
    run_dir = results_dir / "RPi_M1" / "20250101_run"
    _make_environment(run_dir)
    _make_model_results(run_dir)
    _make_multi_stream(run_dir, entries=[
        {
            "model": "yolo26n.dxnn",
            "task": "object_detection",
            "size": "n",
            "use_ort": True,
            "stream_count": 4,
            "avg_e2e_fps": 120.0,
            "avg_per_channel_fps": 30.0,
            "fps_std": 0.42,
            "avg_cpu_pct": 210.5,
            "npu_throttled": False,
            "npu_total_avg_pct": 55.0,
            "max_rss_mib": 400.0,
        },
    ])
    npu_path = tmp_path / "npu.json"
    _make_npu_catalog(npu_path)

    result = aggregate_benchmarks(results_dir=results_dir, npu_catalog_path=npu_path)
    row = result["platforms"][0]["multi_stream"][0]
    assert row["fps_std"] == 0.42
    assert row["avg_cpu_pct"] == 210.5
    assert row["npu_throttled"] is False
    assert row["npu_total_avg_pct"] == 55.0
    assert row["max_rss_mib"] == 400.0


def test_edgeguide_tutorial_workspace_contracts():
    """튜토리얼은 workspace 패널을 설명하고 구 step-wizard 토큰을 제거해야 함."""
    tutorial_js = _read_planner_file("static/js/tutorial.js")

    for token in [
        "plannerWorkspace",
        "requirementsPanel",
        "recommendationsPanel",
        "detailPanel",
        "compare-dropdown",
        "scopeBanner",
        "scenarioChips",
        "workflowSteps",
        "btnSetupNext",
        "fpsHeadroom",
        "maxLatencyPreset",
        "commercePanel",
        "data-open-methodology",
    ]:
        assert token in tutorial_js

    # 구 step-wizard / Step 2·3 언급 금지
    for forbidden in [
        "goToStep",
        "step-indicator",
        "btnBackToStep2",
        "compare-check",
        "Step 2",
        "Step 3",
    ]:
        assert forbidden not in tutorial_js


def test_recommend_js_channels_sort_replaces_cost():
    """Pricing/cost-sort was removed; ranking now offers a measured 'channels' priority.

    The old cost comparator (and its price_usd null / Infinity-minus-Infinity guards) no longer
    exists because EdgeGuide dropped all monetary figures — real prices proved unreliable.
    """
    recommend_src = _read_planner_file("static/js/recommend.js")

    assert "case 'channels'" in recommend_src, "recommend.js must sort by measured max channels"
    # No monetary/cost machinery may remain.
    for gone in ["costPerChannel", "price_usd", "_systemPriceUsd", "case 'cost'"]:
        assert gone not in recommend_src, f"pricing token {gone!r} must be gone from recommend.js"


def test_recommend_js_null_stream_count_uses_theoretical_fallback():
    """stream_count가 모두 null인 실측 항목은 0+ 채널이 아니라 theoretical fallback이어야 한다."""
    recommend_src = _read_planner_file("static/js/recommend.js")

    assert "filtered.every(m => m.stream_count == null)" in recommend_src
    assert "maxMeasured === 0" in recommend_src
    assert "boundaryFlag: 'theoretical'" in recommend_src


def test_planner_release_data_state_contracts():
    """Planner UI는 unknown/stale/empty release data states를 명시적으로 렌더링해야 한다."""
    cards_js = _read_planner_file("static/js/cards.js")
    data_loader_js = _read_planner_file("static/js/data-loader.js")
    explorer_js = _read_planner_file("static/js/explorer.js")
    style_css = _read_planner_file("static/css/style.css")

    # Pricing was removed from EdgeGuide (real prices proved unreliable); no money is rendered
    # in cards or detail, and cost-based sorting is gone.
    assert "_formatMoney" not in cards_js
    assert "_formatMoney" not in explorer_js
    assert "price_usd" not in cards_js
    assert "systemPrice" not in cards_js
    # benchmark date still falls back to 'N/A' when missing
    assert "'N/A'" in cards_js

    # benchmark meta.generated / benchmark_dates가 UI에 노출되어야 함
    for token in [
        "STALE_BENCHMARK_DAYS",
        "getGeneratedAt()",
        "getBenchmarkDate(platformId)",
        "isBenchmarkStale(platformId",
        "benchmark_dates",
    ]:
        assert token in data_loader_js
    for token in [
        "_benchmarkMeta(pid)",
        "DataLoader.getGeneratedAt()",
        "DataLoader.getBenchmarkDate(pid)",
        "DataLoader.isBenchmarkStale(pid)",
        "badge-stale",
    ]:
        assert token in cards_js

    # 추천 결과가 비어도 빈 화면 안내를 보여야 함
    assert "results.length === 0" in cards_js
    assert "planner-empty-recommendations" in cards_js
    assert "No matching recommendations" in cards_js
    assert ".planner-empty-recommendations" in style_css

    # 동적 innerHTML로 삽입된 data-i18n 텍스트는 즉시 현재 언어로 재적용되어야 함
    assert "DXI18n.applyLang()" in cards_js


def test_planner_release_data_state_i18n_entries():
    """동적 release data state 문자열은 6개 언어 dict에 있어야 한다."""
    i18n_js = _read_planner_file("static/js/i18n.js")
    for key in [
        "Generated",
        "Benchmark",
        "Benchmark stale",
        "No matching recommendations",
        "Try relaxing FPS, channel, or model-size requirements.",
    ]:
        match = re.search(rf"'{re.escape(key)}':\s*\{{(?P<body>[^}}]+)\}}", i18n_js)
        assert match, f"Missing i18n entry for {key!r}"
        body = match.group("body")
        for lang in ["ko", "ja", "es", "'zh-CN'", "'zh-TW'"]:
            assert lang in body, f"{key!r} must include {lang}"
