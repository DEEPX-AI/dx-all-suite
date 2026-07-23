"""ModelZoo 16-item hardening DOM/static 계약 테스트."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]


def _read(rel_path: str) -> str:
    return (ROOT / rel_path).read_text(encoding="utf-8")


def _extract_i18n_block(src: str, key: str) -> str:
    match = re.search(rf"['\"]{re.escape(key)}['\"]\s*:\s*\{{(.*?)\n\s*\}}", src, re.DOTALL)
    assert match, f"i18n key missing: {key}"
    return match.group(1)


def _has_locale(block: str, locale: str) -> bool:
    quoted = f"'{locale}'" in block or f'"{locale}"' in block
    unquoted = "-" not in locale and re.search(rf"\b{re.escape(locale)}\s*:", block)
    return bool(quoted or unquoted)


def test_hardening_contract_full_width_layout():
    css = _read("dx_modelzoo/static/css/style.css")
    assert ".mz-explorer-shell" in css
    assert "max-width:1480px" not in css
    assert "max-width:1400px" not in css
    assert "max-width:960px" not in css
    assert re.search(r"\.mz-explorer-shell\s*\{[^}]*width:\s*100%", css, re.DOTALL)
    assert re.search(r"\.mz-explorer-shell\s*\{[^}]*max-width:\s*none", css, re.DOTALL)


def test_hardening_contract_category_checkbox_rail():
    html = _read("dx_modelzoo/templates/index.html")
    js = _read("dx_modelzoo/static/js/catalog.js")
    assert 'data-section="category"' in html
    assert "mz-category-option" in js
    assert 'type="checkbox"' in js


def test_hardening_contract_action_bar_and_dynamic_heading():
    detail = _read("dx_modelzoo/static/js/detail.js")
    catalog = _read("dx_modelzoo/static/js/catalog.js")
    css = _read("dx_modelzoo/static/css/style.css")
    assert "renderDetailActionBar" in detail
    assert "mz-detail-action-bar" in detail
    assert ".mz-detail-action-bar" in css
    assert "updateCatalogHeading" in catalog


def test_hardening_contract_status_and_legal_copy():
    detail = _read("dx_modelzoo/static/js/detail.js")
    catalog = _read("dx_modelzoo/static/js/catalog.js")
    combined = detail + "\n" + catalog
    for token in (
        "Using cached data after refresh failed",
        "Suspect value: source verification required",
        "License text not provided by source",
    ):
        assert token in combined, token


def test_hardening_contract_no_processor_filter_references():
    """Wave 2C: processor filter was removed; no JS should reference it."""
    catalog = _read("dx_modelzoo/static/js/catalog.js")
    tutorial = _read("dx_modelzoo/static/js/tutorial.js")
    assert "_selectedProcessor" not in catalog
    assert "processorFilters" not in catalog
    assert "processorFilters" not in tutorial


def test_hardening_contract_no_metadata_pending_copy():
    """Release cards should not expose internal metadata backlog wording."""
    catalog = _read("dx_modelzoo/static/js/catalog.js")
    assert "Metadata pending" not in catalog


def test_modelzoo_template_has_no_duplicate_i18n_title_attributes():
    html = _read("dx_modelzoo/templates/index.html")
    duplicate_lines = [
        (idx, line.strip())
        for idx, line in enumerate(html.splitlines(), 1)
        if line.count("data-i18n-title=") > 1
    ]
    assert not duplicate_lines, duplicate_lines


def test_hardening_contract_i18n_locales_present():
    # Read all i18n dictionary sources (core + fragments + bootstrap)
    import glob as _glob
    js_dir = str(ROOT / "dx_modelzoo" / "static" / "js")
    parts = [_read("dx_modelzoo/static/js/i18n.js")]
    for frag in sorted(_glob.glob(f"{js_dir}/i18n-dict-*.js")):
        parts.append(Path(frag).read_text(encoding="utf-8"))
    i18n = "\n".join(parts)
    required_locales = ("ko", "ja", "zh-CN", "zh-TW")
    keys = (
        "model variants",
        "unique models",
        "All Models",
        "Selected categories",
        "Using cached data after refresh failed",
        "Suspect value: source verification required",
        "License text",
        "License text not provided by source",
    )
    for key in keys:
        block = _extract_i18n_block(i18n, key)
        for locale in required_locales:
            assert _has_locale(block, locale), f"{key}: {locale}"
