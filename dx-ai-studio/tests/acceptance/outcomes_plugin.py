"""pytest plugin for scripts/acceptance.py: one JSON line per test with outcome, duration and reason.

Loaded with ``-p tests.acceptance.outcomes_plugin``; writes to $DX_ACCEPT_OUTCOMES. A skip is kept as
``skipped`` with its reason, so the runner reports NOT RUN rather than PASS.
"""
from __future__ import annotations

import json
import os

_seen: dict[str, dict] = {}


def _short(rep) -> str:
    if rep.skipped and isinstance(rep.longrepr, tuple):
        return str(rep.longrepr[2])
    text = getattr(rep, "longreprtext", "") or ""
    lines = [ln for ln in text.splitlines() if ln.startswith("E ")]
    return ("\n".join(lines[:6]) or text[-600:]).strip()


def pytest_runtest_logreport(report):
    rec = _seen.setdefault(report.nodeid, {"nodeid": report.nodeid, "outcome": "passed",
                                            "duration": 0.0, "reason": ""})
    rec["duration"] += report.duration
    if report.failed:
        rec["outcome"] = "failed" if report.when == "call" else "error"
        rec["reason"] = rec["reason"] or _short(report)
    elif report.skipped and rec["outcome"] == "passed":
        rec["outcome"] = "skipped"
        rec["reason"] = _short(report)


def pytest_collectreport(report):
    if report.failed:
        _seen.setdefault(report.nodeid or "<collection>", {
            "nodeid": report.nodeid or "<collection>", "outcome": "error", "duration": 0.0,
            "reason": _short(report)})


def pytest_sessionfinish(session, exitstatus):
    path = os.environ.get("DX_ACCEPT_OUTCOMES")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as fh:
        for rec in _seen.values():
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
