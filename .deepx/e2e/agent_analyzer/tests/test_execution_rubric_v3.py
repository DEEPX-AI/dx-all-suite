# SPDX-License-Identifier: Apache-2.0
"""Unit tests for ExecutionTrace rubric v3.

v3 expands the marker dictionary to recognize execution evidence that all 5
tools produce in practice ("Overall FPS", "RESULT: PASS", "End of stream",
etc.), and reallocates the dead `verify_py` weight (sub-scenarios where every
tool scored 0%) into the dominant execution-evidence component.

Both v2 and v3 must remain callable for data lineage preservation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_ANALYZER_DIR = Path(__file__).resolve().parents[1]  # agent_analyzer/ (this file lives in tests/)
if str(_ANALYZER_DIR) not in sys.path:
    sys.path.insert(0, str(_ANALYZER_DIR))

from lib.execution import (
    EXECUTION_RUBRIC_V2,
    EXECUTION_RUBRIC_V3,
    RUBRIC_VERSIONS,
    DEFAULT_RUBRIC_VERSION,
    evaluate_execution,
)


def _write_session(tmp_path: Path, log_body: str = "", extra_files: dict = None) -> Path:
    """Create a fake output dir under tmp_path with given session.log content."""
    d = tmp_path / "session"
    d.mkdir()
    (d / "session.log").write_text(log_body)
    for name, body in (extra_files or {}).items():
        f = d / name
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(body)
    return d


# ---------- 1. New v3 markers: Overall FPS / RESULT: PASS / EOS ----------

def test_inference_overall_fps_marker_v3(tmp_path):
    """v3 must recognize the `Overall FPS` / `Total Frames` / `PERFORMANCE SUMMARY`
    markers as inference evidence; v2 must not.

    NOTE: v2's marker set was later extended (v3.1) to also recognize a bare
    ``<number> FPS`` token, so the log here deliberately avoids any bare
    ``N FPS`` (e.g. ``54.5 FPS``) — otherwise v2 would legitimately match it and
    the regression guard would be meaningless. We isolate the v3-only prefixed
    markers (``Overall FPS : 40.3`` has no number-then-FPS token).
    """
    log = """
    ==================================================
                   PERFORMANCE SUMMARY
    ==================================================
     Total Frames    :   500
     Overall FPS     :   40.3
    ==================================================
    All validations PASSED
    """
    d = _write_session(tmp_path, log)

    v3 = evaluate_execution(d, "dx_app", rubric_version="v3")
    v2 = evaluate_execution(d, "dx_app", rubric_version="v2")

    assert v3.score_breakdown.get("inference_run_evidence", 0) > 0, \
        f"v3 should recognize Overall FPS / Total Frames: breakdown={v3.score_breakdown}"
    assert v2.score_breakdown.get("inference_run_evidence", 0) == 0, \
        f"v2 should NOT recognize the v3-only prefixed markers (regression guard): breakdown={v2.score_breakdown}"


def test_inference_result_pass_marker_v3(tmp_path):
    """v3 must recognize `RESULT: PASS` as inference evidence; v2 must not."""
    log = """
    Running inference...
    Loaded model: yolo26n.dxnn
    RESULT: PASS
    """
    d = _write_session(tmp_path, log)

    v3 = evaluate_execution(d, "dx_app", rubric_version="v3")
    v2 = evaluate_execution(d, "dx_app", rubric_version="v2")

    assert v3.score_breakdown.get("inference_run_evidence", 0) > 0
    assert v2.score_breakdown.get("inference_run_evidence", 0) == 0


def test_inference_v2_compat_bbox_still_passes(tmp_path):
    """v2 patterns (bbox: [, Inference complete) must continue passing under v3."""
    log = "bbox: [10, 20, 100, 200, 'dog', 0.92]"
    d = _write_session(tmp_path, log)

    v3 = evaluate_execution(d, "dx_app", rubric_version="v3")
    v2 = evaluate_execution(d, "dx_app", rubric_version="v2")

    assert v3.score_breakdown.get("inference_run_evidence", 0) > 0
    assert v2.score_breakdown.get("inference_run_evidence", 0) > 0


def test_pipeline_eos_marker_recognized_v3(tmp_path):
    """v3 must recognize `End of stream` as pipeline run evidence (no .mp4 needed)."""
    log = "gst_pipeline state-changed: PLAYING\nEnd of stream\n"
    d = _write_session(tmp_path, log)

    v3 = evaluate_execution(d, "dx_stream", rubric_version="v3")
    v2 = evaluate_execution(d, "dx_stream", rubric_version="v2")

    assert v3.score_breakdown.get("pipeline_dot_or_video", 0) > 0, \
        f"v3 should recognize EOS marker: breakdown={v3.score_breakdown}"
    assert v2.score_breakdown.get("pipeline_dot_or_video", 0) == 0


def test_pipeline_dot_file_still_passes_v3(tmp_path):
    """v3 must still pass on physical .dot/.mp4 files (v2 compatibility)."""
    d = _write_session(tmp_path, "")
    (d / "pipeline.dot").write_text("digraph { a -> b; }")

    v3 = evaluate_execution(d, "dx_stream", rubric_version="v3")
    v2 = evaluate_execution(d, "dx_stream", rubric_version="v2")

    assert v3.score_breakdown.get("pipeline_dot_or_video", 0) > 0
    assert v2.score_breakdown.get("pipeline_dot_or_video", 0) > 0


# ---------- 2. v3 rubric weight invariants ----------

def test_v3_dx_app_total_weights_sum_to_100():
    total = sum(EXECUTION_RUBRIC_V3["dx_app"].values())
    assert total == 100, f"dx_app v3 weights sum {total} != 100: {EXECUTION_RUBRIC_V3['dx_app']}"


def test_v3_dx_stream_total_weights_sum_to_100():
    total = sum(EXECUTION_RUBRIC_V3["dx_stream"].values())
    assert total == 100, f"dx_stream v3 weights sum {total} != 100: {EXECUTION_RUBRIC_V3['dx_stream']}"


def test_v3_dx_stream_cascaded_total_weights_sum_to_100():
    total = sum(EXECUTION_RUBRIC_V3["dx_stream_cascaded"].values())
    assert total == 100, (
        f"dx_stream_cascaded v3 weights sum {total} != 100: "
        f"{EXECUTION_RUBRIC_V3['dx_stream_cascaded']}"
    )


def test_v3_verify_py_removed_from_user_facing_scenarios():
    """verify_py was dead weight (0% pass across all tools) in dx_app/dx_stream/
    cascaded — v3 must remove it from those scenarios."""
    for sc in ("dx_app", "dx_stream", "dx_stream_cascaded"):
        assert "verify_py" not in EXECUTION_RUBRIC_V3[sc], \
            f"v3 {sc} still contains verify_py: {EXECUTION_RUBRIC_V3[sc]}"


def test_v3_compiler_verify_py_preserved():
    """compiler/suite verify_py is meaningful (verify.py exists in practice) — must remain."""
    for sc in ("compiler", "suite"):
        assert "verify_py" in EXECUTION_RUBRIC_V3[sc], \
            f"v3 {sc} unexpectedly removed verify_py: {EXECUTION_RUBRIC_V3[sc]}"


# ---------- 3. Version selector contract ----------

def test_default_rubric_version_is_v3():
    assert DEFAULT_RUBRIC_VERSION == "v3"
    assert "v2" in RUBRIC_VERSIONS and "v3" in RUBRIC_VERSIONS


def test_evaluate_execution_records_version(tmp_path):
    d = _write_session(tmp_path, "bbox: [1, 2, 3, 4]")
    rep_v2 = evaluate_execution(d, "dx_app", rubric_version="v2")
    rep_v3 = evaluate_execution(d, "dx_app", rubric_version="v3")
    assert rep_v2.rubric_version == "v2"
    assert rep_v3.rubric_version == "v3"


def test_v2_rubric_unchanged_from_v1_shape():
    """v2 rubric must remain byte-equivalent to its pre-v3 form (lineage)."""
    assert EXECUTION_RUBRIC_V2["dx_app"] == {
        "session_log_substantial": 10,
        "inference_run_evidence":  25,
        "verify_py":                5,
        "factory_smoke_test":      20,
        "success_markers":         20,
        "clean_logs":              20,
    }
    assert EXECUTION_RUBRIC_V2["dx_stream"] == {
        "pipeline_log_substantial":15,
        "pipeline_dot_or_video":   25,
        "verify_py":                5,
        "gst_element_usage":       20,
        "success_markers":         15,
        "clean_logs":              20,
    }
    assert EXECUTION_RUBRIC_V2["dx_stream_cascaded"] == {
        "pipeline_log_substantial":15,
        "pipeline_dot_or_video":   20,
        "verify_py":                5,
        "two_stage_evidence":      25,
        "success_markers":         15,
        "clean_logs":              20,
    }
