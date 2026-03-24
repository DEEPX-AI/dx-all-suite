# SPDX-License-Identifier: Apache-2.0
"""
Shared fixtures and constants for agentic scenario tests.

Provides project path constants, guide file paths, and agent/skill file
listing fixtures used across all test modules in this suite.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple

import pytest

# ---------------------------------------------------------------------------
# Path constants
# ---------------------------------------------------------------------------

SUITE_ROOT = Path(__file__).resolve().parents[2]  # dx-all-suite/
COMPILER_ROOT = SUITE_ROOT / "dx-compiler"
RUNTIME_ROOT = SUITE_ROOT / "dx-runtime"
APP_ROOT = RUNTIME_ROOT / "dx_app"
STREAM_ROOT = RUNTIME_ROOT / "dx_stream"

# Mapping of project short names to their root paths
PROJECT_ROOTS: Dict[str, Path] = {
    "suite": SUITE_ROOT,
    "compiler": COMPILER_ROOT,
    "runtime": RUNTIME_ROOT,
    "app": APP_ROOT,
    "stream": STREAM_ROOT,
}

# ---------------------------------------------------------------------------
# Guide file definitions (EN/KO pairs)
# ---------------------------------------------------------------------------

@dataclass
class GuidePair:
    """An EN/KO guide document pair."""
    project: str
    en_path: Path
    ko_path: Path
    label: str  # human-readable label


GUIDE_PAIRS: List[GuidePair] = [
    GuidePair(
        project="suite",
        en_path=SUITE_ROOT / "docs/source/agentic_development.md",
        ko_path=SUITE_ROOT / "docs/source/agentic_development-KO.md",
        label="DX All Suite (top-level)",
    ),
    GuidePair(
        project="compiler",
        en_path=COMPILER_ROOT / "source/docs/05_DX-COMPILER_Agentic_Development.md",
        ko_path=COMPILER_ROOT / "source/docs/05_DX-COMPILER_Agentic_Development-KO.md",
        label="DX-COMPILER",
    ),
    GuidePair(
        project="runtime",
        en_path=RUNTIME_ROOT / "docs/source/agentic_development.md",
        ko_path=RUNTIME_ROOT / "docs/source/agentic_development-KO.md",
        label="DX-Runtime",
    ),
    GuidePair(
        project="app",
        en_path=APP_ROOT / "docs/source/docs/12_DX-APP_Agentic_Development.md",
        ko_path=APP_ROOT / "docs/source/docs/12_DX-APP_Agentic_Development-KO.md",
        label="DX-APP",
    ),
    GuidePair(
        project="stream",
        en_path=STREAM_ROOT / "docs/source/docs/08_DX-STREAM_Agentic_Development.md",
        ko_path=STREAM_ROOT / "docs/source/docs/08_DX-STREAM_Agentic_Development-KO.md",
        label="DX-STREAM",
    ),
]


# ---------------------------------------------------------------------------
# Infrastructure file locations per project
# ---------------------------------------------------------------------------

@dataclass
class ProjectInfra:
    """Describes expected agentic infrastructure for a project."""
    project: str
    root: Path
    has_deepx: bool = True  # whether .deepx/ is expected
    has_claude_md: bool = True
    has_agents_md: bool = True
    has_copilot: bool = True
    has_opencode: bool = True
    has_cursor_rules: bool = True


# Note: suite root has NO .deepx/, NO CLAUDE.md
PROJECT_INFRA: List[ProjectInfra] = [
    ProjectInfra("suite", SUITE_ROOT, has_deepx=False, has_claude_md=True, has_copilot=True),
    ProjectInfra("compiler", COMPILER_ROOT),
    ProjectInfra("runtime", RUNTIME_ROOT),
    ProjectInfra("app", APP_ROOT),
    ProjectInfra("stream", STREAM_ROOT),
]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(params=GUIDE_PAIRS, ids=[g.label for g in GUIDE_PAIRS])
def guide_pair(request) -> GuidePair:
    """Parametrized fixture yielding each EN/KO guide pair."""
    return request.param


@pytest.fixture
def all_guide_pairs() -> List[GuidePair]:
    """Return all guide pairs."""
    return GUIDE_PAIRS


@pytest.fixture(params=PROJECT_INFRA, ids=[p.project for p in PROJECT_INFRA])
def project_infra(request) -> ProjectInfra:
    """Parametrized fixture yielding infrastructure info for each project."""
    return request.param


@pytest.fixture
def all_project_infra() -> List[ProjectInfra]:
    """Return all project infrastructure definitions."""
    return PROJECT_INFRA


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def read_markdown(path: Path) -> str:
    """Read a markdown file, raising a clear error if it doesn't exist."""
    if not path.exists():
        pytest.fail(f"Guide file not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_headings(text: str, level: int = 2) -> List[str]:
    """Extract markdown headings of a given level (default ##)."""
    pattern = rf"^{'#' * level}\s+(.+)$"
    return re.findall(pattern, text, re.MULTILINE)


def extract_scenario_numbers(text: str) -> List[int]:
    """Extract scenario numbers from headings like '### Scenario 1:' or '### 시나리오 1:'."""
    # Match both EN and KO scenario heading patterns
    matches = re.findall(
        r"^###\s+(?:Scenario|시나리오)\s+(\d+)", text, re.MULTILINE
    )
    return [int(m) for m in matches]


def extract_agent_references(text: str) -> List[str]:
    """Extract @agent-name references from guide text."""
    # Match @dx-xxx-yyy pattern (agent names)
    return re.findall(r"@(dx-[\w-]+)", text)


def extract_skill_references(text: str) -> List[str]:
    """Extract /skill-name references from guide text.

    Skills are invoked with a leading slash: `/dx-build-python-app`.
    We require the slash to distinguish skill invocations from project names
    (dx-compiler), agent names (dx-app-builder), and prose mentions.
    """
    # Match /dx-xxx-yyy — requires leading slash to be a skill reference
    matches = re.findall(r"(?:^|[\s`|])/+(dx-[\w-]+)", text, re.MULTILINE)
    # Exclude project/module names and known non-skill patterns
    exclusions = {
        "dx-all-suite", "dx-compiler", "dx-runtime", "dx-app", "dx-stream",
        "dx-m1", "dx-m1a", "dx-rt", "dx-com", "dx-agentic-dev",
    }
    return [m for m in matches if m not in exclusions]


def list_md_files(directory: Path) -> List[Path]:
    """List all .md files in a directory (non-recursive)."""
    if not directory.exists():
        return []
    return sorted(directory.glob("*.md"))


def agent_names_from_dir(directory: Path) -> List[str]:
    """Get agent names from .md filenames in an agents directory."""
    return [p.stem for p in list_md_files(directory)]


# ---------------------------------------------------------------------------
# Instruction file EN/KO pairs (CLAUDE.md, AGENTS.md, copilot-instructions.md)
# ---------------------------------------------------------------------------

@dataclass
class InstructionPair:
    """An EN/KO instruction file pair."""
    project: str
    en_path: Path
    ko_path: Path
    label: str  # human-readable label


INSTRUCTION_PAIRS: List[InstructionPair] = []

for _proj, _root in [
    ("suite", SUITE_ROOT),
    ("compiler", COMPILER_ROOT),
    ("runtime", RUNTIME_ROOT),
    ("app", APP_ROOT),
    ("stream", STREAM_ROOT),
]:
    INSTRUCTION_PAIRS.extend([
        InstructionPair(
            project=_proj,
            en_path=_root / "CLAUDE.md",
            ko_path=_root / "CLAUDE-KO.md",
            label=f"{_proj}/CLAUDE",
        ),
        InstructionPair(
            project=_proj,
            en_path=_root / "AGENTS.md",
            ko_path=_root / "AGENTS-KO.md",
            label=f"{_proj}/AGENTS",
        ),
        InstructionPair(
            project=_proj,
            en_path=_root / ".github" / "copilot-instructions.md",
            ko_path=_root / ".github" / "copilot-instructions-KO.md",
            label=f"{_proj}/copilot",
        ),
    ])


@pytest.fixture(params=INSTRUCTION_PAIRS, ids=[p.label for p in INSTRUCTION_PAIRS])
def instruction_pair(request) -> InstructionPair:
    """Parametrized fixture yielding each EN/KO instruction file pair."""
    return request.param


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def extract_headings_at_level(text: str, level: int) -> List[str]:
    """Extract markdown headings at a specific level."""
    pattern = rf"^{'#' * level}(?!#)\s+(.+)$"
    return re.findall(pattern, text, re.MULTILINE)


def extract_code_blocks(text: str) -> List[str]:
    """Extract fenced code blocks from markdown."""
    return re.findall(r"^```[\s\S]*?^```", text, re.MULTILINE)


def extract_tables(text: str) -> int:
    """Count markdown tables (lines starting with |)."""
    table_lines = [l for l in text.splitlines() if l.strip().startswith("|")]
    # A table needs at least 2 rows (header + separator)
    return len(table_lines)


def skill_names_from_dir(directory: Path) -> List[str]:
    """Get skill names from .md filenames in a .deepx/skills directory,
    or from subdirectory names in a .opencode/skills directory."""
    if not directory.exists():
        return []
    # .deepx/skills/ uses flat .md files: dx-validate.md → "dx-validate"
    md_names = [p.stem for p in list_md_files(directory)]
    # .opencode/skills/ uses subdirectories with SKILL.md: dx-validate-all/SKILL.md → "dx-validate-all"
    subdir_names = [
        p.name for p in sorted(directory.iterdir())
        if p.is_dir() and (p / "SKILL.md").exists()
    ]
    return sorted(set(md_names + subdir_names))
