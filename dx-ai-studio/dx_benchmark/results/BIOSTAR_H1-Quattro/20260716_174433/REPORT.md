# YOLO26 Benchmark Report

**Generated:** 2026-07-21 20:13:36 (Local)

## Test Timing

| # | Type | Families | Sizes | Start | End | Duration |
|---|------|----------|-------|-------|-----|----------|
| 1 | run | all | n,s,m,l,x | 2026-07-16 17:44:33 | 2026-07-17 16:39:38 | 22h 55m 4s |
| 2 | resume | multi | n | 2026-07-20 22:15:20 | 2026-07-20 22:50:59 | 35m 38s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 11.71 | 934.8 | 498.9 | 17 |
| yolo26n.dxnn | OFF | 11.63 | 935.4 | 460.7 | 15 |
| yolo26s.dxnn | ON | 18.65 | 539.0 | 497.3 | 17 |
| yolo26s.dxnn | OFF | 18.44 | 539.6 | 457.2 | 14 |
| yolo26m.dxnn | ON | 25.88 | 376.4 | 372.2 | 12 |
| yolo26m.dxnn | OFF | 25.56 | 376.6 | 371.6 | 12 |
| yolo26l.dxnn | ON | 34.14 | 277.4 | 274.8 | 9 |
| yolo26l.dxnn | OFF | 33.78 | 277.2 | 274.6 | 9 |
| yolo26x.dxnn | ON | 61.32 | 158.1 | 158.2 | 5 |
| yolo26x.dxnn | OFF | 61.08 | 158.2 | 158.1 | 5 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 11.65 | 907.4 | 550.0 | 19 |
| yolo26n-pose.dxnn | OFF | 11.82 | 907.5 | 561.2 | 20 |
| yolo26s-pose.dxnn | ON | 19.27 | 522.1 | 515.1 | 17 |
| yolo26s-pose.dxnn | OFF | 18.95 | 522.8 | 514.6 | 17 |
| yolo26m-pose.dxnn | ON | 26.77 | 366.7 | 364.0 | 12 |
| yolo26m-pose.dxnn | OFF | 26.44 | 366.9 | 362.9 | 12 |
| yolo26l-pose.dxnn | ON | 34.90 | 271.7 | 269.0 | 8 |
| yolo26l-pose.dxnn | OFF | 34.69 | 272.0 | 268.9 | 8 |
| yolo26x-pose.dxnn | ON | 62.63 | 155.7 | 155.4 | 5 |
| yolo26x-pose.dxnn | OFF | 62.32 | 155.8 | 155.2 | 5 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 20.07 | 579.0 | 366.0 | 12 |
| yolo26n-seg.dxnn | OFF | 19.60 | 608.4 | 326.5 | 10 |
| yolo26s-seg.dxnn | ON | 28.72 | 424.0 | 364.3 | 12 |
| yolo26s-seg.dxnn | OFF | 28.29 | 422.9 | 320.6 | 10 |
| yolo26m-seg.dxnn | ON | 42.61 | 266.9 | 265.3 | 8 |
| yolo26m-seg.dxnn | OFF | 42.27 | 265.6 | 265.2 | 8 |
| yolo26l-seg.dxnn | ON | 50.62 | 213.3 | 211.6 | 7 |
| yolo26l-seg.dxnn | OFF | 50.33 | 213.4 | 211.1 | 7 |
| yolo26x-seg.dxnn | ON | 90.19 | 120.3 | 119.8 | 3 |
| yolo26x-seg.dxnn | OFF | 89.63 | 120.4 | 120.3 | 4 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 26.02 | 308.5 | 305.9 | 10 |
| yolo26n-obb.dxnn | OFF | 25.71 | 308.4 | 305.6 | 10 |
| yolo26s-obb.dxnn | ON | 43.48 | 179.5 | 178.8 | 5 |
| yolo26s-obb.dxnn | OFF | 43.22 | 179.6 | 178.9 | 5 |
| yolo26m-obb.dxnn | ON | 61.41 | 131.3 | 130.9 | 4 |
| yolo26m-obb.dxnn | OFF | 61.05 | 131.3 | 130.7 | 4 |
| yolo26l-obb.dxnn | ON | 82.07 | 95.9 | 95.8 | 3 |
| yolo26l-obb.dxnn | OFF | 81.86 | 95.9 | 95.8 | 3 |
| yolo26x-obb.dxnn | ON | 153.95 | 55.1 | 55.2 | 1 |
| yolo26x-obb.dxnn | OFF | 153.52 | 55.1 | 55.2 | 1 |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.00 | 14122.4 | 784.0 | — |
| yolo26n-cls.dxnn | OFF | 1.02 | 14132.0 | 780.9 | — |
| yolo26s-cls.dxnn | ON | 1.70 | 7684.6 | 773.3 | — |
| yolo26s-cls.dxnn | OFF | 1.69 | 7682.9 | 778.9 | — |
| yolo26m-cls.dxnn | ON | 2.32 | 5420.3 | 774.2 | — |
| yolo26m-cls.dxnn | OFF | 2.35 | 5418.3 | 776.5 | — |
| yolo26l-cls.dxnn | ON | 3.66 | 3410.6 | 755.4 | — |
| yolo26l-cls.dxnn | OFF | 3.58 | 3409.7 | 760.8 | — |
| yolo26x-cls.dxnn | ON | 6.20 | 1823.3 | 747.1 | — |
| yolo26x-cls.dxnn | OFF | 6.38 | 1824.2 | 748.6 | — |

## Environment

| Item | Value |
|------|-------|
| Hostname | deepx-B650MT |
| OS | Ubuntu 22.04.5 LTS |
| Kernel | 6.8.0-124-generic |
| CPU | AMD Ryzen 5 9600X 6-Core Processor |
| CPU Cores | 12 |
| RAM | 30.5 GB |
| NPU SKU | H1-Quattro |
| DX-AllSuite | v2.3.3 |
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5x 6000 Mbps, 3.92GiB |
| NPU Board | H1, Rev 0.0 |
| NPU PCIe | Gen3 X4 [04:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.20.3 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.20.3 |
| dxtop | Yes | DX-TOP 1.1.0 |
| ffprobe | Yes | ffprobe version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2007-20... |

## Benchmark Parameters

| Parameter | Value |
|-----------|-------|
| Throughput duration (-t) | 30 sec |
| Latency loops (-l) | 300 |
| Model warmup runs | 1 |
| Model latency runs | 1 |
| Model throughput runs | 3 |
| E2E pipeline runs | 3 |
| Multi-stream FPS threshold | 30.0 fps |
| ORT modes | ON, OFF |
| Benchmark families | model, e2e, multi |

## Measurement Protocol

| Item | Value |
|------|-------|
| Version | v3 |
| Thermal Mode | steady |
| Throughput Time | 30 s |
| Latency Loops | 300 |
| Model Warmup | 1 |
| Model Latency Runs | 1 |
| Model Throughput Runs | 3 |
| E2E Runs | 3 |
| FPS Threshold | 30.0 |
| Multi-Stream Search | single-stream-estimate-linear-boundary |
| Stable Capacity Rule | status_ok_and_all_runs_success_and_avg_per_channel_fps_ge_threshold |
| Cooldown Target ΔT | 10.0 °C |
| Cooldown Absolute Cap | 55.0 °C |
| Hot-Start Block | 60.0 °C |
| Cooldown Max Time | 1000.0 s |
| NPU Warmup | 1.0 s |
| NPU Drain | 0.5 s |

## Benchmarked Models

| Model | Task | Input Size | NPU Memory (MB) | ORT CPU Offload | Multi-Stream Sweep |
|-------|------|------------|:----------------:|:---------------:|:------------------:|
| yolo26n.dxnn | Object Detection | 640×640 | 116.5 | Yes | ✅ |
| yolo26s.dxnn | Object Detection | 640×640 | 151.6 | Yes | ✅ |
| yolo26m.dxnn | Object Detection | 640×640 | 241.9 | Yes | ✅ |
| yolo26l.dxnn | Object Detection | 640×640 | 293.5 | Yes | ✅ |
| yolo26x.dxnn | Object Detection | 640×640 | 522.7 | Yes | ✅ |
| yolo26n-pose.dxnn | Pose Estimation | 640×640 | 118.5 | Yes | ✅ |
| yolo26s-pose.dxnn | Pose Estimation | 640×640 | 158.7 | Yes | ✅ |
| yolo26m-pose.dxnn | Pose Estimation | 640×640 | 254.0 | Yes | ✅ |
| yolo26l-pose.dxnn | Pose Estimation | 640×640 | 305.6 | Yes | ✅ |
| yolo26x-pose.dxnn | Pose Estimation | 640×640 | 516.5 | Yes | ✅ |
| yolo26n-seg.dxnn | Segmentation | 640×640 | 138.8 | Yes | ✅ |
| yolo26s-seg.dxnn | Segmentation | 640×640 | 177.6 | Yes | ✅ |
| yolo26m-seg.dxnn | Segmentation | 640×640 | 270.2 | Yes | ✅ |
| yolo26l-seg.dxnn | Segmentation | 640×640 | 321.8 | Yes | ✅ |
| yolo26x-seg.dxnn | Segmentation | 640×640 | 555.0 | Yes | ✅ |
| yolo26n-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 240.6 | Yes | ✅ |
| yolo26s-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 447.2 | Yes | ✅ |
| yolo26m-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 645.3 | Yes | ✅ |
| yolo26l-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 790.1 | Yes | ✅ |
| yolo26x-obb.dxnn | Oriented BBox (OBB) | 1024×1024 | 1316.5 | Yes | ✅ |
| yolo26n-cls.dxnn | Classification | 224×224 | 4.5 | No | — |
| yolo26s-cls.dxnn | Classification | 224×224 | 9.0 | No | — |
| yolo26m-cls.dxnn | Classification | 224×224 | 15.8 | No | — |
| yolo26l-cls.dxnn | Classification | 224×224 | 19.5 | No | — |
| yolo26x-cls.dxnn | Classification | 224×224 | 48.6 | No | — |

## Input Videos

### Object Detection / Pose / Segmentation

| Item | Value |
|------|-------|
| File | od_benchmark_video.mp4 |
| Resolution | 1920 x 1080 |
| Codec | h264 |
| FPS | 30.0 |
| Frames | 3455 |
| Duration | 115.3 sec |
| Bitrate | 4.47 Mbps |
| Format | QuickTime / MOV |
| Pixel Format | yuv420p |

### Oriented BBox (OBB)

| Item | Value |
|------|-------|
| File | obb_benchmark_video.mp4 |
| Resolution | 1920 x 1080 |
| Codec | h264 |
| FPS | 30.0 |
| Frames | 2640 |
| Duration | 88.0 sec |
| Bitrate | 4.87 Mbps |
| Format | QuickTime / MOV |
| Pixel Format | yuv420p |

### Classification

| Item | Value |
|------|-------|
| File | od_benchmark_video.mp4 |
| Resolution | 1920 x 1080 |
| Codec | h264 |
| FPS | 30.0 |
| Frames | 3455 |
| Duration | 115.3 sec |
| Bitrate | 4.47 Mbps |
| Format | QuickTime / MOV |
| Pixel Format | yuv420p |

## Model-Level Benchmarks

### Throughput (Multi-Core, Async)

> **Buffer-count sweep (★)** — the _Buffer-count sweep_ tables below list throughput fps per `--buffer-count`; ★ marks the winner (highest measured throughput, at full probe precision; fps rounded to 1 decimal). A smaller buffer-count wins only on an exact tie. The sweep's goal is the throughput ceiling — the winning buffer-count value itself is secondary, since tied buffer-counts deliver effectively equal throughput.

#### Object Detection

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 934.8 ±0.9 | 5 | 250 | 92.2 | 100.0 | 46~49 | 1000 | ok |
| yolo26s.dxnn | 539.0 ±0.3 | 4 | 124 | 91.1 | 100.0 | 55~57 | 1000 | ok |
| yolo26m.dxnn | 376.4 ±0.3 | 4 | 85 | 91.4 | 100.0 | 58~61 | 1000 | ok |
| yolo26l.dxnn | 277.4 ±0.2 | 4 | 62 | 91.5 | 100.0 | 57~60 | 1000 | ok |
| yolo26x.dxnn | 158.1 ±0.4 | 4 | 37 | 91.3 | 100.0 | 58~62 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 5 | [3]:779.4 · [4]:915.0 · **[5]:933.5 ★** · [6]:927.7 · [7]:925.2 · [8]:928.3 |
| yolo26s.dxnn | 4 | [3]:486.5 · **[4]:537.6 ★** · [5]:529.3 · [6]:536.2 · [7]:535.2 · [8]:537.1 |
| yolo26m.dxnn | 4 | [3]:344.4 · **[4]:375.4 ★** · [5]:371.4 · [6]:370.1 · [7]:369.3 · [8]:370.6 |
| yolo26l.dxnn | 4 | [3]:259.1 · **[4]:276.3 ★** · [5]:274.8 · [6]:271.9 · [7]:273.1 · [8]:272.0 |
| yolo26x.dxnn | 4 | [3]:151.2 · **[4]:158.1 ★** · [5]:155.5 · [6]:154.3 · [7]:154.2 · [8]:155.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 935.4 ±0.5 | 4 | 155 | 91.3 | 100.0 | 54~55 | 1000 | ok |
| yolo26s.dxnn | 539.6 ±0.2 | 4 | 85 | 91.6 | 100.0 | 54~56 | 1000 | ok |
| yolo26m.dxnn | 376.6 ±0.2 | 4 | 58 | 92.5 | 100.0 | 58~61 | 1000 | ok |
| yolo26l.dxnn | 277.2 ±0.2 | 4 | 42 | 91.5 | 100.0 | 57~60 | 1000 | ok |
| yolo26x.dxnn | 158.2 ±0.1 | 4 | 25 | 91.5 | 100.0 | 58~61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 4 | [3]:804.8 · **[4]:936.2 ★** · [5]:916.0 · [6]:928.7 · [7]:928.0 · [8]:928.3 |
| yolo26s.dxnn | 4 | [3]:488.0 · **[4]:538.7 ★** · [5]:531.9 · [6]:535.8 · [7]:535.9 · [8]:535.5 |
| yolo26m.dxnn | 4 | [3]:347.4 · **[4]:375.6 ★** · [5]:372.3 · [6]:371.2 · [7]:371.7 · [8]:371.2 |
| yolo26l.dxnn | 4 | [3]:260.6 · **[4]:276.4 ★** · [5]:274.4 · [6]:271.8 · [7]:271.7 · [8]:272.0 |
| yolo26x.dxnn | 4 | [3]:149.7 · **[4]:158.2 ★** · [5]:155.8 · [6]:154.8 · [7]:155.5 · [8]:154.2 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 907.4 ±0.5 | 4 | 148 | 92.3 | 100.0 | 54~55 | 1000 | ok |
| yolo26s-pose.dxnn | 522.1 ±0.2 | 4 | 83 | 91.4 | 100.0 | 55~57 | 1000 | ok |
| yolo26m-pose.dxnn | 366.7 ±0.6 | 4 | 57 | 92.3 | 100.0 | 58~61 | 1000 | ok |
| yolo26l-pose.dxnn | 271.7 ±0.1 | 4 | 43 | 89.8 | 100.0 | 57~60 | 1000 | ok |
| yolo26x-pose.dxnn | 155.7 ±0.0 | 4 | 28 | 91.3 | 100.0 | 58~61 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 4 | [3]:797.7 · **[4]:907.5 ★** · [5]:879.8 · [6]:886.6 · [7]:887.1 · [8]:888.2 |
| yolo26s-pose.dxnn | 4 | [3]:480.2 · **[4]:521.2 ★** · [5]:514.5 · [6]:516.0 · [7]:516.6 · [8]:515.8 |
| yolo26m-pose.dxnn | 4 | [3]:338.4 · **[4]:365.0 ★** · [5]:362.6 · [6]:360.5 · [7]:359.5 · [8]:362.2 |
| yolo26l-pose.dxnn | 4 | [3]:254.4 · **[4]:271.4 ★** · [5]:266.8 · [6]:264.4 · [7]:264.2 · [8]:264.7 |
| yolo26x-pose.dxnn | 4 | [3]:146.9 · **[4]:155.1 ★** · [5]:152.3 · [6]:151.6 · [7]:151.1 · [8]:151.8 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 907.5 ±0.2 | 4 | 93 | 91.8 | 100.0 | 54~55 | 1000 | ok |
| yolo26s-pose.dxnn | 522.8 ±0.2 | 4 | 53 | 90.9 | 100.0 | 54~56 | 1000 | ok |
| yolo26m-pose.dxnn | 366.9 ±0.2 | 4 | 37 | 90.6 | 100.0 | 58~60 | 1000 | ok |
| yolo26l-pose.dxnn | 272.0 ±0.1 | 4 | 28 | 91.1 | 100.0 | 57~59 | 1000 | ok |
| yolo26x-pose.dxnn | 155.8 ±0.1 | 4 | 18 | 89.3 | 100.0 | 58~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 4 | [3]:808.4 · **[4]:907.0 ★** · [5]:884.1 · [6]:886.1 · [7]:886.4 · [8]:887.8 |
| yolo26s-pose.dxnn | 4 | [3]:482.4 · **[4]:521.6 ★** · [5]:518.1 · [6]:515.5 · [7]:515.8 · [8]:516.3 |
| yolo26m-pose.dxnn | 4 | [3]:338.6 · **[4]:366.1 ★** · [5]:363.3 · [6]:361.5 · [7]:358.2 · [8]:360.7 |
| yolo26l-pose.dxnn | 4 | [3]:254.3 · **[4]:271.3 ★** · [5]:266.8 · [6]:264.5 · [7]:264.4 · [8]:264.8 |
| yolo26x-pose.dxnn | 4 | [3]:146.7 · **[4]:155.3 ★** · [5]:152.4 · [6]:152.3 · [7]:151.5 · [8]:152.5 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 579.0 ±3.8 | 9 | 517 | 57.5 | 84.8 | 53~54 | 1000 | ok |
| yolo26s-seg.dxnn | 424.0 ±0.1 | 5 | 347 | 91.6 | 100.0 | 56~58 | 1000 | ok |
| yolo26m-seg.dxnn | 266.9 ±0.1 | 4 | 207 | 89.3 | 100.0 | 60~63 | 1000 | ok |
| yolo26l-seg.dxnn | 213.3 ±0.2 | 4 | 163 | 90.5 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-seg.dxnn | 120.3 ±0.4 | 5 | 92 | 88.7 | 100.0 | 60~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 9 | [3]:495.4 · [4]:578.8 · [5]:577.0 · [6]:577.9 · [7]:575.4 · [8]:579.3 · **[9]:581.2 ★** · [10]:575.6 |
| yolo26s-seg.dxnn | 5 | [3]:341.9 · [4]:409.0 · **[5]:423.1 ★** · [6]:419.9 · [7]:419.4 · [8]:418.5 |
| yolo26m-seg.dxnn | 4 | [3]:232.7 · **[4]:265.9 ★** · [5]:264.7 · [6]:264.1 · [7]:264.8 · [8]:264.7 |
| yolo26l-seg.dxnn | 4 | [3]:190.9 · **[4]:212.7 ★** · [5]:208.0 · [6]:209.4 · [7]:208.6 · [8]:209.4 |
| yolo26x-seg.dxnn | 5 | [3]:109.7 · [4]:119.3 · **[5]:120.9 ★** · [6]:115.9 · [7]:116.3 · [8]:116.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 608.4 ±7.3 | 7 | 434 | 61.2 | 89.2 | 53~55 | 1000 | ok |
| yolo26s-seg.dxnn | 422.9 ±0.5 | 5 | 289 | 91.0 | 100.0 | 56~58 | 1000 | ok |
| yolo26m-seg.dxnn | 265.6 ±0.7 | 8 | 177 | 93.0 | 100.0 | 61~64 | 1000 | ok |
| yolo26l-seg.dxnn | 213.4 ±0.0 | 4 | 138 | 90.4 | 100.0 | 59~62 | 1000 | ok |
| yolo26x-seg.dxnn | 120.4 ±0.2 | 4 | 77 | 90.7 | 100.0 | 59~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 7 | [3]:524.2 · [4]:618.1 · [5]:622.3 · [6]:612.6 · **[7]:623.3 ★** · [8]:618.0 |
| yolo26s-seg.dxnn | 5 | [3]:352.0 · [4]:416.6 · **[5]:422.6 ★** · [6]:419.2 · [7]:418.3 · [8]:420.0 |
| yolo26m-seg.dxnn | 8 | [3]:236.5 · [4]:266.5 · [5]:260.5 · [6]:263.8 · [7]:264.2 · **[8]:266.6 ★** · [9]:266.1 · [10]:265.5 |
| yolo26l-seg.dxnn | 4 | [3]:194.3 · **[4]:212.3 ★** · [5]:207.3 · [6]:208.8 · [7]:209.0 · [8]:210.1 |
| yolo26x-seg.dxnn | 4 | [3]:110.0 · **[4]:120.3 ★** · [5]:119.0 · [6]:116.9 · [7]:116.5 · [8]:117.6 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 308.5 ±0.1 | 4 | 52 | 92.2 | 100.0 | 53~54 | 1000 | ok |
| yolo26s-obb.dxnn | 179.5 ±0.0 | 5 | 34 | 90.3 | 100.0 | 51~54 | 1000 | ok |
| yolo26m-obb.dxnn | 131.3 ±0.0 | 4 | 26 | 92.4 | 100.0 | 57~59 | 1000 | ok |
| yolo26l-obb.dxnn | 95.9 ±0.1 | 4 | 20 | 89.1 | 100.0 | 56~59 | 1000 | ok |
| yolo26x-obb.dxnn | 55.1 ±0.1 | 7 | 13 | 86.8 | 100.0 | 57~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 4 | [3]:292.3 · **[4]:307.9 ★** · [5]:306.2 · [6]:305.9 · [7]:305.6 · [8]:306.1 |
| yolo26s-obb.dxnn | 5 | [3]:172.6 · [4]:179.1 · **[5]:179.6 ★** · [6]:0.0 · [7]:0.0 · [8]:0.0 |
| yolo26m-obb.dxnn | 4 | [3]:125.9 · **[4]:130.9 ★** · [5]:130.3 · [6]:130.3 · [7]:130.1 · [8]:129.6 |
| yolo26l-obb.dxnn | 4 | [3]:92.5 · **[4]:95.6 ★** · [5]:95.2 · [6]:94.9 · [7]:94.6 · [8]:94.9 |
| yolo26x-obb.dxnn | 7 | [3]:52.5 · [4]:54.6 · [5]:54.8 · [6]:54.6 · **[7]:54.9 ★** · [8]:54.6 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 308.4 ±0.0 | 4 | 35 | 92.2 | 100.0 | 53~54 | 1000 | ok |
| yolo26s-obb.dxnn | 179.6 ±0.1 | 5 | 22 | 91.4 | 100.0 | 54~55 | 1000 | ok |
| yolo26m-obb.dxnn | 131.3 ±0.0 | 4 | 17 | 89.8 | 100.0 | 56~59 | 1000 | ok |
| yolo26l-obb.dxnn | 95.9 ±0.0 | 4 | 13 | 90.3 | 100.0 | 56~58 | 1000 | ok |
| yolo26x-obb.dxnn | 55.1 ±0.1 | 10 | 8 | 86.9 | 100.0 | 58~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 4 | [3]:293.5 · **[4]:307.9 ★** · [5]:306.5 · [6]:305.4 · [7]:305.1 · [8]:305.6 |
| yolo26s-obb.dxnn | 5 | [3]:172.6 · [4]:179.2 · **[5]:179.3 ★** · [6]:178.8 · [7]:178.9 · [8]:179.2 |
| yolo26m-obb.dxnn | 4 | [3]:126.7 · **[4]:131.0 ★** · [5]:130.7 · [6]:130.1 · [7]:129.8 · [8]:130.0 |
| yolo26l-obb.dxnn | 4 | [3]:93.1 · **[4]:95.6 ★** · [5]:95.2 · [6]:95.0 · [7]:95.0 · [8]:95.1 |
| yolo26x-obb.dxnn | 10 | [3]:53.1 · [4]:54.6 · [5]:54.5 · [6]:54.6 · [7]:54.3 · [8]:54.8 · [9]:54.8 · **[10]:54.9 ★** |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 14122.4 ±2.5 | 8 | 89 | 88.8 | 97.2 | 51~52 | 1000 | ok |
| yolo26s-cls.dxnn | 7684.6 ±0.9 | 6 | 45 | 91.4 | 98.5 | 53~54 | 1000 | ok |
| yolo26m-cls.dxnn | 5420.3 ±2.0 | 10 | 31 | 91.4 | 99.0 | 57~60 | 1000 | ok |
| yolo26l-cls.dxnn | 3410.6 ±1.0 | 4 | 20 | 92.0 | 99.5 | 54~56 | 1000 | ok |
| yolo26x-cls.dxnn | 1823.3 ±0.8 | 5 | 11 | 91.7 | 100.0 | 56~58 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 8 | [3]:10887.6 · [4]:13842.3 · [5]:13783.5 · [6]:14139.0 · [7]:14140.1 · **[8]:14164.9 ★** · [9]:14146.7 · [10]:14143.5 |
| yolo26s-cls.dxnn | 6 | [3]:6564.8 · [4]:7688.5 · [5]:7688.4 · **[6]:7707.4 ★** · [7]:7690.0 · [8]:7694.9 |
| yolo26m-cls.dxnn | 10 | [3]:4741.3 · [4]:5415.2 · [5]:5422.8 · [6]:5428.6 · [7]:5429.5 · [8]:5431.2 · [9]:5431.6 · **[10]:5434.1 ★** |
| yolo26l-cls.dxnn | 4 | [3]:3102.0 · **[4]:3417.9 ★** · [5]:3402.1 · [6]:3403.1 · [7]:3397.9 · [8]:3400.4 |
| yolo26x-cls.dxnn | 5 | [3]:1694.8 · [4]:1825.5 · **[5]:1827.0 ★** · [6]:1824.3 · [7]:1825.6 · [8]:1825.2 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 14132.0 ±25.6 | 8 | 88 | 58.9 | 97.2 | 51~52 | 1000 | ok |
| yolo26s-cls.dxnn | 7682.9 ±3.1 | 6 | 45 | 89.6 | 98.5 | 52~54 | 1000 | ok |
| yolo26m-cls.dxnn | 5418.3 ±2.3 | 6 | 32 | 90.8 | 98.6 | 56~58 | 1000 | ok |
| yolo26l-cls.dxnn | 3409.7 ±0.6 | 4 | 20 | 91.9 | 99.6 | 54~56 | 1000 | ok |
| yolo26x-cls.dxnn | 1824.2 ±0.2 | 8 | 11 | 91.4 | 100.0 | 57~59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 8 | [3]:10882.0 · [4]:13852.4 · [5]:13787.2 · [6]:14111.1 · [7]:14133.7 · **[8]:14161.0 ★** · [9]:0.0 |
| yolo26s-cls.dxnn | 6 | [3]:6555.8 · [4]:7689.5 · [5]:7694.5 · **[6]:7706.8 ★** · [7]:7692.3 · [8]:7701.7 |
| yolo26m-cls.dxnn | 6 | [3]:4749.9 · [4]:5422.0 · [5]:5421.5 · **[6]:5429.5 ★** · [7]:5428.3 · [8]:5428.2 |
| yolo26l-cls.dxnn | 4 | [3]:3094.6 · **[4]:3416.6 ★** · [5]:3400.6 · [6]:3404.7 · [7]:3398.9 · [8]:3400.2 |
| yolo26x-cls.dxnn | 8 | [3]:1695.9 · [4]:1825.5 · [5]:1825.1 · [6]:1825.7 · [7]:1825.8 · **[8]:1826.8 ★** · [9]:1825.8 · [10]:1825.9 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 85.4 ±0.9 | 11.71 | 11.44 | 0.27 | 39 | ok |
| yolo26s.dxnn | 53.6 ±0.3 | 18.65 | 18.36 | 0.29 | 49 | ok |
| yolo26m.dxnn | 38.6 ±0.3 | 25.88 | 25.57 | 0.31 | 49 | ok |
| yolo26l.dxnn | 29.3 ±0.2 | 34.14 | 33.81 | 0.33 | 49 | ok |
| yolo26x.dxnn | 16.3 ±0.4 | 61.32 | 61.00 | 0.32 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 86.0 ±0.5 | 11.63 | 11.63 | N/A | 49 | ok |
| yolo26s.dxnn | 54.2 ±0.1 | 18.44 | 18.44 | N/A | 49 | ok |
| yolo26m.dxnn | 39.1 ±0.2 | 25.56 | 25.56 | N/A | 49 | ok |
| yolo26l.dxnn | 29.6 ±0.2 | 33.78 | 33.78 | N/A | 49 | ok |
| yolo26x.dxnn | 16.4 ±0.1 | 61.08 | 61.08 | N/A | 49 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 85.9 ±0.5 | 11.65 | 11.43 | 0.22 | 49 | ok |
| yolo26s-pose.dxnn | 51.9 ±0.1 | 19.27 | 18.97 | 0.31 | 49 | ok |
| yolo26m-pose.dxnn | 37.3 ±0.6 | 26.77 | 26.46 | 0.32 | 49 | ok |
| yolo26l-pose.dxnn | 28.7 ±0.1 | 34.90 | 34.60 | 0.30 | 49 | ok |
| yolo26x-pose.dxnn | 16.0 ±0.0 | 62.63 | 62.33 | 0.31 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 84.6 ±0.2 | 11.82 | 11.82 | N/A | 49 | ok |
| yolo26s-pose.dxnn | 52.8 ±0.1 | 18.95 | 18.95 | N/A | 49 | ok |
| yolo26m-pose.dxnn | 37.8 ±0.2 | 26.44 | 26.44 | N/A | 49 | ok |
| yolo26l-pose.dxnn | 28.8 ±0.1 | 34.69 | 34.69 | N/A | 49 | ok |
| yolo26x-pose.dxnn | 16.0 ±0.1 | 62.32 | 62.32 | N/A | 48 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 49.8 ±3.8 | 20.07 | 19.67 | 0.40 | 48 | ok |
| yolo26s-seg.dxnn | 34.8 ±0.1 | 28.72 | 28.34 | 0.38 | 49 | ok |
| yolo26m-seg.dxnn | 23.5 ±0.1 | 42.61 | 42.21 | 0.40 | 49 | ok |
| yolo26l-seg.dxnn | 19.8 ±0.2 | 50.62 | 50.23 | 0.39 | 49 | ok |
| yolo26x-seg.dxnn | 11.1 ±0.4 | 90.19 | 89.78 | 0.42 | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 51.0 ±7.3 | 19.60 | 19.60 | N/A | 49 | ok |
| yolo26s-seg.dxnn | 35.3 ±0.5 | 28.29 | 28.29 | N/A | 49 | ok |
| yolo26m-seg.dxnn | 23.7 ±0.7 | 42.27 | 42.27 | N/A | 49 | ok |
| yolo26l-seg.dxnn | 19.9 ±0.0 | 50.33 | 50.33 | N/A | 49 | ok |
| yolo26x-seg.dxnn | 11.2 ±0.2 | 89.63 | 89.63 | N/A | 48 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 38.4 ±0.1 | 26.02 | 25.71 | 0.30 | 49 | ok |
| yolo26s-obb.dxnn | 23.0 ±0.1 | 43.48 | 43.16 | 0.32 | 49 | ok |
| yolo26m-obb.dxnn | 16.3 ±0.0 | 61.41 | 61.09 | 0.32 | 49 | ok |
| yolo26l-obb.dxnn | 12.2 ±0.1 | 82.07 | 81.76 | 0.31 | 48 | ok |
| yolo26x-obb.dxnn | 6.5 ±0.1 | 153.95 | 153.61 | 0.34 | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 38.9 ±0.0 | 25.71 | 25.71 | N/A | 49 | ok |
| yolo26s-obb.dxnn | 23.1 ±0.1 | 43.22 | 43.22 | N/A | 49 | ok |
| yolo26m-obb.dxnn | 16.4 ±0.0 | 61.05 | 61.05 | N/A | 48 | ok |
| yolo26l-obb.dxnn | 12.2 ±0.0 | 81.86 | 81.86 | N/A | 48 | ok |
| yolo26x-obb.dxnn | 6.5 ±0.1 | 153.52 | 153.52 | N/A | 48 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 1002.8 ±2.5 | 1.00 | 1.00 | N/A | 49 | ok |
| yolo26s-cls.dxnn | 590.0 ±0.9 | 1.70 | 1.70 | N/A | 48 | ok |
| yolo26m-cls.dxnn | 431.3 ±2.0 | 2.32 | 2.32 | N/A | 48 | ok |
| yolo26l-cls.dxnn | 273.0 ±1.0 | 3.66 | 3.66 | N/A | 48 | ok |
| yolo26x-cls.dxnn | 161.3 ±0.8 | 6.20 | 6.20 | N/A | 48 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 977.2 ±32.4 | 1.02 | 1.02 | N/A | 48 | ok |
| yolo26s-cls.dxnn | 592.8 ±3.1 | 1.69 | 1.69 | N/A | 48 | ok |
| yolo26m-cls.dxnn | 425.3 ±2.3 | 2.35 | 2.35 | N/A | 48 | ok |
| yolo26l-cls.dxnn | 279.7 ±0.6 | 3.58 | 3.58 | N/A | 48 | ok |
| yolo26x-cls.dxnn | 156.6 ±0.2 | 6.38 | 6.38 | N/A | 49 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vaapidecodebin | 3455 | 3 | 498.9 ±0.7 | 6.92 | 219 | 25.1 | 63.0 | 49 | 1000 | 312 | ok |
| yolo26s.dxnn | vaapidecodebin | 3455 | 3 | 497.3 ±0.3 | 6.95 | 220 | 63.7 | 86.9 | 50 | 1000 | 402 | ok |
| yolo26m.dxnn | vaapidecodebin | 3455 | 3 | 372.2 ±0.4 | 9.28 | 149 | 78.4 | 100.0 | 51~52 | 1000 | 512 | ok |
| yolo26l.dxnn | vaapidecodebin | 3455 | 3 | 274.8 ±0.3 | 12.57 | 101 | 82.9 | 100.0 | 51~53 | 1000 | 526 | ok |
| yolo26x.dxnn | vaapidecodebin | 3455 | 3 | 158.2 ±0.2 | 21.84 | 52 | 84.6 | 100.0 | 53~56 | 1000 | 572 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | vaapidecodebin | 3455 | 3 | 460.7 ±1.3 | 7.50 | 244 | 25.3 | 76.4 | 49 | 1000 | 433 | ok |
| yolo26s.dxnn | vaapidecodebin | 3455 | 3 | 457.2 ±1.5 | 7.56 | 242 | 52.3 | 76.2 | 50 | 1000 | 496 | ok |
| yolo26m.dxnn | vaapidecodebin | 3455 | 3 | 371.6 ±0.9 | 9.30 | 192 | 76.1 | 100.0 | 51~52 | 1000 | 581 | ok |
| yolo26l.dxnn | vaapidecodebin | 3455 | 3 | 274.6 ±0.2 | 12.58 | 133 | 83.1 | 100.0 | 51~53 | 1000 | 594 | ok |
| yolo26x.dxnn | vaapidecodebin | 3455 | 3 | 158.1 ±0.7 | 21.86 | 71 | 84.7 | 100.0 | 53~56 | 1000 | 634 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 498.9 | 460.7 | +38.2 | +8.3% |
| yolo26s.dxnn | 497.3 | 457.2 | +40.0 | +8.8% |
| yolo26m.dxnn | 372.2 | 371.6 | +0.5 | +0.1% |
| yolo26l.dxnn | 274.8 | 274.6 | +0.2 | +0.1% |
| yolo26x.dxnn | 158.2 | 158.1 | +0.2 | +0.1% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vaapidecodebin | 3455 | 3 | 550.0 ±0.6 | 6.28 | 169 | 31.2 | 69.2 | 49 | 1000 | 293 | ok |
| yolo26s-pose.dxnn | vaapidecodebin | 3455 | 3 | 515.1 ±1.6 | 6.71 | 167 | 71.3 | 100.0 | 50~51 | 1000 | 431 | ok |
| yolo26m-pose.dxnn | vaapidecodebin | 3455 | 3 | 364.0 ±1.4 | 9.49 | 101 | 76.9 | 100.0 | 51~52 | 1000 | 460 | ok |
| yolo26l-pose.dxnn | vaapidecodebin | 3455 | 3 | 269.0 ±0.6 | 12.84 | 72 | 81.0 | 100.0 | 51~53 | 1000 | 476 | ok |
| yolo26x-pose.dxnn | vaapidecodebin | 3455 | 3 | 155.4 ±0.3 | 22.23 | 40 | 87.3 | 100.0 | 53~56 | 1000 | 525 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | vaapidecodebin | 3455 | 3 | 561.2 ±2.0 | 6.16 | 131 | 31.6 | 71.1 | 49 | 1000 | 288 | ok |
| yolo26s-pose.dxnn | vaapidecodebin | 3455 | 3 | 514.6 ±1.3 | 6.71 | 127 | 75.6 | 100.0 | 50 | 1000 | 458 | ok |
| yolo26m-pose.dxnn | vaapidecodebin | 3455 | 3 | 362.9 ±1.0 | 9.52 | 78 | 76.0 | 100.0 | 51~52 | 1000 | 490 | ok |
| yolo26l-pose.dxnn | vaapidecodebin | 3455 | 3 | 268.9 ±0.7 | 12.85 | 56 | 79.7 | 100.0 | 51~53 | 1000 | 503 | ok |
| yolo26x-pose.dxnn | vaapidecodebin | 3455 | 3 | 155.2 ±0.5 | 22.27 | 31 | 87.9 | 100.0 | 53~56 | 1000 | 544 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 550.0 | 561.2 | -11.2 | -2.0% |
| yolo26s-pose.dxnn | 515.1 | 514.6 | +0.5 | +0.1% |
| yolo26m-pose.dxnn | 364.0 | 362.9 | +1.2 | +0.3% |
| yolo26l-pose.dxnn | 269.0 | 268.9 | +0.2 | +0.1% |
| yolo26x-pose.dxnn | 155.4 | 155.2 | +0.2 | +0.2% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vaapidecodebin | 3455 | 3 | 366.0 ±0.6 | 9.44 | 539 | 24.9 | 77.0 | 49~50 | 1000 | 561 | ok |
| yolo26s-seg.dxnn | vaapidecodebin | 3455 | 3 | 364.3 ±0.5 | 9.48 | 532 | 57.3 | 80.8 | 50~51 | 1000 | 694 | ok |
| yolo26m-seg.dxnn | vaapidecodebin | 3455 | 3 | 265.3 ±0.5 | 13.02 | 297 | 82.4 | 100.0 | 52~54 | 1000 | 813 | ok |
| yolo26l-seg.dxnn | vaapidecodebin | 3455 | 3 | 211.6 ±1.1 | 16.33 | 221 | 83.2 | 100.0 | 52~54 | 1000 | 826 | ok |
| yolo26x-seg.dxnn | vaapidecodebin | 3455 | 3 | 119.8 ±0.5 | 28.85 | 119 | 88.1 | 100.0 | 55~59 | 1000 | 876 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | vaapidecodebin | 3455 | 3 | 326.5 ±0.9 | 10.58 | 429 | 22.5 | 83.8 | 49 | 1000 | 670 | ok |
| yolo26s-seg.dxnn | vaapidecodebin | 3455 | 3 | 320.6 ±0.6 | 10.78 | 417 | 47.5 | 89.6 | 50~51 | 1000 | 791 | ok |
| yolo26m-seg.dxnn | vaapidecodebin | 3455 | 3 | 265.2 ±0.2 | 13.03 | 325 | 81.7 | 100.0 | 52~54 | 1000 | 911 | ok |
| yolo26l-seg.dxnn | vaapidecodebin | 3455 | 3 | 211.1 ±0.2 | 16.37 | 244 | 84.0 | 100.0 | 52~55 | 1000 | 925 | ok |
| yolo26x-seg.dxnn | vaapidecodebin | 3455 | 3 | 120.3 ±0.3 | 28.73 | 134 | 89.7 | 100.0 | 55~59 | 1000 | 973 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 366.0 | 326.5 | +39.5 | +12.1% |
| yolo26s-seg.dxnn | 364.3 | 320.6 | +43.7 | +13.6% |
| yolo26m-seg.dxnn | 265.3 | 265.2 | +0.1 | +0.0% |
| yolo26l-seg.dxnn | 211.6 | 211.1 | +0.6 | +0.3% |
| yolo26x-seg.dxnn | 119.8 | 120.3 | -0.5 | -0.4% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vaapidecodebin | 2640 | 3 | 305.9 ±0.1 | 8.63 | 115 | 78.0 | 100.0 | 50 | 1000 | 481 | ok |
| yolo26s-obb.dxnn | vaapidecodebin | 2640 | 3 | 178.8 ±0.2 | 14.77 | 63 | 83.4 | 100.0 | 50~52 | 1000 | 495 | ok |
| yolo26m-obb.dxnn | vaapidecodebin | 2640 | 3 | 130.9 ±0.1 | 20.17 | 45 | 84.9 | 100.0 | 52~54 | 1000 | 533 | ok |
| yolo26l-obb.dxnn | vaapidecodebin | 2640 | 3 | 95.8 ±0.1 | 27.56 | 34 | 90.5 | 100.0 | 53~56 | 1000 | 548 | ok |
| yolo26x-obb.dxnn | vaapidecodebin | 2640 | 3 | 55.2 ±0.0 | 47.83 | 20 | 87.7 | 100.0 | 56~60 | 1000 | 594 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | vaapidecodebin | 2640 | 3 | 305.6 ±0.0 | 8.64 | 119 | 77.0 | 100.0 | 50 | 1000 | 501 | ok |
| yolo26s-obb.dxnn | vaapidecodebin | 2640 | 3 | 178.9 ±0.2 | 14.76 | 65 | 85.1 | 100.0 | 51~52 | 1000 | 526 | ok |
| yolo26m-obb.dxnn | vaapidecodebin | 2640 | 3 | 130.7 ±0.2 | 20.20 | 48 | 86.0 | 100.0 | 52~54 | 1000 | 557 | ok |
| yolo26l-obb.dxnn | vaapidecodebin | 2640 | 3 | 95.8 ±0.0 | 27.55 | 35 | 90.1 | 100.0 | 53~56 | 1000 | 575 | ok |
| yolo26x-obb.dxnn | vaapidecodebin | 2640 | 3 | 55.2 ±0.1 | 47.83 | 21 | 87.8 | 100.0 | 56~60 | 1000 | 621 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 305.9 | 305.6 | +0.3 | +0.1% |
| yolo26s-obb.dxnn | 178.8 | 178.9 | -0.1 | -0.1% |
| yolo26m-obb.dxnn | 130.9 | 130.7 | +0.2 | +0.1% |
| yolo26l-obb.dxnn | 95.8 | 95.8 | -0.0 | -0.1% |
| yolo26x-obb.dxnn | 55.2 | 55.2 | +0.0 | +0.0% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vaapidecodebin | 3455 | 3 | 784.0 ±6.8 | 4.41 | 41 | 3.3 | 15.7 | 48~49 | 1000 | 166 | ok |
| yolo26s-cls.dxnn | vaapidecodebin | 3455 | 3 | 773.3 ±12.0 | 4.47 | 42 | 6.0 | 28.7 | 48~49 | 1000 | 234 | ok |
| yolo26m-cls.dxnn | vaapidecodebin | 3455 | 3 | 774.2 ±1.6 | 4.46 | 42 | 8.6 | 41.1 | 49 | 1000 | 203 | ok |
| yolo26l-cls.dxnn | vaapidecodebin | 3455 | 3 | 755.4 ±15.4 | 4.57 | 44 | 14.0 | 63.9 | 49 | 1000 | 240 | ok |
| yolo26x-cls.dxnn | vaapidecodebin | 3455 | 3 | 747.1 ±7.6 | 4.62 | 45 | 24.4 | 59.7 | 49 | 1000 | 263 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | vaapidecodebin | 3455 | 3 | 780.9 ±0.9 | 4.42 | 41 | 3.3 | 15.5 | 48~49 | 1000 | 165 | ok |
| yolo26s-cls.dxnn | vaapidecodebin | 3455 | 3 | 778.9 ±2.3 | 4.44 | 41 | 6.0 | 28.7 | 48~49 | 1000 | 183 | ok |
| yolo26m-cls.dxnn | vaapidecodebin | 3455 | 3 | 776.5 ±1.8 | 4.45 | 42 | 8.7 | 40.5 | 49 | 1000 | 194 | ok |
| yolo26l-cls.dxnn | vaapidecodebin | 3455 | 3 | 760.8 ±3.8 | 4.54 | 43 | 13.7 | 63.5 | 49 | 1000 | 212 | ok |
| yolo26x-cls.dxnn | vaapidecodebin | 3455 | 3 | 748.6 ±2.2 | 4.62 | 45 | 25.4 | 58.6 | 49 | 1000 | 260 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 784.0 | 780.9 | +3.2 | +0.4% |
| yolo26s-cls.dxnn | 773.3 | 778.9 | -5.6 | -0.7% |
| yolo26m-cls.dxnn | 774.2 | 776.5 | -2.3 | -0.3% |
| yolo26l-cls.dxnn | 755.4 | 760.8 | -5.4 | -0.7% |
| yolo26x-cls.dxnn | 747.1 | 748.6 | -1.5 | -0.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 16 | 3 | 541.9 ±1.1 | 33.9 | 306 | 39.4 | 78.2 | 53~56 | 1000 | 677 | ok |
| yolo26n.dxnn | 17 | 3 | 539.7 ±1.8 | 31.8 | 309 | 39.4 | 78.1 | 58~59 | 1000 | 696 | ok |
| yolo26n.dxnn | 18 | 3 | 539.2 ±1.7 | 29.9 | 310 | 39.3 | 77.7 | 60~61 | 1000 | 717 | ok |
| yolo26s.dxnn | 16 | 3 | 531.2 ±1.0 | 33.2 | 312 | 92.9 | 100.0 | 59~64 | 1000 | 741 | ok |
| yolo26s.dxnn | 17 | 3 | 531.6 ±1.0 | 31.3 | 312 | 93.8 | 100.0 | 68~70 | 1000 | 762 | ok |
| yolo26s.dxnn | 18 | 3 | 530.2 ±0.2 | 29.5 | 312 | 93.7 | 100.0 | 71 | 1000 | 779 | ok |
| yolo26m.dxnn | 12 | 3 | 373.4 ±0.4 | 31.1 | 176 | 96.1 | 100.0 | 65~71 | 1000 | 718 | ok |
| yolo26m.dxnn | 13 | 3 | 373.7 ±0.3 | 28.8 | 177 | 95.9 | 100.0 | 76~77 | 1000 | 742 | ok |
| yolo26l.dxnn | 9 | 3 | 275.6 ±0.3 | 30.6 | 115 | 96.4 | 100.0 | 64~70 | 1000 | 687 | ok |
| yolo26l.dxnn | 10 | 3 | 275.9 ±0.1 | 27.6 | 116 | 96.6 | 100.0 | 74~76 | 1000 | 690 | ok |
| yolo26x.dxnn | 5 | 3 | 158.5 ±0.2 | 31.7 | 56 | 95.9 | 100.0 | 68~73 | 1000 | 649 | ok |
| yolo26x.dxnn | 6 | 3 | 158.4 ±0.3 | 26.4 | 57 | 96.2 | 100.0 | 77~79 | 1000 | 663 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 15 | 3 | 451.1 ±1.5 | 30.1 | 257 | 30.7 | 88.0 | 53~56 | 1000 | 776 | ok |
| yolo26n.dxnn | 16 | 3 | 448.9 ±0.6 | 28.1 | 257 | 30.5 | 88.8 | 58 | 1000 | 799 | ok |
| yolo26s.dxnn | 15 | 3 | 448.7 ±1.0 | 29.9 | 261 | 67.0 | 81.1 | 58~62 | 1000 | 833 | ok |
| yolo26s.dxnn | 14 | 3 | 446.6 ±0.4 | 31.9 | 260 | 66.3 | 81.7 | 65~66 | 1000 | 813 | ok |
| yolo26m.dxnn | 12 | 3 | 373.6 ±0.5 | 31.1 | 221 | 96.3 | 100.0 | 65~71 | 1000 | 815 | ok |
| yolo26m.dxnn | 13 | 3 | 374.0 ±0.3 | 28.8 | 222 | 96.2 | 100.0 | 76~78 | 1000 | 830 | ok |
| yolo26l.dxnn | 9 | 3 | 275.6 ±0.1 | 30.6 | 148 | 96.6 | 100.0 | 64~70 | 1000 | 766 | ok |
| yolo26l.dxnn | 10 | 3 | 275.8 ±0.1 | 27.6 | 149 | 96.7 | 100.0 | 75~77 | 1000 | 796 | ok |
| yolo26x.dxnn | 5 | 3 | 158.2 ±0.8 | 31.6 | 76 | 95.6 | 100.0 | 67~73 | 1000 | 729 | ok |
| yolo26x.dxnn | 6 | 3 | 158.3 ±0.6 | 26.4 | 76 | 96.2 | 100.0 | 77~79 | 1000 | 751 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 17 | 31.8 | 15 | 30.1 |
| yolo26s.dxnn | 17 | 31.3 | 14 | 31.9 |
| yolo26m.dxnn | 12 | 31.1 | 12 | 31.1 |
| yolo26l.dxnn | 9 | 30.6 | 9 | 30.6 |
| yolo26x.dxnn | 5 | 31.7 | 5 | 31.6 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 18 | 3 | 599.5 ±1.3 | 33.3 | 242 | 48.7 | 76.0 | 52~56 | 1000 | 702 | ok |
| yolo26n-pose.dxnn | 19 | 3 | 597.0 ±0.7 | 31.4 | 244 | 48.8 | 75.1 | 59~61 | 1000 | 717 | ok |
| yolo26n-pose.dxnn | 20 | 3 | 597.8 ±1.3 | 29.9 | 244 | 48.4 | 74.9 | 61~62 | 1000 | 730 | ok |
| yolo26s-pose.dxnn | 17 | 3 | 518.4 ±0.3 | 30.5 | 204 | 96.3 | 100.0 | 60~65 | 1000 | 724 | ok |
| yolo26s-pose.dxnn | 18 | 3 | 519.6 ±0.5 | 28.9 | 206 | 94.9 | 100.0 | 68~69 | 1000 | 729 | ok |
| yolo26m-pose.dxnn | 12 | 3 | 364.2 ±0.7 | 30.4 | 120 | 95.5 | 100.0 | 65~72 | 1000 | 674 | ok |
| yolo26m-pose.dxnn | 13 | 3 | 365.2 ±0.2 | 28.1 | 121 | 96.3 | 100.0 | 76~78 | 1000 | 703 | ok |
| yolo26l-pose.dxnn | 8 | 3 | 269.5 ±0.6 | 33.7 | 82 | 95.5 | 100.0 | 63~69 | 1000 | 616 | ok |
| yolo26l-pose.dxnn | 9 | 3 | 269.9 ±0.3 | 30.0 | 83 | 96.4 | 100.0 | 73~75 | 1000 | 636 | ok |
| yolo26x-pose.dxnn | 5 | 3 | 156.1 ±0.3 | 31.2 | 42 | 96.7 | 100.0 | 67~72 | 1000 | 608 | ok |
| yolo26x-pose.dxnn | 6 | 3 | 156.1 ±0.2 | 26.0 | 43 | 96.9 | 100.0 | 76~77 | 1000 | 622 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 18 | 3 | 613.0 ±0.6 | 34.0 | 183 | 50.5 | 76.5 | 49~55 | 1000 | 838 | ok |
| yolo26n-pose.dxnn | 19 | 3 | 612.9 ±2.3 | 32.3 | 186 | 50.7 | 76.9 | 58~60 | 1000 | 890 | ok |
| yolo26n-pose.dxnn | 20 | 3 | 613.2 ±2.3 | 30.7 | 186 | 50.5 | 76.7 | 61~62 | 1000 | 867 | ok |
| yolo26n-pose.dxnn | 21 | 3 | 612.4 ±1.6 | 29.2 | 185 | 50.8 | 75.8 | 63 | 1000 | 870 | ok |
| yolo26s-pose.dxnn | 17 | 3 | 517.9 ±0.6 | 30.5 | 160 | 96.3 | 100.0 | 59~64 | 1000 | 767 | ok |
| yolo26s-pose.dxnn | 18 | 3 | 519.1 ±0.1 | 28.8 | 161 | 95.5 | 100.0 | 67~68 | 1000 | 780 | ok |
| yolo26m-pose.dxnn | 12 | 3 | 364.0 ±0.7 | 30.3 | 93 | 95.7 | 100.0 | 65~71 | 1000 | 713 | ok |
| yolo26m-pose.dxnn | 13 | 3 | 364.6 ±0.0 | 28.0 | 95 | 96.5 | 100.0 | 75~77 | 1000 | 741 | ok |
| yolo26l-pose.dxnn | 8 | 3 | 269.0 ±0.1 | 33.6 | 65 | 96.0 | 100.0 | 63~69 | 1000 | 654 | ok |
| yolo26l-pose.dxnn | 9 | 3 | 269.3 ±0.3 | 29.9 | 66 | 96.5 | 100.0 | 72~74 | 1000 | 679 | ok |
| yolo26x-pose.dxnn | 5 | 3 | 156.0 ±0.1 | 31.2 | 33 | 96.9 | 100.0 | 66~72 | 1000 | 632 | ok |
| yolo26x-pose.dxnn | 6 | 3 | 155.9 ±0.1 | 26.0 | 34 | 97.1 | 100.0 | 76~77 | 1000 | 647 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 19 | 31.4 | 20 | 30.7 |
| yolo26s-pose.dxnn | 17 | 30.5 | 17 | 30.5 |
| yolo26m-pose.dxnn | 12 | 30.4 | 12 | 30.3 |
| yolo26l-pose.dxnn | 8 | 33.7 | 8 | 33.6 |
| yolo26x-pose.dxnn | 5 | 31.2 | 5 | 31.2 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 12 | 3 | 376.3 ±1.4 | 31.4 | 637 | 32.3 | 78.5 | 54~57 | 1000 | 1019 | ok |
| yolo26n-seg.dxnn | 13 | 3 | 376.0 ±1.6 | 28.9 | 640 | 32.5 | 79.3 | 59~61 | 1000 | 1039 | ok |
| yolo26s-seg.dxnn | 12 | 3 | 373.9 ±0.3 | 31.2 | 635 | 77.0 | 90.9 | 60~66 | 1000 | 1038 | ok |
| yolo26s-seg.dxnn | 13 | 3 | 371.9 ±0.8 | 28.6 | 635 | 76.0 | 91.2 | 69~71 | 1000 | 1062 | ok |
| yolo26m-seg.dxnn | 8 | 3 | 267.4 ±0.3 | 33.4 | 326 | 96.2 | 100.0 | 68~76 | 1000 | 980 | ok |
| yolo26m-seg.dxnn | 9 | 3 | 261.0 ±5.3 | 29.0 | 320 | 95.2 | 100.0 | 82~83 | 600~1000 | 1012 | ok |
| yolo26l-seg.dxnn | 7 | 3 | 212.4 ±0.1 | 30.3 | 237 | 95.7 | 100.0 | 68~75 | 1000 | 983 | ok |
| yolo26l-seg.dxnn | 8 | 3 | 212.0 ±0.6 | 26.5 | 238 | 96.0 | 100.0 | 80~82 | 800~1000 | 999 | ok |
| yolo26x-seg.dxnn | 3 | 3 | 120.6 ±0.5 | 40.2 | 123 | 94.0 | 100.0 | 70~76 | 1000 | 936 | ok |
| yolo26x-seg.dxnn | 4 | 3 | 117.2 ±2.4 | 29.3 | 121 | 95.0 | 100.0 | 81~82 | 600~1000 | 963 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 10 | 3 | 320.3 ±0.5 | 32.0 | 438 | 26.1 | 83.8 | 53~56 | 1000 | 990 | ok |
| yolo26n-seg.dxnn | 11 | 3 | 318.5 ±0.9 | 28.9 | 438 | 26.0 | 83.9 | 57~58 | 1000 | 1044 | ok |
| yolo26s-seg.dxnn | 10 | 3 | 313.4 ±1.1 | 31.3 | 432 | 55.0 | 87.7 | 58~63 | 1000 | 1064 | ok |
| yolo26s-seg.dxnn | 11 | 3 | 312.0 ±0.2 | 28.4 | 430 | 54.0 | 86.6 | 66~67 | 1000 | 1094 | ok |
| yolo26m-seg.dxnn | 8 | 3 | 266.7 ±0.1 | 33.3 | 353 | 95.3 | 100.0 | 69~77 | 1000 | 1108 | ok |
| yolo26m-seg.dxnn | 9 | 3 | 260.6 ±6.5 | 29.0 | 345 | 94.9 | 100.0 | 82~84 | 600~1000 | 1121 | ok |
| yolo26l-seg.dxnn | 7 | 3 | 212.5 ±0.2 | 30.4 | 259 | 96.0 | 100.0 | 68~75 | 1000 | 1087 | ok |
| yolo26l-seg.dxnn | 8 | 3 | 212.6 ±0.2 | 26.6 | 260 | 95.7 | 100.0 | 80~82 | 800~1000 | 1134 | ok |
| yolo26x-seg.dxnn | 4 | 3 | 120.7 ±0.3 | 30.2 | 135 | 96.2 | 100.0 | 72~79 | 800~1000 | 1067 | ok |
| yolo26x-seg.dxnn | 5 | 3 | 115.8 ±0.9 | 23.1 | 131 | 95.1 | 100.0 | 82~83 | 600~1000 | 1088 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 12 | 31.4 | 10 | 32.0 |
| yolo26s-seg.dxnn | 12 | 31.2 | 10 | 31.3 |
| yolo26m-seg.dxnn | 8 | 33.4 | 8 | 33.3 |
| yolo26l-seg.dxnn | 7 | 30.3 | 7 | 30.4 |
| yolo26x-seg.dxnn | 3 | 40.2 | 4 | 30.2 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 10 | 3 | 306.9 ±0.1 | 30.7 | 133 | 94.9 | 100.0 | 56~59 | 1000 | 674 | ok |
| yolo26n-obb.dxnn | 11 | 3 | 307.3 ±0.1 | 27.9 | 134 | 95.7 | 100.0 | 62~64 | 1000 | 693 | ok |
| yolo26s-obb.dxnn | 5 | 3 | 179.4 ±0.1 | 35.9 | 68 | 95.8 | 100.0 | 57~60 | 1000 | 587 | ok |
| yolo26s-obb.dxnn | 6 | 3 | 179.7 ±0.0 | 29.9 | 69 | 95.5 | 100.0 | 63~64 | 1000 | 609 | ok |
| yolo26m-obb.dxnn | 4 | 3 | 131.3 ±0.1 | 32.8 | 49 | 95.4 | 100.0 | 62~67 | 1000 | 609 | ok |
| yolo26m-obb.dxnn | 5 | 3 | 131.3 ±0.2 | 26.3 | 49 | 96.3 | 100.0 | 71~73 | 1000 | 622 | ok |
| yolo26l-obb.dxnn | 3 | 3 | 96.1 ±0.0 | 32.0 | 36 | 95.5 | 100.0 | 62~66 | 1000 | 599 | ok |
| yolo26l-obb.dxnn | 4 | 3 | 96.0 ±0.1 | 24.0 | 36 | 95.6 | 100.0 | 70~71 | 1000 | 625 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 55.2 ±0.0 | 55.2 | 20 | 87.7 | 100.0 | 56~60 | 1000 | 594 | ok |
| yolo26x-obb.dxnn | 2 | 3 | 55.4 ±0.0 | 27.7 | 21 | 91.7 | 100.0 | 67~70 | 1000 | 628 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 10 | 3 | 306.8 ±0.1 | 30.7 | 136 | 94.1 | 100.0 | 56~59 | 1000 | 692 | ok |
| yolo26n-obb.dxnn | 11 | 3 | 307.2 ±0.0 | 27.9 | 137 | 95.6 | 100.0 | 62~64 | 1000 | 730 | ok |
| yolo26s-obb.dxnn | 5 | 3 | 179.3 ±0.0 | 35.9 | 71 | 95.5 | 100.0 | 57~60 | 1000 | 619 | ok |
| yolo26s-obb.dxnn | 6 | 3 | 179.7 ±0.1 | 29.9 | 72 | 95.5 | 100.0 | 63~64 | 1000 | 640 | ok |
| yolo26m-obb.dxnn | 4 | 3 | 131.3 ±0.1 | 32.8 | 51 | 95.8 | 100.0 | 62~67 | 1000 | 638 | ok |
| yolo26m-obb.dxnn | 5 | 3 | 131.3 ±0.1 | 26.3 | 51 | 96.2 | 100.0 | 71~73 | 1000 | 651 | ok |
| yolo26l-obb.dxnn | 3 | 3 | 96.1 ±0.0 | 32.0 | 37 | 96.1 | 100.0 | 63~66 | 1000 | 623 | ok |
| yolo26l-obb.dxnn | 4 | 3 | 96.1 ±0.1 | 24.0 | 37 | 95.7 | 100.0 | 70~71 | 1000 | 656 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 55.2 ±0.1 | 55.2 | 21 | 87.8 | 100.0 | 56~60 | 1000 | 621 | ok |
| yolo26x-obb.dxnn | 2 | 3 | 55.4 ±0.0 | 27.7 | 22 | 91.9 | 100.0 | 67~70 | 1000 | 651 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 10 | 30.7 | 10 | 30.7 |
| yolo26s-obb.dxnn | 5 | 35.9 | 5 | 35.9 |
| yolo26m-obb.dxnn | 4 | 32.8 | 4 | 32.8 |
| yolo26l-obb.dxnn | 3 | 32.0 | 3 | 32.0 |
| yolo26x-obb.dxnn | 1 | 55.2 | 1 | 55.2 |

---
*Report generated by dx-benchmark tool*
