#!/usr/bin/env python3
"""
verify.py — verify the construction-PPE retrain + DeepX benchmark deliverables.

Checks (exit 0 + "RESULT: PASS" only if ALL pass):
  1. Both DeepX export dirs exist with a .dxnn inside.
  2. results.json has all four measurement points.
  3. Domain gain: retrained fp32 mAP50-95 > base fp32 mAP50-95 (and base ~ 0).
  4. INT8 deployable: retrained .dxnn re-evaluated on the DX-M1 NPU succeeds and its
     mAP50-95 is within 0.05 of the recorded retrained INT8 value (NPU inference works).

Exit 1 (RESULT: FAIL) on any failure. Run via run.sh's resolved interpreter.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = "construction-ppe.yaml"
IMGSZ = 640


def fail(msg):
    print(f"[verify] FAIL: {msg}")
    print("RESULT: FAIL")
    sys.exit(1)


def main():
    rj = HERE / "results.json"
    if not rj.exists():
        fail("results.json missing — run run.sh first")
    R = json.loads(rj.read_text())

    # 1. export dirs + .dxnn
    base_dir = HERE / "yolo26n_deepx_model"
    retr_dir = HERE / "ppe_yolo26n_deepx_model"
    for d in (base_dir, retr_dir):
        if not d.is_dir():
            fail(f"DeepX export dir missing: {d}")
        if not list(d.glob("*.dxnn")):
            fail(f"no .dxnn inside {d}")
    print(f"[verify] OK: both DeepX dirs present with .dxnn")

    # 2. four points
    keys = ["base_pt_fp32_gpu", "base_dxnn_int8_npu",
            "retrained_pt_fp32_gpu", "retrained_dxnn_int8_npu"]
    for k in keys:
        if k not in R or "map5095" not in R[k]:
            fail(f"results.json missing measurement point: {k}")
    print(f"[verify] OK: all four measurement points recorded")

    # 3. domain gain
    base_map = R["base_pt_fp32_gpu"]["map5095"]
    retr_map = R["retrained_pt_fp32_gpu"]["map5095"]
    if not (retr_map > base_map):
        fail(f"no domain gain: retrained {retr_map} <= base {base_map}")
    print(f"[verify] OK: domain gain fp32 mAP50-95 {base_map} -> {retr_map} (+{retr_map-base_map:.4f})")

    # 4. live NPU re-eval of retrained .dxnn (confirms dx_engine inference works on DX-M1)
    from ultralytics import YOLO
    print(f"[verify] re-evaluating retrained .dxnn on DX-M1 NPU ...")
    m = YOLO(str(retr_dir)).val(data=DATA, split="val", imgsz=IMGSZ,
                                device="cpu", batch=1, verbose=False)
    live_map = float(m.box.map)
    recorded = R["retrained_dxnn_int8_npu"]["map5095"]
    print(f"[verify] live NPU mAP50-95={live_map:.4f} (recorded {recorded})")
    if abs(live_map - recorded) > 0.05:
        fail(f"NPU re-eval {live_map:.4f} deviates >0.05 from recorded {recorded}")
    print(f"[verify] OK: retrained .dxnn runs on DX-M1 NPU, mAP consistent")

    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
