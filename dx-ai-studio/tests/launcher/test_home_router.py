"""Static contracts for home-router: source only, so they run in the blocking gate.

Contracts such as "no fetch during parsing" and "a single entry point" need no browser and are cheap,
so every PR must be held to them. The contracts that need a browser are in test_home_router_browser.py.
"""
from __future__ import annotations

import re

from tests.launcher.home_router_support import HERO_CHIPS, ROUTER, source  # noqa: F401

# ── static contracts (always run) ───────────────────────────────


def test_router_exposes_one_pure_entry_point():
    src = source()
    assert "DXHomeRouter" in src, "the router must be reachable as window.DXHomeRouter"
    assert "function resolve" in src, "resolve(text, catalog, demos) is the entry point"


def test_router_does_not_fetch_while_parsing():
    """Parsing must cost nothing. Data is passed in, not fetched per keystroke."""
    src = source()
    body = src[src.index("function resolve") :]
    body = body[: body.index("\n  }")] if "\n  }" in body else body
    assert "fetch(" not in body, "resolve() must not reach the network"


def test_every_hero_chip_has_a_term_the_router_knows():
    """The chips are the router's published vocabulary.

    Checked against the term tables in the source so this holds with or without
    a JS engine on the host.
    """
    src = source()
    missing = []
    for chip in HERO_CHIPS:
        words = re.findall(r"[a-z0-9]+", chip.lower())
        if not any(f"'{w}'" in src or f'"{w}"' in src for w in words):
            missing.append(chip)
    assert not missing, f"hero chips the router has no term for: {missing}"


def test_router_knows_the_studio_vocabulary():
    src = source().lower()
    for term in ("detection", "pose", "segment", "compile", "face"):
        assert f"'{term}" in src or f'"{term}' in src, f"router has no term for {term!r}"


