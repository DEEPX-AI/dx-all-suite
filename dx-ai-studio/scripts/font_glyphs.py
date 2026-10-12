"""Collect, per language, the CJK glyphs the studio draws on screen.

build_font_subsets.py and font_coverage_gate.py share these functions; if the builder and the
checker saw different glyphs, the gate would mean nothing.
"""
from __future__ import annotations

from pathlib import Path

from tools.i18n_audit.extractors import extract_inventory, iter_source_files

ROOT = Path(__file__).resolve().parents[1]
LANGS = ("ko", "ja", "zh-CN", "zh-TW")
# Only files that reach the screen; .py sources would add glyphs that are never rendered.
RENDERED_SUFFIXES = {".js", ".html", ".json"}


def is_hangul(cp: int) -> bool:
    return 0xAC00 <= cp <= 0xD7A3 or 0x1100 <= cp <= 0x11FF or 0x3130 <= cp <= 0x318F


def is_kana(cp: int) -> bool:
    return 0x3040 <= cp <= 0x30FF or 0x31F0 <= cp <= 0x31FF


def is_han(cp: int) -> bool:
    return 0x4E00 <= cp <= 0x9FFF or 0x3400 <= cp <= 0x4DBF or 0xF900 <= cp <= 0xFAFF


def is_cjk_punct(cp: int) -> bool:
    return 0x3000 <= cp <= 0x303F or 0xFF00 <= cp <= 0xFFEF


def is_cjk(cp: int) -> bool:
    return is_hangul(cp) or is_kana(cp) or is_han(cp) or is_cjk_punct(cp)


def dictionary_glyphs(root: Path = ROOT) -> dict[str, set[int]]:
    """CJK glyphs from the translation dictionaries, per language. The gate checks only these."""
    per: dict[str, set[int]] = {lang: set() for lang in LANGS}
    for rec in extract_inventory(root):
        for lang in LANGS:
            per[lang].update(cp for cp in map(ord, rec.texts.get(lang, "")) if is_cjk(cp))
    return per


def _is_rendered(path: Path, root: Path) -> bool:
    rel = "/" + path.relative_to(root).as_posix()
    return path.suffix in RENDERED_SUFFIXES and ("/static/" in rel or "/templates/" in rel)


def all_glyphs(root: Path = ROOT) -> dict[str, set[int]]:
    """Dictionary glyphs plus glyphs written directly outside the dictionaries. Subsets are built from this.

    Glyphs outside the dictionaries have no known language, so they are assigned by script: Hangul to
    ko, kana to ja, Han to all three Han-using languages, punctuation to all four. Glyphs whose language
    the dictionaries already establish are not reassigned: static files also contain the dictionary
    strings themselves, and reassigning them would leak zh dictionary Han into the ja font.
    """
    per = dictionary_glyphs(root)
    known = set().union(*per.values())
    for path in iter_source_files(root):
        if not _is_rendered(path, root):
            continue
        for cp in map(ord, path.read_text(encoding="utf-8", errors="replace")):
            if cp in known:
                continue
            if is_hangul(cp):
                per["ko"].add(cp)
            elif is_kana(cp):
                per["ja"].add(cp)
            elif is_han(cp):
                for lang in ("ja", "zh-CN", "zh-TW"):
                    per[lang].add(cp)
            elif is_cjk_punct(cp):
                for lang in LANGS:
                    per[lang].add(cp)
    return per
