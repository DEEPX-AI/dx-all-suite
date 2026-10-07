# Setting Up Environment

**DX-AllSuite** is an integrated environment construction tool for verifying and utilizing DEEPX devices. This guide resolves complex dependency issues and provides a consistent development experience across both local hosts and Docker containers.  

<div align="center">
  <img src="./resources/DXNN-AllSuite.png" width="600">
  <p><strong>Figure. DX-AllSuite Supported Environments & Integrations.</strong></p>
</div>

**Installation Summary**  

**[Common] 1. Prerequisites**: Acquire source code and understand virtual environment management policies.  

**[Optional]** Choose Installation Path.  
- **[Route A] 2. Local Installation**: Direct installation on the host OS.  
- **[Route B] 3. Docker Installation**: Isolated installation based on containers.  

---

## Quick Install (one-line)

If you only need a single component, install it directly — no cloning, no submodule
synchronization:

```Bash
# DX-Compiler (x86_64 Host PC)
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-compiler/main/oneline-install.sh | sh

# DX-Runtime (target device with a DEEPX NPU: NPU driver + dx_rt + firmware)
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-install.sh | sh
```

Each installer resolves the newest version on its own — DX-Compiler from its latest
release on PyPI, DX-Runtime from the `latest` pointer on each component's `main` branch.
Override with `DX_VERSION=2.4.1` (DX-Compiler) or, for DX-Runtime, per component with
`DX_RT_VERSION=3.4.2`, `DX_DRIVER_VERSION=2.6.0`, `DX_FW_VERSION=2.7.4`. DX-Compiler also
accepts `DX_INSTALL_DIR=<dir>` (default `~/deepx`) to move the install root; DX-Runtime
has no equivalent, because it installs system packages through `dpkg` rather than into a
directory you choose.

!!! warning "DX-Runtime tracks `main`, so runs are not reproducible by default"
    Because versions are resolved at run time, the downloaded artifacts are not
    checksum-verified, and the three components follow their own branches independently —
    a run made between dx-runtime releases can install a combination that has not been
    validated together. Pin the versions above, or use the repository's `install.sh`,
    whenever you need a known-good set.

!!! note "DX-Compiler needs root for its system packages"
    `dx-com` is installed from PyPI into `$DX_INSTALL_DIR/venv-dx-compiler` (default
    `~/deepx/venv-dx-compiler`), and the `dxcom` launcher is linked into `DX_BIN_DIR`
    (default `~/.local/bin`) so it runs without activating the venv. The installer also
    apt-installs `libgl1-mesa-dev` and `libglib2.0-0`: `dx-com` depends on
    `opencv-python`, whose `cv2` extension links against those libraries and fails to
    import without them. Run as root or with `sudo` available, on Debian or Ubuntu.
    This route does not install the sample data — clone the repository for that.

!!! warning "DX-Runtime: reboot required"
    A reboot is mandatory after installation so the kernel loads the NPU driver. When no
    NPU device is detected the firmware update step is skipped — rerun the same command
    after rebooting to finish it.

!!! note "Scope of one-line install"
    One-line install covers `dx_fw`, `dx_rt`, and `dx_rt_npu_linux_driver` for DX-Runtime.
    `dx_app`, `dx_stream`, source builds, and the Docker route all use the full setup
    described below.

### Uninstalling a one-line install

```Bash
# DX-Compiler
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-compiler/main/oneline-uninstall.sh | sh

# DX-Runtime
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-uninstall.sh | sh
```

DX-Compiler must be given the same `DX_INSTALL_DIR` / `DX_BIN_DIR` used at install time,
otherwise it looks in the default location and finds nothing. DX-Runtime takes no such
argument: both of its install routes produce the same Debian packages, so this command
removes an `install.sh` install as well.

!!! warning "What uninstalling cannot undo"
    Firmware already flashed to the NPU is not reverted — there is no uninstall path for it.
    The `dx_engine` Python wheel is also left in place: `libdxrt-bin` cannot know which
    interpreter or virtualenv it went into, so it prints removal instructions during its own
    purge instead. `dx_app` and `dx_stream` are untouched, since the one-liner never installs
    them; use the repository's `uninstall.sh` for those.

## APT Repository Install (DX-Runtime)

The NPU driver and the DX-RT runtime are also published as Debian packages in the DEEPX APT
repository, for Ubuntu and Debian on `amd64` and `arm64`. Use this route when you want them managed by
`apt` like any other system package — installed, upgraded and removed with the usual commands.

```Bash
# 1. Download the DEEPX signing key and check its fingerprint
wget -O deepx-archive-keyring.asc https://apt.releases.deepx.ai/gpg
gpg --show-keys deepx-archive-keyring.asc

# 2. Only if the fingerprint matches, install the key and remove the download
sudo gpg --dearmor -o /usr/share/keyrings/deepx-archive-keyring.gpg deepx-archive-keyring.asc
rm deepx-archive-keyring.asc

# 3. Add the repository for this Ubuntu / Debian release
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/deepx-archive-keyring.gpg] https://apt.releases.deepx.ai $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") main" | sudo tee /etc/apt/sources.list.d/deepx.list

# 4. Install the driver and the runtime
sudo apt update
sudo apt install dxrt-driver-dkms
sudo apt install libdxrt-bin
```

!!! danger "Verify the key fingerprint before step 2"
    To guard against a tampered key (e.g. a man-in-the-middle attack), check the output of
    `gpg --show-keys` before installing the key. It must show exactly this 40-character
    fingerprint — `3A20CC853C64AE328D0F58CFD816AAC6689DBDEA`:
    ```
    pub   rsa4096 2026-08-11 [SCEA]
          3A20CC853C64AE328D0F58CFD816AAC6689DBDEA
    uid                      DeepX APT Repo <jhsa@deepx.ai>
    ```
    If it differs, stop, delete `deepx-archive-keyring.asc`, and contact DEEPX support.

| Package | Contents |
|---|---|
| `dxrt-driver-dkms` | NPU kernel driver, built for the running kernel through DKMS (pulls in `dkms` and `build-essential`) and rebuilt automatically on kernel updates |
| `libdxrt-bin` | Pre-built DX-RT library and headers under `/usr/local`, `dxrt-cli` and the other runtime tools, and the `dxrt` service |

!!! warning "Reboot and firmware"
    Reboot after installing `dxrt-driver-dkms` so the kernel loads the NPU driver. Firmware
    is not shipped in the APT repository — update it with the one-line installer above or
    `./dx-runtime/install.sh --target=dx_fw`, then cold boot as described in
    **DX-Runtime Installation**.

!!! note "Install the `dx_engine` Python package from PyPI"
    `libdxrt-bin` does not install the `dx_engine` Python binding, since it cannot know which
    interpreter or virtualenv you use. Install it from PyPI (`dx-engine`) into your virtualenv,
    pinned to the same major.minor version as the installed `libdxrt-bin` — the wheel carries
    its own copy of the runtime library, so mismatched versions are not caught by `apt` or `pip`:
    ```Bash
    source /path/to/venv/bin/activate
    pip install "dx-engine==$(dpkg-query -W -f='${Version}' libdxrt-bin | cut -d. -f1,2).*"
    ```
    For offline installs, the same wheels (one per CPython ABI) are staged in
    `/usr/share/libdxrt-bin/python`; the package prints the exact `pip install` command after
    installation.

Upgrade to later releases with `sudo apt update && sudo apt upgrade`, and remove the packages
with `sudo apt purge libdxrt-bin dxrt-driver-dkms`. This route covers the driver and runtime
only; `dx_app` and `dx_stream` still use the full setup below.

## Prerequisites

Follow these steps first to ensure a stable installation. This is the full-suite route —
skip it if the one-line install above already covers what you need.

### Repository Cloning and Submodule Synchronization

**DX-AllSuite** is a collection of several independent modules. If submodules are missing, compilation and runtime execution will not be possible. Please use the following commands exactly.  

**A. Clone Repository (Including Submodules)**  
```Bash
# Via HTTPS (Recommended)
git clone --recurse-submodules https://github.com/DEEPX-AI/dx-all-suite.git

# Via SSH
git clone --recurse-submodules git@github.com:DEEPX-AI/dx-all-suite.git

cd dx-all-suite
```

**B. (Optional) Update Existing Repository**  
If you have already cloned the repository but the subfolders are empty, you **must** perform manual initialization.  
```Bash
# Initialize and update submodules to the latest state
git submodule update --init --recursive

# Check submodule status (Success if no '-' prefix exists)
git submodule status
```

**C. (Optional) Prepare Docker Environment**  
If you plan to use the Docker route but do not have Docker installed, use the provided automation script.  
```Bash
# Automatic installation of Docker and Docker Compose
./scripts/install_docker.sh
```

### Automated Environment Management

DX-AllSuite automates the creation of Python virtual environments (venv) to prevent package conflicts. The installation scripts automatically configure independent environments optimized for each execution context, so users do not need to create virtual environments manually.  

- **Compiler Environment**: Created at `dx-compiler/venv-dx-compiler`  
- **Runtime Environment**: Created at `dx-runtime/venv-dx-runtime`  

!!! warning "CAUTION"  
    If you are installing an individual module (e.g., `dx-rt` only), you **must** activate the corresponding virtual environment (`source .../activate`) created by the script to avoid installation failure.     
    
### SDK Workflow Guide

**DX-AllSuite** provides two paths for utilizing the DEEPX NPU, depending on whether you are bringing your own model or using a pre-optimized one. The SDK automatically manages the necessary virtual environments and dependencies to ensure a seamless development experience.  

**[Path A] Custom Model Inference Path**  
The standard workflow for converting and deploying user-trained models.  

<div align="center">
  <img src="./resources/DXNN-CustomModel.png" width="600">
  <p><strong>Figure. Custom Model Inference.</strong></p>
</div>

This path is designed for users who have a specific model architecture trained in frameworks and need to optimize it for DEEPX hardware.  

- **Step 1 (Source)**: Secure your trained models and source code from major AI frameworks such as PyTorch or TensorFlow.     
- **Step 2 (Export)**: Export the model to **ONNX**, the standard format recognized by **DX-COM**.  
    : Tip: Set input tensor size and use **Opset 11 or higher** to ensure maximum compatibility with NPU specifications.  
- **Step 3 (DX-COM)**: Convert the ONNX model into an NPU-optimized `.dxnn` binary within the compiler virtual environment (`venv-dx-compiler`).  
- **Step 4 (DX-RT)**: Load the generated model and run inference on the target device using the runtime virtual environment (`venv-dx-runtime`).  
- **Step 5 (NPU Acceleration)**: Verify real-time AI inference performance and inspect the final output.  

**[Path B] Pre-Compiled Model Path (Fast Track)**  
The "Fast Track" for immediate hardware validation.  

<div align="center">
  <img src="./resources/DXNN-Pre-builtModel.png" width="600">
  <p><strong>Figure. Pre-Built Model Inference.</strong></p>
</div>

This path is ideal for users who want to quickly benchmark DEEPX NPU performance or test hardware integration using industry-standard models.  

- **Step 1 (Select)**: Choose a pre-validated `.dxnn` model from the **DEEPX ModelZoo** or sample data.  
- **Step 2 (DX-RT)**: Load the selected model immediately in the runtime environment (`venv-dx-runtime`) without a separate compilation process.  
- **Step 3 (NPU Acceleration)**: Execute hardware-accelerated inference and analyze key performance indicators like **FPS** and **Latency**.  

---

## Local Installation

Installing **DX-AllSuite** directly on the **Host OS** ensures maximum hardware performance and seamless compatibility between all software modules. This method is recommended for production environments and advanced performance benchmarking.  

### DX-Compiler Installation (DX-COM)

DX-Compiler (DX-COM) can be used as a CLI tool or a Python module on supported Linux distributions.  

**Differences in Usage**  
- **CLI Tool (Command Line Interface)**: Perform compilation by entering `dxcom` commands directly in the terminal (Bash). Ideal for quick execution and automated shell scripts without additional coding.  
- **Python Module (Library)**: Call functions or classes via `import dx_com` within your Python scripts. This is the preferred method for integrating the compiler into your existing AI training or automation pipelines.  

!!! warning "Change in Distribution Method"  
    The standalone executable distribution method is **no longer supported**. This guide describes the latest **Wheel-based** installation workflow, which ensures better dependency management and Python environment integration.  

#### A. Pre-Installation Requirements
Before installing **DX-COM**, you **must** install the following system libraries to support core utilities and graphical operations.  

- **`libgl1-mesa-glx`**: OpenGL runtime support for graphics processing  
- **`libglib2.0-0`**: Core utility library (related to GNOME/GTK)

**Installation Command**  
```Bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends libgl1-mesa-glx libglib2.0-0 make
```

#### B. Installation Method
**Supported Environments**  

- **OS**: Linux (x86_64)  
- **Python Version**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13, 3.14 (The installation script will automatically detect your version)

**Integrated Package Installation**  
The provided install.sh script handles everything in one go, including Python version detection and package installation.  
```Bash
# Run the interactive installation script (recommended)
./dx-compiler/install.sh
```

#### C. Verify and Usage
After installation, activate the virtual environment (`venv-dx-compiler`) to verify the setup.  
```Bash
# 1. Activate the Virtual Environment
source ./dx-compiler/venv-dx-compiler/bin/activate

# 2. Verify Installed Version (CLI and Python Modules)
dxcom --version
python3 -c "import dx_com; print(dx_com.__version__)"

# 3. Access Help Documentation
dxcom -h
```

- **Sample Data Location**: `./dx-compiler/dx_com/sample_models/`  

!!! note "Tip"  
    If the automatic sample data download fails, you can manually fetch the assets using the following scripts:  
    - `./dx-compiler/example/1-download_sample_models.sh` (Model data)  
    - `./dx-compiler/example/2-download_sample_calibration_dataset.sh` (Calibration data)  

#### D. Model Visualization
**DX-TRON has been removed** as of DX-Compiler v2.5.0. To inspect the compiled model structure and CPU/NPU workload distribution, generate the interactive HTML **Compilation Summary Report** with DX-COM:  
```bash
dxcom -m model.onnx -c config.json -o output/ --export_html
```
Then open `output/<model_name>_summary.html` in your browser.  

### DX-Runtime Installation (RT, Driver, FW, App, Stream)

The **DX-Runtime** stack is the core software layer required to control DEEPX NPU hardware and execute AI applications. Each component is managed as a submodule within the `./dx-runtime` directory.  

#### A. Building and Installing Modules
Depending on your requirements, you can perform a full installation or target specific modules to save time.  
```Bash
# Option 1: Install all modules (Driver, FW, RT, App, Stream)
./dx-runtime/install.sh --all

# Option 2: Full install excluding firmware
# (Use this if your NPU already has the latest FW version)
./dx-runtime/install.sh --all --exclude-fw

# Option 3: Install a specific module only
./dx-runtime/install.sh --target=<module_name>
```

#### B. Firmware (DX-FW) Update and Activation
Updating the firmware is a critical process. To ensure the hardware logic is correctly initialized, follow these steps precisely.

**Step 1. Update the Firmware**  
You can update the firmware using the automated installation script or the dedicated CLI tool.  
```Bash
# Method 1. Using the installation script
./dx-runtime/install.sh --target=dx_fw

# Method 2. Manual update using dxrt-cli
dxrt-cli -u ./dx-runtime/dx_fw/m1/X.X.X/mdot2/fw.bin
```

**Step 2. Perform a Cold Boot**  
It is **strongly recommended** to completely shut down the system, turn off the power, and then turn it back on. A simple 'Restart' may not be sufficient for hardware initialization.  

**Step 3. System Reboot**  
After installation is complete, be sure to perform `sudo reboot` to activate the installed kernel driver.  

### [Local] Installation Verification (Sanity Check)

Once the local installation is finished, perform a final check to confirm that the hardware and software are communicating correctly. 

#### A. Hardware and Version Check  
Run the following command to display information about the NPU devices recognized by the system.  
```Bash
dxrt-cli -s
```

**Success Checklist**  

- **[x] Device Recognition**: Does it display `Device 0: M1?`  
- **[x] Version Info**: Do `RT Driver`, `PCIe Driver`, and `FW version` show valid numbers (e.g., v1.x.x)?  
- **[x] Status**: Are real-time metrics for **Voltage**, **Clock**, and **Temperature** visible at the bottom?  

#### B. System Integrity Check  
Run the batch sanity script to verify that all modules are located in their designated paths.  
```Bash
./dx-runtime/scripts/sanity_check.sh
```

!!! note "Tip"  
    If any item returns a **FAIL** or **Not Found**, please revisit the **DX-Runtime Installation** section (Building and Installing Modules) to ensure all components were compiled correctly.    

---

## Docker Installation

Docker allows you to run **DX-AllSuite** in an isolated environment without complex dependency settings.  

### Host System Preparation (Critical)

Because Docker containers share the host kernel, **the driver must be installed on the host system (PC) first** for NPU hardware recognition.  

**A. Install NPU Driver (Host)**  
Execute the installation script on your **Host PC** first.  
```Bash
./dx-runtime/install.sh --target=dx_rt_npu_linux_driver
```

**B. Prevent Service Daemon (`dxrtd`) Conflicts**  
Only one instance of `dxrtd` can run across the host and containers. Stop the host service before running the container.
```Bash
sudo systemctl stop dxrt.service
```

### Build Docker Image and Run Container

**A. Build Image**  
Using the `--all` option builds an integrated image containing the Compiler, Runtime, and ModelZoo.  
```Bash
# Build integrated image (Based on Ubuntu 24.04)
./docker_build.sh --all --ubuntu_version=24.04

# Build specific environment only (Using --target)
./docker_build.sh --target=dx-runtime --ubuntu_version=24.04
```

**B. Run Container**  
Run the container after the image build is complete.  
```Bash
./docker_run.sh --all --ubuntu_version=24.04
```

!!! warning "Note on GUI Environments"  
    If you encounter X11 warnings or mount errors (e.g., cannot open display), it is likely due to the host OS using a **Wayland** session. Refer to **Q2. X11 Session Warnings & Mount Errors (Wayland Issues)** in [**FAQ Troubleshooting Guide**](05_FAQ_Troubleshooting_Guide.md).  

### GPU Acceleration Options (Optional)

Docker images can optionally be built with GPU acceleration. The two options serve **different purposes and different containers**, and are mutually exclusive (Ubuntu only):

| Option | Accelerates | Target containers | Typical use case |
|---|---|---|---|
| `--nvidia_gpu` | Compute (CUDA) | `dx-compiler`, `dx-modelzoo` | Faster ONNX raw accuracy evaluation (dx-modelzoo) and `q-pro` quantization calibration (dx-compiler) |
| `--intel_gpu_hw_acc` | Media (VA-API) | `dx-runtime` — **dx_stream pipelines only** | Offload video decode/scale to the Intel iGPU so the CPU stays free for pre/post-processing in multi-channel GStreamer pipelines |

**A. NVIDIA GPU (CUDA) — dx-compiler / dx-modelzoo**

Host requirements: NVIDIA driver and [nvidia-container-toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
(`sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker`).

```Bash
# Build on a CUDA base image (default CUDA version: 12.8.1, override with --cuda_version=<ver>)
./docker_build.sh --target=dx-modelzoo --ubuntu_version=24.04 --nvidia_gpu
./docker_build.sh --target=dx-compiler --ubuntu_version=24.04 --nvidia_gpu

# Run / stop — GPU images are tagged cuda<ver>-ubuntu-<os> and coexist with CPU images
./docker_run.sh  --target=dx-modelzoo --ubuntu_version=24.04 --nvidia_gpu
./docker_down.sh --target=dx-modelzoo --ubuntu_version=24.04 --nvidia_gpu
```

Inside the dx-modelzoo container, install GPU dependencies before evaluation: `pip install -e ".[gpu]"`.
For dx-compiler, `q-pro` calibration uses the GPU automatically (`quantization_device` auto-detection).

**B. Intel GPU (VA-API Media Acceleration) — dx-runtime (dx_stream)**

Host requirements: Intel GPU with the `i915`/`xe` driver loaded (`/dev/dri/renderD*` present on the host).

```Bash
./docker_build.sh --target=dx-runtime --ubuntu_version=24.04 --intel_gpu_hw_acc
./docker_run.sh   --target=dx-runtime --ubuntu_version=24.04 --intel_gpu_hw_acc
./docker_down.sh  --target=dx-runtime --ubuntu_version=24.04 --intel_gpu_hw_acc
```

No dx_stream code changes are required — GStreamer `decodebin` automatically selects the VA-API HW decoder (e.g., `vah264dec`), and adding `vapostproc` to a pipeline additionally offloads resize/color conversion to the iGPU video-enhance engine.

!!! note "Intel GPU scope"
    `--intel_gpu_hw_acc` accelerates **media processing for dx_stream (GStreamer) pipelines only**. It does not accelerate dx-compiler or dx-modelzoo workloads (compute acceleration is CUDA-only via `--nvidia_gpu`), and dx_app uses software decoding by default.

### Container Access and Task Guide

#### A. DX-Compiler Environment (Model Conversion)
The DX-Compiler environment is used to generate hardware-optimized `.dxnn` binaries. 

**A-1. Accessing the Container**  
To perform tasks within the container, you **must** first log in to the running container's shell.  
```Bash
# 1. Run in Host Terminal: Enter the container
docker exec -it dx-compiler-24.04 bash 

# 2. Inside Container: Navigate to the work directory
cd /deepx/dx-compiler/dx_com
```

!!! warning "Path Logic Notice"  
    The `/deepx` path is an absolute path **internal** to the container. This path does not exist on your host machine. Before executing commands, ensure your terminal prompt has changed to `root@...` or `user@container_id`.

**A-2. Compiling Sample Model**  
Sample models are pre-downloaded to the `./sample_models/` directory upon installation. You can compile them using one of the following two methods.  

- **Method 1**: Batch Compilation (Recommended)  
Use the provided script to compile all sample models automatically.  
```Bash
../example/3-compile_sample_models.sh
```

- **Method 2**: Manual Compilation (CLI)  
For granular control, activate the virtual environment and use the `dxcom` tool directly.  
```Bash
source ../venv-dx-compiler/bin/activate  # Activate venv

dxcom -m sample_models/onnx/YOLOV5S-1.onnx \
      -c sample_models/json/YOLOV5S-1.json \
      -o output/YOLOV5S-1
```

**A-3. Checking the Results**  
Upon successful completion, the optimized `.dxnn` binary will be generated in the `output/` directory (or the path specified by the `-o` flag).  

- **Output File**: `output/YOLOV5S-1.dxnn`  
- **Next Step**: Transfer this file to the **Runtime Environment** for hardware execution.  

#### B. DX-Runtime Environment (NPU Inference & Streaming)
The **DX-Runtime** environment is designed for executing model inference and processing high-performance video streams using DEEPX NPU hardware.  

**B-1. Accessing the Container and Status Check**  
Before running any inference, ensure the container can communicate with the NPU hardware.
```Bash
# 1. Run from the host terminal: Enter the container
docker exec -it dx-runtime-24.04 

# 2. Inside Container: Verify NPU hardware recognition
dxrt-cli -s
```

**B-2. Running Sample Applications (`dx_app`)**  
This module provides inference demos for various vision tasks.  

- **Working Directory**: `/deepx/dx-runtime/dx_app`  

```Bash
cd /deepx/dx-runtime/dx_app

# 1. Prepare resources (Download .dxnn models and sample images)
./setup.sh

# 2. Run demo 
./run_demo.sh 			# Run C++ based demo
./run_demo_python.sh 		# Run Python demo
```

!!! note "Demo Selection"  
    Upon execution, the terminal will display a list of available demos (0, 1, 2...). Simply enter the corresponding number and press **Enter** to start.

**B-3. Running the Streaming Framework (`dx_stream`)**  
This module is a GStreamer-based module optimized for real-time multi-channel video stream processing.  

- **Working Directory**: `/deepx/dx-runtime/dx_stream`  

```Bash
cd /deepx/dx-runtime/dx_stream

# 1. Prepare assets (Downloads streaming-specific models and video assets) 
./setup.sh

# 2. Run the streaming demo (C++ based)
./run_demo.sh
```

!!! note "Scenario Selection"  
    You can select specific streaming scenarios by entering the scenario number displayed in the terminal.

**Path Precautions**  
It is critical to distinguish between your **Host** terminal and the **Container** terminal to avoid "`File not found`" errors.  

- **Inside Docker Container**: Always use the absolute path starting with `/deepx` (e.g., `cd /deepx/dx-runtime/...`).  
- **Local Host Environment**: Use relative paths based on your current directory (e.g., `cd ./dx-runtime/...`).  

!!! warning "Common Error"  
    If you attempt to enter a path starting with `/deepx` in a Host terminal, the system will return a `No such file or directory` error. Always check if your prompt starts with `root@...` or `user@container_id` before navigating.  

### [Docker] Advanced Troubleshooting (Multi-Runtime Containers)

The `dxrtd` daemon **must** run as a single instance (Singleton) within the system. To launch multiple containers simultaneously, you **must** modify the `Entrypoint` to prevent automatic execution.  

- **Method 1**: Modifying Dockerfile  
Edit the `docker/Dockerfile.dx-runtime` file to disable the default startup command and replace it with a persistent idle state.  
```Dockerfile
# 1. Comment out the existing settings
# ENTRYPOINT [ "/usr/local/bin/dxrtd" ]

# 2. Enable infinite wait settings to keep containers running
ENTRYPOINT ["tail", "-f", "/dev/null"]
```

- **Method 2**: Modifying docker-compose  
If you are using Docker Compose, you can overwrite the default Entrypoint directly in `docker/docker-compose.yml` within the corresponding service section.  
```YAML
services:
  dx-runtime:
    entrypoint: ["/bin/sh", "-c"]
    command: ["sleep infinity"]
```

!!! note "Manual Startup"  
    When the above settings are applied, the NPU will be in a waiting state. After entering the container, run it manually using the `dxrtd &` command.  

### [Docker] Verification of Installation Results (Sanity Check)

This performs a final check to ensure that the installation was completed successfully and that the software and hardware communicate correctly.  

#### A. Hardware Recognition Check (`dxrt-cli`)
Run the following command inside the container to verify that the NPU is visible and operational:  
```Bash
dxrt-cli -s
```

**Success Checklist**  
If your output meets the following three conditions, the hardware integration is successful:  

- **[x] Device Recognition**: `Device 0: M1` (or your specific model) is displayed.  
- **[x] Version Information**: Valid version numbers appear for `RT Driver version`, `FW version`, etc.  
- **[x] Daemon Status**: No error messages such as "`Other instance of dxrtd is running`" are present.  

[Example of Normal Output]  
```Plaintext
DX-RT v3.2.0
========================================================
* Device 0: M1, Accelerator type
--------------------- Version ---------------------
* RT Driver version : v2.1.0
* FW version :      v2.5.0
-------------------------------------------------------
... (Continued)
```

#### B. System Consistency Check
This script performs a batch check to ensure all individual modules are correctly placed in their designated paths and are ready for execution.  
```Bash
# Check the integrity of the runtime environment
./dx-runtime/scripts/sanity_check.sh
```

If **[OK]** or **PASS** is output for all items, you are ready to start service development.  

---
