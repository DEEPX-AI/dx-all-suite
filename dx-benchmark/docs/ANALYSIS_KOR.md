# YOLO26 × DEEPX NPU — Benchmark 분석

> **이 보고서가 다루는 질문.** YOLO26 task와 model size별로 DEEPX NPU가 host system마다 어느 정도의
> inference throughput을 내는지, 그리고 video application이 실제로 얻는 E2E FPS와 최대 채널 수는
> 얼마인지 다룬다. 그 차이를 만드는 host 측 요인(video decoding, CPU, PCIe link, 냉각, 메모리)과,
> 목표 workload에 맞는 host와 NPU module을 고르는 기준도 정리한다.
>
> **데이터.** dx-all-suite **v2.5.0**, host + NPU 환경 6개, YOLO26 task 5개 × model size 5개.
> 모든 cell은 ONNX Runtime ON과 OFF로 각각 측정했다. 모든 수치는 [`results/`](../results/) 아래
> run별 결과 파일에서 다시 계산할 수 있고, [dashboard](https://deepx-ai.github.io/dx-all-suite/dx-benchmark/)에서도
> 볼 수 있다.

---

## 목차

1. [요약](#1-요약)
2. [구성 선택](#2-구성-선택)
3. [Inference throughput](#3-inference-throughput)
4. [Inference latency](#4-inference-latency)
5. [Video pipeline: E2E FPS와 최대 채널 수](#5-video-pipeline-e2e-fps와-최대-채널-수)
6. [Host 측 제한 요인](#6-host-측-제한-요인)
7. [ORT mode 선택](#7-ort-mode-선택)
8. [측정 방법과 한계](#8-측정-방법과-한계)
9. [부록](#9-부록)

**이 보고서의 지표.** Model 수준 수치와 video pipeline 수치를 구분하며, 어느 쪽인지 항상 지표
이름으로 밝힌다(정의: [§8.3](#83-측정-지표와-절차)).

| 지표 | 수준 | 의미 |
|------|------|------|
| **Inference throughput** (FPS) | Model | NPU에 입력을 최대한 빠르게 넣었을 때 초당 처리하는 frame 수(`dxrun`, 비동기, video 없음). Complete model(ORT ON) 기준으로 제시 |
| **Inference latency** (ms) | Model | 요청을 하나씩 보낼 때 frame 1개가 model을 통과하는 시간 |
| **E2E FPS** | Video pipeline | 1920×1080 30 fps H.264 stream 1개가 GStreamer pipeline 전체(decode → pre-process → NPU → post-process)를 통과하는 frame rate. NPU 관련 단계는 DX-Stream element(`dxpreprocess`, `dxinfer`, `dxpostprocess`)로 구성 |
| **합산 E2E FPS** | Video pipeline | 동시에 처리하는 모든 stream의 E2E FPS 합 |
| **최대 채널 수** | Video pipeline | 모든 stream이 30 fps 이상을 유지하는 1920×1080 30 fps stream의 최대 동시 처리 수 |

**Model size.** YOLO26은 **n**(nano), **s**(small), **m**(medium), **l**(large), **x**(extra-large)
다섯 가지 size가 있다. Size가 클수록 정확도가 높고 frame당 NPU 시간이 더 든다. 이 보고서는 size n과
s를 *경량 model*, size l과 x를 *대형 model*이라 부른다. 표에서는 size를 n…x로 표기하고, 본문에서는
"size n" 또는 "YOLO26-n"처럼 model 이름으로 쓴다.

**ORT ON / OFF.** Compile된 YOLO26 model은 graph 일부(*CPU part*)를 host에서 실행한다. ORT ON은
inference 호출 안에서 ONNX Runtime으로 CPU part를 실행해 complete model의 출력을 돌려준다. ORT OFF는
NPU raw tensor를 돌려주고, GStreamer pipeline에서는 `dxpostprocess` element가 DX-Stream
post-processing library로 CPU part를 계산한다. 따라서 두 mode의 최종 검출 결과는 같다. Inference
throughput과 latency는 ORT ON 기준으로 제시하고, E2E FPS와 최대 채널 수는 두 mode를 비교한다.

---

## 1. 요약

### 1.1 YOLO26-n의 E2E FPS와 최대 채널 수

가장 작은 model인 YOLO26-n으로 1920×1080 30 fps H.264 video를 처리할 때 환경별 single-stream E2E
FPS와 최대 채널 수다. 더 큰 model의 E2E FPS는 이보다 같거나 낮다. 모든 size의 결과는
[§5](#5-video-pipeline-e2e-fps와-최대-채널-수)에 있다.

**표 1. YOLO26-n (nano): single-stream E2E FPS / 채널당 30 fps 기준 최대 채널 수 (사용한 ORT mode),
dx-all-suite v2.5.0.** 입력: 1920×1080 30 fps H.264.

| 환경 | Object Detection | Pose Estimation | Segmentation | Oriented Bounding Box | Classification (FPS) |
|------|------------------|-----------------|--------------|-----------------------|----------------------|
| **BIOSTAR_H1-Quattro** | 493.6 / 17 (ON) | 554.6 / 20 (OFF) | 359.1 / 11 (ON) | 394.6 / 14 (ON) | 809.7 |
| **DX-AIPlayer-N97_M1** | 178.0 / 6 (OFF) | 192.2 / 7 (OFF) | 106.5 / 3 (OFF) | 105.3 / 3 (OFF) | 276.7 |
| **OrangePi5+_M1** | 149.2 / 4 (ON) | 248.0 / 8 (OFF) | 100.8 / 3 (ON) | 104.7 / 3 (OFF) | 1086.4 |
| **ROCK5B+_M1** | 140.7 / 4 (ON) | 227.5 / 8 (OFF) | 87.9 / 2 (ON) | 105.4 / 3 (OFF) | 972.9 |
| **RPi5B_M1** | 80.0 / 2 (OFF) | 113.5 / 3 (OFF) | 55.5 / 1 (OFF) | 82.7 / 2 (OFF) | 189.7 |
| **RPi5B_M1M** | 79.5 / 2 (OFF) | 112.0 / 3 (OFF) | 54.9 / 1 (OFF) | 74.0 / 2 (OFF) | 192.8 |

> 각 cell의 두 값은 같은 ORT mode에서 측정한 값이다. 최대 채널 수가 많은 mode를 고르고, 같으면
> single-stream E2E FPS가 높은 mode를 고른다. Classification은 multi-stream 측정 대상이 아니므로 두
> mode 중 높은 single-stream E2E FPS만 표시한다. 출처: 각 v2.5.0 run의 `pipeline_results.json`,
> `multi_stream_results.json`.

### 1.2 핵심 발견

1. **대형 model(size l, x)의 inference throughput은 host와 관계없이 같다.**
   NPU가 병목이고, frame마다 host가 하는 작업은 NPU가 frame 하나를 처리하는 시간 안에 끝나기
   때문이다. → [§3](#3-inference-throughput)

2. **Inference throughput은 NPU module에 비례한다.**
   M1 chip 4개를 탑재한 H1-Quattro card는 M1 하나의 약 4배다. Memory가 느리고 작은 하위 module인
   M1M은 M1의 0.72–0.82배다. → [§3](#3-inference-throughput)

3. **경량 model(size n, s)의 E2E FPS는 NPU가 아니라 host가 정한다.**
   NPU는 경량 model의 frame을 몇 ms 만에 처리하므로, host의 decoding, pre-processing,
   post-processing이 속도를 정한다. Size n에서는 stream 1개가 NPU를 절반도 쓰지 못한다.
   → [§5.1](#51-task별-결과)

4. **Host의 첫 번째 요건은 hardware video decoder다.**
   Hardware decoder가 없으면 H.264 decoding이 pipeline의 다른 작업과 CPU를 나눠 써야 한다. 같은 M1으로
   YOLO26-n detection을 처리할 때 Raspberry Pi 5는 2채널, hardware decoder가 있는 host는 4–6채널이다.
   → [§6.1](#61-video-decoding)

5. **대형 model의 지속 E2E FPS는 냉각이 정한다.**
   NPU가 뜨거워지면 clock을 낮추고(thermal throttling) E2E FPS도 함께 떨어진다. 발열 제약이 가장 큰
   board에서는 size x의 E2E FPS가 inference throughput의 57%까지 내려간다.
   → [§6.4](#64-발열과-냉각)

6. **ORT mode는 host마다 측정해서 고른다.**
   두 mode의 출력은 같지만 CPU part를 계산하는 software가 다르고, 어느 쪽이 빠른지는 host CPU에 따라
   달라진다. → [§7](#7-ort-mode-선택)

---

## 2. 구성 선택

추천 구성은 측정한 6개 환경 안에서만 골랐으며, 모두 측정 결과를 근거로 한다.

**표 2. 요구 사항별 추천 구성 (dx-all-suite v2.5.0, 1920×1080 30 fps H.264, 채널당 30 fps 기준
최대 채널 수).**

| 요구 사항 | 추천 구성 | 근거 |
|-----------|-----------|------|
| Detection, pose, segmentation 10채널 이상 | x86 host + **H1-Quattro** | Size n에서 detection / pose / segmentation 17 / 20 / 11채널, size m에서 detection 16채널([§5](#5-video-pipeline-e2e-fps와-최대-채널-수)) |
| 경량 model(size n, s)로 3–8채널 | Hardware video decoder가 있는 host(Intel N97, RK3588) + **M1** | Size n에서 detection 4–6채널, pose 7–8채널([§5](#5-video-pipeline-e2e-fps와-최대-채널-수)) |
| 대형 model(size l, x) | 측정한 어느 host든 + **M1**, 충분한 냉각 | Inference throughput은 host와 관계없이 같다([§3](#3-inference-throughput)). 지속 E2E FPS는 thermal throttling이 일어날 때만 떨어진다([§6.4](#64-발열과-냉각)) |
| 최저 system 비용으로 1–2채널 | **Raspberry Pi 5 + M1** | Size n–l에서 detection 2채널, size n–m에서 pose 3채널. Software decoding이 한계([§6.1](#61-video-decoding)) |
| 하위 등급 NPU module | **M1M** — inference throughput은 M1의 0.72–0.82×, 메모리는 절반 | `RPi5B_M1M`: detection은 size n과 s에서 2채널, m과 l에서 1채널, x에서 0채널([§3](#3-inference-throughput), [§6.5](#65-메모리)) |

**Host checklist.** Host에서 확인할 요소이며, 측정된 영향이 큰 순서다.

1. **Hardware video decoder.** Software decoding은 pipeline의 다른 작업과 같은 CPU를 써서, NPU와
   관계없이 E2E FPS를 제한하기 때문이다. Raspberry Pi 5에서는 size n부터 l까지 detection E2E FPS가 약
   80 fps(2채널)에 머물지만, hardware decoder가 있는 host는 size n에서 detection 4–6채널을
   처리한다([§6.1](#61-video-decoding)).
2. **냉각.** NPU가 thermal limit에 닿으면 clock을 공칭 1000 MHz 아래로 낮추고(thermal throttling),
   E2E FPS도 함께 떨어지기 때문이다. 지속 부하에서 clock은
   300 MHz까지 내려갔고, 발열 제약이 가장 큰 board에서는 size x의 E2E FPS가 inference throughput의
   57%까지 떨어졌다([§6.4](#64-발열과-냉각)).
3. **CPU.** ORT ON에서는 model의 CPU part가 frame마다 host에서 실행되어, 경량 model에서는 CPU가
   inference throughput을 제한하기 때문이다. Size n에서 inference throughput은 NPU만의 수치의 53–58%(ARM
   host), 75–76%(x86)다([§6.2](#62-host-cpu와-model의-cpu-part)).
4. **PCIe link 폭**(lane 수: Gen3 ×1, Gen3 ×2, Gen3 ×4). 좁은 link는 경량 640×640 model을 제한할 수 있기
   때문이다. PCIe connector가 lane 1개(Gen3 ×1)인 Raspberry Pi 5는 size n에서 detection과 segmentation의 NPU만의 inference throughput이 39–47% 낮았다. 다만 이 host에서는
   CPU와 software decoding이 먼저 한계에 닿았으므로, lane 2개 이상(Gen3 ×2 이상)의 link는 측정된 이득이 아니라
   여유분이다([§6.3](#63-pcie-link-폭)).
5. **Host RAM.** 채널이 늘 때마다 pipeline 메모리가 늘어나기 때문이다(채널당 중앙값 약 32 MiB).
   채널이 많은 system은 NPU와 함께 host RAM도 산정해야 한다([§6.5](#65-메모리)).

---

## 3. Inference throughput

Inference throughput은 NPU에 입력을 최대한 빠르게 넣었을 때 **complete model**(ORT ON)이 초당
처리하는 frame 수이며, video decoding은 포함하지 않는다. 해당 host에서 application이 얻을 수 있는
상한이다.

**표 3. Inference throughput (FPS), complete model (ORT ON), dx-all-suite v2.5.0.** 입력:
640×640(detection, pose, segmentation), 1024×1024(oriented bounding box), 224×224(classification).

| Task | 환경 | n | s | m | l | x |
|------|------|--:|--:|--:|--:|--:|
| Object detection | BIOSTAR_H1-Quattro | 1058.1 | 823.5 | 511.3 | 375.0 | 200.8 |
| Object detection | DX-AIPlayer-N97_M1 | 244.0 | 199.5 | 123.6 | 90.8 | 48.8 |
| Object detection | OrangePi5+_M1 | 178.3 | 179.9 | 123.1 | 90.3 | 48.8 |
| Object detection | ROCK5B+_M1 | 157.5 | 149.2 | 123.3 | 90.6 | 48.9 |
| Object detection | RPi5B_M1 | 104.2 | 104.7 | 104.7 | 90.8 | 48.9 |
| Object detection | RPi5B_M1M | 102.3 | 102.2 | 85.3 | 67.2 | 37.1 |
| Pose estimation | BIOSTAR_H1-Quattro | 1277.1 | 752.4 | 499.0 | 367.6 | 195.1 |
| Pose estimation | DX-AIPlayer-N97_M1 | 303.8 | 183.9 | 122.6 | 89.3 | 47.5 |
| Pose estimation | OrangePi5+_M1 | 284.4 | 184.6 | 122.2 | 88.7 | 47.6 |
| Pose estimation | ROCK5B+_M1 | 246.4 | 169.0 | 122.0 | 89.0 | 47.6 |
| Pose estimation | RPi5B_M1 | 151.8 | 150.8 | 122.5 | 89.2 | 47.6 |
| Pose estimation | RPi5B_M1M | 146.2 | 141.1 | 90.8 | 66.9 | 36.2 |
| Segmentation | BIOSTAR_H1-Quattro | 561.0 | 573.1 | 320.6 | 269.4 | 141.2 |
| Segmentation | DX-AIPlayer-N97_M1 | 138.1 | 134.7 | 77.1 | 64.9 | 34.3 |
| Segmentation | OrangePi5+_M1 | 131.3 | 132.8 | 77.3 | 64.4 | 34.1 |
| Segmentation | ROCK5B+_M1 | 104.6 | 99.8 | 76.3 | 64.7 | 34.4 |
| Segmentation | RPi5B_M1 | 67.5 | 68.3 | 67.7 | 64.9 | 34.4 |
| Segmentation | RPi5B_M1M | 65.9 | 66.0 | 57.2 | 48.6 | 27.2 |
| Oriented bounding box | BIOSTAR_H1-Quattro | 453.9 | 265.8 | 179.4 | 129.7 | 71.2 |
| Oriented bounding box | DX-AIPlayer-N97_M1 | 107.1 | 64.1 | 42.4 | 31.0 | 17.0 |
| Oriented bounding box | OrangePi5+_M1 | 106.3 | 63.8 | 42.5 | 30.9 | 17.0 |
| Oriented bounding box | ROCK5B+_M1 | 107.1 | 63.4 | 41.5 | 30.8 | 17.0 |
| Oriented bounding box | RPi5B_M1 | 107.2 | 62.7 | 42.5 | 31.0 | 17.0 |
| Oriented bounding box | RPi5B_M1M | 75.2 | 45.5 | 29.2 | 22.3 | 12.7 |
| Classification | BIOSTAR_H1-Quattro | 14280.3 | 7989.3 | 5657.2 | 3598.6 | 2017.2 |
| Classification | DX-AIPlayer-N97_M1 | 3512.5 | 1958.0 | 1381.8 | 888.2 | 496.5 |
| Classification | OrangePi5+_M1 | 3383.9 | 1912.8 | 1363.0 | 874.2 | 492.9 |
| Classification | ROCK5B+_M1 | 3483.0 | 1967.8 | 1379.9 | 886.0 | 496.4 |
| Classification | RPi5B_M1 | 3460.3 | 1896.1 | 1352.0 | 870.6 | 494.7 |
| Classification | RPi5B_M1M | 2877.2 | 1516.0 | 1057.7 | 712.0 | 384.8 |

> 출처: `model_results.json`, family = throughput, ORT ON. NPU를 냉각한 뒤 시작한 30초 run 3회의 평균.

**표 4. Size l과 x에서 NPU module별 inference throughput 비교, ORT ON, v2.5.0.**

| Task | M1 host 4대 간 편차 (최대 CV) | H1-Quattro ÷ M1 | M1M ÷ M1 (같은 Raspberry Pi 5 host 종류) |
|------|:-----------------------------:|:---------------:|:----------------------------------------:|
| Object detection | 0.2 % | 4.11–4.14× | 0.74–0.76× |
| Pose estimation | 0.2 % | 4.10–4.13× | 0.75–0.76× |
| Segmentation | 0.3 % | 4.12–4.16× | 0.75–0.79× |
| Oriented bounding box | 0.2 % | 4.18–4.20× | 0.72–0.75× |
| Classification | 0.8 % | 4.07–4.09× | 0.78–0.82× |

> CV = single-M1 host 4대 값의 모표준편차 ÷ 평균이며, size l과 x 중 큰 값이다. H1-Quattro는
> `BIOSTAR_H1-Quattro`를 single-M1 host 4대 평균으로 나눈 값이다. M1M ÷ M1은 `RPi5B_M1M`을
> `RPi5B_M1`로 나눈 값이다.

**해석.**

- **Size l 이상에서는 host가 결과를 바꾸지 않는다.** Single-M1 host 4대의 값이 모든 task에서 0.8%
  이내로 같다. NPU가 병목이기 때문이다. NPU 사용률은 90–96%이고, CPU part(frame당 1–6 ms)는 NPU의
  frame당 처리 시간(11–59 ms) 안에 끝난다. 대부분의 host는 size m에서 이미 NPU가 병목이지만, Raspberry
  Pi 5는 detection과 segmentation에서 아직 그렇지 않다(YOLO26-m detection: 104.7 fps, 다른 host
  123.1–123.6 fps).
- **Size n과 s에서는 host가 inference throughput을 정한다.** 같은 M1이라도 YOLO26-n detection에서 Intel N97
  box는 244.0 fps, Raspberry Pi 5는 104.2 fps다. Host가 frame마다 model의 CPU part를 실행하기
  때문이다([§6.2](#62-host-cpu와-model의-cpu-part)). 이 구간은 대상 host의 값을 봐야 한다.
- **H1-Quattro는 inference throughput을 4배로 늘린다.** `dxrun`이 inference를 chip 4개에 나눠 single-M1
  평균의 4.07–4.20×가 된다.
- **M1M은 clock이 아니라 memory가 다르다.** 두 module 모두 1000 MHz로 동작하고, M1M은
  LPDDR4(4200 Mbps, 1.92 GiB), M1은 LPDDR5(5600 Mbps, 3.92 GiB)를 쓴다. 이 비율에는 서로 다른 두
  Raspberry Pi 5 unit의 차이도 섞여 있다([§8.4](#84-한계)).

---

## 4. Inference latency

Inference latency는 **frame 1개**가 model을 통과하는 시간이며, NPU core 1개에서 동기 방식으로
측정한다(`dxrun`, 300 loop). 응답성을 나타내는 지표이며 inference throughput과는 다르다.

**표 5. YOLO26 object detection inference latency (ms), complete model (ORT ON), v2.5.0.**

| 환경 | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 10.89 | 16.99 | 24.19 | 31.52 | 57.26 |
| DX-AIPlayer-N97_M1 | 24.39 | 30.70 | 38.52 | 45.98 | 71.11 |
| OrangePi5+_M1 | 37.84 | 47.32 | 58.31 | 88.27 | 116.47 |
| ROCK5B+_M1 | 28.67 | 43.96 | 51.45 | 61.81 | 96.80 |
| RPi5B_M1 | 25.18 | 30.19 | 38.46 | 44.85 | 71.25 |
| RPi5B_M1M | 25.39 | 32.38 | 42.37 | 48.88 | 77.62 |

> 출처: `model_results.json`의 `total_ms`, family = latency, ORT ON. Cell마다 warm-up run을 한 번
> 버린 뒤 300-loop run 1회.

- **Inference throughput과 달리 inference latency는 host에 따라 다르다.** 같은 M1에서 YOLO26-n은
  Intel N97 box에서 24.4 ms, Raspberry Pi 5에서 25.2 ms, RK3588 board에서 28.7–37.8 ms다.
  `BIOSTAR_H1-Quattro`는 모든 size에서 가장 짧다.
- **CPU part는 x86에서 0.31–1.36 ms, ARM에서 2.31–5.79 ms를 더한다**(object detection, size n, m, x).
  RK3588 board에서는 process가 어느 CPU core에 배치되느냐에 따라 latency가 달라지기도
  한다([§8.4](#84-한계)).
- **Inference latency로 inference throughput을 환산할 수 없다.** Intel N97 box에서 YOLO26-n
  detection은 24.4 ms가 걸리지만 inference throughput은 244.0 fps로, 1 ÷ 24.4 ms ≈ 41 fps보다
  훨씬 높다. 여러 frame을 동시에 처리하기 때문이다. 시스템 산정에는 [§3](#3-inference-throughput)과
  [§5](#5-video-pipeline-e2e-fps와-최대-채널-수)를 쓴다.

---

## 5. Video pipeline: E2E FPS와 최대 채널 수

### 5.1 Task별 결과

각 cell의 형식: **single-stream E2E FPS / 채널당 30 fps 기준 최대 채널 수 (ORT mode)**. 두 값은 같은
mode에서 측정한 값이다. 최대 채널 수가 많은 mode를 고르고, 같으면 single-stream E2E FPS가 높은
mode를 고른다. 입력: 1920×1080 30 fps H.264, dx-all-suite v2.5.0.

**표 6. Object detection (640×640).**

| 환경 | n | s | m | l | x |
|------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 493.6 / 17 (ON) | 492.9 / 17 (ON) | 491.7 / 16 (ON) | 376.8 / 12 (ON) | 201.1 / 6 (ON) |
| DX-AIPlayer-N97_M1 | 178.0 / 6 (OFF) | 165.1 / 5 (OFF) | 117.1 / 3 (ON) | 91.1 / 2 (OFF) | 49.0 / 1 (OFF) |
| OrangePi5+_M1 | 149.2 / 4 (ON) | 127.1 / 4 (ON) | 99.2 / 3 (ON) | 90.4 / 2 (OFF) | 48.8 / 1 (OFF) |
| ROCK5B+_M1 | 140.7 / 4 (ON) | 132.8 / 4 (ON) | 113.8 / 2 (ON) | 89.8 / 2 (ON) | 39.6 / 1 (ON) |
| RPi5B_M1 | 80.0 / 2 (OFF) | 80.2 / 2 (OFF) | 80.2 / 2 (OFF) | 80.4 / 2 (OFF) | 49.0 / 1 (OFF) |
| RPi5B_M1M | 79.5 / 2 (OFF) | 80.2 / 2 (OFF) | 75.4 / 1 (OFF) | 53.1 / 1 (OFF) | 21.8 / 0 (OFF) |

**표 7. Pose estimation (640×640).**

| 환경 | n | s | m | l | x |
|------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 554.6 / 20 (OFF) | 554.1 / 20 (OFF) | 501.9 / 16 (ON) | 366.7 / 12 (OFF) | 195.7 / 6 (OFF) |
| DX-AIPlayer-N97_M1 | 192.2 / 7 (OFF) | 179.1 / 5 (OFF) | 121.2 / 3 (OFF) | 89.4 / 2 (OFF) | 47.8 / 1 (ON) |
| OrangePi5+_M1 | 248.0 / 8 (OFF) | 174.6 / 5 (OFF) | 119.8 / 3 (OFF) | 89.4 / 2 (OFF) | 47.3 / 1 (OFF) |
| ROCK5B+_M1 | 227.5 / 8 (OFF) | 180.0 / 5 (OFF) | 121.2 / 2 (OFF) | 89.5 / 2 (OFF) | 39.1 / 1 (OFF) |
| RPi5B_M1 | 113.5 / 3 (OFF) | 113.8 / 3 (OFF) | 110.6 / 3 (OFF) | 89.3 / 2 (OFF) | 47.7 / 1 (OFF) |
| RPi5B_M1M | 112.0 / 3 (OFF) | 111.9 / 3 (OFF) | 70.7 / 1 (OFF) | 53.0 / 1 (OFF) | 20.3 / 0 (ON) |

**표 8. Segmentation (640×640).**

| 환경 | n | s | m | l | x |
|------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 359.1 / 11 (ON) | 361.2 / 11 (ON) | 316.9 / 8 (OFF) | 268.0 / 8 (ON) | 141.6 / 4 (ON) |
| DX-AIPlayer-N97_M1 | 106.5 / 3 (OFF) | 97.4 / 3 (OFF) | 76.3 / 1 (OFF) | 64.5 / 1 (OFF) | 30.5 / 1 (OFF) |
| OrangePi5+_M1 | 100.8 / 3 (ON) | 88.1 / 2 (ON) | 76.7 / 1 (OFF) | 63.5 / 1 (OFF) | 26.1 / 0 (OFF) |
| ROCK5B+_M1 | 87.9 / 2 (ON) | 81.0 / 2 (ON) | 65.5 / 1 (OFF) | 54.8 / 1 (OFF) | 19.6 / 0 (OFF) |
| RPi5B_M1 | 55.5 / 1 (OFF) | 55.1 / 1 (OFF) | 54.5 / 1 (OFF) | 53.4 / 1 (OFF) | 34.1 / 1 (OFF) |
| RPi5B_M1M | 54.9 / 1 (OFF) | 54.9 / 1 (OFF) | 34.1 / 1 (ON) | 28.2 / 0 (ON) | 13.6 / 0 (ON) |

**표 9. Oriented bounding box (1024×1024).**

| 환경 | n | s | m | l | x |
|------|---|---|---|---|---|
| BIOSTAR_H1-Quattro | 394.6 / 14 (ON) | 263.4 / 8 (ON) | 176.1 / 5 (ON) | 130.1 / 4 (OFF) | 71.2 / 2 (OFF) |
| DX-AIPlayer-N97_M1 | 105.3 / 3 (OFF) | 63.5 / 2 (OFF) | 42.3 / 1 (OFF) | 31.0 / 1 (OFF) | 14.6 / 0 (ON) |
| OrangePi5+_M1 | 104.7 / 3 (OFF) | 62.9 / 2 (OFF) | 41.8 / 1 (OFF) | 30.9 / 1 (OFF) | 14.4 / 0 (ON) |
| ROCK5B+_M1 | 105.4 / 3 (OFF) | 62.9 / 2 (ON) | 38.9 / 1 (ON) | 26.1 / 0 (ON) | 11.0 / 0 (ON) |
| RPi5B_M1 | 82.7 / 2 (OFF) | 63.0 / 2 (OFF) | 42.2 / 1 (OFF) | 31.1 / 1 (ON) | 16.9 / 0 (ON) |
| RPi5B_M1M | 74.0 / 2 (OFF) | 45.9 / 1 (OFF) | 22.1 / 0 (ON) | 14.5 / 0 (OFF) | 7.3 / 0 (ON) |

> 표 6–9 출처: 각 v2.5.0 run의 `pipeline_results.json`(single-stream E2E FPS)과
> `multi_stream_results.json`(최대 채널 수: 모든 run이 완료되고 모든 stream이 30 fps 이상인 최대
> stream 수). E2E와 multi-stream은 지속 부하에서 측정한 값이다([§6.4](#64-발열과-냉각)).

**표 읽는 법.**

- **경량 model(size n, s): host가 E2E FPS를 정한다.** M1 하나로 size n의 detection 최대 채널 수는 2(Raspberry
  Pi 5, software decoding)부터 6(Intel N97)까지다. H1-Quattro는 17채널로, 가장 좋은 single-M1 host의
  4배가 아니라 약 3배다. Size n에서 single-stream pipeline이 NPU를 21%만 쓰기 때문이다(표 10).
- **어느 지점까지는 model을 키워도 E2E FPS가 줄지 않는다.** Host가 pipeline을 제한하는 구간에서는
  model이 커져도 E2E FPS가 그대로다. Detection E2E FPS는 `BIOSTAR_H1-Quattro`에서 size n부터
  m까지(493.6 → 491.7 fps), `RPi5B_M1`에서 size n부터 l까지(80.0 → 80.4 fps) 거의 같다.
- **대형 model(size l, x): NPU와 냉각이 E2E FPS를 정한다.** Single-M1 host에서 detection과 pose의 E2E
  FPS는 size l에서 89–91, size x에서 47–49로 모인다. 예외는 NPU가 throttling한 경우([§6.4](#64-발열과-냉각))와
  software decoding이 여전히 E2E FPS를 제한하는 경우(`RPi5B_M1`, YOLO26-l detection: 80.4 fps)다.
- **Segmentation과 oriented bounding box가 가장 무거운 pipeline이다.** size x에서 2채널 이상을 처리하는
  환경은 `BIOSTAR_H1-Quattro`뿐이고, size x의 oriented bounding box는 어떤 single-M1 host도 stream
  1개를 30 fps로 유지하지 못한다.

**표 10. Single-stream pipeline의 NPU 사용률, YOLO26 object detection, 표 6와 같은 mode,
v2.5.0.**

| 환경 | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 21 % | 38 % | 67 % | 73 % | 84 % |
| DX-AIPlayer-N97_M1 | 42 % | 74 % | 87 % | 90 % | 94 % |
| OrangePi5+_M1 | 38 % | 58 % | 74 % | 90 % | 93 % |
| ROCK5B+_M1 | 36 % | 59 % | 82 % | 90 % | 94 % |
| RPi5B_M1 | 18 % | 34 % | 55 % | 80 % | 94 % |
| RPi5B_M1M | 22 % | 41 % | 83 % | 94 % | 95 % |

> 출처: `pipeline_results.json`의 `npu_total_avg_pct`, task = object_detection.

Size n에서 NPU 사용률은 모든 환경에서 18–42%다. Host pipeline(decode → pre-process → post-process)이
stream 1개로는 NPU를 다 채우지 못해, 나머지 NPU 시간은 쓰이지 않는다.

### 5.2 Single-stream E2E FPS로 최대 채널 수 추정하기

최대 채널 수 = ⌊N개 stream의 합산 E2E FPS ÷ 30⌋이고, 합산 E2E FPS는 single-stream E2E FPS와 비슷하다
(YOLO26-n detection에서 모든 환경이 −1%에서 +8% 범위).
따라서 single-stream 측정만으로도 좋은 추정치를 얻을 수 있으며, 120개 cell 중 98개에서 정확하다.

**표 11. 측정한 최대 채널 수 − ⌊single-stream E2E FPS ÷ 30⌋, cell 120개(환경 6개 × video task 4개 ×
Size 5개), 표 6–9와 같은 mode, v2.5.0.**

| Size | 같음 | +1 | +2 | −1 | −2 |
|:----:|:----:|:--:|:--:|:--:|:--:|
| n | 18 | 5 | 1 | 0 | 0 |
| s | 21 | 1 | 1 | 1 | 0 |
| m | 15 | 0 | 0 | 7 | 2 |
| l | 20 | 0 | 0 | 4 | 0 |
| x | 24 | 0 | 0 | 0 | 0 |

- **Size n과 s: 추정치가 보수적이다.** Stream 하나가 순서대로 처리하는 작업을 여러 stream이 겹쳐 처리할 수
  있으므로, 합산 E2E FPS가 single-stream E2E FPS의 최대 1.21×까지 올라간다(`DX-AIPlayer-N97_M1`,
  YOLO26-n pose: 7채널에서 233.4 fps, single-stream 192.2 fps). 경계값 근처에서는 1%만 늘어도 1채널이 더
  들어간다(`DX-AIPlayer-N97_M1`, YOLO26-n detection: 178.0 fps → 5.93, 측정 6채널).
- **Size m과 l: throttling하는 board에서는 추정치가 낙관적이다.** 추정보다 낮은 13개 cell은 모두
  multi-stream 부하에서 300–600 MHz로 throttling했고, 처음 실패한 stream 수에서 합산 E2E FPS는
  single-stream E2E FPS의 0.58–0.88×로 떨어졌다.
- **Size x: 추정치가 정확하다.**

**실용 규칙:** 최대 채널 수 ≈ ⌊single-stream E2E FPS ÷ 30⌋. 경량 model은 1–2채널 더 나올 수 있고,
냉각 여유가 없는 size m과 l은 1–2채널 적게 잡는다.

---

## 6. Host 측 제한 요인

Video application이 [§3](#3-inference-throughput)의 inference throughput을 그대로 얻는 경우는
드물다. 이 절에서는 그중 얼마가 E2E FPS와 최대 채널 수로 이어지는지를 정하는 host 측 요인을 다룬다.
영향이 큰 순서로 정리한 요약은 [§2](#2-구성-선택)의 host checklist에 있다.

### 6.1 Video decoding

**표 12. Host별 pipeline 상한: YOLO26-cls-n single-stream E2E FPS, 1920×1080 30 fps H.264,
v2.5.0.** 이 classifier는 NPU를 거의 쓰지 않으므로(NPU 사용률 3–12%) 이 E2E FPS는 host의 decoding과
pre-processing이 정한다.

| 환경 | Video decoder | Pipeline 상한 (FPS) | Host CPU 사용률 |
|------|---------------|--------------------:|----------------:|
| OrangePi5+_M1 | mppvideodec (HW) | 1086.4 | 176 % / 800 % |
| ROCK5B+_M1 | mppvideodec (HW) | 972.9 | 150 % / 800 % |
| BIOSTAR_H1-Quattro | vaapidecodebin (HW) | 809.7 | 37 % / 1200 % |
| DX-AIPlayer-N97_M1 | vah264dec (HW) | 276.7 | 86 % / 400 % |
| RPi5B_M1M | avdec_h264 (SW) | 192.8 | 287 % / 400 % |
| RPi5B_M1 | avdec_h264 (SW) | 189.7 | 269 % / 400 % |

> 출처: `pipeline_results.json`의 `avg_e2e_fps`, `decoder`, `avg_cpu_pct`, `npu_total_avg_pct`,
> task = classification, size = n, 두 ORT mode 중 높은 값.

- **Raspberry Pi 5에서는 software decoding이 CPU 대부분을 쓴다.** ~190 fps에서 decoder만으로 core
  4개 중 약 270–290%를 쓴다. Detection model에서는 남은 CPU를 post-processing과 나눠 써야 하므로
  `RPi5B_M1`의 E2E FPS는 **Size n부터 l까지 80.0–80.4 fps**에 머문다. 같은 구간에서 inference
  throughput은 size n부터 m까지 104.2–104.7 fps다(표 3). 30 fps detection 2채널은 되지만 3채널은 안 된다.
- **Hardware decoder가 있으면 상한이 올라간다.** RK3588 board와 Ryzen host는 810–1086 fps다. Intel
  N97 box는 CPU가 대부분 쉬는데도 277 fps에 그치므로, 이 상한은 hardware decoder가 정한다.

### 6.2 Host CPU와 model의 CPU part

NPU용으로 compile한 YOLO26 model은 graph 일부(CPU part)를 host에 남긴다. 이 부분은 frame마다 host
CPU에서 실행된다. ORT ON에서는 inference 호출 안에서, ORT OFF에서는 application의
post-processing에서 실행된다. 아래 비율은 이 host 작업이 inference throughput을 얼마나 줄이는지
보여준다. NPU만의 inference throughput(ORT OFF)은 여기서 기준값으로만 쓴다.

**표 13. Inference throughput 비율, complete model (ORT ON) ÷ NPU만 (ORT OFF), YOLO26 object
detection, v2.5.0.**

| 환경 | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| BIOSTAR_H1-Quattro | 0.76 | 1.00 | 1.00 | 1.00 | 1.00 |
| DX-AIPlayer-N97_M1 | 0.75 | 1.00 | 1.00 | 1.00 | 1.00 |
| OrangePi5+_M1 | 0.55 | 0.90 | 1.00 | 1.00 | 1.00 |
| ROCK5B+_M1 | 0.53 | 0.75 | 1.00 | 1.00 | 1.00 |
| RPi5B_M1 | 0.58 | 0.58 | 0.85 | 1.00 | 1.00 |
| RPi5B_M1M | 0.57 | 0.66 | 1.00 | 1.00 | 1.00 |

> 출처: `model_results.json`, task = object_detection, family = throughput, ORT ON fps ÷
> ORT OFF fps.

- **Size m, l, x에서는 CPU part가 inference throughput을 줄이지 않는다**(비율 1.00). 예외는 `RPi5B_M1`의
  m(0.85)이다.
- **Size n에서 complete model의 inference throughput은 ARM host에서 NPU만의 수치의 약 절반**
  (0.53–0.58), x86에서 약 3/4(0.75–0.76)이다. 이때 inference throughput은 model size와 거의
  관계없다. `RPi5B_M1`은 size n, s, m에서 104.2, 104.7, 104.7 fps다. Frame마다 일정한 host 비용이 든다는
  뜻이다.
- **ORT OFF는 이 비용을 없애지 않고 옮길 뿐이다.** 비용은 application의 post-processing으로
  옮겨지고, E2E FPS에 포함되어 측정된다([§7](#7-ort-mode-선택)).

### 6.3 PCIe link 폭

PCIe link 폭은 host와 NPU module 사이의 lane 수(Gen3 ×1, Gen3 ×2, Gen3 ×4)다. PCIe Gen3 lane 1개는 방향당 약
1 GB/s를 전송하므로, Gen3 ×1 link의 대역폭은 Gen3 ×4 link의 1/4이다. 측정한 host는 Gen3 ×1(Raspberry Pi 5),
Gen3 ×2(Intel N97, `ROCK5B+_M1`), Gen3 ×4(`OrangePi5+_M1`, `BIOSTAR_H1-Quattro`)다.

이 절은 NPU만의 inference throughput(ORT OFF)을 진단용으로 쓴다. Host CPU가 아니라 link가 한계가 될
수 있는 유일한 측정이기 때문이다. 시스템 산정에 쓰는 수치가 아니다.

**표 14. PCIe link별 size n의 NPU만의 inference throughput (FPS), ORT OFF, v2.5.0.**

| 환경 | Link | Object detection | Pose estimation | Segmentation | Oriented bounding box | Classification |
|------|:----:|-----------------:|----------------:|-------------:|----------------------:|---------------:|
| DX-AIPlayer-N97_M1 | Gen3 ×2 | 326.2 | 305.3 | 180.2 | 107.2 | 3521.3 |
| OrangePi5+_M1 | Gen3 ×4 | 324.2 | 305.7 | 164.8 | 107.1 | 3380.0 |
| ROCK5B+_M1 | Gen3 ×2 | 296.6 | 304.8 | 160.4 | 107.2 | 3471.3 |
| RPi5B_M1 | Gen3 ×1 | 179.5 | 264.3 | 95.8 | 106.9 | 3457.9 |

> 출처: `model_results.json`, size = n, family = throughput, ORT OFF. Link는 `environment.json`.

Gen3 ×1 link인 Raspberry Pi 5는 size n의 detection과 segmentation에서 NPU만의 inference throughput이 Gen3 ×2 또는
Gen3 ×4 link host보다 39–47% 낮다. 이때 NPU 사용률은 45%(detection)에 그친다. Oriented bounding
box(1024×1024)와 classification(224×224)은 영향이 없고, size m 이상에서는 link와 관계없이 값이
같다(표 4). 이 결과는 경량 640×640 model에서 link가 한계가 된다는 해석과 맞지만, 같은 host에서 Gen3 ×1과
Gen3 ×4 link를 비교하지 않았으므로 host CPU의 영향과 분리하지는 못했다.

**Raspberry Pi 5에서는 Gen3 ×1 link가 실제 한계가 아니었다.** Complete model로 Raspberry Pi 5의 YOLO26-n detection
inference throughput은 104.2 fps로, link가 처리한 179.5 fps보다 낮다. E2E FPS는 software decoding이
제한한다([§6.1](#61-video-decoding)). 넓은 link는 CPU와 decoder가 먼저 한계에 닿지 않는 host를 위한
여유이며, 이번 측정에서 확인된 이득은 아니다.

### 6.4 발열과 냉각

NPU는 thermal limit에 닿으면 스스로를 보호하기 위해 clock을 공칭 1000 MHz 아래로 낮춘다. 이를
**thermal throttling**이라 하며, clock이 낮아지면 inference throughput과 E2E FPS도 떨어진다. 측정 중
NPU clock이 한 번이라도 1000 MHz 아래로 내려가면 throttling cell로 본다. Throttling cell의 clock은
300–800 MHz까지 내려갔다. Benchmark는 model 수준 측정마다 NPU를
먼저 냉각하므로 inference throughput(표 3)은 냉각 상태의 값이다. 반면 E2E와 multi-stream 단계는
실제 운용 중인 pipeline처럼 연속으로 실행된다.

**표 15. NPU가 throttling한 E2E와 multi-stream cell 수, 최고 NPU 온도, v2.5.0 (모든 task, size, ORT mode).**

| 환경 (v2.5.0) | Throttling cell 수 (E2E) | Throttling cell 수 (multi-stream) | 최고 NPU 온도 |
|---------------|:------------------------:|:---------------------------------:|:-------------:|
| BIOSTAR_H1-Quattro (능동 냉각) | 0 / 50 | 40 / 93 | 87 °C |
| DX-AIPlayer-N97_M1 (능동 냉각) | 4 / 50 | 35 / 82 | 86 °C |
| OrangePi5+_M1 | 8 / 50 | 36 / 76 | 86 °C |
| ROCK5B+_M1 | 21 / 50 | 53 / 77 | 88 °C |
| RPi5B_M1 | 1 / 50 | 7 / 78 | 81 °C |
| RPi5B_M1M | 10 / 50 | 19 / 66 | 96 °C |

> 출처: `model_results.json`, `pipeline_results.json`, `multi_stream_results.json` 모든 행의
> `npu_throttled`, `npu_temp_max_c`. Inference throughput cell 300개 중 throttling한 cell은 없다.

**표 16. Size x의 지속 single-stream E2E FPS를 냉각 상태 inference throughput(ORT ON) 대비 비율로
나타낸 값과, 해당 E2E cell의 최저 NPU clock, v2.5.0.**

| 환경 | Object detection | Pose estimation | Segmentation | Oriented bounding box |
|------|:----------------:|:---------------:|:------------:|:---------------------:|
| BIOSTAR_H1-Quattro | 100 % | 100 % | 100 % | 100 % |
| DX-AIPlayer-N97_M1 | 100 % | 100 % | 89 % (600 MHz) | 86 % (600 MHz) |
| OrangePi5+_M1 | 100 % | 99 % (800 MHz) | 77 % (400 MHz) | 85 % (600 MHz) |
| ROCK5B+_M1 | 81 % (600 MHz) | 82 % (600 MHz) | 57 % (400 MHz) | 65 % (400 MHz) |
| RPi5B_M1 | 100 % | 100 % | 99 % | 99 % |
| RPi5B_M1M | 59 % (300 MHz) | 56 % | 50 % | 58 % |

> [§5](#5-video-pipeline-e2e-fps와-최대-채널-수)에서 사용한 mode의 E2E FPS ÷ 표 3. E2E cell에서
> NPU가 throttling한 경우 clock을 함께 표시했다.

- **NPU가 1000 MHz를 유지하면 대형 model의 E2E FPS는 inference throughput과 같다**
  (`BIOSTAR_H1-Quattro`와 `RPi5B_M1`에서 99–100%, `DX-AIPlayer-N97_M1`은 detection과 pose).
- **`ROCK5B+_M1`은 발열 제약이 가장 큰 board다**(E2E 50개 중 21개, multi-stream 77개 중 53개 cell이
  throttling). YOLO26-x video task 4개 모두에서 thermal throttling으로 NPU clock이 400–600 MHz까지 내려갔고, 그래서 YOLO26-x E2E
  FPS는 inference throughput의 57–82%다. Detection은 39.6 fps로, 다른 single-M1 host의
  48.8–49.0 fps보다 낮다.
- **Throttling은 size m과 l에서 최대 채널 수도 줄인다**
  ([§5.2](#52-single-stream-e2e-fps로-최대-채널-수-추정하기)).
- Size x에서 `RPi5B_M1M`의 E2E FPS는 detection cell에서만 throttling했는데도 inference throughput의
  50–59%에 그친다. 원인은 밝히지 못했다([§8.4](#84-한계)).

### 6.5 메모리

**표 17. 적재된 model 1개가 차지하는 NPU 메모리 (MiB), dx-all-suite v2.5.0.**

| Task | n | s | m | l | x |
|------|--:|--:|--:|--:|--:|
| Object detection | 118 | 152 | 245 | 298 | 529 |
| Pose estimation | 120 | 158 | 257 | 310 | 523 |
| Segmentation | 140 | 178 | 273 | 326 | 561 |
| Oriented bounding box | 243 | 383 | 651 | 799 | 1330 |
| Classification | 5 | 10 | 15 | 20 | 49 |

> 출처: `model_results.json` latency 행의 `npu_model_mem_bytes`(모든 환경에서 같음).

- **NPU 메모리는 stream 수가 늘어도 늘지 않는다.** 모든 stream이 적재된 model 하나를 공유하기
  때문이다. 동시 적재를 제한하는 것은 *서로 다른* model의 개수와 크기다. M1은 3.92 GiB, M1M은
  1.92 GiB를 제공한다. YOLO26-x oriented bounding box model 하나가 1.3 GiB로, M1M의 2/3를 차지한다.
- **Host 메모리는 채널 수에 따라 늘어난다.** v2.5.0 multi-stream run에서 최대 채널 수일 때 pipeline
  메모리(RSS)는 ≈243 MiB에서 ≈1599 MiB까지였고, 채널을 하나 더할 때마다 중앙값 약 32 MiB(90th
  percentile 약 121 MiB)가 늘었다. Single-M1 board에서는 0.75 GiB 미만이었으므로, host RAM을 NPU와
  함께 따져야 하는 것은 채널이 많은 4-chip server뿐이다.

---

## 7. ORT mode 선택

**표 18. Single-stream E2E FPS가 더 높은 ORT mode와 그 차이, size n과 s, v2.5.0.**

| 환경 | Object Detection | Pose Estimation | Segmentation | OBB | Classification |
|------|:----------------:|:---------------:|:------------:|:---:|:--------------:|
| BIOSTAR_H1-Quattro | **ON** (+10.2–10.4 %) | tie | **ON** (+12.6–14.7 %) | tie | tie |
| DX-AIPlayer-N97_M1 | **OFF** (+11.3–18.5 %) | OFF (+12.7–13.1 %) | **OFF** (+12.1–12.7 %) | tie | tie |
| OrangePi5+_M1 | **ON** (+29.2–57.0 %) | OFF (+12.5–22.3 %) | **ON** (+5.9–18.7 %) | OFF (+0.8–8.8 %) | tie |
| ROCK5B+_M1 | **ON** (+38.7–48.7 %) | OFF (+10.8–19.7 %) | **ON** (+5.6–11.2 %) | tie | tie |
| RPi5B_M1 | **OFF** (+17.0–17.6 %) | OFF (+36.2–36.8 %) | **OFF** (+21.3–22.2 %) | OFF (+0.8–17.5 %) | tie |
| RPi5B_M1M | **OFF** (+20.1–20.9 %) | OFF (+39.0–39.9 %) | **OFF** (+24.6–24.7 %) | OFF (+1.8–7.9 %) | tie |

> 출처: `pipeline_results.json`의 `avg_e2e_fps`, size n과 s. 차이 = 높은 E2E FPS ÷ 낮은 E2E FPS − 1.
> "tie": 두 size 모두 차이가 5% 미만. Classification은 CPU part가 없으므로 두 mode가 같다.

- **두 mode의 최종 출력은 같고, CPU part를 실행하는 위치만 다르다.** ORT OFF에서는 `dxinfer` element
  안에서 CPU part를 건너뛰고, DX-Stream post-processing library가 raw tensor로 결과를 계산한다. 어느
  mode의 E2E FPS가 더 높은지는 host에 따라 다르다. `OrangePi5+_M1`(YOLO26-n detection)에서는 ORT OFF가 CPU를
  덜 쓰는데도(800% 중 212% 대 247%) ORT ON의 E2E FPS가 57% 높다(149.2 대 95.0 fps). Software
  decoding이 이미 CPU를 차지하는 Raspberry Pi 5에서는 detection E2E FPS가 ORT OFF에서 17–21% 높다.
- **Size m 이상에서는 어느 mode를 골라도 차이가 작다.** 두 mode 모두 NPU가 병목이다.
- **기능 요건을 먼저 본다.** 원본 ONNX model과 같은 출력이 필요한 application은 ORT ON을 써야 한다.
  둘 다 가능하다면 대상 host에서 두 mode를 모두 측정한다. `./run.sh run`은 두 mode를 함께 기록한다.

---

## 8. 측정 방법과 한계

### 8.1 실험 환경

| 환경 | Host CPU | Arch | RAM | DEEPX NPU | Chip 수 | PCIe link | CPU governor | Video decoder |
|------|----------|:----:|----:|-----------|:-------:|:---------:|:------------:|---------------|
| **BIOSTAR_H1-Quattro** | AMD Ryzen 5 9600X (6-core) | x86_64 | 30.5 GB | H1-Quattro card | 4 | Gen3 ×4 | powersave | vaapidecodebin (HW) |
| **DX-AIPlayer-N97_M1** | Intel N97 (4-core) | x86_64 | 7.5 GB | M1 module | 1 | Gen3 ×2 | powersave | vah264dec (HW) |
| **OrangePi5+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 15.6 GB | M1 module | 1 | Gen3 ×4 | ondemand | mppvideodec (HW) |
| **ROCK5B+_M1** | Rockchip RK3588 (A76/A55) | aarch64 | 7.8 GB | M1 module | 1 | Gen3 ×2 | ondemand | mppvideodec (HW) |
| **RPi5B_M1** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | M1 module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |
| **RPi5B_M1M** | Broadcom BCM2712 (Cortex-A76) | aarch64 | 7.9 GB | **M1M** module | 1 | Gen3 ×1 | ondemand | avdec_h264 (SW) |

> 출처: 각 v2.5.0 `environment.json`의 `host`, `npu`, decoder는 `pipeline_results.json`. 모든
> 환경은 같은 software stack을 썼다: DX-RT v3.5.0, NPU firmware v2.7.6, DX-Stream 3.2.0, DX-COM
> v2.5.0-rc.1로 compile한 model. 모든 NPU module의 공칭 clock은 1000 MHz다.

### 8.2 Workload

- **Model 입력:** object detection,
  pose estimation, segmentation은 640×640, oriented bounding box는 1024×1024, classification은
  224×224.
- **Video:** 1920×1080 30 fps H.264 clip 2개. Detection, pose, segmentation, classification은
  `od_benchmark_video.mp4`(3455 frame), oriented bounding box는 `obb_benchmark_video.mp4`
  (2640 frame)를 쓴다.

### 8.3 측정 지표와 절차

| 지표 | 측정 방법 |
|------|-----------|
| Inference throughput | `dxrun`, 모든 NPU core에서 비동기, 30초, 3회 평균. 매 run은 NPU를 min(idle + 10 °C, 55 °C)까지 냉각한 뒤 시작한다. Buffer count를 sweep해 최적값으로 보고한다. 두 ORT mode 모두 측정하며, ORT ON으로 보고하고 ORT OFF는 진단에만 쓴다. |
| Inference latency | `dxrun`, core 1개에서 동기, 300 loop, warm-up run을 한 번 버린 뒤 1회. |
| E2E FPS | GStreamer pipeline(`gst-launch-1.0`), stream 1개, warm-up 후 연속 3회 평균. 냉각한 NPU에서 시작해 연속으로 실행한다. |
| 최대 채널 수 | E2E 직후(냉각 없이) multi-stream을 실행하며, 어느 stream이든 30 fps 아래로 떨어질 때까지 stream 수를 늘린다. 모든 run이 완료되고 모든 stream이 30 fps 이상이어야 통과다. |
| NPU 사용률, clock, 온도 | 측정 중 `dxtop`으로 sampling. NPU clock이 1000 MHz 아래로 떨어진 cell을 *throttling* cell로 본다. |

Protocol parameter는 [§9.2](#92-측정-protocol--주요-parameter)에 있다.

### 8.4 한계

- **지속 부하 값.** E2E FPS와 최대 채널 수에는 연속 부하에서 도달한 발열 상태가 반영되어 있다. 24/7
  운용에서는 benchmark보다 더 뜨거워질 수 있다. Inference throughput은 냉각 상태 값이므로 연속
  운용의 상한이다.
- **Video format 한 가지.** 1920×1080 H.264만 측정했다. H.265, 다른 해상도, 다른 객체 밀도에서는
  decoding과 post-processing 부하가 달라진다.
- **30 fps 기준.** 최대 채널 수는 채널당 30 fps를 기준으로 한다. 다른 service level은
  `--fps-threshold <fps>`로 다시 측정한다.
- **RK3588 core 배치.** RK3588 board는 빠른 core(A76)와 효율 core(A55)를 함께 쓰며, benchmark는
  process를 특정 core에 고정하지 않는다. 단일 run이 어느 core에든 배치될 수 있어 이 두 host의 run 간
  편차가 가장 크다(inference throughput 최대 3.8%: `ROCK5B+_M1`, YOLO26-n segmentation). 이 두 host의 작은
  차이, 특히 단일 run inference latency 차이는 크게 해석하지 않는다.
- **M1과 M1M은 서로 다른 unit에서 측정했다.** `RPi5B_M1M`은 `RPi5B_M1`(Debian 12, kernel 6.12)과
  다른 Raspberry Pi 5(Debian 13, kernel 6.18)에서 측정했다. M1과 M1M 수치를 평균하지 않는다.
- **Buffer count.** Inference throughput은 `dxrun --max-throughput`이 찾은 최적 buffer
  count(중앙값: size n과 s는 6, m과 l은 5, x는 4)에서의 값이다. 기본값을 쓰는 application은 일부 cell, 주로
  Size n에서 이 값에 못 미칠 수 있다.
- **원인을 밝히지 못한 현상.** Size x에서 `RPi5B_M1M`의 E2E FPS는 detection cell에서만 throttling했는데도
  inference throughput의 50–59%에 그친다. H1-Quattro는 M1 하나의 4배를 약간 넘는다. 두 ORT mode의
  상대 속도는 host마다 다르다. 데이터로 현상은 확인되지만 원인은 특정하지 못했다.
- **측정하지 않은 항목:** model 정확도, 소비 전력, pipeline 단계별 시간, 냉각 방식에 따른 차이.

---

## 9. 부록

### 9.1 Benchmark 재현

`dx-benchmark/` directory에서 실행한다. 설정 방법은 [`README.md`](../README.md)에 있다.

```bash
./run.sh preflight                                   # 환경 점검
./run.sh dry-run                                     # benchmark matrix 미리 보기
./run.sh run                                         # 전체 실행 (model 수준 + E2E + multi-stream)
./run.sh run --sizes n,s --task object_detection     # 일부만 실행
./run.sh run --resume results/<env>/<run_id> --retry-failed
python3 -m benchmark report results/<env>/<run_id>   # REPORT.md 재생성
python3 -m benchmark dashboard results               # dashboard 재생성
```

### 9.2 측정 protocol — 주요 parameter

| Parameter | 값 |
|-----------|----|
| Protocol version | v2 (thermal mode: steady) |
| Inference throughput 측정 시간 | 30초 |
| Inference latency loop 수 | 300 loop (single-core, 동기) |
| Inference throughput 반복 | 3회, 매회 냉각과 2초 wake-up run 선행 |
| Buffer-count 선택 | `dxrun` auto-stop sweep (`dxrun --max-throughput`): 10초 probe, 3회 반복, 1% tolerance, 매 반복 전 `--cool-down-temp` |
| End-to-end 반복 | 3회 (연속) |
| Warm-up run | latency와 end-to-end 전에 1회 (버림) |
| Multi-stream 채널당 기준 | 30 fps |
| 최대 채널 수 통과 조건 | status ok + 모든 run 완료 + 채널당 E2E FPS ≥ 30 |
| Thermal hot-start 차단 | 60 °C (초과 시 run 거부) |
| 냉각 시점 | model × ORT cell 시작; sweep 반복 전; 측정 inference throughput run 전; E2E 단계 직전. E2E와 multi-stream 사이에는 없음 |
| 냉각 목표 | min(안정 idle + 10 °C, 55 °C) — 6개 환경에서 44–55 °C |
| Video 입력 | H.264 clip 2개, 1920×1080, 30 fps ([§8.2](#82-workload)) |

> 출처: 각 run `environment.json`의 `protocol`, `thermal` block.

### 9.3 환경별 report

| 환경 | Report |
|------|--------|
| BIOSTAR_H1-Quattro | [`results/BIOSTAR_H1-Quattro/20261022_152931/REPORT.md`](../results/BIOSTAR_H1-Quattro/20261022_152931/REPORT.md) |
| DX-AIPlayer-N97_M1 | [`results/DX-AIPlayer-N97_M1/20261022_152931/REPORT.md`](../results/DX-AIPlayer-N97_M1/20261022_152931/REPORT.md) |
| OrangePi5+_M1 | [`results/OrangePi5+_M1/20261022_152933/REPORT.md`](../results/OrangePi5+_M1/20261022_152933/REPORT.md) |
| ROCK5B+_M1 | [`results/ROCK5B+_M1/20261022_062933/REPORT.md`](../results/ROCK5B+_M1/20261022_062933/REPORT.md) |
| RPi5B_M1 | [`results/RPi5B_M1/20261022_152932/REPORT.md`](../results/RPi5B_M1/20261022_152932/REPORT.md) |
| RPi5B_M1M | [`results/RPi5B_M1M/20261022_152931/REPORT.md`](../results/RPi5B_M1M/20261022_152931/REPORT.md) |

### 9.4 용어

| 용어 | 의미 |
|------|------|
| **Coefficient of variation (CV)** | 모표준편차 ÷ 평균, 백분율 |
| **Complete model (ORT ON)** | NPU part와, host에서 ONNX Runtime으로 실행하는 CPU part. 출력이 원본 ONNX model과 같다 |
| **CPU part** | Compile된 model 중 NPU가 실행하지 않는 부분 |
| **NPU만 (ORT OFF)** | NPU part 단독. Application이 post-processing할 NPU raw tensor를 돌려준다. Model 수준에서는 진단용 수치로만 쓴다 |
| **NPU 사용률** | 측정 중 `dxtop`으로 sampling한 NPU core 평균 사용률 |
| **PCIe link 폭** | Host와 NPU module 사이의 PCIe lane 수(Gen3 ×1, Gen3 ×2, Gen3 ×4). Gen3 lane 1개는 방향당 약 1 GB/s를 전송한다 |
| **Throttling** | 고온에서 NPU clock이 1000 MHz 아래로 내려가는 현상 |

---

*`dx-benchmark` tool이 commit한 측정 데이터로 작성했다. 이 문서의 모든 값은 `results/` 아래 결과
파일에서 다시 계산할 수 있다.*

