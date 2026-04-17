# FAQ Troubleshooting Guide

This guide addresses common errors and symptoms encountered while using the **DXNN SDK** and provides step-by-step solutions. 

**Table of Contents**  

- [Q1. Container 'Restarting' Error (#dxrtd-conflict)](#q1-container-restarting-error-dxrtd-conflict)  
- [Q2. X11 Session Warnings & Mount Errors (Wayland Issues)](#q2-x11-session-warnings--mount-errors-wayland-issues)  
- [Q3. Firmware Version Mismatch Error](#q3-firmware-version-mismatch-error)  
- [Q4. Device Driver Update Error](#q4-device-driver-update-error)  
- [Q5. Model-Runtime Version Compatibility Error](#q5-model-runtime-version-compatibility-error)  

---

## Q1. Container 'Restarting' Error (`dxrtd` Conflict)

This issue occurs when the container status is continuously displayed as Restarting after running docker_run.sh, making it impossible to enter the container.  

### Diagnostic Steps

- **Step 1.	Check Status**: Run `docker ps` and check if the `STATUS` is repeatedly showing `Restarting (255)`.  
- **Step 2.	Check Logs**: Run `docker logs <container_name>` and check for the message "`Other instance of dxrtd is running`".  

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

For more details, refer to the [**Host System Preparation**](02_Setting_Up_Environment.md#host-system-preparation-critical) in **02. Setting Up Environment**.  

**Method 2: Prevent Auto-execution in the Container**  
If you **must** keep the host service running, configure the container so that the daemon (`dxrtd`) does not start automatically upon launch.  

For more details, refer to the [**Docker Advanced Troubleshooting**](02_Setting_Up_Environment.md#docker-advanced-troubleshooting-multi-runtime-containers) in **02. Setting Up Environment**.  

---

## Q2. X11 Session Warnings & Mount Errors (Wayland Issues)

This occurs when X11 forwarding authentication fails, leading to GUI tool errors or container startup refusal.  

### Diagnostic Steps

- **Q2.1 Warning**: `[WARN] it is recommended to use an X11 session` appears during startup.  
- **Q2.2 Error**: The container fails with `error mounting /tmp/.docker.xauth` after a system reboot or logout.  

### Cause

- **Q2.1:** GUI tools such as **DX-TRON** are optimized for X11. Wayland sessions can cause `xauth` processes to be unstable.  
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
Remove orphan containers before re-running.  
```Bash
# Clean up existing containers
docker compose -f docker/docker-compose.yml down --remove-orphans

# Re-run the container
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04
```

For more details, refer to the [**Docker Installation**](02_Setting_Up_Environment.md#docker-installation) section in **02. Setting Up Environment**.  

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

For more details, refer to the [**Firmware (DX-FW) Update and Activation**](02_Setting_Up_Environment.md#b-firmware-dx-fw-update-and-activation) section in **02. Setting Up Environment**.  

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

For more details, refer to the [**Module Build and Installation**](02_Setting_Up_Environment.md#a-building-and-installing-modules) section in **02. Setting Up Environment**.  

---

## Q5. Model-Runtime Version Compatibility Error

This error occurs when the application stops because of the incompatibility between the compiler version (used to create the `.dxnn` file) and the runtime library version.  

### Diagnostic Steps

Check the terminal for the following error message.  
```Plaintext
The model's compiler version(X.X.X) is not compatible in this RT library. 
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
To find the exact compatible combinations for each module, please refer to the [**DXNN SDK Component Version Compatibility Matrix**](04_Version_Compatibility.md#dxnn-sdk-component-version-compatibility-matrix).

Copyright © DEEPX. All rights reserved.

---
