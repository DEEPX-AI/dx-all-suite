"""Every var(--x) must be defined somewhere.

An undefined custom property does not fail loudly: the whole declaration becomes invalid at
computed-value time and the property falls back to its inherited or initial value:

    border: 1px solid var(--bdr)   →  the border disappears entirely (initial: none)
    background: var(--bg2)         →  transparent
    color: var(--dim)              →  inherits the parent color

By eye this cannot be told apart from "a design with no border", so only a gate catches it —
typically names carried over with markup from another stylesheet.

var(--x, fallback) is not checked: the author already handles the name being absent.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP_PARTS = {".venv", "node_modules", "var", ".git", "dx-agent-dev"}
EXTS = (".css", ".js", ".html")

_DEFINE = re.compile(r"(--[A-Za-z0-9_-]+)\s*:")
_SET_PROP = re.compile(r"setProperty\(\s*['\"](--[A-Za-z0-9_-]+)")
# Only a closing paren right after the name — a comma means there is a fallback.
_USE = re.compile(r"var\(\s*(--[A-Za-z0-9_-]+)\s*\)")


def _files():
    for p in ROOT.rglob("*"):
        if p.is_file() and p.suffix in EXTS and not (SKIP_PARTS & set(p.parts)):
            yield p


def test_every_custom_property_reference_resolves():
    defined: set[str] = set()
    texts: list[tuple[Path, str]] = []
    for p in _files():
        t = p.read_text(encoding="utf-8", errors="ignore")
        texts.append((p, t))
        defined |= set(_DEFINE.findall(t))
        defined |= set(_SET_PROP.findall(t))

    missing: dict[str, list[str]] = {}
    for p, t in texts:
        for i, line in enumerate(t.splitlines(), 1):
            for name in _USE.findall(line):
                if name not in defined:
                    missing.setdefault(name, []).append(f"{p.relative_to(ROOT)}:{i}")

    assert not missing, (
        "정의 없는 커스텀 속성 참조 — 해당 선언이 통째로 무효가 된다 "
        "(테두리 사라짐 / 배경 투명 / 글자색 상속): "
        + "; ".join(f"{k} @ {v[0]} (x{len(v)})" for k, v in sorted(missing.items()))
    )
