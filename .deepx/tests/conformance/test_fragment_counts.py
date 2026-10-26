# SPDX-License-Identifier: Apache-2.0
"""Fragment inventory counts written in docs must match the fragments directory.

2026-09-04: README/authoring-guide sat at "16 EN + 16 KO / 32 files" while the
directory held 18+18, then 19+19. Nothing guarded the number; this does.
"""
from __future__ import annotations

import re

import pytest

from .conftest import SUITE_ROOT

FRAG = SUITE_ROOT / ".deepx" / "templates" / "fragments"
DOCS = [
    SUITE_ROOT / ".deepx" / "README.md",
    SUITE_ROOT / ".deepx" / "README-KO.md",
    SUITE_ROOT / ".deepx" / "docs" / "fragment-authoring-guide.md",
    SUITE_ROOT / ".deepx" / "docs" / "fragment-authoring-guide-KO.md",
]
COUNT_RE = re.compile(r"(\d+)\s*(?:EN\b|개의 공유 fragment|shared fragments|files total|개 fragment 파일)|(?:EN|KO)\s*(\d+)개")


def test_en_ko_fragment_dirs_have_same_stems():
    en = {p.stem for p in (FRAG / "en").glob("*.md")}
    ko = {p.stem for p in (FRAG / "ko").glob("*.md")}
    assert en == ko, f"EN-only: {sorted(en - ko)}; KO-only: {sorted(ko - en)}"


@pytest.mark.parametrize("doc", DOCS, ids=[d.name for d in DOCS])
def test_docs_state_live_fragment_count(doc):
    n = len(list((FRAG / "en").glob("*.md")))
    text = doc.read_text(encoding="utf-8")
    stated = {int(g) for m in COUNT_RE.finditer(text) for g in m.groups() if g}
    assert stated, f"{doc.relative_to(SUITE_ROOT)}: no fragment count matched — update COUNT_RE"
    stated -= {2 * n}  # "38 files total" is the EN+KO sum — allowed
    assert stated <= {n}, f"{doc.relative_to(SUITE_ROOT)}: states fragment counts {sorted(stated)}, directory has {n}"


SECTION_RE = re.compile(r"^## 8\..*?(?=^## 9\.|\Z)", re.M | re.S)


def test_readme_fragment_table_lists_every_fragment():
    n = {p.stem for p in (FRAG / "en").glob("*.md")}
    for readme in DOCS[:2]:
        text = readme.read_text(encoding="utf-8")
        section = SECTION_RE.search(text)
        assert section, f"{readme.name}: '## 8. ...' Shared Fragments section not found"
        listed = set(re.findall(r"^\|\s*`([a-z0-9-]+)`\s*\|", section.group(0), re.M))
        missing = n - listed
        stale = listed - n
        assert n == listed, f"{readme.name}: missing from table: {sorted(missing)}; stale in table: {sorted(stale)}"
