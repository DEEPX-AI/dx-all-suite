#!/usr/bin/env python3
"""DXBaseHandler + DXServer — 모든 DX 서버의 공통 베이스 클래스.

DX App, DX Sandbox, DX Stream, DX Model Zoo, DX Compiler, Launcher의
35개 장점을 통합한 단일 베이스. 서브클래스는 route()만 오버라이드하면 된다.

Usage:
    from shared.dx_server import DXBaseHandler, DXServer

    class MyHandler(DXBaseHandler):
        server_name = "My App"
        static_dir = Path(__file__).parent / "static"
        templates_dir = Path(__file__).parent / "templates"
        log_filter = ["/static/", "/api/hb"]

        def route(self):
            if self.url_path == "/":
                return self.send_html(...)
            if self.url_path == "/api/data":
                return self.send_json({"ok": True})
            self.send_error_json(404, "Not found")

    if __name__ == "__main__":
        DXServer(MyHandler, "My App", default_port=8080).start()
"""
from __future__ import annotations

import argparse
from email import policy
from email.parser import BytesHeaderParser
import email.utils
import gzip
import hashlib
import hmac
import ipaddress
import io
import json
import math
import mimetypes
import os
import re
import signal
import socket
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs, parse_qsl, unquote, urlencode, urlunsplit, urlsplit

from shared.paths import is_safe_path as _shared_is_safe_path

from shared import shell as _shell


# Behind a TLS-inspecting proxy (e.g. FortiGate) the OS trust store holds the
# inspection root CA, but Python's `requests`/certifi bundle does not — so HTTPS
# downloads (ModelZoo .dxnn models, pip, etc.) fail with CERTIFICATE_VERIFY_FAILED
# even though the same URL verifies fine via the system CA bundle. Point Python at
# the system bundle when present and not already configured. Every studio module
# server imports this base, and the setting is inherited by the subprocesses they
# spawn (setup.sh downloader, agent CLIs) via the copied environment.
def _bridge_system_ca_trust():
    if os.environ.get("REQUESTS_CA_BUNDLE") and os.environ.get("SSL_CERT_FILE"):
        return
    for _ca in ("/etc/ssl/certs/ca-certificates.crt",   # Debian/Ubuntu
                "/etc/pki/tls/certs/ca-bundle.crt",      # RHEL/Fedora
                "/etc/ssl/cert.pem"):                    # misc
        if os.path.isfile(_ca):
            os.environ.setdefault("REQUESTS_CA_BUNDLE", _ca)
            os.environ.setdefault("SSL_CERT_FILE", _ca)
            break


_bridge_system_ca_trust()


def _resolve_bind_host() -> str | None:
    """모듈 서버의 bind 주소 — 기본은 loopback (QA COM-A1, 2026-10-01).

    모듈 (dx_app · dx_compiler …) 은 launcher 가 127.0.0.1 로 중계하므로 밖에 열 이유가 없다. launcher 는 자식
    env 에 DX_BIND_HOST=127.0.0.1 을 명시한다. 단독 실행에서 넓히려면 DX_BIND_HOST=<host> — 그때는 DX_API_TOKEN 이
    있어야 시작한다 (`DXServer._create_server`). DX_BIND_LOCAL=1 은 예전처럼 127.0.0.1.
    """
    if os.environ.get("DX_BIND_LOCAL", "").strip().lower() in ("1", "true", "yes"):
        return "127.0.0.1"
    explicit = os.environ.get("DX_BIND_HOST", "").strip()
    return explicit or "127.0.0.1"


def _is_loopback_host(host: str | None) -> bool:
    h = (host or "").strip().strip("[]").lower()
    if h == "localhost":
        return True
    try:
        return ipaddress.ip_address(h).is_loopback
    except ValueError:
        return False


def _configured_api_token() -> str | None:
    token = os.environ.get("DX_API_TOKEN", "").strip()
    return token or None


class _BodyCounter:
    """요청 하나 동안 rfile 을 감싸 handler 가 읽은 본문 바이트를 센다 (`DXBaseHandler._dispatch_request`)."""

    def __init__(self, raw):
        self.raw = raw
        self.count = 0

    def read(self, n=-1):
        data = self.raw.read(n)
        self.count += len(data)
        return data

    def read1(self, n=-1):
        data = self.raw.read1(n)
        self.count += len(data)
        return data

    def readline(self, limit=-1):
        data = self.raw.readline(limit)
        self.count += len(data)
        return data

    def readinto(self, b):
        n = self.raw.readinto(b) or 0
        self.count += n
        return n

    def __getattr__(self, name):
        return getattr(self.raw, name)


class RequestBodyError(Exception):
    """요청 body 파싱 실패를 HTTP status와 함께 전달한다."""

    def __init__(self, status_code: int, message: str):
        super().__init__(message)
        self.status_code = status_code
        self.message = message



class DXBaseHandler(SimpleHTTPRequestHandler):
    """HTTP 요청 핸들러 베이스 — 응답 헬퍼, SSE, 캐시, 보안, 라우팅 통합."""

    protocol_version = "HTTP/1.1"


    server_name: str = "DXServer"
    static_dir: Path | None = None
    templates_dir: Path | None = None
    # shared.shell.ShellSpec — 통합 App Shell(Option A)을 쓰는 모듈만 설정한다.
    # None이면 serve_template이 템플릿을 그대로 통과시킨다.
    shell_spec: "_shell.ShellSpec | None" = None

    # 로깅: 해당 경로 포함 시 로그 생략
    log_filter: list[str] | None = None
    log_silent: bool = False

    # 캐시 (opt-in)
    cache_enabled: bool = False
    cache_max: int = 512
    cache_ttl: int = 3600

    # 업로드 크기 제한 (바이트)
    upload_max_bytes: int = 500 * 1024 * 1024  # 500MB
    json_max_bytes: int = 1024 * 1024  # 1MB

    # 공유 캐시 저장소 (클래스 레벨)
    _cache: dict = {}
    _cache_lock = threading.Lock()

    # 에셋 콘텐츠 해시 캐시 (클래스 레벨)
    _asset_hash_cache: dict = {}
    _asset_hash_lock = threading.Lock()
    _ASSET_ATTR_RE = re.compile(
        r'(?P<prefix>\b(?:src|href)=["\'])(?P<url>/(?!/)[^"\']+\.(?:js|css)(?:\?[^"\']*)?)(?P<suffix>["\'])'
    )

    def handle(self):
        try:
            super().handle()
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            self.close_connection = True


    def _parse_request_url(self):
        """URL 파싱 → self.parsed, self.url_path, self.query 설정."""
        self.parsed = urlparse(self.path)
        self.url_path = unquote(self.parsed.path).rstrip("/") or "/"
        self.query = parse_qs(self.parsed.query)

    def read_json_body(self) -> dict:
        """POST/PUT body를 JSON으로 파싱. 빈 body → {}."""
        length = self._content_length_or_error()
        if length > self.json_max_bytes:
            raise RequestBodyError(413, "JSON body too large")
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as exc:
            raise RequestBodyError(400, f"Invalid JSON: {exc}") from exc
        if not isinstance(data, dict):
            raise RequestBodyError(400, "Invalid JSON object")
        return data

    def _content_length_or_error(self) -> int:
        raw = self.headers.get("Content-Length", "0")
        try:
            length = int(raw)
        except (TypeError, ValueError) as exc:
            raise RequestBodyError(400, "Invalid Content-Length") from exc
        if length < 0:
            raise RequestBodyError(400, "Invalid Content-Length")
        return length

    def read_query_param(self, key: str, default: str = "") -> str:
        """query string에서 단일 파라미터 추출."""
        return self.query.get(key, [default])[0]

    def _is_head_request(self) -> bool:
        return getattr(self, "command", "GET") == "HEAD"

    def parse_multipart(self):
        """multipart/form-data 파싱. Returns (fields_dict, files_dict).

        files_dict: {name: {"filename": str, "data": bytes}}
        """
        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            return {}, {}

        boundary = None
        for part in content_type.split(";"):
            part = part.strip()
            if part.startswith("boundary="):
                boundary = part[9:].strip('"')
                break
        if not boundary:
            return {}, {}

        length = self._content_length_or_error()
        if length > self.upload_max_bytes:
            raise RequestBodyError(413, "Multipart body too large")

        delimiter = b"--" + boundary.encode("utf-8", "strict")
        continuation = b"\r\n" + delimiter
        spool = tempfile.TemporaryFile()
        try:
            remaining = length
            while remaining > 0:
                chunk = self.rfile.read(min(65536, remaining))
                if not chunk:
                    break
                spool.write(chunk)
                remaining -= len(chunk)
            if remaining:
                raise RequestBodyError(400, "Incomplete multipart body")

            def boundary_suffix(offset, marker_length):
                spool.seek(offset + marker_length)
                suffix = spool.read(2)
                if suffix == b"\r\n":
                    return False
                if suffix != b"--":
                    return None
                return spool.read(2) in (b"", b"\r\n")

            spool.seek(0)
            if spool.read(len(delimiter)) != delimiter:
                return {}, {}
            first_final = boundary_suffix(0, len(delimiter))
            if first_final is None:
                return {}, {}

            markers = [(0, len(delimiter), first_final)]
            overlap = len(continuation) - 1
            carry = b""
            file_offset = 0
            spool.seek(0)
            while True:
                chunk = spool.read(65536)
                if not chunk:
                    break
                haystack = carry + chunk
                base_offset = file_offset - len(carry)
                start = 0
                while True:
                    found = haystack.find(continuation, start)
                    if found < 0:
                        break
                    offset = base_offset + found
                    final = boundary_suffix(offset, len(continuation))
                    if final is not None:
                        markers.append((offset, len(continuation), final))
                    start = found + 1
                spool.seek(file_offset + len(chunk))
                carry = haystack[-overlap:] if overlap else b""
                file_offset += len(chunk)

            if not markers[-1][2]:
                return {}, {}

            fields = {}
            files = {}
            for index, (offset, marker_length, final) in enumerate(markers[:-1]):
                if final:
                    break
                next_offset = markers[index + 1][0]
                part_start = offset + marker_length + 2
                spool.seek(part_start)
                segment = spool.read(next_offset - part_start)
                raw_headers, separator, data = segment.partition(b"\r\n\r\n")
                if not separator:
                    continue
                headers = BytesHeaderParser(policy=policy.default).parsebytes(
                    raw_headers + b"\r\n\r\n"
                )
                name = headers.get_param("name", header="content-disposition") or "unknown"
                filename = headers.get_filename()
                if filename is not None:
                    files[name] = {"filename": filename, "data": data}
                else:
                    charset = headers.get_content_charset() or "utf-8"
                    fields[name] = data.decode(charset, "replace")
            return fields, files
        finally:
            spool.close()


    # 이보다 큰 200 JSON 은 gzip + 내용 ETag (2026-10-11 성능 감사 — launcher 가 화면마다 2.5 MB catalog 를 새로 받았다)
    _JSON_TRANSPORT_MIN = 8 * 1024
    _json_gzip_cache: dict[str, bytes] = {}

    def send_json(self, data, code: int = 200):
        """JSON 응답 + CORS + charset + Content-Length.

        큰 200 응답은 내용 hash ETag 와 no-cache 를 달아 같은 내용의 재요청을 304 로 끝내고, gzip 을 받는
        client 에는 압축해 보낸다. 작은 응답과 오류 응답은 예전 그대로다."""
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        if code != 200 or len(body) < self._JSON_TRANSPORT_MIN:
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            if self._is_head_request():
                return
            self.wfile.write(body)
            return

        etag = '"' + hashlib.blake2b(body, digest_size=12).hexdigest() + '"'
        inm = self.headers.get("If-None-Match")
        if inm is not None and etag in [t.strip() for t in inm.split(",")]:
            self.send_response(304)
            self.send_header("ETag", etag)
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Vary", "Accept-Encoding")
            self.end_headers()
            return

        payload = body
        gz = "gzip" in self.headers.get("Accept-Encoding", "")
        if gz:
            cache = DXBaseHandler._json_gzip_cache
            payload = cache.get(etag)
            if payload is None:
                payload = gzip.compress(body, compresslevel=5)
                if len(cache) >= 8:
                    try:
                        cache.pop(next(iter(cache)), None)
                    except (StopIteration, RuntimeError):   # 다른 thread 가 동시에 바꿨다 — 다음에 비운다
                        pass
                cache[etag] = payload
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("ETag", etag)
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Vary", "Accept-Encoding")
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.send_header("Content-Length", len(payload))
        self.end_headers()
        if self._is_head_request():
            return
        self.wfile.write(payload)

    def send_html(self, html, code: int = 200):
        """HTML 응답."""
        if isinstance(html, str):
            html = html.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", len(html))
        self.end_headers()
        if self._is_head_request():
            return
        self.wfile.write(html)

    def send_error_json(self, code: int, message: str):
        """구조화된 에러 JSON 응답: {"error": message}."""
        self.send_json({"error": message}, code)

    def send_bytes(self, data: bytes, content_type: str, code: int = 200,
                   filename: str | None = None):
        """바이너리 응답. filename이 있으면 Content-Disposition: attachment."""
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(data))
        if filename:
            self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.end_headers()
        if self._is_head_request():
            return
        self.wfile.write(data)

    # 장기 캐시 대상 확장자
    _IMMUTABLE_SUFFIXES = frozenset((
        ".woff", ".woff2", ".ttf", ".otf", ".eot",
        ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
    ))
    # ?v=<내용 hash> 가 맞는 static (render_html_with_asset_hashes 가 붙인 URL)
    _HASHED_CACHE = "public, max-age=31536000, immutable"
    # 아이콘 sprite — <use href> 와 dx-icon.js 가 같은 hash URL 을 쓰게 한다
    _SPRITE_URL = "/static/shared/dx-icons.svg"
    _SPRITE_REF_RE = re.compile(r'(?P<q>["\'])/static/shared/dx-icons\.svg(?:\?[^"\'#]*)?#')
    _SPRITE_META_RE = re.compile(r'<meta name="dx-icons" content="[^"]*">')
    # gzip 대상 MIME 타입 (text/html, text/event-stream 제외)
    _GZIP_MIME_TYPES = frozenset((
        "application/javascript", "application/x-javascript",
        "application/json", "application/xml", "image/svg+xml",
    ))

    def send_file(self, filepath, content_type: str | None = None, cache_control: str | None = None,
                  content_disposition: str | None = None):

        p = Path(filepath)
        if not p.exists() or not p.is_file():
            self.send_error(404)
            return
        content_type = content_type or mimetypes.guess_type(str(p))[0] or "application/octet-stream"

        stat = p.stat()
        file_size = stat.st_size
        mtime_ns = stat.st_mtime_ns
        mtime_sec = stat.st_mtime

        etag = f'W/"{mtime_ns:x}-{file_size:x}"'
        last_modified = email.utils.formatdate(mtime_sec, usegmt=True)

        # Cache-Control 정책 (override via cache_control= for shell assets)
        #
        # JS/CSS/JSON/SVG는 no-cache(매 요청 재검증, ETag로 304). max-age로 캐시하면
        # 삭제/이동된 비버전 리소스를 옛 캐시가 참조해 첫 로드에서 404 → 화면 blank가
        # 되고, 일반 새로고침은 max-age 만료 전이라 캐시를 그대로 써 고쳐지지 않는다
        # (하드 리프레시만 회피). launcher가 자기 에셋에 이미 쓰는 정책과 일치.
        # 폰트/이미지(immutable)는 내용이 안정적이고 무거우며, 프레시 HTML/CSS/JSON이
        # 참조할 때만 로드되므로 장기 캐시 유지.
        base_ct = content_type.split(";")[0].strip().lower()
        suffix = p.suffix.lower()
        if cache_control is None:
            if base_ct == "text/html":
                cache_control = "no-cache"
            elif suffix in self._IMMUTABLE_SUFFIXES:
                cache_control = "public, max-age=86400, must-revalidate"
            else:
                cache_control = "no-cache, must-revalidate"
        # ?v= 가 지금 내용 hash 와 같으면 URL 이 곧 내용이다 — 재검증할 이유가 없다. HTML 이 늘 새로
        # 받아지고 (no-cache) 새 hash 를 적으므로, 내용이 바뀌면 URL 이 바뀐다. 옛 HTML 이 옛 hash 로
        # 부르면 맞지 않아 위 정책 그대로 (stale 없음). 명시 cache_control= (launcher shell) 보다 우선.
        if base_ct != "text/html" and self._request_asset_version_matches(p):
            cache_control = self._HASHED_CACHE

        gzip_eligible = False
        if base_ct not in ("text/html", "text/event-stream"):
            if base_ct.startswith("text/") or base_ct in self._GZIP_MIME_TYPES:
                gzip_eligible = True

        # 조건부 요청 처리 (304) — Content-Length 생략 (RFC 7232 §4.1)
        inm = self.headers.get("If-None-Match")
        if inm is not None and inm.strip() == etag:
            self.send_response(304)
            self.send_header("Cache-Control", cache_control)
            self.send_header("ETag", etag)
            self.send_header("Last-Modified", last_modified)
            if gzip_eligible:
                self.send_header("Vary", "Accept-Encoding")
            self.end_headers()
            return

        ims = self.headers.get("If-Modified-Since")
        if ims is not None:
            try:
                ims_ts = email.utils.parsedate_to_datetime(ims).timestamp()
                if int(mtime_sec) <= int(ims_ts):
                    self.send_response(304)
                    self.send_header("Cache-Control", cache_control)
                    self.send_header("ETag", etag)
                    self.send_header("Last-Modified", last_modified)
                    if gzip_eligible:
                        self.send_header("Vary", "Accept-Encoding")
                    self.end_headers()
                    return
            except Exception:
                pass

        accept_enc = self.headers.get("Accept-Encoding", "")
        use_gzip = gzip_eligible and "gzip" in accept_enc

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", cache_control)
        self.send_header("ETag", etag)
        self.send_header("Last-Modified", last_modified)
        if content_disposition:
            self.send_header("Content-Disposition", content_disposition)
        if gzip_eligible:
            self.send_header("Vary", "Accept-Encoding")

        if use_gzip:
            data = p.read_bytes()
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as gz:
                gz.write(data)
            compressed = buf.getvalue()
            self.send_header("Content-Encoding", "gzip")
            self.send_header("Content-Length", len(compressed))
            self.end_headers()
            if self._is_head_request():
                return
            self.wfile.write(compressed)
        else:
            # Open first, then fstat on the descriptor to avoid TOCTOU race
            f = open(p, "rb")
            try:
                fd_stat = os.fstat(f.fileno())
                self.send_header("Content-Length", fd_stat.st_size)
                self.end_headers()
                if self._is_head_request():
                    return
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    self.wfile.write(chunk)
            finally:
                f.close()

    def send_download(self, filepath, filename: str):
        """Content-Disposition: attachment 파일 다운로드."""
        p = Path(filepath)
        if not p.exists() or not p.is_file():
            self.send_error(404)
            return
        content_type = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        data = p.read_bytes()
        self.send_bytes(data, content_type, filename=filename)

    def serve_static(self, rel_path: str, base_dir: Path | None = None):
        """static/ 디렉토리에서 안전하게 파일 서빙 (path traversal 차단)."""
        base = base_dir or self.static_dir
        if base is None:
            self.send_error(404)
            return
        base = base.resolve()
        safe_path = (base / rel_path).resolve()
        if not self._path_is_within(safe_path, base):
            self.send_error_json(403, "Path traversal not allowed")
            return
        if not safe_path.exists() or not safe_path.is_file():
            self.send_error(404)
            return
        ct = mimetypes.guess_type(str(safe_path))[0] or "application/octet-stream"
        self.send_file(safe_path, ct)

    def serve_template(self, name: str):
        """templates/ 디렉토리에서 HTML 읽기 → 에셋 해시 리라이트 → no-cache 응답."""
        if self.templates_dir is None:
            self.send_error(404)
            return
        filepath = self.templates_dir / name
        if not filepath.exists() or not filepath.is_file():
            self.send_error(404)
            return
        html = filepath.read_text(encoding="utf-8")
        # 통합 App Shell 주입: 모듈이 shell_spec 을 선언하면 템플릿의
        # {{DX_SHELL_*}} 자리가 shared/shell.py 마크업으로 채워진다.
        # 선언하지 않은 모듈은 그대로 통과한다 (아직 이관 전).
        html = _shell.apply(html, self.shell_spec)
        asset_scope = None
        if self.static_dir is not None:
            asset_scope = self.static_dir.parent.name
        html = self.render_html_with_asset_hashes(html, asset_scope=asset_scope)
        self.send_html_no_cache(html)


    @staticmethod
    def _path_is_within(path: Path, root: Path) -> bool:
        """Return True when *path* is inside *root* or exactly *root*."""
        return _shared_is_safe_path(path, [root])

    @classmethod
    def asset_content_hash(cls, filepath) -> str:
        """파일 콘텐츠의 SHA-256 해시 앞 8자를 반환.

        해시는 콘텐츠에서 직접 계산한다. 예전엔 (path, st_mtime_ns, st_size)로 캐시했으나,
        일부 파일시스템은 mtime_ns 해상도가 거칠어 '같은 크기·같은 mtime_ns로 내용만 바뀐'
        경우(빠른 재기록/배포 스왑)를 놓쳐 stale 해시를 반환했다. 정적 자산은 작으므로
        매 호출 콘텐츠를 읽어 정확성을 보장하고, 캐시는 경로당 최신 1개만 유지한다."""
        p = Path(filepath).resolve()
        data = p.read_bytes()
        digest = hashlib.sha256(data).hexdigest()[:8]
        with cls._asset_hash_lock:
            for old_key in [old for old in cls._asset_hash_cache if old[0] == str(p)]:
                del cls._asset_hash_cache[old_key]
            cls._asset_hash_cache[(str(p), len(data))] = digest
        return digest

    def _resolve_asset_path(self, url_path: str, extra_static_roots=None):
        """URL 경로를 로컬 파일로 안전하게 해석. 없으면 None."""
        shared_static = self._shared_static.resolve()
        if url_path.startswith("/static/shared/"):
            rel = url_path[len("/static/shared/"):]
            candidate = (self._shared_static / rel).resolve()
            if self._path_is_within(candidate, shared_static) and candidate.is_file():
                return candidate, False  # (path, is_module_local)
        elif url_path.startswith("/static/"):
            if self.static_dir is not None:
                rel = url_path[len("/static/"):]
                base = self.static_dir.resolve()
                candidate = (self.static_dir / rel).resolve()
                if self._path_is_within(candidate, base) and candidate.is_file():
                    return candidate, True
        elif extra_static_roots:
            for root in extra_static_roots:
                root_resolved = root.resolve()
                candidate = (root / url_path.lstrip("/")).resolve()
                if self._path_is_within(candidate, root_resolved) and candidate.is_file():
                    return candidate, False
        return None, False

    def _request_asset_version_matches(self, p: Path) -> bool:
        """요청 query 의 v 가 파일 내용 hash 와 같은가."""
        try:
            versions = parse_qs(urlsplit(getattr(self, "path", "") or "").query).get("v")
            return bool(versions) and versions[-1] == self.asset_content_hash(p)
        except (OSError, ValueError):
            return False

    @classmethod
    def sprite_url(cls) -> str | None:
        """내용 hash 붙은 sprite URL. sprite 가 없으면 None."""
        try:
            return f"{cls._SPRITE_URL}?v={cls.asset_content_hash(cls._shared_static / 'dx-icons.svg')}"
        except (OSError, PermissionError):
            return None

    @classmethod
    def version_sprite_refs(cls, text: str) -> str:
        """sprite 참조 (정적 <use> · inline script 문자열) 에 hash 를 붙인다. fragment (#id) 는 그대로.
        rewrite 뒤에 끼워 넣는 조각 (launcher 의 NPU Monitor widget) 도 이것을 거친다."""
        url = cls.sprite_url()
        if url is None:
            return text
        return cls._SPRITE_REF_RE.sub(lambda m: f"{m.group('q')}{url}#", text)

    def _render_sprite_refs(self, html: str) -> str:
        """sprite 참조에 hash 를 붙이고 <meta name="dx-icons"> 로 dx-icon.js 에 같은 URL 을 알린다."""
        url = self.sprite_url()
        if url is None:
            return html
        html = self.version_sprite_refs(html)
        meta = f'<meta name="dx-icons" content="{url}">'
        if self._SPRITE_META_RE.search(html):
            return self._SPRITE_META_RE.sub(meta, html, count=1)
        idx = html.lower().find("</head>")
        if idx == -1:
            return html
        return html[:idx] + meta + html[idx:]

    def render_html_with_asset_hashes(self, html: str, asset_scope=None, extra_static_roots=None) -> str:
        """HTML 내 로컬 CSS/JS URL에 콘텐츠 해시 v= 쿼리를 추가 (아이콘 sprite 참조 포함)."""
        def _replace_url(match):
            prefix = match.group("prefix")
            raw_url = match.group("url")
            suffix = match.group("suffix")

            parts = urlsplit(raw_url)
            url_path = parts.path

            resolved, is_module_local = self._resolve_asset_path(url_path, extra_static_roots)
            if resolved is None:
                return match.group(0)

            try:
                digest = self.asset_content_hash(resolved)
            except (OSError, PermissionError):
                return match.group(0)

            # 기존 쿼리 파싱 → v, m 제거 후 재구성
            params = [(k, v) for k, v in parse_qsl(parts.query) if k not in ("v", "m")]
            if is_module_local and asset_scope:
                params.append(("m", asset_scope))
            params.append(("v", digest))
            new_query = urlencode(params)
            new_url = urlunsplit(("", "", url_path, new_query, ""))
            return f"{prefix}{new_url}{suffix}"

        return self._render_sprite_refs(self._ASSET_ATTR_RE.sub(_replace_url, html))

    def send_html_no_cache(self, html: str, status: int = 200):
        """HTML 응답 + Cache-Control: no-cache."""
        data = html.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        if self._is_head_request():
            return
        self.wfile.write(data)


    def start_sse(self):
        """SSE 응답 헤더 전송. 이후 send_sse()로 이벤트 전송."""
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()
        self._sse_chunked = True

    def _write_chunk(self, data: bytes):
        """HTTP/1.1 chunked transfer-encoding으로 한 프레임 기록 후 flush."""
        self.wfile.write(f"{len(data):x}\r\n".encode("ascii"))
        self.wfile.write(data)
        self.wfile.write(b"\r\n")
        self.wfile.flush()

    def _end_chunked(self):
        """종단 청크(0\\r\\n\\r\\n) 전송."""
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def end_sse(self):
        """SSE 스트림 종료. chunked 모드일 때 종단 청크 전송 (멱등)."""
        if not getattr(self, "_sse_chunked", False):
            return
        self._sse_chunked = False
        try:
            self._end_chunked()
        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_sse(self, event: str, data):
        """SSE 이벤트 전송. data는 자동으로 JSON 직렬화.

        BrokenPipeError / ConnectionResetError 시 False 반환.
        """
        try:
            if not isinstance(data, str):
                data = json.dumps(data, ensure_ascii=False, default=str)
            payload = f"event: {event}\ndata: {data}\n\n".encode("utf-8")
            if getattr(self, "_sse_chunked", False):
                self._write_chunk(payload)
            else:
                self.wfile.write(payload)
                self.wfile.flush()
            return True
        except (BrokenPipeError, ConnectionResetError):
            return False

    def send_sse_data(self, data):
        """event 없이 data만 전송 (기존 패턴 호환)."""
        try:
            if not isinstance(data, str):
                data = json.dumps(data, ensure_ascii=False, default=str)
            payload = f"data: {data}\n\n".encode("utf-8")
            if getattr(self, "_sse_chunked", False):
                self._write_chunk(payload)
            else:
                self.wfile.write(payload)
                self.wfile.flush()
            return True
        except (BrokenPipeError, ConnectionResetError):
            return False


    def cache_get(self, prefix: str, data: dict):
        """SHA256 해시 키로 캐시 조회. TTL 만료 시 None."""
        if not self.cache_enabled:
            return None
        key = self._make_cache_key(prefix, data)
        with self._cache_lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            result, ts = entry
            if time.time() - ts > self.cache_ttl:
                del self._cache[key]
                return None
            return result

    def cache_set(self, prefix: str, data: dict, result):
        """캐시 저장 + LRU 제거 (max 초과 시)."""
        if not self.cache_enabled:
            return
        key = self._make_cache_key(prefix, data)
        with self._cache_lock:
            if len(self._cache) >= self.cache_max:
                oldest = min(self._cache, key=lambda k: self._cache[k][1])
                del self._cache[oldest]
            self._cache[key] = (result, time.time())

    def cache_clear(self):
        """전체 캐시 무효화."""
        with self._cache_lock:
            count = len(self._cache)
            self._cache.clear()
            return count

    def cache_stats(self) -> dict:
        """캐시 통계 반환."""
        with self._cache_lock:
            return {
                "cached_entries": len(self._cache),
                "max": self.cache_max,
                "ttl_sec": self.cache_ttl,
            }

    def send_cached_json(self, prefix: str, data: dict, producer):
        """캐시된 결과가 있으면 반환, 없으면 producer()를 실행하고 캐시."""
        cached = self.cache_get(prefix, data)
        if cached is not None:
            self.send_json(cached)
            return
        result = producer()
        self.cache_set(prefix, data, result)
        self.send_json(result)

    @staticmethod
    def _make_cache_key(prefix: str, data: dict) -> str:
        raw = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return prefix + ":" + hashlib.sha256(raw.encode()).hexdigest()[:16]


    @staticmethod
    def is_safe_path(path: str, allowed_dir: str | Path | None = None) -> bool:
        """경로가 allowed_dir 범위 안에 있는지 검증.

        allowed_dir가 None이면 path가 유효한지만 검사
        (상대경로 트래버설 '..' 검출).
        """
        try:
            if allowed_dir is not None:
                return _shared_is_safe_path(path, [allowed_dir])
            # allowed_dir 없으면 '..' 없는지 확인 (resolve()로 null-byte 등 무효 경로도 거부)
            Path(path).resolve()
            return ".." not in Path(path).parts
        except (ValueError, OSError):
            return False

    @staticmethod
    def sanitize_id(value: str) -> str | None:
        """안전한 ID 검증: [a-zA-Z0-9_-]만 허용. 실패 시 None."""
        if value and re.match(r'^[a-zA-Z0-9_.-]+$', value):
            return value
        return None


    _CHAT_ROUTES = frozenset((
        "/api/chat",
        "/api/chat/config",
        "/api/chat/config/test",
        "/api/chat/local/models",
        "/api/chat/knowledge/refresh",
    ))

    # Providers that need no API key: local/self-hosted runtimes + CLI-backed agents
    # (the coding-agent CLI carries its own login).
    _KEYLESS_PROVIDERS = frozenset(("local", "agent-cli"))

    def _effective_request_origin(self) -> tuple[str, str]:
        """현재 요청의 외부 origin(scheme, netloc)을 reverse proxy 헤더까지 반영해 계산."""
        host = self.headers.get("Host", "").split(",", 1)[0].strip().lower()
        forwarded_host = self.headers.get(
            "X-Forwarded-Host", ""
        ).split(",", 1)[0].strip().lower()
        reference_host = (
            forwarded_host
            if forwarded_host and self._is_loopback_netloc(host)
            else host
        )
        forwarded_proto = self.headers.get(
            "X-Forwarded-Proto", ""
        ).split(",", 1)[0].strip().lower()
        scheme = forwarded_proto if forwarded_proto in ("http", "https") else "http"
        return scheme, reference_host

    def _url_matches_effective_origin(self, raw_url: str) -> bool:
        p = urlparse(raw_url)
        if p.scheme not in ("http", "https") or not p.netloc:
            return False
        scheme, netloc = self._effective_request_origin()
        return p.scheme.lower() == scheme and p.netloc.lower() == netloc

    def _is_cross_origin_chat(self) -> bool:
        """Check if the current request to a chat route is cross-origin.

        Returns True (reject) if Origin or Referer is present and not same-origin.
        Returns False (allow) if both are absent or if same-origin.
        """
        origin = self.headers.get("Origin", "")
        if origin:
            return not self._url_matches_effective_origin(origin)
        referer = self.headers.get("Referer", "")
        if referer:
            return not self._url_matches_effective_origin(referer)
        return False

    def _is_loopback_netloc(self, netloc: str) -> bool:
        if not netloc:
            return False
        if netloc.startswith("["):
            end = netloc.find("]")
            host = netloc[1:end] if end != -1 else netloc
        else:
            host = netloc.split(":", 1)[0]
        return host in {"127.0.0.1", "localhost", "::1"}

    def do_OPTIONS(self):
        """preflight — same-origin 만 (QA COM-A1). 교차 Origin 은 403, CORS 허용 헤더는 보내지 않는다."""
        self._parse_request_url()
        if not self._host_ok():
            return self._refuse_host()
        origin = self.headers.get("Origin", "")
        if origin and not self._url_matches_effective_origin(origin):
            return self._refuse_cross_origin()
        self.send_response(204)
        self.send_header("Allow", "GET, HEAD, POST, PUT, PATCH, DELETE, OPTIONS")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _check_same_origin(self) -> bool:
        """Origin/Referer가 있으면 same-origin인지 확인. 없으면 True(허용).

        브라우저 origin 기준에 맞춰 scheme + netloc을 모두 비교한다.
        reverse proxy에서는 X-Forwarded-Proto/Host를 외부 origin으로 사용한다.
        """
        origin = self.headers.get("Origin", "")
        if origin:
            return self._url_matches_effective_origin(origin)
        referer = self.headers.get("Referer", "")
        if referer:
            return self._url_matches_effective_origin(referer)
        # Origin/Referer 없음 (curl 등) → 허용
        return True

    # ── 원격 접근 (QA COM-A1, spec 2026-10-01) ────────────────────────────────
    # launcher 가 shared.remote_access.RemoteAccess 를 둔다 (페어링 · 세션). 모듈 서버는 None.
    remote_access = None

    def _peer_ip(self) -> str:
        try:
            return self.client_address[0]
        except (AttributeError, IndexError, TypeError):
            return ""

    @staticmethod
    def _proxy_secret() -> str:
        """launcher 가 자식 env 로만 넘기는 비밀 — 중계한 요청에 X-DX-Proxy 로 실린다."""
        return os.environ.get("DX_PROXY_SECRET", "")

    def _is_local(self) -> bool:
        """이 기계 안에서 직접 온 요청 — 로컬 사용은 그대로 둔다 (사용자 결정).

        loopback peer 이고 X-Forwarded-For 가 없어야 한다 (같은 기계의 reverse proxy 경유는 원격). launcher 가
        중계한 요청은 X-Forwarded-For 가 붙지만 X-DX-Proxy 의 비밀이 맞으면 launcher 가 이미 인증한 것이다."""
        ip = self._peer_ip().split("%", 1)[0]
        try:
            addr = ipaddress.ip_address(ip)
            if getattr(addr, "ipv4_mapped", None):
                addr = addr.ipv4_mapped
            loopback = addr.is_loopback
        except ValueError:
            loopback = False
        if not loopback:
            return False
        if self.headers.get("X-Forwarded-For") or self.headers.get("Forwarded"):
            secret = self._proxy_secret()
            return bool(secret) and hmac.compare_digest(
                self.headers.get("X-DX-Proxy", "").encode("utf-8"), secret.encode("utf-8"))
        return True

    def _host_ok(self) -> bool:
        """DNS rebinding 차단 — IP Host 는 허용, 이름은 localhost · 이 기계 · DX_ALLOWED_HOSTS."""
        from shared.remote_access import host_allowed
        return host_allowed(self.headers.get("Host", ""))

    def _origin_ok(self, require: bool = False) -> bool:
        """Origin (없으면 Referer) 이 same-origin 인가. 둘 다 없으면 ``not require``."""
        origin = self.headers.get("Origin", "")
        if origin:
            return self._url_matches_effective_origin(origin)
        referer = self.headers.get("Referer", "")
        if referer:
            return self._url_matches_effective_origin(referer)
        return not require

    def _refuse_host(self):
        self.send_error_json(403, "Host not allowed")

    def _refuse_cross_origin(self):
        self.send_error_json(403, "Cross-origin request refused")

    def _is_state_changing(self) -> bool:
        return self.command in ("POST", "PUT", "PATCH", "DELETE")

    def _token_ok(self) -> bool:
        token = _configured_api_token()
        if not token:
            return False
        # Constant-time comparison (hmac.compare_digest) so a valid token can't be
        # recovered by timing the response to guessed prefixes.
        def _eq(candidate: str) -> bool:
            return hmac.compare_digest(candidate.encode("utf-8"), token.encode("utf-8"))

        auth = self.headers.get("Authorization", "")
        if auth.startswith("Bearer ") and _eq(auth[7:].strip()):
            return True
        return _eq(self.headers.get("X-DX-Api-Token", "").strip())

    def _remote(self):
        return type(self).remote_access

    def _session(self):
        ra = self._remote()
        if ra is None:
            return None
        token = ra.cookie_value(self.headers.get("Cookie", ""))
        return ra.sessions.valid(token) if token else None

    def _auth_exempt(self) -> bool:
        """인증 없이 원격에서 닿아도 되는 경로 (launcher: 페어링 화면 · 코드 입력)."""
        return False

    def _send_unauthorized(self):
        self.send_error_json(401, "Unauthorized")

    def _enforce_auth(self) -> bool:
        """막았으면 True. 로컬 → 통과, 원격 → DX_API_TOKEN 또는 페어링 세션 (쿠키) 이 있어야 한다."""
        self.auth_kind = None
        if self._is_local():
            self.auth_kind = "local"
            return False
        if self._token_ok():
            self.auth_kind = "token"
            return False
        session = self._session()
        if session:
            # 쿠키는 브라우저가 알아서 붙인다 — 상태를 바꾸는 요청은 Origin/Referer 가 반드시 같은 곳이어야 (CSRF)
            if self._is_state_changing() and not self._origin_ok(require=True):
                self._refuse_cross_origin()
                return True
            self.auth_kind = "session"
            self.auth_session = session
            return False
        if self._auth_exempt():
            return False
        self._send_unauthorized()
        return True

    def _dispatch_request(self):
        """URL 파싱 후 route() 호출. 다 읽히지 않은 본문은 응답 뒤에 비운다 (`_BodyCounter`)."""
        length, chunked = self._declared_body()
        counter = None
        if length > 0 and not chunked:
            counter = self.rfile = _BodyCounter(self.rfile)
        try:
            self._dispatch_checked()
        finally:
            if counter is not None:
                self.rfile = counter.raw
                self._drain_unread(length - counter.count)
            elif chunked or length < 0:
                self.close_connection = True

    def _declared_body(self):
        te = (self.headers.get("Transfer-Encoding") or "").lower()
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except (TypeError, ValueError):
            length = -1
        return length, "chunked" in te

    # 거부 (401 · 403) 와 본문을 쓰지 않는 handler (logout 등) 는 본문을 읽지 않는다. 그 바이트가 keep-alive 연결에
    # 남으면 다음 요청 줄 앞에 붙어 (`{}GET / HTTP/1.1`) 501 이 된다 — 원격 브라우저가 연결을 끊고 새로고침하면
    # 페어링 화면 대신 오류가 나왔다 (2026-10-02). handler 마다 고치는 대신 여기서 한 번에 비운다. 크면 (거절된
    # 업로드) 읽지 않고 연결을 닫는다.
    _DRAIN_MAX = 1024 * 1024

    def _drain_unread(self, left: int) -> None:
        if left <= 0:
            return
        if left > self._DRAIN_MAX:
            self.close_connection = True
            return
        try:
            while left > 0:
                chunk = self.rfile.read(min(65536, left))
                if not chunk:
                    break
                left -= len(chunk)
        except OSError:
            self.close_connection = True
            return
        if left > 0:
            self.close_connection = True

    def _dispatch_checked(self):
        self._parse_request_url()
        if not self._host_ok():
            return self._refuse_host()
        # 상태를 바꾸는 교차 Origin 요청은 로컬이어도 거부 — 보드 안 브라우저의 악성 페이지가 127.0.0.1 로 보내는 CSRF
        if self._is_state_changing() and not self._origin_ok():
            return self._refuse_cross_origin()
        if self._enforce_auth():
            return
        try:
            self.route()
        except RequestBodyError as exc:
            self.send_error_json(exc.status_code, exc.message)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            # Client hung up — let handle() suppress this quietly (no 500, no traceback).
            raise
        except Exception:
            # Defense in depth: never let an unexpected handler error escape and drop the
            # connection with no response — the launcher/reverse-proxy surfaces that as an
            # opaque 502 (exactly how the SpooledTemporaryFile multipart bug manifested).
            # Log it and return a real 500 instead. Best-effort: if the response already
            # started, the re-send is itself guarded so we never raise from here.
            import traceback
            traceback.print_exc()
            try:
                self.send_error_json(500, "Internal server error")
            except Exception:
                pass

    def do_GET(self):
        self._dispatch_request()

    def do_HEAD(self):
        self._dispatch_request()

    def do_POST(self):
        self._dispatch_request()

    def do_PUT(self):
        self._dispatch_request()

    def do_PATCH(self):
        self._dispatch_request()

    def do_DELETE(self):
        self._dispatch_request()

    def route(self):
        """서브클래스에서 오버라이드하여 앱 라우트 정의."""
        if self.route_common():
            return
        self.route_legacy()

    def route_common(self) -> bool:
        """공통 GET 라우트 처리. 처리했으면 True, 아니면 False.

        Handles:
          GET / or /index.html
          GET /static/shared/*
          GET /static/*
        """
        if self.command not in ("GET", "HEAD"):
            return False

        if self.url_path in ("/", "/index.html"):
            if self.templates_dir is not None:
                index = self.templates_dir / "index.html"
                if index.is_file():
                    self.serve_template("index.html")
                    return True

        if self.url_path.startswith("/static/shared/"):
            rel = self.url_path[len("/static/shared/"):]
            self.serve_shared_static(rel)
            return True

        if self.url_path.startswith("/static/"):
            rel = self.url_path[len("/static/"):]
            self.serve_static(rel)
            return True

        return False

    def route_legacy(self):
        """Legacy fallback used while modules migrate to common routing."""
        self.send_error(404)
        return True


    _shared_chat_static = Path(__file__).parent / "chat" / "static"
    _shared_static = Path(__file__).parent / "static"

    def serve_shared_static(self, rel_path: str):
        """shared/static/ 우선, shared/chat/static/ fallback."""
        candidate = (self._shared_static / rel_path).resolve()
        if (self._path_is_within(candidate, self._shared_static.resolve())
                and candidate.is_file()):
            ct = mimetypes.guess_type(str(candidate))[0] or "application/octet-stream"
            self.send_file(candidate, ct)
            return
        self.serve_static(rel_path, base_dir=self._shared_chat_static)

    def send_sse_stream(self, token_generator):
        """Generator[str]를 SSE로 스트리밍. 각 토큰을 data json으로 전송."""
        self.start_sse()
        try:
            for token in token_generator:
                data = json.dumps({"token": token}, ensure_ascii=False)
                self.send_sse_data(data)
            self.send_sse_data("[DONE]")
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            self.end_sse()

    def handle_chat_routes(self, chat_engine):
        """공통 채팅 라우트 처리. True 반환 시 처리됨.

        Routes:
          GET  /api/chat/config → 설정 상태
          POST /api/chat → SSE 스트리밍 응답
          POST /api/chat/config → 설정 저장
          POST /api/chat/config/test → 연결 테스트
          GET  /static/shared/* → shared static 파일

        Cross-origin requests to chat routes are rejected with 403.

        Usage in subclass route():
          if self.handle_chat_routes(chat_engine):
              return
        """
        method = self.command

        if method == "GET" and self.url_path.startswith("/static/shared/"):
            rel = self.url_path[len("/static/shared/"):]
            self.serve_shared_static(rel)
            return True

        # Cross-origin guard for chat routes
        if self.url_path in self._CHAT_ROUTES:
            if self._is_cross_origin_chat():
                self.send_error_json(403, "Cross-origin chat requests are not allowed")
                return True

        if method == "GET" and self.url_path == "/api/chat/config":
            self.send_json(chat_engine.get_config_status())
            return True

        # POST /api/chat/knowledge/refresh → regenerate SDK knowledge from the live .deepx
        if method == "POST" and self.url_path == "/api/chat/knowledge/refresh":
            try:
                from shared.chat.knowledge_sync import generate
                count = generate()
                self.send_json({"ok": True, "sources": count})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e)})
            return True

        # GET /api/chat/local/models?base=... → discover models from a local LLM runtime
        if method == "GET" and self.url_path == "/api/chat/local/models":
            from urllib.parse import urlparse, parse_qs
            from shared.chat.providers import discover_local_models
            base = (parse_qs(urlparse(self.path).query).get("base", [""])[0] or "").strip()
            models = discover_local_models(base or None)
            self.send_json({"models": models, "available": bool(models)})
            return True

        if method == "POST" and self.url_path == "/api/chat":
            data = self.read_json_body()
            message = data.get("message", "").strip()
            if not message:
                self.send_error_json(400, "message is required")
                return True
            history = data.get("history")
            lang = data.get("lang", "en")
            runtime_context = data.get("context")
            if runtime_context is not None and not isinstance(runtime_context, dict):
                runtime_context = None
            self.send_sse_stream(
                chat_engine.stream(message, history, lang=lang, runtime_context=runtime_context)
            )
            return True

        # POST /api/chat/config — save config
        if method == "POST" and self.url_path == "/api/chat/config":
            data = self.read_json_body()
            provider = data.get("provider", "").strip() if isinstance(data.get("provider"), str) else ""
            api_key = data.get("api_key", "").strip() if isinstance(data.get("api_key"), str) else ""
            model = data.get("model", "").strip() if isinstance(data.get("model"), str) else ""
            key_required = provider not in self._KEYLESS_PROVIDERS
            if not provider or not model or (key_required and not api_key):
                fields = "provider, model" + (", api_key" if key_required else "")
                self.send_error_json(400, f"{fields} are required")
                return True
            try:
                temperature = float(data.get("temperature", 0.7))
            except (TypeError, ValueError):
                self.send_error_json(400, "temperature must be a number")
                return True
            if not math.isfinite(temperature) or temperature < 0 or temperature > 2.0:
                self.send_error_json(400, "temperature must be between 0 and 2")
                return True
            from shared.chat.config import save_config
            endpoint_value = data.get("endpoint")
            endpoint = endpoint_value.strip() or None if isinstance(endpoint_value, str) else None
            save_config(
                provider=provider,
                api_key=api_key,
                model=model,
                endpoint=endpoint,
                temperature=temperature,
            )
            self.send_json({"ok": True})
            return True

        # POST /api/chat/config/test — test connection
        if method == "POST" and self.url_path == "/api/chat/config/test":
            data = self.read_json_body()
            provider = data.get("provider", "").strip() if isinstance(data.get("provider"), str) else ""
            api_key = data.get("api_key", "").strip() if isinstance(data.get("api_key"), str) else ""
            model = data.get("model", "").strip() if isinstance(data.get("model"), str) else ""
            key_required = provider not in self._KEYLESS_PROVIDERS
            if not provider or not model or (key_required and not api_key):
                fields = "provider, model" + (", api_key" if key_required else "")
                self.send_error_json(400, f"{fields} are required")
                return True
            from shared.chat.providers import stream_chat, ChatAPIError
            endpoint_value = data.get("endpoint")
            endpoint = endpoint_value.strip() or None if isinstance(endpoint_value, str) else None
            try:
                messages = [{"role": "user", "content": "Hello, respond with just 'OK'."}]
                tokens = list(stream_chat(
                    provider=provider, api_key=api_key, model=model,
                    messages=messages,
                    endpoint=endpoint,
                    temperature=0.1,
                ))
                response = "".join(tokens)
                self.send_json({"ok": True, "response": response[:200]})
            except ChatAPIError as e:
                self.send_json({"ok": False, "error": str(e), "error_type": e.error_type})
            except Exception as e:
                self.send_json({"ok": False, "error": str(e), "error_type": "unknown"})
            return True

        return False


    def log_message(self, fmt, *args):
        if self.log_silent:
            return
        msg = fmt % args
        if self.log_filter:
            if any(f in msg for f in self.log_filter):
                return
        print(f"[{self.server_name}] {msg}")



class _DualStackHTTPServer(ThreadingHTTPServer):
    """IPv4 + IPv6 dual-stack 서버 (localhost에서 ::1, 127.0.0.1 모두 동작)."""
    address_family = socket.AF_INET6
    allow_reuse_address = True
    daemon_threads = True

    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


class DXServer:
    """서버 생성·시작 래퍼: CLI 파싱, IPv6 듀얼스택, 포트 충돌 해결, 시그널 핸들링."""

    def __init__(self, handler_class, name: str, default_port: int):
        self.handler_class = handler_class
        self.name = name
        self.default_port = default_port
        self._server = None
        self._shutdown_lock = threading.Lock()
        self._shutdown_requested = False

    def start(self):
        """CLI 파싱 → 서버 생성 → 시그널 등록 → serve_forever."""
        args = self._parse_args()
        port = args.port

        self._server = self._create_server(port)
        if self._server is None:
            sys.exit(1)
        # With --port 0 the OS assigns a free port; use the real one everywhere below.
        actual_port = self._server.server_address[1]
        self._report_port()

        self._register_signals()
        self._print_banner(actual_port)

        if not args.no_browser:
            url = f"http://localhost:{actual_port}"
            threading.Timer(1.0, lambda: webbrowser.open(url)).start()

        self._server.serve_forever()

    def create_http_server(self, port: int):
        """Create and store an HTTP server without starting the serve loop."""
        self._server = self._create_server(port)
        self._report_port()
        return self._server

    def _report_port(self):
        """If DX_PORT_FILE is set, atomically write the actual bound port so a parent
        launcher can discover an OS-assigned (--port 0) ephemeral port."""
        pf = os.environ.get("DX_PORT_FILE")
        if not pf or not self._server:
            return
        try:
            actual = self._server.server_address[1]
            tmp = f"{pf}.tmp"
            with open(tmp, "w") as f:
                f.write(str(actual))
            os.replace(tmp, pf)
        except OSError:
            pass

    def register_signals(self):
        """Register shutdown signal handlers for the current server."""
        self._register_signals()

    def print_banner(self, port: int):
        """Print the standard DX server startup banner."""
        self._print_banner(port)

    def _parse_args(self):
        parser = argparse.ArgumentParser(description=f"{self.name} Server")
        parser.add_argument("--port", "-p", type=int, default=self.default_port)
        parser.add_argument("--no-browser", action="store_true",
                            help="브라우저 자동 열기 억제")
        return parser.parse_args()

    def _create_server(self, port: int, max_attempts: int = 5):
        """IPv6 듀얼스택 우선, 실패 시 IPv4 폴백. 포트 충돌 시 재시도."""
        bind_host = _resolve_bind_host()
        if not _is_loopback_host(bind_host) and not _configured_api_token():
            # 원격에 열면서 인증이 없으면 시작하지 않는다 (QA COM-A1). 모듈은 launcher 뒤 loopback 이 기본.
            print(f"  [{self.name}] ERROR: refusing to listen on {bind_host} without DX_API_TOKEN "
                  "(set DX_API_TOKEN, or use the launcher which pairs remote browsers).")
            return None
        for attempt in range(max_attempts):
            # port 0 → OS picks a guaranteed-free port; never force-free / probe it.
            if port != 0 and (self._is_port_open(port) or attempt > 0):
                print(f"  [{self.name}] Port {port} in use — releasing "
                      f"(attempt {attempt + 1}/{max_attempts})...")
                self._force_free_port(port)

            if bind_host:
                try:
                    srv = ThreadingHTTPServer((bind_host, port), self.handler_class)
                    srv.allow_reuse_address = True
                    srv.daemon_threads = True
                    return srv
                except OSError as e:
                    if attempt == max_attempts - 1:
                        print(f"  [{self.name}] ERROR: Cannot bind {bind_host}:{port}: {e}")
                        return None
                    print(f"  [{self.name}] Bind failed ({e}), retrying...")
                    continue

            # IPv6 듀얼스택 시도
            try:
                return _DualStackHTTPServer(("::", port), self.handler_class)
            except OSError:
                pass

            # IPv4 폴백
            try:
                srv = ThreadingHTTPServer(("0.0.0.0", port), self.handler_class)
                srv.allow_reuse_address = True
                srv.daemon_threads = True
                return srv
            except OSError as e:
                if attempt == max_attempts - 1:
                    print(f"  [{self.name}] ERROR: Cannot bind port {port}: {e}")
                    return None
                print(f"  [{self.name}] Bind failed ({e}), retrying...")

        return None

    def _register_signals(self):
        # 신호 처리기는 serve_forever() 가 도는 main thread 에서 불린다. 여기서 바로 shutdown() 을 부르면
        # shutdown() 이 serve_forever() 가 끝나기를 기다리고, serve_forever() 는 이 처리기가 끝나기를
        # 기다려 둘 다 멈춘다 — SIGTERM 을 받은 서버가 살아남아 고아로 쌓였다. dx_monitor 처럼 다른
        # thread 에 맡기면 serve_forever() 가 돌아와 start() 가 끝나고 프로세스가 내려간다.
        def _shutdown(*_):
            print(f"\n  [{self.name}] Shutting down...")
            with self._shutdown_lock:
                if self._shutdown_requested or self._server is None:
                    return
                self._shutdown_requested = True
                threading.Thread(target=self._server.shutdown, name=f"{self.name}-shutdown", daemon=True).start()

        signal.signal(signal.SIGINT, _shutdown)
        signal.signal(signal.SIGTERM, _shutdown)

    def _print_banner(self, port: int):
        url = f"http://localhost:{port}"
        print("╔══════════════════════════════════════════════╗")
        print(f"║  {self.name:<42s}  ║")
        print(f"║  {url:<42s}  ║")
        print("╚══════════════════════════════════════════════╝")

    @staticmethod
    def _is_port_open(port: int) -> bool:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            result = s.connect_ex(("127.0.0.1", port))
            s.close()
            return result == 0
        except Exception:
            return False

    @staticmethod
    def _force_free_port(port: int):
        port = int(port)
        subprocess.run(["fuser", "-k", f"{port}/tcp"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(["fuser", "-k", f"{port}/tcp6"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(1.0)
