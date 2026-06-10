#!/usr/bin/env python3
"""Export a YOLO .pt to a deployable DeepX NPU model via the one-shot ``format=deepx`` path.

Internally: ONNX export -> INT8 EMA calibration (medical-pills images) -> dx_com
compile -> packaging into ``<stem>_deepx_model/`` ({.dxnn, config.json, metadata.yaml}).
The produced dir is moved into the session dir under ``--out-name``.

Usage:
    python export_deepx.py --model yolo26n.pt        --out-name yolo26n_deepx_model
    python export_deepx.py --model runs/.../best.pt  --out-name yolo26n_pills_deepx_model
"""
import argparse
import shutil
import sys
from pathlib import Path

from ultralytics import YOLO

SESSION_DIR = Path(__file__).resolve().parent
DATA = "medical-pills.yaml"   # calibration source (representative of inference distribution)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="path to .pt weights")
    ap.add_argument("--out-name", required=True, help="target *_deepx_model dir name in session")
    ap.add_argument("--imgsz", type=int, default=640)
    args = ap.parse_args()

    model_path = Path(args.model).resolve()
    if not model_path.exists():
        print(f"ERROR: model not found: {model_path}", file=sys.stderr)
        return 1

    model = YOLO(str(model_path))
    # int8=True is enforced by the deepx exporter; data drives INT8 calibration.
    out = model.export(format="deepx", imgsz=args.imgsz, data=DATA, batch=1)
    produced = Path(out).resolve()
    if produced.is_file():           # returned the .dxnn inside the dir
        produced = produced.parent
    if not produced.is_dir():
        # fall back: locate the *_deepx_model dir next to the .pt
        cands = list(model_path.parent.glob("*_deepx_model"))
        if not cands:
            print(f"ERROR: no *_deepx_model produced (export returned {out})", file=sys.stderr)
            return 1
        produced = cands[0]

    target = SESSION_DIR / args.out_name
    if target.resolve() != produced.resolve():
        if target.exists():
            shutil.rmtree(target)
        shutil.move(str(produced), str(target))

    dxnn = list(target.glob("*.dxnn"))
    if not dxnn:
        print(f"ERROR: no .dxnn inside {target}", file=sys.stderr)
        return 1
    print(f"EXPORT_DONE dir={target} dxnn={dxnn[0].name} size={dxnn[0].stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
