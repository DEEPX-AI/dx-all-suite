# DX-AIPlayer N97 — AWS IoT Greengrass 시작 가이드

이 가이드는 DEEPX DX-AIPlayer N97에서 AWS IoT Greengrass V2를 설정하고 디바이스가 AWS IoT 서비스와 통신하는지 확인하는 과정을, 개봉부터 첫 Greengrass 컴포넌트 배포까지 순서대로 설명합니다.

## 빠른 시작 경로

다음 다섯 단계로 진행하십시오.

1. DX-AIPlayer N97과 하드웨어를 이해합니다.
2. 디바이스, 네트워크, AWS 계정, Greengrass 사전 요구 사항을 준비합니다.
3. AWS IoT Greengrass를 설치하고 등록합니다.
4. Hello World 컴포넌트를 만들고 배포합니다.
5. 설치 상태를 디버깅하거나 DX-Edge 런타임 배포로 진행합니다.

## 1. 문서 정보

### 1.1 문서 개정 이력

| 개정 | 날짜 | 설명 |
|---|---|---|
| 1.0 | 2026-08-19 | 최초 배포 |

### 1.2 이 가이드가 적용되는 운영체제

이 가이드는 Intel® Processor N97(x86_64)과 Ubuntu 24.04 LTS 운영체제에서 AWS IoT Greengrass를 실행하는 DX-AIPlayer N97 시스템에 적용됩니다.

| 역할 | 운영체제 |
|---|---|
| 디바이스 (DX-AIPlayer N97) | Ubuntu 24.04 LTS (64-bit, x86_64) |
| 호스트 컴퓨터 | 웹 브라우저와 SSH 클라이언트를 사용할 수 있는 모든 OS (Windows 10/11, macOS, Linux) |

## Part I. 디바이스 이해

## 2. 개요

DX-AIPlayer N97은 Intel® Processor N97(x86_64)과 DEEPX DX-M1 AI 가속기(M.2 모듈)를 기반으로 하는 소형 팬리스 엣지 AI 시스템으로, 가속기 전력 1–5 W에서 최대 25 TOPS의 AI 추론 성능을 제공합니다. 듀얼 GbE LAN, USB 3.2, 시리얼 포트, 온보드 스토리지를 갖추고 있어 로컬 AI 추론과 AWS IoT Greengrass를 통한 클라우드 연결이 함께 필요한 비전 AI, 스마트 팩토리, 리테일 분석 등 엣지 애플리케이션에 적합합니다.

DX-AIPlayer N97은 Ubuntu 24.04 LTS에서 AWS IoT Greengrass Core 소프트웨어(클래식 nucleus)를 실행하며, Greengrass 컴포넌트 로컬 실행, 메시징, 데이터 관리, AWS 클라우드와의 보안 통신을 지원합니다.

## 3. 하드웨어 설명

### 3.1 데이터시트

- 제품 페이지: https://deepx.ai/product/dx-aiplayer-n97/
- 제품 브로슈어 (PDF): https://d3cq9fuihrmma1.cloudfront.net/wp-content/uploads/2026/05/11111133/DEEPX-DX-AIPlayer-N97-AI-Edge-Box-E-Brochure-1.pdf

주요 사양:

| 항목 | 사양 |
|---|---|
| CPU | Intel® Processor N97, quad-core up to 3.6 GHz (x86_64) |
| AI 가속기 | DEEPX DX-M1 (M.2 2280 module), 25 TOPS INT8, 4 GB LPDDR5, max 5 W |
| 메모리 | 8 GB LPDDR5 |
| 스토리지 | 64 GB eMMC onboard |
| 네트워크 | 2x GbE LAN (RJ45); optional Wi-Fi/BT via M.2 2230 E-Key |
| USB | 3x USB 3.2 Gen 2 Type-A |
| 시리얼 | 2x RS-232/422/485 COM ports |
| 디스플레이 | HDMI 2.0b, DisplayPort 1.2 |
| 보안 | TPM 2.0 |
| 전원 | 12V DC-in, 5A (threaded locking barrel jack) |
| 동작 온도 | 0°C to 60°C |
| 크기 / 마운팅 | 95 x 95 x 55 mm / VESA mounting compatible |
| OS | Ubuntu 24.04 LTS |

### 3.2 기본 구성품

- DX-AIPlayer N97 본체 1개 (DEEPX DX-M1 M.2 모듈 사전 장착)
- 전원 어댑터 1개 (12V DC, 5A, threaded locking barrel jack)

### 3.3 사용자 준비 항목

- 인터넷 연결용 이더넷 케이블 (또는 선택 사양인 M.2 2230 E-Key Wi-Fi 모듈)
- 초기 설정용 USB 키보드/마우스와 HDMI 또는 DisplayPort 입력을 지원하는 모니터 (또는 네트워크를 통한 SSH 사용)
- 원격 접속용 호스트 컴퓨터 (초기 설정 이후에는 선택 사항)

### 3.4 서드파티 구매 항목

없음.

## Part II. 환경 준비

## 4. 개발 환경

### 4.1 도구 설치 (IDE, 툴체인, SDK)

DX-AIPlayer N97에서 AWS IoT Greengrass를 실행하는 데 디바이스 전용 IDE나 툴체인은 필요하지 않습니다. 다음 항목이 필요합니다.

- 명령줄로 설정하려면 디바이스 또는 호스트에 AWS Command Line Interface(AWS CLI)를 설치합니다. [AWS CLI 설치](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)를 참고합니다.
- (선택) DX-M1 가속기를 사용하는 AI 가속 Greengrass 컴포넌트를 개발하려면 DEEPX DXNN® SDK를 설치합니다. [DEEPX 기술 문서](https://developer.deepx.ai/tech-docs)을 참고합니다.

## 5. 디바이스 하드웨어 설정

DX-AIPlayer N97은 세 면에 I/O를 배치합니다. 모든 포트는 섀시에 라벨로 표시되어 있습니다.

**우측면** — 2x GbE LAN (LAN 1 / LAN 2), HDMI, DisplayPort (DP), 2x USB 3.2 Gen 2, 12V DC 전원 잭, 전원 버튼:

![우측면 포트](img/n97/n97-right.png)

**좌측면** — COM 1 (RS-232/422/485), USB 3.2 Gen 2, Wi-Fi/BT 안테나 마운트:

![좌측면 포트](img/n97/n97-left.png)

**후면** — COM 2 (RS-232/422/485), Line Out, Mic In:

![후면 포트](img/n97/n97-back.png)

1. 평평하고 통풍이 잘되는 곳에 디바이스를 놓습니다.
2. 인터넷에 연결된 네트워크의 이더넷 케이블을 우측면의 **LAN 1**에 연결합니다.
3. (초기 설정) 모니터(우측면 HDMI 또는 DP)와 USB 키보드를 연결하거나, SSH 접속을 위해 디바이스 IP 주소를 확인해 둡니다.
4. 제공된 전원 어댑터를 우측면의 **12V DC** 잭에 연결하고 전원 버튼을 누릅니다.
5. 첫 부팅 시 Ubuntu 초기 설정을 완료해 사용자 계정을 생성한 뒤, 생성한 계정으로 로그인합니다.

인터넷 연결을 확인합니다.

```bash
ping -c 3 amazon.com
```

사전 요구 사항을 설치합니다. AWS IoT Greengrass Core 소프트웨어는 Java 런타임 환경(Java 8 이상)과 일반적인 Linux 유틸리티를 필요로 합니다(Ubuntu 24.04에 이미 포함되어 있습니다).

```bash
sudo apt update
sudo apt install -y default-jre curl unzip
java -version
```

## 6. AWS IoT Greengrass 개요

AWS IoT Greengrass에 대한 자세한 내용은 [AWS IoT Greengrass 작동 방식](https://docs.aws.amazon.com/greengrass/v2/developerguide/how-it-works.html)과 [AWS IoT Greengrass 버전 2의 새로운 기능](https://docs.aws.amazon.com/greengrass/v2/developerguide/greengrass-v2-whats-new.html)을 참고합니다.

## 7. Greengrass 사전 요구 사항

AWS IoT Greengrass에 필요한 사전 요구 사항은 온라인 문서에서 확인합니다. [자습서: AWS IoT Greengrass V2 시작하기](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html)의 다음 섹션에 있는 지침을 따릅니다.

- [1단계: AWS 계정 설정](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-set-up-aws-account.html)
- [2단계: 환경 설정](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-prerequisites.html)

## Part III. Greengrass 설치 및 등록

## 8. AWS IoT Greengrass 설치

온라인 가이드 [자동 프로비저닝으로 AWS IoT Greengrass Core 소프트웨어 설치](https://docs.aws.amazon.com/greengrass/v2/developerguide/quick-installation.html)를 따릅니다. 아래 단계는 DX-AIPlayer N97에서의 진행 과정을 요약한 것입니다.

1. 디바이스에 AWS 자격 증명을 제공합니다. 개발 환경에서는 IAM 사용자의 장기 자격 증명을 사용할 수 있습니다.

```bash
export AWS_ACCESS_KEY_ID=<the access key id for your user>
export AWS_SECRET_ACCESS_KEY=<the secret access key for your user>
```

> **보안 참고**
>
> 장기 IAM 사용자 자격 증명은 개발 및 테스트 환경에서만 사용하십시오.
> 운영 환경에서는 IAM 역할 또는 임시 자격 증명을 사용하고, 조직의 자격 증명
> 관리 정책을 따르십시오.

2. AWS IoT Greengrass Core 소프트웨어를 내려받습니다.

```bash
cd ~
curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-nucleus-latest.zip -o greengrass-nucleus-latest.zip
unzip greengrass-nucleus-latest.zip -d GreengrassInstaller
```

3. AWS IoT Greengrass Core 소프트웨어를 설치합니다(리전, 사물 이름, 그룹 이름은 필요에 맞게 변경합니다).

```bash
sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE \
  -jar ./GreengrassInstaller/lib/Greengrass.jar \
  --aws-region ap-northeast-2 \
  --thing-name DX-AIPlayer-N97-Core \
  --thing-group-name DXGreengrassGroup \
  --thing-policy-name GreengrassV2IoTThingPolicy \
  --tes-role-name GreengrassV2TokenExchangeRole \
  --tes-role-alias-name GreengrassCoreTokenExchangeRoleAlias \
  --component-default-user ggc_user:ggc_group \
  --provision true \
  --setup-system-service true
```

4. Greengrass Core 소프트웨어가 실행 중인지 확인합니다.

```bash
sudo systemctl status greengrass.service
```

AWS IoT 콘솔의 **Greengrass devices > Core devices**에서 디바이스 상태가 **Healthy**인지도 확인할 수 있습니다.

## Part IV. 첫 번째 컴포넌트 배포

## 9. "Hello World" 컴포넌트

### 9.1 엣지 디바이스에서 컴포넌트 만들기

온라인 문서 [디바이스에서 컴포넌트 개발 및 테스트](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html#create-first-component)의 지침에 따라 DX-AIPlayer N97에서 간단한 Hello World 컴포넌트를 로컬로 만들고 출력을 확인합니다.

```bash
sudo tail -f /greengrass/v2/logs/com.example.HelloWorld.log
```

### 9.2 "Hello World" 컴포넌트 업로드

온라인 문서 [AWS IoT Greengrass 서비스에서 컴포넌트 생성](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html#upload-first-component)의 지침에 따라 컴포넌트를 클라우드에 업로드합니다. 업로드한 컴포넌트는 필요에 따라 다른 디바이스에 배포할 수 있습니다.

### 9.3 컴포넌트 배포

온라인 문서 [컴포넌트 배포](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html#deploy-first-component)의 지침에 따라 AWS IoT 콘솔에서 컴포넌트를 배포하고 디바이스에서 정상 실행되는지 확인합니다.

## Part V. 운영 및 문제 해결

## 10. 디버깅

- Greengrass Core 로그는 `/greengrass/v2/logs/greengrass.log`에, 컴포넌트 로그는 `/greengrass/v2/logs/<component-name>.log`에 있습니다.
- nucleus 로그 수준을 변경하려면 [로그 수준](https://docs.aws.amazon.com/greengrass/v2/developerguide/monitor-logs.html)을 참고합니다.
- 시스템 부팅 및 서비스 메시지를 확인하려면 `journalctl -u greengrass.service -f`를 사용합니다.

## 11. 문제 해결

| 증상 | 해결 방법 |
|---|---|
| 설치 프로그램이 `java: command not found`로 실패 | Java를 설치한 뒤(`sudo apt install -y default-jre`) 설치 프로그램을 다시 실행합니다 |
| AWS IoT 콘솔에 디바이스가 표시되지 않음 | 인터넷 연결 상태와 AWS 엔드포인트로 나가는 TCP 443이 방화벽에서 허용되는지 확인하고, AWS 리전이 콘솔 리전과 일치하는지 확인합니다 |
| `greengrass.service`가 시작되지 않음 | `/greengrass/v2/logs/greengrass.log`를 확인하고, `/tmp`가 `exec` 옵션으로 마운트되었는지와 설치 시 `sudo`를 사용했는지 확인합니다 |
| 컴포넌트 배포가 진행되지 않음 | 토큰 교환 역할이 생성되었는지(`--provision true` 출력) 확인하고 콘솔에서 배포 상태를 확인합니다 |

자세한 내용은 온라인 문서 [AWS IoT Greengrass V2 문제 해결](https://docs.aws.amazon.com/greengrass/v2/developerguide/troubleshooting.html)을 참고합니다.

디바이스 관련 지원이 필요하면 DEEPX에 tech_support@deepx.ai로 문의하거나 https://deepx.ai/contact-us/technical-support/ 를 방문합니다.

## 다음 단계 — DX-Edge로 DEEPX 런타임 배포하기

디바이스가 AWS IoT Core에 등록되고 Thing Group에 포함되면, AWS Marketplace에서 제공하는 **DEEPX Greengrass Solution**을 사용해 DEEPX NPU 드라이버, 펌웨어, `dx_rt` 런타임, `dx_stream` 미디어 파이프라인을 현장 작업 없이 OTA로 설치할 수 있습니다. [DEEPX Greengrass Solution](01_DEEPX_Greengrass_Solution_kor.md)을 참고합니다.

직접 만든 ONNX 모델을 AWS에서 DEEPX NPU 실행 형식으로 컴파일하려면 [DEEPX Compiler Solution](02_DEEPX_Compiler_Solution_kor.md)을 참고합니다.
