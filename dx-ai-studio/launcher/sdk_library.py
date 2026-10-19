"""Keep the SDK Library list in step with the md files in dx-all-suite.

sdk-library-data.json is a hand-picked list (drawer, section, title). That structure stays; when serving it:

- md sizes come from disk (hand-written sizes go stale)
- a file appears only once per section
- a new md in a ``docs`` folder that already has registered docs joins that section on its own (title from the
  first ``#`` line). Agent instruction files (CLAUDE, AGENTS, copilot) are not docs.
- pymdownx snippets (``--8<-- "file"``) are expanded — some docs, like dx_app's change log, are just that one line.

Contract: tests/launcher/test_sdk_library_live.py
"""
from __future__ import annotations

import copy
import re
from pathlib import Path

_NOT_DOCS = re.compile(r"^(claude|agents|copilot[-_]instructions)([-_].*)?\.md$", re.I)
_SNIPPET = re.compile(r'^-{2}8<-{2}\s+["\']([^"\']+)["\']\s*$', re.M)


def _title(path: Path) -> str:
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.startswith("# "):
                return line[2:].strip()
    except OSError:
        pass
    return path.stem.replace("_", " ")


def _size(path: Path):
    try:
        return path.stat().st_size
    except OSError:
        return None


def augment(data: dict, suite_root) -> dict:
    suite_root = Path(suite_root)
    out = copy.deepcopy(data)
    registered = set()
    for drawer in out.get("drawers", []):
        for section in drawer.get("sections", []):
            seen, files = set(), []
            for f in section.get("files", []):
                p = f.get("path")
                if not p or p in seen:
                    continue
                seen.add(p)
                registered.add(p)
                if f.get("type") == "md" or str(p).endswith(".md"):
                    size = _size(suite_root / p)
                    if size is not None:
                        f["size"] = size
                files.append(f)
            section["files"] = files
    for drawer in out.get("drawers", []):
        for section in drawer.get("sections", []):
            dirs = sorted({str(Path(f["path"]).parent) for f in section["files"]
                           if str(f["path"]).endswith(".md") and "docs" in Path(f["path"]).parts})
            for d in dirs:
                folder = suite_root / d
                if not folder.is_dir():
                    continue
                for md in sorted(folder.glob("*.md")):
                    rel = f"{d}/{md.name}"
                    # A broken symlink is not a doc (dx_stream's docs/RELEASE_NOTES.md is a dangling link)
                    if rel in registered or _NOT_DOCS.match(md.name) or not md.is_file():
                        continue
                    registered.add(rel)
                    section["files"].append({"path": rel, "title": _title(md), "size": _size(md),
                                             "type": "md", "auto": True})
    return out


def allowed_paths(data: dict) -> set:
    return {f["path"] for d in data.get("drawers", []) for s in d.get("sections", [])
            for f in s.get("files", []) if f.get("path")}


def expand_snippets(text: str, doc_rel: str, suite_root, depth: int = 0) -> str:
    """``--8<-- "file"`` → that file. pymdownx looks snippets up from mkdocs' base_path; here it is the first match
    walking up from the doc's folder (never leaving the suite)."""
    suite_root = Path(suite_root).resolve()
    if depth > 4:
        return text

    def repl(m):
        name = m.group(1).strip()
        if name.startswith("/") or ".." in Path(name).parts:
            return m.group(0)
        d = (suite_root / doc_rel).parent
        while True:
            cand = (d / name).resolve()
            try:
                cand.relative_to(suite_root)
            except ValueError:
                break
            if cand.is_file():
                inner = cand.read_text(encoding="utf-8", errors="ignore")
                return expand_snippets(inner, str(cand.relative_to(suite_root)), suite_root, depth + 1)
            if d == suite_root or d == d.parent:
                break
            d = d.parent
        return m.group(0)

    return _SNIPPET.sub(repl, text)
