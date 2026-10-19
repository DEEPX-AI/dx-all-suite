# Running Your First NPU Model

이 가이드는 모든 설치를 마친 후 **DEEPX NPU**에서 실제 AI 모델을 실행하기 위한 엔드 투 엔드(end-to-end) 실습 과정을 다룹니다. 자동화 스크립트를 순서대로 실행함으로써, 모델 컴파일부터 성공적인 추론에 이르는 전체 파이프라인을 경험할 수 있습니다.  

## Overall Pipeline

DEEPX NPU 모델 배포는 최적화(컴파일러)부터 실행(런타임)까지 구조화된 6단계 워크플로우(Step 0~5)를 따릅니다.  

| 단계 | 작업 (Task) | 관련 스크립트 | 비고 |
| :--- | :--- | :--- | :--- |
| **Step 0** | 환경 점검 | `compiler-0...sh`,<br>`runtime-0...sh` | SDK 설치 및 NPU 드라이버 확인 |
| **Step 1** | 모델 다운로드 | `compiler-1_download_onnx.sh` | 원본 훈련 모델(ONNX) 다운로드 |
| **Step 2** | 데이터 준비 | `compiler-2_setup_calibration_dataset.sh` | 양자화 최적화를 위한 참조 데이터셋 준비 |
| **Step 3** | 경로 설정 | `compiler-3_setup_output_path.sh` | 컴파일된 결과물(`.dxnn`)의 저장 경로 구성 |
| **Step 4** | NPU 컴파일 | `compiler-4_model_compile.sh` | 하드웨어에 최적화된 `.dxnn` 바이너리 생성 |
| **Step 5** | NPU 추론 | `runtime-3_run_example_using_dxrt.sh` | NPU에서 모델 실행 및 결과 검증 |

!!! note "DX-ModelZoo 경로"  
    샘플 모델 대신 사전 구성된 모델을 평가하려면(ONNX 기준 평가 → NPU 컴파일 → NPU 평가) `modelzoo-*.sh` 스크립트를 사용하십시오. 아래 **DX-ModelZoo: Model Evaluation Scripts Guide**를 참조하십시오.  

**디렉토리 구조**  
완료 시, `getting-started/` 폴더는 실제 데이터 소스에 대한 심볼릭 링크로 구성됩니다.  

```Plaintext 
getting-started/
├── calibration_dataset             # dx-compiler/dx_com/calibration_dataset
├── dxnn                            # dx-compiler/dx_com/output
├── forked_dx_app_example        	# Example execution target (forked)
│   ├── bin
│   │   ├── efficientnet_async
│   │   └── yolov5_async
│   │   └── yolov5face_async
│   └── sample
│       └── ILSVRC2012
├── modelzoo                        # workspace/modelzoo (models, datasets, result)
└── sample_models                	# dx-compiler/dx_com/sample_models
    ├── json
    └── onnx
```

**준비 사항**  
시작하기 전에 환경이 다음 기준을 충족하는지 확인하십시오.  

- **전제 조건**: DX-AllSuite 설치가 **반드시** 완전히 완료되어야 합니다.  
- **환경 선택**  
    : **Local**: 호스트 OS에 드라이버와 SDK를 직접 설치한 사용자.  
    : **Docker**: DEEPX Docker 이미지에서 제공하는 컨테이너 내부에서 작업하는 사용자.  
      팁: 모든 스크립트는 **반드시** 컨테이너 내부에서 실행되어야 합니다 (`docker exec`를 통해).  

---

## DX-Compiler: AI Model Compilation Scripts Guide (Steps 0–4)

이 섹션은 표준 AI 모델을 Step 0부터 Step 4까지의 순차적 워크플로우를 통해 NPU 전용 바이너리(`.dxnn`)로 변환하는 과정을 상세히 설명합니다.  

### A. Execution Order

스크립트는 **반드시** getting-started 디렉토리 내에서 다음 순서대로 실행되어야 합니다.  
```Bash
./getting-started/compiler-0_install_dx-compiler.sh         # Environment Setup
./getting-started/compiler-1_download_onnx.sh               # Model Acquisition
./getting-started/compiler-2_setup_calibration_dataset.sh   # Data Preparation
./getting-started/compiler-3_setup_output_path.sh           # Path Configuration
./getting-started/compiler-4_model_compile.sh               # Final Compilation
```

### B. Common Principles & Tips

모든 컴파일러 스크립트는 일관된 워크플로우를 유지하기 위해 "스마트 위임(smart delegation)" 설계를 따릅니다.  

- **로직 위임**: 실제 처리는 `dx-compiler/example/`에 위치한 원본 스크립트로 위임됩니다.  
- **환경 자동 감지**: 스크립트는 실행 환경이 **Host**인지 **Docker**인지 자동으로 식별하여 경로와 심볼릭 링크를 구성합니다.  
- **최종 자산**: 모든 단계는 NPU 추론의 필수 자산인 `.dxnn` 파일을 생성하기 위한 이정표입니다.  

### C. Detailed Script Guide

**[단계 0] `compiler-0_install_dx-compiler.sh` (패키지 설치)**  
모델 컴파일러(`dxcom`)를 위한 환경을 설정합니다.  

- **핵심 기능**:  `dx-compiler` 환경을 설치하고 빠른 상태 점검을 수행합니다.  
- **스마트 체크**: `dxcom -v`를 사용하여 기존 설치 여부를 조사합니다. 이미 설치되어 있다면 재설치를 건너뜁니다 (단, `--force` 플래그 사용 시 제외).  

**[단계 1] `compiler-1_download_onnx.sh` (모델 다운로드)**  
컴파일을 위한 샘플 모델 파일(`.onnx` 및 `.json`)을 준비합니다.  

- **지원 모델**: `YOLOV5S-1, YOLOV5S_Face-1, MobileNetV2-1`  
- **매핑**: `getting-started/sample_models`와 SDK 내부의 `dx-compiler/dx_com/sample_models` 사이에 심볼릭 링크를 생성합니다.  

**[단계 2] `compiler-2_setup_calibration_dataset.sh` (교정 데이터 설정)**  
모델 양자화 과정에서 정확도를 유지하기 위한 참조 데이터셋을 확보합니다.  

- **목적**: 대표 이미지 데이터셋을 다운로드하고 압축을 해제합니다. 이 데이터는 최적화 후에도 정확도가 높게 유지되도록 모델을 교정(calibration)하는 데 사용됩니다.  
- **결과**: 로컬의 `getting-started/calibration_dataset`을 SDK 코어와 연결합니다.  

**[단계 3] `compiler-3_setup_output_path.sh` (경로 구성)**  

| 환경 | 물리적 경로 (실제 저장소) | 논리적 경로 (접근 포인트) |
| :--- | :--- | :--- |
| **Docker** | `${DOCKER_VOLUME_PATH}/dxnn` | `getting-started/dxnn/` |
| **Local** | `${DX_AS_PATH}/workspace/dxnn` | `getting-started/dxnn/` |

!!! note "팁"  
    이 "논리적 경로" 추상화를 통해 이후의 런타임 스크립트가 서버에서 실행되든 로컬 PC에서 실행되든 상관없이 동일한 위치(`dxnn/`)에서 모델을 찾을 수 있습니다.  

**[단계 4] `compiler-4_model_compile.sh` (모델 컴파일 실행)**  
준비된 모델과 데이터를 결합하여 NPU에 최적화된 바이너리를 생성하는 최종 단계입니다.  

- **핵심 동작**: `dxcom` 엔진을 호출하여 다음과 같은 융합을 수행합니다.  
   : **ONNX** (구조) + **JSON** (설정) + **Calibration** (정밀도) = **.dxnn** (최적화된 바이너리)  
- **출력**: 생성된 `.dxnn` 파일은 `dx-compiler/dx_com/output/` 에 저장되며 `getting-started/dxnn` 링크를 통해 즉시 접근 가능합니다.  

---

## DX-Runtime: Application Execution Scripts Guide (Step 0, 5)

이 장은 최적화된 모델을 실제 DEEPX NPU 하드웨어에 배포하고 실행하는 Step 0(환경 설정)과 Step 5(추론)에 초점을 맞춥니다.  

### A. Full Execution Order

안정적인 작동을 위해 `getting-started/` 디렉토리 내에서 다음 스크립트들을 순차적으로 실행하십시오.  
```Bash
./getting-started/runtime-0_install_dx-runtime.sh # Set up environment
./getting-started/runtime-1_setup_input_path.sh # Connect model
./getting-started/runtime-2_setup_assets.sh # Prepare resources
./getting-started/runtime-3_run_example_using_dxrt.sh # Run example
```

### B. Common Principles & Tips

모든 런타임 스크립트는 원활한 배포 경험을 보장하기 위해 다음과 같은 로직으로 설계되었습니다.  

- **지능형 진단 및 복구**: 스크립트는 `sanity_check.sh`를 사용하여 NPU 드라이버와 설치 무결성을 자동으로 확인합니다. 환경이 손상된 경우 `-f` 또는 `--force`를 사용하여 다시 초기화하십시오.  
- **환경 적응형 로직**: 호스트 또는 Docker 환경에 따라 경로가 동적으로 할당됩니다. 헤드리스(TTY) 환경에서는 GUI 오류를 방지하기 위해 스크립트가 `--no-display` 플래그를 자동으로 적용합니다.  
- **리소스 위임**: 스크립트는 `dx_app/setup.sh`를 트리거하여 `forked_dx_app_example` 폴더를 필요한 바이너리 및 샘플 데이터로 자동으로 채웁니다. 
- **시각적 검증**  
   : **CLI 환경**: 결과 이미지를 터미널에서 직접 볼 수 있도록 `fim` (fbi improved) 설치 루틴을 포함합니다.  
   : **Docker 환경**: GUI 출력이 제한적이므로, `docker cp <container_id>:/path/to/result ./local_path`를 사용하여 결과를 가져올 수 있습니다.  

!!! caution "전제 조건"  
    이전 **컴파일러** 단계에서 성공적으로 `.dxnn` 파일을 **생성했어야 합니다**. 런타임 엔진은 이러한 하드웨어 최적화 바이너리 없이는 작동할 수 없습니다.  

### C. Detailed Script Guide

**[단계 0] `runtime-0_install_dx-runtime.sh` (패키지 설치)**  
DEEPX NPU 제어를 위한 핵심 소프트웨어 스택을 구축합니다.  

- **주요 기능**: 런타임 라이브러리를 설치하고 드라이버 작동을 확인합니다.  
- **최적화**: `sanity_check.sh`가 드라이버가 이미 올바르게 로드되었음을 감지하면 중복 설치 단계를 건너뜁니다.  
- **시간 절약 옵션**: 펌웨어 업데이트를 건너뛰고 소프트웨어 스택만 설치하려면 `--exclude-fw`를 사용하십시오 (펌웨어가 이미 최신 버전인 경우 유용함).  

**[단계 5를 위한 준비] `runtime-1_setup_input_path.sh` (모델 경로 동기화)**  
런타임 엔진이 컴파일 단계에서 생성된 `.dxnn` 모델을 로드할 수 있도록 경로를 동기화합니다.  

| 환경 | 물리적 경로 (실제 저장소) | 논리적 경로 (접근 포인트) |
| :--- | :--- | :--- |
| **Docker** | `${DOCKER_VOLUME_PATH}/dxnn` | `getting-started/dxnn/` |
| **Local** | `${DX_AS_PATH}/workspace/dxnn` | `getting-started/dxnn/` |

**[단계 5를 위한 준비] `runtime-2_setup_assets.sh` (리소스 준비)**  
추론 예제를 실행하는 데 필요한 의존성 파일과 샘플 데이터를 준비합니다.  

- **동작**: `dx_app` 및 `dx_stream` 디렉토리 내의 `setup.sh` 스크립트를 순차적으로 호출합니다.  
- **참고**: 이 스크립트는 각 모듈 내에서 리소스를 관리하며, `forked_dx_app_example` 폴더에 중복 복사본을 생성하지 않습니다.  

**[단계 5] `runtime-3_run_example_using_dxrt.sh` (예제 실행 및 결과 확인)**  
이 스크립트는 모델을 NPU에 로드하고, 실제 성능을 측정하며, 세 가지 핵심 작업에 대해 시각화된 출력을 생성합니다.  

| 모델 | 입력 데이터 | 작업 | 반복 횟수 |
| :--- | :--- | :--- | :--- |
| **YOLOV5S_Face-1** | `face_sample.jpg` | [1] Face Detection | 30 |
| **YOLOV5S-1** | `1.jpg` | [2] Object Detection | 300 |
| **MobileNetV2-1** | `1.jpeg` | [3] Image Classification | 300 |

- **결과 보고**: 실행이 완료되면 스크립트는 평균 **FPS** (초당 프레임 수)와 **Latency** (지연 시간, ms)를 터미널에 출력합니다.  

!!! caution "필수 확인 사항"  
    이 파이프라인은 Step 1의 세 가지 샘플 모델이 Step 4에서 성공적으로 컴파일되었음을 전제로 합니다.  
    - 모델이 누락된 경우 추론 중에 "**File Not Found**" 오류가 발생합니다.  
    - 전체 엔드 투 엔드 프로세스를 검증하기 위해 런타임 스크립트를 실행하기 전 **3개 모델 모두**를 컴파일할 것을 강력히 권장합니다.  

---

## DX-ModelZoo: Model Evaluation Scripts Guide

이 섹션은 `modelzoo-*.sh` 스크립트를 사용하여 사전 구성된 **DX-ModelZoo** 모델을 ONNX 기준 평가, NPU 컴파일, NPU 평가까지 엔드 투 엔드로 수행하는 과정을 설명합니다.  

### A. Execution Order

스크립트는 **반드시** 다음 순서대로 실행되어야 합니다. DX-ModelZoo는 DX-Runtime 환경을 재사용하므로 런타임 설치를 먼저 완료하십시오.  
```Bash
./getting-started/runtime-0_install_dx-runtime.sh          # Prerequisite: DX-Runtime environment
./getting-started/modelzoo-0_install_dx-modelzoo.sh        # Environment Setup
./getting-started/modelzoo-1_prepare_assets.sh             # Workspace & .env Configuration
./getting-started/modelzoo-2_run_first_npu_model.sh        # ONNX Eval -> Compile -> NPU Eval
```

### B. Common Principles & Tips

- **런타임 환경 공유**: DX-ModelZoo는 `dx-runtime/venv-dx-runtime`(Docker에서는 `/venv-dxnn`)에 설치되므로, `dxmz`는 `runtime-0_install_dx-runtime.sh`가 설치한 `dx_engine`을 NPU 평가에 사용합니다.  
- **환경 자동 감지**: `compiler-3_setup_output_path.sh`와 같이 **Host** 또는 **Docker** 환경을 감지하여 `getting-started/modelzoo`를 해당 워크스페이스 경로로 연결합니다.  
- **평가 후 컴파일**: `dxmz eval`은 누락된 모델을 `DXMZ_MODEL_URL`에서 다운로드하지만 `dxmz compile`은 다운로드하지 않습니다. 실행 스크립트는 ONNX 평가를 먼저 수행하여 컴파일 전에 ONNX 파일이 존재하도록 합니다.  
- **컴파일 없이 NPU 평가**: `dxmz eval --profile <c-lite|q-lite|q-pro>`도 `DXMZ_MODEL_URL`에서 사전 빌드된 `.dxnn`을 다운로드합니다. `--skip-onnx --skip-compile`을 사용하면 `dx_com`과 ONNX 기준 평가 없이 NPU 평가만 실행할 수 있습니다.  
- **`dx_com` 자동 설치**: 컴파일이 필요한데 `dx_com`이 없으면 실행 스크립트가 `pip`으로 설치합니다(`dx-compiler/compiler.properties`에 고정된 버전, 실패 시 PyPI 릴리스). `--dx-com-wheel <path>`는 로컬 wheel로 설치할 때만 사용합니다.  
- **데이터셋은 다운로드되지 않음**: 평가와 캘리브레이션은 모델 YAML에 정의된 데이터셋을 사용합니다. 실행 전에 `getting-started/modelzoo/datasets` 아래에 배치하십시오. Docker에서는 호스트의 기존 데이터셋 디렉토리를 read-only로 마운트할 수도 있습니다: `DX_DATASETS_PATH=/mnt/datasets ./docker_run.sh --target=dx-modelzoo --ubuntu_version=24.04` 실행 시 `/deepx/datasets`에 마운트됩니다. 이후 스크립트를 `DATA_ROOT=/deepx/datasets`와 함께 실행하면 `getting-started/modelzoo/datasets` 대신 마운트된 데이터셋을 사용합니다.  

!!! caution "전제 조건"  
    NPU 평가에는 정상 동작하는 DX-RT 스택(`dxrt-cli -s`)이 필요합니다. 컴파일에는 동일한 환경에 `dx_com`이 필요하며, 실행 스크립트가 자동으로 설치합니다.  

### C. Detailed Script Guide

**[단계 0] `modelzoo-0_install_dx-modelzoo.sh` (패키지 설치)**  
`dx-modelzoo` 서브모듈에서 DX-ModelZoo(`dxmz` CLI)를 설치합니다.  

- **핵심 기능**: 런타임 환경에서 `pip install -e "dx-modelzoo[cpu]"`를 실행하고 `dxmz --help`를 확인합니다.  
- **스마트 체크**: `dxmz`가 이미 동작하면 설치를 건너뜁니다 (단, `--force` 플래그 사용 시 제외).  
- **옵션**: `--extra gpu` (ONNX Runtime GPU로 전환; `onnxruntime-gpu`와 충돌하므로 `onnxruntime`은 제거됨), `--venv <path>`, `--source <path>`.  

**[단계 1] `modelzoo-1_prepare_assets.sh` (워크스페이스 구성)**  

| 환경 | 물리적 경로 (실제 저장소) | 논리적 경로 (접근 포인트) |
| :--- | :--- | :--- |
| **Docker** | `${DOCKER_VOLUME_PATH}/modelzoo` | `getting-started/modelzoo/` |
| **Local** | `${DX_AS_PATH}/workspace/modelzoo` | `getting-started/modelzoo/` |

- **구조**: 워크스페이스에 `models/`, `datasets/`, `result/`를 생성합니다.  
- **`.env` 설정**: `.env`가 없을 때만 `dx-modelzoo/.env.example`을 `dx-modelzoo/.env`로 복사합니다. 네트워크 환경에 맞게 `DXMZ_MODEL_URL`을 설정하십시오.  

**[단계 2] `modelzoo-2_run_first_npu_model.sh` (평가, 컴파일 및 NPU 실행)**  
하나의 모델(기본값: `resnet50_224x224`, 프로파일 `q-lite`)에 대해 DX-ModelZoo 전체 흐름을 실행합니다.  

| 단계 | 명령 | 결과 |
| :--- | :--- | :--- |
| [1] 모델 정보 | `dxmz info` | 입력, 프로파일, 데이터셋 경로 |
| [2] ONNX 평가 | `dxmz eval --profile onnx --save` | `result/eval_<model>_onnx.json` |
| [3] NPU 컴파일 | `dxmz compile --profile q-lite` | `models/<model>/<model>_q-lite.dxnn` |
| [4] NPU 평가 | `dxmz eval --profile q-lite --save` | `result/eval_<model>_q-lite.json` |

- **옵션**: `--model <name>`, `--profile <c-lite|q-lite|q-pro>`, `--venv <path>`, `--dx-com-wheel <path>` (pip 패키지 대신 로컬 wheel 사용), `--skip-onnx`, `--skip-compile`.  
- **단축 실행**: `--skip-onnx --skip-compile`은 `DXMZ_MODEL_URL`에서 받은 `.dxnn`으로 [4]단계만 실행합니다 — NPU 경로를 가장 빠르게 확인하는 방법입니다.  
- **결과 보고**: ONNX 및 DXNN 결과 파일의 지표(예: Top-1/Top-5)와 **FPS**를 비교하여 양자화 영향을 확인합니다.  

!!! caution "필수 확인 사항"  
    기본 모델 `resnet50_224x224`는 평가와 캘리브레이션 모두 `getting-started/modelzoo/datasets/ILSVRC2012/val`의 전체 ImageNet 검증 세트(클래스 디렉토리 1,000개, JPEG 이미지 50,000장)를 사용합니다. CPU에서 50,000장 전체 ONNX 평가는 수십 분이 소요됩니다 (테스트 환경에서 약 27 FPS, 약 35분). ONNX 파일이 이미 있으면 `--skip-onnx`로 기준 평가를 건너뛸 수 있습니다. 데이터셋 또는 모델 다운로드가 누락된 경우 [**FAQ Troubleshooting Guide**](05_FAQ_Troubleshooting_Guide_kor.md)의 **Q7–Q9**를 참조하십시오.  

---
