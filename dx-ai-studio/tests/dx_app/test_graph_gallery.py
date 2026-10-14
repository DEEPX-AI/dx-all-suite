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


def _calls(studio):
    p = studio["calls"]
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def test_a_folder_of_people_becomes_a_gallery_file(studio):
    body, code = graph_gallery.build("sample/gallery/staff", MODEL)
    assert code == 200, body
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
    assert argv[argv.index("--images") + 1] == str(studio["root"] / "sample" / "gallery" / "staff")
    assert argv[argv.index("--models-dir") + 1] == str(studio["models"])
    assert npu_jobs.busy() is None
    assert [p.name for p in out.parent.iterdir()] == [out.name], "no temporary file is left"


def test_one_folder_without_people_names_each_image_after_its_file(studio):
    body, code = graph_gallery.build("sample/img", MODEL, name="desk")
    assert code == 200 and body["path"].endswith("/desk.bin")
    assert (body["images"], body["people"], body["names"]) == (1, 1, ["a"])


@pytest.mark.parametrize("folder", ["../outside", str(Path("/etc")), "sample/gallery/../../../outside",
                                    "sample/gallery/none", "sample/img/a.jpg", "", None, 3])
def test_only_folders_under_the_input_roots(studio, folder):
    body, code = graph_gallery.build(folder, MODEL)
    assert (code, body["error_key"]) == (400, "invalid_folder"), body
    assert _calls(studio) == []


def test_an_absolute_folder_outside_the_roots_is_refused(studio):
    body, code = graph_gallery.build(str(studio["tmp"] / "outside"), MODEL)
    assert (code, body["error_key"]) == (400, "invalid_folder")


def test_an_empty_folder_is_refused(studio):
    body, code = graph_gallery.build("sample/gallery/empty", MODEL)
    assert (code, body["error_key"]) == (400, "gallery_no_images") and _calls(studio) == []


@pytest.mark.parametrize("model, code, key", [("../osnet", 400, "invalid_model"), ("a b", 400, "invalid_model"),
                                              ("", 400, "invalid_model"), (None, 400, "invalid_model"),
                                              ("resnet50", 409, "model_missing")])
def test_the_model_must_be_an_installed_model_name(studio, model, code, key):
    body, got = graph_gallery.build("sample/gallery/staff", model)
    assert (got, body["error_key"]) == (code, key) and _calls(studio) == []


@pytest.mark.parametrize("name", ["../x", "a/b", "x" * 65, ".hidden", 5])
def test_the_output_name_is_a_plain_file_name(studio, name):
    body, code = graph_gallery.build("sample/gallery/staff", MODEL, name=name)
    assert (code, body["error_key"]) == (400, "invalid_name")


def test_a_missing_script_or_runtime_is_said(studio, monkeypatch):
    (studio["root"] / "scripts" / "build_gallery_database.py").unlink()
    assert graph_gallery.build("sample/gallery/staff", MODEL)[0]["error_key"] == "gallery_script_missing"
    (studio["root"] / "scripts" / "build_gallery_database.py").write_text(FAKE_SCRIPT, encoding="utf-8")
    monkeypatch.setattr(graph_gallery, "_python", lambda: None)
    body, code = graph_gallery.build("sample/gallery/staff", MODEL)
    assert (code, body["error_key"]) == (409, "runtime_python_missing")


def test_a_failed_build_reports_the_script_s_error_and_leaves_no_file(studio, monkeypatch):
    monkeypatch.setenv("FAKE_FAIL", "1")
    body, code = graph_gallery.build("sample/gallery/staff", MODEL)
    assert (code, body["error_key"]) == (422, "gallery_build_failed")
    assert "no example found" in body["error"] and "no example found" in body["log_tail"]
    assert not (Path(config.OUTPUTS_DIR) / "graph" / "galleries").exists() or \
        list((Path(config.OUTPUTS_DIR) / "graph" / "galleries").iterdir()) == []
    assert npu_jobs.busy() is None


def test_a_build_that_takes_too_long_is_stopped(studio, monkeypatch):
    monkeypatch.setenv("FAKE_SLEEP", "30")
    monkeypatch.setattr(graph_gallery, "_TIMEOUT", 0.5)
    t0 = time.time()
    body, code = graph_gallery.build("sample/gallery/staff", MODEL)
    assert (code, body["error_key"]) == (504, "gallery_timeout") and time.time() - t0 < 10
    assert npu_jobs.busy() is None


def test_the_build_holds_the_npu(studio, monkeypatch):
    npu_jobs.acquire("graph_live", "a-live")
    body, code = graph_gallery.build("sample/gallery/staff", MODEL)
    assert (code, body["error_key"]) == (409, "graph_live_busy") and _calls(studio) == []
    npu_jobs.release("a-live")

    monkeypatch.setenv("FAKE_SLEEP", "1.5")
    done = {}
    t = threading.Thread(target=lambda: done.update(r=graph_gallery.build("sample/gallery/staff", MODEL)))
    t.start()
    end = time.time() + 5
    while not npu_jobs.held_by("gallery") and time.time() < end:
        time.sleep(0.02)
    assert npu_jobs.busy()["kind"] == "gallery"
    from tests.dx_app import graph_fakes
    graph_fakes.install(studio["tmp"], monkeypatch, "exit 0")
    run = graph_run.start({"nodes": [{"id": "cam", "type": "source", "uri": "sample/img/a.jpg"}], "edges": []})
    assert (run[1], run[0]["error_key"]) == (409, "gallery_busy")
    assert graph_gallery.build("sample/gallery/staff", MODEL)[0]["error_key"] == "gallery_busy"
    t.join(10)
    assert done["r"][1] == 200 and npu_jobs.busy() is None


def test_the_others_name_a_gallery_build_when_it_holds_the_npu():
    from dx_app.core import graph_live, live
    assert graph_run._BUSY["gallery"]["error_key"] == "gallery_busy"
    assert graph_live._BUSY["gallery"]["error_key"] == "gallery_busy"
    assert live._BUSY["gallery"][0] == "gallery_busy"


def test_stop_all_ends_a_build(studio, monkeypatch):
    monkeypatch.setenv("FAKE_SLEEP", "30")
    done = {}
    t = threading.Thread(target=lambda: done.update(r=graph_gallery.build("sample/gallery/staff", MODEL)))
    t.start()
    end = time.time() + 5
    while not _calls(studio) and time.time() < end:
        time.sleep(0.02)
    graph_gallery.stop_all()
    t.join(10)
    assert done["r"][1] == 422 and npu_jobs.busy() is None


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
