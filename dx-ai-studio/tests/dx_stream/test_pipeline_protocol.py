"""PipelineBackend protocol conformance tests."""

import sys
from pathlib import Path

_STREAM_ROOT = str(Path(__file__).resolve().parents[2] / "dx_stream")
if _STREAM_ROOT not in sys.path:
    sys.path.insert(0, _STREAM_ROOT)


def _ensure_stream_path():
    for mod_name in list(sys.modules):
        if mod_name == "core" or mod_name.startswith("core."):
            del sys.modules[mod_name]
    if _STREAM_ROOT not in sys.path:
        sys.path.insert(0, _STREAM_ROOT)
    elif sys.path[0] != _STREAM_ROOT:
        sys.path.remove(_STREAM_ROOT)
        sys.path.insert(0, _STREAM_ROOT)


def test_pipeline_backend_protocol_exists():
    """PipelineBackendProtocol is importable from core.backend."""
    _ensure_stream_path()
    from core.backend import PipelineBackendProtocol

    assert hasattr(PipelineBackendProtocol, "start")
    assert hasattr(PipelineBackendProtocol, "stop")
    assert hasattr(PipelineBackendProtocol, "is_running")


def test_pipeline_backend_protocol_is_runtime_checkable():
    """PipelineBackendProtocol supports isinstance checks."""
    _ensure_stream_path()
    from core.backend import PipelineBackendProtocol

    class FakeBackend:
        def start(self, pipeline_str, extra_env=None):
            return "id"

        def stop(self):
            pass

        def is_running(self):
            return False

        def get_pipeline_id(self):
            return None

        def get_last_error(self):
            return None

    assert isinstance(FakeBackend(), PipelineBackendProtocol)


def test_pipeline_manager_satisfies_backend_protocol(monkeypatch):
    """PipelineManager satisfies PipelineBackendProtocol."""
    _ensure_stream_path()
    from core.backend import PipelineBackendProtocol
    import core.pipeline as pipeline

    monkeypatch.setattr(pipeline, "_gst_available", False)

    pm = pipeline.PipelineManager()
    assert isinstance(pm, PipelineBackendProtocol)


def test_pipeline_backend_protocol_rejects_non_backend():
    """A plain object should not satisfy PipelineBackendProtocol."""
    _ensure_stream_path()
    from core.backend import PipelineBackendProtocol

    class NotABackend:
        pass

    assert not isinstance(NotABackend(), PipelineBackendProtocol)
