# 설치 가이드

DX-All-Suite은 DEEPX 디바이스를 검증하고 활용하기 위한 환경을 구축하는 도구입니다. DX-All-Suite은 통합 환경을 설정하기 위한 다음의 방법들을 제공합니다:

**로컬 머신에 설치** - 호스트 환경에 직접 DX-All-Suite 환경을 구축합니다 (각 개별 도구 간의 호환성을 유지함).

**Docker 이미지 빌드 및 컨테이너 실행** - Docker 환경 내에서 DX-All-Suite 환경을 빌드하거나, 미리 빌드된 이미지를 로드하여 컨테이너를 생성합니다.

## Preparation

### 메인 리포지토리 클론

```bash
git clone --recurse-submodules https://github.com/DEEPX-AI/dx-all-suite.git
```

또는

```bash
git clone --recurse-submodules git@github.com:DEEPX-AI/dx-all-suite.git
```

#### (선택) 이미 클론된 리포지토리에서 서브모듈 초기화 및 업데이트

```bash
git submodule update --init --recursive
```

### 서브모듈 상태 확인

```bash
git submodule status
```

#### (선택) Docker 및 Docker Compose 설치

```bash
./scripts/install_docker.sh
```

#### (선택) Python 및 Python 가상 환경 설치

설치 스크립트가 자동으로 Python 버전을 감지하고, 필요한 경우 호환 가능한 Python을 설치하며, 가상 환경을 생성하고 활성화합니다. Python이나 가상 환경을 수동으로 설정할 필요 없이, 설치 스크립트를 실행하면 모든 것을 자동으로 처리합니다.

Python이 시스템에 설치되어 있지 않은 경우, 미리 설치해두면 빌드 시간을 줄일 수 있습니다:

```bash
sudo apt install python3 python3-dev python3-venv
```

---

## 로컬 설치

### DX-Compiler 환경 설치 (dx_com, dx_tron)

`DX-Compiler` 환경은 사전 빌드된 바이너리를 제공하며, 소스 코드는 포함되지 않습니다. 각 모듈은 원격 서버에서 다운로드하여 설치할 수 있습니다.

```bash
./dx-compiler/install.sh
```

#### Python 버전 호환성

`dx_com` 설치는 Python을 필요로 합니다.

설치 스크립트는 Python 버전 호환성을 자동으로 확인합니다. 지원되는 Python 버전은 `3.8`, `3.9`, `3.10`, `3.11`, `3.12`입니다.

현재 시스템의 Python 버전이 호환되지 않는 경우, 스크립트가 이를 감지하고 사용자에게 호환 가능한 Python 버전을 설치할 것인지 묻습니다. `--python_version` 옵션을 사용하여 특정 Python 버전을 지정할 수도 있습니다:

```bash
./dx-compiler/install.sh --python_version=3.11
```

#### 설치 모드

설치 스크립트는 Python wheel 패키지를 가상 환경에 다운로드하고 설치하며, Python 버전에 맞는 패키지를 자동으로 선택합니다.

가상 환경을 활성화한 후 `dxcom` 명령어를 사용하세요.

성공적으로 설치되면:

1.  `dx_com` 모듈이 다운로드 및 설치됩니다:
    - Python wheel 패키지가 가상 환경에 설치됩니다

2.  심볼릭 링크가 `./dx-compiler/dx_com`에 생성됩니다.

3.  **샘플 데이터가 자동으로 다운로드**됩니다 (`./dx-compiler/dx_com/`):
    - `sample_models/` — 샘플 ONNX 모델 및 JSON 설정 파일 (`YOLOV5S-1`, `YOLOV5S_Face-1`, `MobileNetV2-1`)
    - `calibration_dataset/` — 양자화(Quantization)용 캘리브레이션 이미지

    > 자동 다운로드가 실패하면 수동으로 실행할 수 있습니다:
    > ```bash
    > ./dx-compiler/example/1-download_sample_models.sh
    > ./dx-compiler/example/2-download_sample_calibration_dataset.sh
    > ```

#### dx_com 사용하기

가상 환경을 활성화한 후 `dxcom` 명령어를 사용할 수 있습니다:

```bash
# 가상 환경 활성화
source ./dx-compiler/venv-dx-compiler/bin/activate

# dxcom 사용
dxcom -h
```

#### 아카이브 모드 (--archive_mode=y)

`--archive_mode=y` 옵션은 주로 docker_build.sh를 사용하여 `dx-compiler` 환경에 대한 Docker 이미지를 빌드할 때 사용됩니다. 이 모드를 활성화하면, 모듈의 `.tar.gz` 파일을 다운로드하는 것까지만 진행되고 압축 해제 및 심볼릭 링크 생성은 수행되지 않습니다.

```bash
./dx-compiler/install.sh --archive_mode=y
```

위 명령을 실행하면, 모듈 아카이브 파일(`*.tar.gz`)이 아래 경로에 다운로드 및 저장됩니다:

archives/dx_com_M1_v[VERSION].tar.gz

이 아카이브 파일들은 Docker 이미지 빌드 프로세스에서 활용될 수 있습니다.

#### DX-TRON 사용하기

`dx_tron` (DX-TRON)은 그래픽 기반 모델 컴파일러 도구입니다.

**deb(Debian Package: 기본값) 모드로 설치한 경우:**

`dxtron` 명령어를 사용할 수 있습니다:

```bash
dxtron
```

**AppImage로 실행 (GUI):**

```bash
./dx-compiler/run_dxtron_appimage.sh
```

**웹 서버로 실행:**

```bash
./dx-compiler/run_dxtron_web.sh --port=8080
```

그런 다음 브라우저에서 `http://localhost:8080`에 접속하세요.

다른 포트를 사용하려면:

```bash
./dx-compiler/run_dxtron_web.sh --port=3000
```

**(P.S.) 윈도우용 dxtron: `developer.deepx.ai`를 통해 다운로드 가능 합니다.**

---

### DX-Runtime 환경 설치

`DX-Runtime` 환경은 각 모듈의 소스 코드를 포함하며, `./dx-runtime` 디렉터리에서 Git 서브모듈(`dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, and `dx_stream`)로 관리됩니다.  
모든 모듈을 빌드 및 설치하려면 아래 명령을 실행하세요.

```bash
./dx-runtime/install.sh --all
```

이 명령어는 다음 모듈을 빌드 및 설치합니다.  
`dx_fw`, `dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, `dx_stream`

```bash
./dx-runtime/install.sh --all --exclude-fw
```

`--exclude-fw` 옵션을 사용하여 `dx_fw`를 제외하고 설치가 가능합니다.

#### 특정 모듈만 설치

특정 모듈을 지정하여 설치하려면:

```bash
./dx-runtime/install.sh --target=<module_name>
```

#### `dx_fw` (펌웨어 이미지) 업데이트

`dx_fw` 모듈은 소스 코드를 포함하지 않으며, `fw.bin` 이미지 파일을 제공합니다.  
`dxrt-cli`를 사용하여 펌웨어를 업데이트하려면:

```bash
dxrt-cli -u ./dx-runtime/dx_fw/m1/X.X.X/mdot2/fw.bin
```

또는:

```bash
./dx-runtime/install.sh --target=dx_fw
```

**펌웨어 업데이트 후에는 시스템을 완전히 종료하고 전원을 껐다가 다시 켜는 것이 권장됩니다.**

#### Sanity check

```bash
./dx-runtime/scripts/sanity_check.sh
```

이 명령어를 통해 `dx_rt`와 `dx_rt_npu_linux_driver`가 정상적으로 설치가 되었는지 체크 할 수 있습니다.

---

## Docker를 이용한 설치

### DX-Runtime 및 DX-Compiler 환경 설치

#### 참고 사항

##### 1. Docker 환경을 사용할 경우, NPU 드라이버는 반드시 호스트 시스템에 설치해야 합니다.

```bash
./dx-runtime/install.sh --target=dx_rt_npu_linux_driver
```

##### 2. 호스트 시스템에 `dx_rt`가 설치되어 있고 `service daemon`(`/usr/local/bin/dxrtd`)이 실행 중이면,

`DX-Runtime` Docker 컨테이너를 실행할 때 `Other instance of dxrtd is running` 오류가 발생하며 종료됩니다.  
 컨테이너 실행 전에 호스트에서 서비스 데몬을 중지하세요.

##### 3. 만약 다른 컨테이너에서 이미 `서비스 데몬`(`/usr/local/bin/dxrtd`)이 실행 중이라면, 새로운 컨테이너를 실행하더라도 동일한 오류가 발생합니다.

여러 개의 DX-Runtime 컨테이너를 동시에 실행하려면, [#4](#4-컨테이너-내부가-아닌-호스트에서-실행-중인-서비스-데몬을-그대로-사용하고자-하는-경우)를 참고하세요.

##### 4. 컨테이너 내부가 아닌 호스트에서 실행 중인 `dxrtd`(서비스 데몬)을 그대로 사용하고자 하는 경우,

다음 두 가지 방법 중 하나로 설정할 수 있습니다:

###### 해결 방법 1: Docker 이미지 빌드 단계에서 수정

`docker/Dockerfile.dx-runtime` 파일을 아래와 같이 수정합니다:

- 변경 전:

```Dockerfile
...
ENTRYPOINT [ "/usr/local/bin/dxrtd" ]
# ENTRYPOINT ["tail", "-f", "/dev/null"]
```

- 변경 후:

```Dockerfile
...
# ENTRYPOINT [ "/usr/local/bin/dxrtd" ]
ENTRYPOINT ["tail", "-f", "/dev/null"]
```

###### 해결 방법 2: Docker 컨테이너 실행 단계에서 수정

`docker/docker-compose.yml` 파일을 아래와 같이 수정합니다:

- 변경 전:

```bash
  ...
  dx-runtime:
    container_name: dx-runtime-${UBUNTU_VERSION}
    image: dx-runtime:${UBUNTU_VERSION}
    ...
    restart: on-failure
    devices:
      - "/dev:/dev"                           # NPU / GPU / USB CAM
```

- 변경 후:

```bash
  ...
  dx-runtime:
    container_name: dx-runtime-${UBUNTU_VERSION}
    image: dx-runtime:${UBUNTU_VERSION}
    ...
    restart: on-failure
    devices:
      - "/dev:/dev"                           # NPU / GPU / USB CAM

    entrypoint: ["/bin/sh", "-c"]             # 추가됨
    command: ["sleep infinity"]               # 추가됨
```

#### Docker 이미지 빌드

```bash
./docker_build.sh --all --ubuntu_version=24.04
```

위 명령어는 `dx-compiler`, `dx-runtime` 및 `dx-modelzoo` 환경이 포함된 Docker 이미지를 빌드합니다.  
빌드된 이미지는 아래 명령어로 확인할 수 있습니다.

```bash
docker images
```

```
REPOSITORY         TAG       IMAGE ID       CREATED         SIZE
dx-runtime         24.04     05127c0813dc   41 hours ago    4.8GB
dx-compiler        24.04     b08c7e39e89f   42 hours ago    7.08GB
dx-modelzoo        24.04     cb2a92323b41   2 weeks ago     2.11GB
```

##### 특정 환경만 빌드

```bash
./docker_build.sh --target=dx-runtime --ubuntu_version=24.04
```

```bash
./docker_build.sh --target=dx-compiler --ubuntu_version=24.04
```

```bash
./docker_build.sh --target=dx-modelzoo --ubuntu_version=24.04
```

`--target=<environment_name>` 옵션을 사용하여 `dx-runtime` 또는 `dx-compiler`만 빌드할 수 있습니다.

#### Docker 컨테이너 실행

**(선택) Host 환경에 이미 `dx_rt`가 설치되어 있는 경우, Docker 컨테이너 실행 전에 `dxrt` 서비스 데몬을 중지하세요.**  
(사유: Host환경 또는 특정컨테이너에 `dxrt` 서비스 데몬이 이미 실행되어 있는 경우, `dx-runtime` 컨테이너 실행이 되지 않습니다. 서비스 데몬은 Host와 컨테이너를 포함하여 1개만 실행 가능)
(#4 참고)

```
sudo systemctl stop dxrt.service
```

##### 모든 환경(`dx_compiler`, `dx_runtime` 및 `dx-modelzoo`) 포함 컨테이너 실행

```bash
./docker_run.sh --all --ubuntu_version=<ubuntu_version>
```

실행 중인 컨테이너 확인:

```bash
docker ps
```

```
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS          PORTS     NAMES
f040e793662b   dx-runtime:24.04       "/usr/local/bin/dxrtd"   33 seconds ago   Up 33 seconds             dx-runtime-24.04
e93af235ceb1   dx-modelzoo:24.04      "/bin/sh -c 'sleep i…"   42 hours ago     Up 33 seconds             dx-modelzoo-24.04
b3715d613434   dx-compiler:24.04      "tail -f /dev/null"      42 hours ago     Up 33 seconds             dx-compiler-24.04
```

##### 컨테이너 내부 접속

```bash
docker exec -it dx-runtime-<ubuntu_version> bash
```

```bash
docker exec -it dx-compiler-<ubuntu_version> bash
```

```bash
docker exec -it dx-modelzoo-<ubuntu_version> bash
```

위 명령어를 통해 `dx-compiler`, `dx-runtime` 및 `dx-modelzoo` 환경에 접속할 수 있습니다.

##### 컨테이너 내부에서 DX-Runtime 설치 확인

```bash
dxrt-cli -s
```

출력 예시:

```
DXRT v2.6.3
=======================================================
* Device 0: M1, Accelerator type
---------------------   Version   ---------------------
* RT Driver version   : v1.3.1
* PCIe Driver version : v1.2.0
-------------------------------------------------------
* FW version          : v1.6.0
--------------------- Device Info ---------------------
* Memory : LPDDR5 5800 MHz, 3.92GiB
* Board  : M.2, Rev 10.0
* PCIe   : Gen3 X4 [02:00:00]

NPU 0: voltage 750 mV, clock 1000 MHz, temperature 29'C
NPU 1: voltage 750 mV, clock 1000 MHz, temperature 28'C
NPU 2: voltage 750 mV, clock 1000 MHz, temperature 28'C
DVFS Disabled
=======================================================
```

---

## 샘플 애플리케이션 실행

### dx_app

#### 설치 경로

1. **호스트 환경에서 실행하는 경우:**
   ```bash
   cd ./dx-runtime/dx_app
   ```
2. **도커 컨테이너 내부에서 실행하는 경우:**
   ```bash
    docker exec -it dx-runtime-<ubuntu_version> bash
    cd /deepx/dx-runtime/dx_app
   ```

#### 애셋 설정 (사전 컴파일된 NPU 모델 및 샘플 입력 영상)

```bash
./setup.sh
```

#### `dx_app` C++ demo 실행

```bash
./run_demo.sh
```

#### `dx_app` python demo 실행

```bash
./run_demo_python.sh
```

**자세한 내용은 [dx-runtime/dx_app/README.md](/dx-runtime/dx_app/README.md).**

---

### dx_stream

#### 설치 경로

1. **호스트 환경에서 실행하는 경우:**
   ```bash
   cd ./dx-runtime/dx_stream
   ```
2. **도커 컨테이너 내부에서 실행하는 경우:**
   ```bash
    docker exec -it dx-runtime-<ubuntu_version> bash
    cd /deepx/dx-runtime/dx_stream
   ```

#### Assets 설정 (사전 컴파일된 NPU 모델 및 샘플 입력 영상)

```bash
./setup.sh
```

#### `dx_stream` 실행

```bash
./run_demo.sh
```

**자세한 내용은 [dx-runtime/dx_stream/README.md](/dx-runtime/dx_stream/README.md)를 참고하세요.**

---

## DX-Compiler 실행

### dx_com

#### 설치 경로

1. **호스트 환경에서 실행하는 경우:**
   ```bash
   cd ./dx-compiler/dx_com
   ```
2. **도커 컨테이너 내부에서 실행하는 경우:**
   ```bash
   docker exec -it dx-compiler-<ubuntu_version> bash
   # cd /deepx/dx-compiler/dx_com
   ```

#### 샘플 ONNX 입력을 사용하여 `dx_com` 실행

설치 시 샘플 모델이 자동으로 `./dx-compiler/dx_com/sample_models/`에 다운로드됩니다.
`./dx-compiler/dx_com/` 디렉토리 기준으로 실행합니다.

**샘플 모델 일괄 컴파일 (권장):**

```bash
../example/3-compile_sample_models.sh
```

**개별 모델 수동 컴파일:**

```bash
# 가상 환경 활성화
source ./dx-compiler/venv-dx-compiler/bin/activate

cd ./dx-compiler/dx_com

dxcom \
        -m sample_models/onnx/YOLOV5S-1.onnx \
        -c sample_models/json/YOLOV5S-1.json \
        -o output/YOLOV5S-1
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:47<00:00, 47.66s/model ]

dxcom \
        -m sample_models/onnx/MobileNetV2-1.onnx \
        -c sample_models/json/MobileNetV2-1.json \
        -o output/MobileNetV2-1
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:06<00:00,  7.00s/model ]
```

**자세한 내용은 [dx-compiler/source/docs/02_02_Installation_of_DX-COM.md](/dx-compiler/source/docs/02_02_Installation_of_DX-COM.md)를 참고하세요.**
