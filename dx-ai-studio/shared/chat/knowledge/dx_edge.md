# DX Cloud (dx_edge) — AWS 클라우드 컴파일 · 엣지 배포

## [section:overview,소개,개요,cloud,aws,marketplace] DX Cloud 개요

DX Cloud (모듈 이름 dx_edge, Studio 안 경로 `/cloud/`)는 DEEPX on AWS 화면입니다.

- **AWS Marketplace 제품 2개**
  - **DEEPX Compiler Solution**: EC2 에서 `dxcom` 을 실행합니다. CloudFormation 스택으로 배포하면, 모델 bucket 에 `.onnx` 와 그 `.json` 을 올리는 것만으로 같은 위치에 `.dxnn` 이 만들어집니다 (Lambda trigger → Step Functions → compiler EC2).
  - **DEEPX Greengrass Solution**: NPU driver · firmware · `dx_rt` · `dx_stream` 을 IoT Thing Group 의 모든 디바이스에 배포합니다 (Zero-Touch Provisioning). 같은 스택에 컴파일 파이프라인도 있습니다.
- 화면 위쪽 상태 chip: Profile · Region · Account · Subscription · Ready stacks
- 제품마다 탭이 하나씩 있습니다: **DEEPX Compiler Solution** / **DEEPX Greengrass Solution**
- **AWS Console guide** (`/cloud/guide`): AWS 콘솔에서 같은 일을 하는 단계별 안내
- 6개 언어 UI · 인앱 튜토리얼 · AI Help (이 챗봇)

## [section:aws,credential,자격,profile,프로필,region,리전,login,로그인,sso,setup,설정] AWS 연결

1. DX Cloud 는 Studio 가 실행 중인 Linux PC 의 **AWS CLI 설정(`~/.aws`)** 을 씁니다. access key 를 묻거나 저장하거나 기록하지 않습니다.
2. ① 단계의 **AWS CLI setup guide** 에 설치 script(x86_64 · aarch64 공용)와 로그인 명령이 있습니다.
   - Option A: access key — `aws configure`
   - Option B: IAM Identity Center (SSO) — named profile 을 한 번 만들고 `aws sso login`
3. **AWS profile** 과 **Region** 을 고르고 **Check connection** 을 누릅니다. 새 named profile 은 다시 시작하지 않아도 목록에 나타납니다.
4. `boto3` 가 없으면 화면은 열리지만 설치 안내가 보입니다 (`pip install -e '.[aws]'`).

## [section:stack,스택,deploy,배포,subscription,구독,template] 구독 · 스택 배포

1. **Marketplace subscription**: 계정 관리자가 AWS 계정마다 한 번 구독합니다 (**Open Marketplace listing**).
2. **Compiler stacks** / **Greengrass stacks**: 구독한 template 으로 **New stack name** 을 적고 **Deploy stack**. 진행 상태가 목록에 보이고, **Refresh** 로 다시 읽습니다.
3. 스택 삭제는 **Delete** → 스택 이름을 입력해 확인합니다. S3 모델 bucket 은 지워지지 않습니다 (DeletionPolicy: Retain).

## [section:compile,컴파일,onnx,dxnn,cloud compile,업로드] Cloud Compile

1. **Compiler stack** (또는 Greengrass stack) 에서 준비된 스택을 고릅니다 (**Find stacks**).
2. **ONNX model** 에 `.onnx`, **Compile config (.json)** 에 그 `.json` 을 놓고 **Upload and compile**.
3. 상태는 pending → running → succeeded / failed. **Compile log** 에 진행이 보이고, **Compile jobs** 표에 지난 작업이 남습니다.
4. 성공하면 **Download .dxnn** 또는 **Save to Studio models** (DX App 모델 폴더, `DX_APP_MODELS_DIR`).
- 로컬 `dxcom` 이 없어도 됩니다. 로컬 컴파일은 DX Compiler 모듈에서 합니다.

## [section:greengrass,device,디바이스,thing,register,등록] Greengrass 디바이스

1. **DEEPX Greengrass Solution** 탭에서 Greengrass 스택을 배포합니다.
2. **Register device**: **Thing name** 을 적고 **Generate script** → **Download .sh**. 디바이스는 이 script 를 자기 AWS 자격 증명으로 실행하며 Java 11 이상이 필요합니다. script 안에는 자격 증명이 없습니다.
3. **Devices (dx-runtime)** 표에 core device 마다 Thing Group · Deployment · Components · Last update 가 보입니다.
