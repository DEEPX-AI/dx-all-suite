#!/usr/bin/env python3
"""Build a non-thinking vs thinking comparison HTML.

Inputs: two analyzer_reports/<run_id>/<ts>/ directories.
Output: comparison.html with per-tool/per-scenario delta table + side-by-side iframes.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import sys as _sys
_sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import env_failure as _ef  # noqa: E402


def _row_is_env_failure(r: dict) -> bool:
    """Single source of truth: lib.env_failure.is_env_failure decides exclusion.

    Pulls the same signals SessionEval feeds it from per_session.csv columns.
    Robust to older CSVs (pre-T3) that lack env_failure_signature — uses ""
    fallback and lets criterion A/B handle the case.
    """
    def _b(x):
        return str(x).strip().lower() in ("true", "1", "yes")

    def _i(x):
        try:
            return int(float(x))
        except (TypeError, ValueError):
            return 0

    exit_raw = r.get("exit_status_round")
    try:
        exit_status = int(float(exit_raw)) if exit_raw not in (None, "", "NA") else None
    except (TypeError, ValueError):
        exit_status = None
    return _ef.is_env_failure(
        env_signature=(r.get("env_failure_signature") or ""),
        has_start=_b(r.get("has_start")),
        has_done=_b(r.get("has_done")),
        exit_status=exit_status,
        has_output_dirs=bool((r.get("output_dirs") or "").strip()),
        output_tokens=_i(r.get("output_tokens")),
        tool_call_count=_i(r.get("tool_call_count")),
    )


def load_per_session(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        print(f"WARN: missing {path}", file=sys.stderr)
        return rows
    with path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows


def to_float(s: str | None) -> float | None:
    if s in (None, "", "NA", "N/A"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


# Map logical metric → per_session.csv column name. Composite isn't in the CSV
# (it's recomputed from compliance/quality/execution/runnability with v2.1
# scenario-aware weights), so we omit it from comparison.
METRIC_COLUMNS = {
    "compliance": "compliance_pct",
    "quality": "quality_score",
    "execution_trace": "execution_score",
    "runnability": "runnability_score",
    "overall": "overall_score",
}


def aggregate(rows: list[dict[str, Any]]) -> dict[tuple[str, str], dict[str, float]]:
    """(tool, scenario) -> {metric: mean}."""
    buckets: dict[tuple[str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if _row_is_env_failure(r):
            continue
        tool = r.get("tool") or ""
        scenario = r.get("scenario") or ""
        if not tool or not scenario:
            continue
        for m, col in METRIC_COLUMNS.items():
            v = to_float(r.get(col))
            if v is not None:
                buckets[(tool, scenario)][m].append(v)
    return {
        (tool, scenario): {m: (sum(vs) / len(vs)) if vs else float("nan") for m, vs in mdict.items()}
        for (tool, scenario), mdict in buckets.items()
    }


def aggregate_by_tool(rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    buckets: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for r in rows:
        if _row_is_env_failure(r):
            continue
        tool = r.get("tool") or ""
        if not tool:
            continue
        for m, col in METRIC_COLUMNS.items():
            v = to_float(r.get(col))
            if v is not None:
                buckets[tool][m].append(v)
    return {
        tool: {m: (sum(vs) / len(vs)) if vs else float("nan") for m, vs in mdict.items()}
        for tool, mdict in buckets.items()
    }


def fmt(v: float) -> str:
    if v != v:  # NaN
        return "—"
    return f"{v:.1f}"


def fmt_delta(a: float, b: float) -> str:
    if a != a or b != b:
        return "—"
    d = b - a
    sign = "+" if d > 0 else ""
    color = "#0a8a3f" if d > 0 else "#c62828" if d < 0 else "#666"
    return f'<span style="color:{color};font-weight:600">{sign}{d:.1f}</span>'


def _report_rel(report_dir: Path) -> str:
    """Return a relative URL from the comparison.html location to report_dir's
    comprehensive_report.html.

    The comparison.html is written alongside the two report dirs (e.g.
    <label>/comparison.html with <label>/old/ and <label>/new/).

    When report_dir is inside an ``analyzer_reports/`` tree the original
    depth-counting logic is preserved.  When ``analyzer_reports`` is absent
    from the path (e.g. a durable archive at $HOME/shared/…/<label>/old/) we
    fall back to ``<dirname>/comprehensive_report.html``, which is the correct
    sibling-relative path from the comparison file location.
    """
    try:
        idx = report_dir.parts.index("analyzer_reports")
        depth = len(report_dir.parts[idx + 1:])
        return "../" * depth + str(report_dir.relative_to(report_dir.parents[2])) + "/comprehensive_report.html"
    except ValueError:
        # "analyzer_reports" not in path — fall back to sibling-relative link
        return f"{report_dir.name}/comprehensive_report.html"


def render_html(non_thinking_dir: Path, thinking_dir: Path, non_thinking_run_id: str, thinking_run_id: str) -> str:
    nt_csv = load_per_session(non_thinking_dir / "per_session.csv")
    th_csv = load_per_session(thinking_dir / "per_session.csv")

    nt_by_pair = aggregate(nt_csv)
    th_by_pair = aggregate(th_csv)
    nt_by_tool = aggregate_by_tool(nt_csv)
    th_by_tool = aggregate_by_tool(th_csv)

    tools = sorted(set(nt_by_tool.keys()) | set(th_by_tool.keys()))
    metrics = tuple(METRIC_COLUMNS.keys())
    metric_labels = {
        "compliance": "Compliance",
        "quality": "Quality",
        "execution_trace": "ExecutionTrace",
        "runnability": "Runnability",
        "overall": "Overall",
    }

    # Per-tool delta table
    tool_rows = []
    for tool in tools:
        nt = nt_by_tool.get(tool, {})
        th = th_by_tool.get(tool, {})
        cells = [f"<th>{html.escape(tool)}</th>"]
        for m in metrics:
            a = nt.get(m, float("nan"))
            b = th.get(m, float("nan"))
            cells.append(f"<td>{fmt(a)}</td><td>{fmt(b)}</td><td>{fmt_delta(a, b)}</td>")
        tool_rows.append("<tr>" + "".join(cells) + "</tr>")

    # Per-(tool,scenario) delta table
    pairs = sorted(set(nt_by_pair.keys()) | set(th_by_pair.keys()))
    pair_rows = []
    for (tool, scenario) in pairs:
        nt = nt_by_pair.get((tool, scenario), {})
        th = th_by_pair.get((tool, scenario), {})
        cells = [f"<th>{html.escape(tool)}</th>", f"<td>{html.escape(scenario)}</td>"]
        for m in metrics:
            a = nt.get(m, float("nan"))
            b = th.get(m, float("nan"))
            cells.append(f"<td>{fmt(a)}</td><td>{fmt(b)}</td><td>{fmt_delta(a, b)}</td>")
        pair_rows.append("<tr>" + "".join(cells) + "</tr>")

    # Header row spanning NT/TH/Δ for each metric
    metric_header_top = "<tr><th rowspan=2>Tool</th>" + "".join(
        f'<th colspan="3">{metric_labels[m]}</th>' for m in metrics
    ) + "</tr>"
    metric_header_sub = "<tr>" + "".join("<th>NT</th><th>TH</th><th>Δ</th>" for _ in metrics) + "</tr>"

    pair_header_top = "<tr><th rowspan=2>Tool</th><th rowspan=2>Scenario</th>" + "".join(
        f'<th colspan="3">{metric_labels[m]}</th>' for m in metrics
    ) + "</tr>"

    nt_report_rel = _report_rel(non_thinking_dir)
    th_report_rel = _report_rel(thinking_dir)

    html_str = f"""<!DOCTYPE html>
<html lang="ko"><head>
<meta charset="utf-8">
<title>Non-thinking vs Thinking 비교 — {html.escape(non_thinking_run_id)} vs {html.escape(thinking_run_id)}</title>
<style>
body{{font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;max-width:1400px;margin:24px auto;padding:0 24px;color:#222}}
h1,h2{{border-bottom:2px solid #0a4d8c;padding-bottom:6px;color:#0a4d8c}}
table{{border-collapse:collapse;width:100%;margin:16px 0;font-size:13px}}
th,td{{border:1px solid #ccc;padding:6px 10px;text-align:right}}
th{{background:#eef3f9}}
th:first-child,td:first-child{{text-align:left}}
.meta{{background:#f5f5f5;padding:12px 16px;border-radius:6px;margin:8px 0;font-size:13px}}
.meta code{{background:#fff;padding:2px 4px;border-radius:3px}}
.legend{{font-size:12px;color:#666;margin-top:4px}}
.iframe-wrap{{display:flex;gap:8px;margin-top:24px}}
.iframe-wrap > div{{flex:1;display:flex;flex-direction:column}}
.iframe-wrap iframe{{width:100%;height:1200px;border:1px solid #ccc;border-radius:4px}}
.iframe-wrap h3{{margin-bottom:4px;color:#0a4d8c}}
.iframe-wrap a{{font-size:12px;color:#0a4d8c}}
</style>
</head><body>
<h1>Non-thinking vs Thinking 비교 리포트</h1>
<div class="meta">
  <strong>Non-thinking (NT)</strong>: <code>{html.escape(non_thinking_run_id)}</code> → <code>{html.escape(str(non_thinking_dir))}</code><br>
  <strong>Thinking (TH)</strong>: <code>{html.escape(thinking_run_id)}</code> → <code>{html.escape(str(thinking_dir))}</code><br>
  <span class="legend">Δ = TH − NT (양수 = thinking 모드가 더 높음, 색: 녹색 ↑ / 빨강 ↓)</span>
</div>

<h2>1. 도구별 종합 (NT vs TH)</h2>
<table>
  {metric_header_top}
  {metric_header_sub}
  {''.join(tool_rows)}
</table>

<h2>2. (도구 × 시나리오)별 상세</h2>
<table>
  {pair_header_top}
  <tr>{''.join('<th>NT</th><th>TH</th><th>Δ</th>' for _ in metrics)}</tr>
  {''.join(pair_rows)}
</table>

<h2>3. 원본 리포트 (side-by-side)</h2>
<div class="iframe-wrap">
  <div>
    <h3>Non-thinking</h3>
    <a href="{html.escape(nt_report_rel)}" target="_blank">새 창에서 열기 ↗</a>
    <iframe src="{html.escape(nt_report_rel)}" title="non-thinking"></iframe>
  </div>
  <div>
    <h3>Thinking</h3>
    <a href="{html.escape(th_report_rel)}" target="_blank">새 창에서 열기 ↗</a>
    <iframe src="{html.escape(th_report_rel)}" title="thinking"></iframe>
  </div>
</div>

<p style="margin-top:32px;color:#888;font-size:11px">Generated by build_comparison.py</p>
</body></html>
"""
    return html_str


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--non-thinking-dir", required=True, help="Path to analyzer_reports/<nt_run_id>/<ts>/")
    ap.add_argument("--thinking-dir", required=True, help="Path to analyzer_reports/<th_run_id>/<ts>/")
    ap.add_argument("--non-thinking-run-id", required=True)
    ap.add_argument("--thinking-run-id", required=True)
    ap.add_argument("--output", required=True, help="Output HTML path")
    args = ap.parse_args()

    nt_dir = Path(args.non_thinking_dir).resolve()
    th_dir = Path(args.thinking_dir).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    html_str = render_html(nt_dir, th_dir, args.non_thinking_run_id, args.thinking_run_id)
    out_path.write_text(html_str, encoding="utf-8")
    print(f"Wrote: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
