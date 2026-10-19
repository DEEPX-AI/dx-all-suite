# intro Compiler 장면 — 출처

`scripts/intro/bake_compile.py` 가 2026-09-30 에 구웠다. 손으로 고치지 않는다.

- graph: `yolo26n.onnx` — Ultralytics Ultralytics YOLO26n model (v8.4.83, imgsz [640, 640])
- node 384 · edge 526 · 깊이 301 층 · parameter 2,450,977
- op: Conv 102 · Mul 90 · Sigmoid 88 · Concat 24 · Add 21 · Split 12 · Reshape 12 · Transpose 5 · MatMul 4 · MaxPool 3 · Unsqueeze 3 · Softmax 2 · Resize 2 · Slice 2 · TopK 2 · Flatten 2 · Tile 2 · GatherElements 2 · Sub 1 · ReduceMax 1 · Div 1 · Mod 1 · Gather 1 · Cast 1
- compile 결과: 공식 Model Zoo `yolo26-n_640x640.dxnn` (7.1 MB, onnx 9.9 MB)
- DX-M1 처리량: `run_model -b` → **212.21 FPS** (NPU 3 core)
