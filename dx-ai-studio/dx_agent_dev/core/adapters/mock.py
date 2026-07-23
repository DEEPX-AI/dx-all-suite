"""결정적 이벤트 시퀀스 — 폐쇄망 계약 검증용(기존 동작 보존)."""
from dx_agent_dev.core.adapters.base import AgentAdapter


class MockAdapter(AgentAdapter):
    def is_available(self) -> bool:
        return True

    def run(self, prompt, session_dir, harness_dirs, run_ctx=None):
        yield {"type": "status", "text": "session_started"}
        yield {"type": "message", "text": f"요청 분석: {prompt}"}
        yield {"type": "command", "text": "dx-suite-builder --plan"}
        yield {"type": "log", "text": "[1/2] 모델 준비"}
        yield {"type": "log", "text": "[2/2] 파이프라인 구성"}
        yield {"type": "message", "text": "완료되었습니다."}
        yield {"type": "done", "text": "ok"}

    def cancel(self):
        pass
