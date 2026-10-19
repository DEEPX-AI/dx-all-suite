# FAQ Troubleshooting Guide

이 가이드는 **DXNN SDK** 사용 중 발생하는 일반적인 오류와 증상을 다루며, 단계별 해결 방법을 제공합니다.  

**목차**  

- Q1. Container 'Restarting' Error (#dxrtd-conflict)  
- Q2. X11 Session Warnings & Mount Errors (Wayland Issues)  
- Q3. Firmware Version Mismatch Error  
- Q4. Device Driver Update Error  
- Q5. Model-Runtime Version Compatibility Error  
- Q6. Insufficient Shared Memory (shm) Error  
- Q7. DX-ModelZoo Environment Error (`dxmz` / `dx_engine` / `dx_com` Not Found)  
- Q8. DX-ModelZoo Model Download Timeout  
- Q9. DX-ModelZoo Dataset Not Found  

---

## Q1. Container 'Restarting' Error (dxrtd Conflict)

`docker_run.sh` 실행 후 컨테이너 상태가 계속 `Restarting`으로 표시되어 컨테이너에 진입할 수 없는 문제입니다.  

### 진단 단계

- **단계 1.	상태 확인**: `docker ps`를 실행하여 `STATUS`가 `Restarting (255)`로 반복 표시되는지 확인합니다.  
- **단계 2. 로그 확인**: `docker logs <container_name>`를 실행하여 "`Other instance of dxrtd is running`"이라는 메시지가 있는지 확인합니다.  

```Bash
# Check container status
docker ps

# Example Output: STATUS repeats 'Restarting (255)'
CONTAINER ID   IMAGE             COMMAND                 STATUS                          NAMES
041b9a4933e3   dx-runtime:24.04  "/usr/local/bin/dxrtd"  Restarting (255) 4 seconds ago  dx-runtime-24.04

# Check container logs 
docker logs dx-runtime-24.04 
# Output: "Other instance of dxrtd is running"
```

### 원인

DEEPX 런타임 데몬(`dxrtd`)은 **싱글톤(Singleton)**으로 설계되었습니다. 즉, 전체 시스템(호스트 + 모든 컨테이너)에서 단 하나의 인스턴스만 실행될 수 있습니다. 만약 호스트에서 `dxrtd`가 이미 실행 중이라면, 컨테이너 내부의 데몬은 초기화에 실패하고 충돌 루프(crash loop)에 빠지게 됩니다.  

### 해결 방법: 호스트 런타임 서비스(`dxrtd`) 중지

**방법 1: 호스트 서비스 중지 (권장)**  
호스트의 서비스를 중지하여 컨테이너화된 데몬이 NPU 제어권을 가질 수 있도록 합니다.  
```Bash
# Stop the host service
sudo systemctl stop dxrt.service 

# Re-run the container
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04 
```

자세한 내용은 [**Setting Up Environment**](02_Setting_Up_Environment.md)의 **Host System Preparation** 섹션을 참조하십시오.  

**방법 2: 컨테이너 내 자동 실행 방지**  
호스트 서비스를 **반드시** 유지해야 하는 경우, 컨테이너 시작 시 데몬(`dxrtd`)이 자동으로 실행되지 않도록 설정하십시오.  

자세한 내용은 [**Setting Up Environment**](02_Setting_Up_Environment.md)의 **Docker Advanced Troubleshooting (Multi-Runtime Containers)** 섹션을 참조하십시오.  

---

## Q2. X11 Session Warnings & Mount Errors (Wayland Issues)

X11 포워딩 인증이 실패하여 GUI 도구 에러가 발생하거나 컨테이너 시작이 거부되는 현상입니다.  

### 진단 단계

- **Q2.1 경고**: `[WARN] it is recommended to use an X11 session` 메시지가 나타납니다.  
- **Q2.2 오류**: 시스템 재부팅 또는 로그아웃 후 컨테이너 실행 시 `error mounting /tmp/.docker.xauth` 에러와 함께 실패합니다.  

### 원인

- **Q2.1:** GUI 애플리케이션(예: Docker 컨테이너에서 X11로 포워딩되는 창)은 X11에 최적화되어 있습니다. Wayland 세션에서는 `xauth` 프로세스가 불안정할 수 있습니다.  
- **Q2.2:** Wayland 세션이 종료되면 X 인증 데이터가 삭제되거나 디렉토리 경로가 변경되어 Docker 마운트 포인트가 무효화될 수 있습니다.  

### 해결 방법: 시스템 기본 세션을 X11로 설정

가장 확실한 해결 방법은 로그인 세션을 X11(`Xorg`)로 설정하는 것입니다. 이는 Ubuntu/GNOME 환경의 표준 절차입니다.  

**단계 1. GDM 설정 수정**   
GDM3 설정 파일을 엽니다.  
```Bash
sudo nano /etc/gdm3/custom.conf
```

`WaylandEnable=false` 부분의 주석을 해제하여 로그인 화면이 Xorg를 사용하도록 강제합니다.  
```Plaintext
# Force the login screen to use Xorg
WaylandEnable=false
```

**단계 2. 설정 적용**   
GDM을 재시작하거나 시스템을 재부팅합니다.  
```Bash
sudo systemctl restart gdm3
# Or simply reboot the PC
```

**단계 3. 리소스 정리**  
재실행 전 기존의 고립된(orphan) 컨테이너를 제거합니다.  
```Bash
# Clean up existing containers
docker compose -f docker/docker-compose.yml down --remove-orphans

# Re-run the container
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04
```

자세한 내용은 **Docker Installation** 섹션을 [**Setting Up Environment**](02_Setting_Up_Environment.md)에서 참조하십시오.  

---

## Q3. Firmware Version Mismatch Error

NPU 하드웨어의 펌웨어가 요구되는 소프트웨어 스택 버전보다 낮아 애플리케이션이 중단되는 경우입니다.  

### 진단 단계

Check the error message in your terminal.  
```Plaintext
The current firmware version is X.X.X.
Please update your firmware to version Y.Y.Y or higher.
```

### 원인

Mismatch between the installed **DX-RT** (Runtime) library and the **DX-FW** (Firmware) flashed onto the NPU. 

### 해결 방법: 펌웨어(DX-FW) 업데이트 및 콜드 부팅

**방법 1: 통합 설치 스크립트 사용 (권장)**  
통합 설정 스크립트를 사용하여 펌웨어를 업데이트합니다.  
```Bash
./dx-runtime/install.sh --target=dx_fw
```

**방법 2: 전용 CLI 도구(`dxrt-cli`) 사용**  
특정 바이너리 파일을 지정하여 수동으로 펌웨어를 업데이트합니다.  
```Bash
dxrt-cli -u ./dx-runtime/dx_fw/m1/X.X.X/mdot2/fw.bin
```

**업데이트 후 필수 조치: 콜드 부팅(Cold Booting)**  
하드웨어 로직을 완전히 초기화하고 새 펌웨어 버전이 적용되도록 하려면 다음 절차를 따르십시오.  

**옵션 1.** [권장] 콜드 부팅  
- 방법: 시스템을 완전히 종료하고, **전원 케이블을 뽑아** 잔류 전원을 모두 제거한 뒤, 다시 연결하여 전원을 켭니다.   
- 이유: NPU의 하드웨어 레벨 리셋을 보장하는 가장 확실한 방법입니다.  

**옵션 2.** 원격/SSH 환경의 경우  
- 물리적 전원 차단이 불가능한 경우(예: 원격 서버실), OS 레벨에서 `sudo reboot` 명령을 통해 시스템 재시작을 수행하십시오. 대부분의 표준적인 상황에서는 재부팅만으로도 펌웨어가 갱신됩니다.  

**최종 확인**  
재부팅 후 터미널에 다음 명령어를 입력하여 펌웨어가 성공적으로 업데이트되었는지 확인합니다.  
```Bash
dxrt-cli -s
```

자세한 내용은 **Firmware (DX-FW) Update and Activation** 섹션을 [**Setting Up Environment**](02_Setting_Up_Environment.md)에서 참조하십시오.  

---

## Q4. Device Driver Update Error

커널 드라이버 버전이 낮아 애플리케이션 실행이 중단되는 문제입니다.  

### 진단 단계

터미널에서 다음 에러 메시지를 확인하십시오.  
```Plaintext
The current device driver version is X.X.X.
Please update your device driver to version Y.Y.Y or higher.
```

### 원인

설치된 커널 드라이버(`dx_rt_npu_linux_driver`)가 현재 **DX-RT**의 최소 요구사항을 충족하지 않습니다.  

### 해결 방법: 호스트 OS에서 장치 드라이버 업데이트

이 문제를 해결하려면, **반드시** 호스트 운영 체제에서 직접 드라이버 모듈을 업데이트해야 합니다.  

**단계 1. 드라이버 모듈 설치**  
드라이버를 대상으로 설치 스크립트를 실행합니다.  
```Bash
./dx-runtime/install.sh --target=dx_rt_npu_linux_driver
```

**단계 2. 시스템 재부팅**  
드라이버를 Linux 커널에 다시 로드해야 하므로 시스템 재부팅이 필수적입니다.  
```Bash
sudo reboot
```

**단계 3. 상태 확인**  
재부팅 후 업데이트가 성공했는지 확인합니다.  
```Bash
dxrt-cli -s
```

!!! caution "Docker 사용자 주의사항"  
    Docker 컨테이너는 호스트의 커널을 공유하므로, **드라이버 업데이트는 컨테이너 내부가 아닌 반드시 호스트 OS에서 수행**해야 합니다. 컨테이너 내부에서 드라이버를 업데이트하는 것은 하드웨어 통신 계층에 아무런 영향을 주지 않습니다.  

자세한 내용은 **Building and Installing Modules** 섹션을 [**Setting Up Environment**](02_Setting_Up_Environment.md)에서 참조하십시오.  

---

## Q5. Model-Runtime Version Compatibility Error

`.dxnn` 파일을 생성할 때 사용한 컴파일러 버전과 런타임 라이브러리 버전이 호환되지 않아 발생하는 오류입니다.  

### 진단 단계

터미널에서 다음 에러 메시지를 확인하십시오.  
```Plaintext
The model's compiler version(X.X.X) is not compatible with this RT library. 
Please downgrade the RT library version to X.X.X or use a model file generated with a compiler version X.X.X or higher.
```

### 원인

**DX-COM**(컴파일러)과 **DX-RT**(런타임) 간의 버전 불일치로 인해 발생합니다.  

### 해결 방법: 재컴파일을 통한 버전 동기화

**반드시** 모델과 런타임 환경이 호환되는 버전을 사용하고 있는지 확인해야 합니다.  

**방법 1: 모델 재컴파일 (권장)**  
현재 시스템의 **DX-RT** 버전과 호환되는 컴파일러 버전을 사용하여 `.dxnn` 파일을 다시 생성하십시오. 이는 최적의 성능과 기능 지원을 보장하는 가장 안전한 방법입니다.  

**방법 2: 런타임 라이브러리 버전 조정**  
모델의 요구사항과 일치하는 버전으로 **DX-RT**를 다시 설치합니다.  

!!! note "참고"  
    이 방법을 선택할 경우, NPU 드라이버 및 펌웨어와의 호환성도 **반드시** 다시 확인해야 합니다.  

**버전 확인 가이드**  
각 모듈에 대한 정확한 호환 조합은 **DXNN SDK Version Compatibility Matrix**를 [**Version Compatibility**](04_Version_Compatibility.md)에서 참조하십시오.  

---

## Q6. Insufficient Shared Memory (shm) Error

Docker 환경에서 모델 컴파일 시 **DX-COM**의 공유 메모리 요구량이 기본 `/dev/shm` 크기를 초과할 때 발생하는 오류입니다.

### 진단 단계

터미널에서 다음 에러 메시지를 확인하십시오.
```plaintext
[ResourceError]: Insufficient shared memory (shm). Increase the available /dev/shm size (e.g. --shm-size for Docker).
```

### 원인

Docker 컨테이너의 기본 `/dev/shm` 크기는 **64 MB**입니다. **DX-COM**은 모델 컴파일 과정에서 공유 메모리를 사용합니다. 크거나 복잡한 모델을 컴파일할 때 이 기본 한도를 초과할 수 있습니다.

### 해결 방법: Docker 공유 메모리 크기 증가

**방법 1: `docker run`에 `--shm-size` 옵션 사용 (권장)**  
컨테이너 시작 시 `--shm-size` 플래그를 전달합니다. 모델 크기에 따라 값을 조정하며, `256m`부터 시작하고 대형 모델의 경우 `1g` 이상으로 늘리십시오.  
```bash
docker run --shm-size=256m ...
# 대형 모델의 경우
docker run --shm-size=1g ...
```

**방법 2: `docker-compose.yml` 수정**  
Docker Compose로 컨테이너를 관리하는 경우(예: `docker_run.sh` 사용), `dx-compiler` 서비스 정의에 `shm_size` 항목을 추가합니다.  
```yaml
services:
  dx-compiler:
    shm_size: '1gb'
```

!!! tip "적절한 크기 선택"  
    대부분의 경우 `256m`으로 해결됩니다. 대용량 모델이나 배치 처리 시 오류가 지속된다면 `1g` 이상으로 늘리십시오.

---

## Q7. DX-ModelZoo Environment Error (`dxmz` / `dx_engine` / `dx_com` Not Found)

DX-ModelZoo 명령을 필요한 패키지가 모두 설치되지 않은 Python 환경에서 실행할 때 발생하는 오류입니다.  

### 진단 단계

터미널에서 다음 메시지 중 하나를 확인하십시오.  
```Plaintext
bash: dxmz: command not found
ImportError: dx_engine is required for DxRuntimeSession. Please install the DeepX runtime package.
ImportError: dx_com is not installed. Install it to use compile: pip install dx_com
TypeError: compile() got an unexpected keyword argument 'calibration'
```

### 원인

`dxmz`, `dx_engine`(NPU 평가용 DX-RT Python API), `dx_com`(컴파일용 DX-COM)은 **반드시** 동일한 Python 환경에 설치되어야 합니다. DX-ModelZoo는 런타임 환경(`dx-runtime/venv-dx-runtime`, Docker에서는 `/venv-dxnn`)에 설치되며, `dx_com`은 기본적으로 설치되어 있지 않습니다. `compile()` 키워드 인자에서 `TypeError`가 발생하면 설치된 `dx_com`이 DX-ModelZoo가 사용하는 API보다 오래된 것이므로, `dx-compiler/compiler.properties`의 `COM_VERSION` 버전으로 `dx_com`을 재설치하십시오.  

### 해결 방법: 런타임 환경에 모든 패키지 설치

**단계 1. DX-Runtime 설치 (`dx_engine` 제공)**  
```Bash
./getting-started/runtime-0_install_dx-runtime.sh
```

**단계 2. 동일한 환경에 DX-ModelZoo 설치**  
```Bash
./getting-started/modelzoo-0_install_dx-modelzoo.sh
```

**단계 3. 컴파일용 `dx_com` 제공**  
실행 스크립트가 DX-ModelZoo의 `numpy>=1.20,<2.0` 요구 사항을 유지하면서 `pip`으로 `dx_com`을 자동 설치합니다(`dx-compiler/compiler.properties`에 고정된 버전, 실패 시 PyPI 릴리스).  
```Bash
./getting-started/modelzoo-2_run_first_npu_model.sh
```
로컬 wheel로 설치하려면 환경의 Python 버전과 일치하는 wheel을 전달하십시오 (예: Python 3.10은 `cp310`).  
```Bash
./getting-started/modelzoo-2_run_first_npu_model.sh --dx-com-wheel /path/to/dx_com-*.whl
```
NPU 평가만 필요하다면 `dx_com`은 필요하지 않습니다 — `DXMZ_MODEL_URL`에서 사전 빌드된 `.dxnn`을 다운로드합니다.  
```Bash
./getting-started/modelzoo-2_run_first_npu_model.sh --skip-onnx --skip-compile
```

**단계 4. 확인**  
```Bash
source ./dx-runtime/venv-dx-runtime/bin/activate
dxmz --help
python3 -c "import dx_engine, dx_com; print('OK')"
```

자세한 내용은 [**Setting Up Environment**](02_Setting_Up_Environment_kor.md)의 **DX-ModelZoo Installation** 섹션을 참조하십시오.  

---

## Q8. DX-ModelZoo Model Download Timeout

`dxmz eval`이 누락된 모델을 다운로드하려 할 때 연결이 완료되지 않는 문제입니다.  

### 진단 단계

- **단계 1. 로그 확인**: 다운로드 로그가 진행 없이 대기하다가 몇 분 후(서버 주소당 60초 timeout) 실패합니다.  
```Plaintext
WARNING | Model file not found locally: .../models/resnet50_224x224/resnet50_224x224.onnx
INFO    | Downloading model: https://sdk.deepx.ai/modelzoo/onnx/resnet50_224x224.onnx → ...
SessionCreationError: Failed to download model from https://sdk.deepx.ai/modelzoo/onnx/resnet50_224x224.onnx: <urlopen error ...>
```
- **단계 2. 연결 확인**: DNS는 정상이지만 443 포트 TCP 연결이 timeout 됩니다.  
```Bash
getent ahosts sdk.deepx.ai
timeout 15 nc -4 -vz -w 10 sdk.deepx.ai 443
env | grep -i proxy
```

로그에 다음이 표시되면 `DXMZ_MODEL_URL`이 설정되지 않은 것입니다 (예: `dx-modelzoo/.env` 없음).  
```Plaintext
Model file not found: .../models/resnet50_224x224/resnet50_224x224.onnx
To enable auto-download, set DXMZ_MODEL_URL environment variable.
```

### 원인

`DXMZ_MODEL_URL`로의 outbound HTTPS(TCP 443)가 방화벽, NAT 또는 프록시 미설정으로 차단된 상태입니다. 연결이 TLS 협상 **이전**에 실패하므로 인증서 문제가 아니며, `--cacert`나 CA 업데이트로 해결되지 않습니다. `dxmz compile`은 모델을 다운로드하지 않으므로, 다운로드가 완료되지 않으면 `ONNX file not found`로 실패합니다.  

### 해결 방법: 네트워크 허용 또는 모델 수동 배치

**방법 1: Outbound 허용 또는 프록시 설정 (권장)**  
`sdk.deepx.ai`로의 outbound TCP 443을 허용하거나, 스크립트 실행 전에 프록시를 설정합니다.  
```Bash
export HTTPS_PROXY=http://<proxy_host>:<port>
export HTTP_PROXY=http://<proxy_host>:<port>
```
네트워크에서 모델 미러를 제공하는 경우 `dx-modelzoo/.env`의 `DXMZ_MODEL_URL`을 설정하십시오.  

**방법 2: 모델 파일 수동 배치 (오프라인)**  
인터넷이 가능한 호스트에서 파일을 다운로드한 뒤 다음 경로로 복사합니다.  
```Plaintext
getting-started/modelzoo/models/<model>/<model>.onnx
getting-started/modelzoo/models/<model>/<model>_<profile>.dxnn
```

---

## Q9. DX-ModelZoo Dataset Not Found

모델 YAML에 정의된 데이터셋이 없거나 불완전할 때 평가 또는 컴파일(캘리브레이션) 중 발생하는 오류입니다.  

### 진단 단계

터미널에서 다음과 같은 메시지를 확인하십시오 (`resnet50_224x224`).  
```Plaintext
DatasetValidationError:
  Dataset not found: ILSVRC2012
  Expected path: .../ILSVRC2012/val
DatasetValidationError: Dataset validation failed for ILSVRC2012: Expected 50000 images in .../ILSVRC2012/val, but found 0.
```

### 원인

DX-ModelZoo는 데이터셋을 다운로드하지 않습니다. 각 모델은 평가와 캘리브레이션 모두 `dataset.eval_path`(예: `${DATA_ROOT}/ILSVRC2012/val`)를 사용하며, 데이터셋 로더가 구조를 검증합니다.  

### 해결 방법: `DATA_ROOT` 아래에 데이터셋 준비

**단계 1. 필요한 경로 확인**  
`modelzoo-2_run_first_npu_model.sh`의 `[1] Model info` 단계가 `Dataset` 경로를 보여 주고, `PATH INFO` 헤더가 `DATA_ROOT`(기본값: `getting-started/modelzoo/datasets`)를 보여 줍니다. `dxmz`를 직접 실행하면 `DATA_ROOT`는 `--data-root` 또는 `dx-modelzoo/.env`에서 결정됩니다.  

**단계 2. 데이터셋 배치**  
`resnet50_224x224`의 경우 전체 ImageNet 검증 세트(클래스 디렉토리 1,000개, JPEG 이미지 50,000장)를 `getting-started/modelzoo/datasets/ILSVRC2012/val` 아래에 배치합니다. 실행 스크립트는 항상 `--data-root getting-started/modelzoo/datasets`를 전달하므로, 기존 데이터셋을 재사용하려면 `.env`를 수정하는 대신 링크를 만드십시오.  
```Bash
ln -s /path/to/ILSVRC2012 getting-started/modelzoo/datasets/ILSVRC2012
```
`dxmz`를 직접 실행할 때는 `dx-modelzoo/.env`의 `DATA_ROOT`를 설정하거나 `--data-root`를 전달할 수도 있습니다.  

---

## Q10. 호스트 경로 재생성 후 Docker 마운트 오류

실행 중인 컨테이너에 bind mount된 호스트 경로를 삭제했다가 다시 만들었을 때 발생합니다.  

### 증상

컨테이너가 실행 중인데도 `docker exec`가 실패합니다.  
```Plaintext
Error response from daemon: mount /home/user/dx-all-suite/dummy_xauthority:/var/lib/docker/rootfs/.../dummy_xauthority, flags: 0x5000: not a directory
```

### 원인

bind mount는 컨테이너 시작 시점의 inode에 바인딩됩니다. 호스트 경로를 삭제하고 다시 생성하면(예: `workspace/` 또는 `dummy_xauthority` 삭제) 컨테이너는 이전 inode에 연결된 상태로 남아 마운트가 일치하지 않습니다. 또한 소스 경로가 없으면 Docker 데몬이 그 자리에 **디렉토리**를 생성하므로, 파일을 기대하는 경우 실패합니다(`dummy_xauthority`는 `docker_run.sh`가 생성하는 파일입니다).  

### 해결: 경로 타입 복구 후 컨테이너 재시작

**단계 1. 디렉토리로 바뀐 파일 소스 복구**  
```Bash
rmdir dummy_xauthority && touch dummy_xauthority
```

**단계 2. 마운트를 다시 생성하도록 컨테이너 재시작**  
```Bash
./docker_run.sh --target=dx-modelzoo --ubuntu_version=24.04
```

!!! note "Stale 워크스페이스 마운트"  
    `workspace/`도 동일합니다. 컨테이너 시작 이후에 재생성된 경우 호스트에서 추가한 파일이 컨테이너 내부에서 보이지 않습니다. 컨테이너를 재시작하여 마운트를 다시 연결하십시오.  

---

## Q11. NPU 디바이스 드라이버 버전이 낮은 경우

### 증상

모델 로드 직후 NPU 평가가 실패합니다.
```Plaintext
RuntimeError: Failed to create InferenceEngine for model '.../resnet50_224x224_q-lite.dxnn':
[dxrt-exception] Invalid operation exception {"The current device driver version is 2.6.0.
Please update your device driver to version 2.7.0 or higher.":lib/device_version.cpp:217:CheckVersion}
```

### 원인

컨테이너 내부의 DX-RT와 **호스트**의 NPU 디바이스 드라이버는 서로 별개의 구성 요소입니다. 드라이버는 호스트 커널 모듈이므로 Docker 이미지를 재빌드해도 DX-RT만 갱신되고 드라이버는 그대로 남습니다. 재빌드된 이미지의 DX-RT가 설치된 드라이버보다 최신이면 DX-RT가 inference engine 생성을 거부합니다.

호스트에 설치된 버전을 확인합니다.
```Bash
dxrt-cli --status | grep -A2 Version
```

### 해결 방법: 호스트 NPU 드라이버 업데이트

**Step 1. DX-AllSuite가 지정한 드라이버 버전 확인**
```Bash
git submodule status dx-runtime/dx_rt_npu_linux_driver
```

**Step 2. 지정된 드라이버를 호스트에 설치**
```Bash
./getting-started/runtime-0_install_dx-runtime.sh
```

**Step 3. 드라이버 버전 확인 후 평가 재실행**
```Bash
dxrt-cli --status | grep "RT Driver version"
```

!!! note "호스트와 컨테이너는 함께 업그레이드"
    런타임 또는 DX-ModelZoo 이미지를 재빌드할 때는 호스트 드라이버도 반드시 함께 업데이트하십시오. 컨테이너는 `/dev`를 통해 호스트 드라이버를 그대로 사용하므로, 드라이버가 오래되면 이미지 내용과 무관하게 모든 NPU 작업이 차단됩니다.

---
