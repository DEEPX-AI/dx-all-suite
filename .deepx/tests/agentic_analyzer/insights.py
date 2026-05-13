#!/usr/bin/env python3
"""Agentic insight generation — uses a CLI agent to derive qualitative analysis.

Two modes:

  --mode insights      Read analysis.md + analysis.json → call CLI agent →
                       generate insights.md with per-tool strengths/weaknesses

  --mode runnability   For each session, read README.md + setup.sh + run.sh →
                       call CLI agent to judge end-user runnability →
                       generate runnability_report.md

Usage:
    # Generate insights from an existing report
    python insights.py --mode insights --report-dir reports/<ts>/ --cli claude

    # Judge end-user runnability of a sample of sessions
    python insights.py --mode runnability --report-dir reports/<ts>/ \\
        --cli copilot --sample 10

Supported CLI agents:
    claude    — `claude -p --dangerously-skip-permissions`
    copilot   — `copilot --yolo --no-ask-user -s -p`
    cursor    — `agent -p --force`
    opencode  — `opencode run --format text`
    codex     — `codex exec --json -s danger-full-access`

If the CLI is not installed or fails, falls back to writing a prompt-only template
(insights_prompt.md) that the user can run manually.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# CLI configuration per agent tool
# ---------------------------------------------------------------------------

#
# Per-CLI config keys:
#   binary              -- the executable name to invoke
#   args                -- fixed args after `[--model X]` and before the prompt
#   stdin_prompt        -- pass prompt via stdin (legacy; most CLIs use prompt_via_arg)
#   prompt_via_arg      -- append the prompt as the final positional arg
#   model_flag          -- the CLI's model-selection flag (None if not supported)
#   free_default_model  -- the recommended **no-cost** model for this CLI
#                          (None means this CLI has no free-tier model — must use
#                           --allow-paid or override with --model)
#   paid_default_model  -- the recommended highest-quality model when paid usage
#                          is acceptable
#
# Free vs paid policy (per user account state at the time of writing):
#   - Claude Code: team-plan seat → free WITHIN weekly limit. Treated as PAID
#     in auto-chain because the limit is precious and easily exhausted.
#   - Copilot Enterprise: gpt-4.1, gpt-5-mini, gpt-5.4-mini are free; Claude
#     models + larger GPT (5/5.2/5.3/5.4/5.5/codex variants) consume premium
#     requests.
#   - Cursor subscription: `auto` (composer-2-fast) is free; pinned named
#     models consume Cursor credits.
#   - OpenCode / Codex: route through Copilot provider → all sonnet/gpt-5
#     model selections are paid.
#
CLI_CONFIG = {
    # claude:  -p <prompt> (positional prompt accepted; --dangerously-skip-permissions auto-approves)
    "claude": {
        "binary": "claude",
        "args": ["--dangerously-skip-permissions", "-p"],
        "stdin_prompt": False,
        "prompt_via_arg": True,   # append prompt as positional
        "model_flag": "--model",
        "free_default_model": None,           # team-plan limit is precious — treat as paid
        "paid_default_model": "claude-sonnet-4-6",
    },
    # copilot:  -p "<prompt>" (the `-p` flag takes a value — must come as separate token)
    "copilot": {
        "binary": "copilot",
        "args": ["--yolo", "--no-ask-user", "-s", "-p"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
        "model_flag": "--model",
        "free_default_model": "gpt-4.1",      # Enterprise free
        "paid_default_model": "claude-sonnet-4.6",
    },
    # cursor agent:  -p "<prompt>" (similar)
    "cursor": {
        "binary": "agent",
        "args": ["--force", "-p"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
        "model_flag": "--model",
        "free_default_model": "auto",         # subscription composer-2-fast, no extra charge
        "paid_default_model": "sonnet-4.6",
    },
    "opencode": {
        "binary": "opencode",
        "args": ["run"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
        "model_flag": "--model",
        # opencode routes through copilot provider → can use free copilot models
        "free_default_model": "github-copilot/gpt-4.1",
        "paid_default_model": "github-copilot/claude-sonnet-4.6",
    },
    "codex": {
        "binary": "codex",
        "args": ["exec", "--json", "-s", "danger-full-access"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
        "model_flag": "--model",
        # codex CLI authenticates via `gh auth token` → uses copilot provider models
        "free_default_model": "gpt-4.1",
        "paid_default_model": "gpt-5.3-codex",
    },
}


# Auto-chain priority (first installed CLI wins).
# Free chain: only CLIs that can use a no-cost model.
# Paid chain: all CLIs.
# Order: copilot first per user policy (most reliable + best free model coverage).
AUTO_CHAIN_FREE = ["copilot", "cursor", "opencode", "codex"]
AUTO_CHAIN_PAID = ["copilot", "claude", "cursor", "opencode", "codex"]


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

INSIGHTS_PROMPT_TEMPLATE = """\
You are analyzing the results of an end-to-end test suite that evaluates multiple AI
coding agents on a set of code-generation scenarios.

INPUT BELOW:
A comprehensive Markdown report containing quantitative metrics across:
  - Multiple tools (different agentic CLI implementations)
  - Multiple rounds (independent re-runs of the same tasks)
  - Multiple scenarios (different code-generation tasks)

Each session has metrics including: Compliance %, Quality %, Verdict %,
ExecutionTrace %, Overall %, Duration, σ(Overall), Tool Calls, LOC, Token usage,
Premium Requests, Cost, Pass/Partial/Fail verdict, Sentinel emission rate,
and a Cursor-specific bias check section.

YOUR JOB:
Produce a Korean Markdown report (`insights.md`) that derives **data-driven, objective
insights** from the metrics. Do NOT assume any pre-existing findings — let the data
speak. Structure your output as follows.

## 1. 도구별 강점 / 약점 (per-tool)
For EACH tool present in the data, list:
- 3 strengths (what this tool consistently does WELL — cite specific metrics)
- 3 weaknesses (recurring issues observed — cite specific metrics)
- 1 scenario where this tool excels most (highest Overall/Verdict)
- 1 scenario where this tool struggles most (lowest Overall/Verdict)

## 2. 시나리오별 도구 추천 (per-scenario)
For EACH scenario, identify the top-performing tool by composite score, and the
worst-performing tool. Explain the gap quantitatively.

## 3. 회차간 변동성 / 학습 패턴
- Which tools have the LOWEST round-to-round σ(Overall)? Most consistent.
- Which tools show a clear improvement or regression trend across rounds?
- Are there scenario × round combinations that are systematically problematic?

## 4. Outlier / 이상점 탐지
Identify the most striking outliers in the data — sessions or tool×scenario
combinations whose metrics deviate sharply from the median. For each outlier:
- describe the deviation
- propose a plausible cause based on adjacent metrics

## 5. Cost / 효율 분석
Using the Token Usage + Premium Requests + Efficiency Index data:
- Which tool delivered the BEST cost-effectiveness (verdict achieved per token/request)?
- Are there tools whose token/request count is disproportionate to their output quality?
- For tools using identical or comparable underlying models, are there efficiency gaps?

## 6. 메트릭 신뢰성 점검
Note any metrics that appear unreliable, biased, or limited:
- Cite the bias-check section if applicable
- Identify metrics with poor cross-tool comparability (e.g., tool call counting variance)
- Flag any cases where Verdict and Overall disagree (artifact exists but score low, or vice versa)

## 7. 향후 운영 권장
Based on the data, provide actionable recommendations for future rounds.
Examples (only include if data supports them):
- Whether to deprecate/de-prioritize any tool
- Whether to change the scoring weights based on observed metric stability
- Whether to add additional scenarios or replace existing ones
- Whether to adjust timeout limits based on observed durations

OUTPUT REQUIREMENTS:
- All sections in Korean
- Cite **specific numbers** from the input data — never speculate without data backing
- Identify findings DIRECTLY from the data; do not import outside assumptions
- If the data is insufficient for a section, explicitly say so rather than guessing
- Start the output directly with the `# ` heading (no preamble)

CRITICAL OUTPUT MECHANISM:
- The stdout of your response IS the `insights.md` file. The wrapper script captures
  your stdout verbatim and writes it to the target path.
- DO NOT use the Write, Edit, or any file-creation tools. The file already has a path
  determined by the wrapper — your job is to emit the content, not to save it.
- DO NOT wrap your output in a code fence or quote block. Emit raw markdown.
- DO NOT add a trailing sentence describing what you did (e.g., "insights.md 생성 완료").
  The first line MUST be `# ` and the last line MUST be the actual final markdown content.

REPORT INPUT:
====================

{REPORT_CONTENT}

====================

Emit the full markdown content of `insights.md` now (inline; no file writes).
"""


RUNNABILITY_PROMPT_TEMPLATE = """\
You are evaluating whether an end-user can run a generated session's artifacts.

CONTEXT:
This session was generated by an AI coding agent for a DEEPX Agentic Development task.
The output directory contains README.md, setup.sh, run.sh, and other artifacts.

ARTIFACTS (below):
- README.md content (the user's primary entrypoint instructions)
- setup.sh content (environment setup)
- run.sh content (how to actually run the result)
- session.log content (agent's reported execution evidence)

YOUR TASK:
Judge whether a typical end-user (DEEPX SDK developer, but unfamiliar with this exact
session) could successfully follow README.md to install + run + verify this artifact.

OUTPUT FORMAT (Korean markdown):

### {session_label}

- **end-user runnability**: PASS / PARTIAL / FAIL
- **README clarity (1-5)**: <score>
- **Setup completeness (1-5)**: <score>
- **Run instructions completeness (1-5)**: <score>
- **Verification provided (Y/N)**: <yes/no>
- **Key issues** (if any): <bullet list, max 3>
- **One-sentence verdict**: <summary>

ARTIFACTS:
=====================

README.md:
```
{README}
```

setup.sh:
```
{SETUP}
```

run.sh:
```
{RUN}
```

session.log (excerpt):
```
{SESSION_LOG}
```

=====================

Produce the markdown analysis block now.
"""


# ---------------------------------------------------------------------------
# CLI invocation
# ---------------------------------------------------------------------------

def resolve_effective_model(cli: str, model: Optional[str],
                             allow_paid: bool) -> Optional[str]:
    """Pick the model to use for this CLI call.

    Precedence: explicit `model` arg > paid_default (if allow_paid) > free_default.
    Returns None when the CLI has no free option AND allow_paid is False —
    callers must skip the invocation in that case.
    """
    if model:
        return model
    conf = CLI_CONFIG.get(cli, {})
    if allow_paid:
        return conf.get("paid_default_model") or conf.get("free_default_model")
    return conf.get("free_default_model")


def resolve_cli(name: str, allow_paid: bool) -> Optional[str]:
    """Resolve `--cli auto` to the first installed CLI in the appropriate chain.
    Returns the resolved CLI name (one of CLI_CONFIG keys), or None when nothing
    is available. Non-auto values pass through if the binary is installed.
    """
    if name and name != "auto":
        conf = CLI_CONFIG.get(name)
        if conf and shutil.which(conf["binary"]):
            return name
        return None
    chain = AUTO_CHAIN_PAID if allow_paid else AUTO_CHAIN_FREE
    for c in chain:
        if shutil.which(CLI_CONFIG[c]["binary"]):
            return c
    return None


def invoke_cli(cli: str, prompt: str, *, model: Optional[str] = None,
               allow_paid: bool = False, timeout_sec: int = 300) -> Optional[str]:
    """Invoke an agent CLI with a prompt. Return the stdout text, or None on failure.

    When `model` is None, the effective model is derived from CLI_CONFIG using
    `allow_paid` — see `resolve_effective_model`. If the CLI has no free model
    and `allow_paid` is False, the call is skipped (None returned).
    """
    conf = CLI_CONFIG.get(cli)
    if not conf:
        print(f"ERROR: unknown CLI '{cli}'", file=sys.stderr)
        return None
    if not shutil.which(conf["binary"]):
        print(f"WARN: CLI '{conf['binary']}' not found in PATH — skipping invocation.",
              file=sys.stderr)
        return None

    effective_model = resolve_effective_model(cli, model, allow_paid)
    if effective_model is None:
        print(f"WARN: CLI '{cli}' has no free-tier model. Pass --allow-paid or "
              f"--model <name> to override.", file=sys.stderr)
        return None

    cmd = [conf["binary"]]
    model_flag = conf.get("model_flag")
    if model_flag:
        cmd.extend([model_flag, effective_model])
    cmd.extend(conf["args"])
    try:
        if conf.get("prompt_via_arg"):
            cmd.append(prompt)
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        else:
            # Pass via stdin
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               timeout=timeout_sec)
        if r.returncode != 0:
            print(f"WARN: CLI '{cli}' (model={effective_model}) returned exit "
                  f"{r.returncode}: {r.stderr[:300]}", file=sys.stderr)
            return None
        return r.stdout
    except subprocess.TimeoutExpired:
        print(f"WARN: CLI '{cli}' (model={effective_model}) timed out after "
              f"{timeout_sec}s", file=sys.stderr)
        return None
    except Exception as e:
        print(f"WARN: CLI '{cli}' (model={effective_model}) invocation failed: {e}",
              file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Mode: insights
# ---------------------------------------------------------------------------

def run_insights(report_dir: Path, cli: str, output_dir: Path,
                  *, model: Optional[str] = None, allow_paid: bool = False) -> int:
    """Generate insights.md from analysis.md + analysis.json using a CLI agent."""
    analysis_md = report_dir / "analysis.md"
    if not analysis_md.is_file():
        print(f"ERROR: {analysis_md} not found", file=sys.stderr)
        return 2

    report_content = analysis_md.read_text(encoding="utf-8")
    # Truncate if too long for CLI prompt limits (most CLIs handle ~200k+ chars OK)
    if len(report_content) > 250_000:
        report_content = report_content[:250_000] + "\n[...TRUNCATED...]"
    prompt = INSIGHTS_PROMPT_TEMPLATE.format(REPORT_CONTENT=report_content)

    # Save the prompt regardless (so user can re-run manually)
    prompt_path = output_dir / "insights_prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")
    print(f"Saved prompt to: {prompt_path}")

    print(f"Invoking CLI '{cli}'... (this can take several minutes)")
    result = invoke_cli(cli, prompt, model=model, allow_paid=allow_paid,
                         timeout_sec=900)
    if result is None:
        print(f"⚠ CLI invocation failed/skipped. The prompt is saved at "
              f"{prompt_path} — run it manually with your preferred agent.")
        return 1

    insights_path = output_dir / "insights.md"
    final_text, source = _select_insights_content(result, report_dir, insights_path)
    insights_path.write_text(final_text, encoding="utf-8")
    if source == "stdout":
        print(f"✓ Wrote insights to: {insights_path}")
    else:
        print(f"✓ Wrote insights to: {insights_path} (recovered from {source})")
    return 0


def _select_insights_content(stdout: str, report_dir: Path,
                              target_path: Path) -> tuple[str, str]:
    """Pick the best insights content: stdout if it looks like a full report,
    otherwise search known fallback paths for an insights.md the CLI may have
    written via a file-creation tool against our explicit prompt instructions.
    Returns (content, source_label).
    """
    stdout_text = stdout or ""
    # Heuristic: a real insights report starts with '# ' and is >2KB.
    is_full_report = stdout_text.lstrip().startswith("# ") and len(stdout_text) >= 2048
    if is_full_report:
        return stdout_text, "stdout"

    # Stdout looks like a chat summary, not the report. Look for fallback files
    # the CLI may have written via Write tool (against prompt instructions).
    suite_root = _find_suite_root(report_dir)
    fallback_candidates = [
        suite_root / "dx-agentic-dev" / "e2e-tests" / "results" / "insights.md",
        Path.cwd() / "insights.md",
    ]
    now = datetime.now().timestamp()
    for cand in fallback_candidates:
        if cand.is_file() and cand.resolve() != target_path.resolve():
            try:
                mtime = cand.stat().st_mtime
            except OSError:
                continue
            # Only trust files touched within the last 30 minutes
            if now - mtime > 1800:
                continue
            content = cand.read_text(encoding="utf-8", errors="ignore")
            if content.lstrip().startswith("# ") and len(content) >= 2048:
                # Move the misplaced file out of the way
                try:
                    cand.unlink()
                except OSError:
                    pass
                return content, str(cand)

    # No good fallback — return whatever stdout had (caller will write it).
    return stdout_text, "stdout"


def _find_suite_root(start: Path) -> Path:
    """Walk up from start looking for the dx-all-suite root (has dx-runtime/ and
    dx-compiler/ siblings). Falls back to start.parent.parent.parent."""
    p = start.resolve()
    for _ in range(8):
        if (p / "dx-runtime").is_dir() and (p / "dx-compiler").is_dir():
            return p
        if p.parent == p:
            break
        p = p.parent
    return start.resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# Mode: runnability
# ---------------------------------------------------------------------------

def _read_safely(path: Path, limit: int = 10_000) -> str:
    if not path.is_file():
        return "(file not found)"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        return text[:limit] + ("...[truncated]" if len(text) > limit else "")
    except Exception as e:
        return f"(read error: {e})"


def run_runnability(report_dir: Path, cli: str, output_dir: Path,
                     sample: int = 8, *, model: Optional[str] = None,
                     allow_paid: bool = False) -> int:
    """Judge end-user runnability of sessions using a CLI agent.

    Sample selection modes:
      - sample > 0: pick one diverse session per (tool, scenario), shuffle,
                    take first `sample`. (Same as before.)
      - sample <= 0 (or `--all`): EXHAUSTIVE — evaluate every session.
                                  Expensive: 396 sessions ≈ 30min~5h depending
                                  on CLI throughput.
    """
    json_path = report_dir / "analysis.json"
    if not json_path.is_file():
        print(f"ERROR: {json_path} not found", file=sys.stderr)
        return 2

    data = json.loads(json_path.read_text(encoding="utf-8"))
    sessions = data.get("sessions", [])

    if sample <= 0:
        # Exhaustive: keep all sessions in their original (tool, round, scenario) order
        sampled = list(sessions)
        mode_label = "EXHAUSTIVE"
    else:
        # Sample selection: prefer diverse (per tool × scenario)
        # Group by (tool, scenario), pick 1 from each up to sample limit
        by_key = {}
        for s in sessions:
            key = (s.get("tool"), s.get("scenario"))
            by_key.setdefault(key, []).append(s)
        sampled = [lst[0] for lst in by_key.values()]
        random.shuffle(sampled)
        sampled = sampled[:sample]
        mode_label = f"sample={sample}"

    out_path = output_dir / "runnability_report.md"
    started_at = datetime.now().isoformat(timespec='seconds')

    def _write_report(results: List[str], done: int, total: int, final: bool) -> None:
        """Write runnability_report.md with current progress. Called after every
        session in exhaustive mode so an interrupted run still leaves usable
        partial data on disk.
        """
        status = "complete" if final else f"in-progress ({done}/{total})"
        header = (
            f"# End-User Runnability Report\n"
            f"> Generated: {started_at}  (status: {status})\n"
            f"> Sessions evaluated: {done}/{total}  |  Mode: {mode_label}  |  CLI: `{cli}`\n\n"
            f"---\n\n"
        )
        out_path.write_text(header + "\n\n---\n\n".join(results), encoding="utf-8")

    print(f"Evaluating runnability of {len(sampled)} sessions ({mode_label}, CLI: {cli})...")
    results: List[str] = []
    total = len(sampled)
    for i, s in enumerate(sampled, 1):
        tool = s.get("tool")
        scenario = s.get("scenario")
        round_ix = s.get("round_index")
        out_dirs = s.get("output_dirs", [])
        if not out_dirs:
            continue
        out_dir = Path(out_dirs[0])
        if not out_dir.is_dir():
            continue
        readme = _read_safely(out_dir / "README.md", 8000)
        setup = _read_safely(out_dir / "setup.sh", 4000)
        run_sh = _read_safely(out_dir / "run.sh", 4000)
        slog = _read_safely(out_dir / "session.log", 3000)

        label = f"R{round_ix} {tool} {scenario}"
        prompt = RUNNABILITY_PROMPT_TEMPLATE.format(
            session_label=label,
            README=readme, SETUP=setup, RUN=run_sh, SESSION_LOG=slog,
        )
        print(f"  [{i}/{total}] {label}")
        ans = invoke_cli(cli, prompt, model=model, allow_paid=allow_paid,
                          timeout_sec=180)
        if ans is None:
            results.append(f"### {label}\n\n(CLI invocation failed/skipped)\n")
        else:
            results.append(ans.strip() + "\n")
        # Incremental flush — protects multi-hour exhaustive runs against
        # interruption (kill, timeout, machine reboot). Cheap (<1ms per call).
        _write_report(results, i, total, final=False)

    _write_report(results, len(results), total, final=True)
    print(f"✓ Wrote runnability report to: {out_path}")
    return 0


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def _env_bool(name: str, default: bool = False) -> bool:
    v = os.environ.get(name, "")
    return v.lower() in ("1", "true", "yes", "on") if v else default


def main(argv: Optional[List[str]] = None) -> int:
    env_cli = os.environ.get("DX_INSIGHTS_CLI") or "auto"
    env_model = os.environ.get("DX_INSIGHTS_MODEL") or None
    env_allow_paid = _env_bool("DX_INSIGHTS_ALLOW_PAID")

    p = argparse.ArgumentParser(description="Agentic insight generator (post-analysis)")
    p.add_argument("--mode", choices=["insights", "runnability"], required=True,
                   help="What to analyze")
    p.add_argument("--report-dir", required=True,
                   help="Path to a previously-generated report dir (with analysis.md + analysis.json)")
    p.add_argument("--cli", choices=list(CLI_CONFIG.keys()) + ["auto"],
                   default=env_cli,
                   help=("Which CLI agent to call. 'auto' picks the first installed "
                         "CLI from the free chain (or paid chain if --allow-paid). "
                         f"Default: {env_cli} (env: DX_INSIGHTS_CLI)"))
    p.add_argument("--model", default=env_model,
                   help=("Override the CLI's default model (e.g. 'gpt-4.1', "
                         "'claude-sonnet-4-6', 'auto'). When omitted, the CLI's "
                         "free_default_model is used unless --allow-paid is set. "
                         "Env: DX_INSIGHTS_MODEL"))
    p.add_argument("--allow-paid", action="store_true", default=env_allow_paid,
                   help=("Permit paid/billed model selections (Claude Code seat, "
                         "claude-sonnet-4-6 via copilot, gpt-5/codex, etc.). "
                         "Default: only free models. Env: DX_INSIGHTS_ALLOW_PAID=1"))
    p.add_argument("--output-dir", default=None,
                   help="Where to write the output (default: same as --report-dir)")
    p.add_argument("--sample", type=int, default=8,
                   help=("(runnability mode) number of sessions to sample (default: 8). "
                         "Use 0 (or --all) for EXHAUSTIVE — evaluate every session "
                         "(expensive)."))
    p.add_argument("--all", action="store_true",
                   help="(runnability mode) alias for --sample 0 (exhaustive)")

    args = p.parse_args(argv)
    report_dir = Path(args.report_dir).resolve()
    if not report_dir.is_dir():
        print(f"ERROR: report-dir not found: {report_dir}", file=sys.stderr)
        return 2
    out_dir = Path(args.output_dir).resolve() if args.output_dir else report_dir

    # Resolve CLI (handle 'auto' here so failures emit a clear message)
    chosen_cli = resolve_cli(args.cli, args.allow_paid)
    if not chosen_cli:
        chain = AUTO_CHAIN_PAID if args.allow_paid else AUTO_CHAIN_FREE
        print(f"ERROR: no usable CLI found. Tried: {chain}. "
              f"Install one (or pass --allow-paid to widen the chain), or use "
              f"--cli <name> with a specific binary in PATH.", file=sys.stderr)
        return 3

    effective_sample = 0 if args.all else args.sample

    if args.mode == "insights":
        return run_insights(report_dir, chosen_cli, out_dir,
                            model=args.model, allow_paid=args.allow_paid)
    elif args.mode == "runnability":
        return run_runnability(report_dir, chosen_cli, out_dir, effective_sample,
                                model=args.model, allow_paid=args.allow_paid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
