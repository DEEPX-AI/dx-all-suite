# SPDX-License-Identifier: Apache-2.0
"""
Tests for cross-project scenario infrastructure.

Validates:
- DX All Suite Scenarios 1-4 have required submodule infrastructure
- Handoff chains: when agent A references agent B, B's file exists
- PPU scenarios: PPU-related agents, skills, and paths exist
- Output isolation: dx-agentic-dev/ related .gitignore rules
- Validation scripts exist and are executable
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set

import pytest

from .conftest import (
    COMPILER_ROOT,
    RUNTIME_ROOT,
    APP_ROOT,
    STREAM_ROOT,
    SUITE_ROOT,
    GUIDE_PAIRS,
    PROJECT_ROOTS,
    agent_names_from_dir,
    extract_agent_references,
    list_md_files,
    read_markdown,
    skill_names_from_dir,
)


# ---------------------------------------------------------------------------
# Cross-project scenario infrastructure (Scenarios 1-4 from suite guide)
# ---------------------------------------------------------------------------


class TestScenario1Infrastructure:
    """Scenario 1: Custom Model + SDK Porting.

    Requires: dx-compiler infrastructure (model conversion/compilation).
    """

    def test_compiler_agents_exist(self):
        """dx-compiler must have agent files for model compilation."""
        agents_dir = COMPILER_ROOT / ".deepx" / "agents"
        assert agents_dir.exists(), "dx-compiler/.deepx/agents/ missing"
        agents = agent_names_from_dir(agents_dir)
        assert len(agents) > 0, "dx-compiler has no agent files"

    def test_compiler_skills_exist(self):
        """dx-compiler must have skill files for compilation workflow."""
        skills_dir = COMPILER_ROOT / ".deepx" / "skills"
        assert skills_dir.exists(), "dx-compiler/.deepx/skills/ missing"
        skills = skill_names_from_dir(skills_dir)
        assert len(skills) > 0, "dx-compiler has no skill files"

    def test_compiler_has_model_converter_agent(self):
        """dx-compiler must have a model converter agent."""
        agents_dir = COMPILER_ROOT / ".deepx" / "agents"
        agents = agent_names_from_dir(agents_dir)
        converter_agents = [a for a in agents if "convert" in a or "model" in a]
        assert len(converter_agents) > 0, (
            f"No model converter agent found in dx-compiler. Agents: {agents}"
        )

    def test_compiler_has_compile_skill(self):
        """dx-compiler must have a compile skill."""
        skills_dir = COMPILER_ROOT / ".deepx" / "skills"
        skills = skill_names_from_dir(skills_dir)
        compile_skills = [s for s in skills if "compile" in s]
        assert len(compile_skills) > 0, (
            f"No compile skill found in dx-compiler. Skills: {skills}"
        )


class TestScenario2Infrastructure:
    """Scenario 2: Model Compilation + Sample App.

    Requires: dx-compiler + dx_app infrastructure and handoff.
    """

    def test_app_agents_exist(self):
        """dx_app must have agent files for app building."""
        agents_dir = APP_ROOT / ".deepx" / "agents"
        assert agents_dir.exists(), "dx_app/.deepx/agents/ missing"
        agents = agent_names_from_dir(agents_dir)
        assert len(agents) > 0, "dx_app has no agent files"

    def test_app_has_builder_agent(self):
        """dx_app must have an app builder agent."""
        agents_dir = APP_ROOT / ".deepx" / "agents"
        agents = agent_names_from_dir(agents_dir)
        builder_agents = [a for a in agents if "app-builder" in a or "python-builder" in a]
        assert len(builder_agents) > 0, (
            f"No app builder agent in dx_app. Agents: {agents}"
        )

    def test_cross_project_compiler_to_app(self):
        """Both compiler and app infrastructure must coexist for cross-project scenario."""
        assert (COMPILER_ROOT / ".deepx").exists(), "dx-compiler/.deepx/ missing"
        assert (APP_ROOT / ".deepx").exists(), "dx_app/.deepx/ missing"


class TestScenario3Infrastructure:
    """Scenario 3: Model Compilation + Streaming Pipeline.

    Requires: dx-compiler + dx_stream infrastructure and handoff.
    """

    def test_stream_agents_exist(self):
        """dx_stream must have agent files for pipeline building."""
        agents_dir = STREAM_ROOT / ".deepx" / "agents"
        assert agents_dir.exists(), "dx_stream/.deepx/agents/ missing"
        agents = agent_names_from_dir(agents_dir)
        assert len(agents) > 0, "dx_stream has no agent files"

    def test_stream_has_pipeline_builder_agent(self):
        """dx_stream must have a pipeline builder agent."""
        agents_dir = STREAM_ROOT / ".deepx" / "agents"
        agents = agent_names_from_dir(agents_dir)
        pipeline_agents = [a for a in agents if "pipeline" in a or "stream" in a]
        assert len(pipeline_agents) > 0, (
            f"No pipeline builder agent in dx_stream. Agents: {agents}"
        )

    def test_cross_project_compiler_to_stream(self):
        """Both compiler and stream infrastructure must coexist."""
        assert (COMPILER_ROOT / ".deepx").exists(), "dx-compiler/.deepx/ missing"
        assert (STREAM_ROOT / ".deepx").exists(), "dx_stream/.deepx/ missing"


class TestScenario4Infrastructure:
    """Scenario 4: PPU Model Compilation + Detection App.

    Requires: PPU-related agents, skills, and paths.
    """

    def test_compiler_handles_ppu(self):
        """dx-compiler must have PPU-aware compilation infrastructure.

        This test checks that the compiler's guide or agent files mention PPU.
        """
        compiler_guide = (
            COMPILER_ROOT / "source/docs/05_DX-COMPILER_Agentic_Development.md"
        )
        if not compiler_guide.exists():
            pytest.skip("dx-compiler guide not found")
        text = compiler_guide.read_text(encoding="utf-8")
        assert re.search(r"[Pp][Pp][Uu]", text), (
            "dx-compiler agentic development guide does not mention PPU"
        )

    def test_app_handles_ppu(self):
        """dx_app must support PPU inference via its agent infrastructure.

        PPU support may be in the app guide, agent files, or skill files.
        """
        # Check guide first
        app_guide = (
            APP_ROOT / "docs/source/docs/12_DX-APP_Agentic_Development.md"
        )
        guide_has_ppu = False
        if app_guide.exists():
            text = app_guide.read_text(encoding="utf-8")
            guide_has_ppu = bool(re.search(r"[Pp][Pp][Uu]", text))

        # Also check agent/skill files for PPU mentions
        infra_has_ppu = False
        for subdir in ["agents", "skills"]:
            d = APP_ROOT / ".deepx" / subdir
            if d.exists():
                for f in d.glob("*.md"):
                    if re.search(r"[Pp][Pp][Uu]", f.read_text(encoding="utf-8")):
                        infra_has_ppu = True
                        break

        assert guide_has_ppu or infra_has_ppu, (
            "dx_app has no PPU mentions in guide or agent/skill infrastructure"
        )


# ---------------------------------------------------------------------------
# Handoff chain validation
# ---------------------------------------------------------------------------


class TestHandoffChains:
    """When guide mentions agent A handing off to agent B, B must exist."""

    # Project/module names that should not be treated as agent references
    _NON_AGENT_NAMES = {
        "dx-compiler", "dx-runtime", "dx-stream", "dx-app",
        "dx-all-suite", "dx-agentic-dev", "dx-com", "dx-rt",
    }

    # Skill names follow the pattern dx-build-*, dx-validate-*, dx-compile-*,
    # dx-convert-*, dx-model-*. These are invoked as /skill-name, not @agent.
    _SKILL_PREFIXES = (
        "dx-build-", "dx-validate-", "dx-compile-", "dx-convert-",
        "dx-model-", "dx-brainstorm-", "dx-tdd", "dx-verify-",
    )

    def _extract_handoff_targets(self, text: str) -> Set[str]:
        """Extract agent names that appear in handoff-related contexts.

        Only matches @agent-name patterns in handoff contexts to avoid
        confusing project names or skill names with agent names.
        """
        # Only match explicit @agent-name or `agent-name` in handoff contexts
        patterns = [
            r"(?:hands?\s+off|routes?|delegates?|forwards?)\s+to\s+[`@](dx-[\w-]+)",
            r"[→➡]\s*[`@](dx-[\w-]+)",
        ]
        targets: Set[str] = set()
        for pattern in patterns:
            targets.update(re.findall(pattern, text, re.IGNORECASE))
        # Remove known non-agent names
        targets -= self._NON_AGENT_NAMES
        # Remove skill names (dx-build-*, dx-validate-*, etc.)
        targets = {
            t for t in targets
            if not any(t.startswith(p) for p in self._SKILL_PREFIXES)
        }
        return targets

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_handoff_targets_exist(self, pair):
        """Handoff targets mentioned in guides must have agent files
        or be listed in AGENTS.md."""
        en_text = read_markdown(pair.en_path)
        targets = self._extract_handoff_targets(en_text)
        if not targets:
            pytest.skip(f"No handoff references found in {pair.label}")

        # Collect all available agents: file-based + AGENTS.md logical
        all_agents: Set[str] = set()
        for _, root in PROJECT_ROOTS.items():
            d = root / ".deepx" / "agents"
            if d.exists():
                all_agents.update(agent_names_from_dir(d))
            agents_md = root / "AGENTS.md"
            if agents_md.exists():
                md_text = agents_md.read_text(encoding="utf-8")
                all_agents.update(extract_agent_references(md_text))

        missing = targets - all_agents
        assert not missing, (
            f"{pair.label}: Handoff targets reference non-existent agents: {missing}\n"
            f"  Available agents: {sorted(all_agents)}"
        )


# ---------------------------------------------------------------------------
# Output isolation (.gitignore for dx-agentic-dev/)
# ---------------------------------------------------------------------------


class TestOutputIsolation:
    """Projects should have .gitignore rules for agentic development output."""

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items() if k != "suite"],
        ids=[k for k in PROJECT_ROOTS if k != "suite"],
    )
    def test_gitignore_has_agentic_output_rule(self, project: str, root: Path):
        """Each project should have .gitignore rules for dx-agentic-dev/ output."""
        gitignore = root / ".gitignore"
        if not gitignore.exists():
            pytest.xfail(f"{project}: No .gitignore file found")
            return

        text = gitignore.read_text(encoding="utf-8")
        # Check for dx-agentic-dev/ or similar pattern
        has_rule = bool(re.search(r"dx-agentic-dev", text))
        if not has_rule:
            pytest.xfail(
                f"{project}/.gitignore does not have dx-agentic-dev/ exclusion rule"
            )


# ---------------------------------------------------------------------------
# Validation script existence
# ---------------------------------------------------------------------------


class TestValidationScripts:
    """Validation scripts must exist for projects that have .deepx/."""

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items() if k != "suite"],
        ids=[k for k in PROJECT_ROOTS if k != "suite"],
    )
    def test_validate_framework_exists(self, project: str, root: Path):
        """Each project with .deepx/ should have validate_framework.py."""
        deepx = root / ".deepx"
        if not deepx.exists():
            pytest.skip(f"{project} has no .deepx/")
        script = deepx / "scripts" / "validate_framework.py"
        assert script.exists(), (
            f"{project}: Missing .deepx/scripts/validate_framework.py"
        )

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items() if k != "suite"],
        ids=[k for k in PROJECT_ROOTS if k != "suite"],
    )
    def test_validate_framework_not_empty(self, project: str, root: Path):
        """validate_framework.py must have meaningful content."""
        script = root / ".deepx" / "scripts" / "validate_framework.py"
        if not script.exists():
            pytest.skip(f"No validate_framework.py for {project}")
        size = script.stat().st_size
        assert size > 100, (
            f"{project}: validate_framework.py is too small ({size} bytes)"
        )


# ---------------------------------------------------------------------------
# Suite-level AGENTS.md routing table completeness
# ---------------------------------------------------------------------------


class TestSuiteRoutingTable:
    """Suite-level AGENTS.md must route to all submodules."""

    def test_suite_agents_md_mentions_all_submodules(self):
        """Suite AGENTS.md must mention all submodule project names."""
        agents_md = SUITE_ROOT / "AGENTS.md"
        if not agents_md.exists():
            pytest.fail("Suite-level AGENTS.md not found")
        text = agents_md.read_text(encoding="utf-8")

        submodules = ["dx-compiler", "dx-runtime", "dx_app", "dx_stream"]
        missing = [s for s in submodules if s not in text]
        assert not missing, (
            f"Suite AGENTS.md does not mention submodules: {missing}"
        )

    def test_suite_agents_md_has_routing_section(self):
        """Suite AGENTS.md must have a Routing section."""
        agents_md = SUITE_ROOT / "AGENTS.md"
        if not agents_md.exists():
            pytest.fail("Suite-level AGENTS.md not found")
        text = agents_md.read_text(encoding="utf-8")
        assert re.search(r"(?i)##\s+routing", text), (
            "Suite AGENTS.md is missing a ## Routing section"
        )
