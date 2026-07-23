"""Cross-surface audit for launcher module names."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
LAUNCHER = ROOT / "launcher" / "static"
REQUIRED_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")

# Top-bar nav tabs and status-dot abbreviations stay English for all UI languages.
ENGLISH_NAV_TAB_LABELS = {
    "app": "DX App",
    "stream": "DX Stream",
    "zoo": "Model Zoo",
    "compiler": "Compiler",
    "planner": "EdgeGuide",
    "benchmark": "Benchmark",
    "dx_monitor": "Monitor",
    "agent": "Agent Dev",
    "sdk-library": "SDK Library",
    "about": "About DEEPX",
}

PROHIBITED_PATTERNS = (
    "モデルズー",
    "모델주",
    "Modelzoo",
    "📊 基准测试",
    "📊 基準測試",
)


def _read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def _extract_nav_tab_label(source: str, app_key: str) -> str:
    block = re.search(r"NAV_TAB_LABELS\s*=\s*\{(?P<body>.*?)\n  \};", source, re.S)
    assert block, "NAV_TAB_LABELS must exist"
    key = re.escape(app_key)
    match = re.search(rf"(?:'{key}'|{key}):\s*'([^']*)'", block.group("body"))
    assert match, f"NAV_TAB_LABELS entry for {app_key} not found"
    return match.group(1)


@pytest.fixture(scope="module")
def frame_js() -> str:
    return (LAUNCHER / "launcher-app-frame.js").read_text(encoding="utf-8")


@pytest.mark.parametrize("app_key", list(ENGLISH_NAV_TAB_LABELS.keys()))
def test_nav_tab_labels_are_english_fixed(app_key: str, frame_js: str):
    raw = _extract_nav_tab_label(frame_js, app_key)
    normalized = re.sub(r"^[\U0001F300-\U0001FAFF]\s*", "", raw)
    expected = ENGLISH_NAV_TAB_LABELS[app_key]
    assert expected in normalized, f"{app_key}: got {raw!r}, want fragment {expected!r}"


def test_nav_tab_labels_do_not_use_runtime_localization(frame_js: str):
    config_match = re.search(r"NAV_TAB_CONFIG\s*=\s*\[(.*?)\];", frame_js, re.S)
    assert config_match, "NAV_TAB_CONFIG must exist"
    body = config_match.group(1)
    assert "getLabel" not in body, "Top-bar nav tabs must not call getLabel/_lt"
    assert "ns._lt(" not in body, "Top-bar nav tabs must stay English-fixed"


def test_status_dot_labels_are_english_fixed(frame_js: str):
    for label_id, expected in (
        ("statusLabelZoo", "Zoo"),
        ("statusLabelCompiler", "Compiler"),
        ("statusLabelBenchmark", "Benchmark"),
        ("statusLabelMonitor", "Monitor"),
    ):
        assert f"{label_id}: '{expected}'" in frame_js or f'{label_id}: "{expected}"' in frame_js, (
            f"{label_id} must stay English-fixed"
        )
    refresh = re.search(r"function _refreshStatusDotLabels\(\)\s*\{(?P<body>.*?)\n  \}", frame_js, re.S)
    assert refresh, "_refreshStatusDotLabels must exist"
    assert "ns._lt(" not in refresh.group("body"), "Status dot labels must not localize"


def test_prohibited_module_name_patterns_removed(frame_js: str):
    combined = frame_js + _read("launcher/static/tutorial.js") + _read("launcher/static/sdk-tutorial.js")
    combined += _read("dx_modelzoo/templates/index.html")
    for bad in PROHIBITED_PATTERNS:
        assert bad not in combined, f"prohibited pattern still present: {bad!r}"


def test_model_zoo_brand_name_uses_official_spacing():
    html = _read("dx_modelzoo/templates/index.html")
    assert "name: 'Model Zoo'" in html or 'name: "Model Zoo"' in html


def test_model_zoo_explorer_keeps_product_name_in_all_langs():
    catalog = _read("dx_modelzoo/static/js/i18n-dict-catalog.js")
    block = re.search(r"'DX Model Zoo Explorer':\s*\{(?P<body>[^}]+)\}", catalog, re.S)
    assert block
    body = block.group("body")
    for lang in REQUIRED_LANGS:
        assert f"{lang}:" in body or f"'{lang}':" in body
    for lang in REQUIRED_LANGS:
        value = re.search(rf"['\"]?{re.escape(lang)}['\"]?\s*:\s*'([^']*)'", body)
        assert value, lang
        assert "Model Zoo" in value.group(1), f"{lang} explorer title must keep Model Zoo product name"


def test_about_deepx_loading_copy_localized():
    about = _read("launcher/static/about-deepx.js")
    assert "Acerca de DEEPX" in about
    assert "DEEPXについて" in about
    assert "关于 DEEPX" in about or "正在加载" in about


def test_home_about_cards_use_canonical_module_names():
    html = _read("launcher/static/index.html")
    assert "All About DEEPX" not in html
    assert "All About SDK" not in html
    assert 'data-i18n-module="about"' in html
    assert 'data-i18n-module="sdk-library"' in html


def test_module_label_matrix_defined_in_frame_js(frame_js: str):
    assert "MODULE_LABEL_MATRIX" in frame_js
    assert "MODULE_ORBITAL_MATRIX" in frame_js
    assert "_refreshModuleLabelElements" in frame_js
    for app_key in ENGLISH_NAV_TAB_LABELS:
        assert f"{app_key}:" in frame_js or f"'{app_key}':" in frame_js


def test_platform_modal_pm_names_wired_for_i18n(frame_js: str):
    html = _read("launcher/static/index.html")
    assert "PM_HELP_ID_TO_MODULE" in frame_js
    for help_id in (
        "pm-dx-app", "pm-dx-stream", "pm-model-zoo", "pm-compiler", "pm-edgeguide",
        "pm-benchmark", "pm-monitor", "pm-agent-dev", "pm-sdk-library", "pm-about-deepx",
    ):
        assert f'data-help-id="{help_id}"' in html


def test_about_view_uses_shared_brand():
    """About DEEPX header uses the shared DXBrand slot (unified with modules), mounted from
    about-deepx.js — its name/subtitle localization lives there, not in a bespoke logo title."""
    html = _read("launcher/static/index.html")
    assert 'id="aboutBrand"' in html and "dx-brand-slot" in html
    js = _read("launcher/static/about-deepx.js")
    assert "target: '#aboutBrand'" in js


def test_dx_brand_subtitles_have_six_langs_for_core_modules():
    modules = (
        "dx_app/templates/index.html",
        "dx_stream/templates/index.html",
        "dx_modelzoo/templates/index.html",
        "dx_compiler/templates/base.html",
        "dx_planner/templates/index.html",
        "dx_benchmark/templates/index.html",
        "dx_monitor/templates/index.html",
        "dx_agent_dev/templates/index.html",
    )
    for rel in modules:
        html = _read(rel)
        mount = re.search(r"DXBrand\.mount\(\{(?P<body>.*?)\}\);", html, re.S)
        assert mount, rel
        body = mount.group("body")
        for lang in REQUIRED_LANGS:
            assert f"{lang}:" in body or f"'{lang}':" in body, f"{rel} missing subtitle lang {lang}"
