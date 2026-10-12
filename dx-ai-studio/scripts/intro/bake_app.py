"""Bake the intro App scene: real segmentation from DX-M1 on every frame of a real driving video.

The source is `blackbox-city-road.mp4` from the official DEEPX sample video bundle the dx_stream demos use (not kept
in the repo; the bake_stream.py docstring shows how to fetch it). Inference runs the official Model Zoo segformer-b0
(Cityscapes, 19 classes) on DX-M1 through the dx_app example's factory, unchanged.

    dx-runtime/venv-dx-runtime/bin/python3 scripts/intro/bake_app.py \\
        --videos <videos> --model <segformer_mit-b0_512x1024.dxnn> [--bench]

Colors are five muted groups; the standard 19-color Cityscapes palette looked like a paper demo.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import numpy as np

STUDIO = Path(__file__).resolve().parents[2]
SUITE = STUDIO.parent
EXAMPLES = SUITE / "dx-runtime" / "dx_app" / "src" / "python_example"
EXAMPLE = EXAMPLES / "semantic_segmentation" / "segformer_b0_512x1024"
OUT = STUDIO / "launcher" / "static" / "img" / "intro" / "app"
SOURCE_PACK = "https://sdk.deepx.ai/res/video/sample_videos.tar.gz"
VIDEO, START, SECONDS = "blackbox-city-road.mp4", 1.0, 3.0
STAGE = 16 / 10
CLIP = (1440, 900)
SKY, NONE = 10, 255

# Cityscapes id → (BGR, alpha). The sky is left unpainted.
GROUPS = {
    "vehicle": ((13, 14, 15, 16, 17, 18), (255, 151, 41), .72),   # --accent
    "person": ((11, 12), (58, 172, 245), .80),                     # amber
    "road": ((0, 1), (130, 60, 24), .55),                          # navy
    "green": ((8, 9), (116, 128, 28), .45),                        # teal
    "built": ((2, 3, 4), (118, 88, 70), .35),                      # slate
    "street": ((5, 6, 7), (235, 205, 185), .55),                   # poles, signals, signs
}
EDGE = np.array((255, 235, 220), np.float32)   # edge line: pale blue-white
MIN_AREA = 0.0005                               # smaller fragments are removed (fraction of frame area)


def cover(img: np.ndarray, ratio: float = STAGE) -> np.ndarray:
    h, w = img.shape[:2]
    if w / h > ratio:
        nw = int(round(h * ratio))
        x = (w - nw) // 2
        return img[:, x:x + nw]
    nh = int(round(w / ratio))
    y = (h - nh) // 2
    return img[y:y + nh]


class Segmenter:
    def __init__(self, model: Path):
        sys.path[:0] = [str(EXAMPLES), str(EXAMPLE)]
        from dx_engine import InferenceEngine
        from factory import Segformer_b0_512x1024Factory

        cfg_path = EXAMPLE / "config.json"
        cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
        self.ie = InferenceEngine(str(model))
        shape = self.ie.get_input_tensors_info()[0]["shape"]
        ih, iw = (shape[1], shape[2]) if shape[-1] in (1, 3) else (shape[2], shape[3])
        factory = Segformer_b0_512x1024Factory(cfg)
        self.pre = factory.create_preprocessor(iw, ih)
        self.post = factory.create_postprocessor(iw, ih)

    def __call__(self, img: np.ndarray) -> np.ndarray:
        tensor, ctx = self.pre.process(img)
        res = self.post.process(self.ie.run([tensor]), ctx)
        res = res[0] if isinstance(res, list) else res
        return cv2.resize(res.mask.astype(np.uint8), (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST)


def steady(prev: np.ndarray | None, cur: np.ndarray, nxt: np.ndarray | None) -> np.ndarray:
    """A pixel that differs only in this frame while the previous and next frames agree is flicker; follow them."""
    if prev is None or nxt is None:
        return cur
    out = cur.copy()
    agree = prev == nxt
    out[agree] = prev[agree]
    return out


def tidy(labels: np.ndarray) -> np.ndarray:
    """Fill small fragments with the surrounding class. Tiny fragments around street lights and signs make the edges
    jitter, and just deleting them leaves unpainted black holes, so each hole takes the class of the nearest kept pixel."""
    out = labels.copy()
    floor = MIN_AREA * labels.size
    for c in np.unique(labels):
        if c == SKY:
            continue
        n, comp, stats, _ = cv2.connectedComponentsWithStats((labels == c).astype(np.uint8), connectivity=8)
        small = np.where(stats[1:, cv2.CC_STAT_AREA] < floor)[0] + 1
        if small.size:
            out[np.isin(comp, small)] = NONE
    holes = out == NONE
    if holes.any():
        # Label every zero (kept pixel); each hole takes the class of the nearest label
        _, idx = cv2.distanceTransformWithLabels(holes.astype(np.uint8), cv2.DIST_L2, 5,
                                                 labelType=cv2.DIST_LABEL_PIXEL)
        kept = out[~holes]                       # label order = scan order of the kept pixels
        out[holes] = kept[idx[holes] - 1]
    return out


def paint(img: np.ndarray, labels: np.ndarray) -> np.ndarray:
    base = img.astype(np.float32) * 0.62
    out = base.copy()
    for ids, bgr, a in GROUPS.values():
        sel = np.isin(labels, ids)
        out[sel] = base[sel] * (1 - a) + np.array(bgr, np.float32) * a
    # class edges; none between the sky and unpainted areas
    painted = (labels != SKY) & (labels != NONE)
    grad = cv2.morphologyEx(labels, cv2.MORPH_GRADIENT, np.ones((3, 3), np.uint8)) > 0
    edge = grad & cv2.dilate(painted.astype(np.uint8), np.ones((3, 3), np.uint8)).astype(bool)
    out[edge] = out[edge] * 0.3 + EDGE * 0.7
    return out.clip(0, 255).astype(np.uint8)


def bench(model: Path) -> str:
    out = subprocess.run(["run_model", "-m", str(model), "-b", "-t", "8", "-w", "20"],
                         capture_output=True, text=True, check=True).stdout
    return re.search(r"FPS\s*:\s*([\d.]+)", out).group(1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--videos", type=Path, required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--bench", action="store_true")
    ap.add_argument("--crf", type=int, default=28)
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    seg = Segmenter(args.model)

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(START), "-t", str(SECONDS),
                        "-i", str(args.videos / VIDEO), "-q:v", "2", str(tmp / "in_%03d.jpg")], check=True)
        frames = sorted(tmp.glob("in_*.jpg"))
        imgs = [cover(cv2.imread(str(f))) for f in frames]
        raw = [seg(im) for im in imgs]
        for i, im in enumerate(imgs):
            labels = tidy(steady(raw[i - 1] if i else None, raw[i], raw[i + 1] if i + 1 < len(raw) else None))
            frame = cv2.resize(paint(im, labels), CLIP, interpolation=cv2.INTER_AREA)
            cv2.imwrite(str(tmp / f"out_{i:03d}.png"), frame)
            if i == 0:
                cv2.imwrite(str(args.out / "first.webp"), im, [cv2.IMWRITE_WEBP_QUALITY, 70])
                cv2.imwrite(str(args.out / "seg-first.webp"), frame, [cv2.IMWRITE_WEBP_QUALITY, 72])
        fps = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=r_frame_rate", "-of", "csv=p=0", str(args.videos / VIDEO)],
                             capture_output=True, text=True, check=True).stdout.strip()
        # H.264 main has the widest hardware decode support (Safari included). VP9 GPU decode can fail on some
        # paths; the page only shows the video once the first frame has actually rendered (intro-app.js).
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", fps, "-i", str(tmp / "out_%03d.png"),
                        "-c:v", "libx264", "-profile:v", "main", "-preset", "slow", "-crf", str(args.crf),
                        "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(args.out / "seg.mp4")],
                       check=True)
        stale = args.out / "seg.webm"
        if stale.exists():
            stale.unlink()

    npu = bench(args.model) if args.bench else None
    lines = [
        "# intro App 장면 — 출처",
        "",
        f"`scripts/intro/bake_app.py` 가 {datetime.date.today().isoformat()} 에 구웠다. 손으로 고치지 않는다.",
        "",
        f"- 영상: DEEPX 공식 sample 영상 묶음 `{SOURCE_PACK}` 의 `{VIDEO}` — {START:g} s 부터 {SECONDS:g} s "
        f"({len(frames)} frame, {fps} fps, 16:10 crop)",
        f"- model: 공식 Model Zoo `{args.model.name}` (Cityscapes 19 class, dx_app `Segformer_b0_512x1024Factory`) — "
        "모든 frame 을 DX-M1 에서",
        "- 칠하기: 차 · 사람 · 도로 · 식물 · 건물 · 거리 시설 여섯 무리, 하늘은 칠하지 않는다. 앞뒤 frame 과 맞춰 "
        f"깜빡임을 누르고, frame 면적 {MIN_AREA:.2%} 미만 조각은 지운다",
        f"- clip: `seg.mp4` H.264 main crf {args.crf}, {CLIP[0]}×{CLIP[1]}",
    ]
    if npu:
        lines.append(f"- NPU 처리량: `run_model -b -t 8 -w 20` → **{npu} FPS** (DX-M1, NPU 3 core)")
    (args.out / "SOURCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{len(frames)} frames · {npu or '-'} FPS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
