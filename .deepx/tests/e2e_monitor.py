#!/usr/bin/env python3
"""
e2e_monitor.py — Live TUI monitor for E2E runner progress.

Reads state.json from the latest (or specified) run and displays:
  - Per-tool round progress table
  - In-progress tool / scenario tail log
  - Timeline of completed rounds (scrollable)

Usage:
    python .deepx/tests/e2e_monitor.py                  # watch latest run
    python .deepx/tests/e2e_monitor.py --run-id 20260521_100000
    python .deepx/tests/e2e_monitor.py --tool claude-code --tail 30  # tail log only
    python .deepx/tests/e2e_monitor.py --once            # print snapshot and exit
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    from rich.columns import Columns
    from rich.console import Console
    from rich.layout import Layout
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
RESULTS_ROOT = REPO_ROOT / "dx-agentic-dev/e2e-tests/results"
RUNNER_STATE_DIR = SCRIPT_DIR / "runner_state"

ALL_TOOLS: List[str] = [
    "claude-code",
    "copilot-cli",
    "cursor-cli",
    "opencode-cli",
    "codex-cli",
]

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
        # Check "latest" symlink
        latest = RUNNER_STATE_DIR / "latest"
        if latest.is_symlink():
            target = RUNNER_STATE_DIR / latest.readlink()
            candidate = target / "state.json"
            if candidate.exists():
                return candidate
        # Fallback: newest by mtime
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

    def __init__(self, tool: str, log_dir: Optional[Path], n: int = 20):
        self.tool = tool
        self.log_dir = log_dir
        self.n = n

    @property
    def _path(self) -> Optional[Path]:
        if self.log_dir is None:
            return None
        p = self.log_dir / f"{self.tool}.log"
        return p if p.exists() else None

    def tail(self) -> List[str]:
        p = self._path
        if p is None:
            return [f"(no log for {self.tool})"]
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            return lines[-self.n:]
        except Exception as exc:
            return [f"(error reading log: {exc})"]


# ---------------------------------------------------------------------------
# Results watcher — detects new result dirs
# ---------------------------------------------------------------------------


class ResultsWatcher:
    def __init__(self):
        self._seen: set = set()
        self._events: List[str] = []
        self.refresh()

    def refresh(self) -> List[str]:
        """Return list of new entries discovered since last refresh."""
        if not RESULTS_ROOT.exists():
            return []
        current = {e.name for e in RESULTS_ROOT.iterdir() if e.is_dir()}
        new_entries = current - self._seen
        self._seen = current
        for name in sorted(new_entries):
            ts = datetime.now().strftime("%H:%M:%S")
            self._events.append(f"[{ts}] NEW result: {name}")
        return list(new_entries)

    def events_tail(self, n: int = 20) -> List[str]:
        return self._events[-n:]


# ---------------------------------------------------------------------------
# Rich TUI rendering
# ---------------------------------------------------------------------------


def _make_progress_table(data: dict) -> Table:
    tbl = Table(title=None, expand=True, border_style="dim")
    tbl.add_column("Tool", style="cyan", no_wrap=True, min_width=14)
    tbl.add_column("Done", justify="right", style="green", min_width=5)
    tbl.add_column("Fail", justify="right", style="red", min_width=5)
    tbl.add_column("Rem", justify="right", style="yellow", min_width=5)
    tbl.add_column("Status", min_width=10)
    tbl.add_column("Current Round / Last Result")

    target = data.get("target_rounds", "?")
    for tool in data.get("tools", ALL_TOOLS):
        ts = data["tool_states"].get(tool, {})
        completed = ts.get("completed", [])
        ok = sum(1 for r in completed if r.get("exit_code") == 0)
        ng = sum(1 for r in completed if r.get("exit_code") != 0)
        rem = max(0, int(target) - len(completed))
        status = ts.get("status", "pending")
        ip = ts.get("in_progress")

        status_style = {
            "done": "[green]done[/green]",
            "running": "[yellow]running[/yellow]",
            "pending": "[dim]pending[/dim]",
        }.get(status, status)

        detail = ""
        if ip:
            detail = f"Round {ip['round']} (started {ip.get('start_utc', '?')[:19]}Z)"
        elif completed:
            last = completed[-1]
            detail = (last.get("result_dir_name") or "")[-50:]

        tbl.add_row(
            tool,
            str(ok),
            str(ng) if ng else "—",
            str(rem) if rem > 0 else "✓",
            Text.from_markup(status_style),
            detail,
        )
    return tbl


def _make_log_panel(tool: str, lines: List[str], n: int = 20) -> Panel:
    content = "\n".join(lines[-n:]) or "(no output yet)"
    return Panel(content, title=f"[bold]{tool}[/bold] — tail log", border_style="blue")


def _make_timeline_panel(events: List[str]) -> Panel:
    content = "\n".join(events) or "(waiting for first result...)"
    return Panel(content, title="Timeline (new results)", border_style="dim")


def _running_tools(data: dict) -> List[str]:
    return [
        t
        for t in data.get("tools", ALL_TOOLS)
        if data["tool_states"].get(t, {}).get("in_progress") is not None
    ]


# ---------------------------------------------------------------------------
# One-shot text output (no rich)
# ---------------------------------------------------------------------------


def print_snapshot(data: dict, watcher: ResultsWatcher) -> None:
    target = data.get("target_rounds", "?")
    thinking = data.get("thinking", False)
    print(f"\n=== E2E Monitor  run_id={data.get('run_id', '?')} ===")
    print(f"Target: {target} rounds  Thinking: {thinking}\n")
    print(f"{'Tool':<16} {'Done':>5} {'Fail':>5} {'Rem':>5} {'Status':<10}")
    print("-" * 50)
    for tool in data.get("tools", ALL_TOOLS):
        ts = data["tool_states"].get(tool, {})
        completed = ts.get("completed", [])
        ok = sum(1 for r in completed if r.get("exit_code") == 0)
        ng = sum(1 for r in completed if r.get("exit_code") != 0)
        rem = max(0, int(target) - len(completed))
        status = ts.get("status", "pending")
        print(f"{tool:<16} {ok:>5} {ng:>5} {rem:>5} {status:<10}")
    print()


# ---------------------------------------------------------------------------
# Main monitor loop
# ---------------------------------------------------------------------------


def run_monitor(run_id: Optional[str], tool_filter: Optional[str], tail_n: int, once: bool) -> None:
    reader = StateReader(run_id)
    watcher = ResultsWatcher()

    if not _RICH or once:
        data = reader.load()
        if data is None:
            print("No run state found. Start a run with e2e_runner.py first.")
            return
        watcher.refresh()
        print_snapshot(data, watcher)

        if not once:
            log_dir = reader.log_dir()
            for tool in (data.get("tools", ALL_TOOLS) if not tool_filter else [tool_filter]):
                tailer = LogTailer(tool, log_dir, n=tail_n)
                print(f"\n--- {tool} log ---")
                for line in tailer.tail():
                    print(line)
        return

    # --- Rich Live TUI ---
    console = Console()
    refresh_secs = 3

    with Live(console=console, refresh_per_second=1, screen=False) as live:
        while True:
            data = reader.load()
            watcher.refresh()

            if data is None:
                live.update(Panel("[yellow]No run state found. Start e2e_runner.py first.[/yellow]"))
                time.sleep(refresh_secs)
                continue

            log_dir = reader.log_dir()
            running = _running_tools(data)
            display_tools = [tool_filter] if tool_filter else (running or data.get("tools", ALL_TOOLS))

            # Header
            run_id_str = data.get("run_id", "?")
            target = data.get("target_rounds", "?")
            thinking = "ON" if data.get("thinking") else "OFF"
            now_str = datetime.now().strftime("%H:%M:%S")
            header = Text(
                f"E2E Monitor  run_id={run_id_str}  target={target}R  thinking={thinking}  [{now_str}]",
                style="bold",
            )

            # Progress table
            prog_panel = Panel(_make_progress_table(data), title="Round Progress", border_style="green")

            # Log panels for running (or filtered) tools
            log_panels = []
            for tool in display_tools[:3]:  # max 3 side-by-side panels
                tailer = LogTailer(tool, log_dir, n=tail_n)
                log_panels.append(_make_log_panel(tool, tailer.tail(), tail_n))

            # Timeline
            timeline_panel = _make_timeline_panel(watcher.events_tail(15))

            # Compose layout
            from rich.console import Group
            from rich import print as rprint

            renderables = [header, prog_panel]
            if log_panels:
                renderables.append(Columns(log_panels, equal=True, expand=True))
            renderables.append(timeline_panel)
            live.update(Group(*renderables))

            # Check if all done
            all_done = all(
                data["tool_states"].get(t, {}).get("status") == "done"
                for t in data.get("tools", ALL_TOOLS)
            )
            if all_done:
                time.sleep(1)
                break

            time.sleep(refresh_secs)

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
    p.add_argument("--tool", help="Focus on a specific tool's log")
    p.add_argument("--tail", type=int, default=20, help="Number of log lines to show (default: 20)")
    p.add_argument("--once", action="store_true", help="Print snapshot once and exit (no live update)")
    return p


def main() -> int:
    args = build_parser().parse_args()
    run_monitor(args.run_id, args.tool, args.tail, args.once)
    return 0


if __name__ == "__main__":
    sys.exit(main())
