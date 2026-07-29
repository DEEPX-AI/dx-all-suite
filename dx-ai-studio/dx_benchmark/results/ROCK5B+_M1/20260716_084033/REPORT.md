# YOLO26 Benchmark Report

**Generated:** 2026-07-21 20:13:36 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | retry-failed | 2026-07-18 09:01:57 | 2026-07-19 02:07:06 | 17h 5m 9s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 23.46 | 158.0 | 144.3 | 4 |
| yolo26n.dxnn | OFF | 32.54 | 224.5 | 97.9 | 3 |
| yolo26s.dxnn | ON | 40.05 | 128.7 | 130.6 | 4 |
| yolo26s.dxnn | OFF | 42.75 | 130.7 | 97.6 | 3 |
| yolo26m.dxnn | ON | 59.94 | 91.0 | 90.6 | 2 |
| yolo26m.dxnn | OFF | 50.71 | 91.2 | 90.4 | 2 |
| yolo26l.dxnn | ON | 68.17 | 66.8 | 66.5 | 1 |
| yolo26l.dxnn | OFF | 59.43 | 67.2 | 66.5 | 1 |
| yolo26x.dxnn | ON | 98.08 | 38.0 | 32.5 | 1 |
| yolo26x.dxnn | OFF | 93.10 | 37.8 | 32.4 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 29.69 | 215.9 | 211.5 | 6 |
| yolo26n-pose.dxnn | OFF | 25.15 | 215.0 | 213.6 | 7 |
| yolo26s-pose.dxnn | ON | 35.06 | 126.0 | 125.8 | 4 |
| yolo26s-pose.dxnn | OFF | 31.64 | 126.1 | 125.9 | 4 |
| yolo26m-pose.dxnn | ON | 48.02 | 87.2 | 87.7 | 2 |
| yolo26m-pose.dxnn | OFF | 38.00 | 82.8 | 87.5 | 2 |
| yolo26l-pose.dxnn | ON | 55.98 | 64.9 | 64.9 | 1 |
| yolo26l-pose.dxnn | OFF | 50.50 | 64.7 | 64.8 | 1 |
| yolo26x-pose.dxnn | ON | 90.50 | 37.1 | 32.0 | 1 |
| yolo26x-pose.dxnn | OFF | 85.25 | 37.2 | 32.0 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 35.44 | 107.1 | 94.5 | 3 |
| yolo26n-seg.dxnn | OFF | 36.03 | 159.4 | 80.5 | 2 |
| yolo26s-seg.dxnn | ON | 46.70 | 99.8 | 92.9 | 2 |
| yolo26s-seg.dxnn | OFF | 42.80 | 100.9 | 79.5 | 2 |
| yolo26m-seg.dxnn | ON | 64.50 | 60.2 | 56.3 | 1 |
| yolo26m-seg.dxnn | OFF | 59.80 | 58.1 | 56.8 | 1 |
| yolo26l-seg.dxnn | ON | 69.47 | 50.5 | 44.4 | 1 |
| yolo26l-seg.dxnn | OFF | 66.55 | 49.9 | 44.7 | 1 |
| yolo26x-seg.dxnn | ON | 118.40 | 25.4 | 18.5 | — |
| yolo26x-seg.dxnn | OFF | 109.10 | 24.4 | 18.5 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 50.49 | 74.3 | 74.2 | 2 |
| yolo26n-obb.dxnn | OFF | 44.04 | 74.4 | 74.1 | 2 |
| yolo26s-obb.dxnn | ON | 69.94 | 43.6 | 43.6 | 1 |
| yolo26s-obb.dxnn | OFF | 66.79 | 43.6 | 43.6 | 1 |
| yolo26m-obb.dxnn | ON | 90.53 | 31.8 | 30.9 | 1 |
| yolo26m-obb.dxnn | OFF | 83.63 | 31.9 | 31.1 | 1 |
| yolo26l-obb.dxnn | ON | 112.32 | 23.3 | 21.9 | — |
| yolo26l-obb.dxnn | OFF | 108.16 | 23.2 | 22.1 | — |
| yolo26x-obb.dxnn | ON | 193.27 | 13.2 | 10.5 | — |
| yolo26x-obb.dxnn | OFF | 186.15 | 13.5 | 10.6 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 1.39 | 3505.8 | 985.1 | — |
| yolo26n-cls.dxnn | OFF | 1.21 | 3507.7 | 971.6 | — |
| yolo26s-cls.dxnn | ON | 3.25 | 1898.7 | 951.1 | — |
| yolo26s-cls.dxnn | OFF | 1.97 | 1898.1 | 980.1 | — |
| yolo26m-cls.dxnn | ON | 2.63 | 1336.7 | 946.9 | — |
| yolo26m-cls.dxnn | OFF | 4.23 | 1335.4 | 947.7 | — |
| yolo26l-cls.dxnn | ON | 3.86 | 841.9 | 807.8 | — |
| yolo26l-cls.dxnn | OFF | 3.91 | 841.6 | 807.5 | — |
| yolo26x-cls.dxnn | ON | 6.76 | 449.8 | 444.5 | — |
| yolo26x-cls.dxnn | OFF | 6.51 | 449.1 | 446.9 | — |

## Environment

| Item | Value |
|------|-------|
| Product | ROCK5B+ |
| Hostname | rock-5b-plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-15-rk2312 |
| CPU | - |
| CPU Cores | 8 |
| RAM | 7.8 GB |
| NPU SKU | M1 |
| DX-AllSuite | v2.3.3 |
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X2 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.9 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.9 |
| dxtop | Yes | DX-TOP 1.1.0 |
| ffprobe | Yes | ffprobe version 5.1.9-0+deb12u1 Copyright (c) 2007-2026 the ... |

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
| Benchmark families | all |

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
| yolo26n.dxnn | 158.0 ±1.3 | 6 | 203 | 47.6 | 79.5 | 58~61 | 1000 | ok |
| yolo26s.dxnn | 128.7 ±2.1 | 6 | 172 | 88.8 | 100.0 | 69~71 | 1000 | ok |
| yolo26m.dxnn | 91.0 ±0.2 | 10 | 126 | 89.5 | 100.0 | 77~81 | 1000 | ok |
| yolo26l.dxnn | 66.8 ±0.2 | 6 | 99 | 89.4 | 100.0 | 75~79 | 1000 | ok |
| yolo26x.dxnn | 38.0 ±0.7 | 5 | 76 | 89.1 | 100.0 | 77~81 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 6 | [3]:112.3 · [4]:146.6 · [5]:154.9 · **[6]:157.5 ★** · [7]:153.3 · [8]:153.0 |
| yolo26s.dxnn | 6 | [3]:86.7 · [4]:109.1 · [5]:126.3 · **[6]:130.7 ★** · [7]:129.4 · [8]:129.3 |
| yolo26m.dxnn | 10 | [3]:69.1 · [4]:84.6 · [5]:90.8 · [6]:90.9 · [7]:90.7 · [8]:91.0 · [9]:91.1 · **[10]:91.5 ★** |
| yolo26l.dxnn | 6 | [3]:52.2 · [4]:64.5 · [5]:66.9 · **[6]:67.2 ★** · [7]:66.5 · [8]:66.4 |
| yolo26x.dxnn | 5 | [3]:29.7 · [4]:38.1 · **[5]:38.2 ★** · [6]:37.9 · [7]:38.0 · [8]:37.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 224.5 ±0.4 | 8 | 135 | 92.1 | 100.0 | 67~69 | 1000 | ok |
| yolo26s.dxnn | 130.7 ±0.4 | 6 | 101 | 89.2 | 100.0 | 68~71 | 1000 | ok |
| yolo26m.dxnn | 91.2 ±0.3 | 6 | 86 | 92.6 | 100.0 | 76~79 | 1000 | ok |
| yolo26l.dxnn | 67.2 ±0.2 | 4 | 58 | 90.3 | 100.0 | 75~78 | 1000 | ok |
| yolo26x.dxnn | 37.8 ±0.9 | 4 | 38 | 86.7 | 100.0 | 78~81 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 8 | [3]:121.9 · [4]:159.0 · [5]:185.0 · [6]:222.4 · [7]:226.0 · **[8]:226.1 ★** · [9]:222.7 · [10]:223.4 |
| yolo26s.dxnn | 6 | [3]:96.5 · [4]:116.0 · [5]:130.2 · **[6]:130.7 ★** · [7]:130.4 · [8]:130.0 |
| yolo26m.dxnn | 6 | [3]:69.6 · [4]:89.3 · [5]:90.3 · **[6]:91.9 ★** · [7]:91.6 · [8]:90.6 |
| yolo26l.dxnn | 4 | [3]:57.3 · **[4]:67.0 ★** · [5]:66.5 · [6]:66.4 · [7]:66.4 · [8]:66.3 |
| yolo26x.dxnn | 4 | [3]:30.3 · **[4]:38.5 ★** · [5]:38.3 · [6]:38.0 · [7]:37.9 · [8]:37.9 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 215.9 ±0.3 | 7 | 192 | 90.3 | 100.0 | 68~70 | 1000 | ok |
| yolo26s-pose.dxnn | 126.0 ±0.4 | 6 | 126 | 89.1 | 100.0 | 71~73 | 1000 | ok |
| yolo26m-pose.dxnn | 87.2 ±0.3 | 8 | 100 | 90.8 | 100.0 | 77~81 | 800~1000 | ok |
| yolo26l-pose.dxnn | 64.9 ±0.4 | 5 | 90 | 89.4 | 100.0 | 75~79 | 1000 | ok |
| yolo26x-pose.dxnn | 37.1 ±0.9 | 4 | 64 | 86.7 | 100.0 | 78~81 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 7 | [3]:137.2 · [4]:167.8 · [5]:196.7 · [6]:215.5 · **[7]:215.8 ★** · [8]:212.6 |
| yolo26s-pose.dxnn | 6 | [3]:95.1 · [4]:118.8 · [5]:123.8 · **[6]:125.9 ★** · [7]:125.4 · [8]:125.9 · [9]:125.8 · [10]:125.7 |
| yolo26m-pose.dxnn | 8 | [3]:65.9 · [4]:83.7 · [5]:87.6 · [6]:87.3 · [7]:87.8 · **[8]:88.0 ★** · [9]:87.3 · [10]:87.7 |
| yolo26l-pose.dxnn | 5 | [3]:52.1 · [4]:63.6 · **[5]:65.2 ★** · [6]:64.8 · [7]:64.5 · [8]:64.5 |
| yolo26x-pose.dxnn | 4 | [3]:31.5 · **[4]:37.9 ★** · [5]:37.1 · [6]:37.5 · [7]:37.2 · [8]:37.2 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 215.0 ±0.4 | 6 | 104 | 89.9 | 100.0 | 67~69 | 1000 | ok |
| yolo26s-pose.dxnn | 126.1 ±0.2 | 6 | 106 | 90.3 | 100.0 | 69~72 | 1000 | ok |
| yolo26m-pose.dxnn | 82.8 ±9.2 | 4 | 70 | 83.0 | 100.0 | 73~79 | 1000 | ok |
| yolo26l-pose.dxnn | 64.7 ±0.1 | 6 | 75 | 90.3 | 100.0 | 75~78 | 1000 | ok |
| yolo26x-pose.dxnn | 37.2 ±1.2 | 4 | 49 | 86.7 | 100.0 | 78~81 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 6 | [3]:129.9 · [4]:182.2 · [5]:213.2 · **[6]:214.6 ★** · [7]:213.9 · [8]:214.2 |
| yolo26s-pose.dxnn | 6 | [3]:69.8 · [4]:120.0 · [5]:125.7 · **[6]:126.1 ★** · [7]:125.6 · [8]:126.1 |
| yolo26m-pose.dxnn | 4 | [3]:58.2 · **[4]:88.2 ★** · [5]:87.9 · [6]:87.2 · [7]:87.8 · [8]:87.3 |
| yolo26l-pose.dxnn | 6 | [3]:49.4 · [4]:64.4 · [5]:64.1 · **[6]:64.9 ★** · [7]:64.5 · [8]:64.6 |
| yolo26x-pose.dxnn | 4 | [3]:33.5 · **[4]:38.1 ★** · [5]:37.4 · [6]:37.2 · [7]:37.2 · [8]:37.2 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 107.1 ±0.1 | 6 | 268 | 38.7 | 66.1 | 64~66 | 1000 | ok |
| yolo26s-seg.dxnn | 99.8 ±2.6 | 7 | 250 | 83.9 | 100.0 | 72~75 | 1000 | ok |
| yolo26m-seg.dxnn | 60.2 ±3.6 | 6 | 131 | 89.0 | 100.0 | 80~82 | 600~1000 | ok |
| yolo26l-seg.dxnn | 50.5 ±1.4 | 5 | 104 | 87.6 | 100.0 | 79~81 | 800~1000 | ok |
| yolo26x-seg.dxnn | 25.4 ±1.4 | 7 | 71 | 87.6 | 100.0 | 80~82 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 6 | [3]:67.2 · [4]:91.9 · [5]:102.9 · **[6]:107.6 ★** · [7]:107.1 · [8]:105.5 |
| yolo26s-seg.dxnn | 7 | [3]:59.0 · [4]:73.3 · [5]:88.4 · [6]:98.8 · **[7]:101.7 ★** · [8]:99.1 |
| yolo26m-seg.dxnn | 6 | [3]:44.9 · [4]:57.4 · [5]:64.4 · **[6]:64.7 ★** · [7]:64.5 · [8]:64.5 |
| yolo26l-seg.dxnn | 5 | [3]:39.3 · [4]:48.2 · **[5]:52.0 ★** · [6]:51.1 · [7]:51.9 · [8]:51.6 |
| yolo26x-seg.dxnn | 7 | [3]:23.0 · [4]:28.1 · [5]:29.2 · [6]:29.4 · **[7]:29.6 ★** · [8]:29.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 159.4 ±14.8 | 7 | 233 | 74.4 | 95.9 | 68~71 | 1000 | ok |
| yolo26s-seg.dxnn | 100.9 ±0.1 | 7 | 140 | 88.9 | 100.0 | 71~74 | 1000 | ok |
| yolo26m-seg.dxnn | 58.1 ±2.9 | 8 | 89 | 90.2 | 100.0 | 81~83 | 600~1000 | ok |
| yolo26l-seg.dxnn | 49.9 ±1.3 | 6 | 87 | 87.9 | 100.0 | 79~81 | 600~1000 | ok |
| yolo26x-seg.dxnn | 24.4 ±1.4 | 8 | 58 | 86.5 | 100.0 | 81~82 | 600~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 7 | [3]:86.7 · [4]:103.1 · [5]:131.0 · [6]:150.3 · **[7]:167.6 ★** · [8]:166.6 |
| yolo26s-seg.dxnn | 7 | [3]:61.7 · [4]:80.5 · [5]:94.6 · [6]:98.6 · **[7]:100.9 ★** · [8]:100.4 |
| yolo26m-seg.dxnn | 8 | [3]:46.1 · [4]:59.6 · [5]:65.3 · [6]:64.6 · [7]:64.7 · **[8]:65.7 ★** · [9]:65.0 · [10]:64.1 |
| yolo26l-seg.dxnn | 6 | [3]:37.2 · [4]:49.8 · [5]:51.5 · **[6]:52.1 ★** · [7]:51.0 · [8]:51.0 |
| yolo26x-seg.dxnn | 8 | [3]:23.9 · [4]:28.6 · [5]:27.6 · [6]:28.4 · [7]:28.4 · **[8]:29.2 ★** · [9]:27.6 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.3 ±0.1 | 7 | 99 | 89.6 | 100.0 | 67~69 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.0 | 9 | 85 | 89.3 | 100.0 | 70~72 | 1000 | ok |
| yolo26m-obb.dxnn | 31.8 ±0.1 | 7 | 62 | 88.9 | 100.0 | 75~79 | 1000 | ok |
| yolo26l-obb.dxnn | 23.3 ±0.1 | 5 | 49 | 88.1 | 100.0 | 76~78 | 1000 | ok |
| yolo26x-obb.dxnn | 13.2 ±0.2 | 8 | 42 | 84.1 | 100.0 | 79~81 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 7 | [3]:61.1 · [4]:70.8 · [5]:73.9 · [6]:73.9 · **[7]:74.2 ★** · [8]:74.1 |
| yolo26s-obb.dxnn | 9 | [3]:37.5 · [4]:42.7 · [5]:43.0 · [6]:43.4 · [7]:43.4 · [8]:43.5 · **[9]:43.5 ★** · [10]:43.4 |
| yolo26m-obb.dxnn | 7 | [3]:27.7 · [4]:31.6 · [5]:31.0 · [6]:31.8 · **[7]:31.9 ★** · [8]:31.8 |
| yolo26l-obb.dxnn | 5 | [3]:20.7 · [4]:23.1 · **[5]:23.3 ★** · [6]:23.0 · [7]:23.2 · [8]:23.3 · [9]:23.1 · [10]:23.2 |
| yolo26x-obb.dxnn | 8 | [3]:12.2 · [4]:13.4 · [5]:13.5 · [6]:13.3 · [7]:13.3 · **[8]:13.5 ★** · [9]:13.4 · [10]:13.3 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.4 ±0.2 | 7 | 84 | 90.7 | 100.0 | 66~68 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.1 | 5 | 67 | 89.2 | 100.0 | 69~71 | 1000 | ok |
| yolo26m-obb.dxnn | 31.9 ±0.0 | 4 | 50 | 89.2 | 100.0 | 75~78 | 1000 | ok |
| yolo26l-obb.dxnn | 23.2 ±0.1 | 7 | 44 | 88.6 | 100.0 | 75~77 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.1 | 5 | 29 | 86.2 | 100.0 | 77~80 | 800~1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 7 | [3]:48.5 · [4]:69.5 · [5]:73.8 · [6]:73.9 · **[7]:74.4 ★** · [8]:74.2 |
| yolo26s-obb.dxnn | 5 | [3]:36.6 · [4]:43.1 · **[5]:43.6 ★** · [6]:43.5 · [7]:43.5 · [8]:43.5 |
| yolo26m-obb.dxnn | 4 | [3]:26.8 · **[4]:31.9 ★** · [5]:31.2 · [6]:31.7 · [7]:31.7 · [8]:31.6 |
| yolo26l-obb.dxnn | 7 | [3]:19.6 · [4]:23.2 · [5]:23.0 · [6]:23.1 · **[7]:23.2 ★** · [8]:23.0 |
| yolo26x-obb.dxnn | 5 | [3]:11.8 · [4]:13.4 · **[5]:13.5 ★** · [6]:13.4 · [7]:13.3 · [8]:13.4 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3505.8 ±2.4 | 7 | 119 | 86.9 | 96.7 | 63~64 | 1000 | ok |
| yolo26s-cls.dxnn | 1898.7 ±0.5 | 7 | 68 | 87.9 | 96.8 | 65~67 | 1000 | ok |
| yolo26m-cls.dxnn | 1336.7 ±0.5 | 7 | 55 | 89.4 | 97.3 | 73~75 | 1000 | ok |
| yolo26l-cls.dxnn | 841.9 ±0.2 | 5 | 61 | 90.1 | 98.6 | 69~72 | 1000 | ok |
| yolo26x-cls.dxnn | 449.8 ±0.1 | 8 | 50 | 90.3 | 99.5 | 74~76 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 7 | [3]:2192.0 · [4]:3030.0 · [5]:3467.2 · [6]:3508.7 · **[7]:3519.9 ★** · [8]:3519.3 |
| yolo26s-cls.dxnn | 7 | [3]:1149.2 · [4]:1817.1 · [5]:1843.8 · [6]:1896.1 · **[7]:1906.8 ★** · [8]:1900.2 |
| yolo26m-cls.dxnn | 7 | [3]:814.1 · [4]:1207.3 · [5]:1335.7 · [6]:1339.8 · **[7]:1341.2 ★** · [8]:1339.9 |
| yolo26l-cls.dxnn | 5 | [3]:576.9 · [4]:787.5 · **[5]:843.5 ★** · [6]:842.8 · [7]:841.4 · [8]:841.3 |
| yolo26x-cls.dxnn | 8 | [3]:350.6 · [4]:447.2 · [5]:447.8 · [6]:449.7 · [7]:449.9 · **[8]:450.0 ★** · [9]:449.6 · [10]:449.6 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3507.7 ±3.7 | 8 | 118 | 88.6 | 96.6 | 64~65 | 1000 | ok |
| yolo26s-cls.dxnn | 1898.1 ±3.5 | 7 | 70 | 90.0 | 97.7 | 65~67 | 1000 | ok |
| yolo26m-cls.dxnn | 1335.4 ±0.7 | 10 | 59 | 90.5 | 97.8 | 73~76 | 1000 | ok |
| yolo26l-cls.dxnn | 841.6 ±1.0 | 5 | 61 | 88.9 | 97.9 | 69~71 | 1000 | ok |
| yolo26x-cls.dxnn | 449.1 ±0.2 | 7 | 50 | 90.1 | 99.4 | 73~75 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 8 | [3]:2212.6 · [4]:3028.3 · [5]:3471.9 · [6]:3502.2 · [7]:3503.3 · **[8]:3521.6 ★** · [9]:3519.3 · [10]:3519.6 |
| yolo26s-cls.dxnn | 7 | [3]:1113.5 · [4]:1835.3 · [5]:1840.0 · [6]:1902.1 · **[7]:1908.0 ★** · [8]:1902.3 |
| yolo26m-cls.dxnn | 10 | [3]:819.4 · [4]:1211.2 · [5]:1334.9 · [6]:1340.2 · [7]:1340.7 · [8]:1341.0 · [9]:1338.4 · **[10]:1341.9 ★** |
| yolo26l-cls.dxnn | 5 | [3]:576.3 · [4]:781.1 · **[5]:843.2 ★** · [6]:841.6 · [7]:841.9 · [8]:842.0 |
| yolo26x-cls.dxnn | 7 | [3]:355.9 · [4]:445.8 · [5]:448.2 · [6]:449.7 · **[7]:450.7 ★** · [8]:450.6 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 42.6 ±1.2 | 23.46 | 20.73 | 2.73 | 49 | ok |
| yolo26s.dxnn | 25.0 ±2.1 | 40.05 | 34.45 | 5.60 | 57 | ok |
| yolo26m.dxnn | 16.7 ±0.2 | 59.94 | 51.20 | 8.74 | 57 | ok |
| yolo26l.dxnn | 14.7 ±0.2 | 68.17 | 59.32 | 8.85 | 58 | ok |
| yolo26x.dxnn | 10.2 ±0.7 | 98.08 | 93.01 | 5.07 | 59 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 30.7 ±0.3 | 32.54 | 32.54 | N/A | 56 | ok |
| yolo26s.dxnn | 23.4 ±0.4 | 42.75 | 42.75 | N/A | 57 | ok |
| yolo26m.dxnn | 19.7 ±0.3 | 50.71 | 50.71 | N/A | 58 | ok |
| yolo26l.dxnn | 16.8 ±0.2 | 59.43 | 59.43 | N/A | 59 | ok |
| yolo26x.dxnn | 10.7 ±0.8 | 93.10 | 93.10 | N/A | 60 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 33.7 ±0.3 | 29.69 | 25.20 | 4.49 | 57 | ok |
| yolo26s-pose.dxnn | 28.5 ±0.4 | 35.06 | 32.72 | 2.34 | 57 | ok |
| yolo26m-pose.dxnn | 20.8 ±0.3 | 48.02 | 45.11 | 2.91 | 58 | ok |
| yolo26l-pose.dxnn | 17.9 ±0.4 | 55.98 | 51.58 | 4.40 | 58 | ok |
| yolo26x-pose.dxnn | 11.0 ±0.9 | 90.50 | 87.48 | 3.02 | 60 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 39.8 ±0.4 | 25.15 | 25.15 | N/A | 56 | ok |
| yolo26s-pose.dxnn | 31.6 ±0.2 | 31.64 | 31.64 | N/A | 57 | ok |
| yolo26m-pose.dxnn | 26.3 ±9.2 | 38.00 | 38.00 | N/A | 59 | ok |
| yolo26l-pose.dxnn | 19.8 ±0.1 | 50.50 | 50.50 | N/A | 59 | ok |
| yolo26x-pose.dxnn | 11.7 ±1.2 | 85.25 | 85.25 | N/A | 60 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 28.2 ±0.1 | 35.44 | 32.18 | 3.26 | 57 | ok |
| yolo26s-seg.dxnn | 21.4 ±2.6 | 46.70 | 42.90 | 3.80 | 58 | ok |
| yolo26m-seg.dxnn | 15.5 ±3.6 | 64.50 | 60.16 | 4.34 | 59 | ok |
| yolo26l-seg.dxnn | 14.4 ±1.4 | 69.47 | 64.81 | 4.66 | 59 | ok |
| yolo26x-seg.dxnn | 8.4 ±1.4 | 118.40 | 113.04 | 5.36 | 61 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 27.8 ±14.8 | 36.03 | 36.03 | N/A | 57 | ok |
| yolo26s-seg.dxnn | 23.4 ±0.1 | 42.80 | 42.80 | N/A | 57 | ok |
| yolo26m-seg.dxnn | 16.7 ±3.0 | 59.80 | 59.80 | N/A | 60 | ok |
| yolo26l-seg.dxnn | 15.0 ±1.3 | 66.55 | 66.55 | N/A | 60 | ok |
| yolo26x-seg.dxnn | 9.2 ±1.4 | 109.10 | 109.10 | N/A | 62 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 19.8 ±0.1 | 50.49 | 44.27 | 6.21 | 57 | ok |
| yolo26s-obb.dxnn | 14.3 ±0.0 | 69.94 | 66.06 | 3.87 | 58 | ok |
| yolo26m-obb.dxnn | 11.0 ±0.1 | 90.53 | 83.56 | 6.96 | 60 | ok |
| yolo26l-obb.dxnn | 8.9 ±0.1 | 112.32 | 108.52 | 3.80 | 60 | ok |
| yolo26x-obb.dxnn | 5.2 ±0.2 | 193.27 | 189.21 | 4.06 | 62 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 22.7 ±0.1 | 44.04 | 44.04 | N/A | 57 | ok |
| yolo26s-obb.dxnn | 15.0 ±0.1 | 66.79 | 66.79 | N/A | 59 | ok |
| yolo26m-obb.dxnn | 12.0 ±0.0 | 83.63 | 83.63 | N/A | 61 | ok |
| yolo26l-obb.dxnn | 9.2 ±0.1 | 108.16 | 108.16 | N/A | 61 | ok |
| yolo26x-obb.dxnn | 5.4 ±0.1 | 186.15 | 186.15 | N/A | 63 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 720.6 ±2.4 | 1.39 | 1.39 | N/A | 56 | ok |
| yolo26s-cls.dxnn | 307.3 ±0.5 | 3.25 | 3.25 | N/A | 56 | ok |
| yolo26m-cls.dxnn | 380.4 ±0.5 | 2.63 | 2.63 | N/A | 56 | ok |
| yolo26l-cls.dxnn | 259.0 ±0.2 | 3.86 | 3.86 | N/A | 56 | ok |
| yolo26x-cls.dxnn | 148.0 ±0.1 | 6.76 | 6.76 | N/A | 57 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 826.3 ±3.7 | 1.21 | 1.21 | N/A | 56 | ok |
| yolo26s-cls.dxnn | 508.7 ±3.5 | 1.97 | 1.97 | N/A | 56 | ok |
| yolo26m-cls.dxnn | 236.3 ±0.7 | 4.23 | 4.23 | N/A | 56 | ok |
| yolo26l-cls.dxnn | 255.9 ±1.0 | 3.91 | 3.91 | N/A | 56 | ok |
| yolo26x-cls.dxnn | 153.7 ±0.2 | 6.51 | 6.51 | N/A | 57 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 144.3 ±0.8 | 23.94 | 260 | 40.3 | 70.1 | 56~59 | 1000 | 148 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 130.6 ±0.2 | 26.45 | 211 | 87.6 | 100.0 | 65~68 | 1000 | 162 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 90.6 ±0.2 | 38.14 | 165 | 89.8 | 100.0 | 72~78 | 1000 | 183 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 66.5 ±0.1 | 51.96 | 123 | 92.5 | 100.0 | 74~79 | 1000 | 193 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 32.5 ±4.5 | 106.16 | 77 | 94.3 | 100.0 | 80~83 | 400~1000 | 313 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 97.9 ±1.1 | 35.29 | 194 | 25.3 | 83.8 | 60~61 | 1000 | 166 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 97.6 ±0.5 | 35.39 | 195 | 52.3 | 87.0 | 64~67 | 1000 | 180 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 90.4 ±0.1 | 38.21 | 198 | 92.1 | 100.0 | 72~77 | 1000 | 197 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 66.5 ±0.1 | 51.94 | 147 | 91.9 | 100.0 | 74~80 | 800~1000 | 209 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 32.4 ±4.3 | 106.52 | 102 | 94.8 | 100.0 | 80~83 | 400~1000 | 313 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 144.3 | 97.9 | +46.4 | +47.4% |
| yolo26s.dxnn | 130.6 | 97.6 | +33.0 | +33.8% |
| yolo26m.dxnn | 90.6 | 90.4 | +0.2 | +0.2% |
| yolo26l.dxnn | 66.5 | 66.5 | -0.0 | -0.0% |
| yolo26x.dxnn | 32.5 | 32.4 | +0.1 | +0.3% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 211.5 ±1.3 | 16.33 | 280 | 78.0 | 96.8 | 63~64 | 1000 | 138 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 125.8 ±0.1 | 27.48 | 163 | 89.6 | 100.0 | 66~69 | 1000 | 153 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 87.7 ±0.2 | 39.40 | 116 | 92.5 | 100.0 | 73~79 | 1000 | 175 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 64.9 ±0.1 | 53.26 | 97 | 93.5 | 100.0 | 74~80 | 1000 | 184 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 32.0 ±3.8 | 107.96 | 70 | 94.7 | 100.0 | 81~83 | 400~1000 | 325 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 213.6 ±1.2 | 16.18 | 172 | 81.7 | 100.0 | 62~64 | 1000 | 128 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 125.9 ±0.5 | 27.45 | 120 | 90.1 | 100.0 | 66~69 | 1000 | 144 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 87.5 ±0.2 | 39.49 | 101 | 92.0 | 100.0 | 72~78 | 1000 | 164 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 64.8 ±0.1 | 53.32 | 94 | 93.8 | 100.0 | 74~79 | 1000 | 176 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 32.0 ±3.8 | 107.83 | 66 | 93.9 | 100.0 | 81~83 | 600~1000 | 325 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 211.5 | 213.6 | -2.1 | -1.0% |
| yolo26s-pose.dxnn | 125.8 | 125.9 | -0.1 | -0.1% |
| yolo26m-pose.dxnn | 87.7 | 87.5 | +0.2 | +0.2% |
| yolo26l-pose.dxnn | 64.9 | 64.8 | +0.1 | +0.1% |
| yolo26x-pose.dxnn | 32.0 | 32.0 | -0.0 | -0.1% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 94.5 ±0.8 | 36.58 | 377 | 30.9 | 72.5 | 62~64 | 1000 | 236 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 92.9 ±1.4 | 37.21 | 334 | 74.3 | 86.7 | 67~72 | 1000 | 257 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 56.3 ±7.5 | 61.38 | 191 | 91.8 | 100.0 | 79~82 | 400~1000 | 286 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 44.4 ±6.8 | 77.86 | 153 | 93.3 | 100.0 | 78~83 | 400~1000 | 292 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 18.5 ±2.3 | 186.47 | 83 | 94.4 | 100.0 | 82~83 | 400~1000 | 362 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 80.5 ±0.5 | 42.94 | 279 | 26.2 | 85.9 | 61~64 | 1000 | 280 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 79.5 ±1.7 | 43.45 | 265 | 55.0 | 93.5 | 66~71 | 1000 | 295 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 56.8 ±6.8 | 60.87 | 184 | 93.1 | 100.0 | 79~82 | 400~1000 | 313 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 44.7 ±6.2 | 77.31 | 149 | 94.0 | 100.0 | 79~82 | 400~1000 | 321 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 18.5 ±2.1 | 186.59 | 87 | 94.4 | 100.0 | 82~83 | 400~1000 | 365 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 94.5 | 80.5 | +14.0 | +17.4% |
| yolo26s-seg.dxnn | 92.9 | 79.5 | +13.3 | +16.8% |
| yolo26m-seg.dxnn | 56.3 | 56.8 | -0.5 | -0.8% |
| yolo26l-seg.dxnn | 44.4 | 44.7 | -0.3 | -0.7% |
| yolo26x-seg.dxnn | 18.5 | 18.5 | +0.0 | +0.1% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 74.2 ±0.0 | 35.59 | 125 | 91.3 | 100.0 | 64~67 | 1000 | 163 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.6 ±0.1 | 60.58 | 90 | 94.0 | 100.0 | 69~73 | 1000 | 182 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 30.9 ±1.3 | 85.40 | 76 | 94.0 | 100.0 | 77~83 | 600~1000 | 204 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 21.9 ±1.6 | 120.57 | 58 | 94.4 | 100.0 | 79~83 | 400~1000 | 215 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 10.5 ±0.7 | 251.82 | 43 | 93.7 | 100.0 | 82~83 | 300~1000 | 333 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 74.1 ±0.1 | 35.63 | 128 | 91.8 | 100.0 | 65~68 | 1000 | 164 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.6 ±0.0 | 60.58 | 98 | 93.7 | 100.0 | 69~73 | 1000 | 178 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 31.1 ±1.2 | 84.92 | 76 | 93.9 | 100.0 | 76~82 | 600~1000 | 206 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 22.1 ±1.3 | 119.19 | 62 | 94.8 | 100.0 | 79~83 | 600~1000 | 212 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 10.6 ±0.9 | 250.04 | 40 | 93.9 | 100.0 | 83 | 400~1000 | 333 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 74.2 | 74.1 | +0.1 | +0.1% |
| yolo26s-obb.dxnn | 43.6 | 43.6 | +0.0 | +0.0% |
| yolo26m-obb.dxnn | 30.9 | 31.1 | -0.2 | -0.6% |
| yolo26l-obb.dxnn | 21.9 | 22.1 | -0.2 | -1.1% |
| yolo26x-obb.dxnn | 10.5 | 10.6 | -0.1 | -0.8% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 985.1 ±28.7 | 3.51 | 153 | 11.9 | 44.1 | 57 | 1000 | 54 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 951.1 ±26.9 | 3.63 | 154 | 24.5 | 71.7 | 57~58 | 1000 | 67 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 946.9 ±23.9 | 3.65 | 151 | 27.1 | 81.1 | 59~60 | 1000 | 91 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 807.8 ±10.5 | 4.28 | 135 | 57.7 | 98.6 | 60~61 | 1000 | 103 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 444.5 ±1.4 | 7.77 | 98 | 64.3 | 98.9 | 63~64 | 1000 | 179 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 971.6 ±10.7 | 3.56 | 152 | 13.4 | 46.0 | 56~57 | 1000 | 55 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 980.1 ±25.0 | 3.52 | 153 | 29.4 | 68.1 | 57~58 | 1000 | 67 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 947.7 ±22.8 | 3.65 | 152 | 31.0 | 77.9 | 59~60 | 1000 | 91 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 807.5 ±5.6 | 4.28 | 134 | 57.3 | 98.1 | 60~61 | 1000 | 103 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 446.9 ±1.5 | 7.73 | 98 | 65.1 | 98.8 | 63~64 | 1000 | 179 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 985.1 | 971.6 | +13.5 | +1.4% |
| yolo26s-cls.dxnn | 951.1 | 980.1 | -29.0 | -3.0% |
| yolo26m-cls.dxnn | 946.9 | 947.7 | -0.9 | -0.1% |
| yolo26l-cls.dxnn | 807.8 | 807.5 | +0.3 | +0.0% |
| yolo26x-cls.dxnn | 444.5 | 446.9 | -2.4 | -0.5% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 4 | 3 | 142.2 ±1.0 | 35.6 | 267 | 43.6 | 69.5 | 66~71 | 1000 | 170 | ok |
| yolo26n.dxnn | 5 | 3 | 142.4 ±0.5 | 28.5 | 268 | 43.8 | 69.5 | 73 | 1000 | 175 | ok |
| yolo26s.dxnn | 4 | 3 | 131.0 ±0.1 | 32.7 | 229 | 96.0 | 100.0 | 78~82 | 1000 | 186 | ok |
| yolo26s.dxnn | 5 | 3 | 127.6 ±0.5 | 25.5 | 222 | 95.2 | 100.0 | 84 | 600~1000 | 192 | ok |
| yolo26m.dxnn | 3 | 3 | 67.5 ±3.6 | 22.5 | 126 | 96.3 | 100.0 | 84 | 400~1000 | 202 | ok |
| yolo26m.dxnn | 2 | 3 | 64.0 ±0.8 | 32.0 | 123 | 94.7 | 100.0 | 84 | 400~1000 | 195 | ok |
| yolo26l.dxnn | 1 | 3 | 66.5 ±0.1 | 66.5 | 123 | 92.5 | 100.0 | 74~79 | 1000 | 193 | ok |
| yolo26l.dxnn | 2 | 3 | 52.0 ±3.3 | 26.0 | 104 | 95.6 | 100.0 | 83~84 | 400~1000 | 204 | ok |
| yolo26x.dxnn | 1 | 3 | 32.5 ±4.5 | 32.5 | 77 | 94.3 | 100.0 | 80~83 | 400~1000 | 313 | ok |
| yolo26x.dxnn | 2 | 3 | 25.9 ±0.3 | 13.0 | 70 | 95.2 | 100.0 | 82~83 | 400~1000 | 314 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 3 | 3 | 98.2 ±1.1 | 32.7 | 205 | 26.9 | 83.9 | 64~66 | 1000 | 188 | ok |
| yolo26n.dxnn | 4 | 3 | 97.7 ±0.9 | 24.4 | 202 | 27.2 | 83.9 | 67 | 1000 | 198 | ok |
| yolo26s.dxnn | 3 | 3 | 97.3 ±0.5 | 32.5 | 194 | 54.2 | 86.6 | 72~75 | 1000 | 203 | ok |
| yolo26s.dxnn | 4 | 3 | 97.5 ±0.2 | 24.4 | 199 | 55.0 | 86.7 | 76~77 | 1000 | 213 | ok |
| yolo26m.dxnn | 3 | 3 | 66.1 ±2.3 | 22.0 | 148 | 95.6 | 100.0 | 83~84 | 400~1000 | 223 | ok |
| yolo26m.dxnn | 2 | 3 | 64.9 ±0.8 | 32.5 | 146 | 95.4 | 100.0 | 84 | 400~1000 | 213 | ok |
| yolo26l.dxnn | 1 | 3 | 66.5 ±0.1 | 66.5 | 147 | 91.9 | 100.0 | 74~80 | 800~1000 | 209 | ok |
| yolo26l.dxnn | 2 | 3 | 51.0 ±2.4 | 25.5 | 130 | 95.8 | 100.0 | 83 | 400~1000 | 223 | ok |
| yolo26x.dxnn | 1 | 3 | 32.4 ±4.3 | 32.4 | 102 | 94.8 | 100.0 | 80~83 | 400~1000 | 313 | ok |
| yolo26x.dxnn | 2 | 3 | 26.0 ±0.4 | 13.0 | 86 | 95.1 | 100.0 | 82~83 | 400~1000 | 314 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 4 | 35.6 | 3 | 32.7 |
| yolo26s.dxnn | 4 | 32.7 | 3 | 32.5 |
| yolo26m.dxnn | 2 | 32.0 | 2 | 32.5 |
| yolo26l.dxnn | 1 | 66.5 | 1 | 66.5 |
| yolo26x.dxnn | 1 | 32.5 | 1 | 32.4 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 7 | 3 | 208.0 ±0.9 | 29.7 | 286 | 87.2 | 94.0 | 74~79 | 1000 | 186 | ok |
| yolo26n-pose.dxnn | 6 | 3 | 206.6 ±1.2 | 34.4 | 293 | 85.2 | 93.3 | 81~82 | 1000 | 178 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 126.0 ±0.0 | 31.5 | 170 | 95.0 | 100.0 | 78~82 | 1000 | 183 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 120.9 ±0.8 | 24.2 | 163 | 96.5 | 100.0 | 84 | 600~1000 | 188 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 67.8 ±5.0 | 33.9 | 99 | 94.6 | 100.0 | 83 | 400~1000 | 189 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 62.6 ±0.8 | 20.9 | 96 | 96.3 | 100.0 | 83 | 400~1000 | 198 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 64.9 ±0.1 | 64.9 | 97 | 93.5 | 100.0 | 74~80 | 1000 | 184 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 50.5 ±1.8 | 25.2 | 87 | 95.7 | 100.0 | 83~84 | 400~1000 | 198 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 32.0 ±3.8 | 32.0 | 70 | 94.7 | 100.0 | 81~83 | 400~1000 | 325 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 25.5 ±0.5 | 12.8 | 63 | 96.0 | 100.0 | 83~84 | 400~1000 | 325 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 7 | 3 | 214.8 ±0.1 | 30.7 | 194 | 95.7 | 100.0 | 74~78 | 1000 | 183 | ok |
| yolo26n-pose.dxnn | 8 | 3 | 214.6 ±0.1 | 26.8 | 183 | 96.1 | 100.0 | 80~81 | 1000 | 188 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 125.9 ±0.0 | 31.5 | 123 | 95.1 | 100.0 | 77~81 | 1000 | 178 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 124.0 ±0.5 | 24.8 | 122 | 96.4 | 100.0 | 83~84 | 800~1000 | 185 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 70.5 ±4.7 | 35.2 | 94 | 94.7 | 100.0 | 82~83 | 400~1000 | 179 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 63.5 ±0.4 | 21.2 | 91 | 96.3 | 100.0 | 83~84 | 400~1000 | 188 | ok |
| yolo26l-pose.dxnn | 1 | 3 | 64.8 ±0.1 | 64.8 | 94 | 93.8 | 100.0 | 74~79 | 1000 | 176 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 51.9 ±2.3 | 26.0 | 83 | 95.6 | 100.0 | 82~83 | 400~1000 | 188 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 32.0 ±3.8 | 32.0 | 66 | 93.9 | 100.0 | 81~83 | 600~1000 | 325 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 26.1 ±0.1 | 13.1 | 57 | 96.1 | 100.0 | 83 | 400~1000 | 325 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 6 | 34.4 | 7 | 30.7 |
| yolo26s-pose.dxnn | 4 | 31.5 | 4 | 31.5 |
| yolo26m-pose.dxnn | 2 | 33.9 | 2 | 35.2 |
| yolo26l-pose.dxnn | 1 | 64.9 | 1 | 64.8 |
| yolo26x-pose.dxnn | 1 | 32.0 | 1 | 32.0 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 94.1 ±0.6 | 31.4 | 381 | 32.7 | 74.8 | 70~72 | 1000 | 267 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 95.0 ±0.3 | 23.8 | 362 | 33.5 | 69.3 | 75 | 1000 | 277 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 89.7 ±2.6 | 29.9 | 340 | 80.2 | 98.2 | 81~85 | 400~1000 | 289 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 80.5 ±1.0 | 40.2 | 287 | 89.6 | 100.0 | 84~85 | 400~1000 | 277 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 56.3 ±7.5 | 56.3 | 191 | 91.8 | 100.0 | 79~82 | 400~1000 | 286 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 39.1 ±0.2 | 19.6 | 128 | 96.6 | 100.0 | 83 | 400~800 | 302 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.4 ±6.8 | 44.4 | 153 | 93.3 | 100.0 | 78~83 | 400~1000 | 292 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 33.0 ±0.4 | 16.5 | 115 | 96.1 | 100.0 | 83~84 | 400~1000 | 312 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 18.5 ±2.3 | 18.5 | 83 | 94.4 | 100.0 | 82~83 | 400~1000 | 362 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 79.9 ±0.1 | 40.0 | 282 | 26.6 | 84.9 | 67~68 | 1000 | 300 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 79.8 ±0.1 | 26.6 | 283 | 26.8 | 84.9 | 70~71 | 1000 | 318 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 78.2 ±0.2 | 39.1 | 266 | 56.5 | 93.0 | 76~79 | 1000 | 319 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 78.2 ±0.0 | 26.1 | 266 | 57.0 | 93.3 | 82~83 | 1000 | 334 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 56.8 ±6.8 | 56.8 | 184 | 93.1 | 100.0 | 79~82 | 400~1000 | 313 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 39.0 ±0.3 | 19.5 | 130 | 96.4 | 100.0 | 83~84 | 400~800 | 345 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 44.7 ±6.2 | 44.7 | 149 | 94.0 | 100.0 | 79~82 | 400~1000 | 321 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 33.0 ±0.3 | 16.5 | 119 | 96.2 | 100.0 | 83~84 | 400~800 | 346 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 18.5 ±2.1 | 18.5 | 87 | 94.4 | 100.0 | 82~83 | 400~1000 | 365 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 3 | 31.4 | 2 | 40.0 |
| yolo26s-seg.dxnn | 2 | 40.2 | 2 | 39.1 |
| yolo26m-seg.dxnn | 1 | 56.3 | 1 | 56.8 |
| yolo26l-seg.dxnn | 1 | 44.4 | 1 | 44.7 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.3 ±0.0 | 37.1 | 126 | 95.1 | 100.0 | 71~74 | 1000 | 180 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.2 ±0.1 | 24.8 | 127 | 95.9 | 100.0 | 77~78 | 1000 | 194 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.6 ±0.1 | 43.6 | 90 | 94.0 | 100.0 | 69~73 | 1000 | 182 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.6 ±0.0 | 21.8 | 87 | 96.1 | 100.0 | 79~80 | 1000 | 198 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 30.9 ±1.3 | 30.9 | 76 | 94.0 | 100.0 | 77~83 | 600~1000 | 204 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 24.5 ±0.4 | 12.2 | 69 | 95.8 | 100.0 | 83 | 400~1000 | 220 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 21.9 ±1.6 | 21.9 | 58 | 94.4 | 100.0 | 79~83 | 400~1000 | 215 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 10.5 ±0.7 | 10.5 | 43 | 93.7 | 100.0 | 82~83 | 300~1000 | 333 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.2 ±0.0 | 37.1 | 133 | 94.8 | 100.0 | 72~74 | 1000 | 181 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.2 ±0.0 | 24.7 | 134 | 96.4 | 100.0 | 77~78 | 1000 | 190 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.6 ±0.0 | 43.6 | 98 | 93.7 | 100.0 | 69~73 | 1000 | 178 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.6 ±0.0 | 21.8 | 95 | 96.1 | 100.0 | 78~80 | 1000 | 199 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.1 ±1.2 | 31.1 | 76 | 93.9 | 100.0 | 76~82 | 600~1000 | 206 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 24.7 ±0.3 | 12.4 | 72 | 96.2 | 100.0 | 83 | 400~1000 | 218 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 22.1 ±1.3 | 22.1 | 62 | 94.8 | 100.0 | 79~83 | 600~1000 | 212 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 10.6 ±0.9 | 10.6 | 40 | 93.9 | 100.0 | 83 | 400~1000 | 333 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 37.1 | 2 | 37.1 |
| yolo26s-obb.dxnn | 1 | 43.6 | 1 | 43.6 |
| yolo26m-obb.dxnn | 1 | 30.9 | 1 | 31.1 |

---
*Report generated by dx-benchmark tool*
