"""에이전트 실행 러너. 어댑터는 core.adapters로 이전(import 호환 재노출)."""
import os  # noqa: F401 — 보호 테스트 test_copilot_adapter_cancel_kills_process_group가
            # monkeypatch.setattr(agent_runner.os, ...)로 패치한다. os는 싱글톤이라
            # 전역 패치가 base.os.killpg까지 도달하므로 이 import만 유지하면 테스트 보존.
import queue
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Iterator, Optional

from dx_agent_dev.core.agents_config import MODEL_SHORT
from dx_agent_dev.core.config import GENERATION_TIMEOUT_SEC, KEEPALIVE_SEC

from dx_agent_dev.core.adapters import AgentAdapter, SubprocessAdapter, MockAdapter, CopilotAdapter
from dx_agent_dev.core.conversation_store import Conversation
from dx_agent_dev.core.run_context import RunContext

__all__ = ["AgentAdapter", "SubprocessAdapter", "MockAdapter", "CopilotAdapter",
           "AgentRunner", "detect_session_dirs"]


def detect_session_dirs(target) -> set:
    """Return absolute paths of `dx-agent-dev/<session>/` dirs under `target`.

    Mirrors the original test.sh `detect_new_sessions`: the agent (running with cwd at the
    target, per CLAUDE.md Output Isolation) creates its artifacts under
    `<sub-project>/dx-agent-dev/<session_id>/`. Bounded to depth ≤2 sub-dirs so a suite-root
    target (e.g. dx-runtime/dx_app/dx-agent-dev) is covered without scanning the whole tree.
    Best-effort: a missing/unreadable target yields an empty set, never raises.
    """
    base = Path(target)
    if not base.is_dir():
        return set()
    found = set()
    for pattern in ("dx-agent-dev/*", "*/dx-agent-dev/*", "*/*/dx-agent-dev/*"):
        try:
            for p in base.glob(pattern):
                if p.is_dir():
                    found.add(str(p.resolve()))
        except OSError:
            continue
    return found


_STREAM_END = object()  # 워커 스레드가 어댑터 스트림 종료 시 큐에 넣는 센티널


class AgentRunner:
    """서버당 실행 세션 1개. 요청별 어댑터 주입 지원(H3)."""
    def __init__(self, adapter, workspace_root, timeout: float = GENERATION_TIMEOUT_SEC):
        self._adapter = adapter
        self._workspace = Path(workspace_root)
        self._lock = threading.Lock()
        self._busy = False
        self._active_adapter = None
        self._timeout = timeout  # 단일 생성 wall-clock 상한(초). F-19: 슬롯 영구 점유 방지.

    def is_busy(self) -> bool:
        return self._busy

    def run(
        self,
        prompt: str,
        harness_dirs: list,
        adapter=None,
        *,
        conversation: Optional[Conversation] = None,
        run_ctx: Optional[RunContext] = None,
    ) -> Iterator[dict]:
        with self._lock:
            if self._busy:
                yield {"type": "error", "text": "agent busy"}
                return
            self._busy = True
            active = adapter or self._adapter
            self._active_adapter = active
        if conversation and conversation.session_dir:
            session_dir = Path(conversation.session_dir)
            session_dir.mkdir(parents=True, exist_ok=True)
        else:
            session_dir = self._build_session_dir(active)
            session_dir.mkdir(parents=True, exist_ok=True)
        # Snapshot the agent-created session dirs under the target workdir (harness_dirs[0])
        # so we can detect which one this run produces (artifacts live there, not in the
        # studio's tracking session_dir). Best-effort — never blocks the run.
        target = harness_dirs[0] if harness_dirs else None
        before = detect_session_dirs(target) if target else set()

        # F-19: the adapter stream is consumed in a worker thread so that a hung
        # generation (a subprocess that stops emitting output) cannot block the
        # request thread — and thus hold the single concurrency slot — forever.
        # The consumer below enforces a wall-clock deadline; when it elapses the
        # run is cancelled, the slot is released, and an error event is surfaced.
        events: "queue.Queue" = queue.Queue()

        def _pump():
            try:
                for ev in active.run(prompt, session_dir, harness_dirs, run_ctx=run_ctx):
                    events.put(ev)
            except Exception as exc:  # 어댑터 예외를 스트림 이벤트로 표면화
                events.put({"type": "error", "text": f"run failed: {exc}"})
            finally:
                events.put(_STREAM_END)

        worker = threading.Thread(target=_pump, name="agent-run", daemon=True)
        worker.start()

        deadline = time.monotonic() + self._timeout if self._timeout else None
        timed_out = False
        try:
            while True:
                if deadline is not None:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        timed_out = True
                        break
                    wait = min(remaining, KEEPALIVE_SEC)
                else:
                    wait = KEEPALIVE_SEC
                try:
                    ev = events.get(timeout=wait)
                except queue.Empty:
                    # 유휴 상태 — SSE 연결 유지용 keepalive ping.
                    yield {"type": "ping", "text": ""}
                    continue
                if ev is _STREAM_END:
                    break
                yield ev
            if timed_out:
                yield {"type": "error",
                       "text": f"agent timeout after {self._timeout:g}s"}
        finally:
            # 정상 완료·타임아웃·소비자 조기 종료(GeneratorExit) 모두 여기로 수렴한다.
            # cancel()은 멈춘 subprocess를 종료해 워커 스레드가 빠져나오게 하고 슬롯을 푼다.
            active.cancel()
            if target:
                fresh = sorted(detect_session_dirs(target) - before)
                if fresh and conversation is not None:
                    try:
                        conversation.artifact_dirs = fresh
                    except Exception:
                        pass
            with self._lock:
                self._active_adapter = None
                self._busy = False

    def cancel(self):
        with self._lock:
            target = self._active_adapter or self._adapter
        if target is not None:
            target.cancel()

    def _build_session_dir(self, adapter):
        name = getattr(adapter, "name", None)
        if not name:
            return self._workspace / uuid.uuid4().hex  # 기본·Mock 폴백(하위호환)
        model = getattr(adapter, "model", None)
        short = MODEL_SHORT.get(model, model) if model else "default"
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")  # 로컬 타임존(UTC 금지)
        sid = f"{ts}_{name}_{short}_default_chat"
        path = self._workspace / sid
        if path.exists():
            sid = f"{sid}_{uuid.uuid4().hex[:8]}"  # 동일초 충돌 회피
        return self._workspace / sid
