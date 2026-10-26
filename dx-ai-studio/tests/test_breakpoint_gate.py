"""Ratchet that keeps breakpoint fragmentation from growing.

Responsive layouts in the product switch at many unrelated widths (one screen folds at
900, another at 960, for no reason). Moving existing values onto the scale would change
layouts in those width ranges with no responsive baseline to check them, so this only
blocks new values.
"""
from __future__ import annotations

import json

from scripts.breakpoint_gate import BASELINE_PATH, SCALE, distinct, new_values, scan


def test_scale_is_ordered_and_distinct():
    assert list(SCALE) == sorted(set(SCALE))


def test_no_file_introduces_a_new_breakpoint():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    new = new_values(scan(), baseline)
    assert not new, (
        f"새 breakpoint 가 생겼다 — {SCALE} 중에서 고르거나 그 파일이 이미 "
        f"쓰는 값을 쓰세요: {new}"
    )


def test_scale_values_need_no_baseline_entry():
    """Scale values never add fragmentation, so they are allowed without a baseline entry —
    the failure message tells authors to pick from the scale, and that must actually pass."""
    assert new_values({"new.css": list(SCALE)}, {}) == {}


def test_values_off_the_scale_are_still_new():
    assert new_values({"new.css": [900, 1100]}, {}) == {"new.css": [1100]}
    # Values the file already used stay allowed even off the scale (moving them is a separate step)
    assert new_values({"old.css": [768, 1100]}, {"old.css": [768]}) == {"old.css": [1100]}


def test_breakpoint_baseline_has_no_stale_values():
    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    counts = scan()
    stale = {
        rel: [v for v in values if v not in set(counts.get(rel, []))]
        for rel, values in baseline.items()
    }
    stale = {rel: vals for rel, vals in stale.items() if vals}
    assert not stale, (
        "안 쓰는 breakpoint 가 baseline 에 남았다. "
        f"`python -m scripts.breakpoint_gate --write` 로 조인다: {stale}"
    )


def test_distinct_breakpoints_do_not_grow():
    assert len(distinct(scan())) <= 19
