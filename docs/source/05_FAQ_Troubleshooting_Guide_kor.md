# FAQ Troubleshooting Guide

이 가이드는 **DXNN SDK** 사용 중 발생하는 일반적인 오류와 증상을 다루며, 단계별 해결 방법을 제공합니다.  

**목차**  

- [Q1. Container 'Restarting' Error (#dxrtd-conflict)](#q1-container-restarting-error-dxrtd-conflict)  
- [Q2. X11 Session Warnings & Mount Errors (Wayland Issues)](#q2-x11-session-warnings--mount-errors-wayland-issues)  
- [Q3. Firmware Version Mismatch Error](#q3-firmware-version-mismatch-error)  
- [Q4. Device Driver Update Error](#q4-device-driver-update-error)  
- [Q5. Model-Runtime Version Compatibility Error](#q5-model-runtime-version-compatibility-error)  

---

## Q1. Container 'Restarting' Error (`dxrtd` Conflict)

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

자세한 내용은 **02. Setting Up Environment**의 [**Host System Preparation**](02_Setting_Up_Environment.md#host-system-preparation-critical) 섹션을 참조하십시오.  

**방법 2: 컨테이너 내 자동 실행 방지**  
호스트 서비스를 **반드시** 유지해야 하는 경우, 컨테이너 시작 시 데몬(`dxrtd`)이 자동으로 실행되지 않도록 설정하십시오.  

자세한 내용은 **02. Setting Up Environment**의 [**Docker Advanced Troubleshooting**](02_Setting_Up_Environment.md#docker-advanced-troubleshooting-multi-runtime-containers) 섹션을 참조하십시오.  

---

## Q2. X11 Session Warnings & Mount Errors (Wayland Issues)

X11 포워딩 인증이 실패하여 GUI 도구 에러가 발생하거나 컨테이너 시작이 거부되는 현상입니다.  

### 진단 단계

- **Q2.1 경고**: `[WARN] it is recommended to use an X11 session` 메시지가 나타납니다.  
- **Q2.2 오류**: 시스템 재부팅 또는 로그아웃 후 컨테이너 실행 시 `error mounting /tmp/.docker.xauth` 에러와 함께 실패합니다.  

### 원인

- **Q2.1:** **DX-TRON**과 같은 GUI 도구는 X11에 최적화되어 있습니다. Wayland 세션에서는 `xauth` 프로세스가 불안정할 수 있습니다.  
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

자세한 내용은 **02. Setting Up Environment**의 [**Docker Installation**](02_Setting_Up_Environment.md#docker-installation) 섹션을 참조하십시오.  

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

자세한 내용은 **02. Setting Up Environment**의 [**Firmware (DX-FW) Update and Activation**](02_Setting_Up_Environment.md#b-firmware-dx-fw-update-and-activation) 섹션을 참조하십시오.  

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

자세한 내용은 **02. Setting Up Environment**의 [**Module Build and Installation**](02_Setting_Up_Environment.md#a-building-and-installing-modules) 섹션을 참조하십시오.  

---

## Q5. Model-Runtime Version Compatibility Error

`.dxnn` 파일을 생성할 때 사용한 컴파일러 버전과 런타임 라이브러리 버전이 호환되지 않아 발생하는 오류입니다.  

### 진단 단계

터미널에서 다음 에러 메시지를 확인하십시오.  
```Plaintext
The model's compiler version(X.X.X) is not compatible in this RT library. 
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
각 모듈에 대한 정확한 호환 조합은 [**DXNN SDK Component Version Compatibility Matrix**](04_Version_Compatibility.md#dxnn-sdk-component-version-compatibility-matrix) 를 참조하십시오.  

Copyright © DEEPX. All rights reserved.

---
