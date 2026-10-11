"""Chat says why an external API failed (2026-10-11, checked against the real Anthropic API with a fake key).

api.anthropic.com answered 401 `{"type":"error","error":{"type":"authentication_error","message":"invalid x-api-key"}}`.
Chat replaced it with the offline fallback "No AI model connected — set an API key", which is wrong for a user who set
a key. Other statuses showed only "HTTP 400" and dropped the provider's reason. On this network api.openai.com and
generativelanguage.googleapis.com time out; the user waited 120 s for "Request timed out", with no host named. An
error event in the middle of a stream ended the answer quietly.

The bodies below copy each provider's real error shape.
"""
from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from shared.chat import providers as P

ANTHROPIC_401 = {"type": "error", "error": {"type": "authentication_error", "message": "invalid x-api-key"},
                 "request_id": "req_x"}
OPENAI_400 = {"error": {"message": "Unsupported value: 'temperature' does not support 0.7 with this model.",
                        "type": "invalid_request_error", "param": "temperature", "code": "unsupported_value"}}
GOOGLE_404 = {"error": {"code": 404, "message": "models/gemini-9 is not found for API version v1beta",
                        "status": "NOT_FOUND"}}
ANTHROPIC_STREAM_ERROR = (
    'event: message_start\ndata: {"type":"message_start","message":{"id":"m"}}\n\n'
    'event: content_block_delta\ndata: {"type":"content_block_delta","index":0,'
    '"delta":{"type":"text_delta","text":"Hel"}}\n\n'
    'event: error\ndata: {"type":"error","error":{"type":"overloaded_error","message":"Overloaded"}}\n\n')
OPENAI_STREAM_ERROR = ('data: {"choices":[{"delta":{"content":"Hel"}}]}\n\n'
                       'data: {"error":{"message":"The server had an error while processing your request."}}\n\n')

ROUTES = {
    "/anthropic-401": (401, "application/json", json.dumps(ANTHROPIC_401)),
    "/openai-400": (400, "application/json", json.dumps(OPENAI_400)),
    "/google-404": (404, "application/json", json.dumps(GOOGLE_404)),
    "/anthropic-stream-error": (200, "text/event-stream", ANTHROPIC_STREAM_ERROR),
    "/openai-stream-error": (200, "text/event-stream", OPENAI_STREAM_ERROR),
}


class _Fake(BaseHTTPRequestHandler):
    def do_POST(self):  # noqa: N802
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        status, ctype, body = ROUTES[self.path]
        data = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


@pytest.fixture(scope="module")
def base():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Fake)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def _point(monkeypatch, provider, url):
    real = P._BUILDERS[provider]

    def build(ak, m, msgs, ep, t):
        req = real(ak, m, msgs, ep, t)
        req["url"] = url
        return req
    monkeypatch.setitem(P._BUILDERS, provider, build)


def _run(provider, model="m"):
    return list(P.stream_chat(provider, "k", model, [{"role": "user", "content": "hi"}]))


@pytest.mark.parametrize(("provider", "path", "etype", "reason"), [
    ("anthropic", "/anthropic-401", "invalid_api_key", "invalid x-api-key"),
    ("openai", "/openai-400", "api_error", "Unsupported value: 'temperature'"),
    ("google", "/google-404", "api_error", "models/gemini-9 is not found"),
])
def test_the_providers_reason_is_kept(base, monkeypatch, provider, path, etype, reason):
    _point(monkeypatch, provider, base + path)
    with pytest.raises(P.ChatAPIError) as err:
        _run(provider)
    assert err.value.error_type == etype
    assert reason in str(err.value)
    assert str(err.value.status_code) in str(err.value)


@pytest.mark.parametrize(("provider", "path", "reason"), [
    ("anthropic", "/anthropic-stream-error", "Overloaded"),
    ("openai", "/openai-stream-error", "The server had an error"),
])
def test_an_error_in_the_stream_is_raised_not_swallowed(base, monkeypatch, provider, path, reason):
    _point(monkeypatch, provider, base + path)
    got = []
    with pytest.raises(P.ChatAPIError) as err:
        for tok in P.stream_chat(provider, "k", "m", [{"role": "user", "content": "hi"}]):
            got.append(tok)
    assert got == ["Hel"]
    assert reason in str(err.value)


def test_an_unknown_host_is_named_at_once(monkeypatch):
    _point(monkeypatch, "openai", "https://no-such-host.invalid/v1/chat/completions")
    t0 = time.time()
    with pytest.raises(P.ChatAPIError) as err:
        _run("openai")
    assert err.value.error_type == "unreachable"
    assert "no-such-host.invalid" in str(err.value)
    assert time.time() - t0 < 10


def test_a_blocked_host_gives_up_after_the_connect_timeout(monkeypatch):
    monkeypatch.setattr(P, "_CONNECT_TIMEOUT", 1.0)
    # 10.255.255.1 is not routed: the TCP connect hangs, as api.openai.com does behind this firewall.
    _point(monkeypatch, "openai", "http://10.255.255.1:81/v1/chat/completions")
    t0 = time.time()
    with pytest.raises(P.ChatAPIError) as err:
        _run("openai")
    assert err.value.error_type == "unreachable"
    assert "10.255.255.1" in str(err.value)
    assert time.time() - t0 < 5


@pytest.mark.parametrize(("etype", "status", "detail", "lang", "must"), [
    ("invalid_api_key", 401, "invalid x-api-key", "en", "rejected the API key"),
    ("invalid_api_key", 401, "invalid x-api-key", "ko", "API key"),
    ("rate_limit", 429, "quota", "en", "limit"),
    ("unreachable", 0, "Could not reach api.openai.com", "en", "api.openai.com"),
    ("api_error", 400, "model not found", "ja", "model not found"),
])
def test_chat_says_what_failed_instead_of_no_model_connected(monkeypatch, etype, status, detail, lang, must):
    # Other suites reload shared.chat; patch the engine module this test actually uses, and raise its ChatAPIError.
    import importlib
    E = importlib.import_module("shared.chat.engine")
    engine = E.ChatEngine(app_name="dx_app")
    monkeypatch.setattr(E, "load_config", lambda: {"provider": "anthropic", "api_key": "k", "model": "claude-x"})

    def boom(**_kw):
        raise E.ChatAPIError(etype, detail, status)
        yield  # pragma: no cover

    monkeypatch.setattr(E, "stream_chat", boom)
    text = "".join(engine.stream("How do I run yolov8n?", lang=lang))
    assert "No AI model connected" not in text
    assert must in text
    assert "anthropic" in text.lower()
    assert "⚙" in text


def test_the_hint_does_not_point_at_the_removed_test_button():
    """The settings lost their Test button (saving tests the connection, 2026-10-11 redesign); the hint named it."""
    import importlib
    E = importlib.import_module("shared.chat.engine")
    for lang, text in E.ChatEngine._API_ERROR_HINT.items():
        assert "**Test**" not in text and "Test" not in text, (lang, text)
