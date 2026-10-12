"""Deterministic event sequence for checking the contract offline.

DX_AGENT_MOCK_DELAY=<seconds> pauses that long between events: testing "attach to a running run" needs the run
to last long enough to attach (default 0: immediate). DX_AGENT_MOCK_REPLY is the final reply (for markdown tests).
"""
import os
import time

from dx_agent_dev.core.adapters.base import AgentAdapter


class MockAdapter(AgentAdapter):
    def is_available(self) -> bool:
        return True

    def run(self, prompt, session_dir, harness_dirs, run_ctx=None):
        try:
            delay = float(os.environ.get("DX_AGENT_MOCK_DELAY") or 0)
        except ValueError:
            delay = 0.0
        events = [
            {"type": "status", "text": "session_started"},
            {"type": "message", "text": f"요청 분석: {prompt}"},
            {"type": "command", "text": "dx-suite-builder --plan"},
            {"type": "log", "text": "[1/2] 모델 준비"},
            {"type": "log", "text": "[2/2] 파이프라인 구성"},
            # A given reply is sent as the final message, like a real agent: it replaces the earlier message
            ({"type": "message", "text": os.environ["DX_AGENT_MOCK_REPLY"], "final": True}
             if os.environ.get("DX_AGENT_MOCK_REPLY") else {"type": "message", "text": "완료되었습니다."}),
            {"type": "done", "text": "ok"},
        ]
        for i, ev in enumerate(events):
            if delay and i:
                time.sleep(delay)
            yield ev

    def cancel(self):
        pass
