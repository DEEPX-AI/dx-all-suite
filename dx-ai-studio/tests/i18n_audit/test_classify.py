from tools.i18n_audit.classify import classify_records
from tools.i18n_audit.schema import AuditRecord


def test_missing_language_is_high_for_primary_record():
    record = AuditRecord(
        module="launcher",
        surface="static-html",
        route_or_state="/",
        source_file="launcher/static/index.html",
        selector_or_key=".hub-tagline",
        text_role="body",
        texts={"en": "All-in-One", "ja": "一体型", "ko": "올인원", "es": "", "zh-CN": "一体化", "zh-TW": "一體化"},
    )

    findings = classify_records([record])

    assert findings[0].issue_type == "missing-language"
    assert findings[0].severity == "High"
    assert "es" in findings[0].message


def test_non_critical_missing_language_is_medium():
    """Non-launcher, non-critical-role records with missing languages get Medium."""
    record = AuditRecord(
        module="dx_app",
        surface="json-language-map",
        route_or_state="source",
        source_file="dx_app/messages.json",
        selector_or_key="hero.title",
        text_role="data",
        texts={"en": "Hello", "ja": "", "ko": "안녕", "es": "", "zh-CN": "", "zh-TW": ""},
    )

    findings = classify_records([record])

    assert findings[0].severity == "Medium"


def test_brand_terms_are_not_reported_as_hardcoded_copy():
    record = AuditRecord(
        module="shared",
        surface="static-html-attribute",
        route_or_state="source",
        source_file="shared/hw_widget/widget.html",
        selector_or_key="title:DX-M1",
        text_role="title",
        texts={"en": "DX-M1"},
        brand_terms=("DX-M1",),
    )

    assert classify_records([record]) == []
