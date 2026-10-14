"""graph_gallery: the graph's gallery op needs a DXGAL1 .bin; Studio builds one from an image folder with dx_app's own
scripts/build_gallery_database.py, here a fake that writes the same file format without an NPU."""
from __future__ import annotations

import json
import struct
import sys
import threading
import time
from pathlib import Path

import pytest

from dx_app.core import config, graph_gallery, graph_run, npu_jobs

# Takes build_gallery_database.py's arguments and writes a DXGAL1 file: one 4-d vector per image, labelled with the
# image's folder when the images span several folders (the script's --labels folder). FAKE_* steer it.
FAKE_SCRIPT = r'''
import argparse, json, os, struct, sys, time
from pathlib import Path
ap = argparse.ArgumentParser()
ap.add_argument("--variant", required=True)
ap.add_argument("--images", required=True, nargs="+")
ap.add_argument("--out", required=True)
ap.add_argument("--models-dir")
args = ap.parse_args()
with open(os.environ["FAKE_CALLS"], "a") as f:
    f.write(json.dumps({"argv": sys.argv, "python": sys.executable}) + "\n")
if os.environ.get("FAKE_SLEEP"):
    time.sleep(float(os.environ["FAKE_SLEEP"]))
if os.environ.get("FAKE_FAIL"):
    print("[DXAPP] [ERROR] no example found for variant '%s'." % args.variant)
    sys.exit(1)
imgs = sorted(p for p in Path(args.images[0]).rglob("*") if p.suffix.lower() in (".jpg", ".png"))
parents = {p.parent for p in imgs}
labels = [p.parent.name if len(parents) > 1 else "" for p in imgs]
print("[DXAPP] [INFO] images   : %d" % len(imgs))
with open(args.out, "wb") as fh:
    fh.write(b"DXGAL1\0\0")
    fh.write(struct.pack("<II", len(imgs), 4))
    fh.write(b"\0" * (16 * len(imgs)))
    for blob in (args.variant.encode(), "\n".join(str(p) for p in imgs).encode(), "\n".join(labels).encode()):
        fh.write(struct.pack("<I", len(blob)))
        fh.write(blob)
print("[DXAPP] [INFO] wrote %s: %d x 4-d" % (args.out, len(imgs)))
'''

MODEL = "osnet_x0_25_256x128"


@pytest.fixture(autouse=True)
def _npu_free():
    npu_jobs._reset()
    yield
    npu_jobs._reset()


@pytest.fixture
def studio(tmp_path, monkeypatch):
    root = tmp_path / "dx_app"
    (root / "scripts").mkdir(parents=True)
    (root / "scripts" / "build_gallery_database.py").write_text(FAKE_SCRIPT, encoding="utf-8")
    people = root / "sample" / "gallery" / "staff"
    for who, n in (("alice", 2), ("bob", 1)):
        (people / who).mkdir(parents=True)
        for i in range(n):
            (people / who / f"{i}.jpg").write_bytes(b"\xff\xd8")
    (root / "sample" / "gallery" / "empty").mkdir()
    (root / "sample" / "img").mkdir()
    (root / "sample" / "img" / "a.jpg").write_bytes(b"\xff\xd8")
    (root / "assets").mkdir()
    (tmp_path / "outside").mkdir()
    (tmp_path / "outside" / "x.jpg").write_bytes(b"\xff\xd8")
    models = tmp_path / "models"
    models.mkdir()
    (models / f"{MODEL}.dxnn").write_bytes(b"DXNN")
    for name, value in (("DX_APP_ROOT", root), ("SAMPLE_DIR", root / "sample"), ("ASSETS_DIR", root / "assets"),
                        ("OUTPUTS_DIR", tmp_path / "outputs")):
        monkeypatch.setattr(config, name, value)
    from dx_app.core import graph_cli
    monkeypatch.setattr(graph_cli, "models_dir", lambda: models)
    monkeypatch.setattr(graph_gallery, "_python", lambda: sys.executable)
    calls = tmp_path / "calls.jsonl"
    monkeypatch.setenv("FAKE_CALLS", str(calls))
    return {"tmp": tmp_path, "root": root, "calls": calls, "models": models}


def _build(*args, **kw):
    """Start a build and poll it to its end: (the last poll, 200), or the start's refusal (body, status)."""
    body, code = graph_gallery.start(*args, **kw)
    if code != 200:
        return body, code
    end = time.time() + 20
    while time.time() < end:
        p, c = graph_gallery.poll(body["job_id"])
        assert c == 200, p
        if p["state"] != "running":
            return p, c
        time.sleep(0.05)
    raise AssertionError("the build did not end")


def _calls(studio):
    p = studio["calls"]
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def test_a_folder_of_people_becomes_a_gallery_file(studio):
    body, code = _build("sample/gallery/staff", MODEL)
    assert (code, body["state"]) == (200, "done"), body
    out = Path(body["path"])
    assert out == Path(config.OUTPUTS_DIR) / "graph" / "galleries" / f"staff_{MODEL}.bin"
    assert out.read_bytes()[:8] == b"DXGAL1\0\0"
    assert body["gallery"] == str(out), "the value the gallery op's `gallery` param takes"
    assert body["url"] == f"/outputs/graph/galleries/staff_{MODEL}.bin"
    assert (body["images"], body["people"], body["names"], body["dim"], body["model"]) == \
        (3, 2, ["alice", "bob"], 4, MODEL)
    argv = _calls(studio)[-1]["argv"]
    assert _calls(studio)[-1]["python"] == sys.executable
    assert argv[0].endswith("scripts/build_gallery_database.py")
    assert argv[argv.index("--variant") + 1] == MODEL
    staged = Path(argv[argv.index("--images") + 1])
    assert staged.name == "staff" and not staged.is_relative_to(studio["root"]), "a staged copy of the vetted files"
    assert not staged.exists(), "the staged folder is removed after the build"
    assert argv[argv.index("--models-dir") + 1] == str(studio["models"])
    assert npu_jobs.busy() is None
    assert [p.name for p in out.parent.iterdir()] == [out.name], "no temporary file is left"


def test_one_folder_without_people_names_each_image_after_its_file(studio):
    body, code = _build("sample/img", MODEL, name="desk")
    assert body["state"] == "done" and body["path"].endswith("/desk.bin")
    assert (body["images"], body["people"], body["names"]) == (1, 1, ["a"])


@pytest.mark.parametrize("folder", ["../outside", str(Path("/etc")), "sample/gallery/../../../outside",
                                    "sample/gallery/none", "sample/img/a.jpg", "", None, 3])
def test_only_folders_under_the_input_roots(studio, folder):
    body, code = _build(folder, MODEL)
    assert (code, body["error_key"]) == (400, "invalid_folder"), body
    assert _calls(studio) == []


def test_an_absolute_folder_outside_the_roots_is_refused(studio):
    body, code = _build(str(studio["tmp"] / "outside"), MODEL)
    assert (code, body["error_key"]) == (400, "invalid_folder")


def test_an_empty_folder_is_refused(studio):
    body, code = _build("sample/gallery/empty", MODEL)
    assert (code, body["error_key"]) == (400, "gallery_no_images") and _calls(studio) == []


@pytest.mark.parametrize("model, code, key", [("../osnet", 400, "invalid_model"), ("a b", 400, "invalid_model"),
                                              ("", 400, "invalid_model"), (None, 400, "invalid_model"),
                                              ("resnet50", 409, "model_missing")])
def test_the_model_must_be_an_installed_model_name(studio, model, code, key):
    body, got = _build("sample/gallery/staff", model)
    assert (got, body["error_key"]) == (code, key) and _calls(studio) == []


@pytest.mark.parametrize("name", ["../x", "a/b", "x" * 65, ".hidden", 5])
def test_the_output_name_is_a_plain_file_name(studio, name):
    body, code = _build("sample/gallery/staff", MODEL, name=name)
    assert (code, body["error_key"]) == (400, "invalid_name")


def test_a_missing_script_or_runtime_is_said(studio, monkeypatch):
    (studio["root"] / "scripts" / "build_gallery_database.py").unlink()
    assert _build("sample/gallery/staff", MODEL)[0]["error_key"] == "gallery_script_missing"
    (studio["root"] / "scripts" / "build_gallery_database.py").write_text(FAKE_SCRIPT, encoding="utf-8")
    monkeypatch.setattr(graph_gallery, "_python", lambda: None)
    body, code = _build("sample/gallery/staff", MODEL)
    assert (code, body["error_key"]) == (409, "runtime_python_missing")


def test_a_failed_build_reports_the_script_s_error_and_leaves_no_file(studio, monkeypatch):
    monkeypatch.setenv("FAKE_FAIL", "1")
    body, code = _build("sample/gallery/staff", MODEL)
    assert (body["state"], body["error_key"]) == ("failed", "gallery_build_failed")
    assert "no example found" in body["error"] and "no example found" in body["log_tail"]
    assert not (Path(config.OUTPUTS_DIR) / "graph" / "galleries").exists() or \
        list((Path(config.OUTPUTS_DIR) / "graph" / "galleries").iterdir()) == []
    assert npu_jobs.busy() is None


def test_a_build_that_takes_too_long_is_stopped(studio, monkeypatch):
    monkeypatch.setenv("FAKE_SLEEP", "30")
    monkeypatch.setattr(graph_gallery, "_TIMEOUT", 0.5)
    t0 = time.time()
    body, code = _build("sample/gallery/staff", MODEL)
    assert (body["state"], body["error_key"]) == ("failed", "gallery_timeout") and time.time() - t0 < 10
    assert npu_jobs.busy() is None


def test_the_build_holds_the_npu(studio, monkeypatch):
    npu_jobs.acquire("graph_live", "a-live")
    body, code = _build("sample/gallery/staff", MODEL)
    assert (code, body["error_key"]) == (409, "graph_live_busy") and _calls(studio) == []
    npu_jobs.release("a-live")

    monkeypatch.setenv("FAKE_SLEEP", "1.5")
    body, code = graph_gallery.start("sample/gallery/staff", MODEL)
    assert code == 200 and npu_jobs.busy()["kind"] == "gallery"
    from tests.dx_app import graph_fakes
    graph_fakes.install(studio["tmp"], monkeypatch, "exit 0")
    run = graph_run.start({"nodes": [{"id": "cam", "type": "source", "uri": "sample/img/a.jpg"}], "edges": []})
    assert (run[1], run[0]["error_key"]) == (409, "gallery_busy")
    assert graph_gallery.start("sample/gallery/staff", MODEL)[0]["error_key"] == "gallery_busy"
    end = time.time() + 10
    while graph_gallery.poll(body["job_id"])[0]["state"] == "running" and time.time() < end:
        time.sleep(0.05)
    assert graph_gallery.poll(body["job_id"])[0]["state"] == "done" and npu_jobs.busy() is None


def test_the_others_name_a_gallery_build_when_it_holds_the_npu():
    from dx_app.core import graph_live, live
    assert graph_run._BUSY["gallery"]["error_key"] == "gallery_busy"
    assert graph_live._BUSY["gallery"]["error_key"] == "gallery_busy"
    assert live._BUSY["gallery"][0] == "gallery_busy"


def test_stop_all_ends_a_build(studio, monkeypatch):
    monkeypatch.setenv("FAKE_SLEEP", "30")
    jid = graph_gallery.start("sample/gallery/staff", MODEL)[0]["job_id"]
    end = time.time() + 5
    while not _calls(studio) and time.time() < end:
        time.sleep(0.02)
    graph_gallery.stop_all()
    end = time.time() + 10
    while graph_gallery.poll(jid)[0]["state"] == "running" and time.time() < end:
        time.sleep(0.05)
    p = graph_gallery.poll(jid)[0]
    assert (p["state"], p["error_key"]) == ("failed", "gallery_stopped") and npu_jobs.busy() is None


# The build is a job: start answers at once, the page polls it and may stop it.

def test_start_answers_at_once_and_the_poll_follows_the_build(studio, monkeypatch):
    monkeypatch.setenv("FAKE_SLEEP", "1")
    t0 = time.time()
    body, code = graph_gallery.start("sample/gallery/staff", MODEL)
    assert code == 200 and time.time() - t0 < 1 and set(body) == {"job_id", "status", "images"}
    assert (body["status"], body["images"]) == ("started", 3)
    p, c = graph_gallery.poll(body["job_id"])
    assert (c, p["state"], p["job_id"]) == (200, "running", body["job_id"]) and p["elapsed"] >= 0
    end = time.time() + 10
    while p["state"] == "running" and time.time() < end:
        time.sleep(0.05)
        p = graph_gallery.poll(body["job_id"])[0]
    assert p["state"] == "done" and (p["images"], p["people"]) == (3, 2) and p["url"].endswith(".bin")
    assert graph_gallery.poll(body["job_id"])[0]["state"] == "done", "a finished build can be polled again"


def test_stop_ends_a_build_and_gives_the_npu_back(studio, monkeypatch):
    monkeypatch.setenv("FAKE_SLEEP", "30")
    jid = graph_gallery.start("sample/gallery/staff", MODEL)[0]["job_id"]
    assert graph_gallery.stop(jid) == {"status": "stopping"}
    end = time.time() + 10
    while graph_gallery.poll(jid)[0]["state"] == "running" and time.time() < end:
        time.sleep(0.05)
    p = graph_gallery.poll(jid)[0]
    assert (p["state"], p["error_key"]) == ("failed", "gallery_stopped") and npu_jobs.busy() is None
    assert not (Path(config.OUTPUTS_DIR) / "graph" / "galleries").exists() or \
        list((Path(config.OUTPUTS_DIR) / "graph" / "galleries").iterdir()) == []
    assert graph_gallery.stop(jid) == {"status": "no_process"}
    assert graph_gallery.stop("nope") == {"status": "no_process"}


def test_an_unknown_build_says_so(studio):
    assert graph_gallery.poll("nope") == ({"error": "unknown_job", "error_key": "unknown_job"}, 404)
    assert graph_gallery.poll(None)[1] == 404


def test_the_builder_reads_no_terminal_input(studio, monkeypatch):
    seen = {}
    real = graph_gallery.subprocess.Popen

    def spy(cmd, *a, **k):
        seen.update(k)
        return real(cmd, *a, **k)
    monkeypatch.setattr(graph_gallery.subprocess, "Popen", spy)
    assert _build("sample/gallery/staff", MODEL)[0]["state"] == "done"
    assert seen["stdin"] == graph_gallery.subprocess.DEVNULL


# The folder is listed by Studio: only files under the input roots reach the builder.

def test_a_symlink_out_of_the_input_roots_is_left_out(studio):
    staff = studio["root"] / "sample" / "gallery" / "staff"
    (staff / "carol").mkdir()
    (staff / "carol" / "x.jpg").symlink_to(studio["tmp"] / "outside" / "x.jpg")
    (staff / "bob" / "desk.jpg").symlink_to(studio["root"] / "sample" / "img" / "a.jpg")
    (staff / "eve").symlink_to(studio["tmp"] / "outside", target_is_directory=True)
    body, code = graph_gallery.start("sample/gallery/staff", MODEL)
    assert (code, body["images"]) == (200, 4), "alice 2, bob 1 + a link inside the roots; not carol's or eve's"
    end = time.time() + 10
    while (p := graph_gallery.poll(body["job_id"])[0])["state"] == "running" and time.time() < end:
        time.sleep(0.05)
    assert (p["images"], p["names"]) == (4, ["alice", "bob"])


def test_a_folder_of_only_outside_links_has_no_images(studio):
    d = studio["root"] / "sample" / "gallery" / "links"
    d.mkdir()
    (d / "x.jpg").symlink_to(studio["tmp"] / "outside" / "x.jpg")
    body, code = graph_gallery.start("sample/gallery/links", MODEL)
    assert (code, body["error_key"]) == (400, "gallery_no_images") and _calls(studio) == []


def test_a_folder_too_large_to_list_is_refused_without_walking_it_all(studio, monkeypatch):
    monkeypatch.setattr(graph_gallery, "MAX_ENTRIES", 5)
    visited = []
    real = graph_gallery.os.walk

    def walk(top, **kw):
        for entry in real(top, **kw):
            visited.append(entry)
            yield entry
    monkeypatch.setattr(graph_gallery.os, "walk", walk)
    for i in range(20):
        (studio["root"] / "sample" / "img" / f"n{i}.txt").write_text("x")
    body, code = graph_gallery.start(".", MODEL)
    assert (code, body["error_key"]) == (400, "gallery_folder_too_large") and _calls(studio) == []
    assert len(visited) < sum(1 for _ in real(studio["root"])), "the walk stops at the cap"


def test_the_file_header_is_read_back(tmp_path):
    p = tmp_path / "g.bin"
    blobs = [b"m", b"x/1.jpg\ny/2.jpg\nz/2.jpg", b"ann\n\n"]
    p.write_bytes(b"DXGAL1\0\0" + struct.pack("<II", 3, 8) + b"\0" * 96
                  + b"".join(struct.pack("<I", len(b)) + b for b in blobs))
    assert graph_gallery.read_summary(p) == {"images": 3, "dim": 8, "model": "m", "people": 2, "names": ["2", "ann"]}
    p.write_bytes(b"NOTGAL")
    assert graph_gallery.read_summary(p) is None


def test_the_builder_runs_in_the_dx_rt_runtime_python(monkeypatch):
    monkeypatch.setattr(config, "_RUNTIME_PYTHON", "/opt/venv-dx-runtime/bin/python3", raising=False)
    monkeypatch.setattr(config, "_RUNTIME_PYTHONPATH", "/opt/dx_engine", raising=False)
    assert graph_gallery._python() == "/opt/venv-dx-runtime/bin/python3"
    assert graph_gallery._env()["PYTHONPATH"].split(":")[0] == "/opt/dx_engine"
