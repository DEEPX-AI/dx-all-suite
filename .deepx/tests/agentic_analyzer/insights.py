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
    copilot   — `copilot -p --yolo --no-ask-user -s`
    cursor    — `agent -p --force`
    opencode  — `opencode run --format text`

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

CLI_CONFIG = {
    "claude": {
        "binary": "claude",
        "args": ["-p", "--dangerously-skip-permissions"],
        "stdin_prompt": True,            # accepts prompt on stdin
    },
    "copilot": {
        "binary": "copilot",
        "args": ["-p", "--yolo", "--no-ask-user", "-s"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
    },
    "cursor": {
        "binary": "agent",
        "args": ["-p", "--force"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
    },
    "opencode": {
        "binary": "opencode",
        "args": ["run"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
    },
}


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

REPORT INPUT:
====================

{REPORT_CONTENT}

====================

Now produce `insights.md`.
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

def invoke_cli(cli: str, prompt: str, timeout_sec: int = 300) -> Optional[str]:
    """Invoke an agent CLI with a prompt. Return the stdout text, or None on failure."""
    conf = CLI_CONFIG.get(cli)
    if not conf:
        print(f"ERROR: unknown CLI '{cli}'", file=sys.stderr)
        return None
    if not shutil.which(conf["binary"]):
        print(f"WARN: CLI '{conf['binary']}' not found in PATH — skipping invocation.",
              file=sys.stderr)
        return None

    cmd = [conf["binary"], *conf["args"]]
    try:
        if conf.get("prompt_via_arg"):
            cmd.append(prompt)
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_sec)
        else:
            # Pass via stdin
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               timeout=timeout_sec)
        if r.returncode != 0:
            print(f"WARN: CLI '{cli}' returned exit {r.returncode}: {r.stderr[:300]}",
                  file=sys.stderr)
            return None
        return r.stdout
    except subprocess.TimeoutExpired:
        print(f"WARN: CLI '{cli}' timed out after {timeout_sec}s", file=sys.stderr)
        return None
    except Exception as e:
        print(f"WARN: CLI '{cli}' invocation failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Mode: insights
# ---------------------------------------------------------------------------

def run_insights(report_dir: Path, cli: str, output_dir: Path) -> int:
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
    result = invoke_cli(cli, prompt, timeout_sec=900)
    if result is None:
        print(f"⚠ CLI invocation failed/skipped. The prompt is saved at "
              f"{prompt_path} — run it manually with your preferred agent.")
        return 1

    insights_path = output_dir / "insights.md"
    insights_path.write_text(result, encoding="utf-8")
    print(f"✓ Wrote insights to: {insights_path}")
    return 0


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
                     sample: int = 8) -> int:
    """Judge end-user runnability of a sample of sessions using a CLI agent."""
    json_path = report_dir / "analysis.json"
    if not json_path.is_file():
        print(f"ERROR: {json_path} not found", file=sys.stderr)
        return 2

    data = json.loads(json_path.read_text(encoding="utf-8"))
    sessions = data.get("sessions", [])

    # Sample selection: prefer diverse (per tool × scenario)
    # Group by (tool, scenario), pick 1 from each up to sample limit
    by_key = {}
    for s in sessions:
        key = (s.get("tool"), s.get("scenario"))
        by_key.setdefault(key, []).append(s)
    sampled = []
    for key, lst in by_key.items():
        sampled.append(lst[0])  # take first
    random.shuffle(sampled)
    sampled = sampled[:sample]

    print(f"Evaluating runnability of {len(sampled)} sample sessions (CLI: {cli})...")
    results: List[str] = []
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
        print(f"  [{i}/{len(sampled)}] {label}")
        ans = invoke_cli(cli, prompt, timeout_sec=180)
        if ans is None:
            results.append(f"### {label}\n\n(CLI invocation failed/skipped)\n")
        else:
            results.append(ans.strip() + "\n")

    out_path = output_dir / "runnability_report.md"
    header = (
        f"# End-User Runnability Report\n"
        f"> Generated: {datetime.now().isoformat(timespec='seconds')}\n"
        f"> Sampled sessions: {len(sampled)}  |  CLI used: `{cli}`\n\n"
        f"---\n\n"
    )
    out_path.write_text(header + "\n\n---\n\n".join(results), encoding="utf-8")
    print(f"✓ Wrote runnability report to: {out_path}")
    return 0


# ---------------------------------------------------------------------------
# CLI parser
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Agentic insight generator (post-analysis)")
    p.add_argument("--mode", choices=["insights", "runnability"], required=True,
                   help="What to analyze")
    p.add_argument("--report-dir", required=True,
                   help="Path to a previously-generated report dir (with analysis.md + analysis.json)")
    p.add_argument("--cli", choices=list(CLI_CONFIG.keys()), default="claude",
                   help="Which CLI agent to call (default: claude)")
    p.add_argument("--output-dir", default=None,
                   help="Where to write the output (default: same as --report-dir)")
    p.add_argument("--sample", type=int, default=8,
                   help="(runnability mode) number of sessions to sample (default: 8)")

    args = p.parse_args(argv)
    report_dir = Path(args.report_dir).resolve()
    if not report_dir.is_dir():
        print(f"ERROR: report-dir not found: {report_dir}", file=sys.stderr)
        return 2
    out_dir = Path(args.output_dir).resolve() if args.output_dir else report_dir

    if args.mode == "insights":
        return run_insights(report_dir, args.cli, out_dir)
    elif args.mode == "runnability":
        return run_runnability(report_dir, args.cli, out_dir, args.sample)
    return 0


if __name__ == "__main__":
    sys.exit(main())
