"""SDKREQ-482 [Common] start-up, access and Health — against a real ./launcher.sh studio.

Module lists come from the launcher (its proxy map and /api/health), so a ninth or tenth module is
checked without editing this file. The watchdog checks kill only a module server that this test's own
launcher started (its PID comes from the launcher's pid file in the test's run dir).
"""
from __future__ import annotations

import os
import re
import signal
import time

from tests.acceptance.conftest import http_get, http_json, module_frame, wait_home

LEGACY_FIXED_PORTS = set(range(8080, 8100))
# The module the watchdog checks kill: light to restart, nothing else depends on it.
VICTIM = ("dx_benchmark", "benchmark", "benchmark")      # server id, health key, launcher JS key


def _proxy_paths() -> dict:
    from launcher.launcher import _MODULE_PROXY_PATHS

    return dict(_MODULE_PROXY_PATHS)


def test_every_module_runs_on_an_ephemeral_port_found_by_the_port_file_handshake(studio):
    mods = studio.modules()
    assert len(mods) == len(_proxy_paths()), (mods, _proxy_paths())
    reported = {p.stem: int(p.read_text().strip()) for p in (studio.run_dir / ".ports").glob("*.port")}
    assert len(reported) == len(mods), reported
    for key, st in mods.items():
        assert st["alive"], (key, st)
        assert st["port"] not in LEGACY_FIXED_PORTS, (key, st)
        assert st["port"] in reported.values(), (key, st, reported)
    assert studio.port not in reported.values()


def test_every_module_proxy_path_serves_its_page(studio):
    for server_id, prefix in _proxy_paths().items():
        status, headers, body = http_get(studio.base + prefix, timeout=30,
                                         headers={"Sec-Fetch-Dest": "iframe", "Accept": "text/html"})
        assert status == 200, (server_id, prefix, status)
        assert "text/html" in headers.get("Content-Type", ""), (server_id, headers)
        assert b"<html" in body[:4000].lower(), (server_id, body[:200])
    # A top-level visit to a module path gets the launcher shell, which then opens the module.
    status, _, body = http_get(studio.base + "/zoo/", headers={"Sec-Fetch-Dest": "document", "Accept": "text/html"})
    assert status == 200 and b"studioGrid" in body


def test_health_api_reports_launcher_boot_and_every_module(studio):
    status, h = http_json(studio.base + "/api/health")
    assert status == 200
    assert re.fullmatch(rf"{studio.port}-\d+", h["launcher_boot"] or ""), h["launcher_boot"]
    assert int(h["launcher_boot"].split("-")[1]) == studio.proc.pid
    assert h["studio_ready"] is True
    mods = {k: v for k, v in h.items() if isinstance(v, dict)}
    assert len(mods) == len(_proxy_paths())
    for key, st in mods.items():
        assert set(st) >= {"port", "alive"} and st["alive"] is True and isinstance(st["port"], int), (key, st)


def _module_status(studio, key):
    return http_json(studio.base + f"/api/modules/{key}/status")[1]


def _victim_pid(studio) -> int:
    # The pid file names a module by its display name at boot and by its server id after a restart.
    from launcher.launcher import _CANONICAL_TO_DISPLAY_NAME

    pids = studio.module_pids()
    pid = pids.get(VICTIM[0]) or pids.get(_CANONICAL_TO_DISPLAY_NAME[VICTIM[0]])
    assert pid, pids
    return int(pid)


def _kill_victim(studio) -> int:
    pid = _victim_pid(studio)
    assert pid in studio.started_pids
    os.kill(pid, signal.SIGKILL)
    return pid


def _wait_status(studio, key, want, timeout):
    deadline = time.monotonic() + timeout
    seen = []
    while time.monotonic() < deadline:
        st = _module_status(studio, key)
        if not seen or seen[-1] != st.get("status"):
            seen.append(st.get("status"))
        if st.get("status") in ((want,) if isinstance(want, str) else want):
            return st, seen
        time.sleep(0.5)
    raise AssertionError(f"{key} never became {want!r} in {timeout}s; went through {seen}")


def test_watchdog_restarts_a_killed_module_on_a_new_port_within_120s(studio):
    key = VICTIM[1]
    before = _module_status(studio, key)
    assert before["status"] == "alive", before
    t0 = time.monotonic()
    old_pid = _kill_victim(studio)
    dead, _ = _wait_status(studio, key, "dead", 30)
    after, _ = _wait_status(studio, key, "alive", 120)
    took = time.monotonic() - t0
    assert took <= 120, took
    assert after["port"] != before["port"] and after["restart_count"] >= 1, (before, after)
    new_pid = _victim_pid(studio)
    assert new_pid != old_pid
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline and studio.health()[key]["port"] != after["port"]:
        time.sleep(0.5)
    assert studio.health()[key] == {"port": after["port"], "alive": True}
    assert http_get(studio.base + "/benchmark/", headers={"Sec-Fetch-Dest": "iframe"})[0] == 200


def test_watchdog_gives_up_after_three_restarts_and_the_user_can_retry(studio, pages):
    """After 3 restarts in 120 s the module is 'unavailable'; the launcher shows Retry, which brings it back."""
    key = VICTIM[1]
    for _ in range(5):
        st, _ = _wait_status(studio, key, ("alive", "unavailable"), 120)
        if st["status"] == "unavailable":
            break
        _kill_victim(studio)
        _wait_status(studio, key, ("dead", "unavailable"), 30)
    st, _ = _wait_status(studio, key, "unavailable", 60)
    assert "Max restarts (3)" in (st.get("last_error") or ""), st

    page = pages.new("/")
    wait_home(page)
    page.evaluate("(k) => DXLauncher.launch(k)", VICTIM[2])
    retry = page.locator(".module-entry-error .module-retry-btn")
    retry.wait_for(timeout=60000)
    assert "could not be recovered" in page.locator(".module-entry-error").inner_text()
    retry.click()
    _wait_status(studio, key, "alive", 60)
    module_frame(page, VICTIM[2], timeout=60000)
