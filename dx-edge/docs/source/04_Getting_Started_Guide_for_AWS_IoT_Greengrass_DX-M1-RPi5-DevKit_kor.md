# DX-M1 Edge AI Development Kit with Raspberry Pi 5 — AWS IoT Greengrass 시작 가이드

이 가이드는 DEEPX DX-M1 Edge AI Development Kit with Raspberry Pi 5에서 AWS IoT Greengrass V2를 설정하고 디바이스가 AWS IoT 서비스와 통신하는지 확인하는 과정을, 키트 조립부터 첫 Greengrass 컴포넌트 배포까지 순서대로 설명합니다.

## 빠른 시작 경로

다음 다섯 단계로 진행하십시오.

1. DX-M1 Raspberry Pi 5 키트와 하드웨어를 이해합니다.
2. 키트를 조립하고 Raspberry Pi OS 설치, PCIe Gen 3 활성화, AWS 계정 및 Greengrass 사전 요구 사항을 준비합니다.
3. AWS IoT Greengrass를 설치하고 등록합니다.
4. Hello World 컴포넌트를 만들고 배포합니다.
5. 설치 상태를 디버깅하거나 DX-Edge 런타임 배포로 진행합니다.

## 1. 문서 정보

### 1.1 문서 개정 이력

| 개정 | 날짜 | 설명 |
|---|---|---|
| 1.0 | 2026-08-20 | 최초 배포 |

### 1.2 이 가이드가 적용되는 운영체제

이 가이드는 Raspberry Pi 5(aarch64) 호스트와 Raspberry Pi OS(64-bit) 운영체제에서 AWS IoT Greengrass를 실행하는 DEEPX DX-M1 Edge AI Development Kit에 적용됩니다.

| 역할 | 운영체제 |
|---|---|
| 디바이스 (DX-M1 Kit / Raspberry Pi 5) | Raspberry Pi OS (64-bit, Debian 13 "Trixie", aarch64) |
| 호스트 컴퓨터 | 웹 브라우저와 SSH 클라이언트를 사용할 수 있는 모든 OS (Windows 10/11, macOS, Linux) |

## Part I. 디바이스 이해

## 2. 개요

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="img/badges/aws-qualified-device-dark.png">
  <img src="img/badges/aws-qualified-device-light.png" alt="AWS Qualified Device — AWS IoT Greengrass" width="120" align="right">
</picture>

DEEPX DX-M1 Edge AI Development Kit with Raspberry Pi 5는 Raspberry Pi 5(8 GB) 호스트와 DEEPX DX-M1 AI 가속기(M.2 모듈)를 M.2 base HAT으로 결합한 개발 키트로, 가속기 전력 1–5 W에서 최대 25 TOPS의 신경망 추론 성능을 제공합니다. 로컬 NPU 가속 추론과 AWS IoT Greengrass를 통한 클라우드 연결을 함께 활용하는 엣지 AI 비전 프로젝트를 개발하고 평가하려는 개발자를 대상으로 합니다.

이 키트는 Raspberry Pi OS(64-bit, Debian 13 "Trixie", aarch64)에서 AWS IoT Greengrass Core 소프트웨어(클래식 nucleus)를 실행하며, Greengrass 컴포넌트 로컬 실행, Docker 애플리케이션 컴포넌트, 메시징, AWS 클라우드와의 보안 통신을 지원합니다.

![DEEPX DX-M1 Edge AI Development Kit with Raspberry Pi 5](img/rpi5/kit-hero.jpg)

## 3. 하드웨어 설명

### 3.1 데이터시트

- DEEPX DX-M1 제품 정보: https://deepx.ai
- 키트 제품 페이지 (구매): https://www.eleparts.co.kr/goods/view?no=18574428

주요 사양:

| 항목 | 사양 |
|---|---|
| 호스트 보드 | Raspberry Pi 5 (Broadcom BCM2712, quad-core Arm Cortex-A76 @ 2.4 GHz, aarch64) |
| AI 가속기 | DEEPX DX-M1 (M.2 2280 M-Key), 25 TOPS INT8, 4 GB LPDDR5 (5600 MT/s), 1–5 W |
| 메모리 | 8 GB LPDDR4X (host) |
| 스토리지 | microSD card (included) |
| 가속기 인터페이스 | PCIe Gen 3 via MAKEROBO M.2 HAT (DX-M1 supports Gen 1/2/3, x1/x2/x4) |
| 네트워크 | 1x GbE LAN (RJ45) |
| USB | 2x USB 3.0, 2x USB 2.0 |
| 디스플레이 | 2x micro-HDMI |
| OS | Raspberry Pi OS (64-bit, Debian 13 "Trixie") |

### 3.2 기본 구성품

- Raspberry Pi 5 (8 GB RAM) 1개
- DEEPX DX-M1 AI 가속기 (M.2 2280 M-Key 모듈) 1개
- MAKEROBO M.2 HAT for Raspberry Pi 5 (PCIe-to-M.2 캐리어, 모델 CLBPCIEPI5_9) 1개 — 스탠드오프, 나사, PCIe FPC 케이블 포함
- Raspberry Pi 5용 액티브 쿨러 1개
- USB 전원 어댑터 1개
- microSD 카드 (OS 및 프로젝트 저장용) 1개와 USB 카드 리더
- 참고 자료: DX-AllSuite 가이드 (GitHub), 조립 가이드 (PDF), Raspberry Pi 5 사용자 가이드 (PDF)

### 3.3 사용자 준비 항목

- 인터넷 연결용 이더넷 케이블
- 초기 설정용 USB 키보드/마우스와 micro-HDMI 입력을 지원하는 모니터 (또는 네트워크를 통한 SSH 사용)
- 원격 접속용 호스트 컴퓨터

키트에 microSD 카드, 액티브 쿨러, USB 전원 어댑터, 마운팅 부품을 포함한 M.2 HAT이 모두 들어 있으므로, 가속기 캐리어·스토리지·냉각·전원 액세서리를 따로 준비할 필요가 없습니다.

### 3.4 서드파티 구매 항목

없음. 핵심 구성품은 모두 키트에 포함되어 있습니다.

## Part II. 환경 준비

## 4. 개발 환경

### 4.1 도구 설치 (IDE, 툴체인, SDK)

키트에서 AWS IoT Greengrass를 실행하는 데 디바이스 전용 IDE나 툴체인은 필요하지 않습니다. 다음 항목이 필요합니다.

- 명령줄로 설정하려면 디바이스 또는 호스트에 AWS Command Line Interface(AWS CLI)를 설치합니다. [AWS CLI 설치](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)를 참고합니다.
- (선택) DX-M1 가속기를 사용하는 AI 가속 Greengrass 컴포넌트를 개발하려면 DEEPX DX-RT 런타임과 DXNN® SDK를 설치합니다. [DEEPX 기술 문서](https://developer.deepx.ai/tech-docs)를 참고합니다.

## 5. 디바이스 하드웨어 설정

### 5.1 키트 조립

1. 키트에 포함된 조립 가이드에 따라, 제공된 스탠드오프로 M.2 HAT을 Raspberry Pi 5에 고정하고 PCIe FPC 케이블을 연결합니다.
2. DEEPX DX-M1 M.2 모듈을 HAT의 M.2 슬롯에 장착하고 제공된 나사로 고정합니다.
3. 제공된 액티브 쿨러를 Raspberry Pi 5에 장착합니다.
4. Raspberry Pi OS를 설치한 microSD 카드를 삽입합니다([5.2](#52-raspberry-pi-os-설치) 참고).
5. Raspberry Pi 5 LAN 포트에 이더넷 케이블을 연결합니다.
6. (초기 설정) micro-HDMI로 모니터를, USB로 키보드를 연결하거나 SSH 접속을 준비합니다.
7. 제공된 USB 전원 어댑터를 연결해 부팅합니다.

**상단** — Raspberry Pi 5 위 M.2 base HAT에 장착된 DX-M1 모듈:

![조립된 키트 상단](img/rpi5/kit-top.jpg)

**측면** — 적층 구조. Raspberry Pi 5 I/O는 아래쪽 가장자리에서 접근할 수 있습니다:

![조립된 키트 측면](img/rpi5/kit-side.jpg)

### 5.2 Raspberry Pi OS 설치

호스트 컴퓨터에서 Raspberry Pi Imager를 사용해, 동봉된 카드 리더로 연결한 microSD 카드에 **Raspberry Pi OS (64-bit)**를 기록합니다. 이미지 기록 중 또는 첫 부팅 시 사용자 계정을 만들고, 원격으로 작업하려면 SSH를 활성화합니다.

디바이스에서 인터넷 연결을 확인합니다.

```bash
ping -c 3 amazon.com
```

### 5.3 PCIe Gen 3 활성화

DX-M1은 Raspberry Pi 5의 PCIe 인터페이스를 사용합니다. 전체 대역폭을 사용하려면 PCIe Gen 3를 활성화합니다.

```bash
sudo raspi-config
# Advanced Options -> PCIe Speed -> Yes (enable PCIe Gen 3) -> Finish -> reboot
```

재부팅 후 PCIe 버스에서 가속기가 인식되는지 확인합니다.

```bash
lspci | grep -i deepx
# Expected: 0001:01:00.0 Processing accelerators: DEEPX Co., Ltd. DX_M1 (rev 01)
```

### 5.4 DX-M1 드라이버 및 런타임 설치

DX-AllSuite [환경 설정](../../../docs/source/02_Setting_Up_Environment_kor.md) 가이드와 [DEEPX 기술 문서](https://developer.deepx.ai/tech-docs)를 따라 DEEPX NPU 드라이버(DKMS)와 DX-RT 런타임을 설치합니다. 설치 후 다음을 확인합니다.

```bash
lsmod | grep -E 'dxrt|dx_'        # expect dxrt_driver and dx_dma loaded
ls /dev/dxrt0                     # expect the device node to exist
dxrt-cli --version                # expect DX-RT runtime version to print
```

> **참고**
>
> DX-M1 드라이버와 런타임은 가속기에서 AI 추론을 실행하는 데 필요합니다.
> Greengrass Core 소프트웨어 경로를 검증하는 AWS IoT Greengrass 인증과는
> 무관합니다. 이 단계를 건너뛰고 Greengrass 등록 후
> [DEEPX Greengrass Solution](01_DEEPX_Greengrass_Solution_kor.md)으로 OTA 설치할 수도
> 있습니다([다음 단계](#다음-단계--dx-edge로-deepx-런타임-배포하기) 참고).

### 5.5 Greengrass 사전 요구 사항 설치

AWS IoT Greengrass Core 소프트웨어는 Java 런타임 환경(Java 8 이상)을 필요로 합니다.

```bash
sudo apt update
sudo apt install -y default-jre curl unzip
java -version
```

(선택) Docker 애플리케이션 컴포넌트를 배포하려면 Docker Engine을 설치하고 클래식 이미지 저장소를 사용하는지 확인합니다.

```bash
docker --version
docker info | grep -i 'storage driver'   # expect: overlay2
```

## 6. AWS IoT Greengrass 개요

AWS IoT Greengrass에 대한 자세한 내용은 [AWS IoT Greengrass 작동 방식](https://docs.aws.amazon.com/greengrass/v2/developerguide/how-it-works.html)과 [AWS IoT Greengrass 버전 2의 새로운 기능](https://docs.aws.amazon.com/greengrass/v2/developerguide/greengrass-v2-whats-new.html)을 참고합니다.

## 7. Greengrass 사전 요구 사항

AWS IoT Greengrass에 필요한 사전 요구 사항은 온라인 문서에서 확인합니다. [자습서: AWS IoT Greengrass V2 시작하기](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html)의 다음 섹션에 있는 지침을 따릅니다.

- [1단계: AWS 계정 설정](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-set-up-aws-account.html)
- [2단계: 환경 설정](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-prerequisites.html)

## Part III. Greengrass 설치 및 등록

## 8. AWS IoT Greengrass 설치

온라인 가이드 [자동 프로비저닝으로 AWS IoT Greengrass Core 소프트웨어 설치](https://docs.aws.amazon.com/greengrass/v2/developerguide/quick-installation.html)를 따릅니다. 아래 단계는 키트에서의 진행 과정을 요약한 것입니다.

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
  --thing-name DX-M1-RPI5-Core \
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

온라인 문서 [디바이스에서 컴포넌트 개발 및 테스트](https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html#create-first-component)의 지침에 따라 키트에서 간단한 Hello World 컴포넌트를 로컬로 만들고 출력을 확인합니다.

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
| `lspci`에 DX_M1이 표시되지 않음 | `raspi-config`에서 PCIe Gen 3가 활성화되었는지, M.2 모듈이 완전히 장착되었는지, HAT FPC 케이블이 연결되었는지 확인한 뒤 재부팅합니다 |
| `dxrt-cli`를 찾을 수 없음 | DX-M1 드라이버와 DX-RT 런타임을 설치하고([5.4](#54-dx-m1-드라이버-및-런타임-설치) 참고) `lsmod`로 `dxrt_driver`가 로드되었는지 확인합니다 |
| AWS IoT 콘솔에 디바이스가 표시되지 않음 | 인터넷 연결 상태와 AWS 엔드포인트로 나가는 TCP 443이 방화벽에서 허용되는지 확인하고, AWS 리전이 콘솔 리전과 일치하는지 확인합니다 |
| `greengrass.service`가 시작되지 않음 | `/greengrass/v2/logs/greengrass.log`를 확인하고 설치 시 `sudo`를 사용했는지 확인합니다 |
| Docker 컴포넌트 배포 실패 | Docker Engine이 설치되어 있고 `docker info`가 `overlay2` 스토리지 드라이버를 보고하는지 확인합니다 |

자세한 내용은 온라인 문서 [AWS IoT Greengrass V2 문제 해결](https://docs.aws.amazon.com/greengrass/v2/developerguide/troubleshooting.html)을 참고합니다.

디바이스 관련 지원이 필요하면 DEEPX에 tech_support@deepx.ai로 문의하거나 https://deepx.ai/contact-us/technical-support/ 를 방문합니다.

## 다음 단계 — DX-Edge로 DEEPX 런타임 배포하기

디바이스가 AWS IoT Core에 등록되고 Thing Group에 포함되면, AWS Marketplace에서 제공하는 **DEEPX Greengrass Solution**을 사용해 DEEPX NPU 드라이버, 펌웨어, `dx_rt` 런타임, `dx_stream` 미디어 파이프라인을 현장 작업 없이 OTA로 설치할 수 있습니다. [DEEPX Greengrass Solution](01_DEEPX_Greengrass_Solution_kor.md)을 참고합니다.

직접 만든 ONNX 모델을 AWS에서 DEEPX NPU 실행 형식으로 컴파일하려면 [DEEPX Compiler Solution](02_DEEPX_Compiler_Solution_kor.md)을 참고합니다.

---
