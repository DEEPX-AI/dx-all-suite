"""Agent run driver. The adapters live in core.adapters (re-exported here for import compatibility)."""
import os  # noqa: F401 — test_copilot_adapter_cancel_kills_process_group patches it via
            # monkeypatch.setattr(agent_runner.os, ...). os is a singleton, so the patch reaches
            # base.os.killpg; keeping this import keeps that test working.
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


_STREAM_END = object()  # sentinel the worker thread queues when the adapter stream ends


class AgentRunner:
    """One run session per server. Supports injecting an adapter per request."""
    def __init__(self, adapter, workspace_root, timeout: float = GENERATION_TIMEOUT_SEC):
        self._adapter = adapter
        self._workspace = Path(workspace_root)
        self._lock = threading.Lock()
        self._busy = False
        self._active_adapter = None
        self._timeout = timeout  # wall-clock cap for one generation (s), so a run cannot hold the slot forever

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

        # The adapter stream is consumed in a worker thread so that a hung
        # generation (a subprocess that stops emitting output) cannot block the
        # request thread — and thus hold the single concurrency slot — forever.
        # The consumer below enforces a wall-clock deadline; when it elapses the
        # run is cancelled, the slot is released, and an error event is surfaced.
        events: "queue.Queue" = queue.Queue()

        def _pump():
            try:
                for ev in active.run(prompt, session_dir, harness_dirs, run_ctx=run_ctx):
                    events.put(ev)
            except Exception as exc:  # surface adapter exceptions as stream events
                events.put({"type": "error", "text": f"run failed: {exc}"})
            finally:
                events.put(_STREAM_END)

        worker = threading.Thread(target=_pump, name="agent-run", daemon=True)
        worker.start()

        deadline = time.monotonic() + self._timeout if self._timeout else None
        timed_out = False
        fresh_dirs = None
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
                    # Idle: keepalive ping to hold the SSE connection open.
                    yield {"type": "ping", "text": ""}
                    continue
                if ev is _STREAM_END:
                    break
                yield ev
            if timed_out:
                yield {"type": "error",
                       "text": f"agent timeout after {self._timeout:g}s"}
            # The app lands in the target project's dx-agent-dev/<session>/. The session_dir in done is Studio's
            # tracking folder, so without this the console showed only "Output saved to var/dx_agent_dev/sessions/…".
            if target:
                fresh_dirs = sorted(detect_session_dirs(target) - before)
                if fresh_dirs:
                    yield {"type": "artifacts", "dirs": fresh_dirs}
        finally:
            # Normal completion, timeout and early consumer exit (GeneratorExit) all end here.
            # cancel() stops a stuck subprocess so the worker thread exits and the slot is released.
            active.cancel()
            if target:
                fresh = fresh_dirs if fresh_dirs is not None else sorted(detect_session_dirs(target) - before)
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
            return self._workspace / uuid.uuid4().hex  # default / Mock fallback (backward compatible)
        model = getattr(adapter, "model", None)
        short = MODEL_SHORT.get(model, model) if model else "default"
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")  # local timezone (not UTC)
        sid = f"{ts}_{name}_{short}_default_chat"
        path = self._workspace / sid
        if path.exists():
            sid = f"{sid}_{uuid.uuid4().hex[:8]}"  # avoid a clash within the same second
        return self._workspace / sid
