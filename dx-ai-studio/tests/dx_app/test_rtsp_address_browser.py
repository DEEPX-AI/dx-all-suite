"""DX App RTSP input takes the camera's own URL (2026-10-11 real-use audit).

Run / Benchmark / A/B Compare asked for "RTSP Server (IP:Port)" plus a "Stream 1-16" pick and always sent
rtsp://<server>/streamN, so a real camera (rtsp://user:pass@cam:554/cam/realmonitor?channel=1, /h264, /live/ch0 ...)
could not be reached; an empty field sent rtsp:///stream1 and failed later without saying why. A full rtsp:// URL is
now used as typed (the Stream pick steps aside), host:port alone keeps the old form, and an empty field stops at once.
"""
from __future__ import annotations

import pytest

pytest.importorskip("playwright.sync_api")

from tests.server_helpers import start_module_server  # noqa: E402

CAM = "rtsp://admin:pw@192.168.0.64:554/cam/realmonitor?channel=1&subtype=0"


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    srv, port = start_module_server("dx_app")
    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    ctx = br.new_context(viewport={"width": 1440, "height": 900})
    ctx.add_init_script("try{localStorage.setItem('dx-tutorial-mode','off');localStorage.setItem('dx-lang','en')}catch(e){}")
    pg = ctx.new_page()
    pg.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
    yield pg
    ctx.close()
    br.close()
    pw.stop()
    srv.shutdown()


@pytest.mark.parametrize("prefix", ["c", "b", "ab"])
def test_a_full_camera_url_is_sent_as_typed(page, prefix):
    page.evaluate("p => { initRTSPStreams(p + '-rtsp-stream'); }", prefix)
    page.evaluate("([p, v]) => { const el = document.getElementById(p + '-rtsp-ip'); el.value = v;"
                  " el.dispatchEvent(new Event('input', {bubbles: true})); }", [prefix, CAM])
    assert page.evaluate("p => buildRTSPUrl(p + '-rtsp-ip', p + '-rtsp-stream')", prefix) == CAM
    assert page.evaluate("p => document.getElementById(p + '-rtsp-stream').disabled", prefix)


@pytest.mark.parametrize("prefix", ["c", "b", "ab"])
def test_host_and_port_keep_the_stream_form(page, prefix):
    page.evaluate("p => { initRTSPStreams(p + '-rtsp-stream'); }", prefix)
    page.evaluate("([p, v]) => { const el = document.getElementById(p + '-rtsp-ip'); el.value = v;"
                  " el.dispatchEvent(new Event('input', {bubbles: true})); }", [prefix, "10.0.0.5:8554"])
    page.evaluate("p => { document.getElementById(p + '-rtsp-stream').value = 'stream3'; }", prefix)
    assert page.evaluate("p => buildRTSPUrl(p + '-rtsp-ip', p + '-rtsp-stream')", prefix) == "rtsp://10.0.0.5:8554/stream3"
    assert not page.evaluate("p => document.getElementById(p + '-rtsp-stream').disabled", prefix)


def test_an_empty_address_stops_the_benchmark_before_running(page):
    runs = []
    page.route("**/api/run", lambda r: (runs.append(r.request.post_data), r.fulfill(status=200, body="{}")))
    try:
        page.evaluate("nav('bench')")
        page.select_option("#b-input-type", "rtsp")
        page.fill("#b-rtsp-ip", "")
        page.wait_for_selector(".b-chk", state="attached", timeout=10000)
        page.evaluate("document.querySelector('.b-chk').checked = true")
        page.evaluate("doBench()")
        page.wait_for_timeout(500)
        assert runs == []
        assert "RTSP" in page.inner_text("#toast-container, .toast-container, body")
    finally:
        page.unroute("**/api/run")
