import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _function_body(source: str, signature: str) -> str:
    start = source.index(signature)
    paren = source.index("(", start)
    depth = 0
    for pos in range(paren, len(source)):
        if source[pos] == "(":
            depth += 1
        elif source[pos] == ")":
            depth -= 1
            if depth == 0:
                brace = source.index("{", pos)
                break
    else:
        raise AssertionError(f"Could not parse function signature: {signature}")
    depth = 0
    for pos in range(brace, len(source)):
        if source[pos] == "{":
            depth += 1
        elif source[pos] == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1:pos]
    raise AssertionError(f"Could not parse function body: {signature}")


def test_quick_run_waits_for_media_readiness_and_invokes_once():
    source = (ROOT / "dx_app" / "static" / "js" / "inference.js").read_text(
        encoding="utf-8"
    )
    quick_run = _function_body(source, "function quickRun(")
    apply_pending = _function_body(source, "function _applyPendingAutoSelect(")
    start_pending = _function_body(source, "function _tryRunPendingQuickRun(")

    assert "consumed:false" in quick_run
    assert "setTimeout" not in apply_pending
    assert "ps.selectedInput=_selectedRunInput()" not in apply_pending
    assert "mediaReady=true" in source
    assert "doRun()" in start_pending
    assert start_pending.index("ps.consumed=true") < start_pending.index("doRun()")


def test_quick_run_defers_consumption_until_an_active_run_finishes():
    source = (ROOT / "dx_app" / "static" / "js" / "inference.js").read_text(
        encoding="utf-8"
    )
    start_pending = _function_body(source, "function _tryRunPendingQuickRun(")
    do_run = _function_body(source, "async function doRun(")

    assert "if(_runInFlight)return;" in start_pending
    assert start_pending.index("if(_runInFlight)return;") < start_pending.index(
        "ps.consumed=true"
    )
    assert "_tryRunPendingQuickRun();" in do_run
    assert do_run.index("_runInFlight=false") < do_run.rindex(
        "_tryRunPendingQuickRun();"
    )


def test_quick_run_preserves_existing_user_selected_media():
    source = (ROOT / "dx_app" / "static" / "js" / "inference.js").read_text(
        encoding="utf-8"
    )
    quick_run = _function_body(source, "function quickRun(")
    apply_pending = _function_body(source, "function _applyPendingAutoSelect(")
    render_media = _function_body(source, "function _renderRunMedia(")
    input_mode = _function_body(source, "function updateRunInputMode(")

    assert "selectedMedia" in quick_run
    assert "selectedInput" in quick_run
    assert "selectedInput" in render_media
    assert "!selectedInput" in render_media
    assert "rVideo.value=ps.selectedMedia" in render_media
    assert "ps.selectedInput" in input_mode


def _prepare_dx_app_runtime(tmp_path, monkeypatch):
    import inference

    app_root = tmp_path / "dx_app_root"
    build_dir = app_root / "build"
    outputs_dir = app_root / "outputs"
    cpp_dir = app_root / "cpp_example"
    py_dir = app_root / "python_example"
    for path in (build_dir, outputs_dir, cpp_dir, py_dir):
        path.mkdir(parents=True, exist_ok=True)

    (app_root / "model.dxnn").write_bytes(b"model")
    (app_root / "input.mp4").write_bytes(b"video")
    binary = build_dir / "demo_sync"
    binary.write_text("#!/bin/sh\n")
    binary.chmod(0o755)

    monkeypatch.setattr(inference, "DX_APP_ROOT", app_root)
    monkeypatch.setattr(inference, "BUILD_DIR", build_dir)
    monkeypatch.setattr(inference, "OUTPUTS_DIR", outputs_dir)
    monkeypatch.setattr(inference, "CPP_DIR", cpp_dir)
    monkeypatch.setattr(inference, "PY_DIR", py_dir)
    monkeypatch.setattr(inference, "get_hw", lambda: {})
    monkeypatch.setattr(inference, "_parse_perf", lambda stdout: {"overall_fps": "30"})

    return inference, app_root


def _fake_successful_image_run(monkeypatch, inference, image_bytes=b"result"):
    class FakeProc:
        returncode = 0

        def __init__(self, _cmd, stdout=None, **_kwargs):
            save_path = Path(_kwargs["env"]["DXAPP_SAVE_IMAGE"])
            save_path.write_bytes(image_bytes)
            if stdout:
                stdout.write("[INFO] done\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)


def test_image_run_can_skip_persisting_output_file(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    (inference.DX_APP_ROOT / "input.jpg").write_bytes(b"input")
    _fake_successful_image_run(monkeypatch, inference)

    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_path="input.jpg", timeout=1,
        save_output=False,
    )

    assert result["result_image"]
    assert "result_image_url" not in result
    assert list(inference.OUTPUTS_DIR.glob("result_*.jpg")) == []


def test_image_run_saves_output_file_by_default(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    (inference.DX_APP_ROOT / "input.jpg").write_bytes(b"input")
    _fake_successful_image_run(monkeypatch, inference)

    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_path="input.jpg", timeout=1,
    )

    saved = list(inference.OUTPUTS_DIR.glob("result_demo_*.jpg"))
    assert len(saved) == 1
    assert result["result_image_url"] == f"/outputs/{saved[0].name}"


def test_cpp_image_run_removes_annotated_save_directory(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    temp_dir = tmp_path / "temp"
    temp_dir.mkdir()
    monkeypatch.setattr(inference, "_TMP", str(temp_dir))
    (inference.DX_APP_ROOT / "input.jpg").write_bytes(b"input")
    _fake_successful_image_run(monkeypatch, inference)

    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_path="input.jpg", timeout=1,
        save_output=False,
    )

    assert result["result_image"]
    assert list(temp_dir.glob("dxapp_img_*")) == []


def test_cpp_video_run_enables_save_for_annotated_output(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    captured = {}

    class FakeProc:
        returncode = 0

        def __init__(self, cmd, stdout=None, **_kwargs):
            captured["cmd"] = cmd
            captured["env"] = _kwargs.get("env", {})
            if stdout:
                stdout.write("[INFO] done\nOverall FPS         :   51.0 FPS\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)

    inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="video", video_path="input.mp4", lang="cpp", timeout=1,
    )

    cmd = captured["cmd"]
    assert "--save_video" not in cmd
    assert "--save" not in cmd
    assert "-s" in cmd
    assert "--save-dir" in cmd
    assert "DXAPP_SAVE_IMAGE" not in captured.get("env", {})


def test_video_run_prefers_python_when_script_exists(tmp_path, monkeypatch):
    inference, app_root = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    py_script = inference.PY_DIR / "object_detection" / "demo" / "demo_sync.py"
    py_script.parent.mkdir(parents=True, exist_ok=True)
    py_script.write_text("# stub\n")
    captured = {}

    class FakeProc:
        returncode = 0

        def __init__(self, cmd, stdout=None, **_kwargs):
            captured["cmd"] = cmd
            if stdout:
                stdout.write("[INFO] done\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)

    inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="video", video_path="input.mp4", lang="python", variant="sync", timeout=1,
    )

    cmd = captured["cmd"]
    assert str(py_script) in cmd
    assert "--save" in cmd
    assert "--save-dir" in cmd


def test_classification_run_passes_show_log(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    (inference.DX_APP_ROOT / "input.jpg").write_bytes(b"input")
    captured = {}

    class FakeProc:
        returncode = 0

        def __init__(self, cmd, stdout=None, **_kwargs):
            captured["cmd"] = cmd
            Path(_kwargs["env"]["DXAPP_SAVE_IMAGE"]).write_bytes(b"result")
            if stdout:
                stdout.write("[CLS] hat 0.9\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)

    inference.run_inference(
        "demo", "attribute_recognition", "model.dxnn",
        input_type="image", image_path="input.jpg", timeout=1,
        save_output=False,
    )

    assert "--show-log" in captured["cmd"]


def test_cpp_video_result_uses_saved_output_path_from_stdout(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    saved_video = tmp_path / "run" / "output.mp4"
    saved_video.parent.mkdir()
    saved_video.write_bytes(b"mp4")

    class FakeProc:
        returncode = 0

        def __init__(self, _cmd, stdout=None, **_kwargs):
            if stdout:
                stdout.write(f"[INFO] Saving output video: {saved_video}\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    def fake_convert(src, dst):
        assert Path(src) == saved_video
        Path(dst).write_bytes(b"converted")
        return True

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)
    monkeypatch.setattr(inference, "_cvt_video", fake_convert)
    monkeypatch.setattr(
        inference,
        "_video_has_frames",
        lambda path: Path(path) == saved_video,
    )

    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="video", video_path="input.mp4", timeout=1,
    )

    assert result["result_video_url"].startswith("/outputs/result_demo_")


def test_cpp_run_drains_dxrt_message_queues_before_subprocess(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    calls = []

    class FakeProc:
        returncode = 0

        def __init__(self, _cmd, stdout=None, **_kwargs):
            calls.append("spawn")
            if stdout:
                stdout.write("[INFO] done\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference, "_drain_dxrt_msgqueues", lambda: calls.append("drain"), raising=False)
    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)

    inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_path="input.mp4", timeout=1,
    )

    assert calls[:2] == ["drain", "spawn"]


def test_cpp_run_uses_executable_fallback_when_direct_runner_is_not_executable(
    tmp_path, monkeypatch
):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    direct_runner = inference.BUILD_DIR / "demo_sync"
    direct_runner.chmod(0o644)
    fallback_runner = inference.BUILD_DIR / "mobilenetv2_sync"
    fallback_runner.write_text("#!/bin/sh\n", encoding="utf-8")
    fallback_runner.chmod(0o755)
    captured = {}

    class FakeProc:
        returncode = 0

        def __init__(self, cmd, stdout=None, **_kwargs):
            captured["cmd"] = cmd
            if stdout:
                stdout.write("[INFO] done\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)

    result = inference.run_inference(
        "demo", "classification", "model.dxnn",
        input_type="video", video_path="input.mp4", timeout=1,
    )

    assert result["exit_code"] == 0
    assert captured["cmd"][0] == str(fallback_runner)


def test_image_run_uses_base64_upload_instead_of_default_sample(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    default_sample = inference.DX_APP_ROOT / "sample" / "img" / "sample_street.jpg"
    default_sample.parent.mkdir(parents=True, exist_ok=True)
    default_sample.write_bytes(b"default")
    captured = {}

    class FakeProc:
        returncode = 0

        def __init__(self, cmd, stdout=None, **_kwargs):
            captured["input_path"] = cmd[cmd.index("-i") + 1]
            Path(_kwargs["env"]["DXAPP_SAVE_IMAGE"]).write_bytes(b"result")
            if stdout:
                stdout.write("[INFO] done\n")
                stdout.flush()

        def wait(self, timeout=None):
            return 0

    monkeypatch.setattr(inference.subprocess, "Popen", FakeProc)

    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_base64="dXBsb2FkZWQ=", timeout=1,
        save_output=False,
    )

    assert result["result_image"]
    assert captured["input_path"] != str(default_sample)
    assert Path(captured["input_path"]).name.startswith("dxapp_upload_")
    assert not Path(captured["input_path"]).exists()


def test_image_run_rejects_invalid_base64_upload(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_base64="not valid base64!", timeout=1,
    )
    assert result["error"] == "Invalid image_base64"


def test_image_run_rejects_oversized_base64_upload_before_decoding(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr(inference, "MAX_IMAGE_BASE64_BYTES", 8, raising=False)

    def fail_decode(*_args, **_kwargs):
        raise AssertionError("oversized image_base64 should be rejected before decode")

    monkeypatch.setattr(inference.base64, "b64decode", fail_decode)

    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_base64="QUJDREVGR0hJSg==", timeout=1,
    )

    assert result["error"] == "image_base64 too large"


def test_base64_upload_temp_file_removed_when_binary_missing(tmp_path, monkeypatch):
    inference, _ = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    for binary in inference.BUILD_DIR.glob("demo_*"):
        binary.unlink()
    created = []
    original_mkstemp = inference.tempfile.mkstemp

    def tracking_mkstemp(*args, **kwargs):
        fd, path = original_mkstemp(*args, **kwargs)
        if kwargs.get("prefix") == "dxapp_upload_":
            created.append(Path(path))
        return fd, path

    monkeypatch.setattr(inference.tempfile, "mkstemp", tracking_mkstemp)

    result = inference.run_inference(
        "demo", "object_detection", "model.dxnn",
        input_type="image", image_base64="dXBsb2FkZWQ=", timeout=1,
    )

    assert result["error"].startswith("Binary not found")
    assert created
    assert all(not path.exists() for path in created)


def test_base64_upload_uses_atomic_tempfile_creation():
    source = (ROOT / "dx_app" / "core" / "inference.py").read_text(encoding="utf-8")
    assert "tempfile.mkstemp(prefix=\"dxapp_upload_\"" in source
    assert "tempfile.mktemp(prefix=\"dxapp_upload_\"" not in source
