#!/usr/bin/env python3
"""Measure NPU inference FPS + accuracy (mAP50-95, mAP50) of a DeepX model on the
african-wildlife validation split, via the Ultralytics DeepX backend (dx_engine).

Usage: measure.py <deepx_model_dir> <out_metrics.json> <tag>
"""
import json
import os
import sys

SD = os.path.dirname(os.path.abspath(__file__))


def main():
    deepx_dir = sys.argv[1]
    out_json = sys.argv[2]
    tag = sys.argv[3]
    from ultralytics import YOLO

    model = YOLO(deepx_dir)  # loads the .dxnn via the dx_engine backend (NPU)
    metrics = model.val(
        data="african-wildlife.yaml",
        split="val",
        batch=1,          # DX-M1 NPU is batch=1
        imgsz=640,
        device="cpu",     # keep torch postproc off the GPU; inference runs on NPU
        verbose=True,
    )

    speed = dict(metrics.speed)  # ms/image: preprocess, inference, postprocess, (loss)
    inf_ms = float(speed.get("inference") or 0.0)
    fps = (1000.0 / inf_ms) if inf_ms > 0 else None

    result = {
        "tag": tag,
        "deepx_dir": os.path.relpath(deepx_dir, SD),
        "dataset": "african-wildlife.yaml",
        "split": "val",
        "imgsz": 640,
        "batch": 1,
        "device": "DX-M1 NPU (dx_engine)",
        "map50_95": round(float(metrics.box.map), 5),
        "map50": round(float(metrics.box.map50), 5),
        "map75": round(float(metrics.box.map75), 5),
        "per_class_map50_95": {
            metrics.names[c]: round(float(metrics.box.maps[i]), 5)
            for i, c in enumerate(getattr(metrics.box, "ap_class_index", range(len(metrics.box.maps))))
        } if hasattr(metrics.box, "maps") else {},
        "speed_ms_per_image": {k: round(float(v), 4) for k, v in speed.items()},
        "npu_inference_fps": round(fps, 2) if fps else None,
    }
    with open(out_json, "w") as f:
        json.dump(result, f, indent=2)
    print(json.dumps(result, indent=2))
    # numeric sanity for the TDD gate
    assert isinstance(result["map50_95"], float)
    assert result["npu_inference_fps"] is not None
    print(f"[measure] OK -> {out_json}")


if __name__ == "__main__":
    main()
