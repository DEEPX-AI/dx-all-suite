"""Spacing values off the 4px scale may only go down.

The tokens define seven steps: `--sp-1..7` = 4·8·12·16·24·32·48px. Raw px values in spacing declarations that
are not on that scale (6px, 10px, 14px and so on) are counted per file.

A 2px difference is invisible in one place. The problem is **when they stack**: 6px inside a card, 10px in the list
inside it and 14px in a badge inside that, and nothing lines up. Shared components matter most, since every module
that uses them inherits the drift.

So this works like the colour (css_token_gate) and breakpoint (breakpoint_gate) gates: **the current counts are the
ceiling and only an increase fails.** Reducing them is always allowed.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "scripts" / "spacing_scale_gate.py"
BASELINE = ROOT / "config" / "spacing_scale_baseline.json"


def test_the_gate_exists():
    assert GATE.is_file(), f"{GATE} 가 없다"


def test_the_baseline_exists():
    assert BASELINE.is_file(), f"{BASELINE} 가 없다"


def test_the_gate_passes_on_the_current_tree():
    r = subprocess.run([sys.executable, "-m", "scripts.spacing_scale_gate"],
                       cwd=ROOT, capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, f"게이트가 실패한다:\n{r.stdout}\n{r.stderr}"
    assert "스케일 밖" in r.stdout, f"요약을 출력하지 않는다: {r.stdout!r}"


def test_the_baseline_only_ratchets_down():
    """Raising the ceiling would defeat the gate, so the contract forbids it."""
    src = GATE.read_text(encoding="utf-8")
    assert ">" in src and "baseline" in src.lower()
    assert "새 간격" in src or "늘었다" in src, "늘어남을 막는 메시지가 없다"


def test_it_is_wired_into_run_ci():
    ci = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert "spacing_scale_gate" in ci, "run_ci.sh 가 이 게이트를 부르지 않는다"


def test_the_scale_follows_the_tokens(monkeypatch, tmp_path):
    """The scale is **read from the token file**, not written into the code.

    Checking that the source mentions 'dx-tokens.css' is not enough: a hard-coded copy of the scale would pass
    because the values happen to match. Change the tokens and check that the gate **follows**.
    """
    sys.path.insert(0, str(ROOT))
    from scripts import spacing_scale_gate as gate

    real = gate.TOKENS.read_text(encoding="utf-8")
    fake = tmp_path / "dx-tokens.css"
    # Switch the scale to multiples of 5, which share no value with the real one.
    fake.write_text("--sp-1:5px;--sp-2:10px;--sp-3:15px;", encoding="utf-8")
    monkeypatch.setattr(gate, "TOKENS", fake)
    assert gate.scale() == {5, 10, 15}, (
        f"토큰을 바꿨는데 스케일이 따라오지 않는다: {gate.scale()}")
    assert "px" in real  # the real file was being read


def test_a_new_off_scale_value_is_rejected(tmp_path):
    """The gate actually bites: lower the baseline so one file goes over it."""
    baseline = json.loads(BASELINE.read_text(encoding="utf-8"))
    worst = max(baseline, key=lambda k: baseline[k])
    assert baseline[worst] > 0, "스케일 밖이 하나도 없다면 이 검사는 무의미하다"
    tight = dict(baseline)
    tight[worst] = baseline[worst] - 1
    backup = BASELINE.read_text(encoding="utf-8")
    try:
        BASELINE.write_text(json.dumps(tight, indent=2), encoding="utf-8")
        r = subprocess.run([sys.executable, "-m", "scripts.spacing_scale_gate"],
                           cwd=ROOT, capture_output=True, text=True, timeout=180)
        assert r.returncode == 1, "상한을 넘겼는데 통과했다"
        assert worst in r.stdout, f"어느 파일인지 말하지 않는다: {r.stdout!r}"
    finally:
        BASELINE.write_text(backup, encoding="utf-8")
