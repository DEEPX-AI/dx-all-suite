"""Model card for Studio's "Save as HTML": the same renderer, labels translated by the page.

Contract: tests/dx_modelzoo/test_model_card_endpoint.py
"""
from __future__ import annotations

import base64
from pathlib import PurePosixPath

from dx_modelzoo.core.model_card import (build_card, load_benchmark, load_manifest_urls, load_registry,
                                         load_setup_names, manifest_url_for)
from dx_modelzoo.core.model_card_html import render_html
from dx_modelzoo.core.model_card_image import example_image, webp_bytes
from dx_modelzoo.core.model_card_labels import clean_labels

SUPPORTED_LANGS = ("en", "ko", "ja", "es", "zh-CN", "zh-TW")


class DxAppMissing(Exception):
    """The dx_app checkout (its model registry) is not there; the server answers 503."""


class NoDxAppExample(Exception):
    """This model has no example in the dx_app registry; the server answers 404."""


def category_label(categories, category_id, lang="en"):
    if isinstance(categories, dict):
        info = categories.get(category_id) or {}
    else:
        info = next((c for c in categories or [] if isinstance(c, dict) and c.get("id") == category_id), {})
    return info.get(f"label_{lang}") or info.get("label_en") or info.get("label") or None


def studio_card(model, categories, payload, *, dx_app_root, data_dir, benchmark_path, asof=None):
    """→ (html, filename). NoDxAppExample when this model has no dx_app example, DxAppMissing without a dx_app
    checkout. asof: the catalog date, or None (the footer then leaves the date out)."""
    payload = payload if isinstance(payload, dict) else {}
    lang = payload.get("lang") if payload.get("lang") in SUPPORTED_LANGS else "en"
    variant = PurePosixPath(((model.get("demo") or {}).get("python_example") or "").rstrip("/")).name
    try:
        registry = load_registry(dx_app_root)
    except (OSError, ValueError) as exc:
        raise DxAppMissing(str(dx_app_root)) from exc
    row = registry.get(variant)
    if row is None:
        raise NoDxAppExample(variant or model.get("id"))
    task_label = payload.get("task_label")
    if not isinstance(task_label, str) or not 0 < len(task_label) <= 80:
        task_label = category_label(categories, model.get("category"), lang)
    # The same setup name as the dx_app card, so "Get the model" is the command setup.sh knows.
    setup_name = load_setup_names(dx_app_root)[1].get(PurePosixPath(row["dxnn_file"]).name)
    card = build_card(model, row, dx_app_root, benchmark_rows=load_benchmark(benchmark_path), setup_name=setup_name,
                      manifest_url=manifest_url_for(load_manifest_urls(dx_app_root), row),
                      task_label=task_label, asof=asof, lang=lang)
    image = example_image(model, data_dir)
    card["has_image"] = image is not None
    src = "data:image/webp;base64," + base64.b64encode(webp_bytes(image)).decode() if image else None
    html = render_html(card, labels=clean_labels(payload.get("labels")), lang=lang, image_src=src,
                       readme_href=None, other_href=None)
    return html, f"{variant}_modelcard.html"
