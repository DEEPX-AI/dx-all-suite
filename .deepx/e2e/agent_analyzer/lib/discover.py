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

# DONE sentinel from agent's session log — the authoritative list of output
# directories the agent produced. Multi-path entries (cross-project suite)
# are separated by " + " per the contract in CLAUDE.md.
DONE_SENTINEL_RE = re.compile(r'\[DX-AGENT-DEV: DONE \(output-dir: ([^)]+)\)\]')


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
    # Runner-supplied metadata (extracted from manifest fields written by
    # conftest.pytest_sessionfinish or backfilled retroactively). Empty strings
    # / dicts when the manifest predates the metadata schema.
    mode: str = ""                          # "NT" / "TH" / "NA" / ""
    intended_models: dict = field(default_factory=dict)
    thinking_env_applied: dict = field(default_factory=dict)


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
    output_dirs: List[Path] = field(default_factory=list)  # symlink targets → dx-agent-dev/<sid>/
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
        mode=str(manifest.get("mode") or "").strip(),
        intended_models=dict(manifest.get("intended_models") or {}),
        thinking_env_applied=dict(manifest.get("thinking_env_applied") or {}),
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
    """Assign 1-based round_index per tool with run_id-aware offsets.

    Single-run-id case: per-tool R1..Rn (chronological) — unchanged.
    Multi-run-id case: each tool gets a single continuous round counter that
    spans every run_id in chronological run-order. E.g. run A has 5 rounds,
    run B has 5 → tool sees R1..R5 from A then R6..R10 from B. This prevents
    the (round, tool) aggregation from collapsing R1@A with R1@B in §5/§6
    round-by-round tables.
    """
    # First, order run_ids by their earliest session timestamp so the
    # offset is deterministic (oldest run gets R1..Rn, next run continues).
    run_id_first_ts: Dict[str, str] = {}
    for rd in rds:
        prev = run_id_first_ts.get(rd.run_id)
        if prev is None or rd.timestamp < prev:
            run_id_first_ts[rd.run_id] = rd.timestamp
    ordered_run_ids = sorted(run_id_first_ts.keys(), key=lambda r: run_id_first_ts[r])

    # Group by tool, then iterate run_ids in order, accumulating round offset.
    by_tool: Dict[str, List[ResultDir]] = {}
    for rd in rds:
        by_tool.setdefault(rd.tool, []).append(rd)

    for tool, lst in by_tool.items():
        offset = 0
        for run_id in ordered_run_ids:
            sub = sorted(
                (rd for rd in lst if rd.run_id == run_id),
                key=lambda r: r.timestamp,
            )
            for i, rd in enumerate(sub, start=1):
                rd.round_index = offset + i
            offset += len(sub)


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
                if target.parts and "dx-agent-dev" in target.parts:
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

    # Filter each ref's output_dirs by DONE sentinel when present. Agents that
    # retry a scenario produce multiple dx-agent-dev/<sid>/ directories within
    # the test's time window; conftest captures all of them as symlinks, so
    # output_dirs ends up with both the abandoned attempts and the final ones.
    # The DONE sentinel emitted by the agent is the authoritative list — anything
    # not mentioned there should not contribute to downstream evaluation (Runn,
    # Quality, ExecutionTrace). No-op when no sentinel is found.
    for r in out:
        _filter_output_dirs_by_done_sentinel(r)

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


def _parse_done_sentinel_paths(ref: "ScenarioRef") -> List[str]:
    """Return the list of output-dir paths declared by the agent's DONE sentinel.

    Searches the session transcript (markdown) and the stream JSONL for the
    sentinel pattern. Multi-path entries (separated by " + ") are split and
    returned as a list of relative paths. Empty list if no sentinel is found.
    """
    sources: List[Path] = []
    if ref.transcript_md is not None:
        sources.append(ref.transcript_md)
    if ref.stream_jsonl is not None:
        sources.append(ref.stream_jsonl)
    for src in sources:
        if not src.is_file():
            continue
        try:
            text = src.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m = DONE_SENTINEL_RE.search(text)
        if not m:
            continue
        return [p.strip() for p in m.group(1).split(" + ") if p.strip()]
    return []


def _filter_output_dirs_by_done_sentinel(ref: "ScenarioRef") -> None:
    """Restrict ref.output_dirs to directories named in the DONE sentinel,
    OR recover them from the sentinel when no symlinks were captured.

    Three behaviors depending on input state:
      1. output_dirs non-empty + sentinel present → filter (suffix match).
      2. output_dirs empty + sentinel present → **fallback**: resolve sentinel
         relative paths against suite root and add existing dirs to output_dirs.
         Recovers the "agent reused a pre-existing dir which conftest didn't
         classify as new" bug (see plan: Root-Cause Fix — Agent Reuse).
      3. output_dirs empty + no sentinel → no-op (downstream sees empty).

    Matching is suffix-based: an output_dir is kept if any sentinel path
    appears as a suffix of its absolute path. Falls back to the original
    (unfiltered) list when filtering would leave zero output_dirs (defensive
    — never drop everything for case 1).
    """
    sentinel_paths = _parse_done_sentinel_paths(ref)

    # Case 2: fallback recovery — output_dirs is empty (symlink omitted because
    # the agent reused a pre-existing dx-agent-dev/<sid>/ dir that conftest's
    # _detect_new_sessions did not classify as "new"). Use the agent's DONE
    # sentinel as the authoritative claim of what it produced.
    if not ref.output_dirs:
        if not sentinel_paths:
            return
        # Resolve suite root by walking up from artifact_path until both
        # 'dx-compiler' and 'dx-runtime' siblings exist.
        suite_root: Optional[Path] = None
        cur = ref.artifact_path.resolve() if ref.artifact_path else None
        while cur is not None and cur != cur.parent:
            if (cur / "dx-compiler").is_dir() and (cur / "dx-runtime").is_dir():
                suite_root = cur
                break
            cur = cur.parent
        if suite_root is None:
            return
        # Agent's sentinel path may be relative to either suite root or to a
        # sub-project workdir (dx-compiler/, dx-runtime/, dx-runtime/dx_app/,
        # dx-runtime/dx_stream/). Try each base in turn.
        sub_bases = [
            suite_root,
            suite_root / "dx-compiler",
            suite_root / "dx-runtime",
            suite_root / "dx-runtime" / "dx_app",
            suite_root / "dx-runtime" / "dx_stream",
        ]
        for sp in sentinel_paths:
            p_norm = sp.strip().replace("\\", "/").rstrip("/")
            if not p_norm:
                continue
            if p_norm.startswith("/"):
                cand = Path(p_norm)
                if cand.is_dir():
                    ref.output_dirs.append(cand)
                    ref.output_dir_names.append(cand.name)
                continue
            for base in sub_bases:
                cand = base / p_norm
                if cand.is_dir():
                    ref.output_dirs.append(cand)
                    ref.output_dir_names.append(cand.name)
                    break
        return

    # Case 1: filter existing list by sentinel
    if not sentinel_paths:
        return  # no sentinel → preserve current behavior

    filtered_dirs: List[Path] = []
    filtered_names: List[str] = []
    for od, name in zip(ref.output_dirs, ref.output_dir_names):
        od_str = str(od).replace("\\", "/").rstrip("/")
        kept = False
        for sp in sentinel_paths:
            sp_norm = sp.replace("\\", "/").rstrip("/")
            # Either the full sentinel path is a suffix of the absolute
            # output_dir path, or the directory name itself matches the
            # tail of the sentinel path. The second form catches cases
            # where sentinel was written with a slightly different prefix.
            if od_str.endswith(sp_norm) or sp_norm.endswith("/" + name) or sp_norm == name:
                kept = True
                break
        if kept:
            filtered_dirs.append(od)
            filtered_names.append(name)

    # Never produce an empty list — when the sentinel paths fail to match any
    # captured dir (mis-typed by the agent, normalization mismatch, etc.) we
    # silently fall back to the original list so downstream eval still runs.
    if filtered_dirs:
        ref.output_dirs = filtered_dirs
        ref.output_dir_names = filtered_names


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
