#!/usr/bin/env python3
"""Export a YOLO26n .pt to DeepX NPU format via Ultralytics one-shot `format=deepx`
(ONNX export -> INT8 EMA calibration -> dx_com compile -> packaging).

Usage: export_deepx.py <input.pt> <target_dir_name>
Produces <SD>/<target_dir_name>/ = {<stem>.dxnn, config.json, metadata.yaml}.
Calibration on CPU (device='cpu') so it can overlap GPU training safely.
"""
import os
import shutil
import sys

SD = os.path.dirname(os.path.abspath(__file__))


def main():
    pt = sys.argv[1]
    target = sys.argv[2]
    from ultralytics import YOLO

    model = YOLO(pt)
    # INT8 enforced by the deepx exporter; african-wildlife = representative calibration set.
    out = model.export(
        format="deepx",
        data="african-wildlife.yaml",
        imgsz=640,
        batch=1,
        device="cpu",
    )
    out = str(out)
    print(f"[export] exporter returned: {out}")

    # Resolve to the produced *_deepx_model directory.
    if os.path.isdir(out):
        src = out
    else:
        cand = os.path.splitext(out)[0]
        src = cand if os.path.isdir(cand) else os.path.dirname(out)
    print(f"[export] source dir: {src}")

    dst = os.path.join(SD, target)
    if os.path.abspath(src) != os.path.abspath(dst):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.move(src, dst)
    print(f"[export] final dir: {dst}")

    dxnn = [f for f in os.listdir(dst) if f.endswith(".dxnn")]
    has_cfg = os.path.exists(os.path.join(dst, "config.json"))
    has_meta = os.path.exists(os.path.join(dst, "metadata.yaml"))
    print(f"[export] contents: dxnn={dxnn} config.json={has_cfg} metadata.yaml={has_meta}")
    assert dxnn, "no .dxnn produced"
    assert has_cfg and has_meta, "missing config.json/metadata.yaml"

    # Surface the compile config.json at the session root (mandatory deliverable).
    shutil.copy2(os.path.join(dst, "config.json"), os.path.join(SD, "config.json"))
    print("[export] OK")


if __name__ == "__main__":
    main()
