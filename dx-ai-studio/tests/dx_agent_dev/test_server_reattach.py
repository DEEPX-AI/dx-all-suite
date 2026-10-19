"""The server owns the run: it continues when the stream drops, and clients can reattach.

`test_live_run.py` covers the buffer itself; this file checks it is wired into the HTTP path. A correct
buffer does not help if the handler calls `_runner.run()` directly.
"""
from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request

import pytest

from tests.server_helpers import start_module_server


@pytest.fixture()
def agent(monkeypatch):
    # Use mock: a run without an agent goes to the default copilot, which would start real runs on a
    # machine where the copilot CLI is installed and signed in. A slow mock makes "leave mid-run, then
    # reattach" possible (an instant mock would finish before the client leaves).
    monkeypatch.setenv("DX_AGENT_ADAPTER", "mock")
    monkeypatch.setenv("DX_AGENT_MOCK_DELAY", "0.25")
    server, port = start_module_server("dx_agent_dev")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


def _get(base, path):
    with urllib.request.urlopen(base + path, timeout=10) as r:
        return json.loads(r.read().decode())


def _post_stream(base, payload):
    req = urllib.request.Request(
        base + "/api/agent/run",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    return urllib.request.urlopen(req, timeout=30)


def test_status_reports_the_current_run(agent):
    st = _get(agent, "/api/agent/status")
    for key in ("busy", "run_id", "event_count"):
        assert key in st, f"status 에 {key} 가 없다: {sorted(st)}"


def test_the_run_survives_a_consumer_that_walks_away(agent):
    """This is what moving from home to Agent Dev looks like."""
    resp = _post_stream(agent, {"prompt": "make baseball game"})
    first = resp.readline()
    assert first, "스트림이 아무것도 주지 않았다"
    resp.close()                       # same as closing the window
    time.sleep(0.4)

    st = _get(agent, "/api/agent/status")
    assert st.get("run_id"), "실행이 서버에 남아 있지 않다"
    assert st.get("event_count", 0) >= 1, st


def test_you_can_attach_to_a_run_you_did_not_start(agent):
    """The path Agent Dev uses to attach to a run home started."""
    resp = _post_stream(agent, {"prompt": "make baseball game"})
    resp.readline()
    resp.close()

    with urllib.request.urlopen(agent + "/api/agent/run/events?from=0", timeout=60) as att:
        body = att.read().decode("utf-8", "replace")
    assert "data:" in body, f"붙었는데 이벤트가 없다: {body[:200]!r}"


def test_attaching_from_an_index_skips_what_was_seen(agent):
    """`from` really skips events. Event counts differ per adapter, so compare relatively."""
    resp = _post_stream(agent, {"prompt": "make baseball game"})
    resp.read()
    resp.close()
    full = _get(agent, "/api/agent/status")["event_count"]
    assert full >= 1, full

    def _count(from_index):
        with urllib.request.urlopen(
            agent + f"/api/agent/run/events?from={from_index}", timeout=60
        ) as att:
            return att.read().decode("utf-8", "replace").count("data:")

    beginning = _count(0)
    assert beginning >= 1, "처음부터 붙었는데 아무것도 못 받았다"
    assert _count(full) < beginning, (
        f"끝 지점에서 붙었는데 처음과 같은 양을 받았다 ({beginning})"
    )


def test_the_post_response_shape_is_unchanged(agent):
    """Agent Dev's own console (console.js) must keep working."""
    resp = _post_stream(agent, {"prompt": "make baseball game"})
    try:
        assert resp.headers.get("Content-Type", "").startswith("text/event-stream")
        line = resp.readline().decode()
        assert line.startswith("data: "), line
    finally:
        resp.close()
