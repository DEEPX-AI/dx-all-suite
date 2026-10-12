"""What the launcher tutorial points at must actually be created somewhere.

A step whose target does not exist (for example a removed `.status-dots` strip) makes the engine poll for about
two seconds before falling back to a floating tooltip; to the user, pressing Next appears to skip that step.

Checking CSS is not enough: a style rule can outlive its markup, so "mentioned somewhere" would still pass. The
contract requires a place that **creates** the element — markup or JS.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TUTORIAL = ROOT / "launcher" / "static" / "tutorial.js"

# Elements the engine injects itself (tutorial cards, preview mock-ups) are not in the markup.
ENGINE_OWNED = ("dxt-",)

# Places that can create elements: the launcher's markup and scripts, and the shared widgets.
# CSS is left out on purpose: styles do not create elements.
# tutorial.js itself must be excluded: a step naming its own target is not evidence that the target
# exists, and a contract that cites itself passes every mutation.
CREATORS = [
    ROOT / "launcher" / "static" / "index.html",
    *sorted(p for p in (ROOT / "launcher" / "static").glob("*.js") if p.name != "tutorial.js"),
    *sorted((ROOT / "shared" / "static").glob("*.js")),
    *sorted((ROOT / "shared" / "chat" / "static").glob("*.js")),
]


def _targets() -> list[str]:
    return re.findall(r"target:\s*'([^']+)'", TUTORIAL.read_text(encoding="utf-8"))


def _tokens(selector: str) -> list[str]:
    """Extract just the id/class names to look up from a selector."""
    return re.findall(r"[#.]([A-Za-z0-9_-]+)", selector)


def test_every_launcher_tutorial_target_is_created_somewhere():
    haystack = "\n".join(
        p.read_text(encoding="utf-8") for p in CREATORS if p.is_file()
    )
    # tutorial.js itself is excluded. A step mentioning its own target is not evidence.
    orphans = []
    for selector in _targets():
        names = [n for n in _tokens(selector) if not n.startswith(ENGINE_OWNED)]
        if not names:
            continue
        if not any(n in haystack for n in names):
            orphans.append(selector)
    assert not orphans, (
        "튜토리얼이 만들어지지 않는 것을 가리킨다 — 스텝이 아무것도 비추지 못하고, "
        f"사용자에게는 건너뛴 것처럼 보인다: {orphans}"
    )
