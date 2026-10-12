"""Bake the Stream Demo Launcher card and stage preview images from real inference results.

Each demo runs its model on DX-M1 over one frame of an official DEEPX sample video. Inference and drawing come
straight from the dx_app Python examples (IFactory, SyncRunner); each example writes its result to `DXAPP_SAVE_IMAGE`.

    dx-runtime/venv-dx-runtime/bin/python3 scripts/demo/bake_stream_thumbs.py --videos <videos> --models <models>

Inputs (not kept in the repo):
    videos: blackbox-city-road.mp4 · dance-group.mov, from the official bundle the dx_stream demos use
            curl -s https://sdk.deepx.ai/res/video/sample_videos.tar.gz | tar -xz -C <videos> \\
                --wildcards '*blackbox-city-road.mp4' '*dance-group.mov'
    models: official Model Zoo .dxnn files, saved under the dx_stream demo names (MODEL_ZOO table)

Output: dx_stream/static/img/demo/<id>.webp (640×360, ≤ 60 KB) + SOURCE.md
"""
from __future__ import annotations

import argparse
import datetime
import os
import subprocess
import sys
import tempfile
from pathlib import Path

STUDIO = Path(__file__).resolve().parents[2]
SUITE = STUDIO.parent
DX_APP = Path(os.environ.get("DX_APP_ROOT") or SUITE / "dx-runtime" / "dx_app")
EXAMPLES = DX_APP / "src" / "python_example"
OUT = STUDIO / "dx_stream" / "static" / "img" / "demo"
SIZE = (640, 360)
MAX_BYTES = 60 * 1024

ROAD, DANCE = "blackbox-city-road.mp4", "dance-group.mov"

# dx_stream demo model name → official Model Zoo file (2_4_0)
MODEL_ZOO = {
    "yolo26n.dxnn": "q-lite-dxnn/2_4_0/yolo26-n_640x640.dxnn",
    "YoloV5S_PPU.dxnn": "q-lite-dxnn/2_4_0/yolov5-s_640x640_ppu.dxnn",
    "YOLOv5s_Face.dxnn": "q-lite-dxnn/2_4_0/yolov5-s-face_640x640.dxnn",
    "SCRFD500M_PPU.dxnn": "dxnn/2_4_0/SCRFD500M_PPU.dxnn",
    "yolo26n-pose.dxnn": "q-lite-dxnn/2_4_0/yolo26-n-pose_640x640.dxnn",
    "YOLOV5Pose_PPU.dxnn": "dxnn/2_4_0/YOLOV5Pose_PPU.dxnn",
    "yolo26n-seg.dxnn": "q-lite-dxnn/2_4_0/yolo26-n-seg_640x640.dxnn",
    "yolo26-depth-n_768x768.dxnn": "dxnn/2_4_0/yolo26-depth-n_768x768.dxnn",
    "SCRFD500M.dxnn": "q-lite-dxnn/2_4_0/scrfd-500m_640x640.dxnn",
}

# demo id → its model, the dx_app example to run, and the source frame. `steps` are drawn on top of each other in
# order (secondary inference). `grid` tiles four frames 2×2, like multi-stream. The table must match DEMOS in
# dx_stream/core/demos.py (tests/dx_stream/test_demo_thumbs.py).
PLAN = {
    0: {"model": "yolo26n.dxnn", "steps": [("object_detection/yolo26n", "yolo26n.dxnn")], "video": ROAD, "at": [6.0]},
    1: {"model": "YoloV5S_PPU.dxnn", "steps": [("ppu/yolov5s_ppu", "YoloV5S_PPU.dxnn")], "video": ROAD, "at": [6.0]},
    2: {"model": "YOLOv5s_Face.dxnn", "steps": [("face_detection/yolov5s_face", "YOLOv5s_Face.dxnn")], "video": DANCE, "at": [6.0]},
    3: {"model": "SCRFD500M_PPU.dxnn", "steps": [("ppu/scrfd500m_ppu", "SCRFD500M_PPU.dxnn")], "video": DANCE, "at": [6.0]},
    4: {"model": "yolo26n-pose.dxnn", "steps": [("pose_estimation/yolo26n_pose", "yolo26n-pose.dxnn")], "video": DANCE, "at": [10.0]},
    5: {"model": "YOLOV5Pose_PPU.dxnn", "steps": [("ppu/yolov5pose_ppu", "YOLOV5Pose_PPU.dxnn")], "video": DANCE, "at": [10.0]},
    6: {"model": "yolo26n-seg.dxnn", "steps": [("instance_segmentation/yolo26n_seg", "yolo26n-seg.dxnn")], "video": ROAD, "at": [3.0]},
    7: {"model": "YoloV5S_PPU.dxnn", "steps": [("ppu/yolov5s_ppu", "YoloV5S_PPU.dxnn")], "video": ROAD, "at": [9.0],
        "note": "tracker ID 는 GStreamer dxtracker 가 붙인다 — 이미지는 같은 model 의 frame 한 장"},
    8: {"model": "YoloV5S_PPU.dxnn", "steps": [("ppu/yolov5s_ppu", "YoloV5S_PPU.dxnn")], "video": ROAD,
        "at": [1.0, 4.0, 7.0, 10.0], "grid": True, "note": "네 channel — 같은 영상의 네 시점을 2×2 로"},
    9: {"model": "YoloV5S_PPU.dxnn", "steps": [("ppu/yolov5s_ppu", "YoloV5S_PPU.dxnn")], "video": ROAD, "at": [2.0],
        "note": "RTSP 기본 입력 (demo CCTV) 은 sample 묶음에 없다 — 도로 영상 frame 으로 대신"},
    10: {"model": "YoloV5S_PPU.dxnn", "steps": [("ppu/yolov5s_ppu", "YoloV5S_PPU.dxnn"),
                                                 ("face_detection/scrfd500m", "SCRFD500M.dxnn")], "video": DANCE, "at": [6.0],
         "note": "1차 사람 (YoloV5S_PPU) 위에 2차 얼굴 (SCRFD500M) 을 겹쳐 그림. 속성 분류 (EfficientNet_Lite0) 는 글자뿐이라 뺐다"},
    11: {"model": "yolo26-depth-n_768x768.dxnn", "steps": [("depth_estimation/yolo26_depth_n", "yolo26-depth-n_768x768.dxnn")],
         "video": ROAD, "at": [6.0]},
}

RUNTIME_PY = SUITE / "dx-runtime" / "venv-dx-runtime" / "bin" / "python3"


def grab(video: Path, at: float, out: Path) -> None:
    import cv2

    cap = cv2.VideoCapture(str(video))
    cap.set(cv2.CAP_PROP_POS_MSEC, at * 1000)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise SystemExit(f"frame 을 못 읽었다: {video} @ {at}s")
    cv2.imwrite(str(out), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])


def example_dir(example: str, model: str) -> Path:
    """PLAN examples use the <task>/<model> layout. When dx_app uses the per-model layout, use the model's
    Model Zoo stem folder (<task>/<family>/<stem>) instead, the same shape as shared/dx_app_layout.py."""
    legacy = EXAMPLES / example
    if legacy.is_dir():
        return legacy
    # Runs in the runtime venv, where the studio's shared package is missing; one glob finds the folder.
    stem = MODEL_ZOO.get(model, model).rsplit("/", 1)[-1].removesuffix(".dxnn")
    hits = sorted(d for d in EXAMPLES.glob(f"*/*/{stem}") if (d / f"{stem}_sync.py").is_file())
    if not hits:
        raise SystemExit(f"예제를 찾지 못했다: {example} ({stem})")
    return hits[0]


def infer(example: str, model: Path, image: Path, out: Path) -> None:
    ex = example_dir(example, model.name)
    script = ex / f"{ex.name}_sync.py"
    env = dict(os.environ, DXAPP_SAVE_IMAGE=str(out))
    env.pop("DISPLAY", None)
    env.pop("WAYLAND_DISPLAY", None)
    r = subprocess.run([sys.executable, str(script), "-m", str(model), "-i", str(image), "--no-display"],
                       cwd=ex, env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not out.exists():
        raise SystemExit(f"{example} 실패 (exit {r.returncode}):\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")


def cover(img, size=SIZE):
    import cv2

    h, w = img.shape[:2]
    ratio = size[0] / size[1]
    if w / h > ratio:
        nw = int(round(h * ratio))
        img = img[:, (w - nw) // 2:(w - nw) // 2 + nw]
    else:
        nh = int(round(w / ratio))
        img = img[(h - nh) // 2:(h - nh) // 2 + nh]
    return cv2.resize(img, size, interpolation=cv2.INTER_AREA)


def tile(images):
    import numpy as np

    gap = 4
    cw, ch = (SIZE[0] - gap) // 2, (SIZE[1] - gap) // 2
    canvas = np.full((SIZE[1], SIZE[0], 3), 14, np.uint8)
    for i, img in enumerate(images[:4]):
        x, y = (i % 2) * (cw + gap), (i // 2) * (ch + gap)
        canvas[y:y + ch, x:x + cw] = cover(img, (cw, ch))
    return canvas


def write_webp(img, path: Path) -> int:
    import cv2

    for q in (80, 72, 64, 56, 48, 40):
        ok, buf = cv2.imencode(".webp", img, [cv2.IMWRITE_WEBP_QUALITY, q])
        if ok and len(buf) <= MAX_BYTES:
            path.write_bytes(buf.tobytes())
            return len(buf)
    raise SystemExit(f"{path.name}: {MAX_BYTES} bytes 안으로 못 줄였다")


def bake(demo_id: int, plan: dict, videos: Path, models: Path, tmp: Path) -> tuple[int, str]:
    import cv2

    shots = []
    for k, at in enumerate(plan["at"]):
        src = tmp / f"{demo_id}_{k}_src.jpg"
        grab(videos / plan["video"], at, src)
        cur = src
        for j, (example, model) in enumerate(plan["steps"]):
            nxt = tmp / f"{demo_id}_{k}_{j}.jpg"
            infer(example, models / model, cur, nxt)
            cur = nxt
        shots.append(cv2.imread(str(cur)))
    img = tile(shots) if plan.get("grid") else cover(shots[0])
    size = write_webp(img, OUT / f"{demo_id}.webp")
    return size, ", ".join(f"{t:g}s" for t in plan["at"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--videos", type=Path, required=True)
    ap.add_argument("--models", type=Path, required=True)
    ap.add_argument("--only", type=int, nargs="*", help="이 demo id 만")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    with tempfile.TemporaryDirectory() as td:
        for demo_id, plan in PLAN.items():
            if args.only and demo_id not in args.only:
                continue
            size, at = bake(demo_id, plan, args.videos, args.models, Path(td))
            models = " + ".join(f"`{m}` ({MODEL_ZOO[m]})" for _, m in plan["steps"])
            rows.append((demo_id, plan["video"], at, models, plan.get("note", ""), size))
            print(f"demo {demo_id}: {size} bytes")
    if args.only:
        return
    lines = [
        "# Stream demo 이미지 — 출처",
        "",
        f"`scripts/demo/bake_stream_thumbs.py` 로 {datetime.date.today().isoformat()} 에 DX-M1 에서 구웠다. 소재는 dx_stream demo 가",
        "쓰는 DEEPX 공식 sample 영상 묶음 (https://sdk.deepx.ai/res/video/sample_videos.tar.gz), model 은 공식",
        "Model Zoo (https://sdk.deepx.ai/modelzoo/). 추론 · 그리기는 dx_app Python 예제 (SyncRunner) 그대로.",
        "",
        "| id | 영상 · 시점 | model (Model Zoo) | 메모 | 크기 |",
        "|---|---|---|---|---|",
    ]
    for demo_id, video, at, models, note, size in rows:
        lines.append(f"| {demo_id} | `{video}` @ {at} | {models} | {note} | {size // 1024} KB |")
    (OUT / "SOURCE.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
