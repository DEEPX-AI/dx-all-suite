"""Phase 4 i18n Audit Contracts — Module Language Bridges.

Validates:
- Module language bridge integration (postMessage or DXI18n.onLangChange hook)
- No Korean default fallback in critical modules
- CSS/HTML language marker updates via shared/i18n.js or module-local code
- Hardcoded visible text remediation (Critical/High)
"""
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
REQUIRED_LANGS = {"en", "ko", "ja", "zh-CN", "zh-TW"}
BRAND_ALLOWLIST = {
    "DX AI Studio": "official product name",
    "DX App": "official product name",
    "DX Stream": "official product name",
    "DX Sandbox": "official product name",
    "DX Model Zoo": "official product name",
    "DX Compiler": "official product name",
    "DX EdgeGuide": "official product name",
    "DX Benchmark": "official product name",
    "DX Monitor": "official product name",
    "SDK Library": "official product/documentation feature name",
}
MODULE_BRIDGE_FILES = {
    "dx_app": ["dx_app/static/js/lang-refresh.js"],
    "dx_stream": ["dx_stream/static/js/stream-lang-refresh.js"],
    "dx_modelzoo": ["dx_modelzoo/static/js/i18n.js"],
    "dx_compiler": ["dx_compiler/static/js/compiler-i18n.js"],
    "dx_planner": ["dx_planner/static/js/i18n.js"],
    "dx_benchmark": ["dx_benchmark/static/js/app.js"],
    "dx_monitor": ["dx_monitor/static/js/i18n.js", "dx_monitor/static/js/dashboard.js"],
    "dx_agent_dev": ["dx_agent_dev/static/js/console.js"],
}
SHARED_I18N = "shared/static/i18n.js"



def _read(relpath: str) -> str:
    """Read a file relative to project root."""
    p = ROOT / relpath
    if not p.exists():
        pytest.skip(f"File not found: {relpath}")
    return p.read_text(encoding="utf-8")


def _read_module_source(module: str) -> str:
    """Read all bridge files for a module, concatenated."""
    parts = []
    for f in MODULE_BRIDGE_FILES[module]:
        parts.append(_read(f))
    return "\n".join(parts)


def test_planner_i18n_js_has_commas_before_spanish_entries():
    source = _read("dx_planner/static/js/i18n.js")
    missing = re.findall(r"'zh-TW':\s*'(?:\\.|[^'\\])*'\s*\n\s*es:", source)
    assert not missing, missing[:5]


def test_about_deepx_inline_t_maps_include_spanish():
    source = _read("launcher/static/about-deepx.js")
    missing = []
    for match in re.finditer(r"T\(\{(?P<body>.*?)\}\)", source, re.S):
        body = match.group("body")
        if not re.search(r"(?:^|[\s,])(?:'es'|\"es\"|es)\s*:", body):
            line_no = source[:match.start()].count("\n") + 1
            missing.append(line_no)
    assert not missing, f"about-deepx.js T() maps missing es at lines: {missing}"


def test_about_nav_initial_labels_are_not_korean_only():
    html = _read("launcher/static/index.html")
    expected = {
        "aboutCompany": "Company",
        "aboutTech": "Technology",
        "aboutProducts": "Products",
        "aboutInvestment": "Awards",
        "aboutPartners": "Partners",
        "aboutNews": "News",
    }
    for section, label in expected.items():
        pattern = (
            rf'<a[^>]+class="about-nav-tab"[^>]+data-section="{section}"'
            rf'[^>]*>\s*{re.escape(label)}\s*</a>'
        )
        assert re.search(pattern, html), (
            f"{section}: initial label must be English before JSON/i18n load"
        )


def test_sdk_library_brand_subtitle_has_spanish():
    source = _read("launcher/static/sdk-library.js")
    mount = re.search(r"DXBrand\.mount\(\{(?P<body>.*?)\n\s*\}\);", source, re.S)
    assert mount, "SDK Library must mount DXBrand"
    subtitle = re.search(r"subtitle:\s*\{(?P<body>.*?)\n\s*\}", mount.group("body"), re.S)
    assert subtitle, "SDK Library DXBrand subtitle map missing"
    assert re.search(r"(?:^|[\s,])(?:'es'|\"es\"|es)\s*:", subtitle.group("body")), (
        "SDK Library DXBrand subtitle map must define es"
    )


@pytest.mark.parametrize(
    ("lang", "expected"),
    [
        ("en", "Please check API settings"),
        ("ko", "채팅 설정"),
        ("ja", "チャット設定"),
        ("es", "configuración"),
        ("zh-CN", "聊天设置"),
        ("zh-TW", "聊天設定"),
    ],
)
def test_shared_chat_error_response_supports_six_languages(lang, expected):
    from shared.chat.engine import ChatEngine

    text = "".join(ChatEngine("dx_app")._error_response("Boom", "detail", lang=lang))
    assert expected in text


@pytest.mark.parametrize(
    "template",
    [
        "dx_compiler/templates/base.html",
        "dx_benchmark/templates/index.html",
        "dx_monitor/templates/index.html",
        "dx_planner/templates/index.html",
    ],
)
def test_release_module_templates_start_with_english_lang(template):
    html = _read(template)
    assert re.search(r"<html[^>]+lang=[\"']en[\"']", html), template


def _read_module_with_shared(module: str) -> str:
    """Read module bridge files + shared i18n (all modules load it)."""
    parts = [_read_module_source(module)]
    shared = ROOT / SHARED_I18N
    if shared.exists():
        parts.append(shared.read_text(encoding="utf-8"))
    return "\n".join(parts)



class TestModuleBridgePatterns:
    """Each module must have language bridge integration."""

    @pytest.mark.parametrize("module", list(MODULE_BRIDGE_FILES.keys()))
    def test_module_has_lang_change_handling(self, module):
        """Module must handle dx-lang-change (via shared i18n or own listener)."""
        source = _read_module_with_shared(module)
        assert "dx-lang-change" in source, (
            f"{module}: no dx-lang-change handling found in module or shared i18n"
        )

    @pytest.mark.parametrize("module", list(MODULE_BRIDGE_FILES.keys()))
    def test_module_has_message_listener(self, module):
        """Module (+ shared i18n) must have addEventListener('message')."""
        source = _read_module_with_shared(module)
        assert (
            "addEventListener('message'" in source
            or 'addEventListener("message"' in source
        ), f"{module}: no message event listener"

    @pytest.mark.parametrize("module", list(MODULE_BRIDGE_FILES.keys()))
    def test_module_reads_localstorage_lang(self, module):
        """Module (+ shared i18n) must read localStorage dx-lang."""
        source = _read_module_with_shared(module)
        assert (
            "localStorage.getItem('dx-lang')" in source
            or 'localStorage.getItem("dx-lang")' in source
            or "localStorage.getItem(STORAGE_KEY)" in source
        ), f"{module}: no localStorage dx-lang read"

    @pytest.mark.parametrize("module", list(MODULE_BRIDGE_FILES.keys()))
    def test_module_has_local_refresh_hook(self, module):
        """Module must register a local refresh hook for language changes."""
        source = _read_module_source(module)
        has_hook = (
            "DXI18n.onLangChange" in source
            or "_DX_I18N_CALLBACKS.push(" in source
            or "dx-lang-change" in source
            or "refreshLanguage" in source
        )
        assert has_hook, (
            f"{module}: no local language change hook "
            "(DXI18n.onLangChange, _DX_I18N_CALLBACKS.push(...), or dx-lang-change listener)"
        )

    @pytest.mark.parametrize("module", ["dx_app", "dx_modelzoo", "dx_stream"])
    def test_module_has_own_message_listener(self, module):
        """Modules with own postMessage handling or DXI18n.onLangChange must have local bridge."""
        source = _read_module_source(module)
        has_local_bridge = (
            "addEventListener('message'" in source
            or 'addEventListener("message"' in source
            or "DXI18n.onLangChange" in source
            or "dx-lang-change" in source
        )
        assert has_local_bridge, (
            f"{module}: no module-local language bridge (message listener or DXI18n.onLangChange)"
        )



class TestNoKoreanDefaults:
    """Critical: modules must not default to Korean."""

    def test_dx_stream_does_not_default_to_korean(self):
        source = _read("dx_stream/static/js/stream-app.js") + _read("dx_stream/static/js/tutorial.js")
        assert "|| 'ko'" not in source, (
            "dx_stream defaults to Korean — must use 'en'"
        )
        assert '|| "ko"' not in source, (
            "dx_stream defaults to Korean — must use 'en'"
        )

    def test_dx_benchmark_tutorial_does_not_default_to_korean(self):
        source = _read("dx_benchmark/static/js/tutorial.js")
        assert "|| 'ko'" not in source, (
            "dx_benchmark tutorial defaults to Korean — must use 'en'"
        )
        assert '|| "ko"' not in source, (
            "dx_benchmark tutorial defaults to Korean — must use 'en'"
        )

    def test_dx_benchmark_i18n_does_not_default_to_korean(self):
        source = _read("dx_benchmark/static/js/i18n.js")
        assert "|| 'ko'" not in source, (
            "dx_benchmark i18n defaults to Korean — must use 'en'"
        )
        assert '|| "ko"' not in source, (
            "dx_benchmark i18n defaults to Korean — must use 'en'"
        )

    def test_shared_tutorial_init_does_not_default_to_korean(self):
        source = _read("shared/static/tutorial-init.js")
        assert "|| 'ko'" not in source, (
            "shared/tutorial-init.js defaults to Korean — must use 'en'"
        )
        assert '|| "ko"' not in source, (
            "shared/tutorial-init.js defaults to Korean — must use 'en'"
        )



class TestCSSLanguageMarkers:
    """Modules using CSS language classes must update html lang and body classes."""

    def test_shared_i18n_updates_html_and_body_markers(self):
        """shared/i18n.js (loaded by all modules) must set documentElement.lang and body classes."""
        source = _read(SHARED_I18N)
        assert "document.documentElement.lang" in source or "documentElement.lang" in source, (
            "shared/i18n.js does not set document.documentElement.lang"
        )
        assert "classList.remove('lang-'" in source or 'classList.remove("lang-"' in source or "classList.remove('lang-' +" in source, (
            "shared/i18n.js does not remove lang- classes from body"
        )
        assert "classList.add('lang-'" in source or 'classList.add("lang-"' in source or "classList.add('lang-' +" in source, (
            "shared/i18n.js does not add lang- classes to body"
        )

    def test_dx_stream_relies_on_shared_css_markers(self):
        """dx_stream uses CSS language spans — shared i18n must provide markers."""
        source = _read("dx_stream/static/js/stream-app.js")
        # Module uses language-specific spans like '.ko', '.en'
        has_lang_spans = (
            "'.ko'" in source or '".ko"' in source
            or "'.en'" in source or '".en"' in source
            or "class=\"ko\"" in source or "class='ko'" in source
        )
        assert has_lang_spans, (
            "dx_stream does not appear to use CSS language spans (.ko/.en)"
        )



class TestNoHardcodedCriticalText:
    """Critical hardcoded UI text must use i18n wrappers."""

    def test_dx_monitor_dashboard_uses_i18n_for_labels(self):
        """Dashboard status labels should use T() or statusLabel() not raw strings."""
        source = _read("dx_monitor/static/js/dashboard.js")
        # statusLabel function should exist for translatable labels
        assert "statusLabel(" in source or "T(" in source or "_t(" in source, (
            "dx_monitor dashboard has no i18n function calls for status labels"
        )

    def test_dx_benchmark_app_uses_i18n(self):
        """BenchApp empty states should use _t() or T()."""
        source = _read("dx_benchmark/static/js/app.js")
        assert "_t(" in source or "T(" in source, (
            "dx_benchmark app.js has no i18n function for user-visible text"
        )
