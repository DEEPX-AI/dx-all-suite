"""graph_live: a graph Live through a fake runner that draws nothing but prints progress and events until stopped.

The Live display (Xvfb, the window grab) is replaced by stubs; tests/dx_app/test_graph_real_cli.py runs the real one.
"""
from __future__ import annotations

import time

import pytest

from dx_app.core import camera, config, graph_live, graph_run, live, npu_jobs
from tests.dx_app import graph_fakes

@pytest.fixture(autouse=True)
def _npu_free():
    """No test inherits another's hold on the NPU (npu_jobs.py): a fake runner whose poll() never ends keeps it."""
    from dx_app.core import npu_jobs
    npu_jobs._reset()
    yield
    npu_jobs._reset()


LIVE_RUNNER = r"""
case "$1" in --help) cat "$FIX/help_p2.txt"; exit 0 ;; --check) exit 0 ;; esac
evf=""
while [ $# -gt 0 ]; do case "$1" in --events) evf="$2"; shift 2 ;; *) shift ;; esac; done
echo "note: DISPLAY=$DISPLAY"
trap 'echo stopped; exit 0' TERM
i=0
while true; do
  i=$((i+1))
  echo "[PROGRESS] frames=$i fps=25.0 avg_fps=24.5 node_ms=od:12.5,zone:0.2"
  echo "[EVENT] {\"frame\": $i, \"time\": 0.04, \"stream\": \"cam\", \"node\": \"zone\", \"event\": \"enter\", \"track_id\": $i, \"data\": {}}"
  [ -n "$evf" ] && echo "{\"frame\": $i, \"node\": \"zone\", \"event\": \"enter\"}" >> "$evf"
  sleep 0.1 & wait
done
"""

FAILING = r"""
case "$1" in --help) cat "$FIX/help_p2.txt"; exit 0 ;; --check) exit 0 ;; esac
echo 'ERROR [MODEL_LOAD] node "od": model "yolov8-n_640x640" could not be loaded'
echo '  -> the NPU device memory may be full'
exit 1
"""

GRAPH = {"version": 1, "name": "zone",
         "nodes": [{"id": "cam", "type": "source", "uri": "assets/videos/clip.mp4"},
                   {"id": "od", "model": "yolov8-n_640x640", "track": {}},
                   {"id": "zone", "type": "logic", "op": "zone", "params": {"zones": [[0, 0, 1, 0, 1, 1]]}}],
         "edges": [{"from": "cam", "to": "od"}, {"from": "od", "to": "zone", "carry": "result"}]}


@pytest.fixture
def studio(tmp_path, monkeypatch):
    root = tmp_path / "dx_app"
    (root / "assets" / "videos").mkdir(parents=True)
    (root / "assets" / "videos" / "clip.mp4").write_bytes(b"\0")
    (root / "sample" / "img").mkdir(parents=True)
    (root / "sample" / "img" / "a.jpg").write_bytes(b"\xff\xd8")
    for name, value in (("DX_APP_ROOT", root), ("SAMPLE_DIR", root / "sample"), ("ASSETS_DIR", root / "assets"),
                        ("OUTPUTS_DIR", tmp_path / "outputs")):
        monkeypatch.setattr(config, name, value)
    xvfb = []
    monkeypatch.setattr(graph_live, "_deps_missing", lambda: [])
    monkeypatch.setattr(camera, "_ensure_xvfb", lambda slot=0: xvfb.append(("start", slot)))
    monkeypatch.setattr(camera, "stop_xvfb", lambda slot: xvfb.append(("stop", slot)))
    monkeypatch.setattr(camera, "capture_live_frame", lambda slot=0: b"jpeg-of-slot-%d" % slot)
    monkeypatch.setattr(graph_live, "_STOP_GRACE", 1.0)
    graph_live._job = None
    graph_run._jobs.clear()
    yield {"tmp": tmp_path, "xvfb": xvfb}
    graph_live.stop_all()
    graph_live._job = None


def _poll_until(job_id, cond, timeout=8):
    end = time.time() + timeout
    while time.time() < end:
        p = graph_live.poll(job_id)
        if cond(p):
            return p
        time.sleep(0.05)
    raise AssertionError(f"timed out: {p}")


def test_a_looping_video_runs_live_with_progress_events_and_a_frame_stream(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    body, code = graph_live.start(GRAPH)
    assert code == 200 and body["frame_url"] == f"/api/graph/live/frame?id={body['job_id']}"
    jid = body["job_id"]
    p = _poll_until(jid, lambda p: p["frames"] >= 2 and p["event_total"] >= 2)
    assert p["running"] is True and p["fps"] == 25.0 and p["node_ms"] == {"od": 12.5, "zone": 0.2}
    assert p["events"][0]["node"] == "zone" and p["events"][0]["seq"] == 1
    args = [c for c in graph_fakes.calls(studio["tmp"]) if "--graph" in c][-1]
    assert "--display" in args and "--loop" in args and "--events" in args and "cam=" in args and "clip.mp4" in args
    assert graph_live.frame_ok(jid) and graph_live.frame(jid) == b"jpeg-of-slot-8"
    assert graph_live.frame("someone-else") is None and not graph_live.frame_ok("") and not graph_live.frame_ok(None)
    assert ("start", graph_live.SLOT) in studio["xvfb"]
    assert graph_live.stop(jid) == {"status": "stopping"}
    end = _poll_until(jid, lambda p: not p["running"])
    assert end["exit_code"] == 0 and end["stopped_by"] == "user" and end["errors"] == []
    assert end["events_url"] == f"/outputs/graph/live/{jid}/events.jsonl"
    assert ("stop", graph_live.SLOT) in studio["xvfb"] and not graph_live.running()


def test_the_runner_draws_on_the_live_slot_display(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    jid = graph_live.start(GRAPH)[0]["job_id"]
    time.sleep(0.4)
    graph_live.stop(jid)
    end = _poll_until(jid, lambda p: not p["running"])
    assert f"note: DISPLAY=:{camera._XVFB_BASE + graph_live.SLOT}" in end["log_tail"]


def test_a_camera_or_stream_needs_no_loop(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    body, code = graph_live.start(GRAPH, inputs={"cam": "rtsp://10.0.0.2/stream1"})
    assert code == 200
    _poll_until(body["job_id"], lambda p: p["frames"] >= 1)
    args = [c for c in graph_fakes.calls(studio["tmp"]) if "--graph" in c][-1]
    assert "cam=rtsp://10.0.0.2/stream1" in args and "--loop" not in args
    graph_live.stop(body["job_id"])


@pytest.mark.parametrize("inputs, code, key", [
    ({"cam": "camera:63"}, 400, "invalid_live_input"),              # no /dev/video63
    ({"cam": "rtsp://a b"}, 400, "invalid_live_input"),
    ({"cam": "sample/img/a.jpg"}, 400, "invalid_live_input"),       # an image does not stream
    ({"cam": "/etc/passwd"}, 400, "invalid_live_input"),
])
def test_inputs_that_cannot_stream_are_refused(studio, monkeypatch, inputs, code, key):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    body, got = graph_live.start(GRAPH, inputs=inputs)
    assert (got, body["error_key"]) == (code, key)
    assert not any("--graph" in c for c in graph_fakes.calls(studio["tmp"]))


def test_a_build_that_cannot_loop_refuses_a_video_but_says_what_works(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, graph_fakes.JSON_CLI)
    body, code = graph_live.start(GRAPH)
    assert (code, body["error_key"]) == (409, "loop_unsupported") and "camera" in body["error"]


def test_one_live_at_a_time_and_never_beside_a_run_or_the_run_pages_live(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    first = graph_live.start(GRAPH)[0]["job_id"]
    body, code = graph_live.start(GRAPH)
    assert (code, body["error_key"]) == (409, "graph_live_busy")
    assert graph_run.start(GRAPH)[0]["error_key"] == "graph_live_busy"
    r = live.run_inference_live("yolov8n", "object_detection", "x.dxnn")
    assert r["error_key"] == "graph_live_busy"
    graph_live.stop(first)
    _poll_until(first, lambda p: not p["running"])
    npu_jobs.acquire("graph_run", "a-run")                     # the registry every NPU job starts through
    assert graph_live.start(GRAPH)[0]["error_key"] == "graph_run_busy"
    npu_jobs.release("a-run")
    npu_jobs.acquire("live", "live-slot-0")
    assert graph_live.start(GRAPH)[0]["error_key"] == "live_busy"


def test_missing_live_tools_are_named(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    monkeypatch.setattr(graph_live, "_deps_missing", lambda: ["Xvfb (sudo apt install xvfb)"])
    body, code = graph_live.start(GRAPH)
    assert (code, body["error_key"]) == (409, "live_deps_missing") and "Xvfb" in body["error"]


def test_a_live_nobody_watches_is_stopped(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    monkeypatch.setattr(graph_live, "_TTL", 0.5)
    jid = graph_live.start(GRAPH)[0]["job_id"]
    deadline = time.time() + 8
    while graph_live.running() and time.time() < deadline:
        time.sleep(0.1)
    assert not graph_live.running()
    assert _poll_until(jid, lambda p: not p["running"])["stopped_by"] == "unwatched"


def test_a_failed_load_ends_live_with_the_error_on_its_node(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, FAILING)
    jid = graph_live.start(GRAPH)[0]["job_id"]
    end = _poll_until(jid, lambda p: not p["running"])
    assert end["exit_code"] == 1 and (end["errors"][0]["code"], end["errors"][0]["node"]) == ("MODEL_LOAD", "od")


def test_stop_all_ends_the_live(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    jid = graph_live.start(GRAPH)[0]["job_id"]
    graph_live.stop_all()
    assert not graph_live.running() and graph_live.poll(jid)["running"] in (True, False)


def test_the_runner_s_lines_arrive_line_by_line(studio, monkeypatch):
    """Through a pipe the runner's stdio would hold lines in a buffer; stdbuf -oL makes it hand each line over."""
    import shutil
    if not shutil.which("stdbuf"):
        pytest.skip("coreutils stdbuf is not installed")
    seen = {}
    real = graph_live.subprocess.Popen

    def spy(cmd, *a, **k):
        seen["cmd"] = cmd
        return real(cmd, *a, **k)
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    monkeypatch.setattr(graph_live.subprocess, "Popen", spy)
    jid = graph_live.start(GRAPH)[0]["job_id"]
    assert seen["cmd"][1:3] == ["-oL", "-eL"] and seen["cmd"][0].endswith("stdbuf")
    graph_live.stop(jid)


def test_the_job_id_is_compared_in_constant_time(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    jid = graph_live.start(GRAPH)[0]["job_id"]
    seen = []
    real = graph_live.hmac.compare_digest
    monkeypatch.setattr(graph_live.hmac, "compare_digest", lambda a, b: seen.append((a, b)) or real(a, b))
    assert graph_live.frame_ok(jid) and seen, "the stream's gate goes through hmac.compare_digest"
    for bad in (jid[:-1] + ("0" if jid[-1] != "0" else "1"), jid + "0", "", "é" * 32, None, 7):
        assert graph_live.frame_ok(bad) is False, bad
        assert graph_live.frame(bad) is None
    assert graph_live.poll("é")["error"] == "unknown_job"
    graph_live.stop(jid)


def test_an_unknown_live_says_so_with_an_error_key(studio):
    assert graph_live.poll("nope") == {"error": "unknown_job", "error_key": "unknown_job"}


def test_the_runner_reads_no_terminal_input(studio, monkeypatch):
    seen = {}
    real = graph_live.subprocess.Popen

    def spy(cmd, *a, **k):
        seen.update(k)
        return real(cmd, *a, **k)
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    monkeypatch.setattr(graph_live.subprocess, "Popen", spy)
    jid = graph_live.start(GRAPH)[0]["job_id"]
    assert seen["stdin"] == graph_live.subprocess.DEVNULL
    graph_live.stop(jid)


class _DeadProc:
    """A runner that has exited; its stdout breaks while being read."""
    returncode = 0

    class _Out:
        def __iter__(self):
            raise ValueError("I/O operation on closed file")

    def __init__(self):
        self.stdout = self._Out()

    def poll(self):
        return 0

    def wait(self, timeout=None):
        return 0


def _old_job(tmp, jid="old"):
    import threading
    from collections import deque
    from dx_app.core import graph_events
    d = tmp / jid
    d.mkdir()
    return {"id": jid, "dir": d, "proc": _DeadProc(), "graph": GRAPH, "start": 0, "touched": 0,
            "progress": {"node_ms": {}}, "events": graph_events.EventLog(), "tail": deque(), "result": None,
            "stop_reason": None, "done": threading.Event(), "events_url": "/outputs/x"}


def test_the_reader_always_ends_the_job_even_when_reading_fails(studio):
    job = _old_job(studio["tmp"])
    graph_live._job = job
    assert npu_jobs.acquire("graph_live", "old") is None
    with pytest.raises(ValueError):
        graph_live._read(job)
    assert job["done"].is_set() and npu_jobs.busy() is None
    assert job["result"] is not None, "the poll still learns that the Live ended"


def test_a_new_live_waits_for_the_old_reader_and_keeps_its_display(studio, monkeypatch):
    """The old runner has exited (the NPU is free) but its reader has not finished: it must not close the display
    the new Live has just opened."""
    import threading
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    old = _old_job(studio["tmp"])
    old["proc"].stdout = iter(["last line\n"])
    graph_live._job = old
    order = studio["xvfb"]

    def finish_old():
        time.sleep(0.3)
        order.append("old reader")
        graph_live._read(old)
    t = threading.Thread(target=finish_old)
    t.start()
    jid = graph_live.start(GRAPH)[0]["job_id"]
    t.join(5)
    assert order.index("old reader") < order.index(("start", graph_live.SLOT)), order
    assert ("stop", graph_live.SLOT) not in order, "the old reader leaves the new Live's display alone"
    graph_live.stop(jid)
    _poll_until(jid, lambda p: not p["running"])
    assert order[-1] == ("stop", graph_live.SLOT), "the current Live's reader closes it"


# Results view: the nodes Live draws are picked before it starts (dx_app --draw).

DRAW_RUNNER = LIVE_RUNNER.replace('cat "$FIX/help_p2.txt"', 'cat "$FIX/help_p3.txt"')


def test_live_draws_only_the_picked_nodes(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, DRAW_RUNNER)
    body, code = graph_live.start(GRAPH, draw=["zone", "od"])
    assert code == 200, body
    _poll_until(body["job_id"], lambda p: p["frames"] >= 1)
    args = [c for c in graph_fakes.calls(studio["tmp"]) if "--graph" in c][-1]
    assert "--draw zone,od" in args
    graph_live.stop(body["job_id"])


def test_without_a_pick_every_node_draws(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, DRAW_RUNNER)
    body, _ = graph_live.start(GRAPH, draw=None)
    _poll_until(body["job_id"], lambda p: p["frames"] >= 1)
    assert "--draw" not in [c for c in graph_fakes.calls(studio["tmp"]) if "--graph" in c][-1]
    graph_live.stop(body["job_id"])


@pytest.mark.parametrize("draw", [["cam"], ["nope"], "od", [], [1], ["od"] * 300])
def test_a_pick_that_is_not_the_graph_s_drawing_nodes_is_refused(studio, monkeypatch, draw):
    graph_fakes.install(studio["tmp"], monkeypatch, DRAW_RUNNER)
    body, code = graph_live.start(GRAPH, draw=draw)
    assert (code, body["error_key"]) == (400, "invalid_draw") and npu_jobs.busy() is None


def test_a_build_without_draw_refuses_a_pick(studio, monkeypatch):
    graph_fakes.install(studio["tmp"], monkeypatch, LIVE_RUNNER)
    body, code = graph_live.start(GRAPH, draw=["od"])
    assert (code, body["error_key"]) == (409, "draw_unsupported")
