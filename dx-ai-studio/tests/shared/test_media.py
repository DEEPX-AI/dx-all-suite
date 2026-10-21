"""Media operations use a separate compatible Python, never host native imports."""
import json
import subprocess
import sys
import threading
from functools import lru_cache
from pathlib import Path
from types import SimpleNamespace

import pytest


def test_media_probe_does_not_require_dx_engine(monkeypatch, tmp_path):
    from shared import media

    python = tmp_path / "runtime" / "bin" / "python3"
    python.parent.mkdir(parents=True)
    python.touch()
    monkeypatch.setattr(media.runtime, "STUDIO_INFER_VENV", tmp_path / "absent")
    monkeypatch.setattr(media.runtime, "runtime_venv_roots", lambda: [python.parent.parent])
    monkeypatch.setattr(media.sys, "executable", str(python))
    monkeypatch.setattr(media.shutil, "which", lambda name: None)
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="4.6.0\n", stderr="")

    monkeypatch.setattr(media.subprocess, "run", run)
    media.media_python.cache_clear()
    try:
        assert media.media_python() == str(python)
        command, kwargs = calls[0]
        assert "import numpy, cv2" in command[-1]
        assert "dx_engine" not in command[-1]
        assert "-I" in command
        assert "PYTHONPATH" not in kwargs["env"]
    finally:
        media.media_python.cache_clear()


def test_media_operation_passes_json_only_to_isolated_child(monkeypatch):
    from shared import media

    monkeypatch.setenv("PYTHONPATH", "/foreign/python")
    monkeypatch.setenv("PYTHONHOME", "/foreign/home")
    monkeypatch.setattr(media, "media_python", lambda: "/media/python")
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout='{"count": 12}', stderr="")

    monkeypatch.setattr(media.subprocess, "run", run)
    assert media.run_media("frame_count", source="/clip.mp4") == {"count": 12}
    command, kwargs = calls[0]
    assert command[:3] == ["/media/python", "-I", "-B"]
    assert Path(command[3]).name == "media_worker.py"
    assert command[4:] == ["frame_count"]
    assert json.loads(kwargs["input"]) == {"source": "/clip.mp4"}
    assert "PYTHONPATH" not in kwargs["env"]
    assert "PYTHONHOME" not in kwargs["env"]


@pytest.mark.parametrize(
    "result",
    [
        SimpleNamespace(returncode=1, stdout="", stderr="NumPy ABI mismatch"),
        SimpleNamespace(returncode=0, stdout="not JSON", stderr=""),
        SimpleNamespace(returncode=0, stdout="[]", stderr=""),
    ],
)
def test_media_failures_are_explicit(monkeypatch, result):
    from shared import media

    monkeypatch.setattr(media, "media_python", lambda: "/media/python")
    monkeypatch.setattr(media.subprocess, "run", lambda *args, **kwargs: result)
    with pytest.raises(media.MediaError, match="frame_count"):
        media.run_media("frame_count", source="/clip.mp4")


def test_media_timeout_is_explicit(monkeypatch):
    from shared import media

    monkeypatch.setattr(media, "media_python", lambda: "/media/python")
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])
    monkeypatch.setattr(media.subprocess, "run", timeout)
    with pytest.raises(media.MediaError, match="timed out"):
        media.run_media("cameras", devices=[])


def test_worker_image_operations_without_host_opencv(tmp_path):
    from shared import media

    try:
        python = media.media_python()
    except media.MediaError as error:
        pytest.skip(str(error))
    source = tmp_path / "input.ppm"
    source.write_bytes(b"P6\n8 4\n255\n" + b"\xff\x00\x00" * 32)
    thumb = tmp_path / "thumb.tmp"
    roi = tmp_path / "roi.jpg"
    result = media.run_media("thumbnail", source=str(source), output=str(thumb), width=4)
    assert result == {"width": 4, "height": 2}
    assert thumb.read_bytes().startswith(b"\xff\xd8")
    cropped = media.run_media(
        "crop", source=str(source), output=str(roi),
        roi={"x": 2, "y": 1, "w": 3, "h": 2},
    )
    assert cropped["bbox"] == [2, 1, 5, 3]
    dimensions = subprocess.run(
        [python, "-I", "-B", "-c",
         "import cv2, sys; print(cv2.imread(sys.argv[1]).shape[:2])", str(roi)],
        capture_output=True, text=True, timeout=20, check=True,
    )
    assert dimensions.stdout.strip() == "(2, 3)"


def test_worker_rejects_corrupt_images(tmp_path):
    from shared import media

    try:
        media.media_python()
    except media.MediaError as error:
        pytest.skip(str(error))
    source = tmp_path / "bad.jpg"
    source.write_bytes(b"not an image")
    with pytest.raises(media.MediaError, match="Cannot read image"):
        media.run_media("thumbnail", source=str(source), output=str(tmp_path / "out"), width=4)


@pytest.mark.parametrize("width,height,crop_panel,expected", [
    (16, 4, True, {"width": 8, "height": 4}),
    (32, 8, True, {"width": 14, "height": 8}),
    (16, 8, True, {"width": 16, "height": 8}),
    (4, 2, True, {"width": 8, "height": 4}),
    (16, 4, False, {"width": 8, "height": 4}),
])
def test_normalization_preserves_panel_and_upscale_rules(
    tmp_path, width, height, crop_panel, expected,
):
    from shared import media

    try:
        media.media_python()
    except media.MediaError as error:
        pytest.skip(str(error))
    source, output = tmp_path / "source.ppm", tmp_path / "output.jpg"
    source.write_bytes(b"P6\n8 4\n255\n" + b"\xff\x00\x00" * 32)
    output.write_bytes(
        f"P6\n{width} {height}\n255\n".encode() + b"\xff\x00\x00" * width * height
    )
    assert media.run_media(
        "normalize", source=str(source), output=str(output), crop_panel=crop_panel,
    ) == expected
    assert output.read_bytes().startswith(b"\xff\xd8")


def test_a_failed_probe_is_cached_for_the_process_until_setup_clears_it(monkeypatch, tmp_path):
    """A board without a compatible OpenCV must not re-run interpreter probes (up to 15 s each)
    on every camera list / preview; the failure is kept until a Setup step changes the runtime."""
    from shared import media

    python = tmp_path / "runtime" / "bin" / "python3"
    python.parent.mkdir(parents=True)
    python.touch()
    monkeypatch.setattr(media.runtime, "STUDIO_INFER_VENV", tmp_path / "absent")
    monkeypatch.setattr(media.runtime, "runtime_venv_roots", lambda: [python.parent.parent])
    monkeypatch.setattr(media.sys, "executable", str(python))
    monkeypatch.setattr(media.shutil, "which", lambda name: None)
    calls = []

    def run(command, **kwargs):
        calls.append(command)
        return SimpleNamespace(returncode=1, stdout="", stderr="ModuleNotFoundError: cv2")

    monkeypatch.setattr(media.subprocess, "run", run)
    media.media_python.cache_clear()
    try:
        with pytest.raises(media.MediaError, match="cv2"):
            media.media_python()
        one_round = len(calls)
        assert one_round >= 1
        for _ in range(3):
            with pytest.raises(media.MediaError, match="cv2"):
                media.media_python()
        assert len(calls) == one_round, "the failure is cached, not re-probed"
        media.media_python.cache_clear()
        with pytest.raises(media.MediaError):
            media.media_python()
        assert len(calls) == 2 * one_round
    finally:
        media.media_python.cache_clear()


def test_setup_steps_clear_the_media_cache_when_they_finish():
    source = (Path(__file__).resolve().parents[2] / "dx_app" / "core" / "setup_steps.py").read_text()
    assert "media_python.cache_clear()" in source


def test_setup_cache_reset_cannot_be_overwritten_by_an_inflight_failure(monkeypatch):
    from shared import media

    media.media_python.cache_clear()
    probing = threading.Event()
    release_probe = threading.Event()
    resetting = threading.Event()
    reset_done = threading.Event()
    failures = []
    attempts = []

    @lru_cache(maxsize=1)
    def probe():
        attempts.append(None)
        if len(attempts) == 1:
            probing.set()
            assert release_probe.wait(5)
            raise media.MediaError("pre-Setup OpenCV unavailable")
        return "/repaired/python"

    def old_request():
        try:
            media.media_python()
        except media.MediaError as error:
            failures.append(str(error))

    def reset():
        resetting.set()
        media.media_python.cache_clear()
        reset_done.set()

    monkeypatch.setattr(media, "_probe_media_python", probe)
    request = threading.Thread(target=old_request)
    setup = threading.Thread(target=reset)
    try:
        request.start()
        assert probing.wait(5)
        setup.start()
        assert resetting.wait(5)
        assert not reset_done.wait(0.1), "Reset completed while an older probe could still publish a failure"
        release_probe.set()
        request.join(5)
        setup.join(5)
        assert not request.is_alive() and not setup.is_alive()
        assert failures == ["pre-Setup OpenCV unavailable"]
        assert reset_done.is_set()
        assert media.media_python() == "/repaired/python"
        assert media.media_python() == "/repaired/python"
    finally:
        release_probe.set()
        request.join(5)
        if setup.ident is not None:
            setup.join(5)
        media.media_python.cache_clear()
