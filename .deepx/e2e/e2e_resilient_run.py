#!/usr/bin/env python3
"""
e2e_resilient_run.py — Usage-limit-resilient controller for e2e_runner.py.

Wraps e2e_runner with a redo-env-failures → wait-for-reset → resume loop so
long eval runs survive Claude session/usage limits automatically.

Usage:
    # Resilient run: 5 rounds for claude-code, resume on usage limits
    python .deepx/e2e/e2e_resilient_run.py \\
        --tool claude-code --model claude-opus-4-8 --rounds 5

    # With thinking mode
    python .deepx/e2e/e2e_resilient_run.py \\
        --tool claude-code --model claude-opus-4-8 --rounds 5 --thinking

    # Dry run (print planned first command and exit)
    python .deepx/e2e/e2e_resilient_run.py \\
        --tool claude-code --model claude-opus-4-8 --dry-run
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = (SCRIPT_DIR / "../..").resolve()
RUNNER_STATE_DIR = SCRIPT_DIR / "runner_state"
RESULTS_ROOT = REPO_ROOT / "dx-agent-dev/e2e-tests/results"

# ---------------------------------------------------------------------------
# Tool → model flag mapping
# ---------------------------------------------------------------------------

TOOL_MODEL_FLAG: Dict[str, str] = {
    "claude-code": "--claude-model",
    "copilot-cli": "--copilot-model",
    "codex-cli": "--codex-model",
    "opencode-cli": "--opencode-model",
    "cursor-cli": "--cursor-model",
}

# ---------------------------------------------------------------------------
# 1. parse_reset_seconds
# ---------------------------------------------------------------------------

# Match "usage limit reached|<epoch>" — pipe separator after the phrase.
# Use \d{4,} (>= 4 digits) to avoid false positives on small line numbers
# while still matching short integers used in unit tests.
_RE_EPOCH_PIPE = re.compile(
    r"(?:usage\s+limit\s+reached)\s*\|\s*(\d{4,})",
    re.IGNORECASE,
)
# JSON form: "resetsAt":<epoch>
_RE_RESETS_AT_EPOCH = re.compile(
    r'"resetsAt"\s*:\s*(\d{4,})',
    re.IGNORECASE,
)
# "resets at <epoch>" bare form — must NOT be followed by am/pm (those are clock times)
_RE_RESETS_AT_EPOCH2 = re.compile(
    r"resets\s+at\s+(\d{4,})\b(?!\s*(?:am|pm))",
    re.IGNORECASE,
)
# "session limit · resets <epoch>"
_RE_SESSION_LIMIT_EPOCH = re.compile(
    r"session\s+limit\s*[·•]\s*resets\s+(\d{4,})\b(?!\s*(?:am|pm))",
    re.IGNORECASE,
)

# Clock forms: "resets at 3pm", "resets at 3:30pm", "resets 15:00",
# "session limit · resets 3pm"
_RE_CLOCK = re.compile(
    r"(?<!\d)(?:resets\s+at|resets)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?(?!\d)",
    re.IGNORECASE,
)


def parse_reset_seconds(text: str, now_epoch: float) -> Optional[int]:
    """Scan *text* for a usage-limit reset time; return seconds to wait (>=0) or None.

    *now_epoch* is injected (never calls time.time() internally) so tests are
    deterministic.

    Handles:
    - Epoch pipe: ``usage limit reached|<10-digit-epoch>``
    - JSON form: ``"resetsAt":<10-digit-epoch>``
    - Clock form: ``resets at 3pm``, ``resets at 3:30pm``, ``resets 15:00``,
      ``session limit · resets 3pm``

    Returns the **smallest non-negative** wait in seconds, or None if nothing
    matched.
    """
    candidates: List[int] = []

    # --- epoch forms ---
    for pattern in (
        _RE_EPOCH_PIPE,
        _RE_RESETS_AT_EPOCH,
        _RE_RESETS_AT_EPOCH2,
        _RE_SESSION_LIMIT_EPOCH,
    ):
        for m in pattern.finditer(text):
            epoch_val = int(m.group(1))
            wait = max(0, int(epoch_val - now_epoch))
            candidates.append(wait)

    # --- clock forms ---
    import time as _time

    local = _time.localtime(now_epoch)
    now_secs_in_day = local.tm_hour * 3600 + local.tm_min * 60 + local.tm_sec

    for m in _RE_CLOCK.finditer(text):
        hour = int(m.group(1))
        minute = int(m.group(2)) if m.group(2) else 0
        ampm = (m.group(3) or "").lower()

        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
        # If no am/pm, treat as 24-h clock (e.g. "15:00")

        target_secs = hour * 3600 + minute * 60
        diff = target_secs - now_secs_in_day
        if diff <= 0:
            diff += 86400  # roll to tomorrow
        candidates.append(int(diff))

    if not candidates:
        return None
    return min(candidates)


# ---------------------------------------------------------------------------
# 1b. parse_env_failed_count
# ---------------------------------------------------------------------------

# Match "[redo-env] run <RID>: N env-failure round(s)"
_RE_ENV_FAILED_COUNT = re.compile(
    r":\s+(\d+)\s+env-failure\s+round",
    re.IGNORECASE,
)


def parse_env_failed_count(text: str) -> int:
    """Return N from '[redo-env] run <RID>: N env-failure round(s)', else 0.

    Returns 0 for "no env-failure rounds detected" or any unmatched text.
    This is used to parse the output of:
        e2e_runner.py --redo-env-failures --dry-run --run-id <RID>
    """
    if "no env-failure rounds detected" in text.lower():
        return 0
    m = _RE_ENV_FAILED_COUNT.search(text)
    if m:
        return int(m.group(1))
    return 0


# ---------------------------------------------------------------------------
# 2. completed_rounds
# ---------------------------------------------------------------------------


def completed_rounds(state_path: Path, tool: str) -> int:
    """Return number of completed rounds for *tool* from state.json.

    Returns 0 if the file is absent, unreadable, or the tool is missing.
    """
    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
        completed = data.get("tool_states", {}).get(tool, {}).get("completed", [])
        if isinstance(completed, list):
            return len(completed)
        if isinstance(completed, int):
            return completed
        return 0
    except Exception:
        return 0


# ---------------------------------------------------------------------------
# 3. build_runner_cmd
# ---------------------------------------------------------------------------


def build_runner_cmd(
    runner: str,
    tool: str,
    model: str,
    rounds: int,
    thinking: bool,
    resume: bool,
    run_id: Optional[str],
) -> List[str]:
    """Assemble the argv list for e2e_runner.py (excluding the python interpreter).

    The caller prepends ``[sys.executable, runner]`` to produce the full command.
    """
    model_flag = TOOL_MODEL_FLAG.get(tool, f"--{tool}-model")

    cmd = [
        runner,
        "--tools", tool,
        "--rounds", str(rounds),
        model_flag, model,
    ]
    if thinking:
        cmd.append("--thinking")
    if resume and run_id:
        cmd.extend(["--resume", "--run-id", run_id])
    elif resume:
        cmd.append("--resume")
    return cmd


# ---------------------------------------------------------------------------
# 4. run_resilient
# ---------------------------------------------------------------------------


def run_resilient(
    *,
    runner: str,
    tool: str,
    model: str,
    rounds: int,
    thinking: bool,
    max_attempts: int = 6,
    fallback_wait: int = 3600,
    runner_fn: Callable[[List[str]], Tuple[int, str, str]],
    sleep_fn: Callable[[float], None],
    now_fn: Callable[[], float],
    transcript_reader: Callable[[str], str],
    env_failed_fn: Callable[[str], int],
) -> dict:
    """Resilient run loop: run → detect rate-limit → redo-env → wait → resume.

    Parameters
    ----------
    runner:
        Path to e2e_runner.py (passed as first element of cmd list).
    tool, model, rounds, thinking:
        Forwarded to build_runner_cmd.
    max_attempts:
        Hard cap on total run+resume attempts before giving up.
    fallback_wait:
        Seconds to sleep when no reset time is parseable from the transcript.
    runner_fn:
        Callable(cmd: list[str]) -> (returncode: int, stdout: str, run_id: str).
        The run_id should be extracted from stdout by the implementation.
    sleep_fn:
        Callable(seconds: float) -> None.  Injected so tests run instantly.
    now_fn:
        Callable() -> float (epoch seconds).  Injected for determinism.
    transcript_reader:
        Callable(run_id: str) -> str.  Returns recent transcript text for
        reset-time parsing.
    env_failed_fn:
        Callable(run_id: str) -> int.  Returns the number of env-failure
        (rate-limited) rounds in the current run.  In real mode this calls
        ``e2e_runner --redo-env-failures --dry-run --run-id <RID>`` and parses
        via parse_env_failed_count.  Injected so tests run instantly.

    Returns
    -------
    dict with keys:
        status:       "complete" | "incomplete-nonenv" | "max-attempts"
        run_id:       the last run_id used (or None if never started)
        attempts:     number of run attempts made
        valid_rounds: completed_rounds minus env_failed (last check)
        env_failed:   number of env-failure rounds detected (last check)
    """
    run_id: Optional[str] = None
    attempt = 0
    last_valid = 0
    last_env_failed = 0

    while attempt < max_attempts:
        attempt += 1
        resume = attempt > 1

        cmd = [sys.executable] + build_runner_cmd(
            runner=runner,
            tool=tool,
            model=model,
            rounds=rounds,
            thinking=thinking,
            resume=resume,
            run_id=run_id,
        )

        print(f"\n[resilient] attempt {attempt}/{max_attempts}  resume={resume}  run_id={run_id}")
        print(f"[resilient] cmd: {' '.join(cmd)}")

        rc, stdout, new_run_id = runner_fn(cmd)
        if new_run_id:
            run_id = new_run_id
            print(f"[resilient] run_id resolved to: {run_id}")

        # Check completed rounds via state.json
        if run_id:
            state_path = RUNNER_STATE_DIR / run_id / "state.json"
            done = completed_rounds(state_path, tool)
        else:
            done = 0

        # Check how many of those rounds were env-failures (rate-limited)
        env_failed_count = env_failed_fn(run_id) if run_id else 0
        valid = done - env_failed_count
        last_valid = valid
        last_env_failed = env_failed_count

        print(
            f"[resilient] completed={done}  env_failed={env_failed_count}"
            f"  valid={valid}  target={rounds}"
        )

        if valid >= rounds:
            print(f"[resilient] valid target reached — COMPLETE after {attempt} attempt(s).")
            return {
                "status": "complete",
                "run_id": run_id,
                "attempts": attempt,
                "valid_rounds": valid,
                "env_failed": env_failed_count,
            }

        # Not yet done — decide path based on env_failed_count
        if not run_id:
            print("[resilient] no run_id captured; cannot redo-env-failures — stopping.")
            return {
                "status": "incomplete-nonenv",
                "run_id": run_id,
                "attempts": attempt,
                "valid_rounds": valid,
                "env_failed": env_failed_count,
            }

        if env_failed_count == 0:
            # Shortfall is NOT due to rate/usage limits — stop, don't loop forever
            print(
                "[resilient] valid < target but no env-failure rounds detected"
                " — non-usage-limit failure; stopping."
            )
            return {
                "status": "incomplete-nonenv",
                "run_id": run_id,
                "attempts": attempt,
                "valid_rounds": valid,
                "env_failed": env_failed_count,
            }

        # env_failed_count > 0: rate/usage-limit rounds exist — redo them, wait, resume
        redo_cmd = [
            sys.executable, runner,
            "--redo-env-failures",
            "--run-id", run_id,
        ]
        print(f"[resilient] running redo-env-failures: {' '.join(redo_cmd)}")
        _redo_rc, redo_stdout, _ = runner_fn(redo_cmd)

        removed = _parse_redo_removed(redo_stdout)
        print(f"[resilient] redo-env-failures removed={removed}")

        # Env/rate-limit rounds were removed — wait for reset
        transcript_text = transcript_reader(run_id)
        wait = parse_reset_seconds(transcript_text, now_fn()) if transcript_text else None
        if wait is None:
            wait = fallback_wait
            print(f"[resilient] no reset time parsed from transcript; using fallback_wait={wait}s")
        else:
            print(f"[resilient] parsed reset wait={wait}s from transcript")

        # Only sleep if we have more attempts remaining
        if attempt < max_attempts:
            print(f"[resilient] sleeping {wait}s before resume attempt {attempt + 1}...")
            sleep_fn(wait)
        else:
            print(f"[resilient] max_attempts={max_attempts} exhausted — skip sleep.")

    print(f"[resilient] max_attempts={max_attempts} exhausted — giving up.")
    return {
        "status": "max-attempts",
        "run_id": run_id,
        "attempts": attempt,
        "valid_rounds": last_valid,
        "env_failed": last_env_failed,
    }


def _parse_redo_removed(stdout: str) -> int:
    """Parse '[redo-env] removed N round(s)' or 'no env-failure rounds detected' from stdout."""
    # "no env-failure rounds detected" → 0
    if "no env-failure rounds detected" in stdout.lower():
        return 0
    m = re.search(r"\[redo-env\]\s+removed\s+(\d+)\s+round", stdout, re.IGNORECASE)
    if m:
        return int(m.group(1))
    # If we can't parse, assume 0 (don't loop forever)
    return 0


# ---------------------------------------------------------------------------
# Real runner_fn / transcript_reader for main()
# ---------------------------------------------------------------------------


def _real_runner_fn(cmd: List[str]) -> Tuple[int, str, str]:
    """Execute cmd, stream stdout to stderr (so parent log sees it), capture it too."""
    print(f"[resilient] executing: {' '.join(cmd)}", flush=True)
    lines: List[str] = []
    run_id = ""
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )
        assert proc.stdout is not None
        for line in proc.stdout:
            sys.stderr.write(line)
            sys.stderr.flush()
            lines.append(line)
            # Extract run_id from e2e_runner output
            if not run_id:
                m = re.search(r"E2E Runner(?:\s+COMPLETE)?\s+run_id=(\S+)", line)
                if m:
                    run_id = m.group(1)
        proc.wait()
        stdout = "".join(lines)
        return proc.returncode, stdout, run_id
    except Exception as exc:
        print(f"[resilient] runner_fn error: {exc}", file=sys.stderr)
        return 1, "", ""


def _real_env_failed_fn(run_id: str) -> int:
    """Call e2e_runner --redo-env-failures --dry-run --run-id RID; parse count."""
    runner = str(SCRIPT_DIR / "e2e_runner.py")
    cmd = [
        sys.executable, runner,
        "--redo-env-failures",
        "--dry-run",
        "--run-id", run_id,
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
        )
        output = result.stdout + result.stderr
        return parse_env_failed_count(output)
    except Exception as exc:
        print(f"[resilient] env_failed_fn error: {exc}", file=sys.stderr)
        return 0


def _real_transcript_reader(run_id: str) -> str:
    """Collect recent text from the run's results directory for reset parsing."""
    run_dir = RESULTS_ROOT / run_id
    if not run_dir.exists():
        return ""
    texts: List[str] = []
    for path in run_dir.rglob("*.txt"):
        try:
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass
    for path in run_dir.rglob("*.md"):
        try:
            texts.append(path.read_text(encoding="utf-8", errors="replace"))
        except Exception:
            pass
    return "\n".join(texts)


# ---------------------------------------------------------------------------
# 5. main()
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Usage-limit-resilient e2e runner controller.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--tool",
        default="claude-code",
        choices=list(TOOL_MODEL_FLAG.keys()),
        help="Which coding tool to test (default: claude-code)",
    )
    parser.add_argument(
        "--model",
        required=True,
        help="Model ID passed to the tool (e.g. claude-opus-4-8)",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=5,
        help="Target number of rounds (default: 5)",
    )
    parser.add_argument(
        "--thinking",
        action="store_true",
        help="Enable thinking / high-reasoning mode",
    )
    parser.add_argument(
        "--max-attempts",
        type=int,
        default=6,
        help="Maximum run+resume attempts before giving up (default: 6)",
    )
    parser.add_argument(
        "--fallback-wait",
        type=int,
        default=3600,
        help="Seconds to wait when no reset time is parseable (default: 3600)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned first command and exit 0 (no actual run)",
    )

    args = parser.parse_args()

    runner = str(SCRIPT_DIR / "e2e_runner.py")

    first_cmd = [sys.executable] + build_runner_cmd(
        runner=runner,
        tool=args.tool,
        model=args.model,
        rounds=args.rounds,
        thinking=args.thinking,
        resume=False,
        run_id=None,
    )

    if args.dry_run:
        print("Planned first command:")
        print(" ".join(first_cmd))
        sys.exit(0)

    result = run_resilient(
        runner=runner,
        tool=args.tool,
        model=args.model,
        rounds=args.rounds,
        thinking=args.thinking,
        max_attempts=args.max_attempts,
        fallback_wait=args.fallback_wait,
        runner_fn=_real_runner_fn,
        sleep_fn=time.sleep,
        now_fn=time.time,
        transcript_reader=_real_transcript_reader,
        env_failed_fn=_real_env_failed_fn,
    )

    print(f"\n[resilient] DONE — {result}")
    if result["status"] == "complete":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
