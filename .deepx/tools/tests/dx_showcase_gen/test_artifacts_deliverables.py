"""Tests for curated-deliverable handling: model artifacts (.dxnn/.pt/.onnx) are copied
into a showcase and required by the verify gate for retrain/export showcases.

Regression guard for the "runs/ + *_deepx_model/ + .dxnn were never committed" gap.
"""
from pathlib import Path

from dx_showcase_gen import artifacts, verify


def _make_session(tmp_path):
    s = tmp_path / "session"
    (s / "runs" / "train" / "weights").mkdir(parents=True)
    (s / "venv" / "lib").mkdir(parents=True)
    (s / "__pycache__").mkdir(parents=True)
    (s / "model.dxnn").write_bytes(b"\x00dxnn")
    (s / "model.onnx").write_bytes(b"\x00onnx")
    (s / "config.json").write_text("{}")
    (s / "runs" / "train" / "results.png").write_bytes(b"\x89PNG")
    (s / "runs" / "train" / "weights" / "best.pt").write_bytes(b"\x00pt")
    (s / "venv" / "lib" / "junk.pt").write_bytes(b"\x00pt")
    (s / "__pycache__" / "m.pyc").write_bytes(b"\x00")
    (s / "clip.mp4").write_bytes(b"\x00")
    return s


def test_copy_keeps_model_deliverables_but_skips_env_and_media(tmp_path):
    s = _make_session(tmp_path)
    dst = tmp_path / "showcase"
    artifacts.copy_session_artifacts(str(s), str(dst))
    # curated deliverables ARE copied
    assert (dst / "model.dxnn").exists()
    assert (dst / "model.onnx").exists()
    assert (dst / "config.json").exists()
    assert (dst / "runs" / "train" / "results.png").exists()
    assert (dst / "runs" / "train" / "weights" / "best.pt").exists()
    # environments / caches / heavy media are NOT copied
    assert not (dst / "venv").exists()
    assert not (dst / "__pycache__").exists()
    assert not (dst / "clip.mp4").exists()


def _make_retrain_showcase(tmp_path):
    sc = tmp_path / "ultralytics-retrain-eval-deepx-export-demo"
    dm = sc / "yolo26n_demo_deepx_model"
    dm.mkdir(parents=True)
    (dm / "config.json").write_text("{}")
    (dm / "metadata.yaml").write_text("k: v\n")
    (dm / "yolo26n_demo.dxnn").write_bytes(b"\x00")
    (sc / "runs" / "train").mkdir(parents=True)
    (sc / "runs" / "train" / "results.png").write_bytes(b"\x89PNG")
    (sc / "runs" / "train" / "weights").mkdir(parents=True)
    (sc / "runs" / "train" / "weights" / "best.pt").write_bytes(b"\x00")
    return sc


def test_evidence_gaps_none_when_complete(tmp_path):
    sc = _make_retrain_showcase(tmp_path)
    assert verify.showcase_evidence_gaps(str(sc), "retrain") == []


def test_evidence_gaps_lists_all_missing(tmp_path):
    sc = tmp_path / "ultralytics-retrain-eval-deepx-export-empty"
    sc.mkdir()
    gaps = verify.showcase_evidence_gaps(str(sc), "retrain")
    assert any("deepx_model" in g for g in gaps)
    assert any("results.png" in g for g in gaps)
    assert any("best.pt" in g for g in gaps)


def test_evidence_gaps_export_needs_deepx_only(tmp_path):
    sc = tmp_path / "ultralytics-yolo-deepx-export-demo"
    dm = sc / "yolo26n_deepx_model"
    dm.mkdir(parents=True)
    (dm / "config.json").write_text("{}")
    (dm / "metadata.yaml").write_text("k: v\n")
    (dm / "yolo26n.dxnn").write_bytes(b"\x00")
    # export kind must NOT require runs/best.pt (no training stage)
    assert verify.showcase_evidence_gaps(str(sc), "export") == []


def test_evidence_gaps_skipped_for_game(tmp_path):
    sc = tmp_path / "mini-game-demo"
    sc.mkdir()
    assert verify.showcase_evidence_gaps(str(sc), "game") == []
