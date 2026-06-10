#!/usr/bin/env python3
"""verify.py — gate for the YOLO26n African-wildlife DeepX showcase.

Exit 0 ONLY when:
  - both DeepX model dirs exist and each contains a *.dxnn,
  - both metric JSONs exist with a numeric map50_95 and numeric npu_inference_fps,
  - the improved model's mAP50-95 is materially better than the baseline's.
Exit 1 otherwise.
"""
import json
import os
import sys

SD = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.join(SD, "yolo26n_baseline_deepx_model")
IMPR_DIR = os.path.join(SD, "yolo26n_improved_deepx_model")
BASE_JSON = os.path.join(SD, "metrics_baseline.json")
IMPR_JSON = os.path.join(SD, "metrics_improved.json")

failures = []


def has_dxnn(d):
    return os.path.isdir(d) and any(f.endswith(".dxnn") for f in os.listdir(d))


def load_metrics(p):
    with open(p) as f:
        m = json.load(f)
    assert isinstance(m["map50_95"], (int, float)), "map50_95 not numeric"
    assert isinstance(m["npu_inference_fps"], (int, float)), "npu_inference_fps not numeric"
    return m


def check(name, ok):
    print(f"[{'OK' if ok else 'FAIL'}] {name}")
    if not ok:
        failures.append(name)


check("baseline deepx dir + .dxnn", has_dxnn(BASE_DIR))
check("improved deepx dir + .dxnn", has_dxnn(IMPR_DIR))
check("metrics_baseline.json exists", os.path.exists(BASE_JSON))
check("metrics_improved.json exists", os.path.exists(IMPR_JSON))

base = impr = None
if os.path.exists(BASE_JSON):
    try:
        base = load_metrics(BASE_JSON)
        check("baseline metrics numeric", True)
    except Exception as e:  # noqa: BLE001
        check(f"baseline metrics numeric ({e})", False)
if os.path.exists(IMPR_JSON):
    try:
        impr = load_metrics(IMPR_JSON)
        check("improved metrics numeric", True)
    except Exception as e:  # noqa: BLE001
        check(f"improved metrics numeric ({e})", False)

if base and impr:
    check(
        f"improved mAP50-95 ({impr['map50_95']}) >> baseline ({base['map50_95']})",
        impr["map50_95"] > base["map50_95"] + 0.1,
    )
    print("\n--- measured summary ---")
    print(f"  baseline: mAP50-95={base['map50_95']:.4f}  mAP50={base['map50']:.4f}  "
          f"FPS={base['npu_inference_fps']}")
    print(f"  improved: mAP50-95={impr['map50_95']:.4f}  mAP50={impr['map50']:.4f}  "
          f"FPS={impr['npu_inference_fps']}")

check("report.md exists", os.path.exists(os.path.join(SD, "report.md")))

if failures:
    print(f"\nRESULT: FAIL ({len(failures)} check(s) failed)")
    sys.exit(1)
print("\nRESULT: PASS")
sys.exit(0)
