# DXNN - DEEPX NPU SDK (DX-AllSuite: DEEPX All Suite)

**DX-AllSuite** is an all-in-one software platform designed to streamline the entire process of compiling, optimizing, simulating, and deploying AI inference applications on **DEEPX NPUs**. It ensures optimal compatibility and powerful hardware performance through a complete toolchain that covers everything from model creation to real-world "Physical AI" deployment.  

<div align="center">
  <img src="./docs/source/img/DXNN-SDK-Full-Architecture.png" width="600">
  <p><strong>Figure. DXNN SDK Full Architecture Overview.</strong></p>
</div>

**Key Features**  

- **High Efficiency**: Equipped with the proprietary **DX-COM** compiler that extracts 100% of NPU performance. It utilizes advanced quantization (Intelligent Quantization with INT8) to minimize accuracy loss while maximizing inference speed.  
- **Seamless Integration**: Build intelligent video analytics pipelines that bridge the entire pre-processing, inference, and post-processing workflow. Using **DX-Stream** (GStreamer-based custom plugins), you can deploy complex vision tasks without extensive code modifications.  
- **Flexible Ecosystem**: Fully supports **Python and C++ APIs** and offers a **ModelZoo** with over 270 optimized models. As a leader in the Open-Source Physical AI Alliance, we provide seamless workflows for popular frameworks.  

<div align="center">
  <img src="./docs/source/img/DXNN-SDK-Simple-Architecture.png" width="600">
  <p><strong>Figure. DXNN SDK Simple Architecture Overview.</strong></p>
</div>

## ✨ Build Apps with Natural Language — dx-agentic-dev (Beta)

> **Develop a complete fitness game on the DEEPX NPU — fully autonomously, by natural
> language — in about 20 minutes for roughly $10.** Describe the app in plain language
> and an AI coding agent builds it on the DEEPX SDK end-to-end.

### Showcase 1: Squat-Counting Fitness Mini-Game (DEEPX SQUAT CHALLENGE)

<div align="center">
<table>
<tr>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-squat-build.gif" width="470"><br><sub><b>dx-agentic-dev building the app (timelapse)</b></sub></td>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-squat-gameplay.gif" width="188"><br><sub><b>Generated app running on NPU</b></sub></td>
</tr>
</table>
</div>

**▶️ Run it yourself** — checked in at
**[`dx-agentic-dev-showcase/squat-fitness-mini-game/`](./dx-agentic-dev-showcase/squat-fitness-mini-game/)**.
Read its [README](./dx-agentic-dev-showcase/squat-fitness-mini-game/README.md) and run it.

**🔍 See how the agent built it** — the full
[Claude Code session](./dx-agentic-dev-showcase/squat-fitness-mini-game/claude-code-session.md)
is included, showing how it followed the harness instructions and used the project skills/agents.

### Showcase 2: Arcade Stretching Coach Mini-Game (STRETCH ARCADE)

<div align="center">
<table>
<tr>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-stretch-build.gif" width="470"><br><sub><b>dx-agentic-dev building the stretching game (timelapse)</b></sub></td>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-stretch-gameplay.gif" width="188"><br><sub><b>Generated app on NPU (coach avatar + 3 stages)</b></sub></td>
</tr>
</table>
</div>

**▶️ Run it yourself** — checked in at
**[`dx-agentic-dev-showcase/stretching-coach-mini-game/`](./dx-agentic-dev-showcase/stretching-coach-mini-game/)**
([README](./dx-agentic-dev-showcase/stretching-coach-mini-game/README.md)).

### Showcase 3: Ultralytics YOLO → DeepX Export (one-shot `format=deepx`)

<div align="center">
<img src="./docs/source/img/dx-agentic-dev-ultralytics-build.gif" width="640"><br><sub><b>dx-agentic-dev building this showcase (timelapse) — export → dx_com compile → NPU inference → verify</b></sub>
</div>

DEEPX × **Ultralytics** technical integration: an Ultralytics YOLO `.pt` becomes a
deployable DeepX NPU model in a **single command** —

```bash
yolo export model=yolo26n.pt format=deepx   # → yolo26n_deepx_model/ (.dxnn + config + metadata)
```

From the prompt *"export my YOLO26n model to DeepX and run inference"*, the agent
routes through the knowledge base to the
[`ultralytics-deepx-export`](./dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md)
toolset and drives the export + deployment — no hand-rolled pipeline.

**▶️ Run it yourself** — checked in at
**[`dx-agentic-dev-showcase/ultralytics-yolo-deepx-export/`](./dx-agentic-dev-showcase/ultralytics-yolo-deepx-export/)**
([README](./dx-agentic-dev-showcase/ultralytics-yolo-deepx-export/README.md)).

### Showcase 4: Ultralytics Retrain → DeepX NPU (domain optimization)

<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-wildlife:gif:start -->
<div align="center">
<img src="./docs/source/img/dx-agentic-dev-ultralytics-retrain-build.gif" width="760"><br><sub><b>dx-agentic-dev building this showcase — retrain → DeepX → NPU FPS/mAP</b></sub>
</div>
<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-wildlife:gif:end -->


**Wildlife monitoring**: stock COCO `yolo26n` can't reliably detect wildlife species, so
retrain it on `african-wildlife` and deploy on the DX-M1 NPU — **mAP50-95 ~0.001 → 0.79**
(mAP50 0.94, INT8 NPU), **+38% FPS** (59 → 82); 4-way (base/retrained × fp32-GPU /
INT8-NPU) eval, INT8 ≈ fp32.

**▶️ Run it yourself** — checked in at
**[`dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-wildlife/`](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-wildlife/)**
([README](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-wildlife/README.md)).

### Showcase 5: Ultralytics PPE Detection → DeepX NPU (construction safety)

<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-ppe:gif:start -->
<div align="center">
<table><tr>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-ultralytics-ppe-build.gif" width="470"><br><sub><b>building (timelapse)</b></sub></td>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-ultralytics-ppe-sample.jpg" width="280"><br><sub><b>PPE detection on DX-M1 NPU</b></sub></td>
</tr></table>
</div>
<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-ppe:gif:end -->


Domain optimization for a **construction site-safety camera**: retrain `yolo26n` on the
`construction-ppe` dataset and deploy on the DX-M1 NPU — stock COCO model **mAP50-95
0.0001 → retrained 0.256** (INT8 NPU), **+32% FPS** (58 → 76); evaluated 4 ways
(base/retrained × fp32-GPU / INT8-NPU).

**▶️ Run it yourself** — **[`dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-ppe/`](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-ppe/)**
([README](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-ppe/README.md)).

### Showcase 6: Ultralytics Brain-Tumor Screening → DeepX NPU (medical edge)

<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-braintumor:gif:start -->
<div align="center">
<table><tr>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-ultralytics-braintumor-build.gif" width="470"><br><sub><b>building (timelapse)</b></sub></td>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-ultralytics-braintumor-sample.jpg" width="280"><br><sub><b>tumor detection on DX-M1 NPU</b></sub></td>
</tr></table>
</div>
<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-braintumor:gif:end -->


Domain optimization for a **medical edge device**: retrain `yolo26n` on the `brain-tumor`
dataset (MRI/CT) and deploy on the DX-M1 NPU — stock COCO model **mAP50-95 ~0.0005 →
retrained 0.40** (INT8 NPU), **+34% FPS** (58 → 78); 4-way (base/retrained × fp32/INT8) eval.

**▶️ Run it yourself** — **[`dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-braintumor/`](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-braintumor/)**
([README](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-braintumor/README.md)).

### Showcase 7: Ultralytics Pill Detection → DeepX NPU (pharma)

<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-pills:gif:start -->
<div align="center">
<table><tr>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-ultralytics-pills-build.gif" width="470"><br><sub><b>building (timelapse)</b></sub></td>
<td align="center"><img src="./docs/source/img/dx-agentic-dev-ultralytics-pills-sample.jpg" width="280"><br><sub><b>pill detection on DX-M1 NPU</b></sub></td>
</tr></table>
</div>
<!-- dx-showcase:ultralytics-retrain-eval-deepx-export-pills:gif:end -->


Domain optimization for a **pharmaceutical pill counting station**: retrain `yolo26n` on
`medical-pills` and deploy on the DX-M1 NPU — stock COCO model **mAP50-95 ~0.001 →
retrained 0.75** (mAP50 0.97, INT8 NPU), **+38% FPS** (56 → 77.5); 4-way eval.

**▶️ Run it yourself** — **[`dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-pills/`](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-pills/)**
([README](./dx-agentic-dev-showcase/ultralytics-retrain-eval-deepx-export-pills/README.md)).

➡️ **[Get started with Agentic Development (Beta)](./docs/source/00_Agentic_Development.md)**

## Getting Started

**DX-AllSuite** provides two environments depending on your intended use. Choose the environment that fits your needs to get started.

### AI Model Compile Environment (Host PC)  

This environment is used for converting and optimizing trained AI models into DEEPX NPU-specific binaries.  

- **Arch**: x86_64  
- **OS**: Ubuntu 24.04 / 22.04 / 20.04 (LTS), Fedora, Redhat, CentOS  
-	**Hardware**: x86_64 Host PC  
- **Software**: Python 3.8~3.12, CUDA (Optional for simulation)  
-	**Key Tasks**: AI model (`.onnx`) compilation, Quantization, `.dxnn` generation  
-	**Action**: DX-Compiler Local Installation Guide [Link]  

### AI Model Runtime Environment (Target Device)

This environment is for performing inference and running applications on devices physically equipped with DEEPX NPUs.  

-	**Arch**: x86_64, aarch64 
-	**OS**: Ubuntu 24.04 / 22.04 / 20.04 / 18.04 (LTS), Debian 13 / 12
-	**Hardware**: Host PC / Target Board (DEEPX NPU is required)
-	**Software**: Python 3.8+
-	**Key Tasks**: `.dxnn` model execution, real-time data inference, resource management
-	**Action**: DX-Runtime Installation Guide [Link]

!!! warning "Activation Required"  
    A system reboot is mandatory after installation to properly load the NPU Driver into the kernel.  
    ```Bash  
    sudo reboot  
    ```

## Supported Models

DX-AllSuite supports a vast array of industry-standard AI architectures, optimized for peak performance on our NPU.  

- **Image Classification**: AlexNet, ResNet/ResNeXt/WideResNet, MobileNet, EfficientNet (Lite/V2), ViT/DeiT/BEiT, MobileViT, FastViT, CasViT, RegNet, ShuffleNet, VGG, and more.  
- **Object Detection**: YOLO families (YOLOv3–YOLOv11, YOLOX, YOLO26), SSD, EfficientDet, NanoDet, DamoYOLO.  
- **Segmentation**: DeepLabV3/DeepLabV3+, SegFormer, BiSeNet, UNet, YOLACT, and YOLO-based segmentation variants (YOLOv5/YOLOv8/YOLO26).  
- **Advanced Vision Tasks**: Face analysis (Detection, Recognition, Landmarks, Attributes), Human/Hand Pose Estimation, Low-Light Enhancement, Image Denoising, Super Resolution, Depth Estimation, Oriented Object Detection (OBB), Zero-Shot Instance Segmentation, and Person Attributes.  

!!! note "Pro Tip"  
    Instead of compiling models yourself, you can download ready-to-use binaries from the [**DEEPX ModelZoo**](https://developer.deepx.ai/modelzoo/), which features **over 270 optimized models**.  


## Documentation Navigation

If you are a first-time user, we recommend following the documentation in this order.  

- **★ [Agentic Development (Beta)](./docs/source/00_Agentic_Development.md)**: Build DEEPX apps with natural-language prompts using AI coding agents (Claude Code, Cursor, GitHub Copilot, OpenCode, Codex CLI)  
- **Step 1. [DX-AllSuite Architecture Overview](./docs/source/01_DX-AllSuite_Architecture_Overview.md)**: SDK overview, module descriptions, and ModelZoo usage  
- **Step 2. [Setting Up Environment](./docs/source/02_Setting_Up_Environment.md)**: Detailed Local/Docker installation and troubleshooting  
- **Step 3. [Running Your First NPU Model](./docs/source/03_Running_Your_First_NPU_Model.md)**: Step-by-step hands-on script execution  
- **Step 4. [Checking Version Compatibility](./docs/source/04_Version_Compatibility.md)**: SDK, Driver, and Firmware dependency matrix  
- **Step 5. [FAQ Troubleshooting Guide](./docs/source/05_FAQ_Troubleshooting_Guide.md)**: Solutions for environment conflicts and GUI session (X11) errors  

## Support

The DEEPX Technical Support Team is here to help you build smooth AI solutions.  

- **DEEPX Developer Portal**: [https://developer.deepx.ai](https://developer.deepx.ai) (Latest documentation and SDK release notes)  
- **Technical Support**: [tech-support@deepx.ai](mailto:tech-support@deepx.ai) (Consultation on custom model deployment and hardware integration)    

Copyright © DEEPX. All rights reserved.  

---
