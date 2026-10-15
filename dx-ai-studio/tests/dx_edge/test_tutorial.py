"""Tutorial language and selector contracts for DX Cloud (dx_edge).

Follows the `tests/dx_monitor/test_tutorial.py` pattern. Static contract tests: they check
source text only, with no browser or JS runtime.
"""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_edge"
TEMPLATES = APP / "templates"
TUTORIAL = APP / "static" / "js" / "tutorial.js"

# Injected by the shell/toolbar or rendered by edge.js at runtime.
RUNTIME_TOKENS = {"#dxToolbar", ".btn-danger"}
# Optional: the compile log panel may or may not exist; _pick() falls back past it.
OPTIONAL_PREFIXES = ('[id^="edgeLog"]',)

EXPECTED_SECTION_IDS = ["overview", "marketplace", "connection", "solutions", "stacks", "compile", "devices"]
LANGS = ("ko", "en", "ja", "zh-CN", "zh-TW", "es")


def rendered_index() -> str:
    from dx_edge.server import DX_EDGE_SHELL
    from shared.shell import apply as apply_shell

    return apply_shell((TEMPLATES / "index.html").read_text(encoding="utf-8"), DX_EDGE_SHELL)


def _selectors(source: str) -> set:
    found = set(re.findall(r"target:\s*'([^']+)'", source))
    for group in re.findall(r"_pick\(this,\s*\[(.*?)\]\)", source):
        found.update(re.findall(r"'([^']+)'", group))
    return found


def _missing(selector: str, html: str, tokens: set) -> list:
    missing = []
    for attr, value in re.findall(r'\[([a-z-]+)="([^"]+)"\]', selector):
        if f'{attr}="{value}"' not in html:
            missing.append(f"[{attr}={value}]")
    bare = re.sub(r"\[[^\]]*\]", "", selector)
    for tok in re.findall(r"[#.][A-Za-z][A-Za-z0-9_-]*", bare):
        if tok not in tokens:
            missing.append(tok)
    return missing


def test_targets_exist_in_rendered_page():
    html = rendered_index()
    ids = {f"#{i}" for i in re.findall(r'id="([^"]+)"', html)}
    classes = {f".{c}" for m in re.findall(r'class="([^"]+)"', html) for c in m.split()}
    tokens = ids | classes | RUNTIME_TOKENS
    source = TUTORIAL.read_text(encoding="utf-8")
    selectors = _selectors(source)
    assert len(selectors) >= 20
    unresolved = {
        s: m for s in sorted(selectors)
        if not any(p in s for p in OPTIONAL_PREFIXES) and (m := _missing(s, html, tokens))
    }
    assert not unresolved, f"tutorial targets missing from the page: {unresolved}"


def test_sections_and_languages():
    source = TUTORIAL.read_text(encoding="utf-8")
    for sid in EXPECTED_SECTION_IDS:
        assert re.search(rf"id:\s*'{sid}'", source), sid
    ko = len(re.findall(r"\{ ko:", source))
    for lang in LANGS:
        key = f"'{lang}':" if "-" in lang else f" {lang}:"
        assert source.count(key) >= ko, f"{lang} missing in some i18n objects"


def test_tour_never_clicks_aws_write_buttons():
    source = TUTORIAL.read_text(encoding="utf-8")
    # Only tab buttons may be clicked from the tour.
    assert re.findall(r"\.click\(\)", source) == [".click()"]
    assert "tab.click()" in source
    for write_id in ("edgeDeploy-", "edgeStart-", "edgeDeleteOk", "edgeRegGen", "edgeCheck'"):
        assert f"getElementById('{write_id}" not in source


def test_index_loads_tutorial_assets_in_order():
    html = (TEMPLATES / "index.html").read_text(encoding="utf-8")
    assert "/static/shared/tutorial.css" in html
    e = html.find("/static/shared/tutorial-engine.js")
    i = html.find("/static/shared/tutorial-init.js")
    t = html.find("/static/js/tutorial.js")
    assert -1 < html.find("/static/js/edge.js") < e < i < t
