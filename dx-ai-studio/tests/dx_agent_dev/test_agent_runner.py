"""dx_agent_dev 에이전트 러너/어댑터 테스트."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))

VALID_TYPES = {"message", "command", "log", "status", "done", "error", "ping", "degraded"}


def test_adapter_is_abstract():
    from core.agent_runner import AgentAdapter
    import pytest
    with pytest.raises(TypeError):
        AgentAdapter()


def test_mock_adapter_available():
    from core.agent_runner import MockAdapter
    assert MockAdapter().is_available() is True


def test_mock_adapter_emits_valid_event_sequence(tmp_path):
    from core.agent_runner import MockAdapter
    events = list(MockAdapter().run("build a yolo demo", tmp_path, []))
    assert all(e["type"] in VALID_TYPES for e in events)
    assert all("text" in e for e in events)
    assert events[-1]["type"] == "done"
    # 결정적: 동일 입력 → 동일 시퀀스
    events2 = list(MockAdapter().run("build a yolo demo", tmp_path, []))
    assert [e["type"] for e in events] == [e["type"] for e in events2]


def test_mock_adapter_includes_command_and_log(tmp_path):
    from core.agent_runner import MockAdapter
    types = [e["type"] for e in MockAdapter().run("x", tmp_path, [])]
    assert "command" in types
    assert "log" in types


def test_runner_creates_isolated_session_dir(tmp_path):
    from core.agent_runner import AgentRunner, MockAdapter
    runner = AgentRunner(MockAdapter(), tmp_path)
    list(runner.run("hello", []))
    sessions = list(tmp_path.iterdir())
    assert len(sessions) == 1 and sessions[0].is_dir()


def test_runner_single_session_rejects_concurrent(tmp_path):
    """서버당 1세션: busy 중 2차 run은 error 이벤트로 거부."""
    import threading
    from core.agent_runner import AgentRunner, AgentAdapter

    class BlockingAdapter(AgentAdapter):
        def __init__(self):
            self.release = threading.Event()

        def is_available(self):
            return True

        def run(self, p, s, h, run_ctx=None):
            yield {"type": "status", "text": "start"}
            self.release.wait(timeout=2)
            yield {"type": "done", "text": "ok"}

        def cancel(self):
            self.release.set()

    a = BlockingAdapter()
    runner = AgentRunner(a, tmp_path)
    gen1 = runner.run("first", [])
    next(gen1)  # busy 진입
    second = list(runner.run("second", []))
    assert second[0]["type"] == "error"
    a.release.set()
    list(gen1)


def test_runner_clears_busy_after_completion(tmp_path):
    from core.agent_runner import AgentRunner, MockAdapter
    runner = AgentRunner(MockAdapter(), tmp_path)
    list(runner.run("a", []))
    assert runner.is_busy() is False
    list(runner.run("b", []))  # 재실행 가능
    assert runner.is_busy() is False


def test_runner_calls_adapter_cancel_in_finally(tmp_path):
    """R5: 정상완료 시에도 finally에서 adapter.cancel()이 호출되어 subprocess 정리 보장."""
    from core.agent_runner import AgentRunner, MockAdapter
    calls = []
    adapter = MockAdapter()
    adapter.cancel = lambda: calls.append(1)
    runner = AgentRunner(adapter, tmp_path)
    list(runner.run("x", []))
    assert calls == [1]


def test_runner_timeout_releases_slot_on_hung_generation(tmp_path):
    """F-19: a hung generation must not hold the single concurrency slot forever.

    After the wall-clock timeout elapses the runner must cancel the stuck run,
    surface an error event, free the busy slot, and let a new request proceed.
    """
    import threading
    from core.agent_runner import AgentRunner, AgentAdapter, MockAdapter

    class HungAdapter(AgentAdapter):
        def __init__(self):
            self.cancelled = threading.Event()

        def is_available(self):
            return True

        def run(self, p, s, h, run_ctx=None):
            yield {"type": "status", "text": "start"}
            # Simulate a stuck subprocess: block until cancel() is invoked.
            self.cancelled.wait(timeout=30)
            yield {"type": "done", "text": "late"}

        def cancel(self):
            self.cancelled.set()

    hung = HungAdapter()
    runner = AgentRunner(hung, tmp_path, timeout=0.3)
    events = list(runner.run("hang", []))

    # The timeout surfaces as an error event...
    assert any(e["type"] == "error" for e in events)
    # ...the stuck run was cancelled to terminate it...
    assert hung.cancelled.is_set()
    # ...and the slot is freed.
    assert runner.is_busy() is False

    # A subsequent request must NOT be rejected as "agent busy".
    second = list(runner.run("again", [], adapter=MockAdapter()))
    assert not (second and second[0].get("type") == "error"
                and second[0].get("text") == "agent busy")
    assert second[-1]["type"] == "done"


def test_copilot_adapter_cancel_kills_process_group(monkeypatch):
    """I-1/R5: 살아있는 자식은 프로세스 그룹 단위로 SIGTERM 종료(좀비 방지)."""
    import signal
    from core import agent_runner
    sent = {}
    monkeypatch.setattr(agent_runner.os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(agent_runner.os, "killpg", lambda pgid, sig: sent.setdefault("sig", sig))

    class FakeProc:
        pid = 4321
        def poll(self):
            return None  # 살아있음

        def wait(self, timeout=None):
            return 0

    a = agent_runner.CopilotAdapter("/usr/bin/copilot")
    a._proc = FakeProc()
    a.cancel()
    assert sent.get("sig") == signal.SIGTERM
