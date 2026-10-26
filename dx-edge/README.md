# DX-Edge <picture><source media="(prefers-color-scheme: dark)" srcset="docs/source/img/badges/available-in-aws-marketplace-dark.png"><img src="docs/source/img/badges/available-in-aws-marketplace-light.png" alt="Available in AWS Marketplace" height="40" align="right"></picture><picture><source media="(prefers-color-scheme: dark)" srcset="docs/source/img/badges/powered-by-aws-dark.png"><img src="docs/source/img/badges/powered-by-aws-light.png" alt="Powered by AWS" height="32" align="right"></picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/source/img/badges/aws-partner-dark.png">
  <img src="docs/source/img/badges/aws-partner-light.png" alt="AWS Partner" width="120" align="right">
</picture>

DX-Edge is the AWS-native path for taking a trained model to a DEEPX NPU running in the field. It covers the three things that stand between a trained ONNX model and a working edge deployment — compiling the model for the NPU, provisioning the runtime on the device, and having qualified hardware to run it on — and it does each of them through AWS services you already operate.

한국어 문서는 [README-KO.md](README-KO.md)를 참고하십시오.

---

## Four tracks

| Track | What it does | AWS delivery | Guide |
| :--- | :--- | :--- | :--- |
| **DEEPX Greengrass Solution** | Compiles ONNX models to `.dxnn` in the cloud, then installs the NPU driver, firmware, `dx_rt`, and `dx_stream` on edge devices over the air (ZTP) via AWS IoT Greengrass V2 | CloudFormation stack on AWS Marketplace | [Guide](docs/source/01_DEEPX_Greengrass_Solution.md) · [한국어](docs/source/01_DEEPX_Greengrass_Solution_kor.md) |
| **DEEPX Compiler Solution** | Compiles ONNX models into the DEEPX NPU execution format (DXNN) on AWS — either interactively on an EC2 instance or through an event-driven S3 → Lambda → Step Functions pipeline | AMI on AWS Marketplace | [Guide](docs/source/02_DEEPX_Compiler_Solution.md) · [한국어](docs/source/02_DEEPX_Compiler_Solution_kor.md) |
| **AWS HW Path — DX-AIPlayer N97** | A compact edge AI system (Intel® N97 + DEEPX DX-M1) running Ubuntu 24.04 LTS, set up as an AWS IoT Greengrass core device from unboxing to first component deployment | Hardware | [Getting Started Guide](docs/source/03_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-AIPlayer-N97.md) · [한국어](docs/source/03_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-AIPlayer-N97_kor.md) |
| **AWS HW Path — DX-M1 Raspberry Pi 5 Dev Kit** | A development kit (Raspberry Pi 5 8 GB + DEEPX DX-M1 on an M.2 HAT) running Raspberry Pi OS (64-bit), set up as an AWS IoT Greengrass core device from assembly to first component deployment | Hardware | [Getting Started Guide](docs/source/04_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-M1-RPi5-DevKit.md) · [한국어](docs/source/04_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-M1-RPi5-DevKit_kor.md) |

## How the tracks fit together

```
   ONNX model                DEEPX Compiler Solution              .dxnn artifact
       │                  (DEEPX Compiler Solution AMI)                  │
       └──────────────────────────────►─────────────────────────────────┘
                                                                        │
   Edge device                DEEPX Greengrass Solution                 ▼
   (DX-AIPlayer N97,   ──►    driver · firmware · dx_rt · dx_stream  ──► inference
    Raspberry Pi 5,           installed over the air (ZTP) via
    x86_64 Ubuntu host)       AWS IoT Greengrass V2
```

The Greengrass Solution includes the compilation pipeline, so it is the single-stack option. The Compiler Solution is the right choice when you only need model compilation and manage device runtimes yourself.

## AWS Marketplace listings

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/source/img/badges/aws-qualified-software-dark.png">
  <img src="docs/source/img/badges/aws-qualified-software-light.png" alt="AWS Qualified Software" width="120" align="right">
</picture>

- **[DEEPX Greengrass Solution](https://aws.amazon.com/marketplace/pp/prodview-732s46qfzuh34)** (CloudFormation) — compilation pipeline + automated edge runtime deployment
- **[DEEPX Compiler Solution](https://aws.amazon.com/marketplace/pp/prodview-ev6ed5omu4ulo)** (AMI) — model compilation on its own, deployable as an Amazon EC2 instance or as an AWS CloudFormation stack

You pay for the AWS resources you use; see each AWS Marketplace listing for software pricing and subscription terms.

## AWS services used

AWS CloudFormation · Amazon S3 · AWS Lambda · AWS Step Functions · Amazon EC2 · AWS Systems Manager · Amazon CloudWatch Logs · AWS IoT Core · AWS IoT Greengrass V2

## Validated hardware

| Hardware | Specification |
| :--- | :--- |
| **DEEPX DX-M1** | M.2 2280 AI accelerator, 25 TOPS INT8, 4 GB LPDDR5, max 5 W. Installs in an arm64 host such as a Raspberry Pi 5 or an x86_64 industrial PC |
| **DX-AIPlayer N97** | Intel® Processor N97 (x86_64) + DX-M1, 8 GB LPDDR5 / 64 GB eMMC, 2x GbE, Ubuntu 24.04 LTS, 95 x 95 x 55 mm |
| **DX-M1 Edge AI Development Kit with Raspberry Pi 5** | Raspberry Pi 5 8 GB (aarch64) + DX-M1 over PCIe Gen 3 (M.2 HAT), microSD, 1x GbE, Raspberry Pi OS (64-bit, Debian 13 "Trixie") |

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/source/img/badges/aws-qualified-device-dark.png">
  <img src="docs/source/img/badges/aws-qualified-device-light.png" alt="AWS Qualified Device — AWS IoT Greengrass" width="120" align="right">
</picture>

The DX-AIPlayer N97 and the DX-M1 Edge AI Development Kit with Raspberry Pi 5 are AWS Qualified Devices for AWS IoT Greengrass; each has a Getting Started Guide listed above. Both the classic AWS IoT Greengrass nucleus and Greengrass nucleus lite for resource-constrained devices are supported.

## Documentation

```
dx-edge/
├── README.md / README-KO.md
└── docs/source/
    ├── 01_DEEPX_Greengrass_Solution.md                                    (+ _kor)
    ├── 02_DEEPX_Compiler_Solution.md                                      (+ _kor)
    ├── 03_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-AIPlayer-N97.md (+ _kor)
    ├── 04_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-M1-RPi5-DevKit.md (+ _kor)
    └── img/{greengrass,compiler,n97,rpi5}/
```

The DX-AIPlayer N97 and DX-M1 Raspberry Pi 5 Dev Kit documents follow the AWS Device Qualification Program *Getting Started Guide for AWS IoT Greengrass Devices* template, and carry every mandatory section in the template's order.

## Related

- [DEEPX Developer Documentation](https://developer.deepx.ai)
- [DEEPX ModelZoo](https://developer.deepx.ai/modelzoo/)
- [DEEPX DX-AllSuite](https://github.com/DEEPX-AI/dx-all-suite)

For technical support, contact tech_support@deepx.ai or visit https://deepx.ai/contact-us/technical-support/

---
