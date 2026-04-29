# SPDX-License-Identifier: Apache-2.0
"""
Tests for instruction file synchronization.

Task 5: EN ↔ KO instruction file sync
Task 3: Same-level cross-platform sync (CLAUDE vs AGENTS vs copilot)
Task 4: Suite ↔ Sub-level rule propagation
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set

import pytest

from .conftest import (
    INSTRUCTION_PAIRS,
    PROJECT_ROOTS,
    InstructionPair,
    extract_agent_references,
    extract_code_blocks,
    extract_headings_at_level,
    extract_skill_references,
    extract_tables,
    read_markdown,
)


# ---------------------------------------------------------------------------
# Task 5: EN ↔ KO instruction file sync
# ---------------------------------------------------------------------------


class TestEnKoInstructionSync:
    """EN and KO instruction files must be structurally synchronized."""

    @pytest.mark.parametrize(
        "pair", INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS]
    )
    def test_both_files_exist(self, pair: InstructionPair):
        """Both EN and KO files must exist."""
        assert pair.en_path.exists(), f"EN file missing: {pair.en_path}"
        assert pair.ko_path.exists(), f"KO file missing: {pair.ko_path}"

    @pytest.mark.parametrize(
        "pair", INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS]
    )
    def test_h2_heading_count_matches(self, pair: InstructionPair):
        """EN and KO files must have the same number of ## headings."""
        if not pair.en_path.exists() or not pair.ko_path.exists():
            pytest.skip("Files missing")
        en_h2 = extract_headings_at_level(read_markdown(pair.en_path), 2)
        ko_h2 = extract_headings_at_level(read_markdown(pair.ko_path), 2)
        assert len(en_h2) == len(ko_h2), (
            f"{pair.label}: EN has {len(en_h2)} ## headings, KO has {len(ko_h2)}\n"
            f"  EN: {en_h2}\n  KO: {ko_h2}"
        )

    @pytest.mark.parametrize(
        "pair", INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS]
    )
    def test_h3_heading_count_matches(self, pair: InstructionPair):
        """EN and KO files must have the same number of ### headings."""
        if not pair.en_path.exists() or not pair.ko_path.exists():
            pytest.skip("Files missing")
        en_h3 = extract_headings_at_level(read_markdown(pair.en_path), 3)
        ko_h3 = extract_headings_at_level(read_markdown(pair.ko_path), 3)
        assert len(en_h3) == len(ko_h3), (
            f"{pair.label}: EN has {len(en_h3)} ### headings, KO has {len(ko_h3)}\n"
            f"  EN: {en_h3}\n  KO: {ko_h3}"
        )

    @pytest.mark.parametrize(
        "pair", INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS]
    )
    def test_agent_references_match(self, pair: InstructionPair):
        """EN and KO must reference the same @dx-xxx agents."""
        if not pair.en_path.exists() or not pair.ko_path.exists():
            pytest.skip("Files missing")
        en_refs = set(extract_agent_references(read_markdown(pair.en_path)))
        ko_refs = set(extract_agent_references(read_markdown(pair.ko_path)))
        assert en_refs == ko_refs, (
            f"{pair.label}: Agent refs differ\n"
            f"  EN only: {en_refs - ko_refs}\n  KO only: {ko_refs - en_refs}"
        )

    @pytest.mark.parametrize(
        "pair", INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS]
    )
    def test_skill_references_match(self, pair: InstructionPair):
        """EN and KO must reference the same /dx-xxx skills."""
        if not pair.en_path.exists() or not pair.ko_path.exists():
            pytest.skip("Files missing")
        en_refs = set(extract_skill_references(read_markdown(pair.en_path)))
        ko_refs = set(extract_skill_references(read_markdown(pair.ko_path)))
        assert en_refs == ko_refs, (
            f"{pair.label}: Skill refs differ\n"
            f"  EN only: {en_refs - ko_refs}\n  KO only: {ko_refs - en_refs}"
        )

    @pytest.mark.parametrize(
        "pair", INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS]
    )
    def test_code_block_count_matches(self, pair: InstructionPair):
        """EN and KO must have the same number of code blocks."""
        if not pair.en_path.exists() or not pair.ko_path.exists():
            pytest.skip("Files missing")
        en_blocks = extract_code_blocks(read_markdown(pair.en_path))
        ko_blocks = extract_code_blocks(read_markdown(pair.ko_path))
        assert len(en_blocks) == len(ko_blocks), (
            f"{pair.label}: EN has {len(en_blocks)} code blocks, KO has {len(ko_blocks)}"
        )

    @pytest.mark.parametrize(
        "pair", INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS]
    )
    def test_table_line_count_matches(self, pair: InstructionPair):
        """EN and KO must have similar number of table lines (within 10% tolerance)."""
        if not pair.en_path.exists() or not pair.ko_path.exists():
            pytest.skip("Files missing")
        en_tables = extract_tables(read_markdown(pair.en_path))
        ko_tables = extract_tables(read_markdown(pair.ko_path))
        if en_tables == 0 and ko_tables == 0:
            return  # No tables in either
        tolerance = max(3, int(en_tables * 0.1))  # 10% or at least 3 lines
        assert abs(en_tables - ko_tables) <= tolerance, (
            f"{pair.label}: Table line count differs significantly: "
            f"EN={en_tables}, KO={ko_tables} (tolerance={tolerance})"
        )


# ---------------------------------------------------------------------------
# Task 3: Same-level cross-platform instruction file sync
# ---------------------------------------------------------------------------


class TestCrossPlatformInstructionSync:
    """Within the same level, CLAUDE.md / AGENTS.md / copilot-instructions.md
    must share key sections and keywords."""

    # Sections that should exist in ALL three files at EVERY level.
    # Use keyword substring matching (not exact heading match).
    COMMON_KEYWORDS = [
        "Autopilot Mode Guard",
        "Output Isolation",
        "Rule Conflict Resolution",
        "Instruction File Verification Loop",
    ]

    # Level-specific keywords: only checked at these levels
    LEVEL_SPECIFIC_KEYWORDS = {
        "suite": ["Git Safety"],
        "compiler": ["Target Hardware", "Quantization", "Git Operations"],
        "runtime": ["Git Safety", "Git Operations"],
        "app": ["Git Operations"],
        "stream": ["Git Operations"],
    }

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_common_sections_in_all_files(self, project: str, root: Path):
        """All three instruction files must contain common keywords."""
        files = {
            "CLAUDE.md": root / "CLAUDE.md",
            "AGENTS.md": root / "AGENTS.md",
            "copilot": root / ".github" / "copilot-instructions.md",
        }
        existing = {k: v for k, v in files.items() if v.exists()}
        if len(existing) < 2:
            pytest.skip(f"{project}: fewer than 2 instruction files")

        keywords = self.COMMON_KEYWORDS + self.LEVEL_SPECIFIC_KEYWORDS.get(project, [])

        missing_report = []
        for keyword in keywords:
            for fname, fpath in existing.items():
                text = fpath.read_text(encoding="utf-8")
                if keyword not in text:
                    missing_report.append(f"  {fname} missing '{keyword}'")

        assert not missing_report, (
            f"{project}: Cross-platform section sync failures:\n"
            + "\n".join(missing_report)
        )

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_copilot_h2_headings_in_claude_and_agents(self, project: str, root: Path):
        """copilot-instructions.md ## headings (minus platform/level-specific) should
        exist in CLAUDE.md and AGENTS.md.

        Note: CLAUDE.md and AGENTS.md are shorter than copilot-instructions.md,
        so we check that at least 50% of copilot headings are shared."""
        copilot_path = root / ".github" / "copilot-instructions.md"
        if not copilot_path.exists():
            pytest.skip(f"{project}: no copilot-instructions.md")

        copilot_text = read_markdown(copilot_path)
        copilot_h2 = set(extract_headings_at_level(copilot_text, 2))

        # Headings that are allowed to differ across files
        platform_exclude = {
            "Platform File Loading Reference",
            "Copilot-Specific",
            "copilot-specific",
            "Process Skills",  # copilot-specific section
        }
        copilot_h2 -= platform_exclude
        if not copilot_h2:
            pytest.skip(f"{project}: no non-excluded headings")

        missing_report = []
        for fname in ["CLAUDE.md", "AGENTS.md"]:
            fpath = root / fname
            if not fpath.exists():
                continue
            text = fpath.read_text(encoding="utf-8")
            file_h2 = set(extract_headings_at_level(text, 2))
            file_h2 -= platform_exclude
            shared = copilot_h2 & file_h2
            coverage = len(shared) / len(copilot_h2) if copilot_h2 else 1.0
            if coverage < 0.7:
                missing = sorted(copilot_h2 - file_h2)
                missing_report.append(
                    f"  {fname}: only {coverage:.0%} heading coverage "
                    f"({len(shared)}/{len(copilot_h2)}), missing: {missing}"
                )

        assert not missing_report, (
            f"{project}: copilot headings not sufficiently mirrored:\n"
            + "\n".join(missing_report)
        )


# ---------------------------------------------------------------------------
# Task 3 continued: Agent/Skill file CONTENT sync across platforms
# ---------------------------------------------------------------------------


class TestAgentFileContentSync:
    """Same agent across .deepx/, .github/, .opencode/ must share key content.

    .github/ and .opencode/ contain abbreviated versions with YAML frontmatter.
    We verify that abbreviated copies have a meaningful description field."""

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items()],
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_agent_files_have_description(self, project: str, root: Path):
        """Agent files across platforms must have a description."""
        deepx_dir = root / ".deepx" / "agents"
        gh_dir = root / ".github" / "agents"
        oc_dir = root / ".opencode" / "agents"

        if not deepx_dir.exists():
            pytest.skip(f"{project}: no .deepx/agents/")

        from .conftest import agent_names_from_dir
        deepx_agents = agent_names_from_dir(deepx_dir)

        mismatches = []
        for agent_name in deepx_agents:
            # Check .github version has description
            gh_file = gh_dir / f"{agent_name}.agent.md"
            if gh_file.exists():
                gh_text = gh_file.read_text(encoding="utf-8")
                if "description:" not in gh_text:
                    mismatches.append(
                        f"  {agent_name}: .github missing description"
                    )

            # Check .opencode version has description
            oc_file = oc_dir / f"{agent_name}.md"
            if oc_file.exists():
                oc_text = oc_file.read_text(encoding="utf-8")
                if "description:" not in oc_text:
                    mismatches.append(
                        f"  {agent_name}: .opencode missing description"
                    )

        assert not mismatches, (
            f"{project}: Agent content sync failures:\n" + "\n".join(mismatches)
        )


class TestSkillFileContentSync:
    """Same skill across .deepx/ and .opencode/ must share key content.

    Note: .opencode/ SKILL.md files are abbreviated, so we check that the
    skill name appears in the .opencode version (not exact title match)."""

    @pytest.mark.parametrize(
        "project,root",
        [(k, v) for k, v in PROJECT_ROOTS.items()],
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_skill_files_share_skill_name(self, project: str, root: Path):
        """Skill files in .deepx/ and .opencode/ must mention the skill name."""
        deepx_dir = root / ".deepx" / "skills"
        oc_dir = root / ".opencode" / "skills"

        if not deepx_dir.exists() or not oc_dir.exists():
            pytest.skip(f"{project}: missing .deepx/skills/ or .opencode/skills/")

        from .conftest import skill_names_from_dir
        deepx_skills = skill_names_from_dir(deepx_dir)

        mismatches = []
        for skill_name in deepx_skills:
            oc_skill_file = oc_dir / skill_name / "SKILL.md"
            if oc_skill_file.exists():
                oc_text = oc_skill_file.read_text(encoding="utf-8")
                if skill_name not in oc_text:
                    mismatches.append(
                        f"  {skill_name}: .opencode doesn't mention own name"
                    )

        assert not mismatches, (
            f"{project}: Skill content sync failures:\n" + "\n".join(mismatches)
        )


# ---------------------------------------------------------------------------
# Task 4: Suite ↔ Sub-level rule propagation
# ---------------------------------------------------------------------------


class TestSuiteSubLevelRulePropagation:
    """Common rules in suite-level copilot-instructions.md must propagate
    to sub-level copilot-instructions.md files."""

    # Rules that MUST exist at ALL levels (using substring match)
    UNIVERSAL_RULES = [
        "Output Isolation",
        "Rule Conflict Resolution",
        "Instruction File Verification Loop",
    ]

    # Rules checked at specific levels only
    LEVEL_RULES = {
        "suite": ["Git Safety"],
        "compiler": [],
        "runtime": ["Git Safety", "Git Operations"],
        "app": ["Git Operations"],
        "stream": [],
    }

    # Rules that must exist at suite + runtime (but not necessarily app/stream)
    SUITE_RUNTIME_RULES = [
        "Sub-Project Development Rules",
    ]

    @pytest.mark.parametrize(
        "rule", UNIVERSAL_RULES, ids=UNIVERSAL_RULES
    )
    def test_universal_rule_at_all_levels(self, rule: str):
        """Universal rules must appear in copilot-instructions.md at all 5 levels."""
        missing = []
        for project, root in PROJECT_ROOTS.items():
            copilot = root / ".github" / "copilot-instructions.md"
            if not copilot.exists():
                missing.append(f"  {project}: file missing")
                continue
            text = copilot.read_text(encoding="utf-8")
            if rule not in text:
                missing.append(f"  {project}: missing '{rule}'")
        assert not missing, (
            f"Universal rule '{rule}' missing at some levels:\n"
            + "\n".join(missing)
        )

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_level_specific_rules(self, project: str, root: Path):
        """Level-specific rules must appear in copilot-instructions.md."""
        rules = self.LEVEL_RULES.get(project, [])
        if not rules:
            pytest.skip(f"{project}: no level-specific rules to check")
        copilot = root / ".github" / "copilot-instructions.md"
        if not copilot.exists():
            pytest.fail(f"{project}: copilot-instructions.md missing")
        text = copilot.read_text(encoding="utf-8")
        missing = [r for r in rules if r not in text]
        assert not missing, (
            f"{project}/copilot-instructions.md missing rules: {missing}"
        )

    @pytest.mark.parametrize(
        "rule", SUITE_RUNTIME_RULES, ids=SUITE_RUNTIME_RULES
    )
    def test_suite_runtime_rule_propagation(self, rule: str):
        """Rules must exist at suite and runtime levels."""
        for project in ["suite", "runtime"]:
            root = PROJECT_ROOTS[project]
            copilot = root / ".github" / "copilot-instructions.md"
            if not copilot.exists():
                pytest.fail(f"{project}: copilot-instructions.md missing")
            text = copilot.read_text(encoding="utf-8")
            assert rule in text, (
                f"{project}/copilot-instructions.md missing '{rule}'"
            )

    def test_suite_copilot_mentions_all_subprojects(self):
        """Suite copilot-instructions.md must mention all sub-projects."""
        suite_copilot = PROJECT_ROOTS["suite"] / ".github" / "copilot-instructions.md"
        if not suite_copilot.exists():
            pytest.fail("Suite copilot-instructions.md missing")
        text = suite_copilot.read_text(encoding="utf-8")
        for subproject in ["dx-compiler", "dx-runtime", "dx_app", "dx_stream"]:
            assert subproject in text, (
                f"Suite copilot-instructions.md doesn't mention '{subproject}'"
            )

    def test_runtime_copilot_mentions_sub_apps(self):
        """Runtime copilot-instructions.md must mention dx_app and dx_stream."""
        rt_copilot = PROJECT_ROOTS["runtime"] / ".github" / "copilot-instructions.md"
        if not rt_copilot.exists():
            pytest.fail("Runtime copilot-instructions.md missing")
        text = rt_copilot.read_text(encoding="utf-8")
        for sub in ["dx_app", "dx_stream"]:
            assert sub in text, (
                f"Runtime copilot-instructions.md doesn't mention '{sub}'"
            )


# ---------------------------------------------------------------------------
# Table format validation
# ---------------------------------------------------------------------------


class TestTableFormatIntegrity:
    """Markdown tables must not have corrupted row separators (e.g., '||')."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_no_concatenated_table_rows(self, project: str, root: Path):
        """Instruction files must not have '||' mid-line (concatenated table rows)."""
        files = {
            "CLAUDE.md": root / "CLAUDE.md",
            "AGENTS.md": root / "AGENTS.md",
            "copilot": root / ".github" / "copilot-instructions.md",
        }
        defects = []
        for fname, fpath in files.items():
            if not fpath.exists():
                continue
            for lineno, line in enumerate(fpath.read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.strip()
                if stripped.startswith("|") and "||" in stripped:
                    # Ignore separator rows (e.g., |---|---|)
                    if re.match(r"^\|[\s\-:|]+\|$", stripped):
                        continue
                    # Ignore empty cells (e.g., | foo || bar |) which are valid
                    # Only flag if || appears between content cells
                    if re.search(r"[^|]\|\|[^|]", stripped):
                        defects.append(f"  {fname}:{lineno}: {stripped[:80]}")
        assert not defects, (
            f"{project}: Concatenated table rows found (missing newline?):\n"
            + "\n".join(defects)
        )


# ---------------------------------------------------------------------------
# Cross-reference direction validation
# ---------------------------------------------------------------------------


class TestCrossReferenceDirection:
    """'See X above/below' references must point in the correct direction."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_brainstorming_rule_conflict_ref_direction(self, project: str, root: Path):
        """Brainstorming #5 references 'Rule Conflict Resolution' — direction must be correct."""
        files = {
            "CLAUDE.md": root / "CLAUDE.md",
            "AGENTS.md": root / "AGENTS.md",
            "copilot": root / ".github" / "copilot-instructions.md",
        }
        defects = []
        for fname, fpath in files.items():
            if not fpath.exists():
                continue
            text = fpath.read_text(encoding="utf-8")
            lines = text.splitlines()

            # Find Brainstorming section line and Rule Conflict Resolution section line
            brainstorm_line = None
            rcr_line = None
            for i, line in enumerate(lines):
                if re.match(r"^##[^#].*Brainstorming", line):
                    brainstorm_line = i
                if re.match(r"^##[^#].*Rule Conflict Resolution", line):
                    rcr_line = i

            if brainstorm_line is None or rcr_line is None:
                continue

            # Check if Brainstorming #5 says "above" but RCR is below
            for i, line in enumerate(lines):
                if (brainstorm_line <= i < brainstorm_line + 30 and
                        'Rule Conflict Resolution' in line and
                        'above' in line.lower()):
                    if rcr_line > brainstorm_line:
                        defects.append(
                            f"  {fname}:{i+1}: says 'above' but Rule Conflict "
                            f"Resolution is at line {rcr_line+1} (below Brainstorming at {brainstorm_line+1})"
                        )

        assert not defects, (
            f"{project}: Incorrect cross-reference direction:\n"
            + "\n".join(defects)
        )


# ---------------------------------------------------------------------------
# Pre-flight Classification structural sync (EN/KO fragment parity)
# ---------------------------------------------------------------------------


class TestPreFlightClassificationSync:
    """Verify that KO instruction files contain the Q1/Q2/Q3 decision tree
    in the Pre-flight Classification section, matching the EN structure.

    Root cause: the KO `instruction-verification-loop` fragment was missing
    the 'Answer these three questions' blockquote block (Q1/Q2/Q3), while the
    EN version had it. Existing EN/KO sync tests (code block count, H3 count)
    did not catch this because the counts happened to match by coincidence.
    """

    INSTRUCTION_PAIRS_COPILOT = [
        (
            Path("/data/home/dhyang/github/dx-all-suite/.github/copilot-instructions.md"),
            Path("/data/home/dhyang/github/dx-all-suite/.github/copilot-instructions-KO.md"),
            "suite",
        ),
        (
            Path("/data/home/dhyang/github/dx-all-suite/dx-compiler/.github/copilot-instructions.md"),
            Path("/data/home/dhyang/github/dx-all-suite/dx-compiler/.github/copilot-instructions-KO.md"),
            "compiler",
        ),
        (
            Path("/data/home/dhyang/github/dx-all-suite/dx-runtime/.github/copilot-instructions.md"),
            Path("/data/home/dhyang/github/dx-all-suite/dx-runtime/.github/copilot-instructions-KO.md"),
            "runtime",
        ),
        (
            Path("/data/home/dhyang/github/dx-all-suite/dx-runtime/dx_app/.github/copilot-instructions.md"),
            Path("/data/home/dhyang/github/dx-all-suite/dx-runtime/dx_app/.github/copilot-instructions-KO.md"),
            "app",
        ),
        (
            Path("/data/home/dhyang/github/dx-all-suite/dx-runtime/dx_stream/.github/copilot-instructions.md"),
            Path("/data/home/dhyang/github/dx-all-suite/dx-runtime/dx_stream/.github/copilot-instructions-KO.md"),
            "stream",
        ),
    ]

    @pytest.mark.parametrize(
        "en_path,ko_path,label",
        INSTRUCTION_PAIRS_COPILOT,
        ids=[p[2] for p in INSTRUCTION_PAIRS_COPILOT],
    )
    def test_preflight_ko_has_q1_q2_q3_decision_tree(
        self, en_path: Path, ko_path: Path, label: str
    ):
        """KO instruction file must contain the Q1/Q2/Q3 decision tree in
        the Pre-flight Classification section, matching the EN structure.

        The decision tree is the blockquote block starting with 'Q1.'/'Q2.'/'Q3.'
        It guides agents through classifying a file before editing it.
        If it's missing from KO, Korean-language agents may not see the
        three-step flow and may misclassify files.
        """
        if not en_path.exists() or not ko_path.exists():
            pytest.skip(f"{label}: files missing")

        en_text = en_path.read_text(encoding="utf-8")
        ko_text = ko_path.read_text(encoding="utf-8")

        # EN must have the Q1/Q2/Q3 blockquote (sanity)
        assert "Q1." in en_text and "Q2." in en_text and "Q3." in en_text, (
            f"{label}/EN: missing Q1/Q2/Q3 decision tree in Pre-flight Classification"
        )

        # KO must also have Q1/Q2/Q3
        missing = [q for q in ("Q1.", "Q2.", "Q3.") if q not in ko_text]
        assert not missing, (
            f"{label}/KO: Pre-flight Classification is missing the Q1/Q2/Q3 "
            f"decision tree blocks: {missing}\n\n"
            f"Fix: add the Korean translation of the Q1/Q2/Q3 blockquote to "
            f".deepx/templates/fragments/ko/instruction-verification-loop.md"
        )
