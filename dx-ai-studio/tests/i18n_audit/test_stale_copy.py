"""Stale-copy classifier flags English verbatim in non-en locales."""

from tools.i18n_audit.classify import classify_stale_copy
from tools.i18n_audit.schema import AuditRecord


def test_stale_copy_flags_english_in_spanish():
    record = AuditRecord(
        module="launcher",
        surface="html-span-group",
        route_or_state="home",
        source_file="launcher/static/index.html",
        selector_or_key="example",
        text_role="body",
        texts={
            "en": "One-click download and deploy",
            "ko": "원클릭",
            "ja": "ワンクリック",
            "es": "One-click download and deploy",
            "zh-CN": "一键",
            "zh-TW": "一鍵",
        },
    )
    findings = classify_stale_copy([record])
    assert any(f.issue_type == "stale-copy" and "es" in f.message for f in findings)


def test_stale_copy_skips_brand_terms():
    from tools.i18n_audit.config import BRAND_TERMS
    brand = next(iter(BRAND_TERMS))
    record = AuditRecord(
        module="dx_app",
        surface="js-i18n-dictionary",
        route_or_state="",
        source_file="dx_app/static/js/i18n.js",
        selector_or_key=brand,
        text_role="label",
        texts={lang: brand for lang in ("en", "ja", "ko", "es", "zh-CN", "zh-TW")},
        brand_terms=(brand,),
    )
    findings = classify_stale_copy([record])
    assert not findings
