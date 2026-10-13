"""Model card for Studio's "Save as HTML": the same renderer, labels translated by the page.

Contract: tests/dx_modelzoo/test_model_card_endpoint.py
"""
from __future__ import annotations


def category_label(categories, category_id, lang="en"):
    if isinstance(categories, dict):
        info = categories.get(category_id) or {}
    else:
        info = next((c for c in categories or [] if isinstance(c, dict) and c.get("id") == category_id), {})
    return info.get(f"label_{lang}") or info.get("label_en") or info.get("label") or None
