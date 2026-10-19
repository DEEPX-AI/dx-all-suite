"""A guard that blocks external sockets and keeps localhost open.

The studio is deployed on air-gapped networks, so code that depends on the internet is a
product defect; this guard makes such code fail in the suite. Tiers: docs/offline-contract.md.

Leaving localhost open is the point: tests start module servers and talk to them on 127.0.0.1,
and blocking that would stop everything. Only the outside is blocked.
"""
from __future__ import annotations

import socket
from contextlib import contextmanager

_LOCAL = ("127.", "::1", "localhost", "0.0.0.0")


def _is_local(host) -> bool:
    if host is None:
        return True
    h = str(host)
    return h.startswith("127.") or h in ("::1", "localhost", "0.0.0.0")


@contextmanager
def no_external_network():
    """Inside this block, outgoing TCP connections to external hosts raise OSError."""
    real = socket.socket.connect

    def guard(self, address):
        host = address[0] if isinstance(address, tuple) else None
        if not _is_local(host):
            raise OSError(
                101,
                f"BLOCKED external connect to {host} — "
                "docs/offline-contract.md 를 보고 이 호출이 어느 등급인지 정하세요",
            )
        return real(self, address)

    socket.socket.connect = guard
    try:
        yield
    finally:
        socket.socket.connect = real


_installed = False


def install() -> None:
    """Install the guard for the whole process (never undone).

    Calling only `__enter__` on `no_external_network()` and dropping the reference lets the
    generator be collected, which runs `finally` and lifts the guard — the suite would then pass
    without being guarded at all. The setting must hold for the whole session, so use this
    function rather than the context manager.
    """
    global _installed
    if _installed:
        return
    real = socket.socket.connect

    def guard(self, address):
        host = address[0] if isinstance(address, tuple) else None
        if not _is_local(host):
            raise OSError(
                101,
                f"BLOCKED external connect to {host} — "
                "docs/offline-contract.md 를 보고 이 호출이 어느 등급인지 정하세요",
            )
        return real(self, address)

    socket.socket.connect = guard
    _installed = True
