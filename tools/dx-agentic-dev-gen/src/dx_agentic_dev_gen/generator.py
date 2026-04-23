"""Main generator orchestrator."""

from __future__ import annotations

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
                    results[path] = "written"

        return results

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
            report.append(f"\nRun 'dx-agentic-gen generate' to update.")

        return clean, report

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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

            # Build skills get directory layout, utility skills get flat files
            if name.startswith("dx-build-") or name.startswith("dx-tdd") or "/" in name:
                files[github / "skills" / name / "SKILL.md"] = content
            else:
                # All skills in subdirectory layout for consistency
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
            mdc_fm = f"---\ndescription: \"{desc}\"\nalwaysApply: false\n---\n"
            header = self._header(f".deepx/agents/{stem}.md")
            content = mdc_fm + "\n" + header + "\n" + body
            files[cursor / f"{stem}.mdc"] = content

        # Skill rules
        for name, fm, body in self._read_skills():
            desc = fm.get("description", first_paragraph(body))
            mdc_fm = f"---\ndescription: \"{desc}\"\nalwaysApply: false\n---\n"
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
