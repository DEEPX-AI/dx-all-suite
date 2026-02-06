# Getting-Started

## Overall

**🔄 Full Execution Order**

```bash
# Compiler Steps
bash compiler-1_download_onnx.sh
bash compiler-2_setup_calibration_dataset.sh
bash compiler-3_setup_output_path.sh
bash compiler-4_model_compile.sh

# Runtime Steps
bash runtime-1_setup_input_path.sh
bash runtime-2_setup_assets.sh
bash runtime-3_run_example_using_dxrt.sh
```

**📁 폴더 구조 예시 (실행 이후)**

```
getting-started/
├── calibration_dataset
├── dxnn                         # ← Model output symbolic link created by dx-compiler
├── forked_dx_app_example        # ← Example execution target (forked)
│   ├── bin
│   │   ├── efficientnet_async
│   │   └── yolov5_async
│   │   └── yolov5face_async
│   └── sample
│       └── ILSVRC2012
└── modelzoo
    ├── json
    └── onnx
```

## Preparation

### 📦 DX-AS (DEEPX All Suite) 설치

[https://github.com/DEEPX-AI/dx-all-suite](https://github.com/DEEPX-AI/dx-all-suite)를 참고하여 `DXNN® - DEEPX NPU 소프트웨어 (SDK)`를 로컬 환경 또는 도커 컨테이너 환경에 설치합니다.

1. [Local 환경에 직접 설치](installation.md#local-installation)
2. [Docker 이미지 빌드 및 컨테이너 실행 환경 구축](installation.md#installation-using-docker)

---

## 🧩 DX-Compiler: AI Model Compilation Scripts Guide

이 문서는 `compiler-1_download_onnx.sh` ~ `compiler-4_model_compile.sh` 까지 각 스크립트의 역할과 실행 순서를 설명합니다.

**🔄 실행 순서**

```bash
./getting-started/compiler-1_download_onnx.sh
./getting-started/compiler-2_setup_calibration_dataset.sh
./getting-started/compiler-3_setup_output_path.sh
./getting-started/compiler-4_model_compile.sh
```

**💡 Tip**

- `.dxnn` 파일은 `dx_com`으로 생성된 최종 실행 대상입니다.
- 각 스크립트는 독립적으로 실행할 수 있지만, 위 순서를 지켜야 전체 프로세스가 정상 동작합니다.

---

### 📁 1. compiler-1_download_onnx.sh

모델 파일(.onnx, .json)을 다운로드 받아 설정된 workspace로 연결합니다.

- **기능**: 모델 다운로드 자동화
- **설명**:
  - `modelzoo/onnx` 와 `modelzoo/json` 디렉토리에 `.onnx` 모델과 설정파일을 다운로드합니다.
  - `YOLOV5S-1`, `YOLOV5S_Face-1`, `MobileNetV2-1` 모델을 기준으로 동작합니다.
  - `--force` 옵션으로 기존 파일을 덮어쓸 수 있습니다.

#### 📌 주요 함수

- `show_help([type], [message])`

  - 잘못된 옵션 입력 시 도움말 메시지를 출력하고 종료합니다.
  - `--force`, `--help` 지원.

- `download(model_name, ext_name)`

  - 주어진 모델 이름과 확장자를 기반으로 리소스를 다운로드합니다.
  - `get_resource.sh`를 호출해 `modelzoo/{ext_name}/{model_name}.{ext_name}`에 저장.
  - workspace (`workspace/modelzoo/`)와의 심볼릭 링크 생성도 포함.

- `main()`
  - 모델 리스트와 확장자 리스트를 순회하며 `download()

---

### 📁 2. compiler-2_setup_calibration_dataset.sh

Calibration dataset 경로를 설정하고 `.json` 파일 내 경로도 덮어씌웁니다.

- **기능**: Calibration 데이터셋 설정
- **설명**:
  - 심볼릭 링크를 생성:`./calibration_dataset` → `dx_com/calibration_dataset`
  - `modelzoo/json/*.json` 내 `dataset_path` 항목을 `./calibration_dataset` 으로 강제 변경(hijack)합니다.
  - `dx_com` 내부에 포함된 샘플 calibration dataset을 사용하도록 구성되어 있습니다.

#### 📌 주요 함수

- `make_symlink_calibration_dataset()`

  - `dx_com/calibration_dataset` → `./calibration_dataset` 심볼릭 링크 생성.
  - 기존 링크가 깨져 있는 경우 재생성 처리.

- `hijack_dataset_path(model_name)`

  - `json/{model_name}.json` 내 `"dataset_path"` 값을 `./calibration_dataset` 로 강제 변경.
  - 기존 파일 백업(`.bak`) 후 `sed` 명령어로 값 수정.
  - 변경 전/후 `diff` 출력.

- `main()`
  - `make_symlink_calibration_dataset()` 실행.
  - 예시 모델 각각에 대해 `hijack_dataset_path()` 수행.

---

### 📁 3. compiler-3_setup_output_path.sh

모델 컴파일 결과물 경로(`./dxnn`)를 설정하고 심볼릭 링크를 생성합니다.

- **기능**: 컴파일된 모델 결과물 출력 경로 설정
- **설명**:
  - `./dxnn` 경로에 심볼릭 링크를 생성하여 결과물 저장 경로를 `workspace/dxnn` 으로 지정합니다.
  - Docker 컨테이너 환경과 호스트 환경을 모두 지원하며 자동으로 감지합니다.

#### 📌 주요 함수

- `setup_compiled_model_path()`
  - 컨테이너 환경인지 검사 후 결과물 위치 결정:
    - 컨테이너: `${DOCKER_VOLUME_PATH}/dxnn`
    - 호스트: `${DX_AS_PATH}/workspace/dxnn`
  - `./dxnn` 심볼릭 링크를 해당 workspace 디렉토리에 연결.
  - 기존 링크가 깨진 경우 복구 처리 포함.

---

### 📁 4. compiler-4_model_compile.sh

`.onnx` 모델을 `.dxnn` 포맷으로 컴파일합니다.

- **기능**: 모델 컴파일 실행
- **설명**:
  - `dx_com` 툴을 이용해 `.onnx` 및 `.json` 파일을 `.dxnn` 포맷으로 변환합니다.
  - 변환된 `.dxnn` 파일은 `./dxnn/` 디렉토리에 저장됩니다.

#### 📌 주요 함수

- `compile(model_name)`

  - `dx_com` 실행하여 `.onnx + .json → .dxnn` 으로 변환.
  - 결과물은 `./dxnn` 디렉토리에 저장.
  - 실패 시 종료.

- `main()`
  - 모델 리스트 순회하며 `compile()` 호출.

---

## 🧩 DX-Runtime: Application Execution Scripts Guide

이 문서는 `runtime-1_setup_input_path.sh` ~ `runtime-3_run_example_using_dxrt.sh` 스크립트의 역할과 실행 흐름을 설명합니다.  
`dx-compiler` 에서 `.dxnn` 모델을 생성한 후, 이를 실제 런타임 환경에서 실행하기 위한 예제 기반 가이드입니다.

**🔄 Runtime 실행 순서**

```bash
bash runtime-1_setup_input_path.sh
bash runtime-2_setup_assets.sh
bash runtime-3_run_example_using_dxrt.sh
```

**💡 Tip**

- `DXNN®` 모델이 `.dxnn` 형태로 정상 생성된 이후에 `runtime-*` 스크립트를 실행하세요.
- `fim` 툴은 이미지 결과 확인용 CLI 도구로, 자동 설치 루틴이 포함되어 있습니다.
- 예제 실행 전 `dx_app/setup.sh`을 통해 필요한 모델/샘플 데이터를 반드시 준비해야 합니다.

---

### 📁 1. runtime-1_setup_input_path.sh

컴파일된 `.dxnn` 모델 경로(`./dxnn`)를 런타임 실행을 위한 위치에 연결합니다.

- **기능**: 런타임용 모델 경로 설정
- **설명**:
  - `./dxnn` 심볼릭 링크를 생성해 `workspace/dxnn`을 가리키도록 설정합니다.
  - 호스트와 Docker 컨테이너 환경 모두 자동 감지 및 지원합니다.

#### 📌 주요 함수

- `setup_compiled_model_path()`
  - 컨테이너 여부를 감지해 경로를 자동 설정.
    - 컨테이너: `${DOCKER_VOLUME_PATH}/dxnn`
    - 호스트: `${DX_AS_PATH}/workspace/dxnn`
  - `./dxnn` → 해당 workspace 경로로 연결 (broken symlink도 복구 처리 포함)

---

### 📁 2. runtime-2_setup_assets.sh

실행 예제를 위한 설정 파일 및 모델 리소스를 준비합니다.

- **기능**: 실행 예제용 설정파일, 리소스 준비
- **설명**:
  - `dx_app` 및 `dx_stream`의 `setup.sh` 를 호출하여 예제 실행에 필요한 리소스를 다운로드/복사합니다.
  - 자동으로 필요한 모델, 설정파일, 샘플 이미지 등을 준비합니다.

#### 📌 주요 함수

- `setup_assets(target_path)`
  - 각 모듈 (`dx_app`, `dx_stream`)의 `setup.sh`를 실행.
  - 내부적으로 샘플 이미지, JSON 설정, 모델 등을 복사하거나 링크.

---

### 📁 3. runtime-3_run_example_using_dxrt.sh

`dx_app` 예제를 기반으로 `.dxnn` 모델을 실행하고 결과를 확인합니다.

- **기능**: 런타임 예제 실행 (Object Detection, Face Detection, Classification)
- **설명**:
  - `dx_app` 예제를 복제(fork)하여 `forked_dx_app_example` 폴더 생성
  - `.json` 설정 파일 내 모델 경로를 사용자 컴파일 결과로 hijack
  - `run_detector`, `run_classifier` 바이너리 실행
  - 이미지 결과(fim) 또는 로그 출력 확인

#### 📌 주요 함수

- `fork_examples()`

  - `dx_app/bin` 실행 바이너리 및 `example/*`, `sample/*` 리소스 전체 복사
  - Git 초기화 및 커밋으로 diff 추적 가능하게 구성

- `hijack_example(file_path, source_str, target_str, commit_msg)`

  - `.json` 설정파일 내 `"./assets/models/*.dxnn"` 경로를 실제 생성된 모델 경로로 대체
  - diff 확인

- `run_hijacked_example(exe, config, save_log)`

  - 바이너리 실행 + 결과 확인
    - Object/Face Detection: 결과 이미지 출력 후 `fim`으로 확인
    - Classification: 결과 로그 (`result-app.log`)로 출력

- `main()`
  - YOLOV5S_Face, YOLOV5S, MobileNetV2 모델 각각에 대해 fork → hijack → run 수행

---
