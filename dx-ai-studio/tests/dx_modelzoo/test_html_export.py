"""The "Save as HTML" model-card export must be fully localized and complete
(legal block, compile guide, use-case, export timestamp), per the agreed scope."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "dx_modelzoo" / "static" / "js"


def _export_fn():
    src = (JS / "detail.js").read_text(encoding="utf-8")
    return src.split("function _buildModelCardHtml(", 1)[1].split("\nfunction ", 1)[0]


def test_export_is_localized():
    body = _export_fn()
    # html lang + headings via T(), not hardcoded English
    assert "html lang=\"' + e(lang)" in body
    for key in ("Key Facts", "Technical", "Accuracy Matrix", "Compile Guide",
                "Artifacts & Downloads", "Demo", "Source & License"):
        assert f"T('{key}')" in body, f"heading '{key}' must go through T()"


def test_export_has_complete_legal():
    body = _export_fn()
    for key in ("License", "License text", "Copyright", "Source", "Source profile",
                "Last metadata sync"):
        assert f"T('{key}')" in body, f"legal row '{key}' missing from export"


def test_export_has_compile_guide_and_timestamp():
    body = _export_fn()
    assert "m.compile_guide" in body and "recommended_quant" in body
    assert "toLocaleString(lang)" in body, "export must stamp the export time"


def test_export_added_dict_keys_complete():
    src = (JS / "i18n-dict-detail.js").read_text(encoding="utf-8")
    for key in ("Technical", "Demo", "Source & License", "Compile Guide", "Exported",
                "Preview", "Task", "Config"):
        block = src.split(f"'{key}':", 1)
        assert len(block) == 2, f"{key} missing from detail dict"
        seg = block[1].split("},", 1)[0]
        for lang in ("ko", "ja", "zh-CN", "zh-TW", "es"):
            assert lang in seg, f"{key} missing {lang}"
