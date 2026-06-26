#!/usr/bin/env python3
"""Verify yolo26n_deepx_model artifacts exist and are valid."""
import sys
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MODEL_DIR = SCRIPT_DIR / "yolo26n_deepx_model"

errors = []

if not MODEL_DIR.exists():
    print(f"[verify] ✗ yolo26n_deepx_model/ directory not found — run export.py first", file=sys.stderr)
    sys.exit(1)

for fname in ["yolo26n.dxnn", "config.json", "metadata.yaml"]:
    p = MODEL_DIR / fname
    if p.exists():
        print(f"[verify] ✓ {fname}  ({p.stat().st_size:,} bytes)")
    else:
        print(f"[verify] ✗ MISSING: {fname}", file=sys.stderr)
        errors.append(fname)

# Verify config.json is valid JSON
cfg_path = MODEL_DIR / "config.json"
if cfg_path.exists():
    try:
        data = json.loads(cfg_path.read_text())
        print(f"[verify] ✓ config.json  valid JSON ({len(data)} top-level keys)")
    except Exception as e:
        errors.append(f"config.json invalid: {e}")
        print(f"[verify] ✗ config.json parse error: {e}", file=sys.stderr)

# Verify .dxnn is non-trivially sized
dxnn_path = MODEL_DIR / "yolo26n.dxnn"
if dxnn_path.exists() and dxnn_path.stat().st_size < 1024:
    errors.append("yolo26n.dxnn too small (< 1KB) — likely corrupt")
    print(f"[verify] ✗ yolo26n.dxnn is suspiciously small: {dxnn_path.stat().st_size} bytes", file=sys.stderr)

if errors:
    print(f"\n[verify] RESULT: FAIL  — {errors}", file=sys.stderr)
    sys.exit(1)

print("\n[verify] RESULT: PASS — all artifacts verified")
