#!/usr/bin/env python3
"""DX AI Studio 성능 측정/전수조사 도구.

기본 모드는 파일 읽기만 수행한다. 실행 중인 서버를 건드리는 측정은 명시한
모드에서만 수행하며, launcher boot benchmark처럼 프로세스를 시작/종료할 수
있는 작업은 보고서에 "비추천/미실행"으로만 기록한다.
"""

from __future__ import annotations

import argparse
import gzip
import http.client
import json
import os
import re
import socket
import statistics
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen


SCHEMA_VERSION = "1.0.0"

APP_DIRS = {
    "launcher": "launcher",
    "dx_app": "dx_app",
    "dx_stream": "dx_stream",
    "dx_modelzoo": "dx_modelzoo",
    "dx_compiler": "dx_compiler",
    "dx_planner": "dx_planner",
    "dx_benchmark": "dx_benchmark",
    "dx_monitor": "dx_monitor",
}

PORT_VAR_TO_APP = {
    "LAUNCHER_PORT": "launcher",
    "APP_PORT": "app",
    "STREAM_PORT": "stream",
    "ZOO_PORT": "zoo",
    "COMPILER_PORT": "compiler",
    "PLANNER_PORT": "planner",
    "BENCHMARK_PORT": "benchmark",
    "MONITOR_PORT": "monitor",
}

PROBE_TARGETS = [
    {"name": "launcher.health", "port": 8890, "path": "/api/health", "once": False},
    {"name": "launcher.chat_config", "port": 8890, "path": "/api/chat/config", "once": False},
    {"name": "app.heartbeat", "port": 8080, "path": "/api/hb", "once": False},
    {"name": "app.models", "port": 8080, "path": "/api/models", "once": True},
    {"name": "app.categories", "port": 8080, "path": "/api/categories", "once": False},
    {"name": "app.outputs", "port": 8080, "path": "/api/outputs", "once": False},
    {"name": "app.compiler_status", "port": 8080, "path": "/api/compiler/status", "once": False},
    {"name": "app.setup_status", "port": 8080, "path": "/api/setup/status", "once": True},
    {"name": "stream.status", "port": 8093, "path": "/api/status", "once": False},
    {"name": "stream.demos", "port": 8093, "path": "/api/demos", "once": True},
    {"name": "stream.elements", "port": 8093, "path": "/api/elements", "once": False},
    {"name": "stream.pipeline_list", "port": 8093, "path": "/api/pipeline/list", "once": False},
    {"name": "zoo.health", "port": 8094, "path": "/api/health", "once": False},
    {"name": "zoo.categories", "port": 8094, "path": "/api/categories", "once": False},
    {"name": "zoo.catalog", "port": 8094, "path": "/api/catalog", "once": False},
    {"name": "compiler.feature_check", "port": 8095, "path": "/feature-check", "once": False},
    {"name": "compiler.setup_status", "port": 8095, "path": "/setup/status", "once": True},
    {"name": "benchmark.health", "port": 8097, "path": "/api/health", "once": False},
    {"name": "benchmark.dataset", "port": 8097, "path": "/api/dataset", "once": True},
    {"name": "benchmark.results", "port": 8097, "path": "/api/results", "once": False},
    {"name": "planner.heartbeat", "port": 8096, "path": "/api/hb", "once": False},
    {"name": "monitor.heartbeat", "port": 8098, "path": "/api/hb", "once": False},
    {"name": "monitor.hw_status", "port": 8098, "path": "/api/hw_status", "once": False},
    {"name": "monitor.system_info", "port": 8098, "path": "/api/system_info", "once": True},
    {"name": "monitor.events", "port": 8098, "path": "/api/events?since=0", "once": False},
]

SSE_PROBES = [
    {"name": "monitor.hw_stream", "port": 8098, "path": "/api/hw_stream", "expected_interval_s": 1.5},
]

AVOIDLIST = [
    {"method": "GET", "path": "/api/setup/diagnostics", "reason": "diagnostics subprocess fan-out"},
    {"method": "POST", "path": "/api/run", "reason": "starts inference"},
    {"method": "POST", "path": "/api/run_live", "reason": "starts camera/live process"},
    {"method": "POST", "path": "/api/run_multi", "reason": "starts batch inference"},
    {"method": "POST", "path": "/api/compiler/compile", "reason": "long dxcom compile"},
    {"method": "POST", "path": "/api/modelzoo/download", "reason": "network/model download"},
    {"method": "POST", "path": "/api/setup/run", "reason": "mutates system setup"},
    {"method": "POST", "path": "/api/dev/git_commit", "reason": "mutates git state"},
    {"method": "GET", "path": "/api/live_frame", "reason": "streaming worker"},
    {"method": "GET", "path": "/api/stream/mjpeg", "reason": "streaming worker"},
    {"method": "POST", "path": "/api/chat/config/test", "reason": "external LLM call"},
    {"method": "POST", "path": "/setup/install-sdk", "reason": "pip/system install"},
    {"method": "GET", "path": "/api/diagnostics", "reason": "deep diagnostics"},
]


def relpath(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


EXCLUDED_RELEASE_PREFIXES: tuple[str, ...] = ()


def is_release_path(root: Path, path: Path) -> bool:
    """릴리스 제외 대상 경로(EXCLUDED_RELEASE_PREFIXES)를 필터링한다."""
    rel = relpath(path, root)
    return not any(
        rel == prefix.rstrip("/") or rel.startswith(prefix)
        for prefix in EXCLUDED_RELEASE_PREFIXES
    )


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * pct)))
    return ordered[index]


class StaticAnalyser:
    def analyse_port_map(self, launcher_py: Path) -> dict[str, int]:
        if not launcher_py.exists():
            return {}
        source = launcher_py.read_text(encoding="utf-8", errors="replace")
        ports: dict[str, int] = {}
        for name, via_port, direct in re.findall(
            r"^([A-Z_]+_PORT)\s*=\s*(?:_port\([^,]+,\s*(\d+)\)|(\d+))\s*$",
            source,
            re.M,
        ):
            app = PORT_VAR_TO_APP.get(name)
            if app:
                ports[app] = int(via_port or direct)
        return ports

    def analyse_static_assets(self, root: Path, max_gzip_bytes: int = 10_000_000) -> list[dict]:
        candidates: list[Path] = []
        for app_dir in APP_DIRS.values():
            base = root / app_dir
            for sub in ("static", "data"):
                directory = base / sub
                if directory.exists():
                    candidates.extend(p for p in directory.rglob("*") if p.is_file())
            dataset = base / "dataset.json"
            if dataset.exists():
                candidates.append(dataset)

        shared = root / "shared" / "static"
        if shared.exists():
            candidates.extend(p for p in shared.rglob("*") if p.is_file())

        seen: set[Path] = set()
        records: list[dict] = []
        for path in sorted(candidates):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                size = path.stat().st_size
            except OSError:
                continue
            gzip_bytes = None
            if size <= max_gzip_bytes and path.suffix.lower() in {
                ".js", ".css", ".json", ".html", ".svg", ".txt", ".md"
            }:
                try:
                    gzip_bytes = len(gzip.compress(path.read_bytes()))
                except OSError:
                    gzip_bytes = None
            records.append({
                "path": relpath(path, root),
                "app": self._app_for_path(root, path),
                "kind": self._asset_kind(path),
                "size_bytes": size,
                "gzip_bytes": gzip_bytes,
                "gzip_ratio": round(gzip_bytes / size, 4) if gzip_bytes is not None and size else None,
            })
        return records

    def analyse_templates(self, root: Path) -> list[dict]:
        templates = [p for p in root.glob("*/templates/*.html") if is_release_path(root, p)]
        launcher_index = root / "launcher" / "static" / "index.html"
        if launcher_index.exists():
            templates.append(launcher_index)

        records = []
        for path in sorted(templates):
            source = path.read_text(encoding="utf-8", errors="replace")
            scripts = re.findall(r"<script\b([^>]*)>", source, re.I)
            script_srcs = [
                re.search(r'\bsrc=["\']([^"\']+)["\']', attrs, re.I).group(1)
                for attrs in scripts
                if re.search(r'\bsrc=["\']([^"\']+)["\']', attrs, re.I)
            ]
            blocking = [
                attrs for attrs in scripts
                if "src=" in attrs.lower()
                and " defer" not in f" {attrs.lower()}"
                and " async" not in f" {attrs.lower()}"
            ]
            inline_bytes = sum(
                len(match.encode("utf-8"))
                for match in re.findall(r"<script\b(?![^>]*\bsrc=)[^>]*>(.*?)</script>", source, re.I | re.S)
            )
            links = re.findall(r"<link\b([^>]*)>", source, re.I)
            css_links = [
                attrs for attrs in links
                if "stylesheet" in attrs.lower()
            ]
            versioned = sum(1 for src in script_srcs if "?v=" in src)
            img_tags = re.findall(r"<img\b([^>]*)>", source, re.I)
            lazy_imgs = sum(1 for attrs in img_tags if "loading=" in attrs.lower())
            records.append({
                "path": relpath(path, root),
                "app": self._app_for_path(root, path),
                "script_count": len(script_srcs),
                "blocking_scripts": len(blocking),
                "css_link_count": len(css_links),
                "inline_script_bytes": inline_bytes,
                "cache_bust_ratio": round(versioned / len(script_srcs), 4) if script_srcs else None,
                "relative_script_count": sum(1 for src in script_srcs if src.startswith("static/")),
                "image_count": len(img_tags),
                "lazy_image_count": lazy_imgs,
            })
        return records

    def analyse_frontend_inventory(self, root: Path) -> dict:
        js_files = [p for p in root.glob("*/static/**/*.js") if is_release_path(root, p)] + list((root / "shared" / "static").glob("**/*.js"))
        html_files = [p for p in root.glob("*/templates/*.html") if is_release_path(root, p)]
        launcher_index = root / "launcher" / "static" / "index.html"
        if launcher_index.exists():
            html_files.append(launcher_index)

        polling = []
        fetch_calls = []
        event_sources = []
        timeouts = []
        for path in sorted([p for p in js_files + html_files if p.exists()]):
            source = path.read_text(encoding="utf-8", errors="replace")
            for match in re.finditer(r"setInterval\s*\((?P<body>.{0,140}?),(?P<ms>\s*\d+)\s*\)", source, re.S):
                polling.append({
                    "path": relpath(path, root),
                    "app": self._app_for_path(root, path),
                    "interval_ms": int(match.group("ms")),
                    "snippet": " ".join(match.group(0).split())[:180],
                })
            for match in re.finditer(r"setTimeout\s*\((?P<body>.{0,140}?),(?P<ms>\s*\d+)\s*\)", source, re.S):
                timeouts.append({
                    "path": relpath(path, root),
                    "app": self._app_for_path(root, path),
                    "delay_ms": int(match.group("ms")),
                    "snippet": " ".join(match.group(0).split())[:180],
                })
            for match in re.finditer(r"\bfetch\s*\(\s*([^,\)]+)", source):
                fetch_calls.append({
                    "path": relpath(path, root),
                    "app": self._app_for_path(root, path),
                    "target": match.group(1).strip()[:160],
                })
            for match in re.finditer(r"new\s+EventSource\s*\(\s*([^\)]+)", source):
                event_sources.append({
                    "path": relpath(path, root),
                    "app": self._app_for_path(root, path),
                    "target": match.group(1).strip()[:160],
                })
        return {
            "polling": polling,
            "timeouts": timeouts,
            "fetch_calls": fetch_calls,
            "event_sources": event_sources,
        }

    def analyse_routes(self, root: Path) -> dict[str, list[str]]:
        routes: dict[str, list[str]] = {}
        candidates = [s for s in root.glob("*/server.py") if is_release_path(root, s)]
        candidates.append(root / "launcher" / "launcher.py")
        for server in sorted(candidates):
            if not server.exists():
                continue
            source = server.read_text(encoding="utf-8", errors="replace")
            found = sorted(set(re.findall(r'["\'](/(?:api|setup|progress|feature-check)[^"\'\s{}]*)', source)))
            routes[relpath(server, root)] = found
        return routes

    def analyse_sse_sources(self, root: Path) -> list[dict]:
        records = []
        for path in sorted(root.glob("**/*.py")):
            if any(part in {".venv", "__pycache__", "dc_dx_studio"} for part in path.parts):
                continue
            if not is_release_path(root, path):
                continue
            source = path.read_text(encoding="utf-8", errors="replace")
            if "start_sse" not in source and "send_sse" not in source and "EventSource" not in source:
                continue
            routes = sorted(set(re.findall(r'["\'](/[^"\'\s{}]*(?:stream|progress|status|chat)[^"\'\s{}]*)', source)))
            records.append({
                "path": relpath(path, root),
                "route_hints": routes,
                "uses_start_sse": "start_sse" in source,
                "uses_send_sse": "send_sse" in source,
            })
        return records

    def analyse_cache_policy(self, root: Path) -> dict:
        launcher = root / "launcher" / "launcher.py"
        shared = root / "shared" / "dx_server.py"
        policy = {
            "health_cache_ttl_sec": None,
            "sse_proxy_timeout_sec": None,
            "proxy_timeout_sec": None,
            "dxbase_http_protocol": None,
        }
        if launcher.exists():
            source = launcher.read_text(encoding="utf-8", errors="replace")
            ttl = re.search(r"_HEALTH_CACHE_TTL_SEC\s*=\s*([\d.]+)", source)
            timeout = re.search(r"conn\.sock\.settimeout\((\d+)\)", source)
            proxy_timeout = re.search(r"HTTPConnection\([^,\n]+,\s*[^,\n]+,\s*timeout=(\d+)\)", source)
            policy["health_cache_ttl_sec"] = float(ttl.group(1)) if ttl else None
            policy["sse_proxy_timeout_sec"] = int(timeout.group(1)) if timeout else None
            policy["proxy_timeout_sec"] = int(proxy_timeout.group(1)) if proxy_timeout else None
        if shared.exists():
            source = shared.read_text(encoding="utf-8", errors="replace")
            protocol = re.search(r"protocol_version\s*=\s*[\"']([^\"']+)", source)
            policy["dxbase_http_protocol"] = protocol.group(1) if protocol else None
        return policy

    def analyse_modelzoo_optimized_images(self, root: Path) -> dict:
        """ModelZoo 원본/최적화 이미지 커버리지를 분석한다."""
        data = root / "dx_modelzoo" / "data"
        image_exts = {".jpg", ".jpeg", ".png", ".webp"}

        def _count_images(*dirs: Path) -> int:
            total = 0
            for d in dirs:
                if d.is_dir():
                    total += sum(
                        1 for p in d.rglob("*")
                        if p.is_file() and p.suffix.lower() in image_exts
                    )
            return total

        originals = _count_images(data / "thumbnails", data / "examples")
        optimized = _count_images(
            data / "optimized" / "thumbnails",
            data / "optimized" / "examples",
        )
        # 옵티마이저는 원본당 2개(WebP + JPG)를 생성하므로 coverage = optimized / (originals * 2)
        if originals == 0:
            ratio = 0.0
        else:
            ratio = min(optimized / (originals * 2), 1.0)

        result: dict = {
            "original_images": originals,
            "optimized_images": optimized,
            "coverage_ratio": round(ratio, 4),
        }
        manifest = data / "optimized" / "manifest.json"
        result["manifest_present"] = manifest.is_file()
        return result

    def _asset_kind(self, path: Path) -> str:
        suffix = path.suffix.lower()
        if suffix in {".js"}:
            return "js"
        if suffix in {".css"}:
            return "css"
        if suffix in {".json"}:
            return "json"
        if suffix in {".ttf", ".otf", ".woff", ".woff2"}:
            return "font"
        if suffix in {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico"}:
            return "image"
        if suffix in {".html"}:
            return "html"
        return suffix.lstrip(".") or "other"

    def _app_for_path(self, root: Path, path: Path) -> str:
        rel = relpath(path, root)
        first = rel.split("/", 1)[0]
        return first if first in APP_DIRS else "shared"


class RulesEngine:
    def build_findings(self, report: dict) -> list[dict]:
        findings: list[dict] = []
        for asset in report.get("static_assets", []):
            if asset["size_bytes"] > 1_000_000:
                findings.append({
                    "severity": "warning",
                    "category": "asset_size",
                    "path": asset["path"],
                    "message": f"large asset {asset['size_bytes']} bytes",
                    "collision_risk": "low",
                })
            elif asset["size_bytes"] > 100_000 and asset["kind"] in {"js", "json", "font", "image"}:
                findings.append({
                    "severity": "info",
                    "category": "asset_size",
                    "path": asset["path"],
                    "message": f"notable {asset['kind']} asset {asset['size_bytes']} bytes",
                    "collision_risk": "low",
                })

        for template in report.get("templates", []):
            if template["blocking_scripts"] >= 10:
                findings.append({
                    "severity": "warning",
                    "category": "blocking_scripts",
                    "path": template["path"],
                    "message": f"{template['blocking_scripts']} blocking script tags",
                    "collision_risk": "medium",
                })
            if template["inline_script_bytes"] > 50_000:
                findings.append({
                    "severity": "warning",
                    "category": "inline_script",
                    "path": template["path"],
                    "message": f"{template['inline_script_bytes']} inline script bytes",
                    "collision_risk": "medium",
                })

        for poll in report.get("frontend_inventory", {}).get("polling", []):
            if poll["interval_ms"] < 2000:
                findings.append({
                    "severity": "warning",
                    "category": "polling_interval",
                    "path": poll["path"],
                    "message": f"fast polling interval {poll['interval_ms']} ms",
                    "collision_risk": "medium",
                })

        zoo_cov = report.get("modelzoo_optimized_images", {})
        if zoo_cov.get("original_images", 0) > 0 and zoo_cov.get("optimized_images", 0) == 0:
            findings.append({
                "severity": "warning",
                "category": "modelzoo_optimized_images",
                "path": "dx_modelzoo/data/optimized",
                "message": f"{zoo_cov['original_images']} original images but no optimized versions found",
                "collision_risk": "low",
            })

        if not findings:
            findings.append({
                "severity": "info",
                "category": "baseline",
                "path": "",
                "message": "no static performance findings triggered",
                "collision_risk": "low",
            })
        return findings


class ProbeCollector:
    def probe_endpoint(self, url: str, reps: int = 3, timeout: float = 3.0) -> dict:
        latencies: list[float] = []
        status = None
        body_bytes = 0
        last_error = None
        for _ in range(max(1, reps)):
            started = time.perf_counter()
            try:
                with urlopen(url, timeout=timeout) as resp:
                    body = resp.read()
                    status = resp.status
                    body_bytes = len(body)
                latencies.append((time.perf_counter() - started) * 1000)
            except Exception as exc:
                last_error = str(exc)
                break
        if not latencies:
            return {"url": url, "status": status, "error": last_error, "latency_ms": {"reps": 0}}
        return {
            "url": url,
            "status": status,
            "body_bytes": body_bytes,
            "latency_ms": {
                "reps": len(latencies),
                "min": round(min(latencies), 3),
                "p50": round(statistics.median(latencies), 3),
                "p95": round(percentile(latencies, 0.95), 3),
                "max": round(max(latencies), 3),
            },
        }

    def probe_sse_first_event(self, url: str, timeout: float = 5.0) -> dict:
        started = time.perf_counter()
        req = Request(url, headers={"Accept": "text/event-stream"})
        try:
            with urlopen(req, timeout=timeout) as resp:
                first_event = ""
                for _ in range(200):
                    line = resp.readline()
                    if not line:
                        break
                    decoded = line.decode("utf-8", "replace").strip()
                    if decoded.startswith("data:") or decoded.startswith("event:"):
                        first_event = decoded
                        break
                elapsed = (time.perf_counter() - started) * 1000
                return {
                    "url": url,
                    "status": resp.status,
                    "content_type": resp.headers.get("Content-Type"),
                    "first_event": first_event,
                    "first_event_latency_ms": round(elapsed, 3),
                }
        except Exception as exc:
            return {
                "url": url,
                "status": None,
                "error": str(exc),
                "first_event_latency_ms": None,
            }


def run_static(root: Path | str, max_gzip_bytes: int = 10_000_000) -> dict:
    root = Path(root)
    analyser = StaticAnalyser()
    report = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root": str(root),
        "coverage": {
            "static_assets": {"status": "measured", "collision_risk": "low"},
            "frontend_inventory": {"status": "measured", "collision_risk": "low"},
            "endpoint_latency": {"status": "available_when_running", "collision_risk": "low_medium"},
            "sse_first_event": {"status": "available_when_running", "collision_risk": "medium"},
            "process_state": {"status": "available_when_running", "collision_risk": "low"},
            "launcher_boot_benchmark": {"status": "unsafe_by_default", "collision_risk": "high"},
            "asgi_comparison": {"status": "requires_prototype", "collision_risk": "low"},
        },
        "port_map": analyser.analyse_port_map(root / "launcher" / "launcher.py"),
        "static_assets": analyser.analyse_static_assets(root, max_gzip_bytes=max_gzip_bytes),
        "templates": analyser.analyse_templates(root),
        "frontend_inventory": analyser.analyse_frontend_inventory(root),
        "route_inventory": analyser.analyse_routes(root),
        "sse_sources": analyser.analyse_sse_sources(root),
        "cache_policy": analyser.analyse_cache_policy(root),
        "modelzoo_optimized_images": analyser.analyse_modelzoo_optimized_images(root),
        "probe_policy": {
            "allowlist": PROBE_TARGETS,
            "sse": SSE_PROBES,
            "avoidlist": AVOIDLIST,
        },
        "boot_benchmark": {
            "status": "skipped",
            "reason": "disabled by design because launcher startup can kill processes occupying DX ports",
        },
        "asgi_comparison": {
            "status": "not_run",
            "reason": "requires isolated experiments/fastapi_spike prototype and offline dependency wheelhouse",
        },
    }
    report["findings"] = RulesEngine().build_findings(report)
    return report


def run_attach(root: Path | str) -> dict:
    root = Path(root)
    pidfile = root / "launcher" / ".launcher_pids"
    pids: dict[str, int] = {}
    if pidfile.exists():
        try:
            raw = json.loads(pidfile.read_text(encoding="utf-8"))
            pids.update({str(name): int(pid) for name, pid in raw.items()})
        except Exception as exc:
            return {"error": f"failed to read pidfile: {exc}"}

    listeners = _read_listeners()
    for item in listeners:
        if item.get("port") == 8890 and item.get("pid"):
            pids.setdefault("launcher", int(item["pid"]))

    processes = {}
    for name, pid in sorted(pids.items()):
        processes[name] = _read_proc(pid)
    return {
        "pidfile": relpath(pidfile, root),
        "processes": processes,
        "listeners": listeners,
    }


def run_health(root: Path | str, reps: int = 3, timeout: float = 3.0) -> list[dict]:
    _ = Path(root)
    collector = ProbeCollector()
    records = []
    for target in PROBE_TARGETS:
        actual_reps = 1 if target.get("once") else reps
        url = f"http://127.0.0.1:{target['port']}{target['path']}"
        record = collector.probe_endpoint(url, reps=actual_reps, timeout=timeout)
        record["name"] = target["name"]
        record["path"] = target["path"]
        record["port"] = target["port"]
        records.append(record)
    return records


def run_sse(root: Path | str, timeout: float = 5.0) -> list[dict]:
    _ = Path(root)
    collector = ProbeCollector()
    records = []
    for target in SSE_PROBES:
        url = f"http://127.0.0.1:{target['port']}{target['path']}"
        record = collector.probe_sse_first_event(url, timeout=timeout)
        record["name"] = target["name"]
        record["path"] = target["path"]
        record["port"] = target["port"]
        record["expected_interval_s"] = target["expected_interval_s"]
        records.append(record)
    return records


def run_report(
    root: Path | str,
    mode: str = "static",
    include_sse: bool = False,
    reps: int = 3,
    timeout: float = 3.0,
) -> dict:
    report = run_static(root)
    if mode in {"attach", "full"}:
        report["process_state"] = run_attach(root)
    if mode in {"health", "full"}:
        report["endpoint_latency"] = run_health(root, reps=reps, timeout=timeout)
    if include_sse or mode == "sse":
        report["sse_first_event"] = run_sse(root, timeout=max(timeout, 5.0))
    return report


def render_markdown(report: dict) -> str:
    assets = report.get("static_assets", [])
    templates = report.get("templates", [])
    findings = report.get("findings", [])
    lines = [
        "# DX AI Studio Performance Audit",
        "",
        f"- schema: `{report.get('schema_version')}`",
        f"- root: `{report.get('root')}`",
        "",
        "## Coverage",
    ]
    for name, data in report.get("coverage", {}).items():
        lines.append(f"- **{name}**: {data.get('status')} / risk={data.get('collision_risk')}")

    total_asset_bytes = sum(item["size_bytes"] for item in assets)
    large_assets = sorted(assets, key=lambda item: item["size_bytes"], reverse=True)[:10]
    lines.extend([
        "",
        "## Static Assets",
        f"- files: {len(assets)}",
        f"- total bytes: {total_asset_bytes}",
    ])
    for item in large_assets:
        gzip_text = item["gzip_bytes"] if item["gzip_bytes"] is not None else "n/a"
        lines.append(f"- `{item['path']}`: {item['size_bytes']} bytes, gzip={gzip_text}")

    lines.extend(["", "## Templates"])
    for item in sorted(templates, key=lambda row: row["blocking_scripts"], reverse=True)[:10]:
        lines.append(
            f"- `{item['path']}`: scripts={item['script_count']}, "
            f"blocking={item['blocking_scripts']}, inline={item['inline_script_bytes']} bytes"
        )

    frontend = report.get("frontend_inventory", {})
    lines.extend([
        "",
        "## Frontend Inventory",
        f"- polling timers: {len(frontend.get('polling', []))}",
        f"- fetch calls: {len(frontend.get('fetch_calls', []))}",
        f"- EventSource calls: {len(frontend.get('event_sources', []))}",
    ])

    if "process_state" in report:
        processes = report["process_state"].get("processes", {})
        lines.extend(["", "## Process State"])
        for name, data in processes.items():
            if "error" in data:
                lines.append(f"- {name}: {data['error']}")
            else:
                lines.append(
                    f"- {name}: pid={data.get('pid')}, rss={data.get('rss_mb')}MB, "
                    f"threads={data.get('threads')}, fds={data.get('fds')}"
                )

    if "endpoint_latency" in report:
        lines.extend(["", "## Endpoint Latency"])
        for item in report["endpoint_latency"]:
            latency = item.get("latency_ms", {})
            if item.get("error"):
                lines.append(f"- {item['name']}: ERROR {item['error']}")
            else:
                lines.append(f"- {item['name']}: status={item.get('status')}, p50={latency.get('p50')}ms")

    if "sse_first_event" in report:
        lines.extend(["", "## SSE First Event"])
        for item in report["sse_first_event"]:
            if item.get("error"):
                lines.append(f"- {item['name']}: ERROR {item['error']}")
            else:
                lines.append(f"- {item['name']}: first_event={item.get('first_event_latency_ms')}ms")

    lines.extend(["", "## Findings"])
    for finding in findings[:25]:
        lines.append(
            f"- **{finding['severity']}** `{finding.get('path', '')}` "
            f"{finding['category']}: {finding['message']}"
        )
    return "\n".join(lines) + "\n"


def _read_proc(pid: int) -> dict:
    base = Path("/proc") / str(pid)
    try:
        status = (base / "status").read_text(encoding="utf-8", errors="replace")
        stat = (base / "stat").read_text(encoding="utf-8", errors="replace").split()
        data = {
            "pid": pid,
            "rss_mb": _status_kb(status, "VmRSS") / 1024 if _status_kb(status, "VmRSS") is not None else None,
            "vmpeak_mb": _status_kb(status, "VmPeak") / 1024 if _status_kb(status, "VmPeak") is not None else None,
            "threads": _status_int(status, "Threads"),
            "fds": len(list((base / "fd").iterdir())) if (base / "fd").exists() else None,
        }
        if len(stat) > 15:
            data["utime_ticks"] = int(stat[13])
            data["stime_ticks"] = int(stat[14])
        return data
    except Exception as exc:
        return {"pid": pid, "error": str(exc)}


def _status_kb(status: str, key: str) -> int | None:
    match = re.search(rf"^{re.escape(key)}:\s+(\d+)\s+kB", status, re.M)
    return int(match.group(1)) if match else None


def _status_int(status: str, key: str) -> int | None:
    match = re.search(rf"^{re.escape(key)}:\s+(\d+)", status, re.M)
    return int(match.group(1)) if match else None


def _read_listeners() -> list[dict]:
    try:
        result = subprocess.run(
            ["ss", "-ltnp"],
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3,
        )
    except Exception:
        return []
    listeners = []
    for line in result.stdout.splitlines():
        if not line.startswith("LISTEN"):
            continue
        parts = line.split()
        if len(parts) < 5:
            continue
        local = parts[3]
        match = re.search(r":(\d+)$", local)
        if not match:
            continue
        pid_match = re.search(r"pid=(\d+)", line)
        listeners.append({
            "port": int(match.group(1)),
            "recv_q": int(parts[1]) if parts[1].isdigit() else None,
            "send_q": int(parts[2]) if parts[2].isdigit() else None,
            "pid": int(pid_match.group(1)) if pid_match else None,
        })
    return listeners


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="DX AI Studio performance audit")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--mode", choices=("static", "attach", "health", "sse", "full"), default="static")
    parser.add_argument("--include-sse", action="store_true", help="full/health 모드에서 SSE first-event도 측정")
    parser.add_argument("--reps", type=int, default=3, help="endpoint latency 반복 횟수")
    parser.add_argument("--timeout", type=float, default=3.0, help="HTTP probe timeout seconds")
    parser.add_argument("--json", action="store_true", help="JSON 출력")
    parser.add_argument("--out", type=Path, help="결과 파일 경로")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)
    report = run_report(
        args.root,
        mode=args.mode,
        include_sse=args.include_sse,
        reps=args.reps,
        timeout=args.timeout,
    )
    rendered = json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_markdown(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
