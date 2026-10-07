# SPDX-License-Identifier: Apache-2.0
"""
Tests for dx-agent-dev-gen generator correctness.

Validates:
- Generator package is importable and CLI is functional
- Generator check is clean for all 5 repos (no drift)
- Generator is idempotent (generate twice = same output)
- Canonical source completeness (.deepx/agents/ → platform counterparts)
- Frontmatter transformation rules
- Generated files have AUTO-GENERATED header
- .github/skills/ is not a symlink (inline copy)
- KO files have same section structure as EN
- No leftover template placeholders in generated files
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from dx_agent_dev_gen.internal_only import is_internal_only_agent

# Co-located tool tests — no test-package (avoid shadowing the real
# `dx_agent_dev_gen` import package), so define the repo roots locally.
# .deepx/tools/tests/dx_agent_dev_gen/test_generator.py → parents[4] == suite root
SUITE_ROOT = Path(__file__).resolve().parents[4]
PROJECT_ROOTS = {
    "suite": SUITE_ROOT,
    "compiler": SUITE_ROOT / "dx-compiler",
    "runtime": SUITE_ROOT / "dx-runtime",
    "app": SUITE_ROOT / "dx-runtime" / "dx_app",
    "stream": SUITE_ROOT / "dx-runtime" / "dx_stream",
}


# ---------------------------------------------------------------------------
# Generator package availability
# ---------------------------------------------------------------------------


class TestGeneratorPackage:
    """dx-agent-dev-gen must be installed and functional."""

    def test_importable(self):
        """Package can be imported."""
        import dx_agent_dev_gen
        assert dx_agent_dev_gen.__version__

    def test_cli_version(self):
        """CLI --version works."""
        from dx_agent_dev_gen.cli import main
        with pytest.raises(SystemExit) as exc:
            main(["--version"])
        assert exc.value.code == 0


# ---------------------------------------------------------------------------
# Generator check clean (no drift)
# ---------------------------------------------------------------------------


class TestGeneratorCheckClean:
    """All 5 repos must have no drift between .deepx/ and generated files."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_check_clean(self, project: str, root: Path):
        """dx-agent-gen check must exit 0 (no drift)."""
        from dx_agent_dev_gen.generator import Generator

        gen = Generator(root)
        clean, report = gen.check(platform="all")
        assert clean, (
            f"{project}: Generator drift detected:\n" + "\n".join(report)
        )


# ---------------------------------------------------------------------------
# Canonical source completeness
# ---------------------------------------------------------------------------


class TestCanonicalSourceCompleteness:
    """Every platform agent file must have a .deepx/agents/ canonical source."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_agents_have_canonical_source(self, project: str, root: Path):
        """Every .github/agents/*.agent.md has a .deepx/agents/*.md source."""
        github_agents = root / ".github" / "agents"
        deepx_agents = root / ".deepx" / "agents"
        if not github_agents.exists():
            pytest.skip(f"{project}: no .github/agents/")
        if not deepx_agents.exists():
            pytest.skip(f"{project}: no .deepx/agents/")

        orphans = []
        for gh_file in sorted(github_agents.glob("*.agent.md")):
            if is_internal_only_agent(root, gh_file):
                continue
            stem = gh_file.stem.replace(".agent", "")
            deepx_file = deepx_agents / f"{stem}.md"
            if not deepx_file.exists():
                orphans.append(gh_file.name)
        assert not orphans, (
            f"{project}: .github/agents/ files without .deepx/agents/ source: {orphans}"
        )

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_opencode_agents_have_canonical_source(self, project: str, root: Path):
        """Every .opencode/agents/*.md has a .deepx/agents/*.md source."""
        oc_agents = root / ".opencode" / "agents"
        deepx_agents = root / ".deepx" / "agents"
        if not oc_agents.exists():
            pytest.skip(f"{project}: no .opencode/agents/")
        if not deepx_agents.exists():
            pytest.skip(f"{project}: no .deepx/agents/")

        orphans = []
        for oc_file in sorted(oc_agents.glob("*.md")):
            deepx_file = deepx_agents / oc_file.name
            if not deepx_file.exists():
                orphans.append(oc_file.name)
        assert not orphans, (
            f"{project}: .opencode/agents/ files without .deepx/agents/ source: {orphans}"
        )


# ---------------------------------------------------------------------------
# Generated file header
# ---------------------------------------------------------------------------


class TestGeneratedHeader:
    """Generated files must have AUTO-GENERATED header."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_agents_have_header(self, project: str, root: Path):
        """Generated .github/agents/ files must contain AUTO-GENERATED marker."""
        github_agents = root / ".github" / "agents"
        if not github_agents.exists():
            pytest.skip(f"{project}: no .github/agents/")

        missing = []
        for f in sorted(github_agents.glob("*.agent.md")):
            if is_internal_only_agent(root, f):
                continue
            content = f.read_text(encoding="utf-8")
            if "AUTO-GENERATED" not in content:
                missing.append(f.name)
        assert not missing, (
            f"{project}: .github/agents/ files missing AUTO-GENERATED header: {missing}"
        )

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_claude_agents_have_header(self, project: str, root: Path):
        """Generated .claude/agents/ files must contain AUTO-GENERATED marker."""
        claude_agents = root / ".claude" / "agents"
        if not claude_agents.exists():
            pytest.skip(f"{project}: no .claude/agents/")

        missing = []
        for f in sorted(claude_agents.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            if "AUTO-GENERATED" not in content:
                missing.append(f.name)
        assert not missing, (
            f"{project}: .claude/agents/ files missing AUTO-GENERATED header: {missing}"
        )


# ---------------------------------------------------------------------------
# No symlinks for .github/skills/
# ---------------------------------------------------------------------------


class TestNoSymlinks:
    """.github/skills/ must be a real directory (inline copy), not symlink."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_github_skills_not_symlink(self, project: str, root: Path):
        github_skills = root / ".github" / "skills"
        if not github_skills.exists():
            pytest.skip(f"{project}: no .github/skills/")
        assert not github_skills.is_symlink(), (
            f"{project}: .github/skills/ is still a symlink. "
            f"Run: dx-agent-gen generate"
        )


# ---------------------------------------------------------------------------
# Frontmatter transformation
# ---------------------------------------------------------------------------


class TestFrontmatterTransformation:
    """Capabilities → tools mapping must be correct."""

    def test_copilot_tools_mapping(self):
        """COPILOT_TOOLS dict must have all standard capabilities."""
        from dx_agent_dev_gen.constants import COPILOT_TOOLS
        required = {"read", "edit", "search", "execute", "sub-agent", "ask-user"}
        assert required.issubset(COPILOT_TOOLS.keys())

    def test_claude_tools_mapping(self):
        """CLAUDE_TOOLS dict must have all standard capabilities."""
        from dx_agent_dev_gen.constants import CLAUDE_TOOLS
        required = {"read", "edit", "search", "execute", "sub-agent", "ask-user"}
        assert required.issubset(CLAUDE_TOOLS.keys())

    def test_capabilities_to_tools_expansion(self):
        """capabilities_to_tools must return sorted deduplicated tools."""
        from dx_agent_dev_gen.transformers import capabilities_to_tools
        from dx_agent_dev_gen.constants import COPILOT_TOOLS

        result = capabilities_to_tools(["read", "edit"], COPILOT_TOOLS)
        assert isinstance(result, list)
        assert result == sorted(set(result))  # sorted + deduped
        assert len(result) > 0

    def test_routes_to_handoffs(self):
        """routes-to entries must convert to handoffs with correct keys."""
        from dx_agent_dev_gen.transformers import routes_to_handoffs

        routes = [
            {"label": "Build", "target": "dx-builder", "description": "Route to builder"},
        ]
        handoffs = routes_to_handoffs(routes)
        assert len(handoffs) == 1
        h = handoffs[0]
        assert h["label"] == "Build"
        assert h["agent"] == "dx-builder"
        assert h["prompt"] == "Route to builder"
        assert h["send"] is False


# ---------------------------------------------------------------------------
# Instruction template validation
# ---------------------------------------------------------------------------


class TestTemplatePlaceholders:
    """Generated instruction files must not have leftover {{...}} placeholders."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_no_leftover_placeholders(self, project: str, root: Path):
        """CLAUDE.md, AGENTS.md, copilot-instructions.md must not contain {{...}}."""
        import re

        pattern = re.compile(r"\{\{[A-Z_:]+\}\}")
        instruction_files = [
            root / "CLAUDE.md",
            root / "AGENTS.md",
            root / ".github" / "copilot-instructions.md",
            root / "CLAUDE-KO.md",
            root / "AGENTS-KO.md",
            root / ".github" / "copilot-instructions-KO.md",
        ]
        leftover = []
        for f in instruction_files:
            if f.exists():
                content = f.read_text(encoding="utf-8")
                matches = pattern.findall(content)
                if matches:
                    leftover.append(f"{f.name}: {matches}")
        assert not leftover, (
            f"{project}: Leftover template placeholders: {leftover}"
        )


class TestKOStructuralParity:
    """KO instruction files must have the same section structure as EN."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_ko_sections_match_en(self, project: str, root: Path):
        """KO files must have same number of ## headings as EN counterparts."""
        import re

        pairs = [
            ("CLAUDE.md", "CLAUDE-KO.md"),
            ("AGENTS.md", "AGENTS-KO.md"),
            ("copilot-instructions.md", "copilot-instructions-KO.md"),
        ]
        heading_re = re.compile(r"^#{1,3} ", re.MULTILINE)
        mismatches = []
        for en_name, ko_name in pairs:
            if "copilot" in en_name:
                en_path = root / ".github" / en_name
                ko_path = root / ".github" / ko_name
            else:
                en_path = root / en_name
                ko_path = root / ko_name
            if not en_path.exists() or not ko_path.exists():
                continue
            en_count = len(heading_re.findall(en_path.read_text(encoding="utf-8")))
            ko_count = len(heading_re.findall(ko_path.read_text(encoding="utf-8")))
            if en_count != ko_count:
                mismatches.append(
                    f"{en_name}({en_count}) != {ko_name}({ko_count})"
                )
        assert not mismatches, (
            f"{project}: KO/EN heading count mismatch: {mismatches}"
        )


class TestInstructionGeneratorClean:
    """Instruction generation must match disk for all repos."""

    @pytest.mark.parametrize(
        "project,root",
        list(PROJECT_ROOTS.items()),
        ids=list(PROJECT_ROOTS.keys()),
    )
    def test_instructions_check_clean(self, project: str, root: Path):
        """dx-agent-gen check --platform instructions must be clean."""
        from dx_agent_dev_gen.generator import Generator

        gen = Generator(root)
        clean, report = gen.check(platform="instructions")
        assert clean, (
            f"{project}: Instruction drift:\n" + "\n".join(report)
        )


# ---------------------------------------------------------------------------
# Prune — remove stale generator outputs (orphans), never hand-authored files
# ---------------------------------------------------------------------------


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _make_min_repo(tmp_path: Path) -> Path:
    """A minimal repo with one skill + one agent so generate() produces outputs."""
    deepx = tmp_path / ".deepx"
    _write(
        deepx / "skills" / "dx-foo" / "SKILL.md",
        "---\nname: dx-foo\ndescription: Foo skill for tests.\n---\n\nBody of foo.\n",
    )
    _write(
        deepx / "agents" / "dx-bar.md",
        "---\nname: dx-bar\ndescription: Bar agent for tests.\n"
        "capabilities: [read, execute]\n---\n\nBar agent body.\n",
    )
    return tmp_path


class TestGeneratorPrune:
    """`prune` removes orphan outputs (renamed/removed source) but preserves
    live generated files AND hand-authored files."""

    AUTO_MARKER = "AUTO-GENERATED from .deepx/"

    def _inject_orphans(self, repo: Path):
        """Returns (orphans, keepers) path lists."""
        orphans = [
            repo / ".github" / "skills" / "dx-old" / "SKILL.md",
            repo / ".claude" / "skills" / "dx-old" / "SKILL.md",
            repo / ".cursor" / "rules" / "skill-dx-old.mdc",
            repo / ".github" / "agents" / "dx-oldagent.agent.md",
            repo / ".claude" / "agents" / "dx-oldagent.md",
            repo / ".opencode" / "agents" / "dx-oldagent.md",
            repo / ".cursor" / "rules" / "dx-oldagent.mdc",  # orphan agent rule
        ]
        for o in orphans:
            # orphan agent rule must carry the gen marker to be eligible
            body = f"<!-- {self.AUTO_MARKER} -->\nstale\n" if o.suffix == ".mdc" else "stale\n"
            _write(o, body)
        # hand-authored cursor rule WITHOUT the gen marker — must be preserved
        hand = repo / ".cursor" / "rules" / "python-example.mdc"
        _write(hand, "---\ndescription: hand-authored\n---\nKeep me.\n")
        return orphans, [hand]

    def test_prune_dry_run_lists_orphans_only(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator

        repo = _make_min_repo(tmp_path)
        gen = Generator(repo)
        gen.generate(platform="all")
        live = set(gen._collect_expected("all"))
        orphans, keepers = self._inject_orphans(repo)

        removed, report = gen.prune(platform="all", dry_run=True)
        removed = set(removed)

        def _covered(p: Path) -> bool:
            # prune may remove a whole skill dir, which subsumes its SKILL.md
            return p in removed or any(parent in removed for parent in p.parents)

        # every injected orphan is flagged (directly or via its parent dir)
        for o in orphans:
            assert _covered(o), f"orphan not flagged: {o.relative_to(repo)}\n{report}"
        # hand-authored + live outputs are NOT flagged
        for k in keepers:
            assert k not in removed, f"hand-authored wrongly flagged: {k}"
        assert not (live & removed), "live generated output wrongly flagged for prune"
        # dry-run must not delete anything
        for o in orphans:
            assert o.exists(), "dry-run deleted a file"

    def test_prune_deletes_orphans_preserves_rest(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator

        repo = _make_min_repo(tmp_path)
        gen = Generator(repo)
        gen.generate(platform="all")
        live = set(gen._collect_expected("all"))
        orphans, keepers = self._inject_orphans(repo)

        gen.prune(platform="all", dry_run=False)

        for o in orphans:
            assert not o.exists(), f"orphan not pruned: {o.relative_to(repo)}"
        for k in keepers:
            assert k.exists(), f"hand-authored file wrongly deleted: {k}"
        for f in live:
            assert f.exists(), f"live generated file wrongly deleted: {f}"

    def test_prune_is_idempotent(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator

        repo = _make_min_repo(tmp_path)
        gen = Generator(repo)
        gen.generate(platform="all")
        self._inject_orphans(repo)
        gen.prune(platform="all", dry_run=False)
        removed2, _ = gen.prune(platform="all", dry_run=False)
        assert removed2 == [], "second prune should find nothing"

    def test_generate_prune_integration_via_cli(self, tmp_path):
        from dx_agent_dev_gen.cli import main

        repo = _make_min_repo(tmp_path)
        # first generate to lay down live outputs
        assert main(["generate", "--repo", str(repo)]) == 0
        orphans, keepers = self._inject_orphans(repo)
        # generate --prune should remove orphans in one pass
        rc = main(["generate", "--repo", str(repo), "--prune"])
        assert rc == 0
        for o in orphans:
            assert not o.exists(), f"generate --prune left orphan: {o.relative_to(repo)}"
        for k in keepers:
            assert k.exists(), f"generate --prune deleted hand-authored: {k}"


# ---------------------------------------------------------------------------
# Template context: live model/task counts (Approach C, 2026-09-04)
# ---------------------------------------------------------------------------


def _mk_repo(tmp_path: Path, *, registry: int | None, tasks: tuple[str, ...]) -> Path:
    repo = tmp_path / "repo"
    (repo / ".deepx" / "templates" / "en").mkdir(parents=True)
    (repo / ".deepx" / "templates" / "en" / "CLAUDE.md.tmpl").write_text(
        "{{MODEL_COUNT}} models across {{TASK_COUNT}} AI tasks\n", encoding="utf-8")
    if registry is not None:
        (repo / "config").mkdir()
        (repo / "config" / "model_registry.json").write_text(
            json.dumps(
                [{"model_name": f"m{i}", "dxnn_file": f"m{i}.dxnn"} for i in range(registry)]
            ),
            encoding="utf-8")
    for t in tasks:
        (repo / "src" / "python_example" / t).mkdir(parents=True)
    return repo


class TestTemplateContextCounts:
    """{{MODEL_COUNT}}/{{TASK_COUNT}}/{{TASK_LIST}} come from the live registry /
    task dirs (single source of truth: dx_agent_dev_gen.counts)."""

    def test_counts_substituted_from_registry_and_task_dirs(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator
        # '__pycache__' and '.hidden' must be filtered like 'common'.
        repo = _mk_repo(tmp_path, registry=3, tasks=("a", "b", "common", "__pycache__", ".hidden"))
        out = Generator(repo)._generate_instructions()
        content = out[repo / "CLAUDE.md"]
        assert content == "3 models across 2 AI tasks\n"

    def test_suite_level_resolves_nested_dx_app(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator
        repo = _mk_repo(tmp_path, registry=None, tasks=())
        nested = repo / "dx-runtime" / "dx_app"
        (nested / "config").mkdir(parents=True)
        (nested / "config" / "model_registry.json").write_text("[{}, {}, {}, {}]", encoding="utf-8")
        (nested / "src" / "python_example" / "det").mkdir(parents=True)
        content = Generator(repo)._generate_instructions()[repo / "CLAUDE.md"]
        assert content == "4 models across 1 AI tasks\n"

    def test_middle_candidate_dx_runtime_layout(self, tmp_path):
        """dx-runtime itself (not the suite) reaches dx_app via ./dx_app."""
        from dx_agent_dev_gen.generator import Generator
        repo = _mk_repo(tmp_path, registry=None, tasks=())
        middle = repo / "dx_app"
        (middle / "config").mkdir(parents=True)
        (middle / "config" / "model_registry.json").write_text("[{}, {}]", encoding="utf-8")
        (middle / "src" / "python_example" / "x").mkdir(parents=True)
        content = Generator(repo)._generate_instructions()[repo / "CLAUDE.md"]
        assert content == "2 models across 1 AI tasks\n"

    def test_missing_registry_fails_loudly(self, tmp_path):
        """No silent fallback: an unresolved {{MODEL_COUNT}}/{{TASK_COUNT}} raises
        instead of emitting a wrong number or a leftover placeholder that could
        slip through unnoticed."""
        from dx_agent_dev_gen.generator import Generator
        repo = _mk_repo(tmp_path, registry=None, tasks=())
        with pytest.raises(RuntimeError, match="MODEL_COUNT"):
            Generator(repo)._generate_instructions()

    def test_malformed_registry_fails_loudly(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator
        repo = _mk_repo(tmp_path, registry=None, tasks=())
        (repo / "config").mkdir()
        (repo / "config" / "model_registry.json").write_text("{ not json", encoding="utf-8")
        with pytest.raises(RuntimeError, match="MODEL_COUNT"):
            Generator(repo)._generate_instructions()

    def test_task_list_variable(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator
        repo = tmp_path / "repo"
        (repo / ".deepx" / "templates" / "en").mkdir(parents=True)
        (repo / ".deepx" / "templates" / "en" / "CLAUDE.md.tmpl").write_text(
            "{{TASK_LIST}}\n", encoding="utf-8")
        (repo / "config").mkdir()
        (repo / "config" / "model_registry.json").write_text("[{}]", encoding="utf-8")
        for t in ("b", "a", "common"):
            (repo / "src" / "python_example" / t).mkdir(parents=True)
        content = Generator(repo)._generate_instructions()[repo / "CLAUDE.md"]
        assert content == "a, b\n"

    def test_check_on_repo_without_variables_does_not_raise(self, tmp_path):
        """A repo whose templates carry no MODEL_COUNT/TASK_COUNT/TASK_LIST
        placeholders (dx-compiler, dx_stream) must not be affected by the
        leftover-variable hard-fail."""
        from dx_agent_dev_gen.generator import Generator
        repo = tmp_path / "repo"
        (repo / ".deepx" / "templates" / "en").mkdir(parents=True)
        (repo / ".deepx" / "templates" / "en" / "CLAUDE.md.tmpl").write_text(
            "no variables here\n", encoding="utf-8")
        content = Generator(repo)._generate_instructions()[repo / "CLAUDE.md"]
        assert content == "no variables here\n"

    def test_unrelated_leftover_variable_does_not_mention_submodule(self, tmp_path):
        """An unresolved variable unrelated to MODEL_COUNT/TASK_COUNT/TASK_LIST
        (e.g. a typo'd template placeholder) must raise mentioning the actual
        variable name, but must NOT suggest `git submodule update` — that hint
        is only correct when the leftover is one of the registry-derived vars."""
        from dx_agent_dev_gen.generator import Generator
        repo = _mk_repo(tmp_path, registry=1, tasks=("a",))
        (repo / ".deepx" / "templates" / "en" / "CLAUDE.md.tmpl").write_text(
            "{{FOO}}\n", encoding="utf-8")
        with pytest.raises(RuntimeError, match="FOO") as exc_info:
            Generator(repo)._generate_instructions()
        assert "submodule update" not in str(exc_info.value)


# ---------------------------------------------------------------------------
# check() drift hint: run_all.sh only exists at the suite root (polish round Q5)
# ---------------------------------------------------------------------------


def _mk_drifted_repo_under_suite(tmp_path: Path) -> Path:
    """A minimal nested repo (two levels under a fake suite root) with one
    agent whose .claude/ counterpart is missing on disk, so check() reports
    drift. A fake .deepx/tools/scripts/run_all.sh marks the suite root."""
    suite = tmp_path / "suite"
    (suite / ".deepx" / "tools" / "scripts").mkdir(parents=True)
    (suite / ".deepx" / "tools" / "scripts" / "run_all.sh").write_text(
        "#!/usr/bin/env bash\necho fake run_all.sh\n", encoding="utf-8"
    )
    repo = suite / "dx-runtime" / "dx_app"
    (repo / ".deepx" / "agents").mkdir(parents=True)
    (repo / ".deepx" / "agents" / "dx-x.md").write_text(
        "---\nname: dx-x\ndescription: test agent\n---\nBody.\n", encoding="utf-8"
    )
    # Deliberately do NOT create .claude/agents/dx-x.md -> MISSING drift.
    return repo


class TestCheckDriftHintSuiteRoot:
    """check()'s drift hint must name a run_all.sh that actually exists at
    the level it's suggesting — the old hardcoded 'run_all.sh' (with no
    path) only resolves from the suite root, so a nested repo (e.g.
    dx-runtime/dx_app) got a misleading recommendation."""

    def test_drift_hint_names_suite_root_run_all_and_per_repo_fallback(self, tmp_path):
        """When run_all.sh is found, the hint is two proper sentences: the
        recommended run_all.sh command, then the per-level fallback."""
        from dx_agent_dev_gen.generator import Generator

        repo = _mk_drifted_repo_under_suite(tmp_path)
        clean, report = Generator(repo).check(platform="claude")
        assert not clean
        text = "\n".join(report)
        run_all = repo.parent.parent / ".deepx" / "tools" / "scripts" / "run_all.sh"
        assert (
            f"Run 'bash {run_all}' to regenerate ALL levels (recommended)." in text
        )
        assert (
            f"Or: 'dx-agent-gen generate --repo {repo}' for this level only." in text
        )

    def test_drift_hint_falls_back_when_no_suite_root_found(self, tmp_path):
        """A repo with no discoverable run_all.sh anywhere above it gets only
        the single per-level fallback sentence, without a dangling run_all.sh
        recommendation."""
        from dx_agent_dev_gen.generator import Generator

        repo = tmp_path / "standalone_repo"
        (repo / ".deepx" / "agents").mkdir(parents=True)
        (repo / ".deepx" / "agents" / "dx-x.md").write_text(
            "---\nname: dx-x\ndescription: test agent\n---\nBody.\n", encoding="utf-8"
        )
        clean, report = Generator(repo).check(platform="claude")
        assert not clean
        text = "\n".join(report)
        assert "run_all.sh" not in text
        assert f"Run 'dx-agent-gen generate --repo {repo}' to update." in text

    def test_run_all_hint_is_absolute_for_a_relative_repo_path(self, tmp_path, monkeypatch):
        """polish round F3: _find_run_all_sh() must resolve self.repo before
        walking up, so a relative --repo argument (e.g. the cwd-relative
        default Path('.') the CLI passes) still produces an absolute,
        actually-runnable run_all.sh path in the hint — not a relative one
        that silently means something different once printed and copy-pasted
        from a different cwd."""
        from dx_agent_dev_gen.generator import Generator

        repo = _mk_drifted_repo_under_suite(tmp_path)
        monkeypatch.chdir(repo.parent.parent)  # cwd = the fake suite root
        rel_repo = Path("dx-runtime") / "dx_app"  # relative to new cwd
        clean, report = Generator(rel_repo).check(platform="claude")
        assert not clean
        text = "\n".join(report)
        run_all = repo.parent.parent / ".deepx" / "tools" / "scripts" / "run_all.sh"
        assert f"Run 'bash {run_all}'" in text
        assert run_all.is_absolute()


# ---------------------------------------------------------------------------
# check() keeps the drift report when one template raises (polish round Q6)
# ---------------------------------------------------------------------------


class TestCheckSurvivesTemplateRuntimeError:
    """A RuntimeError from one platform's generation (e.g. an unresolved
    template placeholder) must not abort check() before it reports drift
    already found in other platforms — the error becomes an ERROR: line and
    check() continues to the next platform instead of propagating."""

    def test_check_reports_both_drift_and_template_error(self, tmp_path):
        from dx_agent_dev_gen.generator import Generator

        repo = _mk_drifted_repo_under_suite(tmp_path)
        # Force _generate_instructions() to raise by adding a bad template.
        (repo / ".deepx" / "templates" / "en").mkdir(parents=True)
        (repo / ".deepx" / "templates" / "en" / "CLAUDE.md.tmpl").write_text(
            "{{FOO}}\n", encoding="utf-8"
        )

        clean, report = Generator(repo).check(platform="all")
        assert clean is False
        text = "\n".join(report)
        assert "CHANGED:" in text or "MISSING:" in text
        assert "ERROR: instructions:" in text
        assert "FOO" in text
