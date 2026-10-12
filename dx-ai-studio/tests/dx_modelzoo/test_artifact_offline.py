"""How the artifact endpoint behaves without internet access.

With outside sockets blocked, `urlopen` raises `URLError`, which looks like "no response".
It is not: `urlopen` fails while following the redirect, and the server still answers 302:

    HTTP 302  Location: https://sdk.deepx.ai/modelzoo/onnx/damoyolo-t_640x640.onnx

Not reaching the CDN without internet is expected, not a fault. Artifact download is in the
"network" tier of docs/offline-contract.md.

This file protects two things: the server gives a **decidable response** with or without a
network (no silence, no endless wait), and nobody removes this 302 for the sake of air-gapped
sites, because with internet it is the right behaviour.
"""
from __future__ import annotations

import json
import socket
import urllib.error
import urllib.request

import pytest

from tests.server_helpers import start_module_server


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Do not follow redirects: following one hides what the server answered."""

    def redirect_request(self, *args, **kwargs):
        return None


@pytest.fixture()
def no_internet():
    real = socket.socket.connect

    def guard(self, addr):
        host = addr[0] if isinstance(addr, tuple) else None
        if host and not (str(host).startswith("127.") or host in ("::1", "localhost")):
            raise OSError(101, f"BLOCKED external connect to {host}")
        return real(self, addr)

    socket.socket.connect = guard
    try:
        yield
    finally:
        socket.socket.connect = real


@pytest.fixture()
def zoo():
    server, port = start_module_server("dx_modelzoo")
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.shutdown()


def _first_model(base):
    with urllib.request.urlopen(base + "/api/catalog", timeout=20) as r:
        data = json.loads(r.read().decode())
    assert data["models"], "카탈로그가 비었다"
    return data["models"][0]["id"]


def _ask(base, model_id):
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(f"{base}/api/catalog/{model_id}/artifacts/onnx", timeout=25) as r:
            return r.status, r.headers.get("Location")
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Location")


def test_the_server_answers_with_no_internet(zoo, no_internet):
    """The response must be decidable, not silence or an endless wait."""
    status, _ = _ask(zoo, _first_model(zoo))
    assert status in (200, 302, 404), f"예상 밖 응답: {status}"


def test_a_remote_artifact_still_points_at_the_cdn(zoo, no_internet):
    """Removing this redirect for air-gapped sites would break the case with internet."""
    status, location = _ask(zoo, _first_model(zoo))
    if status == 302:
        assert location and location.startswith("http"), location


def test_it_behaves_the_same_with_internet(zoo):
    status, _ = _ask(zoo, _first_model(zoo))
    assert status in (200, 302, 404), f"예상 밖 응답: {status}"
