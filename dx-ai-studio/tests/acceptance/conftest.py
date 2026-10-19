"""Acceptance (SQA) fixtures: one real Studio per test file, started the way a user starts it.

``studio`` runs ``./launcher.sh --no-kill --port <free> --fast --no-browser`` as a child process, so
every module is a real server behind the real launcher proxy, on OS-assigned ports. It never touches
another running studio:

* ``--no-kill``: launcher.sh otherwise pkills every studio server on the machine.
* ``DX_LAUNCHER_RUN_DIR`` / ``XDG_STATE_HOME``: port handshake files, pid file and module logs go to a
  temp dir, so a studio already running from this checkout keeps its own.
* ``.launcher-port`` / ``.launcher-url`` (written by launcher.sh) are put back afterwards.
* Teardown stops the launcher, then only the module PIDs this launcher wrote to its own pid file.

A test file may set ``LAUNCHER_ENV = {...}`` for extra environment (e.g. a mock agent adapter).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

from tests.acceptance.hardware import ROOT, need

QUIET = ("try{sessionStorage.setItem('dx-splash-seen','1');localStorage.setItem('dx-splash-seen','1');"
         "sessionStorage.setItem('dx-home-entered','1');}catch(e){}")
NO_LAUNCHER_TOUR = "localStorage.setItem('dx-tutorial-launcher-autostarted','1');"
BOOT_TIMEOUT = 240


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def http_get(url: str, timeout: float = 15, headers: dict | None = None, follow: bool = True):
    """(status, headers, body bytes) — HTTP errors are returned, not raised. follow=False reports a redirect."""
    req = urllib.request.Request(url, headers=headers or {})
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        if 300 <= e.code < 400:          # the redirect itself is the answer; its body is not needed
            e.close()
            return e.code, dict(e.headers), b""
        return e.code, dict(e.headers), e.read()


def http_json(url: str, timeout: float = 15):
    status, _, body = http_get(url, timeout)
    return status, json.loads(body or b"null")


class Studio:
    def __init__(self, port: int, run_dir: Path, proc: subprocess.Popen, log: Path):
        self.port = port
        self.base = f"http://127.0.0.1:{port}"
        self.run_dir = run_dir
        self.proc = proc
        self.log = log
        self.started_pids: set[int] = set()

    def health(self) -> dict:
        # /api/health is cached for 2 s on the server; module status reads the watchdog directly.
        return http_json(self.base + "/api/health")[1]

    def modules(self) -> dict:
        """The launcher's own module registry: health key -> {port, alive}. A new module shows up here."""
        return {k: v for k, v in self.health().items() if isinstance(v, dict) and "alive" in v}

    def launcher_output(self) -> str:
        return self.log.read_text(encoding="utf-8", errors="replace")

    def module_pids(self) -> dict:
        """Display name -> PID of the module servers THIS launcher started (its own pid file)."""
        try:
            data = json.loads((self.run_dir / ".launcher_pids").read_text())
        except (OSError, ValueError):
            return {}
        self.started_pids.update(int(p) for p in data.values())
        return data


def _wait_ready(studio: Studio) -> None:
    deadline = time.monotonic() + BOOT_TIMEOUT
    last = None
    while time.monotonic() < deadline:
        if studio.proc.poll() is not None:
            raise RuntimeError(f"launcher exited ({studio.proc.returncode}):\n{studio.launcher_output()[-3000:]}")
        try:
            h = studio.health()
            mods = {k: v for k, v in h.items() if isinstance(v, dict)}
            last = h
            if h.get("studio_ready") and mods and all(v.get("alive") for v in mods.values()):
                return
        except OSError:
            pass
        time.sleep(1)
    raise RuntimeError(f"studio not ready in {BOOT_TIMEOUT}s: {last}\n{studio.launcher_output()[-3000:]}")


def _output_entries() -> set[Path]:
    """What is under outputs/ now: the result files, videos and graph runs the studio writes."""
    out = ROOT / "outputs"
    found = set()
    for parent in [out, *out.glob("*"), *out.glob("*/graph/runs")]:
        if parent.is_dir():
            found.update(parent.iterdir())
    return found


def _remove_new_outputs(before: set[Path]) -> None:
    """Delete what this studio's checks wrote to outputs/ (inference results, demo videos, graph runs)."""
    for path in sorted(_output_entries() - before, key=lambda p: len(p.parts), reverse=True):
        if path.is_dir() and path.parent.name in ("runs",):
            shutil.rmtree(path, ignore_errors=True)
        elif path.is_file() and path.name.startswith("result_"):
            path.unlink(missing_ok=True)


def _is_ours(pid: int) -> bool:
    try:
        cmd = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return False
    return str(ROOT) in cmd and "server.py" in cmd


@pytest.fixture(scope="module")
def studio(request):
    extra = dict(getattr(request.module, "LAUNCHER_ENV", {}) or {})
    base_tmp = os.environ.get("DX_ACCEPT_TMP") or "/dev/shm"
    work = Path(tempfile.mkdtemp(prefix="dx-accept-", dir=base_tmp if Path(base_tmp).is_dir() else None))
    run_dir = work / "run"
    run_dir.mkdir()
    sticky = {name: (ROOT / name).read_bytes() if (ROOT / name).exists() else None
              for name in (".launcher-port", ".launcher-url")}
    before_outputs = _output_entries()
    port = _free_port()
    env = {**os.environ, **extra,
           "DX_LAUNCHER_RUN_DIR": str(run_dir), "XDG_STATE_HOME": str(work / "state"),
           "DX_BIND_LOCAL": "1", "PYTHONUNBUFFERED": "1", "DX_NO_BROWSER": "1"}
    log = work / "launcher.out"
    with open(log, "wb") as out:
        proc = subprocess.Popen(["bash", str(ROOT / "launcher.sh"), "--no-kill", "--port", str(port), "--fast",
                                 "--no-browser"], cwd=str(ROOT), env=env, stdout=out, stderr=subprocess.STDOUT,
                                start_new_session=True)
    s = Studio(port, run_dir, proc, log)
    try:
        _wait_ready(s)
        s.module_pids()
        yield s
    finally:
        s.module_pids()
        if proc.poll() is None:
            proc.send_signal(signal.SIGTERM)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=10)
        for pid in s.started_pids:          # only what this launcher started
            if _is_ours(pid):
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
        _remove_new_outputs(before_outputs)
        for name, data in sticky.items():
            path = ROOT / name
            if data is None:
                path.unlink(missing_ok=True)
            else:
                path.write_bytes(data)
        shutil.rmtree(work, ignore_errors=True)


@pytest.fixture(scope="module")
def browser(studio):
    need("browser")
    from playwright.sync_api import sync_playwright

    from tests.browser_support import launch_browser

    pw = sync_playwright().start()
    br = launch_browser(pw, "chromium")
    try:
        yield br
    finally:
        br.close()
        pw.stop()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


class Pages:
    """New browser contexts on the studio; failed tests leave one screenshot per page."""

    def __init__(self, studio, browser, request):
        self.studio, self.browser, self.request = studio, browser, request
        self.opened = []
        self.errors: list[str] = []

    def new(self, path="/", lang="en", tutorial="off", width=1440, height=900, quiet=True, launcher_tour=False,
            wait="domcontentloaded"):
        ctx = self.browser.new_context(viewport={"width": width, "height": height})
        # Settings are seeded once per tab, so a reload shows what the user's own clicks left behind.
        seed = "" if launcher_tour else NO_LAUNCHER_TOUR
        if lang:
            seed += f"localStorage.setItem('dx-lang','{lang}');"
        if tutorial is None:
            seed += "localStorage.removeItem('dx-tutorial-mode');"
        else:
            seed += f"localStorage.setItem('dx-tutorial-mode','{tutorial}');"
        script = (QUIET if quiet else "") + (
            "try{if(!sessionStorage.getItem('dx-accept-seeded')){" + seed +
            "sessionStorage.setItem('dx-accept-seeded','1');}}catch(e){}")
        ctx.add_init_script(script)
        page = ctx.new_page()
        page.on("pageerror", lambda e: self.errors.append(str(e)))
        self.opened.append((ctx, page))
        if path is not None:
            page.goto(self.studio.base + path, wait_until=wait, timeout=60000)
        return page

    def close(self):
        failed = getattr(self.request.node, "rep_call", None)
        art = os.environ.get("DX_ACCEPT_ARTIFACTS")
        for i, (ctx, page) in enumerate(self.opened):
            if failed is not None and failed.failed and art:
                Path(art).mkdir(parents=True, exist_ok=True)
                name = re.sub(r"[^A-Za-z0-9_.-]+", "_", self.request.node.nodeid)[-150:]
                try:
                    page.screenshot(path=str(Path(art) / f"{name}.{i}.png"))
                except Exception:  # noqa: BLE001 - a screenshot is a courtesy, never the failure
                    pass
            ctx.close()


@pytest.fixture()
def pages(studio, browser, request):
    p = Pages(studio, browser, request)
    try:
        yield p
    finally:
        p.close()


def wait_home(page, timeout=60000):
    page.wait_for_function("window.DXLauncher && DXLauncher._studioReadyResolved === true", timeout=timeout)
    page.locator("#studioGrid .orbital-card").first.wait_for(state="visible", timeout=timeout)


def module_frame(page, key: str, timeout=60000, ready: str = "#dxToolbar, .toolbar"):
    """The Frame of module ``key``'s iframe inside the launcher, once its page has loaded."""
    sel = f'iframe.module-iframe[data-app="{key}"]'
    page.wait_for_function(
        "(s) => { const f = document.querySelector(s); return f && f.contentDocument && "
        "f.contentDocument.readyState === 'complete' && f.contentWindow.location.href !== 'about:blank'; }",
        arg=sel, timeout=timeout)
    frame = page.locator(sel).element_handle().content_frame()
    if ready:
        frame.wait_for_selector(ready, state="attached", timeout=timeout)
    return frame


def open_module(pages, key: str, lang="en", tutorial="off", **kw):
    """Open module ``key`` the way a user does: its launcher route (/app, /zoo …) in a fresh tab."""
    page = pages.new("/", lang=lang, tutorial=tutorial, **kw)
    wait_home(page)
    path = page.evaluate("(k) => DXLauncher.APP_PATHS[k]", key)
    assert path, f"{key} is not in the launcher's module registry"
    page.evaluate("(k) => DXLauncher.launch(k)", key)
    return page, module_frame(page, key)
