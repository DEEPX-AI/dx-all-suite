#!/usr/bin/env python3
"""DX EdgeGuide 웹 서버 — 포트 8096.

DX EdgeGuide — Edge AI 제품 추천 가이드.
DXBaseHandler 기반.
"""

from pathlib import Path

from shared.dx_server import DXBaseHandler, DXServer
from shared.chat import ChatEngine
from dx_planner.core.aggregator import aggregate_benchmarks as _aggregate

DEFAULT_PORT = 8096
STATIC_DIR = Path(__file__).resolve().parent / "static"
TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
SERVER_NAME = "DX EdgeGuide"

_chat_engine = ChatEngine(
    app_name="dx_planner",
    fallback_rules=[
        (["tco", "비용", "cost"], {
            "ko": "TCO 계산기를 사용하여 엣지 AI와 클라우드 비용을 비교할 수 있습니다.",
            "en": "Use the TCO calculator to compare edge AI and cloud costs.",
        }),
        (["planner", "플래너"], {
            "ko": "DX EdgeGuide는 워크로드에 맞는 최적의 DEEPX Edge AI 제품을 추천합니다.",
            "en": "DX EdgeGuide recommends the optimal DEEPX Edge AI product for your workload.",
        }),
        (["deepx", "m1", "h1", "npu"], {
            "ko": "DEEPX DX-M1은 25 TOPS, 3W TDP의 팬리스 M.2 NPU입니다.",
            "en": "DEEPX DX-M1 is a fanless M.2 NPU with 25 TOPS and 3W TDP.",
        }),
    ]
)


class DXPlannerHandler(DXBaseHandler):
    """DX EdgeGuide HTTP 요청 핸들러."""

    server_name = SERVER_NAME
    static_dir = STATIC_DIR
    templates_dir = TEMPLATES_DIR
    log_silent = True

    def route(self):
        if self.handle_chat_routes(_chat_engine):
            return

        if self.route_common():
            return

        path = self.url_path

        if self.command == "GET":
            if path == "/api/hb":
                return self.send_json({"ok": True})

        self.route_legacy()


def _run_aggregation():
    """벤치마크 결과를 집계하여 static/data/benchmarks.json 생성."""
    base_dir = Path(__file__).resolve().parent.parent
    results_dir = base_dir / "dx_benchmark" / "results"
    npu_catalog_path = Path(__file__).resolve().parent / "data" / "npu.json"
    out_path = Path(__file__).resolve().parent / "static" / "data" / "benchmarks.json"

    result = _aggregate(
        results_dir=results_dir,
        npu_catalog_path=npu_catalog_path,
        out_path=out_path,
    )
    count = result["meta"]
    print(
        f"[aggregate_benchmarks] {out_path} 생성 완료"
        f" ({out_path.stat().st_size // 1024}KB,"
        f" {count['platform_count']} 플랫폼,"
        f" {count['model_count']} 모델)"
    )


def create_server(port=DEFAULT_PORT):
    """테스트용 서버 팩토리: HTTPServer 인스턴스를 반환."""
    from http.server import ThreadingHTTPServer
    srv = ThreadingHTTPServer(("127.0.0.1", port), DXPlannerHandler)
    srv.daemon_threads = True
    return srv


if __name__ == "__main__":
    try:
        _run_aggregation()
    except Exception as _agg_exc:
        print(f"[aggregate_benchmarks] 경고: 집계 실패 — {_agg_exc}")
    DXServer(DXPlannerHandler, SERVER_NAME, default_port=DEFAULT_PORT).start()
