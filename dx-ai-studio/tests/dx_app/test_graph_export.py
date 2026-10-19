"""graph_export: Studio's side of "take away" (Graph Composer Phase 3) against a fake dx_app exporter.

The fake is a Python script named like dx_app's scripts/export_graph_project.py in a dx_app root under tmp_path. It
answers --version, prints the recorded plan (fixtures/graph/export_plan.json: the real exporter's --dry-run --json of
dx_app's tests/cpp_example/graph_export/user_zone.json), writes a small project for an export and prints
export_done.json. FAKE_EXPORT=refuse makes it refuse (model_unknown), FAKE_EXPORT=garbage print no JSON, and
FAKE_EXPORT=old answer another --version. tests/dx_app/test_graph_real_cli.py runs the real one.
"""
from __future__ import annotations

import json
import os
import stat
import zipfile
from pathlib import Path

import pytest

from dx_app.core import config, graph_cli, graph_export, graph_run

FIX = Path(__file__).resolve().parent / "fixtures" / "graph"
FAKE_EXPORTER = '''\
import json, os, pathlib, sys
FIX = pathlib.Path({fix!r})
args = sys.argv[1:]
with open({calls!r}, "a") as log:
    log.write(json.dumps(args) + "\\n")
mode = os.environ.get("FAKE_EXPORT", "ok")
if "--version" in args:
    print("export_graph_project 0" if mode == "old" else "export_graph_project 1")
    sys.exit(0)
if mode == "refuse":
    print(json.dumps({{"ok": False, "error": "node 'od': model 'nope' is not in config/model_registry.json",
                      "error_key": "model_unknown"}}))
    sys.exit(1)
if mode == "unsized" and "--dry-run" in args:
    plan = json.loads((FIX / "export_plan.json").read_text())
    plan["models"][0].update(present=False, bytes=None)
    plan.update(model_bytes=0, model_bytes_unknown=1, bytes=plan["source_bytes"] + plan["input_bytes"])
    print(json.dumps(plan))
    sys.exit(0)
if mode == "garbage":
    print("Traceback (most recent call last): boom", file=sys.stderr)
    sys.exit(1)
plan = json.loads((FIX / "export_plan.json").read_text())
plan["include_models"] = "--no-models" not in args
if "--dry-run" in args:
    print(json.dumps(plan))
    sys.exit(0)
out = pathlib.Path(args[args.index("--out") + 1])
out.mkdir(parents=True)
(out / "CMakeLists.txt").write_text("project(user_zone CXX)\\n")
for script in ("setup.sh", "run.sh"):
    (out / script).write_text("#!/usr/bin/env bash\\necho " + script + "\\n")
    os.chmod(out / script, 0o755)
(out / "models").mkdir()
if plan["include_models"]:
    (out / "models" / "yolov8-n_640x640.dxnn").write_bytes(b"\\0" * 4096)
done = json.loads((FIX / "export_done.json").read_text())
done.update(out=str(out), include_models=plan["include_models"])
print(json.dumps(done))
'''
GRAPH = {"version": 1, "name": "user-zone",
         "nodes": [{"id": "cam", "type": "source", "uri": "sample/img/people.jpg"},
                   {"id": "od", "model": "yolov8-n_640x640", "engine": {"buffers": 2}},
                   {"id": "tag", "type": "logic", "op": "user",
                    "params": {"name": "tag_people", "input": "boxes", "output": "boxes"}}],
         "edges": [{"from": "cam", "to": "od"}, {"from": "od", "to": "tag", "carry": "result"}]}


@pytest.fixture
def fake(tmp_path, monkeypatch):
    """A dx_app root with the fake exporter and a sample image; outputs and scratch files in tmp_path."""
    root = tmp_path / "dx_app"
    (root / "scripts").mkdir(parents=True)
    (root / "sample" / "img").mkdir(parents=True)
    (root / "sample" / "img" / "people.jpg").write_bytes(b"\xff\xd8\xff\xe0 not a real jpeg")
    calls = tmp_path / "export_calls.log"
    (root / "scripts" / "export_graph_project.py").write_text(
        FAKE_EXPORTER.format(fix=str(FIX), calls=str(calls)), encoding="utf-8")
    monkeypatch.setattr(config, "DX_APP_ROOT", root)
    monkeypatch.setattr(config, "SAMPLE_DIR", root / "sample")
    monkeypatch.setattr(config, "ASSETS_DIR", root / "assets")
    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path / "outputs")
    monkeypatch.setattr(graph_cli, "capabilities", lambda: dict(graph_cli.no_capabilities(), engine_key=True))
    monkeypatch.setattr(graph_cli, "models_dir", lambda: tmp_path / "models")
    monkeypatch.setattr(graph_cli, "scratch_file", lambda prefix: tmp_path / f"{prefix}.json")
    monkeypatch.delenv("FAKE_EXPORT", raising=False)
    graph_export._probe.update(key=None, value=False)

    def logged():
        return [json.loads(line) for line in calls.read_text().splitlines()] if calls.exists() else []
    return root, logged


def test_the_exporter_is_found_and_must_speak_schema_1(fake, monkeypatch):
    root, logged = fake
    assert graph_export.available() is True
    assert graph_export.available() is True and logged() == [["--version"]], "probed once per file version"
    monkeypatch.setenv("FAKE_EXPORT", "old")
    graph_export._probe.update(key=None, value=False)
    assert graph_export.available() is False
    (root / "scripts" / "export_graph_project.py").unlink()
    assert graph_export.exporter() is None and graph_export.available() is False
    body, code = graph_export.plan(GRAPH)
    assert (code, body["error_key"]) == (409, "export_unsupported")


def test_a_plan_hands_the_prepared_graph_to_the_exporter(fake, tmp_path):
    root, logged = fake
    body, code = graph_export.plan(GRAPH, name="user-zone")
    assert code == 200 and body == dict(json.loads((FIX / "export_plan.json").read_text()), include_models=True)
    args = logged()[-1]
    assert args[args.index("--model-dir") + 1] == str(tmp_path / "models") and "--dry-run" in args
    assert args[args.index("--name") + 1] == "user-zone" and args[-1] == "--json"
    assert not (tmp_path / "export.json").exists(), "the graph file is removed after the call"


def test_the_graph_is_prepared_like_a_run(fake):
    root, _ = fake
    g = graph_export.prepare(GRAPH)
    assert g["nodes"][0]["uri"] == str((root / "sample/img/people.jpg").resolve())
    assert g["nodes"][1]["engine"] == {"buffers": 2}                       # this build reads "engine"
    assert GRAPH["nodes"][0]["uri"] == "sample/img/people.jpg", "the page's graph is not changed"
    assert graph_export.prepare(GRAPH, {"cam": "camera:0"})["nodes"][0]["uri"] == "camera:0"
    assert graph_export.prepare(GRAPH, {"cam": "rtsp://cam.local/s"})["nodes"][0]["uri"] == "rtsp://cam.local/s"
    for bad in ({"cam": "/etc/passwd"}, {"cam": "sample/img/none.jpg"}, {"cam": 3}):
        with pytest.raises(graph_export.Refused) as e:
            graph_export.prepare(GRAPH, bad)
        assert e.value.key == "invalid_input"
    with pytest.raises(graph_export.Refused) as e:
        graph_export.prepare(GRAPH, ["cam"])
    assert e.value.key == "invalid_payload"


def test_a_gallery_outside_the_input_roots_is_refused(fake):
    g = json.loads(json.dumps(GRAPH))
    g["nodes"].append({"id": "known", "type": "logic", "op": "gallery", "params": {"gallery": "/etc/x.bin"}})
    body, code = graph_export.plan(g)
    assert (code, body["error_key"]) == (400, "gallery_outside_roots")


@pytest.mark.parametrize("name", ["", "9lives", "a b", "x" * 49, "../up", None, 7])
def test_a_bad_folder_name_is_refused_before_the_exporter_runs(fake, name):
    _, logged = fake
    body, code = graph_export.export(GRAPH, name)
    assert (code, body["error_key"]) == (400, "export_name_invalid") and logged() == []


def test_an_export_writes_the_folder_and_a_zip_that_keeps_the_scripts_executable(fake, tmp_path):
    _, logged = fake
    body, code = graph_export.export(GRAPH, "user-zone", include_models=True)
    assert code == 200, body
    folder = Path(body["folder"])
    assert folder.name == "user-zone" and folder.parent.parent == tmp_path / "outputs" / "graph" / "exports"
    assert (folder / "setup.sh").is_file() and body["user_logic"][0]["name"] == "tag_people"
    assert body["zip_url"] == "/outputs/graph/exports/{}/user-zone.zip".format(folder.parent.name)
    zpath = folder.parent / "user-zone.zip"
    assert body["zip_bytes"] == zpath.stat().st_size and not list(folder.parent.glob("*.part"))
    with zipfile.ZipFile(zpath) as z:
        infos = {i.filename: i for i in z.infolist()}
    assert set(infos) == {"user-zone/CMakeLists.txt", "user-zone/setup.sh", "user-zone/run.sh",
                          "user-zone/models/yolov8-n_640x640.dxnn"}
    assert (infos["user-zone/setup.sh"].external_attr >> 16) & stat.S_IXUSR
    assert infos["user-zone/models/yolov8-n_640x640.dxnn"].compress_type == zipfile.ZIP_STORED
    assert infos["user-zone/CMakeLists.txt"].compress_type == zipfile.ZIP_DEFLATED
    calls = logged()
    assert "--dry-run" in calls[-2] and calls[-1][calls[-1].index("--out") + 1] == str(folder)


def test_without_the_models_the_exporter_is_told_so(fake):
    """The models are left out unless asked for (the user's answer, 2026-10-15)."""
    _, logged = fake
    body, code = graph_export.export(GRAPH, "user-zone")
    assert code == 200 and body["include_models"] is False
    assert all("--no-models" in c for c in logged() if "--version" not in c)
    assert not list(Path(body["folder"]).glob("models/*.dxnn"))


def test_the_exporters_refusal_reaches_the_page_and_leaves_nothing(fake, monkeypatch, tmp_path):
    monkeypatch.setenv("FAKE_EXPORT", "refuse")
    body, code = graph_export.export(GRAPH, "user-zone")
    assert (code, body["error_key"]) == (400, "model_unknown") and "nope" in body["error"]
    monkeypatch.setenv("FAKE_EXPORT", "garbage")
    body, code = graph_export.plan(GRAPH)
    assert (code, body["error_key"]) == (500, "export_failed") and "boom" in body["error"]
    assert not any(graph_export.exports_dir().iterdir())


def test_not_enough_disk_is_refused_before_anything_is_written(fake, monkeypatch, tmp_path):
    monkeypatch.setattr(graph_export.shutil, "disk_usage", lambda p: type("U", (), {"free": 100 * 1048576})())
    body, code = graph_export.export(GRAPH, "user-zone")
    assert (code, body["error_key"]) == (507, "export_no_space")
    assert body["need_bytes"] == 2 * json.loads((FIX / "export_plan.json").read_text())["bytes"] + \
        graph_export.HEADROOM
    assert not any(graph_export.exports_dir().iterdir())


def test_one_export_runs_at_a_time(fake):
    assert graph_export._lock.acquire(blocking=False)
    try:
        body, code = graph_export.export(GRAPH, "user-zone")
    finally:
        graph_export._lock.release()
    assert (code, body["error_key"]) == (409, "export_busy")


def test_only_the_newest_exports_are_kept(fake, tmp_path):
    d = graph_export.exports_dir()
    for i in range(6):
        old = d / "old-{}".format(i)
        old.mkdir()
        os.utime(old, (1000 + i, 1000 + i))
    body, code = graph_export.export(GRAPH, "user-zone")
    assert code == 200
    kept = sorted(p.name for p in d.iterdir())
    assert len(kept) == graph_export.KEEP and Path(body["folder"]).parent.name in kept
    assert "old-0" not in kept and "old-5" in kept


# Review fixes (Phase 3 M1)

def test_a_run_folders_upload_is_never_exported(fake, tmp_path):
    from dx_app.core import graph_live
    for folder in (graph_run.runs_dir() / "job1", graph_live.live_dir() / "job2"):
        folder.mkdir(parents=True, exist_ok=True)
        upload = folder / "input_cam.jpg"
        upload.write_bytes(b"\xff\xd8\xff\xe0 an upload")
        with pytest.raises(graph_export.Refused) as e:
            graph_export.prepare(GRAPH, {"cam": str(upload)})
        assert e.value.key == "invalid_input" and "upload" in str(e.value)


def test_the_engine_settings_go_into_the_export_whatever_the_local_binary_reads(fake, monkeypatch):
    monkeypatch.setattr(graph_cli, "capabilities", lambda: dict(graph_cli.no_capabilities(), engine_key=False))
    assert graph_export.prepare(GRAPH)["nodes"][1]["engine"] == {"buffers": 2}


def test_a_probe_that_fails_by_chance_is_asked_again(fake, monkeypatch):
    real = graph_export.subprocess.run
    calls = []

    def flaky(*a, **k):
        calls.append(1)
        if len(calls) == 1:
            raise graph_export.subprocess.TimeoutExpired(a[0], 30)
        return real(*a, **k)
    monkeypatch.setattr(graph_export.subprocess, "run", flaky)
    assert graph_export.available() is False
    assert graph_export.available() is True and len(calls) == 2


def test_any_failure_after_the_folder_is_made_removes_it_and_keeps_the_old_exports(fake, monkeypatch):
    d = graph_export.exports_dir()
    for i in range(graph_export.KEEP):
        old = d / "old-{}".format(i)
        old.mkdir()
        os.utime(old, (1000 + i, 1000 + i))

    def broken(*a, **k):
        raise RuntimeError("zip broke")
    monkeypatch.setattr(graph_export, "_zip", broken)
    body, code = graph_export.export(GRAPH, "user-zone")
    assert (code, body["error_key"]) == (500, "export_failed") and "zip broke" in body["error"]
    assert sorted(p.name for p in d.iterdir()) == ["old-{}".format(i) for i in range(graph_export.KEEP)]
    assert graph_export._lock.acquire(blocking=False)
    graph_export._lock.release()


def test_the_upload_dirs_are_the_run_and_live_folders(fake):
    from dx_app.core import graph_live
    assert graph_export._UPLOAD_DIRS() == (graph_run.runs_dir(), graph_live.live_dir())


def test_a_model_of_unknown_size_reaches_the_page_as_unknown(fake, monkeypatch):
    """A model that is not installed and whose download size the exporter does not know: bytes null, never 0."""
    monkeypatch.setenv("FAKE_EXPORT", "unsized")
    body, code = graph_export.plan(GRAPH)
    assert code == 200
    assert body["models"][0]["bytes"] is None and body["models"][0]["present"] is False
    assert body["model_bytes_unknown"] == 1
    body, code = graph_export.export(GRAPH, "user-zone")          # without the models: the unknown size costs nothing
    assert code == 200 and Path(body["folder"]).is_dir()
