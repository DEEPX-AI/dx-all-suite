"""The Studio interpreter must not inherit native SDK package environments."""
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("available", [True, False])
def test_system_info_uses_isolated_opencv_probe(monkeypatch, available):
    import builtins
    from shared import hardware, media

    native_imports = []
    original_import = builtins.__import__

    def guarded(name, *args, **kwargs):
        if name.split(".")[0] in {"numpy", "cv2", "dx_engine"}:
            native_imports.append(name)
            raise ImportError("Native imports belong in a worker")
        return original_import(name, *args, **kwargs)

    def probe(operation):
        assert operation == "probe"
        if not available:
            raise media.MediaError("OpenCV ABI mismatch")
        return {"opencv": "5.0.0", "numpy": "2.5.3"}

    monkeypatch.setattr(media, "run_media", probe)
    monkeypatch.setattr(builtins, "__import__", guarded)
    info = hardware.get_sysinfo()
    assert not native_imports, native_imports
    assert info["opencv"] == ("5.0.0" if available else "N/A")
    if not available:
        assert info["opencv_error"] == "OpenCV ABI mismatch"


def test_config_import_preserves_package_paths_and_telemetry(tmp_path):
    foreign = tmp_path / "site-packages"
    (foreign / "numpy").mkdir(parents=True)
    (foreign / "numpy" / "__init__.py").write_text("")
    script = """
import importlib.abc
import importlib.util
import sys
from pathlib import Path
from shared import hardware, runtime

foreign = Path(sys.argv[1])
runtime.dx_engine_search_paths = lambda: [foreign]
runtime.runtime_python = lambda: None
runtime.dx_engine_pythonpath_dirs = lambda python: []
native_imports = []
class NativeGuard(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'dx_engine', 'cv2'}:
            native_imports.append(fullname)
            raise ImportError('Native imports belong in a worker')
sys.meta_path.insert(0, NativeGuard())
binding = object()
hardware.init_hw(telemetry=binding)
before_paths = list(sys.path)
before_numpy = importlib.util.find_spec('numpy')
before_origin = before_numpy.origin if before_numpy else None
from dx_app.core import config
after_numpy = importlib.util.find_spec('numpy')
after_origin = after_numpy.origin if after_numpy else None
assert sys.path == before_paths, 'Studio config injected foreign site-packages'
assert after_origin == before_origin, 'Studio config changed NumPy origin'
assert not native_imports, native_imports
assert hardware._TELEMETRY is binding, 'Config import detached live telemetry'
"""
    result = subprocess.run(
        [sys.executable, "-c", script, str(foreign)],
        cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("serve_fails", [False, True])
def test_app_main_owns_isolated_telemetry_lifecycle(monkeypatch, serve_fails):
    from dx_app import server
    from dx_monitor.core import hardware_init

    calls = []
    def serve():
        calls.append("serve")
        if serve_fails:
            raise RuntimeError("server stopped unexpectedly")
    http = SimpleNamespace(serve_forever=serve, server_close=lambda: calls.append("close"))
    runner = SimpleNamespace(
        create_http_server=lambda port: http,
        register_signals=lambda: None, print_banner=lambda port: None,
    )
    monkeypatch.setattr(server, "DXServer", lambda *args: runner)
    monkeypatch.setattr(server, "_idle_shutdown_enabled", lambda: False)
    monkeypatch.setattr(server, "_stop_children", lambda: calls.append("children"))
    monkeypatch.delenv("DX_MONITOR_PORT_FILE", raising=False)   # standalone: DX App owns a supervisor
    monkeypatch.setattr(hardware_init, "init", lambda **kw: calls.append("telemetry_start"))
    monkeypatch.setattr(hardware_init, "shutdown", lambda: calls.append("telemetry_stop"))
    monkeypatch.setattr(sys, "argv", ["dx-app", "--no-browser"])
    if serve_fails:
        with pytest.raises(RuntimeError, match="server stopped unexpectedly"):
            server.main()
    else:
        server.main()
    assert calls == ["telemetry_start", "serve", "children", "telemetry_stop", "close"]


def test_camera_route_reports_media_runtime_failure(monkeypatch):
    from dx_app import server
    from shared.media import MediaError
    from tests.dx_app.test_server import _handler

    def unavailable():
        raise MediaError("OpenCV media runtime unavailable: ABI mismatch")
    monkeypatch.setattr(server, "list_cameras", unavailable)
    response = _handler("GET", "/api/cameras")
    assert response["code"] == 503
    assert response["data"]["error_key"] == "media_runtime_unavailable"
    assert "ABI mismatch" in response["data"]["error"]


def test_cascade_crop_does_not_import_host_opencv(tmp_path, monkeypatch):
    import builtins
    from dx_app.core import inference
    from shared import media

    try:
        media.media_python()
    except media.MediaError as error:
        pytest.skip(str(error))
    source = tmp_path / "input.jpg"
    source.write_bytes(b"P6\n8 4\n255\n" + b"\xff\x00\x00" * 32)
    monkeypatch.setattr(inference, "DX_APP_ROOT", tmp_path)
    monkeypatch.setattr(inference, "_TMP", str(tmp_path))
    monkeypatch.setattr(inference, "_parse_detections", lambda output: [
        {"bbox": [2, 1, 5, 3], "disp_w": 8, "disp_h": 4}
    ])
    calls = []
    def infer(*args, **kwargs):
        calls.append(kwargs["image_path"])
        assert Path(kwargs["image_path"]).read_bytes()
        return {"output": "detection"}
    monkeypatch.setattr(inference, "run_inference", infer)
    original_import = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name.split(".")[0] in {"numpy", "cv2"}:
            raise AssertionError(f"Host native import: {name}")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded)
    results = inference.run_pipeline(
        [{"model_name": "detector"}, {"model_name": "classifier"}],
        str(source), mode="cascade",
    )
    assert len(calls) == 2
    assert results[1]["cascade_crops"][0]["crop_bbox"] == [2, 1, 5, 3]
    assert not Path(calls[1]).exists()


@pytest.mark.parametrize("operation", ["thumbnail", "roi"])
def test_image_helpers_work_without_host_opencv(tmp_path, monkeypatch, operation):
    import builtins
    from dx_app.core import assets, camera
    from shared import media

    try:
        media.media_python()
    except media.MediaError as error:
        pytest.skip(str(error))
    source = tmp_path / "input.jpg"
    source.write_bytes(b"P6\n8 4\n255\n" + b"\xff\x00\x00" * 32)
    monkeypatch.setattr(assets, "DX_APP_ROOT", tmp_path)
    monkeypatch.setattr(assets, "_THUMB_CACHE_DIR", tmp_path / "cache")
    monkeypatch.setattr(camera, "_TMP", str(tmp_path))
    original_import = builtins.__import__
    def guarded(name, *args, **kwargs):
        if name.split(".")[0] in {"numpy", "cv2"}:
            raise AssertionError(f"Host native import: {name}")
        return original_import(name, *args, **kwargs)
    monkeypatch.setattr(builtins, "__import__", guarded)
    if operation == "thumbnail":
        image = assets.sample_thumbnail("input.jpg", width=4)
        expected = {"width": 4, "height": 2}
        assert assets.sample_thumbnail("input.jpg", width=4) == image
    else:
        image = Path(camera._crop_roi(source, {"x": 2, "y": 1, "w": 3, "h": 2}))
        expected = {"width": 3, "height": 2}
    assert image is not None and image.read_bytes().startswith(b"\xff\xd8")
    assert media.run_media(
        "thumbnail", source=str(image), output=str(tmp_path / "check.jpg"), width=100,
    ) == expected


def test_thumbnail_publish_failure_cleans_owned_temporary_file(tmp_path, monkeypatch):
    from dx_app.core import assets

    (tmp_path / "input.jpg").write_bytes(b"image")
    monkeypatch.setattr(assets, "DX_APP_ROOT", tmp_path)
    monkeypatch.setattr(assets, "_THUMB_CACHE_DIR", tmp_path / "cache")
    def thumbnail(operation, **params):
        Path(params["output"]).write_bytes(b"jpeg")
    monkeypatch.setattr(assets, "run_media", thumbnail)
    def denied(*args):
        raise PermissionError("cannot publish thumbnail")
    monkeypatch.setattr(assets.os, "replace", denied)
    assert assets.sample_thumbnail("input.jpg") is None
    assert not list((tmp_path / "cache").iterdir())


def test_roi_cleanup_failure_preserves_crop_error_and_reports_the_staging_file(tmp_path, monkeypatch, caplog):
    from dx_app.core import camera
    from shared.media import MediaError

    original = MediaError("crop runtime unavailable")
    def crop(*args, **kwargs):
        raise original
    unlink = Path.unlink
    def denied(path, *args, **kwargs):
        if path.parent == tmp_path and path.suffix == ".jpg":
            raise PermissionError("ROI cleanup denied")
        return unlink(path, *args, **kwargs)

    monkeypatch.setattr(camera, "_TMP", str(tmp_path))
    monkeypatch.setattr(camera, "run_media", crop)
    monkeypatch.setattr(Path, "unlink", denied)
    with pytest.raises(MediaError) as caught:
        camera._crop_roi(tmp_path / "source.jpg", {"x": 0, "y": 0, "w": 1, "h": 1})
    assert caught.value is original
    remaining = list(tmp_path.glob("*.jpg"))
    assert len(remaining) == 1
    assert str(remaining[0]) in caplog.text
    assert "ROI cleanup denied" in caplog.text


@pytest.mark.parametrize("failure", [ImportError("cache import failed"), AttributeError("cache reset missing")])
def test_setup_reports_media_cache_reset_failures(tmp_path, monkeypatch, caplog, failure):
    from dx_app.core import setup_steps
    from shared import media

    started = []
    thread_type = setup_steps.threading.Thread
    def thread(*args, **kwargs):
        worker = thread_type(*args, **kwargs)
        started.append(worker)
        return worker
    def reset():
        raise failure

    monkeypatch.setattr(setup_steps.threading, "Thread", thread)
    monkeypatch.setattr(media.media_python, "cache_clear", reset)
    monkeypatch.setitem(setup_steps.SETUP_STEPS, "test-cache-reset", {
        "cmd": lambda: [sys.executable, "-c", "print('installed')"],
        "cwd": lambda: tmp_path,
    })
    for name, value in (("_comp_proc", None), ("_comp_stdin_proc", None),
                        ("_comp_done", False), ("_comp_exit_code", -1), ("_comp_log", "")):
        monkeypatch.setattr(setup_steps.config, name, value)
    assert setup_steps.setup_run("test-cache-reset") == {"ok": True, "started": True}
    assert len(started) == 1
    started[0].join(5)
    assert not started[0].is_alive()
    assert setup_steps.config._comp_done is True
    assert setup_steps.config._comp_exit_code == 0
    assert "installed" in setup_steps.config._comp_log
    assert str(failure) in caplog.text
    assert any(record.exc_info for record in caplog.records)
