# FAQ

## Question #1

When running the `dx-runtime` or `dx-modelzoo` container using the `docker_run.sh` script, the container stays in a **Restarting** state, and you cannot execute `docker exec -it <container-name> bash`.

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

First, check if the **dxrtd** (dx-runtime service daemon) is already running on the host system:

```bash
$ ps aux | grep dxrtd
```

```plaintext
root       60451  0.0  0.0 253648  6956 ?        Ssl  10:52   0:00 **/usr/local/bin/dxrtd**
```

If **dxrtd is already running on the host**, the attempt to run `dxrtd` inside the Docker container will fail, causing the container to enter a **restart loop**.

Check the container status with:

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

### Solution 1:

**Stop the `dxrtd` service running on the host**, then rerun the `docker_run.sh` script so that `dxrtd` runs **only inside the Docker container**.

Refer to the installation guide [Link](/docs/source/installation.md#run-the-docker-container) for more details.

```bash
sudo systemctl stop dxrt.service
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04
```

### Solution 2:

Keep `dxrtd` running **on the host**, and **prevent it from running inside the Docker container**.

Refer to this guide [Link](/docs/source/installation.md#4-if-you-prefer-to-use-the-service-daemon-running-on-the-host-system-instead-of-inside-the-container) for configuration instructions.

---

## Question #2

### Q2.1 When running `docker_run.sh`, the following warning message may appear:
```
[WARN] it is recommended to use an **X11 session (with .Xauthority support)** when working with the 'dx-all-suite' container.
```

### Q2.2 After a system reboot or session logout, the container failed to restart due to the following issue: `error mounting /tmp/.docker.xauth`.

Example error message:
```
Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: error mounting "/run/user/1000/.mutter-Xwaylandauth.N9UI62" to rootfs at "/tmp/.docker.xauth": create mountpoint for /tmp/.docker.xauth mount: cannot create subdirectories in "/var/lib/docker/overlay2/00690e188f08ad4bad24fbc8786b00653e76b44f32d9b88b1ae5ed1e2d7654c8/merged/tmp/.docker.xauth": not a directory: unknown: Are you trying to mount a directory onto a file (or vice-versa)? Check if the specified host path exists and is the expected type
Error: failed to start containers: dx-runtime-22.04
```

## Answer #2

The `dx-all-suite` Docker container uses **X11 forwarding** to display GUI windows when running sample applications or example code. For this, it relies on `xauth` to manage authentication.

However, if the user's host environment is not based on **X11 (with .Xauthority)** but instead uses **Xwayland** or similar, the `xauth` data may be lost after a system reboot or session logout. As a result, the authentication file mount between the host and the container may fail, making it impossible to restart or reuse the container.


Therefore, it is recommended to use an **X11 session (with .Xauthority support)** when working with the `dx-all-suite` container.

You can resolve this issue by setting **X11 as the default session**, as described in the instructions above.

### Set X11 as the Default Session

To make X11 the default session (and disable Wayland), modify the GDM configuration file.

#### For GNOME (Ubuntu-based systems):

1. Open the GDM configuration file with root permissions:

```bash
sudo nano /etc/gdm3/custom.conf
```

2. Find the following line and uncomment it (remove the #), or add it if it doesn't exist:

```conf
WaylandEnable=false
```
3. Save the file and exit (Ctrl+O, Enter, then Ctrl+X in nano).

4. Restart the GDM service to apply the changes:

```bash
sudo systemctl restart gdm3
```

After reboot or GDM restart, the system will use the X11 session by default instead of Wayland.

