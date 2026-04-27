## SWE 프로세스 게이트 — 내부 개발 (HARD GATE)

AI 에이전트(Claude Code, Copilot CLI, Cursor CLI, Copilot Chat (VS Code),
Cursor (IDE), OpenCode, 기타 모든 도구)를 사용하여 내부 dx-agentic-dev 기능을
개발하거나 수정할 때는 전체 소프트웨어 엔지니어링 규율이 **필수**입니다.
다음 경로에 영향을 미치는 모든 작업에 적용됩니다:

| 경로 | 예시 |
|------|------|
| `tests/test_agentic_e2e_scenarios/` | `conftest.py`, `test_*.py` fixture |
| `tests/test_agentic_scenarios/` | 시나리오 테스트 케이스 |
| `tests/test.sh` | 수동/자동 shell runner |
| `tests/conftest.py`, `tests/parse_copilot_session.py` | 공유 테스트 인프라 |
| `tools/dx-agentic-dev-gen/` | generator 소스, CLI, transformer |
| `.deepx/` | agent, skill, 템플릿, fragment (canonical source) |

이 규칙은 아래 **Instruction File Verification Loop**에 **추가로** 적용됩니다.

### 필수 Skill 시퀀스 (비-trivial 변경)

모든 비-trivial 내부 변경은 반드시 이 시퀀스를 거쳐야 합니다.
**이 시퀀스가 완료되기 전까지 코드 작성 금지.**

| 단계 | Skill | 적용 시점 |
|------|-------|-----------|
| 1 | `/dx-skill-router` | **항상** — 모든 작업 전 적용 가능한 skill 식별 |
| 2 | `/dx-brainstorm-and-plan` | 기능 추가, 동작 변경, 구조적 리팩토링 시 |
| 3 | `/dx-writing-plans` | 승인된 계획이 >2 구현 단계를 포함할 때 |
| 4 | `/dx-tdd` | 모든 코드 변경 — 구현 전 테스트/검증을 먼저 확인하거나 작성 |
| 5 | Verification loop | 모든 변경 후 — generator + drift check + test 실행 |
| 6 | `/dx-verify-completion` | 완료 선언 전 — 주장이 아닌 증거 필요 |

### "테스트 우선"의 의미

내부 개발 맥락에서 `/dx-tdd`:

- **`tests/` 변경** — 기존 suite를 실행하여 구현 전 **RED** 상태를 확인합니다.
  코드를 작성하기 전에 예상된 이유로 테스트가 실패해야 합니다.
- **`.deepx/` 변경** — 편집 전 `dx-agentic-gen check` 기준 출력을 캡처합니다.
  변경 후 재실행하여 의도한 drift만 나타나는지 확인합니다.
- **`tools/` 변경** — 변경이 해소해야 할 구체적인 실패 모드(잘못된 경로, 잘못된 출력,
  누락된 규칙)를 식별합니다. 이를 포착하는 테스트를 작성하거나 가리킵니다.
- **`test.sh` 변경** — 편집 전 실행 경로를 수동으로 추적하거나 (`bash -n` 구문 검사).
  필요 시 `bash -x`로 영향받는 코드 경로를 확인합니다.

### Trivial 변경 예외

다음의 경우에만 2–3단계(brainstorm/plan)를 건너뛸 수 있습니다:
- 한 줄 오탈자 또는 문구 수정
- 순수 서식 변경 (공백, 빈 줄)
- 명백하고 격리된 원인을 가진 단일 변수 이름 변경

4–6단계(TDD, verification, completion check)는 trivial 변경에도 **절대 건너뛸 수 없습니다**.

### Hard Gate

| Gate | 규칙 |
|------|------|
| **계획 없이 코드 작성 금지** | >1 파일에 영향을 미치는 변경은 먼저 승인된 계획 필요 |
| **실패하는 테스트 없이 기능 추가 금지** | RED 확인 후에만 구현 |
| **증거 없이 완료 선언 금지** | pytest/generator 출력 제시 — 완료 주장 불가 |
| **생성된 파일 직접 편집 금지** | `CLAUDE.md`, `AGENTS.md`, `.claude/` → `.deepx/` source 편집 |

### 흔한 안티패턴 (금지)

- "변경이 명확하다"는 이유로 `/dx-brainstorm-and-plan` 건너뛰기 — 절대 명확하지 않음
- 테스트 suite 실행 없이 fixture 추가 또는 `conftest.py` 변경 (눈먼 변경)
- 실제 pytest 출력 또는 `dx-agentic-gen check` 출력 없이 완료 주장
- "마지막에 검증하겠다" 방식 — `/dx-tdd`에 따라 파일별로 검증
- generator 출력 파일 직접 편집 — 다음 `dx-agentic-gen generate` 실행 시 덮어씌워짐
- `/dx-skill-router` 호출 전 구현 시작
