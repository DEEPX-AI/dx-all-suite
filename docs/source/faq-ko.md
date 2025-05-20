# FAQ

## Question #1

### Q1.1 `docker_run.sh` 실행 시 아래와 같은 경고 메시지가 발생 됩니다.
```
[WARN] it is recommended to use an **X11 session (with .Xauthority support)** when working with the 'dx-all-suite' container.
```

### Q1.2
시스템 재부팅 또는 세션이 종료된 이후 컨테이너를 재시작이 안되는 문제(error mounting /tmp/.docker.xauth)가 발생했습니다. 

에러 메세지 예시:
```
Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/run/user/1000/.mutter-Xwaylandauth.N9UI62" to rootfs at "/tmp/.docker.xauth": create mountpoint for /tmp/.docker.xauth mount: cannot create subdirectories in "/var/lib/docker/overlay2/00690e188f08ad4bad24fbc8786b00653e76b44f32d9b88b1ae5ed1e2d7654c8/merged/tmp/.docker.xauth": not a directory: unknown: Are you trying to mount a directory onto a file (or vice-versa)? Check if the specified host path exists and is the expected type
Error: failed to start containers: dx-runtime-22.04
```

## Answer #1

`dx-all-suite`의 Docker 컨테이너는 sample application 또는 example code 실행 시 GUI를 표시하기 위해 **X11 Forwarding**을 사용하며, 이를 위해 `xauth` 기반의 인증 정보를 활용합니다.

하지만 사용자의 호스트 환경이 **X11(Xauthority 사용)** 기반이 아닌 **Xwayland** 등의 환경일 경우, 시스템 재부팅 또는 세션이 종료된 이후 `xauth` 정보가 사라지게 됩니다. 이로 인해 호스트와 컨테이너 간의 인증 파일 마운트가 실패하며, 컨테이너를 재시작하거나 재사용하는 것이 불가능해질 수 있습니다.

따라서, `dx-all-suite`를 사용하는 환경에서는 `X11 (with .Xauthority)` 기반 세션을 사용하는 것이 권장됩니다.

아래 답변을 참고하여 **X11을 default sesison으로 설정**하여 해결 할 수 있습니다. 

### Set X11 as the Default Session

To make X11 the default session (and disable Wayland), modify the GDM configuration file.

#### For GNOME (Ubuntu-based systems):

1. Open the GDM configuration file with root permissions:

   ```bash
   sudo nano /etc/gdm3/custom.conf
Find the following line and uncomment it (remove the #), or add it if it doesn't exist:

```
WaylandEnable=false
```
Save the file and exit (Ctrl+O, Enter, then Ctrl+X in nano).

Restart the GDM service to apply the changes:

```
sudo systemctl restart gdm3
```

After reboot or GDM restart, the system will use the X11 session by default instead of Wayland.
