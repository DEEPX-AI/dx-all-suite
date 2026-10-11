"""Multi-provider LLM API client with SSE streaming.

Supports OpenAI, Anthropic, Google, GitHub Models, and Custom (OpenAI-compatible) endpoints.
Uses only Python standard library (urllib.request, json, ssl).
"""
from __future__ import annotations

import json
import shutil
import socket
import ssl
import subprocess
import threading
import time
import urllib.error
import urllib.request
from typing import Generator
from urllib.parse import urlsplit


class ChatAPIError(Exception):
    """Custom exception for LLM API errors."""

    def __init__(self, error_type: str, message: str, status_code: int = 0):
        self.error_type = error_type
        self.status_code = status_code
        super().__init__(message)




def parse_openai_sse_line(line: str) -> str | None:
    """Parse a single SSE line from OpenAI / OpenAI-compatible APIs.

    Returns:
        None  — stream finished ([DONE])
        ""    — empty delta (keep-alive)
        str   — token text
    """
    if not line.startswith("data: "):
        return ""
    payload = line[len("data: "):]
    if payload.strip() == "[DONE]":
        return None
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError:
        return ""
    delta = obj.get("choices", [{}])[0].get("delta", {})
    return delta.get("content", "")


def parse_anthropic_sse_line(line: str) -> str:
    """Parse a single SSE data line from Anthropic's Messages API."""
    if not line.startswith("data: "):
        return ""
    payload = line[len("data: "):]
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError:
        return ""
    if obj.get("type") == "content_block_delta":
        delta = obj.get("delta", {})
        if delta.get("type") == "text_delta":
            return delta.get("text", "")
    return ""


def parse_google_sse_line(line: str) -> str:
    """Parse a single SSE data line from Google Generative Language API."""
    if not line.startswith("data: "):
        return ""
    payload = line[len("data: "):]
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError:
        return ""
    candidates = obj.get("candidates", [])
    if candidates:
        parts = candidates[0].get("content", {}).get("parts", [])
        if parts:
            return parts[0].get("text", "")
    return ""




def build_openai_request(
    api_key: str,
    model: str,
    messages: list[dict],
    endpoint: str | None = None,
    temperature: float = 0.7,
) -> dict:
    """Build an HTTP request dict for OpenAI chat completions."""
    url = endpoint or "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "stream": True,
    })
    return {"url": url, "headers": headers, "body": body}


def build_anthropic_request(
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
) -> dict:
    """Build an HTTP request dict for Anthropic Messages API."""
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    system_text = None
    filtered: list[dict] = []
    for msg in messages:
        if msg.get("role") == "system":
            system_text = msg.get("content", "")
        else:
            filtered.append(msg)

    body_dict: dict = {
        "model": model,
        "messages": filtered,
        "temperature": temperature,
        "max_tokens": 4096,
        "stream": True,
    }
    if system_text is not None:
        body_dict["system"] = system_text

    return {"url": url, "headers": headers, "body": json.dumps(body_dict)}


def build_google_request(
    api_key: str,
    model: str,
    messages: list[dict],
    temperature: float = 0.7,
) -> dict:
    """Build an HTTP request dict for Google Generative Language API."""
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}"
        f":streamGenerateContent?alt=sse&key={api_key}"
    )
    headers = {"Content-Type": "application/json"}

    system_instruction = None
    contents: list[dict] = []

    for msg in messages:
        role = msg.get("role", "")
        text = msg.get("content", "")
        if role == "system":
            system_instruction = {"parts": [{"text": text}]}
        else:
            mapped_role = "model" if role == "assistant" else role
            contents.append({
                "role": mapped_role,
                "parts": [{"text": text}],
            })

    body_dict: dict = {
        "contents": contents,
        "generationConfig": {"temperature": temperature},
    }
    if system_instruction is not None:
        body_dict["systemInstruction"] = system_instruction

    return {"url": url, "headers": headers, "body": json.dumps(body_dict)}



_DEFAULT_LOCAL_BASE = "http://localhost:11434"  # Ollama default; user-overridable


def _local_base_root(base: str | None) -> str:
    """Normalize a user-entered local endpoint to its root (strip API suffixes)."""
    b = (base or _DEFAULT_LOCAL_BASE).strip().rstrip("/")
    for suffix in ("/v1/chat/completions", "/chat/completions", "/v1"):
        if b.endswith(suffix):
            b = b[: -len(suffix)]
            break
    return b.rstrip("/") or _DEFAULT_LOCAL_BASE


def local_chat_url(base: str | None) -> str:
    """Full OpenAI-compatible chat-completions URL for a local runtime base URL."""
    return _local_base_root(base) + "/v1/chat/completions"


def discover_local_models(base: str | None) -> list[str]:
    """List models from a local runtime. Tries OpenAI ``/v1/models`` then Ollama ``/api/tags``.

    Returns [] if neither is reachable (runtime-agnostic; no API key assumed).
    """
    root = _local_base_root(base)
    try:
        req = urllib.request.Request(root + "/v1/models")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        ids = [m.get("id") for m in data.get("data", []) if isinstance(m, dict) and m.get("id")]
        if ids:
            return ids
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        pass
    try:
        req = urllib.request.Request(root + "/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        return [m.get("name") for m in data.get("models", []) if isinstance(m, dict) and m.get("name")]
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return []


# CLI-backed provider — route chat through an authenticated coding-agent CLI
# (one CLI login powers both the chatbot and dx_agent_dev). No API key needed.

# agent -> (binary name, argv-tail builder(prompt, model, effort)). Self-contained
# (no dependency on dx_agent_dev) to respect the shared-infra layering.
# Model-flag per agent mirrors dx_agent_dev's adapters so a picked model actually applies:
#   claude/cursor/copilot → --model, opencode/codex → -m. "auto" is a studio sentinel
#   ("let the CLI decide"), NOT a real id — omit the flag for it (copilot rejects --model auto).
def _model_flag(flag, m):
    return [flag, m] if (m and m != "auto") else []

_AGENT_CHAT = {
    "claude": ("claude", lambda p, m, e: ["-p", p]
               + _model_flag("--model", m) + (["--effort", e] if e else [])),
    "opencode": ("opencode", lambda p, m, e: ["run", p] + _model_flag("-m", m)),
    "copilot": ("copilot", lambda p, m, e: ["-p", p] + _model_flag("--model", m)),
    "cursor": ("cursor-agent", lambda p, m, e: ["-p", p] + _model_flag("--model", m)),
    "codex": ("codex", lambda p, m, e: ["exec", p] + _model_flag("-m", m)),
}

# Preference order when the configured chat agent's CLI is absent (mirrors dx_agent_dev's
# _DEGRADED_AGENT_ORDER) — the chatbot falls back to the first installed coding-agent CLI.
_AGENT_CHAT_FALLBACK_ORDER = ["claude", "copilot", "cursor", "codex", "opencode"]


def _flatten_prompt(messages: list[dict]) -> str:
    """Collapse a chat message list into a single prompt string for a CLI agent."""
    parts: list[str] = []
    for msg in messages:
        role = msg.get("role", "")
        content = msg.get("content", "")
        if not content:
            continue
        if role == "system":
            parts.append(content)
        elif role == "assistant":
            parts.append("Assistant: " + content)
        else:
            parts.append("User: " + content)
    return "\n\n".join(parts)


# How often to emit a keepalive token while the CLI subprocess runs silently.
# Mirrors dx_agent_dev/core/agent_runner.py's KEEPALIVE_SEC=15 pattern.
_KEEPALIVE_SEC = 15


def stream_agent_cli(
    agent: str,
    model: str | None,
    messages: list[dict],
    effort: str | None = None,
    timeout: int = 180,
) -> Generator[str, None, None]:
    """Run an authenticated coding-agent CLI as a chat backend; yield its answer text.

    Uses Popen (instead of a single blocking subprocess.run) so a keepalive
    token ("") can be yielded roughly every _KEEPALIVE_SEC while the CLI is
    still generating — the SSE connection stays alive during long runs. The
    final yielded answer text, error handling, and 180s timeout enforcement
    are unchanged: stdout is still captured in full (via communicate() in a
    background thread, same as capture_output=True) and only yielded once,
    stripped, at the end.
    """
    spec = _AGENT_CHAT.get(agent)
    if spec is None:
        raise ChatAPIError("unknown_agent", f"Unknown agent: {agent}")
    bin_name, build_tail = spec
    cli = shutil.which(bin_name)
    if not cli:
        # The configured chat agent's CLI isn't installed on this box (e.g. the deployment has
        # copilot but not claude). Fall back to the first available coding-agent CLI so the
        # chatbot still answers, instead of erroring out. Drop the model (it belonged to the
        # requested agent and won't be valid for a different CLI).
        for alt in _AGENT_CHAT_FALLBACK_ORDER:
            if alt == agent:
                continue
            alt_bin, alt_build = _AGENT_CHAT[alt]
            alt_cli = shutil.which(alt_bin)
            if alt_cli:
                agent, bin_name, build_tail, cli, model = alt, alt_bin, alt_build, alt_cli, None
                break
    if not cli:
        raise ChatAPIError("cli_missing", "No coding-agent CLI found on PATH (claude/copilot/cursor/codex/opencode)")
    prompt = _flatten_prompt(messages)
    cmd = [cli] + build_tail(prompt, model, effort)
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    except OSError as exc:
        raise ChatAPIError("api_error", f"launch failed: {exc}") from exc

    # communicate() drains stdout/stderr in a worker thread while the main
    # generator waits below — draining is required to avoid deadlocking on
    # a full pipe buffer (a plain proc.wait() would not read the pipes).
    result: dict = {}

    def _communicate():
        try:
            out, err = proc.communicate()
            result["stdout"] = out
            result["stderr"] = err
        except Exception as exc:  # surfaced as api_error below
            result["exc"] = exc

    worker = threading.Thread(target=_communicate, name="agent-cli-chat", daemon=True)
    worker.start()

    deadline = time.monotonic() + timeout
    timed_out = False
    while worker.is_alive():
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            timed_out = True
            break
        worker.join(timeout=min(remaining, _KEEPALIVE_SEC))
        if worker.is_alive():
            yield ""  # keepalive — empty token, appends nothing on the client

    if timed_out:
        proc.kill()
        worker.join(timeout=5)
        raise ChatAPIError("timeout", "Agent CLI timed out")

    if "exc" in result:
        raise ChatAPIError("api_error", f"launch failed: {result['exc']}") from result["exc"]

    if proc.returncode != 0:
        detail = (result.get("stderr") or result.get("stdout") or "agent CLI failed").strip()
        raise ChatAPIError("api_error", detail[:300], proc.returncode)
    out = (result.get("stdout") or "").strip()
    if out:
        yield out




# 연결 (TCP · TLS · 응답 header) 은 이 안에 끝나야 한다. 방화벽이 막은 host (이 망의 api.openai.com) 를 120 s 기다리던
# 것을 끊는다. 연결된 뒤 token 사이는 read timeout 으로 기다린다 (2026-10-11).
_CONNECT_TIMEOUT = 15.0


def _error_reason(body: bytes) -> str:
    """The provider's own reason from an error body. OpenAI, Anthropic and Google all send {"error": {"message": …}}."""
    try:
        obj = json.loads(body.decode("utf-8", errors="replace"))
    except (ValueError, AttributeError):
        text = body.decode("utf-8", errors="replace").strip() if isinstance(body, bytes) else ""
        return text[:200]
    if isinstance(obj, list) and obj:          # Google sometimes wraps the error in a list
        obj = obj[0]
    if not isinstance(obj, dict):
        return ""
    err = obj.get("error")
    if isinstance(err, dict):
        return str(err.get("message") or err.get("type") or "")[:300]
    if isinstance(err, str):
        return err[:300]
    return str(obj.get("message") or "")[:300]


def _unreachable(host: str, exc: BaseException) -> ChatAPIError:
    reason = getattr(exc, "reason", exc)
    if isinstance(reason, socket.gaierror):
        why = "the name could not be resolved (DNS)"
    elif isinstance(reason, ConnectionRefusedError):
        why = "the connection was refused"
    elif isinstance(reason, (TimeoutError, socket.timeout)):
        why = f"no answer within {int(_CONNECT_TIMEOUT)} s — a firewall or proxy may be blocking it"
    else:
        why = str(reason)
    return ChatAPIError("unreachable", f"Could not reach {host}: {why}", 0)


def _http_stream(
    url: str,
    headers: dict,
    body: str,
    timeout: int = 120,
) -> Generator[str, None, None]:
    """Open an HTTP connection and yield raw SSE lines."""
    req = urllib.request.Request(
        url,
        data=body.encode("utf-8"),
        headers=headers,
        method="POST",
    )
    host = urlsplit(url).hostname or url
    ctx = ssl.create_default_context()
    try:
        resp = urllib.request.urlopen(req, timeout=_CONNECT_TIMEOUT, context=ctx)
    except urllib.error.HTTPError as exc:
        status = exc.code
        try:
            reason = _error_reason(exc.read(4096))
        except Exception:
            reason = ""
        detail = f"HTTP {status}" + (f": {reason}" if reason else "")
        if status == 401:
            raise ChatAPIError("invalid_api_key", detail, 401) from exc
        if status == 429:
            raise ChatAPIError("rate_limit", detail, 429) from exc
        raise ChatAPIError("api_error", detail, status) from exc
    except (TimeoutError, socket.timeout, urllib.error.URLError, OSError) as exc:
        raise _unreachable(host, exc) from exc

    # 연결됐다 — 이제 token 사이의 간격은 read timeout 으로 기다린다.
    try:
        resp.fp.raw._sock.settimeout(timeout)
    except AttributeError:
        pass
    try:
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").rstrip("\n\r")
            if line:
                yield line
    except (TimeoutError, socket.timeout) as exc:
        raise ChatAPIError("timeout", f"{host} stopped answering for {timeout} s", 0) from exc
    finally:
        resp.close()


def _stream_error(line: str) -> str | None:
    """An error the provider sends inside a 200 stream: Anthropic `{"type": "error", …}`, OpenAI `{"error": …}`."""
    if not line.startswith("data: "):
        return None
    payload = line[len("data: "):]
    if '"error"' not in payload:
        return None
    try:
        obj = json.loads(payload)
    except json.JSONDecodeError:
        return None
    if not isinstance(obj, dict) or not (obj.get("type") == "error" or "error" in obj):
        return None
    return _error_reason(payload.encode("utf-8")) or "stream error"



# GitHub Models uses Azure AI Inference at this fixed endpoint (OpenAI-compatible)
_GITHUB_MODELS_ENDPOINT = "https://models.inference.ai.azure.com/chat/completions"

_PARSERS = {
    "openai": parse_openai_sse_line,
    "github": parse_openai_sse_line,
    "custom": parse_openai_sse_line,
    "local": parse_openai_sse_line,
    "anthropic": parse_anthropic_sse_line,
    "google": parse_google_sse_line,
}

_BUILDERS = {
    "openai": lambda ak, m, msgs, ep, t: build_openai_request(ak, m, msgs, temperature=t),
    "github": lambda ak, m, msgs, ep, t: build_openai_request(ak, m, msgs, endpoint=_GITHUB_MODELS_ENDPOINT, temperature=t),
    "custom": lambda ak, m, msgs, ep, t: build_openai_request(ak, m, msgs, endpoint=ep, temperature=t),
    # Local / self-hosted: OpenAI-compatible at a user base URL; no API key required.
    "local": lambda ak, m, msgs, ep, t: build_openai_request(ak or "local", m, msgs, endpoint=local_chat_url(ep), temperature=t),
    "anthropic": lambda ak, m, msgs, ep, t: build_anthropic_request(ak, m, msgs, temperature=t),
    "google": lambda ak, m, msgs, ep, t: build_google_request(ak, m, msgs, temperature=t),
}


def stream_chat(
    provider: str,
    api_key: str,
    model: str,
    messages: list[dict],
    endpoint: str | None = None,
    temperature: float = 0.7,
) -> Generator[str, None, None]:
    """Stream chat tokens from the specified LLM provider.

    Yields non-empty token strings.
    """
    # CLI-backed provider: model field carries "<agent>::<model>" (e.g. "claude::claude-opus-5").
    # The sub-model is optional — bare "<agent>" runs the agent's own default model.
    if provider == "agent-cli":
        agent_name, _sep, sub_model = (model or "").partition("::")
        yield from stream_agent_cli(agent_name or model, sub_model or None, messages, effort=None)
        return

    if provider not in _BUILDERS:
        raise ValueError(f"Unknown provider: {provider}")

    req = _BUILDERS[provider](api_key, model, messages, endpoint, temperature)
    parser = _PARSERS[provider]

    for line in _http_stream(req["url"], req["headers"], req["body"]):
        failed = _stream_error(line)
        if failed:
            raise ChatAPIError("api_error", failed, 0)
        token = parser(line)
        if token is None:
            return
        if token:
            yield token
