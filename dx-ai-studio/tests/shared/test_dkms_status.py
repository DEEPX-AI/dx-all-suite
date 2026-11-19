"""DKMS check asks for the DX-RT driver module only.

A bare `dkms status` walks every DKMS module on every installed kernel. On a Raspberry Pi with v4l2loopback and
seven kernels it took 6.5 s (the driver module alone: 0.8 s), so DX Stream's /api/diagnostics outran a 5 s client.
Falls back to the full listing when the module query finds nothing (older packages named the module differently).
"""
from __future__ import annotations

import subprocess

from shared import dxrt

DXRT_LINE = "dxrt-driver-dkms/2.7.0-2, 6.8.0-149-generic, aarch64: installed"


def _fake(monkeypatch, answers):
    calls = []

    def run(argv, *a, **k):
        calls.append(argv)
        out = answers.get(tuple(argv), "")
        return subprocess.CompletedProcess(argv, 0, out, "")

    monkeypatch.setattr(dxrt.subprocess, "run", run)
    return calls


def test_queries_only_the_driver_module(monkeypatch):
    calls = _fake(monkeypatch, {("dkms", "status", "-m", "dxrt-driver-dkms"): DXRT_LINE + "\n"})
    rc, out = dxrt.dkms_dxrt_status()
    assert (rc, out) == (0, DXRT_LINE)
    assert calls == [["dkms", "status", "-m", "dxrt-driver-dkms"]]


def test_falls_back_to_the_full_listing(monkeypatch):
    full = "v4l2loopback/0.12.7, 6.8.0-149-generic, aarch64: installed\ndeepx/1.0, 6.8.0, x86_64: installed"
    calls = _fake(monkeypatch, {("dkms", "status"): full})
    rc, out = dxrt.dkms_dxrt_status()
    assert rc == 0 and out == full
    assert calls == [["dkms", "status", "-m", "dxrt-driver-dkms"], ["dkms", "status"]]


def test_missing_dkms_is_reported(monkeypatch):
    def run(argv, *a, **k):
        raise FileNotFoundError("dkms")

    monkeypatch.setattr(dxrt.subprocess, "run", run)
    assert dxrt.dkms_dxrt_status() == (-1, "")


def test_both_diagnostics_use_it(monkeypatch):
    from dx_stream.core import diagnostics
    from dx_app.core import setup_steps
    seen = []
    monkeypatch.setattr(dxrt, "dkms_dxrt_status", lambda: seen.append(1) or (0, DXRT_LINE))
    assert diagnostics._check_dkms()["ok"] is True
    assert setup_steps._dkms_check()["ok"] is True
    assert len(seen) == 2
