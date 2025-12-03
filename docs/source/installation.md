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

#### Python Virtual Environment (Recommended)

The installation scripts will install Python packages via pip. To avoid conflicts with system packages and maintain a clean environment, it is strongly recommended to use a Python virtual environment:

```bash
# Create a virtual environment
python -m venv dx-venv

# Activate the virtual environment
source dx-venv/bin/activate  # On Linux
# or
dx-venv\Scripts\activate  # On Windows

# Verify the virtual environment is active
which python
# Should show: /path/to/dx-venv/bin/python
```

After activating the virtual environment, proceed with the installation steps below.

---

## Local Installation

### Install DX-Compiler Environment (dx_com)

The `DX-Compiler` environment provides prebuilt binary outputs and does not include source code. Each module can be downloaded and installed from a remote server using the following command:

```bash
./dx-compiler/install.sh
```

When executing the above command, DEEPX Developers' Portal ([https://developer.deepx.ai](https://developer.deepx.ai)) account authentication is required to download and install the DX-Compiler modules.

To obtain Developer Portal credentials: Please send an email to [sales@deepx.ai](mailto:sales@deepx.ai) with the following information:

- Company/Organization name
- Your job title

The script obtains authentication information based on the following priority:

1.  **Directly specify when executing the command (1st priority):**
    ```bash
    ./dx-compiler/install.sh --username=<your_email> --password=<your_password>
    ```
2.  **Use environment variables (2nd priority):**

    ```bash
    export DX_USERNAME=<your_email>
    export DX_PASSWORD=<your_password>
    ./dx-compiler/install.sh
    ```

    Alternatively, you can add account information to `compiler.properties` as shown below, which will be injected as environment variables:

    ```bash
    DX_USERNAME=<your_email>
    DX_PASSWORD=<your_password>
    ```

3.  **Prompt for input (3rd priority):**
    If neither of the above methods is used, the script will prompt you to enter your account information directly in the terminal during execution.

Upon successful installation:

1.  The `dx-com` module archive files (`.tar.gz`) will be downloaded and saved to:

    - `./workspace/release/dx_com/download/dx_com_M1A_v[VERSION].tar.gz`

2.  The downloaded modules will be extracted to:

    - `./workspace/release/dx_com/dx_com_M1A_v[VERSION]`
    - Symbolic links will also be created at `./dx-compiler/dx-com`.

#### Archive Mode (--archive_mode=y)

The `--archive_mode=y` option is primarily used when building Docker images for the `dx-compiler` environment with `docker_build.sh`. When this mode is activated, only the download of the module's `.tar.gz` file proceeds; no extraction or symbolic link creation is performed.

```bash
./dx-compiler/install.sh --archive_mode=y
```

When executing the above command, the module archive files (`*.tar.gz`) will be downloaded and saved to:

- `../archives/dx_com_M1A_v[VERSION].tar.gz`

These archive files can then be utilized by the Docker image build process.

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

#### Sanity check

```bash
./dx-runtime/scripts/sanity_check.sh
```

You can use this command to verify that `dx_rt` and `dx_rt_npu_linux_driver` are installed correctly.

**It is recommended to completely shut down and power off the system before rebooting after a firmware update.**

---

## Installation Using Docker

### Install DX-Compiler, DX-Runtime, and DX-ModelZoo Environment

#### Notes

##### 1. When using a Docker environment, the NPU driver must be installed on the host system:

```bash
./dx-runtime/install.sh --target=dx_rt_npu_linux_driver
```

##### 2. The `docker_run.sh` script automatically detects if `dxrtd` (service daemon) is already running on the host or in another container.

By default, the dx-runtime container starts its own dxrtd service. If dxrtd is already running elsewhere, the script will prevent container startup and provide three solutions:

###### Solution 1: Use --disable_dxrt_service option (Recommended)

Use the existing dxrtd service on the host or another container by adding the `--disable_dxrt_service` option:

```bash
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04 --disable_dxrt_service
```

This is the simplest solution and doesn't require stopping services or modifying configuration files.

###### Solution 2: Modify docker-compose.yml

Update the `docker/docker-compose.yml` to prevent dxrtd from starting inside the container:

- Before:

```yaml
  dx-runtime:
    container_name: dx-runtime-${BASE_IMAGE_NAME}-${OS_VERSION}
    image: dx-runtime:${BASE_IMAGE_NAME}-${OS_VERSION}
    ...
    restart: on-failure
    devices:
      - "/dev:/dev"                           # NPU / GPU / USB CAM
```

- After:

```yaml
  dx-runtime:
    container_name: dx-runtime-${BASE_IMAGE_NAME}-${OS_VERSION}
    image: dx-runtime:${BASE_IMAGE_NAME}-${OS_VERSION}
    ...
    restart: on-failure
    devices:
      - "/dev:/dev"                           # NPU / GPU / USB CAM

    entrypoint: ["/bin/sh", "-c"]             # ADDED
    command: ["sleep infinity"]               # ADDED
```

###### Solution 3: Stop external dxrtd and run inside container

Stop the dxrtd service running on the host, then run the container normally:

```bash
sudo systemctl stop dxrt.service
./docker_run.sh --target=dx-runtime --ubuntu_version=24.04
```

##### 3. To run multiple DX-Runtime containers simultaneously, use the `--disable_dxrt_service` option for containers that should use an external dxrtd service.

**Workflow Diagram: dxrtd Conflict Detection and Resolution**

![dxrtd Workflow Diagram](img/dxrtd-workflow.svg)

**Key Points:**
- **With `--disable_dxrt_service`**: Container requires external dxrtd (on host or another container)
- **Without option (default)**: Container starts its own dxrtd, blocks if dxrtd already exists
- **Automatic detection**: Script checks for conflicts before starting containers
- **Multiple containers**: Use `--disable_dxrt_service` for additional containers sharing one dxrtd instance

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

The `docker_run.sh` script automatically checks for dxrtd conflicts before starting containers. If dxrtd is already running on the host or in another container, the script will provide solutions to resolve the conflict.

For the recommended approach using the `--disable_dxrt_service` option, refer to note [#2](#2-the-docker_runsh-script-automatically-detects-if-dxrtd-service-daemon-is-already-running-on-the-host-or-in-another-container).

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

#### Run `dx_app`

```bash
./scripts/run_detector.sh
fim ./result-app1.jpg
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

```bash
make
dx_com/dx_com \
        -m sample/MobileNetV1-1.onnx \
        -c sample/MobileNetV1-1.json \
        -o sample/MobileNetV1-1
        -o sample/MobileNetV1-1
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:06<00:00,  7.00s/model ]

dx_com/dx_com \
        -m sample/ResNet50-1.onnx \
        -c sample/ResNet50-1.json \
        -o sample/ResNet50-1
        -o sample/ResNet50-1
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:19<00:00, 19.17s/model ]

dx_com/dx_com \
        -m sample/YOLOV5-1.onnx \
        -c sample/YOLOV5-1.json \
        -o sample/YOLOV5-1
        -o sample/YOLOV5-1
Compiling Model : 100%|███████████████████████████████| 1.0/1.0 [00:47<00:00, 47.66s/model ]
```

**For more details, refer to [dx-compiler/source/docs/02_02_Installation_of_DX-COM.md](/dx-compiler/source/docs/02_02_Installation_of_DX-COM.md).**
