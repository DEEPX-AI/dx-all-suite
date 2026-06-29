#!/usr/bin/env python3
"""
verify.py — acceptance check for the YOLO26n african-wildlife retrain + DeepX session.

Verifies (exit 0 + "RESULT: PASS" only if ALL hold):
  1. Both DeepX export dirs contain a real .dxnn binary.
  2. results.json has all 4 measured points, each with a numeric map5095 and fps.
  3. The retrained model is more accurate on the domain than the base model
     (retrained mAP50-95 > base mAP50-95, both fp32 and INT8).
  4. sample_detect.jpg exists and is non-empty.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
FAIL = []


def check(cond, msg):
    print(f"  [{'PASS' if cond else 'FAIL'}] {msg}")
    if not cond:
        FAIL.append(msg)


def main():
    print("==== verify.py — YOLO26n african-wildlife retrain + DeepX ====")

    # 1. .dxnn binaries
    base_dxnn = HERE / "yolo26n_deepx_model" / "yolo26n.dxnn"
    retr_dxnn = HERE / "wildlife_yolo26n_deepx_model" / "wildlife_yolo26n.dxnn"
    check(base_dxnn.exists() and base_dxnn.stat().st_size > 0,
          f"base .dxnn exists & non-empty: {base_dxnn}")
    check(retr_dxnn.exists() and retr_dxnn.stat().st_size > 0,
          f"retrained .dxnn exists & non-empty: {retr_dxnn}")

    # 2. results.json with 4 measured points
    rj = HERE / "results.json"
    check(rj.exists(), f"results.json exists: {rj}")
    results = json.loads(rj.read_text()) if rj.exists() else {}
    keys = ["base_pt_fp32_gpu", "base_dxnn_int8_npu",
            "retrained_pt_fp32_gpu", "retrained_dxnn_int8_npu"]
    for k in keys:
        e = results.get(k, {})
        ok = isinstance(e.get("map5095"), (int, float)) and \
            isinstance(e.get("fps"), (int, float))
        check(ok, f"results['{k}'] has numeric map5095 & fps")

    # 3. retrained > base accuracy
    if all(k in results for k in keys):
        base_fp = results["base_pt_fp32_gpu"]["map5095"]
        retr_fp = results["retrained_pt_fp32_gpu"]["map5095"]
        base_q = results["base_dxnn_int8_npu"]["map5095"]
        retr_q = results["retrained_dxnn_int8_npu"]["map5095"]
        check(retr_fp > base_fp,
              f"retrained fp32 mAP ({retr_fp}) > base fp32 mAP ({base_fp})")
        check(retr_q > base_q,
              f"retrained INT8 mAP ({retr_q}) > base INT8 mAP ({base_q})")

    # 4. sample image
    sample = HERE / "sample_detect.jpg"
    check(sample.exists() and sample.stat().st_size > 0,
          f"sample_detect.jpg exists & non-empty: {sample}")

    print("=" * 60)
    if FAIL:
        print(f"RESULT: FAIL ({len(FAIL)} check(s) failed)")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
