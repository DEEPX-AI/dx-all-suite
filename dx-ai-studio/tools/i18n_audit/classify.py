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
                # Firmware 는 스페인어에서도 그대로 쓰는 외래어다 — 바로 옆의 Hardware 와
                # 같은 경우다. 예전에는 'Firmware del dispositivo'(기기 펌웨어)로 늘려
                # 적어 stale-copy 를 피하고 있었지만, 영어에 없는 말을 덧붙인 것이라
                # 라벨이 2.6배 길어졌다(dashboard.js:563 의 메트릭 라벨). 올바른 번역이
                # 영어와 같아지는 경우를 결함으로 세면 안 된다.
                "Firmware", "🔧 Firmware",
                # Throughput 도 같다 — 스페인어 'Rendimiento' 는 Performance 와 겹쳐서
                # 영어 기술 용어를 그대로 쓴다(FPS 처럼). 'Throughput' 한 낱말은 위의
                # 짧은 낱말 규칙으로 이미 빠지고, 단위가 붙은 라벨만 여기서 뺀다.
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


# ── 여기서부터: 칸이 채워졌는지가 아니라 **무엇이 채워졌는지** 를 본다 ────────────
#
# classify_records / classify_stale_copy 는 빈 칸과 "영어 그대로" 만 잡는다. 그래서
# 감사가 0건이어도 사용자는 어색한 화면을 볼 수 있다. 아래 셋은 기계가 확실히
# 판정할 수 있는 것만 다룬다 — 문법이나 어투가 자연스러운지는 시도하지 않는다.
# 그것은 원어민의 몫이고, 흉내 내면 지금의 0건보다 나쁜 가짜 안전감이 된다.

# 한 글자가 한 낱말 몫을 하는 표기. 길이 비교에서 제외한다 — 중국어/일본어는
# 영어보다 **짧은** 것이 정상이라 같은 잣대를 대면 의미가 없다.
_CJK_LANGS = ("zh-CN", "zh-TW", "ja")

# 번역이 영어의 몇 배를 넘으면 UI 를 넘칠 위험으로 본다. 2.2 는 실측에서 고른 값:
# 스페인어가 영어보다 20~30% 긴 것은 정상이고, 2.2배를 넘는 것은 대개 풀어쓴
# 설명문이 버튼/라벨 자리에 들어간 경우였다.
_LENGTH_RATIO = 2.2
_LENGTH_MIN_DELTA = 14   # 짧은 문자열의 배수는 쉽게 튄다 — 절대 증가분도 본다

_PLACEHOLDER_RE = re.compile(r"\{[^}]*\}|%[sd]|\$\{[^}]*\}")


def _skip_for_drift(text: str) -> bool:
    """용어 불일치에서 건너뛸 말.

    `_is_brand_or_short` 를 그대로 쓸 수 없다. 그것은 "12자 이하이고 공백이 없는"
    것을 전부 건너뛰는데, 그러면 'Dashboard' 나 'Settings' 같은 **한 낱말 용어가
    통째로 빠진다** — 정작 화면마다 갈리기 쉬운 것이 그런 말이다. stale-copy 에는
    맞는 규칙이지만 여기서는 정반대다.

    여기서는 브랜드와 아주 짧은 약어만 뺀다.
    """
    t = (text or "").strip()
    if not t or t in BRAND_TERMS:
        return True
    if t.startswith("DX ") or t.startswith("DX-") or t.startswith("DXNN"):
        return True
    # 'ID', 'OK', 'FPS' 처럼 짧은 약어는 문맥마다 달리 옮기는 것이 정상이다.
    if len(t) <= 3 or (t.isupper() and len(t) <= 6):
        return True
    return False


def classify_terminology_drift(records: list[AuditRecord]) -> list[Finding]:
    """같은 영어가 화면마다 다르게 번역된 것을 보고한다.

    Dashboard 가 어떤 화면에서는 仪表板, 다른 화면에서는 仪表盘 이면 둘 다 맞는
    말이어도 제품은 조잡해 보인다. 문법 판정이 아니라 **일관성** 판정이므로
    기계가 확실히 할 수 있다.

    짧거나 브랜드에 해당하는 말은 건너뛴다 — 'ID' 가 문맥에 따라 '아이디' 와
    '식별자' 로 갈리는 것은 정상이다.
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


def classify_length_overflow(records: list[AuditRecord]) -> list[Finding]:
    """번역이 영어보다 지나치게 길어 UI 를 넘칠 위험을 보고한다.

    줌 감사는 레이아웃을 보지만 **번역 길이** 는 보지 않는다. 라벨이 두 배 넘게
    길어지면 버튼이 줄바꿈되거나 잘린다 — 이번 세션에 ACTIONS 열이 71px 늘어
    표 전체가 밀린 것과 같은 종류다.
    """
    findings: list[Finding] = []
    for record in records:
        en = (record.texts.get("en") or "").strip()
        if len(en) < 6:
            continue
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
    """번역이 {n} 같은 자리표시자를 잃거나 바꾼 것을 보고한다.

    잃으면 값이 사라지고(사용자는 'Found  models' 를 본다), 이름이 바뀌면 포맷이
    터진다. 실측 시점에는 0건이었으나, 0 을 계약으로 고정해 두지 않으면 다음
    번역 추가 때 조용히 들어온다.
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
