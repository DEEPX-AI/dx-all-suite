# DX Planner (EdgeGuide) — NPU 제품 추천 가이드

## [section:overview,소개,개요,edgeguide] DX EdgeGuide 개요

DX Planner (내부명 **DX EdgeGuide**, 포트 8096)는 컴퓨터 비전 워크로드에 맞는 **최적의 DEEPX Edge AI 제품(NPU 보드 + 호스트)을 추천**하는 도구입니다.

- 워크로드를 입력하면 실제 **YOLO26 벤치마크 측정치**를 근거로 플랫폼 순위를 매김
- 플랫폼 상세 비교, 근거(Evidence) 확인, 제품 정보/견적 요청까지 한 페이지에서 진행
- **Scenario → Pick → Evidence → Buy** 4단계 흐름의 단일 페이지 구성
- **AI Help** 챗봇으로 요구사항/결과 기반 후속 질문 대응
- **6개 언어 지원** + 인앱 튜토리얼

## [section:usage,사용법,시나리오,요구사항] 사용 방법

### 1단계 — 워크로드 설명 (Requirements 패널)
- **Quick scenario** 칩(CCTV / Retail / Pose)으로 빠르게 프리필 가능
- **AI Task**: Object Detection / Pose Estimation / Segmentation / Oriented BBox / Classification
- **Model Size**: n(최속) ~ x(최고 정확도)
- **운영 요구사항**: 카메라/채널 수, 목표 FPS, 런타임(ONNX Runtime vs Native), FPS 여유율(headroom), 최대 지연시간

### 2단계 — 우선순위 선택 후 추천
- **Next: priority** 클릭 → 랭킹 우선순위 선택: **Lowest Cost / Best Performance / Lowest Power**
- **Get Recommendations** 클릭 (이후 입력 변경 시 결과 자동 갱신)

### 3단계 — 추천 결과 확인
- 상단 요약: **Top pick** + 채널/FPS 목표 충족 여부
- 각 카드: 신뢰도 배지(Measured → Interpolated → Theoretical), `Host-limited` 등 플래그 표시
- 카드 또는 처리량 차트 막대 클릭 → 상세 패널 오픈

### 4단계 — 탐색/비교
- **Details 패널**: 핵심 정보, 플랫폼 스펙, Performance Radar, 정렬 가능한 벤치마크 테이블, 모델 크기별 차트
- **Compare with**로 두 번째 플랫폼과 나란히 비교

### 5단계 — 구매/문의 (Buy 패널)
- 시스템 가격 및 채널당 대략적 비용 표시
- **Product info**, **Request quote** 버튼으로 DEEPX 문의 연결

## [section:ranking,신뢰도,우선순위] 추천 로직 & 신뢰도

- **실측 기반**: 스펙시트 계산이 아닌 YOLO26 벤치마크 매트릭스 실측값으로 추천
- **신뢰도 등급**: Measured(실측) → Interpolated(보간) → Theoretical(이론치) 순으로 표기
- **How ranking works** 버튼: 정확한 계산식과 실시간 요약, 한계점(전체 스펙시트 아님, 표시 비용은 NPU 보드 채널당 가격이며 호스트/전력/설치비 등은 **TCO에 포함되지 않음**) 명시
- **Multi-stream 근거**: 채널당/총 FPS 수치를 채널 추정치 뒤에 노출
- **공유 가능**: 현재 선택 상태가 URL에 담겨, DX Benchmark에서 넘어온 링크 등으로 입력값 그대로 재현/재추천 가능

## [section:npu,hardware,디바이스,dx-m1,dx-h1] 지원 NPU 제품 카탈로그

| 제품 | TOPS | 폼팩터 |
|------|------|--------|
| DX-M1 | 25 TOPS | M.2 |
| DX-M1M | 25 TOPS | M.2 |
| DX-M1ML | 13 TOPS | M.2 |
| DX-H1 V-NPU | 50 TOPS | PCIe Card |
| DX-H1 Quattro | 100 TOPS | PCIe Card |

> 정확한 TDP/가격 등 세부 스펙은 제품별로 다르며, EdgeGuide 내 플랫폼 상세(Details) 패널에서 확인.

## [section:link,연동,dx_benchmark] 다른 모듈과의 연동

- 추천에 사용되는 벤치마크 데이터는 **DX Benchmark**의 결과를 집계(`aggregate_benchmarks`)한 것
- DX Benchmark 대시보드에서 EdgeGuide로 바로 이동하는 버튼 제공 (💰 아이콘)

## [section:error,troubleshoot,문제,에러] 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| 추천 결과 없음 | 벤치마크 데이터 부재/집계 실패 | DX Benchmark에 결과가 있는지 확인, 서버 재시작 시 재집계됨 |
| "Host-limited" 플래그 | 호스트 PC 성능이 병목 | 호스트 사양 상향 또는 채널 수 조정 고려 |
| 신뢰도가 Theoretical만 표시 | 해당 조합의 실측 벤치마크 데이터 없음 | 유사 크기/태스크 조합 참고, 실측 데이터 추가 대기 |
| 비용이 TCO와 다름 | 표시 비용은 NPU 보드 채널당 가격 | 호스트/전력/설치 비용은 별도 고려 필요 |
