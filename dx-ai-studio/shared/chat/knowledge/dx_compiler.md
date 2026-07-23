# DX Compiler — ONNX 컴파일 GUI (DX-COM v2.3.0)

## [section:overview,소개] DX Compiler 개요

DX Compiler (포트 8095)는 **ONNX 모델을 NPU용 `.dxnn`으로 변환**하는 웹 GUI이며,
내부적으로 **DX-COM (DEEPX Compiler)**을 호출합니다.

- **DX-COM**: ONNX → .dxnn 핵심 컴파일러. INT8 Intelligent Quantization, NPU/CPU 자동 파티셔닝
- **DX-TRON**: GUI 시각화 도구. .dxnn 모델 구조를 컬러 코딩 그래프로 시각화
- **Split-screen 인터페이스**: 왼쪽 그래프 시각화 + 오른쪽 컴파일 폼
- **6단계 컴파일 파이프라인**: PREPARE → SURGERY → PARTITION → QUANTIZATION → OPTIMIZE → CODEGEN
- **실시간 SSE 스트리밍**: 진행률, 로그, 그래프 변화 실시간 표시
- **그래프 뷰어**: SVG 렌더링 (dagre 레이아웃) + 줌/팬 + 노드 검색
- **Compile Range Selection**: 그래프 일부만 선택 컴파일 (고급)
- **지원 플랫폼**: x86_64 (Ubuntu 20.04/22.04/24.04) — **컴파일은 Host PC에서만 가능**

### 설치 방법 (DX-COM)
```bash
# Local 설치
./install.sh                     # DX-Compiler 전체 설치

# Docker 설치
./docker_build.sh               # Docker 이미지 빌드
./docker_run.sh                 # 컨테이너 실행

# 실행 (DX-TRON Web UI)
./run_dxtron_web.sh             # 웹 기반 GUI 실행
./run_dxtron_appimage.sh        # AppImage 기반 실행
```

## [section:compile,build,convert,onnx,dxnn,컴파일] 컴파일 워크플로우

### 기본 사용법
1. **ONNX 업로드**: 웹 UI에서 `.onnx` 파일 업로드 (드래그 & 드롭)
2. **모델 검사**: 자동으로 입력/출력 Shape, Dynamic 축 감지
3. **옵션 설정**: 최적화 레벨, 양자화, 파티셔닝 옵션
4. **Config 생성**: Config Wizard로 전처리 파이프라인 설정
5. **컴파일 시작**: Submit → 6단계 자동 진행
6. **결과 확인**: DX-TRON 그래프 시각화 + `.dxnn` 다운로드

### End-to-End 워크플로우 (E2E)
```
[PyTorch/TensorFlow] → ONNX export → [DX-COM 컴파일] → .dxnn → [DX-RT로 NPU 추론]
```
- 컴파일은 **Host PC (x86_64)**에서 수행
- 생성된 `.dxnn` 파일을 타겟 디바이스 (x86_64/aarch64)로 복사하여 사용

### 6단계 파이프라인

| 단계 | 설명 | 시각화 | 상세 |
|------|------|--------|------|
| **PREPARE** | 모델 로드 + 그래프 준비 | ✅ 원본 그래프 | ONNX 로드, Shape 추론 |
| **SURGERY** | 그래프 변환 (fusion, folding) | ✅ 변환된 그래프 | Conv+BN fusion, 상수 폴딩 |
| **PARTITION** | NPU/CPU 자동 파티셔닝 | ✅ 파티션 그래프 (색상 구분) | NPU 미지원 Op → CPU fallback |
| **QUANTIZATION** | INT8 양자화 | 진행률만 | Intelligent Quantization |
| **OPTIMIZE** | NPU 최적화 | 진행률만 | 메모리/연산 최적화 |
| **CODEGEN** | `.dxnn` 바이너리 생성 | ✅ 최종 그래프 | NPU 실행 코드 생성 |

진행률: `(완료_단계 / 6) × 100%`

## [section:compile,option,옵션] 컴파일 옵션

### 기본 옵션
| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `opt_level` | 최적화 레벨 (0=없음 ~ 3=최대) | 2 |
| `aggressive_partitioning` | 적극적 NPU 파티셔닝 | False |
| `gen_log` | 상세 로그 출력 | False |
| `node_selection` | 컴파일 범위 선택 기능 | False |

### DXQ 양자화 (INT8 Intelligent Quantization)
DeepX 독자 양자화 기술로 정확도 손실 최소화 + 추론 속도 극대화:

| 설정 | 설명 |
|------|------|
| P0 ~ P5 | 양자화 프리셋 (P0=기본, P5=최고 정밀) |
| weight_dtype | `int8`, `uint8`, `float16` |
| activation_dtype | `uint8`, `int8` |
| calibration_method | `entropy`, `percentile`, `kl` |
| calibration_dataset | 캘리브레이션용 데이터 경로 (정확도에 중요) |

### Config Wizard (전처리 설정)
- **리사이즈**: 보간 모드 설정 (bilinear, nearest 등)
- **노멀라이제이션**: 채널별/텐서별 (mean, std 값)
- **패딩**: 입력 크기 조정
- **캘리브레이션**: 데이터 경로 + 샘플 수 지정 (기본 100장)

### CLI 컴파일 (dxcom 직접 사용)
```bash
dxcom compile --model model.onnx --config config.json --output model.dxnn
dxcom compile --model model.onnx --opt-level 3 --quant P0
```

## [section:compile,graph,그래프] 그래프 뷰어 (DX-TRON)

### 시각화 기능
- **SVG 렌더링**: dagre 레이아웃 엔진으로 자동 배치
- **줌/팬**: 마우스 휠 + 드래그
- **Fit-to-View**: 전체 그래프 화면에 맞추기
- **노드 클릭**: 상세 정보 (Op Type, Shape, 속성)
- **엣지 하이라이트**: 텐서 데이터 흐름 추적
- **서브그래프 토글**: NPU/CPU 그룹 접기/펼치기

### 노드 카테고리 (8종)
| 카테고리 | 예시 Op |
|----------|---------|
| compute | Conv, MatMul, Gemm |
| memory | Reshape, Transpose, Concat |
| activation | Relu, Sigmoid, Softmax |
| normalization | BatchNormalization, LayerNorm |
| pooling | MaxPool, AveragePool, GlobalPool |
| elementwise | Add, Mul, Sub |
| quantize | QuantizeLinear, DequantizeLinear |
| other | Custom Op 등 |

### 파티션 컬러 코딩
- **NPU 노드**: 파란색/초록색 (서브그래프 ID 표시)
- **CPU 노드**: 회색/주황색 (`cpu_reasons` 태그)
- **CPU Fallback 사유**: `unsupported_op`, `memory_limit`, `dynamic_shape` 등

## [section:compile,node_selection,노드선택] 컴파일 범위 선택 (고급)

### 사용 시나리오
- 매우 큰 모델의 **일부만 NPU** 컴파일하고 싶을 때
- 특정 레이어 구간만 테스트하고 싶을 때

### 워크플로우
1. `node_selection=true` 활성화 후 컴파일 시작
2. PREPARE 완료 후 → **자동 일시정지**
3. 그래프에서 **입력/출력 경계 노드 선택**
4. "Calculate Exclude" → 제외 노드 미리보기 (BFS)
5. "Resume" → 선택 범위만 컴파일 계속

### BFS 제외 알고리즘
- 입력+출력 노드 선택: `포함 = 입력의 하류 ∩ 출력의 상류`
- 출력 노드만 선택: 하류 전체 제외
- 입력 노드만 선택: 상류 전체 제외

## [section:error,fail,bug,에러] 에러 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| "dx_com not installed" | dxcom 미설치 | `which dxcom`으로 확인, `./install.sh`로 설치 |
| 컴파일 중 Op 에러 | 미지원 ONNX 연산자 | CPU Fallback 확인, Op 대체 고려 |
| ONNX 로드 실패 | 파일 손상 또는 형식 오류 | `python -c "import onnx; onnx.load('model.onnx')"` 테스트 |
| Config JSON 파싱 에러 | 잘못된 JSON 형식 | Config Wizard로 재생성 |
| 파티셔닝 후 CPU 노드 많음 | 미지원 Op 다수 | `aggressive_partitioning=true` 시도, Op 분해 고려 |
| 컴파일 시간 초과 | 모델 너무 큼 | 노드 선택으로 범위 축소, opt_level 낮추기 |
| `.dxnn` 파일 안 생김 | 코드 생성 실패 | SSE 로그에서 에러 메시지 확인 |
| 양자화 정확도 낮음 | 캘리브레이션 데이터 부적절 | 실제 데이터와 유사한 캘리브레이션 데이터 사용, P-preset 높이기 |
| Dynamic Shape 처리 불가 | 가변 축 존재 | 고정 Shape로 export 또는 Config에서 고정값 지정 |

## [section:install,setup,설치] 전제 조건 및 설치

### DX-Compiler 설치 옵션
| 방법 | 설명 | 장점 |
|------|------|------|
| **Local** | `./install.sh` | 직접 접근, 빠른 실행 |
| **Docker** | `docker_build.sh` + `docker_run.sh` | 환경 격리, 재현성 |
| **DX-AllSuite** | 통합 설치 | 전체 SDK와 호환 보장 |

### 호환 환경
- **OS**: Ubuntu 20.04/22.04/24.04 (Debian 기반)
- **Architecture**: x86_64 only (ARM에서는 컴파일 불가, 추론만 가능)
- **Python**: 3.8~3.12 (dxcom은 내부적으로 Python 의존)

### Feature Check
- `/feature-check` API로 설치 여부 확인: `{compile: true/false}`
- 컴파일러 미설치 시 UI에서 안내 메시지 표시
- 업로드 경로: `compiler_uploads/` (보안 경로 검증 포함)

### 문서 생성
```bash
pip install mkdocs mkdocs-material mkdocs-video pymdown-extensions mkdocs-to-pdf
mkdocs build  # HTML (docs/) + PDF 생성
```
