"""Which DEEPX products a model runs on — the one rule every catalog path uses.

Products (dxrt-cli -s): DX-M1 (0x0100), DX-M1M (0x0110, LPDDR4 1.92 GiB), DX-H1 Quattro (0x0101, 4 × M1 chips).
- Every model in the catalog is compiled for DX-M1.
- DX-H1 Quattro is four M1 chips with M1's memory and clock, so it runs whatever M1 runs (DXM1-1764).
- DX-M1M has less NPU memory; whether a model fits is recorded per model in dx-modelzoo YAML (DXM1-1775):
      target_hardware:
        m1:  {buffer_count: 6}
        m1m: {buffer_count: 1}          # present → runs on M1M
        # m1m absent, or {supported: false, reason: "..."} → does not
  Until a model's YAML carries `target_hardware`, its M1M status is "pending" — never guessed.
"""
from __future__ import annotations

M1, M1M, H1_QUATTRO = "dx_m1", "dx_m1m", "dx_h1_quattro"


def _supported(entry) -> bool:
    return not (isinstance(entry, dict) and entry.get("supported") is False)


def processor_info(target_hardware=None) -> dict:
    """Catalog `processor` block for a model's YAML `target_hardware` (None when the YAML has none)."""
    if not isinstance(target_hardware, dict) or not target_hardware:
        # "metadata_pending": the model's YAML has no hardware field yet — M1 / H1 Quattro follow the rule above,
        # M1M is not known.
        return {"supported_devices": [M1, H1_QUATTRO], "status": "metadata_pending",
                "m1m": {"status": "pending", "reason": None}}
    devices = []
    if "m1" in target_hardware and _supported(target_hardware.get("m1")):
        devices.append(M1)
    m1m = target_hardware.get("m1m")
    if "m1m" in target_hardware and _supported(m1m):
        devices.append(M1M)
        m1m_info = {"status": "supported", "reason": None}
    else:
        reason = m1m.get("reason") if isinstance(m1m, dict) else None
        m1m_info = {"status": "unsupported", "reason": str(reason) if reason else None}
    if M1 in devices:
        devices.append(H1_QUATTRO)
    return {"supported_devices": devices, "status": "provided", "m1m": m1m_info,
            "target_hardware": target_hardware}


def upgrade_processor(processor) -> dict:
    """A catalog entry's `processor` in the current shape. Old generated catalogs said ["dx_m1"] (a hardcode, not
    data) or [] — both mean "no hardware field yet"."""
    if isinstance(processor, dict) and isinstance(processor.get("m1m"), dict):
        return processor
    th = processor.get("target_hardware") if isinstance(processor, dict) else None
    return processor_info(th)
