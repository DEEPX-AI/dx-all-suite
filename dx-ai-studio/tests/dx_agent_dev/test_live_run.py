"""A run belongs to the server, not to the window that requested it.

If a run were tied to one HTTP response, a browser dropping its stream reader would raise
`GeneratorExit` in the server generator and `agent_runner.py`'s `finally` would kill the subprocess.
That cleanup is right for completion and timeouts, but closing a window must not trigger it.

So the run is detached from the response: a background worker buffers events and responses read the
buffer. The run continues with no consumer, and a late consumer receives everything from the start.
"""
from __future__ import annotations

import threading
import time

import pytest

from dx_agent_dev.core.live_run import LiveRun


def _slow_source(n=5, delay=0.02, started=None, finished=None):
    def gen():
        if started:
            started.set()
        for i in range(n):
            time.sleep(delay)
            yield {"type": "message", "text": f"e{i}"}
        yield {"type": "done"}
        if finished:
            finished.set()
    return gen()


def test_events_accumulate_with_nobody_listening():
    """The run progresses before any consumer attaches."""
    run = LiveRun()
    run.start(_slow_source(3))
    deadline = time.time() + 5
    while time.time() < deadline and not run.snapshot()["done"]:
        time.sleep(0.02)
    snap = run.snapshot()
    assert snap["done"], "아무도 안 듣는다고 실행이 멈췄다"
    assert snap["count"] == 4, snap          # 3 + done


def test_attaching_late_replays_from_the_beginning():
    run = LiveRun()
    run.start(_slow_source(3))
    while not run.snapshot()["done"]:
        time.sleep(0.02)
    got = [e for e in run.events(0)]
    assert [e.get("text") for e in got[:3]] == ["e0", "e1", "e2"], got
    assert got[-1]["type"] == "done"


def test_two_consumers_see_the_same_run():
    """home and Agent Dev can watch the same run at once."""
    run = LiveRun()
    run.start(_slow_source(4, delay=0.03))
    out = {}

    def drain(key):
        out[key] = [e for e in run.events(0)]

    a = threading.Thread(target=drain, args=("a",))
    b = threading.Thread(target=drain, args=("b",))
    a.start(); b.start(); a.join(10); b.join(10)
    assert out["a"] == out["b"], (out["a"], out["b"])
    assert len(out["a"]) == 5


def test_start_does_not_block_the_caller():
    """If the run executes on the caller's thread, this class achieves nothing.

    Without this check the "continues after the consumer leaves" test below passes trivially: with a
    synchronous pump start() runs to the end before returning, so the run is over before anyone attaches.
    """
    run = LiveRun()
    started = threading.Event()
    run.start(_slow_source(6, delay=0.05, started=started))
    assert started.wait(5), "소스가 시작되지 않았다"
    assert not run.snapshot()["done"], "start() 가 실행을 끝내고 돌아왔다"
    run.cancel()


def test_a_consumer_giving_up_does_not_stop_the_run():
    """The core contract: closing the window must not stop the run."""
    run = LiveRun()
    finished = threading.Event()
    run.start(_slow_source(6, delay=0.05, finished=finished))

    stream = run.events(0)
    next(stream)                 # take only the first event
    assert not run.snapshot()["done"], "떠나기도 전에 실행이 끝났다 — 검사가 무의미하다"
    stream.close()               # same as the browser leaving

    assert finished.wait(10), "소비자가 떠나자 실행이 멈췄다"
    assert run.snapshot()["count"] == 7


def test_resuming_from_an_index_skips_what_was_seen():
    run = LiveRun()
    run.start(_slow_source(3))
    while not run.snapshot()["done"]:
        time.sleep(0.02)
    rest = [e for e in run.events(2)]
    assert [e.get("text") for e in rest[:1]] == ["e2"], rest


def test_a_new_run_replaces_the_last_one():
    """One run per server. A finished run stays only until the next one starts."""
    run = LiveRun()
    first = run.start(_slow_source(2))
    while not run.snapshot()["done"]:
        time.sleep(0.02)
    second = run.start(_slow_source(2))
    assert second != first
    assert run.snapshot()["run_id"] == second


def test_starting_while_busy_is_refused():
    run = LiveRun()
    run.start(_slow_source(6, delay=0.05))
    with pytest.raises(RuntimeError):
        run.start(_slow_source(2))
    run.cancel()
