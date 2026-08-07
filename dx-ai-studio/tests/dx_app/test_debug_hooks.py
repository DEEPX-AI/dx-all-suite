import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_server_action_endpoints_log_action():
    src = (ROOT / "dx_app" / "server.py").read_text(encoding="utf-8")
    assert "from shared import debug_log" in src or "import shared.debug_log" in src
    for action in ('"run"', '"run_async"', '"run_multi"', '"composer_run"', '"composer_run_async"', '"setup_run"'):
        assert 'debug_log.log_action("dx_app", ' + action in src, action


def test_run_inference_logs_exec():
    src = (ROOT / "dx_app" / "core" / "inference.py").read_text(encoding="utf-8")
    assert "from shared import debug_log" in src or "import shared.debug_log" in src
    assert 'debug_log.log_exec("dx_app"' in src
