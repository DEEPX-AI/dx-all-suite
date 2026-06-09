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
    "dx_stream": "_dx_stream_agentic",  # not cascaded
    "cascaded": "_dx_stream_cascaded",
    "runtime": "_runtime_",
    "suite": "_suite_",
}

TIMESTAMP_RE = re.compile(r"^\[(\d{2}:\d{2}:\d{2})\]")


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


def _make_progress_table(data: dict, log_dir: Optional[Path] = None) -> Table:
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

        status_style = {
            "done": "[green]done[/green]",
            "running": "[yellow]running[/yellow]",
            "pending": "[dim]pending[/dim]",
            "aborted": "[red]aborted[/red]",
            "stopped": "[red]stopped[/red]",
        }.get(status, status)

        if status == "running" and log_dir:
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



def _make_completed_rounds_table(data: dict) -> Optional[Table]:
    """Build a Rich Table showing completed rounds across all tools. Returns None if no completions."""
    tool_states = data.get("tool_states", {})
    detail_tbl = Table(title="Completed Rounds", expand=True, border_style="dim")
    detail_tbl.add_column("Tool", style="cyan", no_wrap=True)
    detail_tbl.add_column("Round", justify="right")
    detail_tbl.add_column("Start", no_wrap=True)
    detail_tbl.add_column("End", no_wrap=True)
    detail_tbl.add_column("Duration", no_wrap=True)
    detail_tbl.add_column("Exit", justify="right")
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
            detail_tbl.add_row(tool, f"R{r.get('round', '?')}", start, end, dur, Text(exit_code, style=exit_style))
    return detail_tbl if has_rows else None


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

    if _RICH:
        from rich.console import Console as RConsole
        console = RConsole()
        header = Text(f"E2E Monitor  run_id={run_id_str}  target={target}R  thinking={thinking}", style="bold")
        console.print(header)

        log_dir = StateReader(run_id_str).log_dir()
        tbl = _make_progress_table(data, log_dir)
        console.print(Panel(tbl, title="Round Progress", border_style="green"))

        # Per-tool completed round detail
        detail_tbl = _make_completed_rounds_table(data)
        if detail_tbl:
            console.print(detail_tbl)
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
            status = ts.get("status", "pending")
            print(f"{tool:<16} {ok:>5} {ng:>5} {rem:>5} {status:<10} {_format_tool_timing(ts):<22}")
        print()


# ---------------------------------------------------------------------------
# List command
# ---------------------------------------------------------------------------



def show_list() -> None:
    if not RUNNER_STATE_DIR.exists():
        print("No runs found.")
        return

    latest_target = None
    latest_link = RUNNER_STATE_DIR / "latest"
    if latest_link.is_symlink():
        latest_target = latest_link.readlink()

    states = sorted(
        (p for p in RUNNER_STATE_DIR.glob("*/state.json") if p.parent.name != "latest"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not states:
        print("No runs found.")
        return

    print(f"\n{'Latest':<7} {'Run ID':<18} {'Created':<20} {'Rounds':<10} {'Thinking':<9} {'Status':<12} Progress")
    print(f"{'-'*7} {'-'*18} {'-'*20} {'-'*10} {'-'*9} {'-'*12} {'-'*40}")

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

        progress = ", ".join(
            f"{t}:{len(tool_states.get(t, {}).get('completed', []))}/{target}"
            for t in tools
        )

        marker = "*" if str(latest_target) == run_id else ""
        print(
            f"{marker:<7} {run_id:<18} {created:<20} {str(target):<10} {thinking:<9} "
            f"{overall:<12} {progress}"
        )
    print()


# ---------------------------------------------------------------------------
# Main monitor loop
# ---------------------------------------------------------------------------



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

                prog_panel = Panel(_make_progress_table(data, log_dir), title="Round Progress", border_style="green")

                renderables = [header, prog_panel]
                completed_tbl = _make_completed_rounds_table(data)
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

                live.update(Group(*renderables))

                all_done = all(
                    tool_states.get(tool, {}).get("status") == "done"
                    for tool in data.get("tools", ALL_TOOLS)
                )
                if all_done:
                    time.sleep(1)
                    break
                time.sleep(refresh_secs)
    except KeyboardInterrupt:
        pass
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
    return p



def main() -> int:
    args = build_parser().parse_args()
    if args.list:
        show_list()
        return 0
    run_monitor(args.run_id, args.tool, args.tail, args.once)
    return 0


if __name__ == "__main__":
    sys.exit(main())
