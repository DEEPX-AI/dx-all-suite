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

    All three fields are stripped consistently — the parser used to be
    copy-drifted across 3 call sites with inconsistent per-field stripping;
    this is the safe superset (strip everything).
    """
    conf_path = Path(conf_path)
    if not conf_path.exists():
        return []
    models = []
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
        models.append({
            "id": model_name,
            "name": model_name,
            "category": category,
            "model_file": model_file,
        })
    return models
