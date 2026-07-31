# YOLO26 × DEEPX NPU — 벤치마크 분석

> **범위.** 본 보고서는 [`dx-benchmark/results/`](../results/) 에 commit된 측정
> 데이터를 근거로 작성되었다 — **6개 hardware 환경 × 2개 dx-all-suite release
> (v2.3.3, v2.4.0) = 12개 benchmark run**. 모든 run은 동일한 tool과 동일한 protocol로
> 측정되었으므로 환경 간·버전 간 비교가 동일 조건에서 성립한다. v2.4.0 run이 현재
> release이며 본 보고서의 분석 대상이고, v2.3.3 run은
> [§9](#9-dx-all-suite-release별-성능-추이)의 release 간 추이를 제공한다.
>
> **추적성.** 각 표는 출처 좌표(환경, dx-all-suite 버전, task, model size,
> ONNX-Runtime mode)를 명시한다. 따라서 모든 값은 run별 `*_results.json` 파일 또는
> interactive dashboard([`results/dashboard/index.html`](../results/dashboard/index.html))
> 로 재확인할 수 있다.
>
> **유의사항.** 일부 cell은 정확한 해석이 필요한 실제 platform 동작을 반영한다 —
> thermal limit에 도달한 board의 throttling, 그리고 NPU-bound가 아니라 host-bound인
> 지표다. 이러한 사항은 생략하지 않고 [§2](#2-수치를-읽는-법)에서 명시적으로 다룬다.

---

## 목차

1. [요약](#1-요약)
2. [수치를 읽는 법](#2-수치를-읽는-법)
3. [무엇을 측정했는가 — 용어와 방법](#3-무엇을-측정했는가--용어와-방법)
4. [실험 환경](#4-실험-환경)
5. [NPU 연산 성능 (Model-Level Throughput)](#5-npu-연산-성능-model-level-throughput)
6. [Inference Latency](#6-inference-latency)
7. [End-to-End 영상 파이프라인 (Single Stream)](#7-end-to-end-영상-파이프라인-single-stream)
8. [Multi-Stream 채널 수용량](#8-multi-stream-채널-수용량)
9. [dx-all-suite release별 성능 추이](#9-dx-all-suite-release별-성능-추이)
10. [환경별 배포 가이드](#10-환경별-배포-가이드)
11. [부록](#11-부록)

---

## 1. 요약

아래 표는 **현재 release(dx-all-suite v2.4.0)** 에서 각 환경의 **가장 가벼운 nano
model**이 보이는 실용 성능이다. 입력은 **Full HD(1920×1080) 30 fps** 영상이다.

표를 읽는 방법:

- 형식은 **`single-stream end-to-end FPS / 최대 동시 채널 수`**다. 앞의 값은 Full HD 영상
  **1개 stream**을 pipeline 전체(decode → preprocess → NPU → post-process)로 처리했을 때의
  FPS이고, 뒤의 값은 각 stream이 30 fps 이상을 유지하는 조건에서 동시에 처리할 수 있는 최대
  stream 수다.
- 각 cell은 두 ONNX-Runtime mode(ORT ON / OFF —
  [§3](#3-무엇을-측정했는가--용어와-방법)에서 정의) 중 single-stream end-to-end FPS가 더 높은
  쪽의 값이다.
- Classification은 single-stream end-to-end FPS만 표시한다. multi-stream 측정 대상이 아니기
  때문이다([§8](#8-multi-stream-채널-수용량) 참조).

| 환경 | Object Detection | Pose Estimation | Segmentation | Oriented Bounding Box | Classification |
|------|------------------|-----------------|--------------|-----------------------|----------------|
| **BIOSTAR_H1-Quattro** | 496.8 fps / 17 ch | 553.9 fps / 20 ch | 360.8 fps / 12 ch | 392.9 fps / 14 ch | 772.4 fps |
| **DX-AIPlayer-N97_M1** | 184.9 fps / 6 ch | 197.3 fps / 7 ch | 108.3 fps / 3 ch | 98.9 fps / 3 ch | 278.6 fps |
| **OrangePi5+_M1** | 148.1 fps / 4 ch | 243.4 fps / 8 ch | 101.5 fps / 3 ch | 100.0 fps / 3 ch | 1072.7 fps |
| **ROCK5B+_M1** | 141.5 fps / 4 ch | 237.9 fps / 8 ch | 86.8 fps / 2 ch | 101.8 fps / 3 ch | 957.9 fps |
| **RPi5B_M1** | 80.1 fps / 2 ch | 112.2 fps / 3 ch | 55.1 fps / 1 ch | 81.8 fps / 2 ch | 189.1 fps |
| **RPi5B_M1M** | 79.8 fps / 2 ch | 112.4 fps / 3 ch | 54.9 fps / 1 ch | 72.3 fps / 2 ch | 189.3 fps |

> **출처:** `results/<env>/<v2.4.0 run>/`, task = 각 열, size = `n`(nano), ORT = ON/OFF
> 중 더 나은 쪽. End-to-end FPS는 `pipeline_results.json`, 채널 수는
> 30-fps-per-channel threshold 기준 `multi_stream_results.json`.

### 핵심 발견

1. **DEEPX M1 NPU는 사양이 크게 다른 host CPU에서도 거의 동일한 연산 성능을 제공한다.**
   medium·large·x-large model, 즉 host가 아니라 NPU가 bottleneck인 구간에서는 4개의
   single-M1 machine(Intel N97, Rockchip OrangePi, Rockchip ROCK5B, Raspberry Pi 5)이
   수 % 이내로 일치한다([§5](#5-npu-연산-성능-model-level-throughput)). NPU가 성능의
   기준점이며, host와 그 interconnect는 주로 가장 가벼운 model과 NPU 주변의 영상
   pipeline에 영향을 준다.

2. **NPU-bound 구간(medium·large·x-large)의 model-level throughput이 v2.3.3 stack 대비
   v2.4.0 stack에서 중앙값 +28.4% 향상되었다.** 6개 환경 × 3개 size = 18개 cell 중 14개가
   +25–35% 구간에 들며, 모든 cell에서 향상 방향이 일관된다. DX-COM·DX-RT·driver·firmware가
   함께 바뀐 결과다([§9](#9-dx-all-suite-release별-성능-추이),
   [§2.1](#21-버전-추이는-release-stack-전체가-함께-바뀐-결과다)).

3. **H1-Quattro card는 M1 chip 4개로 model-level throughput을 약 4× 확장한다** — object
   detection medium·large·x-large의 `run_model` throughput이 single-M1 4대 평균의
   4.24–4.32×다([§5.2](#52-h1-quattro는-chip-4개로-model-level-throughput을-약-4-확장한다)).
   단일 stream end-to-end FPS는 host 공급 한계 때문에 같은 비율로 확장되지 않는다
   ([§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다)).

4. **경량 model의 end-to-end 상한은 NPU가 아니라 host다.** nano·small 구간의 single-stream
   end-to-end FPS는 동일 조건 model throughput의 45–82%에 머물며, NPU 평균 활용률은
   18–41%다([§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다)). 남는 NPU 여력은
   multi-stream으로 회수된다.

5. **ORT mode의 최적값은 환경 × task 조합에 따라 달라지며, 경량 model에서 그 차이는 최대
   +48.8%에 이른다.** 단일 기본값이 존재하지 않으므로 배포 전 확인이 필요하다
   ([§7.2](#72-ort-mode-선택은-환경--task-조합으로-결정된다)).

---

## 2. 수치를 읽는 법

아래 다섯 항목은 개별 수치로 결론을 내리기 전에 반드시 확인해야 할 사항이다.

### 2.1 버전 추이는 release stack 전체가 함께 바뀐 결과다

두 release 사이에는 특정 구성요소 하나가 아니라 **dx-all-suite가 배포하는 stack 전체**가
바뀌었다. 각 run의 metadata에 기록된 차이는 다음과 같다.

| 구성요소 | v2.3.3 측정 | v2.4.0 측정 | model-level 경로 | E2E·multi-stream 경로 |
|----------|:-------------:|:-------------:|:----------------:|:---------------------:|
| DX-COM (model 재컴파일) | v2.3.0-rc.5 | v2.4.0-rc.4 | 포함 | 포함 |
| DX-RT runtime | v3.3.2 | v3.4.0 | 포함 | 포함 |
| RT driver | v2.4.1 | v2.5.1 | 포함 | 포함 |
| PCIe driver | v2.2.0 | v2.4.1 | 포함 | 포함 |
| NPU firmware | v2.5.6 | v2.7.3 | 포함 | 포함 |
| DX-Stream | 3.0.1 | 3.1.0 | 미포함 | 포함 |

> **출처:** 각 run `environment.json`의 `benchmarked_models[].dxcom_version`, `npu`
> (`rt_version` / `driver` / `pcie_driver` / `firmware`), `software.dx_stream`. 6개 환경
> 모두 release별로 동일한 버전 조합을 사용했다.

동일하게 유지된 조건은 다음과 같다. DXNN binary format은 두 측정 모두 `v8`이며, 각 환경의
host OS·kernel은 변경되지 않았고, 측정 protocol 값(30초 throughput, 300-loop latency, 반복
횟수, 30 fps threshold, cooldown 목표) 역시 동일하다. tool 변경은 내부 실패 처리 안정화에 국한되며,
정상 측정 절차 자체는 바뀌지 않았다.

따라서 [§9](#9-dx-all-suite-release별-성능-추이)의 정확한 해석은 "medium·large·x-large 구간의
**model-level throughput**이 v2.3.3 stack 대비 v2.4.0 stack에서 중앙값 +28.4% 향상되었다"이며,
**개별 구성요소의 기여도는 본 데이터로 분리할 수 없다.**

또한 이 추이를 **single-stream E2E FPS에 그대로 적용해서는 안 된다.** 위 표의 마지막 열이
보여주듯 구성요소별로 영향 경로가 다르며, host가 이미 상한인 셀에서는 model-level 향상이
E2E로 전이될 자리가 없다([§2.4](#24-일부-지표는-npu-bound가-아니라-host-bound다),
[§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다)). 그런 셀의 E2E FPS는 두
release 사이에서 동등하거나, 환경·task 조합에 따라 소폭 낮게 측정되기도 한다. 이 차이는 NPU
성능이 아니라 E2E 경로(decode → preprocess → inference → postprocess) 내부에서 발생하지만,
**구성요소 단위 귀속에는 추가 측정이 필요하므로 본 문서에서는 원인을 단정하지 않는다.**
후속 release 문서에서 갱신할 예정이다.

### 2.2 M1과 M1M은 서로 다른 제품이며 수치를 섞어서는 안 된다

`RPi5B_M1`과 `RPi5B_M1M`은 **동일한 Raspberry Pi 5 host**에 **서로 다른 두 DEEPX
module**을 장착한 구성이다. NPU-bound model에서 M1M은 확연히 느리다 — 동일 host, 동일
release(v2.4.0), object detection, ORT OFF 기준:

| Size | RPi5B_M1 throughput | RPi5B_M1M throughput | M1M ÷ M1 |
|------|--------------------:|---------------------:|:--------:|
| m | 118.7 fps | 73.5 fps | 0.62 |
| l | 86.8 fps | 60.0 fps | 0.69 |
| x | 49.2 fps | 26.3 fps | 0.53 |

> **출처:** [`results/RPi5B_M1/20260722_150437/`](../results/RPi5B_M1/20260722_150437/)
> 및 [`results/RPi5B_M1M/20260723_142408/`](../results/RPi5B_M1M/20260723_142408/),
> `model_results.json`, family = `throughput`, ORT OFF.

M1M은 이 model들에서 31–47% 더 느린 별개의 SKU다(m −38%, l −31%, x −47%). 두 module 모두
nominal 1000 MHz core clock으로 동작하므로 이 차이는 clock 차이가 아닌 architectural
차이다. 또한 M1M은 LPDDR4(4200 Mbps, 1.92 GiB)를, M1은 LPDDR5(5600 Mbps, 3.92 GiB)를
사용한다. 가장 큰
model에서는 해당 M1M unit이 추가로 throttling하기 때문에 격차가 더 벌어진다
([§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다) 참조).

dashboard와 본 보고서는 두 구성을 별개 환경으로 유지한다. **M1과 M1M의 수치를 평균해서는
안 된다.**

### 2.3 Thermal limit에 도달하는 board는 지속 부하 구간에서 throttling한다

protocol(v3)은 각 model × ORT cell을 다음 순서로 실행하며, **cooldown을 두 지점에 배치**한다.

```
① cooldown → ② latency → ③ throughput → ④ cooldown(E2E 직전) → ⑤ E2E → ⑥ multi-stream
```

즉 E2E는 앞 단계의 잔열을 그대로 물려받지 않는다. ④의 cooldown이 각 board를
min(idle + 10 °C, 55 °C)로 되돌리며, v2.4.0 측정의 E2E 진입 온도는 39–55 °C였다. 따라서 E2E
단계의 throttling은 이전 단계에서 누적된 열이 아니라 **E2E 자체의 지속 부하** 때문에 발생한다.

반면 **⑤ E2E와 ⑥ multi-stream 사이에는 cooldown이 없다.** multi-stream은 E2E의 열 상태를
이어받은 상태에서 N개 stream을 동시에 처리하므로, 본 측정에서 부하가 가장 큰 구간이다. 모든
환경에서 throttling된 cell 비율이 multi-stream에서 가장 높은 것이 이 구조를 반영한다.

지속 부하를 방열하지 못하는 board는 NPU가 thermal limit에 도달해 clock을 1000 MHz에서
200–800 MHz 구간으로 낮춘다. 이는 software regression이 아니라 실제 thermal 동작이다.
Throttling된 cell은 raw 데이터에 `npu_throttled = true`로 기록되며, dashboard에는 clock
badge로 표시된다.

> **출처:** 각 v2.4.0 run `pipeline_results.json`의 `cooldown_temp_c` / `cooldown_wait_sec`,
> 3개 결과 파일의 `npu_clock_mhz_min`.

| 환경 (v2.4.0) | Model-level throttled | End-to-end throttled | Multi-stream throttled | Max NPU temp |
|----------------|:---------------------:|:--------------------:|:----------------------:|:------------:|
| BIOSTAR_H1-Quattro (active cooling) | 0 / 100 | 0 / 50 | 16 / 90 | 83 °C |
| DX-AIPlayer-N97_M1 (active cooling) | 0 / 100 | 5 / 50 | 33 / 78 | 84 °C |
| OrangePi5+_M1 | 0 / 100 | 4 / 50 | 29 / 78 | 82 °C |
| ROCK5B+_M1 | 24 / 100 | 22 / 50 | 51 / 76 | 86 °C |
| RPi5B_M1 | 0 / 100 | 2 / 50 | 8 / 78 | 80 °C |
| RPi5B_M1M | 28 / 100 | 26 / 50 | 43 / 66 | 87 °C |

> **출처:** 각 v2.4.0 run의 `model_results.json`, `pipeline_results.json`,
> `multi_stream_results.json`에 기록된 cell별 `npu_throttled` / `npu_temp_max_c`.

*model-level* 단계, 즉 단일 cooldown 직후의 latency·throughput 구간에서 이미 thermal limit에
도달한 board는 **ROCK5B+_M1**(24개 cell)과 **RPi5B_M1M**(28개 cell) 두 대다. 모든 board는
multi-stream 구간에서 어느 정도 throttling하며, active cooling이 적용된 x86 board와
`RPi5B_M1`은 model 단계 전 구간에서 clock을 유지한다.

Thermal limit에 도달한 두 board의 medium·large·x-large 수치는 module의 상한이 아니라
**지속 부하 하한**으로 해석해야 한다. cooling을 개선하면 상승한다.

Throttling은 평균 성능만 낮추는 것이 아니라 **측정 편차도 함께 키운다.** v2.4.0의 model
throughput cell 300개를 대상으로 run 간 편차(fps 표준편차 ÷ 평균)를 계산하면, throttling되지
않은 cell(249개)은 중앙값 0.31%(상위 10% 경계 1.15%)인 반면 throttling된 cell(51개)은 중앙값
5.46%, 최대 17.0%다. 이 model-level cell들에서 clock이 run마다 300–800 MHz 구간의 서로 다른
지점으로 하향되기 때문이다.
따라서 **편차가 큰 cell은 그 자체로 thermal 문제의 신호**로 활용할 수 있다.

> **출처:** 각 v2.4.0 run `model_results.json`의 `fps_std` / `fps` / `npu_throttled` /
> `npu_clock_mhz_min`, family = throughput 전체 cell.

### 2.4 일부 지표는 NPU-bound가 아니라 host-bound다

- **PCIe lane 폭이 가장 가벼운 model을 제한한다.** ORT OFF의 nano/small throughput은 NPU
  연산이 아니라 frame이 PCIe link를 통과하는 속도에 의해 제한된다. single-lane
  (**Gen3 ×1**) board 두 대(`RPi5B_M1`, `RPi5B_M1M`)는 nano object detection에서
  **약 179 fps**가 상한이지만, ×2/×4 board는 *동일한* NPU·release에서 **약 315–320 fps**에
  도달한다. 이것이 nano의 환경 간 편차는 크고 medium·large·x-large 편차는 작은 주된
  이유다([§5.1](#51-npu가-성능의-기준점이다)).

  NPU 활용률이 이를 직접 뒷받침한다. nano throughput 측정 구간의 NPU core 평균 활용률은
  Gen3 ×1 board에서 44%(`RPi5B_M1`)·56%(`RPi5B_M1M`)에 머무르는 반면, ×2/×4 board는
  **89–91%** 다. 즉 ×1 board의 NPU는 절반 이상 입력을 기다리는 상태다. 같은 board의
  medium 이상에서는 활용률이 89–92%로 회복되며, 이는 연산 시간이 길어져 전송 시간의 비중이
  줄어들기 때문이다. 참고로 PCIe 이론 단방향 대역폭은 Gen3 ×1 ≈ 1.0 GB/s, ×2 ≈ 2.0 GB/s,
  ×4 ≈ 3.9 GB/s다.

- **Latency는 host CPU와 interconnect에 의해 제한된다.** 동일 M1 module, 동일 v2.4.0
  release, object detection nano 기준으로 `RPi5B_M1`은 21.1 ms, `OrangePi5+_M1`은
  37.1 ms다. 이 편차는 NPU 특성이 아니라 host 특성이다([§6](#6-inference-latency)).

- **Classification end-to-end FPS는 NPU-bound가 아니라 decoder-bound다.** Classification
  model은 입력이 224×224로 작아 NPU 부하가 낮으며, 이 경량 부하 조건에서는 ARM board의
  hardware decoder가 x86 decode 경로보다 더 높은 decoded frame rate를 유지했다
  (end-to-end 기준 OrangePi 1072.7 fps, H1-Quattro 772.4 fps). 따라서 classification
  end-to-end FPS는 NPU 능력치가 아니라 *pipeline·decoder* 수치로 해석해야 한다.

### 2.5 이 수치는 정규화된 benchmark 조건이며, production duty cycle이 아니다

protocol은 수치의 비교 가능성을 확보하기 위해 조건을 의도적으로 통제한다. 실제 배포 환경은
아래 네 가지 점에서 다르며, 시스템 sizing 시 이를 반영해야 한다.

| Benchmark 조건 | 실제 production | 해석 |
|---|---|---|
| 각 model × ORT cell이 통제된 thermal 상태에서 시작한다(cooldown target ≤ min(idle + Δ10 °C, 55 °C), 60 °C 초과 시 시작 거부) | 24/7 pipeline은 model 사이에 냉각되지 않는다 | thermal-limited board에서는 지속 운용 시 [§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다)보다 **더 심하게** throttling할 수 있다. 해당 수치는 연속 운용의 상한으로 취급해야 한다. |
| task별로 Full HD(1920×1080) 30 fps **H.264** clip 1개 | 다른 codec(H.265)·해상도·bitrate·객체 밀도 | decoder와 post-processing 부하가 달라진다. H.265나 더 높은 해상도는 [§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다)의 host-bound 상한을 이동시킨다. |
| latency는 cold 상태의 single-core·synchronous 단발 측정 | warm 상태의 asynchronous·multi-core 서빙 경로 | latency는 host 응답성의 *상대 비교*([§6](#6-inference-latency))에 사용하고, production per-frame 예산으로 쓰지 않는다. |
| 채널 수용량은 **channel당 30 fps** threshold 기준 | channel당 15 fps 또는 60 fps SLA | 수용량은 threshold에 의존한다. 자체 SLA 기준으로 sizing하려면 `--fps-threshold <fps>`로 재측정해야 한다. |

---

## 3. 무엇을 측정했는가 — 용어와 방법

이 절은 이후 사용되는 모든 용어를 정의한다.

### 3.1 Workload 정의

**Model size.** YOLO26은 5개 size로 제공된다 — `n`(nano) < `s`(small) < `m`(medium) <
`l`(large) < `x`(extra-large). model이 클수록 정확도가 높고 속도는 느리다.

**입력 해상도.** object detection·pose estimation·segmentation은 640×640, oriented
bounding box는 1024×1024, classification은 224×224이다. 모든 영상 입력은
Full HD(1920×1080) 30 fps다.

### 3.2 하드웨어

**NPU (Neural Processing Unit).** neural network를 실행하는 DEEPX accelerator로, module
`M1` 또는 `M1M`, 또는 4-chip `H1-Quattro` card를 의미한다. 모든 module은 nominal
1000 MHz core clock으로 동작한다.

### 3.3 측정 지표

**Throughput (model-level, FPS).** DEEPX `run_model` tool이 NPU를 **모든 core에 걸쳐
asynchronous하게** 30초간 구동해 얻는 지속 frame rate. 영상 decoding과 rendering이 포함되지
않으므로 **NPU 연산 능력**의 가장 순수한 측정치다.

**Latency (ms).** **single frame** 처리 시간으로, **single-core·synchronous** 조건에서
측정한다(`run_model` 300-loop mode). host↔NPU 왕복을 포함한 단일 inference 호출의 응답성을
반영한다.

**End-to-end FPS.** **전체 GStreamer 영상 pipeline**(decode → preprocess → NPU inference →
post-process)의 frame rate로, DEEPX dx_stream element를 통해 측정한다. 실제 영상 분석
application이 체감하는 수치다.

**최대 채널 수 (Maximum channels).** **모든** stream이 30 fps 이상(per-channel threshold)을
유지하는 최대 동시 영상 stream 수. stream 수를 증가시키며 어느 stream이 30 fps 아래로
떨어지는 지점까지 경계 탐색으로 결정한다. status가 ok이고 모든 반복이 완료되었으며
per-channel FPS가 threshold를 만족하는 결과만 유효한 것으로 인정한다.

### 3.4 ONNX-Runtime mode (ORT ON / OFF) — model의 CPU 구간을 어디서 실행할지

DEEPX compiler는 필요에 따라 model graph를 **NPU 구간**과 **CPU 구간**으로 분할한다. ORT
mode는 ONNX Runtime으로 이 CPU 구간을 실행할지 여부를 결정한다.

| Mode | runtime이 실행하는 범위 | 반환되는 출력 | 비용 |
|------|------------------------|--------------|------|
| **ORT ON** | NPU 구간 **+** CPU 구간(후자는 ONNX Runtime library를 통해 **host CPU**로 offload) | 원본 ONNX model과 동일 — 그대로 사용 가능 | frame마다 host CPU 작업이 추가됨 |
| **ORT OFF** | NPU 구간만 | raw NPU 출력 tensor | host CPU offload 없음. 동등한 연산을 application이 직접 구현해야 함 |

두 mode는 모든 cell에서 함께 측정·공개되므로, application이 원본 ONNX model과 동일한
출력을 요구하는지 또는 최적 성능에 따라 선택할 수 있다.

### 3.5 측정 상세

**반복 횟수.** latency는 300-loop 1회, throughput은 30초 측정 3회 평균, end-to-end는 3회
평균이다. 각 측정 앞에 warm-up 1회를 실행하고 그 결과는 버린다. 표에는 평균과 함께 해당
측정들의 표준편차를 `±`로 표기하며, 이 편차가 throttling과 어떤 관계인지는
[§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다)에서 다룬다.
전체 protocol parameter는 [부록](#112-측정-protocol--주요-parameter)에 있다.

**Buffer-count — throughput 상한을 찾는 방법.** `run_model --buffer-count`에 대한 throughput은
포화 곡선이므로 **본 보고서의 모든 throughput cell은 sweep 결과다.** 공개된 수치는 기본값(6)에서의
값이 아니라 상한(ceiling)이다. v2.4.0 cell 전체에서 승자 buffer-count의 중앙값은 model이 커질수록
낮아진다 — **7(nano·small) → 6(medium) → 5(large) → 4(x-large)**. 따라서 asynchronous inference를
직접 구동하는 application이 이 flag를 기본값으로 두면 이 수치에 미달할 수 있다. 이 flag는
model-level 경로에만 적용되며, latency와 E2E/multi-stream pipeline에는 적용되지 않는다.

---

## 4. 실험 환경

4-chip x86 server부터 Raspberry Pi 5까지 6개 환경을 측정했으며, 각 환경은 DEEPX NPU를
장착한다. 환경 이름은 본 보고서와 dashboard 전반의 식별 key로 사용되며, host와 NPU module을
함께 나타낸다.

| 환경 | Host CPU | Arch | RAM | DEEPX NPU | Chips | PCIe link | CPU governor | Video decoder |
|------|----------|:----:|----:|-----------|:-----:|:---------:|:------------:|---------------|
| **BIOSTAR_H1-Quattro** | AMD Ryzen 5 9600X (6-core) | x86_64 | 30.5 GB | H1-Quattro card | 4 | Gen3 ×4 | powersave | vaapidecodebin (HW) |
| **DX-AIPlayer-N97_M1** | Intel N97 (4-core) | x86_64 | 7.5 GB | M1 module | 1 | Gen3 ×2 | powersave | vah264dec (HW) |
| **OrangePi5+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 15.6 GB | M1 module | 1 | Gen3 ×4 | ondemand | mppvideodec (HW) |
| **ROCK5B+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 7.8 GB | M1 module | 1 | Gen3 ×2 | ondemand | mppvideodec (HW) |
| **RPi5B_M1** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | M1 module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |
| **RPi5B_M1M** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | **M1M** module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |

> **출처:** 각 v2.4.0 `environment.json`의 `host` / `npu` 필드와
> `pipeline_results.json`의 `decoder` 필드.

각 release 내에서 6개 환경은
[§2.1](#21-버전-추이는-release-stack-전체가-함께-바뀐-결과다)에 정리한 동일한 software stack으로
측정되었다.

---

## 5. NPU 연산 성능 (Model-Level Throughput)

**DEEPX NPU의 가장 순수한 측정치**로, 영상 decoding이나 rendering이 없는 경로에서
`run_model`이 산출하는 지속 multi-core throughput이다.

**Object detection, throughput (fps), ORT OFF, 현재 release(v2.4.0):**

| 환경 | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 1326.0 | 794.0 | 491.1 | 372.5 | 201.8 |
| DX-AIPlayer-N97_M1 | 314.9 | 197.8 | 120.1 | 85.6 | 47.4 |
| OrangePi5+_M1 | 320.3 | 197.6 | 117.4 | 87.2 | 48.0 |
| ROCK5B+_M1 | 319.3 | 188.0 | 107.5 | 84.9 | 42.7 |
| RPi5B_M1 | 179.5 | 179.1 | 118.7 | 86.8 | 49.2 |
| RPi5B_M1M | 179.2 | 153.2 | 73.5 | 60.0 | 26.3 |

> **출처:** `results/<env>/<v2.4.0 run>/model_results.json`, task = object_detection,
> family = throughput, `use_ort` = false.

### 5.1 NPU가 성능의 기준점이다

4개의 single-M1 machine에서 medium 이상 model, 즉 NPU가 bottleneck인 구간은 근접하게
일치하며, 가벼운 model은 전적으로 host 측 요인으로 편차가 벌어진다.

| Size | N97 | OrangePi | ROCK5B | RPi5B_M1 | 평균 | 편차 (coefficient of variation) |
|------|----:|---------:|-------:|---------:|-----:|:-------------------------------:|
| l | 85.6 | 87.2 | 84.9 | 86.8 | 86.1 | **1.0 %** |
| m | 120.1 | 117.4 | 107.5 | 118.7 | 115.9 | 4.3 % |
| x | 47.4 | 48.0 | 42.7 | 49.2 | 46.8 | 5.3 % |
| s | 197.8 | 197.6 | 188.0 | 179.1 | 190.6 | 4.1 % |
| n | 314.9 | 320.3 | 319.3 | 179.5 | 283.5 | 21.2 % |

> **출처:** 위 object-detection v2.4.0 ORT-OFF 표. coefficient of variation = 4개 M1 host
> 값의 **모표준편차(population standard deviation) ÷ 평균**이며, 반올림 전 raw fps로
> 계산했다.

**해석.**

- size **l**에서 네 host는 **1.0%** 이내로 일치한다. DEEPX NPU가 사실상 모든 연산을
  수행하고 module이 동일하므로 host의 영향이 거의 없다.
- **m**과 **x**의 잔여 편차는 `ROCK5B+_M1`의 thermal
  throttling([§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다))에서
  비롯되며, 해당 board의 수치를 나머지 세 대보다 낮게 만든다.
- **nano**의 큰 편차는 host CPU 효과가 아니라 **PCIe 대역폭** 효과다. ×1 board는 약 179 fps가
  상한인 반면 ×2/×4 board는 약 315–320 fps에 도달하며, 이때 NPU 활용률은 44%에 불과하다
  ([§2.4](#24-일부-지표는-npu-bound가-아니라-host-bound다)).

**용량 설계 시 시사점.** 배포 규모는 host 간 이식성이 있는 medium·large·x-large 수치를
기준으로 산정해야 한다. nano/small 수치는 host의 PCIe link와 CPU에 의존한다.

### 5.2 H1-Quattro는 chip 4개로 model-level throughput을 약 4× 확장한다

H1-Quattro card는 M1 chip 4개를 탑재한다. 아래 비교는 **`run_model` model-level
throughput**(object detection, ORT OFF)만을 대상으로 하며, NPU가 bottleneck인
medium·large·x-large에서 single M1 4대 평균의 약 4배에 도달한다.

| Object detection (v2.4.0, ORT OFF) | H1-Quattro | M1 평균 | 배율 |
|------------------------------------|-----------:|--------:|:----:|
| m | 491.1 | 115.9 | 4.24× |
| l | 372.5 | 86.1 | 4.32× |
| x | 201.8 | 46.8 | 4.31× |

> **출처:** [§5](#5-npu-연산-성능-model-level-throughput)의 object-detection v2.4.0
> ORT-OFF 표. M1 평균은 4개 M1 host의 평균이며 ROCK5B의 throttling된 수치를 포함한다.

이 배율은 **model-level throughput에만** 적용된다. 단일 stream end-to-end FPS는 host 공급
한계가 먼저 걸리므로 nano에서 throughput의 47%에 머물고, 4-chip의 여력은 multi-stream
채널 수(nano 17채널)로 나타난다([§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다),
[§8](#8-multi-stream-채널-수용량)).

### 5.3 Task 난이도 순서는 모든 환경에서 일관적이다

출력 head가 복잡하고 입력이 클수록 throughput이 감소한다. size m, v2.4.0, ORT OFF
기준으로 그 순서는 모든 환경에서 동일하다(`BIOSTAR_H1-Quattro` / `RPi5B_M1` 값).

| Task | 입력 | H1-Quattro | RPi5B_M1 |
|------|:----:|-----------:|---------:|
| Classification (최소 head) | 224×224 | 5514.7 fps | 1401.1 fps |
| Object detection | 640×640 | 491.1 fps | 118.7 fps |
| Pose estimation | 640×640 | 468.6 fps | 112.6 fps |
| Segmentation (mask 출력) | 640×640 | 321.5 fps | 80.0 fps |
| Oriented bounding box (최대 입력) | 1024×1024 | 174.4 fps | 42.2 fps |

> **출처:** `model_results.json`, size = m, family = throughput, ORT OFF, 명시된 두 환경의
> v2.4.0 run.

---

## 6. Inference Latency

Latency는 single-frame·single-core 측정치다. **응답성** 지표이며 부분적으로 **host·
interconnect-bound**다.

**Object detection latency (ms), ORT OFF, v2.4.0:**

| 환경 | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 10.38 | 16.28 | 23.31 | 30.80 | 56.22 |
| DX-AIPlayer-N97_M1 | 22.35 | 28.78 | 36.43 | 43.64 | 69.57 |
| OrangePi5+_M1 | 37.07 | 44.01 | 42.93 | 57.78 | 86.21 |
| ROCK5B+_M1 | 34.29 | 35.72 | 50.14 | 59.30 | 88.51 |
| RPi5B_M1 | 21.13 | 27.04 | 33.26 | 41.32 | 66.79 |
| RPi5B_M1M | 22.50 | 29.20 | 39.60 | 46.40 | 75.43 |

> **출처:** `results/<env>/<v2.4.0 run>/model_results.json`, task = object_detection,
> family = latency, ORT OFF.

**해석.** throughput과 달리 latency는 M1 host 간 편차가 크다. nano 기준으로 `RPi5B_M1`은
21.1 ms, `OrangePi5+_M1`은 37.1 ms이며, 이는 *동일한 NPU module·release* 조건에서의
결과다. 단일 synchronous 호출은 raw NPU 연산이 아니라 host CPU와 host↔NPU interconnect가
지배하기 때문이다 — NPU module이 동일함에도 Raspberry Pi 5 host 두 대가 RK3588 board보다
낮은 latency를 기록한다.

따라서 latency는 특정 host에서의 단일 요청 응답성을 판단하는 데 사용하고, NPU 용량은
throughput([§5](#5-npu-연산-성능-model-level-throughput))으로 판단하는 것이 적절하다.

**ORT ON의 latency에는 host CPU 구간이 포함된다.** ORT ON 측정에서 `run_model`은 model의
CPU 구간 실행 시간(`cpu_0_ms`)을 함께 보고한다. object detection n·m·x 기준으로 그 값은 x86
board에서 0.26–1.38 ms, ARM board에서 2.3–8.0 ms다. 응답성이 중요한 application에서는 ORT
ON이 제공하는 편의성과 이 추가 시간을 함께 고려해야 한다
([§3.4](#34-onnx-runtime-mode-ort-on--off--model의-cpu-구간을-어디서-실행할지)).

> **출처:** 각 v2.4.0 run `model_results.json`, task = object_detection, family = latency,
> `use_ort` = true의 `cpu_0_ms`.

---

## 7. End-to-End 영상 파이프라인 (Single Stream)

End-to-end FPS는 single Full HD 30 fps stream에서 전체 pipeline(decode → preprocess →
NPU → post-process)을 측정한 값으로, 실제 application이 관측하는 수치다.

**Object detection end-to-end FPS, v2.4.0, 더 나은 ORT mode 기준:**

| 환경 | ORT | n | s | m | l | x | Video decoder |
|------|:---:|--:|--:|--:|--:|--:|---------------|
| BIOSTAR_H1-Quattro | ON | 496.8 | 494.4 | 491.7 | 367.8 | 202.6 | vaapidecodebin (HW) |
| DX-AIPlayer-N97_M1 | OFF | 184.9 | 164.1 | 116.6 | 85.1 | 49.0 | vah264dec (HW) |
| OrangePi5+_M1 | ON | 148.1 | 125.0 | 98.5 | 80.1 | 48.1 | mppvideodec (HW) |
| ROCK5B+_M1 | ON | 141.5 | 130.4 | 108.1 | 85.5 | 36.5 | mppvideodec (HW) |
| RPi5B_M1 | OFF | 80.1 | 80.1 | 79.5 | 80.3 | 48.8 | avdec_h264 (SW) |
| RPi5B_M1M | OFF | 79.8 | 80.2 | 77.8 | 57.6 | 21.2 | avdec_h264 (SW) |

> **출처:** `results/<env>/<v2.4.0 run>/pipeline_results.json`, task = object_detection.
> 각 행에 표시된 ORT mode는 nano FPS가 더 높았던 쪽이며, "HW"/"SW"는 hardware/software
> video decoder를 표시한다. 모든 환경의 두 mode 결과는 raw 데이터와 dashboard에 포함되어
> 있다.

**해석.**

- **Video decoder가 가벼운 model을 제한할 수 있다.** `RPi5B_M1`에서는 nano부터 large까지
  model size와 무관하게 약 80 fps에 수렴한다. 가벼운 model의 상한은 NPU가 아니라
  **software** H.264 decoder(`avdec_h264`)다. hardware decoder를 탑재한
  board(`vaapidecodebin`, `vah264dec`, `mppvideodec`)는 훨씬 높은 rate에 이르기까지 이
  제약에 도달하지 않는다.

- **무거운 model에서는 다시 NPU가 상한이 되며**, end-to-end FPS는
  [§5](#5-npu-연산-성능-model-level-throughput)의 throughput 순서를 따른다. `RPi5B_M1`의
  x-large는 end-to-end 48.8 fps로 약 80 fps인 decoder 상한보다 낮은데, 이 구간에서는 NPU가
  더 느린 단계이기 때문이다. `RPi5B_M1M`의 large·x-large는 느린 SKU와 throttling이 겹쳐
  더 낮다(57.6 / 21.2 fps).

- **어느 ORT mode가 유리한지는 환경과 task에 따라 뒤집힌다.** 경량 model에서 그 차이는 최대
  +48.8%에 이르며, 단일 기본값이 존재하지 않는다. 상세 비교와 원인은
  [§7.2](#72-ort-mode-선택은-환경--task-조합으로-결정된다)에서 다룬다.

### 7.1 경량 model의 end-to-end 상한은 NPU가 아니라 host다

end-to-end FPS를 동일 ORT mode의 model
throughput([§5](#5-npu-연산-성능-model-level-throughput))과 비교하면, 경량 model에서 NPU 연산
능력의 절반 이상이 사용되지 않는다는 사실이 드러난다.

**object detection, v2.4.0 — `end-to-end ÷ model throughput` / end-to-end 구간의 NPU 평균 활용률:**

| Size | BIOSTAR_H1-Quattro | OrangePi5+_M1 | RPi5B_M1 |
|:----:|:------------------:|:-------------:|:--------:|
| n | 47 % / NPU 21 % | 82 % / NPU 37 % | 45 % / NPU 18 % |
| s | 63 % / NPU 41 % | 69 % / NPU 58 % | 45 % / NPU 34 % |
| m | 100 % / NPU 70 % | 84 % / NPU 73 % | 67 % / NPU 55 % |
| l | 99 % / NPU 74 % | 101 % / NPU 91 % | 92 % / NPU 80 % |
| x | 100 % / NPU 83 % | 99 % / NPU 93 % | 99 % / NPU 94 % |

> **출처:** `pipeline_results.json`의 `avg_e2e_fps` ÷ `model_results.json`의 동일 ORT mode
> throughput `fps`, 그리고 `pipeline_results.json`의 `npu_total_avg_pct`. 각 size는 두 ORT
> mode 중 end-to-end가 더 높은 쪽을 사용했다.

**해석.**

- 경량 model(n·s)에서는 비율이 45–82%에 그치고 NPU 활용률이 18–41%에 머문다. 상한은 NPU가
  아니라 단일 pipeline의 host 처리 속도(decode → preprocess → 제출 → post-process)다.
- medium 이상에서는 비율이 92–101%, 활용률이 55–94%로 상승한다. NPU 연산 시간이 충분히
  길어져 host가 공급을 따라잡기 때문이다.
- **배포 시사점:** 경량 model에서 남는 NPU 여력은 **multi-stream으로만 회수된다.**
  `BIOSTAR_H1-Quattro`의 nano single stream은 throughput의 47%에 불과하지만, multi-stream
  에서는 17채널을 수용한다([§8](#8-multi-stream-채널-수용량)). 반대로 medium 이상은 단일
  stream만으로 이미 NPU를 포화시키므로 채널 확장 여지가 작다.

### 7.2 ORT mode 선택은 환경 × task 조합으로 결정된다

경량 model(n·s)에서 두 mode의 end-to-end 차이는 최대 +48.8%(OrangePi5+_M1 object detection
nano)이며, 어느 쪽이 유리한지는 환경과 task에 따라 반대로 뒤집힌다.

| 환경 | Object Detection | Pose Estimation | Segmentation | OBB | Classification |
|------|:----------------:|:---------------:|:------------:|:---:|:--------------:|
| BIOSTAR_H1-Quattro | **ON** (+9.9–10.6 %) | 동등 | **ON** (+12.9–14.6 %) | 동등 | 동등 |
| DX-AIPlayer-N97_M1 | **OFF** (+14.6–17.4 %) | OFF (+11.4–13.4 %) | **OFF** (+12.2–14.4 %) | 동등 | 동등 |
| OrangePi5+_M1 | **ON** (+24.9–48.8 %) | OFF (+12.5–21.3 %) | **ON** (+4.4–20.7 %) | OFF (+1.3–8.9 %) | 동등 |
| ROCK5B+_M1 | **ON** (+36.6–48.8 %) | OFF (+8.8–23.1 %) | **ON** (+4.0–11.5 %) | 동등 | 동등 |
| RPi5B_M1 | **OFF** (+18.3–18.7 %) | OFF (+36.3–37.4 %) | **OFF** (+23.2–23.5 %) | OFF (+1.1–18.3 %) | 동등 |
| RPi5B_M1M | **OFF** (+17.5–18.9 %) | OFF (+36.5–37.4 %) | **OFF** (+22.6–23.8 %) | OFF (+0.0–6.9 %) | 동등 |

> **출처:** `results/<env>/<v2.4.0 run>/pipeline_results.json`, size = n·s. 괄호 안은 우세한
> mode의 상대 이득으로, **nano와 small 두 값의 범위**이며 `avg_e2e_fps`로 직접 계산했다
> (예: OrangePi5+_M1 object detection nano = 148.1 ÷ 99.6 − 1 = +48.8 %). **"동등"은 nano와
> small 모두 차이가 5% 이내인 cell**을 뜻한다. Classification은 CPU 구간이 없어 두 mode가
> 동일하다([§3.4](#34-onnx-runtime-mode-ort-on--off--model의-cpu-구간을-어디서-실행할지)).

**왜 뒤집히는가.** ORT OFF는 host CPU 작업을 줄이지만, pipeline에서 그 연산이 사라지는 것은
아니다. application이 담당하는 post-processing 단계로 이동한다. Rockchip board의 object
detection이 대표적인 사례다.

| OrangePi5+_M1, OD nano (v2.4.0) | ORT ON | ORT OFF |
|---------------------------------|-------:|--------:|
| End-to-end FPS | 148.1 | 99.6 |
| host CPU 사용률 | 250 % | 211 % |
| NPU 평균 활용률 | 37.3 % | 22.0 % |

> **출처:** `pipeline_results.json`의 `avg_e2e_fps` / `avg_cpu_pct` / `npu_total_avg_pct`,
> task = object_detection, size = n.

ORT OFF는 CPU 사용률이 *더 낮은데도* FPS와 NPU 활용률이 함께 하락한다. 즉 CPU 포화가 원인이
아니라, 직렬 단계 하나(post-processing)가 느려진 것이 원인이다. 측정 pipeline의 모든 queue는
`leaky=no`이므로 이 정체가 상류로 backpressure로 전파되고, NPU에 새 frame이 공급되지 않아
NPU가 idle 상태에 머문다. ORT ON에서는 model의 CPU 구간을 ONNX Runtime이 처리해 post-processing
단계로 전달되는 tensor가 이미 정제된 형태이므로 이 정체가 발생하지 않는다.

반대 방향의 사례도 같은 원리다. `RPi5B_M1`·`RPi5B_M1M`은 software decoder가 CPU를 크게
점유하므로, ORT ON의 추가 CPU 작업이 decode와 경합해 모든 task에서 ORT OFF가 유리하다.

**Segmentation은 host post-processing 비용이 가장 큰 task다.** 동일 환경·동일 nano·ORT ON
기준으로 `BIOSTAR_H1-Quattro`의 host CPU 사용률은 object detection 213%, segmentation 517%다.
mask 출력을 host에서 재구성해야 하기 때문이며, 이것이 segmentation의 채널 수용량이 detection
보다 낮은 주된 이유다([§8](#8-multi-stream-채널-수용량)).

### 7.3 E2E 상한이 host에 있는 환경에서는 model을 키워도 FPS 손실이 없다

[§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다)의 결과를 배포 관점으로
환산하면, host가 상한인 구간에서는 model size를 올려도 end-to-end FPS가 거의 변하지 않는다.
정확도를 추가 비용 없이 확보할 수 있는 구간이다.

| 환경 | nano 대비 5% 이내를 유지하는 최대 size | 근거 (object detection end-to-end FPS) |
|------|:--------------------------------------:|----------------------------------------|
| BIOSTAR_H1-Quattro | **m** | n 496.8 → s 494.4 → m 491.7 → l 367.8 |
| DX-AIPlayer-N97_M1 | n | n 184.9 → s 164.1 (−11 %) |
| OrangePi5+_M1 | n | n 148.1 → s 125.0 (−16 %) |
| ROCK5B+_M1 | n | n 141.5 → s 130.4 (−8 %) |
| RPi5B_M1 | **l** | n 80.1 → s 80.1 → m 79.5 → l 80.3 |
| RPi5B_M1M | **m** | n 79.8 → s 80.2 → m 77.8 → l 57.6 |

> **출처:** `pipeline_results.json`, task = object_detection, 각 size에서 두 ORT mode 중 더
> 높은 값. 기준은 nano 값의 95% 이상 유지다.

Task별로도 동일한 계산이 성립한다. `RPi5B_M1`은 pose estimation에서 medium, segmentation에서
large까지 무상이며, `BIOSTAR_H1-Quattro`는 pose estimation·segmentation 모두 small까지다.
반면 `DX-AIPlayer-N97_M1`·`OrangePi5+_M1`·`ROCK5B+_M1`은 nano에서 이미 NPU 또는 pipeline이
상한이므로 size를 올리면 곧바로 FPS가 하락한다.

**배포 지침:** 목표 FPS를 만족하는 가장 큰 model을 선택하면 동일 hardware에서 정확도를 높일 수
있다. 단, 이 여유는 host 상한에서 비롯되므로 host를 개선(hardware decoder, 더 넓은 PCIe link)
하면 다시 model size가 FPS를 지배한다.

---

## 8. Multi-Stream 채널 수용량

채널 수용량은 각 stream이 30 fps 이상을 유지하는 조건에서의 Full HD 30 fps stream 최대
개수다.

**Object detection, 최대 채널 수, v2.4.0 (ORT ON/OFF 중 더 나은 쪽):**

| 환경 | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 17 | 17 | 16 | 12 | 6 |
| DX-AIPlayer-N97_M1 | 6 | 5 | 3 | 2 | 1 |
| OrangePi5+_M1 | 4 | 4 | 3 | 2 | 1 |
| ROCK5B+_M1 | 4 | 4 | 2 | 1 | 1 |
| RPi5B_M1 | 2 | 2 | 2 | 2 | 1 |
| RPi5B_M1M | 2 | 2 | 1 | 1 | 0 |

> **출처:** `results/<env>/<v2.4.0 run>/multi_stream_results.json`, task =
> object_detection, stable-capacity rule(status ok + 모든 run 완료 + per-channel FPS ≥ 30)을
> 만족하는 최대 `stream_count`.

**해석.** 채널 수용량은 end-to-end FPS의 multi-stream 일반화이며 동일한 bottleneck을
그대로 반영한다.

- H1-Quattro의 4개 chip이 큰 우위를 제공한다(nano object detection에서 최대 17채널).
  single-M1 board는 host CPU·PCIe link·cooling에 따라 2–6채널 범위다.
- Gen3 ×1 board 두 대(`RPi5B_M1`, `RPi5B_M1M`)는 PCIe link 제약으로 가벼운 detection에서
  2채널이 상한이다([§2.4](#24-일부-지표는-npu-bound가-아니라-host-bound다)).
- `RPi5B_M1M`은 x-large에서 0채널로 기록되었다. 느린 M1M
  SKU([§2.2](#22-m1과-m1m은-서로-다른-제품이며-수치를-섞어서는-안-된다))와
  throttling([§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다))이
  겹쳐 x-large stream 하나조차 30 fps로 유지하지 못한다.

**Classification은 multi-stream을 의도적으로 측정하지 않는다.** 224×224 classifier는 실제
multi-stream 영상 분석 workload를 대표하지 못하며, 그 end-to-end 수치는
decoder-bound([§2.4](#24-일부-지표는-npu-bound가-아니라-host-bound다))이기 때문이다.

---

## 9. dx-all-suite release별 성능 추이

동일한 환경들을 `results/`에 commit된 두 release(v2.3.3, v2.4.0)에서 측정했다. 두 측정 사이에는
DX-COM(model 재컴파일)·DX-RT runtime·RT driver·PCIe driver·NPU firmware가 모두 변경되었으므로
([§2.1](#21-버전-추이는-release-stack-전체가-함께-바뀐-결과다)), 이 추이는 해당 stack 전체의
**복합** 개선을 반영하며 개별 구성요소로 분리할 수 없다.

**Object detection throughput (fps), ORT OFF, v2.3.3 → v2.4.0:**

| 환경 | Size | v2.3.3 | v2.4.0 | 변화 |
|------|:----:|-------:|-------:|:----:|
| BIOSTAR_H1-Quattro | m | 376.6 | 491.1 | **+30.4 %** |
| BIOSTAR_H1-Quattro | l | 277.2 | 372.5 | **+34.3 %** |
| BIOSTAR_H1-Quattro | x | 158.2 | 201.8 | **+27.5 %** |
| DX-AIPlayer-N97_M1 | m | 91.1 | 120.1 | +31.8 % |
| DX-AIPlayer-N97_M1 | l | 66.9 | 85.6 | +27.9 % |
| OrangePi5+_M1 | m | 90.5 | 117.4 | +29.7 % |
| OrangePi5+_M1 | l | 67.3 | 87.2 | +29.5 % |
| RPi5B_M1 | m | 90.8 | 118.7 | +30.6 % |
| RPi5B_M1 | l | 67.4 | 86.8 | +28.9 % |
| RPi5B_M1M | m | 55.7 | 73.5 | +32.0 % |
| RPi5B_M1M | l | 41.8 | 60.0 | +43.4 % |

> **출처:** 각 환경의 v2.3.3 / v2.4.0 run `model_results.json`, task = object_detection,
> family = throughput, ORT OFF, (task, size, ORT mode) 기준 매칭.

**해석.** NPU-bound 구간(medium·large·x-large) 18개 cell의 model-level throughput 변화는
중앙값 **+28.4%** 이며, 18개 중 14개가 +25–35% 구간에 든다. 최저는 `ROCK5B+_M1` x-large의
+12.9%로 해당 v2.4.0 run이 throttling한 결과이고
([§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다)), 최고는
`RPi5B_M1M` large의 +43.4%다. 모든 cell에서 향상 방향은 일관된다.

경량 model(nano·small) 12개 cell의 변화폭은 −0.1%~+63.2%로 훨씬 넓다. 이 구간은 NPU가 아니라
host·PCIe 상한에 지배되므로([§2.4](#24-일부-지표는-npu-bound가-아니라-host-bound다),
[§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다)) 단일 범위로 요약하지 않는다.
`RPi5B_M1`의 nano는 −0.1%로, 두 release 모두 Gen3 ×1 link 상한(약 179 fps)에 걸려 있다.

이는 **최신 dx-all-suite release로의 업그레이드**를 뒷받침하는 가장 명확한 근거다.
**model-level 기준으로** 동일 hardware가 확연히 빠르게 동작한다. 단, single-stream E2E는 host
상한에 지배되는 셀에서 이 향상률을 그대로 따라가지 않는다
([§2.1](#21-버전-추이는-release-stack-전체가-함께-바뀐-결과다)).

---

## 10. 환경별 배포 가이드

아래 가이드는 위 표들에 근거하며, 모든 수치는 v2.4.0 기준이다.

- **BIOSTAR_H1-Quattro (4-chip x86 server).** 고밀도 구성 선택지다. nano에서 object
  detection 16–17채널 또는 pose 20채널을 처리한다. active cooling이 적용되어 model 단계 전
  구간에서 clock을 유지한다(throttling된 model cell 0개). 채널 밀도가 가장 중요한 용도에
  권장된다.

- **DX-AIPlayer-N97_M1 (compact x86 AI box).** 균형 잡힌 single-M1 appliance다. nano에서
  object detection 6채널, pose 7채널을 처리하며 hardware decoder와 active cooling을 갖춘다.
  범용 edge box로 적합하다.

- **OrangePi5+_M1 (ARM SBC, single M1).** ×4 PCIe link와 hardware decoder를 갖춘 우수한
  single-NPU board다. nano에서 object detection 4채널, pose 8채널을 처리하며, ARM board 중
  nano/small model throughput이 가장 높다. model 단계 전 구간에서 clock을 유지했으며, 지속
  multi-stream 운용에는 cooling 보강이 권장된다.

- **ROCK5B+_M1 (ARM SBC, single M1).** OrangePi와 동일한 RK3588 계열이지만, 이 unit은
  thermal limit에 더 이르게 도달해(model-level cell 24개 throttling) medium·large·x-large
  수치가 낮아졌다. detection 2–4채널, pose 최대 8채널을 처리할 수 있으며, throttling으로
  손실된 headroom을 회복하려면 **active cooling 보강이 필요하다.**

- **RPi5B_M1 (Raspberry Pi 5, single M1).** entry-level 구성으로, detection 또는
  segmentation 1–2채널에 적합하다. 두 가지 상한이 존재한다. **software** video decoder가
  가벼운 model의 end-to-end FPS를 약 80 fps로 제한하고, **Gen3 ×1** PCIe link가 nano/small
  model throughput을 약 179 fps로 제한한다. hardware decoding과 더 넓은 PCIe link를 갖춘
  host에서는 두 제약이 모두 해소된다.

- **RPi5B_M1M (Raspberry Pi 5, M1M module).** 본 측정 대상 중 가장 낮은 tier다. M1M SKU는
  무거운 model에서 M1보다 31–47%
  느리고([§2.2](#22-m1과-m1m은-서로-다른-제품이며-수치를-섞어서는-안-된다)), 이 unit은 추가로
  throttling했다([§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다)).
  배포 규모를 보수적으로 산정하고, 무거운 model 수치는 하한으로 해석해야 한다.

### Memory footprint와 배포 적합성

제약은 연산 성능만이 아니다. host RAM도 예산에 넣어야 하고, NPU 쪽 memory는 대상 장비에서 확인해야
한다.

**Host memory는 채널 수에 따라 증가한다.** 측정된 채널 수용량 지점에서 pipeline RSS는
**약 211 MiB**(OrangePi5+_M1, detection nano, 4채널)부터 **약 1376 MiB**(BIOSTAR_H1-Quattro,
segmentation x-large, 5채널) 범위였고, 채널을 하나 추가할 때 수십 MiB 규모가 증가했다. 따라서 높은
채널 수와 무거운 model은 NPU 용량과 함께 host RAM도 예산에 넣어야 하며, 8 GB SBC에서는 NPU보다
host memory가 먼저 제약이 될 수 있다.

**NPU memory 예산은 module마다 다르다.** M1은 LPDDR5 3.92 GiB, M1M은 LPDDR4 1.92 GiB로 약
절반이다([§2.2](#22-m1과-m1m은-서로-다른-제품이며-수치를-섞어서는-안-된다)). model의 NPU memory
점유는 입력 해상도와 size가 커질수록 늘어나므로, 배포할 module의 예산에 맞춰 task·size 조합과
multi-model 동시 상주 여부를 선택해야 한다. 실제 점유량은 대상 장비에서 확인하는 것이 확실하다.

### 일반 지침

- NPU 용량은 host 간 이식성이 있는 **medium·large·x-large throughput** 수치를 기준으로
  설계한다([§5.1](#51-npu가-성능의-기준점이다)). nano/small 수치는 host의 PCIe link와 CPU가
  이를 따라갈 수 있음을 검증한 경우에만 적용한다.
- **경량 model에서 NPU 여력을 모두 사용하려면 multi-stream이 필요하다.** 단일 stream은
  throughput의 45–82%에 머문다([§7.1](#71-경량-model의-end-to-end-상한은-npu가-아니라-host다)).
- **목표 FPS를 만족하는 가장 큰 model을 선택한다.** host가 상한인 환경에서는 size를 올려도
  FPS 손실이 거의 없으므로 정확도를 무상으로 확보할 수
  있다([§7.3](#73-e2e-상한이-host에-있는-환경에서는-model을-키워도-fps-손실이-없다)).
- **ORT mode는 환경 × task 조합으로 결정한다**
  ([§7.2](#72-ort-mode-선택은-환경--task-조합으로-결정된다)). 다만 application이 원본 ONNX
  model과 동일한 출력을 요구하면 성능과 무관하게 **ORT ON**이 필요하고, 동등한 연산을 직접
  구현할 수 있다면 **ORT OFF**도 선택
  가능하다([§3.4](#34-onnx-runtime-mode-ort-on--off--model의-cpu-구간을-어디서-실행할지)).
- passive cooling board에서 지속 multi-stream을 운용하는 경우에는 cooling을 예산에
  반영하거나, peak가 아닌 throttling된 수치를 기준으로 계획한다. 측정 편차가 큰 구간은
  thermal 문제의 신호로 함께 확인한다
  ([§2.3](#23-thermal-limit에-도달하는-board는-지속-부하-구간에서-throttling한다)).

---

## 11. 부록

### 11.1 벤치마크 재현

아래 명령은 `dx-benchmark/` 디렉토리에서 실행한다. 설치·설정 절차는 tool의
[`README.md`](../README.md)에 있다.

```bash
# 환경 점검 + fingerprint 출력
./run.sh preflight

# 실행 없이 벤치마크 matrix 미리보기
./run.sh dry-run

# 전체 suite 실행 (model-level + end-to-end + multi-stream)
./run.sh run

# 특정 size / task만 실행
./run.sh run --sizes n,s --task object_detection

# 기존 결과 디렉토리에서 실패 항목만 재실행
./run.sh run --resume results/<env>/<run_id> --retry-failed

# 기존 결과 디렉토리에서 report 재생성
python3 -m benchmark report results/<env>/<run_id>

# 전체 결과로 dashboard 재생성
python3 -m benchmark dashboard results
```

### 11.2 측정 Protocol — 주요 Parameter

| Parameter | 값 |
|-----------|-----|
| Protocol 버전 | v1 (thermal mode: steady) |
| Throughput 측정 시간 | 30초 |
| Latency loop 수 | 300 loops (single-core, synchronous) |
| Throughput 반복 | 3 |
| End-to-end 반복 | 3 |
| Warm-up run | 1 (버림) |
| Multi-stream per-channel threshold | 30 fps |
| Stable-capacity rule | status ok + 모든 run 완료 + per-channel FPS ≥ 30 |
| Thermal hot-start block | 60 °C (초과 시 run 거부) |
| Cooldown 지점 | model × ORT cell 시작 시 1회 + E2E 단계 직전 1회 (protocol v1) |
| Cooldown 목표 | min(idle + 10 °C, 55 °C) |
| Video 입력 | Full HD (1920×1080), 30 fps |

> **출처:** 각 run `environment.json`의 `protocol` block.

### 11.3 환경별 상세 결과 (현재 release)

각 환경 v2.4.0 run의 전체 machine-readable 결과는 다음과 같다.

| 환경 | Report |
|------|--------|
| BIOSTAR_H1-Quattro | [`results/BIOSTAR_H1-Quattro/20260722_151413/REPORT.md`](../results/BIOSTAR_H1-Quattro/20260722_151413/REPORT.md) |
| DX-AIPlayer-N97_M1 | [`results/DX-AIPlayer-N97_M1/20260722_151104/REPORT.md`](../results/DX-AIPlayer-N97_M1/20260722_151104/REPORT.md) |
| OrangePi5+_M1 | [`results/OrangePi5+_M1/20260722_165355/REPORT.md`](../results/OrangePi5+_M1/20260722_165355/REPORT.md) |
| ROCK5B+_M1 | [`results/ROCK5B+_M1/20260722_080528/REPORT.md`](../results/ROCK5B+_M1/20260722_080528/REPORT.md) |
| RPi5B_M1 | [`results/RPi5B_M1/20260722_150437/REPORT.md`](../results/RPi5B_M1/20260722_150437/REPORT.md) |
| RPi5B_M1M | [`results/RPi5B_M1M/20260723_142408/REPORT.md`](../results/RPi5B_M1M/20260723_142408/REPORT.md) |

각 환경은 `results/<env>/` 아래에 v2.3.3 run도 보유한다. interactive
dashboard([`results/dashboard/index.html`](../results/dashboard/index.html))에서 환경 /
버전 / task / size / ORT mode의 모든 조합을 비교할 수 있다.

### 11.4 용어집

| 용어 | 의미 |
|------|------|
| **Backpressure** | GStreamer pipeline에서 하류 element의 처리 지연이 non-leaky queue를 통해 상류로 전파되어 전체 처리량과 NPU 공급을 함께 제한하는 현상. 본 측정 pipeline의 모든 queue는 `leaky=no`다 |
| **Coefficient of variation** | 표준편차 ÷ 평균을 백분율로 표시한 값 — 환경 간 편차를 정량화하는 데 사용 |
| **CPU 구간 (CPU offload)** | 컴파일된 model graph 중 NPU가 실행할 수 없는 부분. YOLO26에서는 NMS와 keypoint/mask decode에 해당한다. ORT ON일 때만 host CPU에서 실행되며, pipeline의 post-processing 단계와는 구분된다. |
| **NPU · ORT · Throughput · Latency · End-to-end FPS · 최대 채널 수** | [§3](#3-무엇을-측정했는가--용어와-방법)에서 정의 |
| **NPU 활용률** | 측정 구간 동안 dxtop이 sampling한 NPU core 평균 사용률(`npu_total_avg_pct`). 값이 낮으면 NPU가 입력을 기다리는 host-bound 상태를 의미한다 |
| **Thermal throttling** | 고온에서의 NPU clock 하강 (NPU가 1000 MHz에서 clock을 낮춤) |

---

*본 보고서는 `dx-benchmark` tool이 commit한 측정
데이터([`dx-benchmark/results/`](../results/))로부터 작성되었다. 기저 수치를 재생성하거나
interactive하게 탐색하려면 [§11.1](#111-벤치마크-재현)과 dashboard를 참고한다.*
