# Fragment Authoring Guide

This document defines the rules for creating and editing fragment files under
`.deepx/templates/fragments/`. Fragments are the building blocks that get
injected into all platform instruction files (CLAUDE.md, AGENTS.md,
copilot-instructions.md, etc.) across all 5 repos.

The current `.deepx/templates/fragments/` tree holds **32 files total** (16 EN +
16 KO), and every EN file must have a same-stem KO counterpart (see Rule 1).

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
bash .deepx/tools/scripts/run_all.sh generate
dx-agent-gen check      # must report "All generated files are up-to-date."
dx-agent-gen lint       # must report "All EN/KO fragment pairs are consistent."
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

Answer three questions:

1. **Canonical source** — edit directly.
2. **Generator output** — edit `.deepx/` source.
3. **Independent source** — edit directly.
```

```markdown
<!-- GOOD: KO fragment includes both the decision tree AND the numbered list -->
### Pre-flight Classification (MANDATORY)

**Answer these three questions in order before every file edit:**

> **Q1. Is the file path inside `**/.deepx/**`?**
> - YES → **Canonical source.** Edit directly, then run `dx-agent-gen generate` + `check`.
> - NO → go to Q2.
>
> **Q2. Does the file path or name match any of these?**
> ...
> **Q3. Does the file begin with `<!-- AUTO-GENERATED`?**
> ...

1. **Canonical source** — edit directly.
2. **Generator output** — edit `.deepx/` source.
3. **Independent source** — edit directly.
```

---

## Rule 4: No Korean Text in Non-KO Files (MANDATORY)

English fragment files (`.deepx/templates/fragments/en/`) and all non-KO
`.deepx/` files MUST contain only English text. This rule is enforced by
`dx-agent-gen lint` (Check 4) and the pre-commit hook.

**Prohibited** — inserting Korean text into an EN fragment or agent file:

```markdown
<!-- BAD: Korean in an EN fragment -->
이 규칙은 모든 태스크에 적용됩니다.
This rule applies to all tasks.
```

**Correct** — Korean content goes only in the KO counterpart:

```markdown
<!-- en/my-rule.md -->
This rule applies to all tasks.

<!-- ko/my-rule.md -->
이 규칙은 모든 태스크에 적용됩니다.
```

### Exemption: `<!-- KOREAN-OK: <reason> -->`

When Korean text **must** appear in an EN file (e.g., a rule that names a Korean
notation pattern so agents can recognize it), annotate the line with
`<!-- KOREAN-OK: <reason> -->` at the end:

```markdown
Do NOT transliterate into Korean phonetics (한글 음차 표기 금지). <!-- KOREAN-OK: rule text references Korean notation term agents must recognize -->
```

```markdown
- "웹 기반 비주얼 컴패니언" (web-based visual companion) <!-- KOREAN-OK: Korean feature name included so agents recognize prohibited requests in Korean -->
```

The annotation must be on the **same line** as the Korean text.
Placing it on a preceding comment line does NOT exempt the Korean line.

### What lint checks (Check 4)

`dx-agent-gen lint` scans all `.deepx/**/*.md` files that are not KO files
(filename contains `-KO`/`_KO`, or file is under a `/ko/` directory) and reports
`[ERROR]` for any Korean character found without a `<!-- KOREAN-OK: ... -->` annotation.

---

## Rule 3: Verify With lint Before Committing

After any fragment change, always run lint before committing:

```bash
dx-agent-gen lint        # Check EN/KO parity for current repo
# or suite-wide:
bash .deepx/tools/scripts/run_all.sh lint
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
[ ] bash .deepx/tools/scripts/run_all.sh generate  → OK
[ ] dx-agent-gen check   → "All generated files are up-to-date."
[ ] dx-agent-gen lint    → "All EN/KO fragment pairs are consistent."
[ ] python -m pytest .deepx/tests/conformance/ -q  → all pass
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
