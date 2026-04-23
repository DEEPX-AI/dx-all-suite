# SPDX-License-Identifier: Apache-2.0
"""
Tests for routing table consistency across IDE configuration files.

Validates:
- CLAUDE.md and AGENTS.md reference consistent agents/skills
- copilot-instructions.md references correct agents
- opencode.json references correct agents/skills
- Cursor rules (.mdc) reference appropriate context
- All configuration files across projects are internally consistent
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Set

import pytest

from .conftest import (
    PROJECT_INFRA,
    PROJECT_ROOTS,
    ProjectInfra,
    agent_names_from_dir,
    extract_agent_references,
    extract_skill_references,
    read_markdown,
    skill_names_from_dir,
)


# ---------------------------------------------------------------------------
# CLAUDE.md tests
# ---------------------------------------------------------------------------


class TestClaudeMd:
    """CLAUDE.md files must exist where expected and reference valid agents."""

    @pytest.mark.parametrize(
        "infra", PROJECT_INFRA, ids=[p.project for p in PROJECT_INFRA]
    )
    def test_claude_md_existence(self, infra: ProjectInfra):
        """CLAUDE.md must exist if expected for this project."""
        claude_path = infra.root / "CLAUDE.md"
        if infra.has_claude_md:
            assert claude_path.exists(), (
                f"{infra.project}: Expected CLAUDE.md at {claude_path}"
            )
        else:
            # Not expected — just verify it's indeed absent (informational)
            if claude_path.exists():
                pytest.xfail(
                    f"{infra.project}: Unexpected CLAUDE.md found at {claude_path}"
                )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_claude_md],
        ids=[p.project for p in PROJECT_INFRA if p.has_claude_md],
    )
    def test_claude_md_references_valid_agents(self, infra: ProjectInfra):
        """Agent references in CLAUDE.md must point to existing agent files."""
        claude_path = infra.root / "CLAUDE.md"
        if not claude_path.exists():
            pytest.skip(f"No CLAUDE.md for {infra.project}")
        text = claude_path.read_text(encoding="utf-8")
        refs = extract_agent_references(text)
        if not refs:
            pytest.skip(f"No agent references in {infra.project}/CLAUDE.md")

        agents_dir = infra.root / ".deepx" / "agents"
        available = agent_names_from_dir(agents_dir) if agents_dir.exists() else []
        # Also check parent/sibling projects for cross-project refs
        all_available = set()
        for _, root in PROJECT_ROOTS.items():
            d = root / ".deepx" / "agents"
            if d.exists():
                all_available.update(agent_names_from_dir(d))

        missing = [r for r in set(refs) if r not in all_available]
        assert not missing, (
            f"{infra.project}/CLAUDE.md references unknown agents: {missing}\n"
            f"  Available: {sorted(all_available)}"
        )


# ---------------------------------------------------------------------------
# AGENTS.md tests
# ---------------------------------------------------------------------------


class TestAgentsMd:
    """AGENTS.md files must exist and be consistent with .deepx/ contents."""

    @pytest.mark.parametrize(
        "infra", PROJECT_INFRA, ids=[p.project for p in PROJECT_INFRA]
    )
    def test_agents_md_existence(self, infra: ProjectInfra):
        """AGENTS.md must exist for all projects."""
        agents_md = infra.root / "AGENTS.md"
        if infra.has_agents_md:
            assert agents_md.exists(), (
                f"{infra.project}: Expected AGENTS.md at {agents_md}"
            )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_agents_md and p.has_deepx],
        ids=[p.project for p in PROJECT_INFRA if p.has_agents_md and p.has_deepx],
    )
    def test_agents_md_lists_all_local_agents(self, infra: ProjectInfra):
        """AGENTS.md must mention all agents from .deepx/agents/ (by name or description).

        Note: Some AGENTS.md files list agents as @agent-name in tables,
        while others only list skills (/skill-name) and reference agents
        indirectly. We check that at least the agent filename stem appears
        in the text, OR the AGENTS.md explicitly lists skills instead.
        """
        agents_md = infra.root / "AGENTS.md"
        if not agents_md.exists():
            pytest.skip(f"No AGENTS.md for {infra.project}")
        text = agents_md.read_text(encoding="utf-8")

        agents_dir = infra.root / ".deepx" / "agents"
        if not agents_dir.exists():
            pytest.skip(f"No .deepx/agents/ for {infra.project}")

        disk_agents = agent_names_from_dir(agents_dir)
        missing = [a for a in disk_agents if a not in text]

        # Some AGENTS.md files don't list agents directly but list skills.
        # If AGENTS.md has a Skills section and lists skills, this is acceptable.
        # The heading may be "## Skills", "## All Skills (merged)", etc.
        if missing:
            has_skills_section = bool(re.search(r"(?i)##\s+.*skills", text))
            skills_dir = infra.root / ".deepx" / "skills"
            if has_skills_section and skills_dir.exists():
                disk_skills = skill_names_from_dir(skills_dir)
                skills_mentioned = [s for s in disk_skills if s in text]
                if len(skills_mentioned) > 0:
                    # AGENTS.md lists skills instead of agents — acceptable
                    return

        assert not missing, (
            f"{infra.project}/AGENTS.md does not mention agents: {missing}\n"
            f"  On disk: {disk_agents}"
        )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_agents_md and p.has_deepx],
        ids=[p.project for p in PROJECT_INFRA if p.has_agents_md and p.has_deepx],
    )
    def test_agents_md_lists_all_local_skills(self, infra: ProjectInfra):
        """AGENTS.md should mention skills from .deepx/skills/.

        Skills are listed as /dx-xxx-yyy in AGENTS.md tables. We check
        that each skill file stem appears somewhere in the AGENTS.md text.
        Some process skills (brainstorm, tdd, verify) may not be listed
        in AGENTS.md if they are runtime-internal workflows.
        """
        agents_md = infra.root / "AGENTS.md"
        if not agents_md.exists():
            pytest.skip(f"No AGENTS.md for {infra.project}")
        text = agents_md.read_text(encoding="utf-8")

        skills_dir = infra.root / ".deepx" / "skills"
        if not skills_dir.exists():
            pytest.skip(f"No .deepx/skills/ for {infra.project}")

        disk_skills = skill_names_from_dir(skills_dir)
        missing = [s for s in disk_skills if s not in text]
        # Process/internal skills may not be listed in AGENTS.md
        internal_skill_patterns = ["brainstorm", "tdd", "verify", "validate-and-fix"]
        truly_missing = [
            s for s in missing
            if not any(p in s for p in internal_skill_patterns)
        ]
        assert not truly_missing, (
            f"{infra.project}/AGENTS.md does not mention skills: {truly_missing}\n"
            f"  On disk: {disk_skills}"
        )


# ---------------------------------------------------------------------------
# Copilot instructions tests
# ---------------------------------------------------------------------------


class TestCopilotInstructions:
    """copilot-instructions.md must reference appropriate agents."""

    @pytest.mark.parametrize(
        "infra", PROJECT_INFRA, ids=[p.project for p in PROJECT_INFRA]
    )
    def test_copilot_instructions_existence(self, infra: ProjectInfra):
        """copilot-instructions.md must exist where expected."""
        copilot_path = infra.root / ".github" / "copilot-instructions.md"
        if infra.has_copilot:
            assert copilot_path.exists(), (
                f"{infra.project}: Expected {copilot_path}"
            )
        else:
            if copilot_path.exists():
                pytest.xfail(
                    f"{infra.project}: Unexpected copilot-instructions.md"
                )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_copilot],
        ids=[p.project for p in PROJECT_INFRA if p.has_copilot],
    )
    def test_copilot_references_valid_agents(self, infra: ProjectInfra):
        """Agent references in copilot-instructions.md must be valid.

        Valid means the agent is either:
        1. Present as a file in some project's .deepx/agents/, OR
        2. Listed in any project's AGENTS.md
        """
        copilot_path = infra.root / ".github" / "copilot-instructions.md"
        if not copilot_path.exists():
            pytest.skip(f"No copilot-instructions.md for {infra.project}")
        text = copilot_path.read_text(encoding="utf-8")
        refs = extract_agent_references(text)
        if not refs:
            pytest.skip(f"No agent references in {infra.project} copilot")

        # Collect agents from .deepx/agents/ files
        all_available = set()
        for _, root in PROJECT_ROOTS.items():
            d = root / ".deepx" / "agents"
            if d.exists():
                all_available.update(agent_names_from_dir(d))

        # Also collect agents listed in AGENTS.md files (may be virtual agents)
        for _, root in PROJECT_ROOTS.items():
            agents_md = root / "AGENTS.md"
            if agents_md.exists():
                md_text = agents_md.read_text(encoding="utf-8")
                all_available.update(extract_agent_references(md_text))

        missing = [r for r in set(refs) if r not in all_available]
        assert not missing, (
            f"{infra.project}/copilot-instructions.md references unknown agents: "
            f"{missing}\n  Available: {sorted(all_available)}"
        )


# ---------------------------------------------------------------------------
# OpenCode JSON tests
# ---------------------------------------------------------------------------


class TestOpenCodeJson:
    """opencode.json must exist and have valid structure."""

    @pytest.mark.parametrize(
        "infra", PROJECT_INFRA, ids=[p.project for p in PROJECT_INFRA]
    )
    def test_opencode_json_existence(self, infra: ProjectInfra):
        """opencode.json must exist where expected."""
        oc_path = infra.root / "opencode.json"
        if infra.has_opencode:
            assert oc_path.exists(), (
                f"{infra.project}: Expected opencode.json at {oc_path}"
            )
        else:
            if oc_path.exists():
                pytest.xfail(
                    f"{infra.project}: Unexpected opencode.json found"
                )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode],
    )
    def test_opencode_json_is_valid_json(self, infra: ProjectInfra):
        """opencode.json must be valid JSON."""
        oc_path = infra.root / "opencode.json"
        if not oc_path.exists():
            pytest.skip(f"No opencode.json for {infra.project}")
        try:
            data = json.loads(oc_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            pytest.fail(f"{infra.project}/opencode.json is invalid JSON: {e}")

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode],
    )
    def test_opencode_json_has_expected_keys(self, infra: ProjectInfra):
        """opencode.json should have standard configuration keys."""
        oc_path = infra.root / "opencode.json"
        if not oc_path.exists():
            pytest.skip(f"No opencode.json for {infra.project}")
        data = json.loads(oc_path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), (
            f"{infra.project}/opencode.json root must be a JSON object"
        )


# ---------------------------------------------------------------------------
# Cursor rules tests
# ---------------------------------------------------------------------------


class TestCursorRules:
    """Cursor rule files (.mdc) must exist and have valid structure."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_cursor_rules],
        ids=[p.project for p in PROJECT_INFRA if p.has_cursor_rules],
    )
    def test_cursor_rules_dir_exists(self, infra: ProjectInfra):
        """Projects should have .cursor/rules/ directory."""
        cursor_dir = infra.root / ".cursor" / "rules"
        assert cursor_dir.exists(), (
            f"{infra.project}: Expected .cursor/rules/ at {cursor_dir}"
        )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_cursor_rules],
        ids=[p.project for p in PROJECT_INFRA if p.has_cursor_rules],
    )
    def test_cursor_rules_not_empty(self, infra: ProjectInfra):
        """Cursor rules directory must contain at least one .mdc file."""
        cursor_dir = infra.root / ".cursor" / "rules"
        if not cursor_dir.exists():
            pytest.skip(f"No .cursor/rules/ for {infra.project}")
        mdc_files = list(cursor_dir.glob("*.mdc"))
        assert len(mdc_files) > 0, (
            f"{infra.project}: .cursor/rules/ has no .mdc files"
        )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_cursor_rules],
        ids=[p.project for p in PROJECT_INFRA if p.has_cursor_rules],
    )
    def test_cursor_rules_have_content(self, infra: ProjectInfra):
        """Each .mdc file must have meaningful content."""
        cursor_dir = infra.root / ".cursor" / "rules"
        if not cursor_dir.exists():
            pytest.skip(f"No .cursor/rules/ for {infra.project}")
        for mdc in cursor_dir.glob("*.mdc"):
            size = mdc.stat().st_size
            assert size > 20, (
                f"{infra.project}: Cursor rule {mdc.name} is too small ({size} bytes)"
            )


# ---------------------------------------------------------------------------
# Cross-file consistency: AGENTS.md vs CLAUDE.md
# ---------------------------------------------------------------------------


class TestCrossFileConsistency:
    """AGENTS.md and CLAUDE.md should reference the same agents for a project."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_agents_md and p.has_claude_md],
        ids=[p.project for p in PROJECT_INFRA if p.has_agents_md and p.has_claude_md],
    )
    def test_agents_md_and_claude_md_agents_overlap(self, infra: ProjectInfra):
        """Agent references in AGENTS.md and CLAUDE.md should overlap."""
        agents_md = infra.root / "AGENTS.md"
        claude_md = infra.root / "CLAUDE.md"
        if not agents_md.exists() or not claude_md.exists():
            pytest.skip(f"Missing AGENTS.md or CLAUDE.md for {infra.project}")

        agents_refs = set(extract_agent_references(
            agents_md.read_text(encoding="utf-8")
        ))
        claude_refs = set(extract_agent_references(
            claude_md.read_text(encoding="utf-8")
        ))

        if not agents_refs and not claude_refs:
            pytest.skip(f"No agent references in either file for {infra.project}")

        # CLAUDE.md should reference at least some of the same agents
        if agents_refs and claude_refs:
            overlap = agents_refs & claude_refs
            assert len(overlap) > 0, (
                f"{infra.project}: AGENTS.md and CLAUDE.md reference completely "
                f"different agents.\n"
                f"  AGENTS.md: {agents_refs}\n"
                f"  CLAUDE.md: {claude_refs}"
            )


# ---------------------------------------------------------------------------
# GitHub Agents (.github/agents/) tests
# ---------------------------------------------------------------------------


class TestGitHubAgents:
    """.github/agents/ must exist and mirror .deepx/agents/ where applicable."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_copilot],
        ids=[p.project for p in PROJECT_INFRA if p.has_copilot],
    )
    def test_github_agents_dir_exists(self, infra: ProjectInfra):
        """.github/agents/ directory must exist for Copilot-enabled projects."""
        gh_agents_dir = infra.root / ".github" / "agents"
        assert gh_agents_dir.exists(), (
            f"{infra.project}: Expected .github/agents/ at {gh_agents_dir}"
        )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_copilot and p.has_deepx],
        ids=[p.project for p in PROJECT_INFRA if p.has_copilot and p.has_deepx],
    )
    def test_github_agents_match_deepx_agents(self, infra: ProjectInfra):
        """.github/agents/ filenames must match .deepx/agents/ filenames.

        Both directories use .md files. The .github agents use .agent.md suffix
        (e.g., dx-app-builder.agent.md) while .deepx agents use plain .md.
        """
        deepx_agents_dir = infra.root / ".deepx" / "agents"
        gh_agents_dir = infra.root / ".github" / "agents"
        if not deepx_agents_dir.exists():
            pytest.skip(f"No .deepx/agents/ for {infra.project}")
        if not gh_agents_dir.exists():
            pytest.skip(f"No .github/agents/ for {infra.project}")

        deepx_names = set(agent_names_from_dir(deepx_agents_dir))
        # .github/agents/ uses *.agent.md naming convention
        gh_names = set()
        for p in sorted(gh_agents_dir.glob("*.agent.md")):
            # dx-app-builder.agent.md → dx-app-builder
            name = p.name.replace(".agent.md", "")
            gh_names.add(name)
        # Also check plain .md files (some may use that pattern)
        for p in sorted(gh_agents_dir.glob("*.md")):
            if not p.name.endswith(".agent.md"):
                gh_names.add(p.stem)

        missing_in_gh = deepx_names - gh_names
        assert not missing_in_gh, (
            f"{infra.project}: .deepx/agents/ has agents not in .github/agents/: "
            f"{sorted(missing_in_gh)}\n"
            f"  .deepx: {sorted(deepx_names)}\n"
            f"  .github: {sorted(gh_names)}"
        )


# ---------------------------------------------------------------------------
# OpenCode Agents (.opencode/agents/) tests
# ---------------------------------------------------------------------------


class TestOpenCodeAgents:
    """.opencode/agents/ must exist and mirror .deepx/agents/ where applicable."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode],
    )
    def test_opencode_agents_dir_exists(self, infra: ProjectInfra):
        """.opencode/agents/ directory must exist for OpenCode-enabled projects."""
        oc_agents_dir = infra.root / ".opencode" / "agents"
        assert oc_agents_dir.exists(), (
            f"{infra.project}: Expected .opencode/agents/ at {oc_agents_dir}"
        )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode and p.has_deepx],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode and p.has_deepx],
    )
    def test_opencode_agents_match_deepx_agents(self, infra: ProjectInfra):
        """.opencode/agents/ filenames must match .deepx/agents/ filenames."""
        deepx_agents_dir = infra.root / ".deepx" / "agents"
        oc_agents_dir = infra.root / ".opencode" / "agents"
        if not deepx_agents_dir.exists():
            pytest.skip(f"No .deepx/agents/ for {infra.project}")
        if not oc_agents_dir.exists():
            pytest.skip(f"No .opencode/agents/ for {infra.project}")

        deepx_names = set(agent_names_from_dir(deepx_agents_dir))
        oc_names = set(agent_names_from_dir(oc_agents_dir))

        missing_in_oc = deepx_names - oc_names
        assert not missing_in_oc, (
            f"{infra.project}: .deepx/agents/ has agents not in .opencode/agents/: "
            f"{sorted(missing_in_oc)}\n"
            f"  .deepx: {sorted(deepx_names)}\n"
            f"  .opencode: {sorted(oc_names)}"
        )


# ---------------------------------------------------------------------------
# Cross-platform agent parity: .deepx vs .github vs .opencode
# ---------------------------------------------------------------------------


class TestCrossPlatformAgentParity:
    """All three agent directories must list the same agent names."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_deepx and p.has_copilot and p.has_opencode],
        ids=[
            p.project
            for p in PROJECT_INFRA
            if p.has_deepx and p.has_copilot and p.has_opencode
        ],
    )
    def test_three_way_agent_parity(self, infra: ProjectInfra):
        """.deepx, .github, .opencode agent directories must list the same agents."""
        deepx_dir = infra.root / ".deepx" / "agents"
        gh_dir = infra.root / ".github" / "agents"
        oc_dir = infra.root / ".opencode" / "agents"

        if not all(d.exists() for d in [deepx_dir, gh_dir, oc_dir]):
            pytest.skip(f"Not all agent directories exist for {infra.project}")

        deepx_names = set(agent_names_from_dir(deepx_dir))

        # .github uses *.agent.md naming
        gh_names = set()
        for p in sorted(gh_dir.glob("*.agent.md")):
            gh_names.add(p.name.replace(".agent.md", ""))
        for p in sorted(gh_dir.glob("*.md")):
            if not p.name.endswith(".agent.md"):
                gh_names.add(p.stem)

        oc_names = set(agent_names_from_dir(oc_dir))

        # Check parity
        all_names = deepx_names | gh_names | oc_names
        discrepancies = []
        for name in sorted(all_names):
            present = []
            if name in deepx_names:
                present.append(".deepx")
            if name in gh_names:
                present.append(".github")
            if name in oc_names:
                present.append(".opencode")
            if len(present) < 3:
                missing = set([".deepx", ".github", ".opencode"]) - set(present)
                discrepancies.append(f"  {name}: missing in {sorted(missing)}")

        assert not discrepancies, (
            f"{infra.project}: Agent parity mismatch across platforms:\n"
            + "\n".join(discrepancies)
        )


# ---------------------------------------------------------------------------
# OpenCode Skills (.opencode/skills/) vs .deepx/skills/ parity
# ---------------------------------------------------------------------------


class TestOpenCodeSkills:
    """.opencode/skills/ must mirror .deepx/skills/ skill names."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode and p.has_deepx],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode and p.has_deepx],
    )
    def test_opencode_skills_match_deepx_skills(self, infra: ProjectInfra):
        """.opencode/skills/ must have a SKILL.md for every .deepx/skills/ skill."""
        deepx_skills_dir = infra.root / ".deepx" / "skills"
        oc_skills_dir = infra.root / ".opencode" / "skills"
        if not deepx_skills_dir.exists():
            pytest.skip(f"No .deepx/skills/ for {infra.project}")
        if not oc_skills_dir.exists():
            pytest.skip(f"No .opencode/skills/ for {infra.project}")

        deepx_names = set(skill_names_from_dir(deepx_skills_dir))
        oc_names = set(skill_names_from_dir(oc_skills_dir))

        missing_in_oc = deepx_names - oc_names
        assert not missing_in_oc, (
            f"{infra.project}: .deepx/skills/ has skills not in .opencode/skills/: "
            f"{sorted(missing_in_oc)}\n"
            f"  .deepx: {sorted(deepx_names)}\n"
            f"  .opencode: {sorted(oc_names)}"
        )


# ---------------------------------------------------------------------------
# CLAUDE.md vs AGENTS.md skill list synchronization
# ---------------------------------------------------------------------------


class TestClaudeMdAgentsMdSkillSync:
    """Skills listed in CLAUDE.md must also appear in AGENTS.md."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_claude_md and p.has_agents_md],
        ids=[p.project for p in PROJECT_INFRA if p.has_claude_md and p.has_agents_md],
    )
    def test_claude_md_skills_in_agents_md(self, infra: ProjectInfra):
        """Every skill (/dx-xxx) in CLAUDE.md must also appear in AGENTS.md."""
        claude_md = infra.root / "CLAUDE.md"
        agents_md = infra.root / "AGENTS.md"
        if not claude_md.exists() or not agents_md.exists():
            pytest.skip(f"Missing CLAUDE.md or AGENTS.md for {infra.project}")

        claude_text = claude_md.read_text(encoding="utf-8")
        agents_text = agents_md.read_text(encoding="utf-8")

        claude_skills = set(extract_skill_references(claude_text))
        agents_skills = set(extract_skill_references(agents_text))

        if not claude_skills:
            pytest.skip(f"No skill references in {infra.project}/CLAUDE.md")

        missing = claude_skills - agents_skills
        assert not missing, (
            f"{infra.project}: CLAUDE.md lists skills not in AGENTS.md: "
            f"{sorted(missing)}\n"
            f"  CLAUDE.md skills: {sorted(claude_skills)}\n"
            f"  AGENTS.md skills: {sorted(agents_skills)}"
        )


# ---------------------------------------------------------------------------
# Extended opencode.json validation: agent/skill directory references
# ---------------------------------------------------------------------------


class TestOpenCodeJsonExtended:
    """opencode.json agent/skill directory references must point to real directories."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode],
    )
    def test_opencode_json_agents_dir_exists(self, infra: ProjectInfra):
        """If opencode.json specifies an agents directory, it must exist."""
        oc_path = infra.root / "opencode.json"
        if not oc_path.exists():
            pytest.skip(f"No opencode.json for {infra.project}")
        data = json.loads(oc_path.read_text(encoding="utf-8"))
        agents_ref = data.get("agents")
        if not agents_ref:
            pytest.skip(f"No agents key in {infra.project}/opencode.json")
        agents_dir = infra.root / agents_ref
        assert agents_dir.exists(), (
            f"{infra.project}/opencode.json references agents dir "
            f"'{agents_ref}' but {agents_dir} does not exist"
        )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode],
    )
    def test_opencode_json_skills_dir_exists(self, infra: ProjectInfra):
        """If opencode.json specifies a skills directory, it must exist."""
        oc_path = infra.root / "opencode.json"
        if not oc_path.exists():
            pytest.skip(f"No opencode.json for {infra.project}")
        data = json.loads(oc_path.read_text(encoding="utf-8"))
        skills_ref = data.get("skills")
        if not skills_ref:
            pytest.skip(f"No skills key in {infra.project}/opencode.json")
        # skills can be a string path or a dict with "paths" key
        if isinstance(skills_ref, dict):
            skill_paths = skills_ref.get("paths", [])
            if not skill_paths:
                pytest.skip(
                    f"No paths in skills dict for {infra.project}/opencode.json"
                )
            missing = [
                p for p in skill_paths
                if not (infra.root / p).exists()
            ]
            assert not missing, (
                f"{infra.project}/opencode.json skills.paths references "
                f"missing directories: {missing}"
            )
        else:
            skills_dir = infra.root / skills_ref
            assert skills_dir.exists(), (
                f"{infra.project}/opencode.json references skills dir "
                f"'{skills_ref}' but {skills_dir} does not exist"
            )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_opencode],
        ids=[p.project for p in PROJECT_INFRA if p.has_opencode],
    )
    def test_opencode_json_instructions_exist(self, infra: ProjectInfra):
        """If opencode.json lists instruction files, they must all exist."""
        oc_path = infra.root / "opencode.json"
        if not oc_path.exists():
            pytest.skip(f"No opencode.json for {infra.project}")
        data = json.loads(oc_path.read_text(encoding="utf-8"))
        instructions = data.get("instructions", [])
        if not instructions:
            pytest.skip(f"No instructions in {infra.project}/opencode.json")
        missing = [f for f in instructions if not (infra.root / f).exists()]
        assert not missing, (
            f"{infra.project}/opencode.json references missing instruction files: "
            f"{missing}"
        )


# ---------------------------------------------------------------------------
# Extended Cursor rules: YAML frontmatter validation
# ---------------------------------------------------------------------------


class TestCursorRulesExtended:
    """Cursor .mdc files must have valid YAML frontmatter with description."""

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_cursor_rules],
        ids=[p.project for p in PROJECT_INFRA if p.has_cursor_rules],
    )
    def test_cursor_rules_have_frontmatter(self, infra: ProjectInfra):
        """Each .mdc file must have YAML frontmatter (--- delimited)."""
        cursor_dir = infra.root / ".cursor" / "rules"
        if not cursor_dir.exists():
            pytest.skip(f"No .cursor/rules/ for {infra.project}")
        for mdc in sorted(cursor_dir.glob("*.mdc")):
            content = mdc.read_text(encoding="utf-8")
            assert content.startswith("---"), (
                f"{infra.project}: {mdc.name} does not start with '---' "
                f"(YAML frontmatter missing)"
            )
            # Must have closing ---
            parts = content.split("---", 2)
            assert len(parts) >= 3, (
                f"{infra.project}: {mdc.name} does not have closing '---' "
                f"for YAML frontmatter"
            )

    @pytest.mark.parametrize(
        "infra",
        [p for p in PROJECT_INFRA if p.has_cursor_rules],
        ids=[p.project for p in PROJECT_INFRA if p.has_cursor_rules],
    )
    def test_cursor_rules_have_description(self, infra: ProjectInfra):
        """Each .mdc file's frontmatter must include a description field."""
        cursor_dir = infra.root / ".cursor" / "rules"
        if not cursor_dir.exists():
            pytest.skip(f"No .cursor/rules/ for {infra.project}")
        for mdc in sorted(cursor_dir.glob("*.mdc")):
            content = mdc.read_text(encoding="utf-8")
            if not content.startswith("---"):
                continue  # Skip — caught by frontmatter test
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue  # Skip — caught by frontmatter test
            frontmatter = parts[1]
            assert "description:" in frontmatter, (
                f"{infra.project}: {mdc.name} frontmatter missing 'description:' field"
            )


# ---------------------------------------------------------------------------
# Critical rules parity tests (A방식: self-contained rules at every level)
# ---------------------------------------------------------------------------


class TestCriticalRulesParity:
    """Verify that critical development rules exist at EVERY level of the
    instruction hierarchy.

    The A방식 (self-contained duplication strategy) requires that key rules
    like skeleton-first development, IFactory pattern, SyncRunner/AsyncRunner,
    and Output Isolation are present in instruction files at ALL levels —
    suite, dx-runtime, and dx_app — because git submodule boundaries prevent
    sub-level files from being auto-loaded in interactive mode.

    If any of these tests fail, it means a critical rule was removed from
    one level, breaking the A방식 guarantee.
    """

    # --- Keyword definitions ---
    # Each tuple: (rule_name, keyword_to_search)
    # The keyword must appear literally in the instruction file text.

    DXAPP_CRITICAL_KEYWORDS = [
        ("skeleton-first", "Skeleton-first development"),
        ("ifactory-pattern", "IFactory pattern"),
        ("syncrunner-asyncrunner", "SyncRunner"),
        ("output-isolation", "dx-agentic-dev/"),
        ("no-standalone-scripts", "NEVER write demo scripts from scratch"),
    ]

    COMMON_CRITICAL_KEYWORDS = [
        ("output-isolation-section", "Output Isolation"),
        ("brainstorming-hard-gate", "Brainstorming"),
        ("no-placeholder-code", "No Placeholder Code"),
        ("rule-conflict-resolution", "Rule Conflict Resolution"),
    ]

    # Keywords for the Rule Conflict Resolution section specifically
    RULE_CONFLICT_KEYWORDS = [
        ("user-api-override-guard", "Even if the user explicitly names API methods"),
        ("silent-compliance-violation", "silent compliance is always a violation"),
        ("conflict-ifactory-example", "InferenceEngine.run()"),
    ]

    # --- File path helpers ---

    @staticmethod
    def _instruction_files_for_level(root: Path) -> List[Path]:
        """Return all instruction files (CLAUDE.md, AGENTS.md,
        copilot-instructions.md) that exist at the given root."""
        candidates = [
            root / "CLAUDE.md",
            root / "AGENTS.md",
            root / ".github" / "copilot-instructions.md",
        ]
        return [p for p in candidates if p.exists()]

    # --- Suite level tests ---

    @pytest.mark.parametrize(
        "rule_name,keyword",
        DXAPP_CRITICAL_KEYWORDS,
        ids=[k[0] for k in DXAPP_CRITICAL_KEYWORDS],
    )
    def test_suite_level_has_dxapp_rules(self, rule_name: str, keyword: str):
        """Suite-level instruction files must contain dx_app critical rules."""
        suite_root = PROJECT_ROOTS["suite"]
        files = self._instruction_files_for_level(suite_root)
        assert files, "No instruction files found at suite level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"suite/{fpath.name} missing dx_app critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    @pytest.mark.parametrize(
        "rule_name,keyword",
        COMMON_CRITICAL_KEYWORDS,
        ids=[k[0] for k in COMMON_CRITICAL_KEYWORDS],
    )
    def test_suite_level_has_common_rules(self, rule_name: str, keyword: str):
        """Suite-level instruction files must contain common critical rules."""
        suite_root = PROJECT_ROOTS["suite"]
        files = self._instruction_files_for_level(suite_root)
        assert files, "No instruction files found at suite level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"suite/{fpath.name} missing common critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    # --- dx-runtime level tests ---

    @pytest.mark.parametrize(
        "rule_name,keyword",
        DXAPP_CRITICAL_KEYWORDS,
        ids=[k[0] for k in DXAPP_CRITICAL_KEYWORDS],
    )
    def test_runtime_level_has_dxapp_rules(self, rule_name: str, keyword: str):
        """dx-runtime instruction files must contain dx_app critical rules."""
        runtime_root = PROJECT_ROOTS["runtime"]
        files = self._instruction_files_for_level(runtime_root)
        assert files, "No instruction files found at dx-runtime level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"runtime/{fpath.name} missing dx_app critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    @pytest.mark.parametrize(
        "rule_name,keyword",
        COMMON_CRITICAL_KEYWORDS,
        ids=[k[0] for k in COMMON_CRITICAL_KEYWORDS],
    )
    def test_runtime_level_has_common_rules(self, rule_name: str, keyword: str):
        """dx-runtime instruction files must contain common critical rules."""
        runtime_root = PROJECT_ROOTS["runtime"]
        files = self._instruction_files_for_level(runtime_root)
        assert files, "No instruction files found at dx-runtime level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"runtime/{fpath.name} missing common critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    # --- dx_app level tests ---

    @pytest.mark.parametrize(
        "rule_name,keyword",
        DXAPP_CRITICAL_KEYWORDS,
        ids=[k[0] for k in DXAPP_CRITICAL_KEYWORDS],
    )
    def test_app_level_has_dxapp_rules(self, rule_name: str, keyword: str):
        """dx_app instruction files must contain dx_app critical rules."""
        app_root = PROJECT_ROOTS["app"]
        files = self._instruction_files_for_level(app_root)
        assert files, "No instruction files found at dx_app level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"app/{fpath.name} missing dx_app critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    @pytest.mark.parametrize(
        "rule_name,keyword",
        COMMON_CRITICAL_KEYWORDS,
        ids=[k[0] for k in COMMON_CRITICAL_KEYWORDS],
    )
    def test_app_level_has_common_rules(self, rule_name: str, keyword: str):
        """dx_app instruction files must contain common critical rules."""
        app_root = PROJECT_ROOTS["app"]
        files = self._instruction_files_for_level(app_root)
        assert files, "No instruction files found at dx_app level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"app/{fpath.name} missing common critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    # --- Sub-Project Development Rules section parity ---

    # --- dx-compiler level tests ---

    @pytest.mark.parametrize(
        "rule_name,keyword",
        COMMON_CRITICAL_KEYWORDS,
        ids=[k[0] for k in COMMON_CRITICAL_KEYWORDS],
    )
    def test_compiler_level_has_common_rules(self, rule_name: str, keyword: str):
        """dx-compiler instruction files must contain common critical rules."""
        compiler_root = PROJECT_ROOTS["compiler"]
        files = self._instruction_files_for_level(compiler_root)
        assert files, "No instruction files found at dx-compiler level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"compiler/{fpath.name} missing common critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    # --- dx_stream level tests ---

    @pytest.mark.parametrize(
        "rule_name,keyword",
        COMMON_CRITICAL_KEYWORDS,
        ids=[k[0] for k in COMMON_CRITICAL_KEYWORDS],
    )
    def test_stream_level_has_common_rules(self, rule_name: str, keyword: str):
        """dx_stream instruction files must contain common critical rules."""
        stream_root = PROJECT_ROOTS["stream"]
        files = self._instruction_files_for_level(stream_root)
        assert files, "No instruction files found at dx_stream level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"stream/{fpath.name} missing common critical rule '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    # --- Sub-Project Development Rules section parity ---

    def test_suite_level_sub_project_rules_self_contained(self):
        """Suite-level Sub-Project Development Rules must be marked SELF-CONTAINED."""
        suite_root = PROJECT_ROOTS["suite"]
        for fpath in self._instruction_files_for_level(suite_root):
            text = fpath.read_text(encoding="utf-8")
            assert "SELF-CONTAINED" in text, (
                f"suite/{fpath.name}: Sub-Project Development Rules section must "
                f"be marked 'SELF-CONTAINED' (A방식 requirement)"
            )

    def test_runtime_level_has_sub_project_rules(self):
        """dx-runtime must have its own Sub-Project Development Rules section."""
        runtime_root = PROJECT_ROOTS["runtime"]
        for fpath in self._instruction_files_for_level(runtime_root):
            text = fpath.read_text(encoding="utf-8")
            assert "Sub-Project Development Rules" in text, (
                f"runtime/{fpath.name}: must have 'Sub-Project Development Rules' "
                f"section (A방식 requirement)"
            )

    # --- Rule Conflict Resolution parity (suite + runtime levels) ---

    @pytest.mark.parametrize(
        "rule_name,keyword",
        RULE_CONFLICT_KEYWORDS,
        ids=[k[0] for k in RULE_CONFLICT_KEYWORDS],
    )
    def test_suite_level_has_rule_conflict_keywords(self, rule_name: str, keyword: str):
        """Suite-level instruction files must contain Rule Conflict Resolution details."""
        suite_root = PROJECT_ROOTS["suite"]
        files = self._instruction_files_for_level(suite_root)
        assert files, "No instruction files found at suite level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"suite/{fpath.name} missing Rule Conflict Resolution detail '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    @pytest.mark.parametrize(
        "rule_name,keyword",
        RULE_CONFLICT_KEYWORDS,
        ids=[k[0] for k in RULE_CONFLICT_KEYWORDS],
    )
    def test_runtime_level_has_rule_conflict_keywords(self, rule_name: str, keyword: str):
        """dx-runtime instruction files must contain Rule Conflict Resolution details."""
        runtime_root = PROJECT_ROOTS["runtime"]
        files = self._instruction_files_for_level(runtime_root)
        assert files, "No instruction files found at dx-runtime level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"runtime/{fpath.name} missing Rule Conflict Resolution detail '{rule_name}' "
                f"(expected keyword: '{keyword}')"
            )

    def test_suite_brainstorming_has_conflict_check(self):
        """Suite-level Brainstorming HARD GATE must include rule conflict check."""
        suite_root = PROJECT_ROOTS["suite"]
        for fpath in self._instruction_files_for_level(suite_root):
            text = fpath.read_text(encoding="utf-8")
            assert "Rule conflict check is MANDATORY" in text, (
                f"suite/{fpath.name}: Brainstorming HARD GATE must include "
                f"'Rule conflict check is MANDATORY' (session 402107c1 fix)"
            )

    @pytest.mark.parametrize(
        "level",
        ["compiler", "runtime", "app", "stream"],
    )
    def test_all_sub_levels_brainstorming_has_conflict_check(self, level: str):
        """All sub-levels must have Brainstorming rule #5 (rule conflict check)."""
        root = PROJECT_ROOTS[level]
        files = self._instruction_files_for_level(root)
        assert files, f"No instruction files found at {level} level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert "Rule conflict check is MANDATORY" in text, (
                f"{level}/{fpath.name}: Brainstorming section must include "
                f"'Rule conflict check is MANDATORY' — propagated from suite level"
            )

    def test_app_level_has_rule_conflict_resolution(self):
        """dx_app instruction files must have Rule Conflict Resolution section."""
        app_root = PROJECT_ROOTS["app"]
        for fpath in self._instruction_files_for_level(app_root):
            text = fpath.read_text(encoding="utf-8")
            assert "Rule Conflict Resolution" in text, (
                f"app/{fpath.name}: must have 'Rule Conflict Resolution' section"
            )

    # --- Autopilot Mode Guard parity (rules #6-#7 at ALL levels) ---

    AUTOPILOT_EFFICIENCY_KEYWORDS = [
        ("time-budget-awareness", "Time budget awareness"),
        ("minimize-file-reading", "Minimize file-reading tool calls"),
        ("compilation-parallel-workflow-hard-gate", "Compilation-parallel workflow (HARD GATE)"),
        ("never-sleep-poll", "NEVER sleep-poll for compilation"),
        ("mandatory-artifacts-compilation-independent", "Mandatory artifacts are compilation-independent"),
    ]

    @pytest.mark.parametrize(
        "rule_name,keyword",
        AUTOPILOT_EFFICIENCY_KEYWORDS,
        ids=[k[0] for k in AUTOPILOT_EFFICIENCY_KEYWORDS],
    )
    @pytest.mark.parametrize(
        "level",
        ["suite", "compiler", "runtime", "app", "stream"],
    )
    def test_all_levels_have_autopilot_efficiency_rules(
        self, level: str, rule_name: str, keyword: str
    ):
        """ALL levels must contain autopilot efficiency rules (#6-#7)."""
        root = PROJECT_ROOTS[level]
        files = self._instruction_files_for_level(root)
        assert files, f"No instruction files found at {level} level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"{level}/{fpath.name} missing autopilot efficiency rule "
                f"'{rule_name}' (expected keyword: '{keyword}')"
            )

    # --- Session ID local timezone parity (all levels) ---

    SESSION_ID_TIMEZONE_KEYWORDS = [
        ("session-id-local-timezone", "system local timezone"),
    ]

    @pytest.mark.parametrize(
        "rule_name,keyword",
        SESSION_ID_TIMEZONE_KEYWORDS,
        ids=[k[0] for k in SESSION_ID_TIMEZONE_KEYWORDS],
    )
    def test_suite_level_has_session_id_timezone_rule(self, rule_name: str, keyword: str):
        """Suite-level instruction files must specify local timezone for session IDs."""
        suite_root = PROJECT_ROOTS["suite"]
        files = self._instruction_files_for_level(suite_root)
        assert files, "No instruction files found at suite level"

        for fpath in files:
            text = fpath.read_text(encoding="utf-8")
            assert keyword in text, (
                f"suite/{fpath.name} missing session ID timezone rule '{rule_name}' "
                f"(expected keyword: '{keyword}'). "
                f"E2E Round 7 showed agent using UTC timestamps instead of local "
                f"timezone for session directory naming."
            )


# ---------------------------------------------------------------------------
# Stale path reference tests
# ---------------------------------------------------------------------------


class TestNoStaleOpenCodeSkillsRefs:
    """Instruction and documentation files must not reference .opencode/skills/
    after migration to .deepx/skills/."""

    INSTRUCTION_GLOBS = [
        "CLAUDE.md", "CLAUDE-KO.md",
        "AGENTS.md", "AGENTS-KO.md",
        ".github/copilot-instructions.md", ".github/copilot-instructions-KO.md",
    ]

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items()],
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_no_stale_opencode_skills_in_instruction_files(self, project: str, root: Path):
        """No instruction file should reference .opencode/skills/ (migrated to .deepx/skills/)."""
        violations = []
        for pattern in self.INSTRUCTION_GLOBS:
            fpath = root / pattern
            if fpath.exists():
                text = fpath.read_text(encoding="utf-8")
                if ".opencode/skills/" in text:
                    violations.append(fpath.name)
        assert not violations, (
            f"{project}: Stale .opencode/skills/ references in: {violations}. "
            f"Skills have been migrated to .deepx/skills/."
        )

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items()],
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_no_stale_opencode_skills_in_docs(self, project: str, root: Path):
        """No documentation file should reference .opencode/skills/."""
        violations = []
        for md_file in root.rglob("docs/**/*.md"):
            text = md_file.read_text(encoding="utf-8")
            if ".opencode/skills/" in text:
                violations.append(str(md_file.relative_to(root)))
        assert not violations, (
            f"{project}: Stale .opencode/skills/ references in docs: {violations}. "
            f"Skills have been migrated to .deepx/skills/."
        )


# ---------------------------------------------------------------------------
# Copilot CLI skill discovery tests
# ---------------------------------------------------------------------------


class TestGitHubSkillsSymlink:
    """.github/skills must be a symlink to .deepx/skills/ for Copilot CLI discovery."""

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items()],
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_skills_symlink_exists(self, project: str, root: Path):
        """.github/skills must exist (as symlink or directory)."""
        github_skills = root / ".github" / "skills"
        assert github_skills.exists(), (
            f"{project}: .github/skills does not exist. "
            f"Copilot CLI discovers skills from .github/skills/. "
            f"Run: dx-agentic-gen generate"
        )

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items()],
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_skills_is_not_symlink(self, project: str, root: Path):
        """.github/skills should be a real directory (inline copy), not a symlink."""
        github_skills = root / ".github" / "skills"
        if not github_skills.exists():
            pytest.skip(f"{project}: .github/skills does not exist")
        assert not github_skills.is_symlink(), (
            f"{project}: .github/skills is still a symlink. "
            f"Generator should produce inline copies, not symlinks. "
            f"Remove symlink and run: dx-agentic-gen generate"
        )

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items()],
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_skills_contains_skill_files(self, project: str, root: Path):
        """Skills visible via .github/skills/ must have SKILL.md with YAML frontmatter."""
        github_skills = root / ".github" / "skills"
        if not github_skills.exists():
            pytest.skip(f"{project}: .github/skills does not exist")
        skill_dirs = [
            d for d in sorted(github_skills.iterdir())
            if d.is_dir() and (d / "SKILL.md").exists()
        ]
        assert skill_dirs, (
            f"{project}: .github/skills/ has no skill subdirectories with SKILL.md"
        )
        missing_frontmatter = []
        for d in skill_dirs:
            content = (d / "SKILL.md").read_text(encoding="utf-8")
            if not content.startswith("---"):
                missing_frontmatter.append(d.name)
        assert not missing_frontmatter, (
            f"{project}: Skills missing YAML frontmatter: {missing_frontmatter}. "
            f"Copilot CLI requires ---\\nname: ...\\ndescription: ...\\n--- at top of SKILL.md"
        )


# ---------------------------------------------------------------------------
# argument-hint sync between .deepx/agents/ and .github/agents/
# ---------------------------------------------------------------------------


class TestArgumentHintSync:
    """Agents with argument-hint in .deepx/agents/ must have it in .github/agents/ too."""

    @staticmethod
    def _extract_argument_hint(path: Path) -> str | None:
        """Extract argument-hint value from YAML frontmatter (parsed, not raw)."""
        import yaml

        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            return None
        end = text.find("\n---", 3)
        if end == -1:
            return None
        try:
            fm = yaml.safe_load(text[3:end]) or {}
        except yaml.YAMLError:
            return None
        hint = fm.get("argument-hint")
        return str(hint) if hint is not None else None

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_agents_have_argument_hint(self, project: str, root: Path):
        """Every .github/agents/ file that has a .deepx/agents/ counterpart
        with argument-hint must also contain the same argument-hint."""
        deepx_agents = root / ".deepx" / "agents"
        github_agents = root / ".github" / "agents"
        if not deepx_agents.exists() or not github_agents.exists():
            pytest.skip(f"{project}: missing .deepx/agents/ or .github/agents/")

        missing = []
        mismatched = []
        for deepx_file in sorted(deepx_agents.glob("*.md")):
            hint = self._extract_argument_hint(deepx_file)
            if not hint:
                continue
            # .github counterpart uses .agent.md extension
            gh_file = github_agents / f"{deepx_file.stem}.agent.md"
            if not gh_file.exists():
                continue
            gh_hint = self._extract_argument_hint(gh_file)
            if gh_hint is None:
                missing.append(deepx_file.stem)
            elif gh_hint != hint:
                mismatched.append(f"{deepx_file.stem}: deepx={hint!r} github={gh_hint!r}")

        assert not missing, (
            f"{project}: .github/agents/ missing argument-hint for: {missing}"
        )
        assert not mismatched, (
            f"{project}: argument-hint mismatch: {mismatched}"
        )
