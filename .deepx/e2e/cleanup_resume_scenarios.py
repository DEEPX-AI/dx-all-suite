# SPDX-License-Identifier: Apache-2.0
"""Scenario-level cleanup + targeted re-run + merge-back within a single e2e round.

Problem: e2e_runner operates at the round level — redo/resume re-runs ALL scenarios
in a round. This tool salvages the VALID scenarios in a round and re-runs only the
env-failed (rate-limit) ones, merging the new results back into the original round dir
so it becomes 6 valid scenarios.

Usage (dry-run):
  python .deepx/e2e/cleanup_resume_scenarios.py \\
    --run-id 20260612_194959 \\
    --round-dir 20260612_215200_eb135a_claude-code-autopilot \\
    --scenarios runtime,suite \\
    --tool claude-code \\
    --dry-run

Usage (real):
  python .deepx/e2e/cleanup_resume_scenarios.py \\
    --run-id 20260612_194959 \\
    --round-dir 20260612_215200_eb135a_claude-code-autopilot \\
    --scenarios runtime,suite \\
    --tool claude-code \\
    --model claude-sonnet-4-6

The runner_fn is injected for testability. In real mode it runs
  DX_RUN_ID=<run_id> <model env> bash .deepx/e2e/test.sh <cmd> -k "<scenario exprs>"
and locates the new partial round dir via find_newest_autopilot_dir().
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = (SCRIPT_DIR / "../..").resolve()
TEST_SH = SCRIPT_DIR / "test.sh"
RESULTS_ROOT = REPO_ROOT / "dx-agent-dev/e2e-tests/results"
RUNNER_STATE_DIR = SCRIPT_DIR / "runner_state"

# Mapping: tool → artifact key prefix (used in subdir names and manifest keys)
TOOL_PREFIX: Dict[str, str] = {
    "claude-code":   "claude_code",
    "copilot-cli":   "copilot_cli",
    "cursor-cli":    "cursor_cli",
    "opencode-cli":  "opencode_cli",
    "codex-cli":     "codex_cli",
}

# test.sh command name for each tool (mirrors e2e_runner.TOOL_CMD)
TOOL_CMD: Dict[str, str] = {
    "claude-code":  "agent-driven-e2e-claude-code-autopilot",
    "copilot-cli":  "agent-driven-e2e-copilot-cli-autopilot",
    "cursor-cli":   "agent-driven-e2e-cursor-cli-autopilot",
    "opencode-cli": "agent-driven-e2e-opencode-cli-autopilot",
    "codex-cli":    "agent-driven-e2e-codex-cli-autopilot",
}

# Per-tool model env var name
TOOL_MODEL_ENV: Dict[str, str] = {
    "claude-code":  "DX_AGENT_E2E_CLAUDE_CODE_MODEL",
    "copilot-cli":  "DX_AGENT_E2E_COPILOT_MODEL",
    "cursor-cli":   "DX_AGENT_E2E_CURSOR_MODEL",
    "opencode-cli": "DX_AGENT_E2E_OPENCODE_MODEL",
    "codex-cli":    "DX_AGENT_E2E_CODEX_MODEL",
}

# Per-tool thinking/high-reasoning env vars (mirrors e2e_runner.THINKING_ENV)
TOOL_THINKING_ENV: Dict[str, Dict[str, str]] = {
    "claude-code":  {"DX_AGENT_E2E_CLAUDE_CODE_EXTRA_ARGS": "--effort xhigh"},
    "copilot-cli":  {"DX_AGENT_E2E_COPILOT_EXTRA_ARGS": "--effort xhigh"},
    "opencode-cli": {"DX_AGENT_E2E_OPENCODE_EXTRA_ARGS": "--variant high"},
    "codex-cli":    {"DX_AGENT_E2E_CODEX_EXTRA_ARGS": '-c model_reasoning_effort="xhigh"'},
    "cursor-cli":   {},
}

ALL_SCENARIOS = ["compiler", "dx_app", "dx_stream", "dx_stream_cascaded", "runtime", "suite"]


# ---------------------------------------------------------------------------
# Salvage status file helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    """Return current local time as ISO-8601 string (no UTC offset needed for display)."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _write_salvage_status(run_id: str, **fields) -> None:
    """Write/merge fields into RUNNER_STATE_DIR/<run_id>/salvage.json.

    Refreshes ``updated_at`` on every call. Creates the state dir if absent.
    Existing fields not present in *fields* are preserved (merge semantics).

    Args:
        run_id: e2e run ID (directory name under RUNNER_STATE_DIR).
        **fields: Key-value pairs to set/overwrite in the salvage file.
    """
    state_dir = RUNNER_STATE_DIR / run_id
    state_dir.mkdir(parents=True, exist_ok=True)
    salvage_path = state_dir / "salvage.json"

    # Load existing content (tolerate missing/corrupt)
    existing: dict = {}
    if salvage_path.exists():
        try:
            existing = json.loads(salvage_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            existing = {}

    existing.update(fields)
    existing["updated_at"] = _now_iso()

    salvage_path.write_text(
        json.dumps(existing, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Pure, unit-testable functions
# ---------------------------------------------------------------------------

def scenario_subdir(round_dir: Path, prefix: str, scenario: str) -> Path:
    """Return the path to a scenario subdir: round_dir/{prefix}__{scenario}."""
    return round_dir / f"{prefix}__{scenario}"


def delete_scenarios(round_dir: Path, prefix: str, scenarios: List[str]) -> List[str]:
    """Delete scenario subdirs and remove them from manifest.json artifacts.

    For each scenario in *scenarios*:
    - rmtree the subdir ``{round_dir}/{prefix}__{scenario}`` if it exists
      (handles symlinks: removes the symlink itself, not the target)
    - remove the matching key from manifest.json's "artifacts" dict

    Returns the list of artifact keys that were actually removed (present
    in manifest before deletion). Missing scenarios are tolerated silently.
    """
    removed: List[str] = []

    # Load manifest (tolerate missing)
    manifest_path = round_dir / "manifest.json"
    manifest: dict = {}
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            manifest = {}

    artifacts: dict = manifest.get("artifacts", {})

    for scenario in scenarios:
        key = f"{prefix}__{scenario}"
        subdir = scenario_subdir(round_dir, prefix, scenario)

        # Remove the subdir (or symlink) if present
        if subdir.is_symlink():
            subdir.unlink()
        elif subdir.is_dir():
            shutil.rmtree(subdir)

        # Remove from manifest
        if key in artifacts:
            del artifacts[key]
            removed.append(key)

    # Write manifest back if we changed anything
    if removed and manifest_path.exists():
        manifest["artifacts"] = artifacts
        manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return removed


def merge_scenarios(
    round_dir: Path,
    source_dir: Path,
    prefix: str,
    scenarios: List[str],
) -> List[str]:
    """Move scenario subdirs from source_dir into round_dir and update manifest.

    For each scenario:
    - Move ``source_dir/{prefix}__{scenario}`` → ``round_dir/{prefix}__{scenario}``
      (replacing if already exists; uses shutil.move which preserves symlinks)
    - Copy that scenario's artifacts entry from source_dir/manifest.json into
      round_dir/manifest.json

    Returns the list of artifact keys that were successfully merged.
    """
    merged: List[str] = []

    # Load source manifest
    src_manifest_path = source_dir / "manifest.json"
    src_artifacts: dict = {}
    if src_manifest_path.exists():
        try:
            src_data = json.loads(src_manifest_path.read_text(encoding="utf-8"))
            src_artifacts = src_data.get("artifacts", {})
        except (json.JSONDecodeError, OSError):
            pass

    # Load destination manifest
    dst_manifest_path = round_dir / "manifest.json"
    dst_manifest: dict = {}
    if dst_manifest_path.exists():
        try:
            dst_manifest = json.loads(dst_manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            dst_manifest = {}
    dst_artifacts: dict = dst_manifest.get("artifacts", {})

    for scenario in scenarios:
        key = f"{prefix}__{scenario}"
        src_subdir = source_dir / key
        dst_subdir = round_dir / key

        if not src_subdir.exists() and not src_subdir.is_symlink():
            continue  # source missing — skip

        # Remove destination if it already exists
        if dst_subdir.is_symlink():
            dst_subdir.unlink()
        elif dst_subdir.is_dir():
            shutil.rmtree(dst_subdir)

        # Move: shutil.move handles both regular dirs and symlinks
        shutil.move(str(src_subdir), str(dst_subdir))

        # Copy artifacts entry from source manifest
        if key in src_artifacts:
            dst_artifacts[key] = src_artifacts[key]

        merged.append(key)

    # Write updated destination manifest
    if merged and dst_manifest_path.exists():
        dst_manifest["artifacts"] = dst_artifacts
        dst_manifest_path.write_text(
            json.dumps(dst_manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    return merged


def classify_scenarios(
    round_dir: Path,
    prefix: str,
    scenarios: List[str],
) -> Dict[str, str]:
    """Return {scenario: verdict} using e2e_runner._classify_round_scenario.

    verdict is one of: "valid" | "incomplete" | "envfail" | "skip".
    Imports e2e_runner via sys.path — the same pattern used by test_e2e_runner_env_redo.py.
    """
    _ensure_e2e_runner_importable()
    import e2e_runner as er  # noqa: E402 (imported after sys.path setup)

    result: Dict[str, str] = {}
    for scenario in scenarios:
        subdir = scenario_subdir(round_dir, prefix, scenario)
        if subdir.exists() or subdir.is_symlink():
            verdict, _sigs = er._classify_round_scenario(subdir)
        else:
            verdict = "skip"
        result[scenario] = verdict
    return result


def find_newest_autopilot_dir(
    run_results_dir: Path,
    exclude: set,
) -> Optional[Path]:
    """Return the newest ``*-autopilot`` dir in *run_results_dir* not in *exclude*.

    Dirs are sorted by name (timestamp-prefixed: YYYYMMDD_HHMMSS_…). The newest
    is the lexicographically last. Returns None if no candidate found.
    """
    candidates = []
    for entry in run_results_dir.iterdir():
        if not entry.is_dir():
            continue
        if entry.name in exclude:
            continue
        if "autopilot" in entry.name and not entry.name.startswith(SUPERSEDED_PREFIX):
            candidates.append(entry)
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: p.name)[-1]


# ---------------------------------------------------------------------------
# Transcript reader helper
# ---------------------------------------------------------------------------

def _default_transcript_reader(round_dir: Path, scenarios: List[str]) -> str:
    """Concatenate all text files under the failed scenario subdirs for rate-limit parsing."""
    blobs: List[str] = []
    for entry in round_dir.iterdir():
        if not entry.is_dir():
            continue
        # Match any scenario in the failed list
        for scenario in scenarios:
            if entry.name.endswith(f"__{scenario}"):
                for f in entry.rglob("*"):
                    if f.is_file() and f.suffix in (".md", ".jsonl", ".log", ".txt", ".html"):
                        try:
                            blobs.append(f.read_text(encoding="utf-8", errors="ignore"))
                        except OSError:
                            pass
    return "\n".join(blobs)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def run_cleanup_resume(
    round_dir: Path,
    prefix: str,
    scenarios: List[str],
    *,
    runner_fn: Callable[[List[str]], Path],
    sleep_fn: Callable[[float], None] = time.sleep,
    now_fn: Callable[[], float] = time.time,
    transcript_reader: Callable[[Path, List[str]], str] = _default_transcript_reader,
    max_attempts: int = 4,
    fallback_wait: int = 3600,
    status_cb: Optional[Callable[..., None]] = None,
) -> Dict:
    """Delete env-failed scenarios, re-run them, merge back. Rate-limit resilient.

    Args:
        round_dir: The original round directory (e.g. results/<run_id>/<ts>_<hash>_<tool>-autopilot/).
        prefix: Artifact prefix (e.g. "claude_code").
        scenarios: Scenario names to re-run (e.g. ["runtime", "suite"]).
        runner_fn: Callable that runs the targeted scenarios via test.sh and returns
                   the Path of the new partial round dir.
        sleep_fn: Injected sleep (default: time.sleep). Used between retry attempts.
        now_fn: Injected time source (default: time.time).
        transcript_reader: Reads transcript text from failed scenario dirs for
                           rate-limit reset parsing.
        max_attempts: Maximum retry attempts before giving up.
        fallback_wait: Seconds to wait if no reset time can be parsed.
        status_cb: Optional callable(status, attempt, **extra) invoked at start, each
                   loop iteration after classify, and on terminal status. Injected so
                   callers can write salvage.json or capture calls in tests without
                   touching disk. Signature: ``status_cb(status=..., attempt=..., **kw)``.

    Returns:
        dict with keys:
          "status": "complete" | "max-attempts"
          "attempts": int
          "still_failed": list[str] (only present if status=="max-attempts")
    """
    _ensure_e2e_runner_importable()
    from e2e_resilient_run import parse_reset_seconds  # noqa: E402

    target_scenarios = list(scenarios)

    # Notify: salvage starting (attempt 1)
    if status_cb is not None:
        status_cb(status="running", attempt=1)

    for attempt in range(1, max_attempts + 1):
        # Notify current attempt (after first, update attempt counter)
        if status_cb is not None and attempt > 1:
            status_cb(status="running", attempt=attempt)

        # Step 1: delete the target scenarios from round_dir
        delete_scenarios(round_dir, prefix, target_scenarios)

        # Step 2: run only the failed scenarios
        partial_dir = runner_fn(target_scenarios)

        # Step 3: merge back into round_dir
        merge_scenarios(round_dir, partial_dir, prefix, target_scenarios)

        # Retire the scratch partial dir (scenarios merged out): remove if empty,
        # else rename with a superseded__ prefix so it is not discovered as a
        # phantom round and is clearly marked as a cleaned-up artifact.
        _supersede_partial_dir(partial_dir)

        # Step 4: classify the merged results
        verdicts = classify_scenarios(round_dir, prefix, target_scenarios)
        still_failed = [s for s in target_scenarios if verdicts.get(s) != "valid"]

        if not still_failed:
            if status_cb is not None:
                status_cb(status="complete", attempt=attempt)
            return {"status": "complete", "attempts": attempt}

        if attempt == max_attempts:
            break

        # Step 5: wait for rate-limit reset
        transcript_text = transcript_reader(round_dir, still_failed)
        wait = parse_reset_seconds(transcript_text, now_fn()) if transcript_text else None
        wait_secs = wait if (wait is not None) else fallback_wait
        print(
            f"[cleanup_resume] Attempt {attempt}: {still_failed} still envfail. "
            f"Waiting {wait_secs}s before retry...",
            flush=True,
        )
        sleep_fn(float(wait_secs))
        target_scenarios = still_failed

    if status_cb is not None:
        status_cb(status="max-attempts", attempt=max_attempts, still_failed=still_failed)
    return {"status": "max-attempts", "still_failed": still_failed, "attempts": max_attempts}


SUPERSEDED_PREFIX = "superseded__"


def _supersede_partial_dir(path: Path) -> None:
    """Retire the scratch partial round dir after its scenarios were merged out.

    ``merge_scenarios`` moves the re-run scenario subdirs INTO the canonical round
    dir, leaving the scratch dir with only ``manifest.json`` + ``SUMMARY.md``. That
    shell still matches the analyzer's round regex
    (``^<date>_<time>_<hash>_<tool>-autopilot$`` + a manifest) and would be
    discovered as a PHANTOM extra round.

    So: if the dir is now empty -> remove it; otherwise RENAME it with a
    ``superseded__`` prefix. The prefix (a) breaks the analyzer's ``^\\d{8}`` anchor
    so it is no longer discovered as a round, and (b) clearly marks it as a
    cleaned-up/merged artifact while preserving the re-run record (audit trail).
    """
    try:
        if not path.is_dir():
            return
        if not any(path.iterdir()):
            path.rmdir()
            return
        if path.name.startswith(SUPERSEDED_PREFIX):
            return
        path.rename(path.with_name(SUPERSEDED_PREFIX + path.name))
    except OSError:
        pass


# ---------------------------------------------------------------------------
# Sys.path helper (import e2e_runner without package install)
# ---------------------------------------------------------------------------

def _ensure_e2e_runner_importable() -> None:
    """Insert SCRIPT_DIR into sys.path so e2e_runner and e2e_resilient_run can be imported."""
    e2e_dir = str(SCRIPT_DIR)
    if e2e_dir not in sys.path:
        sys.path.insert(0, e2e_dir)


# ---------------------------------------------------------------------------
# Real runner_fn (used in CLI mode)
# ---------------------------------------------------------------------------

def _make_real_runner_fn(
    run_id: str,
    tool: str,
    model: Optional[str],
    thinking: bool,
) -> Callable[[List[str]], Path]:
    """Build a real runner_fn that invokes test.sh and returns the new partial dir."""

    run_results_dir = RESULTS_ROOT / run_id
    tool_cmd = TOOL_CMD[tool]

    def runner_fn(scenarios: List[str]) -> Path:
        # Snapshot existing autopilot dirs
        existing: set = set()
        if run_results_dir.is_dir():
            for entry in run_results_dir.iterdir():
                if entry.is_dir() and "autopilot" in entry.name:
                    existing.add(entry.name)

        # Build subprocess env
        env = os.environ.copy()
        env["DX_RUN_ID"] = run_id

        if model:
            model_env_key = TOOL_MODEL_ENV.get(tool)
            if model_env_key:
                env[model_env_key] = model

        if thinking:
            env.update(TOOL_THINKING_ENV.get(tool, {}))

        # Build the test.sh command
        k_expr = " or ".join(scenarios)
        cmd = ["bash", str(TEST_SH), tool_cmd, "-k", k_expr]

        print(f"[cleanup_resume] Running: DX_RUN_ID={run_id} {' '.join(cmd)}", flush=True)

        proc = subprocess.run(cmd, env=env, cwd=str(REPO_ROOT))
        print(
            f"[cleanup_resume] test.sh exited with code {proc.returncode}",
            flush=True,
        )

        # Find the new partial dir
        partial_dir = find_newest_autopilot_dir(run_results_dir, exclude=existing)
        if partial_dir is None:
            raise RuntimeError(
                f"Could not find new autopilot dir under {run_results_dir} "
                f"after running {cmd}"
            )
        return partial_dir

    return runner_fn


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _resolve_round_dir(run_id: str, round_dir_arg: str) -> Path:
    """Resolve round_dir from either an absolute path or a dir name under RESULTS_ROOT."""
    p = Path(round_dir_arg)
    if p.is_absolute():
        return p
    # Try under the run_id directory
    candidate = RESULTS_ROOT / run_id / round_dir_arg
    if candidate.is_dir():
        return candidate
    raise FileNotFoundError(
        f"Round dir not found: tried {candidate}. "
        f"Pass an absolute path or a name under results/{run_id}/."
    )


def _infer_prefix(tool: str, round_dir: Path) -> str:
    """Derive artifact prefix from TOOL_PREFIX, verifying against existing subdirs."""
    prefix = TOOL_PREFIX.get(tool)
    if prefix is None:
        # Fallback: replace hyphens and -cli suffix
        prefix = tool.replace("-cli", "").replace("-", "_")

    # Verify against existing round dir contents
    if round_dir.is_dir():
        existing_names = {p.name for p in round_dir.iterdir() if p.is_dir() or p.is_symlink()}
        guesses = [f"{prefix}__{s}" for s in ALL_SCENARIOS]
        if not any(g in existing_names for g in guesses):
            # Try alternative derivation
            alt = tool.replace("-", "_")
            alt_guesses = [f"{alt}__{s}" for s in ALL_SCENARIOS]
            if any(g in existing_names for g in alt_guesses):
                prefix = alt

    return prefix


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Scenario-level cleanup + re-run + merge-back within a single e2e round. "
            "Deletes env-failed scenario subdirs from a round dir, re-runs only those "
            "scenarios via test.sh -k, and merges the new results back — leaving the "
            "original round dir with a complete set of valid scenarios."
        )
    )
    parser.add_argument(
        "--run-id", required=True,
        help="e2e run ID (e.g. 20260612_194959). Round dir lives under results/<run-id>/.",
    )
    parser.add_argument(
        "--round-dir", required=True,
        help=(
            "Round dir name (e.g. 20260612_215200_eb135a_claude-code-autopilot) "
            "or absolute path."
        ),
    )
    parser.add_argument(
        "--scenarios", required=True,
        help=(
            "Comma-separated scenario names to re-run (e.g. runtime,suite) "
            "or 'all' to re-run all scenarios."
        ),
    )
    parser.add_argument(
        "--tool", default="claude-code",
        choices=list(TOOL_CMD.keys()),
        help="Tool whose scenarios to re-run (default: claude-code).",
    )
    parser.add_argument(
        "--model", default=None,
        help="Override the backend model (sets per-tool DX_AGENT_E2E_*_MODEL env var).",
    )
    parser.add_argument(
        "--thinking", action="store_true",
        help="Enable high-reasoning/thinking mode (injects THINKING_ENV extra-args).",
    )
    parser.add_argument(
        "--max-attempts", type=int, default=4,
        help="Maximum retry attempts after rate-limit failures (default: 4).",
    )
    parser.add_argument(
        "--fallback-wait", type=int, default=3600,
        help="Seconds to wait between retries if no reset time is parseable (default: 3600).",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help=(
            "Print the planned delete list and exact test.sh command, execute nothing, exit 0."
        ),
    )

    args = parser.parse_args(argv)

    # Resolve round dir
    try:
        round_dir = _resolve_round_dir(args.run_id, args.round_dir)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Resolve scenarios
    if args.scenarios.lower() == "all":
        scenarios = ALL_SCENARIOS[:]
    else:
        scenarios = [s.strip() for s in args.scenarios.split(",") if s.strip()]

    # Derive prefix
    prefix = _infer_prefix(args.tool, round_dir)

    # Build the test.sh command string (for display/dry-run)
    k_expr = " or ".join(scenarios)
    tool_cmd = TOOL_CMD[args.tool]
    model_env_key = TOOL_MODEL_ENV.get(args.tool, "")
    model_env_str = f"{model_env_key}={args.model} " if args.model and model_env_key else ""
    thinking_env_str = ""
    if args.thinking:
        for k, v in TOOL_THINKING_ENV.get(args.tool, {}).items():
            thinking_env_str += f'{k}="{v}" '
    test_sh_cmd = (
        f"DX_RUN_ID={args.run_id} {model_env_str}{thinking_env_str}"
        f"bash .deepx/e2e/test.sh {tool_cmd} -k \"{k_expr}\""
    )

    if args.dry_run:
        print("=== DRY RUN — no changes will be made ===")
        print()
        print(f"Round dir  : {round_dir}")
        print(f"Prefix     : {prefix}")
        print(f"Scenarios to delete + re-run:")
        for s in scenarios:
            subdir = scenario_subdir(round_dir, prefix, s)
            exists = "EXISTS" if (subdir.exists() or subdir.is_symlink()) else "MISSING"
            print(f"  - {prefix}__{s}  [{exists}]")
        print()
        print(f"Would delete those subdirs from round_dir and remove from manifest.json,")
        print(f"then run:")
        print()
        print(f"  {test_sh_cmd}")
        print()
        print(f"Then merge the new partial dir back into:")
        print(f"  {round_dir}")
        print()
        print(f"Max attempts: {args.max_attempts}, fallback wait: {args.fallback_wait}s")
        return 0

    # Real mode — build salvage status callback
    _salvage_base = {
        "tool": args.tool,
        "model": args.model or "",
        "round_dir": round_dir.name,
        "scenarios": scenarios,
        "pid": os.getpid(),
        "started_at": _now_iso(),
    }
    _write_salvage_status(args.run_id, **_salvage_base)

    def _status_cb(status: str, attempt: int, **_extra: object) -> None:
        _write_salvage_status(args.run_id, status=status, attempt=attempt)

    runner_fn = _make_real_runner_fn(
        run_id=args.run_id,
        tool=args.tool,
        model=args.model,
        thinking=args.thinking,
    )

    result = run_cleanup_resume(
        round_dir=round_dir,
        prefix=prefix,
        scenarios=scenarios,
        runner_fn=runner_fn,
        max_attempts=args.max_attempts,
        fallback_wait=args.fallback_wait,
        status_cb=_status_cb,
    )

    print(f"\n[cleanup_resume] Result: {json.dumps(result, indent=2)}")
    return 0 if result["status"] == "complete" else 1


if __name__ == "__main__":
    sys.exit(main())
