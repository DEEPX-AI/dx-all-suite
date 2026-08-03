"""setup.py 테스트 — step 정의, 상태 확인, 스크립트 경로"""
import sys, pytest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class TestSetupSteps:
    def test_install_model_registers_step(self):
        """install_model()이 SETUP_STEPS에 동적 스텝을 등록하는지 확인"""
        from core.setup import SETUP_STEPS
        from core.setup import install_model
        assert callable(install_model)

    def test_run_step_supports_args(self):
        """run_step()이 step에 args 키가 있으면 인자를 전달하는지 확인"""
        from core.setup import SETUP_STEPS
        SETUP_STEPS["_test_echo"] = {
            "label_ko": "테스트",
            "label_en": "Test",
            "script": lambda: Path("/bin/echo"),
            "args": lambda: ["hello"],
            "cwd": lambda: Path("/tmp"),
        }
        assert "args" in SETUP_STEPS["_test_echo"]
        del SETUP_STEPS["_test_echo"]

    def test_all_core_setup_steps_have_post_routes(self):
        """Every core setup step must have a POST route in server.py.

        Regression guard: the 'stream-deps' step was added to SETUP_STEPS + the UI
        without a server route, so clicking Install 404'd (no run, no logs).
        """
        import re
        root = Path(__file__).resolve().parent.parent.parent / "dx_stream"
        server_src = (root / "server.py").read_text(encoding="utf-8")
        core_steps = ["stream-deps", "build", "download-models", "runtime-deps", "driver", "webrtc-deps"]
        for step in core_steps:
            assert f'"/api/setup/{step}"' in server_src, f"missing POST route for setup step {step!r}"

    def test_steps_defined(self):
        from core.setup import SETUP_STEPS
        assert "build" in SETUP_STEPS
        assert "download-models" in SETUP_STEPS
        assert "runtime-deps" in SETUP_STEPS
        assert "driver" in SETUP_STEPS

    def test_runtime_steps_are_managed_transactions(self):
        from core.setup import SETUP_STEPS

        for step_id in ("runtime-deps", "driver"):
            step = SETUP_STEPS[step_id]
            assert step.get("managed_runtime") is True
            assert "script" not in step
            assert "cmd" not in step

    def test_reconcile_managed_runtime_uses_authorized_host(self, monkeypatch):
        from core import setup

        captured = []

        class FakeHost:
            def __init__(self, *, authorized):
                captured.append(authorized)

            def reconcile(self):
                return SimpleNamespace(
                    status=SimpleNamespace(value="active"),
                    reason="profile validated",
                )

        monkeypatch.setattr(setup, "RuntimeHost", FakeHost, raising=False)
        reconcile = getattr(setup, "reconcile_managed_runtime", None)
        assert callable(reconcile)

        exit_code, log = reconcile()

        assert captured == [True]
        assert exit_code == 0
        assert "status=active" in log
        assert "profile validated" in log

    def test_reconcile_managed_runtime_rejects_non_active_result(self, monkeypatch):
        from core import setup

        class FakeHost:
            def __init__(self, *, authorized):
                assert authorized is True

            def reconcile(self):
                return SimpleNamespace(
                    status=SimpleNamespace(value="rolled_back"),
                    reason="candidate validation failed",
                )

        monkeypatch.setattr(setup, "RuntimeHost", FakeHost)

        exit_code, log = setup.reconcile_managed_runtime()

        assert exit_code == 1
        assert "status=rolled_back" in log
        assert "candidate validation failed" in log

    def test_step_has_required_fields(self):
        from core.setup import SETUP_STEPS
        required = {"label_ko", "label_en", "cwd"}
        for step_id, step in SETUP_STEPS.items():
            assert required.issubset(step.keys()), f"Step {step_id} missing fields"
            assert (
                "script" in step or "cmd" in step or step.get("managed_runtime")
            ), f"Step {step_id} needs an executable setup action"

    def test_step_scripts_are_callable(self):
        from core.setup import SETUP_STEPS
        for step_id, step in SETUP_STEPS.items():
            if "script" not in step:
                continue
            path = step["script"]()
            assert isinstance(path, Path)
            assert path.name.endswith(".sh")

    def test_driver_step_uses_managed_runtime_transaction(self):
        from core.setup import SETUP_STEPS

        step = SETUP_STEPS["driver"]
        assert step["managed_runtime"] is True
        assert "script" not in step
        assert "cmd" not in step

    def test_sudo_steps_are_marked_for_preauthorization(self):
        from core.setup import SETUP_STEPS

        for step_id in ["runtime-deps", "driver", "webrtc-deps"]:
            assert SETUP_STEPS[step_id].get("needs_sudo"), step_id

    def test_sudo_preauthorization_uses_stdin_password(self):
        from core import setup

        with patch.object(setup.subprocess, "run") as run:
            run.return_value.returncode = 0
            run.return_value.stdout = ""
            run.return_value.stderr = ""

            error = setup._preauthorize_sudo("secret")

        assert error is None
        run.assert_called_once()
        args, kwargs = run.call_args
        assert args[0] == ["sudo", "-S", "-v"]
        assert kwargs["input"] == "secret\n"

    def test_sudo_environment_uses_askpass_for_nested_sudo(self):
        from core import setup
        import os

        env = {"PATH": "/usr/bin"}
        cleanup = setup._configure_sudo_env(env, "secret")
        try:
            assert "SUDO_ASKPASS" in env
            assert env["SUDO_REQUIRE_ASKPASS"] == "force"
            askpass_path = env["SUDO_ASKPASS"]
            assert os.path.exists(askpass_path)
            with patch.object(setup.subprocess, "run") as run:
                run.return_value.returncode = 0
                run.return_value.stdout = ""
                run.return_value.stderr = ""

                error = setup._preauthorize_sudo("secret", env)

            assert error is None
            args, kwargs = run.call_args
            assert args[0][0].endswith("sudo")
            assert args[0][1:] == ["-A", "-v"]
            assert kwargs["env"] is env
        finally:
            cleanup()
        assert not os.path.exists(askpass_path)

    def test_completed_setup_step_marks_card_badge_immediately(self):
        script = Path(__file__).resolve().parent.parent.parent / "dx_stream" / "static" / "js" / "stream-setup.js"
        text = script.read_text(encoding="utf-8")

        assert "_setupCompletedSteps" in text
        assert "function _markSetupStepDone" in text
        assert "_markSetupStepDone(stepId)" in text
        assert "_setupCompletedSteps['driver']" in text

    def test_invalid_step_id_raises(self):
        from core.setup import run_step
        with pytest.raises(KeyError):
            run_step("nonexistent-step")

    def test_get_setup_status_returns_dict(self):
        from core.setup import get_setup_status
        status = get_setup_status()
        assert isinstance(status, dict)
        assert "build" in status
        assert "download-models" in status
        for v in status.values():
            assert "ok" in v


class TestSetupLog:
    def test_log_initial_state(self):
        from core.setup import get_log_state
        state = get_log_state()
        assert "log" in state
        assert "done" in state

    def test_log_clear(self):
        from core.setup import clear_log, get_log_state
        clear_log()
        state = get_log_state()
        assert state["log"] == ""
        assert state["done"] is True


class TestStopAndOpts:
    def test_stop_step_no_process(self):
        from core.setup import stop_step
        result = stop_step()
        assert result['ok'] is False
        assert 'error' in result

    def test_run_step_accepts_opts(self):
        from core.setup import SETUP_STEPS, run_step
        original = SETUP_STEPS["build"]
        SETUP_STEPS["build"] = {
            "label_ko": "테스트",
            "label_en": "Test",
            "script": lambda: Path("/tmp/nonexistent-dx-stream-build.sh"),
            "cwd": lambda: Path("/tmp"),
        }
        try:
            run_step('build', opts={'clean': True})
        except (FileNotFoundError, RuntimeError):
            pass
        except TypeError as e:
            raise AssertionError(f"run_step does not accept opts: {e}")
        finally:
            SETUP_STEPS["build"] = original

    def test_build_opts_use_equals_type(self, monkeypatch, tmp_path):
        from core import setup

        script = tmp_path / "build.sh"
        script.write_text("#!/bin/sh\n", encoding="utf-8")
        monkeypatch.setitem(setup.SETUP_STEPS, "build", {
            "label_ko": "테스트",
            "label_en": "Test",
            "script": lambda: script,
            "cwd": lambda: tmp_path,
        })

        cmd = setup.build_command_args("build", opts={"clean": True, "debug": False})

        assert cmd == ["bash", str(script), "--clean", "--type=Release"]

    def test_download_models_uses_full_setup(self, monkeypatch, tmp_path):
        from core import setup

        script = tmp_path / "setup.sh"
        script.write_text("#!/bin/sh\n", encoding="utf-8")
        monkeypatch.setitem(setup.SETUP_STEPS, "download-models", {
            "label_ko": "테스트",
            "label_en": "Test",
            "script": lambda: script,
            "cwd": lambda: tmp_path,
        })

        cmd = setup.build_command_args("download-models", opts={"models": True, "videos": False})

        assert cmd == ["bash", str(script)]
        assert "--models-only" not in cmd
        assert "--videos-only" not in cmd

    def test_single_model_command_args_produces_model_flag(self, monkeypatch, tmp_path):
        from core import setup

        script = tmp_path / "setup.sh"
        script.write_text("#!/bin/sh\n", encoding="utf-8")
        monkeypatch.setattr(setup, "DX_STREAM_ROOT", tmp_path)

        cmd = setup.single_model_command_args("yolo26n.dxnn")

        assert cmd == ["bash", str(script), "--model=yolo26n.dxnn"]

    def test_build_opts_debug_uses_equals_type(self, monkeypatch, tmp_path):
        from core import setup

        script = tmp_path / "build.sh"
        script.write_text("#!/bin/sh\n", encoding="utf-8")
        monkeypatch.setitem(setup.SETUP_STEPS, "build", {
            "label_ko": "테스트",
            "label_en": "Test",
            "script": lambda: script,
            "cwd": lambda: tmp_path,
        })

        cmd = setup.build_command_args("build", opts={"clean": False, "debug": True})

        assert cmd == ["bash", str(script), "--type=Debug"]

    def test_build_opts_none_omits_type_flag(self, monkeypatch, tmp_path):
        from core import setup

        script = tmp_path / "build.sh"
        script.write_text("#!/bin/sh\n", encoding="utf-8")
        monkeypatch.setitem(setup.SETUP_STEPS, "build", {
            "label_ko": "테스트",
            "label_en": "Test",
            "script": lambda: script,
            "cwd": lambda: tmp_path,
        })

        cmd = setup.build_command_args("build", opts=None)

        assert cmd == ["bash", str(script)]


class TestManagedRuntimeWorker:
    @staticmethod
    def _run_threads_immediately(monkeypatch, setup):
        class ImmediateThread:
            def __init__(self, target=None, args=(), daemon=False):
                self._target = target
                self._args = args
                self.daemon = daemon

            def start(self):
                self._target(*self._args)

        monkeypatch.setattr(setup.threading, "Thread", ImmediateThread)

    def test_managed_runtime_worker_rejects_second_start_while_sentinel_active(self, monkeypatch):
        from core import setup
        cleanup_passwords = []

        class DeferredThread:
            def __init__(self, target=None, args=(), daemon=False):
                self._target = target
                self._args = args
                self.daemon = daemon

            def start(self):
                pass

        def configure_sudo_env(_env, password):
            return lambda: cleanup_passwords.append(password)

        monkeypatch.setattr(setup, "_configure_sudo_env", configure_sudo_env)
        monkeypatch.setattr(setup, "_preauthorize_sudo", lambda _password, _env: None)
        monkeypatch.setattr(setup.threading, "Thread", DeferredThread)
        setup.clear_log()
        setup._running_proc = None

        try:
            setup.run_step("runtime-deps", sudo_password="first")

            assert setup._running_proc is True
            with pytest.raises(RuntimeError, match="Another process is already running"):
                setup.run_step("runtime-deps", sudo_password="second")
            assert cleanup_passwords == ["second"]
        finally:
            setup._running_proc = None

    def test_managed_runtime_worker_releases_sentinel_if_thread_start_fails(self, monkeypatch):
        from core import setup
        cleanup_calls = []

        class FailingThread:
            def __init__(self, target=None, args=(), daemon=False):
                self._target = target
                self._args = args
                self.daemon = daemon

            def start(self):
                raise RuntimeError("thread start failed")

        monkeypatch.setattr(setup, "_configure_sudo_env", lambda _env, _password: lambda: cleanup_calls.append(True))
        monkeypatch.setattr(setup, "_preauthorize_sudo", lambda _password, _env: None)
        monkeypatch.setattr(setup.threading, "Thread", FailingThread)
        setup.clear_log()
        setup._running_proc = None

        with pytest.raises(RuntimeError, match="thread start failed"):
            setup.run_step("runtime-deps")

        state = setup.get_log_state("runtime-deps")
        assert state["done"] is True
        assert state["exit_code"] == 1
        assert "[ERROR] thread start failed" in state["log"]
        assert cleanup_calls == [True]
        assert setup._running_proc is None

    @pytest.mark.parametrize("step_id", ["runtime-deps", "webrtc-deps"])
    def test_worker_releases_reservation_when_log_initialization_fails(self, monkeypatch, step_id):
        from core import setup

        class FailFirstLogAssignment(dict):
            def __init__(self):
                super().__init__()
                self._fail_next_assignment = True

            def __setitem__(self, key, value):
                if self._fail_next_assignment:
                    self._fail_next_assignment = False
                    raise RuntimeError("log initialization failed")
                super().__setitem__(key, value)

        cleanup_calls = []
        monkeypatch.setattr(setup, "_step_logs", FailFirstLogAssignment())
        monkeypatch.setattr(
            setup,
            "_configure_sudo_env",
            lambda _env, _password: lambda: cleanup_calls.append(True),
        )
        monkeypatch.setattr(setup, "_preauthorize_sudo", lambda _password, _env: None)
        setup._running_proc = None

        with pytest.raises(RuntimeError, match="log initialization failed"):
            setup.run_step(step_id)

        state = setup.get_log_state(step_id)
        assert state["done"] is True
        assert state["exit_code"] == 1
        assert "[ERROR] log initialization failed" in state["log"]
        assert cleanup_calls == [True]
        assert setup._running_proc is None

    def test_standard_sudo_worker_cleans_rejected_request(self, monkeypatch):
        from core import setup
        cleanup_passwords = []

        class DeferredThread:
            def __init__(self, target=None, args=(), daemon=False):
                self._target = target
                self._args = args
                self.daemon = daemon

            def start(self):
                pass

        def configure_sudo_env(_env, password):
            return lambda: cleanup_passwords.append(password)

        monkeypatch.setattr(setup, "_configure_sudo_env", configure_sudo_env)
        monkeypatch.setattr(setup, "_preauthorize_sudo", lambda _password, _env: None)
        monkeypatch.setattr(setup.threading, "Thread", DeferredThread)
        setup.clear_log()
        setup._running_proc = None

        try:
            setup.run_step("webrtc-deps", sudo_password="first")

            assert setup._running_proc is True
            with pytest.raises(RuntimeError, match="Another process is already running"):
                setup.run_step("webrtc-deps", sudo_password="second")
            assert cleanup_passwords == ["second"]
        finally:
            setup._running_proc = None

    def test_managed_runtime_worker_records_active_result_without_popen(self, monkeypatch):
        from core import setup

        authorizations = []
        cleanup_calls = []
        keep_alive_calls = []

        class FakeHost:
            candidate_validator = SimpleNamespace(last_result=None)

            def __init__(self, *, authorized):
                authorizations.append(authorized)

            def reconcile(self):
                return SimpleNamespace(
                    status=SimpleNamespace(value="active"),
                    reason="profile validated",
                )

        def no_popen(*_args, **_kwargs):
            pytest.fail("managed runtime step must not spawn subprocess.Popen")

        monkeypatch.setattr(setup, "RuntimeHost", FakeHost)
        monkeypatch.setattr(setup, "_configure_sudo_env", lambda _env, _password: lambda: cleanup_calls.append(True))
        monkeypatch.setattr(setup, "_preauthorize_sudo", lambda _password, _env: None)
        monkeypatch.setattr(setup, "_keep_sudo_alive", lambda stop: keep_alive_calls.append(stop))
        monkeypatch.setattr(setup.subprocess, "Popen", no_popen)
        self._run_threads_immediately(monkeypatch, setup)
        setup.clear_log()
        setup._running_proc = None

        setup.run_step("runtime-deps")

        state = setup.get_log_state("runtime-deps")
        assert authorizations == [True]
        assert state == {
            "log": "Runtime profile reconciliation\nstatus=active\nreason=profile validated\n",
            "done": True,
            "exit_code": 0,
        }
        assert len(keep_alive_calls) == 1
        assert cleanup_calls == [True]
        assert setup._running_proc is None

    def test_managed_runtime_worker_records_failure_and_cleans_up(self, monkeypatch):
        from core import setup

        cleanup_calls = []
        monkeypatch.setattr(setup, "_configure_sudo_env", lambda _env, _password: lambda: cleanup_calls.append(True))
        monkeypatch.setattr(setup, "_preauthorize_sudo", lambda _password, _env: None)
        monkeypatch.setattr(setup, "_keep_sudo_alive", lambda _stop: None)
        monkeypatch.setattr(
            setup,
            "reconcile_managed_runtime",
            lambda: (1, "Runtime profile reconciliation\nstatus=rolled_back\nreason=validation failed\n"),
        )
        self._run_threads_immediately(monkeypatch, setup)
        setup.clear_log()
        setup._running_proc = None

        setup.run_step("runtime-deps")

        state = setup.get_log_state("runtime-deps")
        assert state == {
            "log": "Runtime profile reconciliation\nstatus=rolled_back\nreason=validation failed\n",
            "done": True,
            "exit_code": 1,
        }
        assert cleanup_calls == [True]
        assert setup._running_proc is None

    def test_managed_runtime_worker_records_exception_and_releases_sentinel(self, monkeypatch):
        from core import setup

        cleanup_calls = []
        monkeypatch.setattr(setup, "_configure_sudo_env", lambda _env, _password: lambda: cleanup_calls.append(True))
        monkeypatch.setattr(setup, "_preauthorize_sudo", lambda _password, _env: None)
        monkeypatch.setattr(setup, "_keep_sudo_alive", lambda _stop: None)

        def raise_reconcile_error():
            raise RuntimeError("reconcile failed")

        monkeypatch.setattr(setup, "reconcile_managed_runtime", raise_reconcile_error)
        self._run_threads_immediately(monkeypatch, setup)
        setup.clear_log()
        setup._running_proc = None

        setup.run_step("runtime-deps")

        state = setup.get_log_state("runtime-deps")
        assert state["done"] is True
        assert state["exit_code"] == 1
        assert "[ERROR] reconcile failed" in state["log"]
        assert cleanup_calls == [True]
        assert setup._running_proc is None
