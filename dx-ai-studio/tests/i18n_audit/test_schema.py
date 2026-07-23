from tools.i18n_audit.schema import AuditRecord, CoverageState, Finding


def test_audit_record_serializes_all_language_fields():
    record = AuditRecord(
        module="launcher",
        surface="home",
        route_or_state="/",
        source_file="launcher/static/index.html",
        selector_or_key=".hub-tagline",
        text_role="body",
        texts={
            "en": "All-in-One Edge AI Platform",
            "ja": "オールインワン Edge AI プラットフォーム",
            "ko": "올인원 Edge AI 플랫폼",
            "es": "",
            "zh-CN": "一体化 Edge AI 平台",
            "zh-TW": "全方位 Edge AI 平台",
        },
        brand_terms=("DX AI Studio",),
    )

    data = record.to_dict()

    assert data["module"] == "launcher"
    assert data["es"] == ""
    assert data["brand_terms"] == ["DX AI Studio"]


def test_finding_serializes_issue_type_and_severity():
    finding = Finding(
        record_id="launcher:home:.hub-tagline",
        issue_type="missing-language",
        severity="High",
        message="Spanish text is missing",
        suggested_fix="Add general Spanish copy.",
        verification_method="static inventory",
    )

    assert finding.to_dict()["severity"] == "High"
    assert finding.to_dict()["issue_type"] == "missing-language"


def test_coverage_state_tracks_locale_evidence():
    state = CoverageState(
        module="dx_stream",
        state="pipeline-editor",
        route="/stream/",
        locales_checked=("en", "ja", "ko", "es", "zh-CN", "zh-TW"),
        evidence=("browser text samples",),
    )

    assert state.to_dict()["locales_checked"] == ["en", "ja", "ko", "es", "zh-CN", "zh-TW"]



def _make_record(**overrides):
    defaults = dict(
        module="launcher",
        surface="home",
        route_or_state="/",
        source_file="launcher/static/index.html",
        selector_or_key=".hub-tagline",
        text_role="body",
        texts={"en": "Hello", "ko": "안녕"},
    )
    defaults.update(overrides)
    return AuditRecord(**defaults)


def test_texts_mutation_raises_type_error():
    record = _make_record()
    import pytest

    with pytest.raises(TypeError):
        record.texts["en"] = "tampered"


def test_hash_succeeds_and_is_stable():
    a = _make_record()
    b = _make_record()
    assert hash(a) == hash(b)
    assert a == b
    # usable in sets
    assert len({a, b}) == 1


def test_hash_differs_for_different_texts():
    a = _make_record(texts={"en": "Hello"})
    b = _make_record(texts={"en": "Goodbye"})
    # hashes *could* collide but almost certainly won't for these inputs
    assert hash(a) != hash(b)


def test_to_dict_still_emits_all_locale_keys():
    record = _make_record(texts={"en": "Hello"})
    data = record.to_dict()
    from tools.i18n_audit.config import LANGUAGES

    for lang in LANGUAGES:
        assert lang in data
    assert data["en"] == "Hello"
    assert data["ko"] == ""


def test_constructor_accepts_plain_dict():
    """Callers can still pass a plain dict; it gets frozen internally."""
    record = AuditRecord(
        module="m",
        surface="s",
        route_or_state="r",
        source_file="f",
        selector_or_key="k",
        text_role="t",
        texts={"en": "ok"},
    )
    assert record.texts["en"] == "ok"


# --- Issue 3: record_id must include source_file ---

def test_record_id_unique_across_source_files():
    """Same module/surface/selector but different source_file => different record_id."""
    a = _make_record(source_file="file_a.html")
    b = _make_record(source_file="file_b.html")
    assert a.record_id != b.record_id
    assert "file_a.html" in a.record_id
    assert "file_b.html" in b.record_id
