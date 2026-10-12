"""dx_app runs launched by the studio get DXRT_DYNAMIC_CPU_THREAD=ON.

Models with a CPU task in the graph (RT-DETR r18, for one) stall on that task's single thread even when run async.
On DX-RT 3.5.0, C++ async over 100 frames went from 4.2 FPS (CPU queue 78%) with OFF to 9.3 FPS (30%) with ON.
DX-RT itself prints "To improve FPS, set: 'export DXRT_DYNAMIC_CPU_THREAD=ON'", and the dx_rt docs
(04_Model_Inference.md) and dx_app's performance_patterns give the same advice. A value the user already set (OFF
included) is left alone.
"""
from pathlib import Path

from tests.dx_app.test_inference_runtime_regressions import _prepare_dx_app_runtime

ROOT = Path(__file__).resolve().parents[2]


def test_run_env_turns_dynamic_cpu_thread_on_but_keeps_a_user_choice():
    from shared import dxrt
    assert dxrt.run_env({})["DXRT_DYNAMIC_CPU_THREAD"] == "ON"
    assert dxrt.run_env({"DXRT_DYNAMIC_CPU_THREAD": "OFF"})["DXRT_DYNAMIC_CPU_THREAD"] == "OFF"
    base = {"A": "1"}
    dxrt.run_env(base)
    assert base == {"A": "1"}, "넘긴 dict 를 바꾸지 않는다"


def test_an_inference_run_gets_dynamic_cpu_thread(tmp_path, monkeypatch):
    monkeypatch.delenv("DXRT_DYNAMIC_CPU_THREAD", raising=False)
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    captured = {}

    class FakeProc:
        returncode = 0

        def __init__(self, cmd, stdout=None, **kwargs):
            captured["env"] = kwargs.get("env", {})
            if stdout:
                stdout.write("Overall FPS         :   9.3 FPS\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)
    inference.run_inference("demo", "object_detection", "model.dxnn",
                            input_type="video", video_path="input.mp4", lang="cpp", timeout=1)
    assert captured["env"].get("DXRT_DYNAMIC_CPU_THREAD") == "ON"


def test_live_runs_use_the_same_env():
    src = (ROOT / "dx_app" / "core" / "live.py").read_text(encoding="utf-8")
    assert "run_env(" in src, "카메라 · RTSP live 실행도 같은 env 를 쓴다"


def test_run_env_drops_the_qt_paths_that_opencv_python_sets_on_import():
    """opencv-python rewrites QT_QPA_PLATFORM_PLUGIN_PATH and QT_QPA_FONTDIR to its own cv2/qt on import. Once the
    server has used cv2 (image inference, thumbnails), a later C++ runner would load pip's plugins into the system Qt5
    and abort (-6) with "Could not load the Qt platform plugin xcb", leaving the live view black."""
    from shared import dxrt
    cv2_qt = "/venv/lib/python3.12/site-packages/cv2/qt"
    env = dxrt.run_env({"QT_QPA_PLATFORM_PLUGIN_PATH": cv2_qt + "/plugins", "QT_QPA_FONTDIR": cv2_qt + "/fonts",
                        "QT_PLUGIN_PATH": cv2_qt + "/plugins", "DISPLAY": ":99"})
    assert not {"QT_QPA_PLATFORM_PLUGIN_PATH", "QT_QPA_FONTDIR", "QT_PLUGIN_PATH"} & set(env)
    assert env["DISPLAY"] == ":99"
    mine = {"QT_QPA_PLATFORM_PLUGIN_PATH": "/opt/qt5/plugins"}
    assert dxrt.run_env(mine)["QT_QPA_PLATFORM_PLUGIN_PATH"] == "/opt/qt5/plugins", "사용자가 정한 Qt 는 둔다"
