#!/usr/bin/env bash
# DX Model Zoo — release-prep catalog sync.
#
# WHY THIS EXISTS
#   The OFFICIAL model metadata that ships to the public Model Zoo — accuracy,
#   fps, and the onnx/dxnn download URLs — lives ONLY on the internal publish
#   site (https://modelzoo-publish-api.devops.dpx.ai). Those keys are "additive":
#   catalog.py::_enrich_model_entry sources them from generated_catalog.json at
#   load time; they are deliberately NOT in the curated model_catalog.json. So
#   generated_catalog.json must be a *shipped* artifact for the offline build to
#   expose official data.
#
#   >>> This script MUST run in the general-net release stage (which HAS internal
#   >>> network access) BEFORE packaging, so the freshly-fetched official snapshot
#   >>> gets committed/packaged. The air-gapped PR-CI stage CANNOT reach the
#   >>> internal site — it relies on the shipped snapshot (or, if absent, the
#   >>> conftest local bootstrap). Do NOT expect this to fetch anything in CI.
#
# WHAT IT DOES
#   Tries source profiles in order of authoritativeness until one genuinely
#   produces official data:
#     1. internal  — the publish site (self-signed TLS → --no-verify-tls)
#     2. public     — developer.deepx.ai fallback (real network fetch)
#     3. local      — offline bootstrap from the local repos (never absent)
#   "Genuine success" for a network profile means model_count > 0 AND its remote
#   adapter reported NO errors — because sync_metadata can otherwise exit 0 by
#   quietly falling back to a prior cache / on-disk catalog even when the network
#   is down. We inspect sync_report.json to tell the difference honestly.
#
# EXIT CODES
#   0  — a profile succeeded (logged), OR all profiles failed but an existing
#        generated_catalog.json is already on disk (kept, not clobbered).
#   1  — all profiles failed AND no generated_catalog.json exists.
#
# Usage:
#   bash dx_modelzoo/scripts/sync_release_catalog.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# Prefer the project venv's interpreter if present; fall back to system python3.
PY="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY=python3

CATALOG="$ROOT/dx_modelzoo/data/generated_catalog.json"
REPORT="$ROOT/dx_modelzoo/data/sync_report.json"

# Inspect the last sync report: prints "<model_count> <remote_adapter_errors>"
# where remote_adapter_errors counts adapter_errors mentioning the given remote
# adapter name (empty arg → total adapter_errors). Prints "0 1" if unreadable.
report_stats() {
  local remote_adapter="$1"
  "$PY" - "$REPORT" "$remote_adapter" <<'PY'
import json, sys
try:
    r = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    print("0 1"); sys.exit(0)
count = r.get("model_count", 0)
errs = r.get("adapter_errors", []) or []
remote = sys.argv[2]
n = len([e for e in errs if (remote in e if remote else True)])
print(f"{count} {n}")
PY
}

# try_profile <profile> <remote_adapter_name> [extra sync args...]
# Returns 0 iff the sync genuinely produced official data for that profile.
try_profile() {
  local profile="$1"; shift
  local remote_adapter="$1"; shift
  echo "== release-sync: trying --source ${profile} =="
  if ! "$PY" -m dx_modelzoo.tools.sync_metadata --source "$profile" "$@"; then
    echo "   ${profile}: sync CLI exited nonzero" >&2
    return 1
  fi
  local stats count errs
  stats="$(report_stats "$remote_adapter")"
  count="${stats%% *}"
  errs="${stats##* }"
  if [ "$count" -le 0 ]; then
    echo "   ${profile}: sync produced 0 models" >&2
    return 1
  fi
  if [ -n "$remote_adapter" ] && [ "$errs" -gt 0 ]; then
    echo "   ${profile}: remote adapter '${remote_adapter}' reported ${errs} error(s) — data not authoritative" >&2
    return 1
  fi
  echo "   ${profile}: OK (${count} models)"
  return 0
}

if try_profile internal internal_modelzoo --no-verify-tls; then
  echo "release-sync: SUCCESS via 'internal' (official publish-site snapshot)"
  exit 0
fi

echo "release-sync: internal unreachable — falling back to 'public'" >&2
if try_profile public public_modelzoo; then
  echo "release-sync: SUCCESS via 'public' (developer.deepx.ai)"
  exit 0
fi

echo "release-sync: public unreachable — falling back to 'local'" >&2
if try_profile local ""; then
  echo "release-sync: SUCCESS via 'local' (offline bootstrap)"
  exit 0
fi

# All profiles failed. Keep an existing snapshot rather than shipping nothing.
if [ -s "$CATALOG" ]; then
  echo "release-sync: all profiles failed, but existing generated_catalog.json is present — keeping it" >&2
  exit 0
fi

echo "release-sync: FAILED — all profiles failed and no generated_catalog.json exists" >&2
exit 1
