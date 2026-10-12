"""Remote access: authentication, Host, Origin and bind address.

Remote use of the board stays possible, but every remote request must authenticate. Local requests pass as before;
a remote browser connects once with the pairing code shown on the board console (session cookie), and API clients
use DX_API_TOKEN. No response may allow every origin.
"""
from __future__ import annotations

import json
import os
import stat
from pathlib import Path
import sys
import threading
import time
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

import pytest

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from shared import remote_access as ra  # noqa: E402
from shared.dx_server import DXBaseHandler, DXServer, _resolve_bind_host  # noqa: E402

REMOTE_IP = "192.168.0.99"
ROOT = Path(__file__).resolve().parents[2]


# ── Host (DNS rebinding) ──────────────────────────────────────────────────────

@pytest.mark.parametrize("host, ok", [
    ("127.0.0.1:8890", True), ("[::1]:8890", True), ("192.168.0.152:8890", True), ("10.1.2.3", True),
    ("localhost:8890", True), ("foo.localhost", True),
    ("evil.example:8890", False), ("192.168.0.152.nip.io", False), ("", False),
])
def test_ip_hosts_and_local_names_are_allowed_other_names_are_not(host, ok):
    assert ra.host_allowed(host, hostname="board") is ok


def test_this_machines_name_and_configured_hosts_are_allowed(monkeypatch):
    assert ra.host_allowed("board:8890", hostname="board")
    assert ra.host_allowed("board.local", hostname="board")
    monkeypatch.setenv("DX_ALLOWED_HOSTS", "studio.lab.example, other")
    assert ra.host_allowed("studio.lab.example:443", hostname="board")
    assert not ra.host_allowed("studio.lab.example.evil", hostname="board")


# ── Pairing code ──────────────────────────────────────────────────────────────

def test_a_pairing_code_works_once_and_then_changes():
    shown = []
    p = ra.Pairing(announce=shown.append)
    code = p.code
    assert len(code) == 6 and code.isdigit() and shown[-1] == code
    assert p.verify(code) == "ok"
    assert p.code != code and shown[-1] == p.code, "성공해도 코드는 1회용"
    assert p.verify(code) == "bad"


def test_five_wrong_codes_lock_and_replace_the_code():
    clock = [1000.0]
    p = ra.Pairing(announce=lambda c: None, now=lambda: clock[0])
    old = p.code
    for _ in range(5):
        assert p.verify("000000" if old != "000000" else "111111") in ("bad", "locked")
    assert p.verify(old) == "locked"
    assert p.code != old, "잠기면 코드를 바꾼다"
    clock[0] += 61
    assert p.verify(p.code) == "ok"


# ── Sessions ──────────────────────────────────────────────────────────────────

def test_sessions_are_stored_as_hashes_in_a_private_file(tmp_path):
    f = tmp_path / "sessions.json"
    s = ra.SessionStore(f, days=30)
    token, sid = s.create(user_agent="UA", ip=REMOTE_IP)
    assert s.valid(token)["id"] == sid
    raw = f.read_text()
    assert token not in raw
    assert stat.S_IMODE(os.stat(f).st_mode) == 0o600
    assert ra.SessionStore(f, days=30).valid(token), "다시 띄워도 기억한다"
    s.revoke(sid)
    assert s.valid(token) is None


def test_sessions_expire(tmp_path):
    clock = [1000.0]
    s = ra.SessionStore(tmp_path / "s.json", days=1, now=lambda: clock[0])
    token, _ = s.create(user_agent="UA", ip=REMOTE_IP)
    clock[0] += 86400 + 1
    assert s.valid(token) is None


# ── bind ──────────────────────────────────────────────────────────────────────

def test_a_module_server_binds_loopback_by_default(monkeypatch):
    for k in ("DX_BIND_LOCAL", "DX_BIND_HOST"):
        monkeypatch.delenv(k, raising=False)
    assert _resolve_bind_host() == "127.0.0.1"
    monkeypatch.setenv("DX_BIND_HOST", "0.0.0.0")
    assert _resolve_bind_host() == "0.0.0.0"


def test_a_module_bound_beyond_loopback_without_a_token_refuses_to_start(monkeypatch):
    monkeypatch.setenv("DX_BIND_HOST", "0.0.0.0")
    monkeypatch.delenv("DX_API_TOKEN", raising=False)
    srv = DXServer(_Probe, "Probe", 0)
    assert srv._create_server(0) is None
    monkeypatch.setenv("DX_API_TOKEN", "t0k3n-xyz")
    httpd = srv._create_server(0)
    assert httpd is not None
    httpd.server_close()


# ── Module server (DXBaseHandler) ────────────────────────────────────────────

class _Probe(DXBaseHandler):
    server_name = "Probe"
    log_silent = True

    def route(self):
        self.send_json({"ok": True, "method": self.command})


@pytest.fixture()
def probe(monkeypatch):
    monkeypatch.delenv("DX_API_TOKEN", raising=False)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Probe)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def _req(url, method="GET", headers=None, data=None):
    r = urllib.request.Request(url, method=method, headers=headers or {},
                               data=(json.dumps(data).encode() if data is not None else None))
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")


def test_no_wildcard_cors_on_any_response(probe):
    code, headers, _ = _req(probe + "/x")
    assert code == 200 and "Access-Control-Allow-Origin" not in headers


def test_preflight_only_for_the_same_origin(probe):
    code, headers, _ = _req(probe + "/x", "OPTIONS", {"Origin": "http://evil.example"})
    assert code == 403 and "Access-Control-Allow-Origin" not in headers
    code, _, _ = _req(probe + "/x", "OPTIONS", {"Origin": probe})
    assert code == 204


def test_an_unknown_host_name_is_refused(probe):
    code, _, _ = _req(probe + "/x", headers={"Host": "evil.example"})
    assert code == 403


def test_a_cross_origin_state_change_is_refused_even_locally(probe):
    code, _, _ = _req(probe + "/x", "POST", {"Origin": "http://evil.example", "Content-Type": "text/plain"}, {})
    assert code == 403
    code, _, _ = _req(probe + "/x", "POST", {"Referer": "http://evil.example/p"}, {})
    assert code == 403
    code, _, _ = _req(probe + "/x", "POST", {"Origin": probe}, {})
    assert code == 200
    code, _, _ = _req(probe + "/x", "POST", {}, {})
    assert code == 200, "Origin 없는 로컬 비브라우저 요청은 그대로"


def test_a_remote_client_needs_the_api_token(probe, monkeypatch):
    monkeypatch.setattr(DXBaseHandler, "_peer_ip", lambda self: REMOTE_IP)
    code, _, _ = _req(probe + "/x")
    assert code == 401
    monkeypatch.setenv("DX_API_TOKEN", "s3cret-token")
    assert _req(probe + "/x", headers={"Authorization": "Bearer s3cret-token"})[0] == 200
    assert _req(probe + "/x", headers={"X-DX-Api-Token": "s3cret-token"})[0] == 200
    assert _req(probe + "/x", headers={"Authorization": "Bearer wrong"})[0] == 401


def test_a_forwarded_request_is_remote_unless_it_carries_the_launcher_secret(probe, monkeypatch):
    monkeypatch.setattr(DXBaseHandler, "_proxy_secret", staticmethod(lambda: "proxy-secret-123"))
    assert _req(probe + "/x", headers={"X-Forwarded-For": REMOTE_IP})[0] == 401
    assert _req(probe + "/x", headers={"X-Forwarded-For": REMOTE_IP, "X-DX-Proxy": "nope"})[0] == 401
    assert _req(probe + "/x", headers={"X-Forwarded-For": REMOTE_IP, "X-DX-Proxy": "proxy-secret-123"})[0] == 200


# ── launcher ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def launcher(tmp_path, monkeypatch):
    monkeypatch.delenv("DX_API_TOKEN", raising=False)
    import launcher.launcher as lmod
    shown = []
    access = ra.RemoteAccess(sessions=ra.SessionStore(tmp_path / "sessions.json", days=30),
                             pairing=ra.Pairing(announce=shown.append))
    monkeypatch.setattr(lmod, "REMOTE_ACCESS", access)
    srv = ThreadingHTTPServer(("127.0.0.1", 0), lmod.LauncherHandler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    yield base, access, shown, lmod.LauncherHandler
    srv.shutdown()
    srv.server_close()


def test_the_board_itself_is_unchanged(launcher):
    base, _, _, _ = launcher
    assert _req(base + "/api/health")[0] == 200


def test_a_remote_browser_sees_only_the_pairing_page(launcher, monkeypatch):
    base, access, _, handler = launcher
    # Another test may drop and re-import shared, leaving two DXBaseHandler classes; patch the one the launcher uses
    monkeypatch.setattr(handler, "_peer_ip", lambda self: REMOTE_IP)
    code, headers, body = _req(base + "/api/health")
    assert code == 401
    code, headers, body = _req(base + "/", headers={"Accept": "text/html"})
    assert code == 401 and "text/html" in headers.get("Content-Type", "")
    assert 'id="dx-pair' in body and access.pairing.code not in body, "코드는 화면에 넣지 않는다"
    assert _req(base + "/api/auth/status")[0] == 200


def test_pairing_gives_a_strict_httponly_cookie_and_then_everything_works(launcher, monkeypatch):
    base, access, _, handler = launcher
    # Another test may drop and re-import shared, leaving two DXBaseHandler classes; patch the one the launcher uses
    monkeypatch.setattr(handler, "_peer_ip", lambda self: REMOTE_IP)
    origin = {"Origin": base}
    code, _, _ = _req(base + "/api/auth/unlock", "POST", {**origin, "Content-Type": "application/json"},
                      {"code": "000000" if access.pairing.code != "000000" else "111111"})
    assert code == 401
    code, headers, body = _req(base + "/api/auth/unlock", "POST", {**origin, "Content-Type": "application/json"},
                               {"code": access.pairing.code})
    assert code == 200, body
    cookie = headers.get("Set-Cookie", "")
    assert cookie.startswith("dx_session=") and "HttpOnly" in cookie and "SameSite=Strict" in cookie
    jar = {"Cookie": cookie.split(";", 1)[0]}
    assert _req(base + "/api/health", headers=jar)[0] == 200
    # A cookie-authenticated request that changes state must carry Origin/Referer (CSRF)
    assert _req(base + "/api/auth/logout", "POST", jar, {})[0] == 403
    assert _req(base + "/api/auth/logout", "POST", {**jar, **origin}, {})[0] in (200, 204)
    assert _req(base + "/api/health", headers=jar)[0] == 401, "로그아웃한 세션은 끝"


def test_sessions_can_be_listed_and_revoked_from_the_board(launcher, monkeypatch):
    base, access, _, _ = launcher
    token, sid = access.sessions.create(user_agent="Laptop", ip=REMOTE_IP)
    code, _, body = _req(base + "/api/auth/sessions")
    assert code == 200 and any(s["id"] == sid for s in json.loads(body)["sessions"])
    assert token not in body
    assert _req(base + "/api/auth/sessions/revoke", "POST", {"Content-Type": "application/json"}, {"id": sid})[0] == 200
    assert access.sessions.valid(token) is None


def test_the_launcher_hands_modules_loopback_and_its_proxy_secret(monkeypatch, tmp_path):
    import launcher.launcher as lmod
    seen = {}

    class _P:
        def __init__(self, cmd, **kw):
            seen.update(kw.get("env") or {})
            self.pid = 1

        def poll(self):
            return None

    monkeypatch.setenv("DX_BIND_HOST", "0.0.0.0")
    monkeypatch.setenv("DX_BIND_LOCAL", "0")
    monkeypatch.setattr(lmod.subprocess, "Popen", _P)
    monkeypatch.setattr(lmod, "_await_reported_port", lambda pf, timeout=20: 1234)
    monkeypatch.setattr(lmod, "_save_pids", lambda: None)
    (tmp_path / "server.py").write_text("")
    lmod.start_sub_server("probe_mod", tmp_path, 0)
    lmod._procs.pop("probe_mod", None)
    assert seen.get("DX_BIND_HOST") == "127.0.0.1"
    assert "DX_BIND_LOCAL" not in seen
    assert seen.get("DX_PROXY_SECRET") and len(seen["DX_PROXY_SECRET"]) >= 32


def test_the_proxy_sends_its_own_secret_and_drops_a_clients_forged_one(monkeypatch):
    import launcher.launcher as lmod
    from http.server import BaseHTTPRequestHandler
    got = {}

    class _T(BaseHTTPRequestHandler):
        def do_GET(self):
            got["proxy"] = self.headers.get_all("X-DX-Proxy")
            got["xff"] = self.headers.get_all("X-Forwarded-For")
            self.send_response(200)
            self.send_header("Content-Length", "2")
            self.end_headers()
            self.wfile.write(b"ok")

        def log_message(self, *a):
            pass

    target = ThreadingHTTPServer(("127.0.0.1", 0), _T)
    threading.Thread(target=target.serve_forever, daemon=True).start()
    monkeypatch.setattr(lmod, "PROXY_SECRET", "the-real-secret-0123456789abcdef")

    class _H:
        command = "GET"
        client_address = ("192.168.0.99", 5555)
        headers = {"x-dx-proxy": "forged", "X-Forwarded-For": "1.2.3.4", "x-forwarded-for": "5.6.7.8",
                   "Host": "board:8890"}

        class rfile:
            @staticmethod
            def read(n):
                return b""

        def __init__(self):
            import io
            self.wfile = io.BytesIO()
            self.sent = []

        def send_response(self, code):
            self.sent.append(code)

        def send_header(self, *a):
            pass

        def end_headers(self):
            pass

    h = _H()
    h.headers = type("Hd", (dict,), {"get": dict.get})(h.headers)
    lmod._proxy(h, target.server_address[1], "/x", inject_widget=False)
    target.shutdown()
    target.server_close()
    assert got["proxy"] == ["the-real-secret-0123456789abcdef"]
    assert got["xff"] == ["192.168.0.99"]


def test_no_server_code_opens_cors_to_every_origin():
    """No server code sends `Access-Control-Allow-Origin: *`."""
    import re
    hits = []
    for f in _REPO.rglob("*.py"):
        rel = f.relative_to(_REPO).as_posix()
        if rel.startswith(("tests/", ".venv/", "var/", "outputs/")) or "/node_modules/" in rel:
            continue
        text = f.read_text(encoding="utf-8", errors="ignore")
        if re.search(r'Access-Control-Allow-Origin["\']\s*,\s*["\']\*', text):
            hits.append(rel)
    assert not hits, hits


def test_a_module_in_the_launchers_own_process_trusts_what_the_launcher_proxies():
    """browser suites run modules in the launcher's process (tests/server_helpers) — the secret the proxy
    sends must be the one those modules read, or every proxied call is a 401."""
    import launcher.launcher as lmod
    from shared.dx_server import DXBaseHandler
    assert os.environ.get("DX_PROXY_SECRET") == lmod.PROXY_SECRET
    assert DXBaseHandler._proxy_secret() == lmod.PROXY_SECRET


# ── Connected browsers screen ─────────────────────────────────────────────────────────────────

def test_the_board_is_told_where_other_computers_connect_but_a_remote_browser_is_not(launcher, monkeypatch):
    base, access, _, handler = launcher
    import launcher.launcher as lmod
    monkeypatch.setattr(lmod, "_lan_addresses", lambda: ["192.168.0.152"])
    st = json.loads(_req(base + "/api/auth/status")[2])
    port = base.rsplit(":", 1)[1]
    assert st["pairing"] is True and st["local"] is True
    assert st["addresses"] == [f"http://192.168.0.152:{port}"]
    assert access.pairing.code not in json.dumps(st), "코드는 콘솔에만"
    token, _ = access.sessions.create(user_agent="Laptop", ip=REMOTE_IP)
    monkeypatch.setattr(handler, "_peer_ip", lambda self: REMOTE_IP)
    st = json.loads(_req(base + "/api/auth/status", headers={"Cookie": f"dx_session={token}"})[2])
    assert st["authenticated"] is True and st["local"] is False and "addresses" not in st


def test_lan_addresses_are_real_ipv4_and_never_loopback():
    import ipaddress
    import launcher.launcher as lmod
    for a in lmod._lan_addresses():
        ip = ipaddress.ip_address(a)
        assert ip.version == 4 and not ip.is_loopback and not ip.is_link_local


def test_the_launcher_page_loads_the_connected_browsers_script_and_its_words():
    import re
    from scripts.js_object_literal import parse_object_after
    html = (ROOT / "launcher" / "static" / "index.html").read_text(encoding="utf-8")
    assert '<script src="/remote-access.js"></script>' in html
    assert 'path == "/remote-access.js"' in (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")
    js = (ROOT / "launcher" / "static" / "remote-access.js").read_text(encoding="utf-8")
    keys = set(re.findall(r"_t\('([^']+)'\)", js))
    assert {"Connected browsers", "Disconnect", "Last active {when}"} <= keys
    words = parse_object_after(html, "window._DX_I18N_DICT =")
    for k in keys:
        assert k in words, f"{k!r} 가 _DX_I18N_DICT 에 없다"
        for lang in ("ko", "ja", "zh-CN", "zh-TW", "es"):
            assert words[k].get(lang), f"{k!r} 에 {lang} 이 없다"
            for slot in re.findall(r"\{\w+\}", k):
                assert slot in words[k][lang], f"{k!r} {lang} 번역이 {slot} 를 잃었다"


def test_a_body_nobody_read_does_not_poison_the_next_request_on_the_connection(launcher):
    """logout does not read its body, so the body must still be drained: a `{}` left on a keep-alive connection
    would prefix the next request line and turn it into a `{}GET` 501 (a remote browser that logs out and reloads
    would see an error instead of the pairing page). 401 and 403 rejections must drain the body too."""
    import http.client
    base, _, _, _ = launcher
    host, port = base.rsplit("//", 1)[1].split(":")
    conn = http.client.HTTPConnection(host, int(port), timeout=5)
    try:
        conn.request("POST", "/api/auth/logout", body=b"{}",
                     headers={"Content-Type": "application/json", "Origin": base})
        r = conn.getresponse()
        r.read()
        assert r.status in (200, 204)
        conn.request("GET", "/api/health")
        r = conn.getresponse()
        r.read()
        assert r.status == 200, r.status
    finally:
        conn.close()


def test_a_remote_browser_sees_only_itself_and_cannot_disconnect_others(launcher, monkeypatch):
    """Listing and disconnecting other browsers is board-only (01_Installation "from the board"). A remote browser
    sees only its own row and disconnects itself with logout."""
    base, access, _, handler = launcher
    mine, my_id = access.sessions.create(user_agent="Laptop", ip=REMOTE_IP)
    _, other_id = access.sessions.create(user_agent="Phone", ip="192.168.0.77")
    monkeypatch.setattr(handler, "_peer_ip", lambda self: REMOTE_IP)
    jar = {"Cookie": f"dx_session={mine}", "Origin": base}
    rows = json.loads(_req(base + "/api/auth/sessions", headers=jar)[2])["sessions"]
    assert [r["id"] for r in rows] == [my_id] and rows[0]["current"] is True
    code, _, _ = _req(base + "/api/auth/sessions/revoke", "POST", {**jar, "Content-Type": "application/json"},
                      {"id": other_id})
    assert code == 403
    assert any(s["id"] == other_id for s in access.sessions.list()), "다른 브라우저는 그대로"
