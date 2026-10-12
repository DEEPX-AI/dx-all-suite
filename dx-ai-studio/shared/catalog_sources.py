"""Shared catalog *parsers* used by both dx_app and dx_modelzoo.

dx_app and dx_modelzoo keep genuinely different views over the parsed catalog
data (dx_app wants a lightweight id -> file map; dx_modelzoo wants rich UI
metadata) — this module is the home for only the parsing logic that was
literally copy-drifted across the two apps, not a merged "catalog API".
"""
from pathlib import Path


def parse_test_models_conf(conf_path):
    """Parse a test_models.conf file into a list of raw model records.

    Format: tab-separated ``<id>\\t<category>\\t<model_file>`` lines; blank
    lines and ``#`` comments are skipped. Returns
    ``[{"id", "name", "category", "model_file"}, ...]`` in file order, or
    ``[]`` if the file is missing (callers decide whether/how to warn).

    Every field is stripped, so all call sites read the file the same way.
    """
    conf_path = Path(conf_path)
    if not conf_path.exists():
        return []
    models = []
    seen_variants = set()
    for line in conf_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        model_name = parts[0].strip()
        category = parts[1].strip()
        model_file = parts[2].strip()
        # Per-model dx_app layout: family<TAB>task<TAB>model_file<TAB>variant. Column 1 is the family (shared by
        # several lines); the model is the variant in column 4 (the .dxnn name).
        variant = parts[3].strip() if len(parts) > 3 else ""
        if variant:
            # Registry aliases (deit_base384_distilled → deit_base_distilled_2) share a variant and give two
            # conf lines; keep one line per model so the Model Zoo does not list it twice.
            if variant in seen_variants:
                continue
            seen_variants.add(variant)
            models.append({"id": variant, "name": variant, "category": category, "model_file": model_file,
                           "family": model_name, "variant": variant})
            continue
        models.append({
            "id": model_name,
            "name": model_name,
            "category": category,
            "model_file": model_file,
        })
    return models
