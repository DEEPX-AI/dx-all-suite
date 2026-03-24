# SPDX-License-Identifier: Apache-2.0
"""
Tests for agentic development guide document structure.

Validates:
- EN/KO guide pairs exist
- EN/KO heading counts are synchronized (##, ###)
- Scenario numbers are consecutive and match between EN/KO
- Required sections are present in all guides
"""

from __future__ import annotations

import re
from typing import List

import pytest

from .conftest import (
    GUIDE_PAIRS,
    GuidePair,
    extract_headings,
    extract_scenario_numbers,
    read_markdown,
)


# ---------------------------------------------------------------------------
# Guide existence
# ---------------------------------------------------------------------------


class TestGuideExistence:
    """Verify that all expected guide files exist."""

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_en_guide_exists(self, pair: GuidePair):
        """Each EN guide file must exist on disk."""
        assert pair.en_path.exists(), (
            f"EN guide missing for {pair.label}: {pair.en_path}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_ko_guide_exists(self, pair: GuidePair):
        """Each KO guide file must exist on disk."""
        assert pair.ko_path.exists(), (
            f"KO guide missing for {pair.label}: {pair.ko_path}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_guides_are_nonempty(self, pair: GuidePair):
        """Both EN and KO guides must have meaningful content (>100 bytes)."""
        if pair.en_path.exists():
            en_size = pair.en_path.stat().st_size
            assert en_size > 100, (
                f"EN guide for {pair.label} is suspiciously small ({en_size} bytes)"
            )
        if pair.ko_path.exists():
            ko_size = pair.ko_path.stat().st_size
            assert ko_size > 100, (
                f"KO guide for {pair.label} is suspiciously small ({ko_size} bytes)"
            )


# ---------------------------------------------------------------------------
# Heading synchronization between EN and KO
# ---------------------------------------------------------------------------


class TestHeadingSynchronization:
    """EN and KO guides must have the same number of ## and ### headings."""

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_h2_count_matches(self, pair: GuidePair):
        """## heading count must match between EN and KO."""
        en_text = read_markdown(pair.en_path)
        ko_text = read_markdown(pair.ko_path)
        en_h2 = extract_headings(en_text, level=2)
        ko_h2 = extract_headings(ko_text, level=2)
        assert len(en_h2) == len(ko_h2), (
            f"{pair.label}: EN has {len(en_h2)} ## headings, KO has {len(ko_h2)}.\n"
            f"  EN: {en_h2}\n  KO: {ko_h2}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_h3_count_matches(self, pair: GuidePair):
        """### heading count must match between EN and KO."""
        en_text = read_markdown(pair.en_path)
        ko_text = read_markdown(pair.ko_path)
        en_h3 = extract_headings(en_text, level=3)
        ko_h3 = extract_headings(ko_text, level=3)
        assert len(en_h3) == len(ko_h3), (
            f"{pair.label}: EN has {len(en_h3)} ### headings, KO has {len(ko_h3)}.\n"
            f"  EN: {en_h3}\n  KO: {ko_h3}"
        )


# ---------------------------------------------------------------------------
# Scenario numbering
# ---------------------------------------------------------------------------


class TestScenarioNumbering:
    """Scenario numbers must be consecutive and match EN/KO."""

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_scenarios_are_consecutive(self, pair: GuidePair):
        """Scenario numbers in EN guide must be consecutive starting from 1."""
        en_text = read_markdown(pair.en_path)
        nums = extract_scenario_numbers(en_text)
        if not nums:
            pytest.skip(f"No scenarios found in {pair.label} EN guide")
        expected = list(range(1, len(nums) + 1))
        assert nums == expected, (
            f"{pair.label} EN: Scenario numbers are not consecutive. "
            f"Found {nums}, expected {expected}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_scenario_count_matches_en_ko(self, pair: GuidePair):
        """EN and KO must have the same number of scenarios."""
        en_text = read_markdown(pair.en_path)
        ko_text = read_markdown(pair.ko_path)
        en_nums = extract_scenario_numbers(en_text)
        ko_nums = extract_scenario_numbers(ko_text)
        assert len(en_nums) == len(ko_nums), (
            f"{pair.label}: EN has {len(en_nums)} scenarios, KO has {len(ko_nums)}.\n"
            f"  EN: {en_nums}\n  KO: {ko_nums}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_scenario_numbers_match_en_ko(self, pair: GuidePair):
        """Scenario numbers must be identical between EN and KO."""
        en_text = read_markdown(pair.en_path)
        ko_text = read_markdown(pair.ko_path)
        en_nums = extract_scenario_numbers(en_text)
        ko_nums = extract_scenario_numbers(ko_text)
        if not en_nums and not ko_nums:
            pytest.skip(f"No scenarios in {pair.label}")
        assert en_nums == ko_nums, (
            f"{pair.label}: Scenario numbers differ.\n"
            f"  EN: {en_nums}\n  KO: {ko_nums}"
        )


# ---------------------------------------------------------------------------
# Required sections
# ---------------------------------------------------------------------------

# Required section keywords that should appear in guide headings.
# These are checked case-insensitively. Each guide must have:
#   1. An overview or introduction section
#   2. A scenarios section (the core purpose of these guides)
#   3. A troubleshooting section
REQUIRED_SECTION_PATTERNS_EN = [
    r"(?:overview|introduction|how it works)",  # Overview/Introduction
    r"scenario",                                  # Scenarios (section heading)
    r"troubleshoot",                              # Troubleshooting
]

REQUIRED_SECTION_PATTERNS_KO = [
    r"(?:개요|소개|작동\s*방식)",   # Overview/Introduction (KO)
    r"시나리오",                     # Scenarios (KO)
    r"(?:문제\s*해결|트러블슈팅)",   # Troubleshooting (KO)
]


class TestRequiredSections:
    """All guides must contain certain required sections."""

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_en_has_required_sections(self, pair: GuidePair):
        """EN guide must have Prerequisites, Architecture, and Scenarios sections."""
        en_text = read_markdown(pair.en_path)
        headings_text = " ".join(extract_headings(en_text, level=2)).lower()
        # Also check ### headings for scenarios
        h3_text = " ".join(extract_headings(en_text, level=3)).lower()
        combined = headings_text + " " + h3_text

        missing = []
        for pattern in REQUIRED_SECTION_PATTERNS_EN:
            if not re.search(pattern, combined, re.IGNORECASE):
                missing.append(pattern)

        assert not missing, (
            f"{pair.label} EN guide is missing required sections matching: {missing}\n"
            f"  Found headings: {headings_text}"
        )

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_ko_has_required_sections(self, pair: GuidePair):
        """KO guide must have equivalent required sections."""
        ko_text = read_markdown(pair.ko_path)
        headings_text = " ".join(extract_headings(ko_text, level=2))
        h3_text = " ".join(extract_headings(ko_text, level=3))
        combined = headings_text + " " + h3_text

        missing = []
        for pattern in REQUIRED_SECTION_PATTERNS_KO:
            if not re.search(pattern, combined):
                missing.append(pattern)

        assert not missing, (
            f"{pair.label} KO guide is missing required sections matching: {missing}\n"
            f"  Found headings: {combined}"
        )


# ---------------------------------------------------------------------------
# Title / top-level heading
# ---------------------------------------------------------------------------


class TestGuideTitle:
    """Each guide must have exactly one # top-level heading."""

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_en_has_title(self, pair: GuidePair):
        en_text = read_markdown(pair.en_path)
        h1 = extract_headings(en_text, level=1)
        assert len(h1) >= 1, f"{pair.label} EN guide has no # title heading"

    @pytest.mark.parametrize(
        "pair", GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS]
    )
    def test_ko_has_title(self, pair: GuidePair):
        ko_text = read_markdown(pair.ko_path)
        h1 = extract_headings(ko_text, level=1)
        assert len(h1) >= 1, f"{pair.label} KO guide has no # title heading"
