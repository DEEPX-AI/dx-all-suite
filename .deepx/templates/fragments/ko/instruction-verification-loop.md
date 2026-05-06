## Instruction File Verification Loop (HARD GATE) — 내부 개발 전용

canonical source 수정 시 — `**/.deepx/**/*.md` 파일(agents, skills, templates,
fragments 포함) — 작업 완료 선언 전에 다음 루프를 **반드시** 수행해야 합니다:

1. **Generator 실행** — `.deepx/` 변경을 모든 플랫폼으로 전파:
   ```bash
   dx-agentic-gen generate
   # Suite 전체: bash tools/dx-agentic-dev-gen/scripts/run_all.sh generate
   ```
2. **Drift 검증** — 생성물과 commit 상태 일치 확인:
   ```bash
   dx-agentic-gen check
   ```
   drift 발견 시 1단계로 복귀.
3. **자동화 테스트 루프** — 테스트는 generator 출력이 정책을 만족하는지 검증:
   ```bash
   python -m pytest tests/test_agentic_scenarios/ -v --tb=short
   ```
   실패 처리:
   - generator 버그 → generator 수정 → 1단계
   - `.deepx/` 콘텐츠 누락 → `.deepx/` 수정 → 1단계
   - 테스트 규칙 부족 → 테스트 강화 → 1단계
4. **수동 감사** — 테스트 결과에 의존하지 않고, 생성된 파일들을 독립적으로 읽어
   크로스 플랫폼 sync(CLAUDE vs AGENTS vs copilot)와 레벨 간 sync(suite → 하위)를
   검증.
5. **갭 분석** — 수동 감사에서 발견한 이슈:
   - generator가 놓친 경우 → **generator 규칙 수정** 후 1단계
   - 테스트가 놓친 경우 → **테스트 강화** 후 1단계
6. **반복** — 3~5단계 모두 통과할 때까지.

### Pre-flight Classification (MANDATORY)

저장소 내의 `.md` 또는 `.mdc` 파일을 수정하기 전에, 반드시 다음 3가지 카테고리
중 하나로 분류하세요. **이 단계를 절대 건너뛰지 마세요** — generator 관리 파일을
직접 수정하면 다음 generate에서 조용히 덮어써지는 사일런트 손상이 됩니다.

**모든 파일 편집 전 다음 세 가지 질문에 순서대로 답하세요:**

> **Q1. 파일 경로가 `**/.deepx/**` 내부에 있나요?**
> - YES → **Canonical source.** 직접 수정 후 `dx-agentic-gen generate` + `check` 실행.
> - NO → Q2로 이동.
>
> **Q2. 파일 경로 또는 이름이 다음 중 하나와 일치하나요?**
> ```
> .github/agents/    .github/skills/    .opencode/agents/
> .claude/agents/    .claude/skills/    .cursor/rules/
> CLAUDE.md          CLAUDE-KO.md       AGENTS.md    AGENTS-KO.md
> copilot-instructions.md               copilot-instructions-KO.md
> ```
> - YES → **Generator output. 직접 수정 금지.**
>   `.deepx/` source(template, fragment, 또는 agent/skill)를 찾아 수정한 후
>   `dx-agentic-gen generate`를 실행하세요.
> - NO → Q3으로 이동.
>
> **Q3. 파일이 `<!-- AUTO-GENERATED`로 시작하나요?**
> - YES → **Generator output. 직접 수정 금지.** Q2와 동일.
> - NO → **Independent source.** 직접 수정 가능. 수정 후 `dx-agentic-gen check`를 한 번 실행.

1. **Canonical source** (`**/.deepx/**/*.md`) — 직접 수정 후 위의 Verification
   Loop을 실행합니다.
2. **Generator output** — 알려진 출력 경로의 파일:
   `CLAUDE.md`, `CLAUDE-KO.md`, `AGENTS.md`, `AGENTS-KO.md`,
   `copilot-instructions.md`, `.github/agents/`, `.github/skills/`,
   `.claude/agents/`, `.claude/skills/`, `.opencode/agents/`, `.cursor/rules/`
   → **직접 수정 금지.** `.deepx/` source(template, fragment, 또는
   agent/skill)를 찾아 수정한 후 `dx-agentic-gen generate`를 실행하세요.
3. **독립 소스** — 위 두 카테고리에 해당하지 않는 모든 파일 (`docs/source/`,
   `source/docs/`, `tests/`, 서브 프로젝트의 `README.md` 등)
   → 직접 수정 가능. 수정 후 `dx-agentic-gen check`를 한 번 실행하여 예상치
   못한 drift가 없는지 확인하세요.

**Anti-pattern**: 분류 없이 바로 파일을 수정하는 것. 해당 파일이 generator
output인지 확실하지 않으면, 수정 전후에 `dx-agentic-gen check`를 실행하세요
— check가 수정 내용을 덮어쓰면 해당 파일은 generator가 관리하는 파일이므로
`.deepx/` source를 통해 수정해야 합니다.

Pre-commit hook이 generator output 무결성을 강제합니다: 생성된 파일이
최신이 아니면 `git commit`이 실패합니다. Hook 설치:
```bash
tools/dx-agentic-dev-gen/scripts/install-hooks.sh
```

> **KO 대응 파일 규칙**: EN fragment를 편집할 때, KO 대응 파일도 업데이트가
> 필요한지 확인하세요. 단락 1개 이상을 추가하거나 제거했다면, 커밋 전에
> `.deepx/templates/fragments/ko/<stem>.md`를 업데이트하세요. `dx-agentic-gen lint`를
> 실행하여 `[OK]`를 확인하세요 — EN이 KO보다 10줄 이상 많으면 lint가 ERROR를
> 반환합니다.

이 게이트는 `.deepx/` 파일이 작업의 *주요 산출물*인 경우(규칙 추가, 플랫폼 sync,
KO 번역 생성, agents/skills 수정)에 적용됩니다. 기능 구현 중 `.deepx/`에 단순
한 줄 수정이 발생하는 경우에는 적용되지 않습니다.
