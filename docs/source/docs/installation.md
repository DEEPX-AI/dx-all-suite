
DX-ALL is a tool for creating an environment to validate and utilize DEEPX devices. DX-ALL provides the following three methods for setting up the integrated environment:

- Docker: Build a DX-ALL environment within a Docker environment, or load a pre-built image to create a container.
- Local Installation: Set up the DX-ALL environment directly on the host environment (maintaining compatibility between the individual tools).
- Manual Installation: Build each tool individually to create the environment.

## Prerequisites

### Clone main repository

```
$ git clone --recurse-submodules git@github.com:DEEPX-AI/dx-all-suite.git
```

### (Optional) Initializing and updating submodule in an already cloned repository
```
$ git submodule update --init --recursive
```

### Check submodule status
```
$ git submodule status
```

### setup assets (DEEPX)
- dx_app
    ```
    $ cd dx-runtime/dx_app
    $ ./get_assets.sh
    ```

- dx_stream
    ```
    $ cd dx-runtime/dx_stream
    $ ./setup_dxnn_assets.sh
    ```

### (Optional) Install Docker & Docker compose
```
$ ./scripts/install_docker.sh
```

---

## Docker installation

When using a Docker environment, the NPU driver must be installed on the HOST system.
```
$ ./install.sh --target dx_rt_npu_linux_driver
```

### (Optional) Build DX-ALL Docker image 

```
$ ./docker_build.sh
```

### Load image

TBD

### Run continer
- **(Optional) The dxrt service must be stopped before creating a Docker container.**
    ```
    sudo systemctl stop dxrt.service
    ```

- creating a Docker container

    ```
    $ docker compose -f docker/docker-compose.yml up -d
    ```
- exec container
    ```
    $ docker exec -it dx-runtime bash
    ```
- check installation
    ```
    # dxrt-cli -s

    DXRT v2.6.3
    =======================================================
    * Device 0: M1, Accelator type
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
    dvfs Disabled
    =======================================================
    ```

---

## Host installation

To install DEEPX products directly on the host PC without using a Docker environment, individual installation of software components is required, while maintaining compatibility between them. This section describes how to set up the integrated development environment on the host environment, automatically maintaining software compatibility.

### Install All Packages (without fw update)
```
$ ./install.sh --all
```

### Selective Installation of Specific Packages
```
$ ./install.sh --target <package name>
```
- for update dx_fw
    ```
    $ ./install.sh --target dx_fw
    ```
    It is recommended to shut down the system completely and turn off the power entirely before rebooting after firmware update.

---

## Manual installation

This section describes the process of setting up the integrated validation environment by individually installing the DEEPX software components.

모듈별 설치 방법 각 모듈의 User Guide 링크
