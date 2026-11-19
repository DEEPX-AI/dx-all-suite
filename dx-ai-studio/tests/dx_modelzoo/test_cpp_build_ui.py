"""Model Zoo inference panel: Build C++ runner for a downloaded model without a built C++ runner."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = (ROOT / "dx_modelzoo/static/js/inference.js").read_text(encoding="utf-8")
DICT = (ROOT / "dx_modelzoo/static/js/i18n-dict-inference.js").read_text(encoding="utf-8")
KEYS = ["C++ runner not built for this model. C++ is usually faster than Python.", "Build C++ runner",
        "Building C++ runner…", "Show log", "C++ runner built ({t}). C++ · Sync selected.", "C++ runner build failed",
        "Setup is running — try again when it finishes.", "Cancel build"]


def test_panel_offers_the_build_only_for_buildable_models():
    body = JS[JS.index("function renderInferencePanel"):]
    body = body[:body.index("\n}\n")]
    assert "model.cpp_buildable" in body and "btnBuildCpp" in body and "_mzIco('wrench')" in body


def test_flow_uses_the_model_build_proxy_and_selects_cpp():
    for needle in ("/api/proxy/model-build", "/api/proxy/model-build/log", "/api/proxy/model-build/stop",
                   "cpp|sync", "refreshInferencePanelAfterDownload"):
        assert needle in JS, needle


def test_every_new_string_has_six_languages():
    for k in KEYS:
        i = DICT.index(f"'{k}'")
        entry = DICT[i:DICT.index("},", i)]
        for lang in ("en:", "ko:", "ja:", "'zh-CN':", "'zh-TW':", "es:"):
            assert lang in entry, (k, lang)
