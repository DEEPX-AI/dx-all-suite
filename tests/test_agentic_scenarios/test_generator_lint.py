"""Tests for dx-agentic-gen lint subcommand.

RED gate: these tests MUST fail before lint is implemented.

Tests cover:
1. lint command exists in CLI (dx-agentic-gen lint)
2. lint passes on current clean state (all fragments paired + structurally sound)
3. lint detects missing KO pair for an EN fragment
4. lint detects missing structural marker (Q1./Q2./Q3.) in a KO fragment
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
FRAGMENTS_EN = REPO_ROOT / ".deepx/templates/fragments/en"
FRAGMENTS_KO = REPO_ROOT / ".deepx/templates/fragments/ko"


# ---------------------------------------------------------------------------
# 1. CLI subcommand exists
# ---------------------------------------------------------------------------


class TestLintCommandExists:
    def test_lint_subcommand_is_registered(self):
        """dx-agentic-gen lint must be a valid subcommand (exit 0 if clean,
        exit 1 if issues found, but NOT SystemExit(2) which means unknown command).
        """
        from dx_agentic_dev_gen.cli import main

        # SystemExit(2) = argparse 'unrecognized command'; 0 or 1 are both valid
        try:
            ret = main(["lint"])
        except SystemExit as exc:
            assert exc.code != 2, (
                "'dx-agentic-gen lint' returned exit code 2 — subcommand not registered."
            )

    def test_lint_help_available(self):
        """dx-agentic-gen lint --help must not raise SystemExit(2)."""
        from dx_agentic_dev_gen.cli import main

        with pytest.raises(SystemExit) as exc:
            main(["lint", "--help"])
        assert exc.value.code == 0, (
            f"dx-agentic-gen lint --help returned code {exc.value.code}, expected 0."
        )


# ---------------------------------------------------------------------------
# 2. Clean state → lint passes
# ---------------------------------------------------------------------------


class TestLintCleanState:
    def test_lint_passes_on_current_repo(self):
        """Generator.lint() must return clean=True on the current repo state.

        All EN fragments must have KO counterparts and structural parity.
        If this fails it means there is an unresolved EN/KO sync gap.
        """
        from dx_agentic_dev_gen.generator import Generator

        gen = Generator(REPO_ROOT)
        clean, report = gen.lint()
        assert clean, (
            "dx-agentic-gen lint found EN/KO sync issues on the current repo.\n"
            + "\n".join(report)
        )

    def test_lint_reports_no_errors_on_current_repo(self):
        """lint report must not contain any [ERROR] lines for existing fragments."""
        from dx_agentic_dev_gen.generator import Generator

        gen = Generator(REPO_ROOT)
        _clean, report = gen.lint()
        error_lines = [line for line in report if "[ERROR]" in line]
        assert not error_lines, (
            "dx-agentic-gen lint reported ERRORs on clean state:\n"
            + "\n".join(error_lines)
        )


# ---------------------------------------------------------------------------
# 3. Missing KO pair detection
# ---------------------------------------------------------------------------


class TestLintMissingKoPair:
    def test_lint_detects_missing_ko_fragment(self, tmp_path):
        """lint must return clean=False and report [ERROR] when EN fragment
        has no KO counterpart.

        Setup: create a minimal .deepx/ tree with one EN fragment and NO KO counterpart.
        """
        deepx = tmp_path / ".deepx"
        en_dir = deepx / "templates" / "fragments" / "en"
        ko_dir = deepx / "templates" / "fragments" / "ko"
        en_dir.mkdir(parents=True)
        ko_dir.mkdir(parents=True)

        # EN fragment exists; KO fragment is intentionally absent
        (en_dir / "example-rule.md").write_text(
            "## Example Rule\n\nThis rule applies.\n", encoding="utf-8"
        )
        # ko/example-rule.md is intentionally NOT created

        from dx_agentic_dev_gen.generator import Generator

        gen = Generator(tmp_path)
        clean, report = gen.lint()

        assert not clean, (
            "lint should return clean=False when KO fragment is missing."
        )
        report_text = "\n".join(report)
        assert "example-rule" in report_text, (
            "lint report should name the missing KO fragment 'example-rule'.\n"
            f"Report:\n{report_text}"
        )
        assert "[ERROR]" in report_text, (
            "lint report should contain [ERROR] for missing KO pair.\n"
            f"Report:\n{report_text}"
        )


# ---------------------------------------------------------------------------
# 4. Missing structural marker detection
# ---------------------------------------------------------------------------


class TestLintMissingStructuralMarker:
    def test_lint_detects_missing_q_markers_in_ko(self, tmp_path):
        """lint must exit 1 when EN fragment has Q1./Q2./Q3. decision tree but
        KO counterpart does not.

        Setup: EN has Q1./Q2./Q3.; KO has the section heading but is missing
        the Q blocks.
        """
        deepx = tmp_path / ".deepx"
        en_dir = deepx / "templates" / "fragments" / "en"
        ko_dir = deepx / "templates" / "fragments" / "ko"
        en_dir.mkdir(parents=True)
        ko_dir.mkdir(parents=True)

        (en_dir / "preflight.md").write_text(
            "### Pre-flight Classification (MANDATORY)\n\n"
            "Answer these three questions:\n\n"
            "> **Q1. Is the file path inside `**/.deepx/**`?**\n"
            "> - YES → Canonical source.\n"
            "> - NO → go to Q2.\n"
            ">\n"
            "> **Q2. Does the file path match any of these?**\n"
            "> - YES → Generator output.\n"
            "> - NO → go to Q3.\n"
            ">\n"
            "> **Q3. Does the file begin with `<!-- AUTO-GENERATED`?**\n"
            "> - YES → Generator output.\n"
            "> - NO → Independent source.\n\n"
            "1. **Canonical source** — edit directly.\n"
            "2. **Generator output** — edit via .deepx/ source.\n"
            "3. **Independent source** — edit directly.\n",
            encoding="utf-8",
        )

        # KO: has the heading and numbered list but is MISSING Q1./Q2./Q3.
        (ko_dir / "preflight.md").write_text(
            "### Pre-flight Classification (MANDATORY)\n\n"
            "세 가지 질문에 답하세요:\n\n"
            "1. **Canonical source** — 직접 수정.\n"
            "2. **Generator output** — .deepx/ source를 수정.\n"
            "3. **독립 소스** — 직접 수정.\n",
            encoding="utf-8",
        )

        from dx_agentic_dev_gen.generator import Generator

        gen = Generator(tmp_path)
        clean, report = gen.lint()
        report_text = "\n".join(report)

        assert not clean, (
            "lint should return clean=False when KO fragment is missing Q markers."
        )
        assert "preflight" in report_text, (
            "lint report should name the offending fragment 'preflight'.\n"
            f"Report:\n{report_text}"
        )
        assert "[ERROR]" in report_text, (
            "lint report should contain [ERROR] for missing structural markers.\n"
            f"Report:\n{report_text}"
        )

    def test_lint_passes_when_ko_has_all_markers(self, tmp_path):
        """lint must return clean=True when both EN and KO fragments have Q1./Q2./Q3."""
        deepx = tmp_path / ".deepx"
        en_dir = deepx / "templates" / "fragments" / "en"
        ko_dir = deepx / "templates" / "fragments" / "ko"
        en_dir.mkdir(parents=True)
        ko_dir.mkdir(parents=True)

        en_content = (
            "### Classification\n\n"
            "> **Q1.** Is it in .deepx/?\n> - YES\n> - NO → Q2.\n>\n"
            "> **Q2.** Does it match output paths?\n> - YES\n> - NO → Q3.\n>\n"
            "> **Q3.** Does it begin with AUTO-GENERATED?\n> - YES\n> - NO\n"
        )
        ko_content = (
            "### 분류\n\n"
            "> **Q1.** .deepx/ 내부인가요?\n> - YES\n> - NO → Q2.\n>\n"
            "> **Q2.** 출력 경로와 일치하나요?\n> - YES\n> - NO → Q3.\n>\n"
            "> **Q3.** AUTO-GENERATED으로 시작하나요?\n> - YES\n> - NO\n"
        )

        (en_dir / "classification.md").write_text(en_content, encoding="utf-8")
        (ko_dir / "classification.md").write_text(ko_content, encoding="utf-8")

        from dx_agentic_dev_gen.generator import Generator

        gen = Generator(tmp_path)
        clean, report = gen.lint()

        assert clean, (
            "lint should return clean=True when KO has all Q markers.\n"
            + "\n".join(report)
        )
