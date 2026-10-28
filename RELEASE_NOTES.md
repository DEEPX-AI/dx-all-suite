## DX-AllSuite v2.5.0 / 2026-10-23

- DX-Compiler: v2.5.0
    - DX-COM: v2.5.0
    - DX-TRON: Removed
- DX-Runtime: v2.5.0
    - DX_FW: v2.7.6
    - NPU Driver: v2.7.0
    - DX-RT: v3.5.0
    - DX-STREAM: v3.2.0
    - DX-APP: v3.3.0
- DX-ModelZoo: v1.0.0
- DX-K8s-Device-Plugin: v0.1.0

---

Here are the **DX-AllSuite v2.5.0** Release Notes.

### What's New?

This release changes both **how you install and deploy** the DEEPX SDK and **what you can build with it**. Prebuilt container images are now published to the GitHub Container Registry, DX-Compiler and DX-Runtime can be installed with a single `curl | sh` command or from the DEEPX apt repository, and DEEPX DX-M1 NPUs can now be scheduled on Kubernetes. On the module side, DX-COM post-processing runs up to **1.9× faster** on ARM hosts and covers more model families, DX-ModelZoo reaches **v1.0.0** with **497 models**, DX-APP adds **multi-model graphs**, and DX AI Studio gets a **renewed UI**.

It also retires **Ubuntu 18.04** and **DX-TRON** — please read the notice below before upgrading.

> **Important notice: Ubuntu 18.04 and DX-TRON are no longer supported**
>
> - **Ubuntu 18.04 (Bionic Beaver)** has been dropped from the install scripts and Docker builds. The minimum supported version is now **Ubuntu 20.04**.
> - **DX-TRON** has been removed from DX-Compiler as of v2.5.0. To inspect the compiled model structure and the CPU/NPU workload split, generate the interactive HTML **Compilation Summary Report** with DX-COM (`--export_html`).

#### New: Prebuilt container images on GHCR

**DEEPX AllSuite images are now published to the GitHub Container Registry** — pull one instead of building the suite yourself.

| Image | Tags | Platforms |
|---|---|---|
| `ghcr.io/deepx-ai/dx-runtime` | `rt`, `rt-app`, `rt-stream`, `rt-app-stream`, `latest` (+ immutable `v<ver>-…`) | `linux/amd64`, `linux/arm64` |
| `ghcr.io/deepx-ai/dx-compiler` | `latest` (+ immutable `v<ver>`) | `linux/amd64` |
| `ghcr.io/deepx-ai/dx-modelzoo` | `latest` (+ immutable `v<mz-ver>`) | `linux/amd64` |

```bash
docker pull ghcr.io/deepx-ai/dx-runtime:rt-app-stream
docker pull ghcr.io/deepx-ai/dx-compiler:latest
```

**Learn more** — see [`docker/README.md`](docker/README.md).

#### New: One-line install

Install DX-Compiler or DX-Runtime without cloning this repository:

```bash
# DX-Compiler (x86_64 Host PC)
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-compiler/main/oneline-install.sh | sh

# DX-Runtime (target device: NPU driver + dx_rt + firmware)
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-install.sh | sh
```

- Pin versions with `DX_VERSION` (DX-Compiler) or `DX_RT_VERSION` / `DX_DRIVER_VERSION` / `DX_FW_VERSION` (DX-Runtime).
- Matching `oneline-uninstall.sh` scripts remove each install; the DX-Runtime uninstaller also removes an `install.sh` install.
- DX-Runtime one-line install covers `dx_fw`, `dx_rt`, and `dx_rt_npu_linux_driver`; `dx_app` and `dx_stream` still use the full installation guide.
- **Note:** the DX-Runtime one-line install downloads artifacts that are **not checksum-verified**, and each component tracks its own `main` branch, so a run between releases may install an unvalidated combination. Use the version pins or `install.sh` when you need a known-good set.

#### New: DEEPX apt repository

The NPU driver and runtime can now be installed from the DEEPX apt repository:

```bash
wget -O - https://apt.releases.deepx.ai/gpg | sudo gpg --dearmor -o /usr/share/keyrings/deepx-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/deepx-archive-keyring.gpg] https://apt.releases.deepx.ai $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") main" | sudo tee /etc/apt/sources.list.d/deepx.list

sudo apt update
sudo apt install dxrt-driver-dkms
sudo apt install libdxrt-bin
```

#### New: Kubernetes support

**DEEPX DX-M1 NPUs can now be scheduled on Kubernetes (k3s)** through the new `dx-npu` Helm chart and the [`dx-k8s-device-plugin`](dx-k8s-device-plugin) submodule (v0.1.0).

**Highlights**
- **Device plugin** — advertises `deepx.ai/dx-m1` as a schedulable resource; pods request it with `deepx.ai/dx-m1: 1`.
- **CDI injection** — the device nodes (`/dev/dxrtN`) and host libraries are injected into the pod by containerd via CDI.
- **Node labeling** — a NodeFeatureRule labels NPU nodes through node-feature-discovery (optionally installed by the chart with `nfd.enabled=true`).
- **Published OCI chart** on GHCR:
  ```bash
  helm install dx-npu oci://ghcr.io/deepx-ai/charts/dx-npu \
    -n dx-system --create-namespace --set nfd.enabled=true
  ```

**Learn more** — see the [Kubernetes Quickstart](docs/source/06_Kubernetes_Quickstart.md), [Kubernetes Beginner Guide](docs/source/07_Kubernetes_Beginner_Guide.md), and [`deploy/k8s/README.md`](deploy/k8s/README.md).

#### New: Faster post-processing and broader model coverage in DX-COM

**Highlights**
- **Up to 1.9× higher throughput for more model families** — `dx_com.pre_optimize()` now covers pose estimation (YOLOv8/v9/v11/v12/v13 and YOLO26), YOLO26 segmentation, and RTMDet (S/M/L/X) detection. It narrows candidates with TopK before running Sigmoid, DFL decoding, and NMS pre-filtering, so CPU post-processing no longer bottlenecks the NPU on CPU-constrained hosts such as ARM.

  | Model | Before | After | Speed-up |
  |---|---|---|---|
  | RTMDet-S (detection) | 156.56 FPS | 290.16 FPS | 1.9× |
  | YOLOv8n (pose) | 268.98 FPS | 400.59 FPS | 1.5× |
  | YOLO26n (segmentation) | 130.82 FPS | 195.05 FPS | 1.5× |
  | YOLO26n (pose) | 242.77 FPS | 304.38 FPS | 1.3× |

  *Measured on DEEPX DX-M1 with an ARM Cortex-A53 host CPU.*
- **Segmentation Q-Master (QAT)** — Quantization-Aware Training now supports dense segmentation models (binary and multi-class), extending accuracy recovery beyond classification and detection.
- **3D convolution on the NPU** — `Conv` / `ConvTranspose` with 5D inputs now run on the NPU instead of falling back to the CPU.
- **Wider ONNX coverage** — matmul-style two-input `Einsum` and 2-D `Gather` indices are now supported, so more models compile without manual graph edits.

**Learn more** — see the DX-Compiler user manual (`02_09_Pre_Optimize_API.md`).

#### New: DX-ModelZoo v1.0.0

**DX-ModelZoo reaches v1.0.0 with 497 models**, adding new model families and stronger validation for evaluation and compilation.

**Highlights**
- **Expanded model coverage** — YOLO26 depth, pose, classification, and segmentation; PaddlePaddle models; CLIP image and text encoders; anomaly detection and person re-identification.
- **New datasets and evaluation** — including MVTec AD for anomaly detection.
- **Safer evaluation runs** — dataset integrity validation and model input contract validation catch broken datasets and mismatched inputs before evaluation starts.
- **Compile profiles applied end-to-end** — compile profile parameters are now passed through to `dx_com.compile()`.

#### New: DX-APP multi-model graphs and a larger example set

DX-APP v3.3.0 runs several models in one graph and ships examples for 147 newly registered DX-ModelZoo models.

**Highlights**
- **Multi-model graph** — `multi_model_graph_sync` and `multi_model_graph_async`, with `--check`, `--list-models`, and `--report`.
- **147 new DX-ModelZoo examples** — RT-DETR, YOLOv12, YOLOv13, pre-optimized YOLO, anomaly detection, image matting, CLIP retrieval, person re-identification, and visual place recognition.
- **DX-RT v3.5.0 or later** — DX-ModelZoo `.dxnn` files are container format v9.

#### New: DX AI Studio v0.1.1

DX AI Studio renews the home screen and adds a graph composer inside DX App.

**Highlights**
- **New home** — the orbital launcher is now a prompt (*Describe anything. Run it on DX-M1.*), with light, dark, and system themes.
- **Graph Composer** — several models and logic blocks in one graph, checked while you edit, run once or live, and exported as a standalone C++ project. Nine scenario templates are included.
- **Larger catalog** — 497 variants across 29 tasks (348 → 497). 492 of them run in Graph Composer. Run Demo covers 26 demos with live FPS.
- **DX Cloud** — ninth module, for AWS Compiler and AWS Greengrass.

---

### Key Updates

**Performance & Efficiency**

- **GPU preprocessing on ARM**: New OpenGL ES transform backend with DMA-BUF zero-copy offloads crop, resize, letterbox, and color conversion to the GPU. On Raspberry Pi 5 with a 1080p30 camera (NV12 1920x1080 → RGB 640x640), CPU usage drops from **95.2% to 4.8%** (DX-STREAM).
- **Throughput auto-tuning**: `dxrun --max-throughput` automatically finds the I/O buffer count that maximizes throughput on your system, replacing manual trial and error (DX-RT).
- **Faster input path**: float32 → int8 input quantization now runs on NEON/SSE4.1 SIMD kernels, reducing the DMA write time of each inference (DX-RT).
- **Clearer latency metrics**: New E2E Response Time and Core Latency APIs (C/C++/Python) separate on-NPU time from buffer-pool and queue wait time, making bottlenecks easier to locate (DX-RT).
- **Lower idle power**: NPU power gating in power-save mode reduces idle power by about 5–10% (DX_FW).
- **Smaller model packages**: `extract_model_package.sh` copies only the `common/` files a model depends on; use `--no-prune` for the previous full copy (DX-APP).

**New Features & Tools**

- **DX-AS (Docker)**: GPU acceleration options for `docker_run.sh` (Ubuntu-based images only):
    - `--nvidia_gpu` (with optional `--cuda_version`, default `12.8.1`) — runs **dx-compiler / dx-modelzoo** with NVIDIA GPU. Requires `nvidia-container-toolkit`.
    - `--intel_gpu_hw_acc` — runs **dx-runtime** with Intel GPU VA-API media acceleration. Requires `/dev/dri`.
- **DX-AS (CI)**: Release workflow publishes the suite images and the `dx-npu` Helm chart to GHCR on tag push.
- **DX-Compiler**: `install.sh` now installs Python packages with uv when it is available, resolving and installing dependencies much faster than pip. `--uv=true` bootstraps uv automatically if it is missing; the installer falls back to pip otherwise.
- **DX-Compiler**: New `--use_gpu` / `use_gpu` option runs quantization on GPU (default, when available) or forces CPU. Select a specific GPU with `CUDA_VISIBLE_DEVICES`.
- **DX-Compiler**: New `--verbose` / `verbose` option expands masked error messages with the original cause, making compilation failures faster to diagnose.
- **DX-Compiler**: Q-Master (QAT) settings are now passed as a single `QMasterConfig` object exported from `dx_com`, replacing four separate Python arguments.
- **DX-RT**: Support for the V9 `.dxnn` container format, including PPU data transfer.
- **DX-RT**: `import dx_engine` now detects a mismatch between the Python package and `libdxrt.so` at import time, instead of failing later at runtime.
- **DX-RT**: New device-removed error (`DXRT_ERR_DEVICE_REMOVED` / `DeviceRemovedException`) lets applications handle a removed NPU explicitly.
- **DX-RT**: C# now uses the C API via P/Invoke — no .NET SDK or msbuild is needed to build DX-RT. Also adds fan control modes and per-engine control of the model info banner.
- **DX-STREAM**: Added DX-H1 V-NPU hardware-accelerated decode, encode, transform, and inference (`dxvnpudec`, `dxvnpuenc`, `dxinfer`; requires the upcoming DX-H1 V-NPU SDK).
    - The DX-H1 V-NPU SDK is being prepared for distribution through an official repository. To request a beta version for testing, contact the DEEPX CS team.
- **DX-STREAM**: Added YOLO26 depth-estimation and Raspberry Pi camera (`libcamerasrc`) demo pipelines.
- **DX-APP**: Multi-model graph CLIs (`multi_model_graph_sync`, `multi_model_graph_async`) with `--check`, `--list-models`, and `--report`.
- **DX-APP**: 147 DX-ModelZoo models and examples, including RT-DETR, YOLOv12, YOLOv13, pre-optimized YOLO, anomaly detection, image matting, CLIP retrieval, person re-identification, and visual place recognition.
- **DX-APP**: Eight new `dx_postprocess` classes (RT-DETR, anomaly detection, PP-Matting, CLIP text, and more), so these models can use the C++ post-processor from Python.
- **DX AI Studio**: Prompt home, light/dark/system themes, and a single icon set. The orbital launcher and emoji in the UI are gone.
- **DX AI Studio**: DX App Graph Composer, Run Demo (26 demos, live FPS), Model Zoo catalog of 497 variants / 29 tasks (492 runnable in Graph Composer), and DX Cloud (AWS Compiler, AWS Greengrass).

**Stability & Fixes**

- **Firmware & Driver**:
    - Fixed mailbox ACK starvation and LPDDR5X clear logic; hardware operation timeouts are now reported as NPU hangs (2 s HW / 3 s SW timeout), and recovery from EQ failures was added (DX_FW).
    - Fixed occasional latency spikes while the driver unmaps memory after receiving inference output from the NPU. Average performance was unaffected, but individual inferences could be unusually slow (NPU Driver).
    - The driver now signals the endpoint once probe completes, giving the PCIe link a stabilization window after link-up and reducing endpoint load. Firmware older than v2.7.0 skips this step, so compatibility is unaffected (NPU Driver).
- **Runtime Reliability**:
    - Fixed a segfault when PPU outputs are empty, a deadlock/heap corruption on service shutdown, and a busy-spin during teardown after device identification failures (DX-RT).
    - Fixed `dxrtd` NPU memory leaks on abnormal exit, Windows service crashes and stalls, and `find_package(dxrt)` failures on Windows (DX-RT).
    - Prevented latency statistics from overflowing in long-running sessions (DX-RT).
    - `dxrun` now fails clearly when no inference succeeds and rejects invalid `--loops` / `--time` values (DX-RT).
- **Application Accuracy**:
    - Fixed `dx_postprocess` results that differed from the Python and C++ examples — VitPose keypoints placed at 1/4 of their position, double softmax in classification, and per-class instead of class-agnostic NMS for DAMO-YOLO and NanoDet (DX-APP).
    - Fixed Python examples ignoring the model's `score_threshold`, and YOLOv7 PPU boxes decoded with YOLOv5 anchors (DX-APP).
    - Fixed async runners calling a shared post-processor from multiple threads at once (DX-APP).
- **Stream Stability**: Improved OC-SORT tracking reliability across observation history, association, momentum weighting, and invalid predictions (DX-STREAM).
- **Compiler Installer**:
    - When `--python_version` is not given, `install.sh` now uses the OS default `python3` instead of the newest interpreter found on the host, so the environment is no longer built on an unintended Python version (DX-Compiler).
    - Upgrading removes leftover `dx_tron/` directories, and passing the removed `--target=dx_tron` now fails with an explicit migration message instead of a generic "invalid target" error (DX-Compiler).
- **DX-ModelZoo**: Strengthened dataset structure, file, and label validation, and improved consistency of model metadata and compile configurations.

**Deprecations & Removals**

- **DX-AS**: Ubuntu 18.04 support ended; minimum supported Ubuntu version is now 20.04.
- **DX-Compiler**: DX-TRON removed. Use the DX-COM Compilation Summary Report (`--export_html`).
- **DX-Compiler**: The `quantization_device` JSON field and Python argument are deprecated and ignored. Use `use_gpu` and `CUDA_VISIBLE_DEVICES` instead.
- **DX-RT**: The C++/CLI C# package was removed; C# uses the C API via P/Invoke.
- **DX-STREAM**: The SCRFD500M PPU and YOLOv5Pose PPU demos were removed.
- **DX-ModelZoo**: The public `--use-gpu` CLI option was removed.

**Supported Environments**

- **DX-Runtime**: The NPU driver and firmware are supported on bare-metal hosts with the NPU installed. Virtual machines with PCI passthrough are not supported; install DX-Runtime on the physical host. (DX-Compiler and DX-ModelZoo do not require the NPU and can run in a VM or container.)

---

### Known Issues

- **PReLU Degradation**: Significant FPS degradation is still observed in models using PReLU as an activation function. Use `LeakyRelu` or `Relu` where possible until this is resolved in a future release.

---

### Migration Guide

- **Ubuntu 18.04 users**: Upgrade the host OS to Ubuntu 20.04 or later before installing v2.5.0.
- **DX-TRON users**: Replace DX-TRON with the HTML Compilation Summary Report generated by DX-COM (`--export_html`). Remove `--target=dx_tron` from install scripts and CI jobs. On Debian/Ubuntu hosts, remove a previously installed DX-TRON package manually with `sudo apt-get remove dxtron`.
- **Docker users**: Instead of running `docker_build.sh`, you can pull the prebuilt images from `ghcr.io/deepx-ai/*`. Use lowercase `deepx-ai` in the registry path — GHCR rejects uppercase repository names.
- **DX-COM Python/QAT users**: Call `dx_com.compile()` with keyword arguments. Replace `quantization_mode`, `qat_config`, `qat_skip_training`, and `qat_resume_from_checkpoint` with a single `qmaster=QMasterConfig(...)`; the former arguments are no longer honored. QAT triggered from a JSON `qmaster` block is unchanged.
- **DX-COM `pre_optimize` users**: Rename `yolo_postprocess` → `yolo_dfl_postprocess` and `yolo26_postprocess` → `yolo_no_dfl_postprocess` (the old names raise an error). Add the required `task` key (`base`, `seg`, or `pose`) and remove `input_height` / `input_width` (supplying them raises `ValueError`). `pre_optimize` and `ppu` are mutually exclusive: if both are present, DX-COM compiles with `ppu` and silently drops `pre_optimize`, so remove the `ppu` block when migrating.
- **DX-COM config users**: Remove the deprecated `quantization_device` field from existing configs. Pass only `True` or `False` to `use_gpu`; any other value (including `None`) falls back to a legacy path that skips `pre_optimize` and ignores `verbose`.
- **DX-ModelZoo users**: The compile YAML key `compile.quantization` was renamed to `compile.calibration`. Update custom compile YAML files. The public `--use-gpu` option was removed.
- **DX-RT users**: DX-RT v3.5.0 now requires NPU Driver v2.7.0+, PCIe Driver v2.7.0+, and Firmware v2.7.6+. Update them before upgrading.
    - `GetLatency*` now returns the E2E Response Time. Use `GetCoreLatency*` for latency that excludes buffer-pool and queue wait time.
    - `import dx_engine` raises `RuntimeError` if the Python package and `libdxrt.so` major.minor versions differ. Install matching versions (bypass: `DX_ENGINE_SKIP_VERSION_CHECK=1`).
    - C# users: switch from the removed C++/CLI package to the C API via P/Invoke (see `examples/csharp/README.md`).
- **DX-STREAM users**: The retired SCRFD500M PPU and YOLOv5Pose PPU demos/launchers were removed; update any automation or test scripts calling them. Replace the retired EfficientNet-Lite0 256x256 model with the supported 224x224 model in secondary pipelines.
    - V3 DSP users: build with `./build.sh --dxv3` to keep DSP acceleration; without the backend plugin, the software path is used.
- **DX-APP users**: Update scripts that use the old example paths, executable names, or task names. `classification` is now `image_classification`, `obb_detection` is `oriented_object_detection`, and `embedding` is split into `face_recognition`, `image_retrieval`, `visual_place_recognition`, and `zero_shot_image_classification`. Container v9 `.dxnn` files require DX-RT v3.5.0 or later.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

## DX-AllSuite v2.4.3 / 2026-09-03

- DX-Compiler: v2.4.2
    - DX-COM: v2.4.1
    - DX-TRON: v2.0.1 (Deprecated)
- DX-Runtime: v2.4.2
    - DX_FW: v2.7.4
    - NPU Driver: v2.6.0
    - DX-RT: v3.4.2
    - DX-STREAM: v3.1.2
    - DX-APP: v3.2.2

---

Here are the **DX-AllSuite v2.4.3** Release Notes.

### What's New?

This release updates **DX-Compiler to v2.4.2**, which bundles **DX-COM v2.4.1** with a smaller compiled `.dxnn` output and minor stability fixes. DX-Runtime remains at v2.4.2.

It also addresses the availability of previous DX-COM releases on PyPI — please read the notice below if you pin `dx-com` to an older version.

> **Important notice: DX-COM v2.4.0 and v2.3.0 are no longer available on PyPI**
>
> The `dx-com` **2.4.0** and **2.3.0** distributions were inadvertently removed from PyPI. Because PyPI does not allow a deleted version to be re-uploaded, these two versions **can no longer be installed via `pip`**.
>
> - **Highly Recommended:** upgrade to **DX-COM v2.4.1**, which is available on PyPI and is the version bundled with this release.
> - **If you specifically need v2.4.0 or v2.3.0** (e.g., to reproduce existing `.dxnn` outputs), download the wheel from the DEEPX Developer Portal: <https://developer.deepx.ai/sw-download/>

---

### Key Updates

**Performance & Efficiency**

- **DX-COM**: Removed redundant metadata from the compiled `.dxnn` output, reducing model file size.

**Stability & Fixes**

- **DX-COM**: Minor bug fixes and stability improvements.

---

### Migration Guide

- **Users pinning `dx-com==2.4.0` or `dx-com==2.3.0`**: `pip install` will fail for these versions. Update your requirements/lock files to `dx-com==2.4.1` (or `dx-com>=2.4.1`), or install the wheel manually from <https://developer.deepx.ai/sw-download/>.
- **DX-Compiler installer users**: Re-run `install.sh` with the v2.4.3 archive; the installer now targets DX-COM v2.4.1.

For detailed updated items, refer to **each environment & module's Release Notes**.

---
## DX-AllSuite v2.4.2 / 2026-08-14

- DX-Compiler: v2.4.1
    - DX-COM: v2.4.0
    - DX-TRON: v2.0.1 (Deprecated)
- DX-Runtime: v2.4.2
    - DX_FW: v2.7.4
    - NPU Driver: v2.6.0
    - DX-RT: v3.4.2
    - DX-STREAM: v3.1.2
    - DX-APP: v3.2.2

---

Here are the **DX-AllSuite v2.4.2** Release Notes.

### What's New?

This hotfix release resolves centralized runtime sanity checks, Windows build and packaging reliability (DX-RT), depth-estimation and depth-map metadata/rendering in DX-STREAM, and DX-APP demo and model updates including YOLO26-Depth examples.

It also adds **DX-Edge**, the AWS-native documentation set for deploying DEEPX NPUs through AWS Marketplace.

#### New: DX-Edge — Powered by AWS, available on AWS Marketplace

**DX-Edge (`dx-edge`) documents the AWS-native path from a trained ONNX model to a DEEPX NPU running in the field**, across three tracks published on AWS Marketplace.

**Highlights**
- **DEEPX Greengrass Solution** — a single AWS CloudFormation stack that provisions the cloud compilation pipeline and installs the NPU driver, firmware, `dx_rt`, and `dx_stream` on edge devices over the air (Zero-Touch Provisioning) through AWS IoT Greengrass V2. Both the classic Greengrass nucleus and nucleus lite are supported.
- **DEEPX Compiler Solution** — ONNX → `.dxnn` compilation on AWS, either interactively on an Amazon EC2 instance launched from the AMI, or fully automatically through an event-driven Amazon S3 → AWS Lambda → AWS Step Functions pipeline that starts and terminates the compiler instance per job.
- **AWS HW Path (DX-AIPlayer N97)** — a Getting Started Guide for AWS IoT Greengrass covering the Intel® N97 + DEEPX DX-M1 edge AI system, written to the AWS Device Qualification Program template.
- **Bilingual** — every document is published in English and Korean.

**Learn more** — see [`dx-edge/README.md`](dx-edge/README.md).

#### **DX AI Studio (Beta) improvements**
- **Lab Composer** — build, validate, and run inference workflows in one workspace.
- **Plugin workflow** — scaffold custom plugins and export reusable Lab packages.
- **Batch runs** — follow asynchronous inference jobs with live progress and result status.
- **Runtime diagnostics** — improved bootstrap and structured debug logging simplify setup and troubleshooting.

---

### Key Updates

**Performance & Efficiency**

- **DX-RT**: Improved MSVC build log by resolving Windows build warnings; Windows packaging/staging idempotency reduces unnecessary rebuilds and reconfigure failures; Ninja-forced wheel builds avoid Visual Studio generator detection issues on CI.

**Stability & Fixes**

- **DX-RUNTIME(installer)**: Centralized sanity checks into `scripts/sanity_check.sh` prevent divergent driver detection logic between `install.sh` and standalone runs.
- **DX-RT**: Staged generated headers (`gen.h`) into public include path with copy fallback when symlinks are unavailable on Windows.
- **DX-STREAM**: Self-configuring GST_PLUGIN_PATH for Windows pipeline scripts; DX-STREAM and dxosd fixes improve plugin path handling and depth rendering stability on Windows.
- **DX-APP**: Moved SuperPoint point tracking out of keypoint detection post-process into the visualizer; switched depth-estimation demo from Depth-Anything-V2 to YOLO26-Depth-S; used new low-resolution source video (lowres-drone-city-road.mp4) for super-resolution demo; fixed Windows all-build parallelism by consolidating shared-file copies.

**New Features & Tools**

- **DX-RT**: `release.ver` added to Windows DXRT binaries for explicit versioning; recursive copy fallback for vendored headers (cxxopts, rapidjson) on Windows when directory symlinks are unavailable.
- **DX-STREAM**: YOLO26 depth-estimation demo pipeline and depth metadata support to DXFrameMeta and depth-map rendering to dxosd.
- **DX-APP**: YOLO26-Depth examples for all five model sizes (n/s/m/l/x, 768x768) with C++ sync/async plus Python sync/async/sync_cpp_postprocess/async_cpp_postprocess variants; registered 5 yolo26-depth models in `config/model_registry.json` and `scripts/modelzoo_manifest.json`; updated sample video archive to v3.2.2 with low-resolution source for super-resolution demos.

---

## DX-AllSuite v2.4.1 / 2026-08-03

- DX-Compiler: v2.4.1
    - DX-COM: v2.4.0
    - DX-TRON: v2.0.1 (Deprecated)
- DX-Runtime: v2.4.1
    - DX_FW: v2.7.4
    - NPU Driver: v2.6.0
    - DX-RT: v3.4.1
    - DX-STREAM: v3.1.1
    - DX-APP: v3.2.1

---

Here are the **DX-AllSuite v2.4.1** Release Notes.

### What's New?

This release adds **DX-Benchmark (Beta)**, polishes the **DX AI Studio (Beta)** introduced in v2.4.0, includes virtualization support, super-resolution quality improvements, and documentation updates across the suite.

#### New: Reproducible NPU performance benchmarks

**DX-Benchmark (`dx-benchmark`) is now available in Beta** — one standardized procedure that measures YOLO26 performance on any Host PC + NPU combination, published together with results for six hardware environments.

**Highlights**
- **Two measurement tiers** — **Model-Level** (`run_model`): Latency (single-core, sync) and Throughput (multi-core, async); **E2E Pipeline** (DX-STREAM): Single-Stream FPS and Multi-Stream channel capacity.
- **Comparable by construction** — automatic ONNX-Runtime ON/OFF comparison, thermal steady-state normalization with throttle detection, and a full environment fingerprint recorded per run.
- **Published dataset** — 6 hardware environments (H1-Quattro, Intel N97, OrangePi 5+, ROCK 5B+, and Raspberry Pi 5 with M1 / M1M) measured on v2.3.3 and v2.4.0.
- **Interactive dashboard** — self-contained HTML (no CDN) for cross-environment and cross-version comparison; the same dataset backs DX AI Studio's Benchmark view.
- **Performance analysis** — EN/KOR documents covering NPU-bound vs host-bound behaviour, ORT-mode selection, and per-environment deployment guidance.

> **Beta notice:** DX-Benchmark is a Beta release (tool v0.1.0, measurement protocol v1). The CLI and output schema may change.

**Learn more** — see [`dx-benchmark/README.md`](dx-benchmark/README.md) and the [performance analysis](dx-benchmark/docs/ANALYSIS_EN.md).

#### **DX AI Studio (Beta) improvements**
- **Model Zoo** — browse the full model catalog with one-click download (and re-download), in six languages.
- **App demos** — correct, clearer results for classification, pose, and video demos.
- **Stream** — demos and the Pipeline Builder now play reliably in remote / SSH browsers.
- **Compiler** — smoother agentic auto-compile and clearer quantization diagnosis.
- **Benchmark** — refreshed to the latest benchmark dataset.
- **Runtime setup** — guided runtime-profile installation, validation, and rollback make App and Stream startup more reliable.
- **NPU monitoring** — supervised telemetry collection improves status reporting and recovery when monitoring workers fail.

---

### Key Updates

**Stability & Fixes**

- **DX_FW & NPU Driver**: Added VM environment support via MSI IMWR PCIe message API; added kernel 4.4.0 support; fixed forked child process ioctl race condition.
- **DX-RT**: Corrected supported OS list (removed Ubuntu 18.04, added Ubuntu 26.04) and improved documentation clarity.
- **DX-APP**: Fixed RealESRGAN discolored output, removed tile seams in super-resolution, and corrected video/image saving issues in async runners.

**New Features & Tools**

- **DX-RT**: Added bundled wheel installation guide for virtual environments.
- **DX-APP**: Super-resolution now outputs both side-by-side comparison and standalone upscaled images; added `--sr-tile-halo` option for tile overlap control.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

## DX-AllSuite v2.4.0 / 2026-07-22

- DX-Compiler: v2.4.0
    - DX-COM: v2.4.0
    - DX-TRON: v2.0.1 (Deprecated)
- DX-Runtime: v2.4.0
    - DX_FW: v2.7.3
    - NPU Driver: v2.5.1
    - DX-RT: v3.4.0
    - DX-STREAM: v3.1.0
    - DX-APP: v3.2.0

---

Here are the **DX-AllSuite v2.4.0** Release Notes.

### What's New?

This major release focuses on **AI-Powered Development Workflow**, **Next-Generation Quantization**, and **Production-Ready Stability**. The introduction of Agent-Driven Development and advanced quantization techniques make this our most accessible and powerful release to date.

#### New: Build DEEPX NPU apps with natural language

**DEEPX Agent-Driven Development (`dx-agent-dev`) is now available in Beta.**

Describe an app or model task in plain language, and an AI coding agent drives the DEEPX knowledge base from start to finish — **brainstorm → plan → TDD → verify** — taking you from ONNX/`.pt` model compilation all the way to on-device **DX-M1 NPU** deployment.

**Highlights**
- **Natural-language workflow** — turn a plain-language prompt into a working, on-device NPU app.
- **Multi-agent support** — works with Claude Code, Cursor, GitHub Copilot, OpenCode, and Codex.
- **End-to-end coverage** — model compilation (ONNX/`.pt` → `.dxnn`), inference app generation, and DX-M1 NPU deployment.
- **Ultralytics ecosystem** — purpose-built for the Ultralytics model ecosystem on DEEPX NPUs.
- **Reproducible showcases** — every bundled showcase ships with its prompt, measured results, and full build transcript.

> **Beta notice:** `dx-agent-dev` is currently in Beta. Behavior and APIs may change as the feature matures.

**Learn more** — see [Agent-Driven Development docs](docs/source/00_Agent_Driven_Development.md) and the [showcase gallery](dx-agent-dev-showcase/README.md).

#### New: DX AI Studio — one browser workspace for the DEEPX NPU (Beta)

**DX AI Studio is now available in Beta** — an all-in-one desktop web workspace that unifies eight DEEPX tools in a single browser, in six languages.

**Highlights**
- **Eight tools, one hub** — DX App (NPU inference on image/video/camera/RTSP with live multi-stream), DX Stream (real-time GStreamer pipelines with live WebRTC playback), DX Model Zoo (345 models with in-browser demos and one-click `.dxnn`/ONNX downloads), DX Compiler (ONNX → `.dxnn` with a config wizard, quantization tuning/diagnosis, and agentic auto-compile), DX EdgeGuide (board recommendation from real benchmarks), DX Benchmark, DX Monitor (live NPU telemetry), and DX Agent Dev.
- **Zero dependencies, self-installing** — pure Python standard library; `./launcher.sh` installs, boots every tool, and opens the browser with no manual setup.
- **Runs without hardware** — every tool degrades gracefully to sample/mock data, so the whole studio is browsable with no NPU, SDK, or models.
- **Six languages** and a built-in AI assistant (multi-provider, with a fully-offline local option).

> **Beta notice:** DX AI Studio is a Beta release (studio v0.1.0). Features and UI may change before general availability.

**Learn more** — see the DX AI Studio User Manual (`dx-ai-studio/docs/`).

#### Advanced Quantization & Model Quality

- **Automated Q-PRO Configuration**: DX-COM now automatically generates DXQ combinations for higher-accuracy quantization, removing manual tuning requirements.
- **Quantization-Aware Training (QAT)**: End-to-end QAT support directly through `dx_com.compile()`, enabling fine-grained accuracy optimization.
- **QXNN Resume Flow**: Re-run quantization with different settings without recompiling, dramatically shortening iteration cycles.
- **Quantization Diagnosis HTML Report**: Visualize per-layer quantization quality with actionable recommendations.

#### Expanded Model & Platform Support

- **Massive Model Library**: Support for 347 models across 22 AI task categories, including 5 new tasks (3D Object Detection, Keypoint Detection, Object Pose Estimation, Panoptic Driving Perception, Hand Detection).
- **Extended Platform Coverage**: Python 3.13–3.14 support (DX-COM) and Ubuntu 26.04 validation.
- **Windows Ecosystem**: Full Windows MSVC support for DX-STREAM including build, test suite, and Python bindings.

---

### Key Updates

**Performance & Efficiency**

- **Compiler Optimization**: Faster compilation with reduced memory usage, especially on large models (DX-COM).
- **Stable C ABI**: Prebuilt SDK distribution without recompilation via dxrt_c_api.h (103 functions) and header-only C++ wrapper (dxrt_cxx_api.h) for single-include modern C++ usage (DX-RT).
- **CLI Modernization**: Updated CLI binary names (`dxrt-cli` → `dxcli`, `parse_model` → `dxparse`, `run_model` → `dxrun`) with backward-compatible aliases (DX-RT).
- **IPC Infrastructure**: Shared memory-based inter-process communication using memfd with packet-based protocol layer and cross-platform support for Linux/Windows (DX-RT).
- **Python Ecosystem**: Debian package bundles `dx_engine` Python wheels for Python 3.8–3.14 (DX-RT).

**Stability & Fixes**

- **Firmware & Hardware Stability**:
  - Reverted M1/M1M IC, M.2 module, and DX-H1 Quattro board products PCIe device id to `0x0000` (DX_FW).
  - Adjusted CPU reset delay (20ms → 200ms) to ensure stable PLL lock (DX_FW).
  - Updated OTP Revision for improved hardware identification (DX_FW).
  - Disabled Root Complex Tx Equalization Preset 10 to prevent PCIe link compliance/test loops during normal boot (DX_FW).
  - Changed BAR0 type from prefetchable to non-prefetchable on VNPU board type (DX_FW).
  - Fixed input queue clearing when all bound options are deleted (DX_FW).
  - Solved PCIe enumeration issue on RZ/G3E (DX_FW).
  - Rejected in-flight mailbox commands during FW reboot and hardened recovery sleep (NPU Driver).
  - Fixed device recovery issues after firmware updates; resolved module installation errors in certain hardware environments (NPU Driver).
  - Automatic recovery logic for critical runtime error scenarios (NPU Driver).

- **Compiler Robustness**:
  - Fixed Q-PRO/DXQ quantization crashes and stability issues observed on real models (DX-COM).
  - Fixed Python API integer input handling that caused accuracy degradation (DX-COM).
  - Fixed compilation errors in models with Split, Concat, Reshape, Bilinear Resize, Clip, or odd spatial dimensions (DX-COM).
  - Fixed NumPy 2.4+ and onnxruntime ≥ 1.25.0 compatibility issues (DX-COM).

- **Runtime Reliability**:
  - Fixed critical crash (nullptr) in pyRunBenchmark by ensuring memory lifetime of input buffers (DX-RT).
  - Fixed SEGV in NFHLayer caused by uninitialized profiler instrumentation (DX-RT).
  - Improved shared-memory performance and temperature validation in dxtop (DX-RT).
  - Multiple API refinements: error messages, output formatting, ppcpu logic, multi-input dictionary handling (DX-RT).

- **Stream Stability**:
  - LATENCY reporting: All elements now correctly account for processing time, stabilizing synchronization and QoS behavior (DX-STREAM).
  - FLUSH recovery and push thread lifecycle: Proper reset of queues/threads/state on FLUSH, eliminating hangs on seek/replay (DX-STREAM).
  - Error handling: Replaced `abort()` with proper `GST_ELEMENT_ERROR` messages across all elements (DX-STREAM).

- **Application Fixes**:
  - Super-resolution now preserves input resolution via dynamic tile padding (DX-APP).
  - Fixed `--save` option not producing output files in C++ sync runners for multiple AI tasks (DX-APP).
  - Multiple post-processor fixes: DOPE, YOLOPv2, RetinaFace, Depth Anything V2 normalization (DX-APP).
  - Build fixes: pybind missing includes, Windows x64 library paths, async runner metrics (DX-APP).

**New Features & Tools**

- **Compiler & Quantization**:
  - Interactive HTML graph viewer for model inspection with parameter shapes and CPU/NPU partition reasons (replaces DX-TRON) (DX-COM).
  - `dx_com.pre_optimize()` API for ONNX-level pre-processing transforms with built-in YOLO post-processing integration (detection/segmentation) (DX-COM).

- **Runtime & Monitoring**:
  - H1M firmware compatibility check: distinguish H1M (LPDDR4) from H1 (LPDDR5/LPDDR5X); support mixed 4-pack/6-pack configurations (DX-RT).
  - Device monitoring APIs for memory usage, per-core temperature, and utilization (DX-RT).
  - Profiler enhancements: GetJobMetrics() API for comprehensive per-job profiling and Coefficient of Variation (CoV) metric (DX-RT).
  - HTML visualization tool (plot_html.py) for profiling data (DX-RT).
  - Debian packaging improvements: prebuilt directory structure and `libdxrt-bin` with amd64/arm64 auto-detection (DX-RT).

- **Application Framework**:
  - Native C++ post-processing for model zoo (YOLO families, semantic seg, Face3D, embedding/classification/attribute, restoration, YOLO-PPU), replacing Python fallbacks (DX-APP).
  - Opt-in `--fast-postprocess` path for object detection and instance segmentation (DX-APP).
  - YOLO Customizing Guide documentation (DX-APP).
  - Windows Visual Studio solution package extraction workflow with automatic OpenCV/DXRT CMake dependency configuration (DX-APP).
  - Build enhancements: `--demo-models` download option, minimal/category-based builds, Windows build selection TUI, `--all` flag for full build and install (DX-APP).
  - Knowledge base (`.deepx/`): specialized agents, app-building/SWE skills, and multi-platform agent-instruction generation (CLAUDE/AGENTS/copilot/cursor) via `dx-agent-gen` (DX-APP).
  - 7 new post-processors + pybind bindings (43 → 50 classes), 3 C++ factory interfaces, 3 visualizers for new AI tasks (DX-APP).
  - Per-model Python examples (4 variants: sync/async/sync_cpp_postprocess/async_cpp_postprocess) and C++ examples (sync/async) (DX-APP).

- **Streaming Infrastructure**:
  - Multi-Stream Domain: Introduced `application/x-dxvideoraw` domain caps for unified processing of streams with different resolutions/formats (DX-STREAM).
  - Base class migration: `dxinputselector`/`dxgather` → `GstAggregator` for N:1 multiplexing; `dxvnpuoverlay` → `GstBaseSink` for proper render/preroll lifecycle (DX-STREAM).
  - TransformKernelPool: Automatic src-format-based kernel selection with libyuv fallback for dxscale, dxconvert, dxpreprocess, dxmsgconv (DX-STREAM).
  - InferBackend abstraction: Refactored dxinfer to use Put/Get async pattern with backend property (auto/dxrt/dxvnpu) (DX-STREAM).
  - Windows MSVC build and runtime environment: Full support including dependency check, build, demo launcher, test suite, Python binding (pydxs) (DX-STREAM).
  - Test Suite: 73 new test binaries under `test/base/{element,metadata,pipeline}/` covering element contracts, domain boundaries, end-to-end pipelines (DX-STREAM).
  - DxMsgConv: `include-frame` property for base64 JPEG frame encoding with Kafka/MQTT consumer display support (DX-STREAM).

- **Docker & Deployment**:
  - Red Hat family support for the `dx-compiler` container: build and run on Fedora (42–45), RHEL/UBI (9, 10), and CentOS Stream (stream9, stream10) via new `--fedora_version` / `--rhel_version` / `--centos_version` options. `dx-runtime` and `dx-modelzoo` remain Ubuntu/Debian only (Docker).
  - Ubuntu 26.04 base image support for all three containers (Docker).
  - Faster `dx-runtime` / `dx-modelzoo` image builds: `dx_rt` and the matching `dx_engine` Python wheel are installed from prebuilt Debian packages instead of being compiled from source (Docker).
  - DX-Tron on Red Hat family images is provided as the web variant (`run_dxtron_web.sh`) since the `.deb`/AppImage is not supported there (Docker).

### Known Issues

- **PReLU Degradation**: Significant FPS degradation has been observed in models using PReLU as an activation function.

### Deprecation Notices

- **DX-TRON**: Deprecated as of v2.4.0. Migrate to DX-COM's standalone HTML graph viewer for model visualization.
- **PPU Type 2**: Legacy PPU type 2 post-processing mode is deprecated. Migrate to `dx_com.pre_optimize()` API with built-in YOLO post-processing passes.

### Migration Guide

- **DX-TRON Users**: Replace DX-TRON workflow with the new HTML graph viewer generated by DX-COM.
- **PPU Type 2 Users**: Update compilation workflows to use `dx_com.pre_optimize()` API for YOLO models instead of PPU type 2.
- **NumPy 2.4+ Users**: DX-COM v2.4.0 ensures compatibility with NumPy 2.4+ and onnxruntime ≥ 1.25.0.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

## DX-AllSuite v2.3.3 / 2026-05-14

- DX-Compiler: v2.3.1
    - DX-COM: v2.3.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.3.3
    - DX_FW: v2.5.6
    - NPU Driver: v2.4.1
    - DX-RT: v3.3.2
    - DX-STREAM: v3.0.1
    - DX-APP: v3.1.1

---

Here are the **DX-AllSuite v2.3.3** Release Notes.

### What's New?

This hotfix release resolves a missing Debian package file issue in `dx_rt_npu_linux_driver`. (v2.4.1, packaging fix only).

---

## DX-AllSuite v2.3.2 / 2026-05-11

- DX-Compiler: v2.3.1
    - DX-COM: v2.3.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.3.2
    - DX_FW: v2.5.6
    - NPU Driver: v2.4.1
    - DX-RT: v3.3.2
    - DX-STREAM: v3.0.1
    - DX-APP: v3.1.1

---

Here are the **DX-AllSuite v2.3.2** Release Notes.

### What's New?

This patch release focuses on Debian package and Python build improvements in DX-RT.

- **DX-RT Build Quality**: Removed redundant build artifacts from the Debian package, improved Python extension module linking, and added conditional pip upgrade for legacy OS compatibility.

---

### Key Updates

**Stability & Fixes**

- **DX-RT**: Improved Python extension module linking for `_pydxrt` build.

**New Features & Tools**

- **DX-RT**: Removed redundant build artifacts and temporary directories from the Debian package.
- **DX-RT**: Added conditional pip upgrade (v21.3+) to ensure build stability on legacy OS environments.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

## DX-AllSuite v2.3.1 / 2026-05-06

- DX-Compiler: v2.3.1
    - DX-COM: v2.3.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.3.1
    - DX_FW: v2.5.6
    - NPU Driver: v2.4.1
    - DX-RT: v3.3.1
    - DX-STREAM: v3.0.1
    - DX-APP: v3.1.1

---

Here are the **DX-AllSuite v2.3.1** Release Notes.

### What's New?

This patch release focuses on stability improvements, documentation corrections, license compliance, and firmware stability across the DX-Compiler installer, DX-Runtime, and DX-STREAM modules.

- **Installer Fix (DX-Compiler)**: `uninstall.sh` now properly removes all installed packages and extracted module directories, and supports a new `--target` option for selective uninstallation.
- **Runtime Compatibility (DX-RT)**: Updated pre-built library versions (onnxruntime, openvino) for improved compatibility.

---

### Key Updates

**Stability & Fixes**

- **DX-Compiler Installer**: Fixed `uninstall.sh` not removing installed packages (`dx_com` via `pip3 uninstall`) and the `dxtron` Debian package (`apt-get remove`), and not deleting extracted `dx_com/` and `dx_tron/` directories.
- **DX-RT**: Updated pre-built onnxruntime (1.23.2 → 1.22.0) and openvino (25.4 → 25.1) for improved compatibility.
- **DX-STREAM**: Fixed uninstall not removing apps build directories and pydxs build cache.

**New Features & Tools**

- **DX-Compiler Installer**: Added `--target=<dx_com|dx_tron|all>` option to `uninstall.sh` (default: `all`), consistent with `install.sh`.
- **DX-APP & DX-STREAM**: Added license information for third-party models and datasets.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

## DX-AllSuite v2.3.0 / 2026-04-10

- DX-Compiler: v2.3.0
    - DX-COM: v2.3.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.3.0
    - DX_FW: v2.5.6
    - NPU Driver: v2.4.1
    - DX-RT: v3.3.0
    - DX-STREAM: v3.0.0
    - DX-APP: v3.1.0

---

Here are the **DX-AllSuite v2.3.0** Release Notes.  

### What's New?

This major release focuses on Runtime Efficiency, Security Hardening, and a Unified Application Architecture. Significant optimizations in the YOLO post-processing pipeline and a major overhaul of the DX-STREAM architecture make this our most robust release to date.  

- **TopK-Optimized YOLO Pipeline**: DX-COM v2.3.0 introduces a high-efficiency post-processing pipeline for DFL-based YOLO models, applying TopK filtering before decoding to drastically reduce CPU overhead.  
- **Modular & Sudo-less DX-STREAM (v3.0.0)**: A complete architectural refresh of the streaming module, featuring a new kernel abstraction for hardware backends and a user-friendly installation that no longer requires root privileges.  
- **Unified APP Framework**: DX-APP v3.1.0 establishes a strict 5-layer design pattern, ensuring 1:1 parity between C++ and Python implementations for seamless cross-language development.  
- **Enterprise Linux Support**: DX-COM validation has expanded to include Fedora 42–45, Red Hat 9–10, and CentOS Stream 9–10.  

---

### Key Updates

**Performance & Efficiency**  

- **DFL Post-Processing**: Optimized pipeline for YOLO models decoder reduces CPU workload by filtering candidates via TopK before bounding box decoding.  
- **NPU Latency**: Reduced inference latency for the majority of supported models through compiler optimizations.  
- **Zero-Copy Streaming**: DX-STREAM now supports DMA-Buffer zero-copy in RGA and DXOSD, reducing memory bandwidth usage.  
- **CPU Acceleration**: Introduced optional build-time features for CPU-bound operation acceleration in the runtime.  

**Stability & Fixes**  

- **Hardware Compatibility**: Fixed 64-bit PCIe TLP errors on Raspberry Pi 4 and resolved ARM64 IOMMU DMA coherency bugs.  
- **Multi-Device Handling**: Fixed PPU data transfer errors and IPC exceptions occurring in multi-process/H1/multi-M.2 environments.  
- **Robustness**: Implemented DMA abnormal recovery for improved system resilience and fixed PPU safety via 2-cell memory alignment.
- **Power Saving**: Re-enabled run mode NPU and hardened devMode race.

**New Features & Tools**  

- **Expanded AI Tasks**: Added native support for Depth Estimation (FastDepth) and Image Restoration (DnCNN, Zero-DCE, ESPCN).  
- **Massive Model Zoo**: Integrated 280+ models across 17 categories with 560+ examples, supported by a new manifest-based auto-download system.  
- **Development Tools**: Added `dxtop` for No-Service Mode monitoring and new GStreamer elements (`DxScale`, `DxConvert`) for HW-accelerated scaling and color conversion.  

### Known Issues

- **PReLU Activation**: Significant FPS degradation persists in models using PReLU activation functions.  
- **Accuracy Variability**: Certain models (OSNet, RepVGGA2, YoloV9C) may show accuracy variability depending on the host CPU and calibration dataset.  


### Migration Guide

- **DX-STREAM v3.0.0 (Breaking Change)**: Users must move environment variables from `/etc/profile.d/` to ~/.bashrc. Models are now managed via `dx-modelzoo`; run setup_sample_models.sh to update.  
- **DX-APP v3.1.0**: Project structures have changed to follow the 5-layer pattern. Refer to the new `src/` directory for updated implementation standards.  
- **Minimum Dependencies**: DX-RT v3.3.0 now requires NPU Driver v2.4.0+ and Firmware v2.5.2+ at a minimum.  

For detailed updated items, refer to **each environment & module's Release Notes**.  

---

## DX-AllSuite v2.2.2 / 2026-02-26

- DX-Runtime: v2.2.2
    - DX-APP: v3.0.2
    - DX-STREAM: v2.2.1
- DX-Compiler v2.2.1
    - DX-COM: v2.2.1

---

Here are the **DX-AllSuite v2.2.2** Release Notes.

### What's New?

This release enhances the development experience with GPU-accelerated quantization and improved Windows platform support.

- **GPU-Accelerated Quantization**: DX-COM now supports GPU quantization via JSON configuration with automatic GPU detection, significantly speeding up the compilation process.
- **Enhanced Windows Support**: Improved Windows build stability with automated vcpkg installation and fixed compatibility issues.

---

### Key Updates

**Performance & Efficiency**

- GPU Quantization: Added `quantization_device` support in JSON configuration for CLI-based GPU quantization. Automatic GPU detection falls back to CPU when CUDA is unavailable.
- Windows Build: Automated DLL copying (dxrt, vkpkg) to dx-app/bin directory and added vcpkg installation script for streamlined Windows builds.

**Stability & Fixes**

- Fixed DXQ enhanced quantization option bugs in DX-COM.
- Fixed PPU compilation bug in Python Wheel Package for Python 3.8, 3.9, and 3.10.
- Fixed an issue where compilation proceeded without error when invalid model input names were specified.
- Removed experimental filesystem includes and updated float literals in example cpp files to resolve Windows build errors.
- Refactored apply_argmax to reduce nesting and fix gcovr warnings.

**Known Issues**

- Significant FPS degradation has been observed in models using PReLU as an activation function.

---

## DX-AllSuite v2.2.1 / 2026-02-09

- DX-Runtime: v2.2.1
    - DX-APP: v3.0.1

---

Here are the **DX-AllSuite v2.2.1** Release Notes.

### What's New?

This release focuses on enhancing the YOLO ecosystem with expanded model variant support and improved flexibility in post-processing.

- **Extended YOLO26 Coverage**: Full support for YOLO26 variants including classification, pose estimation, segmentation, and oriented bounding box detection.

---

### Key Updates

**Stability & Fixes**

- Fixed hardcoded attribute size limitation in YOLO post-processing that could cause issues with models having different output configurations.

**New Features & Tools**

- Added yolov26 cls, yolo26 pose, yolo26 seg, yolo26 obb examples

---

## DX-AllSuite v2.2.0 / 2026-01-16

- DX-Compiler: v2.2.0
    - DX-COM: v2.2.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.2.0
    - DX_FW: v2.5.0
    - NPU Driver: v2.1.0
    - DX-RT: v3.2.0
    - DX-STREAM: v2.2.0
    - DX-APP: v3.0.0

---

Here are the **DX-AllSuite v2.2.0** Release Notes.

### What's New?

This release introduces a **Python-Centric Ecosystem** and a **Complete Example Overhaul**, making development more intuitive and integrated.

- **Python-First Workflow**: DX-COM is now available via `pip` (Wheel), and new Python bindings (`pydxs, dx_postprocess`) allow for seamless metadata and post-processing management directly in Python.
- **Major DX-APP Refactoring (v3.0.0)**: Legacy demos have been replaced with a modern, task-oriented example system. This includes built-in support for the latest YOLO generations (v26, v10/v11/v12).
- **Expanded Hardware Acceleration**: PPU (Post-Processing Unit) support has been extended to the newest YOLO models, further offloading CPU tasks to the NPU.
- **Advanced Resource Management**: The introduction of NPU QoS (Quality of Service) and improved asynchronous handling ensures stable performance in multi-tasking environments.

---
### Key Updates

**Performance & Efficiency**  
- Extended PPU Support: Hardware-accelerated post-processing now supports YOLO26, YOLOv8, v9, v10, v11, and v12.
- PCIe DMA Optimization: Reduced CPU dependency and improved sequence efficiency for high-speed data transfer (requires DX-RT SDK v3.2.0+).
- Inference Reporting: Updated `inf_time` to include both NPU and PPU runtimes for realistic performance profiling.
- Resource Prioritization: Added QoS to the NPU Scheduler to manage execution priority effectively.
- Memory Footprint: Further reduced device memory usage for models utilizing PPU.

**Stability & Fixes**
- PCIe Stability: Added PERST# signal wait during initial boot stage to ensure reliable link establishment.
- Soft Lockup Prevention: Added sleep/reschedule logic in polling to prevent system hangs during slow hardware ACKs.
- Stream Stability: Resolved race conditions and segfaults in secondary inference modes with shared buffers.
- Model Accuracy: Fixed a known accuracy degradation issue in the DeepLabV3PlusMobilenet-1 model.
- Code Robustness: Implemented global `try-catch` handling and improved argument validation across the application layer.

**New Features & Tools**
- Installation & Deployment:
    - DX-COM Wheel: Install the compiler via `pip` for automated ML pipelines and Jupyter environments.
    - DX-TRON Debian: Added `.deb` package support for Ubuntu 20.04/22.04/24.04/26.04.
- Development Tools:
    - YOLO26 Support: Integration of the latest Ultralytics model optimized for edge deployment.
    - `RuntimeEventDispatcher`: A new centralized C++/Python singleton for handling system events, errors, and warnings.
    - `pydxs`: New Python binding for managing Stream metadata (`DXFrameMeta, DXObjectMeta,` etc.).
- Engine Capabilities: Enabled direct `.dxnn` model loading from memory buffers and per-instance I/O buffer configuration.
- Testing Infrastructure: Established a Pytest-based E2E test system for DX-APP, achieving over 93% code coverage.

**Known Issues**
- PReLU Degradation: Significant FPS drops may occur in models using PReLU activation functions.
- PPU Conversion Gap: DX-Compiler v2.2.0 does not yet support converting face/pose models to PPU format (requires v1.0.0 for these specific tasks).
- Breaking Changes: DX-APP v3.0.0 is not backward compatible with v2.x legacy demos or JSON configuration files.

**Migration Guide**
- Example Transition: Move from the `demos/` directory to the new `src/cpp_example/` and `src/python_example/` structures.
- Configuration: Replace legacy JSON config files with the new Command-Line Argument system in Python (e.g., for YOLO26 execution).
- Environment: Update your Python environment using the provided `requirements.txt` to support the new `dx_engine` and `pydxs` modules.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

## DX-AllSuite v2.1.0 / 2025-11-28

- DX-Compiler: v2.1.0
    - DX-COM: v2.1.0
    - DX-TRON: v2.0.0
- DX-Runtime: v2.1.0
    - DX_FW: v2.4.0
    - NPU Driver: v1.8.0
    - DX-RT: v3.1.0
    - DX-STREAM: v2.1.0
    - DX-APP: v2.1.0

---

Here are the **DX-AllSuite v2.1.0** Release Notes.

### What's New?
This release marks a significant step forward with new features and major stability improvements across all core components.

- **PPU Acceleration Integrated:** The Post-Processing Unit (PPU) is fully integrated into the compiler (DX-COM), runtime (DX-RT), and streaming (DX-STREAM) layers. This allows the NPU to handle NMS/bounding box decoding for models like YOLO and SCRFD, drastically reducing CPU overhead.
- **Next-Gen Model Support:** The entire stack now supports the new DXNN V8 file format and DXNNv8 PPU models (DX-RT and DX_FW), enabling the newest generation of AI applications.
- **Windows Ecosystem:** Full support for Windows 10/11 has been added to the DX-APP layer, complete with automated build scripts, making cross-platform development easier.
- **Advanced Diagnostics & Profilers:** New dedicated tools like the dxbenchmark, and GstShark integration provide comprehensive performance evaluation and optimization capabilities.

---

### Key Updates

**Performance & Efficiency**  
- PPU Integration (Full Stack): PPU functionality is reinstated in DX-COM and integrated into DX-STREAM and DX-APP to offload post-processing tasks (NMS/decoding) from the CPU.
- LPDDR Stability: DX_FW reduced the LPDDR Training Margin (0.7 -> 0.62) and added enhanced margin testing logic to boost system stability.
- Runtime Performance: DX-STREAM enhanced buffer processing via direct buffer manipulation and disabled synchronization in the video sink (secondary mode).
- Optimization Tools: DX-COM added the --aggressive_partitioning option and optimization level control (--opt_level {0,1}).
- Asynchronous Processing: DX-RT implemented the Asynchronous NPU Format Handler (NFH) for non-blocking inference.

**Stability & Fixes**  
- Critical Multi-Model Fixes (DX-RT): Resolved a critical bug affecting models with multi-output and multi-tail configurations and fixed several multi-tasking and CPU offloading buffer management issues.
- Pipeline Stability (DX-STREAM): Fixed a critical event processing timing issue in dxinputselector that caused compositor pipeline freezes.
- LPDDR/Boot Stability (DX_FW): Fixed LPDDR frequency display issues after CPU reset, resolved PRBS training fail judge logic, and improved PCIe link-up stability (including RPi5 warm boot).
- Windows Fixes (DX-APP/DX-RT): Fixed Windows MSBuild warnings using explicit static_cast (DX-APP) and fixed Windows environment compile errors (DX-RT).
- Compiler Flexibility (DX-COM): Removed restrictions on key operators: Split, Transpose, Reshape, Flatten, and Slice.

**New Features & Tools**  
- DXNN V8 Model Support: Added support for the V8 DXNN file format and DXNNv8 PPU models across the stack.
- Windows Support (DX-APP): Added full Windows 10/11 environment support with an automated build script (build.bat).
- Advanced Diagnostics & Monitoring:
    - DX-RT: Added DX-Fit tuning toolkit, dxbenchmark (performance comparison CLI), and model voltage profiler.
    - DX-STREAM: Added GstShark integration for comprehensive pipeline performance analysis.
    - DX_FW: Added Secure Debug and Model Profiling mode.
- PPU Data Types: DX-APP added support for three new PPU data types: BBOX, POSE, and FACE.
- DX_COM: Added Partial Compilation support (--compile_input_nodes/--compile_output_nodes).

**Known Issues (DX-APP / DX-COM)**
- Accuracy degradation observed in the DeepLabV3 Semantic Segmentation model.
- DX-Compiler v2.1.0 does not yet support converting face detection and pose estimation models to PPU format.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

## DX-AllSuite v2.0.0 / 2025-09-08

- DX-Compiler: v2.0.0
    - DX-COM: v2.0.0
    - DX-TRON: v2.0.0
- DX-Runtime: v2.0.0
    - DX_FW: v2.1.4
    - NPU Driver: v1.7.1
    - DX-RT: v3.0.0
    - DX-STREAM: v2.0.0
    - DX-APP: v2.0.0

---

Here are the **DX-AllSuite v2.0.0** Release Notes.

### What's New?
This release marks a significant step forward with new features and major stability improvements.

- **Performance Boost:** The new "stop & go" inference function and an increase in DMA channel threads improve processing speed, especially for large models.
- **Enhanced Stability:** Critical bug fixes, including a kernel panic and a Python compatibility error, make the platform more reliable across different environments.
- **Powerful New Tools:** The new `dxtop` monitoring tool provides real-time insights into NPU performance, while a USB inference module expands connectivity options.
- **Expanded Model Support:** The compiler now supports new operators like `ConvTranspose`, and most notably, offers partial support for Vision Transformer (ViT) models. This opens up a wider range of AI applications.

---

### Key Updates

**Performance & Efficiency**  
- Implemented a new "stop & go" inference function that splits large tiles for better performance.
- Increased the number of threads for the `DeviceOutputWorker` from 3 to 4.
- YOLO post-processing logic was updated to use a `RunAsync() + Wait()` structure to ensure correct output order.
- The default build option for DX-RT is now `USE_ORT=ON`, which enables the CPU task for `.dxnn` models by default. Add automatic handling of input dummy padding and output dummy slicing when `USE_ORT=OFF` (build-time or via InferenceOption). 

**Stability & Fixes**  
- Resolved a kernel panic caused by an incorrect NPU channel number.
- Fixed a build error on Ubuntu 18.04 related to Python 3.6.9 incompatibility by adding automatic installation support for a compatible Python version (3.8.2).
- Corrected a QSPI read logic bug that could cause underflow.
- Addressed a processing delay bug in `dx-inputselector` and fixed a bug in dx_rt that affected multi-tail models.
- In DX-COM, `PPU(Post-Processing Unit)` is no longer supported, and there are no current plans to reinstate it.

**New Features & Tools**  
- Added a new USB inference module.
- Introduced a new terminal-based monitoring tool called `dxtop` for real-time NPU usage insights.
- A new `dxrt-cli --errorstat` option was added to display detailed PCIe error information.
- Support for the `Softmax`, `Slice`, and `ConvTranspose` operators was enabled.
- Partial support for Vision Transformer (ViT) models was added.
- Implemented a new uninstall script (`uninstall.sh`) for project cleanup.
- In DX-RT, add support for both .dxnn file formats: v6 (compiled with dx_com 1.40.2 or later) and v7 (compiled with dx_com 2.x.x).

For detailed updated items, refer to **each environment & module's Release Notes.**

---

## DX-AllSuite v1.0.0 Initial Release / 2025-07-23

We're excited to announce the **initial release of DX-AllSuite (DX-AS) v1.0.0!**

DX-AS is your new integrated environment, bringing together essential frameworks and tools to simplify AI model inference and compilation on DEEPX devices. While you can always install individual tools, DX-AS ensures optimal compatibility by aligning all tool versions for you.

---

### What's Included?

This initial release provides a comprehensive suite to get you started:

* **Integrated Environment:** A unified platform for all your DEEPX AI development needs.
* **Optimal Compatibility:** Pre-aligned versions of individual tools to guarantee seamless operation.

---

### Key Documentation

To help you hit the ground running, we've prepared detailed documentation:

* **Introduction:** Get a comprehensive overview of DX-AS.
* **Installation Guide:** Step-by-step instructions to set up your environment.
* **Getting Started:** A quick guide to begin using DX-AS.
* **Version Compatibility:** Information on supported versions and configurations.
* **FAQ:** Answers to commonly asked questions.

You can find all these resources and more in the `docs` directory of the repository.

---
