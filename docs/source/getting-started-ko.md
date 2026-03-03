# Getting-Started

## Overall

**🔄 Full Execution Order**

```bash
# Compiler Steps
bash compiler-0_install_dx-compiler.sh
bash compiler-1_download_onnx.sh
bash compiler-2_setup_calibration_dataset.sh
bash compiler-3_setup_output_path.sh
bash compiler-4_model_compile.sh

# Runtime Steps
bash runtime-0_install_dx-runtime.sh
bash runtime-1_setup_input_path.sh
bash runtime-2_setup_assets.sh
bash runtime-3_run_example_using_dxrt.sh
```

**📁 폴더 구조 예시 (실행 이후)**

```
getting-started/
├── calibration_dataset          # ← 심볼릭 링크 → dx-compiler/dx_com/calibration_dataset
├── dxnn                         # ← 심볼릭 링크 → dx-compiler/dx_com/output
├── forked_dx_app_example        # ← Example execution target (forked)
│   ├── bin
│   │   ├── efficientnet_async
│   │   └── yolov5_async
│   │   └── yolov5face_async
│   └── sample
│       └── ILSVRC2012
└── sample_models                # ← 심볼릭 링크 → dx-compiler/dx_com/sample_models
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

이 문서는 `compiler-0_install_dx-compiler.sh` ~ `compiler-4_model_compile.sh` 까지 각 스크립트의 역할과 실행 순서를 설명합니다.

**🔄 실행 순서**

```bash
./getting-started/compiler-0_install_dx-compiler.sh
./getting-started/compiler-1_download_onnx.sh
./getting-started/compiler-2_setup_calibration_dataset.sh
./getting-started/compiler-3_setup_output_path.sh
./getting-started/compiler-4_model_compile.sh
```

**💡 Tip**

- `.dxnn` 파일은 `dxcom`으로 생성된 최종 실행 대상입니다.
- 각 스크립트는 독립적으로 실행할 수 있지만, 위 순서를 지켜야 전체 프로세스가 정상 동작합니다.

---

### 📁 0. compiler-0_install_dx-compiler.sh

dx-compiler 패키지를 설치합니다.

- **기능**: dx-compiler 설치
- **설명**:
  - `./dx-compiler/install.sh`를 실행하여 dx-compiler 패키지를 설치합니다.
  - **`dxcom`이 이미 설치된 경우 자동으로 설치를 건너뜁니다** (`-f` 또는 `--force` 사용하지 않는 한).

#### 📌 주요 함수

- `dx-compiler` 디렉토리로 이동하여 설치 스크립트를 실행합니다.
- `dxcom -v`를 python 가상 환경 활성화와 함께 사용하여 `dxcom`이 이미 설치되었는지 확인합니다.
  - `dxcom`이 발견되면 설치를 건너뜁니다 (`-f` 또는 `--force`가 지정되지 않은 경우).
  - `dxcom`이 이미 존재하는 경우에도 재설치하려면 `-f` 또는 `--force`를 사용하세요.
- 설치 종료 코드를 확인하고 성공/실패를 보고합니다.

#### 📌 사용법

```bash
# dx-compiler 설치 (기본값)
bash compiler-0_install_dx-compiler.sh

# dxcom이 이미 설치되어 있어도 강제 재설치
bash compiler-0_install_dx-compiler.sh --force
# 또는
bash compiler-0_install_dx-compiler.sh -f
```

---

### 📁 1. compiler-1_download_onnx.sh

샘플 모델 파일(`.onnx`, `.json`)을 다운로드하고 `getting-started/`에 심볼릭 링크를 생성합니다.

- **기능**: 모델 다운로드 자동화
- **설명**:
  - `dx-compiler/example/1-download_sample_models.sh`에 위임하여 `dx-compiler/dx_com/sample_models/`에 모델을 다운로드합니다.
  - 심볼릭 링크 생성: `getting-started/sample_models` → `dx-compiler/dx_com/sample_models`.
  - 지원 모델: `YOLOV5S-1`, `YOLOV5S_Face-1`, `MobileNetV2-1`.
  - `--force` 옵션으로 기존 파일을 덮어쓸 수 있습니다.

#### 📌 주요 함수

- 다운로드 로직은 `dx-compiler/example/1-download_sample_models.sh`에 위임합니다.
- 다운로드 완료 후 `getting-started/sample_models` 심볼릭 링크를 생성합니다.

---

### 📁 2. compiler-2_setup_calibration_dataset.sh

Calibration dataset을 다운로드하고 `getting-started/`에 심볼릭 링크를 생성합니다.

- **기능**: Calibration 데이터셋 설정
- **설명**:
  - `dx-compiler/example/2-download_sample_calibration_dataset.sh`에 위임하여 `dx-compiler/dx_com/calibration_dataset/`에 데이터셋을 다운로드 및 압축 해제합니다.
  - 심볼릭 링크 생성: `getting-started/calibration_dataset` → `dx-compiler/dx_com/calibration_dataset`.
  - `--force` 옵션으로 기존 파일을 덮어쓸 수 있습니다.

#### 📌 주요 함수

- 다운로드/압축 해제 로직은 `dx-compiler/example/2-download_sample_calibration_dataset.sh`에 위임합니다.
- 다운로드 완료 후 `getting-started/calibration_dataset` 심볼릭 링크를 생성합니다.

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

샘플 `.onnx` 모델을 `.dxnn` 포맷으로 컴파일하고 출력 경로에 심볼릭 링크를 생성합니다.

- **기능**: 모델 컴파일 실행
- **설명**:
  - `dx-compiler/example/3-compile_sample_models.sh`에 위임하여 `dxcom`으로 `onnx + json → dxnn` 변환을 수행합니다.
  - 컴파일된 `.dxnn` 파일은 `dx-compiler/dx_com/output/`에 저장됩니다.
  - 심볼릭 링크 생성: `getting-started/dxnn` → `dx-compiler/dx_com/output`.

#### 📌 주요 함수

- 컴파일 로직은 `dx-compiler/example/3-compile_sample_models.sh`에 위임합니다.
- 컴파일 완료 후 `getting-started/dxnn` 심볼릭 링크를 생성합니다.

---

## 🧩 DX-Runtime: Application Execution Scripts Guide

이 문서는 `runtime-0_install_dx-runtime.sh` ~ `runtime-3_run_example_using_dxrt.sh` 스크립트의 역할과 실행 흐름을 설명합니다.
`dx-compiler` 에서 `.dxnn` 모델을 생성한 후, 이를 실제 런타임 환경에서 실행하기 위한 예제 기반 가이드입니다.

**🔄 Runtime 실행 순서**

```bash
bash runtime-0_install_dx-runtime.sh
bash runtime-1_setup_input_path.sh
bash runtime-2_setup_assets.sh
bash runtime-3_run_example_using_dxrt.sh
```

**💡 Tip**

- `DXNN®` 모델이 `.dxnn` 형태로 정상 생성된 이후에 `runtime-*` 스크립트를 실행하세요.
- `fim` 툴은 이미지 결과 확인용 CLI 도구로, 자동 설치 루틴이 포함되어 있습니다.
- 예제 실행 전 `dx_app/setup.sh`을 통해 필요한 모델/샘플 데이터를 반드시 준비해야 합니다.

---

### 📁 0. runtime-0_install_dx-runtime.sh

dx-runtime 패키지를 설치합니다.

- **기능**: dx-runtime 설치
- **설명**:
  - `./dx-runtime/install.sh --all`을 실행하여 모든 구성 요소를 포함한 dx-runtime 패키지를 설치합니다.
  - `--exclude-fw` 플래그를 지원하여 펌웨어 설치를 제외할 수 있습니다.
  - **dx-runtime이 이미 설치된 경우 자동으로 설치를 건너뜁니다** (`-f` 또는 `--force` 사용하지 않는 한).

#### 📌 주요 함수

- `dx-runtime` 디렉토리로 이동하여 설치 스크립트를 실행합니다.
- 기본적으로 `--all` 플래그와 함께 실행되어 모든 구성 요소를 설치합니다.
- `--exclude-fw` 플래그가 제공되면 펌웨어 설치를 건너뛰고 `--exclude-fw`와 함께 실행됩니다.
- `dx-runtime/scripts/sanity_check.sh`를 사용하여 dx-runtime이 이미 설치되었는지 확인합니다.
  - dx-runtime이 발견되면 설치를 건너뜁니다 (`-f` 또는 `--force`가 지정되지 않은 경우).
  - dx-runtime이 이미 존재하는 경우에도 재설치하려면 `-f` 또는 `--force`를 사용하세요.
- 설치 종료 코드를 확인하고 성공/실패를 보고합니다.

#### 📌 사용법

```bash
# 모든 구성 요소와 함께 설치 (기본값)
bash runtime-0_install_dx-runtime.sh

# 펌웨어 없이 설치
bash runtime-0_install_dx-runtime.sh --exclude-fw

# dxcom이 이미 설치되어 있어도 강제 재설치
bash runtime-0_install_dx-runtime.sh --force
# 또는
bash runtime-0_install_dx-runtime.sh -f

# 펌웨어 없이 강제 재설치
bash runtime-0_install_dx-runtime.sh --exclude-fw --force
# 또는
bash runtime-0_install_dx-runtime.sh --exclude-fw -f
```

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

`dx_app` async 예제를 사용하여 `.dxnn` 모델을 실행하고 결과를 확인합니다.

- **기능**: 런타임 예제 실행 (Object Detection, Face Detection, Image Classification)
- **설명**:
  - `dx_app` 예제 바이너리와 샘플 데이터를 `forked_dx_app_example` 폴더로 복사
  - 컴파일된 `.dxnn` 모델과 함께 `yolov5face_async`, `yolov5_async`, `efficientnet_async` 바이너리 실행
  - TTY/headless 환경을 자동으로 감지하여 디스플레이 동작 조정
  - 실행 전 모델 파일 존재 여부 검증

#### 📌 주요 함수

- `fork_examples()`

  - `dx_app/bin` 바이너리 복사: `yolov5face_async`, `yolov5_async`, `efficientnet_async`
  - 객체 감지, 얼굴 감지, 분류를 위한 샘플 이미지 복사
  - 바이너리 누락 시 `handle_cmd_failure()`를 통해 도움말 제공

- `run_example(exe_file_path, dxnn_file_path, image_path, save_log, loop)`

  - 지정된 모델과 입력 이미지로 async 바이너리 실행
  - `loop`: 추론 반복 횟수 (기본값: 300, 얼굴 감지: 30)
  - `save_log`: "y"로 설정 시 출력을 `result-app.log`로 리다이렉트
  - TTY/headless 환경(`/deepx/tty_flag` 확인)에서 자동으로 `--no-display` 플래그 추가
    - **예외**: `efficientnet_async`는 `--no-display` 옵션을 지원하지 않으므로 플래그가 추가되지 않음
  - 실패 시 오류 메시지와 함께 종료

- `show_result(result_path)`

  - 그래픽 환경: 계속 진행하도록 사용자에게 프롬프트 표시 (레거시 `fim` 뷰어 코드 비활성화)
  - TTY 환경: `docker cp`를 사용하여 결과를 복사하는 방법 안내
  - 두 환경 모두 원활하게 처리

- `main()`
  
  - 모든 `.dxnn` 모델 파일 존재 여부 검증 (`YOLOV5S_Face-1`, `YOLOV5S-1`, `MobileNetV2-1`)
  - 필요한 경우 `fim` 설치 확인 (향후 이미지 뷰어 지원용)
  - 세 가지 예제를 순차적으로 실행:
    - **YOLOV5 Face**: `face_sample.jpg`에 대해 30회 반복
    - **YOLOV5S**: `1.jpg`에 대해 300회 반복
    - **MobileNetV2**: `ILSVRC2012/1.jpeg`에 대해 300회 반복 (로그 출력)

**테스트된 모델:**
- YOLOV5S_Face-1 (얼굴 감지)
- YOLOV5S-1 (객체 감지)
- MobileNetV2-1 (이미지 분류)

---
