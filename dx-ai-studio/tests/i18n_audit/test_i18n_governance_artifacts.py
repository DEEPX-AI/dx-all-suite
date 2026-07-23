from __future__ import annotations

from pathlib import Path
from collections import defaultdict

from tools.i18n_audit.extractors import extract_inventory, iter_source_files
from tools.i18n_audit.integrity import extract_t_calls

ROOT = Path(__file__).resolve().parents[2]

# Dev/tooling/excluded trees are not shipped product UI. The i18n_audit tool's own
# source legitimately contains a literal ``T('en', 'ko')`` in its regex/docstring, so
# scanning it would be a false positive; tests fixtures are likewise not product copy.
_NON_PRODUCT_PREFIXES = ("tools/", "tests/", "dx_sandbox/")


def _product_source_files():
    for path in iter_source_files(ROOT):
        p = path if isinstance(path, Path) else ROOT / path
        rel = str(p.relative_to(ROOT)) if p.is_absolute() else str(path)
        if rel.startswith(_NON_PRODUCT_PREFIXES):
            continue
        yield rel, p


def test_no_unclassified_visible_t_calls_in_product_source():
    """Product UI must not carry literal two-argument ``T('en', 'ko')`` calls.

    The i18n convention is keyed ``T('key')`` lookups; an inline English/Korean pair
    is an unmigrated straggler. This computes the inventory live from source so the
    guard cannot silently rot against a stale committed artifact.
    """
    unclassified = []
    for rel, path in _product_source_files():
        try:
            src = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for call in extract_t_calls(src, source_file=rel):
            if call.get("disposition") == "unclassified":
                unclassified.append(f"{rel}:{call['line']}")
    assert unclassified == [], (
        "Unmigrated literal T('en','ko') calls found in product source; "
        f"convert to keyed T('key'): {unclassified}"
    )


def test_js_i18n_dictionaries_do_not_repeat_keys_per_file():
    seen: dict[tuple[str, str], list[str]] = defaultdict(list)
    for record in extract_inventory(ROOT):
        if record.surface == "js-i18n-dictionary":
            seen[(record.source_file, record.selector_or_key)].append(record.record_id)

    duplicates = {
        f"{source_file}::{key}": record_ids
        for (source_file, key), record_ids in seen.items()
        if len(record_ids) > 1
    }
    assert duplicates == {}
