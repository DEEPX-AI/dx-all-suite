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

## Getting Started

**DX-AllSuite** provides two environments depending on your intended use. Choose the environment that fits your needs to get started.

### AI Model Compile Environment (Host PC)  

This environment is used for converting and optimizing trained AI models into DEEPX NPU-specific binaries.  

- **Arch**: x86_64  
- **OS**: Ubuntu 26.04 / 24.04 / 22.04 / 20.04 (LTS), Fedora 42-45, Red Hat Enterprise Linux 9-10, and CentOS Stream 9-10
-	**Hardware**: x86_64 Host PC  
- **Software**: Python 3.8~3.14, CUDA (Optional for simulation)
-	**Key Tasks**: AI model (`.onnx`) compilation, Quantization, `.dxnn` generation  
-	**Action**: DX-Compiler Local Installation Guide [Link]  

### AI Model Runtime Environment (Target Device)

This environment is for performing inference and running applications on devices physically equipped with DEEPX NPUs.  

-	**Arch**: x86_64, aarch64 
-	**OS**: Ubuntu 26.04 / 24.04 / 22.04 / 20.04 (LTS), Debian 13 / 12
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

- **★ [Agent-Driven Development (Beta)](./docs/source/00_Agent_Driven_Development.md)**: Build DEEPX apps with natural-language prompts using AI coding agents (Claude Code, Cursor, GitHub Copilot, OpenCode, Codex CLI)  
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
