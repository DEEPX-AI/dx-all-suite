# DX-Edge

**Powered by AWS · Available on AWS Marketplace**

DX-Edge는 학습된 모델을 현장의 DEEPX NPU에서 실행하기까지의 과정을 AWS 기반으로 완성하는 경로입니다. 학습된 ONNX 모델과 실제 엣지 배포 사이에 놓인 세 가지 — NPU용 모델 컴파일, 디바이스 런타임 프로비저닝, 그리고 이를 실행할 검증된 하드웨어 — 를 이미 운영 중인 AWS 서비스로 해결합니다.

For the English edition, see [README.md](README.md).

---

## 세 가지 트랙

| 트랙 | 역할 | AWS 제공 형태 | 문서 |
| :--- | :--- | :--- | :--- |
| **DEEPX Greengrass Solution** | 클라우드에서 ONNX 모델을 `.dxnn`으로 컴파일하고, AWS IoT Greengrass V2를 통해 NPU 드라이버·펌웨어·`dx_rt`·`dx_stream`을 엣지 디바이스에 OTA로 설치(ZTP) | AWS Marketplace CloudFormation 스택 | [문서](docs/source/01_DEEPX_Greengrass_Solution_kor.md) · [English](docs/source/01_DEEPX_Greengrass_Solution.md) |
| **DEEPX Compiler Solution** | ONNX 모델을 DEEPX NPU 실행 형식(DXNN)으로 AWS에서 컴파일. EC2 인스턴스에서 대화형으로 실행하거나, S3 → Lambda → Step Functions 이벤트 기반 파이프라인으로 자동 실행 | AWS Marketplace AMI | [문서](docs/source/02_DEEPX_Compiler_Solution_kor.md) · [English](docs/source/02_DEEPX_Compiler_Solution.md) |
| **AWS HW Path — DX-AIPlayer N97** | Intel® N97과 DEEPX DX-M1을 탑재하고 Ubuntu 24.04 LTS로 동작하는 소형 엣지 AI 시스템. 개봉부터 첫 컴포넌트 배포까지 AWS IoT Greengrass 코어 디바이스로 구성 | 하드웨어 | [시작 가이드](docs/source/03_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-AIPlayer-N97_kor.md) · [English](docs/source/03_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-AIPlayer-N97.md) |

## 세 트랙의 관계

```
   ONNX 모델                 DEEPX Compiler Solution              .dxnn 아티팩트
       │                  (DEEPX Compiler Solution AMI)                  │
       └──────────────────────────────►─────────────────────────────────┘
                                                                        │
   엣지 디바이스              DEEPX Greengrass Solution                  ▼
   (DX-AIPlayer N97,   ──►    드라이버 · 펌웨어 · dx_rt · dx_stream  ──►  추론
    Raspberry Pi 5,           AWS IoT Greengrass V2 기반
    x86_64 Ubuntu 호스트)      OTA 설치 (ZTP)
```

Greengrass Solution은 컴파일 파이프라인을 포함하므로 단일 스택으로 전체 흐름을 구성할 수 있습니다. 모델 컴파일만 필요하고 디바이스 런타임은 직접 관리한다면 Compiler Solution을 선택합니다.

## AWS Marketplace 리스팅

- **[DEEPX Greengrass Solution](https://aws.amazon.com/marketplace/pp/prodview-732s46qfzuh34)** (CloudFormation) — 컴파일 파이프라인 + 엣지 런타임 자동 배포
- **[DEEPX Compiler Solution](https://aws.amazon.com/marketplace/pp/prodview-ev6ed5omu4ulo)** (AMI) — 모델 컴파일 단독 사용. Amazon EC2 인스턴스 또는 AWS CloudFormation 스택으로 배포

AWS 리소스 사용 비용이 별도로 발생하며, 소프트웨어 요금과 구독 조건은 각 Marketplace 리스팅을 확인하십시오.

## 사용하는 AWS 서비스

AWS CloudFormation · Amazon S3 · AWS Lambda · AWS Step Functions · Amazon EC2 · AWS Systems Manager · Amazon CloudWatch Logs · AWS IoT Core · AWS IoT Greengrass V2

## 검증된 하드웨어

| 하드웨어 | 사양 |
| :--- | :--- |
| **DEEPX DX-M1** | M.2 2280 AI 가속기, 25 TOPS INT8, 4 GB LPDDR5, 최대 5 W. Raspberry Pi 5 같은 arm64 호스트나 x86_64 산업용 PC에 장착 |
| **DX-AIPlayer N97** | Intel® Processor N97 (x86_64) + DX-M1, 8 GB LPDDR5 / 64 GB eMMC, 2x GbE, Ubuntu 24.04 LTS, 95 x 95 x 55 mm |

클래식 AWS IoT Greengrass nucleus와 경량 디바이스용 Greengrass nucleus lite를 모두 지원합니다.

## 문서 구성

```
dx-edge/
├── README.md / README-KO.md
└── docs/source/
    ├── 01_DEEPX_Greengrass_Solution.md                                    (+ _kor)
    ├── 02_DEEPX_Compiler_Solution.md                                      (+ _kor)
    ├── 03_Getting_Started_Guide_for_AWS_IoT_Greengrass_DX-AIPlayer-N97.md (+ _kor)
    └── img/{greengrass,compiler,n97}/
```

DX-AIPlayer N97 문서는 AWS Device Qualification Program의 *Getting Started Guide for AWS IoT Greengrass Devices* 템플릿을 따르며, 템플릿의 모든 필수 섹션을 같은 순서로 포함합니다.

## 관련 링크

- [DEEPX 개발자 문서](https://developer.deepx.ai)
- [DEEPX Model Zoo](https://developer.deepx.ai/modelzoo/)
- [DEEPX dx-all-suite](https://github.com/DEEPX-AI/dx-all-suite)

기술 지원은 tech_support@deepx.ai 또는 https://deepx.ai/contact-us/technical-support/ 로 문의하십시오.