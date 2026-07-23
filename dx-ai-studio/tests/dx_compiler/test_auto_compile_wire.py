import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2] / "dx_compiler"
JS = (ROOT / "static" / "js" / "auto_compile.js").read_text()
SRV = (ROOT / "server.py").read_text()


def test_posts_to_agent_run_with_target_and_mode():
    assert "/agent/api/agent/run" in JS
    assert "dx-compiler" in JS
    assert '"autopilot"' in JS and '"interactive"' in JS


def test_binds_both_buttons():
    assert "auto-compile-noninteractive" in JS and "auto-compile-interactive" in JS


def test_loads_dxnn_on_done():
    assert "session_dir" in JS or "session-dxnn" in JS
    assert "session-dxnn" in SRV  # safe endpoint added


def test_session_dxnn_endpoint_guarded():
    assert "dx-agent-dev" in SRV  # path guard scopes to the session root
