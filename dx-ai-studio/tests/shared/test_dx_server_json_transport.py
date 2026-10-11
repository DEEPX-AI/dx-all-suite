"""Large JSON API responses are compressed and revalidated (2026-10-11 performance audit).

The launcher shell fetches /zoo/api/catalog on every screen to draw home's module counts. That is 2.5 MB of JSON sent
uncompressed and without a validator, so every visit downloaded all of it again. Model Zoo fetched it twice. Over
remote access (pairing) every screen paid that cost. send_json now gzips a large 200 body for clients that accept it,
and it adds a content ETag with no-cache, so a repeat request revalidates to a 304. Small and non-200 bodies stay as
they were.
"""
from __future__ import annotations

import gzip
import http.client
import json
import threading
from http.server import ThreadingHTTPServer

import pytest

from shared.dx_server import DXBaseHandler

BIG = {"models": [{"name": f"model-{i}", "task": "object_detection", "notes": "x" * 40} for i in range(2000)]}
SMALL = {"ok": True}


class JsonHandler(DXBaseHandler):
    server_name = "JsonTransportTest"
    log_silent = True
    state = {"big": BIG}

    def route(self):
        if self.url_path == "/big":
            return self.send_json(self.state["big"])
        if self.url_path == "/small":
            return self.send_json(SMALL)
        if self.url_path == "/big-error":
            return self.send_json(BIG, 500)
        self.send_error(404)


@pytest.fixture()
def port():
    server = ThreadingHTTPServer(("127.0.0.1", 0), JsonHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield server.server_address[1]
    finally:
        JsonHandler.state["big"] = BIG
        server.shutdown()
        server.server_close()


def _get(port, path, headers=None):
    conn = http.client.HTTPConnection("127.0.0.1", port, timeout=10)
    conn.request("GET", path, headers=headers or {})
    resp = conn.getresponse()
    body = resp.read()
    conn.close()
    return resp, body


def test_a_large_body_is_gzipped_for_a_client_that_accepts_it(port):
    resp, body = _get(port, "/big", {"Accept-Encoding": "gzip, deflate"})
    assert resp.status == 200
    assert resp.getheader("Content-Encoding") == "gzip"
    assert "Accept-Encoding" in (resp.getheader("Vary") or "")
    assert int(resp.getheader("Content-Length")) == len(body)
    assert json.loads(gzip.decompress(body)) == BIG
    assert len(body) * 5 < len(json.dumps(BIG))


def test_a_client_without_gzip_gets_plain_json(port):
    resp, body = _get(port, "/big")
    assert resp.status == 200
    assert resp.getheader("Content-Encoding") is None
    assert json.loads(body) == BIG


def test_a_repeat_request_revalidates_to_304(port):
    first, _ = _get(port, "/big", {"Accept-Encoding": "gzip"})
    etag = first.getheader("ETag")
    assert etag and first.getheader("Cache-Control") == "no-cache"
    again, body = _get(port, "/big", {"Accept-Encoding": "gzip", "If-None-Match": etag})
    assert again.status == 304 and body == b""
    assert again.getheader("Content-Length") is None
    assert again.getheader("ETag") == etag


def test_changed_data_gets_a_new_etag_and_a_full_body(port):
    first, _ = _get(port, "/big")
    etag = first.getheader("ETag")
    JsonHandler.state["big"] = {"models": BIG["models"][:-1]}
    again, body = _get(port, "/big", {"If-None-Match": etag})
    assert again.status == 200 and again.getheader("ETag") != etag
    assert len(json.loads(body)["models"]) == len(BIG["models"]) - 1


def test_small_and_error_bodies_are_unchanged(port):
    resp, body = _get(port, "/small", {"Accept-Encoding": "gzip"})
    assert resp.getheader("Content-Encoding") is None and resp.getheader("ETag") is None
    assert json.loads(body) == SMALL
    resp, body = _get(port, "/big-error", {"Accept-Encoding": "gzip"})
    assert resp.status == 500 and resp.getheader("Content-Encoding") is None and resp.getheader("ETag") is None
    assert json.loads(body) == BIG
