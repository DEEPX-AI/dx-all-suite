"""html_export's venv fallback — the path that actually runs in production.

dx_com normally lives in its OWN venv (the standard launcher setup), so the
in-process `from dx_com.html_export import ...` raises ModuleNotFoundError and
every call goes through _call_via_venv. A break in its arg marshalling or
error reporting would surface only as an opaque failure in the Compiler UI.

No real dx_com or venv is needed — subprocess.run is faked.
"""
import importlib.util
import json

import pytest

from dx_compiler.core import html_export as HE


class _Proc:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


@pytest.fixture()
def venv(monkeypatch):
    """Pretend a compiler venv exists and capture what would be executed."""
    calls = []
    monkeypatch.setattr(HE, "_venv_python", lambda: "/fake/venv/bin/python")

    def _install(proc):
        def _run(cmd, **kwargs):
            calls.append((cmd, kwargs))
            return proc
        monkeypatch.setattr(HE.subprocess, "run", _run)

    _install(_Proc(stdout="<html>ok</html>"))
    return calls, _install


class TestMissingVenv:
    def test_no_venv_raises_a_actionable_error(self, monkeypatch):
        monkeypatch.setattr(HE, "_venv_python", lambda: None)
        with pytest.raises(RuntimeError, match="no compiler venv was found"):
            HE._call_via_venv("generate_summary_html", model_path="m")


class TestArgumentMarshalling:
    def test_kwargs_travel_as_json_in_the_environment(self, venv):
        """Args go via an env var, not argv — a model path with spaces or a nested
        enhanced_scheme dict would not survive naive command-line quoting."""
        calls, _ = venv
        HE._call_via_venv(
            "generate_summary_html",
            model_path="/models/my model.onnx",
            enhanced_scheme={"DXQ-P0": {"a": 1}},
        )
        (cmd, kwargs) = calls[0]
        payload = json.loads(kwargs["env"]["DX_COMPILER_HTML_EXPORT_ARGS"])
        assert payload["model_path"] == "/models/my model.onnx"
        assert payload["enhanced_scheme"] == {"DXQ-P0": {"a": 1}}

    def test_runs_the_venv_python_and_imports_the_named_function(self, venv):
        calls, _ = venv
        HE._call_via_venv("export_summary_html", out="x")
        (cmd, kwargs) = calls[0]
        assert cmd[0] == "/fake/venv/bin/python" and cmd[1] == "-c"
        assert "from dx_com.html_export import export_summary_html as _fn" in cmd[2]
        assert kwargs["timeout"] == 180, "a hung export must not wedge the server"
        assert kwargs["capture_output"] is True

    def test_child_filters_kwargs_by_signature_too(self, venv):
        """The in-process path filters via _filter_kwargs; the child must do the
        same or dx_com version drift becomes a TypeError inside the subprocess."""
        calls, _ = venv
        HE._call_via_venv("generate_summary_html", model_path="m")
        runner = calls[0][0][2]
        assert "inspect.signature(_fn)" in runner
        assert "VAR_KEYWORD" in runner


class TestResultDecoding:
    def test_html_functions_return_raw_stdout(self, venv):
        calls, install = venv
        install(_Proc(stdout="<html>summary</html>"))
        assert HE._call_via_venv("generate_summary_html") == "<html>summary</html>"

    def test_load_shared_js_assets_is_json_decoded(self, venv):
        """This one returns a dict, not HTML — decoding it as text would hand the
        caller a string where it expects assets."""
        calls, install = venv
        install(_Proc(stdout=json.dumps({"chart.js": "console.log(1)"})))
        assert HE._call_via_venv("load_shared_js_assets") == {"chart.js": "console.log(1)"}


class TestFailureReporting:
    def test_nonzero_exit_reports_code_and_stderr(self, venv):
        calls, install = venv
        install(_Proc(stderr="Traceback: boom", returncode=3))
        with pytest.raises(RuntimeError) as err:
            HE._call_via_venv("generate_summary_html")
        assert "exit 3" in str(err.value) and "Traceback: boom" in str(err.value)

    def test_falls_back_to_stdout_when_stderr_is_empty(self, venv):
        calls, install = venv
        install(_Proc(stdout="failure printed to stdout", returncode=1))
        with pytest.raises(RuntimeError, match="failure printed to stdout"):
            HE._call_via_venv("generate_summary_html")

    def test_silent_failure_still_raises(self, venv):
        calls, install = venv
        install(_Proc(returncode=9))
        with pytest.raises(RuntimeError, match="exit 9"):
            HE._call_via_venv("generate_summary_html")


class TestPublicApiFallback:
    """The public wrappers must route to the venv when dx_com is not importable
    in-process — that is the normal launcher configuration, not an edge case."""

    @pytest.mark.parametrize("name", [
        "generate_summary_html", "export_summary_html", "load_shared_js_assets",
    ])
    def test_module_not_found_routes_to_venv(self, name, monkeypatch):
        # This exercises the REAL `except ModuleNotFoundError` branch, which only
        # fires when dx_com is absent in-process. On a host that has dx_com
        # installed the wrapper legitimately calls it directly, so skip rather
        # than assert the opposite.
        if importlib.util.find_spec("dx_com") is not None:
            pytest.skip("dx_com is importable here — the in-process path is taken")

        seen = []
        monkeypatch.setattr(
            HE, "_call_via_venv",
            lambda fn_name, **kw: (seen.append((fn_name, kw)), "routed")[1],
        )
        kwargs = {} if name == "load_shared_js_assets" else {"model_path": "m"}
        assert getattr(HE, name)(**kwargs) == "routed"
        assert seen and seen[0][0] == name
