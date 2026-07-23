"""어댑터 베이스: AgentAdapter(ABC) + SubprocessAdapter 공통 구동."""
from __future__ import annotations

import json
import os
import re
import shutil
import signal
import subprocess
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterator, Optional

from dx_agent_dev.core.message_sanitize import is_harness_status_line, sanitize_assistant_text

# cursor-agent 재연결·내부 상태 줄 → status 슬롯(채팅 말풍선 X)
_STATUS_LINE = re.compile(
    r"(?i)^(connection lost|reconnecting|retry(\s+attempt|\s+\d+)?|\[DX-AGENT)",
)
# 도구/셸 출력 휴리스틱(plain text 폴백)
_COMMAND_LINE = re.compile(
    r"^(?:\$ |\+ |✅\s*\*\*|(?:Read|Write|Bash|Edit|Glob|Grep|Task|Shell)\b)",
)


class AgentAdapter(ABC):
    @abstractmethod
    def is_available(self) -> bool: ...
    @abstractmethod
    def run(self, prompt: str, session_dir: Path, harness_dirs: list) -> Iterator[dict]: ...
    @abstractmethod
    def cancel(self) -> None: ...


class SubprocessAdapter(AgentAdapter):
    """CLI subprocess 공통 구동. 서브클래스는 cli_bin·build_command·normalize만 정의.

    - cwd_mode="session"(기본): cwd=session_dir, 쓰기 격리(--add-dir 도구).
    - cwd_mode="harness": cwd=harness_dirs[0](없으면 session_dir), 하니스 컨텍스트(-C/cwd 도구).
      ⚠️ harness 모드는 쓰기가 하니스 루트에 발생 → 격리와 양립 불가(일반망 검증, spec §6/§11 #4).
    """
    cli_bin = None
    cwd_mode = "session"
    # 인증 상태 감지용(선택): 서브클래스가 홈 기준 상대 경로 + (선택)JSON 키를 선언하면
    # is_authenticated()가 값싼 파일 검사로 True/False를 판정. 미선언 시 None(unknown).
    creds_relpath: tuple | None = None   # 예: (".claude", ".credentials.json")
    creds_key: str | None = None          # 예: "claudeAiOauth"; None이면 파일 존재만 확인
    # in-UI 로그인 안내: 사용자가 터미널에서 실행할 로그인 명령(브라우저 OAuth는 결국 브라우저 필요).
    login_cmd_hint: str | None = None

    def __init__(self, cli_path: str = None, model: str = None, effort: str = None):
        self._cli = cli_path or (shutil.which(self.cli_bin) if self.cli_bin else None)
        self.model = model
        self.effort = effort  # reasoning effort(지원 어댑터만 build_command에서 사용)
        self.name = None  # make_adapter가 주입(레지스트리 키)
        self._proc = None

    def is_available(self) -> bool:
        return bool(self._cli)

    def is_authenticated(self):
        """로그인 여부. True/False(확정) 또는 None(unknown, 값싼 판정 불가).

        거짓 음성(실제 로그인 상태인데 False)을 피하기 위해 확신 없으면 None을 반환한다.
        creds_relpath를 선언한 서브클래스는 홈 기준 파일(+선택 JSON 키)로 판정한다.
        """
        if not self.creds_relpath:
            return None
        path = Path.home().joinpath(*self.creds_relpath)
        try:
            if not path.is_file():
                return False
            if self.creds_key is None:
                return True
            return bool(json.loads(path.read_text(encoding="utf-8")).get(self.creds_key))
        except (ValueError, OSError):
            return None

    def list_models(self):
        """동적 모델 목록(CLI 조회). 지원 어댑터만 override; 기본은 None(정적 폴백)."""
        return None

    def build_command(self, prompt, session_dir, harness_dirs, run_ctx=None) -> list:
        raise NotImplementedError

    def normalize(self, line: str) -> dict:
        """기본 텍스트 휴리스틱. 구조화 출력 도구는 오버라이드."""
        return classify_plain_line(line)

    def _resolve_cwd(self, session_dir, harness_dirs):
        if self.cwd_mode == "harness" and harness_dirs:
            return harness_dirs[0]
        return session_dir

    def _apply_cli_resume(self, cmd: list, run_ctx) -> list:
        if not run_ctx or not getattr(run_ctx, "is_followup", False):
            return cmd
        if not getattr(run_ctx, "supports_cli_resume", True):
            return cmd
        sid = getattr(run_ctx, "cli_session_id", None)
        if sid:
            return cmd + ["--resume", sid]
        return cmd + ["--continue"]

    def run(self, prompt, session_dir, harness_dirs, run_ctx=None):
        if not self.is_available():
            yield {"type": "error", "text": f"{self.cli_bin} CLI not found"}
            return
        cmd = self.build_command(prompt, session_dir, harness_dirs, run_ctx=run_ctx)
        cwd = self._resolve_cwd(session_dir, harness_dirs)
        try:
            self._proc = subprocess.Popen(
                cmd, cwd=str(cwd),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, start_new_session=True,
            )
        except OSError as e:
            yield {"type": "error", "text": f"launch failed: {e}"}
            return
        try:
            for line in self._proc.stdout:
                line = line.rstrip("\n")
                if line:
                    yield self.normalize(line)
        finally:
            code = self._wait_quietly()
        done = {"type": "done", "text": "ok", "session_dir": str(session_dir)}
        if code != 0:
            yield {"type": "error", "text": f"exit {code}"}
        yield done

    def _kill_group(self, sig):
        if not self._proc:
            return
        try:
            os.killpg(os.getpgid(self._proc.pid), sig)
        except (ProcessLookupError, OSError):
            pass

    def _wait_quietly(self) -> int:
        try:
            return self._proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self._kill_group(signal.SIGTERM)
            try:
                return self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._kill_group(signal.SIGKILL)
                try:
                    return self._proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    return -1

    def cancel(self):
        if self._proc and self._proc.poll() is None:
            self._kill_group(signal.SIGTERM)
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._kill_group(signal.SIGKILL)
            except OSError:
                pass


def _hidden_status(text: str = "") -> dict:
    return {"type": "status", "text": text, "hidden": True}


def _message_event(text: str, *, sanitize: bool = False, **extra) -> dict:
    """User-facing assistant text; harness strip only on complete/final payloads."""
    clean = sanitize_assistant_text(text) if sanitize else text
    if not (clean or "").strip():
        return _hidden_status()
    ev = {"type": "message", "text": clean}
    ev.update(extra)
    return ev


def classify_plain_line(line: str) -> dict:
    """비 JSON stdout 한 줄 → AgentEvent (재연결 로그·도구 출력 분류)."""
    stripped = (line or "").strip()
    if not stripped:
        return _hidden_status()
    if is_harness_status_line(line):
        return _hidden_status()
    if _STATUS_LINE.search(stripped):
        return {"type": "status", "text": stripped}
    if _COMMAND_LINE.search(stripped) or stripped.startswith("$") or stripped.startswith("+ "):
        return {"type": "command", "text": line}
    return {"type": "message", "text": line}


def _extract_text_from_content(content) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for block in content:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict):
            btype = block.get("type") or ""
            if btype == "text" and block.get("text"):
                parts.append(str(block["text"]))
            elif block.get("text"):
                parts.append(str(block["text"]))
            elif btype == "tool_use":
                parts.append(f"[tool:{block.get('name', 'tool')}]")
    return "\n".join(p for p in parts if p)


def _extract_message_text(obj: dict) -> str:
    """cursor/claude/codex stream-json·result 공통 텍스트 추출."""
    for key in ("result", "text", "output"):
        val = obj.get(key)
        if isinstance(val, str) and val.strip():
            return val
    msg = obj.get("message")
    if isinstance(msg, str) and msg.strip():
        return msg
    if isinstance(msg, dict):
        text = _extract_text_from_content(msg.get("content"))
        if text.strip():
            return text
    text = _extract_text_from_content(obj.get("content"))
    if text.strip():
        return text
    delta = obj.get("delta")
    if isinstance(delta, dict):
        for key in ("text", "text_delta", "content"):
            val = delta.get(key)
            if isinstance(val, str) and val:
                return val
    return ""


def _format_tool_line(obj: dict, *, completed: bool) -> str:
    tc = obj.get("tool_call") if isinstance(obj.get("tool_call"), dict) else obj
    if not isinstance(tc, dict):
        return str(tc)
    for key in tc:
        inner = tc.get(key)
        if isinstance(inner, dict):
            name = inner.get("name") or key
            args = inner.get("args") or inner.get("arguments") or ""
            prefix = "✓" if completed else "→"
            if args:
                return f"{prefix} {name}: {args}"[:500]
            return f"{prefix} {name}"
    name = tc.get("name") or tc.get("tool_name") or "tool"
    return f"{'✓' if completed else '→'} {name}"


def _dig(obj, *keys):
    cur = obj
    for key in keys:
        if not isinstance(cur, dict):
            return None
        cur = cur.get(key)
    return cur


def _extract_stream_event_text(obj: dict) -> str:
    """Claude stream_event / nested content_block_delta → token text."""
    event = obj.get("event")
    if not isinstance(event, dict):
        return ""
    delta = event.get("delta")
    if isinstance(delta, dict):
        dtype = delta.get("type") or ""
        if dtype in ("text_delta", "input_json_delta"):
            text = delta.get("text") or delta.get("partial_json") or ""
            if isinstance(text, str) and text:
                return text
        text = delta.get("text") or delta.get("text_delta") or ""
        if isinstance(text, str) and text:
            return text
    if event.get("type") in ("content_block_delta", "text_delta"):
        return _extract_message_text(event)
    return ""


def _extract_assistant_blocks(message: dict, *, include_tools: bool) -> str:
    """Pull visible text (and optional tool hints) from assistant message.content."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if not isinstance(content, list):
        return _extract_text_from_content(content)
    parts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type") or ""
        if btype == "text" and block.get("text"):
            parts.append(str(block["text"]))
        elif include_tools and btype == "tool_use":
            name = block.get("name") or "tool"
            args = block.get("input") or block.get("arguments") or ""
            if isinstance(args, dict):
                args = json.dumps(args, ensure_ascii=False)[:200]
            parts.append(f"→ {name}: {args}" if args else f"→ {name}")
    return "\n".join(p for p in parts if p)


def _map_codex_item(obj: dict) -> Optional[dict]:
    """Codex exec --json NDJSON (thread/turn/item.*)."""
    kind = obj.get("type") or ""
    if kind == "thread.started":
        model = obj.get("model") or _dig(obj, "thread", "model") or "Codex"
        return {"type": "status", "text": f"Session started ({model})"}
    if kind == "turn.started":
        return _hidden_status()
    if kind == "item.completed":
        item = obj.get("item") if isinstance(obj.get("item"), dict) else {}
        item_type = str(item.get("type") or "")
        if item_type == "agent_message":
            text = _extract_message_text(item)
            if text:
                return _message_event(text, delta=True, sanitize=False)
            return _hidden_status()
        if item_type == "command_execution":
            cmd = item.get("command") or ""
            if cmd:
                return {"type": "command", "text": f"$ {cmd}"[:500]}
            return {"type": "command", "text": _format_tool_line(item, completed=True)}
        if item_type == "file_change":
            path = item.get("path") or item.get("filename") or "file"
            action = item.get("kind") or item.get("action") or "update"
            return {"type": "command", "text": f"✓ {action}: {path}"[:500]}
        tool = _format_tool_line(item, completed=True)
        if tool and tool != "✓ tool":
            return {"type": "command", "text": tool}
        return _hidden_status()
    if kind == "turn.completed":
        return _hidden_status()
    if kind == "error":
        err = obj.get("message") or _extract_message_text(obj) or "Codex error"
        return {"type": "error", "text": str(err)}
    return None


def _map_json_event(obj, raw):
    """JSON NDJSON → AgentEvent (cursor/claude/codex stream-json·result).

    upstream `.deepx/tools/dx_transcripts/parse_*_session.py` 스키마를 UI 슬롯에 맞게 축약.
    """
    if not isinstance(obj, dict):
        return classify_plain_line(raw)

    kind = obj.get("type") or ""
    subtype = obj.get("subtype") or ""

    codex_ev = _map_codex_item(obj)
    if codex_ev is not None:
        return codex_ev

    if kind == "user":
        msg = obj.get("message")
        if isinstance(msg, dict):
            tool_text = _extract_assistant_blocks(msg, include_tools=False)
            if tool_text and any(
                isinstance(b, dict) and b.get("type") == "tool_result"
                for b in (msg.get("content") or [])
            ):
                return {"type": "log", "text": tool_text[:2000]}
        return _hidden_status()

    if kind == "stream_event":
        text = _extract_stream_event_text(obj)
        if text:
            return _message_event(text, delta=True, sanitize=False)
        return _hidden_status()

    if kind in ("message_delta", "content_block_start", "content_block_stop", "message_start", "message_stop"):
        if kind == "message_delta":
            text = _extract_message_text(obj)
            if text:
                return _message_event(text, delta=True, sanitize=False)
        return _hidden_status()

    if kind == "rate_limit_event":
        info = obj.get("rate_limit_info") or {}
        retry = info.get("retry_after_ms")
        if retry:
            return {"type": "status", "text": f"Rate limited — retry in {retry / 1000:.0f}s"}
        return {"type": "status", "text": "Rate limited — waiting"}

    if kind == "system":
        if subtype == "init":
            model = obj.get("model") or "agent"
            sid = obj.get("session_id") or obj.get("sessionId") or ""
            return {
                "type": "session",
                "cli_session_id": str(sid) if sid else "",
                "status_text": f"Session started ({model})",
            }
        return _hidden_status()

    if kind == "result":
        if obj.get("is_error") or subtype == "error":
            err = _extract_message_text(obj) or "Agent run failed"
            return {"type": "error", "text": err}
        text = obj.get("result")
        if isinstance(text, str) and text.strip():
            return _message_event(text, final=True, sanitize=True)
        dur = obj.get("duration_ms")
        if dur:
            return {"type": "status", "text": f"Finished in {dur / 1000:.1f}s"}
        return _hidden_status()

    if kind in ("content_block_delta", "text_delta"):
        text = _extract_message_text(obj)
        if text:
            return _message_event(text, delta=True, sanitize=False)
        return _hidden_status()

    if kind == "assistant":
        msg = obj.get("message") if isinstance(obj.get("message"), dict) else obj
        text = _extract_assistant_blocks(msg, include_tools=True) or _extract_message_text(obj)
        if not text:
            return _hidden_status()
        is_delta = obj.get("partial") is True or subtype in ("delta", "partial")
        if isinstance(msg, dict) and any(
            isinstance(b, dict) and b.get("type") == "tool_use"
            for b in (msg.get("content") or [])
        ):
            return {"type": "command", "text": text}
        if is_delta:
            return _message_event(text, delta=True, sanitize=False)
        return _message_event(text, sanitize=True)

    if kind == "tool_call":
        return {"type": "command", "text": _format_tool_line(obj, completed=(subtype == "completed"))}

    if kind == "tool_use":
        return {"type": "command", "text": _format_tool_line(obj, completed=False)}

    if kind == "tool_result":
        text = _extract_message_text(obj) or raw
        return {"type": "log", "text": text}

    if kind == "thinking":
        text = obj.get("text") or ""
        if subtype == "delta" and text:
            return {"type": "log", "text": text, "delta": True}
        return _hidden_status()

    if kind in ("command", "tool", "exec", "bash"):
        text = _extract_message_text(obj) or raw
        return {"type": "command", "text": text}

    if kind in ("log", "progress"):
        text = _extract_message_text(obj) or raw
        return {"type": "log", "text": text}

    if kind == "status":
        text = _extract_message_text(obj)
        return {"type": "status", "text": text} if text else _hidden_status()

    text = _extract_message_text(obj)
    if text and (not raw.strip().startswith("{") or text != raw):
        return _message_event(text, sanitize=True)

    if raw.strip().startswith("{"):
        return _hidden_status()

    return classify_plain_line(raw)
