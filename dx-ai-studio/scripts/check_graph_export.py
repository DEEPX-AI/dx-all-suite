"""Outside-suite check of a Graph Composer export (Phase 3; spec §12 and §14): export through Studio, build and run the
project where nothing of the suite can be seen, and compare it with Studio's own run of the same graph.

    .venv/bin/python -m scripts.check_graph_export [--npu] [--keep] [--work DIR]

  1. export   dx_app.core.graph_export.export() of CHECK_GRAPH (zone intrusion with a User logic block between the
              person filter and the zone), into DIR/outputs instead of the Studio's outputs folder
  2. unzip    the zip into DIR/unzipped; DIR must lie outside the suite (default /dev/shm/gc-export-check) and no text
              file of the project may name the suite's path
  3. build    setup.sh with a clean environment (PATH=/usr/local/bin:/usr/bin:/bin, HOME, LANG): the DEEPX runtime,
              CMake, a compiler and OpenCV, nothing else; the program may not name the suite's path either
  4. compare  (--npu) run.sh, then Studio's own run of CHECK_GRAPH (graph_run, the sync executor): the same events, and
              result images within a mean difference of 0.5 per channel
Prints "PASS <step>" per step and "RESULT: PASS" (exit 0); on a failure "FAIL <step>: <why>" and "RESULT: FAIL" (exit
1). "RESULT: SKIP <why>" (exit 0) when the dx_app build cannot export or yolov8-n_640x640.dxnn is not downloaded.
DIR is removed at the end unless --keep. Contract: tests/dx_app/test_graph_export_outside.py
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dx_app.core import config, graph_cli, graph_export, graph_run  # noqa: E402
from shared.paths import SUITE_ROOT  # noqa: E402

NAME = "check-user-zone"
PROGRAM = "check_user_zone"
CHECK_GRAPH = {
    "version": 1, "name": "check-user-zone",
    "nodes": [
        {"id": "cam", "type": "source", "uri": "sample/img/sample_people.jpg"},
        {"id": "od", "model": "yolov8-n_640x640", "params": {"score_threshold": 0.35},
         "track": {"algo": "iou", "iou": 0.3, "max_age": 30}},
        {"id": "person", "type": "logic", "op": "filter", "params": {"classes": ["person"]}},
        {"id": "tag", "type": "logic", "op": "user",
         "params": {"name": "tag_people", "input": "boxes", "output": "boxes"}},
        {"id": "zone", "type": "logic", "op": "zone",
         "params": {"polygon": [0.45, 0.35, 1.0, 0.35, 1.0, 1.0, 0.45, 1.0]}},
        {"id": "alarm", "type": "logic", "op": "condition",
         "params": {"value": "count", "comparator": ">", "threshold": 0, "cooldown_s": 10, "event": "intrusion"}},
    ],
    "edges": [
        {"from": "cam", "to": "od"},
        {"from": "od", "to": "person", "carry": "result"},
        {"from": "person", "to": "tag", "carry": "result"},
        {"from": "tag", "to": "zone", "carry": "result"},
        {"from": "zone", "to": "alarm", "carry": "result"},
    ],
}
CLEAN_ENV = {"HOME": os.environ.get("HOME", "/tmp"), "PATH": "/usr/local/bin:/usr/bin:/bin", "LANG": "C.UTF-8",
             "QT_QPA_PLATFORM": "offscreen"}
BINARY_EXT = (".dxnn", ".bin", ".onnx", ".jpg", ".jpeg", ".png", ".bmp", ".webp", ".mp4", ".mov", ".avi", ".mkv",
              ".webm")


class Failed(Exception):
    """A step that did not pass; the text says why."""


def leaks(folder: Path, needle: str) -> list:
    """The text files under `folder` that contain `needle`, as sorted relative paths."""
    hits = []
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.suffix.lower() not in BINARY_EXT and needle.encode() in p.read_bytes():
            hits.append(p.relative_to(folder).as_posix())
    return hits


def unzip(zip_path: Path, dest: Path) -> None:
    """Extracts `zip_path` into `dest`, keeping each file's mode; an entry that would land outside `dest` fails."""
    dest.mkdir(parents=True, exist_ok=True)
    dest = dest.resolve()
    with zipfile.ZipFile(zip_path) as z:
        for info in z.infolist():
            target = (dest / info.filename).resolve()
            if dest not in target.parents:
                raise Failed(f"the zip entry {info.filename} would land outside {dest}")
        for info in z.infolist():
            z.extract(info, dest)
            mode = (info.external_attr >> 16) & 0o777
            if mode:
                os.chmod(dest / info.filename, mode)


def outside_suite(path: Path) -> bool:
    real, suite = Path(path).resolve(), SUITE_ROOT.resolve()
    return real != suite and suite not in real.parents


def _step(name: str, fn):
    try:
        out = fn()
    except Failed as e:
        print(f"FAIL {name}: {e}", flush=True)
        raise
    print(f"PASS {name}", flush=True)
    return out


def export_step(work: Path) -> dict:
    config.OUTPUTS_DIR = work / "outputs"
    body, code = graph_export.export(CHECK_GRAPH, NAME, include_models=True)   # offline build: the models go in
    if code != 200:
        raise Failed(f"{code} {body.get('error_key')}: {body.get('error')}")
    return body


def unzip_step(body: dict, work: Path) -> Path:
    zip_path = Path(config.OUTPUTS_DIR) / body["zip_url"][len("/outputs/"):]
    unzip(zip_path, work / "unzipped")
    project = work / "unzipped" / NAME
    found = leaks(project, str(SUITE_ROOT))
    if found:
        raise Failed("these files name the suite's path: " + ", ".join(found))
    return project


def build_step(project: Path) -> Path:
    r = subprocess.run(["bash", "setup.sh"], cwd=str(project), env=CLEAN_ENV, capture_output=True, text=True,
                       timeout=1800)
    if r.returncode != 0:
        raise Failed((r.stdout + r.stderr)[-2000:])
    program = project / "build" / PROGRAM
    if not program.is_file():
        raise Failed(f"{program} was not built")
    if str(SUITE_ROOT).encode() in program.read_bytes():
        raise Failed("the program names the suite's path")
    return program


def _events(path: Path) -> list:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def compare_step(project: Path) -> None:
    r = subprocess.run(["bash", "run.sh"], cwd=str(project), env=CLEAN_ENV, capture_output=True, text=True,
                       timeout=600)
    if r.returncode != 0:
        raise Failed("run.sh: " + (r.stdout + r.stderr)[-2000:])
    started, code = graph_run.start(CHECK_GRAPH)
    if code != 200:
        raise Failed(f"Studio's run did not start: {started.get('error')}")
    result = graph_run.wait(started["job_id"], 300)
    if not result.get("ok"):
        raise Failed("Studio's run failed: " + str(result.get("log_tail") or result.get("errors"))[-1000:])
    run_dir = graph_run.runs_dir() / started["job_id"]
    ours, theirs = _events(project / "results" / "events.jsonl"), _events(run_dir / "events.jsonl")
    if not ours or ours != theirs:
        raise Failed(f"the events differ: export {ours} / Studio {theirs}")
    from PIL import Image, ImageChops, ImageStat
    a = Image.open(project / "results" / "result.jpg").convert("RGB")
    b = Image.open(run_dir / "result.jpg").convert("RGB")
    if a.size != b.size:
        raise Failed(f"the result images differ in size: {a.size} / {b.size}")
    mean = sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3
    if mean > 0.5:
        raise Failed(f"the result images differ: mean difference {mean:.2f} per channel")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Build and run a Graph Composer export outside the suite.")
    ap.add_argument("--work", default="/dev/shm/gc-export-check", help="a folder outside the suite (removed after)")
    ap.add_argument("--npu", action="store_true", help="also run it on the NPU and compare with Studio's run")
    ap.add_argument("--keep", action="store_true", help="keep the work folder")
    args = ap.parse_args(argv)
    work = Path(args.work)
    if not outside_suite(work):
        print(f"FAIL setup: --work {work} is inside the suite\nRESULT: FAIL")
        return 1
    if not graph_export.available():
        print("RESULT: SKIP this dx_app build has no scripts/export_graph_project.py")
        return 0
    model = graph_cli.models_dir() / "yolov8-n_640x640.dxnn"
    if not model.is_file() or model.stat().st_size == 0:
        print(f"RESULT: SKIP {model.name} is not downloaded")
        return 0
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)
    saved = config.OUTPUTS_DIR
    try:
        body = _step("export", lambda: export_step(work))
        project = _step("unzip outside the suite", lambda: unzip_step(body, work))
        _step("build with only the runtime", lambda: build_step(project))
        if args.npu:
            _step("same events and image as Studio's run", lambda: compare_step(project))
        print("RESULT: PASS")
        return 0
    except Failed:
        print("RESULT: FAIL")
        return 1
    finally:
        config.OUTPUTS_DIR = saved
        if not args.keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
