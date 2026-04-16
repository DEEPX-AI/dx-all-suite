# DX-AllSuite Architecture Overview

이 가이드는 **DXNN (DEEPX Neural Network)** SDK 아키텍처, 핵심 모듈 및 지원 환경에 대한 포괄적인 개요를 제공합니다.  

## Why DX-AllSuite?

**DX-AllSuite**는 모델 최적화부터 타겟 하드웨어 배포에 이르는 복잡한 파이프라인을 **단일 워크플로우(Single Workflow)**로 통합합니다.  

- **제로 코드 배포(Zero-Code Deployment)**: 데스크톱에서 검증된 로직을 코드 수정 없이 엣지 디바이스에 직접 배포할 수 있습니다.  
- **자원 최적화(Resource Optimization)**: 환경 설정 및 시스템 통합에 소요되는 시간을 단축하여 고성능 AI 애플리케이션 구축에 집중할 수 있도록 합니다.  
- **엔드 투 엔드 솔루션(End-to-End Solution)**: 단일 패키지 내에서 모델 컴파일, 시뮬레이션, 런타임 실행 및 모니터링을 제공합니다.  

## System Architecture & Core Modules

<div align="center">
  <img src="./resources/DXNN-SDK-Full-Architecture.png" width="600">
  <p><strong>Figure. DXNN SDK Full Architecture Overview.</strong></p>
</div>

**[1] AI 모델 컴파일 환경 (호스트 플랫폼)**  
이 환경은 훈련된 AI 모델을 DEEPX NPU 전용 바이너리(`.dxnn`)로 변환하고 최적화합니다. **x86_64** PC 환경을 지원합니다.  

- **DX-COM (컴파일러)**: ONNX 모델과 사용자 설정(JSON) 파일을 기반으로 `.dxnn` 바이너리를 생성하는 핵심 컴파일러입니다. 고유한 알고리즘을 사용하여 모델을 하드웨어에 최적화된 명령어로 변환하는 동시에 정확도 손실을 최소화하며, 저지연 및 고효율 추론을 가능하게 합니다.  
- **DX-TRON (시각화 도구)**: `.dxnn` 모델의 구조를 시각화하고 분석하는 GUI 도구입니다. NPU와 CPU 간의 작업 부하 분산을 색상으로 구분된 그래프로 직관적으로 보여주어, 개발자가 실행 흐름을 이해하고 성능을 최적화할 수 있도록 돕습니다.  
- **DX-ModelZoo**: DEEPX NPU에 최적화된 사전 훈련 모델 저장소입니다. ONNX 모델, JSON 설정 및 사전 컴파일된 `.dxnn` 바이너리를 제공함으로써, 개발자가 별도의 컴파일 과정 없이 즉시 모델을 테스트하고 배포할 수 있게 합니다.  

**[2] AI 모델 런타임 환경 (타겟 플랫폼)**  
이 환경은 최적화된 .dxnn 모델을 실제 NPU 하드웨어에서 실행하고 애플리케이션에 통합합니다. **x86_64** 및 **aarch64** 환경을 모두 지원합니다.  

- **DX-RT (런타임)**: 펌웨어 및 드라이버와 상호 작용하여 DEEPX NPU에서 .dxnn 모델을 실행하는 핵심 소프트웨어입니다. 모델 로딩, I/O 버퍼, 추론 실행 및 실시간 모니터링을 관리하며, C/C++ 및 Python API를 통해 유연한 제어를 제공합니다.  
- **DX-APP**: DX-RT 기반으로 제작된 샘플 애플리케이션입니다. 주요 비전 작업(객체 탐지, 얼굴 인식, 이미지 분류 등)에 대한 참조 코드를 제공하여 개발자가 이러한 템플릿을 사용해 독창적인 AI 앱을 빠르게 구축할 수 있도록 합니다.  
- **DX-Stream**: 실시간 비디오 데이터를 DEEPX NPU 추론과 연결하는 GStreamer 기반 커스텀 플러그인입니다. 전처리, 추론, 후처리를 아우르는 모듈형 파이프라인을 제공하며, 지능형 카메라와 같은 고성능 비전 AI 애플리케이션에 최적화되어 있습니다.  
- **드라이버 및 펌웨어(Driver & FW)**: PCIe 인터페이스를 통한 고속 데이터 통신을 지원하고 NPU 자원 스케줄링 및 전력을 관리합니다. 하드웨어와 소프트웨어 간의 안정성을 보장하는 동시에 하드웨어의 잠재력을 극대화하여 원활한 추론 환경을 제공합니다.  

**개발 워크플로우**  
훈련된 모델에서 NPU 가속에 이르는 경로는 네 가지 논리적 단계를 따릅니다.  

- **단계 1. 모델 준비**: PyTorch 또는 TensorFlow에서 훈련된 모델을 **ONNX** 형식으로 내보냅니다.  
- **단계 2. 최적화 (호스트)**: 양자화 및 하드웨어 최적화를 포함한 **DX-COM**을 사용하여 모델을 컴파일하고 `.dxnn` 파일을 생성합니다.  
- **단계 3. 배포 (타겟)**: 생성된 `.dxnn` 파일을 타겟 디바이스로 전송합니다.  
- **단계 4. 실행 (타겟)**: **DX-RT**를 통해 DEEPX NPU에서 고속 추론을 실행합니다.  

## Technical Compatibility (Support Matrix)

**DX-AllSuite**는 최신 운영 체제 및 다양한 하드웨어 아키텍처와 입증된 호환성을 제공하여 개발 환경과 엣지 배포 간의 안정적인 가교 역할을 합니다.  

<div align="center">
  <img src="./resources/dx-compiler-2.png" width="300" height="200">
  <img src="./resources/dx-runtime-2.png" width="300" height="200">
  <p><strong>Figure. DX-Compiler & DX-Runtime Support Ecosystem.</strong></p>
</div>

### Hardware & OS (Platform)

다음 표는 컴파일(호스트) 및 실행(타겟) 단계에서 지원되는 환경을 나타냅니다.  

| 카테고리 | DX-Compiler (호스트) | DX-Runtime (타겟) |
| :--- | :--- | :--- |
| **아키텍처** | x86_64 | x86_64, aarch64 |
| **OS** | Ubuntu 24.04/22.04/20.04,<br>Fedora, Redhat, CentOS | Ubuntu 24.04/22.04/20.04/18.04,<br>Debian 13/12, Windows 11/10 |
| **언어** | Python 3.8, 3.9, 3.10, 3.11, 3.12 | Python 3.8 이상,<br>C++14 이상 (C++17 for MSVC/Windows) |

### Model & Software Ecosystem

**지원되는 AI 프레임워크**  
DX-AllSuite는 리팩토링을 최소화하기 위해 업계 표준 프레임워크와 원활하게 통합됩니다.  

- **프레임워크**: Ultralytics (YOLO), TensorFlow, PyTorch, Keras  
- **형식**: ONNX (기본 교환 형식)  

**글로벌 AI 생태계 파트너**  
다양한 업계 선도 플랫폼 내에서 DXNN SDK가 완벽하게 작동할 수 있도록 강력한 기술 파트너십을 유지하고 있습니다.  

- **클라우드 및 플랫폼**: AWS (IoT Greengrass), Baidu, DeGirum  
- **비전 및 알고리즘**: Ultralytics (YOLO Series), CVEDIA  
- **VMS 및 보안**: Network Optix (Nx), VCA (Applied Intelligence)  
- **임베디드 OS**: Wind River (VxWorks)  

## DEEPX ModelZoo & Supported Tasks

DEEPX ModelZoo는 **270개 이상의 사전 검증된 모델**을 제공하는 종합 저장소입니다. 사용자는 수동 컴파일 과정 없이 다양한 하드웨어 프로파일에서 성능과 정확도를 즉시 확인할 수 있습니다.  

| 작업 | 대표 모델 |
| :--- | :--- |
| **Image Classification** | ResNet, ResNeXt, MobileNet, EfficientNet (Lite/V2),<br>ViT/DeiT/BEiT, MobileViT, FastViT, CasViT,<br>RegNet, ShuffleNet, VGG |
| **Object Detection** | YOLO families (YOLOv3–YOLOv11, YOLOX, YOLO26),<br>SSD, EfficientDet, NanoDet, DamoYOLO |
| **Instance Segmentation** | YOLACT, YOLOv5-Seg, YOLOv8-Seg, YOLO26-Seg |
| **Semantic Segmentation** | DeepLabV3/DeepLabV3+, SegFormer, BiSeNet, UNet |
| **Oriented Object Detection (OBB)** | YOLO26-OBB |
| **Zero-shot Instance Segmentation** | FastSAM |
| **Face Detection** | RetinaFace, SCRFD, ULFGED, YOLOv5-Face, YOLOv7-Face |
| **Face Recognition** | ArcFace (IResNet50/100, MobileFaceNet, R50) |
| **Face Landmark** | TDDFA v2 (MobileNet variants) |
| **Face Attribute** | FaceAttrResNetV1-18 |
| **Pose Estimation (Human)** | CenterPose, YOLO26-Pose, YOLOv8-Pose |
| **Hand Landmark** | MediaPipeHandsLite |
| **Person Attribute** | DeepMAR (ResNet18/50) |
| **Depth Estimation** | FastDepth, SCDepthV3 |
| **Image Denoising** | DnCNN variants |
| **Low-light Enhancement** | ZeroDCE |
| **Super-resolution** | ESPCN (x2/x3/x4) |

**ModelZoo 파이프라인의 핵심 기능**  

-	**YAML 중심 오케스트레이션**: 높은 재현성과 쉬운 운영을 위해 전처리, 후처리, 평가 및 컴파일 설정을 단일 YAML 파일에서 관리합니다.  
-	**통합 워크플로우**: 리스트 확인, 정보 조회, 평가, 컴파일 및 벤치마크 기능을 단일 CLI 시스템으로 통합하여 단계별 유연한 조합이 가능합니다.  
-	**최적화된 멀티 프로파일 지원**: 모든 모델은 DEEPX NPU 아키텍처에 맞게 양자화 및 최적화되어, ONNX 평가부터 NPU 실행까지 일관된 검증을 보장합니다.  
-	**확장 가능한 레지스트리**: 전/후처리, 데이터셋 및 평가기에 대한 플러그인 방식의 확장을 지원하여 커스텀 모델의 빠른 온보딩이 가능합니다.  
-	**광범위한 작업 지원**: 단순 분류 및 탐지를 넘어 얼굴 분석, OBB, 이미지 향상 등 서비스 준비가 완료된 다양한 비전 작업을 폭넓게 지원합니다.  

Copyright © DEEPX. All rights reserved.  

---
