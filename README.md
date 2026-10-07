# DXNN - DEEPX NPU SDK (DX-AllSuite: DEEPX All Suite)

**DX-AllSuite** is an all-in-one software platform designed to streamline the entire process of compiling, optimizing, simulating, and deploying AI inference applications on **DEEPX NPUs**. It ensures optimal compatibility and powerful hardware performance through a complete toolchain that covers everything from model creation to real-world "Physical AI" deployment.  

## Documentation Navigation

If you are a first-time user, we recommend following the documentation in this order.  

- **[Introduction](./docs/source/index.md)**: DX-AS overview and component descriptions
- **★ [Agent-Driven Development (Beta)](./docs/source/00_Agent_Driven_Development.md)**: Build DEEPX apps with natural-language prompts using AI coding agents (Claude Code, Cursor, GitHub Copilot, OpenCode, Codex CLI)  
- **[DX-Benchmark (Beta)](./dx-benchmark/README.md)**: Reproducible YOLO26 NPU benchmarks (Model-Level + E2E Pipeline) with an interactive performance dashboard  
- **[DX-Edge](./dx-edge/README.md)**: Deploying DEEPX NPUs through AWS Marketplace — Greengrass Solution (ZTP runtime deployment), Compiler Solution (ONNX → `.dxnn` on AWS), and the DX-AIPlayer N97 Getting Started Guide
- **Step 1. [DX-AllSuite Architecture Overview](./docs/source/01_DX-AllSuite_Architecture_Overview.md)**: SDK overview, module descriptions, and ModelZoo usage  
- **Step 2. [Setting Up Environment](./docs/source/02_Setting_Up_Environment.md)**: Detailed Local/Docker installation and troubleshooting  
- **Step 3. [Running Your First NPU Model](./docs/source/03_Running_Your_First_NPU_Model.md)**: Step-by-step hands-on script execution  
- **Step 4. [Checking Version Compatibility](./docs/source/04_Version_Compatibility.md)**: SDK, Driver, and Firmware dependency matrix  
- **Step 5. [FAQ Troubleshooting Guide](./docs/source/05_FAQ_Troubleshooting_Guide.md)**: Solutions for environment conflicts and GUI session (X11) errors  
- **Optional. [Kubernetes Quickstart](./docs/source/06_Kubernetes_Quickstart.md)**: Schedule DX-M1 NPUs as a Kubernetes resource with the `dx-npu` Helm chart
- **Optional. [Kubernetes Beginner Guide](./docs/source/07_Kubernetes_Beginner_Guide.md)**: Kubernetes explained from scratch, with hands-on NPU examples

<div align="center">
  <img src="./docs/source/img/DXNN-SDK-Full-Architecture.png" width="600">
  <p><strong>Figure. DXNN SDK Full Architecture Overview.</strong></p>
</div>

**Key Features**  

- **High Efficiency**: Equipped with the proprietary **DX-COM** compiler that extracts 100% of NPU performance. It utilizes advanced quantization (Intelligent Quantization with INT8) to minimize accuracy loss while maximizing inference speed.  
- **Seamless Integration**: Build intelligent video analytics pipelines that bridge the entire pre-processing, inference, and post-processing workflow. Using **DX-Stream** (GStreamer-based custom plugins), you can deploy complex vision tasks without extensive code modifications.  
- **Flexible Ecosystem**: Fully supports **Python and C++ APIs** and offers a **ModelZoo** with 345 optimized models. As a leader in the Open-Source Physical AI Alliance, we provide seamless workflows for popular frameworks.  

<div align="center">
  <img src="./docs/source/img/DXNN-SDK-Simple-Architecture.png" width="600">
  <p><strong>Figure. DXNN SDK Simple Architecture Overview.</strong></p>
</div>

## ✨ DEEPX Agent-Driven Development — dx-agent-dev (Beta)

<!-- dx-showcase:docs:cardgrid:start -->
**DEEPX Agent-Driven Development (`dx-agent-dev`) is here — currently in Beta.** Build NPU apps with natural language: describe the app or model task in plain language and an AI coding agent — Claude Code, Cursor, GitHub Copilot, OpenCode, or Codex — drives the DEEPX knowledge base end to end: brainstorm → plan → TDD → verify, from ONNX/`.pt` compilation to on-device DX-M1 NPU deployment. It is agent-driven development purpose-built for DEEPX NPUs in the **Ultralytics** model ecosystem, and every showcase below was produced this way — checked in with its prompt, measured results, and full build transcript.

#### NPU-powered AI apps (mini-games)

**Build a fully autonomous DEEPX-NPU app from natural language — in ~20 minutes, for ~$10.** Pose-driven mini-games with arcade HUDs, built end to end from a single prompt.

<table>
<tr>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/mini-game-squat-fitness/README.md"><img src="./docs/source/img/dx-agent-dev-squat-gameplay.gif" height="150"></a><br><b>Squat-Counting Mini-Game</b><br><sub>rep-counting fitness on NPU</sub></td>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/mini-game-stretching-coach/README.md"><img src="./docs/source/img/dx-agent-dev-stretch-gameplay.gif" height="150"></a><br><b>Stretching Coach Mini-Game</b><br><sub>pose-guided arcade coach</sub></td>
</tr>
</table>

#### Ultralytics ecosystem integration

**Take any Ultralytics YOLO to the DEEPX NPU in one command — or retrain it for your domain — all in natural language.** `format=deepx` export + 4-way eval (base/retrained × fp32-GPU / INT8-NPU); INT8 ≈ fp32, and the domain model runs faster on the NPU.

<table>
<tr>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/ultralytics-yolo-deepx-export/README.md"><img src="./docs/source/img/dx-agent-dev-ultralytics-yolo.gif" height="150"></a><br><b>Ultralytics YOLO → DeepX Export</b><br><sub>one-command format=deepx</sub></td>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/ultralytics-yolo-deepx-export/README.md"><img src="./docs/source/img/dx-agent-dev-ultralytics-build.gif" height="150"></a><br><sub><b>build capture (timelapse)</b></sub></td>
</tr>
<tr>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-wildlife/README.md"><img src="./docs/source/img/dx-agent-dev-ultralytics-wildlife-sample.jpg" height="150"></a><br><b>African Wildlife Monitoring</b><br><sub>safari camera retrain</sub></td>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-ppe/README.md"><img src="./docs/source/img/dx-agent-dev-ultralytics-ppe-sample.jpg" height="150"></a><br><b>Construction PPE Safety</b><br><sub>site-safety camera retrain</sub></td>
</tr>
<tr>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-braintumor/README.md"><img src="./docs/source/img/dx-agent-dev-ultralytics-braintumor-sample.jpg" height="150"></a><br><b>Brain-Tumor Screening</b><br><sub>medical edge retrain</sub></td>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/ultralytics-retrain-eval-deepx-export-pills/README.md"><img src="./docs/source/img/dx-agent-dev-ultralytics-pills-sample.jpg" height="150"></a><br><b>Pharmaceutical Pill Inspection</b><br><sub>pharma counting retrain</sub></td>
</tr>
</table>

#### PaddlePaddle ecosystem integration

**PaddleOCR (PP-OCRv5) on the DEEPX NPU — real-time video & webcam OCR from a single, concise prompt.** Baidu's PaddlePaddle OCR (text detection → orientation → recognition) running on the DX-M1 NPU.

<table>
<tr>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/paddleocr-video-ocr/README.md"><img src="./docs/source/img/dx-agent-dev-paddleocr-gameplay.gif" height="150"></a><br><b>Video / Webcam OCR (PP-OCRv5)</b><br><sub>PaddleOCR PP-OCRv5 on the NPU</sub></td>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/paddleocr-video-ocr/README.md"><img src="./docs/source/img/dx-agent-dev-paddleocr-build.gif" height="150"></a><br><sub><b>build capture (timelapse)</b></sub></td>
</tr>
</table>

#### RapidAI ecosystem integration

**A PDF → Markdown document-conversion app on the DEEPX NPU — from a single, concise natural-language prompt.** RapidAI's RapidDoc (PP-StructureV3): layout, OCR, tables, formulas — running PaddlePaddle-trained models on the DX-M1 NPU. A standalone, self-contained app generated from the fork's pipeline.

<table>
<tr>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/rapiddoc-pdf2md/README.md"><img src="./docs/source/img/dx-agent-dev-rapiddoc-pdf2md-sample.png" height="150"></a><br><b>PDF → Markdown (document conversion app)</b><br><sub>RapidDoc PP-StructureV3 on the NPU</sub></td>
 <td width="50%" align="center"><a href="dx-agent-dev-showcase/rapiddoc-pdf2md/README.md"><img src="./docs/source/img/dx-agent-dev-rapiddoc-pdf2md-build.gif" height="150"></a><br><sub><b>build capture (timelapse)</b></sub></td>
</tr>
</table>

**All showcases + summaries →** [`dx-agent-dev-showcase/README.md`](./dx-agent-dev-showcase/README.md)  ·  **About the feature →** [Agent-Driven Development docs](./docs/source/00_Agent_Driven_Development.md)
<!-- dx-showcase:docs:cardgrid:end -->

> **Note on build time & cost** — The build time, output-token count, and cost shown for
> each showcase are **actual measurements** taken from that showcase's recorded
> build-session transcript (`*-session.md`), priced with the coding agent's published
> billing policy — not estimates, and not cherry-picked best runs. Because AI coding
> agents are non-deterministic, the same prompt does not always consume the same output
> tokens, so your own build time and cost may differ depending on environment and model version.

## ✨ DX AI Studio — dx-ai-studio (Beta)

<div align="center">
  <img src="./dx-ai-studio/docs/source/resources/hub.png" width="820">
</div>

**DX AI Studio is here — currently in Beta.** An all-in-one desktop web workspace for building on the DEEPX NPU: eight specialized tools in one browser, launched with a single command — **DX Model Zoo** (model catalog), **DX Compiler** (ONNX/`.pt` → `.dxnn`), **DX App** (inference + one-click **Run Demo**), **DX Stream** (GStreamer pipelines), **DX Benchmark**, **DX Monitor** (live NPU telemetry), **DX EdgeGuide** (deployment planner from measured benchmark data), and **DX Agent Dev** (the agent-driven builder above). Compile a model, run a curated demo, stream a pipeline, and watch NPU utilization live — all on-device.

**Explore the studio →** [`dx-ai-studio/README.md`](./dx-ai-studio/README.md)  ·  **Install & launch →** [Installation and Launch](./dx-ai-studio/docs/source/01_Installation_and_Launch.md)

## ✨ DX-Benchmark — dx-benchmark (Beta)

Reproducible YOLO26 performance benchmarking on the DEEPX NPU — one standardized procedure
across any Host PC + NPU combination. It measures two tiers: **Model-Level** (`run_model`) —
**Latency** (single-core, sync) and **Throughput** (multi-core, async) — and **E2E Pipeline**
(DX-Stream) — **Single-Stream** FPS and **Multi-Stream** channel capacity. Both tiers run
automatic ONNX-Runtime ON/OFF comparison with thermal-throttle detection, then render an
interactive dashboard for cross-environment and cross-version comparison. Measured results for
6 hardware environments are included, and the dashboard built from them is also viewable in
[DX AI Studio](./dx-ai-studio/README.md)'s **DX Benchmark** view.

**Get started →** [`dx-benchmark/README.md`](./dx-benchmark/README.md)  ·  **Performance analysis →** [`dx-benchmark/docs/ANALYSIS_EN.md`](./dx-benchmark/docs/ANALYSIS_EN.md)

## 📦 DX-Edge — Powered by AWS, available on AWS Marketplace

**Take a trained model to a DEEPX NPU in the field, entirely through AWS.** DX-Edge covers the three
things that stand between a trained ONNX model and a working edge deployment — compiling the model
for the NPU, provisioning the runtime on the device, and qualified hardware to run it on — across
three tracks published on AWS Marketplace. The **DEEPX Greengrass Solution** provisions the cloud
compilation pipeline and the edge runtime from a single AWS CloudFormation stack, installing the NPU
driver, firmware, `dx_rt`, and `dx_stream` over the air (Zero-Touch Provisioning) via AWS IoT
Greengrass V2. The **DEEPX Compiler Solution** compiles ONNX to `.dxnn` on AWS — interactively from
an Amazon EC2 instance, or automatically through an event-driven S3 → Lambda → Step Functions pipeline.
The **AWS HW Path** documents the **DX-AIPlayer N97** (Intel® N97 + DX-M1) as an AWS IoT Greengrass
core device, following the AWS Device Qualification Program Getting Started Guide template. Every
document is published in English and Korean.

**Explore DX-Edge →** [`dx-edge/README.md`](./dx-edge/README.md)  ·  **한국어 →** [`dx-edge/README-KO.md`](./dx-edge/README-KO.md)

## Getting Started

**DX-AllSuite** provides two environments depending on your intended use. Choose the environment that fits your needs to get started.

### Quick Install (one-line)

Install a single component without cloning this repository:

```bash
# DX-Compiler (x86_64 Host PC)
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-compiler/main/oneline-install.sh | sh

# DX-Runtime (target device with a DEEPX NPU: NPU driver + dx_rt + firmware)
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-install.sh | sh
```

DX-Compiler installs `dx-com` from PyPI into `~/deepx/venv-dx-compiler` and links the
`dxcom` launcher into `~/.local/bin`, so you can run `dxcom --help` straight afterwards.
It also apt-installs `libgl1-mesa-dev` and `libglib2.0-0`, which `opencv-python` needs to
import, so it requires root or `sudo` on a Debian/Ubuntu host. Note this route does not
bring the sample data — clone the repository for that.

Pin a specific version with `DX_VERSION` (DX-Compiler), or per component with
`DX_RT_VERSION` / `DX_DRIVER_VERSION` / `DX_FW_VERSION` (DX-Runtime, which otherwise
tracks each component's `main`). DX-Compiler also accepts `DX_INSTALL_DIR` to move the
install root; DX-Runtime has none, since it installs system packages via `dpkg`:

```bash
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-compiler/main/oneline-install.sh | DX_VERSION=2.4.1 sh
```

> **DX-Runtime notes**
> One-line install covers `dx_fw`, `dx_rt`, and `dx_rt_npu_linux_driver`; `dx_app`
> and `dx_stream` still use the full installation guide below. The firmware update
> step is skipped when no NPU device is detected — rerun the same command once the
> device is available.

#### Uninstalling

Remove a one-line install without cloning either repository:

```bash
# DX-Compiler
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-compiler/main/oneline-uninstall.sh | sh

# DX-Runtime
curl -fsSL https://raw.githubusercontent.com/DEEPX-AI/dx-runtime/main/oneline-uninstall.sh | sh
```

Pass DX-Compiler the same `DX_INSTALL_DIR` / `DX_BIN_DIR` you installed with, or it looks in
the default location and finds nothing. DX-Runtime needs no such argument, and because both
of its install routes produce the same Debian packages, that one command also removes an
`install.sh` install — you do not have to remember which way it went on.

Two things are never undone: firmware already flashed to the NPU, which has no uninstall path
at all, and the `dx_engine` Python wheel, which `libdxrt-bin` deliberately leaves to you and
explains how to remove while it is being purged.

#### APT Repository (DX-Runtime)

The NPU driver and the DX-RT runtime are also published as Debian packages in the DEEPX
APT repository (Ubuntu / Debian, `amd64` / `arm64`), so you can install and upgrade them with `apt`.
Verify the signing key before trusting it: `gpg --show-keys` must print the fingerprint
`3A20CC853C64AE328D0F58CFD816AAC6689DBDEA`. If it does not match, stop — do not install the key.

```bash
wget -O deepx-archive-keyring.asc https://apt.releases.deepx.ai/gpg
gpg --show-keys deepx-archive-keyring.asc   # fingerprint must be 3A20CC853C64AE328D0F58CFD816AAC6689DBDEA
sudo gpg --dearmor -o /usr/share/keyrings/deepx-archive-keyring.gpg deepx-archive-keyring.asc
rm deepx-archive-keyring.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/deepx-archive-keyring.gpg] https://apt.releases.deepx.ai $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") main" | sudo tee /etc/apt/sources.list.d/deepx.list

sudo apt update
sudo apt install dxrt-driver-dkms   # NPU kernel driver, built for your kernel via DKMS
sudo apt install libdxrt-bin        # DX-RT library, dxrt-cli and tools
```

The `dx_engine` Python package is published on PyPI as `dx-engine`. Install it into your
virtualenv with the same major.minor version as the installed `libdxrt-bin`, since the wheel
carries its own copy of the runtime library:

```bash
pip install "dx-engine==$(dpkg-query -W -f='${Version}' libdxrt-bin | cut -d. -f1,2).*"
```

The same wheels are also staged in `/usr/share/libdxrt-bin/python` for offline installs.
Firmware is not part of these packages; update it with the one-line
installer or `./dx-runtime/install.sh --target=dx_fw`, and reboot after installing the driver.
Later releases arrive through `sudo apt update && sudo apt upgrade`.

For the full suite (all components, source builds, Docker), use the environment
guides below.

### AI Model Compile Environment (Host PC)  

This environment is used for converting and optimizing trained AI models into DEEPX NPU-specific binaries.  

- **Arch**: x86_64  
- **OS**: Ubuntu 26.04 / 24.04 / 22.04 / 20.04 (LTS), Fedora 42-45, Red Hat Enterprise Linux 9-10, and CentOS Stream 9-10
-	**Hardware**: x86_64 Host PC  
- **Software**: Python 3.8~3.14, CUDA (Optional for simulation)
-	**Key Tasks**: AI model (`.onnx`) compilation, Quantization, `.dxnn` generation  
-	**Action**: DX-Compiler Local Installation Guide [Link](./docs/source/02_Setting_Up_Environment.md)

### AI Model Runtime Environment (Target Device)

This environment is for performing inference and running applications on devices physically equipped with DEEPX NPUs.  

-	**Arch**: x86_64, aarch64 
-	**OS**: Ubuntu 26.04 / 24.04 / 22.04 / 20.04 (LTS), Debian 13 / 12
-	**Hardware**: Host PC / Target Board (DEEPX NPU is required)
-	**Software**: Python 3.8+
-	**Key Tasks**: `.dxnn` model execution, real-time data inference, resource management
-	**Action**: DX-Runtime Installation Guide [Link](./docs/source/02_Setting_Up_Environment.md)

> **Warning: Activation Required**  
> A system reboot is mandatory after installation to properly load the NPU Driver into the kernel.  
> ```Bash  
> sudo reboot  
> ```

### Prebuilt Container Images (GHCR)

Prefer containers over a local install? Official Ubuntu 24.04 images are published to GitHub Container Registry, so you can skip building the suite entirely.  

```Bash
docker pull ghcr.io/deepx-ai/dx-runtime:latest
docker run --rm -it --privileged --ipc=host --pid=host -v /dev:/dev \
    --entrypoint bash ghcr.io/deepx-ai/dx-runtime:latest
```

`dx-runtime` ships in four variants (`rt`, `rt-app`, `rt-stream`, `rt-app-stream`) alongside `dx-compiler` and `dx-modelzoo`.

`dx-runtime` is published for both `linux/amd64` and `linux/arm64`; **`dx-compiler` and `dx-modelzoo` are `linux/amd64` only**.

- **Action**: Container image tags, variant selection, and NPU passthrough options [Link](./docker/README.md)

### Kubernetes Cluster (Optional)

This environment schedules DEEPX NPUs across a Kubernetes cluster, so a pod asks for an NPU the
same way it asks for CPU or memory.

-	**Platform**: k3s or vanilla Kubernetes with containerd (CDI is on by default in containerd 2.x)
-	**Hardware**: One or more nodes with DX-M1 installed, each set up as a Runtime Environment above
-	**Components**: Device plugin (`deepx.ai/dx-m1` resource), NFD node labels (firmware/driver versions), CDI injection of the device and runtime libraries, Prometheus metrics, one-command Helm chart (`dx-npu`)
-	**Usage**: Add `resources.limits: {deepx.ai/dx-m1: 1}` to a pod — the scheduler places it on an NPU node and the device arrives inside the container, with no manual device mounts
-	**Action**: [Kubernetes Quickstart](./docs/source/06_Kubernetes_Quickstart.md) · new to Kubernetes? [Beginner Guide](./docs/source/07_Kubernetes_Beginner_Guide.md)

## Supported Models

DX-AllSuite supports a vast array of industry-standard AI architectures, optimized for peak performance on our NPU.  

- **Image Classification**: AlexNet, ResNet/ResNeXt/WideResNet, MobileNet, EfficientNet (Lite/V2), ViT/DeiT/BEiT, MobileViT, FastViT, CasViT, RegNet, ShuffleNet, VGG, and more.  
- **Object Detection**: YOLO families (YOLOv3–YOLOv11, YOLOX, YOLO26), SSD, EfficientDet, NanoDet, DamoYOLO.  
- **Segmentation**: DeepLabV3/DeepLabV3+, SegFormer, BiSeNet, UNet, YOLACT, and YOLO-based segmentation variants (YOLOv5/YOLOv8/YOLO26).  
- **Advanced Vision Tasks**: Face analysis (Detection, Recognition, Landmarks, Attributes), Human/Hand Pose Estimation, Low-Light Enhancement, Image Denoising, Super Resolution, Depth Estimation, Oriented Object Detection (OBB), Zero-Shot Instance Segmentation, and Person Attributes.  

> **Note: Pro Tip**  
> Instead of compiling models yourself, you can download ready-to-use binaries from the [**DEEPX ModelZoo**](https://developer.deepx.ai/modelzoo/), which features **345 optimized models**.  


## Support

The DEEPX Technical Support Team is here to help you build smooth AI solutions.  

- **DEEPX Developer Portal**: [https://developer.deepx.ai](https://developer.deepx.ai) (Latest documentation and SDK release notes)  
- **Technical Support**: [tech-support@deepx.ai](mailto:tech-support@deepx.ai) (Consultation on custom model deployment and hardware integration)    

Copyright © DEEPX. All rights reserved.  

---
