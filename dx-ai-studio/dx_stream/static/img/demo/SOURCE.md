# Stream demo 이미지 — 출처

`scripts/demo/bake_stream_thumbs.py` 로 2026-10-01 에 DX-M1 에서 구웠다. 소재는 dx_stream demo 가
쓰는 DEEPX 공식 sample 영상 묶음 (https://sdk.deepx.ai/res/video/sample_videos.tar.gz), model 은 공식
Model Zoo (https://sdk.deepx.ai/modelzoo/). 추론 · 그리기는 dx_app Python 예제 (SyncRunner) 그대로.

| id | 영상 · 시점 | model (Model Zoo) | 메모 | 크기 |
|---|---|---|---|---|
| 0 | `blackbox-city-road.mp4` @ 6s | `yolo26n.dxnn` (q-lite-dxnn/2_4_0/yolo26-n_640x640.dxnn) |  | 23 KB |
| 1 | `blackbox-city-road.mp4` @ 6s | `YoloV5S_PPU.dxnn` (q-lite-dxnn/2_4_0/yolov5-s_640x640_ppu.dxnn) |  | 24 KB |
| 2 | `dance-group.mov` @ 6s | `YOLOv5s_Face.dxnn` (q-lite-dxnn/2_4_0/yolov5-s-face_640x640.dxnn) |  | 16 KB |
| 3 | `dance-group.mov` @ 6s | `SCRFD500M_PPU.dxnn` (dxnn/2_4_0/SCRFD500M_PPU.dxnn) |  | 16 KB |
| 4 | `dance-group.mov` @ 10s | `yolo26n-pose.dxnn` (q-lite-dxnn/2_4_0/yolo26-n-pose_640x640.dxnn) |  | 27 KB |
| 5 | `dance-group.mov` @ 10s | `YOLOV5Pose_PPU.dxnn` (dxnn/2_4_0/YOLOV5Pose_PPU.dxnn) |  | 24 KB |
| 6 | `blackbox-city-road.mp4` @ 3s | `yolo26n-seg.dxnn` (q-lite-dxnn/2_4_0/yolo26-n-seg_640x640.dxnn) |  | 21 KB |
| 7 | `blackbox-city-road.mp4` @ 9s | `YoloV5S_PPU.dxnn` (q-lite-dxnn/2_4_0/yolov5-s_640x640_ppu.dxnn) | tracker ID 는 GStreamer dxtracker 가 붙인다 — 이미지는 같은 model 의 frame 한 장 | 25 KB |
| 8 | `blackbox-city-road.mp4` @ 1s, 4s, 7s, 10s | `YoloV5S_PPU.dxnn` (q-lite-dxnn/2_4_0/yolov5-s_640x640_ppu.dxnn) | 네 channel — 같은 영상의 네 시점을 2×2 로 | 32 KB |
| 9 | `blackbox-city-road.mp4` @ 2s | `YoloV5S_PPU.dxnn` (q-lite-dxnn/2_4_0/yolov5-s_640x640_ppu.dxnn) | RTSP 기본 입력 (demo CCTV) 은 sample 묶음에 없다 — 도로 영상 frame 으로 대신 | 22 KB |
| 10 | `dance-group.mov` @ 6s | `YoloV5S_PPU.dxnn` (q-lite-dxnn/2_4_0/yolov5-s_640x640_ppu.dxnn) + `SCRFD500M.dxnn` (q-lite-dxnn/2_4_0/scrfd-500m_640x640.dxnn) | 1차 사람 (YoloV5S_PPU) 위에 2차 얼굴 (SCRFD500M) 을 겹쳐 그림. 속성 분류 (EfficientNet_Lite0) 는 글자뿐이라 뺐다 | 20 KB |
| 11 | `blackbox-city-road.mp4` @ 6s | `yolo26-depth-n_768x768.dxnn` (dxnn/2_4_0/yolo26-depth-n_768x768.dxnn) |  | 5 KB |
