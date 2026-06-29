#!/usr/bin/env python3
# =============================================================================
# ocr_video.py — Video-file + webcam OCR on the DEEPX DX-M1 NPU (PP-OCRv5)
#
# Text DETECTION + textline-orientation CLASSIFICATION + RECOGNITION all run on
# the DX-M1 NPU via the vendored PaddleOCR-deepx pipeline (engine.paddleocr.PaddleOcr,
# which drives dx_engine.InferenceEngine per stage). This is our own standalone
# entry — it imports the fork's pipeline as a library; it does NOT shell out to
# any fork demo. (Documented IFactory exception for PaddleOCR/RapidDoc apps.)
#
# Usage:
#   ./run.sh                              # process the bundled demo video
#   python ocr_video.py --source video.mp4 --output annotated.mp4
#   python ocr_video.py --source 0 --show # live webcam (camera index 0)
# =============================================================================
import argparse
import logging
import os
import sys
import time

import numpy as np
import cv2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("ocr_video")

# --- Self-contained imports: make the vendored ./engine package importable ---
APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

DEFAULT_MODEL_DIR = os.path.join(APP_DIR, "engine", "model_files", "server")
DEFAULT_FONT = os.path.join(APP_DIR, "engine", "fonts", "NotoSansCJK-Regular.ttc")

# Recognition aspect-ratio buckets (must match RecognitionNode's preprocess map)
REC_RATIOS = [3, 5, 10, 15, 25, 35]


def build_ocr(model_dir, rec_thresh):
    """Load PP-OCRv5 .dxnn models onto the NPU and build the det+cls+rec pipeline.

    Document orientation / unwarping are document-scan features — disabled for
    video frames to minimise per-frame latency. Only det + cls + rec run.
    """
    from dx_engine import InferenceEngine as IE  # DX-M1 NPU binding
    from engine.paddleocr import PaddleOcr

    def load(name):
        path = os.path.join(model_dir, name)
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f"NPU model not found: {path}\nRun ./setup.sh to download the PP-OCRv5 models."
            )
        logger.info("Loading NPU model: %s", name)
        return IE(path)

    det_models = {640: load("det_v5_640.dxnn"), 960: load("det_v5_960.dxnn")}
    cls_model = load("textline_ori.dxnn")
    rec_models = {r: load(f"rec_v5_ratio_{r}.dxnn") for r in REC_RATIOS}
    dict_path = os.path.join(model_dir, "ppocrv5_dict.txt")
    if not os.path.isfile(dict_path):
        raise FileNotFoundError(f"Recognition dictionary not found: {dict_path}")

    ocr = PaddleOcr(
        det_model=det_models,
        cls_model=cls_model,
        rec_models=rec_models,
        rec_dict_dir=dict_path,
        doc_ori_model=None,
        doc_unwarping_model=None,
        use_doc_preprocessing=False,     # no doc unwarping for video frames
        use_doc_orientation=False,       # no doc orientation for video frames
        use_textline_orientation=True,   # textline 180-degree cls on the NPU
        rec_score_thresh=rec_thresh,
    )
    logger.info("PP-OCRv5 NPU pipeline ready (det 640/960 + textline-ori cls + rec x6).")
    return ocr


def open_source(src):
    """Single code path for a video file path OR a webcam index (int)."""
    if isinstance(src, str) and src.isdigit():
        cap = cv2.VideoCapture(int(src))
        kind = f"webcam[{src}]"
    else:
        cap = cv2.VideoCapture(src)
        kind = f"file[{src}]"
    return cap, kind


def _load_font(size):
    try:
        from PIL import ImageFont
        if os.path.isfile(DEFAULT_FONT):
            return ImageFont.truetype(DEFAULT_FONT, size)
    except Exception as exc:  # pragma: no cover
        logger.warning("Font load failed (%s); falling back to cv2 text.", exc)
    return None


def draw_overlay(frame, rec_results, font, fps, last_ms, det_count):
    """Overlay detected quad boxes + recognized strings + a small HUD.

    rec_results: list of {'bbox_index','bbox','text','score'} from PaddleOcr.
    Boxes are drawn with cv2; text is rendered with PIL (handles non-ASCII PP-OCR
    output) in a single pass, with a cv2.putText ASCII fallback when no font.
    """
    # 1. quad boxes (green) on the BGR frame
    for r in rec_results:
        box = np.array(r["bbox"], dtype=np.int32).reshape(-1, 2)
        cv2.polylines(frame, [box], isClosed=True, color=(0, 220, 0), thickness=2)

    # 2. recognized strings
    if font is not None:
        from PIL import Image, ImageDraw
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        for r in rec_results:
            box = np.array(r["bbox"], dtype=np.int32).reshape(-1, 2)
            x = int(box[:, 0].min())
            y = int(box[:, 1].min())
            label = f"{r['text']} ({r['score']:.2f})"
            ty = max(0, y - 22)
            tb = draw.textbbox((x, ty), label, font=font)
            draw.rectangle([tb[0] - 2, tb[1] - 1, tb[2] + 2, tb[3] + 1], fill=(0, 0, 0))
            draw.text((x, ty), label, font=font, fill=(0, 255, 0))
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    else:
        for r in rec_results:
            box = np.array(r["bbox"], dtype=np.int32).reshape(-1, 2)
            x, y = int(box[:, 0].min()), int(box[:, 1].min())
            ascii_txt = r["text"].encode("ascii", "ignore").decode() or "?"
            cv2.putText(frame, ascii_txt, (x, max(12, y - 6)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1, cv2.LINE_AA)

    # 3. HUD (always ASCII -> cv2 is fine)
    hud = f"NPU PP-OCRv5  {fps:5.1f} FPS  {last_ms:6.1f} ms/frame  texts:{det_count}"
    cv2.rectangle(frame, (0, 0), (max(360, 9 * len(hud)), 26), (0, 0, 0), -1)
    cv2.putText(frame, hud, (6, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                (0, 255, 255), 1, cv2.LINE_AA)
    return frame


def main():
    ap = argparse.ArgumentParser(
        description="Video-file + webcam OCR on the DEEPX DX-M1 NPU (PP-OCRv5).")
    ap.add_argument("--source", required=True,
                    help="Video file path (e.g. clip.mp4) OR webcam index (e.g. 0).")
    ap.add_argument("--output", default="ocr_output.mp4",
                    help="Annotated output video path (default: ocr_output.mp4).")
    ap.add_argument("--sample", default="sample_detect.jpg",
                    help="Path to save one annotated sample frame.")
    ap.add_argument("--show", action="store_true",
                    help="Show a live preview window (needs a display).")
    ap.add_argument("--max-frames", type=int, default=0,
                    help="Stop after N frames (0 = all). Useful for webcam / quick runs.")
    ap.add_argument("--frame-skip", type=int, default=1,
                    help="Run NPU OCR every Nth frame; reuse last result in between "
                         "(>=1; helps webcam keep up). Default 1 = every frame.")
    ap.add_argument("--model-dir", default=DEFAULT_MODEL_DIR,
                    help="Directory containing the PP-OCRv5 .dxnn models.")
    ap.add_argument("--rec-thresh", type=float, default=0.5,
                    help="Recognition score threshold for keeping a string (default 0.5).")
    args = ap.parse_args()

    skip = max(1, args.frame_skip)
    ocr = build_ocr(args.model_dir, args.rec_thresh)
    font = _load_font(20)

    cap, kind = open_source(args.source)
    if not cap.isOpened():
        logger.error("Could not open source: %s", args.source)
        sys.exit(2)
    src_fps = cap.get(cv2.CAP_PROP_FPS)
    out_fps = src_fps if src_fps and src_fps > 0 else 15.0
    logger.info("Source opened: %s  (%.1f fps)", kind, out_fps)

    writer = None
    last_results = []
    frame_idx = 0
    ocr_frames = 0
    sum_total_ms = 0.0
    sum_det_ms = sum_cls_ms = sum_rec_ms = 0.0
    total_text = 0
    sample_saved = False
    last_annotated = None
    wall_start = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frame_idx += 1

        run_ocr = (frame_idx - 1) % skip == 0
        if run_ocr:
            t0 = time.time()
            boxes, crops, rec_results, _proc, dbg = ocr(frame)
            wall_ms = (time.time() - t0) * 1000.0
            last_results = rec_results
            ocr_frames += 1
            lat = dbg.get("latency_ms", {})
            sum_total_ms += lat.get("total", wall_ms)
            sum_det_ms += lat.get("det", 0.0)
            sum_cls_ms += lat.get("cls", 0.0)
            sum_rec_ms += lat.get("rec", 0.0)
            total_text += len(rec_results)
            inst_ms = lat.get("total", wall_ms)
        else:
            inst_ms = 0.0

        running_fps = ocr_frames / max(1e-6, (time.time() - wall_start))
        annotated = draw_overlay(frame, last_results, font, running_fps,
                                 inst_ms if run_ocr else 0.0, len(last_results))
        last_annotated = annotated

        if writer is None:
            h, w = annotated.shape[:2]
            writer = cv2.VideoWriter(args.output, cv2.VideoWriter_fourcc(*"mp4v"),
                                     out_fps, (w, h))
        writer.write(annotated)

        if (not sample_saved) and len(last_results) > 0:
            cv2.imwrite(args.sample, annotated)
            sample_saved = True
            logger.info("Saved annotated sample frame -> %s (%d texts)",
                        args.sample, len(last_results))

        if args.show:
            cv2.imshow("DX-M1 NPU OCR", annotated)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        if frame_idx % 25 == 0:
            logger.info("frame %d | %.1f FPS | last %.1f ms | texts %d",
                        frame_idx, running_fps, inst_ms, len(last_results))

        if args.max_frames and frame_idx >= args.max_frames:
            break

    cap.release()
    if writer is not None:
        writer.release()
    if args.show:
        cv2.destroyAllWindows()

    # Fallback: if no frame ever had detections, still emit a sample frame.
    if (not sample_saved) and last_annotated is not None:
        cv2.imwrite(args.sample, last_annotated)
        logger.info("No detections in any frame; saved last frame -> %s", args.sample)

    wall = time.time() - wall_start
    avg_ms = sum_total_ms / max(1, ocr_frames)
    npu_fps = 1000.0 / avg_ms if avg_ms > 0 else 0.0
    logger.info("=" * 64)
    logger.info("Processed %d frames (%d OCR'd) in %.2fs", frame_idx, ocr_frames, wall)
    logger.info("Per-frame NPU OCR latency: %.1f ms  (det %.1f + cls %.1f + rec %.1f)",
                avg_ms, sum_det_ms / max(1, ocr_frames),
                sum_cls_ms / max(1, ocr_frames), sum_rec_ms / max(1, ocr_frames))
    logger.info("NPU OCR throughput: %.2f FPS | total recognized strings: %d",
                npu_fps, total_text)
    logger.info("Annotated video: %s | sample frame: %s", args.output, args.sample)
    logger.info("=" * 64)


if __name__ == "__main__":
    main()
