# SPDX-License-Identifier: Apache-2.0
"""RED-first unit tests for showcase reproducibility equivalence checkers.

These tests pin the equivalence contract: a known-good output directory must
score EQUIVALENT, an empty one FAILED, and a partial one not-EQUIVALENT. The
P2 (squat) case is validated against the REAL checked-in showcase dir (its app
+ session.log are committed); the P1 (export) case uses a synthesized good
fixture because the showcase's runtime artifacts (.dxnn) are intentionally not
committed.

Run:  python -m pytest .deepx/e2e/showcase_repro/test_checks.py -v
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from showcase_repro.checks import evaluate_showcase
from showcase_repro.isolation import is_sanctioned, isolation_violations
from showcase_repro.showcase_registry import SHOWCASES

SHOWCASE_ROOT = Path(__file__).resolve().parents[3] / "dx-agent-dev-showcase"
GT_DXNN_SIZE = 6_890_634  # ground-truth yolo26n.dxnn size from expected_output.txt


# --------------------------------------------------------------------------- #
# Registry
# --------------------------------------------------------------------------- #
def test_registry_has_both_pilots():
    for key in ("ultralytics-yolo-deepx-export", "mini-game-squat-fitness"):
        assert key in SHOWCASES, f"{key} missing from registry"
        assert SHOWCASES[key].prompt.strip(), f"{key} has empty prompt"


# --------------------------------------------------------------------------- #
# P2 — squat: validate against the REAL committed showcase
# --------------------------------------------------------------------------- #
def test_p2_squat_original_showcase_is_equivalent():
    original = SHOWCASE_ROOT / "mini-game-squat-fitness"
    assert original.is_dir(), f"missing showcase: {original}"
    result = evaluate_showcase("mini-game-squat-fitness", original)
    assert result.verdict == "EQUIVALENT", (
        f"original squat showcase should self-verify as EQUIVALENT, got "
        f"{result.verdict}: {result.summary()}"
    )


# --------------------------------------------------------------------------- #
# P1 — export: synthesized good fixture (runtime .dxnn not committed)
# --------------------------------------------------------------------------- #
def _build_p1_good_fixture(root: Path) -> Path:
    model_dir = root / "yolo26n_deepx_model"
    model_dir.mkdir(parents=True)
    # right-sized .dxnn (matches ground-truth byte count)
    with open(model_dir / "yolo26n.dxnn", "wb") as f:
        f.truncate(GT_DXNN_SIZE)
    (model_dir / "config.json").write_text(json.dumps({"model": "yolo26n", "graphs": 1}))
    (model_dir / "metadata.yaml").write_text("name: yolo26n\ntask: detect\n")
    for fn in ("setup.sh", "run.sh", "verify.py"):
        (root / fn).write_text("#!/bin/bash\necho ok\n" if fn.endswith(".sh") else "print('ok')\n")
    (root / "README.md").write_text("# export showcase repro\n")
    (root / "session.log").write_text(
        "=== STEP 2: Verify artifacts ===\n"
        "[verify] RESULT: PASS — all artifacts verified\n"
        "=== STEP 3: Inference on bus.jpg ===\n"
        "image 1/1 bus.jpg: 640x640 4 persons, 1 bus, 24.2ms\n"
        "[infer] Detected 5 object(s) in image\n"
        "  [  5] bus                   conf=0.951\n"
        "[infer] PASS\n"
    )
    return root


def test_p1_export_synthetic_good_is_equivalent(tmp_path):
    out = _build_p1_good_fixture(tmp_path / "good")
    result = evaluate_showcase("ultralytics-yolo-deepx-export", out)
    assert result.verdict == "EQUIVALENT", (
        f"good export fixture should be EQUIVALENT, got {result.verdict}: {result.summary()}"
    )


def test_p1_export_missing_dxnn_is_not_equivalent(tmp_path):
    out = _build_p1_good_fixture(tmp_path / "nodxnn")
    (out / "yolo26n_deepx_model" / "yolo26n.dxnn").unlink()
    result = evaluate_showcase("ultralytics-yolo-deepx-export", out)
    assert result.verdict != "EQUIVALENT"


# --------------------------------------------------------------------------- #
# Empty / failed
# --------------------------------------------------------------------------- #
def _build_p2_good_fixture(root: Path, *, config: str, with_unit_test: bool) -> Path:
    """Minimal squat app that RAN successfully (counted squats, saved video).

    Parameterized by the config.json body and whether a unit-test file exists, to
    pin two checker-contract points: (1) flat squat-tuning keys count as squat
    config (not only the original's nested ``squat_game``); (2) a unit test is
    informational, not a hard deliverable.
    """
    root.mkdir(parents=True)
    fac = root / "factory"
    fac.mkdir()
    (fac / "squat_game_factory.py").write_text(
        "class F:\n"
        "    def create_preprocessor(self): ...\n"
        "    def create_postprocessor(self): ...\n"
        "    def create_visualizer(self): ...\n"
        "    def get_model_name(self): ...\n"
        "    def get_task_type(self): ...\n"
    )
    (root / "yolo26n_pose_squat_sync.py").write_text("from common.runner import SyncRunner\n")
    (root / "common").mkdir()  # vendored framework (self-contained) — required for copy-out import
    (root / "common" / "__init__.py").write_text("")
    (root / "config.json").write_text(config)
    for fn in ("setup.sh", "run.sh"):
        (root / fn).write_text("#!/bin/bash\necho ok\n")
    (root / "README.md").write_text("# squat repro\n")
    (root / "session.log").write_text(
        "Sanity check PASSED!\n"
        "[INFO] Squat #1 counted (frame 45)\n"
        "[SQUAT GAME] Final score — total squats counted: 3\n"
        "[INFO] Saving output video: output.mp4\n"
        " Overall FPS     :   32.1 FPS\n"
    )
    if with_unit_test:
        (root / "test_squat_logic.py").write_text("def test_x():\n    assert True\n")
    return root


def test_p2_flat_squat_config_is_recognized(tmp_path):
    """A squat app using FLAT tuning keys and NO unit test must still be
    EQUIVALENT if it ran and counted squats (matches the approved criterion)."""
    out = _build_p2_good_fixture(
        tmp_path / "flat",
        config=json.dumps({"squat_down_angle": 90, "squat_up_angle": 155}),
        with_unit_test=False,
    )
    result = evaluate_showcase("mini-game-squat-fitness", out)
    assert result.verdict == "EQUIVALENT", (
        f"flat-config + no-unit-test squat app that ran should be EQUIVALENT, "
        f"got {result.verdict}: {result.summary()}"
    )


def test_p2_output_video_to_artifacts_still_counts(tmp_path):
    """A squat app whose video went to dx_app/artifacts (Save stage in the log, no
    session-dir output.mp4) must still pass output_video_saved (saved, just elsewhere)."""
    out = _build_p2_good_fixture(
        tmp_path / "artifacts_save",
        config=json.dumps({"squat_down_angle": 90}),
        with_unit_test=False,
    )
    # rewrite the session.log to show only the pipeline Save stage (no explicit
    # "Saving output video" line, no session-dir mp4)
    (out / "session.log").write_text(
        "[INFO] Squat #1 counted\n"
        "[SQUAT GAME] Final score — total squats counted: 2\n"
        " Save                4.07 ms      245.7 FPS\n"
        " Overall FPS     :   50.7 FPS\n"
    )
    result = evaluate_showcase("mini-game-squat-fitness", out)
    metrics = result.tiers["metrics"]
    saved = [c for c in metrics.checks if c.name == "output_video_saved"][0]
    in_session = [c for c in metrics.checks if c.name == "output_in_session_dir"][0]
    assert saved.ok, "Save-stage evidence should count as output_video_saved"
    assert not in_session.gating and not in_session.ok, "should flag not-in-session (info)"
    assert result.verdict == "EQUIVALENT"


def test_p2_no_squat_config_is_not_equivalent(tmp_path):
    """No squat-tuning config at all is a genuine artifact gap."""
    out = _build_p2_good_fixture(
        tmp_path / "nocfg",
        config=json.dumps({"score_threshold": 0.4, "nms_threshold": 0.45}),
        with_unit_test=False,
    )
    result = evaluate_showcase("mini-game-squat-fitness", out)
    assert result.verdict != "EQUIVALENT"


def test_stretch_original_showcase_is_equivalent():
    original = SHOWCASE_ROOT / "mini-game-stretching-coach"
    assert original.is_dir(), f"missing showcase: {original}"
    result = evaluate_showcase("mini-game-stretching-coach", original)
    assert result.verdict == "EQUIVALENT", (
        f"original stretching showcase should self-verify EQUIVALENT, got "
        f"{result.verdict}: {result.summary()}"
    )


def test_rapiddoc_original_showcase_is_equivalent():
    original = SHOWCASE_ROOT / "rapiddoc-pdf2md"
    assert original.is_dir(), f"missing showcase: {original}"
    result = evaluate_showcase("rapiddoc-pdf2md", original)
    assert result.verdict == "EQUIVALENT", (
        f"original rapiddoc showcase should self-verify EQUIVALENT, got "
        f"{result.verdict}: {result.summary()}"
    )


def test_retrain_eval_cross_project_union(tmp_path):
    """A cross-project (suite) retrain cell splits artifacts across a compiler + an app session
    dir. evaluate_showcase(primary, extra_dirs=[other]) must score the UNION as EQUIVALENT."""
    app = tmp_path / "app"; app.mkdir()
    comp = tmp_path / "compile"; comp.mkdir()
    # app dir: report.md + deliverables + entry + sample; compile dir: the 4-way metrics.json
    (app / "report.md").write_text("base vs retrained, fp32 vs INT8 — mAP comparison\n")
    (app / "pipeline.py").write_text("print('retrain+eval')\n")
    (app / "sample_detect.jpg").write_bytes(b"\xff\xd8\xff")
    for fn in ("setup.sh", "run.sh"):
        (app / fn).write_text("#!/bin/bash\necho ok\n")
    (app / "README.md").write_text("# retrain\n")
    (app / "session.log").write_text("training complete; mAP50-95 reported\n")
    (comp / "metrics.json").write_text(json.dumps({"points": {
        "base_fp32": {"map": 0.001}, "base_int8": {"map": 0.008},
        "retrained_fp32": {"map": 0.75}, "retrained_int8": {"map": 0.74}}}))
    name = "ultralytics-retrain-eval-deepx-export-pills"
    # primary (app) dir alone is missing the metrics → not equivalent
    assert evaluate_showcase(name, app).verdict != "EQUIVALENT"
    # union with the compiler dir → equivalent
    assert evaluate_showcase(name, app, extra_dirs=[comp]).verdict == "EQUIVALENT"


@pytest.mark.parametrize("variant", ["braintumor", "pills", "ppe", "wildlife"])
def test_retrain_eval_original_showcase_is_equivalent(variant):
    name = f"ultralytics-retrain-eval-deepx-export-{variant}"
    original = SHOWCASE_ROOT / name
    assert original.is_dir(), f"missing showcase: {original}"
    result = evaluate_showcase(name, original)
    assert result.verdict == "EQUIVALENT", (
        f"original {name} should self-verify EQUIVALENT, got {result.verdict}: {result.summary()}"
    )


def test_ocr_original_showcase_is_equivalent():
    original = SHOWCASE_ROOT / "paddleocr-video-ocr"
    assert original.is_dir(), f"missing showcase: {original}"
    result = evaluate_showcase("paddleocr-video-ocr", original)
    assert result.verdict == "EQUIVALENT", (
        f"original paddleocr showcase should self-verify EQUIVALENT, got "
        f"{result.verdict}: {result.summary()}"
    )


# --------------------------------------------------------------------------- #
# Output-Isolation guard (B2)
# --------------------------------------------------------------------------- #
def test_isolation_session_dir_is_sanctioned():
    assert is_sanctioned("dx-runtime/dx_app/dx-agent-dev/20260623-1/x.py")
    assert is_sanctioned("dx-compiler/dx-agent-dev/20260623-1/compile.py")


def test_isolation_showcase_source_is_violation():
    assert not is_sanctioned("dx-agent-dev-showcase/mini-game-stretching-coach/README.md")


def test_isolation_violations_flags_source_writes_only():
    before = " M dx-compiler\n M dx-runtime\n"
    after = (
        " M dx-compiler\n M dx-runtime\n"
        " M dx-agent-dev-showcase/paddleocr-video-ocr/README.md\n"
        "?? dx-agent-dev-showcase/paddleocr-video-ocr/ocr_output.mp4\n"
        "?? dx-runtime/dx_app/dx-agent-dev/20260623-9_cursor_x/yolo.py\n"
    )
    v = isolation_violations(before, after)
    assert "dx-agent-dev-showcase/paddleocr-video-ocr/README.md" in v
    assert "dx-agent-dev-showcase/paddleocr-video-ocr/ocr_output.mp4" in v
    # the legitimate dx-agent-dev/<session>/ write is NOT a violation
    assert all("dx-agent-dev/20260623-9_cursor_x" not in p for p in v)
    # pre-existing submodule churn is ignored
    assert "dx-compiler" not in v and "dx-runtime" not in v


def test_isolation_preexisting_changes_ignored():
    before = " M dx-agent-dev-showcase/x/README.md\n"
    after = " M dx-agent-dev-showcase/x/README.md\n"
    assert isolation_violations(before, after) == []


# --------------------------------------------------------------------------- #
# Portability / self-containment gate (#4)
# --------------------------------------------------------------------------- #
from showcase_repro.checks import _portability_checks  # noqa: E402


def test_portability_clean_app_passes(tmp_path):
    app = tmp_path / "app"; app.mkdir()
    (app / "ocr_video.py").write_text("import os\nAPP=os.path.dirname(__file__)\n")  # app-relative
    (app / "internal").mkdir()
    (app / "link").symlink_to(app / "internal")  # symlink INSIDE the session — ok
    checks = {c.name: c for c in _portability_checks(app)}
    assert checks["portable_no_symlink_escaping_session"].ok
    assert checks["portable_no_showcase_source_reference"].ok


def test_portability_symlink_escape_fails(tmp_path):
    app = tmp_path / "app"; app.mkdir()
    outside = tmp_path / "showcase_engine"; outside.mkdir()
    (app / "engine").symlink_to(outside)  # cursor's failure mode
    checks = {c.name: c for c in _portability_checks(app)}
    assert not checks["portable_no_symlink_escaping_session"].ok


def test_portability_showcase_reference_fails(tmp_path):
    app = tmp_path / "app"; app.mkdir()
    (app / "setup.sh").write_text(
        'SHOWCASE_DIR="$SUITE_ROOT/dx-agent-dev-showcase/paddleocr-video-ocr"\n'
        'MODEL_DIR="$SHOWCASE_DIR/engine/model_files"\n')  # claude's failure mode
    checks = {c.name: c for c in _portability_checks(app)}
    assert not checks["portable_no_showcase_source_reference"].ok


def test_portability_input_media_reference_allowed(tmp_path):
    """Referencing the prompt-specified INPUT media (a /sample/ clip) from a showcase is
    allowed ('read inputs from there') — not a portability violation."""
    app = tmp_path / "app"; app.mkdir()
    (app / "run.sh").write_text(
        'SHOWCASE_VIDEO="$SUITE_ROOT/dx-agent-dev-showcase/paddleocr-video-ocr/sample/ocr_demo.mp4"\n')
    (app / "engine").mkdir()  # engine vendored locally (self-contained)
    checks = {c.name: c for c in _portability_checks(app)}
    assert checks["portable_no_showcase_source_reference"].ok, "input /sample/ ref must be allowed"


def test_portability_engine_reference_still_fails(tmp_path):
    """But referencing the showcase ENGINE/MODELS (not /sample/) is still a violation."""
    app = tmp_path / "app"; app.mkdir()
    (app / "setup.sh").write_text(
        'MODEL_DIR="$SUITE_ROOT/dx-agent-dev-showcase/paddleocr-video-ocr/engine/model_files"\n')
    checks = {c.name: c for c in _portability_checks(app)}
    assert not checks["portable_no_showcase_source_reference"].ok


from showcase_repro.checks import _portability_copyout  # noqa: E402


def test_portability_copyout_vendored_engine_resolves(tmp_path):
    """Entry imports `engine` AND engine/ is vendored in the app → resolves when copied out."""
    app = tmp_path / "app"; (app / "engine").mkdir(parents=True)
    (app / "engine" / "paddleocr.py").write_text("class PaddleOcr: ...\n")
    (app / "ocr_video.py").write_text("from engine.paddleocr import PaddleOcr\n")
    assert _portability_copyout(app).ok


def test_portability_copyout_missing_vendored_engine_fails(tmp_path):
    """Entry imports `engine` but it is NOT vendored (relied on the suite) → FAIL when copied out."""
    app = tmp_path / "app"; app.mkdir()
    (app / "ocr_video.py").write_text(
        "import sys; sys.path.insert(0, '/somewhere/dx-agent-dev-showcase/paddleocr-video-ocr')\n"
        "from engine.paddleocr import PaddleOcr\n")
    assert not _portability_copyout(app).ok


def test_portability_venv_symlinks_ignored(tmp_path):
    app = tmp_path / "app"; app.mkdir()
    (app / "venv" / "bin").mkdir(parents=True)
    (app / "venv" / "bin" / "python").symlink_to("/usr/bin/python3")  # normal venv symlink
    checks = {c.name: c for c in _portability_checks(app)}
    assert checks["portable_no_symlink_escaping_session"].ok, "venv symlinks must be ignored"


@pytest.mark.parametrize("key", ["ultralytics-yolo-deepx-export", "mini-game-squat-fitness"])
def test_empty_dir_is_failed(key, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    result = evaluate_showcase(key, empty)
    assert result.verdict == "FAILED", f"empty dir for {key} should FAIL, got {result.verdict}"
