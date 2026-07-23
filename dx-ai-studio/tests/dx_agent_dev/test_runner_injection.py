"""요청별 어댑터 주입(H3) + 활성 어댑터 cancel 경로."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


class RecordingAdapter:
    def __init__(self, name=None):
        self.name = name
        self.model = None
        self.ran = False
        self.cancelled = 0

    def is_available(self):
        return True

    def run(self, prompt, session_dir, harness_dirs, run_ctx=None):
        self.ran = True
        yield {"type": "message", "text": f"{self.name}:{prompt}"}
        yield {"type": "done", "text": "ok"}

    def cancel(self):
        self.cancelled += 1


def test_injected_adapter_is_used_over_default(tmp_path):
    from core.agent_runner import AgentRunner
    default = RecordingAdapter("default")
    injected = RecordingAdapter("injected")
    runner = AgentRunner(default, tmp_path)
    events = list(runner.run("hi", [], adapter=injected))
    assert injected.ran is True
    assert default.ran is False
    assert any("injected:hi" in e.get("text", "") for e in events)


def test_injected_adapter_cancel_called_in_finally(tmp_path):
    from core.agent_runner import AgentRunner
    default = RecordingAdapter("default")
    injected = RecordingAdapter("injected")
    runner = AgentRunner(default, tmp_path)
    list(runner.run("hi", [], adapter=injected))
    assert injected.cancelled >= 1
    assert default.cancelled == 0


def test_runner_cancel_targets_active_injected_adapter(tmp_path):
    """실행 진행 중 cancel()은 활성(주입) 어댑터를 취소."""
    import threading
    from core.agent_runner import AgentRunner

    class Blocking(RecordingAdapter):
        def __init__(self, name):
            super().__init__(name)
            self.release = threading.Event()

        def run(self, prompt, session_dir, harness_dirs, run_ctx=None):
            self.ran = True
            yield {"type": "status", "text": "start"}
            self.release.wait(timeout=2)
            yield {"type": "done", "text": "ok"}

        def cancel(self):
            super().cancel()
            self.release.set()

    default = RecordingAdapter("default")
    blocking = Blocking("injected")
    runner = AgentRunner(default, tmp_path)
    gen = runner.run("hi", [], adapter=blocking)
    next(gen)  # busy 진입, blocking.run 활성
    runner.cancel()
    assert blocking.cancelled >= 1
    list(gen)


def test_cancel_noop_when_idle(tmp_path):
    """실행 중이 아닐 때 cancel은 기본 어댑터 대상(no active) — 예외 없이 동작."""
    from core.agent_runner import AgentRunner
    default = RecordingAdapter("default")
    runner = AgentRunner(default, tmp_path)
    runner.cancel()  # 예외 없어야 함
