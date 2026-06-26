#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Showcase reproducibility driver.

Feeds each ACTIVE showcase's verbatim end-user prompt to one or more autopilot
coding agents (claude-code, cursor), scores the produced output dir with
showcase_repro.checks, and emits a cross-agent comparison report.

Reuses the existing autopilot runner classes from the e2e conftest — it does NOT
reimplement subprocess/session-detection logic.

Per the design decision: the prompt is the SOLE input. We do not pre-run
sanity_check / install / env setup on the agent's behalf — whether the agent
resolves prereqs inside the run is itself under test.

Usage:
    python run_repro.py --dry-run                      # show the matrix, run nothing
    python run_repro.py                                # all active showcases x [claude-code,cursor]
    python run_repro.py --agents claude-code           # single agent
    python run_repro.py --showcases mini-game-squat-fitness
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# --------------------------------------------------------------------------- #
# Path bootstrap — make `showcase_repro` importable + load the e2e conftest
# --------------------------------------------------------------------------- #
E2E_DIR = Path(__file__).resolve().parents[1]          # .deepx/e2e
SUITE_ROOT = Path(__file__).resolve().parents[3]       # repo root
SCEN_DIR = E2E_DIR / "test_agent_e2e_scenarios"
for _p in (str(E2E_DIR), str(SCEN_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from showcase_repro.checks import ShowcaseResult, evaluate_showcase  # noqa: E402
from showcase_repro.isolation import isolation_violations  # noqa: E402
from showcase_repro.showcase_registry import SHOWCASES, active_showcases  # noqa: E402

# B3 — Output-Isolation reminder appended to every run prompt (the conftest runner
# already appends an autopilot directive; this restates the HARD GATE for agents like
# cursor that otherwise build into a source dir an input path points into).
ISOLATION_DIRECTIVE = (
    " IMPORTANT — Output Isolation + Self-Contained HARD GATE: write ALL generated files "
    "under a NEW dx-agent-dev/<session_id>/ directory in the routed sub-project. NEVER write "
    "into an existing source directory (e.g. dx-agent-dev-showcase/...), even if an input path "
    "points inside one — read inputs from there, but create your app elsewhere. If you reuse a "
    "vendored pipeline (e.g. an engine/ package), you MUST COPY it INTO the session with "
    "`cp -r` — do NOT symlink a source dir and do NOT set a model/download dir THROUGH such a "
    "symlink (model_files written through a symlinked engine/ land in the source = a violation). "
    "Keep every code/model path session-relative ($SCRIPT_DIR/APP_DIR); the app MUST run when "
    "copied OUTSIDE the suite."
)


def _git_status(repo_root: Path) -> str:
    try:
        return subprocess.run(
            ["git", "status", "--porcelain"], cwd=repo_root,
            capture_output=True, text=True, timeout=60,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


_DXDEV_ROOTS = ("dx-runtime/dx_app/dx-agent-dev", "dx-runtime/dx_stream/dx-agent-dev",
                "dx-compiler/dx-agent-dev")


def _recent_session_dirs(t0: float) -> List[Path]:
    """All dx-agent-dev/<session> dirs created/updated since t0 (this cell's window). Cells run
    sequentially, so this recovers a cell's dir(s) even when the agent mislabels the session id
    with another agent's name (the conftest cursor detector then returns no output_dir), and
    surfaces BOTH dirs of a cross-project (compiler + app) run for union scoring."""
    found = []
    for rel in _DXDEV_ROOTS:
        base = SUITE_ROOT / rel
        if not base.is_dir():
            continue
        for d in base.iterdir():
            try:
                if d.is_dir() and d.stat().st_mtime >= t0 - 5:
                    found.append(d)
            except OSError:
                pass
    found.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    return found


def _revert_paths(repo_root: Path, paths: List[str]) -> None:
    """Restore tracked pollution to HEAD; delete untracked pollution."""
    for p in paths:
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", p], cwd=repo_root,
            capture_output=True,
        ).returncode == 0
        if tracked:
            subprocess.run(["git", "checkout", "HEAD", "--", p], cwd=repo_root,
                           capture_output=True)
        else:
            full = repo_root / p
            if full.is_dir():
                shutil.rmtree(full, ignore_errors=True)
            elif full.exists():
                try:
                    full.unlink()
                except OSError:
                    pass


def _load_conftest():
    spec = importlib.util.spec_from_file_location("e2e_conftest", SCEN_DIR / "conftest.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["e2e_conftest"] = mod
    spec.loader.exec_module(mod)
    return mod


def _default_archive() -> Path:
    env = os.environ.get("DX_MODEL_EVAL_ARCHIVE")
    base = Path(env) if env else (Path.home() / "shared" / "coding_agent_diff_report")
    return base / "showcase_repro"


# --------------------------------------------------------------------------- #
# Result record (one matrix cell)
# --------------------------------------------------------------------------- #
@dataclass
class CellResult:
    showcase: str
    agent: str
    status: str                       # EQUIVALENT|DEGRADED|FAILED|BLOCKED
    output_dir: Optional[str] = None
    duration_seconds: float = 0.0
    model_used: Optional[str] = None
    returncode: Optional[int] = None
    summary: str = ""
    note: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)


AGENT_RUNNERS = {
    "claude-code": "ClaudeCodeRunnerAutopilot",
    "cursor": "CursorRunnerAutopilot",
}


def run_cell(conftest, agent: str, showcase: str, timeout: int, archive: Path,
             dry_run: bool) -> CellResult:
    spec = SHOWCASES[showcase]
    runner_cls = getattr(conftest, AGENT_RUNNERS[agent])

    if dry_run:
        return CellResult(showcase, agent, "DRY", note=(
            f"would run: workdir={SUITE_ROOT} scenario_key={spec.scenario_key} "
            f"timeout={timeout}s prompt={spec.prompt[:60]!r}..."))

    # env/auth preflight — BLOCKED(env) is NOT a reproducibility failure
    if not runner_cls.is_available():
        return CellResult(showcase, agent, "BLOCKED", note=f"{agent} CLI not on PATH")
    try:
        if not runner_cls.is_authenticated():
            return CellResult(showcase, agent, "BLOCKED", note=f"{agent} CLI not authenticated")
    except Exception as e:  # auth probe best-effort
        return CellResult(showcase, agent, "BLOCKED", note=f"{agent} auth probe error: {e}")

    log_dir = archive / "runs" / f"{showcase}__{agent}"
    log_dir.mkdir(parents=True, exist_ok=True)
    runner = runner_cls()
    before_status = _git_status(SUITE_ROOT)          # B2: pre-run snapshot
    t0 = time.time()                                  # for the session-dir recovery fallback
    result = runner.run(
        prompt=spec.prompt + ISOLATION_DIRECTIVE,     # B3: isolation reminder
        workdir=SUITE_ROOT,
        scenario_key=spec.scenario_key,
        session_log_dir=log_dir,
        timeout=timeout,
    )

    # B2: Output-Isolation guard — did the run write into a source dir (not dx-agent-dev/)?
    violations = isolation_violations(before_status, _git_status(SUITE_ROOT))
    if violations:
        _revert_paths(SUITE_ROOT, violations)
        shown = ", ".join(violations[:6]) + (" …" if len(violations) > 6 else "")
        return CellResult(
            showcase, agent, "FAILED",
            duration_seconds=result.duration_seconds, model_used=result.model_used,
            returncode=result.returncode,
            note=(f"Output Isolation violation: wrote into source dir(s) instead of "
                  f"dx-agent-dev/<session>/ [{shown}] — reverted to HEAD"))

    # Union of the cell's dirs: the conftest-detected ones PLUS any session dir created in this
    # cell's window (recovers mislabeled cursor dirs; surfaces both dirs of a cross-project run).
    seen, all_dirs = set(), []
    for d in list(result.output_dirs or []) + _recent_session_dirs(t0):
        rp = Path(d).resolve()
        if rp not in seen:
            seen.add(rp)
            all_dirs.append(Path(d))
    if not all_dirs:
        return CellResult(showcase, agent, "FAILED",
                          duration_seconds=result.duration_seconds,
                          model_used=result.model_used, returncode=result.returncode,
                          note="agent produced no dx-agent-dev/<session> output dir")

    primary = Path(result.output_dir) if result.output_dir else all_dirs[0]
    extra = [d for d in all_dirs if d.resolve() != primary.resolve()]
    recovered = result.output_dir is None
    try:
        ev: ShowcaseResult = evaluate_showcase(showcase, primary, extra_dirs=extra)
        verdict, summary = ev.verdict, ev.summary()
    except Exception as e:  # a scoring bug must NOT abort the whole matrix run
        verdict, summary = "ERROR", f"checker raised {type(e).__name__}: {e}"
    note = ""
    if recovered:
        note = f"output_dir recovered via mtime fallback ({len(all_dirs)} dir(s) — agent likely mislabeled the session id)"
    elif extra:
        note = f"scored union of {len(all_dirs)} dirs (cross-project: compiler + app)"
    return CellResult(
        showcase=showcase, agent=agent, status=verdict,
        output_dir=" + ".join(str(d) for d in all_dirs),
        duration_seconds=result.duration_seconds,
        model_used=result.model_used, returncode=result.returncode,
        summary=summary, note=note,
    )


# --------------------------------------------------------------------------- #
# Report
# --------------------------------------------------------------------------- #
def render_report(cells: List[CellResult], agents: List[str], showcases: List[str]) -> str:
    lines = ["# Showcase Reproducibility — Cross-Agent Report", ""]
    lines.append("Verdict per (showcase × agent). Target = the checked-in showcase "
                 "ground truth. EQUIVALENT = artifacts+gates+metrics all within tolerance.")
    lines.append("")
    header = "| showcase | " + " | ".join(agents) + " |"
    sep = "|" + "---|" * (len(agents) + 1)
    lines += [header, sep]
    by = {(c.showcase, c.agent): c for c in cells}
    for sc in showcases:
        row = [sc]
        for ag in agents:
            c = by.get((sc, ag))
            row.append(c.status if c else "—")
        lines.append("| " + " | ".join(row) + " |")
    lines += ["", "## Detail", ""]
    for c in cells:
        lines.append(f"### {c.showcase} — {c.agent}: **{c.status}**")
        if c.output_dir:
            lines.append(f"- output: `{c.output_dir}`")
        if c.model_used:
            lines.append(f"- model: `{c.model_used}`  · duration: {c.duration_seconds:.0f}s  · rc: {c.returncode}")
        if c.summary:
            lines.append(f"- tiers: {c.summary}")
        if c.note:
            lines.append(f"- note: {c.note}")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--agents", default="claude-code,cursor",
                    help="comma list: claude-code,cursor")
    ap.add_argument("--showcases", default="",
                    help="comma list; default = all ACTIVE showcases")
    ap.add_argument("--timeout", type=int, default=7200, help="per-run timeout seconds")
    ap.add_argument("--archive", default=str(_default_archive()),
                    help="durable archive root for reports + run logs")
    ap.add_argument("--dry-run", action="store_true", help="print matrix, execute nothing")
    args = ap.parse_args()

    agents = [a.strip() for a in args.agents.split(",") if a.strip()]
    for a in agents:
        if a not in AGENT_RUNNERS:
            print(f"ERROR: unknown agent '{a}' (supported: {list(AGENT_RUNNERS)})", file=sys.stderr)
            return 2
    showcases = ([s.strip() for s in args.showcases.split(",") if s.strip()]
                 or list(active_showcases().keys()))
    for s in showcases:
        if s not in SHOWCASES:
            print(f"ERROR: unknown showcase '{s}'", file=sys.stderr)
            return 2

    archive = Path(args.archive)
    archive.mkdir(parents=True, exist_ok=True)
    conftest = _load_conftest()

    print(f"[repro] suite_root={SUITE_ROOT}")
    print(f"[repro] agents={agents} showcases={showcases}")
    print(f"[repro] archive={archive}  dry_run={args.dry_run}")

    cells: List[CellResult] = []
    for sc in showcases:
        for ag in agents:
            print(f"[repro] ── {sc} × {ag} ──")
            cell = run_cell(conftest, ag, sc, args.timeout, archive, args.dry_run)
            print(f"[repro]    -> {cell.status}  {cell.note or cell.summary}")
            cells.append(cell)

    report = render_report(cells, agents, showcases)
    if args.dry_run:
        # dry-run is side-effect-free — never clobber a finalized archive report
        print("\n[repro] (dry-run) not writing report.md/results.json\n")
        print(report)
        return 0
    (archive / "report.md").write_text(report)
    (archive / "results.json").write_text(json.dumps([c.to_dict() for c in cells], indent=2))
    print(f"\n[repro] report  -> {archive/'report.md'}")
    print(f"[repro] results -> {archive/'results.json'}")
    print("\n" + report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
