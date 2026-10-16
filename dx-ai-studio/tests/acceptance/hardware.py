"""What this machine can run for the acceptance suite: NPU, camera, dx_com, LLM, AWS, browser.

Stdlib only: scripts/acceptance.py imports it before any test runs, and the acceptance tests call
``need()`` so a test run directly with pytest says NOT RUN for the same reason instead of passing.
Each probe returns (available, detail); detail is the version found or the reason it is missing.
"""
from __future__ import annotations

import fcntl
import glob
import json
import os
import shutil
import struct
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUITE = ROOT.parent
KINDS = ("npu", "camera", "dx_com", "llm", "aws", "browser")
# dxcom writes several GB of intermediate files; with less free space a compile fails half way
# (and can fill the disk for everything else on the board).
DX_COM_MIN_FREE_GB = 8.0
_VIDIOC_QUERYCAP = 0x80685600
_V4L2_CAP_VIDEO_CAPTURE = 0x1
_V4L2_CAP_DEVICE_CAPS = 0x80000000


def _venv_python() -> str:
    exe = ROOT / ".venv" / "bin" / "python"
    return str(exe) if exe.exists() else sys.executable


def _run(cmd, timeout=30, **kw):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kw)
    except (OSError, subprocess.TimeoutExpired):
        return None


def probe_npu():
    devs = sorted(glob.glob("/dev/dxrt*"))
    if not devs:
        return False, "no NPU (/dev/dxrt* missing)"
    cli = shutil.which("dxrt-cli")
    if not cli:
        return True, f"{devs[0]} (dxrt-cli not on PATH)"
    out = _run([cli, "-s"], timeout=30)
    if out is None or out.returncode != 0:
        return False, f"{devs[0]} present but `dxrt-cli -s` failed"
    first = (out.stdout.strip().splitlines() or [""])[0]
    devices = [ln.strip(" *") for ln in out.stdout.splitlines() if "Device" in ln and ":" in ln]
    return True, ", ".join(filter(None, [first, *devices[:2]]))


def _is_capture_device(path: str) -> bool:
    try:
        fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
    except OSError:
        return False
    try:
        buf = fcntl.ioctl(fd, _VIDIOC_QUERYCAP, bytearray(104))
    except OSError:
        return False
    finally:
        os.close(fd)
    caps, device_caps = struct.unpack_from("<II", buf, 84)
    caps = device_caps if caps & _V4L2_CAP_DEVICE_CAPS else caps
    return bool(caps & _V4L2_CAP_VIDEO_CAPTURE)


def probe_camera():
    nodes = sorted(glob.glob("/dev/video*"))
    if not nodes:
        return False, "no camera (/dev/video* missing)"
    capture = [n for n in nodes if _is_capture_device(n)]
    if not capture:
        return False, f"no capture camera ({', '.join(nodes)} are not V4L2 capture devices)"
    return True, ", ".join(capture)


def probe_dx_com():
    code = ("import json; from dx_compiler.core.setup_service import SetupService; "
            "s = SetupService().check_status(); "
            "print(json.dumps({'ok': s['dx_com_installed'], 'v': s['dx_com_version']}))")
    out = _run([_venv_python(), "-c", code], timeout=120, cwd=str(ROOT),
               env={**os.environ, "PYTHONPATH": str(ROOT)})
    if out is None or out.returncode != 0:
        return False, "dx_com probe failed"
    try:
        got = json.loads(out.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return False, "dx_com probe gave no answer"
    if not got["ok"]:
        return False, "dx_com not installed (dx-compiler venv)"
    free_gb = shutil.disk_usage(str(ROOT)).free / 1e9
    if free_gb < DX_COM_MIN_FREE_GB:
        return False, (f"dx_com {got['v']} installed but only {free_gb:.1f} GB free disk "
                       f"(a compile needs {DX_COM_MIN_FREE_GB:.0f} GB)")
    return True, f"dx_com {got['v']}"


def real_chat_config_path() -> Path:
    """The user's own chat settings — tests run with a temp DX_CHAT_CONFIG_DIR, so read the real one."""
    real = os.environ.get("DX_ACCEPT_REAL_CHAT_CONFIG_DIR")
    return Path(real) / "chat_config.json" if real else Path.home() / ".dx-ai-studio" / "chat_config.json"


def probe_llm():
    path = real_chat_config_path()
    try:
        cfg = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False, "no LLM configured in Studio chat settings"
    provider = (cfg or {}).get("provider") or ""
    # A coding-agent CLI answers through a real CLI run, which tests never start
    # (DX_AGENT_NO_REAL_RUN); only a local or cloud endpoint is an LLM the suite can call.
    if not provider or provider in ("agent", "none") or cfg.get("kind") == "agent":
        return False, "no LLM endpoint configured in Studio chat settings (a coding-agent CLI is not used by tests)"
    return True, f"{provider} {cfg.get('model') or ''}".strip()


def probe_aws():
    out = _run([_venv_python(), "-c", "import boto3; print(boto3.__version__)"], timeout=60)
    if out is None or out.returncode != 0:
        return False, "no AWS credentials (boto3 not installed)"
    if os.environ.get("AWS_ACCESS_KEY_ID") or os.environ.get("AWS_PROFILE"):
        return True, f"boto3 {out.stdout.strip()}, credentials from the environment"
    home = Path.home() / ".aws"
    creds = home / "credentials"
    config = home / "config"
    text = ""
    for f in (creds, config):
        try:
            text += f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            pass
    if "aws_access_key_id" in text or "sso_" in text or "credential_process" in text:
        return True, f"boto3 {out.stdout.strip()}, profile in ~/.aws"
    return False, "no AWS credentials (no usable profile in ~/.aws)"


def probe_browser():
    try:
        import playwright  # noqa: F401
    except ImportError:
        return False, "playwright not installed"
    sys.path.insert(0, str(ROOT))
    try:
        from shared.chromium import resolve_chromium_executable
        exe = resolve_chromium_executable()
    except Exception:  # noqa: BLE001 - a missing helper only means "use Playwright's own"
        exe = None
    if exe:
        return True, f"chromium {exe}"
    cache = Path(os.environ.get("PLAYWRIGHT_BROWSERS_PATH") or Path.home() / ".cache" / "ms-playwright")
    if any(cache.glob("chromium*")):
        return True, f"playwright chromium ({cache})"
    return False, "no chromium for Playwright"


_PROBES = {"npu": probe_npu, "camera": probe_camera, "dx_com": probe_dx_com,
           "llm": probe_llm, "aws": probe_aws, "browser": probe_browser}


@lru_cache(maxsize=None)
def probe(kind: str):
    """(available, detail) for one kind. The runner exports DX_ACCEPT_HW so tests reuse its answers."""
    cached = os.environ.get("DX_ACCEPT_HW")
    if cached:
        try:
            got = json.loads(cached).get(kind)
        except ValueError:
            got = None
        if got:
            return bool(got[0]), str(got[1])
    return _PROBES[kind]()


def probe_all() -> dict:
    return {k: probe(k) for k in KINDS}


def need(*kinds: str) -> None:
    """Skip the calling test as NOT RUN when this machine lacks one of ``kinds``."""
    import pytest

    for kind in kinds:
        ok, detail = probe(kind)
        if not ok:
            pytest.skip(f"NOT RUN: {detail}")
