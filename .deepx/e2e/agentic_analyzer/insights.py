#!/usr/bin/env python3
"""Agent-Driven insight generation — uses a CLI agent to derive qualitative analysis.

Three modes:

  --mode insights      Read analysis.md + analysis.json → call CLI agent →
                       generate insights.md with per-tool strengths/weaknesses

  --mode runnability   For each session, read README.md + setup.sh + run.sh →
                       call CLI agent to judge end-user runnability →
                       generate runnability_report.md

  --mode hypothesis    Read a prompt template (.md) → call CLI agent →
                       generate hypothesis.json with experiment hypotheses
                       based on external benchmarks (SWE-Bench, Aider, etc.)

Usage:
    # Generate insights from an existing report
    python insights.py --mode insights --report-dir reports/<ts>/ --cli claude

    # Judge end-user runnability of ALL sessions (exhaustive)
    python insights.py --mode runnability --report-dir reports/<ts>/ \\
        --cli copilot

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
import re
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
        # gpt-4.1 (former Enterprise free) was deprecated/removed → None (no free tier).
        # Use --allow-paid → paid_default (claude-sonnet-4.6), or pass an explicit --model.
        "free_default_model": None,
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
        # 'auto' (Composer) is the only confirmed cursor model id (`agent --list-models`);
        # sonnet-4.6 is not exposed there, so keep paid == auto for cursor.
        "paid_default_model": "auto",
    },
    "opencode": {
        "binary": "opencode",
        "args": ["run"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
        "model_flag": "--model",
        # opencode routes through copilot provider; its free model github-copilot/gpt-4.1
        # was deprecated → None (use --allow-paid → paid_default, or pass --model).
        "free_default_model": None,
        "paid_default_model": "github-copilot/claude-sonnet-4.6",
    },
    "codex": {
        "binary": "codex",
        "args": ["exec", "--json", "-s", "danger-full-access"],
        "stdin_prompt": False,
        "prompt_via_arg": True,
        "model_flag": "--model",
        # codex CLI uses copilot provider models; the gpt-4.1 free model was deprecated →
        # None (use --allow-paid → paid_default gpt-5.3-codex, or pass --model).
        "free_default_model": None,
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
  - Multiple tools (different agent-driven CLI implementations)
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

## 8. 향후 운영 권장
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


HYPOTHESIS_VERIFICATION_SECTION = """\

## 7. 가설 검증: 벤치마크 vs 실측 간극 분석

아래 사전 가설과 실제 결과를 비교 분석하세요.

### 사전 가설 요약

{hypothesis_summary}

### 분석 요구사항

각 가설에 대해 다음 4가지를 반드시 모두 포함:
1. **검증 결과**: 지지(Supported) / 기각(Rejected) / 부분 지지(Partial)
2. **실측 데이터**: 해당 metric의 실제 도구별 순위와 점수
3. **간극 분석**: 예상과 실측의 차이 원인 (도구 특성, 프롬프트 전달 방식, 자동화 수준 등)
4. **시사점**: 벤치마크 점수와 실제 agent-driven 워크플로우 성능 간의 관계에 대한 통찰

### 가설 검증 종합 (필수)

각 가설별 4가지 분석을 마친 뒤 반드시 이 sub-section을 끝에 추가하세요. 다음 두 가지 요소를
**둘 다** 포함해야 합니다 — 누락은 출력 누락으로 간주됩니다:

1. **가설 검증 종합 표** — Markdown 표. 컬럼은 정확히 다음과 같이:
   `| 가설 | 결과 | 핵심 교훈 |`
   `|------|:----:|----------|`
   각 가설(H1~Hn)에 대해 한 행씩. "결과" 컬럼은 ✅ 지지 / ❌ 기각 / 🟡 부분 지지 중 하나.
   "핵심 교훈"은 한 문장(40자 이내).

2. **종합 시사점** — `**종합 시사점**:` 으로 시작하는 단락(3~5문장).
   가설들의 결과를 관통하는 메타 통찰을 서술. 예: 어떤 종류의 가설이 잘 맞았고/틀렸는지,
   벤치마크 데이터와 실측 사이에 어떤 패턴의 간극이 보였는지, 향후 가설 설계에 대한 교훈 등.

OUTPUT에 "## 7. 가설 검증: 벤치마크 vs 실측 간극 분석" 헤딩으로 시작하는 섹션을 추가하세요.
이 섹션은 본 INSIGHTS의 §1~§6 다음에 위치하고, §8 향후 운영 권장은 그 뒤에 옵니다.
"""


RUNNABILITY_PROMPT_TEMPLATE = """\
You are evaluating whether an end-user can run a generated session's artifacts.

CONTEXT:
This session was generated by an AI coding agent for a DEEPX Agent-Driven Development task.
The output directory contains README.md, setup.sh, run.sh, and other artifacts.

ARTIFACTS (below):
- README.md content (the user's primary entrypoint instructions)
- setup.sh content (environment setup)
- run.sh content (how to actually run the result)
- session.log content (shell-wrapper command trace from setup.sh / run.sh)
- session.txt content (agent CLI transcript — exit codes, FPS / inference
  metrics, tool-call outputs the agent captured at execution time; NOT
  user-facing documentation)

YOUR TASK:
Judge whether a typical end-user (DEEPX SDK developer, but unfamiliar with this exact
session) could successfully follow README.md to install + run + verify this artifact.

Note: session.log records the shell wrappers' output; session.txt records
the agent's own execution evidence (often the actual inference run with
exit code + FPS that doesn't appear in session.log). Cross-reference both
when judging "Verification provided" — if session.txt shows a real inference
run completing with exit 0 + FPS, treat verification as PROVIDED even when
README only references --help / smoke checks.

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

session.log (excerpt, shell wrapper):
```
{SESSION_LOG}
```

session.txt (excerpt, agent CLI transcript — execution evidence):
```
{SESSION_TXT}
```

=====================

Produce the markdown analysis block now.
"""


# ---------------------------------------------------------------------------
# CLI invocation
# ---------------------------------------------------------------------------

def _format_group_comparison_block(report_dir: Path) -> str:
    """Format §4 group-comparison aggregates as a markdown block for the LLM.

    Reads analysis.json's ``per_group_tool`` (key: ``"<group>__<tool>"``) and
    produces three Δ tables (thinking effect, model-tier effect, combined) for
    direct inline citation in hypothesis verification. Returns "" when the
    JSON has no per_group_tool data (e.g. pre-metadata runs).
    """
    json_path = report_dir / "analysis.json"
    if not json_path.is_file():
        return ""
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return ""

    per_group = data.get("per_group_tool") or {}
    if not per_group:
        return ""

    # Reshape: {(group, tool): metrics}
    parsed: dict = {}
    for k, v in per_group.items():
        if "__" not in k:
            continue
        group, tool = k.split("__", 1)
        parsed[(group, tool)] = v

    tools = sorted({t for (_g, t) in parsed.keys() if t != "cursor-cli"})

    def _delta_table(group_a: str, group_b: str, label_a: str, label_b: str) -> str:
        rows = []
        for tool in tools:
            a = parsed.get((group_a, tool))
            b = parsed.get((group_b, tool))
            if not a or not b:
                continue
            delta_o = b.get("avg_overall_score", 0) - a.get("avg_overall_score", 0)
            delta_e = b.get("avg_execution_score", 0) - a.get("avg_execution_score", 0)
            delta_r = b.get("avg_runnability_score", 0) - a.get("avg_runnability_score", 0)
            rows.append(
                f"| {tool} | {a.get('avg_overall_score', 0):.1f} "
                f"| {b.get('avg_overall_score', 0):.1f} "
                f"| **{delta_o:+.1f}** | {delta_e:+.1f} | {delta_r:+.1f} |"
            )
        if not rows:
            return ""
        header = (
            f"| Tool | {label_a} Overall | {label_b} Overall | ΔOverall | ΔExec | ΔRunn |\n"
            "|------|---:|---:|---:|---:|---:|"
        )
        return header + "\n" + "\n".join(rows)

    blocks: List[str] = []
    blocks.append(
        "### 그룹 비교 — 가설 검증용 정량 데이터 (analyzer 자동 계산)\n\n"
        "다음 표들은 manifest의 mode/intended_models 메타데이터에서 자동 그룹화한 결과입니다. "
        "cursor-cli는 mode=NA(Composer 2.5 고정)이므로 모든 비교에서 제외됩니다.\n"
    )
    def _codex_row(group_a: str, group_b: str, label_a: str, label_b: str, heading: str) -> str:
        a = parsed.get((group_a, "codex-cli"))
        b = parsed.get((group_b, "codex-cli"))
        if not (a and b):
            return ""
        delta_o = b.get("avg_overall_score", 0) - a.get("avg_overall_score", 0)
        delta_e = b.get("avg_execution_score", 0) - a.get("avg_execution_score", 0)
        delta_r = b.get("avg_runnability_score", 0) - a.get("avg_runnability_score", 0)
        return (
            f"#### {heading}\n\n"
            f"| Tool | {label_a} Overall | {label_b} Overall | ΔOverall | ΔExec | ΔRunn |\n"
            "|------|---:|---:|---:|---:|---:|\n"
            f"| codex-cli | {a.get('avg_overall_score', 0):.1f} "
            f"| {b.get('avg_overall_score', 0):.1f} "
            f"| **{delta_o:+.1f}** | {delta_e:+.1f} | {delta_r:+.1f} |"
        )

    # Thinking effect — sonnet (3 tools) + codex separately
    th_tbl = _delta_table("NT_sonnet", "TH_sonnet", "NT", "TH")
    if th_tbl:
        blocks.append("#### Thinking 효과 — sonnet 4.6 도구 (R1-R5 vs R6-R10)\n\n" + th_tbl)
    th_codex = _codex_row(
        "NT_gpt53codex", "TH_gpt53codex", "NT", "TH",
        "Thinking 효과 — codex-cli (gpt-5.3-codex 고정, R1-R5 vs R6-R10)",
    )
    if th_codex:
        blocks.append(th_codex)

    # Model tier effect — Anthropic sonnet→opus + codex 5.3→5.5
    op_tbl = _delta_table("TH_sonnet", "TH_opus46", "sonnet TH", "opus TH")
    if op_tbl:
        blocks.append("#### 모델 등급 효과 — Anthropic (sonnet→opus, R6-R10 vs R11-R15)\n\n" + op_tbl)
    op_codex = _codex_row(
        "TH_gpt53codex", "TH_gpt55", "gpt-5.3-codex TH", "gpt-5.5 TH",
        "모델 등급 효과 — codex-cli (gpt-5.3-codex → gpt-5.5, R6-R10 vs R11-R15)",
    )
    if op_codex:
        blocks.append(op_codex)

    # Combined effect — Anthropic + codex
    combined_tbl = _delta_table("NT_sonnet", "TH_opus46", "NT sonnet", "TH opus")
    if combined_tbl:
        blocks.append("#### 종합 효과 (참고용) — Anthropic NT sonnet → TH opus\n\n" + combined_tbl)
    combined_codex = _codex_row(
        "NT_gpt53codex", "TH_gpt55", "NT gpt-5.3-codex", "TH gpt-5.5",
        "종합 효과 (참고용) — codex NT gpt-5.3-codex → TH gpt-5.5",
    )
    if combined_codex:
        blocks.append(combined_codex)

    blocks.append(
        "\n**가설 검증 시 위 표를 직접 인용하세요.** "
        "예: 'H3 thinking 효과 ✅ 지지 — sonnet 4.6에서 ΔOverall = +X.Xpt (4개 도구 평균), "
        "cursor-cli는 mode=NA로 제외.'"
    )
    return "\n\n".join(blocks)


def resolve_effective_model(cli: str, model: Optional[str],
                             allow_paid: bool) -> Optional[str]:
    """Pick the model to use for this CLI call.

    Precedence: explicit `model` arg > paid_default (if allow_paid) > free_default.
    Returns None when the CLI has no free option AND allow_paid is False —
    callers must skip the invocation in that case.

    If an explicit model is provided that matches a paid_default but allow_paid
    is False, returns None (blocks the paid model).
    """
    conf = CLI_CONFIG.get(cli, {})
    if model:
        # Guard: block paid model when allow_paid is False
        free_model = conf.get("free_default_model")
        if not allow_paid and free_model and model != free_model:
            # Check if the explicit model is NOT a known free model
            free_models = {"gpt-4.1", "gpt-5-mini", "gpt-5.4-mini", "auto",
                           "github-copilot/gpt-4.1"}
            if model not in free_models:
                print(f"BLOCKED: model '{model}' requires --allow-paid "
                      f"(free alternative: {free_model})", file=sys.stderr)
                return None
        return model
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

    # Node-based CLIs (cursor/opencode/copilot) need the system CA bundle to
    # verify TLS behind the corporate cert — without it they fail with
    # "unable to verify the first certificate" / "Connection lost, reconnecting".
    # Mirrors _cli_env.agent_subprocess_env so judge calls work without the
    # caller having to export NODE_EXTRA_CA_CERTS / NODE_OPTIONS first.
    _env = {**os.environ, "NO_COLOR": "1"}
    _ca_bundle = "/etc/ssl/certs/ca-certificates.crt"
    if os.path.isfile(_ca_bundle):
        _env.setdefault("NODE_EXTRA_CA_CERTS", _ca_bundle)
        _node_opts = _env.get("NODE_OPTIONS", "") or ""
        if "--use-system-ca" not in _node_opts:
            _env["NODE_OPTIONS"] = (_node_opts + " --use-system-ca").strip()

    # OS arg-length safety: if prompt > 100 KB, write to temp file and
    # replace the positional prompt arg with a file-read instruction.
    _MAX_ARG_BYTES = 100_000
    tmp_prompt_file = None
    try:
        if conf.get("prompt_via_arg"):
            if len(prompt.encode("utf-8")) > _MAX_ARG_BYTES:
                # Write prompt to a temp file, pass via stdin instead of arg
                import tempfile
                tmp_prompt_file = tempfile.NamedTemporaryFile(
                    mode="w", suffix=".md", delete=False, encoding="utf-8",
                )
                tmp_prompt_file.write(prompt)
                tmp_prompt_file.close()
                # Remove trailing `-p` from args (if present) since we'll use stdin
                if cmd[-1] == "-p":
                    cmd = cmd[:-1]
                r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                                   timeout=timeout_sec, env=_env)
            else:
                cmd.append(prompt)
                # stdin=DEVNULL: when the prompt is a positional arg, node CLIs may
                # still read stdin and block (claude warns + 3s-proceeds; others hang).
                r = subprocess.run(cmd, stdin=subprocess.DEVNULL, capture_output=True,
                                   text=True, timeout=timeout_sec, env=_env)
        else:
            # Pass via stdin
            r = subprocess.run(cmd, input=prompt, capture_output=True, text=True,
                               timeout=timeout_sec, env=_env)
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
    finally:
        if tmp_prompt_file is not None:
            try:
                os.unlink(tmp_prompt_file.name)
            except OSError:
                pass


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

    # Append §8 hypothesis verification if hypothesis.json exists
    hypothesis_path = report_dir / "hypothesis.json"
    if hypothesis_path.is_file():
        try:
            hyp_data = json.loads(hypothesis_path.read_text(encoding="utf-8"))
            hyp_lines = []
            for h in hyp_data.get("hypotheses", []):
                hyp_lines.append(f"- **{h.get('id', '?')}**: {h.get('statement', 'N/A')}")
                hyp_lines.append(f"  - Metric: {h.get('metric', 'N/A')}")
                ranking = h.get('expected_ranking', [])
                if ranking:
                    hyp_lines.append(f"  - 예상 순위: {' > '.join(ranking)}")
                hyp_lines.append(f"  - 신뢰도: {h.get('confidence', 'N/A')}")
            hypothesis_summary = "\n".join(hyp_lines)

            # Inject group-comparison tables from analysis.json so the LLM can
            # cite Δ values when checking thinking-effect / model-tier hypotheses
            # without re-deriving them from raw per_round data. cursor-cli is
            # already auto-excluded at aggregation time (NA_auto group).
            group_block = _format_group_comparison_block(report_dir)
            if group_block:
                hypothesis_summary = hypothesis_summary + "\n\n" + group_block

            prompt += HYPOTHESIS_VERIFICATION_SECTION.format(
                hypothesis_summary=hypothesis_summary,
            )
            print(f"  (appended §8 hypothesis verification — {len(hyp_data.get('hypotheses', []))} hypotheses)")
        except (json.JSONDecodeError, OSError) as e:
            print(f"WARN: could not read hypothesis.json for §8: {e}", file=sys.stderr)

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
        suite_root / "dx-agent-dev" / "e2e-tests" / "results" / "insights.md",
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


def _parse_existing_labels(existing_report: Path):
    """Parse an existing runnability_report.md and return a list of session
    label-tuples ``(round_label, tool, scenario, run_id)``, preserving file order.

    ``run_id`` defaults to ``"legacy"`` when a header lacks the ``(run=...)``
    suffix — this happens when the report was generated by an older insights.py
    that didn't emit run_id in headers, or when two single-run reports are
    naively concatenated into a merged file.

    Sequential ordering is critical for downstream pairing: when N existing
    entries match (tool, scenario, run_id), the first N current sessions for
    the same key are skipped — regardless of which round_index value the
    analyzer assigned in the current run (the renumbering done by multi-run-id
    mode would otherwise break direct R-label matching).

    Only includes sessions that were actually evaluated (have a verdict field),
    not those marked "CLI invocation failed/skipped".
    """
    if not existing_report.is_file():
        return []
    text = existing_report.read_text(encoding="utf-8", errors="ignore")
    labels = []
    # Match header forms:
    #   ### R1 claude-code dx_app
    #   ### R1 claude-code dx_app (run=20260521_202016)
    pattern = re.compile(
        r"^###\s+(R\d+)\s+(\S+)\s+(\S+?)(?:\s+\(run=([^)]+)\))?\s*$",
        re.MULTILINE,
    )
    for m in pattern.finditer(text):
        r_label, tool, scenario, run_id = m.groups()
        section_start = m.start()
        next_header = text.find("\n### ", section_start + 1)
        section = text[section_start:next_header] if next_header > 0 else text[section_start:]
        if re.search(r"end-user runnability.*?:\s*(PASS|PARTIAL|FAIL)", section, re.IGNORECASE):
            labels.append((r_label, tool, scenario, run_id or "legacy"))
    return labels


def _read_existing_sections(existing_report: Path) -> List[str]:
    """Read existing runnability_report.md and return list of raw section strings
    (each starting with '### R...'). Used to prepend existing results in merged output.
    """
    if not existing_report.is_file():
        return []
    text = existing_report.read_text(encoding="utf-8", errors="ignore")
    sections = []
    # Find the "세션별 평가" marker, then split by ### headers
    eval_start = text.find("## 세션별 평가")
    if eval_start < 0:
        eval_start = 0
    eval_text = text[eval_start:]
    parts = re.split(r"(?=^###\s)", eval_text, flags=re.MULTILINE)
    for part in parts:
        part = part.strip()
        if part.startswith("###"):
            sections.append(part)
    return sections


def run_runnability(report_dir: Path, cli: str, output_dir: Path,
                     *, model: Optional[str] = None,
                     allow_paid: bool = False,
                     existing_report: Optional[Path] = None) -> int:
    """Judge end-user runnability of ALL sessions using a CLI agent.

    Always evaluates every session (exhaustive mode).

    Incremental mode (--existing-report):
      When an existing runnability_report.md is provided, sessions already
      evaluated in that report are skipped. New results are merged with
      existing results in the output file.
    """
    json_path = report_dir / "analysis.json"
    if not json_path.is_file():
        print(f"ERROR: {json_path} not found", file=sys.stderr)
        return 2

    data = json.loads(json_path.read_text(encoding="utf-8"))
    sessions = data.get("sessions", [])

    # Parse existing report for incremental mode
    existing_labels: list = []
    existing_sections: List[str] = []
    if existing_report:
        existing_labels = _parse_existing_labels(existing_report)
        existing_sections = _read_existing_sections(existing_report)
        print(f"→ Incremental mode: {len(existing_labels)} sessions already evaluated "
              f"in {existing_report.name}")

    # Exhaustive: keep all sessions in their original (tool, round, scenario) order
    sampled = list(sessions)
    mode_label = "EXHAUSTIVE"

    # Filter out already-evaluated sessions in incremental mode.
    #
    # Matching strategy: count-based sequential pairing keyed by
    # (tool, scenario, run_id). For each (tool, scenario, run_id) group, the
    # first N current sessions are skipped where N = count of existing entries
    # with the same key. Legacy entries (run_id="legacy", from older reports
    # without run_id in the header) fall back to matching any current run_id
    # for the same (tool, scenario) — preserving the existing behavior for
    # single-run reports while also handling the multi-run-id merged case
    # (where round_index gets renumbered: NT R1-R5 stays R1-R5 but TH R1-R5
    # becomes R6-R10, breaking direct label matching).
    if existing_labels:
        from collections import Counter
        existing_count: Counter = Counter()
        for _r, _tool, _scen, _rid in existing_labels:
            existing_count[(_tool, _scen, _rid)] += 1

        used: Counter = Counter()

        def _is_already_evaluated(s: dict) -> bool:
            tool_s = s.get("tool", "")
            scen_s = s.get("scenario", "")
            run_id_s = s.get("run_id", "legacy") or "legacy"
            # 1) exact (tool, scenario, run_id) match
            exact_key = (tool_s, scen_s, run_id_s)
            if used[exact_key] < existing_count.get(exact_key, 0):
                used[exact_key] += 1
                return True
            # 2) legacy fallback: existing entries without run_id match any current run_id
            legacy_key = (tool_s, scen_s, "legacy")
            if legacy_key != exact_key and used[legacy_key] < existing_count.get(legacy_key, 0):
                used[legacy_key] += 1
                return True
            return False

        before_count = len(sampled)
        sampled = [s for s in sampled if not _is_already_evaluated(s)]
        skipped_count = before_count - len(sampled)
        print(f"  Skipping {skipped_count} already-evaluated sessions, "
              f"{len(sampled)} remaining")
        mode_label += f" (incremental, {skipped_count} reused)"

    # Pre-compute skip analysis (sessions with no output_dirs are skipped before
    # the LLM is called — categorize them so the report explains WHY).
    try:
        # Lazy import keeps insights.py runnable even if the lib path is unusual.
        sys.path.insert(0, str(Path(__file__).parent))
        from lib.skip_analyzer import (  # type: ignore
            categorize_skipped_sessions, render_skip_summary_markdown,
        )
    finally:
        if sys.path and sys.path[0] == str(Path(__file__).parent):
            sys.path.pop(0)
    skip_report = categorize_skipped_sessions(sessions)
    skip_md = render_skip_summary_markdown(skip_report, heading_level=2)

    out_path = output_dir / "runnability_report.md"
    started_at = datetime.now().isoformat(timespec='seconds')

    # Prepare merged results: existing sections first, then new evaluations
    merged_results: List[str] = list(existing_sections)

    total_evaluated = len(existing_labels)  # count of all evaluated (existing + new)

    def _write_report(new_results: List[str], done: int, new_total: int,
                      final: bool) -> None:
        """Write runnability_report.md with current progress. Called after every
        session in exhaustive mode so an interrupted run still leaves usable
        partial data on disk.
        """
        all_results = merged_results + new_results
        evaluated = total_evaluated + len(new_results)
        total_sessions = len(sessions)
        status = "complete" if final else f"in-progress ({done}/{new_total})"
        incremental_note = ""
        if existing_labels:
            incremental_note = (
                f"> Incremental: {len(existing_labels)} reused from existing report, "
                f"{len(new_results)} newly evaluated\n"
            )
        header = (
            f"# End-User Runnability Report\n"
            f"> Generated: {started_at}  (status: {status})\n"
            f"> Sessions evaluated: {evaluated}/{total_sessions}  |  "
            f"Mode: {mode_label}  |  CLI: `{cli}`\n"
            f"{incremental_note}"
            f"> Sessions skipped (no artifacts to evaluate): "
            f"{skip_report['skipped_count']}/{skip_report['total_sessions']}\n\n"
            f"---\n\n"
            f"{skip_md}\n"
            f"---\n\n"
            f"## 세션별 평가\n\n"
        )
        out_path.write_text(header + "\n\n---\n\n".join(all_results), encoding="utf-8")

    if not sampled:
        print("All sessions already evaluated — writing merged report.")
        _write_report([], 0, 0, final=True)
        print(f"✓ Wrote runnability report to: {out_path}")
        return 0

    print(f"Evaluating runnability of {len(sampled)} sessions ({mode_label}, CLI: {cli})...")
    new_results: List[str] = []
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
        # Option D: also feed the agent CLI transcript so the LLM can detect
        # inference evidence (FPS / exit-code 0 / "Inference complete") that
        # the shell wrappers (setup.sh / run.sh) never wrote to session.log.
        stxt = _read_safely(out_dir / "session.txt", 4000)

        # Include run_id in the section label (and thus in the eventual
        # `### R1 ... (run=...)` header in runnability_report.md) so future
        # incremental runs can disambiguate sessions with the same R+tool+scenario
        # but different source runs (multi-run-id merged case).
        run_id_s = s.get("run_id", "") or ""
        if run_id_s and run_id_s != "legacy":
            label = f"R{round_ix} {tool} {scenario} (run={run_id_s})"
        else:
            label = f"R{round_ix} {tool} {scenario}"
        prompt = RUNNABILITY_PROMPT_TEMPLATE.format(
            session_label=label,
            README=readme, SETUP=setup, RUN=run_sh,
            SESSION_LOG=slog, SESSION_TXT=stxt,
        )
        print(f"  [{i}/{total}] {label}")
        ans = invoke_cli(cli, prompt, model=model, allow_paid=allow_paid,
                          timeout_sec=180)
        if ans is None:
            new_results.append(f"### {label}\n\n(CLI invocation failed/skipped)\n")
        else:
            new_results.append(ans.strip() + "\n")
        # Incremental flush — protects multi-hour exhaustive runs against
        # interruption (kill, timeout, machine reboot). Cheap (<1ms per call).
        _write_report(new_results, i, total, final=False)

    _write_report(new_results, len(new_results), total, final=True)
    print(f"✓ Wrote runnability report to: {out_path}")
    return 0


# ---------------------------------------------------------------------------
# Mode: hypothesis
# ---------------------------------------------------------------------------


def run_hypothesis(prompt_path: Path, output_dir: Path, cli: str,
                   *, model: Optional[str] = None,
                   allow_paid: bool = True) -> int:
    """Read a prompt template (.md), invoke an LLM, write hypothesis.json.

    If *prompt_path* is a .json file, copy it directly (skip LLM).
    Returns 0 on success, non-zero on failure.
    """
    if prompt_path.suffix.lower() == ".json":
        import shutil as _shutil
        dest = output_dir / "hypothesis.json"
        _shutil.copy2(prompt_path, dest)
        print(f"  ✓ hypothesis.json copied from {prompt_path}")
        return 0

    prompt_text = prompt_path.read_text(encoding="utf-8")

    result = invoke_cli(cli, prompt_text, model=model, allow_paid=allow_paid,
                        timeout_sec=600)
    if result is None:
        print("ERROR: hypothesis generation failed — no LLM response",
              file=sys.stderr)
        return 1

    # Extract JSON from response (may be wrapped in markdown code block)
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', result, re.DOTALL)
    if json_match:
        raw_json = json_match.group(1)
    else:
        # Try the entire response as JSON
        raw_json = result.strip()

    # Validate JSON
    try:
        parsed = json.loads(raw_json)
    except json.JSONDecodeError as e:
        print(f"ERROR: LLM returned invalid JSON: {e}", file=sys.stderr)
        # Save raw response for debugging
        raw_path = output_dir / "hypothesis_raw.txt"
        raw_path.write_text(result, encoding="utf-8")
        print(f"  Raw LLM response saved to: {raw_path}", file=sys.stderr)
        return 1

    # Basic schema validation
    if "hypotheses" not in parsed:
        print("WARN: hypothesis.json missing 'hypotheses' key", file=sys.stderr)
    num_hyp = len(parsed.get("hypotheses", []))

    out_path = output_dir / "hypothesis.json"
    out_path.write_text(
        json.dumps(parsed, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"  ✓ hypothesis.json written ({num_hyp} hypotheses)")
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
    # Tri-state for allow-paid: None (apply mode-specific default) / True / False.
    # An explicit env var setting overrides the default; absence leaves it None.
    env_allow_paid: Optional[bool] = (
        _env_bool("DX_INSIGHTS_ALLOW_PAID") if "DX_INSIGHTS_ALLOW_PAID" in os.environ
        else None
    )

    p = argparse.ArgumentParser(description="Agent-Driven insight generator (post-analysis)")
    p.add_argument("--mode", choices=["insights", "runnability", "hypothesis"],
                   required=True,
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
    p.add_argument("--allow-paid", action=argparse.BooleanOptionalAction,
                   default=env_allow_paid,
                   help=("Permit paid/billed model selections (Claude Code seat, "
                         "claude-sonnet-4-6 via copilot, gpt-5/codex, etc.). "
                         "Mode-specific defaults when neither --allow-paid nor "
                         "--no-allow-paid is given: insights → PAID (context >64K "
                         "needs sonnet-4.6), runnability → FREE (gpt-4.1 fits "
                         "per-session prompts). Env: DX_INSIGHTS_ALLOW_PAID=0|1"))
    p.add_argument("--output-dir", default=None,
                   help="Where to write the output (default: same as --report-dir)")
    p.add_argument("--existing-report", default=None,
                   help=("(runnability mode) path to an existing runnability_report.md "
                         "from a previous run. Sessions already evaluated in that "
                         "report are skipped; new results are merged with existing "
                         "ones. Use this for incremental runnability evaluation "
                         "(e.g. adding rounds 11-20 to an existing 10-round report)."))
    p.add_argument("--prompt", default=None,
                   help=("(hypothesis mode) path to hypothesis prompt template "
                         "(.md) or pre-built hypothesis (.json). Required for "
                         "hypothesis mode. If .json, copied directly without "
                         "LLM invocation."))

    args = p.parse_args(argv)
    report_dir = Path(args.report_dir).resolve()
    if not report_dir.is_dir():
        print(f"ERROR: report-dir not found: {report_dir}", file=sys.stderr)
        return 2
    out_dir = Path(args.output_dir).resolve() if args.output_dir else report_dir

    # Apply mode-specific default for allow_paid when caller didn't specify.
    # Rationale: insights/hypothesis often benefit from higher-context or
    # higher-capability models, while runnability fits free models.
    if args.allow_paid is None:
        if args.mode in ("insights", "hypothesis"):
            args.allow_paid = True
            print(f"NOTE: {args.mode} mode defaulting to --allow-paid (copilot + "
                  "claude-sonnet-4.6). Pass --no-allow-paid to force a free model.",
                  file=sys.stderr)
        else:
            args.allow_paid = False

    # Resolve CLI (handle 'auto' here so failures emit a clear message)
    chosen_cli = resolve_cli(args.cli, args.allow_paid)
    if not chosen_cli:
        chain = AUTO_CHAIN_PAID if args.allow_paid else AUTO_CHAIN_FREE
        print(f"ERROR: no usable CLI found. Tried: {chain}. "
              f"Install one (or pass --allow-paid to widen the chain), or use "
              f"--cli <name> with a specific binary in PATH.", file=sys.stderr)
        return 3

    if args.mode == "insights":
        return run_insights(report_dir, chosen_cli, out_dir,
                            model=args.model, allow_paid=args.allow_paid)
    elif args.mode == "runnability":
        existing = Path(args.existing_report).resolve() if args.existing_report else None
        return run_runnability(report_dir, chosen_cli, out_dir,
                               model=args.model, allow_paid=args.allow_paid,
                               existing_report=existing)
    elif args.mode == "hypothesis":
        if not args.prompt:
            print("ERROR: --prompt is required for hypothesis mode",
                  file=sys.stderr)
            return 2
        prompt_path = Path(args.prompt)
        if not prompt_path.is_file():
            print(f"ERROR: prompt file not found: {prompt_path}",
                  file=sys.stderr)
            return 2
        return run_hypothesis(prompt_path, out_dir, chosen_cli,
                              model=args.model, allow_paid=args.allow_paid)
    return 0


if __name__ == "__main__":
    sys.exit(main())
