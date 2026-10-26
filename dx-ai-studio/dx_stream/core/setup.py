"""Runs build and download steps.

Same pattern as DX App's setup_steps.py: a background thread runs the process,
collects its log, and the client polls for it.
"""
from __future__ import annotations

import subprocess
import threading
import re
import os
import shutil
import tempfile
import shlex
import sys
from pathlib import Path
from dx_stream.core.config import DX_STREAM_ROOT
from shared.paths import STUDIO_ROOT
from shared.asset_setup import sample_assets_status, validate_stream_model
from shared.runtime_host import RuntimeHost

SETUP_STEPS = {
    "stream-deps": {
        "label_ko": "빌드 도구 & 라이브러리",
        "label_en": "Build Tools & Libraries",
        "script": lambda: DX_STREAM_ROOT / "install.sh",
        "cwd": lambda: DX_STREAM_ROOT,
        "needs_sudo": True,
    },
    "build": {
        "label_ko": "GStreamer 플러그인 빌드",
        "label_en": "GStreamer Plugin Build",
        "script": lambda: DX_STREAM_ROOT / "build.sh",
        "cwd": lambda: DX_STREAM_ROOT,
        # build.sh runs `sudo meson install` (+ sudo chown/rm on builddir). Mark needs_sudo so
        # the studio wires SUDO_ASKPASS; otherwise those internal sudo calls block on stdin.
        "needs_sudo": True,
    },
    "download-models": {
        "label_ko": "모델 & 비디오 다운로드",
        "label_en": "Model & Video Download",
        "cmd": [sys.executable, "-m", "shared.asset_setup", "stream"],
        "cwd": lambda: STUDIO_ROOT,
    },
    "runtime-deps": {
        "label_ko": "DX-Runtime 종속성 설치",
        "label_en": "DX-Runtime Dependencies",
        "managed_runtime": True,
        "cwd": lambda: DX_STREAM_ROOT,
        "needs_sudo": True,
    },
    "driver": {
        "label_ko": "NPU 리눅스 드라이버 설치",
        "label_en": "NPU Linux Driver Install",
        "managed_runtime": True,
        "cwd": lambda: DX_STREAM_ROOT,
        "needs_sudo": True,
    },
    "webrtc-deps": {
        "label_ko": "WebRTC 의존성 설치",
        "label_en": "WebRTC Dependencies",
        "cmd": ["sudo", "apt-get", "install", "-y", "gstreamer1.0-nice", "gir1.2-gst-plugins-bad-1.0"],
        "cwd": lambda: DX_STREAM_ROOT,
        "needs_sudo": True,
    },
}

# Logs are kept per step so steps running at the same time do not mix their output
_log_lock = threading.Lock()
_step_logs = {}  # {step_id: {"log": str, "done": bool, "exit_code": int}}
_proc_lock = threading.Lock()
_running_proc = None


def _is_setup_step_running() -> bool:
    """Return whether a setup subprocess or managed transaction is active."""
    if _running_proc is True:
        return True
    if _running_proc is None:
        return False
    poll = getattr(_running_proc, "poll", None)
    return callable(poll) and poll() is None


def _reserve_setup_worker() -> bool:
    """Atomically reserve the single setup worker when it is not already occupied."""
    global _running_proc
    with _proc_lock:
        if _is_setup_step_running():
            return False
        _running_proc = True  # type: ignore[assignment]
        return True


def _initialize_step_log(step_id: str) -> None:
    """Create the initial status record before a setup worker starts."""
    with _log_lock:
        _step_logs[step_id] = {"log": "", "done": False, "exit_code": -1}


def _record_worker_start_failure(step_id: str, error: Exception, sudo_cleanup) -> None:
    """Finalize a reserved worker after initialization or thread-start failure."""
    global _running_proc
    try:
        with _log_lock:
            state = _step_logs.setdefault(step_id, {"log": "", "done": False, "exit_code": -1})
            state["log"] += f"\n[ERROR] {error}\n"
            state["exit_code"] = 1
            state["done"] = True
    finally:
        try:
            with _proc_lock:
                _running_proc = None
        finally:
            sudo_cleanup()


# sudo-over-web helpers live in shared/sudo_askpass.py (shared with the dx_compiler SDK install),
# aliased here so callers and tests can keep using the module-local names.
from shared.sudo_askpass import (  # noqa: E402
    configure_sudo_env as _configure_sudo_env,
    preauthorize_sudo as _preauthorize_sudo,
    keep_sudo_alive as _keep_sudo_alive,
)


def get_log_state(step_id: str = None) -> dict:
    """Current log state, polled by the client."""
    with _log_lock:
        if step_id and step_id in _step_logs:
            return dict(_step_logs[step_id])
        # The most recent step that is still running
        for sid in reversed(list(_step_logs)):
            if not _step_logs[sid]["done"]:
                return dict(_step_logs[sid])
        # All done: the last log
        if _step_logs:
            return dict(list(_step_logs.values())[-1])
        return {"log": "", "done": True, "exit_code": -1}


def clear_log(step_id: str = None):
    """Clear the log."""
    with _log_lock:
        if step_id:
            _step_logs.pop(step_id, None)
        else:
            _step_logs.clear()


def _base_command_args(step_id: str) -> list[str]:
    step = SETUP_STEPS[step_id]
    if "cmd" in step:
        return list(step["cmd"])
    if "script" in step:
        script = step["script"]()
        if not script.exists():
            raise FileNotFoundError(f"Script not found: {script}")
        args = step.get("args", lambda: [])()
        return ["bash", str(script)] + args
    raise ValueError(f"Step {step_id} has no cmd or script")


def build_command_args(step_id: str, opts: dict = None) -> list[str]:
    """Construct command args for any setup step, applying opts only where supported (e.g. build)."""
    cmd_args = _base_command_args(step_id)
    if step_id == "download-models":
        return cmd_args
    if opts and step_id == "build":
        if opts.get("clean"):
            cmd_args.append("--clean")
        cmd_args.append("--type=Debug" if opts.get("debug") else "--type=Release")
    return cmd_args


def single_model_command_args(model_name: str) -> list[str]:
    validate_stream_model(DX_STREAM_ROOT, model_name)
    return [sys.executable, "-m", "shared.asset_setup", "stream", "--model", model_name]


def reconcile_managed_runtime() -> tuple[int, str]:
    """Reconcile the declared runtime/driver profile through Studio ownership."""
    host = RuntimeHost(authorized=True)
    result = host.reconcile()
    status = result.status.value
    lines = [
        "Runtime profile reconciliation",
        "status={}".format(status),
        "reason={}".format(result.reason),
    ]
    validation = getattr(getattr(host, "candidate_validator", None), "last_result", None)
    if validation is not None:
        lines.append("checks:")
        lines.extend(
            "{}={} ({})".format(
                check.check_id,
                "PASS" if check.passed else "FAIL",
                check.observed,
            )
            for check in validation.checks
        )
    return (0 if status == "active" else 1), "\n".join(lines) + "\n"


def install_model(model_name: str):
    """Download one model, reusing run_step().
    Runs Studio's safe asset CLI in a background thread."""
    step_id = f"model-{model_name}"
    SETUP_STEPS[step_id] = {
        "label_ko": f"{model_name} 다운로드",
        "label_en": f"Download {model_name}",
        "cmd": single_model_command_args(model_name),
        "cwd": lambda: STUDIO_ROOT,
        "_temporary": True,
    }
    try:
        run_step(step_id)
    finally:
        # Drop the temporary step definition (its log stays in _step_logs)
        if step_id in SETUP_STEPS and SETUP_STEPS[step_id].get("_temporary"):
            del SETUP_STEPS[step_id]


def _run_managed_runtime_step(step_id: str, sudo_password: str = None):
    """Run the profile transaction through the normal Stream setup worker lifecycle."""
    global _running_proc

    step = SETUP_STEPS[step_id]
    env = os.environ.copy()
    sudo_cleanup = _configure_sudo_env(env, sudo_password)
    sudo_error = _preauthorize_sudo(sudo_password, env)
    if sudo_error:
        sudo_cleanup()
        raise PermissionError(sudo_error)

    if not _reserve_setup_worker():
        sudo_cleanup()
        raise RuntimeError("Another process is already running")

    def _run():
        global _running_proc
        sudo_stop = threading.Event()
        try:
            threading.Thread(target=_keep_sudo_alive, args=(sudo_stop,), daemon=True).start()
            exit_code, output = reconcile_managed_runtime()
            with _log_lock:
                _step_logs[step_id]["log"] += output
                _step_logs[step_id]["exit_code"] = exit_code
                _step_logs[step_id]["done"] = True
        except Exception as exc:
            with _log_lock:
                _step_logs[step_id]["log"] += f"\n[ERROR] {exc}\n"
                _step_logs[step_id]["exit_code"] = 1
                _step_logs[step_id]["done"] = True
        finally:
            sudo_stop.set()
            with _proc_lock:
                _running_proc = None
            sudo_cleanup()

    try:
        _initialize_step_log(step_id)
        threading.Thread(target=_run, daemon=True).start()
    except Exception as exc:
        _record_worker_start_failure(step_id, exc, sudo_cleanup)
        raise


def run_step(step_id: str, sudo_password: str = None, opts: dict = None):
    """Run a step; a background thread collects stdout into the step's log."""
    global _running_proc

    step = SETUP_STEPS[step_id]  # KeyError if invalid
    if step.get("managed_runtime"):
        return _run_managed_runtime_step(step_id, sudo_password=sudo_password)
    cwd = step["cwd"]()

    cmd_args = build_command_args(step_id, opts)

    # For a sudo command or a script that calls sudo inside, open the sudo timestamp first.
    needs_sudo = bool(step.get("needs_sudo")) or (cmd_args[0] == "sudo" if cmd_args else False)
    env = os.environ.copy()
    # PEP 668 (Ubuntu 24.04+): some dependency scripts fall back to `pip install` on system
    # Python. Allow it via the env var (equivalent to --break-system-packages) so those pip
    # fallbacks don't hard-fail with externally-managed-environment.
    env.setdefault("PIP_BREAK_SYSTEM_PACKAGES", "1")
    sudo_cleanup = lambda: None
    if needs_sudo:
        sudo_cleanup = _configure_sudo_env(env, sudo_password)
        sudo_error = _preauthorize_sudo(sudo_password, env)
        if sudo_error:
            sudo_cleanup()
            # Distinct from RuntimeError ("another process running") so the client can
            # tell a bad/expired sudo password apart and re-prompt instead of giving up.
            raise PermissionError(sudo_error)
    direct_sudo = cmd_args[0] == "sudo" if cmd_args else False
    if direct_sudo and env.get("SUDO_ASKPASS"):
        cmd_args[0] = env.get("DX_REAL_SUDO", "sudo")
        if "-A" not in cmd_args:
            cmd_args.insert(1, "-A")
    elif direct_sudo and "-S" not in cmd_args:
        cmd_args.insert(1, "-S")

    if not _reserve_setup_worker():
        sudo_cleanup()
        raise RuntimeError("Another process is already running")

    def _run():
        global _running_proc
        sudo_stop = threading.Event()
        try:
            if needs_sudo:
                threading.Thread(target=_keep_sudo_alive, args=(sudo_stop,), daemon=True).start()
            # Own process group: Stop ends the script AND its children (wget, meson, …) — terminating
            # only the shell left them running.
            proc = subprocess.Popen(
                cmd_args, cwd=str(cwd),
                stdin=subprocess.PIPE if direct_sudo else None,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env=env, start_new_session=True,
            )
            with _proc_lock:
                _running_proc = proc
            # Pass the sudo password
            if direct_sudo and sudo_password and proc.stdin:
                proc.stdin.write(sudo_password + "\n")
                proc.stdin.flush()
                proc.stdin.close()
            for line in proc.stdout:
                with _log_lock:
                    _step_logs[step_id]["log"] += line
                    if step_id == "download-models" and line.startswith("Downloading"):
                        m = re.search(r"(\d+)/(\d+)", line)
                        if m:
                            _step_logs[step_id]["log"] += f"[PROGRESS] {m.group(1)}/{m.group(2)}\n"
            proc.wait()
            with _log_lock:
                _step_logs[step_id]["exit_code"] = proc.returncode
                _step_logs[step_id]["done"] = True
            with _proc_lock:
                _running_proc = None
        except Exception as e:
            with _log_lock:
                _step_logs[step_id]["log"] += f"\n[ERROR] {e}\n"
                _step_logs[step_id]["exit_code"] = 1
                _step_logs[step_id]["done"] = True
            with _proc_lock:
                _running_proc = None
        finally:
            sudo_stop.set()
            sudo_cleanup()

    try:
        _initialize_step_log(step_id)
        threading.Thread(target=_run, daemon=True).start()
    except Exception as exc:
        _record_worker_start_failure(step_id, exc, sudo_cleanup)
        raise


def stop_step():
    """Stop the running step."""
    global _running_proc
    with _proc_lock:
        if _running_proc is True:
            # runtime-deps / driver run as an in-process transaction — nothing to signal.
            return {"ok": False, "error": "not_stoppable",
                    "message": "This step cannot be stopped; it finishes on its own."}
        if _running_proc is not None and hasattr(_running_proc, 'poll') and _running_proc.poll() is None:
            import signal
            try:
                os.killpg(os.getpgid(_running_proc.pid), signal.SIGTERM)
            except (ProcessLookupError, PermissionError, OSError):
                pass
            _running_proc = None
            with _log_lock:
                for state in _step_logs.values():
                    if not state.get("done"):
                        state["exit_code"] = 130
                        state["done"] = True
            return {"ok": True}
    return {"ok": False, "error": "No running process"}


def running_step() -> str | None:
    """The step that has not finished yet (None if none). Leaving the page or switching language stops log
    polling — the page uses this value to bring back that step's log and Stop button."""
    with _log_lock:
        for sid in reversed(list(_step_logs)):
            if not _step_logs[sid].get("done"):
                return sid
    return None


def get_setup_status() -> dict:
    """Completion state per step — build: .so exists, models: files exist, running: the step in progress."""
    from dx_stream.core import status as _status
    assets = sample_assets_status("stream", sdk_root=DX_STREAM_ROOT)
    model_counts = assets.get("models", {})
    # Installed = present on disk; files without a Studio record are counted (and shown) as unverified.
    assets.update(total=model_counts.get("total", 0),
                  installed=model_counts.get("verified", 0) + model_counts.get("unverified", 0),
                  unverified=model_counts.get("unverified", 0))
    return {
        "build": _status._check_build(),
        "download-models": assets,
        "running": running_step(),
    }
