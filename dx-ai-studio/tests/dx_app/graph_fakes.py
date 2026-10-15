"""Fake graph binaries for the Graph Composer server tests.

Each fake is a bash script named like the real binary that prints recorded CLI output from fixtures/graph, captured
on a DX-M1 host on 2026-10-14: the *.txt files from dx_app 020782cc (no --json yet), list_models.json and check_*.json
from the dx_app Phase 1 work in progress (c822a118 plus its uncommitted --check --json), re-checked against the
landed build (c449d8a2). run_progress.log and report.json are a real 2-frame NPU run of cascade_od_attr.json on
assets/videos/dance-group.mov with DXAPP_PROGRESS=1 and --report-timing (c449d8a2).
Installing a fake points graph_cli at it and keeps temporary graph files in the test's tmp_path.
"""
from __future__ import annotations

import stat
from pathlib import Path

FIX = Path(__file__).resolve().parent / "fixtures" / "graph"


def fixture(name: str) -> str:
    return (FIX / name).read_text(encoding="utf-8")


def install(tmp_path: Path, monkeypatch, body: str, variants=("sync", "async")) -> Path:
    """Write `body` as every graph binary and make graph_cli find only these. Returns the bin dir.

    The script sees FIX (fixtures dir) and CALLS (a file each call appends its arguments to)."""
    from dx_app.core import graph_cli

    d = tmp_path / "bin"
    d.mkdir(exist_ok=True)
    calls = tmp_path / "calls.log"
    for v in variants:
        p = d / graph_cli.NAMES[v]
        p.write_text(f'#!/usr/bin/env bash\nFIX="{FIX}"\nCALLS="{calls}"\necho "$@" >> "$CALLS"\n{body}\n',
                     encoding="utf-8")
        p.chmod(p.stat().st_mode | stat.S_IXUSR)
    monkeypatch.setattr(graph_cli, "_search_dirs", lambda: [d])
    monkeypatch.setattr(graph_cli, "scratch_file", lambda prefix: tmp_path / f"{prefix}.json")
    monkeypatch.setattr(graph_cli, "models_dir", lambda: tmp_path / "models")
    (tmp_path / "models").mkdir(exist_ok=True)
    graph_cli._caps_cache.clear()
    return d


def calls(tmp_path: Path) -> list[str]:
    p = tmp_path / "calls.log"
    return p.read_text(encoding="utf-8").splitlines() if p.exists() else []


# --help without --json, and --check refusing "engine": today's dx_app.
TEXT_CLI = r"""
case "$1" in
  --help) cat "$FIX/help.txt"; exit 0 ;;
  --list-models) cat "$FIX/list_models.txt"; exit 0 ;;
  --check)
    if grep -q '"engine"' "$2"; then cat "$FIX/check_err_engine_key.txt" >&2; exit 1; fi
    if grep -q '"depth"' "$2"; then cat "$FIX/check_err_edge.txt" >&2; exit 1; fi
    cat "$FIX/check_ok_cascade_od_attr.txt"; exit 0 ;;
esac
exit 2
"""

# The dx_app Phase 1 CLI: --json on --list-models / --check, --report-timing, and the "engine" key accepted.
JSON_CLI = r"""
case "$1" in
  --help) cat "$FIX/help.txt"; echo "  --report-timing       with --report: add each frame's node_ms"
          echo "  --json                with --check or --list-models: one JSON document"; exit 0 ;;
  --list-models) cat "$FIX/list_models.json"; exit 0 ;;
  --check)
    if grep -q '"depth"' "$2"; then cat "$FIX/check_err.json"; exit 1; fi
    cat "$FIX/check_ok.json"; exit 0 ;;
esac
exit 2
"""

# The dx_app Phase 2 CLI (docs/superpowers/plans/2026-10-14-graph-composer-p2-dxapp.md Tasks 12-15), recorded from
# that plan until its build lands (Task "align with dx_app" re-captures them): list_ops.json is its --list-ops --json
# catalog, help_p2.txt its --help, check_logic_*.json --check --json on zone_intrusion.json (and with a 2-point
# polygon), run_events.log / events.jsonl / report_logic.json a 2-frame run of it, examples/*.json its six samples.
P2_CLI = r"""
case "$1" in
  --help) cat "$FIX/help_p2.txt"; exit 0 ;;
  --list-models) cat "$FIX/list_models.json"; exit 0 ;;
  --list-ops) cat "$FIX/list_ops.json"; exit 0 ;;
  --check)
    if grep -q '"polygon": \[[0-9.]*, *[0-9.]*, *[0-9.]*, *[0-9.]*\]' "$2"; then   # a polygon of 2 points
      cat "$FIX/check_logic_err.json"; exit 1; fi
    if grep -q '"logic"' "$2"; then cat "$FIX/check_logic_ok.json"; exit 0; fi
    if grep -q '"depth"' "$2"; then cat "$FIX/check_err.json"; exit 1; fi
    cat "$FIX/check_ok.json"; exit 0 ;;
esac
exit 2
"""


def install_examples(root: Path) -> Path:
    """Copy the six logic sample graphs into <root>/src/cpp_example/multi_model_graph (a fake dx_app root)."""
    d = root / "src" / "cpp_example" / "multi_model_graph"
    d.mkdir(parents=True, exist_ok=True)
    for p in sorted((FIX / "examples").glob("*.json")):
        (d / p.name).write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    return d


# The dx_app results-for-front-ends CLI (e4840f9b): help_p3.txt is its --help; layers/layers_fanout.json the real
# layers.json of fanout_od_seg_depth on sample_street.jpg, layers/layers_two_sources.json that of
# multistream_od_two_sources (both with --output result.jpg). The runner writes what the real one writes: --output
# (one file per stream with several sources: result_<source>_000000.jpg, or result_<source>.mp4), --report, and with
# --output-layers the layers.json of one source or of two (cam1, cam2), its PNGs as tiny stand-ins (layers/base.png
# 16x12 RGB, layers/layer.png 16x12 RGBA), and the closing "layers: <dir>/layers.json" line. Arguments are echoed as
# "arg ..." lines; SLEEP=<s> holds it until SIGTERM.
LAYERS_RUNNER = r"""
case "$1" in --help) cat "$FIX/help_p3.txt"; exit 0 ;; --check) exit 0 ;; esac
out=""; rep=""; lay=""; srcs=""
while [ $# -gt 0 ]; do
  case "$1" in
    --output) out="$2"; shift 2 ;;
    --report) rep="$2"; shift 2 ;;
    --output-layers) lay="$2"; shift 2 ;;
    --input) srcs="$srcs ${2%%=*}"; echo "arg --input $2"; shift 2 ;;
    *) echo "arg $1"; shift ;;
  esac
done
if [ -n "$SLEEP" ]; then trap 'echo stopped; exit 0' TERM; sleep "$SLEEP" & wait; fi
set -- $srcs
cat "$FIX/run_progress.log"
[ -n "$rep" ] && cp "$FIX/report.json" "$rep"
ext="${out##*.}"; stem="${out%.*}"
if [ $# -gt 1 ]; then
  for s in "$@"; do
    if [ "$ext" = "mp4" ]; then printf 'vid' > "${stem}_${s}.mp4"; else printf 'img' > "${stem}_${s}_000000.${ext}"; fi
  done
else
  printf 'img' > "$out"
fi
if [ -n "$lay" ]; then
  mkdir -p "$lay"
  if [ $# -gt 1 ]; then cp "$FIX/layers/layers_two_sources.json" "$lay/layers.json"
  else cp "$FIX/layers/layers_fanout.json" "$lay/layers.json"; fi
  names() { grep -o "\"$1\": *\"[^\"]*\"" "$lay/layers.json" | sed 's/.*"\([^"]*\)"$/\1/'; }
  for f in $(names base); do cp "$FIX/layers/base.png" "$lay/$f"; done
  for f in $(names file); do cp "$FIX/layers/layer.png" "$lay/$f"; done
  echo "layers: $lay/layers.json"
fi
exit 0
"""
