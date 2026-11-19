"""Setup page: backend-rendered command lines, the Maintenance card, the NPU sanity row (6 languages)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HTML = (ROOT / "dx_app/templates/index.html").read_text(encoding="utf-8")
JS = (ROOT / "dx_app/static/js/setup.js").read_text(encoding="utf-8")
I18N = (ROOT / "dx_app/static/js/i18n.js").read_text(encoding="utf-8")
KEYS = ["Maintenance", "Clean C++ build", "Clean build", "Reset runtime and reinstall", "Reset and reinstall",
        "Deletes the C++ build folders (build_*, bin/) and rebuilds the demo runners for this machine.",
        "Removes DX-RT, the NPU driver, the Python venvs and the C++ builds, then runs Demo Quick Start. "
        "Downloaded models and videos are kept."]


def test_maintenance_card_sits_after_diagnostics_and_before_the_log():
    page = HTML[HTML.index('<div id="page-setup"'):]
    assert page.index('id="diag-run-btn"') < page.index('id="setup-maint"') < page.index('id="setup-log"')
    card = page[page.index('id="setup-maint"'):page.index("</details>", page.index('id="setup-maint"'))]
    assert "#wrench" in card and "#trash" in card and "#undo" in card
    assert 'onclick="setupCleanBuild()"' in card and 'onclick="setupResetRuntime()"' in card


def test_every_new_label_has_all_languages():
    for k in KEYS:
        assert f'data-i18n="{k}"' in HTML, k
        entry = I18N[I18N.index(f"'{k}'"):][:900]
        entry = entry[:entry.index("}")]
        for lang in ("ko:", "ja:", "'zh-CN':", "'zh-TW':", "es:"):
            assert lang in entry, (k, lang)


def test_js_wires_commands_reset_word_and_sanity():
    for needle in ("r.commands", "'runtime-reset'", "'clean-build'", "setupRunSanity", "/api/setup/sanity",
                   "diag-card-pending", "setupDemoQuickStart()"):
        assert needle in JS, needle
    assert "--arch x86_64" not in HTML


def test_tutorials_cover_the_new_ui():
    t = (ROOT / "dx_app/static/js/tutorial.js").read_text(encoding="utf-8")
    sec = t[t.index("id:'setup'"):]
    sec = sec[:sec.index("\n    },", 10)]
    assert "target:'#setup-maint'" in sec and "NPU sanity check" in sec
    mz = (ROOT / "dx_modelzoo/static/js/tutorial.js").read_text(encoding="utf-8")
    assert "#dxt-mock-exec" in mz and "Build C++ runner" in mz
