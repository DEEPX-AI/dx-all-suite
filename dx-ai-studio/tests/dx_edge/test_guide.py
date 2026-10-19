"""DX Cloud AWS Console guide — content files and page wiring.

Static contracts (source files only, no browser): the six content files share one structure, every screenshot they
reference ships with the package, and the page loads its own script and stylesheet the way index.html does.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "dx_edge"
GUIDE = APP / "static/guide"
LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")
# A real tag such as <b>, <img src=…> or </p>. Placeholders like <stack-name> or <model-name> are not tags.
TAG = re.compile(r"</?[A-Za-z][A-Za-z0-9]*(\s[^>]*)?/?>")


def _load(lang: str) -> dict:
    return json.loads((GUIDE / f"content.{lang}.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def content() -> dict:
    return {lang: _load(lang) for lang in LANGS}


def _skeleton(doc: dict) -> list:
    """Everything that must not differ between languages."""
    return [
        (g["id"], [(s["id"], [(st["id"], st.get("path"), (st.get("image") or {}).get("src"),
                              (st.get("image") or {}).get("width"), (st.get("image") or {}).get("height"),
                              st.get("commands"), len(st["items"]), "note" in st)
                             for st in s["steps"]])
                   for s in g["sections"]])
        for g in doc["guides"]
    ]


def _steps(doc: dict):
    for g in doc["guides"]:
        for s in g["sections"]:
            for st in s["steps"]:
                yield g, st


def _texts(doc: dict):
    yield from doc["ui"].values()
    for g in doc["guides"]:
        yield g["name"]
        yield g["title"]
        yield g["intro"]
        for s in g["sections"]:
            yield s["title"]
    for _, st in _steps(doc):
        yield st["title"]
        yield from st["items"]
        if "note" in st:
            yield st["note"]
        if "image" in st:
            yield st["image"]["alt"]


def test_every_language_file_parses_and_names_its_language(content):
    for lang, doc in content.items():
        assert doc["lang"] == lang
        assert {g["id"] for g in doc["guides"]} == {"compiler", "greengrass"}


def test_structure_is_identical_across_languages(content):
    en = _skeleton(content["en"])
    for lang in LANGS[1:]:
        assert _skeleton(content[lang]) == en, lang
        assert set(content[lang]["ui"]) == set(content["en"]["ui"]), lang


def test_every_referenced_image_exists(content):
    srcs = {st["image"]["src"] for _, st in _steps(content["en"]) if "image" in st}
    assert srcs
    for src in srcs:
        assert (GUIDE / "img" / src).is_file(), src


def test_no_unreferenced_images_are_shipped(content):
    srcs = {st["image"]["src"] for _, st in _steps(content["en"]) if "image" in st}
    assert {p.name for p in (GUIDE / "img").glob("*.png")} == srcs


def test_step_ids_are_unique_and_deep_links_are_unique(content):
    doc = content["en"]
    anchors = []
    for g in doc["guides"]:
        ids = [st["id"] for s in g["sections"] for st in s["steps"]]
        assert len(ids) == len(set(ids)), g["id"]
        assert all(re.fullmatch(r"[a-z0-9-]+", i) for i in ids)
        anchors += [f"{g['id']}-{i}" for i in ids]
    assert len(anchors) == len(set(anchors))
    assert "compiler-cfn-3" in anchors


def test_text_has_no_raw_html(content):
    for lang, doc in content.items():
        for text in _texts(doc):
            assert not TAG.search(text), (lang, text)


def test_links_in_text_are_https_only(content):
    for lang, doc in content.items():
        for text in _texts(doc):
            for url in re.findall(r"\]\(([^)]*)\)", text):
                assert url.startswith("https://"), (lang, url)


def test_ui_strings_are_filled_in_every_language(content):
    for lang, doc in content.items():
        assert all(isinstance(v, str) and v.strip() for v in doc["ui"].values()), lang


def test_page_loads_its_assets_like_the_index_page():
    """Root-relative /static/… URLs, as in index.html: the launcher routes them to this module by Referer, so the
    page works under /cloud/ without naming the prefix."""
    html = (APP / "templates/guide.html").read_text(encoding="utf-8")
    assert re.search(r'<link rel="stylesheet" href="/static/css/guide\.css[^"]*">', html)
    assert re.search(r'<script src="/static/js/guide\.js[^"]*"></script>', html)
    assert "/cloud/" not in html
    for slot in ("{{DX_SHELL_RAIL}}", "{{DX_SHELL_HEADER}}", "/static/shared/i18n.js", "/static/shared/dx-theme.js",
                 "DXBrand.mount"):
        assert slot in html, slot
    # The back link is relative so it lands on the module root under any mount prefix.
    assert 'href="./"' in html


def test_renderer_never_injects_html():
    js = (APP / "static/js/guide.js").read_text(encoding="utf-8")
    assert "innerHTML" not in js and "insertAdjacentHTML" not in js and "outerHTML" not in js
    assert "DXI18n.onLangChange" in js
    assert "content.' + code + '.json" in js
