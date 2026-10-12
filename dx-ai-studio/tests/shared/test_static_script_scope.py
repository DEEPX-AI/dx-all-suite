"""The scripts one page loads share a single global scope.

There is no bundler. A module page lists `<script src>` tags in order, and the top-level declarations of all those
files land in the same global lexical scope. So:

* If two files declare the same name with `const` / `let` / `class`, **the later file fails to parse entirely**
  (SyntaxError: has already been declared). The screen silently stays blank while every Python test passes; two
  files each declaring a shared constant can leave a whole screen unrendered.
* `function` / `var` may be redeclared, but **the later one silently wins**, so an earlier helper with the same
  name is dead code.

Neither shows up without a browser, and the default CI has no browser stage, so this reads the sources instead.

Top level is judged by indentation: every file in this codebase indents by 2 spaces, so a declaration at column 0
is top level.
"""
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

_SCRIPT_SRC = re.compile(r"""<script[^>]*\bsrc=["']([^"']+)["']""", re.I)
_TOP_LEVEL_DECL = re.compile(
    r"^(?:export\s+)?(?:async\s+)?(?P<kind>const|let|var|class|function)\s*\*?\s*"
    r"(?P<name>[A-Za-z_$][\w$]*)"
)
# Kinds whose redeclaration is a SyntaxError. var/function are allowed but silently overridden.
_FATAL_KINDS = {"const", "let", "class"}


def _documents():
    """(document path, [script files…]) in load order."""
    htmls = sorted(ROOT.glob("*/templates/index.html"))
    htmls += [p for p in [ROOT / "launcher" / "static" / "index.html"] if p.exists()]
    for html in htmls:
        module_dir = html.parent.parent if html.name == "index.html" and html.parent.name == "templates" else html.parent
        scripts = []
        for src in _SCRIPT_SRC.findall(html.read_text(encoding="utf-8")):
            path = _resolve(src, module_dir)
            if path is not None and path.exists():
                scripts.append(path)
        yield html, scripts


def _resolve(src: str, module_dir: Path) -> Path | None:
    path = src.split("?")[0]
    if path.startswith(("http://", "https://", "//")):
        return None
    if path.startswith("/static/shared/"):
        return ROOT / "shared" / "static" / path[len("/static/shared/"):]
    if path.startswith("/static/"):
        return module_dir / "static" / path[len("/static/"):]
    return None


def _top_level_declarations(path: Path):
    """{name: kind} for declarations starting at column 0 only."""
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = _TOP_LEVEL_DECL.match(line)
        if match:
            out.setdefault(match.group("name"), match.group("kind"))
    return out


def _collisions(scripts):
    owners = defaultdict(list)
    kinds = {}
    for path in scripts:
        for name, kind in _top_level_declarations(path).items():
            owners[name].append(path)
            kinds.setdefault(name, kind)
            if kind in _FATAL_KINDS:
                kinds[name] = kind
    return {n: (kinds[n], p) for n, p in owners.items() if len(p) > 1}


@pytest.mark.parametrize(
    "html,scripts", list(_documents()), ids=lambda v: v.parts[-3] if isinstance(v, Path) else ""
)
def test_no_fatal_redeclaration_across_scripts(html, scripts):
    """const/let/class collision: the later file fails to parse entirely."""
    fatal = {n: (k, p) for n, (k, p) in _collisions(scripts).items() if k in _FATAL_KINDS}
    assert not fatal, "\n".join(
        f"{html.relative_to(ROOT)}: `{k} {n}` 이(가) "
        + ", ".join(x.name for x in paths)
        + " 에 중복 선언됐다 — 나중 파일이 SyntaxError 로 통째로 죽는다"
        for n, (k, paths) in sorted(fatal.items())
    )


@pytest.mark.parametrize(
    "html,scripts", list(_documents()), ids=lambda v: v.parts[-3] if isinstance(v, Path) else ""
)
def test_no_silent_override_across_scripts(html, scripts):
    """function/var collision: it parses, but the later one silently wins."""
    silent = {n: (k, p) for n, (k, p) in _collisions(scripts).items() if k not in _FATAL_KINDS}
    assert not silent, "\n".join(
        f"{html.relative_to(ROOT)}: `{k} {n}` 이(가) "
        + ", ".join(x.name for x in paths)
        + " 에 중복 선언됐다 — 나중 파일 정의가 앞 파일 호출까지 덮는다"
        for n, (k, paths) in sorted(silent.items())
    )
