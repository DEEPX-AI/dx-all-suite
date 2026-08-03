#!/usr/bin/env python3
"""Bake the ModelZoo public catalog to a local JSON snapshot for OFFLINE use.

ModelZoo's live listing is a network fetch (developer.deepx.ai). On an air-gapped /
closed-network install that call times out, so the App > Models page (get_catalog) would
collapse to almost nothing. Run this script ONLINE at release time to freeze today's full
catalog into ``modelzoo_catalog_public.json`` next to this file; get_catalog() reads that
snapshot first and only falls back to the live listing when the snapshot is absent.

Usage (from the studio root, online):
    PYTHONPATH=. python3 dx_app/scripts/bake_modelzoo_catalog.py
"""
import json
import sys
from pathlib import Path

from dx_app.core.modelzoo_gateway import ModelZooGateway  # noqa: E402

OUT = Path(__file__).resolve().parent / "modelzoo_catalog_public.json"


def main() -> int:
    r = ModelZooGateway().list_models("public")
    models = (r.get("models") if isinstance(r, dict) else r) or []
    if not models:
        print("ERROR: live ModelZoo listing returned no models — are you online?", file=sys.stderr)
        return 1
    OUT.write_text(json.dumps(r, ensure_ascii=False), encoding="utf-8")
    print(f"baked {len(models)} models -> {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
