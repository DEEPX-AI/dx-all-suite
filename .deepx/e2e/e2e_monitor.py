#!/usr/bin/env python3
"""
e2e_monitor.py — Live TUI monitor for E2E runner progress.

Reads state.json from the latest (or specified) run and displays:
  - Per-tool round progress table
  - Optional in-progress tool log tails
  - Optional per-scenario timing for a focused tool

Usage:
    python .deepx/e2e/e2e_monitor.py
    python .deepx/e2e/e2e_monitor.py --run-id 20260521_100000
    python .deepx/e2e/e2e_monitor.py --tool all
    python .deepx/e2e/e2e_monitor.py --tool claude-code --tail 30
    python .deepx/e2e/e2e_monitor.py --list
    python .deepx/e2e/e2e_monitor.py --once
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

try:
    from rich.columns import Columns
    from rich.console import Console, Group
    from rich.live import Live
    from rich.panel import Panel
    from rich.table import Table
    from rich.text import Text

    _RICH = True
except ImportError:
    _RICH = False

# ---------------------------------------------------------------------------
# Paths (mirrored from e2e_runner.py)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = (SCRIPT_DIR / "../..").resolve()
RUNNER_STATE_DIR = SCRIPT_DIR / "runner_state"

ALL_TOOLS: List[str] = [
    "claude-code",
    "copilot-cli",
    "cursor-cli",
    "opencode-cli",
    "codex-cli",
]

# Scenario keys — order matches test.sh execution order
SCENARIO_KEYS: List[str] = ["compiler", "dx_app", "dx_stream", "cascaded", "runtime", "suite"]

# Map scenario key to the substring that appears in test file paths
SCENARIO_FILE_PATTERNS: Dict[str, str] = {
    "compiler": "_compiler_",
    "dx_app": "_dx_app_",
    "dx_stream": "_dx_stream_agent",  # not cascaded
    "cascaded": "_dx_stream_cascaded",
    "runtime": "_runtime_",
    "suite": "_suite_",
}

TIMESTAMP_RE = re.compile(r"^\[(\d{2}:\d{2}:\d{2})\]")


# ---------------------------------------------------------------------------
# e2e_runner import (for round-validity classification reuse)
# ---------------------------------------------------------------------------
#
# We reuse e2e_runner._classify_round_scenario / _analyze_round_env so the
# monitor and the runner agree on what "valid" / "env-failed" / "incomplete"
# mean. Import by file path via importlib (memoized at module load) and guard
# the whole thing so the monitor still works if the import fails.


def _import_e2e_runner():
    """Import e2e_runner.py (same dir) by file path; return module or None."""
    try:
        import importlib.util

        runner_path = SCRIPT_DIR / "e2e_runner.py"
        if not runner_path.exists():
            return None
        spec = importlib.util.spec_from_file_location("_e2e_runner_for_monitor", runner_path)
        if spec is None or spec.loader is None:
            return None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception:
        return None


_E2E_RUNNER = _import_e2e_runner()


def _analyze_round_env(round_dir: Path):
    """Delegate to e2e_runner._analyze_round_env; fall back to a neutral tuple.

    Returns (valid, incomplete, envfail, total, sigs).
    """
    if _E2E_RUNNER is not None and hasattr(_E2E_RUNNER, "_analyze_round_env"):
        try:
            return _E2E_RUNNER._analyze_round_env(round_dir)
        except Exception:
            pass
    return (0, 0, 0, 0, set())


# ---------------------------------------------------------------------------
# Salvage helpers
# ---------------------------------------------------------------------------


def _pid_alive(pid: Optional[int]) -> bool:
    """Return True if *pid* is a live process (send signal 0)."""
    if not pid:
        return False
    try:
        os.kill(int(pid), 0)
    except (OSError, ValueError, TypeError):
        return False
    return True


def _load_salvage(run_id: str) -> Optional[dict]:
    """Load RUNNER_STATE_DIR/<run_id>/salvage.json; return None on any error."""
    try:
        p = RUNNER_STATE_DIR / run_id / "salvage.json"
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _format_salvage(salvage: dict, pid_alive: bool) -> str:
    """Format a one-line salvage status string for display.

    Args:
        salvage: Contents of salvage.json.
        pid_alive: Whether the salvage process is still running.

    Returns:
        A human-readable line such as:
        "Salvage: round 20260612_215200_... scenarios=[runtime,suite] status=running (attempt 2) pid=12345 [LIVE]"
    """
    status = salvage.get("status", "unknown")
    attempt = salvage.get("attempt", "?")
    pid = salvage.get("pid")
    round_dir = salvage.get("round_dir", "?")
    scenarios = salvage.get("scenarios", [])
    scenarios_str = ",".join(scenarios) if isinstance(scenarios, list) else str(scenarios)

    pid_part = f" pid={pid}" if pid else ""

    if status == "running":
        if pid_alive:
            liveness = "[LIVE]"
        else:
            liveness = "[stale — pid dead]"
        return (
            f"Salvage: round {round_dir} scenarios=[{scenarios_str}] "
            f"status=running (attempt {attempt}){pid_part} {liveness}"
        )
    elif status == "complete":
        return (
            f"Salvage: round {round_dir} scenarios=[{scenarios_str}] "
            f"status=complete (attempt {attempt}){pid_part}"
        )
    elif status == "max-attempts":
        return (
            f"Salvage: round {round_dir} scenarios=[{scenarios_str}] "
            f"status=max-attempts (exhausted){pid_part}"
        )
    else:
        return (
            f"Salvage: round {round_dir} scenarios=[{scenarios_str}] "
            f"status={status}{pid_part}"
        )


# ---------------------------------------------------------------------------
# Per-scenario classification (round-dir scenario subdirs)
# ---------------------------------------------------------------------------
#
# These are the CANONICAL round-dir scenario keys — the names that appear as
# ``claude_code__<scenario>`` subdirs inside a round results dir. They are
# DISTINCT from SCENARIO_KEYS above (which drives log-tail scenario timing and
# uses the short "cascaded" form). Order is the test.sh execution order.

ROUND_SCENARIO_KEYS: List[str] = [
    "compiler",
    "dx_app",
    "dx_stream",
    "dx_stream_cascaded",
    "runtime",
    "suite",
]

# Compact abbreviations for per-scenario display, in canonical order.
SCENARIO_ABBREV: Dict[str, str] = {
    "compiler": "cmp",
    "dx_app": "app",
    "dx_stream": "str",
    "dx_stream_cascaded": "csc",
    "runtime": "rt",
    "suite": "ste",
}

# Per-scenario verdict → icon. Verdicts come from
# e2e_runner._classify_round_scenario (valid / incomplete / envfail / skip);
# "re-running" is a display-only verdict injected for active salvage targets.
SCENARIO_ICON: Dict[str, str] = {
    "valid": "✓",
    "envfail": "✗",
    "incomplete": "△",
    "re-running": "⟳",
    "skip": "·",
}


def _classify_round_scenario(scen_dir: Path) -> str:
    """Classify one scenario subdir via e2e_runner; "skip" on any failure.

    Returns one of "valid" / "incomplete" / "envfail" / "skip". Delegates to
    e2e_runner._classify_round_scenario so the monitor and runner agree on what
    each verdict means; falls back to "skip" if the runner import is missing or
    raises (so the monitor never crashes on an odd scenario dir).
    """
    if _E2E_RUNNER is not None and hasattr(_E2E_RUNNER, "_classify_round_scenario"):
        try:
            verdict, _sigs = _E2E_RUNNER._classify_round_scenario(scen_dir)
            return verdict
        except Exception:
            return "skip"
    return "skip"


def _round_scenarios(round_dir: Path) -> Dict[str, str]:
    """Classify every canonical scenario subdir of *round_dir*.

    PURE (filesystem read only). For each of the 6 canonical scenario keys,
    classify ``round_dir/claude_code__<scenario>`` — a missing subdir maps to
    "skip". Returns ``{scenario_key: verdict}`` covering all 6 keys.
    """
    result: Dict[str, str] = {}
    for key in ROUND_SCENARIO_KEYS:
        scen_dir = round_dir / f"claude_code__{key}"
        if scen_dir.is_dir():
            result[key] = _classify_round_scenario(scen_dir)
        else:
            result[key] = "skip"
    return result


def _scenario_cells(scenarios: Dict[str, str],
                    rerun_targets: Optional[set] = None) -> str:
    """Render a compact per-scenario string in canonical order.

    PURE. Produces e.g. ``"cmp✓ app✓ str✓ csc✓ rt✗ ste✗"`` using the
    abbreviation + verdict icon for each of the 6 canonical scenario keys.
    A scenario in *rerun_targets* (the active salvage's target scenarios) shows
    the re-running icon (⟳) ONLY when it is not already valid on disk; a target
    that has already completed (merged back, verdict ``valid``) shows ✓. This
    matches the Round Progress current-round detail — a salvage that targets all
    6 scenarios but has only `suite` left renders ``cmp✓ … rt✓ ste⟳`` (not all ⟳).
    """
    targets = rerun_targets or set()
    cells: List[str] = []
    for key in ROUND_SCENARIO_KEYS:
        abbr = SCENARIO_ABBREV[key]
        on_disk = scenarios.get(key, "skip")
        if key in targets and on_disk != "valid":
            verdict = "re-running"  # being re-run, not yet completed
        else:
            verdict = on_disk       # valid target → ✓; non-target → its verdict
        icon = SCENARIO_ICON.get(verdict, "?")
        cells.append(f"{abbr}{icon}")
    return " ".join(cells)


# ---------------------------------------------------------------------------
# Per-round validity (salvage-aware)
# ---------------------------------------------------------------------------


def _round_status(round_dir: Path, salvage: Optional[dict], salvage_pid_alive: bool) -> dict:
    """Classify a single round dir's validity, salvage-aware.

    Args:
        round_dir: the per-round results dir (``*_<tool>-autopilot``).
        salvage: contents of salvage.json (or None).
        salvage_pid_alive: whether the salvage process PID is live.

    Returns a dict:
        {"round_dir": <name>, "status": <STATUS>, "detail": <str>,
         "counts": (valid, incomplete, envfail, total)}

    STATUS is one of: "re-running", "valid", "env-failed", "incomplete", "empty".

    A round that matches an ACTIVE salvage marker (status=running, pid alive,
    round_dir matches) is reported as "re-running" WITHOUT classification —
    its scenarios are mid-cleanup and would mis-classify; we trust the marker.
    """
    name = round_dir.name

    # Per-scenario breakdown — always attached so the Scenarios column can be
    # rendered for every round regardless of overall verdict.
    scenarios = _round_scenarios(round_dir)

    # Active-salvage short-circuit: do not classify a round being re-run.
    if (
        salvage is not None
        and salvage.get("status") == "running"
        and salvage_pid_alive
        and salvage.get("round_dir") == name
    ):
        attempt = salvage.get("attempt", "?")
        targets = salvage.get("scenarios", [])
        targets_str = ",".join(targets) if isinstance(targets, list) else str(targets)
        return {
            "round_dir": name,
            "status": "re-running",
            "detail": f"attempt {attempt}, scenarios={targets_str}",
            "counts": (0, 0, 0, 0),
            "scenarios": scenarios,
            "rerun_targets": set(targets) if isinstance(targets, list) else set(),
        }

    valid, incomplete, envfail, total, sigs = _analyze_round_env(round_dir)
    counts = (valid, incomplete, envfail, total)

    if total > 0 and envfail == 0 and incomplete == 0:
        return {"round_dir": name, "status": "valid", "detail": "valid",
                "counts": counts, "scenarios": scenarios}

    if envfail > 0:
        sig_str = ",".join(sorted(sigs)) if sigs else "env"
        return {
            "round_dir": name,
            "status": "env-failed",
            "detail": f"{sig_str} — pending re-run",
            "counts": counts,
            "scenarios": scenarios,
        }

    if incomplete > 0:
        return {
            "round_dir": name,
            "status": "incomplete",
            "detail": f"{incomplete} incomplete scenario(s)",
            "counts": counts,
            "scenarios": scenarios,
        }

    return {"round_dir": name, "status": "empty", "detail": "no scenarios",
            "counts": counts, "scenarios": scenarios}


def _run_round_statuses(run_results_dir: Path, salvage: Optional[dict],
                        state: Optional[dict] = None) -> List[dict]:
    """Classify a run's CANONICAL rounds, in chronological order.

    Prefers the rounds recorded in ``state.json`` (``tool_states[*].completed``
    ``result_dir_name``) so that transient salvage scratch dirs (a cleanup_resume
    re-run writes a fresh ``*-autopilot`` dir that is later merged back + removed)
    do NOT appear as phantom extra rounds. Falls back to globbing ``*-autopilot``
    dirs when no state is available. Assigns a 1-based round_index, classifies each.
    """
    statuses: List[dict] = []
    if not run_results_dir.is_dir():
        return statuses

    salvage_pid_alive = _pid_alive(salvage.get("pid")) if salvage else False

    # Canonical round dir names from state (excludes transient salvage scratch dirs).
    round_dir_names: List[str] = []
    if state:
        seen = set()
        entries = []
        for ts in (state.get("tool_states") or {}).values():
            for c in ts.get("completed", []):
                rdn = c.get("result_dir_name")
                if rdn and rdn not in seen:
                    seen.add(rdn)
                    entries.append((c.get("round", 0), rdn))
        entries.sort(key=lambda e: (e[0], e[1]))
        round_dir_names = [rdn for _, rdn in entries]
    if not round_dir_names:
        round_dir_names = [
            d.name for d in sorted(
                (d for d in run_results_dir.iterdir()
                 if d.is_dir() and d.name.endswith("-autopilot")),
                key=lambda d: d.name,
            )
        ]

    for idx, name in enumerate(round_dir_names, start=1):
        rd = run_results_dir / name
        try:
            entry = _round_status(rd, salvage, salvage_pid_alive)
        except Exception:
            entry = {
                "round_dir": name,
                "status": "empty",
                "detail": "classification error",
                "counts": (0, 0, 0, 0),
            }
        entry["round_index"] = idx
        statuses.append(entry)
    return statuses


def _statuses_for(run_id_str: str, data: dict):
    """Resolve (statuses, salvage, salvage_active) for a run — fully guarded.

    Centralizes the salvage + per-round-validity lookup shared by the live
    monitor loop, :func:`print_snapshot`, and :func:`_print_validity_block`:

      1. load ``salvage.json`` (or None),
      2. resolve ``results/<run_id>/`` via the runner and classify its rounds
         with :func:`_run_round_statuses` (passing *data* so transient salvage
         scratch dirs are excluded),
      3. compute ``salvage_active`` (marker ``status=running`` AND pid alive).

    Returns ``([], None, False)`` on ANY error (missing runner import, missing
    results dir, malformed state) so a caller never crashes the monitor.
    """
    try:
        salvage = _load_salvage(run_id_str)
        salvage_active = bool(
            salvage and salvage.get("status") == "running"
            and _pid_alive(salvage.get("pid"))
        )
        statuses: List[dict] = []
        if _E2E_RUNNER is not None and hasattr(_E2E_RUNNER, "run_results_dir"):
            results_dir = _E2E_RUNNER.run_results_dir(run_id_str)
            statuses = _run_round_statuses(results_dir, salvage, data)
        return statuses, salvage, salvage_active
    except Exception:
        return [], None, False


def _validity_summary(statuses: List[dict]) -> str:
    """Compact one-line validity summary for --list.

    Examples:
        "valid:2/5 ⟳R3 ✗R4,R5"   (mixed)
        "valid:5/5"               (all valid)
    """
    total = len(statuses)
    valid = sum(1 for s in statuses if s.get("status") == "valid")
    rerunning = [s for s in statuses if s.get("status") == "re-running"]
    failing = [s for s in statuses if s.get("status") in ("env-failed", "incomplete")]

    parts = [f"valid:{valid}/{total}"]
    if rerunning:
        parts.append("⟳" + ",".join(f"R{s['round_index']}" for s in rerunning))
    if failing:
        parts.append("✗" + ",".join(f"R{s['round_index']}" for s in failing))
    return " ".join(parts)


def _effective_status(state_status: str, salvage: Optional[dict],
                      salvage_pid_alive: bool) -> str:
    """Effective run status for --list, accounting for an active salvage.

    PURE. If a salvage is actively re-running rounds for this run (its marker
    says ``status=running`` AND its process is alive), the run is being
    re-worked — report ``"re-running"`` regardless of what state.json's
    top-level status says (which may already read ``done``). Otherwise the
    state status is returned unchanged.
    """
    if salvage and salvage.get("status") == "running" and salvage_pid_alive:
        return "re-running"
    return state_status


def _list_progress_cell(statuses: List[dict], completed_count: int,
                        tool: str, target: object) -> str:
    """Build the --list Progress cell, leading with the VALID count.

    PURE. When per-round validity classification is available, the headline is
    the validity summary (``valid:2/5 ⟳R3 ✗R4,R5``) followed by a small
    ``(N ran)`` context showing how many rounds the state recorded as completed.
    When classification is unavailable (empty ``statuses``), fall back to the
    legacy ``<tool>:<completed>/<target>`` text so the column is never blank.
    """
    if not statuses:
        return f"{tool}:{completed_count}/{target}"
    return f"{_validity_summary(statuses)}  ({completed_count} ran)"


def _resolve_selection(choice: str, run_ids: List[str]) -> Optional[str]:
    """Resolve an interactive selection to a run_id (or None).

    PURE. Accepts, in order:
      1. ``"q"`` / empty / whitespace → None (quit)
      2. a 1-based index string (``"3"`` → ``run_ids[2]``); out-of-range → None
      3. an exact run_id → itself
      4. a UNIQUE substring of exactly one run_id → that run_id; ambiguous
         (matches >1) or no match → None
    """
    if choice is None:
        return None
    s = choice.strip()
    if not s or s.lower() == "q":
        return None

    # 1-based index (only when it resolves in range; an out-of-range digit
    # falls through to substring matching, e.g. a numeric run_id fragment).
    if s.isdigit():
        idx = int(s)
        if 1 <= idx <= len(run_ids):
            return run_ids[idx - 1]

    # exact match
    if s in run_ids:
        return s

    # unique substring match
    matches = [rid for rid in run_ids if s in rid]
    if len(matches) == 1:
        return matches[0]
    return None


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _parse_utc(ts: Optional[str]) -> Optional[datetime]:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None



def _clock_to_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.strptime(value, "%H:%M:%S")
    except ValueError:
        return None



def _format_duration(seconds: Optional[float], plus: bool = False) -> str:
    if seconds is None:
        return "—"
    minutes = max(0, int(seconds // 60))
    hours, mins = divmod(minutes, 60)
    if hours:
        text = f"{hours}h{mins:02d}m"
    else:
        text = f"{mins}m"
    return f"{text}+" if plus else text



def _short_time(ts: Optional[str]) -> str:
    """Extract HH:MM from ISO timestamp."""
    if not ts:
        return "—"
    dt = _parse_utc(ts)
    if dt:
        return dt.astimezone().strftime("%H:%M")
    # Try local parse
    try:
        return ts[11:16] if len(ts) > 16 else ts
    except Exception:
        return "—"


def _duration_str(start_ts: Optional[str], end_ts: Optional[str]) -> str:
    """Duration between two ISO timestamps."""
    s = _parse_utc(start_ts)
    e = _parse_utc(end_ts)
    if s and e:
        return _format_duration((e - s).total_seconds())
    return "—"


def _elapsed_str(start_ts: Optional[str]) -> str:
    """Elapsed time since an ISO timestamp until now."""
    s = _parse_utc(start_ts)
    if s is None:
        return "?"
    now = datetime.now(s.tzinfo)
    return _format_duration((now - s).total_seconds(), plus=True)



def _format_clock(value: Optional[str]) -> str:
    return value[:5] if value else "-"



def _extract_line_clock(line: str) -> Optional[str]:
    match = TIMESTAMP_RE.match(line)
    return match.group(1) if match else None



def _clock_duration(started_at: Optional[str], ended_at: Optional[str] = None) -> Optional[float]:
    start_dt = _clock_to_datetime(started_at)
    if start_dt is None:
        return None

    if ended_at:
        end_dt = _clock_to_datetime(ended_at)
    else:
        now = datetime.now()
        end_dt = start_dt.replace(hour=now.hour, minute=now.minute, second=now.second)

    if end_dt is None:
        return None
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
    return (end_dt - start_dt).total_seconds()



def _remaining_rounds(target: object, completed_count: int) -> int:
    try:
        return max(0, int(target) - completed_count)
    except (TypeError, ValueError):
        return 0



def _tool_display_list(tool_filter: Optional[str], tools: List[str]) -> List[str]:
    if tool_filter is None:
        return []
    if tool_filter == "all":
        return tools
    return [tool_filter]



def _current_round_label(tool_state: dict) -> str:
    in_progress = tool_state.get("in_progress") or {}
    if in_progress.get("round"):
        return f"R{in_progress['round']}"
    completed = tool_state.get("completed", [])
    if completed:
        return f"R{completed[-1].get('round', '?')}"
    return "R?"



def _format_tool_timing(tool_state: dict) -> str:
    status = tool_state.get("status", "pending")
    if status == "running":
        in_progress = tool_state.get("in_progress") or {}
        round_num = in_progress.get("round", "?")
        started = _parse_utc(in_progress.get("start_utc"))
        if started is None:
            return f"R{round_num}"
        elapsed = _format_duration((datetime.now(started.tzinfo) - started).total_seconds(), plus=True)
        return f"R{round_num} {started.astimezone().strftime('%H:%M')} ({elapsed})"

    if status == "done":
        completed = tool_state.get("completed", [])
        if not completed:
            return "last: —"
        last = completed[-1]
        start_dt = _parse_utc(last.get("start_utc"))
        end_dt = _parse_utc(last.get("end_utc"))
        duration = None if start_dt is None or end_dt is None else (end_dt - start_dt).total_seconds()
        return f"last: {_format_duration(duration)}"

    return "—"



def _scenario_icon(status: str) -> str:
    return {"done": "✓", "running": "▶", "pending": "·"}.get(status, "?")



def _scenario_markup(key: str, status: str) -> str:
    icon = _scenario_icon(status)
    if status == "done":
        return f"[green]{icon}{key}[/green]"
    if status == "running":
        return f"[yellow]{icon}{key}[/yellow]"
    return f"[dim]{icon}{key}[/dim]"



def _scenario_status_text(tool: str, log_dir: Optional[Path]) -> str:
    if not log_dir:
        return ""
    timing = LogTailer(tool, log_dir, n=4).parse_scenario_timing()
    return " ".join(_scenario_markup(key, timing[key]["status"]) for key in SCENARIO_KEYS)



def _scenario_timing_lines(tool: str, tool_state: dict, log_dir: Optional[Path]) -> List[str]:
    timing = LogTailer(tool, log_dir, n=4).parse_scenario_timing()
    header = f"{tool} {_current_round_label(tool_state)} Scenarios:"
    lines = [header]
    for key in SCENARIO_KEYS:
        entry = timing[key]
        status = entry["status"]
        started_at = entry["started_at"]
        ended_at = entry["ended_at"]
        if status == "pending":
            span = "-"
            duration = "-"
        elif status == "running":
            span = f"{_format_clock(started_at)}~"
            duration = _format_duration(_clock_duration(started_at), plus=True)
        else:
            span = f"{_format_clock(started_at)}~{_format_clock(ended_at)}"
            duration = _format_duration(_clock_duration(started_at, ended_at))
        lines.append(f"  {key:<11} {span:<13} ({duration})   {_scenario_icon(status)}")
    return lines


# ---------------------------------------------------------------------------
# State reader
# ---------------------------------------------------------------------------


class StateReader:
    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id
        self._path: Optional[Path] = None

    def find_path(self) -> Optional[Path]:
        if self.run_id:
            p = RUNNER_STATE_DIR / self.run_id / "state.json"
            return p if p.exists() else None
        latest = RUNNER_STATE_DIR / "latest"
        if latest.is_symlink():
            target = RUNNER_STATE_DIR / latest.readlink()
            candidate = target / "state.json"
            if candidate.exists():
                return candidate
        candidates = sorted(
            (RUNNER_STATE_DIR.glob("*/state.json") if RUNNER_STATE_DIR.exists() else []),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        return candidates[0] if candidates else None

    def load(self) -> Optional[dict]:
        p = self._path or self.find_path()
        if p is None:
            return None
        try:
            return json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            return None

    def log_dir(self) -> Optional[Path]:
        p = self.find_path()
        return p.parent / "logs" if p else None


# ---------------------------------------------------------------------------
# Log tailer
# ---------------------------------------------------------------------------


class LogTailer:
    """Read last N lines from a log file."""

    def __init__(self, tool: str, log_dir: Optional[Path], n: int = 4):
        self.tool = tool
        self.log_dir = log_dir
        self.n = n

    @property
    def _path(self) -> Optional[Path]:
        if self.log_dir is None:
            return None
        p = self.log_dir / f"{self.tool}.log"
        return p if p.exists() else None

    def _read_lines(self) -> List[str]:
        p = self._path
        if p is None:
            return []
        try:
            return p.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            return []

    def _current_round_lines(self) -> List[str]:
        lines = self._read_lines()
        last_round_idx = 0
        for idx, line in enumerate(lines):
            if "Round " in line and "START" in line:
                last_round_idx = idx
        return lines[last_round_idx:]

    def tail(self) -> List[str]:
        lines = self._read_lines()
        if not lines:
            return [f"(no log for {self.tool})"]
        return lines[-self.n:]

    def parse_scenario_status(self) -> Dict[str, str]:
        return {key: entry["status"] for key, entry in self.parse_scenario_timing().items()}

    def parse_scenario_timing(self) -> Dict[str, dict]:
        """Return {scenario_key: {"status", "started_at", "ended_at"}} for current round."""
        result = {
            key: {"status": "pending", "started_at": None, "ended_at": None}
            for key in SCENARIO_KEYS
        }
        current_ts: Optional[str] = None
        active_key: Optional[str] = None

        for line in self._current_round_lines():
            line_ts = _extract_line_clock(line)
            if line_ts:
                current_ts = line_ts

            matched_key = next((key for key, pattern in SCENARIO_FILE_PATTERNS.items() if pattern in line), None)
            if matched_key is None:
                continue

            entry = result[matched_key]
            if entry["started_at"] is None:
                if active_key and active_key != matched_key:
                    active_entry = result[active_key]
                    if active_entry["ended_at"] is None:
                        active_entry["ended_at"] = current_ts or active_entry["started_at"]
                        active_entry["status"] = "done"
                entry["started_at"] = current_ts

            if "PASSED" in line or "FAILED" in line:
                entry["ended_at"] = current_ts or entry["ended_at"] or entry["started_at"]
                entry["status"] = "done"
                if active_key == matched_key:
                    active_key = None
            else:
                if entry["ended_at"] is None:
                    entry["status"] = "running"
                    active_key = matched_key

        for key, entry in result.items():
            if entry["ended_at"] is not None:
                entry["status"] = "done"
            elif entry["started_at"] is not None:
                entry["status"] = "running"
        return result


# ---------------------------------------------------------------------------
# Rich TUI rendering
# ---------------------------------------------------------------------------


def _progress_status_label(state_status: str, salvage_active: bool) -> str:
    """Effective per-tool Status label for the Round Progress table.

    PURE. Mirrors :func:`_effective_status` semantics for the per-tool cell:
    when a salvage is actively re-running this run, ANY state status (including
    ``done``) is displayed as ``"re-running"``; otherwise the raw state status
    is returned unchanged.
    """
    if salvage_active:
        return "re-running"
    return state_status


def _salvage_rerun_scenarios_text(data: dict, salvage: dict) -> Optional[str]:
    """Per-scenario re-running detail for the salvage's CURRENT round, or None.

    PURE-ish (filesystem read only, fully guarded). Locates the round being
    re-run (``salvage["round_dir"]``) within the run's CANONICAL results dir,
    derives its 1-based R-index from the canonical round order, classifies each
    TARGET scenario (``salvage["scenarios"]``) in that round dir — valid →
    merged/done (✓), anything else → still re-running/pending (⟳) — and renders
    the targets via :func:`_scenario_cells`, prefixed ``re-running R<idx>:``.

    Returns None on any failure (missing runner import, missing dir, bad data),
    so the caller can fall back to the plain ``re-running…`` text.
    """
    try:
        run_id = data.get("run_id")
        round_name = salvage.get("round_dir")
        targets = salvage.get("scenarios") or []
        if not run_id or not round_name or not targets:
            return None
        if _E2E_RUNNER is None or not hasattr(_E2E_RUNNER, "run_results_dir"):
            return None
        results_dir = _E2E_RUNNER.run_results_dir(run_id)
        round_dir = results_dir / round_name
        if not round_dir.is_dir():
            return None

        # R-index from the canonical round order (chronological dir-name sort).
        canonical = sorted(
            (d.name for d in results_dir.iterdir()
             if d.is_dir() and d.name.endswith("-autopilot"))
        )
        try:
            r_idx = canonical.index(round_name) + 1
        except ValueError:
            r_idx = "?"

        # Classify only the TARGET scenarios: valid (merged) → ✓, else → ⟳.
        target_set = set(targets)
        scenarios: Dict[str, str] = {}
        rerun_targets: set = set()
        for key in ROUND_SCENARIO_KEYS:
            if key not in target_set:
                continue
            scen_dir = round_dir / f"claude_code__{key}"
            verdict = _classify_round_scenario(scen_dir) if scen_dir.is_dir() else "skip"
            if verdict == "valid":
                scenarios[key] = "valid"
            else:
                rerun_targets.add(key)
        cells = _scenario_cells(scenarios, rerun_targets)
        # Restrict the rendered cells to the target scenarios only.
        order = {SCENARIO_ABBREV[k]: i for i, k in enumerate(ROUND_SCENARIO_KEYS)}
        kept = [c for c in cells.split() if c[:-1] in order
                and any(SCENARIO_ABBREV[k] == c[:-1] for k in target_set)]
        cells = " ".join(kept)
        return f"re-running R{r_idx}: {cells}"
    except Exception:
        return None


def _make_progress_table(data: dict, log_dir: Optional[Path] = None,
                         salvage: Optional[dict] = None,
                         salvage_active: bool = False) -> Table:
    tbl = Table(title=None, expand=True, border_style="dim")
    tbl.add_column("Tool", style="cyan", no_wrap=True, min_width=14)
    tbl.add_column("Done", justify="right", style="green", min_width=4)
    tbl.add_column("Fail", justify="right", style="red", min_width=4)
    tbl.add_column("Rem", justify="right", style="yellow", min_width=4)
    tbl.add_column("Status", min_width=8)
    tbl.add_column("Timing", min_width=20)
    tbl.add_column("Scenarios (current round)", min_width=40)

    target = data.get("target_rounds", "?")
    tool_states = data.get("tool_states", {})
    for tool in data.get("tools", ALL_TOOLS):
        ts = tool_states.get(tool, {})
        completed = ts.get("completed", [])
        ok = sum(1 for r in completed if r.get("exit_code") == 0)
        ng = sum(1 for r in completed if r.get("exit_code") != 0)
        rem = _remaining_rounds(target, len(completed))
        status = ts.get("status", "pending")
        # Effective status: an active salvage re-runs rounds in place even when
        # state.json already reads "done" — show "re-running" so the live view
        # tracks the salvage instead of looking finished.
        status = _progress_status_label(status, salvage_active)

        status_style = {
            "done": "[green]done[/green]",
            "running": "[yellow]running[/yellow]",
            "re-running": "[yellow]re-running[/yellow]",
            "pending": "[dim]pending[/dim]",
            "aborted": "[red]aborted[/red]",
            "stopped": "[red]stopped[/red]",
        }.get(status, status)

        if salvage_active:
            detail_text = (
                _salvage_rerun_scenarios_text(data, salvage) if salvage else None
            )
            if detail_text:
                scenario_str = f"[yellow]{detail_text}[/yellow]"
            else:
                scenario_str = "[yellow]re-running…[/yellow]"
        elif status == "running" and log_dir:
            scenario_str = _scenario_status_text(tool, log_dir)
        elif status == "done":
            scenario_str = "[green]all complete[/green]"
        else:
            scenario_str = "[dim]—[/dim]"

        tbl.add_row(
            tool,
            str(ok),
            str(ng) if ng else "—",
            str(rem) if rem > 0 else "✓",
            Text.from_markup(status_style),
            Text(_format_tool_timing(ts)),
            Text.from_markup(scenario_str),
        )
    return tbl



def _validity_cell(status: Optional[str]) -> "Text":
    """Render a per-round Validity cell (icon + color) for a status string.

    Returns a dim ``—`` when *status* is None/unknown (no matching round status).
    """
    if status is None:
        return Text("—", style="dim")
    label = _VALIDITY_ICON.get(status, status)
    if status == "valid":
        style = "green"
    elif status == "re-running":
        style = "yellow"
    elif status in ("env-failed", "incomplete"):
        style = "red"
    else:
        style = "dim"
    return Text(label, style=style)


def _make_completed_rounds_table(data: dict, statuses: Optional[List[dict]] = None) -> Optional[Table]:
    """Build a Rich Table showing completed rounds across all tools. Returns None if no completions.

    When *statuses* (from :func:`_run_round_statuses`) is provided, a per-round
    "Validity" column is added; each completed row is matched to its status
    entry by ``result_dir_name`` == ``round_dir``. Unmatched rows show ``—``.
    """
    by_dir: Dict[str, str] = {}
    for s in (statuses or []):
        rdn = s.get("round_dir")
        if rdn:
            by_dir[rdn] = s.get("status", "empty")

    tool_states = data.get("tool_states", {})
    detail_tbl = Table(title="Completed Rounds", expand=True, border_style="dim")
    detail_tbl.add_column("Tool", style="cyan", no_wrap=True)
    detail_tbl.add_column("Round", justify="right")
    detail_tbl.add_column("Dir", no_wrap=True, style="dim")
    detail_tbl.add_column("Start", no_wrap=True)
    detail_tbl.add_column("End", no_wrap=True)
    detail_tbl.add_column("Duration", no_wrap=True)
    detail_tbl.add_column("Exit", justify="right")
    detail_tbl.add_column("Validity")
    has_rows = False
    for tool in data.get("tools", ALL_TOOLS):
        ts = tool_states.get(tool, {})
        for r in ts.get("completed", []):
            has_rows = True
            start = _short_time(r.get("start_utc") or r.get("started_at"))
            end = _short_time(r.get("end_utc") or r.get("ended_at"))
            dur = _duration_str(r.get("start_utc") or r.get("started_at"), r.get("end_utc") or r.get("ended_at"))
            exit_code = str(r.get("exit_code", "?"))
            exit_style = "green" if exit_code == "0" else "red"
            validity = _validity_cell(by_dir.get(r.get("result_dir_name")))
            rdn = r.get("result_dir_name") or "—"
            # Drop the redundant "_<tool>-autopilot" suffix for a compact R#↔dir map.
            dir_short = rdn[:-len("-autopilot")].rsplit("_", 1)[0] if rdn.endswith("-autopilot") else rdn
            detail_tbl.add_row(tool, f"R{r.get('round', '?')}", dir_short, start, end, dur,
                               Text(exit_code, style=exit_style), validity)
    return detail_tbl if has_rows else None


_VALIDITY_ICON = {
    "valid": "✓ valid",
    "re-running": "⟳ re-running",
    "env-failed": "✗ env-failed",
    "incomplete": "✗ incomplete",
    "empty": "· empty",
}


def _validity_line(statuses: List[dict], completed_state: Optional[int] = None,
                   target: object = None) -> str:
    """One-line validity summary line (plain text) for the single-run view."""
    total = len(statuses)
    valid = sum(1 for s in statuses if s.get("status") == "valid")
    rerunning = sum(1 for s in statuses if s.get("status") == "re-running")
    pending = sum(1 for s in statuses if s.get("status") in ("env-failed", "incomplete"))
    parts = [f"valid {valid}/{total}"]
    if rerunning:
        parts.append(f"re-running {rerunning}")
    if pending:
        parts.append(f"pending {pending}")
    line = "Validity summary: " + " · ".join(parts)
    if completed_state is not None and target is not None:
        line += f"   (state: {completed_state}/{target} completed)"
    return line


def _all_rounds_valid(statuses: List[dict]) -> bool:
    return bool(statuses) and all(s.get("status") == "valid" for s in statuses)


def _make_validity_table(statuses: List[dict]) -> "Table":
    """Rich per-round VALIDITY table (Round / Dir / Validity)."""
    tbl = Table(title="Round Validity", expand=True, border_style="dim")
    tbl.add_column("Round", style="cyan", no_wrap=True, min_width=5)
    tbl.add_column("Dir", no_wrap=True)
    tbl.add_column("Validity")
    tbl.add_column("Scenarios")
    for s in statuses:
        status = s.get("status", "empty")
        label = _VALIDITY_ICON.get(status, status)
        detail = s.get("detail", "")
        if status == "re-running":
            text = f"⟳ re-running ({detail})"
            style = "yellow"
        elif status == "valid":
            text = "✓ valid"
            style = "green"
        elif status == "env-failed":
            text = f"✗ env-failed ({detail})"
            style = "red"
        elif status == "incomplete":
            text = f"✗ incomplete ({detail})"
            style = "red"
        else:
            text = label
            style = "dim"
        # Per-scenario breakdown; targeted scenarios show ⟳ for a re-running round.
        scenarios = s.get("scenarios") or {}
        rerun_targets = s.get("rerun_targets") if status == "re-running" else None
        scen_cell = _scenario_cells(scenarios, rerun_targets) if scenarios else "—"
        tbl.add_row(f"R{s.get('round_index', '?')}", s.get("round_dir", "?"),
                    Text(text, style=style), Text(scen_cell))
    return tbl


def _print_validity_block(run_id_str: str, data: dict) -> None:
    """Render the per-round validity table + summary for a single run.

    Guarded so the monitor never crashes if a round dir is odd. Prints the
    success line only when ALL rounds are valid AND no active salvage.
    """
    try:
        statuses, salvage, salvage_active = _statuses_for(run_id_str, data)
        if not statuses:
            return

        # completed-from-state count (for context line)
        tool_states = data.get("tool_states", {})
        completed_state = max(
            (len(ts.get("completed", [])) for ts in tool_states.values()),
            default=0,
        )
        target = data.get("target_rounds", "?")

        if _all_rounds_valid(statuses) and not salvage_active:
            if _RICH:
                from rich.console import Console as RConsole
                RConsole().print("[green]All rounds valid![/green]")
            else:
                print("All rounds valid!")
            return

        if _RICH:
            from rich.console import Console as RConsole
            console = RConsole()
            console.print(_make_validity_table(statuses))
            console.print(_validity_line(statuses, completed_state, target))
        else:
            print()
            print(f"{'Round':<6} {'Dir':<32} Validity")
            for s in statuses:
                status = s.get("status", "empty")
                detail = s.get("detail", "")
                base = _VALIDITY_ICON.get(status, status)
                if status in ("re-running", "env-failed", "incomplete"):
                    label = f"{base} ({detail})"
                else:
                    label = base
                rdir = (s.get("round_dir", "?"))[:31]
                print(f"R{s.get('round_index', '?'):<5} {rdir:<32} {label}")
            print(_validity_line(statuses, completed_state, target))
    except Exception:
        # Never crash the monitor on validity rendering.
        pass


def _make_log_panel(tool: str, lines: List[str], n: int = 4) -> Panel:
    content = "\n".join(lines[-n:]) or "(no output yet)"
    return Panel(content, title=f"[bold]{tool}[/bold] — tail log", border_style="blue")



def _make_scenario_timing_panel(tool: str, tool_state: dict, log_dir: Optional[Path]) -> Panel:
    return Panel("\n".join(_scenario_timing_lines(tool, tool_state, log_dir)), border_style="magenta")


# ---------------------------------------------------------------------------
# One-shot text output (no rich)
# ---------------------------------------------------------------------------



def print_snapshot(data: dict) -> None:
    target = data.get("target_rounds", "?")
    thinking = "ON" if data.get("thinking") else "OFF"
    run_id_str = data.get("run_id", "?")
    tool_states = data.get("tool_states", {})

    # Salvage-aware per-round validity (shared with the live loop).
    statuses, salvage, salvage_active = _statuses_for(run_id_str, data)

    if _RICH:
        from rich.console import Console as RConsole
        console = RConsole()
        header = Text(f"E2E Monitor  run_id={run_id_str}  target={target}R  thinking={thinking}", style="bold")
        console.print(header)

        log_dir = StateReader(run_id_str).log_dir()
        tbl = _make_progress_table(data, log_dir, salvage=salvage,
                                   salvage_active=salvage_active)
        console.print(Panel(tbl, title="Round Progress", border_style="green"))

        # Per-tool completed round detail (with per-round validity column)
        detail_tbl = _make_completed_rounds_table(data, statuses)
        if detail_tbl:
            console.print(detail_tbl)

        # Salvage status (after round table)
        if salvage:
            alive = _pid_alive(salvage.get("pid"))
            salvage_line = _format_salvage(salvage, alive)
            style = "yellow" if salvage.get("status") == "running" and alive else "dim"
            console.print(Text(salvage_line, style=style))

        # Per-round validity (salvage-aware)
        _print_validity_block(run_id_str, data)
    else:
        print(f"\n=== E2E Monitor  run_id={run_id_str} ===")
        print(f"Target: {target} rounds  Thinking: {thinking}\n")
        print(f"{'Tool':<16} {'Done':>5} {'Fail':>5} {'Rem':>5} {'Status':<10} {'Timing':<22}")
        print("-" * 82)
        for tool in data.get("tools", ALL_TOOLS):
            ts = tool_states.get(tool, {})
            completed = ts.get("completed", [])
            ok = sum(1 for r in completed if r.get("exit_code") == 0)
            ng = sum(1 for r in completed if r.get("exit_code") != 0)
            rem = _remaining_rounds(target, len(completed))
            status = _progress_status_label(ts.get("status", "pending"), salvage_active)
            print(f"{tool:<16} {ok:>5} {ng:>5} {rem:>5} {status:<10} {_format_tool_timing(ts):<22}")
        print()
        # Salvage status (after round table)
        if salvage:
            alive = _pid_alive(salvage.get("pid"))
            print(_format_salvage(salvage, alive))
            print()

        # Per-round validity (salvage-aware)
        _print_validity_block(run_id_str, data)


# ---------------------------------------------------------------------------
# List command
# ---------------------------------------------------------------------------



def _collect_run_rows() -> List[dict]:
    """Gather one summary row per run (mtime-desc), for --list / --select.

    Each row dict carries the precomputed display fields plus the raw run_id so
    callers can both render the table and resolve an interactive selection.
    Returns [] when there are no runs.
    """
    if not RUNNER_STATE_DIR.exists():
        return []

    latest_target = None
    latest_link = RUNNER_STATE_DIR / "latest"
    if latest_link.is_symlink():
        latest_target = latest_link.readlink()

    states = sorted(
        (p for p in RUNNER_STATE_DIR.glob("*/state.json") if p.parent.name != "latest"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )

    rows: List[dict] = []
    for state_file in states:
        try:
            data = json.loads(state_file.read_text())
        except Exception:
            continue

        run_id = data.get("run_id", state_file.parent.name)
        created = data.get("created_at", "?")[:19].replace("T", " ")
        target = data.get("target_rounds", "?")
        thinking = "Yes" if data.get("thinking") else "No"

        tools = data.get("tools", [])
        tool_states = data.get("tool_states", {})

        # Derive overall status using same logic as runner
        top = data.get("status")
        if top in ("done", "aborted", "stopped"):
            overall = top
        else:
            statuses = [tool_states.get(t, {}).get("status", "pending") for t in tools]
            if any(s == "aborted" for s in statuses):
                overall = "aborted"
            elif any(s == "stopped" for s in statuses):
                overall = "stopped"
            elif any(s == "running" for s in statuses):
                overall = "running"
            elif statuses and all(s == "done" for s in statuses):
                overall = "done"
            else:
                overall = "pending"

        # Per-round validity classification (best-effort).
        salvage = _load_salvage(run_id)
        salvage_pid_alive = _pid_alive(salvage.get("pid")) if salvage else False
        round_statuses: List[dict] = []
        try:
            if _E2E_RUNNER is not None and hasattr(_E2E_RUNNER, "run_results_dir"):
                results_dir = _E2E_RUNNER.run_results_dir(run_id)
                round_statuses = _run_round_statuses(
                    results_dir, salvage, {"tool_states": tool_states}
                )
        except Exception:
            round_statuses = []

        # Effective status: reflect an active salvage as "re-running".
        effective = _effective_status(overall, salvage, salvage_pid_alive)

        # Progress cell: lead with the valid count; fall back to legacy text.
        primary_tool = tools[0] if tools else "?"
        completed_count = max(
            (len(tool_states.get(t, {}).get("completed", [])) for t in tools),
            default=0,
        )
        progress = _list_progress_cell(
            round_statuses, completed_count, primary_tool, target
        )

        rows.append({
            "run_id": run_id,
            "created": created,
            "target": target,
            "thinking": thinking,
            "status": effective,
            "progress": progress,
            "is_latest": str(latest_target) == run_id,
        })
    return rows


def _print_list_table(rows: List[dict], indexed: bool = False) -> None:
    """Print the --list table. When *indexed*, prepend a 1-based ``#`` column."""
    if indexed:
        print(f"\n{'#':<4} {'Latest':<7} {'Run ID':<18} {'Created':<20} "
              f"{'Rounds':<8} {'Thinking':<9} {'Status':<12} Progress")
        print(f"{'-'*4} {'-'*7} {'-'*18} {'-'*20} {'-'*8} {'-'*9} {'-'*12} {'-'*40}")
    else:
        print(f"\n{'Latest':<7} {'Run ID':<18} {'Created':<20} {'Rounds':<10} "
              f"{'Thinking':<9} {'Status':<12} Progress")
        print(f"{'-'*7} {'-'*18} {'-'*20} {'-'*10} {'-'*9} {'-'*12} {'-'*40}")

    for i, row in enumerate(rows, start=1):
        marker = "*" if row["is_latest"] else ""
        if indexed:
            print(
                f"{i:<4} {marker:<7} {row['run_id']:<18} {row['created']:<20} "
                f"{str(row['target']):<8} {row['thinking']:<9} "
                f"{row['status']:<12} {row['progress']}"
            )
        else:
            print(
                f"{marker:<7} {row['run_id']:<18} {row['created']:<20} "
                f"{str(row['target']):<10} {row['thinking']:<9} "
                f"{row['status']:<12} {row['progress']}"
            )
    print()


def show_list() -> None:
    rows = _collect_run_rows()
    if not rows:
        print("No runs found.")
        return
    _print_list_table(rows, indexed=False)


def _should_prompt_default(
    run_id_arg: Optional[str],
    is_list: bool,
    is_select: bool,
    is_status: bool,
    isatty: bool,
    num_runs: int,
) -> bool:
    """Decide whether the DEFAULT (no-arg) path should prompt to pick a run.

    PURE. Returns True ONLY when the invocation is the bare default path on an
    interactive terminal with a real choice to make:
      - no ``--run-id`` was given, and
      - none of ``--list`` / ``--select`` / ``--status`` were given, and
      - stdin is a TTY, and
      - more than one run exists.

    Any other combination returns False — so piped/scripted invocations,
    explicit run-id/list/select/status, and the single-run case all keep the
    current latest-run behavior and never block on input.
    """
    if run_id_arg:
        return False
    if is_list or is_select or is_status:
        return False
    if not isatty:
        return False
    return num_runs > 1


def _select_run_id(run_ids, input_fn=input) -> Optional[str]:
    """List + prompt + resolve → a chosen run_id (or None).

    Prints the indexed run table (via the freshly-collected rows so the display
    matches ``--list``), prompts ONCE using *input_fn* (injectable for tests),
    and resolves the answer with :func:`_resolve_selection`. ``q`` / empty /
    out-of-range, plus ``EOFError`` / ``KeyboardInterrupt`` from *input_fn*, all
    return None (clean quit). When *run_ids* is empty, returns None without
    prompting.

    Note: the indexed table is rendered from the live run rows; *run_ids* is the
    authoritative ordered list used for resolution (the caller passes the run_id
    column extracted from those same rows, so indices line up).
    """
    if not run_ids:
        return None

    rows = _collect_run_rows()
    if rows:
        _print_list_table(rows, indexed=True)

    try:
        choice = input_fn(f"Select run [1-{len(run_ids)}], or q to quit: ")
    except (EOFError, KeyboardInterrupt):
        print()  # clean newline after an interrupted prompt
        return None

    return _resolve_selection(choice, run_ids)


def run_selector() -> int:
    """Interactive run picker: numbered list → prompt → single-run detail.

    Prints the indexed --list table, prompts for a 1-based index / run_id /
    substring, resolves it via :func:`_resolve_selection`, then renders the
    chosen run's DETAILED single-run view one-shot (no live loop). ``q`` /
    empty / EOF / Ctrl-C all quit cleanly. Returns a process exit code.
    """
    rows = _collect_run_rows()
    if not rows:
        print("No runs found.")
        return 0

    run_ids = [row["run_id"] for row in rows]
    chosen = _select_run_id(run_ids)
    if chosen is None:
        print("No selection.")
        return 0

    # Render the chosen run's detailed single-run view, one-shot.
    run_monitor(chosen, tool_filter=None, tail_n=4, once=True)
    return 0


# ---------------------------------------------------------------------------
# Main monitor loop
# ---------------------------------------------------------------------------



def _monitor_should_exit(data: dict, salvage_active: bool) -> bool:
    """Whether the live monitor loop should stop refreshing.

    Stop ONLY when every tool's state is "done" AND no salvage is actively
    re-running. A force-killed/rate-limited run is recorded as state "done"
    even while a scenario salvage (cleanup_resume) re-runs it in place — in that
    case keep refreshing so the live view tracks the active re-run instead of
    exiting immediately (which made the default monitor behave like --list).
    """
    if salvage_active:
        return False
    tool_states = data.get("tool_states", {})
    tools = data.get("tools", ALL_TOOLS)
    return all(tool_states.get(t, {}).get("status") == "done" for t in tools)


def run_monitor(run_id: Optional[str], tool_filter: Optional[str], tail_n: int, once: bool) -> None:
    reader = StateReader(run_id)

    if not _RICH or once:
        data = reader.load()
        if data is None:
            print("No run state found. Start a run with e2e_runner.py first.")
            return

        print_snapshot(data)

        if not once:
            log_dir = reader.log_dir()
            tool_states = data.get("tool_states", {})
            for tool in _tool_display_list(tool_filter, data.get("tools", ALL_TOOLS)):
                tailer = LogTailer(tool, log_dir, n=tail_n)
                print(f"\n--- {tool} log ---")
                for line in tailer.tail():
                    print(line)
                if tool_filter not in (None, "all") and tool == tool_filter:
                    print()
                    for line in _scenario_timing_lines(tool, tool_states.get(tool, {}), log_dir):
                        print(line)
        return

    console = Console()
    refresh_secs = 3

    try:
        with Live(console=console, refresh_per_second=1, screen=False, transient=True) as live:
            while True:
                data = reader.load()

                if data is None:
                    live.update(Panel("[yellow]No run state found. Start e2e_runner.py first.[/yellow]"))
                    time.sleep(refresh_secs)
                    continue

                log_dir = reader.log_dir()
                tool_states = data.get("tool_states", {})

                run_id_str = data.get("run_id", "?")
                target = data.get("target_rounds", "?")
                thinking = "ON" if data.get("thinking") else "OFF"
                now_str = datetime.now().strftime("%H:%M:%S")
                header = Text(
                    f"E2E Monitor  run_id={run_id_str}  target={target}R  thinking={thinking}  [{now_str}]",
                    style="bold",
                )

                # Salvage-aware per-round validity (shared with print_snapshot
                # / _print_validity_block). Guarded → never crashes the loop.
                statuses, salvage, salvage_active = _statuses_for(run_id_str, data)

                prog_panel = Panel(
                    _make_progress_table(data, log_dir, salvage=salvage,
                                         salvage_active=salvage_active),
                    title="Round Progress", border_style="green",
                )

                renderables = [header, prog_panel]
                completed_tbl = _make_completed_rounds_table(data, statuses)
                if completed_tbl:
                    renderables.append(completed_tbl)
                display_tools = _tool_display_list(tool_filter, data.get("tools", ALL_TOOLS))
                if display_tools:
                    log_panels = []
                    for tool in display_tools:
                        tailer = LogTailer(tool, log_dir, n=tail_n)
                        log_panels.append(_make_log_panel(tool, tailer.tail(), tail_n))
                    renderables.append(Columns(log_panels, equal=True, expand=True))

                    if tool_filter not in (None, "all") and tool_filter in tool_states:
                        renderables.append(_make_scenario_timing_panel(tool_filter, tool_states[tool_filter], log_dir))

                # Round Validity table + summary line, shown live (not only post-loop).
                if statuses:
                    completed_state = max(
                        (len(ts.get("completed", [])) for ts in tool_states.values()),
                        default=0,
                    )
                    renderables.append(_make_validity_table(statuses))
                    renderables.append(Text(_validity_line(statuses, completed_state, target)))

                live.update(Group(*renderables))

                if _monitor_should_exit(data, salvage_active):
                    time.sleep(1)
                    break
                time.sleep(refresh_secs)
    except KeyboardInterrupt:
        pass
    else:
        # Replace the bare "All tools completed!" with a salvage-aware
        # per-round validity view. The success line is printed by
        # _print_validity_block only when ALL rounds are valid and no salvage
        # is active; otherwise the validity table is shown instead.
        final = reader.load()
        if final is not None:
            _print_validity_block(final.get("run_id", run_id or "?"), final)
        else:
            console.print("\n[green]All tools completed![/green]")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------



def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="e2e_monitor.py",
        description="Live TUI monitor for e2e_runner.py progress.",
    )
    p.add_argument("--run-id", dest="run_id", help="Specific run ID to monitor")
    p.add_argument("--tool", help="Show logs for a tool, or use 'all' for every tool")
    p.add_argument("--tail", type=int, default=4, help="Number of log lines to show (default: 4)")
    p.add_argument("--once", action="store_true", help="Print snapshot once and exit (no live update)")
    p.add_argument("--list", action="store_true", help="List all run IDs")
    p.add_argument(
        "--select",
        action="store_true",
        help="Interactively pick a run from the list and show its detailed view",
    )
    return p



def main() -> int:
    args = build_parser().parse_args()
    # Interactive selector: explicit --select, OR plain --list on an interactive
    # TTY (so scripts that pipe --list never get a prompt). Plain --list without
    # a TTY stays non-interactive and scriptable (one row per run).
    if args.select or (args.list and sys.stdin.isatty()):
        return run_selector()
    if args.list:
        show_list()
        return 0

    effective_run_id = args.run_id
    # Default path (no run-id, no --list/--select/--status): on an interactive
    # TTY with >1 run, let the user pick a run (like --select) and then
    # live-monitor it. Piped/scripted, single-run, or explicit-arg invocations
    # fall through to the current latest-run behavior and never prompt.
    if _should_prompt_default(
        args.run_id,
        is_list=args.list,
        is_select=args.select,
        is_status=False,  # no --status flag in this CLI yet
        isatty=sys.stdin.isatty(),
        num_runs=len(_collect_run_rows()),
    ):
        rows = _collect_run_rows()
        run_ids = [row["run_id"] for row in rows]
        chosen = _select_run_id(run_ids)
        if chosen is None:
            return 0  # clean quit, no monitoring
        effective_run_id = chosen

    run_monitor(effective_run_id, args.tool, args.tail, args.once)
    return 0


if __name__ == "__main__":
    sys.exit(main())
