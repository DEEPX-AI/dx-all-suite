"""Detaches a run from the HTTP response.

If the SSE handler drove the `_runner.run(...)` generator itself, a browser dropping the stream reader would raise
`GeneratorExit` in the generator and the `finally` in `agent_runner.py` would kill the subprocess: closing the
window or moving to another module would kill the running job.

Here a background thread collects the events and the response reads that buffer. The run continues when no
consumer is attached or one leaves midway, and a consumer that attaches later gets everything from the start
(or from a chosen index).

There is one run per server, as `AgentRunner` is built that way, so this is a single slot, not a registry. A
finished run stays until the next one starts, so a window that attaches just after the end still sees the result.

The buffer lives in memory and is lost when the server dies: it is for re-attaching to a running job, not a
run history.
"""
from __future__ import annotations

import threading
import uuid
from typing import Any, Callable, Iterable, Iterator, Optional


class LiveRun:
    def __init__(self, on_event: Optional[Callable[[dict], None]] = None):
        self._cv = threading.Condition()
        self._events: list[dict] = []
        self._done = True
        self._run_id: Optional[str] = None
        self._info: dict = {}
        self._thread: Optional[threading.Thread] = None
        self._cancel: Optional[Callable[[], None]] = None
        self._on_event = on_event

    # ── lifecycle ─────────────────────────────────────────────

    def start(
        self,
        source: Iterable[dict],
        *,
        cancel: Optional[Callable[[], None]] = None,
        on_event: Optional[Callable[[dict], None]] = None,
        info: Optional[dict] = None,
    ) -> str:
        """Start consuming `source` in the background and return the run_id. `info` says what the run is
        (prompt, conversation, mode): whoever attaches later needs the first line and the conversation."""
        with self._cv:
            if not self._done:
                raise RuntimeError("run already in progress")
            run_id = uuid.uuid4().hex
            self._events = []
            self._done = False
            self._run_id = run_id
            self._info = dict(info or {})
            self._cancel = cancel
            if on_event is not None:
                self._on_event = on_event
            self._cv.notify_all()

        def pump():
            try:
                for ev in source:
                    with self._cv:
                        if self._run_id != run_id:
                            break          # another run took the slot
                        self._events.append(ev)
                        self._cv.notify_all()
                    # Work that must happen even without a consumer (such as binding the conversation
                    # record) is done here; done on the response side, it would be lost when the window closes.
                    if self._on_event is not None:
                        try:
                            self._on_event(ev)
                        except Exception:
                            pass
            finally:
                with self._cv:
                    if self._run_id == run_id:
                        self._done = True
                    self._cv.notify_all()

        thread = threading.Thread(target=pump, name=f"live-run-{run_id[:8]}", daemon=True)
        self._thread = thread
        thread.start()
        return run_id

    def cancel(self) -> None:
        with self._cv:
            cancel = self._cancel
        if cancel is not None:
            cancel()

    # ── reading ───────────────────────────────────────────────

    def events(self, from_index: int = 0) -> Iterator[dict]:
        """Stream events from `from_index` on; ends when the run ends.

        Closing this generator does not affect the run; that is why this class exists.
        """
        i = max(0, int(from_index or 0))
        while True:
            with self._cv:
                while i >= len(self._events) and not self._done:
                    self._cv.wait(timeout=0.5)
                if i >= len(self._events):
                    return
                batch = self._events[i:]
                i = len(self._events)
            for ev in batch:
                yield ev

    def snapshot(self) -> dict[str, Any]:
        with self._cv:
            return {"run_id": self._run_id, "count": len(self._events), "done": self._done,
                    "info": dict(self._info)}
