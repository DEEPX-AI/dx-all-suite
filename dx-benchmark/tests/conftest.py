import pytest


@pytest.fixture(autouse=True)
def _no_real_dxtop_probe(monkeypatch):
    """Keep collect_fingerprint() from starting a real dxtop (~2 s, host-dependent)."""
    from benchmark import env_fingerprint
    monkeypatch.setattr(env_fingerprint, "_probe_npu_monitor",
                        lambda: {"ok": True, "reason": "stubbed in tests"})
