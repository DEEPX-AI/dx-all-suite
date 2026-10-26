"""The blocking suite must run without internet.

This file only checks that the guard works. Running the whole suite blocked is done by
`run_ci.sh --offline` — blocking sockets globally in one process would also kill tests that
**need** the network, so it is a separate stage.
"""
from __future__ import annotations

import socket
import urllib.error
import urllib.request

import pytest

from tests.offline_guard import no_external_network


def test_the_guard_blocks_the_outside():
    with no_external_network():
        with pytest.raises((OSError, urllib.error.URLError)):
            urllib.request.urlopen("https://developer.deepx.ai/", timeout=5)


def test_the_guard_leaves_localhost_alone():
    """Blocking 127.0.0.1 too would kill every test that starts a module server."""
    listener = socket.socket()
    listener.bind(("127.0.0.1", 0))
    listener.listen(1)
    try:
        with no_external_network():
            client = socket.socket()
            client.connect(listener.getsockname())
            client.close()
    finally:
        listener.close()


def test_it_puts_itself_back():
    """A guard left behind would make later tests fail for no visible reason."""
    before = socket.socket.connect
    with no_external_network():
        pass
    assert socket.socket.connect is before


def test_the_gate_flag_actually_blocks():
    """With `DX_OFFLINE_GUARD=1`, external calls are really blocked.

    Even with correct guard code, if conftest never turns it on the suite simply passes —
    not because calls are blocked but because none were made, which is false safety.
    The check only means something in a run with the flag set, so it skips otherwise.
    """
    import os

    if os.environ.get("DX_OFFLINE_GUARD") != "1":
        pytest.skip("가드가 꺼져 있다 — run_ci.sh --offline 이 켠다")

    with pytest.raises(Exception) as excinfo:
        urllib.request.urlopen("https://developer.deepx.ai/", timeout=5)
    assert "BLOCKED" in str(excinfo.value), (
        f"막히긴 했으나 가드가 아니다: {excinfo.value}"
    )
