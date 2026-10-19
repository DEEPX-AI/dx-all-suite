# intro Stream 장면 — caption 수치의 근거

caption: **"Stream · 16 channels on one DX-M1 · 495 fps NPU"** (launcher-splash.js `_WORK[0].note`)

측정: 2026-09-30, 이 저장소의 개발 기기 — Intel N97 (4-core) host + DX-M1 (NPU 3 core, 1000 MHz), DXRT v3.4.2.

## NPU 처리량 — `run_model -m yolov5-s_320x320.dxnn -b -t 8 -w 20`

| 회차 | FPS |
|---|---|
| 1 (model 비교) | 505.87 |
| 2 (bake `--bench`) | 494.71 |
| 3 (bake `--bench`) | 497.85 |

caption 은 가장 낮은 값을 내려 쓴다: **495 fps** — 16 × 30 = 480 을 넘는다.

같은 조건의 다른 detection model (비교용): yolo26-n 640 212.21 · yolov8-n 640 199.32 · yolov5-n 640 141.04 ·
yolov5-xs 512 151.55 FPS.

## dx_stream 16채널 end-to-end

pipeline (채널마다, 16개 병렬, `sync=false`):

    filesrc ! qtdemux ! h264parse ! vah264dec ! queue ! dxpreprocess (320, keep_ratio) ! queue !
    dxinfer (yolov5-s_320x320.dxnn) ! queue ! fpsdisplaysink video-sink=fakesink

입력은 SOURCE.md 의 16칸과 같은 영상 (1080p h264). 결과: 16채널이 22.94 s 동안 6507 frame —
**합계 약 284 fps, 채널당 약 18 fps** (채널별 평균 18.0–30.6).

- 병목은 NPU 가 아니라 host 다 (1080p decode 16개 + 320 resize 를 4-core N97 이 따라가지 못한다).
  그래서 caption 은 "16 × 30 fps" 가 아니라, 참인 NPU 수치로 말한다 (사용자 결정).
- `dxpostprocess` 는 빠져 있다: 설치된 `libpostprocess_yolov5s_6.so` 가 이 model 에서 SIGSEGV 를
  낸다 (vah264dec · avdec_h264 둘 다, 입력 320 으로 다시 build 해도 같다). dx_stream 쪽 문제로 따로 본다.
