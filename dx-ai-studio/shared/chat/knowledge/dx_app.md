# DX App — AI 추론 및 개발 플랫폼

## [section:overview,소개] DX App 개요

DX App (Studio 경로 `/app/`)은 DX AI Studio의 핵심 앱이자, **production-ready AI 추론 템플릿 스위트**입니다.
- NPU를 활용한 **이미지/영상/카메라/RTSP 추론** 실행
- 태스크별 모델 예제, C++/Python 듀얼 언어 지원
- **Sync/Async 실행 패러다임** — 비동기(RunAsync)로 FPS 극대화
- **Unified Post-Processing Engine** — C++ 최적화, pybind11(dx_postprocess)로 Python에서도 C++ 속도
- **개발자 도구**: 모델 스캐폴딩, Git 연동, 배포
- 상단 탭: Setup · Models · Run Inference · Run Demo · Benchmark · A/B Compare · ModelZoo · Graph Composer · Lab · Outputs · Reference
- ONNX → `.dxnn` 컴파일은 **DX Compiler** (`/compiler/`), NPU 하드웨어 모니터링은 **DX Monitor** (`/dx_monitor/`)에서 합니다

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
**Run Inference** 탭에는 **Single** / **Continuous** 두 모드가 있습니다.
1. Category → Model 선택, Code Language · Mode (Sync/Async) 선택
2. 입력 유형 선택
   - **Single**: Image (샘플 이미지 또는 **Upload image**) / Video
   - **Continuous**: Video / Camera / RTSP — 카메라 · RTSP 입력은 Continuous 모드에서만 가능 (Model Slots 최대 8개, **Start Continuous**로 시작)
3. 파라미터 조절 (Confidence, NMS threshold) — 모델의 `config.json` score_threshold / nms_threshold 로 전달
4. **Run Inference** 클릭 → 결과 이미지 + FPS/Latency 표시

### CLI 추론 (터미널)
```bash
# 가장 간단한 실행 (모델 자동 다운로드 + 기본 샘플 이미지)
python src/python_example/object_detection/yolov7/yolov7_sync.py --model assets/models/YoloV7.dxnn

# C++ 비동기 비디오 추론 (최대 FPS)
./bin/yolov9s_async -m assets/models/YoloV9S.dxnn -v assets/videos/dance-group.mov

# 결과 저장
./bin/yolov9s_sync -m assets/models/YoloV9S.dxnn -i sample/img/sample_kitchen.jpg --save
```

### 예제 폴더 모양 — 두 가지 (2026-10)
dx_app 은 두 모양 중 하나다. **per-model** 은 예제를 model 마다 한 폴더로 두고 폴더 · 파일 · binary 이름이 `.dxnn` 이름 (stem)
과 같다. **legacy** 는 model 이름 폴더다. 한 PC 에는 한 모양만 있다 — 어느 쪽인지는 prompt 의 "이 PC 의 dx_app" 사실을 따른다.
Python 예제의 입력 옵션은 `--image/-i` · `--video/-v` · `--camera/-c` · `--rtsp/-r` 이다 (`--input` 은 없다).

| | legacy | per-model |
|---|---|---|
| Python 예제 | `src/python_example/object_detection/yolo26n/yolo26n_sync.py` | `src/python_example/object_detection/yolo26/yolo26-n_640x640/yolo26-n_640x640_sync.py` |
| C++ binary | `./bin/yolo26n_sync` | `./bin/yolo26-n_640x640_sync` |
| task 폴더 | `classification` · `obb_detection` · `ppu` · `face_alignment` · `embedding` … (22) | `image_classification` · `oriented_object_detection` · `face_landmark` · `face_recognition` … (28, ppu 는 `object_detection/yolo_ppu` 등으로) |
| 새 task | — | anomaly_detection (EfficientAD · PatchCore), zero_shot_image_classification (CLIP), zero_shot_instance_segmentation (FastSAM), image_matting (PP-Matting), image_retrieval, visual_place_recognition, face_attribute |
| model 수 | 353 | 499 |

- per-model 의 `config.json` 은 중첩 spec 이고 threshold 는 `config` 안에 있다. 늘 `-m <model>.dxnn` 을 준다.
- Model Zoo **2_5_0** 의 `.dxnn` 은 container **v9** 이고 **DX-RT 3.5.0 이상**이 필요하다. DX-RT 3.4.x 는 v6–8 만 읽는다
  ("Model file format version 9 is not supported"). DX AI Studio 는 오래된 DX-RT 에서 같은 이름의 2_4_0 (v8) 을 받고,
  2_5_0 에만 있는 model 은 "Needs DX-RT 3.5" 로 표시한다.
- model 파일은 `assets/models` 다음에 suite 의 `workspace/res/models` 에서도 찾는다.

### Interactive Demo (`run_demo.sh`)
```bash
./run_demo.sh                              # 인터랙티브 메뉴 (태스크 → 모드 → 입력)
./run_demo.sh --task 0 --mode 1 --input 2  # 비인터랙티브 (0번 태스크, cpp_sync, image)
./run_demo.sh --help                       # 데모 개수 · 옵션 확인
```
- `--task NUM`: 데모 태스크 번호 (0부터)
- `--mode NUM`: 언어 + 실행 모드 (최대 6개: cpp_sync, cpp_async, py_sync, py_async, py_sync_cpp_postprocess, py_async_cpp_postprocess — 태스크에 따라 일부만)
- `--input NUM`: 1 = video, 2 = image (image-only 태스크는 자동으로 image)
- 데모 목록(태스크 · 모델 파일)은 `run_demo.sh` 안의 배열이 기준이며 버전마다 바뀝니다. 정확한 목록은 DX App의 **Run Demo** 탭(같은 `run_demo.sh`를 읽어 표시)이나 `./run_demo.sh`의 첫 메뉴에서 확인하세요.
- 없는 데모 모델은 `run_demo.sh`가 자동으로 다운로드합니다.

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

DX App에는 ONNX → `.dxnn` 컴파일 화면이 없습니다. 컴파일은 **DX Compiler** 앱 (Studio 경로 `/compiler/`)에서 합니다.
컴파일된 `.dxnn`은 DX App의 Models / Run Inference에서 실행합니다.

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

### Graph Composer 탭
- 여러 model을 하나의 graph로 연결한다: source, task별 model (설치 상태 표시, 없으면 Download), CPU op (headpose, volume), dx_app 예제 graph 13개.
- 편집할 때마다 dx_app `multi_model_graph_sync --check` 가 graph를 검사하고, 오류는 해당 node / edge 에 표시된다.
- NPU memory bar: model마다 `parse_model` 의 Total 을 더한 값과 장치 여유 메모리. 넘치면 engine 공유, buffer 수 줄이기를 제안한다.
- Run once: 이미지 / 비디오 입력, Sync / Async, 진행률, FPS, node별 시간, 결과 이미지, node별 결과, event 목록.
- Logic 블록 (`"type": "logic", "op"`, dx_app `--list-ops --json` 이 목록과 parameter schema 를 준다): filter, zone, line, count, dwell, condition (→ event), gallery, user (Studio 에서는 pass-through, export 하면 function stub). model 결과는 `"carry": "result"` edge 로 받고, zone / filter 가 넘기는 boxes 는 다른 model 에 ROI edge 로 이어진다. line / dwell 은 tracking 이 켜진 detector 가 필요하다.
- 구역 / 선: Inspector 의 "프레임 위에서 편집…" 이 입력의 첫 프레임 위에 그린다 (점 끌기, 변 가운데 점으로 추가, 구역 여러 개, 선 방향 뒤집기, 키보드 [ ] / 화살표 / Insert / Delete, Ctrl+Z 는 canvas 기록과 같다). 좌표는 기본으로 frame 대비 0..1 (normalized).
- Event: dx_app 이 stdout 에 `[EVENT] {json}` 을, `--events <file.jsonl>` 에 같은 객체를 한 줄씩 쓴다 (`frame, time, stream, node, event, track_id, data`). 실행 패널에서 node / event / track ID / 시간으로 거르고, 행을 누르면 결과 비디오가 그 시점으로 이동하며, JSONL 로 내려받는다. node 에는 event 수가 표시된다.
- Template: Logic 블록이 들어간 dx_app 예제 graph (출입 금지 구역, 선 통과 계수, 보호구 확인, 배회 감지, 인원 계수) 를 결과 그림과 함께 연다.
- Live: camera, RTSP, 반복 재생 비디오로 멈출 때까지 실행 (`--display`, 비디오는 `--loop`). Run 페이지 Live 와 같은 Xvfb 화면 경로 (별도 slot), 화면 / FPS / node별 시간 / event. 한 번에 하나, run once 나 Run 페이지 Live 와 동시에 돌지 않고, 페이지를 떠나면 멈춘다.
- Project: Studio workspace (`outputs/dx_app/graph/projects/`) 에 저장하고, 저장할 때마다 version 이 남는다. JSON export / import.
- C++ project export: 상단의 "C++ 프로젝트 내보내기" 가 dx_app `scripts/export_graph_project.py` 로 graph 를 독립 CMake 프로젝트로 만든다 (`CMakeLists.txt`, `main.cpp`, `graph.json`, 사용한 model 의 factory 만 담은 engine, `models/`, `user_logic/<name>.{hpp,cpp}` stub, `setup.sh`, `run.sh`, `README.md`). 사용자 Logic 블록은 C++ class stub 이 되고 채우기 전에는 pass-through. 필요한 것은 DEEPX runtime (dx_rt), CMake, C++17 compiler, OpenCV 4 뿐이다. model 파일은 기본으로 빠지고 ("모델 파일 포함" 을 고르면 들어감, 모든 model 이 설치돼 있을 때만 가능), 빠진 model 은 `./setup.sh` 가 Model Zoo 에서 내려받는다. `./setup.sh` 가 빌드, `./run.sh` 가 `results/` 에 결과 이미지·`events.jsonl`·`report.json` 을 쓴다. 결과는 `outputs/dx_app/graph/exports/` (최근 5개) 와 zip.

### Studio Lab 탭
- **Add Model**: category 의 기존 예제 하나(**Start from**)를 새 이름으로 복사한다 (`add_model.sh --base-model`).
  C++ / Python / 둘 다. Python 사본은 `python3 <name>_sync.py --model <내 모델>.dxnn` 으로 실행, C++ 사본은 `build.sh` 로 빌드.
- **Create Task**: 새 task type 의 skeleton 코드.
- **Experiment**: 컴파일된 `.dxnn` 을 보드에서 점검 — parse_model 로 읽기 → run_model 1회 추론 → 처리량(FPS) 측정.
- **Generated Files / Safety Center**: 변경마다 쓴 파일. 새 파일만 만든 변경은 `rollback:<이름>` 을 입력하면 되돌린다.
  기존 파일을 덮어쓴 변경은 직접 복구해야 한다.

## [section:install,setup,설치] 설치 및 셋업

### Quick Start (3단계)
```bash
# Step 1: 환경 설치 (하드웨어 확인 필수: dxrt-cli -s)
./install.sh --all              # Build tools, CMake, OpenCV

# Step 2: 모델/비디오 다운로드
./setup.sh                      # 인터랙티브 또는 --all

# Step 3: 빌드 & 실행
./build.sh                      # C++ 바이너리 + dx_postprocess
./run_demo.sh                   # 인터랙티브 데모 실행
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

### 6단계 설치 (웹 UI Setup 탭)
| 단계 | 설명 | 실행 명령 |
|------|------|-----------|
| 1. DX-APP Dependencies | C++ 빌드용 시스템 패키지 (cmake, gcc, ninja, OpenCV …) | `install.sh --all` |
| 2. DX-Runtime Dependencies | NPU runtime 용 패키지 (cmake, ONNX Runtime …) | `dx_rt/install.sh --all` |
| 3. DX-Runtime Build | DX-RT 빌드 + `dx_engine` Python API를 venv-dx-runtime에 설치 | `dx-runtime/install.sh --target=dx_rt` |
| 4. NPU Linux Driver | DEEPX NPU 커널 드라이버 설치 (sudo 필요) | `dx-runtime/install.sh --target=dx_rt_npu_linux_driver` |
| 5. DX-APP Build | C++ 데모 바이너리 빌드 | `build.sh --type Release` |
| 6. Sample Assets Setup | Run / Benchmark 용 샘플 모델 · 비디오 다운로드 | `setup.sh` |

- **Set up the rest**: 남은 단계를 순서대로 실행 (이미 끝난 단계는 그대로 둠)
- **Demo Quick Start** (**Start Demo Setup**): 데모에 필요한 것만 한 번에 설치
- **Deep Diagnostics** (**Run Diagnostics**): PCIe link, 커널 모듈, DKMS, 서비스, CLI 도구, Python venv, 디스크, 메모리, 모델 무결성 점검
- DX-COM 컴파일러 설치 단계는 없습니다 (컴파일은 DX Compiler 앱)

### 스토리지 제약 환경 (RPi, Edge)
| 항목 | 수량 | 크기 |
|------|------|------|
| 전체 모델 | 약 500 | 수 GB |
| 샘플 비디오 | 20 | ~1.1 GB |
| 샘플 이미지 (번들) | — | ~5 MB |

**절약 전략:**
- `run_demo.sh`만 실행 → 없는 데모 모델만 자동 다운로드
- `./setup.sh --demo-models` → `run_demo.sh`가 쓰는 모델만 다운로드
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
| NPU 미감지 | 드라이버 미설치 | Setup → NPU Linux Driver 단계 실행 |
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
```
