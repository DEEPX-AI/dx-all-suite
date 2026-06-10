#!/usr/bin/env python3
"""Measure accuracy (mAP50-95, mAP50) and speed (FPS) for ONE model form, append a JSON row.

fp32 forms (.pt) run on the GPU; DeepX forms (``*_deepx_model/``) run INT8 on the DX-M1 NPU
(the Ultralytics DeepX backend dispatches to dx_engine automatically). FPS is derived from
the single-image inference latency reported by ``model.val()`` (FPS = 1000 / inference_ms).

Usage:
    python benchmark.py --model yolo26n.pt                --tag base_fp32_gpu      --device gpu
    python benchmark.py --model yolo26n_deepx_model       --tag base_int8_npu      --device npu
    python benchmark.py --model .../best.pt               --tag retrained_fp32_gpu --device gpu
    python benchmark.py --model yolo26n_pills_deepx_model --tag retrained_int8_npu --device npu
"""
import argparse
import json
import sys
from pathlib import Path

from ultralytics import YOLO

SESSION_DIR = Path(__file__).resolve().parent
DATA = "medical-pills.yaml"
RESULTS = SESSION_DIR / "bench_results.json"


def load_rows():
    if RESULTS.exists():
        return json.loads(RESULTS.read_text())
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--tag", required=True)
    ap.add_argument("--device", choices=["gpu", "npu"], required=True)
    ap.add_argument("--imgsz", type=int, default=640)
    args = ap.parse_args()

    mpath = Path(args.model)
    if not mpath.is_absolute():
        mpath = (SESSION_DIR / mpath)
    if not mpath.exists():
        print(f"ERROR: model not found: {mpath}", file=sys.stderr)
        return 1

    row = {"tag": args.tag, "model": str(mpath.name), "device": args.device,
           "form": "INT8" if args.device == "npu" else "fp32"}
    try:
        model = YOLO(str(mpath))
        kwargs = dict(data=DATA, imgsz=args.imgsz, verbose=False, plots=False)
        if args.device == "gpu":
            kwargs["device"] = 0
        m = model.val(**kwargs)
        inf_ms = float(m.speed.get("inference", 0.0))
        row.update({
            "map50_95": round(float(m.box.map), 5),
            "map50": round(float(m.box.map50), 5),
            "map75": round(float(m.box.map75), 5),
            "inference_ms": round(inf_ms, 4),
            "fps": round(1000.0 / inf_ms, 2) if inf_ms > 0 else None,
            "speed": {k: round(float(v), 4) for k, v in m.speed.items()},
            "status": "ok",
        })
    except Exception as e:  # record the failure rather than crashing the whole sweep
        row.update({"map50_95": None, "map50": None, "fps": None,
                    "status": f"error: {type(e).__name__}: {e}"})
        print(f"WARN benchmark {args.tag} failed: {e}", file=sys.stderr)

    rows = [r for r in load_rows() if r.get("tag") != args.tag]
    rows.append(row)
    RESULTS.write_text(json.dumps(rows, indent=2))
    print(f"BENCH_DONE {args.tag}: map50_95={row.get('map50_95')} "
          f"map50={row.get('map50')} fps={row.get('fps')} status={row['status']}")
    return 0 if row["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
