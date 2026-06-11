#!/usr/bin/env python3
"""verify.py — verify the DeepX PPE deliverables.

For this Ultralytics format=deepx workflow the meaningful verification is the
fp32(.pt) vs INT8(.dxnn) comparison plus confirming both .dxnn run on the NPU.
Checks:
  1. both *_deepx_model/ dirs contain a real .dxnn + config.json + metadata.yaml
  2. both .dxnn actually run inference on the DX-M1 NPU (dx_engine backend)
  3. retrained INT8 mAP > base INT8 mAP (domain gain survives quantization)
  4. retrained fp32 mAP > base fp32 mAP (domain optimization worked)
Exit 0 + "RESULT: PASS" on success; exit 1 + "RESULT: FAIL" otherwise.
"""
import json
import sys
from pathlib import Path

WORK = Path(__file__).resolve().parent


def fail(msg):
    print(f"[FAIL] {msg}")
    print("RESULT: FAIL")
    sys.exit(1)


def main():
    rj = WORK / "results.json"
    if not rj.exists():
        fail("results.json missing — run export_eval.py first")
    R = json.loads(rj.read_text())

    # 1. model dirs well-formed
    for key, name in [("base_dxnn_dir", "base"), ("retrained_dxnn_dir", "retrained")]:
        d = Path(R.get(key, ""))
        if not d.is_dir():
            fail(f"{name} deepx model dir missing: {d}")
        if not list(d.glob("*.dxnn")):
            fail(f"{name}: no .dxnn in {d}")
        for f in ("config.json", "metadata.yaml"):
            if not (d / f).exists():
                fail(f"{name}: missing {f} in {d}")
        print(f"[OK] {name} deepx model dir well-formed: {d}")

    # 2. NPU inference actually ran (eval populated speed/map for .dxnn)
    for key in ("base_dxnn", "retrained_dxnn"):
        rec = R.get(key)
        if not rec or rec.get("inference_ms", 0) <= 0:
            fail(f"{key}: no NPU inference timing — did it run on the device?")
        print(f"[OK] {key} ran on NPU: {rec['inference_ms']:.2f} ms/img, {rec['fps']:.1f} FPS")

    # 3 & 4. domain gain
    bp, rp = R["base_pt"]["map"], R["retrained_pt"]["map"]
    bd, rd = R["base_dxnn"]["map"], R["retrained_dxnn"]["map"]
    print(f"[INFO] fp32  base={bp:.4f} retrained={rp:.4f}")
    print(f"[INFO] INT8  base={bd:.4f} retrained={rd:.4f}")
    if not (rp > bp):
        fail(f"retrained fp32 mAP ({rp:.4f}) not > base fp32 mAP ({bp:.4f})")
    print(f"[OK] retrained fp32 mAP > base fp32 mAP (domain optimization worked)")
    if not (rd > bd):
        fail(f"retrained INT8 mAP ({rd:.4f}) not > base INT8 mAP ({bd:.4f})")
    print(f"[OK] retrained INT8 mAP > base INT8 mAP (gain survives quantization)")

    # sample image
    s = WORK / "sample_detect.jpg"
    if not (s.exists() and s.stat().st_size > 0):
        fail("sample_detect.jpg missing or empty")
    print(f"[OK] sample_detect.jpg present ({s.stat().st_size} bytes)")

    print("RESULT: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
