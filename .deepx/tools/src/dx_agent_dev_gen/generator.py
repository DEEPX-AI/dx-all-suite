"""Main generator orchestrator."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Any

from .frontmatter import strip_frontmatter, build_frontmatter, first_paragraph
from .transformers import (
    rewrite_deepx_to_github,
    capabilities_to_tools,
    routes_to_handoffs,
)
from .constants import COPILOT_TOOLS, CLAUDE_TOOLS, OPENCODE_TOOLS, GENERATED_HEADER


class Generator:
    """Generates platform-specific files from .deepx/ canonical source."""

    def __init__(self, repo_root: Path) -> None:
        self.repo = repo_root
        self.deepx = repo_root / ".deepx"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate(
        self,
        *,
        platform: str = "all",
        dry_run: bool = False,
    ) -> dict[Path, str]:
        """Generate platform files. Returns {path: action} dict."""
        results: dict[Path, str] = {}

        platforms = (
            ["copilot", "claude", "opencode", "cursor", "instructions"]
            if platform == "all"
            else [platform]
        )

        for plat in platforms:
            method = getattr(self, f"_generate_{plat}")
            files = method()
            for path, content in files.items():
                if dry_run:
                    if path.exists():
                        existing = path.read_text(encoding="utf-8")
                        results[path] = "UNCHANGED" if existing == content else "CHANGED"
                    else:
                        results[path] = "NEW"
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
                    # Ensure generated files are non-executable (644)
                    # regardless of umask or execution context
                    os.chmod(path, 0o644)
                    results[path] = "written"

        return results

    _PLATFORMS = ["copilot", "claude", "opencode", "cursor", "instructions"]

    def _platform_list(self, platform: str) -> list[str]:
        return self._PLATFORMS if platform == "all" else [platform]

    def _collect_expected(self, platform: str = "all") -> set[Path]:
        """The exact set of paths the generator would write for `platform`."""
        expected: set[Path] = set()
        for plat in self._platform_list(platform):
            expected |= set(getattr(self, f"_generate_{plat}")().keys())
        return expected

    def prune(
        self,
        *,
        platform: str = "all",
        dry_run: bool = False,
    ) -> tuple[list[Path], list[str]]:
        """Remove stale generator outputs (orphans) — files in generator-owned
        locations that the generator would no longer produce (e.g. left over
        after a skill/agent was renamed). Hand-authored files are never touched.

        Returns (removed_paths, report_lines).

        Safety model — only delete inside locations the generator solely owns,
        matched by generator-specific patterns, and absent from the expected set:
          * skill dirs   .github/skills/<n>/, .claude/skills/<n>/  (1 dir == 1 skill)
          * cursor skill rules  .cursor/rules/skill-*.mdc          (skill- is ours)
          * agent files  .github/agents/*.agent.md, .claude/agents/*.md,
                         .opencode/agents/*.md                     (pure-generated dirs)
          * cursor agent rules  .cursor/rules/<stem>.mdc           (only if it carries
                         the AUTO-GENERATED header — protects hand-authored .mdc)
        """
        expected = self._collect_expected(platform)
        plats = set(self._platform_list(platform))
        candidates: list[Path] = []

        # 1. skill output dirs (copilot -> .github, claude -> .claude)
        skill_bases = []
        if "copilot" in plats:
            skill_bases.append(self.repo / ".github" / "skills")
        if "claude" in plats:
            skill_bases.append(self.repo / ".claude" / "skills")
        for base in skill_bases:
            if base.is_dir():
                for d in sorted(base.iterdir()):
                    if d.is_dir() and (d / "SKILL.md") not in expected:
                        candidates.append(d)

        # 2. cursor skill rules (skill- prefix is generator-exclusive)
        if "cursor" in plats:
            cur = self.repo / ".cursor" / "rules"
            if cur.is_dir():
                for f in sorted(cur.glob("skill-*.mdc")):
                    if f not in expected:
                        candidates.append(f)

        # 3. agent files in pure-generated dirs
        agent_scopes = []
        if "copilot" in plats:
            agent_scopes.append((self.repo / ".github" / "agents", "*.agent.md"))
        if "claude" in plats:
            agent_scopes.append((self.repo / ".claude" / "agents", "*.md"))
        if "opencode" in plats:
            agent_scopes.append((self.repo / ".opencode" / "agents", "*.md"))
        for base, pat in agent_scopes:
            if base.is_dir():
                for f in sorted(base.glob(pat)):
                    if f not in expected:
                        candidates.append(f)

        # 4. cursor agent rules (non-skill) — header-gated so hand-authored
        #    .mdc files (no AUTO-GENERATED header) are never removed
        if "cursor" in plats:
            cur = self.repo / ".cursor" / "rules"
            if cur.is_dir():
                for f in sorted(cur.glob("*.mdc")):
                    if f.name.startswith("skill-") or f in expected:
                        continue
                    try:
                        text = f.read_text(encoding="utf-8")
                    except Exception:
                        continue
                    if "AUTO-GENERATED from .deepx/" in text:
                        candidates.append(f)

        report: list[str] = []
        removed: list[Path] = []
        for path in candidates:
            rel = path.relative_to(self.repo)
            if dry_run:
                report.append(f"WOULD PRUNE: {rel}")
            else:
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                report.append(f"PRUNED: {rel}")
            removed.append(path)

        if not removed:
            report.append("No orphan generated files to prune.")
        return removed, report

    def check(self, *, platform: str = "all") -> tuple[bool, list[str]]:
        """Check if generated files match on-disk. Returns (clean, report_lines)."""
        report: list[str] = []
        clean = True

        platforms = (
            ["copilot", "claude", "opencode", "cursor", "instructions"]
            if platform == "all"
            else [platform]
        )

        for plat in platforms:
            method = getattr(self, f"_generate_{plat}")
            files = method()
            for path, expected in files.items():
                if not path.exists():
                    report.append(f"MISSING: {path.relative_to(self.repo)}")
                    clean = False
                else:
                    actual = path.read_text(encoding="utf-8")
                    if actual != expected:
                        report.append(f"CHANGED: {path.relative_to(self.repo)}")
                        clean = False

        if clean:
            report.append("All generated files are up-to-date.")
        else:
            report.append(f"\nRun 'dx-agent-gen generate' to update.")

        return clean, report

    def lint(self) -> tuple[bool, list[str]]:
        """Check EN/KO fragment parity.

        Verifies:
        1. Every EN fragment has a matching KO counterpart (pair existence).
        2. Structural markers present in EN (Q1./Q2./Q3. decision-tree anchors)
           are also present in KO.

        Returns (clean, report_lines) — mirrors check() API.
        """
        report: list[str] = []
        clean = True

        fragments_dir = self._find_fragments_dir()
        if not fragments_dir:
            report.append("SKIP: no fragments directory found (nothing to lint).")
            return True, report

        en_dir = fragments_dir / "en"
        ko_dir = fragments_dir / "ko"

        en_files: dict[str, Path] = {}
        ko_files: dict[str, Path] = {}

        if en_dir.is_dir():
            for f in sorted(en_dir.glob("*.md")):
                en_files[f.stem] = f
        if ko_dir.is_dir():
            for f in sorted(ko_dir.glob("*.md")):
                ko_files[f.stem] = f

        if not en_files and not ko_files:
            report.append("SKIP: no fragment files found.")
            return True, report

        # ── Check 1: pair existence ──────────────────────────────────────
        for stem in sorted(en_files):
            if stem not in ko_files:
                report.append(
                    f"[ERROR] {stem}: EN fragment has no KO counterpart "
                    f"(missing {ko_dir.relative_to(self.repo) if ko_dir.is_relative_to(self.repo) else ko_dir}/{stem}.md)"
                )
                clean = False
            else:
                report.append(f"[OK] {stem}: EN/KO pair exists.")

        for stem in sorted(ko_files):
            if stem not in en_files:
                report.append(
                    f"[WARN] {stem}: KO fragment has no EN counterpart."
                )

        # ── Check 2: structural marker parity ───────────────────────────
        # Markers: decision-tree question anchors used in Pre-flight Classification.
        # Pattern: lines containing "**Q<digit>." (e.g. "> **Q1.", "**Q1. Is the")
        import re

        MARKER_PATTERN = re.compile(r"\*\*Q\d+\.")

        for stem in sorted(en_files):
            if stem not in ko_files:
                continue  # already reported as missing pair above

            en_text = en_files[stem].read_text(encoding="utf-8")
            ko_text = ko_files[stem].read_text(encoding="utf-8")

            en_markers = MARKER_PATTERN.findall(en_text)
            ko_markers = MARKER_PATTERN.findall(ko_text)

            if en_markers and not ko_markers:
                missing = sorted(set(en_markers))
                report.append(
                    f"[ERROR] {stem}: KO fragment is missing structural markers "
                    f"found in EN: {missing}"
                )
                clean = False
            elif set(en_markers) != set(ko_markers):
                en_set = sorted(set(en_markers))
                ko_set = sorted(set(ko_markers))
                report.append(
                    f"[WARN] {stem}: EN/KO structural markers differ — "
                    f"EN: {en_set}, KO: {ko_set}"
                )

        # ── Check 3: line-count divergence (EN significantly longer than KO) ──
        # Directional: flag only when EN > KO by ≥ threshold.
        # KO translations are sometimes more verbose than EN (e.g., session-sentinels:
        # EN=52, KO=61) — that is expected and must not be flagged.
        # Threshold: ≥ 10 absolute lines where EN > KO → stale KO indicator.
        LINE_DIFF_THRESHOLD = 10

        for stem in sorted(en_files):
            if stem not in ko_files:
                continue  # already reported as missing pair above

            en_count = len(en_files[stem].read_text(encoding="utf-8").splitlines())
            ko_count = len(ko_files[stem].read_text(encoding="utf-8").splitlines())
            diff = en_count - ko_count

            if diff >= LINE_DIFF_THRESHOLD:
                report.append(
                    f"[ERROR] {stem}: EN fragment has {diff} more lines than KO "
                    f"(EN={en_count}, KO={ko_count}) — KO may be stale. "
                    f"Update .deepx/templates/fragments/ko/{stem}.md, "
                    "then run 'dx-agent-gen generate'."
                )
                clean = False

        # ── Check 4: no Korean text in non-KO .deepx/ files ────────────────
        ko_clean, ko_report = self._check_korean_in_non_ko_files()
        report.extend(ko_report)
        if not ko_clean:
            clean = False

        if clean:
            report.append("All EN/KO fragment pairs are consistent.")
        else:
            report.append(
                "\nFix: update the KO fragment in "
                ".deepx/templates/fragments/ko/, then run "
                "'dx-agent-gen generate'.\n"
                "For intentional Korean in EN files, add "
                "'<!-- KOREAN-OK: <reason> -->' at the end of the line."
            )

        return clean, report

    def _check_korean_in_non_ko_files(self) -> tuple[bool, list[str]]:
        """Check 4: No Korean characters in non-KO .deepx/ markdown files.

        A line is exempt if it ends with (or contains) a
        ``<!-- KOREAN-OK: <reason> -->`` annotation.

        Scope: this check applies only to **fragment-system-related** files
        (agents, skills, templates, fragments, docs, memory). Directories that
        host standalone tooling (`.deepx/tests/`, `.deepx/tools/scripts/`) are
        exempt \u2014 their READMEs are end-user documentation that may be authored
        in either language depending on audience.

        Returns (clean, report_lines).
        """
        import re as _re

        KOREAN = _re.compile(r"[\uAC00-\uD7A3\u3131-\u318E\u3200-\u32FF]")
        EXEMPT = _re.compile(r"<!--\s*KOREAN-OK\b.*?-->", _re.IGNORECASE)

        # Top-level directories under .deepx/ that ARE subject to the fragment
        # canonical-source rule (EN/KO split). All other paths are user-facing
        # docs / standalone tools where mixed-language content is permitted.
        FRAGMENT_SCOPE = {"agents", "skills", "templates", "fragments", "docs", "memory"}

        report: list[str] = []
        clean = True

        if not self.deepx.is_dir():
            return True, []

        for md_file in sorted(self.deepx.rglob("*.md")):
            # Skip KO files: name contains -KO/_KO, or file lives in a /ko/ dir
            name = md_file.name
            if "-KO" in name or "_KO" in name:
                continue
            if "ko" in md_file.parts:
                continue
            # Scope filter: only check files inside fragment-scope subtrees of .deepx/
            try:
                rel_parts = md_file.relative_to(self.deepx).parts
            except ValueError:
                continue
            if not rel_parts:
                continue
            top = rel_parts[0]
            # Top-level README.md of .deepx/ itself IS checked (it's an index doc)
            if top == name and top.endswith(".md"):
                pass  # top-level file like .deepx/README.md \u2192 check
            elif top not in FRAGMENT_SCOPE:
                continue  # outside fragment system \u2192 skip

            try:
                lines = md_file.read_text(encoding="utf-8").splitlines()
            except Exception:
                continue

            in_code_block = False
            for lineno, line in enumerate(lines, 1):
                # Skip fenced code blocks (```...```)
                stripped = line.lstrip()
                if stripped.startswith("```"):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue
                if not KOREAN.search(line):
                    continue
                if EXEMPT.search(line):
                    continue
                rel = md_file.relative_to(self.repo)
                report.append(
                    f"[ERROR] Korean text in non-KO file {rel}:{lineno}: "
                    f"{line.strip()[:80]}"
                )
                clean = False

        return clean, report

    def _read_agents(self) -> list[tuple[str, dict, str]]:
        """Read all .deepx/agents/*.md files.
        
        Returns list of (stem, frontmatter_dict, body).
        """
        agents_dir = self.deepx / "agents"
        if not agents_dir.is_dir():
            return []
        result = []
        for f in sorted(agents_dir.glob("*.md")):
            content = f.read_text(encoding="utf-8")
            fm, body = strip_frontmatter(content)
            result.append((f.stem, fm, body))
        return result

    def _read_skills(self) -> list[tuple[str, dict, str]]:
        """Read all .deepx/skills/*/SKILL.md and .deepx/skills/*.md files.
        
        Returns list of (name, frontmatter_dict, body).
        """
        skills_dir = self.deepx / "skills"
        if not skills_dir.is_dir():
            return []
        result = []
        # Subdirectory pattern: skills/dx-xxx/SKILL.md
        for d in sorted(skills_dir.iterdir()):
            if d.is_dir():
                skill_md = d / "SKILL.md"
                if skill_md.exists():
                    content = skill_md.read_text(encoding="utf-8")
                    fm, body = strip_frontmatter(content)
                    result.append((d.name, fm, body))
        # Flat file pattern: skills/dx-xxx.md
        for f in sorted(skills_dir.glob("*.md")):
            if f.is_file():
                content = f.read_text(encoding="utf-8")
                fm, body = strip_frontmatter(content)
                result.append((f.stem, fm, body))
        return result

    def _header(self, source_rel: str) -> str:
        """Generate the AUTO-GENERATED header comment."""
        return GENERATED_HEADER.format(source=source_rel)

    # ------------------------------------------------------------------
    # Platform generators (stubs — to be implemented)
    # ------------------------------------------------------------------

    def _generate_copilot(self) -> dict[Path, str]:
        """Generate .github/agents/ and .github/skills/ files."""
        files: dict[Path, str] = {}
        github = self.repo / ".github"

        # --- Agents ---
        for stem, fm, body in self._read_agents():
            caps = fm.get("capabilities", [])
            routes = fm.get("routes-to", [])

            out_fm: dict[str, Any] = {
                "name": fm.get("name", stem),
                "description": fm.get("description", ""),
            }
            if fm.get("argument-hint"):
                out_fm["argument-hint"] = fm["argument-hint"]

            out_fm["tools"] = capabilities_to_tools(caps, COPILOT_TOOLS)

            if routes:
                out_fm["handoffs"] = routes_to_handoffs(routes)

            header = self._header(f".deepx/agents/{stem}.md")
            content = build_frontmatter(out_fm) + "\n" + header + "\n" + rewrite_deepx_to_github(body)
            files[github / "agents" / f"{stem}.agent.md"] = content

        # --- Skills (inline copy) ---
        for name, fm, body in self._read_skills():
            skill_fm = {
                "name": fm.get("name", name),
                "description": fm.get("description", first_paragraph(body)),
            }
            header = self._header(f".deepx/skills/{name}/SKILL.md")
            skill_body = rewrite_deepx_to_github(body)
            content = build_frontmatter(skill_fm) + "\n" + header + "\n" + skill_body
            files[github / "skills" / name / "SKILL.md"] = content

        return files

    def _generate_claude(self) -> dict[Path, str]:
        """Generate .claude/agents/ and .claude/skills/ files."""
        files: dict[Path, str] = {}
        claude = self.repo / ".claude"

        # --- Agents ---
        for stem, fm, body in self._read_agents():
            caps = fm.get("capabilities", [])
            out_fm = {
                "name": fm.get("name", stem),
                "description": fm.get("description", ""),
                "tools": capabilities_to_tools(caps, CLAUDE_TOOLS),
            }
            header = self._header(f".deepx/agents/{stem}.md")
            # Claude can read .deepx/ directly — no path rewriting
            content = build_frontmatter(out_fm) + "\n" + header + "\n" + body
            files[claude / "agents" / f"{stem}.md"] = content

        # --- Skills (thin wrappers) ---
        for name, fm, body in self._read_skills():
            skill_fm = {
                "name": fm.get("name", name),
                "description": fm.get("description", first_paragraph(body)),
            }
            header = "<!-- Thin Claude Code wrapper — canonical skill doc lives in .deepx/ -->"
            # Determine source path
            skill_dir = self.deepx / "skills" / name
            if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                ref = f".deepx/skills/{name}/SKILL.md"
            else:
                ref = f".deepx/skills/{name}.md"

            content = (
                build_frontmatter(skill_fm)
                + "\n"
                + header
                + "\n\n"
                + f"Read and follow the complete skill documentation at `{ref}`.\n"
            )
            files[claude / "skills" / name / "SKILL.md"] = content

        return files

    def _generate_opencode(self) -> dict[Path, str]:
        """Generate .opencode/agents/ files."""
        files: dict[Path, str] = {}
        oc = self.repo / ".opencode"

        for stem, fm, body in self._read_agents():
            caps = fm.get("capabilities", [])
            # OpenCode uses mode + tools booleans
            out_fm: dict[str, Any] = {
                "description": fm.get("description", ""),
                "mode": "subagent" if "sub-agent" in caps else "normal",
                "tools": {},
            }
            tool_bools: dict[str, bool] = {}
            if "execute" in caps:
                tool_bools["bash"] = True
            if "edit" in caps:
                tool_bools["edit"] = True
                tool_bools["write"] = True
            if "read" in caps or "search" in caps:
                pass  # implicit
            out_fm["tools"] = tool_bools if tool_bools else {"bash": True}

            header = self._header(f".deepx/agents/{stem}.md")
            content = build_frontmatter(out_fm) + "\n" + header + "\n" + body
            files[oc / "agents" / f"{stem}.md"] = content

        return files

    def _generate_cursor(self) -> dict[Path, str]:
        """Generate .cursor/rules/*.mdc files."""
        files: dict[Path, str] = {}
        cursor = self.repo / ".cursor" / "rules"

        # Agent rules
        for stem, fm, body in self._read_agents():
            desc = fm.get("description", "")
            mdc_fm = build_frontmatter(
                {
                    "description": desc,
                    "alwaysApply": False,
                }
            )
            header = self._header(f".deepx/agents/{stem}.md")
            content = mdc_fm + "\n" + header + "\n" + body
            files[cursor / f"{stem}.mdc"] = content

        # Skill rules
        for name, fm, body in self._read_skills():
            desc = fm.get("description", first_paragraph(body))
            mdc_fm = build_frontmatter(
                {
                    "description": desc,
                    "alwaysApply": False,
                }
            )
            # Redirect to .deepx/
            skill_dir = self.deepx / "skills" / name
            if skill_dir.is_dir():
                ref = f".deepx/skills/{name}/SKILL.md"
            else:
                ref = f".deepx/skills/{name}.md"
            content = mdc_fm + f"\nRead and follow the skill documentation at `{ref}`.\n"
            files[cursor / f"skill-{name}.mdc"] = content

        return files

    def _generate_instructions(self) -> dict[Path, str]:
        """Generate CLAUDE.md, AGENTS.md, copilot-instructions.md (EN + KO)."""
        files: dict[Path, str] = {}

        templates_dir = self.deepx / "templates"
        if not templates_dir.is_dir():
            return files

        # Build template context
        context = self._build_template_context()

        # Load fragments
        fragments = self._load_fragments()

        for lang_dir in ["en", "ko"]:
            lang_path = templates_dir / lang_dir
            if not lang_path.is_dir():
                continue
            # Determine which fragment set to use
            frag_set = fragments.get(lang_dir, {})

            for tmpl_file in sorted(lang_path.glob("*.tmpl")):
                # Render template
                content = tmpl_file.read_text(encoding="utf-8")

                # Replace fragment placeholders: {{FRAGMENT:name}}
                for frag_name, frag_content in frag_set.items():
                    placeholder = "{{FRAGMENT:" + frag_name + "}}\n"
                    if placeholder in content:
                        content = content.replace(placeholder, frag_content.rstrip("\n") + "\n")
                    else:
                        # Try without trailing newline
                        placeholder2 = "{{FRAGMENT:" + frag_name + "}}"
                        if placeholder2 in content:
                            content = content.replace(placeholder2, frag_content.rstrip("\n"))

                # Replace context variables: {{KEY}}
                for key, value in context.items():
                    content = content.replace("{{" + key + "}}", value)

                # Determine output path
                out_name = tmpl_file.stem  # e.g., CLAUDE.md, AGENTS-KO.md
                if "copilot-instructions" in out_name:
                    out_path = self.repo / ".github" / out_name
                else:
                    out_path = self.repo / out_name

                files[out_path] = content

        return files

    def _load_fragments(self) -> dict[str, dict[str, str]]:
        """Load fragment files from .deepx/templates/fragments/{en,ko}/.
        
        Searches the current repo first, then walks up parent directories
        to find fragments in a parent repo (e.g., suite root).
        
        Returns: {"en": {"name": "content", ...}, "ko": {...}}
        """
        result: dict[str, dict[str, str]] = {}
        
        # Search for fragments: current repo, then parents
        fragments_dir = self._find_fragments_dir()
        if not fragments_dir:
            return result

        for lang_dir in ["en", "ko"]:
            lang_path = fragments_dir / lang_dir
            if not lang_path.is_dir():
                continue
            frags: dict[str, str] = {}
            for f in sorted(lang_path.glob("*.md")):
                frags[f.stem] = f.read_text(encoding="utf-8")
            result[lang_dir] = frags

        return result

    def _find_fragments_dir(self) -> Path | None:
        """Find .deepx/templates/fragments/ in current repo or parent repos."""
        # Check current repo first
        local = self.deepx / "templates" / "fragments"
        if local.is_dir():
            return local
        
        # Walk up to find a parent with fragments (e.g., suite root)
        current = self.repo.parent
        for _ in range(5):  # max 5 levels up
            candidate = current / ".deepx" / "templates" / "fragments"
            if candidate.is_dir():
                return candidate
            parent = current.parent
            if parent == current:
                break
            current = parent
        
        return None

    def _build_template_context(self) -> dict[str, str]:
        """Build template variable substitutions from .deepx/ content."""
        ctx: dict[str, str] = {}

        # Skills table
        skills = self._read_skills()
        if skills:
            rows = ["| Skill | Description |", "|-------|-------------|"]
            for name, fm, body in skills:
                desc = fm.get("description", first_paragraph(body))
                rows.append(f"| `{name}` | {desc} |")
            ctx["SKILLS_TABLE"] = "\n".join(rows)
        else:
            ctx["SKILLS_TABLE"] = "_No skills defined._"

        # Agents table
        agents = self._read_agents()
        if agents:
            rows = ["| Agent | Description |", "|-------|-------------|"]
            for stem, fm, body in agents:
                desc = fm.get("description", "")
                rows.append(f"| `{stem}` | {desc} |")
            ctx["AGENTS_TABLE"] = "\n".join(rows)
        else:
            ctx["AGENTS_TABLE"] = "_No agents defined._"

        # Routing table — read from .deepx/routing-table.md if exists
        rt_file = self.deepx / "routing-table.md"
        if rt_file.exists():
            ctx["ROUTING_TABLE"] = rt_file.read_text(encoding="utf-8").strip()
        else:
            ctx["ROUTING_TABLE"] = "_No routing table defined._"

        return ctx
