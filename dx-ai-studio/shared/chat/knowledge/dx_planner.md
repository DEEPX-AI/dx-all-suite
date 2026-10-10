# DX Planner (EdgeGuide) — NPU 제품 추천 가이드

## [section:overview,소개,개요,edgeguide] DX EdgeGuide 개요

DX EdgeGuide (모듈 이름 dx_planner, Studio 안 경로 `/planner/`)는 컴퓨터 비전 워크로드에 맞는 **DEEPX NPU 보드 + 호스트 조합을 추천**합니다.

- 근거는 스펙시트 계산이 아니라 **DX Benchmark 의 YOLO26 실측** (단일 스트림 + 멀티 스트림)
- **Scenario → Pick → Evidence → Buy** 4단계 흐름의 한 페이지
- AI Help (이 챗봇) · 6개 언어 · 인앱 튜토리얼

## [section:usage,사용법,시나리오,요구사항] 사용 방법

1. **조건 입력** — Quick scenario 칩(4-ch CCTV OD / 8-ch retail cls / 2-ch pose 30FPS)으로 채우거나 직접 고른다.
   - AI Task: Object Detection / Pose Estimation / Segmentation / OBB / Classification
   - Model size: n(가장 빠름) ~ x(가장 정확)
   - 카메라(채널) 수, 목표 FPS (15 / 25 / 30 / 60), Runtime (ONNX Runtime / Native), 최대 latency (선택)
2. **Next — choose ranking** → 우선순위: **Most channels / Best Performance / Lowest Power** → **Get Recommendations**. 이후 입력을 바꾸면 결과가 자동 갱신된다. **Start over** 는 처음으로.
3. **결과 확인** — 맨 위 한 줄이 Top pick 과 충족 여부. 카드마다 Measured / Estimated badge 와 근거 한 줄.
4. **Details** — 카드나 막대를 누르면 핵심 수치 · 스펙 · Performance Radar · 벤치마크 표 · 모델 크기별 차트. **Compare with** 로 다른 플랫폼과 나란히 비교.
5. **Buy** — 가격은 견적제. **Product info** · **Request quote** 버튼이 DEEPX 로 연결된다. 화면에 가격 · 채널당 비용은 표시하지 않는다.

## [section:ranking,신뢰도,우선순위,계산,채널,estimated,measured,추정,실측] 추천 로직 — 채널 수는 어떻게 나오나

멀티 스트림 벤치마크는 채널당 30 FPS 부근의 스트림 수만 측정했다. 포화 부근에서는 스트림을 더해도 총 FPS 가 거의 일정하다 (throughput 한계).

- `T_sat` = 측정한 행들 중 **가장 낮은 총 FPS** (가장 보수적인 값)
- `M` = 채널당 FPS 가 목표 이상이었던 **가장 큰 측정 스트림 수**
- `E` = `floor(T_sat / 목표 FPS)`
- 판정:
  - M 바로 위 스트림 수가 목표를 못 채운 측정이 있으면 → **M (Measured, 실측)**
  - 측정한 모든 스트림 수가 목표를 채웠으면 (목표가 측정보다 낮음, 예: 15 FPS) → `max(M, E)`, 단 측정 최대 스트림 수의 2배까지만 (**Estimated**, 상한에 걸리면 **Estimated+**)
  - 어떤 측정도 목표를 못 채웠으면 (예: 60 FPS) → **E (Estimated)**. 1채널도 못 채우면 0
- **throttle**: 측정 중 NPU 가 throttle 됐어도 버리지 않는다 — 그 FPS 가 이미 throttle 된 클럭의 값이다. 카드에 "측정 중 NPU throttle 발생" 표시, 같은 조건이면 throttle 없는 플랫폼보다 뒤.
- **한계(bottleneck)**: 가장 부하가 큰 측정에서 NPU 사용률이 85% 이상이면 "한계: NPU", 아니면 "한계: 호스트 (CPU / 디코딩)" — 호스트를 바꾸면 늘어날 여지가 있다는 뜻.
- **latency**: 단일 스트림 벤치마크 latency. 최대 latency 를 정했는데 측정값이 없으면 "충족 (추정)" 이지 그냥 충족이 아니다.

판정 단계: **충족** (실측 + latency 확인) → **충족 (추정)** (추정치이거나 latency 미측정) → **부족**.

정렬: 판정 단계 → throttle 없는 쪽 → 우선순위 → 채널 수 → 파이프라인 FPS → 플랫폼 id.
- Most channels: 채널 수
- Best Performance: **카메라 파이프라인 FPS** (호스트 + NPU 전 구간 실측 총 FPS). NPU 단독 throughput 이 아니다.
- Lowest Power: NPU TDP, 같으면 NPU 1W 당 FPS. **호스트 전력은 포함하지 않는다.**

카드의 FPS 숫자는 카메라 파이프라인 FPS, Details 의 "Throughput FPS" 는 NPU 단독 벤치마크 값이다.

**How ranking works** 버튼이 위 식과 한계(30 FPS 부근 측정 · 15/60 FPS 는 대부분 추정 · 실제 카메라 코덱/전후처리/다중 모델은 반영 안 됨 · 양산 사양은 DEEPX 문의)를 보여준다.

## [section:npu,hardware,디바이스,dx-m1,dx-h1,플랫폼] 비교하는 플랫폼

현재 벤치마크 데이터의 NPU (호스트: deepx, deepx-B650MT, orangepi5plus, raspberrypi, rock-5b-plus):

| NPU | TOPS | TDP | 폼팩터 |
|-----|------|-----|--------|
| DX-H1 | 100 TOPS | 20 W | PCIe Card |
| DX-M1 | 25 TOPS | 5 W | M.2 |
| DX-M1M | 25 TOPS | 3 W | M.2 |

## [section:link,연동,dx_benchmark,공유] 다른 모듈과의 연동 · 공유

- 데이터는 DX Benchmark 결과를 서버 시작 때 집계한 `benchmarks.json` 이다.
- DX Benchmark 대시보드의 EdgeGuide 링크는 task · size · 채널 · FPS 를 URL 에 담아 넘긴다. 현재 입력은 늘 주소창 URL 에 반영되어 그대로 공유할 수 있다.

## [section:error,troubleshoot,문제,에러,0채널] 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| 추천 카드가 하나도 없음 | 그 task/size/runtime 조합의 벤치마크가 없음 | 다른 모델 크기 · runtime 을 고르거나 DX Benchmark 결과 확인 |
| 0 채널 · 부족 | 측정한 총 FPS 로는 목표 FPS 의 1채널도 못 채움 | 목표 FPS 를 낮추거나 더 작은 모델 크기 |
| Estimated badge | 목표 FPS 가 측정 범위 (채널당 ~30 FPS) 밖 | 양산 전 실제 하드웨어로 확인 |
| "측정 중 NPU throttle 발생" | 큰 모델에서 NPU 가 열 한계에 닿음 | 냉각 강화 또는 더 작은 모델 |
| "한계: 호스트" | CPU · 디코딩이 병목, NPU 는 여유 | 더 빠른 호스트를 쓰면 채널이 늘 수 있음 |
