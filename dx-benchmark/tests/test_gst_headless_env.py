"""Root fix — gst subprocesses run headless by default.

The benchmark sinks to fakesink (never displays), so it must not inherit DISPLAY.
Inheriting it makes VA-API/GL auto-plug a GstGLDisplayX11 and, at high stream
concurrency, abort with `xcb_xlib_threads_sequence_lost` (SIGABRT). Stripping the
display steers GL to DRM/GBM (decode path unchanged). Escape hatch:
DX_BENCH_KEEP_DISPLAY=1. See spec 2026-07-20-dx-benchmark-headless-gst-env-design.md.
"""
from benchmark.runner_pipeline import _build_gst_env


def test_display_stripped_by_default(monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("WAYLAND_DISPLAY", "wayland-0")
    monkeypatch.delenv("DX_BENCH_KEEP_DISPLAY", raising=False)
    env = _build_gst_env()
    assert "DISPLAY" not in env
    assert "WAYLAND_DISPLAY" not in env
    assert env["GST_DEBUG"] == "0"          # existing behavior preserved


def test_escape_hatch_keeps_display(monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.setenv("DX_BENCH_KEEP_DISPLAY", "1")
    env = _build_gst_env()
    assert env["DISPLAY"] == ":0"


def test_env_extra_applied_and_can_override(monkeypatch):
    monkeypatch.setenv("DISPLAY", ":0")
    monkeypatch.delenv("DX_BENCH_KEEP_DISPLAY", raising=False)
    env = _build_gst_env({"FOO": "bar", "DISPLAY": ":9"})
    assert env["FOO"] == "bar"
    assert env["DISPLAY"] == ":9"           # caller override wins over the default strip


def test_no_display_in_parent_is_noop(monkeypatch):
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("DX_BENCH_KEEP_DISPLAY", raising=False)
    env = _build_gst_env()                  # must not raise when DISPLAY absent
    assert "DISPLAY" not in env
