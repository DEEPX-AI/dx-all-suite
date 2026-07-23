from shared.auth_policy import map_launcher_proxy


def test_launcher_proxy_prefixes_map_to_module_ids():
    assert map_launcher_proxy("/app/api/health") == ("dx_app", "/api/health")
    assert map_launcher_proxy("/app") == ("dx_app", "/")
    assert map_launcher_proxy("/stream/") == ("dx_stream", "/")
    assert map_launcher_proxy("/zoo/static/app.js") == ("dx_modelzoo", "/static/app.js")
    assert map_launcher_proxy("/compiler/api/health") == ("dx_compiler", "/api/health")
    assert map_launcher_proxy("/planner/api/status") == ("dx_planner", "/api/status")
    assert map_launcher_proxy("/benchmark/api/health") == ("dx_benchmark", "/api/health")
    assert map_launcher_proxy("/chat/api/messages") == ("shared_chat", "/api/messages")
    assert map_launcher_proxy("/dx_monitor/api/system_info") == ("dx_monitor", "/api/system_info")


def test_non_proxy_paths_do_not_map():
    assert map_launcher_proxy("/") is None
    assert map_launcher_proxy("/static/launcher.js") is None
    assert map_launcher_proxy("/application/api/health") is None
