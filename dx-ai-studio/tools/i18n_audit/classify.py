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
    if en in {"Error", "Error:", "ERROR", "❌ Error", "❌ Error:", "Python", "CPU", "FPS", "ORT", "OBB", "PPU", "Pose", "Multi", "Hardware", "Zoom", "visible"}:
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
