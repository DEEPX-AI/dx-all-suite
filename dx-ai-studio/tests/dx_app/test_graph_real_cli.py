"""The Graph Composer server against the real dx_app graph binary (no fakes).

Skipped when neither of dx_app's multi_model_graph_{sync,async} is built. --list-models, --check and parse_model do not open the NPU;
the run-once test does and needs DX_GRAPH_NPU=1.
"""
from __future__ import annotations

import json
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


from dx_app.core import graph_live, graph_ops  # noqa: E402


def test_the_real_logic_blocks_are_listed():
    graph_ops._cache.update(key=None, value=None)
    r = graph_ops.list_ops(refresh=True)
    if r["error"] == "list_ops_unsupported":
        pytest.skip("this dx_app build has no --list-ops yet")
    assert r["error"] is None
    assert [o["op"] for o in r["ops"]][:8] == ["filter", "zone", "line", "count", "dwell", "condition", "gallery", "user"]
    zone = {p["name"]: p for p in r["ops"][1]["params"]}
    assert zone["polygon"]["type"] == "polygon" and zone["polygon"]["required"] is True


def test_every_logic_template_checks_clean():
    templates = [e for e in graph_catalog.examples() if e["logic"]]
    if not templates:
        pytest.skip("this dx_app has no logic samples yet")
    assert len(templates) == 6
    for ex in templates:
        r = graph_validate.validate(ex["graph"])
        assert r["errors"] == [], (ex["id"], r["errors"])


@pytest.mark.skipif(os.environ.get("DX_GRAPH_NPU") != "1", reason="runs on the NPU; set DX_GRAPH_NPU=1")
def test_a_logic_template_runs_once_with_events_on_the_npu(tmp_path, monkeypatch):
    """zone_intrusion on its own sample_people.jpg: people enter the zone, then the alarm fires once for all of them
    (track_id: the one track, or -1 for several; the ids in data.track_ids)."""
    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)
    graph_run._jobs.clear()
    ex = {e["id"]: e for e in graph_catalog.examples()}["zone_intrusion"]
    body, code = graph_run.start(ex["graph"])
    assert code == 200, body
    end = time.time() + 120
    while time.time() < end and not graph_run.poll(body["job_id"])["has_result"]:
        time.sleep(0.5)
    r = graph_run.result(body["job_id"])
    assert r["ok"] is True, r["log_tail"]
    pairs = [(e["node"], e["event"]) for e in r["events"]]
    assert pairs and set(pairs[:-1]) == {("zone", "enter")} and pairs[-1] == ("alarm", "intrusion"), pairs
    enters = [e["track_id"] for e in r["events"][:-1]]
    alarm = r["events"][-1]
    assert alarm["track_id"] == (enters[0] if len(enters) == 1 else -1), alarm
    assert alarm["data"]["track_ids"] == ",".join(str(t) for t in enters), alarm
    assert r["events_url"] and r["event_counts"]["zone"]["enter"] == len(pairs) - 1
    assert r["nodes"]["alarm"]["last_records"][0]["numbers"]["value"] >= 1


@pytest.mark.skipif(os.environ.get("DX_GRAPH_NPU") != "1", reason="runs on the NPU; set DX_GRAPH_NPU=1")
def test_a_logic_template_runs_live_on_a_looping_video(tmp_path, monkeypatch):
    if graph_live._deps_missing():
        pytest.skip("Live needs " + ", ".join(graph_live._deps_missing()))
    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)
    ex = {e["id"]: e for e in graph_catalog.examples()}["zone_intrusion"]
    body, code = graph_live.start(ex["graph"], inputs={"cam": "assets/videos/dance-group.mov"})
    assert code == 200, body
    try:
        end, p = time.time() + 60, {}
        while time.time() < end:
            p = graph_live.poll(body["job_id"])
            if p.get("frames", 0) >= 30 or not p.get("running"):
                break
            time.sleep(1)
        assert p["running"] and p["frames"] >= 30 and p["fps"], p
        assert p["event_total"] >= 1, "events reach the poll while it runs"
        # The first grab fits the runner's window to the screen and gives none (it would show the window small)
        end, frame = time.time() + 5, None
        while time.time() < end and not frame:
            frame = graph_live.frame(body["job_id"])
            time.sleep(0.1)
        assert frame and frame[:2] == b"\xff\xd8", "a JPEG of the runner's window"
    finally:
        graph_live.stop(body["job_id"])
    end = time.time() + 15
    while time.time() < end and graph_live.poll(body["job_id"]).get("running"):
        time.sleep(0.5)
    p = graph_live.poll(body["job_id"])
    assert p["running"] is False and p["stopped_by"] == "user" and p["errors"] == [], p


def test_the_real_exporter_plans_a_template_without_writing(tmp_path, monkeypatch):
    from dx_app.core import graph_export
    if not graph_export.available():
        pytest.skip("this dx_app has no scripts/export_graph_project.py")
    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)
    zone = [e for e in graph_catalog.examples() if e["id"] == "zone_intrusion"][0]["graph"]
    body, code = graph_export.plan(zone)
    assert code == 200, body
    assert body["dry_run"] is True and [m["model"] for m in body["models"]] == ["yolov8-n_640x640"]
    assert body["user_logic"] == [] and body["inputs"][0]["copied"] is True and body["source_bytes"] > 500_000
    assert not any(tmp_path.iterdir())


def test_the_real_check_and_exporter_both_refuse_a_keyword_name():
    from dx_app.core import graph_export
    g = json.loads(json.dumps(CASCADE))
    g["nodes"].append({"id": "u", "type": "logic", "op": "user",
                       "params": {"name": "class", "input": "boxes", "output": "boxes"}})
    g["edges"].append({"from": "od", "to": "u", "carry": "result"})
    v = graph_validate.validate(g)
    assert [e["node"] for e in v["errors"]] == ["u"]                       # --check pins it on the node
    if graph_export.available():
        body, code = graph_export.plan(g)
        assert (code, body["error_key"]) == (400, "user_name_invalid")
