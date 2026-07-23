# DX Stream — 실시간 비전 AI 스트리밍 플랫폼 (v3.0.0)

## [section:overview,소개] DX Stream 개요

DX Stream (포트 8093)은 **GStreamer 기반 Vision AI 애플리케이션 개발 도구**로, DEEPX NPU를 활용하여 실시간 비전 AI 파이프라인을 빠르고 쉽게 구현할 수 있습니다.
- **13개 DxStream 커스텀 GStreamer 엘리먼트** — 전처리/추론/후처리/추적/메시징 완전 커버
- **10종 프리셋 데모**: Object Detection, Face, Pose, Tracking, Multi-Stream
- **비주얼 파이프라인 빌더**: 드래그 & 드롭으로 커스텀 파이프라인 구성
- **WebRTC 스트리밍**: 브라우저에서 실시간 영상 확인
- **Python bindings (pydxs)**: Python에서 파이프라인 제어
- **16종 사전 학습 모델** (5개 카테고리)
- **지원 보드**: x86_64 PC, Raspberry Pi 5, Orange Pi 5 Plus (aarch64)

### 공식 문서 구조
1. Overview — 아키텍처 개요
2. Installation — 빌드/설치 가이드
3. Elements (13개) — 각 엘리먼트 상세 문서
4. Writing Your Own Application — 커스텀 앱 개발 가이드
5. Pipeline Examples — Single/Multi/Secondary/MsgBroker
6. Troubleshooting & FAQ
7. Appendix — User Metadata, GstShark 성능 평가, Change Log

## [section:pipeline,gstreamer,gst,pipe,파이프라인] 파이프라인 빌더

### 비주얼 에디터
1. 왼쪽 팔레트에서 **엘리먼트 드래그** → 캔버스에 배치
2. 포트 연결 (출력 → 입력) 으로 **엣지 생성**
3. 엘리먼트 속성 편집 (모델 경로, 리사이즈 크기 등)
4. **Validate** → `gst-launch` 문자열로 변환 확인
5. **Run** → GStreamer 파이프라인 실행 + WebRTC 연결

### 파이프라인 → gst-launch 변환
JSON 노드/엣지 구조가 `gst-launch-1.0` 명령어 문자열로 자동 변환됩니다.
- 노드: `element_type property1=value1 property2=value2`
- 엣지: `!` 또는 `name.src ! name.sink` 형태

### 파이프라인 아키텍처 (기본 흐름)
```
[Source] → [DxPreprocess] → [DxInfer] → [DxPostprocess] → [DxOsd] → [Encode] → [WebRTC]
  │                                                   │
  └── rtspsrc, urisourcebin, v4l2src              DxTracker (선택)
```

### 파이프라인 예제 유형
| 예제 | 설명 |
|------|------|
| **Single Stream** | 단일 비디오/카메라 → NPU 추론 → WebRTC 출력 |
| **Multi Stream** | 여러 입력 소스 → 개별 추론 → 그리드 합성 |
| **Secondary Inference** | 1차 감지 → ROI 추출 → 2차 분류/인식 체이닝 |
| **MsgBroker** | 추론 메타데이터 → JSON 변환 → MQTT/Kafka 발행 |

### 제약 사항
- **단일 파이프라인**: 동시에 하나의 파이프라인만 실행 가능
- **WebRTC 1:1**: 하나의 피어 연결만 지원

## [section:video,stream,camera,rtsp,데모] 데모 파이프라인

### 10종 프리셋 데모
| ID | 이름 | 카테고리 | 주요 기능 |
|----|------|----------|-----------|
| 0 | Object Detection | 객체 탐지 | 개별 속성 모드 |
| 1 | Object Detection PPU | 객체 탐지 | Config 파일 모드, PPU 하드웨어 후처리 |
| 2 | Face Detection | 얼굴 탐지 | 전용 postproc 라이브러리 |
| 3 | Face Detection PPU | 얼굴 탐지 | PPU 가속 |
| 4 | Pose Estimation | 자세 추정 | 키포인트 오버레이 |
| 5 | Pose Estimation PPU | 자세 추정 | PPU 가속 |
| 6 | Semantic Segmentation | 시맨틱 분할 | 마스크 시각화 |
| 7 | Multi-Object Tracking | 다중 객체 추적 | OC_SORT 알고리즘 |
| 8 | Multi-Stream | 멀티 스트림 | 4채널 2×2 그리드 |
| 9 | Multi-Stream RTSP | 멀티 RTSP | 네트워크 카메라 입력 |

### CLI 데모 실행
```bash
./run_demo.sh              # 인터랙티브 데모 선택
./setup.sh                 # 모델 + 샘플 비디오 다운로드
```

### 인코더 자동 감지 (우선순위)
1. `vaapih264enc` (하드웨어 H.264)
2. `x264enc tune=zerolatency` (소프트웨어 H.264)
3. `vp8enc deadline=1` (VP8)
4. `jpegenc` (JPEG 폴백)

## [section:element,엘리먼트,플러그인] DxStream 커스텀 엘리먼트 (13개)

### 추론 파이프라인 핵심 3요소
| 엘리먼트 | 역할 | 주요 속성 |
|----------|------|-----------|
| **DxPreprocess** | 추론용 이미지 전처리 | `width`, `height`, `color-format`, `crop-mode` |
| **DxInfer** | DEEPX NPU 모델 추론 | `model` (.dxnn 경로), `config` (JSON), `batch-size` |
| **DxPostprocess** | 결과 디코딩 (.so 라이브러리) | `lib-path`, `func-name`, `label-file` |

### 추적 & 시각화
| 엘리먼트 | 역할 | 주요 속성 |
|----------|------|-----------|
| **DxTracker** | 다중 객체 추적 (OC_SORT) | `algorithm`, `max-age`, `min-hits`, `iou-threshold` |
| **DxOsd** | 바운딩박스/라벨/마스크/키포인트 오버레이 | `font-size`, `border-width`, `show-label`, `show-score` |

### 전처리 보조
| 엘리먼트 | 역할 | 주요 속성 |
|----------|------|-----------|
| **DxScale** | 하드웨어 가속 이미지 스케일링 | `width`, `height`, `method` |
| **DxConvert** | 컬러 스페이스 변환 | `format` |

### 유틸리티
| 엘리먼트 | 역할 | 설명 |
|----------|------|------|
| **DxRate** | 프레임 레이트 제어 | 입력 FPS를 지정된 값으로 제한 |
| **DxGather** | 병렬 브랜치 병합 | 여러 파이프라인 브랜치 결과를 하나로 합침 |
| **DxInputSelector** | 입력 스트림 선택 | 여러 입력 중 하나를 동적 선택 |
| **DxOutputSelector** | 출력 스트림 선택 | 하나의 입력을 여러 출력 중 하나로 라우팅 |

### 메시징 (IoT / 클라우드 연동)
| 엘리먼트 | 역할 | 설명 |
|----------|------|------|
| **DxMsgConv** | 메타데이터 → JSON 변환 | 추론 결과를 구조화된 JSON으로 변환 |
| **DxMsgBroker** | 메시지 브로커 발행 | MQTT, Kafka 등으로 JSON 메시지 전송 |

### 표준 GStreamer 엘리먼트 (파이프라인에서 같이 사용)
- **소스**: `urisourcebin` (파일/URL), `rtspsrc` (RTSP), `v4l2src` (카메라)
- **디코드**: `decodebin` (자동 코덱 감지)
- **변환**: `videoconvert`, `videoscale`
- **인코딩**: `x264enc`, `vaapih264enc`, `vp8enc`, `jpegenc`
- **RTP**: `rtph264pay`, `rtpvp8pay`, `rtpjpegpay`
- **출력**: `webrtcbin name=sendrecv bundle-policy=max-bundle`

## [section:webrtc,스트리밍] WebRTC 스트리밍

### 연결 방식 (HTTP 기반 시그널링, WebSocket 없음)
1. 클라이언트: `POST /api/webrtc/offer` → SDP Offer 전송
2. 서버: SDP Answer 반환
3. 클라이언트: `POST /api/webrtc/ice` → ICE 후보 전송
4. 서버: `GET /api/webrtc/ice` → 서버 ICE 후보 폴링 (100ms 간격)

### 클라이언트 기능
- 자동 재시도: 실패 시 3회 (1초/2초/4초 간격)
- FPS/지연 시간 통계 오버레이
- 키보드 단축키: P=일시정지, M=음소거, F=전체화면

## [section:model,모델] 사전 학습 모델 (16종)

| 카테고리 | 모델 | 비고 |
|----------|------|------|
| Object Detection (8) | YOLOv26n, YOLOv5S, YOLOv7, YOLOv8N, YOLOv9S, YOLOXs, YOLOv11N, YOLOv5S_PPU | PPU 포함 |
| Face Detection (3) | YOLOv5s_Face, SCRFD500M, SCRFD500M_PPU | — |
| Pose Estimation (3) | YOLOv26n_Pose, YOLOv8m_Pose, YOLOV5Pose_PPU | — |
| Segmentation (1) | YOLOv26n_Seg | — |
| Classification (1) | EfficientNet_Lite0 | — |

## [section:install,setup,설치] 설치 및 셋업

### 빌드 & 설치
```bash
# 의존성 설치
./install.sh                  # GStreamer, GI 바인딩, 기타

# 플러그인 빌드
./build.sh                    # libgstdxstream.so 컴파일

# 모델 + 비디오 다운로드
./setup.sh                    # 모델 및 샘플 비디오
./setup_sample_models.sh      # 모델만
./setup_sample_videos.sh      # 비디오만
```

### 플러그인 확인
```bash
gst-inspect-1.0 dxstream     # 플러그인 정보 출력
gst-inspect-1.0 dxinfer      # DxInfer 엘리먼트 상세
```

### GstShark 성능 측정 (선택사항)
```bash
./install_gstshark.sh         # GstShark 설치
# 파이프라인 실행 시 프레임별 레이턴시, 처리량 측정
```

### Writing Your Own Application
DxStream 엘리먼트를 조합하여 커스텀 앱 개발 가능. 공식 가이드:
- https://github.com/DEEPX-AI/dx_stream/blob/main/docs/source/docs/04_Writing_Your_Own_Application.md

### User Metadata Guide
DxStream 파이프라인에서 커스텀 메타데이터를 엘리먼트 간 전달하는 방법:
- https://github.com/DEEPX-AI/dx_stream/blob/main/docs/source/docs/Appendix_User_Metadata_Guide.md

## [section:error,fail,bug,에러] 에러 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| 데모 "Unavailable" | 모델 미설치 또는 NPU 없음 | `./setup.sh`로 모델 다운로드 + NPU 드라이버 확인 |
| WebRTC 연결 실패 | ICE 타임아웃 (30초) | 네트워크 확인, 방화벽 점검 |
| "No such element dxinfer" | 플러그인 미빌드 | `./build.sh` 실행 후 `gst-inspect-1.0 dxstream` |
| 인코더 없음 | GStreamer 플러그인 누락 | `gst-inspect-1.0 x264enc`로 확인, `apt install gstreamer1.0-plugins-ugly` |
| GI 바인딩 없음 | python3-gi 미설치 | `apt install python3-gi gir1.2-gst-rtsp-server-1.0` |
| RTSP 연결 실패 | 카메라 URL 오류 | `ffplay rtsp://주소`로 직접 테스트 |
| 영상 깨짐 | 프레임 레이트 불일치 | DxRate로 FPS 제한 추가 |
| Orange Pi/RPi 빌드 실패 | ARM64 의존성 | Appendix_Build_on_OrangePi5Plus.md 참조 |
| Multi-Stream 지연 | 입력 소스 수 과다 | 스트림 수 줄이기 또는 모델 경량화 (예: YOLOv26n) |
