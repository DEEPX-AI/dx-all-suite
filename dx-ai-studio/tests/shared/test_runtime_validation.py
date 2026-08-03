"""Tests for read-only base runtime candidate validation."""
from subprocess import CompletedProcess
from pathlib import Path


def test_base_validation_requires_complete_python_plugin_and_postprocess(tmp_path):
    from shared.runtime_validation import validate_base_runtime

    python = tmp_path / "infer" / "bin" / "python3"
    plugin = tmp_path / "gst" / "libgstdxstream.so"
    postprocess = tmp_path / "postprocess"
    python.parent.mkdir(parents=True)
    plugin.parent.mkdir(parents=True)
    postprocess.mkdir()
    python.touch()
    plugin.touch()

    result = validate_base_runtime(
        python_probe=lambda: python,
        plugin_path=plugin,
        postprocess_dir=postprocess,
        element_probe=lambda *_: True,
    )

    assert result.passed
    assert {check.check_id for check in result.checks} == {
        "app.python", "gst.plugin", "gst.postprocess_directory",
        "gst.dxinfer",
    }


def test_base_validation_reports_missing_plugin_with_stable_id(tmp_path):
    from shared.runtime_validation import validate_base_runtime

    python = tmp_path / "infer" / "bin" / "python3"
    python.parent.mkdir(parents=True)
    python.touch()
    result = validate_base_runtime(
        python_probe=lambda: python,
        plugin_path=tmp_path / "missing" / "libgstdxstream.so",
        postprocess_dir=tmp_path / "postprocess",
    )

    assert result.first_failure.check_id == "gst.plugin"


def test_base_validation_discovers_debian_multiarch_plugin_without_shell_env(tmp_path, monkeypatch):
    import shared.runtime_validation as validation

    python = tmp_path / "infer" / "bin" / "python3"
    plugin_dir = tmp_path / "usr" / "local" / "lib" / "x86_64-linux-gnu" / "gstreamer-1.0"
    postprocess = tmp_path / "postprocess"
    python.parent.mkdir(parents=True)
    plugin_dir.mkdir(parents=True)
    postprocess.mkdir()
    python.touch()
    (plugin_dir / "libgstdxstream.so").touch()
    monkeypatch.setattr(validation, "KNOWN_PLUGIN_DIRECTORIES", (plugin_dir,))

    result = validation.validate_base_runtime(
        python_probe=lambda: python,
        postprocess_dir=postprocess,
        element_probe=lambda *_: True,
    )

    assert result.passed


def test_base_validation_blocks_when_dxinfer_factory_cannot_load(tmp_path, monkeypatch):
    import shared.runtime_validation as validation

    python = tmp_path / "infer" / "bin" / "python3"
    plugin = tmp_path / "gst" / "libgstdxstream.so"
    postprocess = tmp_path / "postprocess"
    python.parent.mkdir(parents=True)
    plugin.parent.mkdir(parents=True)
    postprocess.mkdir()
    python.touch()
    plugin.touch()
    monkeypatch.setattr(
        validation,
        "_probe_dxinfer_element",
        lambda *_: False,
        raising=False,
    )

    result = validation.validate_base_runtime(
        python_probe=lambda: python,
        plugin_path=plugin,
        postprocess_dir=postprocess,
    )

    assert not result.passed
    assert result.first_failure.check_id == "gst.dxinfer"


def test_selected_pipeline_validation_uses_active_context_and_never_transitions_state():
    import shared.runtime_validation as validation

    assert hasattr(validation, "validate_stream_pipeline")
    captured = {}

    def runner(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return CompletedProcess(args, 0, "", "")

    environment = {
        "VIRTUAL_ENV": "/runtime/infer",
        "GST_PLUGIN_PATH": "/runtime/gst",
        "LD_LIBRARY_PATH": "/runtime/lib",
        "PYTHONNOUSERSITE": "1",
    }
    result = validation.validate_stream_pipeline(
        "videotestsrc ! fakesink",
        python_executable=Path("/runtime/infer/bin/python3"),
        environment=environment,
        runner=runner,
    )

    assert result.passed
    assert captured["args"][0] == "/runtime/infer/bin/python3"
    assert captured["kwargs"]["env"] == environment
    assert captured["kwargs"]["input"] == "videotestsrc ! fakesink"
    assert "Gst.parse_launch" in validation._STREAM_PIPELINE_PARSE_PROBE
    assert "set_state" not in validation._STREAM_PIPELINE_PARSE_PROBE


def test_selected_pipeline_validation_returns_stable_parse_failure():
    import shared.runtime_validation as validation

    assert hasattr(validation, "validate_stream_pipeline")
    result = validation.validate_stream_pipeline(
        "unknownsource ! fakesink",
        python_executable=Path("/runtime/infer/bin/python3"),
        environment={},
        runner=lambda args, **_kwargs: CompletedProcess(
            args, 2, "", "no element \"unknownsource\""
        ),
    )

    assert not result.passed
    failure = result.first_failure
    assert failure is not None
    assert failure.check_id == "gst.selected_pipeline"
    assert "no element" in failure.observed