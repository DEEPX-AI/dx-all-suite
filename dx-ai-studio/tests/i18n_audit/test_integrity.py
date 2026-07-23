from tools.i18n_audit.integrity import extract_t_calls, html_shape, placeholder_tokens, record_integrity_issues
from tools.i18n_audit.schema import AuditRecord


def test_extract_t_calls_reports_inline_fallbacks():
    source = "button.textContent = T('Run Demo', '데모 실행');"
    calls = extract_t_calls(source, source_file="dx_app/static/js/demo.js")
    assert calls == [
        {
            "source_file": "dx_app/static/js/demo.js",
            "line": 1,
            "column": 22,
            "key": "Run Demo",
            "ko_fallback": "데모 실행",
            "disposition": "unclassified",
        }
    ]


def test_extract_t_calls_decodes_javascript_escape_sequences():
    source = r"notify(T('Starting compilation…\n', '\ud314\ub808\t\uc18d\uc131'));"
    calls = extract_t_calls(source, source_file="dx_app/static/js/compiler.js")
    assert calls == [
        {
            "source_file": "dx_app/static/js/compiler.js",
            "line": 1,
            "column": 8,
            "key": "Starting compilation…\n",
            "ko_fallback": "팔레\t속성",
            "disposition": "unclassified",
        }
    ]


def test_extract_t_calls_marks_empty_keys_for_manual_migration():
    source = "countLabel.textContent = total + T('', '개');"
    calls = extract_t_calls(source, source_file="dx_stream/static/js/forum.js")
    assert calls == [
        {
            "source_file": "dx_stream/static/js/forum.js",
            "line": 1,
            "column": 34,
            "key": None,
            "ko_fallback": "개",
            "disposition": "needs-manual-key",
            "rationale": "empty English T() key requires manual migration",
        }
    ]


def test_extract_t_calls_reports_column_for_duplicate_calls_on_one_line():
    source = "items = `${T('eff', '실효')} / ${T('eff', '실효')}`;"
    calls = extract_t_calls(source, source_file="dx_stream/static/js/theory-render.js")
    assert [call["line"] for call in calls] == [1, 1]
    assert [call["column"] for call in calls] == [12, 32]
    assert len({(call["line"], call["column"]) for call in calls}) == 2


def test_extract_t_calls_ignores_dynamic_and_wrong_arity_calls():
    source = "T(label, '이름'); T('Only one'); T('One', '하나', 'extra');"
    assert extract_t_calls(source, source_file="dx_app/static/js/demo.js") == []


def test_extract_t_calls_ignores_comments():
    source = """
    /* Use T('key', '키') for legacy inline fallbacks. */
    // T("Run Demo", "데모 실행")
    button.textContent = T('Run Demo', '데모 실행');
    """
    calls = extract_t_calls(source, source_file="dx_app/static/js/demo.js")
    assert len(calls) == 1
    assert calls[0]["line"] == 4
    assert calls[0]["key"] == "Run Demo"


def test_placeholder_tokens_detects_common_token_styles():
    text = "Model {0} uses ${device} at {{fps}} FPS with %s fallback"
    assert placeholder_tokens(text) == ("${device}", "%s", "{{fps}}", "{0}")


def test_placeholder_tokens_detects_formatted_printf_tokens():
    text = "Temperature %0.2f uses index %03d and label %-10s"
    assert placeholder_tokens(text) == ("%-10s", "%0.2f", "%03d")


def test_placeholder_tokens_ignores_natural_percent_text():
    assert placeholder_tokens("100% done and 80% success rate") == ()


def test_html_shape_keeps_tag_names_and_safe_attributes():
    assert html_shape("<strong>Run</strong><br><code>NPU</code>") == (
        ("strong", ()),
        ("br", ()),
        ("code", ()),
    )


def test_html_shape_keeps_self_closing_tags():
    assert html_shape("<br/><img src=\"logo.png\" alt=\"Logo\"/>") == (
        ("br", ()),
        ("img", ("alt", "src")),
    )


def test_record_integrity_issues_reports_placeholder_drift():
    record = AuditRecord(
        module="dx_app",
        surface="js-i18n-dictionary",
        route_or_state="source",
        source_file="dx_app/static/js/i18n.js",
        selector_or_key="Model {0}",
        text_role="data",
        texts={"en": "Model {0}", "es": "Modelo"},
    )
    issues = record_integrity_issues(record)
    assert issues == ["dx_app:js-i18n-dictionary:dx_app/static/js/i18n.js:Model {0}: es placeholder mismatch"]


def test_record_integrity_issues_reports_html_shape_drift():
    record = AuditRecord(
        module="dx_app",
        surface="js-i18n-dictionary",
        route_or_state="source",
        source_file="dx_app/static/js/i18n.js",
        selector_or_key="Run",
        text_role="data",
        texts={"en": "<strong>Run</strong>", "es": "<em>Ejecutar</em>"},
    )
    issues = record_integrity_issues(record)
    assert issues == ["dx_app:js-i18n-dictionary:dx_app/static/js/i18n.js:Run: es HTML shape mismatch"]


def test_record_integrity_issues_passes_when_locales_preserve_shape():
    record = AuditRecord(
        module="dx_app",
        surface="js-i18n-dictionary",
        route_or_state="source",
        source_file="dx_app/static/js/i18n.js",
        selector_or_key="Model {0}",
        text_role="data",
        texts={
            "en": "<strong>Model {0}</strong>",
            "es": "<strong>Modelo {0}</strong>",
            "ko": "<strong>모델 {0}</strong>",
        },
    )
    assert record_integrity_issues(record) == []
