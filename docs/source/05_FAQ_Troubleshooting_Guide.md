# FAQ Troubleshooting Guide

This guide addresses common errors and symptoms encountered while using the **DXNN SDK** and provides step-by-step solutions. 

**Table of Contents**  

- Q1. Container 'Restarting' Error (#dxrtd-conflict)  
- Q2. X11 Session Warnings & Mount Errors (Wayland Issues)  
- Q3. Firmware Version Mismatch Error  
- Q4. Device Driver Update Error  
- Q5. Model-Runtime Version Compatibility Error  
- Q6. Insufficient Shared Memory (shm) Error  
- Q7. DX-ModelZoo Environment Error (`dxmz` / `dx_engine` / `dx_com` Not Found)  
- Q8. DX-ModelZoo Model Download Timeout  
- Q9. DX-ModelZoo Dataset Not Found  
- Q10. Docker Mount Error After Recreating a Host Path
- Q11. NPU Device Driver Version Is Too Old

---

## Q1. Container 'Restarting' Error (dxrtd Conflict)

This issue occurs when the container status is continuously displayed as `Restarting` after running `docker_run.sh`, making it impossible to enter the container.  

### Diagnostic Steps

- **Step 1.	Check Status**: Run `docker ps` and check if the `STATUS` is repeatedly showing `Restarting (255)`.  
- **Step 2.	Check Logs**: Run `docker logs <container_name>` and check for the message "`Other instance of dxrtd is running`".  

```Bash
# Check container status
docker ps

# Example Output: STATUS repeats 'Restarting (255)'
CONTAINER ID   IMAGE                    COMMAND                 STATUS                          NAMES
041b9a4933e3   dx-runtime:24.04         "/usr/local/bin/dxrtd"  Restarting (255) 4 seconds ago  dx-runtime-24.04

# Check container logs 
docker logs dx-runtime-24.04 
# Output: "Other instance of dxrtd is running"
```

### Cause

The DEEPX Runtime Daemon (`dxrtd`) is designed as a **singleton**. Only one instance can run on the entire system (Host + all Containers). If `dxrtd` is already running on the host, the daemon inside the container will fail to initialize, causing a crash loop.  

### Solution: Stopping the Host Runtime Service (`dxrtd`)

**Method 1: Stop the Host Service (Recommended)**  
Stop the service on the host to allow the containerized daemon to gain control over the NPU.  
```Bash
# Stop the host service
sudo systemctl stop dxrt.service 

# Re-run the container
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04 
```

For more details, refer to the **Host System Preparation** section in [**Setting Up Environment**](02_Setting_Up_Environment.md).  

**Method 2: Prevent Auto-execution in the Container**  
If you **must** keep the host service running, configure the container so that the daemon (`dxrtd`) does not start automatically upon launch.  

For more details, refer to the **Docker Advanced Troubleshooting (Multi-Runtime Containers)** section in [**Setting Up Environment**](02_Setting_Up_Environment.md).  

---

## Q2. X11 Session Warnings & Mount Errors (Wayland Issues)

This occurs when X11 forwarding authentication fails, leading to GUI tool errors or container startup refusal.  

### Diagnostic Steps

- **Q2.1 Warning**: `[WARNING] it is recommended to use an **X11 session (with .Xauthority support)** when working with the 'dx-all-suite' container.` appears during startup.  
- **Q2.2 Error**: The container fails with `error mounting /tmp/.docker.xauth` after a system reboot or logout.  

### Cause

- **Q2.1:** GUI applications (e.g., X11-forwarded windows from Docker containers) are optimized for X11. Wayland sessions can cause `xauth` processes to be unstable.  
- **Q2.2:** Ending a Wayland session may purge X authentication data or change directory paths, causing Docker mount points to become invalid.  

### Solution: Set the Default System Session to X11

The most reliable solution is to set the login session to X11 (`Xorg`). This is the standard procedure for Ubuntu/GNOME environments.  

**Step 1. Modify GDM Configuration**   
Open the GDM3 configuration file.  
```Bash
sudo nano /etc/gdm3/custom.conf
```

Uncomment `WaylandEnable=false` to force the login screen to use Xorg.  
```Plaintext
# Force the login screen to use Xorg
WaylandEnable=false
```

**Step 2. Apply Settings**  
Restart GDM or reboot your system.  
```Bash
sudo systemctl restart gdm3
# Or simply reboot the PC
```

**Step 3. Resource Cleanup**  
Remove the existing container before re-running.  
```Bash
# Clean up existing containers
docker compose -f docker/docker-compose.yml down --remove-orphans

# Re-run the container
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04
```

For more details, refer to the **Docker Installation** section in [**Setting Up Environment**](02_Setting_Up_Environment.md).  

---

## Q3. Firmware Version Mismatch Error

This error occurs when the application stops because the firmware on the NPU hardware is older than the required software stack version.  

### Diagnostic Steps

Check the error message in your terminal.  
```Plaintext
The current firmware version is X.X.X.
Please update your firmware to version Y.Y.Y or higher.
```

### Cause

Mismatch between the installed **DX-RT** (Runtime) library and the **DX-FW** (Firmware) flashed onto the NPU. 

### Solution: Updating Firmware (DX-FW) and Cold Booting

**Method 1: Using the Integrated Installation Script (Recommended)**  
Update the firmware using the all-in-one setup script.  
```Bash
./dx-runtime/install.sh --target=dx_fw
```

**Method 2: Using the Dedicated CLI Tool (`dxrt-cli`)**  
Update the firmware manually by pointing to the specific binary file.  
```Bash
dxrt-cli -u ./dx-runtime/dx_fw/m1/X.X.X/mdot2/fw.bin
```

**Critical Post-Update Action: Cold Booting**  
To completely initialize the hardware logic and ensure the new firmware version is applied, please follow this procedure.  

**Option 1.** [Recommended] Cold Boot  
- Method: Shut down the system completely, **unplug the power cable** to drain any residual power, then plug it back in and turn it on.  
- Reason: This is the most reliable way to guarantee a complete hardware-level reset for the NPU.  

**Option 2.** For Remote/SSH Environments  
- If physical power disconnection is impossible (e.g., in a remote server room), perform a system restart at the OS level using the `sudo reboot` command. In most standard scenarios, a system reboot is sufficient to refresh the firmware.  

**Final Verification**  
After rebooting, enter the following command in the terminal to verify that the firmware has been updated successfully.  
```Bash
dxrt-cli -s
```

For more details, refer to the **Firmware (DX-FW) Update and Activation** section in [**Setting Up Environment**](02_Setting_Up_Environment.md).  

---

## Q4. Device Driver Update Error

This issue occurs when the application execution is interrupted because the kernel driver version is outdated.  

### Diagnostic Steps

Check the terminal for the following error message.  
```Plaintext
The current device driver version is X.X.X.
Please update your device driver to version Y.Y.Y or higher.
```

### Cause

The installed kernel driver (`dx_rt_npu_linux_driver`) does not meet the minimum requirements of the current **DX-RT**.  

### Solution: Update the Device Driver on the Host OS

To resolve this, you **must** update the driver module directly on your host operating system.  

**Step 1. Install the Driver Module**  
Run the installation script specifically targeting the driver.  
```Bash
./dx-runtime/install.sh --target=dx_rt_npu_linux_driver
```

**Step 2. System Reboot**  
Since the driver needs to be reloaded into the Linux kernel, a system reboot is mandatory.  
```Bash
sudo reboot
```

**Step 3. Verify Status**  
After the reboot, confirm the update was successful.  
```Bash
dxrt-cli -s
```

!!! caution "Warning for Docker Users"  
    Because Docker containers share the host's kernel, **driver updates must be performed on the Host OS**, not inside the container. Updating the driver inside a container will not affect the hardware communication layer.  

For more details, refer to the **Building and Installing Modules** section in [**Setting Up Environment**](02_Setting_Up_Environment.md).  

---

## Q5. Model-Runtime Version Compatibility Error

This error occurs when the application stops because of the incompatibility between the compiler version (used to create the `.dxnn` file) and the runtime library version.  

### Diagnostic Steps

Check the terminal for the following error message.  
```Plaintext
The model's compiler version(X.X.X) is not compatible with this RT library. 
Please downgrade the RT library version to X.X.X or use a model file generated with a compiler version X.X.X or higher.
```

### Cause

This happens when there is a version mismatch between the **DX-COM** (Compiler) and the **DX-RT** (Runtime).  

### Solution: Synchronizing Versions via Re-compilation

To resolve this, you **must** ensure that your model and runtime environments are using compatible versions.

**Method 1: Re-compile the Model (Recommended)**  
Re-generate the `.dxnn` file using a compiler version that is compatible with your current system's **DX-RT** version. This is the safest way to ensure optimal performance and feature support.  

**Method 2: Adjust the Runtime Library Version**  
Reinstall **DX-RT** to a version that matches the model's requirements.  

!!! note "Note"  
    If you choose this method, you **must** also re-verify the compatibility of your NPU Driver and Firmware.  

**Version Verification Guide**  
To find the exact compatible combinations for each module, please refer to the **DXNN SDK Version Compatibility Matrix** in [**Version Compatibility**](04_Version_Compatibility.md).

---

## Q6. Insufficient Shared Memory (shm) Error

This error occurs when Docker's default `/dev/shm` size is too small for **DX-COM** (the DEEPX compiler) during model compilation.

### Diagnostic Steps

Check the terminal for the following error message.
```plaintext
[ResourceError]: Insufficient shared memory (shm). Increase the available /dev/shm size (e.g. --shm-size for Docker).
```

### Cause

Docker containers are allocated a default `/dev/shm` of **64 MB**. **DX-COM** uses shared memory during the model compilation process. When compiling large or complex models, this default limit can be exceeded.

### Solution: Increase the Docker Shared Memory Size

**Method 1: `docker run` with `--shm-size` (Recommended)**  
Pass the `--shm-size` flag when starting the container. Set the value based on your model size — `256m` is a common starting point; increase to `1g` or more for large models.  
```bash
docker run --shm-size=256m ...
# For larger models
docker run --shm-size=1g ...
```

**Method 2: `docker-compose.yml`**  
If you manage containers with Docker Compose (e.g., via `docker_run.sh`), add the `shm_size` field to the `dx-compiler` service definition.  
```yaml
services:
  dx-compiler:
    shm_size: '1gb'
```

!!! tip "Choosing the Right Size"  
    A value of `256m` resolves most cases. If the error persists with larger or batch-processed models, increase to `1g` or higher.

---

## Q7. DX-ModelZoo Environment Error (`dxmz` / `dx_engine` / `dx_com` Not Found)

This error occurs when DX-ModelZoo commands run in a Python environment that does not contain all required packages.  

### Diagnostic Steps

Check the terminal for one of the following messages.  
```Plaintext
bash: dxmz: command not found
ImportError: dx_engine is required for DxRuntimeSession. Please install the DeepX runtime package.
ImportError: dx_com is not installed. Install it to use compile: pip install dx_com
TypeError: compile() got an unexpected keyword argument 'calibration'
```

### Cause

`dxmz`, `dx_engine` (DX-RT Python API, for NPU evaluation), and `dx_com` (DX-COM, for compilation) **must** be installed in the same Python environment. DX-ModelZoo is installed into the runtime environment (`dx-runtime/venv-dx-runtime`, or `/venv-dxnn` in Docker), and `dx_com` is not installed there by default. A `TypeError` on a `compile()` keyword argument means the installed `dx_com` is older than the API DX-ModelZoo uses — reinstall `dx_com` with the version pinned in `dx-compiler/compiler.properties` (`COM_VERSION`).  

### Solution: Install All Packages into the Runtime Environment

**Step 1. Install DX-Runtime (provides `dx_engine`)**  
```Bash
./getting-started/runtime-0_install_dx-runtime.sh
```

**Step 2. Install DX-ModelZoo into the same environment**  
```Bash
./getting-started/modelzoo-0_install_dx-modelzoo.sh
```

**Step 3. Provide `dx_com` for compilation**  
The runner installs `dx_com` automatically with `pip` (version pinned in `dx-compiler/compiler.properties`, falling back to the PyPI release) while keeping DX-ModelZoo's `numpy>=1.20,<2.0` requirement.  
```Bash
./getting-started/modelzoo-2_run_first_npu_model.sh
```
To install from a local wheel instead, pass one whose Python tag matches the environment (e.g., `cp310` for Python 3.10).  
```Bash
./getting-started/modelzoo-2_run_first_npu_model.sh --dx-com-wheel /path/to/dx_com-*.whl
```
If you only need NPU evaluation, `dx_com` is not required at all — a prebuilt `.dxnn` is downloaded from `DXMZ_MODEL_URL`.  
```Bash
./getting-started/modelzoo-2_run_first_npu_model.sh --skip-onnx --skip-compile
```

**Step 4. Verify**  
```Bash
source ./dx-runtime/venv-dx-runtime/bin/activate
dxmz --help
python3 -c "import dx_engine, dx_com; print('OK')"
```

For more details, refer to the **DX-ModelZoo Installation** section in [**Setting Up Environment**](02_Setting_Up_Environment.md).  

---

## Q8. DX-ModelZoo Model Download Timeout

This issue occurs when `dxmz eval` tries to download a missing model and the connection never completes.  

### Diagnostic Steps

- **Step 1. Check Logs**: The download log shows no progress, and the command fails after several minutes (60-second timeout per server address).  
```Plaintext
WARNING | Model file not found locally: .../models/resnet50_224x224/resnet50_224x224.onnx
INFO    | Downloading model: https://sdk.deepx.ai/modelzoo/onnx/resnet50_224x224.onnx → ...
SessionCreationError: Failed to download model from https://sdk.deepx.ai/modelzoo/onnx/resnet50_224x224.onnx: <urlopen error ...>
```
- **Step 2. Check Connectivity**: DNS resolves, but the TCP connection to port 443 times out.  
```Bash
getent ahosts sdk.deepx.ai
timeout 15 nc -4 -vz -w 10 sdk.deepx.ai 443
env | grep -i proxy
```

If the log instead shows the following, `DXMZ_MODEL_URL` is not set (for example, `dx-modelzoo/.env` is missing):  
```Plaintext
Model file not found: .../models/resnet50_224x224/resnet50_224x224.onnx
To enable auto-download, set DXMZ_MODEL_URL environment variable.
```

### Cause

Outbound HTTPS (TCP 443) to `DXMZ_MODEL_URL` is blocked by a firewall, NAT, or a missing proxy setting. This is not a certificate problem: the connection fails **before** TLS negotiation, so `--cacert` or CA updates have no effect. `dxmz compile` never downloads models, so it fails with `ONNX file not found` when the download did not complete.  

### Solution: Allow Network Access or Place Models Manually

**Method 1: Allow Outbound Access or Configure a Proxy (Recommended)**  
Allow outbound TCP 443 to `sdk.deepx.ai`, or set the proxy before running the scripts.  
```Bash
export HTTPS_PROXY=http://<proxy_host>:<port>
export HTTP_PROXY=http://<proxy_host>:<port>
```
If your network provides a model mirror, set `DXMZ_MODEL_URL` in `dx-modelzoo/.env`.  

**Method 2: Place Model Files Manually (Offline)**  
Download the files on a host with internet access and copy them to the expected paths.  
```Plaintext
getting-started/modelzoo/models/<model>/<model>.onnx
getting-started/modelzoo/models/<model>/<model>_<profile>.dxnn
```

---

## Q9. DX-ModelZoo Dataset Not Found

This error occurs during evaluation or compilation (calibration) when the dataset defined in the model YAML is missing or incomplete.  

### Diagnostic Steps

Check the terminal for messages such as the following (`resnet50_224x224`).  
```Plaintext
DatasetValidationError:
  Dataset not found: ILSVRC2012
  Expected path: .../ILSVRC2012/val
DatasetValidationError: Dataset validation failed for ILSVRC2012: Expected 50000 images in .../ILSVRC2012/val, but found 0.
```

### Cause

DX-ModelZoo does not download datasets. Each model reads `dataset.eval_path` (for example, `${DATA_ROOT}/ILSVRC2012/val`) for both evaluation and calibration, and the dataset loader validates its structure.  

### Solution: Prepare the Dataset under `DATA_ROOT`

**Step 1. Check the expected path**  
The `[1] Model info` step of `modelzoo-2_run_first_npu_model.sh` shows the `Dataset` path, and the `PATH INFO` header shows `DATA_ROOT` (default: `getting-started/modelzoo/datasets`). When you run `dxmz` directly, `DATA_ROOT` comes from `--data-root` or `dx-modelzoo/.env`.  

**Step 2. Place the dataset**  
For `resnet50_224x224`, place the full ImageNet validation set (1,000 class directories, 50,000 JPEG images) under `getting-started/modelzoo/datasets/ILSVRC2012/val`. The runner always passes `--data-root getting-started/modelzoo/datasets`, so to reuse an existing dataset, link it instead of editing `.env`:  
```Bash
ln -s /path/to/ILSVRC2012 getting-started/modelzoo/datasets/ILSVRC2012
```
When you run `dxmz` directly, you can instead set `DATA_ROOT` in `dx-modelzoo/.env` or pass `--data-root`.  

---

## Q10. Docker Mount Error After Recreating a Host Path

This issue occurs when a host path that is bind-mounted into a running container is deleted and recreated.  

### Symptom

`docker exec` fails even though the container is running.  
```Plaintext
Error response from daemon: mount /home/user/dx-all-suite/dummy_xauthority:/var/lib/docker/rootfs/.../dummy_xauthority, flags: 0x5000: not a directory
```

### Cause

A bind mount is bound to the inode that existed when the container started. Deleting and recreating the host path (for example, removing `workspace/` or `dummy_xauthority`) leaves the container attached to the old inode, so the mount no longer matches. When the source is missing, the Docker daemon creates a **directory** in its place — which fails if the container expects a file (`dummy_xauthority` is a file created by `docker_run.sh`).  

### Solution: Restore the Path Type and Restart the Container

**Step 1. Restore a file source that became a directory**  
```Bash
rmdir dummy_xauthority && touch dummy_xauthority
```

**Step 2. Restart the container so the mounts are re-created**  
```Bash
./docker_run.sh --target=dx-modelzoo --ubuntu_version=24.04
```

!!! note "Stale Workspace Mount"  
    The same applies to `workspace/`: if it was recreated after the container started, files added on the host are not visible inside the container. Restart the container to rebind the mount.  

---

## Q11. NPU Device Driver Version Is Too Old

### Symptom

NPU evaluation fails immediately after the model is loaded.  
```Plaintext
RuntimeError: Failed to create InferenceEngine for model '.../resnet50_224x224_q-lite.dxnn':
[dxrt-exception] Invalid operation exception {"The current device driver version is 2.6.0.
Please update your device driver to version 2.7.0 or higher.":lib/device_version.cpp:217:CheckVersion}
```

### Cause

DX-RT inside the container and the NPU device driver on the **host** are separate components. The driver is a host kernel module, so rebuilding a Docker image upgrades DX-RT but never the driver. When the rebuilt image contains a newer DX-RT than the installed driver supports, DX-RT refuses to create an inference engine.  

Check the installed versions on the host:  
```Bash
dxrt-cli --status | grep -A2 Version
```

### Solution: Update the Host NPU Driver

**Step 1. Check the driver version pinned by DX-AllSuite**  
```Bash
git submodule status dx-runtime/dx_rt_npu_linux_driver
```

**Step 2. Install the pinned driver on the host**  
```Bash
./getting-started/runtime-0_install_dx-runtime.sh
```

**Step 3. Verify the driver version and re-run the evaluation**  
```Bash
dxrt-cli --status | grep "RT Driver version"
```

!!! note "Host and Container Must Be Upgraded Together"  
    Always update the host driver whenever you rebuild the runtime or DX-ModelZoo image. The container reuses the host driver through `/dev`, so an old driver blocks every NPU workload regardless of the image contents.  

---
