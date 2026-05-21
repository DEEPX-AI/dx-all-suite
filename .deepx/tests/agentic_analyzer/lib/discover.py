"""Scan e2e-tests/results/ to enumerate sessions and group them into rounds.

Layout (current, run-id keyed):
  - results/<run_id>/<YYYYMMDD>_<HHMMSS>_<hash>_<tool>-autopilot/manifest.json

Legacy flat layout (still readable; treated as run_id="legacy"):
  - results/<YYYYMMDD>_<HHMMSS>_<hash>_<tool>-autopilot/manifest.json

A "round" is the N-th occurrence (sorted by timestamp) of a tool within a
single run_id — different run-ids have independent round counters so R1 of
run-A and R1 of run-B do not collide.
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
    run_id: str = "legacy"   # parent run_id (results/<run_id>/...); "legacy" for flat layout
    round_index: int = 0     # 1-based round index per (run_id, tool)
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
    secondary_jsonl: Optional[Path] = None  # Codex: persistent JSONL (timestamps, model)
    output_dirs: List[Path] = field(default_factory=list)  # symlink targets → dx-agentic-dev/<sid>/
    output_dir_names: List[str] = field(default_factory=list)  # session_id portion


def _resolve_tool(tool_dir_suffix: str, tools_cfg: dict) -> Optional[str]:
    for name, conf in tools_cfg.items():
        if conf.get("dir_suffix") == tool_dir_suffix:
            return name
    return None


def _read_session_dir(entry: Path, run_id: str, tools_cfg: dict) -> Optional[ResultDir]:
    """Parse a single session directory into a ResultDir, or None if not a session."""
    if not entry.is_dir():
        return None
    m = SESSION_DIR_RE.match(entry.name)
    if not m:
        return None
    manifest_path = entry / "manifest.json"
    if not manifest_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        manifest = {}
    tool = _resolve_tool(m.group("tool_dir"), tools_cfg) or m.group("tool_dir")
    return ResultDir(
        session_id=entry.name,
        path=entry,
        timestamp=f"{m.group('date')}_{m.group('time')}",
        tool=tool,
        run_id=run_id,
        manifest=manifest,
    )


def discover_result_dirs(
    results_root: Path,
    tools_cfg: dict,
    run_ids: Optional[List[str]] = None,
) -> List[ResultDir]:
    """Scan results/ → list of ResultDir, each with manifest loaded.

    Supports both layouts simultaneously:
      - Nested: results/<run_id>/<session>/manifest.json
      - Legacy flat: results/<session>/manifest.json  (treated as run_id="legacy")

    If *run_ids* is given, only those run_ids (and "legacy") are scanned.
    """
    rds: List[ResultDir] = []
    if not results_root.is_dir():
        return rds

    run_id_filter = set(run_ids) if run_ids else None

    for entry in sorted(results_root.iterdir()):
        if not entry.is_dir():
            continue
        # Case 1: nested layout — entry is a run_id directory
        if SESSION_DIR_RE.match(entry.name):
            # Case 2: legacy flat session dir directly under results/
            if run_id_filter and "legacy" not in run_id_filter:
                continue
            rd = _read_session_dir(entry, run_id="legacy", tools_cfg=tools_cfg)
            if rd is not None:
                rds.append(rd)
        else:
            # Nested run_id directory
            run_id = entry.name
            if run_id_filter and run_id not in run_id_filter:
                continue
            for sess_entry in sorted(entry.iterdir()):
                rd = _read_session_dir(sess_entry, run_id=run_id, tools_cfg=tools_cfg)
                if rd is not None:
                    rds.append(rd)
    return rds


def assign_round_indices(rds: List[ResultDir]) -> None:
    """For each (run_id, tool), assign 1-based round index by chronological order.

    Different run_ids have independent round counters so R1 across runs does
    not collide.
    """
    by_key: Dict[tuple, List[ResultDir]] = {}
    for rd in rds:
        by_key.setdefault((rd.run_id, rd.tool), []).append(rd)
    for key, lst in by_key.items():
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
            elif name.endswith(".jsonl"):
                # stream.jsonl (claude-code, cursor, opencode), events-<uuid>.jsonl (copilot),
                # or *-codex-session.jsonl / *-codex-persistent.jsonl (codex-cli)
                is_codex_jsonl = "codex" in name
                if is_codex_jsonl and "persistent" in name:
                    # Codex persistent format (timestamps, model) — must check before "stream"
                    # because dx_stream-codex-persistent.jsonl contains "stream" as substring
                    ref.secondary_jsonl = full
                elif is_codex_jsonl and "session" in name:
                    # Codex exec format (turn.completed with usage)
                    if ref.stream_jsonl is None:
                        ref.stream_jsonl = full
                elif "stream" in name or "events" in name:
                    ref.stream_jsonl = full
        # Filesystem fallback: if transcript_md missing but files exist on disk
        # (e.g., retroactively generated MDs not in manifest)
        if ref.transcript_md is None and art_path.is_dir():
            for candidate in art_path.iterdir():
                if candidate.suffix == ".md" and "session" in candidate.name:
                    ref.transcript_md = candidate
                    break
        if ref.transcript_html is None and art_path.is_dir():
            for candidate in art_path.iterdir():
                if candidate.suffix == ".html" and "session" in candidate.name:
                    ref.transcript_html = candidate
                    break
        out.append(ref)

    # Fallback: if suite scenario has no output_dirs, derive from compiler + dx_app
    suite_refs = [r for r in out if r.scenario == "suite" and not r.output_dirs]
    if suite_refs:
        comp_refs = [r for r in out if r.scenario == "compiler"]
        app_refs = [r for r in out if r.scenario == "dx_app"]
        for sr in suite_refs:
            derived_dirs = []
            derived_names = []
            if comp_refs:
                derived_dirs.extend(comp_refs[0].output_dirs)
                derived_names.extend(comp_refs[0].output_dir_names)
            if app_refs:
                derived_dirs.extend(app_refs[0].output_dirs)
                derived_names.extend(app_refs[0].output_dir_names)
            if derived_dirs:
                sr.output_dirs = derived_dirs
                sr.output_dir_names = derived_names

    return out


def discover_all(
    results_root: Path,
    tools_cfg: dict,
    scenarios_cfg: dict,
    run_ids: Optional[List[str]] = None,
) -> List[ScenarioRef]:
    """Top-level entry: enumerate every (result_dir, scenario) pair with round indices set.

    If *run_ids* is provided, only those run_ids are scanned (multiple → aggregated).
    """
    rds = discover_result_dirs(results_root, tools_cfg, run_ids=run_ids)
    assign_round_indices(rds)
    all_scenarios: List[ScenarioRef] = []
    for rd in rds:
        all_scenarios.extend(extract_scenarios(rd, tools_cfg, scenarios_cfg))
    return all_scenarios
