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
from datetime import datetime
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

    def tail(self) -> List[str]:
        p = self._path
        if p is None:
            return [f"(no log for {self.tool})"]
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
            return lines[-self.n:]
        except Exception as exc:
            return [f"(error reading log: {exc})"]

    def parse_scenario_status(self) -> Dict[str, str]:
        """Parse log to determine per-scenario status for current round.

        Returns dict: scenario_key -> "done"/"running"/"pending"
        """
        p = self._path
        result = {k: "pending" for k in SCENARIO_KEYS}
        if p is None:
            return result
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return result

        # Find the last "Round N" marker to scope to current round
        lines = content.splitlines()
        last_round_idx = 0
        for i, line in enumerate(lines):
            if "Round " in line and "START" in line:
                last_round_idx = i

        # Scan from last round start
        current_round_lines = "\n".join(lines[last_round_idx:])

        # Detect which scenarios have started / finished
        # Pattern: test file path appears when scenario starts executing
        # "PASSED" or "FAILED" after test lines means done
        started = set()
        finished = set()

        for line in lines[last_round_idx:]:
            for key, pattern in SCENARIO_FILE_PATTERNS.items():
                if pattern in line:
                    started.add(key)
                    if "PASSED" in line or "FAILED" in line:
                        finished.add(key)

        # Also check for "passed" / "failed" summary at end
        for key in started:
            if key in finished:
                result[key] = "done"
            else:
                result[key] = "running"

        # The first non-finished started scenario is "running", rest of started are "done"
        # Actually: pytest runs sequentially, so only one can be truly "running"
        running_found = False
        for key in SCENARIO_KEYS:
            if key in started and key not in finished:
                if not running_found:
                    result[key] = "running"
                    running_found = True
                else:
                    result[key] = "running"  # shouldn't happen in sequential

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
    tbl.add_column("Scenarios (current round)", min_width=40)

    target = data.get("target_rounds", "?")
    for tool in data.get("tools", ALL_TOOLS):
        ts = data["tool_states"].get(tool, {})
        completed = ts.get("completed", [])
        ok = sum(1 for r in completed if r.get("exit_code") == 0)
        ng = sum(1 for r in completed if r.get("exit_code") != 0)
        rem = max(0, int(target) - len(completed))
        status = ts.get("status", "pending")

        status_style = {
            "done": "[green]done[/green]",
            "running": "[yellow]running[/yellow]",
            "pending": "[dim]pending[/dim]",
        }.get(status, status)

        # Parse scenario progress from log
        scenario_str = ""
        if status == "running" and log_dir:
            tailer = LogTailer(tool, log_dir, n=4)
            scenarios = tailer.parse_scenario_status()
            parts = []
            for key in SCENARIO_KEYS:
                s = scenarios[key]
                if s == "done":
                    parts.append(f"[green]✓{key}[/green]")
                elif s == "running":
                    parts.append(f"[yellow]▶{key}[/yellow]")
                else:
                    parts.append(f"[dim]·{key}[/dim]")
            scenario_str = " ".join(parts)
        elif status == "done":
            scenario_str = "[green]all complete[/green]"

        tbl.add_row(
            tool,
            str(ok),
            str(ng) if ng else "—",
            str(rem) if rem > 0 else "✓",
            Text.from_markup(status_style),
            Text.from_markup(scenario_str),
        )
    return tbl


def _make_log_panel(tool: str, lines: List[str], n: int = 4) -> Panel:
    content = "\n".join(lines[-n:]) or "(no output yet)"
    return Panel(content, title=f"[bold]{tool}[/bold] — tail log", border_style="blue")


# ---------------------------------------------------------------------------
# One-shot text output (no rich)
# ---------------------------------------------------------------------------


def print_snapshot(data: dict) -> None:
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

    if not _RICH or once:
        data = reader.load()
        if data is None:
            print("No run state found. Start a run with e2e_runner.py first.")
            return
        print_snapshot(data)

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

            if data is None:
                live.update(Panel("[yellow]No run state found. Start e2e_runner.py first.[/yellow]"))
                time.sleep(refresh_secs)
                continue

            log_dir = reader.log_dir()

            # Header
            run_id_str = data.get("run_id", "?")
            target = data.get("target_rounds", "?")
            thinking = "ON" if data.get("thinking") else "OFF"
            now_str = datetime.now().strftime("%H:%M:%S")
            header = Text(
                f"E2E Monitor  run_id={run_id_str}  target={target}R  thinking={thinking}  [{now_str}]",
                style="bold",
            )

            # Progress table (with scenario status)
            prog_panel = Panel(_make_progress_table(data, log_dir), title="Round Progress", border_style="green")

            # Log panels for ALL tools (or filtered)
            display_tools = [tool_filter] if tool_filter else data.get("tools", ALL_TOOLS)
            log_panels = []
            for tool in display_tools:
                tailer = LogTailer(tool, log_dir, n=tail_n)
                log_panels.append(_make_log_panel(tool, tailer.tail(), tail_n))

            # Compose layout
            from rich.console import Group

            renderables = [header, prog_panel]
            if log_panels:
                renderables.append(Columns(log_panels, equal=True, expand=True))
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
    p.add_argument("--tail", type=int, default=4, help="Number of log lines to show (default: 4)")
    p.add_argument("--once", action="store_true", help="Print snapshot once and exit (no live update)")
    return p


def main() -> int:
    args = build_parser().parse_args()
    run_monitor(args.run_id, args.tool, args.tail, args.once)
    return 0


if __name__ == "__main__":
    sys.exit(main())
