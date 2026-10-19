# DX Model Zoo — 모델 카탈로그 및 인퍼런스 플랫폼

## [section:overview,소개] DX Model Zoo 개요

DX Model Zoo (Studio 경로 `/zoo/`)는 **약 500개 사전 검증된 모델의 종합 저장소**입니다.
직접 컴파일 없이 즉시 성능과 정확도를 검증할 수 있습니다.

- **태스크 카테고리**별 모델 브라우저 (필터 + 검색)
- 모델별 상세 정보: 스펙, 예제 코드, 라이선스
- **인퍼런스 데모**: DX App 연동으로 즉시 추론 테스트
- **YAML-Centric Orchestration**: 전처리/후처리/평가/컴파일 설정 단일 YAML 파일 관리
- **Unified CLI**: `dx_tool.sh` (list · search · info · add · extract · validate · run · bench 등) 단일 CLI
- **Multi-Profile 지원**: 모든 모델이 DEEPX NPU 아키텍처에 최적화, ONNX 평가 → NPU 실행까지 일관된 검증
- **Plugin-style 확장**: 전처리/후처리/데이터셋/평가자를 플러그인으로 추가 가능
- 카드/리스트 뷰 전환, 정렬 (이름/카테고리/FPS)
- 오프라인/온라인 모두: https://developer.deepx.ai/modelzoo/

## [section:model,network,catalog,카탈로그] 모델 카탈로그

### 주요 카테고리 (약 500개 모델 중 일부)

| 카테고리 | 아이콘 | 대표 모델 | 수 |
|----------|--------|-----------|-----|
| object_detection | 🎯 | YOLOv3~v12, YOLOX, NanoDet, DAMO-YOLO, SSD, EfficientDet | 50+ |
| classification | 🏷️ | ResNet/ResNeXt/WideResNet, MobileNet, EfficientNet (Lite/V2), ViT/DeiT/BEiT, MobileViT, FastViT, CasViT, RegNet, ShuffleNet, VGG, AlexNet | 30+ |
| face_detection | 👤 | RetinaFace, SCRFD, ULFGED, YOLOv5-Face, YOLOv7-Face | 8+ |
| face_recognition | 🔐 | ArcFace (IResNet50/100, MobileFaceNet, R50) | 5+ |
| face_landmark | 😀 | TDDFA v2 (MobileNet variants) | 2+ |
| face_attribute | 🏷️ | FaceAttrResNetV1-18 | 1+ |
| pose_estimation | 🏃 | CenterPose, YOLO26-Pose, YOLOv8-Pose | 5+ |
| hand_landmark | ✋ | MediaPipeHandsLite | 1+ |
| semantic_segmentation | 🖌️ | DeepLabV3/V3+, SegFormer, BiSeNet, UNet | 10+ |
| instance_segmentation | 🎨 | YOLACT, YOLOv5/v8/YOLO26-Seg | 6+ |
| obb_detection | 📐 | YOLO26-OBB | 3+ |
| zero_shot_segmentation | 🌐 | FastSAM | 1+ |
| depth_estimation | 📏 | FastDepth, SCDepthV3 | 4+ |
| image_denoising | ✨ | DnCNN variants (3/15/25/50채널, 컬러/그레이/블라인드) | 6 |
| super_resolution | 🔍 | ESPCN (x2/x3/x4) | 3+ |
| image_enhancement | 🌟 | ZeroDCE | 1+ |
| person_attribute | 🏷️ | DeepMAR (ResNet18/50) | 2+ |
| reid | 🔎 | CasViT-T, OSNet | 4+ |
| embedding | 🔗 | ArcFace | 8+ |
| ppu | ⚙️ | PPU 파이프라인 모델 | 5+ |

### 모델 상세 정보 (카드 클릭 시)
- **설명**: 한국어/영어 이중언어 지원
- **스펙**: 입력 해상도, 연산량 (FLOPs), 파라미터 수, 학습 데이터셋, 정확도 (mAP/Top-1)
- **양자화**: Q-Lite (INT8 경량), Q-Pro (고정밀)
- **성능**: FPS, FPS/와트 효율 지표
- **컴파일 가이드**: ONNX URL, 추천 양자화 설정, DX-COM 옵션
- **데모 코드**: C++, Python 예제 + CLI 명령어
- **라이선스**: 오픈소스 출처, 저작권 정보

### CLI 모델 다운로드 (DX-APP setup.sh)
```bash
./setup.sh                              # 인터랙티브 메뉴
./setup.sh --all                        # 전체 모델 자동 다운로드
./setup.sh --category "Face Detection"  # 특정 카테고리 (~30 MB)
./setup.sh --models SCRFD500M YOLOV11N  # 특정 모델 (~9 MB)
./setup.sh --list                       # 사용 가능 모델 목록
./setup.sh --dry-run                    # 다운로드 없이 미리보기
```

## [section:inference,run,추론] 인퍼런스 실행

### 사용 방법 (웹 UI)
1. 카탈로그에서 모델 선택 (모델을 먼저 다운로드해야 실행 가능)
2. **Run Inference** 패널에서 **Upload Image** (→ **Choose File**) 또는 **Sample Image** (→ **Use Default**) 선택
3. **Run Inference** 클릭 → DX App (`/app/`) 프록시로 실행
4. 결과 이미지 + FPS/Latency 통계 표시

### 전제 조건
- DX App 모듈이 **실행 중**이어야 함 (런처가 함께 띄운다)
- 상태 인디케이터: 🟢 (정상) / 🔴 (DX App 미실행)
- DX App 미실행 시 인퍼런스 버튼 비활성화

### 예제 이미지 유형
| 유형 | 적용 카테고리 |
|------|--------------|
| **single** | Detection 결과 (바운딩 박스) |
| **before_after** | 노이즈 제거, 초해상도, 이미지 향상 |
| **overlay** | 세그멘테이션, 깊이 맵 |
| **classified** | 분류 예측 |
| **gallery** | 재식별 매칭, 임베딩 |

### CLI 기반 벤치마크
```bash
# 모델 목록 확인
./scripts/dx_tool.sh list

# 모델 검색 / 정보 조회 (이름을 위치 인자로)
./scripts/dx_tool.sh search yolov8
./scripts/dx_tool.sh info yolov8

# 벤치마크 (FPS/Latency 측정)
./scripts/dx_tool.sh bench --filter yolov8 --loops 5

# 전체 명령 (add, export, list, search, info, delete, new-task, validate, run, bench)
./scripts/dx_tool.sh help
```
- `dx_tool.sh`에는 정확도 평가(eval)나 컴파일(compile) 명령이 없습니다. 컴파일은 DX Compiler (Studio 경로 `/compiler/`)를 사용하세요.

## [section:install,download,설치] 다운로드 및 설치

### 모델 다운로드 상태
- `downloaded`: 기본 .dxnn 파일 존재 여부
- `downloaded_qlite`: Q-Lite 양자화 모델
- `downloaded_qpro`: Q-Pro 양자화 모델

### 카탈로그 데이터 소스
- `test_models.conf` (dx_app `config/`): 모델 기본 목록 (탭 구분: 이름, 카테고리, 파일)
- `model_catalog.json`: 상세 메타데이터 (설명, 스펙, 데모 코드)
- 두 소스 자동 병합, `test_models.conf`가 기준

### YAML 오케스트레이션 (ModelZoo CLI)
각 모델의 전체 워크플로우를 YAML 파일 하나로 관리:
```yaml
model:
  name: YoloV7
  onnx_url: https://...
preprocessing:
  resize: [640, 640]
  normalize: true
postprocessing:
  type: yolov7_nms
quantization:
  calibration_dataset: coco_val2017
  method: intelligent_quantization
evaluation:
  dataset: coco
  metric: mAP
```

## [section:speed,performance,comparison,성능] 성능 비교

- 카탈로그에서 **FPS** 기준 정렬 가능
- 모델별 **FPS/와트** 효율 지표
- 카테고리 내 모델 간 스펙 비교
- **정확도 ↔ 속도 트레이드오프** 한눈에 확인
- DEEPX NPU에서 전 모델 최적화 보장 (INT8 Intelligent Quantization)

## [section:error,fail,에러] 에러 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| 인퍼런스 버튼 비활성화 | DX App (`/app/`) 미실행 | DX App 먼저 시작 |
| "DX App Unavailable" | DX App 모듈이 응답하지 않음 | 런처 상단 상태에서 DX App 확인, 필요하면 런처 재시작 |
| 모델 상세 404 | 잘못된 모델 ID | 카탈로그 새로고침 |
| 결과 이미지 안 나옴 | 추론 실패 | DX App 로그에서 에러 확인 |
| 카탈로그 비어있음 | `test_models.conf` 누락 | 파일 존재 여부 확인 |
| 모델 다운로드 실패 | 네트워크/서버 오류 | `--verbose` 옵션으로 상세 로그 확인 |
| Q-Pro 모델 없음 | 고정밀 버전 미제공 | Q-Lite 사용 또는 직접 컴파일 |
