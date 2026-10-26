# SPDX-License-Identifier: Apache-2.0
"""Inventory counts belong to the sub-project that owns them.

2026-09-04: model_registry.json held 353 models while the KB said 347 (EN), 349
(KO) and the suite template said 133 models / 15 AI tasks. The fix then was a
guard that forced every number in every KB to equal the live registry.

2026-10-16: that guard turned out to measure quantities the KB never meant.
`model_count` is `len(model_registry.json)` = 498 raw rows, while the KB
deliberately counts published variants (497 — rows can share a `.dxnn`, one is an
alias). Its per-task grouping uses the registry's `add_model_task` labels, which
are still the pre-Model-Zoo-2.5.0 names (23 of them), while the KB's table counts
the example directories under the current taxonomy (28). The KB was right and the
guard was stale, so enforcing equality produced false failures and pressure to
write wrong numbers.

The rule now: the suite and dx-runtime state NO sub-project counts at all — they
point at the file that owns each number (see the `inventory-counts` fragment).
A sub-project may state its own counts; it sits next to the file that defines
them and owns that call, so this level does not police it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from .conftest import APP_ROOT, SUITE_ROOT, iter_markdown_files

# A line carrying this marker is exempt from both count scans below — e.g. a doc
# that legitimately cites a different project's count (dx_stream's own model
# total) next to a number that happens to collide with the dx_app total pattern.
IGNORE_MARK = "<!-- kb-counts: ignore -->"

# EN: "353 models", "353 compiled `.dxnn` models"; KO: "353개 모델", "353개의 컴파일된 `.dxnn` 모델"
# Negative lookbehind excludes "~350" (approximate), "3.5" (decimal/version), and a
# number glued to a preceding letter — e.g. "YOLO26 models" (a model-name token, not
# a total) or "640x640 model" (an image resolution) must NOT be treated as a claim
# about the KB's total model count.
# Digits are capped at 4 (\d{2,4}) — headroom past 999 models without also
# swallowing unrelated 5+ digit numbers (line numbers, byte sizes, etc.) that
# might otherwise sit next to the word "model(s)".
# re.IGNORECASE so a heading like "## 353 Supported Models" is also caught.
MODEL_RE = re.compile(
    r"(?<![~\d.A-Za-z])(\d{2,4})\s+(?:compiled\s+)?(?:supported\s+)?(?:`\.dxnn`\s+)?models?\b"
    r"|(?<![~\d.A-Za-z])(\d{2,4})개(?:의)?\s*(?:컴파일된\s*)?(?:`\.dxnn`\s*)?모델",
    re.IGNORECASE,
)
# EN: "22 AI tasks", "22 Supported AI Tasks", "22 task dirs", "22 supported tasks",
# "AI task (22 categories)"; KO: "22개 AI 작업/태스크/task", "22개 지원 AI 작업".
# Same glued-number exclusion as MODEL_RE (defensive — no observed hit today, but
# guards against e.g. a future "GPT4 tasks" style token).
TASK_RE = re.compile(
    r"(?<![~\d.A-Za-z])(\d{1,2})\s+(?:supported\s+)?AI\s+tasks?\b"
    r"|(?<![~\d.A-Za-z])(\d{1,2})\s+task dirs\b"
    r"|(?<![~\d.A-Za-z])(\d{1,2})\s+supported tasks\b"
    r"|AI task\s*\(\s*(\d{1,2})\s+categories\)"
    r"|(?<![~\d.A-Za-z])(\d{1,2})개\s*(?:지원\s*)?AI\s*(?:작업|태스크|task)",
    re.IGNORECASE,
)
TOTAL_ROW_RE = re.compile(r"^\s*\|\s*\*\*Total\*\*\s*\|\s*\*\*(\d+)\*\*")
TASK_ROW_RE = re.compile(r"^\s*\|\s*([a-z0-9][a-z0-9_]+)\s*\|\s*(\d+)\s*\|")


def _scan_targets() -> list[Path]:
    files: list[Path] = []
    files += iter_markdown_files(APP_ROOT / ".deepx", "**/*.md")
    files += iter_markdown_files(APP_ROOT / ".deepx" / "templates", "**/*.tmpl")
    # Suite-level canonical source: dx-suite-builder.md, dx-agent-dev-overview.md,
    # etc. can also drift (they cite dx_app's totals directly).
    files += iter_markdown_files(SUITE_ROOT / ".deepx", "**/*.md")
    files += iter_markdown_files(SUITE_ROOT / ".deepx" / "templates", "**/*.tmpl")
    # YAML KB files can also carry stale counts in free-text descriptions.
    files += iter_markdown_files(APP_ROOT / ".deepx" / "knowledge", "**/*.yaml")
    for root in (APP_ROOT, SUITE_ROOT):
        for name in ("CLAUDE.md", "CLAUDE-KO.md", "AGENTS.md", "AGENTS-KO.md",
                     ".github/copilot-instructions.md", ".github/copilot-instructions-KO.md"):
            p = root / name
            if p.is_file():
                files.append(p)
    # Generated agent/rule copies also cite dx_app's totals directly and can drift
    # independently of the CLAUDE/AGENTS entry points scanned above.
    for root in (APP_ROOT, SUITE_ROOT):
        for sub in (".claude/agents", ".github/agents", ".opencode/agents", ".cursor/rules"):
            files += iter_markdown_files(root / sub, "*.md") + iter_markdown_files(root / sub, "*.mdc")
    return files


# Evaluated once at import time (mirrors DEEPX_MD_FILES in test_sdk_grounding.py) —
# the file set is fixed for the life of the test process, so there is no benefit
# to re-globbing on every _mismatches() call.
SCAN_TARGETS = _scan_targets()


# ── The suite must not carry another repo's counts at all ────────────────────
# A number borrowed from a sub-repo becomes a committed SNAPSHOT of whatever that
# repo happened to be at generation time. dx_app main has 353 models and dev has
# 498: no single committed number satisfies both, so the suite gate is red in one
# mode or the other forever. The suite therefore states no counts and points at
# the file that owns them.
STREAM_RE = re.compile(
    r"(?<![~\d.A-Za-z])(\d{1,3})\s+(?:GStreamer\s+)?elements\b"
    r"|(?<![~\d.A-Za-z])(\d{1,3})\s+pipeline categories\b"
    r"|(?<![~\d.A-Za-z])(\d{1,3})개\s*(?:GStreamer\s*)?(?:element|엘리먼트|요소)"
    r"|(?<![~\d.A-Za-z])(\d{1,3})개\s*파이프라인\s*(?:카테고리|분류)",
    re.IGNORECASE,
)
# py3.8: Path.is_relative_to is 3.9+, so compare prefixes as strings.
_OWNS_ITS_COUNTS = tuple(str(SUITE_ROOT / d) + "/" for d in ("dx-runtime/dx_app", "dx-runtime/dx_stream",
                                                            "dx-compiler", "dx-modelzoo"))
SUITE_SCAN = [f for f in SCAN_TARGETS if not str(f).startswith(_OWNS_ITS_COUNTS)]
# dx-runtime is an integration layer: it names its sub-projects but owns none of
# their numbers, so it is scanned exactly like the suite.
for _sub in ("", "dx-runtime"):
    _root = SUITE_ROOT / _sub if _sub else SUITE_ROOT
    SUITE_SCAN += iter_markdown_files(_root / ".deepx", "**/*.md")
    SUITE_SCAN += iter_markdown_files(_root / ".deepx" / "templates", "**/*.tmpl")
    for _name in ("CLAUDE.md", "CLAUDE-KO.md", "AGENTS.md", "AGENTS-KO.md",
                  ".github/copilot-instructions.md", ".github/copilot-instructions-KO.md"):
        _p = _root / _name
        if _p.is_file():
            SUITE_SCAN.append(_p)
SUITE_SCAN = sorted(set(SUITE_SCAN))
SUITE_TEMPLATES = sorted((SUITE_ROOT / ".deepx" / "templates").rglob("*.tmpl"))
REGISTRY_VARS = ("{{MODEL_COUNT}}", "{{TASK_COUNT}}", "{{TASK_LIST}}")


def test_suite_kb_does_not_state_sub_project_counts():
    bad: list[str] = []
    for f in SUITE_SCAN:
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if IGNORE_MARK in line:
                continue
            for regex in (MODEL_RE, TASK_RE, STREAM_RE):
                if regex.search(line):
                    s = line.strip()
                    bad.append(f"{f.relative_to(SUITE_ROOT)}:{i}: {s[:90]}")
                    break
    assert not bad, (
        "The suite KB must not state a sub-project's counts — point at the file that "
        "owns them instead (dx_app: config/model_registry.json + src/python_example/, "
        "dx_stream: model_list.json + gst-dxstream-plugin/src/):\n  " + "\n  ".join(bad))


def test_suite_templates_do_not_depend_on_dx_app_registry():
    bad = [f"{f.relative_to(SUITE_ROOT)}: {v}" for f in SUITE_TEMPLATES
           for v in REGISTRY_VARS if v in f.read_text(encoding="utf-8")]
    assert not bad, (
        "Suite templates must render without dx_app's registry (otherwise the suite "
        "cannot be generated unless the submodule is initialised, and its output is a "
        "snapshot of whichever dx_app branch was checked out):\n  " + "\n  ".join(bad))
