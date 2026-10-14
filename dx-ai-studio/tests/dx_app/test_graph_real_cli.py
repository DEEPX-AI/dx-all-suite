"""The Graph Composer server against the real dx_app graph binary (no fakes).

Skipped when neither of dx_app's multi_model_graph_{sync,async} is built. --list-models, --check and parse_model do not open the NPU;
the run-once test does and needs DX_GRAPH_NPU=1.
"""
from __future__ import annotations

import os
import time

import pytest

from dx_app.core import config, graph_catalog, graph_cli, graph_memory, graph_run, graph_validate

pytestmark = pytest.mark.requires_dx_runtime

CASCADE = {"version": 1, "name": "person-attributes",
           "nodes": [{"id": "cam", "type": "source", "uri": "sample/img/sample_people.jpg"},
                     {"id": "od", "model": "yolov8-n_640x640", "params": {"score_threshold": 0.35},
                      "track": {"algo": "iou", "iou": 0.3, "max_age": 30}},
                     {"id": "attr", "model": "deepmar_resnet50_224x224"}],
           "edges": [{"from": "cam", "to": "od"},
                     {"from": "od", "to": "attr", "roi": {"classes": ["person"], "pad": 0.05}}]}


@pytest.fixture(autouse=True)
def _real_binary():
    if graph_cli.available() is None:
        pytest.skip("dx_app's multi_model_graph_{sync,async} is not built")
    graph_cli._caps_cache.clear()
    graph_catalog._cache.update(key=None, value=None)


def test_the_real_model_list_is_read():
    lm = graph_catalog.list_models(refresh=True)
    assert lm["error"] is None
    assert len(lm["models"]) >= 400
    names = {m["name"] for m in lm["models"]}
    assert {"yolov8-n_640x640", "deepmar_resnet50_224x224", "fastdepth_224x224"} <= names
    assert {m["state"] for m in lm["models"]} <= {"installed", "missing", "invalid", "needs_runtime", "not_ready"}


def test_a_shipped_example_checks_clean():
    r = graph_validate.validate(CASCADE)
    assert r["available"] is True
    assert r["errors"] == [], r["errors"]
    assert [m["node"] for m in r["models"] if m["model"]] == ["od", "attr"]   # text lists the source too, JSON not


def test_a_broken_graph_is_pinned_to_its_edge():
    g = {"version": 1, "name": "bad", "nodes": CASCADE["nodes"] + [{"id": "depth", "model": "fastdepth_224x224"}],
         "edges": CASCADE["edges"] + [{"from": "od", "to": "depth", "roi": {"classes": ["person"]}}]}
    r = graph_validate.validate(g)
    assert r["ok"] is False
    assert [(e["code"], e["edge"]) for e in r["errors"]] == [("GRAPH_EDGE", "od->depth")]


def test_memory_of_an_installed_model_comes_from_parse_model():
    f = graph_cli.models_dir() / "fastdepth_224x224.dxnn"
    if not f.is_file() or f.stat().st_size == 0 or graph_memory.parse_model_binary() is None:
        pytest.skip("fastdepth_224x224.dxnn or parse_model is not installed")
    info = graph_memory.model_memory(f)
    assert info and info["total_bytes"] > info["buffers_bytes"] > 0 and info["pool"] >= 1


@pytest.mark.skipif(os.environ.get("DX_GRAPH_NPU") != "1", reason="runs on the NPU; set DX_GRAPH_NPU=1")
def test_run_once_on_the_npu(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)
    graph_run._jobs.clear()
    body, code = graph_run.start(CASCADE)
    assert code == 200, body
    end = time.time() + 120
    while time.time() < end and not graph_run.poll(body["job_id"])["has_result"]:
        time.sleep(0.5)
    r = graph_run.result(body["job_id"])
    assert r["ok"] is True, r["log_tail"]
    assert r["frames"] == 1 and r["outputs"] and r["nodes"]["od"]["shape"] == "boxes"
    assert r["nodes"]["attr"]["crops_total"] >= 1
