# SPDX-License-Identifier: Apache-2.0
"""Thin pytest wrapper over the showcase_repro evaluation harness — for CI gating.

OPT-IN and HEAVY: each test is a full autopilot agent run (minutes to hours). It is SKIPPED
unless ``DX_REPRO_RUN=1`` so the fast checker unit tests (``test_checks.py``) stay fast.

It does NOT reimplement anything — it reuses ``run_repro.run_cell`` (which applies the same
checks.py scoring + the B2 Output-Isolation guard + the portability gate) and the e2e conftest
autopilot runners. One test per (active showcase × agent); asserts the verdict is not FAILED.

Run:
    DX_REPRO_RUN=1 python -m pytest .deepx/e2e/showcase_repro/test_repro_scenarios.py -v
    DX_REPRO_RUN=1 DX_REPRO_AGENTS=claude-code python -m pytest ... -k mini-game
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from showcase_repro import run_repro
from showcase_repro.showcase_registry import active_showcases

_RUN = os.environ.get("DX_REPRO_RUN") == "1"
_AGENTS = [a.strip() for a in os.environ.get("DX_REPRO_AGENTS", "claude-code,cursor").split(",") if a.strip()]
_TIMEOUT = int(os.environ.get("DX_REPRO_TIMEOUT", "5400"))

pytestmark = pytest.mark.skipif(
    not _RUN, reason="heavy reproduction matrix — set DX_REPRO_RUN=1 to run"
)

_PARAMS = [(sc, ag) for sc in sorted(active_showcases()) for ag in _AGENTS]


@pytest.fixture(scope="session")
def _conftest():
    return run_repro._load_conftest()


@pytest.fixture(scope="session")
def _archive():
    base = Path(os.environ.get("DX_MODEL_EVAL_ARCHIVE",
                               str(Path.home() / "shared" / "coding_agent_diff_report")))
    d = base / "showcase_repro" / "pytest"
    d.mkdir(parents=True, exist_ok=True)
    return d


@pytest.mark.parametrize("showcase,agent", _PARAMS, ids=[f"{s}-{a}" for s, a in _PARAMS])
def test_showcase_reproduces(showcase, agent, _conftest, _archive):
    """The showcase prompt, re-run by the agent, must reproduce a non-FAILED result
    (self-contained + portable, scored by checks.py; source tree kept clean by the guard)."""
    cell = run_repro.run_cell(_conftest, agent, showcase, _TIMEOUT, _archive, dry_run=False)
    if cell.status == "BLOCKED":
        pytest.skip(f"{agent} unavailable (env): {cell.note}")
    assert cell.status != "FAILED", (
        f"{showcase} × {agent}: {cell.status} — {cell.note or cell.summary}"
    )
