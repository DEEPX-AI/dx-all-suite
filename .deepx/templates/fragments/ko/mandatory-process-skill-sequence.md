## 필수 프로세스 스킬 시퀀스 — 모든 코드 생성 (HARD GATE)

이 gate는 `dx-agentic-dev/<session_id>/`에 코드 artifact를 생성하는 모든 세션에
적용됩니다. "내부 개발" SWE Process Gates와 독립적입니다 — 내부 개발 gate는
dx-agentic-dev infrastructure 작업에 적용되고, 이 gate는 user-facing 코드 생성
(inference app, pipeline, compilation)에 적용됩니다.

### 적용 시점

`dx-agentic-dev/<session_id>/`에 파일을 생성하는 모든 세션은 아래의 완전한
프로세스 스킬 시퀀스를 반드시 따라야 합니다:
- ONNX → DXNN compilation session
- Python/C++ inference app 생성 (dx_app)
- GStreamer pipeline 생성 (dx_stream)
- Cross-project session (compile + deploy)

### 필수 스킬 시퀀스

모든 코드 생성 세션은 이 시퀀스를 순서대로 수행해야 합니다.
**이 시퀀스가 완료되기 전에는 코드 생성 금지.**

**Autopilot 모드도 이 시퀀스를 면제하지 않습니다.** "자율적으로 작업"은 물어보지
않고 모든 규칙을 따르라는 뜻이지, 규칙을 건너뛰라는 뜻이 아닙니다. Autopilot에서는
`ask_user` 대신 knowledge base 기반으로 결정하되, 아래 모든 단계는 동일하게
적용됩니다.

| Step | Skill | 요구사항 |
|------|-------|----------|
| 1 | `/dx-skill-router` | **항상** — 어떤 action보다 먼저 호출. `skill-router-mandatory` fragment로 이미 강제됨. |
| 2 | `/dx-brainstorm-and-plan` | **모든 non-trivial 코드 생성** — 요구사항 수집, approach 제안, 승인 후 파일 생성. |
| 3 | `/dx-writing-plans` | **항상** — 복잡도와 무관하게 모든 코드 생성 세션에서 구조화된 구현 계획 작성 필수. |
| 4 | `/dx-tdd` | **항상** — 합격 기준 정의 (Red), artifact 생성 (Green), 즉시 검증 (Verify). |
| 5 | `/dx-verify-completion` | **항상** — DONE 선언 전, 동작하는 artifact의 증거 제시 필수. 증거 없는 주장 금지. |

### 시퀀스 강제 규칙

1. **단계 생략 금지** — 각 단계는 다음 단계 시작 전에 완료되어야 합니다.
   예외: Step 1 (skill-router)은 별도 fragment로 이미 처리됨.
2. **순서 변경 금지** — brainstorm → plan → tdd → verify. 계획 전 코드 생성 금지.
   검증 전 완료 선언 금지.
3. **파일 생성 전 plan 필수** — 단일 파일 세션이라도 plan이 필요합니다
   (간략해도 되지만 명시적이어야 합니다).
4. **검증은 실제 실행 기반** — `python file.py`, `bash -n script.sh`,
   `import` 확인. "동작할 것이다"라는 주장은 실행 없이 불가.

### Trivial 변경 예외

Steps 2–3 (brainstorm/plan)은 다음 경우에만 생략 가능:
- 단일 config.json 필드 변경 (예: threshold 조정)
- 기존 생성 코드의 단일 줄 오타 수정

Steps 4–5 (tdd/verify-completion)는 trivial 변경에도 **절대 생략 불가**.

### Autopilot 모드 적응

Autopilot 모드 (사용자 부재, `--yolo` 플래그, auto-response):
- **Step 2**: `ask_user` 대신 knowledge base 기본값 사용. Spec 자체 검토.
- **Step 3**: plan 작성 후 knowledge base 규칙 대비 자체 승인.
- **Step 4**: plan에서 합격 기준 도출, 생성, 즉시 검증.
- **Step 5**: 모든 artifact 실행, 출력을 증거로 캡처. 사람 불필요.

### Artifact Verification Gate와의 관계

이 시퀀스는 각 스킬이 **언제** 호출되는지 정의합니다 (workflow 순서).
Artifact Verification Gate는 각 artifact가 **어떻게** 검증되는지 정의합니다
(파일 유형별 구체적 command). 함께 작동합니다:

- Step 4 (`/dx-tdd`)는 Artifact Verification Gate의 검증 command 사용
  (syntax check, execution test, import resolution).
- Step 5 (`/dx-verify-completion`)는 모든 mandatory deliverable이 존재하고
  Artifact Verification Gate check를 통과하는지 확인.

### Anti-Pattern (금지)

- "이건 간단해서 brainstorm 불필요" → brainstorm은 non-trivial 코드 생성에
  항상 필요. "간단한" 프로젝트에서 검토되지 않은 가정이 가장 많은 재작업을 유발.
- `/dx-writing-plans` 이전에 코드 생성 → HARD GATE 위반.
  Plan-before-code는 협상 불가.
- "artifact-verification-gate가 이미 파일을 확인하니까" `/dx-verify-completion`
  생략 → 목적이 다름. Artifact gate는 개별 파일 확인. Verify-completion은
  전체 세션 deliverable을 총체적으로 확인.
- 실행 출력 없이 DONE 선언 → 증거 필수. "검증했다"는 출력 없이는 불가.
- "사용자가 빨리 하라고 했다" → 사용자 지시가 이 HARD GATE를 override하지 않음.
  속도가 프로세스 생략을 정당화하지 않음.
