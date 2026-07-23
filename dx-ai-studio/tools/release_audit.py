#!/usr/bin/env python3
"""DX AI Studio — Release Route Smoke Audit.

Navigates each release route and collects:
  - HTTP status, load time
  - Console errors / warnings
  - Page errors
  - Failed network requests (status >= 400)
  - Visible Korean text while locale is forced to English
  - Placeholder tokens: undefined, NaN, null, TODO, FIXME
  - Internal release leak tokens: sandbox, Coming Soon, Metadata pending

Usage:
    python3 tools/release_audit.py [--base-url URL] [--routes r1,r2] [--json FILE]

Exit codes:
    0  No blocker-level findings
    1  Audit execution failure
    2  Blocker-level findings or smoke failures detected
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from urllib import error as urllib_error
from urllib import request as urllib_request
from urllib.parse import urlsplit

RELEASE_ROUTES: list[str] = [
    "/",
    "/app/",
    "/stream/",
    "/zoo/",
    "/compiler/",
    "/planner/",
    "/benchmark/",
    "/dx_monitor/",
    "/sdk-library",
    "/about",
]

# ── Korean Unicode range (Hangul Syllables + Jamo + Compatibility) ─
_KOREAN_RE = re.compile(r"[\uAC00-\uD7AF\u1100-\u11FF\u3130-\u318F]")

# Placeholder tokens that indicate incomplete content.
# Tokens marked with word-boundary regex avoid false positives inside URLs/words.
_PLACEHOLDER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("undefined", re.compile(r"\bundefined\b", re.IGNORECASE)),
    ("null", re.compile(r"\bnull\b", re.IGNORECASE)),
    ("NaN", re.compile(r"\bNaN\b")),
    ("TODO", re.compile(r"\bTODO\b")),
    ("FIXME", re.compile(r"\bFIXME\b")),
]

# Developer/internal tokens that must not leak in release UI.
_DEV_TOKEN_PATTERNS: list[tuple[str, str, re.Pattern[str]]] = [
    ("sandbox", "dev_token_leak", re.compile(r"\bsandbox\b", re.IGNORECASE)),
    ("Coming Soon", "internal_placeholder", re.compile(r"Coming\s+Soon", re.IGNORECASE)),
    ("Metadata pending", "internal_placeholder", re.compile(r"Metadata\s+pending", re.IGNORECASE)),
    ("placeholder", "internal_placeholder", re.compile(r"\bplaceholder\b", re.IGNORECASE)),
]

# Categories that are always blocker severity
BLOCKER_CATEGORIES: set[str] = {"page_error", "status_error"}

LOCAL_API_SMOKE_CHECKS = (
    ("local_api_health", "GET", "/api/health", {200}),
    ("local_api_auth_status", "GET", "/api/auth/status", {200}),
    ("local_api_dx_app_status", "GET", "/api/modules/dx_app/status", {200}),
    ("local_api_chat_config", "GET", "/api/chat/config", {200}),
)

KEYBOARD_SMOKE_ACTIONS = (
    {
        "name": "about_card_enter",
        "selector": ".about-book-card:not(.sdk-card)",
        "key": "Enter",
        "expect_eval": "() => document.getElementById('about-view')?.classList.contains('visible')",
        "wait_for_eval": "() => document.getElementById('about-view')?.classList.contains('visible')",
    },
    {
        "name": "sdk_card_enter",
        "selector": ".about-book-card.sdk-card",
        "key": "Enter",
        "expect_eval": "() => document.getElementById('sdk-library-view')?.classList.contains('visible')",
        "wait_for_eval": "() => document.getElementById('sdk-library-view')?.classList.contains('visible')",
    },
    {
        "name": "landing_poster_enter",
        "selector": "#landingPoster",
        "key": "Enter",
        "expect_eval": "() => document.getElementById('platformInfoOverlay')?.classList.contains('open')",
        "wait_for_eval": "() => document.getElementById('platformInfoOverlay')?.classList.contains('open')",
    },
    {
        "name": "sdk_escape_closes_viewer",
        "selector": "#sdkBookViewer",
        "focus_selector": "body",
        "key": "Escape",
        "setup_eval": """async () => {
            if (window.showSdkLibrary) window.showSdkLibrary();
            if (window.SDKLibrary && typeof window.SDKLibrary.init === 'function') await window.SDKLibrary.init();
            const viewer = document.getElementById('sdkBookViewer');
            if (viewer) viewer.classList.add('open');
        }""",
        "expect_eval": "() => !document.getElementById('sdkBookViewer')?.classList.contains('open')",
        "wait_for_eval": "() => !document.getElementById('sdkBookViewer')?.classList.contains('open')",
    },
)
KEYBOARD_SMOKE_NAMES = {str(action["name"]) for action in KEYBOARD_SMOKE_ACTIONS}


def _severity_for(category: str) -> str:
    """Return 'blocker' if category is in BLOCKER_CATEGORIES, else 'warning'."""
    return "blocker" if category in BLOCKER_CATEGORIES else "warning"


@dataclass
class RouteFinding:
    route: str
    category: str  # e.g. "console_error", "korean_leak", "placeholder", ...
    severity: str  # "blocker" or "warning"
    detail: str


@dataclass
class SmokeCheck:
    name: str
    status: str  # "pass", "fail", or "skipped"
    detail: str = ""


@dataclass
class SmokeResponse:
    status: int | None
    body: dict
    headers: dict[str, str] = field(default_factory=dict)
    raw: str = ""


@dataclass
class RouteResult:
    route: str
    status: int | None = None
    elapsed_ms: float = 0.0
    findings: list[RouteFinding] = field(default_factory=list)
    checks: list[SmokeCheck] = field(default_factory=list)


def _json_request(
    base_url: str,
    method: str,
    path: str,
    body: dict | None = None,
    *,
    headers: dict[str, str] | None = None,
) -> SmokeResponse:
    req_headers = dict(headers or {})
    if body is not None:
        req_headers.setdefault("Content-Type", "application/json")
    data = json.dumps(body or {}).encode("utf-8") if body is not None else None
    req = urllib_request.Request(
        base_url.rstrip("/") + path,
        data=data,
        headers=req_headers,
        method=method,
    )
    try:
        with urllib_request.urlopen(req, timeout=5) as resp:
            raw = resp.read().decode("utf-8", "replace")
            return SmokeResponse(
                resp.status,
                _parse_json_body(raw),
                dict(resp.headers.items()),
                raw,
            )
    except urllib_error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        return SmokeResponse(
            exc.code,
            _parse_json_body(raw),
            dict(exc.headers.items()),
            raw,
        )
    except urllib_error.URLError as exc:
        return SmokeResponse(None, {"error": str(exc.reason)}, {}, str(exc.reason))


def _parse_json_body(raw: str) -> dict:
    try:
        data = json.loads(raw) if raw else {}
    except (json.JSONDecodeError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _expect_status(name: str, resp: SmokeResponse, expected: set[int]) -> SmokeCheck:
    if resp.status in expected:
        return SmokeCheck(name, "pass", f"HTTP {resp.status}")
    return SmokeCheck(name, "fail", f"Expected {sorted(expected)}, got {resp.status}: {resp.raw}")


def _run_local_api_smoke(base_url: str) -> list[SmokeCheck]:
    checks: list[SmokeCheck] = []
    for name, method, path, expected in LOCAL_API_SMOKE_CHECKS:
        resp = _json_request(base_url, method, path)
        check = _expect_status(name, resp, expected)
        if name == "local_api_auth_status" and check.status == "pass":
            if resp.body.get("auth_enabled") is not False or resp.body.get("locked") is not False:
                check = SmokeCheck(name, "fail", f"Unexpected auth status payload: {resp.body}")
        checks.append(check)
    return checks


def _frame_label(frame) -> str:
    try:
        url = frame.url
    except Exception:
        url = ""
    return url or "unknown-frame"


def _format_console_message(msg) -> str:
    location = msg.location
    url = location.get("url", "") if isinstance(location, dict) else ""
    line = location.get("lineNumber", "") if isinstance(location, dict) else ""
    return f"[{msg.type}] frame={url or 'unknown-frame'}:{line} {msg.text}"


def _format_page_error(err, page) -> str:
    return f"frame={getattr(page, 'url', '') or 'unknown-page'} {err}"


def _format_failed_request(req) -> str:
    try:
        frame = _frame_label(req.frame)
    except Exception:
        frame = "unknown-frame"
    return f"frame={frame} {req.method} {req.url} → {req.failure}"


def _is_static_url(url: str) -> bool:
    path = urlsplit(url).path
    return path.startswith("/static/") or bool(re.search(r"\.(?:js|css|png|jpg|jpeg|webp|svg|woff2?)$", path))


def _prepare_keyboard_smoke_page(page) -> None:
    page.evaluate("""() => {
        try { sessionStorage.setItem('dx-splash-seen', '1'); } catch {}
        const splash = document.getElementById('splashOverlay');
        if (splash && typeof window.skipSplash === 'function') window.skipSplash(true);
        if (splash && splash.parentNode) splash.remove();
        if (
            window.DXLauncher &&
            typeof window.DXLauncher._initDeferredLauncherWork === 'function'
        ) {
            window.DXLauncher._initDeferredLauncherWork();
        }
    }""")
    page.wait_for_timeout(100)


def _run_keyboard_smoke(page, route: str) -> list[SmokeCheck]:
    if route != "/":
        return []
    checks: list[SmokeCheck] = []
    try:
        _prepare_keyboard_smoke_page(page)
    except Exception as exc:
        return [SmokeCheck("keyboard_prepare", "fail", str(exc))]
    for action in KEYBOARD_SMOKE_ACTIONS:
        name = str(action["name"])
        try:
            setup_eval = action.get("setup_eval")
            if setup_eval:
                page.evaluate(setup_eval)
            selector = str(action["selector"])
            page.locator(selector).first.wait_for(state="attached", timeout=2_000)
            focus_selector = action.get("focus_selector", selector)
            if focus_selector:
                page.locator(str(focus_selector)).first.focus(timeout=2_000)
            page.keyboard.press(str(action["key"]))
            wait_for_eval = action.get("wait_for_eval")
            if wait_for_eval:
                page.wait_for_function(str(wait_for_eval), timeout=2_000)
            else:
                page.wait_for_timeout(300)
            ok = bool(page.evaluate(str(action["expect_eval"])))
            checks.append(SmokeCheck(name, "pass" if ok else "fail", f"{selector} {action['key']}"))
        except Exception as exc:
            checks.append(SmokeCheck(name, "fail", str(exc)))
        finally:
            try:
                page.evaluate("""() => {
                    if (window.goHome) window.goHome();
                    const platform = document.getElementById('platformInfoOverlay');
                    if (platform) platform.classList.remove('open');
                    const viewer = document.getElementById('sdkBookViewer');
                    if (viewer) viewer.classList.remove('open');
                }""")
            except Exception:
                pass
    return checks


def _finding_counts(results: list[RouteResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for result in results:
        for finding in result.findings:
            counts[finding.category] = counts.get(finding.category, 0) + 1
    return counts


def _smoke_failure_count(checks: list[SmokeCheck]) -> int:
    return sum(1 for check in checks if check.status == "fail")


def _try_playwright_audit(base_url: str, routes: list[str]) -> list[RouteResult]:
    """Run audit with Playwright if available."""
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]
    except ImportError:
        print(
            "[release_audit] playwright not installed – returning empty results",
            file=sys.stderr,
        )
        return [RouteResult(route=r) for r in routes]

    results: list[RouteResult] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        for route in routes:
            result = RouteResult(route=route)
            console_msgs: list[str] = []
            page_errors: list[str] = []
            failed_requests: list[str] = []
            http_error_responses: list[tuple[object, str, str, str]] = []

            # Fresh context per route keeps cookies and storage isolated.
            context = browser.new_context(locale="en-US")
            page = context.new_page()
            page.on("console", lambda msg, _c=console_msgs: _c.append(
                _format_console_message(msg)
            ))
            page.on("pageerror", lambda err, _p=page_errors, _page=page: _p.append(
                _format_page_error(err, _page)
            ))
            page.on("requestfailed", lambda req, _f=failed_requests: _f.append(
                _format_failed_request(req)
            ))

            url = base_url.rstrip("/") + route

            def _on_response(
                resp,
                _h=http_error_responses,
            ):
                if resp.status >= 400:
                    category = "static_failure" if _is_static_url(resp.url) else "http_error_response"
                    frame = _frame_label(resp.request.frame)
                    _h.append((
                        resp,
                        resp.url,
                        category,
                        f"frame={frame} {resp.request.method} {resp.url} → {resp.status}",
                    ))

            page.on("response", _on_response)

            t0 = time.monotonic()
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                # Brief settle for JS rendering
                page.wait_for_timeout(1_000)
                result.elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
                result.status = resp.status if resp else None
            except Exception as exc:
                result.elapsed_ms = round((time.monotonic() - t0) * 1000, 1)
                result.findings.append(
                    RouteFinding(route, "page_error", _severity_for("page_error"), str(exc))
                )
                results.append(result)
                context.close()
                continue

            # Force English locale
            page.evaluate("""() => {
                try { localStorage.setItem('dx-lang', 'en'); } catch {}
                document.documentElement.lang = 'en';
                if (window.DXI18n && typeof DXI18n.set === 'function') {
                    DXI18n.set('en'); DXI18n.apply && DXI18n.apply();
                }
            }""")
            page.wait_for_timeout(500)

            if result.status and result.status >= 400:
                result.findings.append(
                    RouteFinding(
                        route, "status_error", _severity_for("status_error"),
                        f"HTTP {result.status}"
                    )
                )

            for msg in console_msgs:
                if msg.startswith("[error]"):
                    result.findings.append(
                        RouteFinding(route, "console_error", _severity_for("console_error"), msg)
                    )
                elif msg.startswith("[warning]"):
                    result.findings.append(
                        RouteFinding(route, "console_warning", _severity_for("console_warning"), msg)
                    )

            for err in page_errors:
                result.findings.append(
                    RouteFinding(route, "page_error", _severity_for("page_error"), err)
                )

            # Failed requests (network-level failures)
            for req_info in failed_requests:
                result.findings.append(
                    RouteFinding(route, "failed_request", _severity_for("failed_request"), req_info)
                )

            # HTTP error responses (status >= 400, excluding goto response)
            # Filter by object identity so redirected navigations are excluded
            goto_resp = resp
            for resp_obj, _resp_url, category, resp_info in http_error_responses:
                if resp_obj is goto_resp:
                    continue
                result.findings.append(
                    RouteFinding(route, category, _severity_for(category), resp_info)
                )

            try:
                body_text = page.inner_text("body", timeout=5_000)
            except Exception:
                body_text = ""

            # Korean leak while English is forced
            if _KOREAN_RE.search(body_text):
                sample = _KOREAN_RE.search(body_text)
                ctx_start = max(0, sample.start() - 20)  # type: ignore[union-attr]
                ctx_end = min(len(body_text), sample.end() + 20)  # type: ignore[union-attr]
                result.findings.append(
                    RouteFinding(
                        route, "korean_leak", _severity_for("korean_leak"),
                        f"Korean text while en: …{body_text[ctx_start:ctx_end]}…"
                    )
                )

            # Placeholder tokens (word-boundary regex to avoid false positives)
            for token_label, token_re in _PLACEHOLDER_PATTERNS:
                if token_re.search(body_text):
                    result.findings.append(
                        RouteFinding(
                            route, "placeholder", _severity_for("placeholder"),
                            f"Visible placeholder: {token_label}"
                        )
                    )

            for token_label, category, token_re in _DEV_TOKEN_PATTERNS:
                if token_re.search(body_text):
                    result.findings.append(
                        RouteFinding(
                            route, category, _severity_for(category),
                            f"Visible release leak token: {token_label}"
                        )
                    )

            result.checks.extend(_run_keyboard_smoke(page, route))
            for check in result.checks:
                if check.name in KEYBOARD_SMOKE_NAMES and check.status == "fail":
                    result.findings.append(
                        RouteFinding(route, "keyboard_smoke", _severity_for("keyboard_smoke"), f"{check.name}: {check.detail}")
                    )

            results.append(result)
            context.close()

        browser.close()

    return results


def run_audit(base_url: str, routes: list[str]) -> dict:
    """Run the full audit and return a JSON-serializable dict."""
    results = _try_playwright_audit(base_url, routes)
    local_api_smoke = _run_local_api_smoke(base_url)
    keyboard_smoke = [
        check
        for result in results
        for check in result.checks
        if check.name in KEYBOARD_SMOKE_NAMES
    ]
    local_api_smoke_failures = _smoke_failure_count(local_api_smoke)
    keyboard_smoke_failures = _smoke_failure_count(keyboard_smoke)
    has_smoke_failure = local_api_smoke_failures > 0 or keyboard_smoke_failures > 0

    has_blocker = any(
        f.severity == "blocker"
        for r in results
        for f in r.findings
    )

    return {
        "base_url": base_url,
        "routes_audited": len(results),
        "has_blocker": has_blocker,
        "has_smoke_failure": has_smoke_failure,
        "finding_counts": _finding_counts(results),
        "local_api_smoke_failures": local_api_smoke_failures,
        "keyboard_smoke_failures": keyboard_smoke_failures,
        "local_api_smoke": [asdict(c) for c in local_api_smoke],
        "keyboard_smoke": [asdict(c) for c in keyboard_smoke],
        "results": [asdict(r) for r in results],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="DX AI Studio release route audit")
    parser.add_argument(
        "--base-url", default="http://127.0.0.1:8890",
        help="Base URL of the running DX AI Studio instance",
    )
    parser.add_argument(
        "--routes", default=None,
        help="Comma-separated subset of routes to audit",
    )
    parser.add_argument(
        "--json", dest="json_file", default=None,
        help="Path to write JSON output file",
    )
    args = parser.parse_args()

    routes = (
        [r.strip() for r in args.routes.split(",")]
        if args.routes
        else list(RELEASE_ROUTES)
    )

    try:
        report = run_audit(args.base_url, routes)
    except Exception as exc:
        print(f"[release_audit] execution failure: {exc}", file=sys.stderr)
        return 1

    output = json.dumps(report, indent=2, ensure_ascii=False)
    print(output)

    if args.json_file:
        from pathlib import Path
        Path(args.json_file).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_file).write_text(output, encoding="utf-8")
        print(f"\n[release_audit] Written to {args.json_file}", file=sys.stderr)

    if report.get("has_blocker") or report.get("has_smoke_failure"):
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
