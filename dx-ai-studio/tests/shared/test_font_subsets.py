"""Font subset contract.

Guards two things: real weights (a single Inter Regular declared as 100–900 renders all bold Latin as Regular), and
per-language CJK faces (four CJK languages must not share one Simplified Chinese face with only 400 and 700).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
FONTS = ROOT / "shared" / "static" / "fonts"
SOURCES = json.loads((ROOT / "config" / "font_sources.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def glyphs():
    """(dictionary, full). Scanning 3,000+ dictionary entries takes seconds, so compute once."""
    from scripts.font_glyphs import all_glyphs, dictionary_glyphs

    return dictionary_glyphs(), all_glyphs()


def test_glyphs_split_by_script():
    from scripts.font_glyphs import is_hangul, is_kana, is_han, is_cjk_punct

    assert is_hangul(ord("한")) and not is_han(ord("한"))
    assert is_kana(ord("ア")) and is_kana(ord("あ"))
    assert is_han(ord("漢")) and not is_kana(ord("漢"))
    assert is_cjk_punct(ord("、")) and is_cjk_punct(ord("（"))


def test_dictionary_glyphs_are_per_language(glyphs):
    per = glyphs[0]
    assert set(per) == {"ko", "ja", "zh-CN", "zh-TW"}
    # Hangul goes only to ko, kana only to ja
    assert any(0xAC00 <= cp <= 0xD7A3 for cp in per["ko"])
    assert not any(0xAC00 <= cp <= 0xD7A3 for cp in per["zh-CN"])
    assert any(0x3040 <= cp <= 0x30FF for cp in per["ja"])
    # Traditional and Simplified use different characters; merging them would lose this difference
    assert per["zh-TW"] - per["zh-CN"]


def test_language_tagged_content_files_count_as_that_languages_dictionary(glyphs):
    """content.<lang>.json (DX Cloud console guide) is translated text for one language, like a dictionary."""
    from scripts.font_glyphs import is_cjk

    dic = glyphs[0]
    files = sorted((ROOT / "dx_edge" / "static" / "guide").glob("content.*.json"))
    assert files
    for path in files:
        lang = path.name.split(".")[1]
        if lang not in dic:
            continue
        used = {cp for cp in map(ord, path.read_text(encoding="utf-8")) if is_cjk(cp)}
        assert used <= dic[lang], f"{path.name}: {''.join(map(chr, sorted(used - dic[lang])))}"

def test_all_glyphs_is_a_superset_of_the_dictionaries(glyphs):
    dic, full = glyphs
    for lang in dic:
        assert dic[lang] <= full[lang], lang


def test_file_scan_only_distributes_characters_of_unknown_origin(glyphs):
    """Han characters from Chinese dictionary strings do not leak into the Japanese face via the file scan.

    Giving every Han character in static files to ja, zh-CN and zh-TW alike bloats the ja subset with characters
    that only the zh dictionaries use.
    """
    dic, full = glyphs
    known = set().union(*dic.values())
    zh_only = (dic["zh-CN"] | dic["zh-TW"]) - dic["ja"]
    assert zh_only, "fixture: zh 에만 있는 한자가 있어야 이 계약이 의미가 있다"
    assert not (full["ja"] & zh_only), "zh 사전에만 있는 한자가 ja subset 에 들어갔다"
    # Only characters missing from the dictionaries are split by script
    for lang in dic:
        assert full[lang] - dic[lang] <= (full[lang] - known)


def _axes(path):
    from fontTools.ttLib import TTFont

    font = TTFont(path)
    assert "fvar" in font, f"{path.name} 는 가변 글꼴이 아니다"
    return {a.axisTag: (a.minValue, a.maxValue) for a in font["fvar"].axes}


def test_inter_is_really_variable_with_optical_size():
    axes = _axes(FONTS / SOURCES["inter"]["output"])
    assert axes["wght"][0] <= 100 and axes["wght"][1] >= 900
    # Display shapes (large headings) come from the opsz axis
    assert axes["opsz"] == (14.0, 32.0)


@pytest.mark.parametrize("name", ["pretendard", "pretendard-jp", "noto-sans-sc", "noto-sans-tc"])
def test_each_cjk_subset_is_variable_across_400_to_700(name):
    lo, hi = _axes(FONTS / SOURCES[name]["output"])["wght"]
    assert lo <= 400 and hi >= 700


@pytest.mark.parametrize("name", list(SOURCES))
def test_every_font_ships_with_its_licence(name):
    text = (FONTS / SOURCES[name]["license_output"]).read_text(encoding="utf-8", errors="replace")
    assert "SIL Open Font License" in text


def test_launcher_copy_of_inter_is_the_same_file():
    name = SOURCES["inter"]["output"]
    assert (ROOT / "launcher" / "static" / "fonts" / name).read_bytes() == (FONTS / name).read_bytes()


def test_retired_font_files_are_gone():
    for old in ("inter-v20-latin-regular.woff2", "NotoSansCJK-subset-Regular.woff2",
                "NotoSansCJK-subset-Bold.woff2"):
        assert not (FONTS / old).exists(), old
    assert not (ROOT / "launcher" / "static" / "fonts" / "inter-v20-latin-regular.woff2").exists()


def test_subsetting_is_reproducible(tmp_path):
    """Same input, same bytes; otherwise every run of the script leaves a change in git.

    fontTools sets head.modified to the current time on save. It has one-second resolution, so build twice more
    than a second apart.
    """
    import time

    from scripts.build_font_subsets import _subset

    src = (FONTS / SOURCES["inter"]["output"]).read_bytes()
    a, b = tmp_path / "a.woff2", tmp_path / "b.woff2"
    _subset(src, [ord(c) for c in "DX-M1"], a)
    time.sleep(1.1)
    _subset(src, [ord(c) for c in "DX-M1"], b)
    assert a.read_bytes() == b.read_bytes()


def test_coverage_gate_passes_on_the_repo():
    from scripts.font_coverage_gate import missing_glyphs

    assert missing_glyphs() == {}


def test_coverage_chain_matches_the_css_fallback_order():
    """If the gate's chain differed from the CSS, it would check something other than what renders."""
    from scripts.font_coverage_gate import CHAIN

    lang_of = {fam: s["lang"] for fam, s in zip(
        ["DX CJK KR", "DX CJK JP", "DX CJK SC", "DX CJK TC"],
        [SOURCES["pretendard"], SOURCES["pretendard-jp"], SOURCES["noto-sans-sc"], SOURCES["noto-sans-tc"]])}
    tokens = (ROOT / "shared" / "static" / "dx-tokens.css").read_text(encoding="utf-8")
    for lang, chain in CHAIN.items():
        decl = re.search(r":root:lang\(" + re.escape(lang) + r"\)\{--font-cjk:([^}]+)\}", tokens).group(1)
        families = re.findall(r"'([^']+)'", decl)
        assert tuple(lang_of[f] for f in families) == chain, (lang, families)


def test_coverage_gate_reports_a_character_the_subset_lacks(monkeypatch):
    """The gate bites: a rare Han character not in the dictionaries must be reported."""
    from scripts import font_coverage_gate as gate

    real = gate.dictionary_glyphs

    def with_rare_char():
        per = real()
        per["zh-TW"].add(ord("齉"))  # U+9F49, not in any dictionary
        return per

    monkeypatch.setattr(gate, "dictionary_glyphs", with_rare_char)
    assert gate.missing_glyphs() == {"zh-TW": ["齉"]}


CSS = (ROOT / "shared" / "static" / "dx-fonts.css").read_text(encoding="utf-8")
TOKENS = (ROOT / "shared" / "static" / "dx-tokens.css").read_text(encoding="utf-8")
CJK_FAMILY = {"ko": "DX CJK KR", "ja": "DX CJK JP", "zh-CN": "DX CJK SC", "zh-TW": "DX CJK TC"}


def test_every_font_face_points_at_a_shipped_file():
    urls = re.findall(r"url\('/static/shared/fonts/([^']+)'\)", CSS)
    assert urls
    for name in urls:
        assert (FONTS / name).is_file(), name


def test_inter_face_declares_the_real_axes_it_ships():
    face = re.search(r"@font-face\{font-family:'Inter';[^}]*\}", CSS).group(0)
    assert SOURCES["inter"]["output"] in face
    assert "font-weight:100 900" in face


@pytest.mark.parametrize("lang,family", CJK_FAMILY.items())
def test_each_language_gets_its_own_cjk_face(lang, family):
    name = next(s["output"] for s in SOURCES.values() if s["lang"] == lang)
    face = re.search(r"@font-face\{font-family:'" + family + r"';[^}]*\}", CSS).group(0)
    assert name in face
    assert "unicode-range:" in face        # downloaded only when those characters appear
    assert "font-weight:100 900" in face or "font-weight:45 930" in face
    assert re.search(r":root:lang\(" + re.escape(lang) + r"\)\s*\{[^}]*--font-cjk:'" + family, TOKENS)


def test_font_token_puts_cjk_after_inter():
    font = re.search(r"--font:([^;]+);", TOKENS).group(1)
    assert font.strip().startswith("'Inter',var(--font-cjk)")


def test_mono_token_also_falls_back_to_the_language_cjk_face():
    """--mono needs the language CJK face too; without it, CJK text in code blocks falls back to the
    system font."""
    mono = re.search(r"--mono:([^;]+);", TOKENS).group(1)
    assert "var(--font-cjk)" in mono


def test_retired_cjk_family_is_not_referenced_anywhere():
    hits = []
    for path in ROOT.rglob("*"):
        rel = path.relative_to(ROOT).as_posix()
        if (not path.is_file() or path.suffix not in {".css", ".js", ".html"}
                or rel.startswith((".venv/", "var/", "node_modules/"))):
            continue
        if "'Noto Sans CJK'" in path.read_text(encoding="utf-8", errors="replace"):
            hits.append(rel)
    assert hits == []


def test_modules_carry_no_font_copies():
    """Every module page loads /static/shared/dx-fonts.css, which points at shared/static/fonts only, so per-module
    font copies are dead weight (megabytes that nothing requests)."""
    for module in ("dx_app", "dx_benchmark", "dx_compiler", "dx_monitor", "dx_planner", "dx_stream", "dx_modelzoo",
                   "dx_agent_dev"):
        assert not (ROOT / module / "static" / "fonts").exists(), module
