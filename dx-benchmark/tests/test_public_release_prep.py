"""Tests for the public-release-prep changes.

Covers behavior changes agreed during review:
  - B2: absolute developer paths must not leak into results JSON / dataset.json
  - O3: preflight required-tool tiering (always vs E2E) + remediation hints
  - governor: warning must be neutral (no 'performance' nudge), fact recorded
"""
from __future__ import annotations

from pathlib import Path

from benchmark import aggregator, env_fingerprint
from benchmark.config import APP_DIR


# ── B2: no absolute-path / username / internal-repo leak ────────────────────

def test_normalize_run_path_is_relative_no_leak():
    # Deliberately leaky-looking input (username + org path) to prove it is stripped.
    result_dir = Path(
        "/home/someuser/work/example-org/some-suite/some-tool/results/EnvX_M1/20260101_000000"
    )
    run = aggregator._normalize_run("20260101_000000", "EnvX_M1", result_dir, {"npu": {}, "software": {}})
    assert "/home/" not in run["path"]
    assert "example-org" not in run["path"]
    assert run["path"] == "EnvX_M1/20260101_000000"


def test_video_info_path_under_repo_is_relative():
    vp = APP_DIR / "assets" / "videos" / "od_benchmark_video.mp4"
    info = env_fingerprint.get_video_info(vp)
    assert "/home/" not in info["path"]
    assert info["path"].endswith("assets/videos/od_benchmark_video.mp4")
    assert info["filename"] == "od_benchmark_video.mp4"


def test_video_info_path_outside_repo_falls_back_to_basename():
    info = env_fingerprint.get_video_info("/home/someuser/private/myvid.mp4")
    assert "/home/" not in info["path"]
    assert info["path"] == "myvid.mp4"


# ── governor: neutral, no performance nudge ─────────────────────────────────

def test_governor_message_has_no_performance_nudge():
    msg = env_fingerprint.check_cpu_governor({"host": {"cpu_governors": {"ondemand": 8}}})
    assert msg is not None
    low = msg.lower()
    assert "performance" not in low
    assert "cpupower" not in low
    assert "ondemand" in low  # still states the fact


def test_governor_empty_returns_none():
    assert env_fingerprint.check_cpu_governor({"host": {"cpu_governors": {}}}) is None


# ── O3: preflight tiering + hints ───────────────────────────────────────────

def test_required_tools_include_dxrt_and_time():
    assert "run_model" in env_fingerprint.REQUIRED_TOOLS
    assert "dxrt-cli" in env_fingerprint.REQUIRED_TOOLS
    assert "time" in env_fingerprint.REQUIRED_TOOLS


def test_e2e_required_tools_defined():
    assert "ffprobe" in env_fingerprint.E2E_REQUIRED_TOOLS


def test_check_preflight_error_has_remediation_hint():
    ok, errors = env_fingerprint.check_preflight({"missing_required": ["run_model"]})
    assert not ok
    assert errors and any("install" in e.lower() for e in errors)


def test_check_e2e_readiness_reports_missing():
    ok, warns = env_fingerprint.check_e2e_readiness({"missing_e2e": ["ffprobe"]})
    assert not ok
    assert warns


def test_check_e2e_readiness_ok_when_empty():
    ok, warns = env_fingerprint.check_e2e_readiness({"missing_e2e": []})
    assert ok
    assert warns == []
