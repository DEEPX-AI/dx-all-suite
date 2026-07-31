"""NPU product classification from dxrt-cli -s signals.

Single source of truth mapping per-device (Board, Memory) signals to canonical
DEEPX product names (H1-Quattro / M1 / M1M) as listed on deepx.ai/shop_now.
`dxrt-cli -s` reports the *chip* ("M1") on the Device line for every product, so
product type is inferred from Board prefix + Memory technology instead.
"""

from __future__ import annotations

import re

# (board_prefix, memory_substr | None, product, chips_per_card)
# Ordered: more specific memory match first (LPDDR5X before the LPDDR5 substring).
NPU_SIGNATURES: list[tuple[str, str | None, str, int]] = [
    ("H1",  None,       "H1-Quattro", 4),
    ("M.2", "LPDDR4",   "M1M",        1),
    ("M.2", "LPDDR5X",  "H1",         1),   # future standalone H1 M.2; matched before LPDDR5
    ("M.2", "LPDDR5",   "M1",         1),
]

UNKNOWN_PRODUCT = "unknown"


def classify_device(board: str | None, memory: str | None) -> tuple[str, int]:
    """Classify one NPU device. Returns (product, chips_per_card)."""
    b = (board or "").strip().upper()
    m = (memory or "").strip().upper()
    for prefix, mem, product, per_card in NPU_SIGNATURES:
        if b.startswith(prefix.upper()) and (mem is None or mem in m):
            return product, per_card
    return UNKNOWN_PRODUCT, 1


def classify_devices(devices: list[tuple[str | None, str | None]]) -> list[dict]:
    """Aggregate per-device signals into [{"product", "count"}], first-seen order.

    H1 chips fold into cards: count = chips // chips_per_card (>=1 if any chip seen).
    """
    chips: dict[str, int] = {}
    per_card: dict[str, int] = {}
    order: list[str] = []
    for board, memory in devices:
        product, cpc = classify_device(board, memory)
        if product not in chips:
            chips[product] = 0
            per_card[product] = cpc
            order.append(product)
        chips[product] += 1

    modules: list[dict] = []
    for product in order:
        cpc = per_card[product] or 1
        # NOTE: floor-division assumes fully-populated cards; a partial card
        # (e.g. 1-3 of 4 H1 chips reported) folds to count=1, not flagged here.
        # Cross-run/mixed-hardware anomalies are surfaced by the aggregator guard (Task 4).
        count = max(1, chips[product] // cpc) if cpc > 1 else chips[product]
        modules.append({"product": product, "count": count})
    return modules


def format_sku(modules: list[dict]) -> str:
    """Slug for folder/env id: 'M1', 'M1x2', mixed 'M1-M1M'."""
    parts = []
    for mod in modules:
        product = mod.get("product", UNKNOWN_PRODUCT)
        count = int(mod.get("count", 1) or 1)
        parts.append(product if count <= 1 else f"{product}x{count}")
    return "-".join(parts) if parts else UNKNOWN_PRODUCT


def format_badge(modules: list[dict]) -> str:
    """Human display: 'M1', 'M1 ×2', mixed 'M1 + M1M'."""
    parts = []
    for mod in modules:
        product = mod.get("product", UNKNOWN_PRODUCT)
        count = int(mod.get("count", 1) or 1)
        parts.append(product if count <= 1 else f"{product} ×{count}")
    return " + ".join(parts) if parts else UNKNOWN_PRODUCT


def classify_from_raw(raw: str) -> list[dict]:
    """Backfill path: parse per-device (Board, Memory) from dxrt-cli -s raw text."""
    devices: list[tuple[str | None, str | None]] = []
    board = memory = None
    started = False
    for line in raw.splitlines():
        s = line.strip()
        if s.startswith("* Device"):
            if started:
                devices.append((board, memory))
            board = memory = None
            started = True
        elif "Board" in s and ":" in s and "Chip" not in s:
            mm = re.search(r":\s*(.+)", s)
            if mm:
                board = mm.group(1).strip()
        elif "Memory" in s and ":" in s:
            mm = re.search(r":\s*(.+)", s)
            if mm:
                memory = mm.group(1).strip()
    if started:
        devices.append((board, memory))
    return classify_devices(devices)
