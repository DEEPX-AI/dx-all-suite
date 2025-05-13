# DXNN® - DEEPX NPU 소프트웨어 (DX-AS: DEEPX All Suite)

## 사전 준비

### 메인 리포지토리 클론

*temporary: need to change Github URL to cloud public repo*
```
$ git clone --recurse-submodules git@github.com:DEEPX-AI/dx-all-suite.git
```

### (선택) 이미 클론된 리포지토리에서 서브모듈 초기화 및 업데이트

```
$ git submodule update --init --recursive
```

### 서브모듈 상태 확인

```
$ git submodule status
```

### (선택) Docker 및 Docker Compose 설치

```
$ ./scripts/install_docker.sh
```

---

# 로컬 설치

## DX-Compiler 환경 설치 (dx_com, dx_simulator)

`DX-Compiler` 환경은 사전 빌드된 바이너리를 제공하며, 소스 코드는 포함되지 않습니다. 각 모듈은 원격 서버에서 다운로드하여 설치할 수 있습니다.

```
$ ./dx-compiler/install.sh
```

위 명령을 실행하면:

1. `dx-com` 및 `dx-simulator` 모듈이 아래 경로에 다운로드됩니다.  
   - `../docker_volume/release/dx_com/download/dx_com_M1A_v[VERSION].tar.gz`
   - `../docker_volume/release/dx_simulator/download/dx_simulator_v[VERSION].tar.gz`

2. 다운로드된 모듈이 아래 경로에 압축 해제됩니다.  
   - `../docker_volume/release/dx_com/dx_com_M1A_v[VERSION]`
   - `../docker_volume/release/dx_simulator/dx_simulator_v[VERSION]`  
   - 심볼릭 링크가 `./dx-compiler/dx-com` 및 `./dx-simulator`에 생성됩니다.

3. 이미 설치된 경우, `./dx-compiler/install.sh`를 다시 실행하면 기존 설치를 재사용합니다.  
   강제 재설치를 원할 경우 `--force` 옵션을 사용하세요.

   ```
   $ ./dx-compiler/install.sh --force
   ```

### 특정 버전 설치

특정 버전을 설치하려면 `install.sh` 파일에서 환경 변수를 수정하세요.

```
COM_VERSION="1.38.1"        # 기본값
SIM_VERSION="2.14.5"        # 기본값
```

또는 명령어 실행 시 버전을 직접 지정할 수도 있습니다.

```
$ ./install.sh --com_version=<version> --sim_version=<version>
```

---

## DX-Runtime 환경 설치 (`dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, and `dx_stream`)

`DX-Runtime` 환경은 각 모듈의 소스 코드를 포함하며, `./dx-runtime` 디렉터리에서 Git 서브모듈로 관리됩니다.  
모든 모듈을 빌드 및 설치하려면 아래 명령을 실행하세요.

```
$ ./dx-runtime/install.sh --all
```

이 명령어는 다음 모듈을 빌드 및 설치합니다.  
`dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, `dx_stream` (단, `dx_fw` 펌웨어 업데이트 제외)

### 특정 모듈만 설치

```
$ ./dx-runtime/install.sh --target=<module_name>
```

### `dx_fw` (펌웨어 이미지) 업데이트

`dx_fw` 모듈은 소스 코드를 포함하지 않으며, `fw.bin` 이미지 파일을 제공합니다.  
`dxrt-cli`를 사용하여 펌웨어를 업데이트하려면:

```
$ dxrt-cli -u ./dx-runtime/dx_fw/m1a/X.X.X/mdot2/fw.bin -u reset
```

또는:

```
$ ./dx-runtime/install.sh --target=dx_fw
```

**펌웨어 업데이트 후에는 시스템을 완전히 종료하고 전원을 껐다가 다시 켜는 것이 권장됩니다.**

---

# Docker를 이용한 설치

## DX-Runtime 및 DX-Compiler 환경 설치

### 참고 사항

1. Docker 환경을 사용할 경우, NPU 드라이버는 반드시 호스트 시스템에 설치해야 합니다.

   ```
   $ ./install.sh --target=dx_rt_npu_linux_driver
   ```

2. 호스트 시스템에 `dx_rt`가 설치되어 있고 `service daemon`(`/usr/local/bin/dxrtd`)이 실행 중이면,  
   `DX-Runtime` Docker 컨테이너를 실행할 때 `Other instance of dxrtd is running` 오류가 발생하며 종료됩니다.  
   컨테이너 실행 전에 호스트에서 서비스 데몬을 중지하세요.

3. 다른 컨테이너에서 `service daemon`(`/usr/local/bin/dxrtd`)이 실행 중이면, 새로운 컨테이너 실행 시 동일한 오류가 발생합니다.  
   여러 개의 DX-Runtime 컨테이너를 동시에 실행하려면 아래 #4 항목을 참고하세요.

4. 컨테이너 내부가 아닌 호스트 시스템에서 `service daemon`을 실행하려면,  
   `./docker/Dockerfile`에서 다음과 같이 수정하세요.

   ```
   # ENTRYPOINT [ "/usr/local/bin/dxrtd" ]
   ENTRYPOINT ["tail", "-f", "/dev/null"]
   ```

### Docker 이미지 빌드

```
$ ./docker_build.sh --all --ubuntu_version=24.04
```

위 명령어는 `dx-compiler` 및 `dx-runtime` 환경이 포함된 Docker 이미지를 빌드합니다.  
빌드된 이미지는 아래 명령어로 확인할 수 있습니다.

```
$ docker images
```

```
REPOSITORY               TAG       IMAGE ID       CREATED          SIZE
dx-compiler        22.04     9b7e6577c526   6 minutes ago    6.56GB
dx-runtime         22.04     1c96c081fdea   16 hours ago     4.02GB
```

#### 특정 환경만 빌드

```
$ ./docker_build.sh --target=dx-runtime --ubuntu_version=24.04
```

```
$ ./docker_build.sh --target=dx-compiler --ubuntu_version=24.04
```

`--target=<environment_name>` 옵션을 사용하여 `dx-runtime` 또는 `dx-compiler`만 빌드할 수 있습니다.

### Docker 컨테이너 실행

**(선택) Docker 컨테이너 실행 전에 `dxrt` 서비스 데몬을 중지하세요.**  
(#4 참고)

```
sudo systemctl stop dxrt.service
```

#### 모든 환경(`dx_compiler` 및 `dx_runtime`) 포함 컨테이너 실행

```
$ ./docker_run.sh --all --ubuntu_version=<ubuntu_version>
```

실행 중인 컨테이너 확인:

```
$ docker ps
```

```
CONTAINER ID   IMAGE                     COMMAND                  CREATED          STATUS          PORTS     NAMES
47837ae2aa4a   dx-runtime:24.04    "/usr/local/bin/dxrt…"   26 minutes ago   Up 26 minutes             dx-runtime-24.04
6c2b63d248d6   dx-compiler:24.04   "tail -f /dev/null s…"   26 minutes ago   Up 26 minutes             dx-compiler-24.04
```

#### 컨테이너 내부 접속

```
$ docker exec -it dx-runtime-<ubuntu_version> bash
```

```
$ docker exec -it dx-container-<ubuntu_version> bash
```

위 명령어를 통해 `dx-compiler` 및 `dx-runtime` 환경에 접속할 수 있습니다.

#### 컨테이너 내부에서 DX-Runtime 설치 확인

```
# dxrt-cli -s
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

# 샘플 애플리케이션 실행

## dx_app

### 설치 경로

1. **호스트 환경에서 실행하는 경우:**
   ```
   $ cd ./dx-runtime/dx_app
   ```
2. **도커 컨테이너 내부에서 실행하는 경우:**
   ```
    $ docker exec -it dx-runtime-<ubuntu_version> bash
    # cd /deepx/dx_app
   ```

### 애셋 설정 (사전 컴파일된 NPU 모델 및 샘플 입력 영상)

```
$ ./setup.sh
```

### `dx_app` 실행

```
$ ./scripts/run_detector.sh
$ fim ./result-app1.jpg
```

**자세한 내용은 `dx_app/README.md`를 참고하세요.**

---

## dx_stream

### 설치 경로

1. **호스트 환경에서 실행하는 경우:**
   ```
   $ cd ./dx-compiler/dx_stream
   ```
2. **도커 컨테이너 내부에서 실행하는 경우:**
   ```
    $ docker exec -it dx-runtime-<ubuntu_version> bash
    # cd /deepx/dx_stream
   ```

### Assets 설정 (사전 컴파일된 NPU 모델 및 샘플 입력 영상)

```
$ ./setup.sh
```

### `dx_stream` 실행

```
$ ./run_demo.sh
```

**자세한 내용은 `dx_stream/README.md`를 참고하세요.**

---

# DX-Compiler 실행

## dx_com

### 설치 경로

1. **호스트 환경에서 실행하는 경우:**
    ```
    $ cd ./dx-compiler/dx_com
    ```
2. **도커 컨테이너 내부에서 실행하는 경우:**
    ```
    $ docker exec -it dx-compiler-<ubuntu_version> bash
    # cd /deepx/dx_com
    ```

### 샘플 ONNX 입력을 사용하여 `dx_com` 실행

```
$ make
dx_com/dx_com \
        -m sample/MobileNetV1-1.onnx \
        -c sample/MobileNetV1-1.json \
        -o sample/MobileNetV1-1 
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:06<00:00,  7.00s/model ]

dx_com/dx_com \
        -m sample/ResNet50-1.onnx \
        -c sample/ResNet50-1.json \
        -o sample/ResNet50-1 
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:19<00:00, 19.17s/model ]

dx_com/dx_com \
        -m sample/YOLOV5-1.onnx \
        -c sample/YOLOV5-1.json \
        -o sample/YOLOV5-1 
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:47<00:00, 47.66s/model ]
```

**자세한 내용은 `dx_com/README.md`를 참고하세요.**

---

## dx_simulator

### 설치 경로

1. **호스트 환경에서 실행하는 경우:**
    ```
    $ cd ./dx-compiler/dx_simulator
    ```
2. **도커 컨테이너 내부에서 실행하는 경우:**
    ```
    $ docker exec -it dx-compiler-<ubuntu_version> bash
    (venv-dx-simulator) # cd /deepx/dx_simulator
    ```

### 필수 패키지 설치

1. **호스트 환경에서 실행하는 경우:**
    ```
    # install prerequisites, python venv and dx_simulator
    ./scripts/install.sh

    # "To activate the virtual environment, run:"
    source ${VENV_PATH}/bin/activate
    (venv-dx-simulator) $
    ```

2. **도커 컨테이너 내부에서 실행하는 경우:**
    ```
    $ docker exec -it dx-compiler-<ubuntu_version> bash
    (venv-dx-simulator) # cd /deepx/dx_simulator
    (venv-dx-simulator) # pip install /deepx/dx_simulator/dx_simulator-*-cp311-cp311-linux_x86_64.whl --force-reinstall
    (venv-dx-simulator) # pip install ultralytics
    ```

### 샘플 DXNN 입력을 사용하여 `dx_simulator` 실행

```
(venv-dx-simulator) $ python examples/example_yolov5s.py
(venv-dx-simulator) $ fim examples/yolov5s.jpg
```

**자세한 내용은 `dx_simulator/README.md`를 참고하세요.**

