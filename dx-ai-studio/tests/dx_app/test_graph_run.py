"""graph_run: one run of a graph through a fake runner that prints recorded progress and writes a recorded report."""
from __future__ import annotations

import base64
import json
import time

import pytest

from dx_app.core import config, graph_run
from tests.dx_app import graph_fakes

# Writes what the real runner writes: [PROGRESS] lines, --report, --output. Arguments go to the log too.
RUNNER = r"""
out=""; rep=""
while [ $# -gt 0 ]; do
  case "$1" in
    --output) out="$2"; shift 2 ;;
    --report) rep="$2"; shift 2 ;;
    *) echo "arg $1"; shift ;;
  esac
done
if [ -n "$SLEEP" ]; then trap 'echo stopped; exit 0' TERM; sleep "$SLEEP" & wait; fi
cat "$FIX/run_progress.log"
cp "$FIX/report.json" "$rep"
printf 'img' > "$out"
exit 0
"""

FAILING = r"""
echo 'ERROR [MODEL_LOAD] node "attr": model "deepmar_resnet50_224x224" (deepmar_resnet50_224x224.dxnn) could not be loaded: [dxrt-exception] Invalid model exception'
echo '  -> the NPU device memory may be full'
exit 1
"""

GRAPH = {"version": 1, "name": "person-attributes",
         "nodes": [{"id": "cam", "type": "source", "uri": "sample/img/sample_people.jpg"},
                   {"id": "od", "model": "yolov8-n_640x640"}, {"id": "attr", "model": "deepmar_resnet50_224x224"}],
         "edges": [{"from": "cam", "to": "od"}, {"from": "od", "to": "attr", "roi": {"classes": ["person"]}}]}
PNG = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\0" * 32).decode()


@pytest.fixture
def studio(tmp_path, monkeypatch):
    """dx_app root with one sample image, outputs in tmp_path, no jobs left from other tests."""
    root, out = tmp_path / "dx_app", tmp_path / "outputs"
    (root / "sample" / "img").mkdir(parents=True)
    (root / "sample" / "img" / "sample_people.jpg").write_bytes(b"\xff\xd8jpg")
    (root / "assets").mkdir()
    out.mkdir()
    for name, value in (("DX_APP_ROOT", root), ("SAMPLE_DIR", root / "sample"), ("ASSETS_DIR", root / "assets"),
                        ("OUTPUTS_DIR", out)):
        monkeypatch.setattr(config, name, value)
    graph_run._jobs.clear()
    yield tmp_path
    for job in list(graph_run._jobs.values()):
        if job["proc"].poll() is None:
            job["proc"].kill()
    graph_run._jobs.clear()


def _wait(job_id, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        p = graph_run.poll(job_id)
        if p["has_result"]:
            return p
        time.sleep(0.05)
    raise AssertionError("the run did not finish")


def test_progress_lines_carry_fps_and_per_node_time():
    p = graph_run.parse_progress_line("[PROGRESS] frames=2 fps=14.7 avg_fps=14.7 node_ms=od:10.2,attr:5.9")
    assert p == {"frames": 2.0, "fps": 14.7, "avg_fps": 14.7, "node_ms": {"od": 10.2, "attr": 5.9}}
    assert graph_run.parse_progress_line("[DET] 3 objects") is None
    assert graph_run.parse_progress_line("[PROGRESS] frames=1 node_ms=my%20node:1.5")["node_ms"] == {"my node": 1.5}


def test_the_report_becomes_per_node_results():
    s = graph_run.summarize_report(graph_fakes.FIX / "report.json")
    assert (s["frames"], s["error_frames"]) == (2, 0)
    assert s["node_ms"] == {"attr": 6.0, "od": 10.0}
    od, attr = s["nodes"]["od"], s["nodes"]["attr"]
    assert (od["shape"], od["frames"], od["items_total"]) == ("boxes", 2, 3)
    assert od["last_items"] == [{"class_name": "person", "class_id": 0, "score": 0.9, "track_id": 3,
                                 "box": [414.0, 156.0, 118.0, 309.0]}]
    assert (attr["shape"], attr["crops_total"]) == ("scores", 3)
    assert attr["last_items"][0]["top"]["class_name"] == "upper_short_sleeve"


def test_a_run_reports_progress_then_results(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    body, code = graph_run.start(GRAPH)
    assert code == 200, body
    p = _wait(body["job_id"])
    assert p["frames"] == 2 and p["node_ms"] == {"od": 10.2, "attr": 5.9}
    r = graph_run.result(body["job_id"])
    assert r["ok"] is True and r["exit_code"] == 0 and r["frames"] == 2
    assert r["node_ms"] == {"attr": 6.0, "od": 10.0}
    assert r["outputs"][0]["url"].startswith("/outputs/graph/runs/") and r["outputs"][0]["kind"] == "image"
    assert graph_run.result(body["job_id"]) == {"error": "unknown_job"}, "a result is handed out once"
    args = graph_fakes.calls(studio)[-1]
    assert "--input cam=" in args and "sample_people.jpg" in args and "--model-dir" in args
    run_graph = json.loads((config.OUTPUTS_DIR / "graph" / "runs" / body["job_id"] / "graph.json").read_text())
    assert run_graph["nodes"][1] == {"id": "od", "model": "yolov8-n_640x640"}


def test_report_timing_is_asked_for_when_the_build_has_it(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch,
                        'if [ "$1" = "--help" ]; then echo "  --report-timing  with --report"; exit 0; fi\n' + RUNNER)
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"])
    assert "--report-timing" in graph_fakes.calls(studio)[-1]


def test_an_uploaded_image_replaces_the_source(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    body, code = graph_run.start(GRAPH, uploads={"cam": "data:image/png;base64," + PNG})
    assert code == 200
    _wait(body["job_id"])
    assert "input_cam.png" in graph_fakes.calls(studio)[-1]


def test_async_options_reach_the_runner(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    body, _ = graph_run.start(GRAPH, variant="async", max_inflight=4, frames=10)
    _wait(body["job_id"])
    args = graph_fakes.calls(studio)[-1]
    assert "--max-inflight 4" in args and "--frames 10" in args


@pytest.mark.parametrize("inputs, key", [
    ({"cam": "camera:0"}, "live_source"),
    ({"cam": "rtsp://10.0.0.2/stream"}, "live_source"),
    ({"cam": "/etc/passwd"}, "invalid_input"),
    ({"cam": "sample/img/missing.jpg"}, "invalid_input"),
])
def test_inputs_outside_run_once_are_refused(studio, monkeypatch, inputs, key):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    body, code = graph_run.start(GRAPH, inputs=inputs)
    assert code == 400 and body["error_key"] == key
    assert graph_fakes.calls(studio) == [] or "--graph" not in graph_fakes.calls(studio)[-1]


def test_bad_options_are_refused(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    assert graph_run.start(GRAPH, variant="turbo")[1] == 400
    assert graph_run.start(GRAPH, max_inflight=0)[1] == 400
    assert graph_run.start(GRAPH, uploads={"cam": "bm90IGFuIGltYWdl"})[1] == 400      # "not an image"
    assert graph_run.start({"nodes": [{"id": "od", "model": "m"}], "edges": []})[0]["error_key"] == "no_source"


def test_one_run_at_a_time_and_stop_finishes_it(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, "SLEEP=30\n" + RUNNER)
    body, code = graph_run.start(GRAPH)
    assert code == 200
    second, code2 = graph_run.start(GRAPH)
    assert code2 == 409 and second["error_key"] == "graph_run_busy"
    time.sleep(0.3)
    assert graph_run.stop(body["job_id"]) == {"status": "stopping"}
    p = _wait(body["job_id"])
    assert p["running"] is False


def test_a_failed_load_pins_the_error_to_its_node(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, FAILING)
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"])
    r = graph_run.result(body["job_id"])
    assert r["ok"] is False and r["exit_code"] == 1
    assert (r["errors"][0]["code"], r["errors"][0]["node"]) == ("MODEL_LOAD", "attr")


def test_old_run_folders_are_pruned(studio):
    runs = graph_run.runs_dir()
    for i in range(25):
        (runs / f"old{i:02d}").mkdir()
    graph_run._prune_runs(keep=20)
    assert len(list(runs.iterdir())) == 20
