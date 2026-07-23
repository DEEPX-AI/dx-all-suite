"""UX visual gate — fail CI when Phase 2 tutorial spotlight audit reports P0 defects."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PHASE2_DIR = ROOT / "dx-agent-dev" / "20260625-094846_cursor_gpt55_tutorial_audit"
PHASE2_SCRIPT = PHASE2_DIR / "run_phase2_visual_audit.py"
PHASE2_JSONL = PHASE2_DIR / "phase2-results.jsonl"
P0_KINDS = frozenset(
    {
        "FLOATING_FALLBACK",
        "TARGET_MISSING",
        "TARGET_HIDDEN",
        "NO_SPOTLIGHT",
        "NO_OVERLAY",
        "CONSOLE_WARN",
    }
)


def _load_phase2_module():
    spec = importlib.util.spec_from_file_location("phase2_visual_audit", PHASE2_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = mod
    sys.path.insert(0, str(ROOT))
    spec.loader.exec_module(mod)
    return mod


def test_phase2_visual_audit_zero_p0_defects():
    """Phase 2 full matrix must have zero P0 spotlight/tooltip defects."""
    pytest.importorskip("playwright.sync_api")
    if not PHASE2_SCRIPT.is_file():
        pytest.skip("phase2 audit script missing")

    mod = _load_phase2_module()
    has_shards = any(PHASE2_DIR.glob("phase2-results-*.jsonl"))
    if has_shards or (PHASE2_JSONL.is_file() and PHASE2_JSONL.stat().st_size > 0):
        if has_shards:
            mod._merge_jsonl()
        stats = mod.load_stats_from_jsonl()
    else:
        stats = mod.run_audit(parallel=4, only=None, wipe_all=True)
        mod._merge_jsonl()
        stats = mod.load_stats_from_jsonl()
    mod.write_report(stats)

    p0 = [d for d in stats.defects if d.kind in P0_KINDS]
    if p0:
        sample = p0[:12]
        lines = [
            f"Phase2 P0 defects: {len(p0)} (unique fingerprints in report)",
            f"Report: {PHASE2_DIR / 'phase2-visual-defect-report.md'}",
        ]
        for d in sample:
            lines.append(
                f"  - {d.module}/{d.section} step {d.step} {d.kind} "
                f"lang={d.lang} {d.detail}"
            )
        pytest.fail("\n".join(lines))

    assert stats.steps > 1000, f"expected large step matrix, got {stats.steps}"


def test_phase2_results_jsonl_well_formed_when_present():
    if not PHASE2_JSONL.is_file():
        pytest.skip("phase2-results.jsonl not generated yet")
    lines = [ln for ln in PHASE2_JSONL.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert lines, "phase2-results.jsonl empty"
    for ln in lines[:5]:
        rec = json.loads(ln)
        assert "module" in rec and "metrics" in rec
