"""npu_jobs: one NPU job at a time among a graph run once, a graph Live and the Run page's Live.

The registry alone first, then the three starters against each other through fake runners: each refuses while
another kind holds the NPU (with its own error key), starts racing in threads leave exactly one winner, and the
hold ends on every exit path (the runner finishes, crashes, is stopped, fails to start, the server shuts down).
"""
from __future__ import annotations

import subprocess
import threading
import time
import types

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


class _Proc:
    def __init__(self, code=None):
        self.code = code

    def poll(self):
        return self.code


def test_one_kind_holds_the_npu_and_its_process_ends_the_hold():
    assert npu_jobs.acquire("graph_run", "a") is None
    assert npu_jobs.acquire("graph_run", "a") is None, "the holder asking again keeps it"
    assert npu_jobs.acquire("graph_live", "b") == "graph_run"
    assert npu_jobs.acquire("graph_run", "c") == "graph_run"
    assert npu_jobs.busy() == {"kind": "graph_run", "job_id": "a"}
    proc = _Proc()
    npu_jobs.attach("a", proc)
    assert npu_jobs.held_by("graph_run")
    proc.code = 1                                        # the runner crashed
    assert npu_jobs.busy() is None and npu_jobs.acquire("graph_live", "b") is None
    npu_jobs.release("b")
    assert npu_jobs.busy() is None


def test_the_run_pages_live_slots_share_the_npu_with_each_other_only():
    assert npu_jobs.acquire("live", "live-slot-0") is None
    assert npu_jobs.acquire("live", "live-slot-1") is None
    assert npu_jobs.acquire("graph_live", "g") == "live"
    npu_jobs.release("live-slot-0")
    npu_jobs.release("live-slot-1")
    assert npu_jobs.acquire("graph_live", "g") is None
    assert npu_jobs.acquire("live", "live-slot-0") == "graph_live"


def test_a_hold_without_a_process_lapses_and_release_if_idle_keeps_a_running_one(monkeypatch):
    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 0.0)
    assert npu_jobs.acquire("graph_run", "a") is None
    assert npu_jobs.busy() is None, "a reservation nobody attached a process to does not keep the NPU"
    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 120.0)
    npu_jobs.acquire("live", "live-slot-0")
    npu_jobs.attach("live-slot-0", _Proc())
    npu_jobs.release_if_idle("live-slot-0")
    assert npu_jobs.held_by("live")
    npu_jobs.acquire("live", "live-slot-1")
    npu_jobs.release_if_idle("live-slot-1")
    assert npu_jobs.busy() == {"kind": "live", "job_id": "live-slot-0"}
    with pytest.raises(ValueError):
        npu_jobs.acquire("other", "x")


# The three starters against each other.

RUNNER = r"""
case "$1" in --help) cat "$FIX/help_p2.txt"; exit 0 ;; --check) exit 0 ;; esac
trap 'exit 0' TERM
sleep 30 & wait
"""

CRASHING = r"""
case "$1" in --help) cat "$FIX/help_p2.txt"; exit 0 ;; --check) exit 0 ;; esac
echo 'ERROR [MODEL_LOAD] node "od": model "yolov8-n_640x640" could not be loaded'
exit 3
"""

GRAPH = {"version": 1, "name": "zone",
         "nodes": [{"id": "cam", "type": "source", "uri": "assets/videos/clip.mp4"},
                   {"id": "od", "model": "yolov8-n_640x640", "track": {}},
                   {"id": "zone", "type": "logic", "op": "zone", "params": {"zones": [[0, 0, 1, 0, 1, 1]]}}],
         "edges": [{"from": "cam", "to": "od"}, {"from": "od", "to": "zone", "carry": "result"}]}


class _PageProc:
    """The Run page's live runner (its Popen is replaced only inside live.py)."""
    pid = 1

    def __init__(self, cmd, **kw):
        self.code = None

    def poll(self):
        return self.code

    def terminate(self):
        self.code = -15

    def kill(self):
        self.code = -9

    def wait(self, timeout=None):
        return self.code


@pytest.fixture
def studio(tmp_path, monkeypatch):
    root = tmp_path / "dx_app"
    (root / "assets" / "videos").mkdir(parents=True)
    (root / "assets" / "videos" / "clip.mp4").write_bytes(b"\0")
    (root / "sample").mkdir()
    for name, value in (("DX_APP_ROOT", root), ("SAMPLE_DIR", root / "sample"), ("ASSETS_DIR", root / "assets"),
                        ("OUTPUTS_DIR", tmp_path / "outputs")):
        monkeypatch.setattr(config, name, value)
    monkeypatch.setattr(graph_live, "_deps_missing", lambda: [])
    monkeypatch.setattr(graph_live, "_STOP_GRACE", 1.0)
    monkeypatch.setattr(camera, "_ensure_xvfb", lambda slot=0: None)
    monkeypatch.setattr(camera, "stop_xvfb", lambda slot: None)
    monkeypatch.setattr(camera, "_xlib", lambda: object())
    monkeypatch.setattr(camera, "_xcb", lambda: object())
    build = tmp_path / "build"
    build.mkdir()
    (build / "demo_sync").write_text("")
    model = tmp_path / "m.dxnn"
    model.write_bytes(b"DXNN")
    monkeypatch.setattr(live, "BUILD_DIR", build)
    monkeypatch.setattr(live, "resolve_model_path", lambda f, r: model)
    monkeypatch.setattr(live, "_ensure_xvfb", lambda s: None)
    monkeypatch.setattr(live, "_deps_missing", lambda: [])
    monkeypatch.setattr(live, "_video_frame_count", lambda p: None)
    monkeypatch.setattr(live, "subprocess", types.SimpleNamespace(Popen=_PageProc, STDOUT=subprocess.STDOUT))
    graph_fakes.install(tmp_path, monkeypatch, RUNNER)
    graph_live._job = None
    graph_run._jobs.clear()
    yield tmp_path
    graph_live.stop_all()
    graph_live._job = None
    graph_run.stop_all()
    graph_run._jobs.clear()
    live._live_procs.clear()


def _page_live(studio, slot=0):
    return live.run_inference_live("demo", "object_detection", "m.dxnn", lang="cpp", variant="sync",
                                   input_type="video", video_path=str(studio / "dx_app/assets/videos/clip.mp4"),
                                   slot_idx=slot)


def _start(kind, studio, slot=0):
    """(ok, error_key) of starting `kind`."""
    if kind == "graph_run":
        body, code = graph_run.start(GRAPH)
        return code == 200, body.get("error_key")
    if kind == "graph_live":
        body, code = graph_live.start(GRAPH)
        return code == 200, body.get("error_key")
    r = _page_live(studio, slot)
    return r.get("status") == "started", r.get("error_key")


def _until_free(timeout=8):
    end = time.time() + timeout
    while npu_jobs.busy() is not None and time.time() < end:
        time.sleep(0.05)
    return npu_jobs.busy()


def _stop(kind):
    if kind == "graph_run":
        for jid in list(graph_run._jobs):
            graph_run.stop(jid)
    elif kind == "graph_live":
        graph_live.stop(graph_live._job["id"])
    else:
        live.stop_inference_live(None)


BUSY_KEY = {"graph_run": "graph_run_busy", "graph_live": "graph_live_busy", "live": "live_busy"}


@pytest.mark.parametrize("holder,other", [(a, b) for a in BUSY_KEY for b in BUSY_KEY if a != b])
def test_each_kind_refuses_while_another_holds_the_npu(studio, holder, other):
    assert _start(holder, studio) == (True, None)
    assert npu_jobs.busy()["kind"] == holder
    assert _start(other, studio) == (False, BUSY_KEY[holder])
    _stop(holder)
    assert _until_free() is None, "a stopped job gives the NPU back"
    assert _start(other, studio) == (True, None)


def test_the_same_kind_twice(studio):
    assert _start("graph_run", studio) == (True, None)
    assert _start("graph_run", studio) == (False, "graph_run_busy")
    _stop("graph_run")
    assert _until_free() is None
    assert _start("graph_live", studio) == (True, None)
    assert _start("graph_live", studio) == (False, "graph_live_busy")
    _stop("graph_live")
    assert _until_free() is None
    assert _start("live", studio, 0) == (True, None) and _start("live", studio, 1) == (True, None)


def test_starts_racing_in_threads_leave_exactly_one_winner(studio):
    for _ in range(3):
        barrier = threading.Barrier(3)
        results = {}

        def go(kind):
            barrier.wait()
            results[kind] = _start(kind, studio)

        threads = [threading.Thread(target=go, args=(k,)) for k in BUSY_KEY]
        for t in threads:
            t.start()
        for t in threads:
            t.join(10)
        winners = [k for k, (ok, _key) in results.items() if ok]
        assert len(winners) == 1, results
        for k, (ok, key) in results.items():
            if not ok:
                assert key == BUSY_KEY[winners[0]], results
        _stop(winners[0])
        assert _until_free() is None


def test_a_crashed_runner_gives_the_npu_back(studio, monkeypatch):
    graph_fakes.install(studio, monkeypatch, CRASHING)
    assert _start("graph_run", studio) == (True, None)
    assert _until_free() is None
    assert _start("graph_live", studio) == (True, None)
    assert _until_free() is None
    assert _start("live", studio) == (True, None)
    live._live_procs[0].code = 1
    assert npu_jobs.busy() is None


def test_a_start_that_fails_gives_the_npu_back(studio, monkeypatch):
    bad = dict(GRAPH, nodes=[dict(GRAPH["nodes"][0], uri="assets/videos/none.mp4")] + GRAPH["nodes"][1:])
    assert graph_run.start(bad)[1] == 400 and npu_jobs.busy() is None

    def no_popen(*a, **kw):
        raise OSError("exec format error")
    monkeypatch.setattr(graph_live, "subprocess", types.SimpleNamespace(
        Popen=no_popen, PIPE=subprocess.PIPE, STDOUT=subprocess.STDOUT, DEVNULL=subprocess.DEVNULL,
        SubprocessError=subprocess.SubprocessError))
    assert graph_live.start(GRAPH)[1] == 500 and npu_jobs.busy() is None


def test_a_run_page_live_that_fails_to_start_gives_the_npu_back(studio):
    (studio / "build" / "demo_sync").unlink()
    assert _start("live", studio) == (False, "binary_not_found")
    assert npu_jobs.busy() is None


def test_shutdown_gives_the_npu_back(studio):
    assert _start("live", studio) == (True, None)
    live.shutdown_live_processes()
    assert npu_jobs.busy() is None
    assert _start("graph_live", studio) == (True, None)
    graph_live.stop_all()
    assert npu_jobs.busy() is None


def test_attach_after_the_reservation_lapsed(monkeypatch):
    """A job slower than RESERVE_TTL to start its runner: attach says whether it still holds the NPU."""
    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 0.0)
    assert npu_jobs.acquire("graph_run", "a") is None
    assert npu_jobs.attach("a", _Proc()) is True, "lapsed but nobody took the NPU: the hold is kept"
    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 120.0)
    assert npu_jobs.busy() == {"kind": "graph_run", "job_id": "a"}
    npu_jobs._reset()

    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 0.0)
    assert npu_jobs.acquire("graph_run", "a") is None
    assert npu_jobs.busy() is None                       # pruned
    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 120.0)
    assert npu_jobs.attach("a", _Proc()) is False, "a pruned hold is not given back without its kind"
    assert npu_jobs.attach("a", _Proc(), kind="graph_run") is True, "the NPU was free: taken again atomically"
    assert npu_jobs.busy() == {"kind": "graph_run", "job_id": "a"}
    npu_jobs._reset()

    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 0.0)
    assert npu_jobs.acquire("graph_run", "a") is None
    assert npu_jobs.acquire("graph_live", "b") is None, "another job took the NPU meanwhile"
    monkeypatch.setattr(npu_jobs, "RESERVE_TTL", 120.0)
    assert npu_jobs.attach("a", _Proc(), kind="graph_run") is False
    assert npu_jobs.busy() == {"kind": "graph_live", "job_id": "b"}


def test_a_runner_whose_hold_was_lost_is_stopped(studio, monkeypatch):
    """graph_run and graph_live kill the runner they started when attach says the NPU went to another job."""
    monkeypatch.setattr(npu_jobs, "attach", lambda *a, **kw: False)
    body, code = graph_run.start(GRAPH)
    assert (code, body["error_key"]) == (409, "npu_hold_lost") and graph_run._jobs == {}
    body, code = graph_live.start(GRAPH)
    assert (code, body["error_key"]) == (409, "npu_hold_lost") and graph_live._job is None
    r = _page_live(studio)
    assert r.get("error_key") == "npu_hold_lost" and live._live_procs == {}
