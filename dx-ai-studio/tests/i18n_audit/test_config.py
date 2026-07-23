from tools.i18n_audit.config import (
    BRAND_TERMS,
    DISPLAY_ORDER,
    LANGUAGES,
    MODULES,
    SOURCE_EXTENSIONS,
    is_excluded_path,
)


def test_language_order_matches_spec():
    assert LANGUAGES == ("en", "ja", "ko", "es", "zh-CN", "zh-TW")
    assert DISPLAY_ORDER == ("EN", "JA", "KO", "ES", "简", "繁")


def test_all_user_facing_modules_are_registered():
    assert set(MODULES) == {
        "launcher",
        "dx_app",
        "dx_stream",
        "dx_modelzoo",
        "dx_compiler",
        "dx_planner",
        "dx_benchmark",
        "dx_monitor",
        "dx_agent_dev",
        "shared",
    }


def test_submodule_and_runtime_artifacts_are_excluded():
    assert is_excluded_path("dc_dx_studio/app/main.py")
    assert is_excluded_path("dx_app/static/__pycache__/x.pyc")
    assert is_excluded_path("dx_modelzoo/data/generated_catalog.json")
    assert is_excluded_path("dx_modelzoo/data/generated_catalog.cache.json")
    assert is_excluded_path("dx_modelzoo/data/sync_report.json")
    assert is_excluded_path("dx_modelzoo/data/metadata_sync_config.json")
    assert not is_excluded_path("dx_app/static/js/i18n.js")


def test_generated_reports_and_tests_are_excluded():
    """Report outputs and test files must not be scanned by the audit."""
    assert is_excluded_path("docs/superpowers/reports/2026-05-29-six-language-copy-audit.json")
    assert is_excluded_path("docs/superpowers/reports/2026-05-29-six-language-copy-audit.md")
    assert is_excluded_path("docs/superpowers/reports/some-other-report.json")
    assert is_excluded_path("tests/i18n_audit/test_extractors.py")
    assert is_excluded_path("tests/unit/test_something.py")
    # Real source files must still pass
    assert not is_excluded_path("launcher/static/index.html")
    assert not is_excluded_path("dx_app/static/js/i18n.js")


def test_source_extensions_and_brand_terms_are_explicit():
    assert SOURCE_EXTENSIONS == (".html", ".js", ".json", ".py")
    for term in ("DX AI Studio", "NPU", "SDK", "DX-M1", "GStreamer", "WebRTC"):
        assert term in BRAND_TERMS
