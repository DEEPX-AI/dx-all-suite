#!/usr/bin/env python3
# =============================================================================
# verify.py — smoke test that PP-OCRv5 OCR really runs on the DX-M1 NPU.
#
# Asserts: (1) all required .dxnn + dict are present; (2) the pipeline loads on
# the NPU; (3) running OCR on one frame of the demo video yields >=1 detected
# text region (and reports any recognized strings). Exit 0 + "RESULT: PASS" on
# success; exit 1 otherwise. Run under the session venv (./setup.sh built it).
# =============================================================================
import os
import sys

# DX-RT runtime env — set BEFORE dx_engine is imported. DXRT_TASK_MAX_LOAD caps the
# per-model I/O buffer count; without it the default allocates enough NPU memory that
# loading the full 9-model PP-OCRv5 pipeline overflows the 3.92 GiB device. These match
# run.sh so verify.py is correct when launched standalone (`python verify.py`).
for _k, _v in {
    "CUSTOM_INTER_OP_THREADS_COUNT": "1", "CUSTOM_INTRA_OP_THREADS_COUNT": "2",
    "DXRT_DYNAMIC_CPU_THREAD": "1", "DXRT_TASK_MAX_LOAD": "3",
    "NFH_INPUT_WORKER_THREADS": "2", "NFH_OUTPUT_WORKER_THREADS": "4",
    "DXNN_DEVICES": "0",
}.items():
    os.environ.setdefault(_k, _v)

APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

MODEL_DIR = os.path.join(APP_DIR, "engine", "model_files", "server")
REQUIRED = [
    "det_v5_640.dxnn", "det_v5_960.dxnn", "textline_ori.dxnn",
    "rec_v5_ratio_3.dxnn", "rec_v5_ratio_5.dxnn", "rec_v5_ratio_10.dxnn",
    "rec_v5_ratio_15.dxnn", "rec_v5_ratio_25.dxnn", "rec_v5_ratio_35.dxnn",
    "ppocrv5_dict.txt",
]
DEMO_VIDEO = os.environ.get("OCR_DEMO_VIDEO", "/tmp/sc-build/ocr_input/ocr_demo.mp4")


def fail(msg):
    print(f"  [FAIL] {msg}")
    print("RESULT: FAIL")
    sys.exit(1)


def main():
    print("== verify.py : PP-OCRv5 OCR on DX-M1 NPU ==")

    # 1. model files present
    for m in REQUIRED:
        p = os.path.join(MODEL_DIR, m)
        if not os.path.isfile(p):
            fail(f"missing model/dict: {p} (run ./setup.sh)")
    print(f"  [OK] all {len(REQUIRED)} model/dict files present")

    # 2. dependencies + NPU pipeline load
    try:
        import cv2  # noqa: F401
        import dx_engine  # noqa: F401
        from ocr_video import build_ocr, open_source
    except Exception as exc:  # ImportError etc.
        fail(f"import failed (run ./setup.sh to build the venv + bridge): {exc}")

    try:
        ocr = build_ocr(MODEL_DIR, rec_thresh=0.5)
    except Exception as exc:
        fail(f"NPU pipeline load failed: {exc}")
    print("  [OK] PP-OCRv5 pipeline loaded on the NPU")

    # 3. run OCR on one frame of the demo video
    if not os.path.isfile(DEMO_VIDEO):
        fail(f"demo video not found: {DEMO_VIDEO}")
    cap, _ = open_source(DEMO_VIDEO)
    if not cap.isOpened():
        fail(f"could not open demo video: {DEMO_VIDEO}")

    # scan up to 30 frames for one containing text (videos may open on a blank frame)
    found = None
    for _ in range(30):
        ok, frame = cap.read()
        if not ok:
            break
        boxes, crops, rec_results, _proc, dbg = ocr(frame)
        if boxes is not None and len(boxes) > 0:
            found = (boxes, rec_results, dbg)
            break
    cap.release()

    if found is None:
        fail("no text region detected in the first 30 frames of the demo video")

    boxes, rec_results, dbg = found
    lat = dbg.get("latency_ms", {})
    print(f"  [OK] detected {len(boxes)} text region(s) on one frame")
    print(f"       per-frame NPU latency: total={lat.get('total', 0):.1f} ms "
          f"(det={lat.get('det', 0):.1f}, cls={lat.get('cls', 0):.1f}, rec={lat.get('rec', 0):.1f})")
    sample = [r["text"] for r in rec_results[:5]]
    print(f"       recognized {len(rec_results)} string(s); sample: {sample}")

    print("RESULT: PASS")
    sys.exit(0)


if __name__ == "__main__":
    main()
