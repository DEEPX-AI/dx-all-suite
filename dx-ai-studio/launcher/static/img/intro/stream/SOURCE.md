# intro Stream 장면 — 출처

`scripts/intro/bake_stream.py` 가 2026-09-30 에 구웠다. 손으로 고치지 않는다.

- 영상: DEEPX 공식 sample 영상 묶음 `https://sdk.deepx.ai/res/video/sample_videos.tar.gz` (dx_stream demo 용, 1080p)
- model: 공식 Model Zoo `yolov5-s_320x320.dxnn` (dx_app `Yolov5s_4Factory`, threshold score_threshold 0.4, nms_threshold 0.45)
- 결과: 16칸 · box 121개 · 시작 화면은 1번 칸 (`cctv-city-road2.mov`)
- NPU 처리량: `run_model -b -t 8 -w 20` → **497.85 FPS** (DX-M1, NPU 3 core)

| 칸 | 영상 | 초 | box |
|---|---|---|---|
| 0 | `dron-citry-road.mov` | 3 | 7 |
| 1 | `cctv-city-road2.mov` | 2 | 15 |
| 2 | `blackbox-city-road.mp4` | 1 | 7 |
| 3 | `dance-group.mov` | 3 | 8 |
| 4 | `carrierbag.mp4` | 2 | 8 |
| 5 | `cctv-city-road.mov` | 6 | 12 |
| 6 | `dron-citry-road2.mov` | 2 | 5 |
| 7 | `dogs.mp4` | 2 | 4 |
| 8 | `blackbox-city-road2.mov` | 9 | 5 |
| 9 | `dance-solo.mov` | 4 | 1 |
| 10 | `cctv-city-road2.mov` | 8 | 12 |
| 11 | `dron-citry-road.mov` | 12 | 4 |
| 12 | `dance-group2.mov` | 10 | 7 |
| 13 | `dron-citry-road2.mov` | 5 | 10 |
| 14 | `carrierbag.mp4` | 5 | 8 |
| 15 | `blackbox-city-road2.mov` | 3 | 8 |
