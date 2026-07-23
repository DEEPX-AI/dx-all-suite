"""DX Benchmark and DX Monitor runtime language refresh contracts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_benchmark_lang_refresher_registry():
    src = (ROOT / "dx_benchmark/static/js/app.js").read_text(encoding="utf-8")
    assert "registerBenchmarkLangRefresher" in src
    assert "refreshBenchmarkModuleLanguage" in src
    assert "DXI18n.onLangChange" in src


def test_benchmark_dashboard_registers_refresher():
    src = (ROOT / "dx_benchmark/static/js/dashboard.js").read_text(encoding="utf-8")
    assert "registerBenchmarkLangRefresher" in src


def test_monitor_dashboard_lang_hook():
    src = (ROOT / "dx_monitor/static/js/dashboard.js").read_text(encoding="utf-8")
    assert "DXI18n.onLangChange" in src
    assert "refreshLanguage" in src
