"""Real-NPU tier for DX Stream: every demo starts, frames flow, a frame decodes, it stops.

The unit and browser suites drive the Stream page against fakes, so none of them can
tell that a demo which "started" never produced a frame (the S-1/S-6 failures of the
2026-10-10 audit were exactly that). This tier starts the real ``dx_stream/server.py``
on an ephemeral port and drives the same HTTP calls the Demo Launcher makes.

Opt in on a board with a DX-M1: ``DX_E2E_STREAM_NPU=1 pytest tests/e2e -m e2e_npu``
(``DX_E2E_NPU_STRICT=1`` turns a missing NPU into a failure). The RTSP demo needs the
public camera host; it is skipped unless ``DX_E2E_STREAM_RTSP=1``. ``DX_E2E_STREAM_DEMOS``
(comma-separated ids) narrows the run.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
START_TIMEOUT_S = 60
FRAME_WAIT_S = 20


def _unavailable_reason() -> str | None:
    if os.environ.get("DX_E2E_STREAM_NPU") != "1" and os.environ.get("DX_E2E_NPU_STRICT") != "1":
        return "real-NPU Stream tier is opt-in (DX_E2E_STREAM_NPU=1)"
    if not Path("/dev/dxrt0").exists():
        return "no DX-M1 device (/dev/dxrt0)"
    return None


def _call(base: str, path: str, body: dict | None = None, timeout: float = 30.0):
    data = None if body is None else json.dumps(body).encode()
    req = urllib.request.Request(base + path, data=data, method="GET" if body is None else "POST",
                                 headers={"Content-Type": "application/json"} if data else {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


@pytest.fixture(scope="module")
def stream_server():
    reason = _unavailable_reason()
    if reason:
        if os.environ.get("DX_E2E_NPU_STRICT") == "1":
            pytest.fail(f"DX_E2E_NPU_STRICT=1 but the Stream NPU tier cannot run: {reason}")
        pytest.skip(reason)
    tmp = Path(tempfile.mkdtemp(prefix="dx-e2e-stream-"))
    port_file = tmp / "dx_stream.port"
    env = {k: v for k, v in os.environ.items() if k not in ("DX_APP_ROOT", "DX_STUDIO_OUTPUTS")}
    env["DX_PORT_FILE"] = str(port_file)
    env["PYTHONPATH"] = str(ROOT) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")  # as the launcher does
    log = open(tmp / "server.log", "wb")
    proc = subprocess.Popen([sys.executable, str(ROOT / "dx_stream/server.py"), "--port", "0", "--no-browser"],
                            cwd=str(ROOT), env=env, stdout=log, stderr=subprocess.STDOUT,
                            start_new_session=True)
    try:
        deadline = time.time() + START_TIMEOUT_S
        while not (port_file.exists() and port_file.read_text().strip()):
            assert proc.poll() is None, (tmp / "server.log").read_text(errors="replace")[-2000:]
            assert time.time() < deadline, "dx_stream server never reported its port"
            time.sleep(0.2)
        yield f"http://127.0.0.1:{int(port_file.read_text().strip())}"
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=15)
        except subprocess.TimeoutExpired:
            proc.kill()
        log.close()


def _selected(demos: list[dict]) -> list[dict]:
    wanted = os.environ.get("DX_E2E_STREAM_DEMOS")
    ids = {int(x) for x in wanted.split(",")} if wanted else None
    return [d for d in demos if ids is None or d["id"] in ids]


@pytest.mark.e2e
@pytest.mark.e2e_npu
@pytest.mark.requires_dx_runtime
def test_every_stream_demo_produces_frames_on_the_npu(stream_server):
    from dx_stream.core import demos as demo_defs

    status, raw = _call(stream_server, "/api/demos")
    assert status == 200, raw[:300]
    listed = json.loads(raw)
    listed = listed if isinstance(listed, list) else listed.get("demos", [])
    rtsp_ok = os.environ.get("DX_E2E_STREAM_RTSP") == "1"
    failures, ran = [], []
    for demo in _selected(listed):
        did = demo["id"]
        if demo_defs.DEMOS[did].get("pipeline_type") == "rtsp" and not rtsp_ok:
            continue
        if not demo.get("available"):
            failures.append(f"demo {did}: listed as unavailable on a provisioned board")
            continue
        status, raw = _call(stream_server, f"/api/demos/{did}/start", {"forceMjpeg": True}, timeout=90)
        try:
            if status != 200 or not json.loads(raw).get("started"):
                failures.append(f"demo {did}: start {status} {raw[:200]!r}")
                continue
            first = json.loads(_call(stream_server, "/api/stream/stats")[1])["frames"]
            deadline, frames = time.time() + FRAME_WAIT_S, first
            while frames <= first + 5 and time.time() < deadline:
                time.sleep(0.5)
                frames = json.loads(_call(stream_server, "/api/stream/stats")[1])["frames"]
            if frames <= first + 5:
                failures.append(f"demo {did}: frames stalled at {frames}")
                continue
            status, jpeg = _call(stream_server, "/api/stream/snapshot")
            if status != 200 or not jpeg.startswith(b"\xff\xd8") or len(jpeg) < 2000:
                failures.append(f"demo {did}: snapshot {status}, {len(jpeg)} bytes")
                continue
            ran.append(did)
        finally:
            stop_status, _ = _call(stream_server, f"/api/demos/{did}/stop", {})
            if stop_status != 200:
                failures.append(f"demo {did}: stop returned {stop_status}")
    print(f"stream demos with live frames on the NPU: {ran}")
    assert ran, "no demo ran"
    assert not failures, "\n".join(failures)
    stats = json.loads(_call(stream_server, "/api/stream/stats")[1])
    assert not stats["streaming"], f"playback still running after stop: {stats}"
