"""NPU product classification from `dxrt-cli -s`.

Three signals per device, in order of authority:

1. **Board** -- the form factor: ``H1`` is the 4-chip H1-Quattro card, ``M.2`` a single-chip
   M.2 card.
2. **Chip** -- the name on the ``* Device N: <chip>`` line. Every product reports ``M1`` there
   (the H1 board is four M1 chips) except where the runtime names the card itself (``M1M``).
   A chip other than ``M1`` on an M.2 card therefore *is* the product.
3. **Memory** -- a description of the card, not its identity. The M1 M.2 card ships with
   LPDDR5 (5600 Mbps) and with LPDDR5x (6000 Mbps); only LPDDR4 marks the M1M, and only as a
   fallback for older runtimes that reported the M1M chip as "M1".

The per-device record (`parse_devices`) is stored in the fingerprint so the classification
can be audited and redone when this catalog changes.
"""

from __future__ import annotations

import re

# H1 board chips fold into one card; every other product is one chip per card.
H1_QUATTRO = "H1-Quattro"
CHIPS_PER_CARD = {H1_QUATTRO: 4}

UNKNOWN_PRODUCT = "unknown"

_DEVICE_RE = re.compile(r"\*\s*Device\s+(\d+)\s*:\s*([^,\s]+)")


def parse_devices(raw: str) -> list[dict]:
    """One record per ``* Device N`` block of dxrt-cli -s output.

    Each record has ``chip``, ``board``, ``memory``, ``chip_offset`` and ``pcie`` (None when
    the runtime does not print that line).
    """
    devices: list[dict] = []
    current: dict | None = None
    for line in raw.splitlines():
        s = line.strip()
        m = _DEVICE_RE.match(s)
        if m:
            current = {"chip": m.group(2), "board": None, "memory": None,
                       "chip_offset": None, "pcie": None}
            devices.append(current)
            continue
        if current is None or ":" not in s:
            continue
        value = s.split(":", 1)[1].strip()
        if "Chip Offset" in s:
            current["chip_offset"] = int(value) if value.isdigit() else None
        elif "Board" in s:
            current["board"] = value
        elif "Memory" in s:
            current["memory"] = value
        elif "PCIe" in s and "Gen" in s:
            current["pcie"] = value
    return devices


def classify_device(board: str | None, memory: str | None,
                    chip: str | None = None) -> tuple[str, int]:
    """Classify one NPU device. Returns (product, chips_per_card)."""
    b = (board or "").strip().upper()
    m = (memory or "").strip().upper()
    c = (chip or "").strip()
    if b.startswith("H1"):
        return H1_QUATTRO, CHIPS_PER_CARD[H1_QUATTRO]
    if b.startswith("M.2"):
        if c and c.upper() != "M1":
            return c, 1                    # the runtime names the card (M1M, a standalone H1, ...)
        if "LPDDR4" in m:
            return "M1M", 1                # older runtimes reported the M1M chip as "M1"
        return "M1", 1
    if c:
        return c, 1                        # unfamiliar board: the chip is the best identity we have
    return UNKNOWN_PRODUCT, 1


def classify_devices(devices: list[tuple]) -> list[dict]:
    """Aggregate per-device signals into [{"product", "count"}], first-seen order.

    Each signal is ``(board, memory)`` or ``(board, memory, chip)``.

    H1 chips fold into cards: count = chips // chips_per_card (>=1 if any chip seen).
    """
    chips: dict[str, int] = {}
    per_card: dict[str, int] = {}
    order: list[str] = []
    for signal in devices:
        board, memory, *rest = signal
        product, cpc = classify_device(board, memory, rest[0] if rest else None)
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
    """Classify from dxrt-cli -s raw text (backfill and aggregation path)."""
    return classify_devices([(d["board"], d["memory"], d["chip"]) for d in parse_devices(raw)])
