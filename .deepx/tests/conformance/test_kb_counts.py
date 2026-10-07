# SPDX-License-Identifier: Apache-2.0
"""KB model/task counts must equal the live registry.

2026-09-04 audit: model_registry.json held 353 models while the KB said 347 (EN),
349 (KO) and the suite template still said 133 models / 15 AI tasks. Nothing
guarded these numbers. This test scans every place the numbers are written and
fails with file:line so the fix is mechanical.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from dx_agent_dev_gen.counts import model_count, task_model_counts, task_names

from .conftest import APP_ROOT, SUITE_ROOT, iter_markdown_files, read_markdown

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


@pytest.fixture(scope="module")
def live_counts() -> tuple[int, int]:
    # Skips (not fails) when the submodule is absent — CI must init submodules or
    # this guard is vacuous.
    models = model_count(APP_ROOT)
    names = task_names(APP_ROOT)
    if models is None or names is None:
        pytest.skip("dx_app model_registry.json / src/python_example not found (submodule not initialized)")
    return models, len(names)


def _mismatches(regex: re.Pattern, expected: int) -> list[str]:
    out: list[str] = []
    for f in SCAN_TARGETS:
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if IGNORE_MARK in line:
                continue
            for m in regex.finditer(line):
                n = int(m.group(m.lastindex))
                if n != expected:
                    s = line.strip()
                    s = s[:90] + "…" if len(s) > 90 else s
                    out.append(f"{f.relative_to(SUITE_ROOT)}:{i}: {n} (expected {expected}) — {s}")
    return out


def test_model_counts_match_registry(live_counts):
    models, _ = live_counts
    bad = _mismatches(MODEL_RE, models)
    assert not bad, f"Stale model counts (registry has {models}):\n  " + "\n  ".join(bad)


def test_task_counts_match_python_example_dirs(live_counts):
    _, tasks = live_counts
    bad = _mismatches(TASK_RE, tasks)
    assert not bad, f"Stale task counts (src/python_example has {tasks} task dirs):\n  " + "\n  ".join(bad)


def test_model_manager_total_row_matches_registry(live_counts):
    models, _ = live_counts
    f = APP_ROOT / ".deepx" / "agents" / "dx-model-manager.md"
    text = read_markdown(f)
    rows = [(i, int(m.group(1))) for i, l in enumerate(text.splitlines(), 1)
            if (m := TOTAL_ROW_RE.match(l))]
    assert rows, "dx-model-manager.md: '| **Total** | **N** |' row not found"
    bad = [f"line {i}: {n}" for i, n in rows if n != models]
    assert not bad, f"dx-model-manager.md Total row stale (registry {models}): {bad}"


CSV_TASK_HEADER_RE = re.compile(r"^\s*\|.*\bcsv_task\b.*\|\s*$")
# A genuine table header is immediately followed by a "|---|---|" separator row.
# Without this check, a data row that merely *mentions* csv_task — e.g. a schema
# field-reference row like "| `csv_task` | string | Yes | ... |" — is mistaken
# for a header, and every ordinary field name in the rows below it (postprocessor,
# input_width, ...) gets misread as a fabricated csv_task code.
CSV_TASK_SEP_RE = re.compile(r"^\s*\|[\s\-:|]+\|\s*$")


def _csv_task_column_values(text: str) -> list[tuple[int, str]]:
    """(line_no, code) for every code in the csv_task column of every markdown
    table whose header row mentions csv_task."""
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        if (CSV_TASK_HEADER_RE.match(lines[i]) and i + 1 < len(lines)
                and CSV_TASK_SEP_RE.match(lines[i + 1])):
            cols = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            col = next(j for j, c in enumerate(cols) if "csv_task" in c)
            i += 2  # skip separator row
            while i < len(lines) and lines[i].lstrip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if len(cells) > col:
                    for code in re.split(r"[,/]", cells[col]):
                        code = code.strip("` *")
                        if code and code != "csv_task":
                            out.append((i + 1, code))
                i += 1
        else:
            i += 1
    return out


def test_csv_task_codes_exist_in_registry(live_counts):
    registry = json.loads((APP_ROOT / "config" / "model_registry.json").read_text(encoding="utf-8"))
    valid = {m.get("csv_task") for m in registry if isinstance(m, dict)} - {None}
    bad = []
    for f in iter_markdown_files(APP_ROOT / ".deepx", "**/*.md"):
        for ln, code in _csv_task_column_values(f.read_text(encoding="utf-8")):
            if code not in valid:
                bad.append(f"{f.relative_to(SUITE_ROOT)}:{ln}: csv_task `{code}` not in registry")
    assert not bad, "Fabricated csv_task codes (valid: " + ", ".join(sorted(valid)) + "):\n  " + "\n  ".join(bad)


def test_model_manager_per_task_rows_match_registry(live_counts):
    want = task_model_counts(APP_ROOT)
    assert want is not None
    text = read_markdown(APP_ROOT / ".deepx" / "agents" / "dx-model-manager.md")
    got = {m[1]: int(m[2]) for line in text.splitlines()
           if (m := TASK_ROW_RE.match(line)) and m[1] in want}
    assert got == dict(want), (
        "dx-model-manager.md per-task rows drift (task, n): "
        f"{sorted(set(want.items()) ^ set(got.items()))}")
