from __future__ import annotations

import re

from .config import BRAND_TERMS, LANGUAGES
from .schema import AuditRecord, Finding


def _severity_for(record: AuditRecord) -> str:
    """High for launcher or critical UI roles; Medium for all other missing-language findings."""
    if record.module == "launcher" or record.text_role in {"button", "error", "aria-label", "placeholder"}:
        return "High"
    return "Medium"


def _is_brand_or_short(text: str) -> bool:
    t = (text or "").strip()
    if not t or t in BRAND_TERMS:
        return True
    if t.startswith("DX ") or t.startswith("DX-") or t.startswith("DXNN"):
        return True
    if len(t) <= 12 and (t.isupper() or " " not in t):
        return True
    return False


def _should_skip_stale_copy(record: AuditRecord, en: str) -> bool:
    """Skip universal tokens, paths, code ids, and all-locale-identical strings."""
    if _is_brand_or_short(en):
        return True
    if record.brand_terms and en in record.brand_terms:
        return True
    if en.startswith("/") or en.startswith("http"):
        return True
    if "{" in en and "}" in en:
        return True
    if re.match(r"^\d,\d,\d+,\d+$", en):
        return True
    if re.match(r"^[a-z_][a-z0-9_]*$", en):
        return True
    if re.match(r"^Demo \d", en):
        return True
    if re.match(r"^[\d.]+[GMTK]?B", en):
        return True
    if "jpeg" in en and "png" in en:
        return True
    if en.endswith("↗"):
        return True
    if en in {"Error", "Error:", "ERROR", "❌ Error", "❌ Error:", "Python", "CPU", "FPS", "ORT", "OBB", "PPU", "Pose", "Multi", "Hardware", "Zoom", "visible",
                # Spanish keeps "Firmware" as a loanword, like "Hardware" next to it. A
                # correct translation that equals the English must not count as a defect;
                # padding it out to dodge stale-copy only makes the label longer.
                "Firmware", "🔧 Firmware",
                # Same for "Throughput": Spanish 'Rendimiento' collides with Performance, so
                # the English term stays (like FPS). The bare word is already skipped by the
                # short-word rule above; only the label with a unit needs listing here.
                "Throughput (FPS)"}:
        return True
    vals = {(record.texts.get(lang) or "").strip() for lang in LANGUAGES if (record.texts.get(lang) or "").strip()}
    if len(vals) == 1:
        return True
    return False


def classify_stale_copy(records: list[AuditRecord]) -> list[Finding]:
    """Flag locales that copy English verbatim (likely untranslated placeholder)."""
    findings: list[Finding] = []
    for record in records:
        en = record.texts.get("en", "").strip()
        if not en or _should_skip_stale_copy(record, en):
            continue
        for lang in LANGUAGES:
            if lang == "en":
                continue
            loc = record.texts.get(lang, "").strip()
            if loc and loc == en:
                findings.append(Finding(
                    record_id=record.record_id,
                    issue_type="stale-copy",
                    severity="High" if lang == "es" else "Medium",
                    message=f"Locale '{lang}' copies English verbatim",
                    suggested_fix=f"Replace with natural {lang} copy.",
                    verification_method="static inventory",
                ))
    return findings


def classify_records(records: list[AuditRecord]) -> list[Finding]:
    findings: list[Finding] = []
    for record in records:
        missing = [lang for lang in LANGUAGES if not record.texts.get(lang, "").strip()]
        if missing:
            if record.brand_terms and record.texts.get("en", "") in record.brand_terms:
                continue
            findings.append(Finding(
                record_id=record.record_id,
                issue_type="missing-language",
                severity=_severity_for(record),
                message=f"Missing locale values: {', '.join(missing)}",
                suggested_fix="Add locale-specific copy or approve intentional fallback.",
                verification_method="static inventory",
            ))
    findings.extend(classify_stale_copy(records))
    return findings


# ── From here on: not whether a cell is filled, but **what** it is filled with ──────
#
# classify_records / classify_stale_copy catch only empty cells and copies of the
# English, so a clean audit can still ship awkward screens. The three checks below
# cover only what a machine can judge reliably; grammar and tone are left to native
# speakers, since guessing at them would give false confidence.

# Scripts where one character carries a word. Skipped in the length check: Chinese and
# Japanese are normally **shorter** than English, so the same ratio means nothing.
_CJK_LANGS = ("zh-CN", "zh-TW", "ja")

# A translation longer than this multiple of the English risks overflowing the UI. 2.2
# was picked from measured copy: Spanish runs 20-30% longer than English as a rule, and
# anything past 2.2x was usually an explanation sitting in a button or label.
_LENGTH_RATIO = 2.2
_LENGTH_MIN_DELTA = 14   # ratios of short strings jump easily, so require an absolute increase too

_PLACEHOLDER_RE = re.compile(r"\{[^}]*\}|%[sd]|\$\{[^}]*\}")


def _skip_for_drift(text: str) -> bool:
    """Words the terminology-drift check skips.

    `_is_brand_or_short` does not fit here: it skips everything of 12 characters or less
    without spaces, which would drop **single-word terms** like 'Dashboard' or
    'Settings' — exactly the words most likely to drift between screens. That rule is
    right for stale-copy and wrong here.

    Only brands and very short abbreviations are skipped.
    """
    t = (text or "").strip()
    if not t or t in BRAND_TERMS:
        return True
    if t.startswith("DX ") or t.startswith("DX-") or t.startswith("DXNN"):
        return True
    # Short abbreviations such as 'ID', 'OK', 'FPS' legitimately vary with context.
    if len(t) <= 3 or (t.isupper() and len(t) <= 6):
        return True
    return False


def classify_terminology_drift(records: list[AuditRecord]) -> list[Finding]:
    """Report English text that is translated differently on different screens.

    If Dashboard is 仪表板 on one screen and 仪表盘 on another, both are correct but the
    product looks careless. This is a **consistency** check, not a grammar one, so a
    machine can do it reliably.

    Short words and brand names are skipped: an abbreviation like 'ID' may be
    translated differently depending on context.
    """
    by_en: dict[str, dict[str, set[str]]] = {}
    sources: dict[str, dict[str, set[str]]] = {}
    for record in records:
        en = (record.texts.get("en") or "").strip()
        if not en or _skip_for_drift(en):
            continue
        for lang in LANGUAGES:
            if lang == "en":
                continue
            value = (record.texts.get(lang) or "").strip()
            if not value:
                continue
            by_en.setdefault(en, {}).setdefault(lang, set()).add(value)
            sources.setdefault(en, {}).setdefault(lang, set()).add(record.source_file)

    findings: list[Finding] = []
    for en in sorted(by_en):
        for lang in sorted(by_en[en]):
            variants = sorted(by_en[en][lang])
            if len(variants) < 2:
                continue
            where = sorted(sources[en][lang])[:3]
            findings.append(Finding(
                record_id=f"terminology::{lang}::{en}",
                issue_type="terminology-drift",
                severity="Medium",
                message=(f"'{en}' is translated {len(variants)} ways in '{lang}': "
                         + " / ".join(variants)),
                suggested_fix=f"Pick one {lang} term and use it everywhere ({', '.join(where)}).",
                verification_method="static inventory",
            ))
    return findings


_ERROR_KEY_RE = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)+")


def classify_length_overflow(records: list[AuditRecord]) -> list[Finding]:
    """Report translations so much longer than the English that they may overflow the UI.

    The zoom audit checks layout but not **translation length**. A label more than twice
    as long wraps or gets clipped, and a widened column can push a whole table over.
    """
    findings: list[Finding] = []
    for record in records:
        en = (record.texts.get("en") or "").strip()
        if len(en) < 6 or _ERROR_KEY_RE.fullmatch(en):
            continue                     # an error key ('graph_live_busy') is no copy to compare a message with
        for lang in LANGUAGES:
            if lang == "en" or lang in _CJK_LANGS:
                continue
            value = (record.texts.get(lang) or "").strip()
            if not value:
                continue
            if len(value) > len(en) * _LENGTH_RATIO and len(value) - len(en) > _LENGTH_MIN_DELTA:
                findings.append(Finding(
                    record_id=f"length::{lang}::{record.record_id}",
                    issue_type="length-overflow",
                    severity="Low",
                    message=(f"'{lang}' copy is {len(value)} chars for {len(en)} in English "
                             f"({len(value) / len(en):.1f}x): {value[:60]}"),
                    suggested_fix="Shorten the copy or confirm the control can grow.",
                    verification_method="static inventory",
                ))
    return findings


def classify_placeholder_mismatch(records: list[AuditRecord]) -> list[Finding]:
    """Report translations that drop or rename a placeholder such as {n}.

    A dropped placeholder loses the value (the user sees 'Found  models'); a renamed one
    breaks formatting. Holding the count at zero keeps new translations from slipping
    one in silently.
    """
    findings: list[Finding] = []
    for record in records:
        en = record.texts.get("en") or ""
        expected = sorted(_PLACEHOLDER_RE.findall(en))
        if not expected:
            continue
        for lang in LANGUAGES:
            if lang == "en":
                continue
            value = record.texts.get(lang) or ""
            if not value:
                continue
            actual = sorted(_PLACEHOLDER_RE.findall(value))
            if actual != expected:
                findings.append(Finding(
                    record_id=f"placeholder::{lang}::{record.record_id}",
                    issue_type="placeholder-mismatch",
                    severity="High",
                    message=(f"'{lang}' placeholders {actual} do not match English {expected} "
                             f"in {record.source_file}"),
                    suggested_fix="Keep every placeholder from the English string.",
                    verification_method="static inventory",
                ))
    return findings
