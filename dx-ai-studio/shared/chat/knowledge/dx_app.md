# DX App — AI 추론 및 개발 플랫폼 (v3.1.0)

## [section:overview,소개] DX App 개요

DX App (포트 8080)은 DX AI Studio의 핵심 앱이자, **production-ready AI 추론 템플릿 스위트**입니다.
- NPU를 활용한 **이미지/영상/카메라/RTSP 추론** 실행
- **280+ 모델 × 17 태스크**, C++/Python 듀얼 언어 지원
- **Sync/Async 실행 패러다임** — 비동기(RunAsync)로 FPS 극대화
- **Unified Post-Processing Engine** — C++ 최적화, pybind11(dx_postprocess)로 Python에서도 C++ 속도
- ONNX → `.dxnn` **컴파일** (DX-COM 연동)
- **NPU 하드웨어 모니터링** (온도, 전압, 클럭)
- **개발자 도구**: 모델 스캐폴딩, Git 연동, 배포
- **커뮤니티 포럼**: 질문/답변, 태그 기반 검색

## [section:inference,run,predict,추론,실행] 추론 실행

### 지원 입력 유형
| 유형 | 설명 | 포맷 | CLI 옵션 |
|------|------|------|----------|
| **Image** | 정적 이미지 추론 | JPEG, PNG, BMP | `--image` (`-i`) |
| **Video** | 배치 영상 처리 (프레임별) | MP4, MOV, AVI, MKV | `--video` (`-v`) |
| **Live Camera** | 실시간 카메라 스트림 | /dev/video* | `--camera` (`-c`) |
| **RTSP** | 네트워크 카메라 스트림 | rtsp://주소 | `--rtsp` (`-r`) |

> 입력 미지정 시 태스크에 맞는 기본 샘플 이미지 자동 선택 (예: 객체감지 → `sample_street.jpg`)

### 추론 실행 방법 (웹 UI)
1. 모델 선택 (레지스트리에서 카테고리별 필터)
2. 입력 유형 선택 (이미지/영상/카메라/RTSP)
3. 파라미터 조절 (Confidence, NMS threshold) — `config.json`으로 모델별 튜닝
4. **Run** 클릭 → 결과 이미지 + FPS/Latency 표시

### CLI 추론 (터미널)
```bash
# 가장 간단한 실행 (모델 자동 다운로드 + 기본 샘플 이미지)
python src/python_example/object_detection/yolov7/yolov7_sync.py --model assets/models/YoloV7.dxnn

# C++ 비동기 비디오 추론 (최대 FPS)
./bin/yolov9s_async -m assets/models/YoloV9S.dxnn -v assets/videos/dance-group.mov

# 결과 저장
./bin/yolov9s_sync -m assets/models/YoloV9S.dxnn -i sample/img/sample_kitchen.jpg --save
```

### Interactive Demo (18개 데모 태스크)
```bash
./run_demo.sh                          # 인터랙티브 메뉴
./run_demo.sh --task 0 --mode 1 --input 2  # 비인터랙티브 (YOLOv7, C++ sync, image)
```

| 데모 # | 태스크 | 모델 | 크기 |
|--------|--------|------|------|
| 0 | Object Detection | YoloV7.dxnn | 74 MB |
| 1 | Object Detection | YOLOV11N.dxnn | 7 MB |
| 2 | Face Detection | SCRFD500M.dxnn | 2.1 MB |
| 3 | OBB Detection | yolo26n-obb.dxnn | 7.5 MB |
| 4 | Pose Estimation | yolov8s_pose.dxnn | 25 MB |
| 5 | Hand Landmark | HandLandmarkLite_1.dxnn | 2.5 MB |
| 6 | Face Alignment | 3ddfa_v2_mobilnetv1_120x120.dxnn | 6.5 MB |
| 7 | Instance Segmentation | yolov8n_seg.dxnn | 8.9 MB |
| 8 | Semantic Segmentation | DeepLabV3PlusMobilenet.dxnn | 13 MB |
| 9 | Classification | ResNet50.dxnn | 50 MB |
| 10 | Depth Estimation | scdepthv3.dxnn | 29 MB |
| 11 | Image Denoising | DnCNN_50.dxnn | 4.1 MB |
| 12 | Super Resolution | ESPCN_X4.dxnn | 83 KB |
| 13 | Image Enhancement | zero_dce.dxnn | 9.7 MB |
| 14 | Embedding | arcface_mobilefacenet.dxnn | 29 MB |
| 15 | Attribute Recognition | deepmar_resnet50.dxnn | 46 MB |
| 16 | Person Re-ID | casvit_t.dxnn | 82 MB |
| 17 | PPU Pipeline | YoloV7_PPU.dxnn | 74 MB |

### Sync vs Async 실행 패러다임
- **Synchronous (`*_sync`)**: 순차 실행 (Input → Inference → Output). 디버깅/단일 이미지에 적합.
- **Asynchronous (`*_async`)**: `RunAsync()` API로 파이프라인 스테이지 오버랩. NPU가 Frame N 추론 중 CPU가 Frame N+1 전처리 + Frame N-1 후처리 동시 수행. **실시간 비디오에 필수.**

### Python 4가지 변형
| 변형 | Post-process | 실행 | 용도 |
|------|-------------|------|------|
| `*_sync.py` | Pure Python | 동기 | 학습/디버깅 |
| `*_async.py` | Pure Python | 비동기 | 기본 성능 최적화 |
| `*_sync_cpp_postprocess.py` | C++ Binding | 동기 | CPU 병목 해소 |
| `*_async_cpp_postprocess.py` | C++ Binding | 비동기 | **최대 FPS (권장)** |

### 고급 기능
- **Multi-Model**: 여러 모델 순차/병렬 실행
- **Pipeline/Cascade**: 모델 체이닝 (예: 얼굴 감지 → 얼굴 인식)
- **ROI Crop**: 관심 영역만 잘라서 추론
- **Auto-Download**: 모델/비디오 파일 없으면 자동 다운로드 시도
- **Headless Mode**: DISPLAY 없으면 자동으로 cv2.imshow() 스킵
- **Signal Handling**: Ctrl+C로 안전 종료, 리소스 해제
- **Tensor Dump** (`--dump-tensors`): 디버깅용 raw 텐서 덤프

## [section:model,network,weights,모델] 모델 관리

### 모델 레지스트리 (`config/model_registry.json`)
- **Single Source of Truth**: 전체 모델 메타데이터 관리
- 디렉터리 스캔으로 모델 자동 발견 (`config.json` + `.dxnn` 바이너리)
- 핫 리로드: 새 모델 추가 시 서버 재시작 불필요
- 모델별: NPU 코어 수, 데이터셋, 입력 해상도, score/NMS threshold

### 지원 카테고리 (17+)
| 카테고리 | 대표 모델 |
|----------|-----------|
| object_detection | YOLOv3~v12, YOLOX, NanoDet, SSD, DAMO-YOLO, EfficientDet |
| classification | EfficientNet (Lite/V2), ResNet/ResNeXt, MobileNet, ViT/DeiT, FastViT |
| face_detection | SCRFD, RetinaFace, ULFGED, YOLOv5/v7Face |
| face_recognition | ArcFace (IResNet50/100, MobileFaceNet, R50) |
| face_landmark | TDDFA v2 (MobileNet variants) |
| face_attribute | FaceAttrResNetV1-18 |
| pose_estimation | YOLOv8-Pose, CenterPose, YOLO26-Pose |
| hand_landmark | MediaPipeHandsLite |
| semantic_segmentation | DeepLabV3/V3+, SegFormer, BiSeNet, UNet |
| instance_segmentation | YOLACT, YOLOv5/v8/YOLO26-Seg |
| depth_estimation | FastDepth, SCDepthV3 |
| super_resolution | ESPCN (x2/x3/x4) |
| image_denoising | DnCNN variants |
| image_enhancement | ZeroDCE |
| obb_detection | YOLO26-OBB |
| embedding | ArcFace |
| person_attribute | DeepMAR (ResNet18/50) |
| reid | CasViT, OSNet |
| ppu | PPU 파이프라인 (YOLOv7-PPU 등) |

### 모델 다운로드 (`setup.sh`)
```bash
./setup.sh                      # 인터랙티브 메뉴
./setup.sh --all                # 전체 모델 자동 다운로드
./setup.sh --category face_detection  # 특정 카테고리만
./setup.sh --models SCRFD500M YOLOV11N  # 특정 모델만
./setup.sh --dry-run            # 다운로드 없이 미리보기
./setup.sh --list               # 사용 가능한 모델 목록
```

| 옵션 | 설명 |
|------|------|
| `--all` | 전체 다운로드 (비인터랙티브) |
| `--workers=<N>` | 병렬 다운로드 (기본: 4) |
| `--category=<name>` | 특정 카테고리만 |
| `--models <m1> [m2...]` | 특정 모델만 |
| `--force` | 기존 파일 덮어쓰기 |

## [section:compile,build,onnx,dxnn,컴파일] ONNX 컴파일

DX App 내장 컴파일 기능 (DX-COM 연동):

1. **ONNX 업로드**: 웹 UI에서 `.onnx` 파일 업로드
2. **그래프 분석**: ONNX Inspector로 입력/출력 Shape, Opset 확인
3. **컴파일 옵션**: 최적화 레벨 (0~3), Aggressive Partitioning
4. **컴파일 실행**: ONNX → `.dxnn` 변환
5. **테스트 위자드**: Preprocessor + Postprocessor 조합 테스트
6. **Quick Deploy**: 컴파일 결과를 모델 레지스트리에 즉시 등록
7. **DX-TRON**: 웹 기반 그래프 시각화 (NPU/CPU 파티션 컬러 코딩)

## [section:hardware,npu,device,하드웨어] NPU 하드웨어 모니터링

### 실시간 모니터링 항목
| 항목 | 단위 | 설명 |
|------|------|------|
| 온도 | °C | NPU 다이 온도 (코어별, 최대 4코어) |
| 전압 | mV | NPU 공급 전압 |
| 클럭 | MHz | NPU 동작 주파수 |
| DRAM | MB | NPU 전용 메모리 사용량 |

- SSE 스트리밍으로 60초+ 실시간 데이터 제공
- 시스템 정보: CPU 모델, 메모리, 디스크, OS, Python 버전
- NPU 미감지 시 **Mock 데이터**로 동작 (개발/데모용)

## [section:developer,개발자] 개발자 도구 & CLI

### CLI 참고 (모든 예제 공통)
| 옵션 | 설명 |
|------|------|
| `-m, --model` | .dxnn 모델 파일 경로 (없으면 자동 다운로드) |
| `-i, --image` | 이미지 파일/디렉터리 |
| `-v, --video` | 비디오 파일 |
| `-c, --camera` | 카메라 디바이스 인덱스 |
| `-r, --rtsp` | RTSP 스트림 URL |
| `-l, --loop` | 반복 횟수 |
| `--no-display` | 시각화 비활성화 |
| `--show-log` | 상세 로그 |
| `--save` | 결과 저장 |
| `--dump-tensors` | raw 텐서 덤프 |
| `--config` | 모델 config.json 경로 |

### 환경 변수
| 변수 | 설명 |
|------|------|
| `DXAPP_SAVE_IMAGE` | 파일 경로 지정 → 자동 저장 |
| `DXAPP_VERIFY` | `1` → 후처리 결과를 `logs/verify/{model}.json`에 덤프 |

### DX Tool (`scripts/dx_tool.sh`)
```bash
./scripts/dx_tool.sh run          # 인터랙티브 실행 메뉴
./scripts/dx_tool.sh bench        # 벤치마크 (성능 리포트)
./scripts/dx_tool.sh run --lang cpp --category face_detection --filter scrfd
./scripts/dx_tool.sh help         # 전체 명령어
```

### Run Directory (결과 저장)
`--save` 사용 시 타임스탬프 디렉터리 생성:
```
artifacts/cpp_example/
  {model}_sync-image-{name}-{YYYYMMDD-HHMMSS}/
    run_info.txt, output.jpg, output.mp4, dump_tensors/
```

### 모델 스캐폴딩
- 새 Task Type 용 스켈레톤 코드 자동 생성
- C++ 템플릿: Factory, Processor, Visualizer, Runner (동기/비동기)
- Python 템플릿: Postprocessor, Visualizer 모듈

## [section:install,setup,설치] 설치 및 셋업

### Quick Start (3단계)
```bash
# Step 1: 환경 설치 (하드웨어 확인 필수: dxrt-cli -s)
./install.sh --all              # Build tools, CMake, OpenCV

# Step 2: 모델/비디오 다운로드
./setup.sh                      # 인터랙티브 또는 --all

# Step 3: 빌드 & 실행
./build.sh                      # C++ 바이너리 + dx_postprocess
./run_demo.sh                   # 18개 데모 실행
```

### 빌드 옵션
```bash
./build.sh                      # 전체 빌드
./build.sh --clean              # 클린 빌드
./build.sh --target yolov9s_sync yolov9s_async  # 특정 타겟만
./build.sh --target list        # 빌드 타겟 목록
```

### 버전 호환성
- DX-RT ≥ 3.0.0 필요
- 컴파일된 모델 포맷 ≥ v7
- 호환되지 않으면 명확한 에러 메시지 출력

### 6단계 설치 마법사 (웹 UI)
| 단계 | 설명 |
|------|------|
| 1. Dependencies | 필수 패키지 설치 |
| 2. Build | 프로젝트 빌드 |
| 3. Assets | 샘플 모델/이미지 다운로드 |
| 4. Runtime | DX Runtime SDK 설치 |
| 5. Driver | NPU 리눅스 드라이버 설치 |
| 6. Compiler | DX-COM 컴파일러 설치 |

### 스토리지 제약 환경 (RPi, Edge)
| 항목 | 수량 | 크기 |
|------|------|------|
| 데모 모델 (18개) | 18 | ~470 MB |
| 전체 모델 | 280 | 수 GB |
| 샘플 비디오 | 20 | ~1.1 GB |
| 샘플 이미지 (번들) | — | ~5 MB |

**절약 전략:**
- `run_demo.sh`만 실행 → 18개 데모 모델만 자동 다운로드 (~470 MB)
- `--input 2` (이미지 모드) → 비디오 다운로드 불필요
- `./setup.sh --category "Face Detection"` → 최소 카테고리만

## [section:error,fail,bug,에러] 에러 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| "Model binary missing" | `.dxnn` 파일 없음 | `./setup.sh --models <model>` 또는 컴파일 |
| "DX-RT version < 3.0.0" | 런타임 호환 안됨 | 최신 DX-RT 설치 |
| "Model format < v7" | 모델 포맷 구식 | DX-COM 최신 버전으로 재컴파일 |
| 카메라 인식 안됨 | `/dev/video*` 없음 | 드라이버 점검, `v4l2-ctl --list-devices` |
| RTSP 연결 실패 | 네트워크/URL 오류 | URL 확인, ffmpeg 300초 타임아웃 |
| 컴파일러 미설치 | dxcom 경로 없음 | Setup → Compiler 단계 실행 |
| NPU 미감지 | 드라이버 미설치 | Setup → Driver 단계 실행 |
| 메모리 부족 | RAM/DRAM 포화 | 입력 해상도 줄이기, 불필요 프로세스 종료 |
| 추론 속도 느림 | Sync 모드 사용 중 | Async + cpp_postprocess 변형 사용 |
| 후처리 느림(Python) | Pure Python 후처리 | `*_cpp_postprocess.py` 변형으로 전환 |

## [section:speed,performance,fps,성능] 성능 분석 & 프로파일러

### Built-in Performance Profiler (모든 템플릿 내장)
추론 완료 시 콘솔에 **Performance Summary** 출력:

| 지표 | 설명 |
|------|------|
| Pre-processing | 이미지 디코딩, 리사이즈, 정규화 시간 |
| NPU Inference | DEEPX NPU 순수 실행 시간 |
| Post-processing | NMS, 박스 스케일링 등 결과 디코딩 시간 |
| Display/I/O | 렌더링 또는 저장 시간 |
| **End-to-End FPS** | 전체 시스템 처리량 |

### 활용 전략
- **병목 식별**: CPU 쪽(Pre/Post)이 느린지, NPU 쪽이 느린지 즉시 파악
- **Python → C++ Binding**: 후처리가 느리면 `dx_postprocess` 변형으로 전환
- **Sync → Async**: 정량적으로 비동기 성능 향상 측정
- **벤치마크**: `./scripts/dx_tool.sh bench --filter yolov8 --loops 5`

### Numerical Verification
```bash
DXAPP_VERIFY=1 python src/python_example/object_detection/yolov7/yolov7_sync.py --model assets/models/YoloV7.dxnn
# → logs/verify/YoloV7.json 생성
python scripts/verify_inference_output.py  # 태스크별 검증 규칙 적용
```
