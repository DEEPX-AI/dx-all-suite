"""setup.py 테스트 — step 정의, 상태 확인, 스크립트 경로"""
import sys, pytest
from pathlib import Path
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

    def test_step_has_required_fields(self):
        from core.setup import SETUP_STEPS
        required = {"label_ko", "label_en", "cwd"}
        for step_id, step in SETUP_STEPS.items():
            assert required.issubset(step.keys()), f"Step {step_id} missing fields"
            assert "script" in step or "cmd" in step, f"Step {step_id} needs script or cmd"

    def test_step_scripts_are_callable(self):
        from core.setup import SETUP_STEPS
        for step_id, step in SETUP_STEPS.items():
            if "script" not in step:
                continue
            path = step["script"]()
            assert isinstance(path, Path)
            assert path.name.endswith(".sh")

    def test_driver_step_uses_existing_driver_entrypoint(self):
        from core.setup import SETUP_STEPS

        step = SETUP_STEPS["driver"]
        script = step["script"]()
        assert script.exists(), f"{script} does not exist"
        assert script.name == "install.sh"
        assert "--target=dx_rt_npu_linux_driver" in step.get("args", lambda: [])()

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
