"""Build a static HTML dashboard backed by dataset.json."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .aggregator import save_dataset_json
from .config import APP_DIR

DASHBOARD_SRC_DIR = APP_DIR / "dashboard"
DATASET_PLACEHOLDER = "__DATASET_JSON__"
ASSET_VER_PLACEHOLDER = "__ASSET_VER__"


def _asset_version(app_js: str, styles_css: str, embedded_dataset: str) -> str:
    """Short content hash of everything the browser caches.

    Stamped onto the app.js / styles.css refs as ?v=<hash>. Content-derived, so an
    unchanged build reproduces the same hash (no git churn) while any code/style/data
    change yields a new hash — forcing the browser to refetch on a plain reload.
    """
    h = hashlib.sha1()
    for part in (app_js, styles_css, embedded_dataset):
        h.update(part.encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()[:8]


def build_static_dashboard(dataset: dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    save_dataset_json(dataset, output_dir / "dataset.json")

    app_js = (DASHBOARD_SRC_DIR / "app.js").read_text(encoding="utf-8")
    styles_css = (DASHBOARD_SRC_DIR / "styles.css").read_text(encoding="utf-8")

    index_html = (DASHBOARD_SRC_DIR / "index.html").read_text(encoding="utf-8")
    # Escape "</" so a stray "</script>" inside any string field can't terminate
    # the inline <script> block that carries the embedded dataset.
    embedded = json.dumps(dataset).replace("</", "<\\/")
    index_html = index_html.replace(DATASET_PLACEHOLDER, embedded)
    index_html = index_html.replace(
        ASSET_VER_PLACEHOLDER, _asset_version(app_js, styles_css, embedded))
    (output_dir / "index.html").write_text(index_html, encoding="utf-8")

    (output_dir / "app.js").write_text(app_js, encoding="utf-8")
    (output_dir / "styles.css").write_text(styles_css, encoding="utf-8")
    return output_dir / "index.html"
