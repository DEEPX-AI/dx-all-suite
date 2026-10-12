"""Path-based proxy mapping: launcher proxy prefix → module server id."""
from __future__ import annotations

# Launcher proxy prefix → module server id
_PROXY_PREFIX_MAP: dict[str, str] = {
    "/app": "dx_app",
    "/stream": "dx_stream",
    "/zoo": "dx_modelzoo",
    "/compiler": "dx_compiler",
    "/planner": "dx_planner",
    "/benchmark": "dx_benchmark",
    "/dx_monitor": "dx_monitor",
    "/agent": "dx_agent_dev",
    "/chat": "shared_chat",
}


def map_launcher_proxy(path: str) -> tuple[str, str] | None:
    """Turn a launcher proxy path into (target_server_id, stripped_path)."""
    for prefix, server_id in _PROXY_PREFIX_MAP.items():
        if path == prefix:
            return server_id, "/"
        boundary = prefix + "/"
        if path.startswith(boundary):
            stripped = path[len(prefix):] or "/"
            return server_id, stripped
    return None
