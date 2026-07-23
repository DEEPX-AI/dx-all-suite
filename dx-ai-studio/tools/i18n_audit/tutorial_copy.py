"""Extract and classify tutorial copy quality from */static/js/tutorial.js files."""
from __future__ import annotations

import re
from pathlib import Path

from tools.i18n_audit.classify import classify_records, classify_stale_copy
from tools.i18n_audit.config import LANGUAGES
from tools.i18n_audit.schema import AuditRecord

ROOT = Path(__file__).resolve().parents[2]
LANG_KEYS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")
_LANG_BLOCK_RE = re.compile(
    r"\{\s*"
    r"(?:ko|en|ja|zh-CN|zh-TW|es)\s*:"
)
_LANG_PAIR_RE = re.compile(
    r"['\"]?(en|ja|ko|es|zh-CN|zh-TW)['\"]?\s*:\s*"
    r"(?:'(?P<value_s>(?:\\.|[^'\\])*)'|\"(?P<value_d>(?:\\.|[^\"\\])*)\")"
)
_HANGUL_RE = re.compile(r"[\uac00-\ud7a3]")
_CJK_RE = re.compile(r"[\u4e00-\u9fff]")
_HIRAGANA_KATAKANA_RE = re.compile(r"[\u3040-\u30ff]")
_FIELD_ANCHORS = ("title", "content", "description", "label", "desc", "prerequisiteMessage", "body")

# Product terms — identical across locales is OK (do-not-translate identifiers)
_DO_NOT_TRANSLATE = re.compile(
    r"\b(DX App|DX Stream|DX Compiler|DX Monitor|DX Sandbox|DX Model Zoo|"
    r"DX EdgeGuide|DX Benchmark|DX AI Studio|NPU|SDK|GStreamer|WebRTC|"
    r"GstShark|ONNX|Lab|Setup|Reference|Developer|Input Type|Image/Video|"
    r"Camera/RTSP|Actions|TOC|Help|Tutorial|WebRTC|CLI|FPS|RTSP)\b",
    re.I,
)
_KO_TONE_RE = re.compile(r"(합니다|합니다\.|해요|해요\.|입니다|입니다\.|세요|음$|다\.)")
_JA_TONE_RE = re.compile(r"(です|ます|ください|する|した|あります|ません)")
_ES_TU_RE = re.compile(r"\b(tú|tu)\b", re.I)


def _decode(raw: str) -> str:
    if not raw or "\\" not in raw:
        return raw
    if not re.search(r"\\[nrtu'\"\\]|\\u[0-9a-fA-F]{4}|\\x[0-9a-fA-F]{2}", raw):
        return raw
    try:
        return bytes(raw, "utf-8").decode("unicode_escape")
    except UnicodeDecodeError:
        return raw


def _extract_lang_maps(source: str) -> list[tuple[str, dict[str, str]]]:
    records: list[tuple[str, dict[str, str]]] = []
    for anchor in _FIELD_ANCHORS:
        for match in re.finditer(rf"{anchor}\s*:\s*\{{", source):
            start = match.end() - 1
            depth = 0
            end = start
            for i in range(start, len(source)):
                if source[i] == "{":
                    depth += 1
                elif source[i] == "}":
                    depth -= 1
                    if depth == 0:
                        end = i + 1
                        break
            block = source[start:end]
            texts: dict[str, str] = {}
            for lm in _LANG_PAIR_RE.finditer(block):
                val = lm.group("value_s") or lm.group("value_d") or ""
                texts[lm.group(1)] = _decode(val)
            if len(texts) >= 2:
                records.append((anchor, texts))
    return records


def extract_tutorial_records(root: Path | None = None) -> list[AuditRecord]:
    base = root or ROOT
    paths = sorted(base.glob("**/static/js/tutorial.js"))
    launcher_path = base / "launcher" / "static" / "tutorial.js"
    if launcher_path.exists() and launcher_path not in paths:
        paths.append(launcher_path)
    out: list[AuditRecord] = []
    for rel in paths:
        if "node_modules" in rel.parts or "dx-agent-dev" in rel.parts:
            continue
        rel_path = rel.relative_to(base)
        module = rel_path.parts[0]
        source = rel.read_text(encoding="utf-8")
        for field, texts in _extract_lang_maps(source):
            out.append(
                AuditRecord(
                    module=module,
                    surface="tutorial",
                    route_or_state=field,
                    source_file=str(rel_path),
                    selector_or_key=field,
                    text_role=field,
                    texts=texts,
                )
            )
    return out


def _is_brand_or_short_label(text: str) -> bool:
    plain = re.sub(r"<[^>]+>", "", text).strip()
    if len(plain) <= 28:
        return True
    stripped = _DO_NOT_TRANSLATE.sub("", plain).strip()
    if not stripped or len(stripped) <= 8:
        return True
    return False


def classify_locale_mismatch(records: list[AuditRecord]) -> list[str]:
    """Flag long descriptive fields that were not translated."""
    issues: list[str] = []
    long_roles = {"content", "body", "desc", "description", "prerequisiteMessage"}
    for record in records:
        if record.text_role not in long_roles:
            continue
        en = (record.texts.get("en") or "").strip()
        if not en or _is_brand_or_short_label(en):
            continue
        plain_en = re.sub(r"<[^>]+>", "", en).strip()
        if len(plain_en) < 36:
            continue
        for lang in ("ko", "ja", "zh-CN", "zh-TW", "es"):
            text = (record.texts.get(lang) or "").strip()
            if not text or text == en:
                issues.append(
                    f"{record.source_file} [{record.text_role}] {lang} untranslated (identical to en, len={len(plain_en)})"
                )
                continue
            plain = re.sub(r"<[^>]+>", "", text).strip()
            if lang == "ko" and not _HANGUL_RE.search(plain):
                issues.append(
                    f"{record.source_file} [{record.text_role}] ko missing Hangul in long string"
                )
            if lang == "ja" and not _CJK_RE.search(plain) and not _HIRAGANA_KATAKANA_RE.search(plain):
                issues.append(
                    f"{record.source_file} [{record.text_role}] ja missing Japanese script in long string"
                )
            if lang in ("zh-CN", "zh-TW") and not _CJK_RE.search(plain):
                issues.append(
                    f"{record.source_file} [{record.text_role}] {lang} missing CJK in long string"
                )
    return issues


def classify_tone_quality(records: list[AuditRecord]) -> list[str]:
    """Soft tone hints for report only — not a hard gate."""
    issues: list[str] = []
    long_roles = {"content", "body", "desc", "description", "prerequisiteMessage"}
    for record in records:
        if record.text_role not in long_roles:
            continue
        for lang, text in record.texts.items():
            if not text:
                continue
            plain = re.sub(r"<[^>]+>", "", text).strip()
            if len(plain) < 48 or _is_brand_or_short_label(text):
                continue
            rid = f"{record.source_file} [{record.text_role}] {lang}"
            if lang == "ko" and _HANGUL_RE.search(plain) and not _KO_TONE_RE.search(plain):
                issues.append(f"{rid}: ko may lack polite ending")
            elif lang == "ja" and (_CJK_RE.search(plain) or _HIRAGANA_KATAKANA_RE.search(plain)):
                if not _JA_TONE_RE.search(plain):
                    issues.append(f"{rid}: ja may lack です/ます register")
            elif lang == "es" and _ES_TU_RE.search(plain):
                issues.append(f"{rid}: es uses informal tú/tu")
    return issues


def audit_tutorial_copy(root: Path | None = None) -> tuple[list, list[str]]:
    records = extract_tutorial_records(root)
    findings = classify_records(records) + classify_stale_copy(records)
    extra = classify_locale_mismatch(records)
    tone_hints = classify_tone_quality(records)
    return findings, extra + [f"[tone-hint] {h}" for h in tone_hints]


def format_report(findings, extra: list[str]) -> str:
    lines = ["# Tutorial copy quality audit", ""]
    if not findings and not extra:
        lines.append("No issues found.")
        return "\n".join(lines)
    if findings:
        lines.append("## Static i18n findings")
        for f in findings[:200]:
            lines.append(f"- **{f.issue_type}** ({f.severity}) `{f.record_id}`: {f.message}")
        if len(findings) > 200:
            lines.append(f"- … and {len(findings) - 200} more")
    if extra:
        lines.append("")
        lines.append("## Locale mismatch heuristics")
        for item in extra[:100]:
            lines.append(f"- {item}")
    return "\n".join(lines)
