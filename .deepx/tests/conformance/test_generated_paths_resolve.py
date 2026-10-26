# SPDX-License-Identifier: Apache-2.0
"""
Guard against dangling agent/skill path references in generated output —
copilot (`.github/...`) as well as the `.deepx/...`-form references that
claude/opencode/cursor consume directly.

Root cause (polish round P4 + Q1): the generator's `rewrite_deepx_to_github`
used to blanket-rewrite `.deepx/toolsets/`, `.deepx/instructions/`,
`.deepx/memory/` and `.deepx/knowledge/` references to `.github/...`
equivalents that no repo actually ships (only `.deepx/agents/` and
`.deepx/skills/` have a real `.github/` counterpart — the generator itself
creates those two). Root cause (Q2 follow-up): several canonical
`.deepx/agents/`/`.deepx/skills/` sources also cited a sibling project's
agent/skill file by a STALE or wrong-suffix filename (e.g. a pre-rename
`dx-tdd.md` instead of `dx-agent-tdd/SKILL.md`, or a cross-repo agent path
missing the `.agent.md` suffix that copilot output always uses) — fixed at
the source (the stale name was wrong for every platform) or in
`rewrite_deepx_to_github` (the missing `.agent.md` suffix is a copilot-only
transform, since claude/opencode/cursor read `.deepx/` paths unrewritten).

This test scans every generated copilot agent/skill file (`.github/agents/*.md`,
`.github/skills/**/*.md`) — whose bodies DO go through `rewrite_deepx_to_github`
— for a `.github/<dir>/...` reference; `.github/copilot-instructions*.md` for
BOTH `.github/<dir>/...` AND `.deepx/<dir>/...` references (its body is built
by `_generate_instructions()`, which never calls `rewrite_deepx_to_github` —
so any `.deepx/` path in it stays verbatim by construction, exactly like
CLAUDE.md/AGENTS.md; scanning both patterns is a robustness margin in case a
`.github/...` path is ever hardcoded there too); and every generated
claude/opencode/cursor file (`.claude/agents/*.md`, `.claude/skills/**/*.md`,
`.opencode/agents/*.md`, `.cursor/rules/*.mdc`) plus the top-level `CLAUDE.md`,
`CLAUDE-KO.md`, `AGENTS.md`, `AGENTS-KO.md` (when present) for a
`.deepx/<dir>/...` reference. Each match is asserted to resolve to a real file
relative to that project's root, so this class of dangling reference cannot
silently reappear on any platform.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Tuple

import pytest

from .conftest import PROJECT_ROOTS

# Pattern for a .github/<dir>/<path>.<ext> reference worth checking. A
# reference is often written with a leading cross-repo path prefix (e.g.
# "dx-runtime/dx_app/.github/skills/x.md" inside a suite-level doc) — that
# prefix is captured too (when contiguous, i.e. not separated by a backtick
# or space) so the reference is resolved against the right root instead of
# being truncated to a bare ".github/..." path that falsely looks dangling.
GITHUB_REF_PATTERN = re.compile(
    r"(?:[\w.-]+/)*"
    r"\.github/(?:agents|skills|instructions|memory|knowledge|toolsets)/"
    r"[\w./-]+\.(?:md|yaml|json|mdc)"
)

# Same idea, but for the .deepx/-form references that claude/opencode/cursor
# output carries unrewritten (they read .deepx/ directly).
DEEPX_REF_PATTERN = re.compile(
    r"(?:[\w.-]+/)*"
    r"\.deepx/(?:agents|skills|instructions|memory|knowledge|toolsets)/"
    r"[\w./-]+\.(?:md|yaml|json|mdc)"
)


def _platform_files(root: Path) -> List[Tuple[Path, List["re.Pattern[str]"]]]:
    """Return (file, patterns) pairs — which reference pattern(s) apply
    depends on which platform generated the file: copilot agent/skill output
    (`.github/agents,skills`) uses `.github/...` refs, since their bodies go
    through `rewrite_deepx_to_github`; claude/opencode/cursor output, the
    top-level CLAUDE.md/AGENTS.md, and copilot-instructions*.md all keep the
    `.deepx/...` form as-is (copilot-instructions*.md's body is built by
    `_generate_instructions()`, which never calls `rewrite_deepx_to_github`)
    — copilot-instructions*.md is scanned with BOTH patterns anyway as a
    robustness margin in case a `.github/...` path is ever hardcoded there
    too, plus `.deepx/memory/*.md` for the same reason knowledge-base memory
    files cross-reference other repos' agents/skills."""
    files: List[Tuple[Path, List["re.Pattern[str]"]]] = []

    agents_dir = root / ".github" / "agents"
    if agents_dir.is_dir():
        files += [(p, [GITHUB_REF_PATTERN]) for p in sorted(agents_dir.glob("*.md")) if p.is_file()]
    skills_dir = root / ".github" / "skills"
    if skills_dir.is_dir():
        files += [(p, [GITHUB_REF_PATTERN]) for p in sorted(skills_dir.glob("**/*.md")) if p.is_file()]
    github_dir = root / ".github"
    if github_dir.is_dir():
        files += [
            (p, [GITHUB_REF_PATTERN, DEEPX_REF_PATTERN])
            for p in sorted(github_dir.glob("copilot-instructions*.md"))
            if p.is_file()
        ]
    # .github/instructions/*.instructions.md — hand-authored VS Code
    # instructions files (dx_app/dx_stream only). Not generator output, but
    # they cite .deepx/ agent/skill paths verbatim, same as claude/opencode.
    github_instructions = root / ".github" / "instructions"
    if github_instructions.is_dir():
        files += [
            (p, [DEEPX_REF_PATTERN])
            for p in sorted(github_instructions.glob("*.instructions.md"))
            if p.is_file()
        ]

    claude_agents = root / ".claude" / "agents"
    if claude_agents.is_dir():
        files += [(p, [DEEPX_REF_PATTERN]) for p in sorted(claude_agents.glob("*.md")) if p.is_file()]
    claude_skills = root / ".claude" / "skills"
    if claude_skills.is_dir():
        files += [(p, [DEEPX_REF_PATTERN]) for p in sorted(claude_skills.glob("**/*.md")) if p.is_file()]
    opencode_agents = root / ".opencode" / "agents"
    if opencode_agents.is_dir():
        files += [(p, [DEEPX_REF_PATTERN]) for p in sorted(opencode_agents.glob("*.md")) if p.is_file()]
    cursor_rules = root / ".cursor" / "rules"
    if cursor_rules.is_dir():
        files += [(p, [DEEPX_REF_PATTERN]) for p in sorted(cursor_rules.glob("*.mdc")) if p.is_file()]
    memory_dir = root / ".deepx" / "memory"
    if memory_dir.is_dir():
        files += [(p, [DEEPX_REF_PATTERN]) for p in sorted(memory_dir.glob("*.md")) if p.is_file()]

    for name in ("CLAUDE.md", "CLAUDE-KO.md", "AGENTS.md", "AGENTS-KO.md"):
        p = root / name
        if p.is_file():
            files.append((p, [DEEPX_REF_PATTERN]))

    return files


def _extract_refs(text: str, patterns: List["re.Pattern[str]"]) -> List[str]:
    refs = []
    for pattern in patterns:
        for m in pattern.finditer(text):
            ref = m.group(0)
            # Skip placeholder-style matches (shouldn't normally occur given
            # the pattern's character class, but guard defensively per spec).
            if any(c in ref for c in ("<", "*", "{")):
                continue
            refs.append(ref)
    return refs


def _dangling_refs(root: Path) -> List[Tuple[Path, str]]:
    """Return (file, ref) pairs whose path reference does not resolve.

    A reference is always resolved relative to the generating file's OWN
    project root — whether it's a bare "<platform-dir>/agents/x.md"
    (same-repo) or carries a leading cross-repo prefix (e.g.
    "dx_app/.deepx/agents/x.md" inside a dx-runtime doc, or
    "dx-runtime/dx_app/.github/skills/x.md" inside a suite-level doc): in
    both cases the prefix is itself a path relative to that file's own root,
    so `root / ref` resolves it correctly without needing to special-case
    which root the prefix implies.
    """
    dangling: List[Tuple[Path, str]] = []
    for f, patterns in _platform_files(root):
        text = f.read_text(encoding="utf-8", errors="replace")
        for ref in _extract_refs(text, patterns):
            if not (root / ref).exists():
                dangling.append((f, ref))
    return dangling


@pytest.mark.parametrize("project", sorted(PROJECT_ROOTS), ids=sorted(PROJECT_ROOTS))
def test_no_dangling_agent_skill_path_references(project: str):
    """Every agent/skill path reference in generated output — `.github/...`
    (copilot) or `.deepx/...` (claude/opencode/cursor) — must resolve to a
    real file relative to the project root."""
    root = PROJECT_ROOTS[project]
    dangling = _dangling_refs(root)
    if dangling:
        details = "\n".join(
            f"  {f.relative_to(root)}: {ref}" for f, ref in dangling
        )
        pytest.fail(
            f"{project}: {len(dangling)} dangling path reference(s) in "
            f"generated output:\n{details}"
        )
