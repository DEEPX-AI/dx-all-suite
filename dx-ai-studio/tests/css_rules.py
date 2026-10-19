"""CSS rule body extraction, shared by the contract tests.

One copy of the parser, so a change in how the shell writes selectors (e.g. grouped
selectors) is handled in one place instead of breaking several tests at once.
"""
from __future__ import annotations

import re

_COMMENT = re.compile(r"/\*.*?\*/", re.S)
# Selectors contain no < or ;. Excluding both keeps the text before a <style> in HTML from
# being swallowed as a selector (> is allowed: it is the child combinator). At-rule openers are skipped.
_RULE = re.compile(r"(?m)^[ \t]*([^{}@\n<;][^{}<;]*?)\{([^{}]*)\}")


def iter_rules(css: str):
    """Yield (selector list, body) pairs in document order."""
    for m in _RULE.finditer(_COMMENT.sub(" ", css)):
        yield [n.strip() for n in m.group(1).split(",")], m.group(2)


def css_rule(css: str, selector: str) -> str:
    """Body of the first rule for the selector.

    A grouped selector counts as a definition, because the shared layer binds two names
    to one rule (.dx-shell-header-right, .toolbar).
    """
    for names, body in iter_rules(css):
        if selector in names:
            return body
    raise AssertionError(f"selector {selector!r} not found in CSS")


def css_rule_last(css: str, selector: str) -> str:
    """Body of the last rule for the selector — use this to see later overriding definitions."""
    found = None
    for names, body in iter_rules(css):
        if selector in names:
            found = body
    if found is None:
        raise AssertionError(f"selector {selector!r} not found in CSS")
    return found


def defines(css: str, selector: str) -> bool:
    """Whether any rule defines the selector."""
    return any(selector in names for names, _ in iter_rules(css))
