#!/usr/bin/env python3
"""export_deepx.py — Export a YOLO .pt to a DeepX NPU model via the Ultralytics
one-shot `format=deepx` exporter (ONNX export -> INT8 EMA calibration -> dx_com ->
package). INT8 is enforced; target is DX-M1.

Usage:
    python export_deepx.py base        # export base yolo26n.pt
    python export_deepx.py retrained   # export runs/train/weights/best.pt
    python export_deepx.py all         # both (retrained only if best.pt exists)

Output: <session>/<name>_deepx_model/{<stem>.dxnn, config.json, metadata.yaml}
Calibration uses african-wildlife images so the calibration distribution matches
the eval set (fair on-device comparison).
"""
import shutil
import sys
from pathlib import Path

from ultralytics import YOLO

HERE = Path(__file__).resolve().parent
BASE_PT = HERE / "yolo26n.pt"
RETRAINED_PT = HERE / "runs" / "train" / "weights" / "best.pt"

IMGSZ = 640
BATCH = 1                               # DX-M1 is batch=1
CALIB_DATA = "african-wildlife.yaml"    # representative calibration distribution


def export_one(pt_path: Path, out_name: str) -> Path | None:
    """Export pt_path with format=deepx; relocate the produced *_deepx_model/ dir
    into the session dir as <out_name>_deepx_model/. Returns the final dir or None."""
    if not pt_path.exists():
        print(f"[export] SKIP {out_name}: weights not found at {pt_path}")
        return None
    print(f"[export] {out_name}: exporting {pt_path} (format=deepx, int8, imgsz={IMGSZ}, batch={BATCH})")
    model = YOLO(str(pt_path))
    # Ultralytics returns the path to the produced *_deepx_model/ directory.
    produced = model.export(format="deepx", imgsz=IMGSZ, batch=BATCH, data=CALIB_DATA)
    produced = Path(produced)
    src_dir = produced if produced.is_dir() else produced.parent
    dst_dir = HERE / f"{out_name}_deepx_model"
    if src_dir.resolve() != dst_dir.resolve():
        if dst_dir.exists():
            shutil.rmtree(dst_dir)
        shutil.move(str(src_dir), str(dst_dir))
    dxnn = list(dst_dir.glob("*.dxnn"))
    print(f"[export] {out_name}: -> {dst_dir}  (.dxnn: {[p.name for p in dxnn]})")
    return dst_dir if dxnn else None


def main(argv: list[str]) -> int:
    which = argv[1] if len(argv) > 1 else "all"
    targets = []
    if which in ("base", "all"):
        targets.append((BASE_PT if BASE_PT.exists() else Path("yolo26n.pt"), "base_yolo26n"))
    if which in ("retrained", "all"):
        targets.append((RETRAINED_PT, "retrained_yolo26n"))
    ok = True
    for pt, name in targets:
        try:
            if export_one(pt, name) is None and name.startswith("base"):
                ok = False
        except Exception as e:
            print(f"[export] ERROR exporting {name}: {type(e).__name__}: {e}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
