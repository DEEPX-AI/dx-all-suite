"""The python-variant interpreter is resolved at use time, not once at import.

Resolving it once kept the dx_app server on None after Setup → Python Inference Deps had made one
available, so Use Default kept failing (with a raw TypeError) until the Studio restarted."""
import pytest
from dx_app.core import config


@pytest.fixture(autouse=True)
def _no_pythonpath_probe(monkeypatch):
    # dx_engine_pythonpath_dirs(None) itself calls runtime_python(); keep the probe under the test's control.
    monkeypatch.setattr(config._runtime, "dx_engine_pythonpath_dirs", lambda py: [])
    for name in ("_RUNTIME_PYTHON", "_RUNTIME_PYTHONPATH", "_DX_ENGINE_SRC_DIRS", "_RUNTIME_PROBED_AT"):
        monkeypatch.setattr(config, name, getattr(config, name))   # restored after each test


def test_none_is_reprobed_without_restart(monkeypatch):
    seq = iter([None, "/venv/bin/python3"])
    monkeypatch.setattr(config._runtime, "runtime_python", lambda: next(seq))
    monkeypatch.setattr(config, "_RUNTIME_PROBED_AT", 0.0)
    assert config.refresh_runtime_python() is None
    monkeypatch.setattr(config, "_RUNTIME_PROBED_AT", 0.0)        # throttle window elapsed
    assert config.runtime_python() == "/venv/bin/python3"
    assert config._RUNTIME_PYTHON == "/venv/bin/python3"          # graph_gallery reads the attribute


def test_none_reprobe_is_throttled(monkeypatch):
    calls = []
    monkeypatch.setattr(config._runtime, "runtime_python", lambda: calls.append(1))
    config.refresh_runtime_python()
    n = len(calls)
    config.runtime_python(); config.runtime_python()
    assert len(calls) == n


def test_python_run_without_interpreter_says_what_to_do(tmp_path, monkeypatch):
    from tests.dx_app.test_inference_runtime_regressions import _prepare_dx_app_runtime
    inference, app_root = _prepare_dx_app_runtime(tmp_path, monkeypatch)
    monkeypatch.setattr(inference.config, "runtime_python", lambda: None)
    py = inference.PY_DIR / "object_detection" / "demo" / "demo_sync.py"
    py.parent.mkdir(parents=True); py.write_text("# stub\n")
    (app_root / "img.jpg").write_bytes(b"x")
    r = inference.run_inference("demo", "object_detection", "model.dxnn", lang="python",
                                variant="sync", input_type="image", image_path="img.jpg")
    assert r["error_key"] == "python_runtime_missing"
    assert "Demo Quick Start" in r["error"]


def test_setup_step_completion_refreshes_interpreter():
    import inspect
    from dx_app.core import setup_steps
    assert "refresh_runtime_python()" in inspect.getsource(setup_steps._setup_start)


def test_guidance_names_buttons_that_exist():
    """inference-venv is hidden from the Setup list on purpose; point at Quick Start / Set up the rest (they re-run it)."""
    import inspect
    from dx_app.core import setup_steps, inference
    for src in (inspect.getsource(setup_steps.deep_diagnostics), inspect.getsource(inference.run_inference)):
        assert "Run Python Inference Deps" not in src and "Run Setup → Python Inference Deps" not in src
    assert "Demo Quick Start" in inspect.getsource(inference.run_inference)
