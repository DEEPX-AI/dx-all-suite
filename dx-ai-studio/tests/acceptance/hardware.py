"""What this machine can run for the acceptance suite: NPU, camera, dx_com, LLM, AWS, browser, and the DEEPX SDK
pieces a prepared board has (dx_app built with models, dx-runtime, dx-compiler).

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
KINDS = ("npu", "camera", "dx_com", "llm", "aws", "browser", "dx_app", "dx_rt", "dx_compiler")
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


def _capture_state(path: str) -> str:
    """"capture" for a V4L2 video-capture node, "denied" when this user may not open it, else "other"."""
    try:
        fd = os.open(path, os.O_RDWR | os.O_NONBLOCK)
    except PermissionError:
        return "denied"
    except OSError:
        return "other"
    # A mutable buffer is filled in place; fcntl.ioctl then returns the ioctl's int result, not the buffer.
    buf = bytearray(104)
    try:
        fcntl.ioctl(fd, _VIDIOC_QUERYCAP, buf)
    except OSError:
        return "other"
    finally:
        os.close(fd)
    caps, device_caps = struct.unpack_from("<II", buf, 84)
    caps = device_caps if caps & _V4L2_CAP_DEVICE_CAPS else caps
    return "capture" if caps & _V4L2_CAP_VIDEO_CAPTURE else "other"


def _is_capture_device(path: str) -> bool:
    return _capture_state(path) == "capture"


def probe_camera():
    nodes = sorted(glob.glob("/dev/video*"))
    if not nodes:
        return False, "no camera (/dev/video* missing)"
    states = {node: _capture_state(node) for node in nodes}
    capture = [n for n, state in states.items() if state == "capture"]
    if capture:
        return True, ", ".join(capture)
    denied = [n for n, state in states.items() if state == "denied"]
    if denied:
        return False, f"no usable camera: permission denied ({', '.join(denied)})"
    return False, f"no capture camera ({', '.join(nodes)} are not V4L2 capture devices)"


def _studio_answer(code: str, timeout: int = 120):
    """The last line of `code` run by Studio's venv in Studio's root, parsed as JSON; None when it gave no answer."""
    out = _run([_venv_python(), "-c", code], timeout=timeout, cwd=str(ROOT),
               env={**os.environ, "PYTHONPATH": str(ROOT)})
    if out is None or out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None


@lru_cache(maxsize=None)
def _dx_com_status():
    return _studio_answer("import json; from dx_compiler.core.setup_service import SetupService; "
                          "s = SetupService().check_status(); "
                          "print(json.dumps({'ok': s['dx_com_installed'], 'v': s['dx_com_version']}))")


def probe_dx_com():
    got = _dx_com_status()
    if got is None:
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


def probe_dx_app():
    """dx_app as a prepared board has it: checked out, built (bin/) and with models downloaded."""
    got = _studio_answer("import json; from dx_app.core.config import DX_APP_ROOT, MODELS_DIR; "
                         "print(json.dumps({'root': str(DX_APP_ROOT), 'models': str(MODELS_DIR)}))", timeout=60)
    root = Path(got["root"]) if got else SUITE / "dx-runtime" / "dx_app"
    models = Path(got["models"]) if got else root / "assets" / "models"
    if not (root / "config" / "model_registry.json").is_file():
        return False, f"dx_app is not installed ({root}; the dx-runtime submodule)"
    if not any(p.is_file() and os.access(p, os.X_OK) for p in (root / "bin").glob("*")):
        return False, f"dx_app is not built ({root}/bin is empty; DX App > Setup > Build)"
    n = sum(1 for p in models.glob("*.dxnn") if p.is_file())
    if not n:
        return False, f"no dx_app models downloaded ({models}; DX App > Setup)"
    return True, f"dx_app {root} · {n} models"


def probe_dx_rt():
    """dx-runtime installed: a Python that imports dx_engine, which Studio's NPU telemetry and runners use."""
    got = _studio_answer("import json; from shared.runtime import runtime_python; "
                         "print(json.dumps(runtime_python()))", timeout=120)
    if not got:
        return False, "dx-runtime is not installed (no Python with dx_engine; dx-runtime/install.sh)"
    return True, f"dx_engine via {got}"


def probe_dx_compiler():
    """dx-compiler checked out with its sample models and dx_com installed (free disk is dx_com's own check)."""
    samples = SUITE / "dx-compiler" / "dx_com" / "sample_models" / "onnx"
    if not any(samples.glob("*.onnx")):
        return False, f"dx-compiler sample models missing ({samples}; the dx-compiler submodule)"
    got = _dx_com_status()
    if not (got and got["ok"]):
        return False, "dx_com not installed (dx-compiler venv; DX Compiler > Setup)"
    return True, f"dx_com {got['v']}, sample models in {samples.parent}"


_PROBES = {"npu": probe_npu, "camera": probe_camera, "dx_com": probe_dx_com,
           "llm": probe_llm, "aws": probe_aws, "browser": probe_browser,
           "dx_app": probe_dx_app, "dx_rt": probe_dx_rt, "dx_compiler": probe_dx_compiler}


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
    try:
        return _PROBES[kind]()
    except Exception as exc:  # noqa: BLE001 - a probe that raises is that kind's NOT RUN reason, not the end of the run
        return False, f"{kind} probe failed: {type(exc).__name__}: {exc}"


def probe_all() -> dict:
    return {k: probe(k) for k in KINDS}


def need(*kinds: str) -> None:
    """Skip the calling test as NOT RUN when this machine lacks one of ``kinds``."""
    import pytest

    for kind in kinds:
        ok, detail = probe(kind)
        if not ok:
            pytest.skip(f"NOT RUN: {detail}")
