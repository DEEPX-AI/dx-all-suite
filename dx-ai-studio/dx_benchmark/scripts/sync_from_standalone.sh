#!/usr/bin/env bash
# Bundle a snapshot (results/ + dataset.json) from the standalone dx-benchmark.
# Usage: sync_from_standalone.sh [SRC_DIR]   (default: ../../dx-benchmark relative to studio root)
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
STUDIO_BENCH_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SRC_DIR="${1:-$STUDIO_BENCH_DIR/../../dx-benchmark}"
if [ ! -d "$SRC_DIR" ]; then echo "ERROR: standalone dx-benchmark source not found: $SRC_DIR" >&2; exit 1; fi

# Prefer a prebuilt dataset; otherwise build it with the standalone tool.
DATASET="$SRC_DIR/results/dashboard/dataset.json"
if [ ! -f "$DATASET" ]; then
  if [ -f "$SRC_DIR/run.sh" ]; then ( cd "$SRC_DIR" && ./run.sh dashboard results ) || \
    { echo "ERROR: failed to build dataset.json via standalone run.sh" >&2; exit 1; }
  fi
fi
[ -f "$DATASET" ] || { echo "ERROR: dataset.json not produced at $DATASET" >&2; exit 1; }

rm -rf "$STUDIO_BENCH_DIR/results"
mkdir -p "$STUDIO_BENCH_DIR/results"
# copy per-run result trees (exclude the built dashboard/ subdir)
( cd "$SRC_DIR/results" && find . -mindepth 1 -maxdepth 1 -type d ! -name dashboard -print0 | \
  xargs -0 -I{} cp -r "{}" "$STUDIO_BENCH_DIR/results/" )
cp "$DATASET" "$STUDIO_BENCH_DIR/dataset.json"
echo "Synced snapshot from $SRC_DIR → $STUDIO_BENCH_DIR (dataset.json + results/)"
