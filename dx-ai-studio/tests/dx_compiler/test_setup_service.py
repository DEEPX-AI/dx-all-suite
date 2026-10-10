"""SetupService — the dx_com install/download flows behind the Setup panel.

These paths shell out to `install.sh` (with sudo), `python -m venv`, `pip install`
and two download scripts. Nothing here may run for real, so every subprocess entry
point is faked and the SDK paths are redirected into tmp_path; a test that escaped
the fake would try to reinstall the compiler SDK on the developer's machine.

The flows are generators that stream progress dicts to the browser, so the contract
under test is the SEQUENCE of events, not just a return value: a wrong event `type`
leaves the Setup panel spinning forever, and a swallowed failure reports "installed"
for an SDK that is not there.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from dx_compiler.core import setup_service as SS


class _FakeProc:
    """Stand-in for subprocess.Popen: canned stdout lines, then a returncode."""

    def __init__(self, lines, returncode=0):
        self.stdout = iter(lines)
        self._returncode = returncode
        self.returncode = None

    def wait(self):
        self.returncode = self._returncode
        return self.returncode


@pytest.fixture
def sdk(tmp_path, monkeypatch):
    """Redirect every SDK path into tmp_path and return the fake SDK root."""
    root = tmp_path / "dx-compiler"
    (root / "dx_com").mkdir(parents=True)
    (root / "example").mkdir()
    monkeypatch.setattr(SS, "SDK_ROOT", root)
    monkeypatch.setattr(SS, "SDK_EXAMPLE", root / "example")
    monkeypatch.setattr(SS, "SDK_PROPS", root / "compiler.properties")
    monkeypatch.setattr(SS, "SAMPLE_MODELS_DIR", root / "dx_com" / "sample_models")
    monkeypatch.setattr(SS, "CALIB_DIR", root / "dx_com" / "calibration_dataset")
    return root


@pytest.fixture(autouse=True)
def _no_real_subprocess(monkeypatch):
    """Fail loudly if a test forgets to fake a subprocess entry point."""

    def _forbidden(*a, **k):  # pragma: no cover - only runs when a test is wrong
        raise AssertionError(f"real subprocess call escaped the fakes: {a!r}")

    monkeypatch.setattr(SS.subprocess, "Popen", _forbidden)
    monkeypatch.setattr(SS.subprocess, "run", _forbidden)


def _make_venv(root: Path) -> Path:
    """Create the venv layout get_venv_python() looks for."""
    py = root / SS.VENV_CANDIDATES[0] / "bin" / "python3"
    py.parent.mkdir(parents=True, exist_ok=True)
    py.touch()
    return py


def _wheel(root: Path, name: str) -> Path:
    w = root / "dx_com" / name
    w.write_bytes(b"not-a-real-wheel")
    return w


# --------------------------------------------------------------------------
# venv / sample discovery
# --------------------------------------------------------------------------


def test_find_venv_prefers_the_host_candidate_over_the_container_one(sdk):
    for name in SS.VENV_CANDIDATES:
        (sdk / name / "bin").mkdir(parents=True)
        (sdk / name / "bin" / "python3").touch()
    assert SS.SetupService().get_venv_python() == sdk / SS.VENV_CANDIDATES[0] / "bin" / "python3"


def test_get_venv_python_is_none_when_the_dir_exists_but_the_interpreter_does_not(sdk):
    """A half-deleted venv must not be reported as usable."""
    (sdk / SS.VENV_CANDIDATES[0] / "bin").mkdir(parents=True)
    assert SS.SetupService().get_venv_python() is None


def test_get_sample_models_requires_both_onnx_and_config(sdk):
    models = SS.SAMPLE_MODELS_DIR
    (models / "onnx").mkdir(parents=True)
    (models / "json").mkdir(parents=True)
    first = SS.SAMPLE_MODELS[0]
    (models / "onnx" / first["onnx"]).touch()  # config deliberately absent

    got = {m["name"]: m for m in SS.SetupService().get_sample_models()}
    assert got[first["name"]]["downloaded"] is False, (
        "a model with only its .onnx present is not usable and must not report downloaded"
    )
    assert got[first["name"]]["config_path"] is None
    assert got[first["name"]]["onnx_path"] is not None


def test_local_wheel_available_survives_an_unreadable_sdk_dir(sdk, monkeypatch):
    def _boom(*a, **k):
        raise OSError("permission denied")

    monkeypatch.setattr(Path, "glob", _boom)
    assert SS.SetupService()._local_wheel_available() is False


# --------------------------------------------------------------------------
# install_sdk — routing between the wheel path and the install.sh path
# --------------------------------------------------------------------------


def test_install_sdk_uses_the_local_wheel_without_sudo_or_network(sdk, monkeypatch):
    """A wheel on disk must never reach install.sh — that path needs a password."""
    _wheel(sdk, "dx_com-1.0-py3-none-any.whl")
    _make_venv(sdk)
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: _FakeProc(["Successfully installed\n"]))

    def _must_not_run(self, password):  # pragma: no cover - asserts it is not called
        raise AssertionError("install.sh must not run when a local wheel exists")

    monkeypatch.setattr(SS.SetupService, "_run_install_sh", _must_not_run)

    events = list(SS.SetupService().install_sdk())
    assert events[-1]["type"] == "complete"


def test_install_sdk_creates_a_venv_first_when_none_exists(sdk, monkeypatch):
    _wheel(sdk, "dx_com-1.0-py3-none-any.whl")
    calls = []

    def _fake_create(self):
        calls.append("create")
        _make_venv(sdk)
        yield {"type": "progress", "progress": 8, "message": "Virtual environment created."}

    monkeypatch.setattr(SS.SetupService, "_create_venv", _fake_create)
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: _FakeProc(["ok\n"]))

    events = list(SS.SetupService().install_sdk())
    assert calls == ["create"], "the venv must be created before pip runs"
    assert events[-1]["type"] == "complete"


def test_install_sdk_points_at_install_sh_when_the_venv_cannot_be_created(sdk, monkeypatch):
    """The user is stuck without a venv, so the message must be actionable."""
    _wheel(sdk, "dx_com-1.0-py3-none-any.whl")

    def _fake_create(self):
        yield {"type": "error", "message": "nope"}

    monkeypatch.setattr(SS.SetupService, "_create_venv", _fake_create)

    events = list(SS.SetupService().install_sdk())
    assert events[-1]["type"] == "error"
    assert "install.sh" in events[-1]["message"]
    assert str(sdk) in events[-1]["message"]


def test_install_sdk_reports_a_missing_sdk_checkout(tmp_path, monkeypatch):
    monkeypatch.setattr(SS, "SDK_ROOT", tmp_path / "absent")
    events = list(SS.SetupService().install_sdk())
    assert len(events) == 1
    assert events[0]["type"] == "error"
    assert "submodule" in events[0]["message"]


def test_install_sdk_asks_for_a_password_before_touching_install_sh(sdk):
    """No wheel means a download, which needs sudo — the UI must get need_sudo."""
    (sdk / "install.sh").touch()
    events = list(SS.SetupService().install_sdk())
    assert [e["type"] for e in events] == ["need_sudo"]


def test_install_sdk_runs_install_sh_once_a_password_is_supplied(sdk, monkeypatch):
    (sdk / "install.sh").touch()
    seen = {}

    def _fake_run(self, password):
        seen["password"] = password
        yield {"type": "complete", "progress": 100, "message": "done"}

    monkeypatch.setattr(SS.SetupService, "_run_install_sh", _fake_run)
    events = list(SS.SetupService().install_sdk(sudo_password="hunter2"))
    assert seen["password"] == "hunter2"
    assert events[-1]["type"] == "complete"


# --------------------------------------------------------------------------
# _run_install_sh
# --------------------------------------------------------------------------


@pytest.fixture
def sudo(monkeypatch):
    """Fake the sudo helpers; records cleanup so leaks are visible."""
    import shared.sudo_askpass as SA

    state = {"cleanup_calls": 0, "auth_error": None}
    monkeypatch.setattr(
        SA, "configure_sudo_env",
        lambda env, password=None: lambda: state.__setitem__("cleanup_calls", state["cleanup_calls"] + 1),
    )
    monkeypatch.setattr(SA, "preauthorize_sudo", lambda password=None, env=None: state["auth_error"])
    monkeypatch.setattr(SA, "keep_sudo_alive", lambda stop_event: None)
    return state


def test_run_install_sh_reports_a_bad_password_distinctly(sdk, sudo):
    """`sudo_auth` is a separate type so the UI can re-prompt instead of giving up."""
    sudo["auth_error"] = "Sorry, try again"
    events = list(SS.SetupService()._run_install_sh("wrong"))
    assert [e["type"] for e in events] == ["sudo_auth"]
    assert "Sorry, try again" in events[0]["message"]
    assert sudo["cleanup_calls"] == 1, "the askpass temp dir must be removed on the auth failure"


def test_run_install_sh_strips_ansi_and_caps_progress(sdk, sudo, monkeypatch):
    """install.sh emits colour codes; raw escapes would corrupt the web log."""
    lines = ["\x1b[32m[OK] step one\x1b[0m\n", "\n", "plain\n"] + [f"line {i}\n" for i in range(600)]
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: _FakeProc(lines))

    events = list(SS.SetupService()._run_install_sh("pw"))
    messages = [e["message"] for e in events]

    assert "[OK] step one" in messages, "ANSI codes must be stripped, not kept"
    assert not any("\x1b" in m for m in messages)
    assert "" not in messages, "blank lines must be dropped, not streamed as empty progress"
    progresses = [e["progress"] for e in events if e["type"] == "progress"]
    assert max(progresses) <= 95, "progress must stay below the 100 reserved for completion"
    assert events[-1]["type"] == "complete" and events[-1]["progress"] == 100


def test_run_install_sh_surfaces_a_nonzero_exit(sdk, sudo, monkeypatch):
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: _FakeProc(["boom\n"], returncode=2))
    events = list(SS.SetupService()._run_install_sh("pw"))
    assert events[-1]["type"] == "error"
    assert "exit 2" in events[-1]["message"]
    assert sudo["cleanup_calls"] == 1


def test_run_install_sh_cleans_up_when_popen_raises(sdk, sudo, monkeypatch):
    """The finally block is the only thing removing the askpass shim."""

    def _boom(*a, **k):
        raise OSError("no bash")

    monkeypatch.setattr(SS.subprocess, "Popen", _boom)
    events = list(SS.SetupService()._run_install_sh("pw"))
    assert events[-1]["type"] == "error"
    assert "no bash" in events[-1]["message"]
    assert sudo["cleanup_calls"] == 1, "a crash must not leave the sudo shim on PATH"


def test_run_install_sh_never_passes_venv_reuse(sdk, sudo, monkeypatch):
    """install.sh rejects --venv-reuse together with its default force-remove."""
    captured = {}

    def _popen(args, **k):
        captured["args"] = args
        return _FakeProc([])

    monkeypatch.setattr(SS.subprocess, "Popen", _popen)
    list(SS.SetupService()._run_install_sh("pw"))
    assert "--target=dx_com" in captured["args"]
    assert not any("venv-reuse" in a for a in captured["args"])


# --------------------------------------------------------------------------
# _create_venv
# --------------------------------------------------------------------------


def test_create_venv_reports_a_missing_sdk_root(tmp_path, monkeypatch):
    monkeypatch.setattr(SS, "SDK_ROOT", tmp_path / "absent")
    events = list(SS.SetupService()._create_venv())
    assert [e["type"] for e in events] == ["error"]


def test_create_venv_reports_a_timeout(sdk, monkeypatch):
    def _timeout(*a, **k):
        raise subprocess.TimeoutExpired(cmd="venv", timeout=180)

    monkeypatch.setattr(SS.subprocess, "run", _timeout)
    events = list(SS.SetupService()._create_venv())
    assert events[-1]["type"] == "error"


def test_create_venv_reports_the_stderr_detail_on_failure(sdk, monkeypatch):
    monkeypatch.setattr(
        SS.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 1, stdout="", stderr="ensurepip is not available"),
    )
    events = list(SS.SetupService()._create_venv())
    assert events[-1]["type"] == "error"
    assert "ensurepip" in events[-1]["message"], (
        "the real reason must reach the user; a generic message is undebuggable"
    )


def test_create_venv_fails_when_the_command_succeeds_but_produces_no_interpreter(sdk, monkeypatch):
    """returncode 0 is not proof — check the interpreter actually exists."""
    monkeypatch.setattr(
        SS.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout="", stderr=""),
    )
    events = list(SS.SetupService()._create_venv())
    assert events[-1]["type"] == "error"


def test_create_venv_succeeds(sdk, monkeypatch):
    def _run(cmd, **k):
        _make_venv(sdk)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(SS.subprocess, "run", _run)
    events = list(SS.SetupService()._create_venv())
    assert [e["type"] for e in events] == ["progress", "progress"]
    assert events[-1]["progress"] == 8


def test_create_venv_inherits_platform_packages(sdk, monkeypatch):
    """--system-site-packages is what lets the venv see the platform wheels."""
    captured = {}

    def _run(cmd, **k):
        captured["cmd"] = cmd
        _make_venv(sdk)
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(SS.subprocess, "run", _run)
    list(SS.SetupService()._create_venv())
    assert "--system-site-packages" in captured["cmd"]
    assert captured["cmd"][0] == sys.executable


# --------------------------------------------------------------------------
# _pip_install_dx_com
# --------------------------------------------------------------------------


def test_pip_install_reports_when_no_wheel_is_present(sdk):
    events = list(SS.SetupService()._pip_install_dx_com(_make_venv(sdk)))
    assert [e["type"] for e in events] == ["error"]
    assert "No wheel" in events[0]["message"]


def test_pip_install_prefers_the_wheel_matching_this_interpreter(sdk, monkeypatch):
    """Installing another interpreter's wheel fails at import time, far from here.

    glob() order is filesystem order, so the fallback (`wheels[0]`) can land on the
    right wheel by luck — an earlier version of this test passed against a mutant
    with the py_tag filter deleted. Pin the order so the WRONG wheel is first:
    now only the tag match can produce a correct answer.
    """
    tag = f"cp{sys.version_info.major}{sys.version_info.minor}"
    wrong = _wheel(sdk, "dx_com-1.0-cp36-cp36m-linux_x86_64.whl")
    mine = _wheel(sdk, f"dx_com-1.0-{tag}-{tag}-linux_x86_64.whl")
    monkeypatch.setattr(Path, "glob", lambda self, pat: iter([wrong, mine]))
    captured = {}

    def _popen(cmd, **k):
        captured["cmd"] = cmd
        return _FakeProc(["Successfully installed\n"])

    monkeypatch.setattr(SS.subprocess, "Popen", _popen)
    events = list(SS.SetupService()._pip_install_dx_com(_make_venv(sdk)))
    assert str(mine) in captured["cmd"], (
        f"picked {captured['cmd'][-1]!r}; the {tag} wheel must win over the cp36 one"
    )
    assert str(wrong) not in captured["cmd"]
    assert events[-1]["type"] == "complete"


def test_pip_install_falls_back_to_any_wheel_when_none_match(sdk, monkeypatch):
    only = _wheel(sdk, "dx_com-1.0-cp36-cp36m-linux_x86_64.whl")
    captured = {}

    def _popen(cmd, **k):
        captured["cmd"] = cmd
        return _FakeProc([])

    monkeypatch.setattr(SS.subprocess, "Popen", _popen)
    list(SS.SetupService()._pip_install_dx_com(_make_venv(sdk)))
    assert str(only) in captured["cmd"]


def test_pip_install_forces_reinstall(sdk, monkeypatch):
    """Without --force-reinstall a same-version wheel is a silent no-op."""
    _wheel(sdk, "dx_com-1.0-py3-none-any.whl")
    captured = {}

    def _popen(cmd, **k):
        captured["cmd"] = cmd
        return _FakeProc([])

    monkeypatch.setattr(SS.subprocess, "Popen", _popen)
    list(SS.SetupService()._pip_install_dx_com(_make_venv(sdk)))
    assert "--force-reinstall" in captured["cmd"]


def test_pip_install_surfaces_a_nonzero_exit(sdk, monkeypatch):
    _wheel(sdk, "dx_com-1.0-py3-none-any.whl")
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: _FakeProc(["err\n"], returncode=1))
    events = list(SS.SetupService()._pip_install_dx_com(_make_venv(sdk)))
    assert events[-1]["type"] == "error"
    assert "exit 1" in events[-1]["message"]


def test_pip_install_reports_an_exception_instead_of_hanging_the_panel(sdk, monkeypatch):
    _wheel(sdk, "dx_com-1.0-py3-none-any.whl")

    def _boom(*a, **k):
        raise OSError("exec format error")

    monkeypatch.setattr(SS.subprocess, "Popen", _boom)
    events = list(SS.SetupService()._pip_install_dx_com(_make_venv(sdk)))
    assert events[-1]["type"] == "error"
    assert "exec format error" in events[-1]["message"]


# --------------------------------------------------------------------------
# download_samples
# --------------------------------------------------------------------------


def _download_scripts(sdk):
    a = SS.SDK_EXAMPLE / "1-download_sample_models.sh"
    b = SS.SDK_EXAMPLE / "2-download_sample_calibration_dataset.sh"
    return a, b


def test_download_samples_stops_at_a_missing_script(sdk):
    events = list(SS.SetupService().download_samples())
    assert events[-1]["type"] == "error"
    assert "1-download_sample_models.sh" in events[-1]["message"]


def test_download_samples_does_not_run_the_second_script_after_a_failure(sdk, monkeypatch):
    """Calibration data is useless without the models it calibrates."""
    a, b = _download_scripts(sdk)
    a.touch()
    b.touch()
    runs = []

    def _popen(cmd, **k):
        runs.append(Path(cmd[1]).name)
        return _FakeProc(["downloading\n"], returncode=1)

    monkeypatch.setattr(SS.subprocess, "Popen", _popen)
    events = list(SS.SetupService().download_samples())
    assert runs == [a.name], "the second script must not run once the first failed"
    assert events[-1]["type"] == "error"


def test_download_samples_streams_log_lines_then_completes(sdk, monkeypatch):
    a, b = _download_scripts(sdk)
    a.touch()
    b.touch()
    monkeypatch.setattr(
        SS.subprocess, "Popen",
        lambda cmd, **k: _FakeProc(["fetching...\n", "\n", "done\n"]),
    )
    events = list(SS.SetupService().download_samples())
    logs = [e["message"] for e in events if e["type"] == "log"]
    assert logs == ["fetching...", "done", "fetching...", "done"]
    assert events[-1] == {"type": "complete", "progress": 100, "message": "All downloads complete"}


def test_download_samples_reports_an_exception(sdk, monkeypatch):
    a, b = _download_scripts(sdk)
    a.touch()
    b.touch()

    def _boom(*a_, **k):
        raise OSError("bash missing")

    monkeypatch.setattr(SS.subprocess, "Popen", _boom)
    events = list(SS.SetupService().download_samples())
    assert events[-1]["type"] == "error"
    assert "bash missing" in events[-1]["message"]


# --------------------------------------------------------------------------
# CPU-only torch on hosts without an NVIDIA GPU
# --------------------------------------------------------------------------


@pytest.mark.parametrize("has_gpu, expected", [(False, SS.TORCH_CPU_INDEX), (True, None)])
def test_install_sh_pulls_cpu_torch_when_there_is_no_nvidia_gpu(sdk, sudo, monkeypatch, has_gpu, expected):
    """dx-com needs torch, and pip's default x86 torch drags in the CUDA libraries (~5 GB on
    disk). dxcom compiles on the CPU, so on a host without an NVIDIA GPU they are never
    used — and on a nearly full board the install died with "No space left on device"."""
    monkeypatch.delenv("PIP_EXTRA_INDEX_URL", raising=False)
    monkeypatch.delenv("PIP_INDEX_URL", raising=False)
    monkeypatch.setattr(SS, "_has_nvidia_gpu", lambda: has_gpu)
    seen = {}
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: seen.update(k) or _FakeProc([]))

    list(SS.SetupService()._run_install_sh("pw"))

    assert seen["env"].get("PIP_EXTRA_INDEX_URL") == expected


def test_a_pip_index_the_user_set_is_left_alone(sdk, sudo, monkeypatch):
    monkeypatch.setenv("PIP_INDEX_URL", "https://mirror.example/simple")
    monkeypatch.delenv("PIP_EXTRA_INDEX_URL", raising=False)
    monkeypatch.setattr(SS, "_has_nvidia_gpu", lambda: False)
    seen = {}
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: seen.update(k) or _FakeProc([]))

    list(SS.SetupService()._run_install_sh("pw"))

    assert "PIP_EXTRA_INDEX_URL" not in seen["env"]
    assert seen["env"]["PIP_INDEX_URL"] == "https://mirror.example/simple"


def test_the_local_wheel_install_also_pulls_cpu_torch(sdk, monkeypatch, tmp_path):
    monkeypatch.delenv("PIP_EXTRA_INDEX_URL", raising=False)
    monkeypatch.delenv("PIP_INDEX_URL", raising=False)
    monkeypatch.setattr(SS, "_has_nvidia_gpu", lambda: False)
    (sdk / "dx_com" / f"dx_com-2.4.0-cp{sys.version_info.major}{sys.version_info.minor}-x.whl").write_bytes(b"")
    seen = {}
    monkeypatch.setattr(SS.subprocess, "Popen", lambda *a, **k: seen.update(k) or _FakeProc([]))

    list(SS.SetupService()._pip_install_dx_com(tmp_path / "venv" / "bin" / "python"))

    assert seen["env"]["PIP_EXTRA_INDEX_URL"] == SS.TORCH_CPU_INDEX
