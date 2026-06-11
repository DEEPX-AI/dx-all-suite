# Fragment Authoring Guide

이 문서는 `.deepx/templates/fragments/` 하위에 있는 fragment 파일을 생성하고 편집하기
위한 규칙을 정의합니다. Fragment는 5개 repo 전체의 모든 platform instruction 파일
(CLAUDE.md, AGENTS.md, copilot-instructions.md 등) 에 주입되는 빌딩 블록입니다.

현재 `.deepx/templates/fragments/` 에는 EN 16개 + KO 16개 = **총 32개 fragment 파일**이 있으며,
각 EN 파일은 동일한 stem 이름의 KO 페어를 가져야 합니다 (Rule 1 참고).

---

## Rule 1: EN과 KO를 동시에 생성해야 한다 (MANDATORY)

**모든 신규 fragment는 같은 commit에서 EN 버전과 KO 버전을 모두 생성해야 합니다.**

| Path | Purpose |
|------|---------|
| `.deepx/templates/fragments/en/<name>.md` | English 버전 (canonical) |
| `.deepx/templates/fragments/ko/<name>.md` | Korean 번역 |

### 이유

Generator는 fragment를 EN과 KO platform 출력 양쪽에 주입합니다. KO fragment가
누락되면 한국어 agent는 렌더링되지 않은 `{{FRAGMENT:<name>}}` placeholder를 보거나
콘텐츠가 없게 됩니다 — KO 출력이 silently 깨지게 됩니다.

### 신규 fragment 추가 방법

```bash
# 1. EN 버전 작성
vim .deepx/templates/fragments/en/my-new-rule.md

# 2. KO 버전을 즉시 작성 (같은 작업 세션 내에서)
vim .deepx/templates/fragments/ko/my-new-rule.md

# 3. 포함할 template에 등록
vim .deepx/templates/en/CLAUDE.md.tmpl    # {{FRAGMENT:my-new-rule}} 추가
vim .deepx/templates/ko/CLAUDE-KO.md.tmpl # {{FRAGMENT:my-new-rule}} 추가
# (필요에 따라 AGENTS.md.tmpl, copilot-instructions.md.tmpl도 동일하게 처리)

# 4. Generate 및 검증
bash .deepx/tools/scripts/run_all.sh generate
dx-agent-gen check      # "All generated files are up-to-date." 가 출력되어야 함
dx-agent-gen lint       # "All EN/KO fragment pairs are consistent." 가 출력되어야 함
```

---

## Rule 2: KO에 Structural Marker를 보존해야 한다 (MANDATORY)

EN fragment가 decision-tree blockquote (Q1./Q2./Q3. 패턴) 를 포함할 때, KO 카운터파트는
**반드시** 대응하는 한국어 Q1./Q2./Q3. 블록을 포함해야 합니다.

### Structural marker 패턴

structural marker는 `**Q<digit>.` 패턴과 일치하는 모든 라인을 의미합니다 — 예시:

```
> **Q1. Is the file path inside `**/.deepx/**`?**
> **Q2. Does the file path match any of these?**
> **Q3. Does the file begin with `<!-- AUTO-GENERATED`?**
```

### 하지 말아야 할 것

```markdown
<!-- BAD: KO fragment omits the decision tree and only has the numbered list -->
### Pre-flight Classification (MANDATORY)

세 가지 질문에 답하세요:

1. **Canonical source** — 직접 수정.
2. **Generator output** — .deepx/ source를 수정.
3. **독립 소스** — 직접 수정.
```

```markdown
<!-- GOOD: KO fragment includes both the decision tree AND the numbered list -->
### Pre-flight Classification (MANDATORY)

**모든 파일 편집 전 다음 세 가지 질문에 순서대로 답하세요:**

> **Q1. 파일 경로가 `**/.deepx/**` 내부에 있나요?**
> - YES → **Canonical source.** 직접 수정 후 `dx-agent-gen generate` + `check` 실행.
> - NO → Q2로 이동.
>
> **Q2. 파일 경로 또는 이름이 다음 중 하나와 일치하나요?**
> ...
> **Q3. 파일이 `<!-- AUTO-GENERATED`로 시작하나요?**
> ...

1. **Canonical source** — 직접 수정.
2. **Generator output** — .deepx/ source를 수정.
3. **독립 소스** — 직접 수정.
```

---

## Rule 4: KO가 아닌 파일에는 한국어 텍스트 금지 (MANDATORY)

English fragment 파일 (`.deepx/templates/fragments/en/`) 과 모든 비-KO `.deepx/` 파일은
**오직 영문만 포함해야 합니다**. 이 규칙은 `dx-agent-gen lint` (Check 4) 와 pre-commit
hook 으로 강제됩니다.

**금지** — EN fragment 또는 agent 파일에 한국어 텍스트 삽입:

```markdown
<!-- BAD: Korean in an EN fragment -->
이 규칙은 모든 태스크에 적용됩니다.
This rule applies to all tasks.
```

**올바른 방식** — 한국어 콘텐츠는 KO 카운터파트에만 둡니다:

```markdown
<!-- en/my-rule.md -->
This rule applies to all tasks.

<!-- ko/my-rule.md -->
이 규칙은 모든 태스크에 적용됩니다.
```

### 예외: `<!-- KOREAN-OK: <reason> -->` 어노테이션

EN 파일에 한국어가 **반드시** 등장해야 하는 경우 (예: 한국어 표기 패턴 자체를 명명하는 규칙
— 에이전트가 그 패턴을 인식해야 하는 경우), 해당 라인 끝에
`<!-- KOREAN-OK: <reason> -->` 어노테이션을 추가합니다:

```markdown
Do NOT transliterate into Korean phonetics (한글 음차 표기 금지). <!-- KOREAN-OK: rule text references Korean notation term agents must recognize -->
```

```markdown
- "웹 기반 비주얼 컴패니언" (web-based visual companion) <!-- KOREAN-OK: Korean feature name included so agents recognize prohibited requests in Korean -->
```

어노테이션은 한국어 텍스트와 **동일한 라인**에 있어야 합니다.
바로 앞 주석 라인에 두는 것은 면제되지 **않습니다**.

### lint Check 4 동작

`dx-agent-gen lint` 는 KO가 아닌 모든 `.deepx/**/*.md` 파일을 스캔합니다
(파일명에 `-KO`/`_KO` 가 포함되거나 `/ko/` 디렉토리 하위인 파일은 제외).
`<!-- KOREAN-OK: ... -->` 어노테이션 없는 한국어 문자가 발견되면 `[ERROR]` 를 보고합니다.

---

## Rule 3: Commit 전 lint로 검증

Fragment 변경 후에는 항상 commit 전에 lint를 실행하세요:

```bash
dx-agent-gen lint        # 현재 repo에 대한 EN/KO parity check
# 또는 suite 전체:
bash .deepx/tools/scripts/run_all.sh lint
```

`.deepx/` 파일이 staging되면 pre-commit hook이 자동으로 lint를 실행합니다.
lint 실패는 (drift check 실패와 마찬가지로) **commit을 차단합니다**.

---

## 검증 체크리스트 (commit 전 복사-붙여넣기용)

```
[ ] EN fragment 작성: .deepx/templates/fragments/en/<name>.md
[ ] KO fragment 작성: .deepx/templates/fragments/ko/<name>.md
[ ] EN template(s)에 placeholder 추가
[ ] KO template(s)에 placeholder 추가
[ ] bash .deepx/tools/scripts/run_all.sh generate  → OK
[ ] dx-agent-gen check   → "All generated files are up-to-date."
[ ] dx-agent-gen lint    → "All EN/KO fragment pairs are consistent."
[ ] python -m pytest .deepx/tests/conformance/ -q  → 모두 통과
```

---

## 기존 Fragment 편집

동일한 규칙이 적용됩니다:

1. EN fragment를 편집하면 → 같은 commit에서 KO fragment를 편집한다.
2. EN에 새로운 Q1./Q2./Q3. 블록이 추가되면, KO에도 한국어 동등물을 추가한다.
3. Commit 전에 generate + check + lint를 실행한다.

Pre-commit hook은 commit 시점에 KO parity 누락을 잡아냅니다.
다만, **hook은 `--no-verify`로 우회 가능합니다**. lint를 수동으로 실행하는 것은
여전히 작성자의 책임입니다.
