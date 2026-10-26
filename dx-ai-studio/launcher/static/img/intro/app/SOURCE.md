# intro App 장면 — 출처

`scripts/intro/bake_app.py` 가 2026-09-30 에 구웠다. 손으로 고치지 않는다.

- 영상: DEEPX 공식 sample 영상 묶음 `https://sdk.deepx.ai/res/video/sample_videos.tar.gz` 의 `blackbox-city-road.mp4` — 1 s 부터 3 s (90 frame, 30/1 fps, 16:10 crop)
- model: 공식 Model Zoo `segformer_mit-b0_512x1024.dxnn` (Cityscapes 19 class, dx_app `Segformer_b0_512x1024Factory`) — 모든 frame 을 DX-M1 에서
- 칠하기: 차 · 사람 · 도로 · 식물 · 건물 · 거리 시설 여섯 무리, 하늘은 칠하지 않는다. 앞뒤 frame 과 맞춰 깜빡임을 누르고, frame 면적 0.05% 미만 조각은 지운다
- clip: `seg.mp4` H.264 main crf 28, 1440×900
- NPU 처리량: `run_model -b -t 8 -w 20` → **194.03 FPS** (DX-M1, NPU 3 core)
