# Installation Guide

DX-All-Suite is a tool for creating an environment to validate and utilize DEEPX devices. DX-All-Suite provides the following below methods for setting up the integrated environment:

**Install on local machine** - Set up the DX-All-Suite environment directly on the host environment
(maintaining compatibility between the individual tools).

**Build Docker image and run container** - Build a DX-All-Suite environment within a Docker environment, or load a pre-built image to create a container.

## Prerequisites

### Clone the Main Repository

```bash
git clone --recurse-submodules https://github.com/DEEPX-AI/dx-all-suite.git
```

or

```bash
git clone --recurse-submodules git@github.com:DEEPX-AI/dx-all-suite.git
```

#### (Optional) Initialize and Update Submodules in an Already Cloned Repository

```bash
git submodule update --init --recursive
```

### Check Submodule Status

```bash
git submodule status
```

#### (Optional) Install Docker & Docker Compose

```bash
./scripts/install_docker.sh
```

#### (Optional) Install Python and Python Virtual Environment

The installation scripts automatically detect your Python version, install a compatible Python if needed, and create and activate a virtual environment. You do not need to set up Python or a virtual environment manually — simply run the installation script and it will handle everything.

If Python is not already installed on your system, installing it beforehand can reduce build time:

```bash
sudo apt install python3 python3-dev python3-venv
```

---

## Local Installation

### Install DX-Compiler Environment (dx_com, dx_tron)

The `DX-Compiler` environment provides prebuilt binary outputs and does not include source code. Each module can be downloaded and installed from a remote server using the following command:

```bash
./dx-compiler/install.sh
```

#### Python Version Compatibility

`dx_com`'s installation requires Python.

The installation script automatically checks Python version compatibility. Supported Python versions are `3.8`, `3.9`, `3.10`, `3.11`, and `3.12`.

If the current system's Python version is not compatible, the script will detect this and ask the user whether to install a compatible Python version. You can also specify a specific Python version using the `--python_version` option:

```bash
./dx-compiler/install.sh --python_version=3.11
```

#### Installation Modes

The installation script downloads and installs Python wheel packages into the virtual environment, automatically selecting the appropriate package for your Python version.

Use `dxcom` command after activating the virtual environment.

Upon successful installation:

1.  The `dx_com` module will be downloaded and installed:
    - Python wheel packages are installed in the virtual environment

2.  Symbolic links will be created at `./dx-compiler/dx_com`.

3.  **Sample data is automatically downloaded** into `./dx-compiler/dx_com/`:
    - `sample_models/` — sample ONNX models and JSON configs (`YOLOV5S-1`, `YOLOV5S_Face-1`, `MobileNetV2-1`)
    - `calibration_dataset/` — calibration images for quantization

    > If the automatic download fails, you can run it manually:
    > ```bash
    > ./dx-compiler/example/1-download_sample_models.sh
    > ./dx-compiler/example/2-download_sample_calibration_dataset.sh
    > ```

#### Using dx_com

You can use the `dxcom` command after activating the virtual environment:

```bash
# Activate virtual environment
source ./dx-compiler/venv-dx-compiler-local/bin/activate

# Use dxcom
dxcom -h
```

#### Using DX-TRON

`dx_tron` (DX-TRON) is a graphical model compiler tool.

**If installed with deb (Debian Package: default) mode:**

You can use the `dxtron` command:

```bash
dxtron
```

**Run with AppImage (GUI):**

```bash
./dx-compiler/run_dxtron_appimage.sh
```

**Run as web server:**

```bash
./dx-compiler/run_dxtron_web.sh --port=8080
```

Then access `http://localhost:8080` in your browser.

To use a different port:

```bash
./dx-compiler/run_dxtron_web.sh --port=3000
```

**(P.S.) DXTron for Windows: available for download via `developer.deepx.ai`.**

---

### Install DX-Runtime Environment

The `DX-Runtime` environment includes source code for each module. The repositories are managed as Git submodules(`dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, and `dx_stream`) under `./dx-runtime`.  
To build and install all modules, run:

```bash
./dx-runtime/install.sh --all
```

This command will build and install the following modules:  
`dx_fw`, `dx_rt_npu_linux_driver`, `dx_rt`, `dx_app`, and `dx_stream`

```bash
./dx-runtime/install.sh --all --exclude-fw
```

You can exclude `dx_fw` from the installation using the `--exclude-fw` option.

#### Selective Installation of a Specific Module

You can install a specific module using:

```bash
./dx-runtime/install.sh --target=<module_name>
```

#### Update `dx_fw` (Firmware Image)

The `dx_fw` module does not include source code but provides a `fw.bin` image file.  
To update the firmware using `dxrt-cli`, run:

```bash
dxrt-cli -u ./dx-runtime/dx_fw/m1/X.X.X/mdot2/fw.bin
```

Alternatively, you can use:

```bash
./dx-runtime/install.sh --target=dx_fw
```

**It is recommended to completely shut down and power off the system before rebooting after a firmware update.**

#### Sanity check

```bash
./dx-runtime/scripts/sanity_check.sh
```

You can use this command to verify that `dx_rt` and `dx_rt_npu_linux_driver` are installed correctly.

---

## Installation Using Docker

### Install DX-Compiler, DX-Runtime, and DX-ModelZoo Environment

#### Notes

##### 1. When using a Docker environment, the NPU driver must be installed on the host system:

```bash
./dx-runtime/install.sh --target=dx_rt_npu_linux_driver
```

##### 2. If `dx_rt` is already installed on the host system and the `service daemon` (`/usr/local/bin/dxrtd`) is running, launching the `DX-Runtime` Docker container will result in an error (`Other instance of dxrtd is running`) and automatic termination.

Before starting the container, stop the service daemon on the host system.

##### 3. If another container is already running with the `service daemon` (`/usr/local/bin/dxrtd`), starting a new container will also result in the same error.

To run multiple DX-Runtime containers simultaneously, refer to note [#4](#4-if-you-prefer-to-use-the-service-daemon-running-on-the-host-system-instead-of-inside-the-container)

##### 4. If you prefer to use the `dxrtd`(service daemon) running on the host system instead of inside the container,

You can configure this in two ways:

###### Solution 1: Modify at Docker image build level

Update the `docker/Dockerfile.dx-runtime` as follows:

- Before:

```Dockerfile
...
ENTRYPOINT [ "/usr/local/bin/dxrtd" ]
# ENTRYPOINT ["tail", "-f", "/dev/null"]
```

- After:

```Dockerfile
...
# ENTRYPOINT [ "/usr/local/bin/dxrtd" ]
ENTRYPOINT ["tail", "-f", "/dev/null"]
```

###### Solution 2) Modify at Docker container run level

Update the `docker/docker-compose.yml` as follows:

- Before:

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

- After:

```bash
  ...
  dx-runtime:
    container_name: dx-runtime-${UBUNTU_VERSION}
    image: dx-runtime:${UBUNTU_VERSION}
    ...
    restart: on-failure
    devices:
      - "/dev:/dev"                           # NPU / GPU / USB CAM

    entrypoint: ["/bin/sh", "-c"]             # ADDED
    command: ["sleep infinity"]               # ADDED
```

#### Build the Docker Image

```bash
./docker_build.sh --all --ubuntu_version=24.04
```

This command builds a Docker image with both `dx-compiler`, `dx-runtime` and `dx-modelzoo` environments.  
You can check the built images using:

```bash
docker images
```

```
REPOSITORY         TAG       IMAGE ID       CREATED         SIZE
dx-runtime         24.04     05127c0813dc   41 hours ago    4.8GB
dx-compiler        24.04     b08c7e39e89f   42 hours ago    7.08GB
dx-modelzoo        24.04     cb2a92323b41   2 weeks ago     2.11GB
```

##### Selective Docker Image Build for a Specific Environment

```bash
./docker_build.sh --target=dx-runtime --ubuntu_version=24.04
```

```bash
./docker_build.sh --target=dx-compiler --ubuntu_version=24.04
```

```bash
./docker_build.sh --target=dx-modelzoo --ubuntu_version=24.04
```

Use the `--target=<environment_name>` option to build only `dx-runtime` or `dx-compiler` or `dx-modelzoo`.

#### Run the Docker Container

**(Optional) If `dx_rt` is already installed on the host system, please stop the `dxrt` service daemon before running the Docker container.**  
(Reason: If the `dxrt` service daemon is already running on the host or in another container, the `dx-runtime` container will not be able to start. Only one instance of the service daemon can run at a time, including both host and container environments.)

(Refer to note #4 for more details.)

```
sudo systemctl stop dxrt.service
```

##### Run a Docker Container with All Environments (`dx_compiler`, `dx_runtime` and `dx_modelzoo`)

```bash
./docker_run.sh --all --ubuntu_version=<ubuntu_version>
```

To verify running containers:

```bash
docker ps
```

```
CONTAINER ID   IMAGE                  COMMAND                  CREATED          STATUS          PORTS     NAMES
f040e793662b   dx-runtime:24.04       "/usr/local/bin/dxrtd"   33 seconds ago   Up 33 seconds             dx-runtime-24.04
e93af235ceb1   dx-modelzoo:24.04      "/bin/sh -c 'sleep i…"   42 hours ago     Up 33 seconds             dx-modelzoo-24.04
b3715d613434   dx-compiler:24.04      "tail -f /dev/null"      42 hours ago     Up 33 seconds             dx-compiler-24.04
```

##### Enter the Container

```bash
docker exec -it dx-runtime-<ubuntu_version> bash
```

```bash
docker exec -it dx-compiler-<ubuntu_version> bash
```

```bash
docker exec -it dx-modelzoo-<ubuntu_version> bash
```

This allows you to enter the `dx-compiler`, `dx-runtime` and `dx-modelzoo` environments via a bash shell.

##### Check DX-Runtime Installation Inside the Container

```bash
dxrt-cli -s
```

Example output:

```
DXRT v3.2.0
=======================================================
* Device 0: M1, Accelerator type
---------------------   Version   ---------------------
* RT Driver version   : v2.1.0
* PCIe Driver version : v2.0.1
-------------------------------------------------------
* FW version          : v2.4.0
--------------------- Device Info ---------------------
* Memory : LPDDR5 6000 MHz, 3.92GiB
* Board  : M.2, Rev 1.0
* Chip Offset : 0
* PCIe   : Gen3 X4 [02:00:00]

NPU 0: voltage 750 mV, clock 1000 MHz, temperature 29'C
NPU 1: voltage 750 mV, clock 1000 MHz, temperature 28'C
NPU 2: voltage 750 mV, clock 1000 MHz, temperature 28'C
=======================================================
```

---

## Run Sample Application

### dx_app

#### Installation Path

1. **On the Host Environment:**
   ```bash
   cd ./dx-runtime/dx_app
   ```
2. **Inside the Docker Container:**
   ```bash
   docker exec -it dx-runtime-<ubuntu_version> bash
   # cd /deepx/dx-runtime/dx_app
   ```

#### Setup Assets (Precompiled NPU Model and Sample Input Videos)

```bash
./setup.sh
```

#### Run `dx_app` C++ demos

```bash
./run_demo.sh
```

#### Run `dx_app` python demos

```bash
./run_demo_python.sh
```

**For more details, refer to [dx-runtime/dx_app/README.md](/dx-runtime/dx_app/README.md).**

---

### dx_stream

#### Installation Path

1. **On the Host Environment:**
   ```bash
   cd ./dx-runtime/dx_stream
   ```
2. **Inside the Docker Container:**
   ```bash
   docker exec -it dx-runtime-<ubuntu_version> bash
   cd /deepx/dx-runtime/dx_stream
   ```

#### Setup Assets (Precompiled NPU Model and Sample Input Videos)

```bash
./setup.sh
```

#### Run `dx_stream`

```bash
./run_demo.sh
```

**For more details, refer to [dx-runtime/dx_stream/README.md](/dx-runtime/dx_stream/README.md).**

---

## Run DX-Compiler

### dx_com

#### Installation Path

1. **On the Host Environment:**
   ```bash
   cd ./dx-compiler/dx_com
   ```
2. **Inside the Docker Container:**
   ```bash
   docker exec -it dx-compiler-<ubuntu_version> bash
   # cd /deepx/dx-compiler/dx_com
   ```

#### Run `dx_com` using Sample onnx input

Sample models are automatically downloaded to `./dx-compiler/dx_com/sample_models/` during installation.
Run the following from the `./dx-compiler/dx_com/` directory.

**Compile all sample models at once (recommended):**

```bash
../example/3-compile_sample_models.sh
```

**Or compile individual models manually:**

```bash
# Activate virtual environment
source ./dx-compiler/venv-dx-compiler-local/bin/activate

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


**For more details, refer to [dx-compiler/source/docs/02_02_Installation_of_DX-COM.md](/dx-compiler/source/docs/02_02_Installation_of_DX-COM.md).**
