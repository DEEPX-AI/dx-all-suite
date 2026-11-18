"""NPU sanity check in Deep Diagnostics: password-free unless sudo is needed, judged by its text."""
from dx_app.core import setup_steps


class R:
    def __init__(self, code=0, out=""):
        self.returncode, self.stdout, self.stderr = code, out, ""


def test_without_sudo_the_row_is_pending(monkeypatch):
    monkeypatch.setattr(setup_steps.subprocess, "run", lambda *a, **k: R(1))
    assert setup_steps.npu_sanity()["state"] == "needs_password"


def test_pass_and_fail_are_read_from_the_text(monkeypatch):
    outs = iter([R(0), R(0, "x\n** Sanity check PASSED!\n")])
    monkeypatch.setattr(setup_steps.subprocess, "run", lambda *a, **k: next(outs))
    assert setup_steps.npu_sanity()["state"] == "passed"
    # exit code 0 but FAILED text → failed (never trust the exit code)
    outs = iter([R(0), R(0, "[ERROR] Fail to initialize device\n** Sanity check FAILED!\n")])
    monkeypatch.setattr(setup_steps.subprocess, "run", lambda *a, **k: next(outs))
    r = setup_steps.npu_sanity()
    assert r["state"] == "failed" and "initialize device" in r["detail"] and "cold boot" in r["fix"]["en"]


def test_pending_row_does_not_count_as_a_failure(monkeypatch):
    monkeypatch.setattr(setup_steps, "npu_sanity", lambda password=None: {"state": "needs_password"})
    d = setup_steps.deep_diagnostics()
    row = next(c for c in d["checks"] if c["id"] == "npu_sanity")
    assert row["pending"] is True
    assert d["total"] == sum(1 for c in d["checks"] if not c.get("pending"))
