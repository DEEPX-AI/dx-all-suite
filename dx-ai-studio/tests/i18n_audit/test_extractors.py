from tools.i18n_audit.classify import classify_records
from tools.i18n_audit.extractors import (
    extract_from_html,
    extract_from_json_obj,
    extract_from_python_source,
    extract_inventory,
    extract_js_i18n_entries,
    iter_source_files,
)


def test_extract_html_language_span_group_marks_missing_span_language():
    html = """
    <div class="hub-tagline">
      <span class="ko">올인원 Edge AI 플랫폼</span>
      <span class="en">All-in-One Edge AI Platform</span>
      <span class="ja">オールインワン Edge AI プラットフォーム</span>
      <span class="zh-CN">一体化 Edge AI 平台</span>
      <span class="zh-TW">全方位 Edge AI 平台</span>
    </div>
    """

    records = extract_from_html(
        html,
        module="launcher",
        source_file="launcher/static/index.html",
    )

    record = next(r for r in records if r.selector_or_key.endswith(".hub-tagline"))
    assert record.texts["en"] == "All-in-One Edge AI Platform"
    assert record.texts["es"] == ""


def test_extract_html_language_span_group_with_line_break_keeps_missing_language_visible():
    html = """
    <div class="compat-help">
      <span class="ko">CPU + 보드 선택 시 자동으로 검사됩니다.<br>✅ 호환</span>
      <span class="en">Auto-checks when CPU + Board are selected.<br>✅ Compatible</span>
      <span class="ja">CPU + ボード選択時に自動で検査されます。<br>✅ 互換</span>
    </div>
    """

    records = extract_from_html(
        html,
        module="dx_stream",
        source_file="dx_stream/templates/index.html",
    )

    record = next(r for r in records if r.selector_or_key.endswith(".compat-help"))
    assert record.texts["en"] == "Auto-checks when CPU + Board are selected. ✅ Compatible"
    assert record.texts["es"] == ""


def test_extract_html_attributes_for_placeholder_title_and_aria():
    html = '<input placeholder="Search models" title="Search" aria-label="Model search">'

    records = extract_from_html(html, module="dx_modelzoo", source_file="x.html")

    keys = {r.selector_or_key for r in records}
    assert "placeholder:Search models" in keys
    assert "title:Search" in keys
    assert "aria-label:Model search" in keys


def test_iter_source_files_excludes_submodule_and_pycache(tmp_path):
    (tmp_path / "dx_app/static/js").mkdir(parents=True)
    (tmp_path / "dx_app/static/js/i18n.js").write_text("", encoding="utf-8")
    (tmp_path / "dc_dx_studio").mkdir()
    (tmp_path / "dc_dx_studio/main.py").write_text("", encoding="utf-8")

    files = [p.as_posix() for p in iter_source_files(tmp_path)]

    assert any(path.endswith("dx_app/static/js/i18n.js") for path in files)
    assert not any("dc_dx_studio" in path for path in files)


def test_extract_json_language_maps_recursively():
    data = {"hero": {"title": {"en": "About", "ko": "소개", "ja": "概要", "zh-CN": "关于", "zh-TW": "關於"}}}

    records = extract_from_json_obj(data, module="launcher", source_file="about-data.json")

    assert records[0].selector_or_key == "hero.title"
    assert records[0].texts["es"] == ""


def test_extract_js_i18n_dictionary_entries():
    source = "window._DX_I18N_DICT = {'Run': { ko:'실행', ja:'実行', 'zh-CN':'运行', 'zh-TW':'執行' }};"

    records = extract_js_i18n_entries(source, module="dx_stream", source_file="stream-i18n.js")

    assert records[0].selector_or_key == "Run"
    assert records[0].texts["en"] == "Run"
    assert records[0].texts["ko"] == "실행"
    assert records[0].texts["es"] == ""


def test_extract_js_i18n_dictionary_decodes_quoted_keys_and_escapes():
    source = (
        "window._DX_I18N_DICT = {"
        "'Click \"Analyze\"': { ko:'\"분석\" 클릭', es:'Haga clic en \"Analyze\"' },"
        "'Starting…\\n': { ko:'시작 중…\\n', ja:'開始中…\\n' },"
        "\"Board's mode\": { ko:'보드 모드', es:'modo de la placa' }"
        "};"
    )

    records = extract_js_i18n_entries(source, module="dx_stream", source_file="stream-i18n.js")
    by_key = {record.selector_or_key: record for record in records}

    assert by_key['Click "Analyze"'].texts["ko"] == '"분석" 클릭'
    assert by_key["Starting…\n"].texts["ja"] == "開始中…\n"
    assert by_key["Board's mode"].texts["es"] == "modo de la placa"


# --- Issue 1: _SPAN_RE substring false positive ---

def test_css_class_substring_not_treated_as_locale():
    """Classes like 'content' or 'styles' must not match as en/es locale spans."""
    html = '<div class="wrapper"><span class="content">some content</span><span class="styles">other text</span></div>'
    records = extract_from_html(html, module="launcher", source_file="test.html")
    assert not any(r.surface == "static-html" for r in records)


# --- Issue 2: nested same-tag elements break grouping ---

def test_nested_same_tag_does_not_drop_language_spans():
    """Wrapper with nested same-tag child must still find language spans."""
    html = (
        '<div class="wrapper">'
        '<div class="inner-block">inner</div>'
        '<span class="en">English</span>'
        '<span class="ko">Korean</span>'
        '</div>'
    )
    records = extract_from_html(html, module="launcher", source_file="test.html")
    static = [r for r in records if r.surface == "static-html"]
    assert len(static) >= 1
    rec = static[0]
    assert rec.texts["en"] == "English"
    assert rec.texts["ko"] == "Korean"


# --- Issue 3: duplicate records from ancestor propagation ---

def test_extract_html_emits_nearest_language_wrapper_only():
    """Non-language ancestors must not duplicate locale span records."""
    html = """
    <div class="app">
      <section class="nav-section">
        <div class="nav-item">
          <span class="nav-label">
            <span class="en">Setup</span>
            <span class="ko">설정</span>
          </span>
        </div>
      </section>
    </div>
    """

    records = extract_from_html(html, module="dx_app", source_file="dx_app/templates/index.html")
    static_records = [r for r in records if r.surface == "static-html"]

    assert len(static_records) == 1
    assert static_records[0].selector_or_key == ".nav-label"
    assert static_records[0].texts["en"] == "Setup"


# --- Issue 4: _text_ sentinel creates false locale group threshold ---

def test_extract_html_ignores_direct_text_when_deciding_locale_group():
    """Direct text (_text_ sentinel) must not count toward the >=2 span threshold."""
    html = """
    <div class="outer">
      <div class="middle"><span class="en">English</span> and some text</div>
      <span class="ko">Korean</span>
    </div>
    """

    records = extract_from_html(html, module="launcher", source_file="launcher/static/index.html")
    static_records = [r for r in records if r.surface == "static-html"]

    assert len(static_records) == 1
    assert static_records[0].selector_or_key == ".outer"
    assert static_records[0].texts["en"] == "English"
    assert static_records[0].texts["ko"] == "Korean"


# --- Issue 5: JS dictionary regex drops entries with braces in values ---

def test_extract_js_i18n_dictionary_keeps_braces_inside_strings():
    source = "window._DX_I18N_DICT = {'Model {0}': { ko:'모델 {0}', ja:'モデル {0}', 'zh-CN':'模型 {0}' }};"

    records = extract_js_i18n_entries(source, module="dx_modelzoo", source_file="i18n-dict.js")

    assert len(records) == 1
    assert records[0].selector_or_key == "Model {0}"
    assert records[0].texts["en"] == "Model {0}"
    assert records[0].texts["ko"] == "모델 {0}"
    assert records[0].texts["ja"] == "モデル {0}"


# --- Issue 6: wrapper selector truncates to first two CSS classes ---

def test_extract_html_selector_preserves_all_non_locale_classes():
    html = """
    <div class="nav-item primary-action expand">
      <span class="en">Expand</span><span class="ko">확장</span>
    </div>
    <div class="nav-item primary-action collapse">
      <span class="en">Collapse</span><span class="ko">접기</span>
    </div>
    """

    records = [
        r for r in extract_from_html(html, module="launcher", source_file="index.html")
        if r.surface == "static-html"
    ]

    assert {r.selector_or_key for r in records} == {
        ".nav-item.primary-action.expand",
        ".nav-item.primary-action.collapse",
    }
    assert len({r.record_id for r in records}) == 2


# --- Issue 7 (Chunk 3): Brand-term suppression via real extraction path ---

def test_extract_inventory_tags_brand_terms_for_classifier(tmp_path):
    (tmp_path / "launcher/static").mkdir(parents=True)
    (tmp_path / "launcher/static/index.html").write_text(
        '<button aria-label="NPU"></button>', encoding="utf-8"
    )

    records = extract_inventory(tmp_path)

    assert records[0].brand_terms == ("NPU",)
    assert classify_records(records) == []


def test_extract_html_attr_brand_term_attached():
    """HTML attribute records for pure brand terms get brand_terms populated."""
    records = extract_from_html(
        '<input aria-label="SDK" placeholder="Enter model name">',
        module="shared",
        source_file="shared/widget.html",
    )
    brand_rec = next(r for r in records if r.selector_or_key == "aria-label:SDK")
    normal_rec = next(r for r in records if r.selector_or_key == "placeholder:Enter model name")
    assert brand_rec.brand_terms == ("SDK",)
    assert normal_rec.brand_terms == ()


def test_extract_json_brand_term_attached():
    """JSON language-map records with pure brand-term English get brand_terms."""
    data = {"chip": {"label": {"en": "NPU", "ko": "NPU"}}}
    records = extract_from_json_obj(data, module="shared", source_file="hw.json")
    assert records[0].brand_terms == ("NPU",)


def test_extract_js_brand_term_attached():
    """JS i18n entries with pure brand-term key get brand_terms."""
    source = "window._DX_I18N = {'NPU': { ko:'NPU', ja:'NPU' }};"
    records = extract_js_i18n_entries(source, module="shared", source_file="i18n.js")
    assert records[0].brand_terms == ("NPU",)


def test_extract_html_span_group_brand_term_attached():
    """HTML span groups with pure brand-term English text get brand_terms."""
    html = '<div class="brand"><span class="en">GStreamer</span><span class="ko">GStreamer</span></div>'
    records = extract_from_html(html, module="shared", source_file="widget.html")
    static = [r for r in records if r.surface == "static-html"]
    assert static[0].brand_terms == ("GStreamer",)


def test_brand_term_not_attached_for_longer_copy():
    """Records containing a brand term in longer copy should NOT get brand_terms."""
    html = '<input aria-label="Open NPU Settings">'
    records = extract_from_html(html, module="shared", source_file="widget.html")
    assert records[0].brand_terms == ()


# --- Issue 8 (Chunk 3): Python extractor ---

def test_extract_inventory_reads_python_language_maps(tmp_path):
    (tmp_path / "launcher").mkdir()
    (tmp_path / "launcher/messages.py").write_text(
        'MESSAGES = {"hero": {"title": {"en": "About", "ko": "소개", "ja": "概要", "zh-CN": "关于", "zh-TW": "關於"}}}\n',
        encoding="utf-8",
    )

    records = extract_inventory(tmp_path)

    assert records[0].source_file == "launcher/messages.py"
    assert records[0].selector_or_key.endswith("hero.title")
    assert records[0].texts["es"] == ""


def test_extract_from_python_source_simple_dict():
    source = 'LABELS = {"en": "Hello", "ko": "안녕", "ja": "こんにちは"}\n'
    records = extract_from_python_source(source, module="launcher", source_file="labels.py")
    assert len(records) >= 1
    assert records[0].texts["en"] == "Hello"
    assert records[0].texts["ko"] == "안녕"


def test_extract_from_python_source_nested_dict():
    source = 'MESSAGES = {"hero": {"title": {"en": "About", "ko": "소개", "ja": "概要", "zh-CN": "关于", "zh-TW": "關於"}}}\n'
    records = extract_from_python_source(source, module="launcher", source_file="messages.py")
    assert len(records) >= 1
    assert records[0].selector_or_key.endswith("hero.title")


def test_extract_from_python_source_invalid_syntax():
    """Invalid Python should not crash; return empty list."""
    source = "def broken(\n"
    records = extract_from_python_source(source, module="launcher", source_file="bad.py")
    assert records == []


def test_extract_from_python_source_brand_terms():
    """Python extractor should also tag brand terms."""
    source = 'CHIPS = {"label": {"en": "NPU", "ko": "NPU"}}\n'
    records = extract_from_python_source(source, module="shared", source_file="hw.py")
    assert records[0].brand_terms == ("NPU",)


# --- Issue (Chunk 3): Python extractor handles annotated assignments ---

def test_extract_inventory_reads_python_annotated_language_maps(tmp_path):
    (tmp_path / "dx_app").mkdir()
    (tmp_path / "dx_app/messages.py").write_text(
        'LABELS: dict[str, object] = {"hero": {"title": {"en": "Hello", "ko": "안녕", "ja": "こんにちは"}}}\n',
        encoding="utf-8",
    )

    records = extract_inventory(tmp_path)

    assert records
    assert records[0].source_file == "dx_app/messages.py"
    assert records[0].selector_or_key.endswith("hero.title")
    assert records[0].texts["en"] == "Hello"


def test_extract_from_python_source_annotated_assign():
    """AnnAssign nodes (typed assignments) should be extracted like Assign."""
    source = 'LABELS: dict[str, object] = {"en": "Hello", "ko": "안녕"}\n'
    records = extract_from_python_source(source, module="dx_app", source_file="msgs.py")
    assert len(records) >= 1
    assert records[0].texts["en"] == "Hello"


def test_extract_from_python_source_annotated_assign_no_value():
    """AnnAssign without a value (declaration only) should not crash."""
    source = 'LABELS: dict[str, object]\n'
    records = extract_from_python_source(source, module="dx_app", source_file="msgs.py")
    assert records == []


# --- Issue 9: Report self-scan and test contamination ---

def test_iter_source_files_excludes_reports_and_tests(tmp_path):
    """iter_source_files must not yield files under docs/superpowers/reports/ or tests/."""
    (tmp_path / "launcher/static").mkdir(parents=True)
    (tmp_path / "launcher/static/index.html").write_text(
        '<div><span class="en">Hello</span></div>', encoding="utf-8"
    )
    (tmp_path / "docs/superpowers/reports").mkdir(parents=True)
    (tmp_path / "docs/superpowers/reports/audit.json").write_text("{}", encoding="utf-8")
    (tmp_path / "tests/i18n_audit").mkdir(parents=True)
    (tmp_path / "tests/i18n_audit/test_extractors.py").write_text("# test", encoding="utf-8")

    files = [p.relative_to(tmp_path).as_posix() for p in iter_source_files(tmp_path)]

    assert "launcher/static/index.html" in files
    assert not any(f.startswith("docs/superpowers/reports/") for f in files)
    assert not any(f.startswith("tests/") for f in files)


def test_extract_inventory_excludes_reports_and_tests(tmp_path):
    """extract_inventory must not emit records from report artifacts or test files."""
    (tmp_path / "launcher/static").mkdir(parents=True)
    (tmp_path / "launcher/static/index.html").write_text(
        '<div><span class="en">Hello</span><span class="ko">안녕</span></div>',
        encoding="utf-8",
    )
    (tmp_path / "docs/superpowers/reports").mkdir(parents=True)
    (tmp_path / "docs/superpowers/reports/audit.json").write_text(
        '{"records": [{"en": "Phantom", "ko": "유령"}]}', encoding="utf-8"
    )
    (tmp_path / "tests/i18n_audit").mkdir(parents=True)
    (tmp_path / "tests/i18n_audit/test_extractors.py").write_text(
        'LABELS = {"en": "Test", "ko": "테스트"}\n', encoding="utf-8"
    )

    records = extract_inventory(tmp_path)

    assert all(r.source_file.startswith("launcher/") for r in records)
    assert not any(r.source_file.startswith("docs/superpowers/reports/") for r in records)
    assert not any(r.source_file.startswith("tests/") for r in records)
