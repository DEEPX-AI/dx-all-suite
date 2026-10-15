"""graph_run: one run of a graph through a fake runner that prints recorded progress and writes a recorded report."""
from __future__ import annotations

import base64
import json
import threading
import time

import pytest

from dx_app.core import config, graph_run
from tests.dx_app import graph_fakes

@pytest.fixture(autouse=True)
def _npu_free():
    """No test inherits another's hold on the NPU (npu_jobs.py): a fake runner whose poll() never ends keeps it."""
    from dx_app.core import npu_jobs
    npu_jobs._reset()
    yield
    npu_jobs._reset()


# Writes what the real runner writes: [PROGRESS] lines, --report, --output. Arguments go to the log too.
RUNNER = r"""
case "$1" in --help|--check) exit 0 ;; esac     # capability probes answer at once, even in the slow fakes
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
        if job["proc"] is not None and job["proc"].poll() is None:
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
    assert graph_run.parse_progress_line("[PROGRESS] frames=1") == {"frames": 1.0, "node_ms": {}}, "the first line has no rate yet"


def test_the_report_becomes_per_node_results():
    s = graph_run.summarize_report(graph_fakes.FIX / "report.json")
    assert (s["frames"], s["error_frames"]) == (2, 0)
    assert s["node_ms"] == {"attr": 28.88, "od": 39.71}
    od, attr = s["nodes"]["od"], s["nodes"]["attr"]
    assert (od["shape"], od["frames"], od["items_total"]) == ("boxes", 2, 18)
    first = od["last_items"][0]
    assert (first["class_name"], first["class_id"], first["track_id"]) == ("person", 0, 2)
    assert [round(v) for v in first["box"]] == [316, 246, 330, 731] and round(first["score"], 2) == 0.91
    assert (attr["shape"], attr["crops_total"]) == ("scores", 16)
    assert attr["last_items"][0]["src_box"] == [299.0, 209.0, 362.0, 803.0]
    assert attr["last_items"][0]["top"]["class_name"] == "Long Lower"


def test_a_run_reports_progress_then_results(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    body, code = graph_run.start(GRAPH)
    assert code == 200, body
    p = _wait(body["job_id"])
    assert p["frames"] == 2 and p["node_ms"] == {"od": 39.71, "attr": 28.88}
    r = graph_run.result(body["job_id"])
    assert r["ok"] is True and r["exit_code"] == 0 and r["frames"] == 2
    assert r["node_ms"] == {"attr": 28.88, "od": 39.71}
    assert r["outputs"][0]["url"].startswith("/outputs/graph/runs/") and r["outputs"][0]["kind"] == "image"
    assert graph_run.result(body["job_id"]) == {"error": "unknown_job", "error_key": "unknown_job"}, \
        "a result is handed out once"
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



# Review fixes: one runner at a time even under parallel requests, safe input names, bounded runs, shutdown.

STUBBORN = r"""
case "$1" in --help|--check) exit 0 ;; esac
trap '' TERM
exec sleep 30
"""

NOISY = r"""
case "$1" in --help|--check) exit 0 ;; esac
trap 'exit 0' TERM
head -c 400000 /dev/zero | tr '\0' 'x'
sleep 30 & wait
"""


def _started(tmp_path):
    return [c for c in graph_fakes.calls(tmp_path) if "--graph" in c]


def test_two_parallel_starts_launch_one_runner(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, "SLEEP=30\n" + RUNNER)
    real_caps = graph_run.graph_cli.capabilities

    def slow_caps():
        time.sleep(0.3)                      # widen the window between the busy check and Popen
        return real_caps()
    monkeypatch.setattr(graph_run.graph_cli, "capabilities", slow_caps)
    barrier, codes = threading.Barrier(2), []

    def go():
        barrier.wait()
        try:
            codes.append(graph_run.start(GRAPH)[1])
        except Exception as e:          # surfaced by the assertion below
            codes.append(repr(e))
    threads = [threading.Thread(target=go) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(10)
    assert sorted(codes) == [200, 409]
    time.sleep(0.3)
    assert len(_started(studio)) == 1


def test_a_refused_start_frees_the_slot_and_its_folder(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    assert graph_run.start(GRAPH, inputs={"cam": "/etc/passwd"})[1] == 400
    with monkeypatch.context() as m:
        m.setattr(graph_run.subprocess, "Popen", lambda *a, **k: (_ for _ in ()).throw(OSError("no exec")))
        body, code = graph_run.start(GRAPH)
    assert (code, body["error_key"]) == (500, "graph_run_failed")
    assert graph_run._jobs == {} and list(graph_run.runs_dir().iterdir()) == []
    body, code = graph_run.start(GRAPH)
    assert code == 200
    _wait(body["job_id"])


def test_a_disk_error_while_preparing_is_a_clear_failure(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)

    def full(*_a):
        raise OSError(28, "No space left on device")
    monkeypatch.setattr(graph_run, "_write_upload", full)
    body, code = graph_run.start(GRAPH, uploads={"cam": "data:image/png;base64," + PNG})
    assert (code, body["error_key"]) == (500, "graph_run_failed") and "No space left" in body["error"]
    assert graph_run._jobs == {} and list(graph_run.runs_dir().iterdir()) == []


@pytest.mark.parametrize("sid", ["a/b", "x=y", "..", "", "a" * 65, "cam\nx"])
def test_source_ids_that_are_not_plain_names_are_refused(studio, monkeypatch, sid):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    g = json.loads(json.dumps(GRAPH))
    g["nodes"][0]["id"] = sid
    g["edges"][0]["from"] = sid
    body, code = graph_run.start(g, uploads={sid: "data:image/png;base64," + PNG})
    assert (code, body["error_key"]) == (400, "invalid_source_id")
    assert _started(studio) == [] and list(graph_run.runs_dir().iterdir()) == []
    assert not list(studio.rglob("input_*")), "no file is written for a refused id"


def test_a_five_megabyte_upload_is_accepted(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    big = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\0" * (5 * 1024 * 1024 * 3 // 4)).decode()
    body, code = graph_run.start(GRAPH, uploads={"cam": "data:image/png;base64," + big})
    assert code == 200, body
    _wait(body["job_id"])


def test_stop_kills_a_runner_that_ignores_sigterm(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, STUBBORN)
    monkeypatch.setattr(graph_run, "_STOP_GRACE", 0.3)
    body, _ = graph_run.start(GRAPH)
    time.sleep(0.2)
    assert graph_run.stop(body["job_id"]) == {"status": "stopping"}
    _wait(body["job_id"], timeout=5)
    assert graph_run.result(body["job_id"])["exit_code"] == -9


def test_a_run_is_stopped_at_the_time_limit(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, "SLEEP=30\n" + RUNNER)
    monkeypatch.setattr(graph_run, "_MAX_RUN_SECONDS", 0.5)
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"], timeout=6)
    r = graph_run.result(body["job_id"])
    assert r["ok"] is False and r["errors"][0]["code"] == "RUN_TIMEOUT"


def test_a_run_is_stopped_when_its_log_grows_too_large(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, NOISY)
    monkeypatch.setattr(graph_run, "_MAX_LOG_BYTES", 20000)
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"], timeout=6)
    r = graph_run.result(body["job_id"])
    assert r["ok"] is False and r["errors"][0]["code"] == "RUN_LOG_LIMIT"
    assert len(r["log_tail"]) <= 4000


def test_stop_all_ends_every_run(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, STUBBORN)
    monkeypatch.setattr(graph_run, "_STOP_GRACE", 0.3)
    body, _ = graph_run.start(GRAPH)
    proc = graph_run._jobs[body["job_id"]]["proc"]
    t0 = time.time()
    graph_run.stop_all()
    assert proc.poll() is not None and time.time() - t0 < 5


def test_poll_drops_runs_nobody_asked_about(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, "SLEEP=30\n" + RUNNER)
    body, _ = graph_run.start(GRAPH)
    job = graph_run._jobs[body["job_id"]]
    job["touched"] -= graph_run._JOB_TTL + 1
    assert graph_run.poll("someone-else") == {"error": "unknown_job", "error_key": "unknown_job"}
    assert body["job_id"] not in graph_run._jobs
    job["proc"].wait(5)


def test_the_watchdog_stops_graph_runs(monkeypatch):
    from dx_app import server
    calls = []
    monkeypatch.setattr(server, "stop_inference", lambda: None)
    monkeypatch.setattr(server, "shutdown_live_processes", lambda: None)
    monkeypatch.setattr(graph_run, "stop_all", lambda: calls.append(1))
    monkeypatch.setattr(server.time, "sleep", lambda _s: None)
    monkeypatch.setattr(server, "_HB_TIMEOUT", 1)
    monkeypatch.setattr(config, "_HEARTBEAT", time.time() - 10_000)

    class _Srv:
        def shutdown(self):
            pass
    t = threading.Thread(target=server._watchdog, args=(_Srv(),))
    t.start()
    t.join(5)
    assert calls == [1]



# Phase 1 follow-up: all uploads of one run stay under dx_app/server.py's JSON limit for /api/graph/run.

TWO_SOURCES = {"version": 1, "name": "two",
               "nodes": [{"id": "a", "type": "source", "uri": "sample/img/sample_people.jpg"},
                         {"id": "b", "type": "source", "uri": "sample/img/sample_people.jpg"},
                         {"id": "od", "model": "yolov8-n_640x640"}],
               "edges": [{"from": "a", "to": "od"}, {"from": "b", "to": "od"}]}


def test_uploads_that_add_up_past_the_limit_are_refused_before_anything_runs(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    half = "data:image/png;base64," + "A" * (graph_run.MAX_UPLOADS_TOTAL_B64 // 2 + 10)
    body, code = graph_run.start(TWO_SOURCES, uploads={"a": half, "b": half})
    assert (code, body["error_key"], body["limit_bytes"]) == (413, "uploads_too_large", graph_run.MAX_UPLOADS_TOTAL_B64)
    assert "add up to 20.0 MB" in body["error"] and _started(studio) == []
    assert graph_run.MAX_UPLOADS_TOTAL_B64 < 24 * 1024 * 1024, "below dx_app/server.py's JSON limit for /api/graph/run"


def test_the_server_json_limit_leaves_room_above_the_upload_limit():
    from dx_app import server
    assert server.Handler.json_max_bytes_by_path["/api/graph/run"] >= graph_run.MAX_UPLOADS_TOTAL_B64 + 1024 * 1024


# Phase 2: events while it runs and from --events, logic records, the result video's frame rate.

EVENTS_RUNNER = r"""
case "$1" in --help) cat "$FIX/help_p2.txt"; exit 0 ;; --check) exit 0 ;; esac
out=""; rep=""; evf=""
while [ $# -gt 0 ]; do
  case "$1" in
    --output) out="$2"; shift 2 ;;
    --report) rep="$2"; shift 2 ;;
    --events) evf="$2"; shift 2 ;;
    *) shift ;;
  esac
done
cat "$FIX/run_events.log"
[ -n "$evf" ] && cp "$FIX/events.jsonl" "$evf"
cp "$FIX/report_logic.json" "$rep"
printf 'img' > "$out"
exit 0
"""


def test_events_reach_the_poll_while_running_and_the_result_from_the_file(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, EVENTS_RUNNER)
    body, _ = graph_run.start(GRAPH)
    p = _wait(body["job_id"])
    assert p["event_total"] == 3 and [e["event"] for e in p["events"]] == ["enter", "intrusion", "enter"]
    assert graph_run.poll(body["job_id"], events_after=2)["events"][0]["seq"] == 3
    assert "--events" in graph_fakes.calls(studio)[-1]
    r = graph_run.result(body["job_id"])
    assert r["event_total"] == 3 and r["event_counts"] == {"zone": {"enter": 2}, "alarm": {"intrusion": 1}}
    assert r["events_url"] == f"/outputs/graph/runs/{body['job_id']}/events.jsonl" and r["events_truncated"] is False
    assert r["nodes"]["alarm"]["last_records"] == [{"numbers": {"value": 2, "active": 1}, "text": {}}]
    assert r["nodes"]["zone"]["items_total"] == 3 and "last_records" not in r["nodes"]["zone"]


def test_a_build_without_events_files_still_lists_the_printed_events(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, EVENTS_RUNNER.replace('cat "$FIX/help_p2.txt"', 'cat "$FIX/help.txt"'))
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"])
    r = graph_run.result(body["job_id"])
    assert "--events" not in graph_fakes.calls(studio)[-1]
    assert r["event_total"] == 3 and r["events_url"] is None and r["events_partial"] is False


def test_printed_events_from_a_log_cut_to_its_tail_are_partial(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, EVENTS_RUNNER.replace('cat "$FIX/help_p2.txt"', 'cat "$FIX/help.txt"'))
    monkeypatch.setattr(graph_run, "_RESULT_LOG_BYTES", 200)
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"])
    r = graph_run.result(body["job_id"])
    assert r["events_url"] is None and r["events_partial"] is True, "the counts are of the log's tail only"
    graph_fakes.install(studio, monkeypatch, EVENTS_RUNNER)
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"])
    assert graph_run.result(body["job_id"])["events_partial"] is False, "the --events file has them all"


def test_the_report_s_source_nodes_are_not_results(tmp_path):
    """dx_app's report lists the source node too (its image digest); the run panel shows model and logic nodes."""
    rep = json.loads((graph_fakes.FIX / "report.json").read_text())
    for fr in rep["frames"]:
        fr["nodes"]["cam"] = {"payload": {"shape": "image", "digest": "9f2c", "items": []}}
    (tmp_path / "report.json").write_text(json.dumps(rep))
    s = graph_run.summarize_report(tmp_path / "report.json", sources={"cam"})
    assert "cam" not in s["nodes"] and set(s["nodes"]) == {"od", "attr"}
    assert "cam" in graph_run.summarize_report(tmp_path / "report.json")["nodes"]


def test_a_finished_run_leaves_its_source_out_of_the_nodes(studio, monkeypatch):
    rep = json.loads((graph_fakes.FIX / "report.json").read_text())
    for fr in rep["frames"]:
        fr["nodes"]["cam"] = {"payload": {"shape": "image", "digest": "9f2c"}}
    (studio / "report_src.json").write_text(json.dumps(rep))
    graph_fakes.install(studio, monkeypatch, RUNNER.replace('cp "$FIX/report.json"', f'cp "{studio}/report_src.json"'))
    body, _ = graph_run.start(GRAPH)
    _wait(body["job_id"])
    assert set(graph_run.result(body["job_id"])["nodes"]) == {"od", "attr"}


LONG_LOG_RUNNER = r"""
case "$1" in --help|--check) exit 0 ;; esac
head -c 5000 /dev/zero | tr '\0' 'x'; echo
for i in $(seq 1 300); do echo "[PROGRESS] frames=$i fps=10.0 avg_fps=10.0 node_ms=od:1.0"; done
trap 'exit 0' TERM
sleep 30 & wait
"""


def test_a_poll_reads_a_bounded_slice_of_the_log(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, LONG_LOG_RUNNER)
    monkeypatch.setattr(graph_run, "_POLL_READ_BYTES", 1024)
    body, _ = graph_run.start(GRAPH)
    jid = body["job_id"]
    job = graph_run._jobs[jid]
    log = config.OUTPUTS_DIR / "graph" / "runs" / jid / "run.log"
    end = time.time() + 10
    while (not log.exists() or log.stat().st_size < 15000) and time.time() < end:
        time.sleep(0.05)
    steps, frames = [], 0
    for _ in range(200):
        before = job["cursor"]
        frames = graph_run.poll(jid)["frames"]
        steps.append(job["cursor"] - before)
        if frames == 300:
            break
    assert frames == 300, "the polls catch up, a 5000-byte line longer than one slice included"
    assert max(steps) <= 1024 and len(steps) > 10
    graph_run.stop(jid)


def test_ffprobe_reads_no_terminal_input(tmp_path, monkeypatch):
    import subprocess
    seen = {}

    def run(cmd, **kw):
        seen.update(kw)
        return subprocess.CompletedProcess(cmd, 0, stdout="25/1\n", stderr="")
    monkeypatch.setattr(graph_run.shutil, "which", lambda name: "/usr/bin/" + name)
    monkeypatch.setattr(graph_run.subprocess, "run", run)
    assert graph_run.video_fps(tmp_path / "v.mp4") == 25.0 and seen["stdin"] == subprocess.DEVNULL


def test_a_video_output_carries_its_frame_rate(tmp_path):
    import shutil
    import subprocess
    if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
        pytest.skip("ffmpeg is needed to make a test video")
    v = tmp_path / "v.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=64x48:rate=12:duration=1",
                    "-pix_fmt", "yuv420p", str(v)], check=True, timeout=60)
    assert graph_run.video_fps(v) == 12.0
    assert graph_run.video_fps(tmp_path / "none.mp4") is None


# Phase 2: a run once and a graph Live never overlap.

def test_a_run_waits_for_a_graph_live_to_end(studio, monkeypatch):
    from dx_app.core import npu_jobs
    graph_fakes.install(studio, monkeypatch, RUNNER)
    npu_jobs.acquire("graph_live", "a-graph-live")            # the registry every NPU job starts through
    body, code = graph_run.start(GRAPH)
    assert (code, body["error_key"]) == (409, "graph_live_busy") and _started(studio) == []


# Results view: per-node layers of an image run, the stream of every output.

FANOUT = {"version": 1, "name": "adas-fanout",
          "nodes": [{"id": "cam", "type": "source", "uri": "sample/img/sample_people.jpg"},
                    {"id": "od", "model": "yolov8-n_640x640"}, {"id": "seg", "model": "bisenetv2_1024x2048"},
                    {"id": "depth", "model": "fastdepth_224x224"}],
          "edges": [{"from": "cam", "to": "od"}, {"from": "cam", "to": "seg"}, {"from": "cam", "to": "depth"}]}
TWO = {"version": 1, "name": "two-cameras",
       "nodes": [{"id": "cam1", "type": "source", "uri": "sample/img/sample_people.jpg"},
                 {"id": "cam2", "type": "source", "uri": "sample/img/sample_people.jpg"},
                 {"id": "od", "model": "yolov8-n_640x640"}, {"id": "reid", "model": "casvit-t_224x224"}],
       "edges": [{"from": "cam1", "to": "od"}, {"from": "cam2", "to": "od"},
                 {"from": "od", "to": "reid", "roi": {"classes": ["person"]}}]}


def _run_to_end(graph, **kw):
    body, code = graph_run.start(graph, **kw)
    assert code == 200, body
    _wait(body["job_id"])
    return body["job_id"], graph_run.result(body["job_id"])


def test_an_image_run_returns_each_node_s_layer_over_the_clean_frame(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, graph_fakes.LAYERS_RUNNER)
    jid, r = _run_to_end(FANOUT)
    d = config.OUTPUTS_DIR / "graph" / "runs" / jid
    assert f"--output-layers {d / 'layers'}" in graph_fakes.calls(studio)[-1]
    assert r["run_id"] == jid
    (out,) = r["outputs"]
    assert out["stream"] == "cam" and out["name"] == "result.jpg"
    lay = out["layers"]
    base = f"/outputs/graph/runs/{jid}/layers/"
    assert lay["base"] == base + "result_000000_base.png" and (lay["width"], lay["height"]) == (16, 12)
    assert lay["layers"] == [
        {"node": "seg", "model": "bisenetv2_1024x2048", "url": base + "result_000000_seg.png"},
        {"node": "depth", "model": "fastdepth_224x224", "url": base + "result_000000_depth.png"},
        {"node": "od", "model": "yolov8-n_640x640", "url": base + "result_000000_od.png"}], "bottom first"


def test_with_two_sources_every_output_names_its_stream_and_has_its_own_layers(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, graph_fakes.LAYERS_RUNNER)
    jid, r = _run_to_end(TWO)
    assert [(o["stream"], o["name"]) for o in r["outputs"]] == [("cam1", "result_cam1_000000.jpg"),
                                                                ("cam2", "result_cam2_000000.jpg")]
    assert [o["layers"]["base"].rsplit("/", 1)[1] for o in r["outputs"]] == ["result_cam1_000000_base.png",
                                                                             "result_cam2_000000_base.png"]
    assert [x["node"] for x in r["outputs"][1]["layers"]["layers"]] == ["od", "reid"]


def test_a_source_id_with_underscores_still_finds_its_stream(tmp_path):
    assert graph_run._stream_of("result_cam_a_000000.jpg", ["cam", "cam_a"]) == ("cam_a", 0)
    assert graph_run._stream_of("result_cam_000012.jpg", ["cam", "cam_a"]) == ("cam", 12)
    assert graph_run._stream_of("result_cam_a.mp4", ["cam", "cam_a"]) == ("cam_a", None)
    assert graph_run._stream_of("result.jpg", ["cam"]) == ("cam", 0)
    assert graph_run._stream_of("result.mp4", ["cam"]) == ("cam", None)


def test_a_layer_file_outside_the_layers_folder_is_left_out(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, graph_fakes.LAYERS_RUNNER)
    jid, _ = _run_to_end(FANOUT)
    d = config.OUTPUTS_DIR / "graph" / "runs" / jid
    doc = json.loads((d / "layers" / "layers.json").read_text())
    doc["frames"][0]["layers"][0]["file"] = "../graph.json"
    doc["frames"][0]["layers"][1]["file"] = "missing.png"
    (d / "layers" / "layers.json").write_text(json.dumps(doc))
    (out,) = graph_run._outputs(d, False, ["cam"])
    assert [x["node"] for x in out["layers"]["layers"]] == ["od"]


def test_a_build_without_layers_runs_as_before(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, RUNNER)
    _, r = _run_to_end(GRAPH)
    assert "--output-layers" not in graph_fakes.calls(studio)[-1]
    assert r["outputs"][0]["stream"] == "cam" and "layers" not in r["outputs"][0]


def test_a_video_run_asks_for_no_layers(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, graph_fakes.LAYERS_RUNNER)
    (config.ASSETS_DIR / "clip.mp4").write_bytes(b"\0")
    _run_to_end(FANOUT, inputs={"cam": "assets/clip.mp4"})
    args = graph_fakes.calls(studio)[-1]
    assert "raw.mp4" in args and "--output-layers" not in args


def test_a_run_remembers_its_graph_and_inputs_for_a_later_frame(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, graph_fakes.LAYERS_RUNNER)
    jid, _ = _run_to_end(FANOUT, variant="async", uploads={"cam": "data:image/png;base64," + PNG})
    saved = json.loads((config.OUTPUTS_DIR / "graph" / "runs" / jid / "run.json").read_text())
    assert saved["graph"] == FANOUT and saved["variant"] == "async"
    assert saved["inputs"]["cam"].endswith(f"{jid}/input_cam.png")
