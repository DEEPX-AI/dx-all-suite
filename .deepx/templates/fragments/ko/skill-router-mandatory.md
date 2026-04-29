## Skill Router — 범용 Pre-Flight (HARD GATE)

`/dx-skill-router`는 **모든 사용자 메시지**에 대해 **절대적인 첫 번째 action**으로
반드시 invoke되어야 합니다 — 작업 유형(개발, 분석, 읽기, 설명, 질문 등)에 관계없이.

이 규칙은 다음보다 먼저 적용됩니다:
- 파일 읽기 또는 codebase 탐색
- 응답 또는 clarifying question
- SWE gate check 또는 path classification
- 코드 생성 또는 plan 작성

**예외 없음.** 다음 합리화는 모두 금지됩니다:

| 합리화 | 현실 |
|--------|------|
| "이건 그냥 파일 읽기/분석이야" | 읽기도 task입니다. 먼저 router를 invoke하세요. |
| "사용자가 질문만 했을 뿐이야" | 질문도 task입니다. 먼저 router를 invoke하세요. |
| "이건 개발 작업이 아니야" | Router는 모든 task에 적용됩니다. 개발에만 해당되지 않습니다. |
| "요청을 이해한 후에 skill을 확인하자" | 이해하기 전에 먼저 확인하세요. |
| "이건 SWE gates를 트리거하지 않아" | SWE gates는 별개입니다. Router는 범용입니다. |
