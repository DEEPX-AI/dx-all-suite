"""경로 기반 프록시 매핑 — 런처 프록시 접두사 → 모듈 서버 ID 변환."""
from __future__ import annotations

# 런처 프록시 접두사 → 모듈 서버 ID 매핑
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
    """런처 프록시 경로를 (target_server_id, stripped_path)로 변환."""
    for prefix, server_id in _PROXY_PREFIX_MAP.items():
        if path == prefix:
            return server_id, "/"
        boundary = prefix + "/"
        if path.startswith(boundary):
            stripped = path[len(prefix):] or "/"
            return server_id, stripped
    return None
