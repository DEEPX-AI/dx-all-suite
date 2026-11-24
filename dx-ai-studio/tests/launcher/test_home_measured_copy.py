"""The Hub's "Measured on DX-M1" card shows DX Model Zoo figures (catalog performance.fps) — DEEPX's measurements
on DX-M1, not a run on this PC. Its tour step and the manual must not say "measured on this device"."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

STUDIO = Path(__file__).resolve().parents[2]
THIS_DEVICE = ("this device", "Measured here", "이 장치", "여기서 잰", "このデバイス", "ここで測った",
               "本设备", "在这里实测", "本裝置", "在這裡實測", "este dispositivo", "Medido aquí")


def _tour_step():
    text = (STUDIO / "launcher/static/tutorial.js").read_text(encoding="utf-8")
    m = re.search(r"\{ target: '#homeMeasured'.*?\} \},", text, re.S)
    assert m, "tour step for #homeMeasured not found"
    return m.group(0)


def test_tour_step_says_whose_measurement_it_is():
    step = _tour_step()
    for phrase in THIS_DEVICE:
        assert phrase not in step, phrase
    for lang_text in ("DEEPX", "DX-M1", "DX Model Zoo"):
        assert step.count(lang_text) >= 6, lang_text      # every language names the source


def test_hub_manual_does_not_claim_a_local_run():
    manual = STUDIO / "docs/source/02_The_Hub.md"
    if not manual.parent.is_dir():
        pytest.skip("manual not shipped in this checkout (read on developer.deepx.ai)")
    hub = manual.read_text(encoding="utf-8")
    line = next(l for l in hub.splitlines() if "**Measured on DX-M1**" in l)
    assert "this device" not in line and "DX Model Zoo" in line
