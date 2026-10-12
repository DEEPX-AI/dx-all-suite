"""Bake the intro Stream scene: 16 channels of real video plus real detections from DX-M1.

All 16 tiles share one color grade (the wall) so mixed sources look like one system, and boxes are stored as
coordinates (detections.json) rather than baked into the image, so the page draws and animates them itself.

The source is the official DEEPX sample video bundle the dx_stream demos use (not kept in the repo):

    curl -s https://sdk.deepx.ai/res/video/sample_videos.tar.gz | tar -xz -C <videos>

Inference runs the official Model Zoo yolov5-s 320 on DX-M1 through the dx_app example's factory (pre/post
processor, default threshold), unchanged. Run it with the runtime venv that has dx_engine and the NPU:

    dx-runtime/venv-dx-runtime/bin/python3 scripts/intro/bake_stream.py \\
        --videos <videos> --model <yolov5-s_320x320.dxnn> [--bench]
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
OUT = STUDIO / "launcher" / "static" / "img" / "intro" / "stream"
SOURCE_PACK = "https://sdk.deepx.ai/res/video/sample_videos.tar.gz"

# (video, seconds), 4×4 in row order. When a video is used twice, pick moments with a different view and framing.
SHOTS = [
    ("dron-citry-road.mov", 3), ("cctv-city-road2.mov", 2), ("blackbox-city-road.mp4", 1), ("dance-group.mov", 3),
    ("carrierbag.mp4", 2), ("cctv-city-road.mov", 6), ("dron-citry-road2.mov", 2), ("dogs.mp4", 2),
    ("blackbox-city-road2.mov", 9), ("dance-solo.mov", 4), ("cctv-city-road2.mov", 8), ("dron-citry-road.mov", 12),
    ("dance-group2.mov", 10), ("dron-citry-road2.mov", 5), ("carrierbag.mp4", 5), ("blackbox-city-road2.mov", 3),
]
HERO = 1          # intersection: top-down CCTV angle, large vehicles this model detects well
COLS = ROWS = 4
STAGE = (1600, 1000)   # screen coordinates (16:10); the page covers its area with this stage
GAP = 2                # gap between tiles (stage units)
SCALE = 1.5            # atlas resolution = stage × SCALE
TILE = ((STAGE[0] - GAP * (COLS - 1)) / COLS, (STAGE[1] - GAP * (ROWS - 1)) / ROWS)


def frame(video: Path, t: float, tmp: Path) -> np.ndarray:
    out = tmp / f"{video.stem}_{t}.png"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t), "-i", str(video), "-frames:v", "1", str(out)],
                   check=True)
    return cv2.imread(str(out))


def cover(img: np.ndarray, ratio: float) -> np.ndarray:
    h, w = img.shape[:2]
    if w / h > ratio:
        nw = int(round(h * ratio))
        x = (w - nw) // 2
        return img[:, x:x + nw]
    nh = int(round(w / ratio))
    y = (h - nh) // 2
    return img[y:y + nh]


def _duotone_lut() -> np.ndarray:
    """Gray 0–255 → 256 colors (RGB) running from navy through mid blue to cool white."""
    black, mid, white = np.array((3, 8, 20)), np.array((38, 66, 100)), np.array((205, 225, 240))
    g = np.arange(256)[:, None]
    lo = black + (mid - black) * (g / 127)
    hi = mid + (white - mid) * ((g - 127) / 128)
    return np.where(g <= 127, lo, hi).astype(np.float32)


_LUT = _duotone_lut()


def grade(bgr: np.ndarray) -> np.ndarray:
    """The grade that makes 16 tiles read as one system: a navy duotone keeping 18% of the original color (BGR in/out)."""
    rgb = bgr[..., ::-1].astype(np.float32)
    lum = rgb @ np.array([0.299, 0.587, 0.114], dtype=np.float32)
    base = np.clip(lum.mean() + (rgb - lum.mean()) * 1.25, 0, 255)             # contrast 1.25
    gray = np.clip(base @ np.array([0.299, 0.587, 0.114], dtype=np.float32), 0, 255).astype(np.uint8)
    out = (_LUT[gray] * 0.82 + base * 0.18) * 0.85
    return np.clip(out, 0, 255).astype(np.uint8)[..., ::-1]


class Detector:
    def __init__(self, model: Path):
        sys.path[:0] = [str(EXAMPLES), str(EXAMPLES / "object_detection" / "yolov5s_4")]
        from dx_engine import InferenceEngine
        from factory import Yolov5s_4Factory
        from common.utility.labels import get_coco_80_labels

        self.config = json.loads((EXAMPLES / "object_detection" / "yolov5s_4" / "config.json").read_text())
        self.ie = InferenceEngine(str(model))
        shape = self.ie.get_input_tensors_info()[0]["shape"]
        ih, iw = (shape[1], shape[2]) if shape[-1] in (1, 3) else (shape[2], shape[3])
        factory = Yolov5s_4Factory(self.config)
        self.pre = factory.create_preprocessor(iw, ih)
        self.post = factory.create_postprocessor(iw, ih)
        self.labels = get_coco_80_labels()

    def __call__(self, img: np.ndarray) -> list[dict]:
        tensor, ctx = self.pre.process(img)
        h, w = img.shape[:2]
        boxes = []
        for d in self.post.process(self.ie.run([tensor]), ctx):
            x0, y0, x1, y1 = (max(0.0, min(1.0, v)) for v in (d.box[0] / w, d.box[1] / h, d.box[2] / w, d.box[3] / h))
            if x1 - x0 < 0.004 or y1 - y0 < 0.004:
                continue
            name = d.class_name or self.labels[int(d.class_id)]
            boxes.append({"b": [round(x0, 4), round(y0, 4), round(x1, 4), round(y1, 4)], "c": name})
        return boxes


def bench(model: Path) -> str:
    out = subprocess.run(["run_model", "-m", str(model), "-b", "-t", "8", "-w", "20"],
                         capture_output=True, text=True, check=True).stdout
    return re.search(r"FPS\s*:\s*([\d.]+)", out).group(1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--videos", type=Path, required=True)
    ap.add_argument("--model", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=OUT)
    ap.add_argument("--bench", action="store_true", help="run_model 로 NPU FPS 를 재서 SOURCE.md 에 적는다")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    detect = Detector(args.model)
    ratio = TILE[0] / TILE[1]
    atlas = np.zeros((round(STAGE[1] * SCALE), round(STAGE[0] * SCALE), 3), np.uint8)
    tiles = []
    with tempfile.TemporaryDirectory() as tmp:
        for i, (name, t) in enumerate(SHOTS):
            img = cover(frame(args.videos / name, t, Path(tmp)), ratio)
            boxes = detect(img)
            r, c = divmod(i, COLS)
            x, y = c * (TILE[0] + GAP), r * (TILE[1] + GAP)
            x0, y0 = round(x * SCALE), round(y * SCALE)
            x1, y1 = round((x + TILE[0]) * SCALE), round((y + TILE[1]) * SCALE)
            atlas[y0:y1, x0:x1] = grade(cv2.resize(img, (x1 - x0, y1 - y0), interpolation=cv2.INTER_AREA))
            if i == HERO:
                hero = img
            tiles.append({"source": name, "t": t, "boxes": boxes})
            print(f"{i:2} {name:26} t={t:<3} {len(boxes):3} boxes")

    cv2.imwrite(str(args.out / "wall.webp"), atlas, [cv2.IMWRITE_WEBP_QUALITY, 74])
    cv2.imwrite(str(args.out / "hero.webp"), hero, [cv2.IMWRITE_WEBP_QUALITY, 66])
    data = {"stage": list(STAGE), "cols": COLS, "rows": ROWS, "gap": GAP, "hero": HERO, "tiles": tiles}
    (args.out / "detections.json").write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8")

    total = sum(len(t["boxes"]) for t in tiles)
    fps = bench(args.model) if args.bench else None
    lines = [
        "# intro Stream 장면 — 출처",
        "",
        f"`scripts/intro/bake_stream.py` 가 {datetime.date.today().isoformat()} 에 구웠다. 손으로 고치지 않는다.",
        "",
        f"- 영상: DEEPX 공식 sample 영상 묶음 `{SOURCE_PACK}` (dx_stream demo 용, 1080p)",
        f"- model: 공식 Model Zoo `{args.model.name}` (dx_app `Yolov5s_4Factory`, threshold {self_cfg(detect.config)})",
        f"- 결과: 16칸 · box {total}개 · 시작 화면은 {HERO}번 칸 (`{SHOTS[HERO][0]}`)",
    ]
    if fps:
        lines.append(f"- NPU 처리량: `run_model -b -t 8 -w 20` → **{fps} FPS** (DX-M1, NPU 3 core)")
    lines += ["", "| 칸 | 영상 | 초 | box |", "|---|---|---|---|"]
    lines += [f"| {i} | `{t['source']}` | {t['t']} | {len(t['boxes'])} |" for i, t in enumerate(tiles)]
    (args.out / "SOURCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"total {total} boxes" + (f" · {fps} FPS" if fps else ""))
    return 0


def self_cfg(cfg: dict) -> str:
    return ", ".join(f"{k} {v}" for k, v in cfg.items())


if __name__ == "__main__":
    raise SystemExit(main())
