"""tests/acceptance/hardware.py — what the acceptance runner detects before it runs anything."""
from __future__ import annotations

import importlib.util
import struct
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("acceptance_hardware", ROOT / "tests" / "acceptance" / "hardware.py")
hw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hw)


def _fake_v4l2(monkeypatch, device_caps: int):
    """os.open/os.close and fcntl.ioctl as Linux and CPython behave for VIDIOC_QUERYCAP: a mutable buffer is
    filled in place and the call returns the ioctl's int result (0); only an immutable argument comes back as bytes."""
    monkeypatch.setattr(hw.os, "open", lambda path, flags: 7)
    monkeypatch.setattr(hw.os, "close", lambda fd: None)

    def ioctl(fd, request, arg, mutate_flag=True):
        assert request == hw._VIDIOC_QUERYCAP
        filled = bytearray(len(arg))
        filled[0:9] = b"uvcvideo\0"
        struct.pack_into("<II", filled, 84, hw._V4L2_CAP_DEVICE_CAPS | device_caps, device_caps)
        if isinstance(arg, bytearray) and mutate_flag:
            arg[:] = filled
            return 0
        return bytes(filled)

    monkeypatch.setattr(hw.fcntl, "ioctl", ioctl)


def test_a_uvc_capture_camera_is_detected(monkeypatch):
    _fake_v4l2(monkeypatch, hw._V4L2_CAP_VIDEO_CAPTURE)
    assert hw._is_capture_device("/dev/video0") is True


def test_a_metadata_node_of_the_same_camera_is_not_a_capture_device(monkeypatch):
    _fake_v4l2(monkeypatch, 0x00800000)            # V4L2_CAP_META_CAPTURE only (uvcvideo's second node)
    assert hw._is_capture_device("/dev/video1") is False


def test_probe_camera_reports_the_capture_nodes(monkeypatch):
    _fake_v4l2(monkeypatch, hw._V4L2_CAP_VIDEO_CAPTURE)
    monkeypatch.setattr(hw.glob, "glob", lambda pattern: ["/dev/video0"])
    assert hw.probe_camera() == (True, "/dev/video0")


def test_one_failing_probe_is_reported_and_never_stops_the_others(monkeypatch):
    def broken():
        raise TypeError("a bytes-like object is required, not 'int'")

    monkeypatch.delenv("DX_ACCEPT_HW", raising=False)
    monkeypatch.setattr(hw, "_PROBES", {k: (broken if k == "camera" else (lambda k=k: (True, k))) for k in hw.KINDS})
    got = hw.probe_all()
    assert set(got) == set(hw.KINDS)
    assert got["camera"][0] is False and "camera probe failed" in got["camera"][1] and "TypeError" in got["camera"][1]
    assert all(got[k] == (True, k) for k in hw.KINDS if k != "camera")


def test_an_unreadable_camera_is_reported_as_permission_denied_not_as_no_capture_device(monkeypatch):
    import errno

    def denied(path, flags):
        raise PermissionError(errno.EACCES, "Permission denied", path)

    monkeypatch.setattr(hw.os, "open", denied)
    monkeypatch.setattr(hw.glob, "glob", lambda pattern: ["/dev/video0", "/dev/video1"])
    ok, detail = hw.probe_camera()
    assert ok is False
    assert detail == "no usable camera: permission denied (/dev/video0, /dev/video1)"
    assert "not V4L2" not in detail


def _dx_app_tree(tmp_path, built=True, models=1):
    root = tmp_path / "dx_app"
    (root / "config").mkdir(parents=True)
    (root / "config" / "model_registry.json").write_text("[]")
    (root / "bin").mkdir()
    if built:
        runner = root / "bin" / "yolov8_sync"
        runner.write_text("")
        runner.chmod(0o755)
    (root / "assets" / "models").mkdir(parents=True)
    for i in range(models):
        (root / "assets" / "models" / f"m{i}.dxnn").write_bytes(b"DXNN")
    return root


@pytest.mark.parametrize(("built", "models", "ok", "says"), [
    (True, 2, True, "2 models"), (False, 2, False, "not built"), (True, 0, False, "no dx_app models downloaded")])
def test_dx_app_is_a_prepared_board_s_dx_app(tmp_path, monkeypatch, built, models, ok, says):
    root = _dx_app_tree(tmp_path, built, models)
    monkeypatch.setattr(hw, "_studio_answer", lambda code, timeout=0: {"root": str(root),
                                                                        "models": str(root / "assets" / "models")})
    got = hw.probe_dx_app()
    assert got[0] is ok and says in got[1], got


def test_a_checkout_without_the_dx_runtime_submodule_has_no_dx_app(tmp_path, monkeypatch):
    monkeypatch.setattr(hw, "_studio_answer", lambda code, timeout=0: {"root": str(tmp_path / "dx_app"),
                                                                        "models": str(tmp_path / "m")})
    ok, detail = hw.probe_dx_app()
    assert not ok and "dx_app is not installed" in detail


def test_dx_rt_is_a_python_with_dx_engine(monkeypatch):
    monkeypatch.setattr(hw, "_studio_answer", lambda code, timeout=0: None)
    assert hw.probe_dx_rt() == (False, "dx-runtime is not installed (no Python with dx_engine; dx-runtime/install.sh)")
    monkeypatch.setattr(hw, "_studio_answer", lambda code, timeout=0: "/rt/bin/python3")
    assert hw.probe_dx_rt() == (True, "dx_engine via /rt/bin/python3")


def test_dx_compiler_needs_its_sample_models_and_dx_com_but_not_the_compile_disk(tmp_path, monkeypatch):
    monkeypatch.setattr(hw, "SUITE", tmp_path)
    monkeypatch.setattr(hw, "_dx_com_status", lambda: {"ok": True, "v": "2.4.1"})
    assert not hw.probe_dx_compiler()[0]
    onnx = tmp_path / "dx-compiler" / "dx_com" / "sample_models" / "onnx"
    onnx.mkdir(parents=True)
    (onnx / "MobileNetV2-1.onnx").write_bytes(b"")
    assert hw.probe_dx_compiler()[0]
    monkeypatch.setattr(hw, "_dx_com_status", lambda: {"ok": False, "v": None})
    assert hw.probe_dx_compiler() == (False, "dx_com not installed (dx-compiler venv; DX Compiler > Setup)")


def test_the_runner_accepts_every_kind_the_probes_answer():
    spec = importlib.util.spec_from_file_location("acceptance_runner", ROOT / "scripts" / "acceptance.py")
    runner = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runner)
    assert tuple(runner.REQUIREMENTS) == hw.KINDS == tuple(hw._PROBES)
