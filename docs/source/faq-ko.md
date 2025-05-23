# FAQ

## Question #1

`dx-runtime` 또는 `dx-modelzoo` 컨테이너를 `docker_run.sh` 스크립트를 통해 실행하였으나, 컨테이너가 **계속해서 재시작(Restarting)** 상태에 머무르며 `docker exec -it <컨테이너이름> bash` 명령어를 실행할 수 없습니다.


```bash
$ ./docker_run.sh --target=dx-runtime --ubuntu_version=24.04
```

```plaintext
[INFO] UBUNTU_VERSSION(24.04) is set.
[INFO] TARGET_ENV(dx-runtime) is set.
[INFO] XDG_SESSION_TYPE: x11
Installing dx-runtime
[INFO] XAUTHORITY(/run/user/1000/gdm/Xauthority) is set
docker compose -f docker/docker-compose.yml up -d --remove-orphans dx-runtime
[+] Running 1/1
 ✔ Container dx-runtime-24.04  Started                                                                                                                                        0.1s 
```

```bash
$ docker exec -it dx-rumtime-24.04 bash
```

```plaintext
Error response from daemon: No such container: dx-rumtime-24.04
```

## Answer #1

먼저, 호스트 시스템에서 **dxrtd**(dx-runtime 서비스 데몬)가 이미 실행 중인지 확인합니다:

```bash
$ ps aux | grep dxrtd
```

```plaintext
root       60451  0.0  0.0 253648  6956 ?        Ssl  10:52   0:00 **/usr/local/bin/dxrtd**
```

호스트에서 **dxrtd가 이미 실행 중**일 경우, Docker 컨테이너 내부에서 `dxrtd` 실행이 실패하여 **컨테이너가 무한 재시작 상태**에 빠지게 됩니다.

컨테이너 상태를 확인하려면 다음 명령어를 사용합니다:

```bash
$ docker ps 
```

```plaintext
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS                           PORTS     NAMES
041b9a4933e3   dx-runtime:24.04       "/usr/local/bin/dxrtd"   18 seconds ago   **Restarting (255) 4 seconds ago**             dx-runtime-24.04
```

```bash
$ docker logs dx-runtime-24.04 
```

```plaintext
Other instance of dxrtd is running
Other instance of dxrtd is running
Other instance of dxrtd is running
Other instance of dxrtd is running
Other instance of dxrtd is running
Other instance of dxrtd is running
Other instance of dxrtd is running
Other instance of dxrtd is running
Other instance of dxrtd is running
```

### 해결방법 1.

**호스트에서 실행 중인 `dxrtd` 서비스를 중지**한 후, `docker_run.sh`를 실행하여 **Docker 컨테이너에서만 dxrtd가 실행**되도록 합니다.

자세한 내용은 설치 가이드 [Link](/docs/source/installation.md#run-the-docker-container) 섹션을 참고하세요.

```bash
sudo systemctl stop dxrt.service
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04
```

### 해결방법 2. 

**호스트에서 `dxrtd`를 유지**하고, **Docker 컨테이너 내부에서는 dxrtd를 실행하지 않도록 설정**합니다.

자세한 설정 방법은 이 가이드 [Link](/docs/source/installation.md#4-if-you-prefer-to-use-the-service-daemon-running-on-the-host-system-instead-of-inside-the-container) 섹션을 참고하세요.

---

## Question #2

### Q2.1 `docker_run.sh` 실행 시 아래와 같은 경고 메시지가 발생 됩니다.
```
[WARN] it is recommended to use an **X11 session (with .Xauthority support)** when working with the 'dx-all-suite' container.
```

### Q2.2
시스템 재부팅 또는 세션이 종료된 이후 컨테이너를 재시작이 안되는 문제(error mounting /tmp/.docker.xauth)가 발생했습니다. 

에러 메세지 예시:
```
Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/run/user/1000/.mutter-Xwaylandauth.N9UI62" to rootfs at "/tmp/.docker.xauth": create mountpoint for /tmp/.docker.xauth mount: cannot create subdirectories in "/var/lib/docker/overlay2/00690e188f08ad4bad24fbc8786b00653e76b44f32d9b88b1ae5ed1e2d7654c8/merged/tmp/.docker.xauth": not a directory: unknown: Are you trying to mount a directory onto a file (or vice-versa)? Check if the specified host path exists and is the expected type
Error: failed to start containers: dx-runtime-22.04
```

## Answer #2

`dx-all-suite` Docker 컨테이너는 샘플 애플리케이션이나 예제 코드를 실행할 때 **GUI 창을 표시하기 위해 X11 포워딩**을 사용합니다. 이를 위해 `xauth`를 활용하여 인증을 처리합니다.

하지만 사용자의 호스트 환경이 **.Xauthority 기반의 X11**이 아닌, **Xwayland**나 그와 유사한 환경인 경우, 시스템 재부팅이나 로그아웃 이후 `xauth` 데이터가 유실될 수 있습니다.  
이로 인해 호스트와 컨테이너 간의 인증 파일 마운트가 실패하여, 컨테이너를 재시작하거나 재사용하는 것이 불가능해질 수 있습니다.

따라서 `dx-all-suite` 컨테이너를 사용할 때는 **.Xauthority가 포함된 X11 세션 환경**에서 작업할 것을 권장합니다.

아래의 방법으로 **X11을 기본 세션**으로 설정하여 문제를 해결할 수 있습니다.

### X11을 기본 세션으로 설정하기

Wayland 대신 X11을 기본 세션으로 사용하려면 GDM 설정 파일을 수정합니다.

#### GNOME (Ubuntu 기반 시스템의 경우):

1. 루트 권한으로 GDM 설정 파일을 엽니다:

```bash
sudo nano /etc/gdm3/custom.conf
```

2. 다음 라인을 찾아 주석(`#`)을 제거하거나, 존재하지 않으면 추가합니다:

```conf
WaylandEnable=false
```

3. 파일을 저장하고 종료합니다 (nano 기준: `Ctrl+O`, `Enter`, `Ctrl+X`).

4. GDM 서비스를 재시작하여 설정을 적용합니다:

```bash
sudo systemctl restart gdm3
```

재부팅하거나 GDM을 재시작한 이후에는 시스템이 기본적으로 Wayland가 아닌 **X11 세션을 사용**하게 됩니다.

---

## Question #3

Example code 실행 시 아래와 같은 메시지와 함께 에러가 발생했습니다.

```
The current firmware version is X.X.X. Please update your firmware to version X.X.X or higher.
```

## Answer #3

**dx_rt**는 **dx_rt_npu_linux_driver**와 **dx_fw**에 의존성이 있으며, 현재 사용 중인 **dx_rt**를 정상적으로 사용하려면 **dx_fw**의 업데이트가 필요합니다.

[Link](/docs/source/installation.md#update-dx_fw-firmware-image)를 참고하여 **dx_fw**를 업데이트하면 문제를 해결할 수 있습니다.

---

## Question #4

Example code 실행 시 아래와 같은 메시지와 함께 에러가 발생했습니다.

```
The current device driver version is X.X.X. Please update your device driver to version X.X.X or higher.
```

## Answer #4

**dx_rt**는 **dx_rt_npu_linux_driver**와 **dx_fw**에 의존성이 있으며, 현재 사용 중인 **dx_rt**를 정상적으로 사용하려면 **dx_rt_npu_linux_driver**의 업데이트가 필요합니다.

[Link](/docs/source/installation.md#1-when-using-a-docker-environment-the-npu-driver-must-be-installed-on-the-host-system)를 참고하여 **dx_rt_npu_linux_driver**를 업데이트하면 문제를 해결할 수 있습니다.

---

## Question #5

Example code 실행 시 아래와 같은 메시지와 함께 에러가 발생했습니다.

```
The model's compiler version(X.X.X is not compatible in this RT library. Please downgrade the RT library version to X.X.X or use a model file generated with a compiler version X.X.X  or higher.
```

## Answer #5

현재 사용 중인 **dx_rt**와 모델 파일을 컴파일한 **dx_com** 버전 간에 호환성 문제가 발생한 상황입니다. 

호환 가능한 **dx_rt** 버전으로 다운그레이드하거나, 현재 사용 중인 **dx_rt**와 호환되는 **dx_com** 버전을 사용하여 모델 파일(*.dxnn)을 다시 컴파일해야 합니다.

각 모듈 간 버전 호환성은 [Link](/docs/source/version_compatibility.md)를 참고하시기 바랍니다.

