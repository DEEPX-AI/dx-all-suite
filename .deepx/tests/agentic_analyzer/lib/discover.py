"""Scan e2e-tests/results/ to enumerate sessions and group them into rounds.

A "round" is the N-th occurrence (sorted by timestamp) of a tool's autopilot run.
Sub-projects:
  - results/<YYYYMMDD>_<HHMMSS>_<hash>_<tool>-autopilot/manifest.json
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# session_id format: 20260511_194755_d31c86_cursor-cli-autopilot
SESSION_DIR_RE = re.compile(
    r"^(?P<date>\d{8})_(?P<time>\d{6})_(?P<hash>[a-f0-9]{6})_(?P<tool_dir>.+-autopilot)$"
)


@dataclass
class ResultDir:
    """A single autopilot run for one tool (contains all scenarios)."""
    session_id: str          # 20260511_194755_d31c86_cursor-cli-autopilot
    path: Path
    timestamp: str           # 20260511_194755
    tool: str                # cursor-cli (resolved from config)
    round_index: int = 0     # 1-based round index per tool
    manifest: dict = field(default_factory=dict)


@dataclass
class ScenarioRef:
    """One scenario within a result dir (e.g., compiler / dx_app / dx_stream / ...)."""
    parent: ResultDir
    scenario: str            # compiler, dx_app, dx_stream, dx_stream_cascaded, runtime, suite
    artifact_key: str        # e.g., "cursor_cli__compiler"
    artifact_path: Path      # e2e-tests/.../autopilot/<timestamp>/
    transcript_md: Optional[Path] = None
    transcript_html: Optional[Path] = None
    stream_jsonl: Optional[Path] = None
    output_dirs: List[Path] = field(default_factory=list)  # symlink targets → dx-agentic-dev/<sid>/
    output_dir_names: List[str] = field(default_factory=list)  # session_id portion


def _resolve_tool(tool_dir_suffix: str, tools_cfg: dict) -> Optional[str]:
    for name, conf in tools_cfg.items():
        if conf.get("dir_suffix") == tool_dir_suffix:
            return name
    return None


def discover_result_dirs(results_root: Path, tools_cfg: dict) -> List[ResultDir]:
    """Scan results/ → list of ResultDir, each with manifest loaded."""
    rds: List[ResultDir] = []
    if not results_root.is_dir():
        return rds
    for entry in sorted(results_root.iterdir()):
        if not entry.is_dir():
            continue
        m = SESSION_DIR_RE.match(entry.name)
        if not m:
            continue
        manifest_path = entry / "manifest.json"
        if not manifest_path.is_file():
            continue
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            manifest = {}
        tool = _resolve_tool(m.group("tool_dir"), tools_cfg) or m.group("tool_dir")
        rds.append(
            ResultDir(
                session_id=entry.name,
                path=entry,
                timestamp=f"{m.group('date')}_{m.group('time')}",
                tool=tool,
                manifest=manifest,
            )
        )
    return rds


def assign_round_indices(rds: List[ResultDir]) -> None:
    """For each tool, assign 1-based round index by chronological order."""
    by_tool: Dict[str, List[ResultDir]] = {}
    for rd in rds:
        by_tool.setdefault(rd.tool, []).append(rd)
    for tool, lst in by_tool.items():
        lst.sort(key=lambda r: r.timestamp)
        for i, rd in enumerate(lst, start=1):
            rd.round_index = i


def extract_scenarios(rd: ResultDir, tools_cfg: dict, scenarios_cfg: dict) -> List[ScenarioRef]:
    """For a ResultDir, return list of ScenarioRef (one per scenario key in manifest)."""
    out: List[ScenarioRef] = []
    artifacts = rd.manifest.get("artifacts", {})
    tool_conf = tools_cfg.get(rd.tool, {})
    prefix = tool_conf.get("artifact_prefix", "")
    for key, info in artifacts.items():
        # key examples: cursor_cli__compiler, claude_code__suite
        if prefix and key.startswith(prefix + "__"):
            scenario = key[len(prefix) + 2:]  # strip "<prefix>__"
        else:
            # fallback: split on '__'
            parts = key.split("__", 1)
            scenario = parts[1] if len(parts) == 2 else key
        if scenario not in scenarios_cfg:
            # Unknown scenario — keep as-is for visibility
            pass
        art_path = Path(info.get("path", ""))
        ref = ScenarioRef(
            parent=rd,
            scenario=scenario,
            artifact_key=key,
            artifact_path=art_path,
        )
        # Walk contents to find transcript/stream/output symlinks
        for c in info.get("contents", []):
            name = c.get("name", "")
            ctype = c.get("type", "")
            full = art_path / name
            if ctype == "symlink":
                target = Path(c.get("target", ""))
                if target.parts and "dx-agentic-dev" in target.parts:
                    ref.output_dirs.append(target)
                    ref.output_dir_names.append(target.name)
            elif name.endswith(".md") and "session" in name:
                ref.transcript_md = full
            elif name.endswith(".html") and "session" in name:
                ref.transcript_html = full
            elif name.endswith(".jsonl") and ("stream" in name or "events" in name):
                # stream.jsonl (claude-code, cursor, opencode) or events-<uuid>.jsonl (copilot)
                ref.stream_jsonl = full
        out.append(ref)
    return out


def discover_all(results_root: Path, tools_cfg: dict, scenarios_cfg: dict) -> List[ScenarioRef]:
    """Top-level entry: enumerate every (result_dir, scenario) pair with round indices set."""
    rds = discover_result_dirs(results_root, tools_cfg)
    assign_round_indices(rds)
    all_scenarios: List[ScenarioRef] = []
    for rd in rds:
        all_scenarios.extend(extract_scenarios(rd, tools_cfg, scenarios_cfg))
    return all_scenarios
