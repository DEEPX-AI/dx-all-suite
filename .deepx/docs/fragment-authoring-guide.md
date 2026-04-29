# Fragment Authoring Guide

This document defines the rules for creating and editing fragment files under
`.deepx/templates/fragments/`. Fragments are the building blocks that get
injected into all platform instruction files (CLAUDE.md, AGENTS.md,
copilot-instructions.md, etc.) across all 5 repos.

---

## Rule 1: EN + KO Must Be Created Simultaneously (MANDATORY)

**Every new fragment MUST have both an EN and KO version created in the same commit.**

| Path | Purpose |
|------|---------|
| `.deepx/templates/fragments/en/<name>.md` | English version (canonical) |
| `.deepx/templates/fragments/ko/<name>.md` | Korean translation |

### Why

The generator injects fragments into both EN and KO platform outputs.
If the KO fragment is missing, Korean-language agents see an unrendered
`{{FRAGMENT:<name>}}` placeholder or no content — silently breaking KO outputs.

### How to add a new fragment

```bash
# 1. Write the EN version
vim .deepx/templates/fragments/en/my-new-rule.md

# 2. Write the KO version immediately (same sitting)
vim .deepx/templates/fragments/ko/my-new-rule.md

# 3. Register in the template(s) that should include it
vim .deepx/templates/en/CLAUDE.md.tmpl    # add {{FRAGMENT:my-new-rule}}
vim .deepx/templates/ko/CLAUDE-KO.md.tmpl # add {{FRAGMENT:my-new-rule}}
# (repeat for AGENTS.md.tmpl, copilot-instructions.md.tmpl as needed)

# 4. Generate and verify
bash tools/dx-agentic-dev-gen/scripts/run_all.sh generate
dx-agentic-gen check      # must report "All generated files are up-to-date."
dx-agentic-gen lint       # must report "All EN/KO fragment pairs are consistent."
```

---

## Rule 2: Structural Markers Must Be Preserved in KO (MANDATORY)

When an EN fragment contains a decision-tree blockquote (Q1./Q2./Q3. pattern),
the KO counterpart **must** include the corresponding Korean Q1./Q2./Q3. blocks.

### Structural marker pattern

A structural marker is any line matching `**Q<digit>.` — for example:

```
> **Q1. Is the file path inside `**/.deepx/**`?**
> **Q2. Does the file path match any of these?**
> **Q3. Does the file begin with `<!-- AUTO-GENERATED`?**
```

### What NOT to do

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
> - YES → **Canonical source.** 직접 수정 후 `dx-agentic-gen generate` + `check` 실행.
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

## Rule 3: Verify With lint Before Committing

After any fragment change, always run lint before committing:

```bash
dx-agentic-gen lint        # Check EN/KO parity for current repo
# or suite-wide:
bash tools/dx-agentic-dev-gen/scripts/run_all.sh lint
```

The pre-commit hook automatically runs lint when `.deepx/` files are staged.
A lint failure **blocks the commit** (same as a drift check failure).

---

## Verification Checklist (copy-paste before committing)

```
[ ] EN fragment written: .deepx/templates/fragments/en/<name>.md
[ ] KO fragment written: .deepx/templates/fragments/ko/<name>.md
[ ] Template placeholder added to EN template(s)
[ ] Template placeholder added to KO template(s)
[ ] bash tools/dx-agentic-dev-gen/scripts/run_all.sh generate  → OK
[ ] dx-agentic-gen check   → "All generated files are up-to-date."
[ ] dx-agentic-gen lint    → "All EN/KO fragment pairs are consistent."
[ ] python -m pytest tests/test_agentic_scenarios/ -q  → all pass
```

---

## Editing an Existing Fragment

Same rules apply:

1. Edit EN fragment → edit KO fragment in the same commit.
2. If EN gains a new Q1./Q2./Q3. block, add the Korean equivalent to KO.
3. Run generate + check + lint before committing.

The pre-commit hook will catch missing KO parity at commit time.
However, **the hook can be bypassed with `--no-verify`**. Running lint
manually remains the author's responsibility.
