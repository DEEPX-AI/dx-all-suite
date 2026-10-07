# SPDX-License-Identifier: Apache-2.0
"""
Tests for dx_agent_dev_gen.transformers.rewrite_deepx_to_github.

Root cause (polish round P4): no repo in the suite ships a `.github/toolsets/`
directory — toolsets live only under `.deepx/toolsets/`. The old rewrite rule
turned `.deepx/toolsets/x.md` references into `.github/toolsets/x.md`, which
is a dangling path in every generated copilot agent that cited a toolset
(e.g. dx-runtime/dx_app/.github/agents/dx-model-manager.agent.md pointing at
".github/toolsets/model-registry.md", which does not exist). Toolset
references must be left as `.deepx/toolsets/...` for copilot output too.

Root cause (polish round Q1, same defect class): no repo ships `.github/memory/`
or `.github/knowledge/` either. `dx_app`/`dx_stream` DO have a `.github/instructions/`
directory, but it holds hand-authored VS Code `*.instructions.md` files — a
different set from `.deepx/instructions/`. So `.deepx/instructions/`,
`.deepx/memory/`, `.deepx/knowledge/` references must ALSO be left unrewritten
for copilot output (only `.deepx/agents/` and `.deepx/skills/` have a real
`.github/` counterpart that the generator itself creates).
"""

from __future__ import annotations


def test_toolsets_reference_left_as_deepx(tmp_path):
    from dx_agent_dev_gen.transformers import rewrite_deepx_to_github

    body = "See `.deepx/toolsets/model-registry.md` for the schema.\n"
    out = rewrite_deepx_to_github(body)
    assert ".deepx/toolsets/model-registry.md" in out
    assert ".github/toolsets/" not in out


def test_other_deepx_dirs_still_rewritten_to_github(tmp_path):
    """Only .deepx/agents/ and .deepx/skills/ are rewritten to .github/ —
    those are the only two dirs the generator actually creates under
    .github/. memory/knowledge/instructions have no .github/ counterpart in
    any repo and must survive unchanged."""
    from dx_agent_dev_gen.transformers import rewrite_deepx_to_github

    body = (
        "Agent: .deepx/agents/x.md\n"
        "Skill: .deepx/skills/y.md\n"
        "Memory: .deepx/memory/z.md\n"
        "Knowledge: .deepx/knowledge/k.md\n"
        "Instructions: .deepx/instructions/i.md\n"
    )
    out = rewrite_deepx_to_github(body)
    assert ".github/agents/x.agent.md" in out
    assert ".github/skills/y.md" in out
    assert ".deepx/memory/z.md" in out
    assert ".deepx/knowledge/k.md" in out
    assert ".deepx/instructions/i.md" in out
    assert ".github/memory/" not in out
    assert ".github/knowledge/" not in out
    assert ".github/instructions/" not in out


def test_cross_repo_agent_reference_gets_agent_md_suffix(tmp_path):
    """A cross-repo agent reference written in .deepx/ canonical form (e.g.
    "dx_app/.deepx/agents/dx-app-builder.md" — correct for Claude/OpenCode/
    Cursor, which read .deepx/ directly and never rename the file) must gain
    the ".agent.md" suffix when rewritten for copilot output, because
    _generate_copilot always writes agent files as "<stem>.agent.md". Root
    cause (polish round Q2 follow-up): the old generic
    ".deepx/agents/" -> ".github/agents/" replace left the referenced
    filename unchanged, producing a dangling
    "dx_app/.github/agents/dx-app-builder.md" (real file is
    "dx-app-builder.agent.md") in every generated copilot agent that
    mentioned a sibling project's agent by its canonical .deepx/ path."""
    from dx_agent_dev_gen.transformers import rewrite_deepx_to_github

    body = (
        "Route to `dx_app/.deepx/agents/dx-app-builder.md` when needed.\n"
        "Route to `dx_stream/.deepx/agents/dx-stream-builder.md` when needed.\n"
        "Same-repo: `.deepx/agents/dx-validator.md` handles this.\n"
    )
    out = rewrite_deepx_to_github(body)
    assert "dx_app/.github/agents/dx-app-builder.agent.md" in out
    assert "dx_stream/.github/agents/dx-stream-builder.agent.md" in out
    assert ".github/agents/dx-validator.agent.md" in out
    assert "dx-app-builder.md`" not in out
    assert "dx-stream-builder.md`" not in out
    assert "dx-validator.md`" not in out


def test_cross_repo_agent_reference_with_underscore_in_name(tmp_path):
    """polish round F5: the agent-suffix regex used [a-z0-9-]+, which cannot
    match an agent stem containing an underscore (e.g. a hypothetical
    "dx_model_manager.md") — widened to [\\w-]+ so any word-character/dash
    stem gets the .agent.md suffix, not just lowercase-dash ones."""
    from dx_agent_dev_gen.transformers import rewrite_deepx_to_github

    body = "See `.deepx/agents/dx_model_manager.md` for details.\n"
    out = rewrite_deepx_to_github(body)
    assert ".github/agents/dx_model_manager.agent.md" in out
    assert "dx_model_manager.md`" not in out


def test_prose_deepx_mentions_left_unrewritten(tmp_path):
    """polish round F6: the blanket "in `.deepx/`" / "relative to `.deepx/`"
    prose rewrites contradicted the NOTE above them (only agents/skills have
    a real .github/ counterpart) — e.g. "33 files in `.deepx/`" (describing
    the WHOLE framework, or a script like validate_framework.py that isn't
    part of copilot generation at all) became "33 files in `.github/`" for
    copilot output, which is false: copilot only mirrors agents/skills, not
    the whole framework or its scripts. Removed; these sentences must stay
    `.deepx/`-form for copilot output too, exactly like claude/opencode/
    cursor (which never rewrite them at all)."""
    from dx_agent_dev_gen.transformers import rewrite_deepx_to_github

    body = (
        "Framework scope: 33 files in `.deepx/` including agents, skills.\n"
        "See `validate_framework.py` in `.deepx/` for the checker.\n"
        "A change in `.deepx/` triggers regeneration.\n"
        "The fix is relative to `.deepx/` root.\n"
    )
    out = rewrite_deepx_to_github(body)
    assert "in `.deepx/`" in out
    assert "relative to `.deepx/`" in out
    assert "in `.github/`" not in out
    assert "relative to `.github/`" not in out
