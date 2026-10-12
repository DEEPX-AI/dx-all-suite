"""The Agent Dev console attaches to a run it did not start.

`Open in DX Agent Dev` promises to take over a run started from home; passing only `#ask=<text>`
leaves the console unaware of the running job, so nothing appears to happen.

The server owns the run (`run_id` in `/api/agent/status`, `/api/agent/run/events`). These tests
check that the console **uses** that.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "dx_agent_dev" / "static" / "js" / "console.js"


def source() -> str:
    assert SRC.is_file(), "console.js가 없습니다"
    return SRC.read_text(encoding="utf-8")


def test_the_console_knows_how_to_attach():
    src = source()
    assert "/api/agent/run/events" in src, (
        "콘솔이 붙는 경로를 모른다 — 시작한 실행만 볼 수 있다"
    )


def test_it_attaches_on_load_not_only_on_submit():
    """Without a check on open, a user who navigated here sees nothing."""
    src = source()
    m = re.search(r"async function checkStatus\(\)\s*\{(.*?)\n  \}", src, re.S)
    assert m, "checkStatus를 찾을 수 없다"
    assert "run_id" in m.group(1) or "attachIfRunning" in m.group(1), (
        "열릴 때 진행 중인 실행을 확인하지 않는다"
    )


def test_the_stream_reader_is_shared_between_start_and_attach():
    """If the attach path rendered separately, "taking over" would not be real."""
    src = source()
    assert src.count("getReader()") <= 1, (
        "스트림 소비가 두 벌이다 — 시작과 붙기가 갈라진다"
    )
