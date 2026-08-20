# DEEPX Compiler Solution

**AWS에서 ONNX 모델을 DEEPX NPU 실행 형식(DXNN)으로 컴파일하기**

DEEPX NPU는 표준 ONNX 모델을 그대로 실행하지 않습니다. NPU가 실행할 수 있는 명령 집합과 가중치를 담은 DXNN(`.dxnn`) 형식으로 먼저 변환해야 하며, 이 변환을 담당하는 것이 DEEPX 컴파일러(`dx-com`)입니다. 컴파일 과정에는 INT8 양자화를 위한 캘리브레이션이 포함되므로 대표 데이터셋과 충분한 CPU·메모리 자원이 필요합니다.

이 문서에서는 **DEEPX Compiler Solution**을 사용해 이 컴파일 단계를 AWS에서 수행하는 방법을 설명합니다. 로컬에 컴파일 환경을 구축하지 않고, AWS Marketplace의 DEEPX Compiler Solution으로 필요할 때만 AWS에서 컴파일러를 실행하는 방식입니다.

> **참고 — 이 문서의 범위**
>
> 이 문서는 **모델 컴파일만** 다룹니다. 컴파일된 DXNN 모델을 엣지 디바이스에 배포하고 NPU 드라이버·펌웨어·런타임까지 자동으로 설치하려면 [DEEPX Greengrass Solution](01_DEEPX_Greengrass_Solution_kor.md)을 참고하십시오. Greengrass Solution은 이 문서에서 설명하는 컴파일 파이프라인을 포함합니다.

## 컴파일 경로 선택

작업 방식에 맞는 컴파일 경로를 선택하십시오.

1. 2절에서 공통 사전 요구 사항을 준비합니다.
2. 대화형 컴파일과 반복적인 옵션 변경이 필요하면 3절의 Amazon EC2 배포를 따릅니다.
3. 반복 가능하고 이벤트 기반인 컴파일이 필요하면 4절의 AWS CloudFormation 배포를 따릅니다.
4. 5절과 6절에서 모델 설정과 Model Zoo 사용 방법을 확인합니다.
5. 종료 전에 비용, 문제 해결, 리소스 정리 안내를 확인합니다.

---

## Part I. 배포 방식 선택 및 준비

## 1. 두 가지 배포 방식

**DEEPX Compiler Solution**은 AWS Marketplace의 ML Solutions 카테고리에 Amazon Machine Image로 등록되어 있으며, 배포 화면에서 두 가지 배포 서비스를 선택할 수 있습니다. 작업 방식에 맞는 쪽을 고르면 됩니다.

![AWS Marketplace의 DEEPX Compiler Solution 리스팅](img/compiler/fig01_marketplace_listing.png)

*그림 1. AWS Marketplace의 DEEPX Compiler Solution 제품 페이지*

| | **Amazon EC2** | **AWS CloudFormation** |
| :--- | :--- | :--- |
| 배포 화면의 설명 | Custom deployment using Amazon Machine Image (AMI) | Automated, one-step deployment |
| 실행 방식 | 인스턴스를 직접 시작하고 컴파일러를 실행 | Amazon S3에 파일을 업로드하면 컴파일이 자동 시작 |
| 적합한 상황 | 컴파일 옵션을 반복적으로 바꿔가며 실험, 대화형 디버깅 | 정형화된 컴파일을 반복 수행, CI/자동화 연계 |
| 인스턴스 수명 | 사용자가 직접 시작·종료 | 워크플로가 자동 시작·종료 |
| 관련 절 | [3절](#3-amazon-ec2-배포) | [4절](#4-aws-cloudformation-배포) |

두 방식 모두 동일한 컴파일러와 동일한 캘리브레이션 데이터셋을 사용하므로 컴파일 결과는 같습니다.

---

## 2. 사전 준비 사항

- EC2 인스턴스를 시작하거나 CloudFormation 스택을 생성할 수 있는 AWS 계정과 권한
- 컴파일할 ONNX 모델과 컴파일 설정 JSON 파일. 직접 학습한 모델 외에도 [DEEPX Model Zoo](https://developer.deepx.ai/modelzoo/)에서 DEEPX NPU용으로 검증된 사전 학습 모델을 내려받아 바로 사용할 수 있습니다.
- 인스턴스를 실행할 기존 VPC와 서브넷. 서브넷은 Amazon S3, AWS Systems Manager, Amazon CloudWatch Logs 등 필요한 AWS 서비스에 HTTPS로 연결할 수 있어야 합니다. 프라이빗 서브넷을 사용한다면 NAT Gateway 또는 필요한 VPC 엔드포인트를 구성합니다.
- 로컬에서 AWS CLI 명령을 실행하려면 자격 증명이 설정되어 있어야 합니다.

### 로컬 AWS CLI 설정

이미 설정되어 있다면 이 절은 건너뜁니다.

```bash
aws configure
# AWS Access Key ID [None]: <access-key-id>
# AWS Secret Access Key [None]: <secret-access-key>
# Default region name [None]: <region, 예: us-east-1>
# Default output format [None]: json

# 자격 증명이 올바르게 설정되었는지 확인
aws sts get-caller-identity
```

계정 ID와 사용자 ARN이 출력되면 설정이 완료된 것입니다.

---

## Part II. Amazon EC2로 컴파일

## 3. Amazon EC2 배포

DEEPX Compiler Solution을 Amazon EC2 인스턴스로 시작하면 컴파일러와 캘리브레이션 데이터셋이 `/opt/dx-compiler` 아래에 미리 설치된 상태로 제공됩니다. 별도 설치 과정 없이 인스턴스가 뜨는 즉시 컴파일을 시작할 수 있습니다.

### 단계 1. 구독 및 인스턴스 시작

1. Marketplace 제품 페이지에서 **View purchase options**를 선택해 구독합니다. AWS 리소스 사용 비용이 별도로 발생하므로, 현재 소프트웨어 요금과 구독 조건은 AWS Marketplace 리스팅에서 확인하십시오.
2. **Launch DEEPX Compiler Solution** 화면의 **Service**에서 **Amazon EC2**를 선택합니다.
3. **Launch method**에서 다음 중 하나를 선택합니다.
    - **One-click launch from AWS Marketplace** — 최소한의 설정으로 빠르게 시작합니다. 아래 설명은 이 방식을 기준으로 합니다.
    - **Launch from EC2 Console** — 설정을 완전히 제어할 수 있는 방식입니다. 인스턴스 프로파일, 사용자 데이터, 추가 볼륨처럼 Marketplace 양식에 없는 시작 옵션이 필요할 때 사용합니다.
4. 설정 항목을 입력합니다. **Version**(최신 stable `dx-com` 릴리스가 기본 선택됨), **Region**, **Number of instances**, **Instance type**, **VPC**, **Subnet**, **Security group**, **Key pair**.
5. **Launch**를 선택합니다.

![DEEPX Compiler Solution 배포 설정 화면](img/compiler/fig02_launch_configuration.png)

*그림 2. 배포 설정 — Service를 Amazon EC2로 선택한 상태의 인스턴스 유형, 네트워크, 키 페어 설정*

> **참고 — 인스턴스 유형 선택**
>
> 컴파일은 CPU와 메모리를 많이 사용하는 작업입니다. 배포 화면은 `t3.xlarge`(4 vCPU, 16 GiB 메모리)를 **Vendor recommended**로 표시하며, CloudFormation 배포도 같은 유형을 기본값으로 사용합니다. 모델 크기와 캘리브레이션 이미지 수에 따라 더 큰 인스턴스가 유리할 수 있습니다.

보안 그룹은 필요한 통신만 허용하도록 구성합니다. 컴파일 작업 자체는 작업을 위한 SSH 접속 외에 별도의 인바운드 연결을 요구하지 않습니다.

같은 화면의 **AMI details** 패널에는 AMI alias와 리전별 AMI ID가 표시됩니다. alias는 `/aws/service/marketplace/<product-code>/dx-com-<version>` 형태의 AWS Systems Manager 파라미터 경로이며, CloudFormation 배포가 리전별 이미지를 자동 해석할 때 사용하는 것과 같은 방식입니다.

### 단계 2. 접속 및 모델 준비

`ubuntu` 사용자로 인스턴스에 SSH 접속해 컴파일러의 Python 환경을 활성화한 뒤, 컴파일할 ONNX 모델과 JSON 컴파일 설정 파일을 준비합니다. 설정 파일 형식은 [5절](#5-컴파일-설정-파일-json)에서 설명합니다.

```bash
ssh -i <your-key>.pem ubuntu@<instance-address>

# 컴파일러가 동작하는 Python 환경 활성화
source /opt/dx-compiler/venv/bin/activate

# Model Zoo 예제 모델 내려받기
curl -fLO https://sdk.deepx.ai/modelzoo/onnx/yolov5-s-face_640x640.onnx

# 또는 S3에 올려둔 자체 모델 가져오기
aws s3 cp s3://<your-bucket>/<path>/model.onnx .
```

모델과 같은 위치에 대응하는 컴파일 설정 파일을 내려받은 뒤, `dataset_path`가 AMI에 포함된 캘리브레이션 데이터셋을 가리키게 수정합니다.

```bash
curl -fLO https://sdk.deepx.ai/modelzoo/q-lite-json/2_4_0/yolov5-s-face_640x640.json

sed -i 's#"dataset_path": *"[^"]*"#"dataset_path": "/opt/dx-compiler/calibration_dataset/calibration_dataset"#' \
    yolov5-s-face_640x640.json
```

> **참고 — 설정 파일은 직접 작성하지 말고 Model Zoo 것을 사용**
>
> 설정 파일에는 모델의 입력 전처리가 정의되어 있어야 합니다. `inputs`, `calibration_num`,
> `calibration_method`만 넣어 직접 작성한 파일은 `preprocessings` 항목이 없어 컴파일에
> 실패합니다. Model Zoo는 공개하는 모든 모델에 대해 검증된 설정 파일을 함께 제공하므로,
> 이를 받아 필요한 부분만 바꾸는 편이 안전합니다. 각 항목은 [5절](#5-컴파일-설정-파일-json)에서
> 설명합니다.
>
> 경로가 한 단계 더 들어가 있다는 점에 유의하십시오. 캘리브레이션 이미지는 AMI가 안내하는
> 디렉토리보다 한 단계 아래인 `/opt/dx-compiler/calibration_dataset/calibration_dataset`에
> 있습니다.

### 단계 3. 컴파일 실행

`dxcom`은 모델(`-m`), 설정 파일(`-c`), **출력 디렉토리**(`-o`)를 인자로 받습니다. 컴파일러와 이 명령이 사용하는 캘리브레이션 데이터셋은 `/opt/dx-compiler` 아래에 사전 설치되어 있습니다. 단계 2의 가상 환경이 활성화된 상태에서만 명령이 `PATH`에 잡히며, 셸 프롬프트의 `(venv)` 접두사로 확인할 수 있습니다.

```bash
dxcom -m yolov5-s-face_640x640.onnx \
      -c yolov5-s-face_640x640.json \
      -o output/yolov5-s-face_640x640
```

컴파일러는 먼저 컴파일 설정(컴파일러 버전, 모델, 설정 파일, 출력 디렉토리, 최적화 레벨)을 출력하고, 양자화와 전처리 처리 내역을 보고한 뒤 컴파일 진행률을 표시합니다.

![인스턴스에서 dxcom 실행](img/compiler/fig03_dxcom_run.png)

*그림 3. EC2 인스턴스에서 `dxcom`으로 ONNX 모델을 컴파일한 결과*

> **참고 — `dx-compile` 단축 명령**
>
> Marketplace 페이지의 벤더 시작·접속 안내는 모델만 인자로 받는 `dx-compile <model.onnx>`
> 형태를 제시합니다. 다만 이 명령이 설정 파일과 출력 디렉토리를 어떻게 결정하는지는 리스팅에
> 문서화되어 있지 않으므로, 이 가이드는 인자를 명시하는 `dxcom`을 기준으로 설명합니다. 짧은
> 형태를 사용하기 전에 인스턴스에서 `dxcom -h`와 `dx-compile --help`를 비교해 보십시오.

컴파일이 완료되면 `-o`로 지정한 디렉토리 **안에** 모델 이름을 딴 `.dxnn` 파일이 생성됩니다.

```bash
ls -lhR output/
```

![컴파일된 .dxnn 아티팩트](img/compiler/fig04_dxnn_output.png)

*그림 4. 출력 디렉토리에 생성된 `.dxnn` 아티팩트*

결과물을 S3에 업로드해 엣지 디바이스나 다른 작업 환경에서 내려받아 사용할 수 있게 합니다.

```bash
aws s3 cp output/yolov5-s-face_640x640/yolov5-s-face_640x640.dxnn s3://<your-bucket>/<path>/
```

### 단계 4. 인스턴스 종료

컴파일은 일회성 작업이므로, 작업이 끝나면 인스턴스를 종료해 비용 발생을 멈춥니다. 반복 작업이 예상된다면 다음 절의 CloudFormation 배포가 관리와 비용 양쪽에서 유리합니다.

---

## Part III. CloudFormation으로 컴파일 자동화

## 4. AWS CloudFormation 배포

배포 화면에서 **AWS CloudFormation**을 선택하면 한 번의 배포로 완결되는 자동화 구성, 즉 사람이 직접 운영하지 않아도 되는 이벤트 기반 컴파일 파이프라인이 만들어집니다. Amazon S3에 모델과 설정 파일을 업로드하면 이벤트가 워크플로를 시작하고, 워크플로가 컴파일러 인스턴스를 시작해 컴파일한 뒤 인스턴스를 종료합니다. 사용자는 결과물만 내려받으면 됩니다.

DEEPX Greengrass Solution은 엣지 런타임 배포와 함께 이 파이프라인을 같은 스택으로 배포합니다. 해당 스택의 파라미터와 전체 실습 흐름은 [DEEPX Greengrass Solution](01_DEEPX_Greengrass_Solution_kor.md) 문서를 참고하십시오.

### 동작 순서

1. 사용자가 `.onnx` 모델과 `.json` 설정 파일을 S3 모델 버킷의 **같은 경로**에 업로드합니다.
2. S3 `ObjectCreated` 이벤트가 AWS Lambda 트리거 함수를 호출합니다. 함수는 같은 경로에서 짝이 되는 파일을 찾아 **두 파일이 모두 존재할 때만** 다음 단계로 진행합니다. 실행 이름은 파일명 기반 해시로 생성해 중복 실행을 방지합니다.
3. AWS Step Functions 컴파일 워크플로가 시작됩니다.
4. 워크플로가 DEEPX Compiler Solution AMI 기반 Amazon EC2 인스턴스를 시작합니다. 인스턴스는 CloudFormation 파라미터로 지정한 기존 VPC/서브넷에서 실행됩니다.
5. AWS Systems Manager Run Command가 SSM Document에 정의된 컴파일 명령을 인스턴스에 전달합니다.
6. 인스턴스에 사전 설치된 `dxcom` 컴파일러가 실행됩니다. 이때 설정 파일의 `dataset_path`는 AMI에 포함된 캘리브레이션 데이터셋 경로인 `/opt/dx-compiler/calibration_dataset`으로 자동 치환됩니다.
7. 컴파일된 `.dxnn` 바이너리가 원본 모델과 같은 S3 경로에 업로드됩니다. 워크플로는 성공·실패와 무관하게 인스턴스를 종료하므로 유휴 비용이 발생하지 않으며, 실행 로그는 Amazon CloudWatch Logs 로그 그룹(`/dx-compiler/<스택명>/execution`)에서 확인할 수 있습니다.

### 사용 예

```bash
export STACK_NAME=<cloudformation-stack-name>

export MODEL_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "$STACK_NAME" \
  --query "Stacks[0].Outputs[?OutputKey=='ModelBucketName'].OutputValue" \
  --output text)

export MODEL_PREFIX=models/yolov5-s-face_640x640

aws s3 cp --only-show-errors yolov5-s-face_640x640.onnx "s3://${MODEL_BUCKET}/${MODEL_PREFIX}/"
aws s3 cp --only-show-errors yolov5-s-face_640x640.json  "s3://${MODEL_BUCKET}/${MODEL_PREFIX}/"

# 컴파일 완료 후 결과 확인
aws s3 ls "s3://${MODEL_BUCKET}/${MODEL_PREFIX}/"
```

> **참고 — 모델별 전용 prefix 사용**
>
> 트리거 함수는 같은 경로에 있는 `.onnx`와 `.json`을 한 쌍으로 인식합니다. 여러 모델을 다룰 때는 모델마다 별도 prefix를 사용해 다른 모델의 설정 파일이 섞이지 않도록 합니다.

---

## Part IV. 모델 설정 및 검증

## 5. 컴파일 설정 파일 (JSON)

컴파일 설정 파일은 입력 텐서의 형상과 INT8 양자화를 위한 캘리브레이션 방식을 정의합니다. 아래는 640×640 입력을 받는 검출 모델의 예시입니다.

```json
{
    "inputs": {
        "input.1": [1, 3, 640, 640]
    },
    "calibration_num": 100,
    "calibration_method": "ema",
    "default_loader": {
        "dataset_path": "/mnt/datasets/widerface/WIDER_val/images",
        "file_extensions": ["jpeg", "jpg", "png", "JPEG"],
        "preprocessings": [
            {
                "resize": {
                    "mode": "pad",
                    "size": 640,
                    "pad_location": "edge",
                    "pad_value": [114, 114, 114]
                }
            },
            {
                "convertColor": {
                    "form": "BGR2RGB"
                }
            },
            {
                "transpose": {
                    "axis": [2, 0, 1]
                }
            },
            {
                "div": {
                    "x": 255.0
                }
            },
            {
                "expandDim": {
                    "axis": 0
                }
            }
        ]
    }
}
```

| 항목 | 설명 |
| :--- | :--- |
| `inputs` | 입력 텐서 이름과 형상. ONNX 모델의 입력 정의와 일치해야 합니다. |
| `calibration_num` | 캘리브레이션에 사용할 이미지 수 |
| `calibration_method` | 캘리브레이션 알고리즘 (예: `ema`) |
| `default_loader.dataset_path` | 캘리브레이션 데이터셋 경로 |
| `default_loader.preprocessings` | 학습 시 사용한 전처리와 동일하게 구성해야 정확도 손실을 최소화할 수 있습니다. |

> **참고 — 위 예시의 `dataset_path`는 설명용입니다**
>
> 위 예시는 항목의 형태를 보이기 위해 로컬 데이터셋 디렉토리를 가리키고 있을 뿐, 컴파일러
> 인스턴스에 존재하는 경로가 아닙니다. 이 파일을 그대로 복사해 Amazon EC2 인스턴스에서
> `dxcom`을 실행하면 캘리브레이션 이미지를 찾지 못합니다. [3절](#3-amazon-ec2-배포)처럼
> `dataset_path`를 `/opt/dx-compiler/calibration_dataset/calibration_dataset`으로 지정하십시오.

> **참고 — `dataset_path` 자동 치환**
>
> CloudFormation 배포의 파이프라인을 사용하는 경우, 설정 파일의 `dataset_path`에 어떤 값을 넣더라도 컴파일 시점에 AMI에 포함된 캘리브레이션 데이터셋 경로(`/opt/dx-compiler/calibration_dataset`)로 자동 치환됩니다. Amazon EC2 배포에서 직접 `dxcom`을 실행할 때는 이 치환이 적용되지 않으므로, 인스턴스에서 실제로 접근 가능한 경로를 지정해야 합니다.

---

## 6. DEEPX Model Zoo 연계

직접 학습한 모델이 없더라도 [DEEPX Model Zoo](https://developer.deepx.ai/modelzoo/)에서 DEEPX NPU용으로 검증된 사전 학습 ONNX 모델과 그에 대응하는 설정 파일을 내려받아 즉시 컴파일할 수 있습니다. 객체 검출, 얼굴 검출, 분류, 세그멘테이션, 포즈 추정 등 주요 비전 태스크의 모델이 제공되며, INT8 양자화 후 정확도 수치도 함께 공개되어 있습니다.

---

## Part V. 운영 및 마무리

## 7. 비용

AWS 리소스 사용 비용이 별도로 발생합니다. 현재 소프트웨어 요금과 구독 조건은 AWS Marketplace 리스팅에서 확인하고, 다음 AWS 리소스 사용량에 따른 비용도 고려하십시오.

- **Amazon EC2**: 컴파일러 인스턴스 실행 시간에 대해 비용이 발생합니다. CloudFormation 배포의 파이프라인은 컴파일 작업 중에만 인스턴스를 실행하고 성공·실패 양쪽 경로에서 종료하므로 유휴 비용이 없습니다. Amazon EC2 배포에서는 사용자가 인스턴스를 직접 종료해야 합니다.
- **Amazon EBS**: 인스턴스에 연결된 볼륨에 대해 비용이 발생합니다.
- **Amazon S3, AWS Lambda, AWS Step Functions, Amazon CloudWatch Logs** (CloudFormation 배포): 모델 파일 저장, 이벤트 처리, 워크플로 실행, 로그 보관에 따른 비용이 발생합니다.

실제 비용은 모델 크기, 컴파일 시간, 인스턴스 유형, 리전, 로그 보관 기간에 따라 달라집니다. 배포 전에는 [AWS Pricing Calculator](https://calculator.aws/)와 각 서비스의 최신 요금을 기준으로 예상 비용을 확인합니다.

---

## 8. 문제 해결

| 증상 | 확인 사항 |
| :--- | :--- |
| 파일을 업로드했는데 워크플로가 시작되지 않음 (CloudFormation 배포) | `.onnx`와 `.json` 두 파일이 **같은 S3 경로**에 모두 업로드되었는지 확인합니다. 한쪽만 있으면 트리거 함수가 대기합니다. |
| 워크플로가 실패로 종료됨 | Amazon CloudWatch Logs의 `/dx-compiler/<스택명>/execution` 로그 그룹에서 `dxcom` 실행 로그를 확인합니다. |
| 인스턴스가 시작되지 않음 | 서브넷이 필요한 AWS 서비스에 HTTPS로 나갈 수 있는지(NAT Gateway 또는 VPC 엔드포인트), 그리고 Marketplace 구독이 완료되었는지 확인합니다. |
| `dxcom: command not found` | 컴파일러 가상 환경을 먼저 활성화합니다. `source /opt/dx-compiler/venv/bin/activate` |
| `dxcom` 시작 시 `GPU device discovery failed` 경고 | 무시해도 됩니다. 컴파일러 인스턴스에는 GPU가 없어 ONNX Runtime의 디바이스 탐색이 실패하고 CPU로 대체될 뿐이며, 컴파일은 정상 진행됩니다. |
| 직접 작성한 설정 파일로 컴파일이 실패함 | `preprocessings` 항목이 빠졌을 가능성이 높습니다. 최소 설정을 직접 작성하지 말고 해당 모델의 Model Zoo 설정 파일을 사용합니다. |
| 캘리브레이션 이미지를 찾지 못함 | `dataset_path`가 상위 디렉토리가 아니라 `/opt/dx-compiler/calibration_dataset/calibration_dataset`을 가리키는지 확인합니다. |
| 입력 형상 관련 컴파일 오류 | 설정 파일의 `inputs` 텐서 이름과 형상이 ONNX 모델의 입력 정의와 일치하는지 확인합니다. |
| 양자화 후 정확도가 기대보다 낮음 | `preprocessings`가 학습 시 전처리와 동일한지, `calibration_num`이 충분한지 확인합니다. |

## 9. 리소스 정리

1. **Amazon EC2 배포**: 사용을 마친 EC2 인스턴스를 종료합니다. 인스턴스와 함께 삭제되지 않는 EBS 볼륨이 있다면 별도로 삭제합니다.
2. **CloudFormation 배포**: CloudFormation 콘솔에서 스택을 삭제합니다. 모델 버킷은 데이터 보호를 위해 유지되므로, 더 이상 필요하지 않다면 버킷을 비우고 직접 삭제합니다.
3. AWS Marketplace 구독이 더 이상 필요 없다면 [Manage subscriptions](https://aws.amazon.com/marketplace/library)에서 구독을 취소합니다.

## 다음 단계

컴파일한 `.dxnn` 모델을 엣지 디바이스에서 실행하려면 디바이스에 NPU 드라이버, 펌웨어, dx_rt 런타임이 설치되어 있어야 합니다. 이 과정을 AWS IoT Greengrass로 자동화하는 방법은 [DEEPX Greengrass Solution](01_DEEPX_Greengrass_Solution_kor.md) 문서를 참고하십시오.

## 참고 자료

- [DEEPX Compiler Solution — AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-ev6ed5omu4ulo)
- [DEEPX Greengrass Solution — AWS Marketplace](https://aws.amazon.com/marketplace/pp/prodview-732s46qfzuh34)
- [DEEPX Model Zoo](https://developer.deepx.ai/modelzoo/)
- [DEEPX 기술 문서](https://developer.deepx.ai/tech-docs)
- [Amazon EC2 사용 설명서](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [AWS Systems Manager Session Manager](https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager.html)
- [AWS Step Functions 개발자 안내서](https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html)
- [DEEPX dx-all-suite — GitHub](https://github.com/DEEPX-AI/dx-all-suite)
