"""Result layout helpers for nested benchmark results directories."""

from __future__ import annotations

import re
from pathlib import Path

from .npu_catalog import classify_from_raw, format_sku, UNKNOWN_PRODUCT


def _get_sku(npu: dict) -> str:
    """Resolve product SKU: stamped sku > modules > raw backfill > device_count guess."""
    sku = npu.get("sku")
    if sku and sku != UNKNOWN_PRODUCT:
        return str(sku)
    modules = npu.get("modules")
    if modules:
        s = format_sku(modules)
        if s != UNKNOWN_PRODUCT:
            return s
    raw = npu.get("raw")
    if isinstance(raw, str) and raw:
        s = format_sku(classify_from_raw(raw))
        if s != UNKNOWN_PRODUCT:
            return s
    dc = int(npu.get("device_count", 0) or 0)
    if dc >= 1:
        return format_sku([{"product": "M1", "count": dc}])
    return UNKNOWN_PRODUCT


def make_hw_id(fingerprint: dict) -> str:
    """Generate the write-time folder name: {product_name|hostname}_{sku}.

    Runtime env identity is the folder name itself (see aggregator); this is only
    used to auto-name a *new* run directory.
    """
    host = fingerprint.get("host", {})
    npu = fingerprint.get("npu", {})
    name = fingerprint.get("product_name") or host.get("hostname", "unknown")
    raw = f"{name}_{_get_sku(npu)}"
    raw = raw.replace(" ", "_")                    # spaces → underscore
    # Allow the filesystem- and shell-safe chars common in product names
    # (e.g. RPi5+, ROCK5B+, DX-AIPlayer-N97); map everything else to "_".
    raw = re.sub(r"[^A-Za-z0-9._+-]", "_", raw)
    return re.sub(r"_+", "_", raw).strip("_")


def iter_result_dirs(root: Path) -> list[Path]:
    """Return nested run directories under results/{hw_id}/{run_id}."""
    if not root.is_dir():
        return []

    flat_dirs: list[Path] = []
    run_dirs: list[Path] = []
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name == "dashboard":
            continue
        if (child / "environment.json").exists():
            flat_dirs.append(child)
            continue
        for grandchild in sorted(child.iterdir()):
            if grandchild.is_dir() and (grandchild / "environment.json").exists():
                run_dirs.append(grandchild)

    if flat_dirs:
        sample = ", ".join(path.name for path in flat_dirs[:3])
        raise ValueError(
            f"Flat result layout is no longer supported: {sample}. "
            "Expected results/{hw_id}/{run_id}."
        )

    return run_dirs