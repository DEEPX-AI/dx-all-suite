"""빌드/다운로드 실행 관리.

DX App의 setup_steps.py 패턴 적용.
백그라운드 스레드에서 프로세스 실행 + 로그 축적 + 폴링 API 제공.
"""
from __future__ import annotations

import subprocess
import threading
import re
import os
import shutil
import tempfile
import shlex
from pathlib import Path
from dx_stream.core.config import DX_STREAM_ROOT
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
        "script": lambda: DX_STREAM_ROOT / "setup.sh",
        "cwd": lambda: DX_STREAM_ROOT,
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

# 로그 저장소 — per-step 격리 (동시 실행 시 로그 오염 방지)
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


# sudo-over-web helpers now live in shared/sudo_askpass.py (reused by dx_compiler SDK install
# too). Kept as module-local aliases so existing callers and tests are unaffected.
from shared.sudo_askpass import (  # noqa: E402
    configure_sudo_env as _configure_sudo_env,
    preauthorize_sudo as _preauthorize_sudo,
    keep_sudo_alive as _keep_sudo_alive,
)


def get_log_state(step_id: str = None) -> dict:
    """현재 로그 상태 반환 — 클라이언트 폴링용."""
    with _log_lock:
        if step_id and step_id in _step_logs:
            return dict(_step_logs[step_id])
        # 가장 최근 활성(미완료) 로그 반환
        for sid in reversed(list(_step_logs)):
            if not _step_logs[sid]["done"]:
                return dict(_step_logs[sid])
        # 모든 완료면 마지막 로그
        if _step_logs:
            return dict(list(_step_logs.values())[-1])
        return {"log": "", "done": True, "exit_code": -1}


def clear_log(step_id: str = None):
    """로그 초기화."""
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
    return ["bash", str(DX_STREAM_ROOT / "setup.sh"), f"--model={model_name}"]


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
    """단일 모델 다운로드 — run_step() 패턴 재사용.
    setup.sh --model=<name>을 백그라운드 스레드에서 실행."""
    step_id = f"model-{model_name}"
    SETUP_STEPS[step_id] = {
        "label_ko": f"{model_name} 다운로드",
        "label_en": f"Download {model_name}",
        "cmd": single_model_command_args(model_name),
        "cwd": lambda: DX_STREAM_ROOT,
        "_temporary": True,
    }
    try:
        run_step(step_id)
    finally:
        # 임시 step 정의 정리 (로그는 _step_logs에 유지)
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
    """step 실행 — 백그라운드 스레드에서 stdout을 per-step 로그에 축적."""
    global _running_proc

    step = SETUP_STEPS[step_id]  # KeyError if invalid
    if step.get("managed_runtime"):
        return _run_managed_runtime_step(step_id, sudo_password=sudo_password)
    cwd = step["cwd"]()

    cmd_args = build_command_args(step_id, opts)

    # sudo 명령 또는 내부 sudo 스크립트면 먼저 sudo timestamp를 열어 둔다.
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
            proc = subprocess.Popen(
                cmd_args, cwd=str(cwd),
                stdin=subprocess.PIPE if direct_sudo else None,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env=env
            )
            with _proc_lock:
                _running_proc = proc
            # sudo 비밀번호 전달
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
    """현재 실행 중인 스텝 종료"""
    global _running_proc
    with _proc_lock:
        if _running_proc is not None and hasattr(_running_proc, 'poll') and _running_proc.poll() is None:
            _running_proc.terminate()
            _running_proc = None
            with _log_lock:
                for state in _step_logs.values():
                    if not state.get("done"):
                        state["exit_code"] = 130
                        state["done"] = True
            return {"ok": True}
    return {"ok": False, "error": "No running process"}


def get_setup_status() -> dict:
    """각 step의 완료 상태 — build: .so 존재 여부, models: 파일 존재 여부"""
    from dx_stream.core.status import _check_build, _check_models
    return {
        "build": _check_build(),
        "download-models": _check_models(),
    }
