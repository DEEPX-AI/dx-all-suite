# YOLO26 Benchmark Report

**Generated:** 2026-07-21 20:13:36 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-16 17:22:46 | 2026-07-17 17:37:43 | 24h 14m 57s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n.dxnn | ON | 39.09 | 179.7 | 169.5 | 5 |
| yolo26n.dxnn | OFF | 33.21 | 228.6 | 96.4 | 3 |
| yolo26s.dxnn | ON | 49.29 | 131.0 | 128.6 | 4 |
| yolo26s.dxnn | OFF | 43.14 | 131.6 | 97.0 | 3 |
| yolo26m.dxnn | ON | 59.31 | 91.5 | 91.1 | 2 |
| yolo26m.dxnn | OFF | 49.27 | 90.5 | 90.5 | 2 |
| yolo26l.dxnn | ON | 70.98 | 67.3 | 67.2 | 2 |
| yolo26l.dxnn | OFF | 58.82 | 67.3 | 66.3 | 2 |
| yolo26x.dxnn | ON | 98.27 | 38.4 | 38.7 | 1 |
| yolo26x.dxnn | OFF | 87.59 | 38.3 | 38.4 | 1 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-pose.dxnn | ON | 30.23 | 216.4 | 213.1 | 7 |
| yolo26n-pose.dxnn | OFF | 24.68 | 217.7 | 216.3 | 7 |
| yolo26s-pose.dxnn | ON | 35.53 | 126.1 | 126.7 | 4 |
| yolo26s-pose.dxnn | OFF | 32.32 | 126.3 | 126.0 | 4 |
| yolo26m-pose.dxnn | ON | 45.91 | 88.4 | 87.9 | 2 |
| yolo26m-pose.dxnn | OFF | 39.17 | 88.3 | 87.8 | 2 |
| yolo26l-pose.dxnn | ON | 57.90 | 65.8 | 65.2 | 2 |
| yolo26l-pose.dxnn | OFF | 49.66 | 64.8 | 65.2 | 2 |
| yolo26x-pose.dxnn | ON | 86.93 | 38.1 | 37.7 | 1 |
| yolo26x-pose.dxnn | OFF | 78.63 | 38.0 | 37.8 | 1 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-seg.dxnn | ON | 54.63 | 131.5 | 115.5 | 3 |
| yolo26n-seg.dxnn | OFF | 46.62 | 173.5 | 86.8 | 2 |
| yolo26s-seg.dxnn | ON | 62.57 | 102.5 | 98.8 | 3 |
| yolo26s-seg.dxnn | OFF | 52.85 | 101.3 | 85.9 | 2 |
| yolo26m-seg.dxnn | ON | 80.62 | 65.7 | 65.4 | 1 |
| yolo26m-seg.dxnn | OFF | 72.05 | 65.5 | 65.4 | 1 |
| yolo26l-seg.dxnn | ON | 89.57 | 52.2 | 52.3 | 1 |
| yolo26l-seg.dxnn | OFF | 80.34 | 52.0 | 52.1 | 1 |
| yolo26x-seg.dxnn | ON | 129.20 | 29.4 | 27.0 | — |
| yolo26x-seg.dxnn | OFF | 122.89 | 29.3 | 26.8 | — |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-obb.dxnn | ON | 52.27 | 74.4 | 74.4 | 2 |
| yolo26n-obb.dxnn | OFF | 44.40 | 74.2 | 74.1 | 2 |
| yolo26s-obb.dxnn | ON | 72.24 | 43.6 | 43.5 | 1 |
| yolo26s-obb.dxnn | OFF | 60.06 | 43.6 | 43.5 | 1 |
| yolo26m-obb.dxnn | ON | 89.46 | 31.8 | 31.9 | 1 |
| yolo26m-obb.dxnn | OFF | 80.18 | 31.8 | 31.9 | 1 |
| yolo26l-obb.dxnn | ON | 112.00 | 23.2 | 23.4 | — |
| yolo26l-obb.dxnn | OFF | 100.71 | 23.2 | 23.3 | — |
| yolo26x-obb.dxnn | ON | 185.80 | 13.6 | 13.4 | — |
| yolo26x-obb.dxnn | OFF | 174.77 | 13.5 | 13.4 | — |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26n-cls.dxnn | ON | 2.68 | 3509.8 | 1066.2 | — |
| yolo26n-cls.dxnn | OFF | 2.73 | 3510.8 | 1062.8 | — |
| yolo26s-cls.dxnn | ON | 3.16 | 1916.2 | 1065.1 | — |
| yolo26s-cls.dxnn | OFF | 3.27 | 1917.3 | 1066.7 | — |
| yolo26m-cls.dxnn | ON | 4.14 | 1335.9 | 1066.1 | — |
| yolo26m-cls.dxnn | OFF | 4.20 | 1336.6 | 1066.7 | — |
| yolo26l-cls.dxnn | ON | 5.40 | 847.1 | 833.2 | — |
| yolo26l-cls.dxnn | OFF | 5.48 | 846.5 | 837.3 | — |
| yolo26x-cls.dxnn | ON | 8.29 | 450.9 | 446.0 | — |
| yolo26x-cls.dxnn | OFF | 8.02 | 451.0 | 447.2 | — |

## Environment

| Item | Value |
|------|-------|
| Product | OrangePi5+ |
| Hostname | orangepi5plus |
| OS | Debian GNU/Linux 12 (bookworm) |
| Kernel | 6.1.43-rockchip-rk3588 |
| CPU | Cortex-A55 |
| CPU Cores | 8 |
| RAM | 15.6 GB |
| NPU SKU | M1 |
| DX-AllSuite | v2.3.3 |
| NPU RT | v3.3.2 |
| NPU Driver (RT) | v2.4.1 |
| NPU Driver (PCIe) | v2.2.0 |
| NPU Firmware | v2.5.6 |
| NPU Memory | LPDDR5 5600 Mbps, 3.92GiB |
| NPU Board | M.2, Rev 1.0 |
| NPU PCIe | Gen3 X4 [01:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.3.2 run_model |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.22.0 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.22.0 |
| dxtop | Yes | DX-TOP 1.1.0 |
| ffprobe | Yes | ffprobe version 5.1.3-4 Copyright (c) 2007-2022 the FFmpeg d... |

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
| yolo26n.dxnn | 179.7 ±2.9 | 7 | 234 | 56.8 | 93.3 | 47~50 | 1000 | ok |
| yolo26s.dxnn | 131.0 ±0.3 | 7 | 198 | 91.4 | 100.0 | 58~61 | 1000 | ok |
| yolo26m.dxnn | 91.5 ±0.1 | 7 | 172 | 90.9 | 100.0 | 62~66 | 1000 | ok |
| yolo26l.dxnn | 67.3 ±0.1 | 6 | 162 | 89.6 | 100.0 | 62~65 | 1000 | ok |
| yolo26x.dxnn | 38.4 ±0.4 | 7 | 116 | 89.4 | 100.0 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 7 | [3]:98.1 · [4]:142.2 · [5]:175.9 · [6]:181.6 · **[7]:182.7 ★** · [8]:177.9 |
| yolo26s.dxnn | 7 | [3]:63.1 · [4]:89.4 · [5]:111.8 · [6]:126.6 · **[7]:130.9 ★** · [8]:130.3 |
| yolo26m.dxnn | 7 | [3]:45.3 · [4]:66.0 · [5]:81.9 · [6]:90.5 · **[7]:91.1 ★** · [8]:90.0 |
| yolo26l.dxnn | 6 | [3]:39.5 · [4]:51.2 · [5]:64.3 · **[6]:66.8 ★** · [7]:66.8 · [8]:66.5 |
| yolo26x.dxnn | 7 | [3]:25.4 · [4]:34.0 · [5]:38.0 · [6]:38.0 · **[7]:38.6 ★** · [8]:37.9 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n.dxnn | 228.6 ±0.4 | 7 | 178 | 89.9 | 100.0 | 57~58 | 1000 | ok |
| yolo26s.dxnn | 131.6 ±0.1 | 8 | 138 | 89.3 | 100.0 | 59~61 | 1000 | ok |
| yolo26m.dxnn | 90.5 ±0.1 | 7 | 123 | 89.4 | 100.0 | 62~66 | 1000 | ok |
| yolo26l.dxnn | 67.3 ±0.1 | 5 | 102 | 89.2 | 100.0 | 62~65 | 1000 | ok |
| yolo26x.dxnn | 38.3 ±0.1 | 4 | 69 | 87.9 | 100.0 | 63~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n.dxnn | 7 | [3]:127.2 · [4]:166.6 · [5]:207.7 · [6]:226.8 · **[7]:228.0 ★** · [8]:227.4 |
| yolo26s.dxnn | 8 | [3]:78.9 · [4]:97.0 · [5]:128.8 · [6]:130.9 · [7]:131.1 · **[8]:131.7 ★** · [9]:131.0 · [10]:131.2 |
| yolo26m.dxnn | 7 | [3]:53.5 · [4]:77.6 · [5]:90.6 · [6]:90.7 · **[7]:90.9 ★** · [8]:90.2 |
| yolo26l.dxnn | 5 | [3]:45.4 · [4]:59.7 · **[5]:67.0 ★** · [6]:66.5 · [7]:66.5 · [8]:66.2 |
| yolo26x.dxnn | 4 | [3]:30.0 · **[4]:38.3 ★** · [5]:38.2 · [6]:37.8 · [7]:37.9 · [8]:38.0 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 216.4 ±0.3 | 8 | 217 | 91.4 | 100.0 | 58~60 | 1000 | ok |
| yolo26s-pose.dxnn | 126.1 ±0.2 | 8 | 178 | 90.3 | 100.0 | 59~62 | 1000 | ok |
| yolo26m-pose.dxnn | 88.4 ±0.1 | 5 | 141 | 90.0 | 100.0 | 62~65 | 1000 | ok |
| yolo26l-pose.dxnn | 65.8 ±0.1 | 5 | 118 | 89.8 | 100.0 | 62~64 | 1000 | ok |
| yolo26x-pose.dxnn | 38.1 ±0.1 | 5 | 88 | 88.9 | 100.0 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 8 | [3]:99.9 · [4]:145.4 · [5]:186.8 · [6]:207.8 · [7]:215.6 · **[8]:215.9 ★** · [9]:215.2 · [10]:214.3 |
| yolo26s-pose.dxnn | 8 | [3]:72.0 · [4]:93.1 · [5]:116.6 · [6]:125.8 · [7]:126.0 · **[8]:126.4 ★** · [9]:125.6 · [10]:125.8 |
| yolo26m-pose.dxnn | 5 | [3]:53.1 · [4]:72.6 · **[5]:88.3 ★** · [6]:88.3 · [7]:88.0 · [8]:87.9 |
| yolo26l-pose.dxnn | 5 | [3]:40.7 · [4]:57.8 · **[5]:65.2 ★** · [6]:64.8 · [7]:64.9 · [8]:64.7 |
| yolo26x-pose.dxnn | 5 | [3]:26.7 · [4]:36.8 · **[5]:37.9 ★** · [6]:37.1 · [7]:37.2 · [8]:37.1 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-pose.dxnn | 217.7 ±0.4 | 6 | 151 | 89.3 | 100.0 | 57~59 | 1000 | ok |
| yolo26s-pose.dxnn | 126.3 ±0.6 | 5 | 131 | 90.7 | 100.0 | 58~61 | 1000 | ok |
| yolo26m-pose.dxnn | 88.3 ±0.2 | 5 | 113 | 88.5 | 100.0 | 62~66 | 1000 | ok |
| yolo26l-pose.dxnn | 64.8 ±0.1 | 10 | 94 | 89.4 | 100.0 | 63~65 | 1000 | ok |
| yolo26x-pose.dxnn | 38.0 ±0.0 | 4 | 52 | 88.4 | 100.0 | 63~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-pose.dxnn | 6 | [3]:120.0 · [4]:171.3 · [5]:208.5 · **[6]:217.1 ★** · [7]:215.8 · [8]:216.0 |
| yolo26s-pose.dxnn | 5 | [3]:76.9 · [4]:103.7 · **[5]:126.6 ★** · [6]:125.9 · [7]:125.6 · [8]:125.9 |
| yolo26m-pose.dxnn | 5 | [3]:61.4 · [4]:79.1 · **[5]:88.1 ★** · [6]:87.3 · [7]:87.5 · [8]:87.1 |
| yolo26l-pose.dxnn | 10 | [3]:47.0 · [4]:64.4 · [5]:64.0 · [6]:64.8 · [7]:64.7 · [8]:64.9 · [9]:64.7 · **[10]:65.0 ★** |
| yolo26x-pose.dxnn | 4 | [3]:32.8 · **[4]:37.9 ★** · [5]:37.4 · [6]:37.3 · [7]:37.2 · [8]:37.3 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 131.5 ±0.5 | 8 | 291 | 49.2 | 83.9 | 57~58 | 1000 | ok |
| yolo26s-seg.dxnn | 102.5 ±0.3 | 7 | 228 | 89.5 | 100.0 | 60~63 | 1000 | ok |
| yolo26m-seg.dxnn | 65.7 ±0.1 | 7 | 174 | 90.3 | 100.0 | 65~69 | 1000 | ok |
| yolo26l-seg.dxnn | 52.2 ±0.1 | 7 | 155 | 89.6 | 100.0 | 64~68 | 1000 | ok |
| yolo26x-seg.dxnn | 29.4 ±0.3 | 6 | 113 | 89.4 | 100.0 | 67~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 8 | [3]:68.1 · [4]:93.4 · [5]:116.8 · [6]:128.7 · [7]:130.6 · **[8]:131.6 ★** · [9]:129.2 · [10]:128.0 |
| yolo26s-seg.dxnn | 7 | [3]:43.7 · [4]:58.7 · [5]:82.4 · [6]:98.6 · **[7]:101.0 ★** · [8]:100.2 |
| yolo26m-seg.dxnn | 7 | [3]:34.0 · [4]:46.4 · [5]:57.7 · [6]:64.6 · **[7]:64.9 ★** · [8]:64.4 |
| yolo26l-seg.dxnn | 7 | [3]:28.9 · [4]:41.2 · [5]:49.0 · [6]:51.7 · **[7]:52.0 ★** · [8]:51.2 |
| yolo26x-seg.dxnn | 6 | [3]:18.5 · [4]:26.7 · [5]:29.1 · **[6]:29.3 ★** · [7]:29.1 · [8]:28.6 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-seg.dxnn | 173.5 ±0.2 | 8 | 231 | 87.9 | 100.0 | 59~62 | 1000 | ok |
| yolo26s-seg.dxnn | 101.3 ±0.2 | 8 | 170 | 88.7 | 100.0 | 61~63 | 1000 | ok |
| yolo26m-seg.dxnn | 65.5 ±0.3 | 9 | 140 | 89.1 | 100.0 | 68~72 | 1000 | ok |
| yolo26l-seg.dxnn | 52.0 ±0.3 | 7 | 119 | 89.4 | 100.0 | 64~68 | 1000 | ok |
| yolo26x-seg.dxnn | 29.3 ±0.3 | 5 | 90 | 88.1 | 100.0 | 67~71 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-seg.dxnn | 8 | [3]:74.7 · [4]:106.8 · [5]:138.2 · [6]:162.0 · [7]:170.5 · **[8]:172.2 ★** · [9]:171.2 · [10]:171.7 |
| yolo26s-seg.dxnn | 8 | [3]:54.4 · [4]:69.7 · [5]:91.9 · [6]:101.0 · [7]:100.1 · **[8]:101.1 ★** · [9]:100.2 · [10]:99.9 |
| yolo26m-seg.dxnn | 9 | [3]:37.7 · [4]:54.1 · [5]:62.8 · [6]:64.3 · [7]:64.5 · [8]:64.7 · **[9]:65.9 ★** · [10]:65.9 · [11]:64.9 |
| yolo26l-seg.dxnn | 7 | [3]:30.9 · [4]:44.7 · [5]:51.6 · [6]:51.5 · **[7]:52.0 ★** · [8]:51.2 |
| yolo26x-seg.dxnn | 5 | [3]:19.4 · [4]:28.1 · **[5]:29.5 ★** · [6]:29.2 · [7]:28.3 · [8]:28.2 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.4 ±0.1 | 6 | 154 | 89.0 | 100.0 | 56~58 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.0 | 6 | 124 | 90.2 | 100.0 | 57~60 | 1000 | ok |
| yolo26m-obb.dxnn | 31.8 ±0.0 | 7 | 100 | 89.1 | 100.0 | 62~65 | 1000 | ok |
| yolo26l-obb.dxnn | 23.2 ±0.1 | 5 | 76 | 88.5 | 100.0 | 62~64 | 1000 | ok |
| yolo26x-obb.dxnn | 13.6 ±0.0 | 5 | 47 | 85.8 | 100.0 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 6 | [3]:43.7 · [4]:60.9 · [5]:73.8 · **[6]:74.1 ★** · [7]:73.7 · [8]:73.7 |
| yolo26s-obb.dxnn | 6 | [3]:28.7 · [4]:38.5 · [5]:43.4 · **[6]:43.5 ★** · [7]:43.3 · [8]:43.4 |
| yolo26m-obb.dxnn | 7 | [3]:23.3 · [4]:30.8 · [5]:31.7 · [6]:31.8 · **[7]:31.8 ★** · [8]:31.4 |
| yolo26l-obb.dxnn | 5 | [3]:18.9 · [4]:23.0 · **[5]:23.1 ★** · [6]:23.0 · [7]:23.0 · [8]:23.1 |
| yolo26x-obb.dxnn | 5 | [3]:11.5 · [4]:13.4 · **[5]:13.5 ★** · [6]:13.3 · [7]:13.3 · [8]:13.4 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-obb.dxnn | 74.2 ±0.2 | 8 | 123 | 93.2 | 100.0 | 57~59 | 1000 | ok |
| yolo26s-obb.dxnn | 43.6 ±0.0 | 8 | 73 | 89.4 | 100.0 | 59~61 | 1000 | ok |
| yolo26m-obb.dxnn | 31.8 ±0.1 | 7 | 56 | 89.1 | 100.0 | 62~65 | 1000 | ok |
| yolo26l-obb.dxnn | 23.2 ±0.1 | 8 | 42 | 89.9 | 100.0 | 63~65 | 1000 | ok |
| yolo26x-obb.dxnn | 13.5 ±0.0 | 4 | 23 | 85.2 | 100.0 | 64~67 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-obb.dxnn | 8 | [3]:49.9 · [4]:64.3 · [5]:74.0 · [6]:74.3 · [7]:73.9 · **[8]:74.4 ★** · [9]:73.7 · [10]:73.9 |
| yolo26s-obb.dxnn | 8 | [3]:33.5 · [4]:42.9 · [5]:43.4 · [6]:43.5 · [7]:43.4 · **[8]:43.6 ★** · [9]:43.5 · [10]:43.4 |
| yolo26m-obb.dxnn | 7 | [3]:26.8 · [4]:31.7 · [5]:31.0 · [6]:31.7 · **[7]:31.8 ★** · [8]:31.8 |
| yolo26l-obb.dxnn | 8 | [3]:20.2 · [4]:23.2 · [5]:23.3 · [6]:23.2 · [7]:23.1 · **[8]:23.3 ★** · [9]:23.2 · [10]:23.1 |
| yolo26x-obb.dxnn | 4 | [3]:12.4 · **[4]:13.5 ★** · [5]:13.4 · [6]:13.3 · [7]:13.4 · [8]:13.4 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3509.8 ±2.8 | 10 | 146 | 88.8 | 95.9 | 55~56 | 1000 | ok |
| yolo26s-cls.dxnn | 1916.2 ±1.5 | 7 | 104 | 88.3 | 97.5 | 55~57 | 1000 | ok |
| yolo26m-cls.dxnn | 1335.9 ±0.2 | 9 | 88 | 90.4 | 98.3 | 61~64 | 1000 | ok |
| yolo26l-cls.dxnn | 847.1 ±0.2 | 5 | 69 | 88.4 | 98.2 | 58~60 | 1000 | ok |
| yolo26x-cls.dxnn | 450.9 ±0.4 | 8 | 41 | 91.2 | 99.2 | 61~64 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 10 | [3]:1393.7 · [4]:2278.2 · [5]:3077.2 · [6]:3376.1 · [7]:3458.9 · [8]:3484.1 · [9]:3510.8 · **[10]:3518.0 ★** |
| yolo26s-cls.dxnn | 7 | [3]:919.5 · [4]:1422.7 · [5]:1772.3 · [6]:1900.6 · **[7]:1920.8 ★** · [8]:1919.3 |
| yolo26m-cls.dxnn | 9 | [3]:740.7 · [4]:1080.6 · [5]:1297.0 · [6]:1336.8 · [7]:1340.0 · [8]:1340.5 · **[9]:1342.0 ★** · [10]:1341.8 |
| yolo26l-cls.dxnn | 5 | [3]:547.6 · [4]:760.0 · **[5]:850.0 ★** · [6]:844.4 · [7]:843.4 · [8]:845.5 |
| yolo26x-cls.dxnn | 8 | [3]:346.4 · [4]:450.3 · [5]:450.0 · [6]:451.1 · [7]:451.5 · **[8]:451.8 ★** · [9]:450.8 · [10]:451.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26n-cls.dxnn | 3510.8 ±3.3 | 11 | 147 | 87.7 | 96.5 | 55~56 | 1000 | ok |
| yolo26s-cls.dxnn | 1917.3 ±1.4 | 7 | 104 | 90.8 | 97.3 | 55~57 | 1000 | ok |
| yolo26m-cls.dxnn | 1336.6 ±1.7 | 9 | 89 | 88.4 | 97.8 | 61~63 | 1000 | ok |
| yolo26l-cls.dxnn | 846.5 ±0.4 | 5 | 67 | 87.5 | 98.1 | 58~60 | 1000 | ok |
| yolo26x-cls.dxnn | 451.0 ±0.1 | 6 | 40 | 89.5 | 99.4 | 60~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26n-cls.dxnn | 11 | [3]:1408.4 · [4]:2284.4 · [5]:2991.9 · [6]:3377.7 · [7]:3456.7 · [8]:3467.2 · [9]:3518.1 · [10]:3520.8 · **[11]:3523.5 ★** |
| yolo26s-cls.dxnn | 7 | [3]:907.1 · [4]:1416.9 · [5]:1777.4 · [6]:1894.3 · **[7]:1923.8 ★** · [8]:1917.2 |
| yolo26m-cls.dxnn | 9 | [3]:808.8 · [4]:1077.9 · [5]:1299.8 · [6]:1333.9 · [7]:1339.3 · [8]:1342.8 · **[9]:1343.0 ★** · [10]:1341.8 |
| yolo26l-cls.dxnn | 5 | [3]:547.1 · [4]:759.8 · **[5]:849.6 ★** · [6]:845.6 · [7]:844.8 · [8]:844.9 |
| yolo26x-cls.dxnn | 6 | [3]:354.8 · [4]:449.6 · [5]:450.4 · **[6]:452.0 ★** · [7]:451.9 · [8]:451.3 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 25.6 ±2.9 | 39.09 | 32.02 | 7.07 | 40 | ok |
| yolo26s.dxnn | 20.3 ±0.3 | 49.29 | 43.78 | 5.51 | 50 | ok |
| yolo26m.dxnn | 16.9 ±0.1 | 59.31 | 51.24 | 8.07 | 51 | ok |
| yolo26l.dxnn | 14.1 ±0.1 | 70.98 | 65.45 | 5.53 | 51 | ok |
| yolo26x.dxnn | 10.2 ±0.4 | 98.27 | 92.38 | 5.89 | 52 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n.dxnn | 30.1 ±0.5 | 33.21 | 33.21 | N/A | 50 | ok |
| yolo26s.dxnn | 23.2 ±0.1 | 43.14 | 43.14 | N/A | 50 | ok |
| yolo26m.dxnn | 20.3 ±0.1 | 49.27 | 49.27 | N/A | 51 | ok |
| yolo26l.dxnn | 17.0 ±0.1 | 58.82 | 58.82 | N/A | 51 | ok |
| yolo26x.dxnn | 11.4 ±0.1 | 87.59 | 87.59 | N/A | 52 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 33.1 ±0.3 | 30.23 | 26.44 | 3.79 | 50 | ok |
| yolo26s-pose.dxnn | 28.1 ±0.2 | 35.53 | 30.62 | 4.91 | 51 | ok |
| yolo26m-pose.dxnn | 21.8 ±0.1 | 45.91 | 42.99 | 2.92 | 51 | ok |
| yolo26l-pose.dxnn | 17.3 ±0.1 | 57.90 | 54.80 | 3.10 | 51 | ok |
| yolo26x-pose.dxnn | 11.5 ±0.1 | 86.93 | 82.39 | 4.54 | 52 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-pose.dxnn | 40.5 ±0.4 | 24.68 | 24.68 | N/A | 50 | ok |
| yolo26s-pose.dxnn | 30.9 ±0.6 | 32.32 | 32.32 | N/A | 51 | ok |
| yolo26m-pose.dxnn | 25.5 ±0.2 | 39.17 | 39.17 | N/A | 51 | ok |
| yolo26l-pose.dxnn | 20.1 ±0.1 | 49.66 | 49.66 | N/A | 51 | ok |
| yolo26x-pose.dxnn | 12.7 ±0.0 | 78.63 | 78.63 | N/A | 52 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 18.3 ±0.5 | 54.63 | 49.37 | 5.26 | 50 | ok |
| yolo26s-seg.dxnn | 16.0 ±0.3 | 62.57 | 55.76 | 6.80 | 51 | ok |
| yolo26m-seg.dxnn | 12.4 ±0.1 | 80.62 | 73.56 | 7.06 | 51 | ok |
| yolo26l-seg.dxnn | 11.2 ±0.1 | 89.57 | 83.57 | 6.00 | 51 | ok |
| yolo26x-seg.dxnn | 7.7 ±0.3 | 129.20 | 124.12 | 5.07 | 52 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-seg.dxnn | 21.4 ±0.2 | 46.62 | 46.62 | N/A | 50 | ok |
| yolo26s-seg.dxnn | 18.9 ±0.2 | 52.85 | 52.85 | N/A | 51 | ok |
| yolo26m-seg.dxnn | 13.9 ±0.3 | 72.05 | 72.05 | N/A | 51 | ok |
| yolo26l-seg.dxnn | 12.4 ±0.3 | 80.34 | 80.34 | N/A | 51 | ok |
| yolo26x-seg.dxnn | 8.1 ±0.3 | 122.89 | 122.89 | N/A | 53 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 19.1 ±0.1 | 52.27 | 47.20 | 5.07 | 50 | ok |
| yolo26s-obb.dxnn | 13.8 ±0.0 | 72.24 | 67.57 | 4.67 | 51 | ok |
| yolo26m-obb.dxnn | 11.2 ±0.0 | 89.46 | 84.66 | 4.80 | 52 | ok |
| yolo26l-obb.dxnn | 8.9 ±0.1 | 112.00 | 107.51 | 4.48 | 52 | ok |
| yolo26x-obb.dxnn | 5.4 ±0.0 | 185.80 | 181.33 | 4.47 | 53 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-obb.dxnn | 22.5 ±0.2 | 44.40 | 44.40 | N/A | 51 | ok |
| yolo26s-obb.dxnn | 16.6 ±0.0 | 60.06 | 60.06 | N/A | 51 | ok |
| yolo26m-obb.dxnn | 12.5 ±0.1 | 80.18 | 80.18 | N/A | 52 | ok |
| yolo26l-obb.dxnn | 9.9 ±0.1 | 100.71 | 100.71 | N/A | 53 | ok |
| yolo26x-obb.dxnn | 5.7 ±0.0 | 174.77 | 174.77 | N/A | 54 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 373.1 ±2.8 | 2.68 | 2.68 | N/A | 50 | ok |
| yolo26s-cls.dxnn | 316.7 ±1.6 | 3.16 | 3.16 | N/A | 50 | ok |
| yolo26m-cls.dxnn | 241.8 ±0.2 | 4.14 | 4.14 | N/A | 50 | ok |
| yolo26l-cls.dxnn | 185.1 ±0.2 | 5.40 | 5.40 | N/A | 50 | ok |
| yolo26x-cls.dxnn | 120.7 ±0.4 | 8.29 | 8.29 | N/A | 50 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26n-cls.dxnn | 366.7 ±3.3 | 2.73 | 2.73 | N/A | 50 | ok |
| yolo26s-cls.dxnn | 305.8 ±1.4 | 3.27 | 3.27 | N/A | 50 | ok |
| yolo26m-cls.dxnn | 238.0 ±1.7 | 4.20 | 4.20 | N/A | 50 | ok |
| yolo26l-cls.dxnn | 182.6 ±0.4 | 5.48 | 5.48 | N/A | 50 | ok |
| yolo26x-cls.dxnn | 124.8 ±0.1 | 8.02 | 8.02 | N/A | 50 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 169.5 ±0.8 | 20.39 | 288 | 49.1 | 86.3 | 51~53 | 1000 | 147 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 128.6 ±0.3 | 26.87 | 231 | 85.1 | 100.0 | 55~58 | 1000 | 162 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 91.1 ±0.1 | 37.91 | 195 | 88.8 | 100.0 | 60~65 | 1000 | 183 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 67.2 ±0.1 | 51.45 | 173 | 93.2 | 100.0 | 61~67 | 1000 | 192 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 38.7 ±0.0 | 89.19 | 131 | 95.7 | 100.0 | 68~75 | 1000 | 314 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | mppvideodec | 3455 | 3 | 96.4 ±5.5 | 35.83 | 208 | 25.5 | 85.5 | 52 | 1000 | 167 | ok |
| yolo26s.dxnn | mppvideodec | 3455 | 3 | 97.0 ±5.2 | 35.62 | 220 | 51.5 | 88.7 | 54~56 | 1000 | 179 | ok |
| yolo26m.dxnn | mppvideodec | 3455 | 3 | 90.5 ±0.2 | 38.19 | 231 | 91.5 | 100.0 | 60~65 | 1000 | 199 | ok |
| yolo26l.dxnn | mppvideodec | 3455 | 3 | 66.3 ±0.1 | 52.07 | 199 | 92.2 | 100.0 | 61~67 | 1000 | 202 | ok |
| yolo26x.dxnn | mppvideodec | 3455 | 3 | 38.4 ±0.2 | 89.96 | 150 | 94.6 | 100.0 | 67~75 | 1000 | 314 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n.dxnn | 169.5 | 96.4 | +73.0 | +75.8% |
| yolo26s.dxnn | 128.6 | 97.0 | +31.6 | +32.6% |
| yolo26m.dxnn | 91.1 | 90.5 | +0.7 | +0.7% |
| yolo26l.dxnn | 67.2 | 66.3 | +0.8 | +1.2% |
| yolo26x.dxnn | 38.7 | 38.4 | +0.3 | +0.9% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 213.1 ±0.3 | 16.22 | 267 | 79.6 | 98.5 | 54~55 | 1000 | 138 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 126.7 ±0.1 | 27.26 | 194 | 89.3 | 100.0 | 56~58 | 1000 | 153 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 87.9 ±0.1 | 39.31 | 165 | 92.6 | 100.0 | 60~65 | 1000 | 175 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 65.2 ±0.1 | 52.98 | 144 | 93.1 | 100.0 | 60~66 | 1000 | 184 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 37.7 ±0.2 | 91.66 | 114 | 94.9 | 100.0 | 67~75 | 1000 | 325 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | mppvideodec | 3455 | 3 | 216.3 ±0.2 | 15.98 | 196 | 80.2 | 100.0 | 53~55 | 1000 | 129 | ok |
| yolo26s-pose.dxnn | mppvideodec | 3455 | 3 | 126.0 ±0.5 | 27.43 | 168 | 89.1 | 100.0 | 55~58 | 1000 | 144 | ok |
| yolo26m-pose.dxnn | mppvideodec | 3455 | 3 | 87.8 ±0.1 | 39.33 | 138 | 92.2 | 100.0 | 59~65 | 1000 | 166 | ok |
| yolo26l-pose.dxnn | mppvideodec | 3455 | 3 | 65.2 ±0.2 | 53.02 | 115 | 93.4 | 100.0 | 60~66 | 1000 | 174 | ok |
| yolo26x-pose.dxnn | mppvideodec | 3455 | 3 | 37.8 ±0.3 | 91.41 | 88 | 94.7 | 100.0 | 67~75 | 1000 | 325 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-pose.dxnn | 213.1 | 216.3 | -3.2 | -1.5% |
| yolo26s-pose.dxnn | 126.7 | 126.0 | +0.8 | +0.6% |
| yolo26m-pose.dxnn | 87.9 | 87.8 | +0.0 | +0.0% |
| yolo26l-pose.dxnn | 65.2 | 65.2 | +0.0 | +0.1% |
| yolo26x-pose.dxnn | 37.7 | 37.8 | -0.1 | -0.3% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 115.5 ±1.3 | 29.92 | 373 | 40.8 | 69.9 | 53~56 | 1000 | 246 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 98.8 ±0.1 | 34.97 | 321 | 83.7 | 95.4 | 57~61 | 1000 | 256 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 65.4 ±0.2 | 52.86 | 230 | 92.6 | 100.0 | 64~71 | 1000 | 283 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 52.3 ±0.1 | 66.09 | 201 | 93.7 | 100.0 | 66~74 | 1000 | 291 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 27.0 ±2.2 | 127.80 | 132 | 94.7 | 100.0 | 75~82 | 600~1000 | 362 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | mppvideodec | 3455 | 3 | 86.8 ±0.4 | 39.82 | 268 | 28.0 | 90.5 | 53~55 | 1000 | 281 | ok |
| yolo26s-seg.dxnn | mppvideodec | 3455 | 3 | 85.9 ±0.2 | 40.22 | 273 | 61.9 | 95.2 | 56~60 | 1000 | 296 | ok |
| yolo26m-seg.dxnn | mppvideodec | 3455 | 3 | 65.4 ±0.2 | 52.81 | 238 | 93.4 | 100.0 | 64~73 | 1000 | 306 | ok |
| yolo26l-seg.dxnn | mppvideodec | 3455 | 3 | 52.1 ±0.1 | 66.37 | 203 | 94.4 | 100.0 | 66~74 | 1000 | 315 | ok |
| yolo26x-seg.dxnn | mppvideodec | 3455 | 3 | 26.8 ±2.6 | 128.85 | 133 | 94.9 | 100.0 | 75~81 | 600~1000 | 367 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-seg.dxnn | 115.5 | 86.8 | +28.7 | +33.1% |
| yolo26s-seg.dxnn | 98.8 | 85.9 | +12.9 | +15.0% |
| yolo26m-seg.dxnn | 65.4 | 65.4 | -0.1 | -0.1% |
| yolo26l-seg.dxnn | 52.3 | 52.1 | +0.2 | +0.4% |
| yolo26x-seg.dxnn | 27.0 | 26.8 | +0.2 | +0.9% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 74.4 ±0.1 | 35.50 | 173 | 91.8 | 100.0 | 54~57 | 1000 | 165 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.5 ±0.0 | 60.63 | 129 | 94.2 | 100.0 | 58~62 | 1000 | 181 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 31.9 ±0.1 | 82.79 | 115 | 94.1 | 100.0 | 64~71 | 1000 | 204 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 23.4 ±0.0 | 113.07 | 94 | 95.3 | 100.0 | 66~73 | 1000 | 214 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 13.4 ±0.3 | 197.03 | 56 | 93.1 | 100.0 | 74~79 | 800~1000 | 334 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | mppvideodec | 2640 | 3 | 74.1 ±0.1 | 35.62 | 181 | 92.4 | 100.0 | 55~57 | 1000 | 160 | ok |
| yolo26s-obb.dxnn | mppvideodec | 2640 | 3 | 43.5 ±0.0 | 60.61 | 140 | 93.4 | 100.0 | 58~62 | 1000 | 180 | ok |
| yolo26m-obb.dxnn | mppvideodec | 2640 | 3 | 31.9 ±0.1 | 82.81 | 122 | 94.1 | 100.0 | 64~70 | 1000 | 201 | ok |
| yolo26l-obb.dxnn | mppvideodec | 2640 | 3 | 23.3 ±0.0 | 113.11 | 98 | 95.3 | 100.0 | 66~73 | 1000 | 212 | ok |
| yolo26x-obb.dxnn | mppvideodec | 2640 | 3 | 13.4 ±0.4 | 197.55 | 60 | 92.9 | 100.0 | 74~79 | 800~1000 | 334 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-obb.dxnn | 74.4 | 74.1 | +0.2 | +0.3% |
| yolo26s-obb.dxnn | 43.5 | 43.5 | -0.0 | -0.0% |
| yolo26m-obb.dxnn | 31.9 | 31.9 | +0.0 | +0.0% |
| yolo26l-obb.dxnn | 23.4 | 23.3 | +0.0 | +0.0% |
| yolo26x-obb.dxnn | 13.4 | 13.4 | +0.0 | +0.3% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 1066.2 ±10.9 | 3.24 | 189 | 14.2 | 53.0 | 50 | 1000 | 55 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 1065.1 ±12.1 | 3.24 | 189 | 27.6 | 70.5 | 51 | 1000 | 67 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 1066.1 ±11.5 | 3.24 | 187 | 41.8 | 85.1 | 52 | 1000 | 91 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 833.2 ±2.0 | 4.15 | 163 | 58.6 | 98.6 | 52 | 1000 | 103 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 446.0 ±3.2 | 7.75 | 123 | 66.7 | 99.3 | 53~54 | 1000 | 179 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-cls.dxnn | mppvideodec | 3455 | 3 | 1062.8 ±5.8 | 3.25 | 187 | 16.4 | 52.2 | 50 | 1000 | 55 | ok |
| yolo26s-cls.dxnn | mppvideodec | 3455 | 3 | 1066.7 ±12.1 | 3.24 | 188 | 26.2 | 69.2 | 51 | 1000 | 67 | ok |
| yolo26m-cls.dxnn | mppvideodec | 3455 | 3 | 1066.7 ±2.1 | 3.24 | 186 | 42.0 | 87.3 | 52 | 1000 | 91 | ok |
| yolo26l-cls.dxnn | mppvideodec | 3455 | 3 | 837.3 ±1.4 | 4.13 | 165 | 57.3 | 98.4 | 52 | 1000 | 103 | ok |
| yolo26x-cls.dxnn | mppvideodec | 3455 | 3 | 447.2 ±1.6 | 7.72 | 129 | 66.1 | 98.8 | 53~54 | 1000 | 179 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26n-cls.dxnn | 1066.2 | 1062.8 | +3.4 | +0.3% |
| yolo26s-cls.dxnn | 1065.1 | 1066.7 | -1.6 | -0.1% |
| yolo26m-cls.dxnn | 1066.1 | 1066.7 | -0.6 | -0.1% |
| yolo26l-cls.dxnn | 833.2 | 837.3 | -4.0 | -0.5% |
| yolo26x-cls.dxnn | 446.0 | 447.2 | -1.2 | -0.3% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 5 | 3 | 171.0 ±0.7 | 34.2 | 284 | 55.1 | 86.8 | 59~62 | 1000 | 174 | ok |
| yolo26n.dxnn | 6 | 3 | 169.7 ±0.9 | 28.3 | 300 | 54.3 | 86.5 | 65~66 | 1000 | 177 | ok |
| yolo26s.dxnn | 4 | 3 | 129.4 ±0.1 | 32.4 | 235 | 93.5 | 100.0 | 66~71 | 1000 | 186 | ok |
| yolo26s.dxnn | 5 | 3 | 129.8 ±0.1 | 26.0 | 233 | 94.5 | 100.0 | 74~76 | 1000 | 192 | ok |
| yolo26m.dxnn | 3 | 3 | 88.7 ±3.6 | 29.6 | 192 | 96.2 | 100.0 | 76~81 | 1000 | 202 | ok |
| yolo26m.dxnn | 2 | 3 | 82.2 ±0.9 | 41.1 | 188 | 95.1 | 100.0 | 82 | 800~1000 | 194 | ok |
| yolo26l.dxnn | 2 | 3 | 67.1 ±0.4 | 33.5 | 173 | 95.4 | 100.0 | 74~78 | 1000 | 204 | ok |
| yolo26l.dxnn | 3 | 3 | 61.5 ±0.1 | 20.5 | 170 | 97.2 | 100.0 | 80~81 | 1000 | 211 | ok |
| yolo26x.dxnn | 1 | 3 | 38.7 ±0.0 | 38.7 | 131 | 95.7 | 100.0 | 68~75 | 1000 | 314 | ok |
| yolo26x.dxnn | 2 | 3 | 34.3 ±1.1 | 17.1 | 121 | 95.7 | 100.0 | 81~82 | 800~1000 | 314 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n.dxnn | 3 | 3 | 99.9 ±0.6 | 33.3 | 219 | 27.4 | 85.2 | 55~56 | 1000 | 186 | ok |
| yolo26n.dxnn | 4 | 3 | 100.3 ±0.3 | 25.1 | 220 | 27.5 | 85.4 | 58~59 | 1000 | 199 | ok |
| yolo26s.dxnn | 3 | 3 | 100.0 ±0.4 | 33.3 | 214 | 55.7 | 88.5 | 62~65 | 1000 | 203 | ok |
| yolo26s.dxnn | 4 | 3 | 100.0 ±0.5 | 25.0 | 223 | 56.4 | 88.5 | 68~69 | 1000 | 212 | ok |
| yolo26m.dxnn | 3 | 3 | 87.6 ±3.6 | 29.2 | 230 | 96.8 | 100.0 | 76~81 | 1000 | 220 | ok |
| yolo26m.dxnn | 2 | 3 | 81.5 ±0.4 | 40.8 | 222 | 95.2 | 100.0 | 82 | 800~1000 | 210 | ok |
| yolo26l.dxnn | 2 | 3 | 66.4 ±0.2 | 33.2 | 201 | 95.3 | 100.0 | 74~79 | 1000 | 218 | ok |
| yolo26l.dxnn | 3 | 3 | 61.1 ±0.3 | 20.4 | 193 | 96.8 | 100.0 | 80~81 | 1000 | 224 | ok |
| yolo26x.dxnn | 1 | 3 | 38.4 ±0.2 | 38.4 | 150 | 94.6 | 100.0 | 67~75 | 1000 | 314 | ok |
| yolo26x.dxnn | 2 | 3 | 34.5 ±0.9 | 17.2 | 142 | 96.1 | 100.0 | 81~82 | 800~1000 | 314 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n.dxnn | 5 | 34.2 | 3 | 33.3 |
| yolo26s.dxnn | 4 | 32.4 | 3 | 33.3 |
| yolo26m.dxnn | 2 | 41.1 | 2 | 40.8 |
| yolo26l.dxnn | 2 | 33.5 | 2 | 33.2 |
| yolo26x.dxnn | 1 | 38.7 | 1 | 38.4 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 7 | 3 | 214.0 ±0.1 | 30.6 | 278 | 91.6 | 99.1 | 64~69 | 1000 | 185 | ok |
| yolo26n-pose.dxnn | 8 | 3 | 214.2 ±0.2 | 26.8 | 279 | 92.2 | 98.9 | 72~74 | 1000 | 190 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 126.8 ±0.3 | 31.7 | 197 | 96.0 | 100.0 | 66~71 | 1000 | 182 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 127.2 ±0.1 | 25.4 | 197 | 95.5 | 100.0 | 74~76 | 1000 | 188 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 87.9 ±0.1 | 44.0 | 169 | 95.6 | 100.0 | 72~77 | 1000 | 189 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 81.4 ±0.8 | 27.1 | 161 | 95.8 | 100.0 | 80~81 | 1000 | 197 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 65.4 ±0.1 | 32.7 | 147 | 94.8 | 100.0 | 73~78 | 1000 | 198 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 60.8 ±0.2 | 20.3 | 140 | 96.7 | 100.0 | 79~80 | 1000 | 208 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.7 ±0.2 | 37.7 | 114 | 94.9 | 100.0 | 67~75 | 1000 | 325 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 34.2 ±0.9 | 17.1 | 108 | 96.3 | 100.0 | 81 | 800~1000 | 325 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-pose.dxnn | 7 | 3 | 217.3 ±0.0 | 31.0 | 207 | 95.6 | 100.0 | 63~68 | 1000 | 182 | ok |
| yolo26n-pose.dxnn | 8 | 3 | 217.4 ±0.1 | 27.2 | 206 | 95.6 | 100.0 | 71~72 | 1000 | 189 | ok |
| yolo26s-pose.dxnn | 4 | 3 | 126.3 ±0.1 | 31.6 | 169 | 96.5 | 100.0 | 66~69 | 1000 | 177 | ok |
| yolo26s-pose.dxnn | 5 | 3 | 126.4 ±0.1 | 25.3 | 170 | 97.2 | 100.0 | 72~73 | 1000 | 184 | ok |
| yolo26m-pose.dxnn | 2 | 3 | 87.9 ±0.1 | 44.0 | 143 | 95.6 | 100.0 | 72~76 | 1000 | 180 | ok |
| yolo26m-pose.dxnn | 3 | 3 | 82.7 ±1.4 | 27.6 | 132 | 96.5 | 100.0 | 79~81 | 1000 | 190 | ok |
| yolo26l-pose.dxnn | 2 | 3 | 65.4 ±0.1 | 32.7 | 118 | 96.1 | 100.0 | 73~77 | 1000 | 188 | ok |
| yolo26l-pose.dxnn | 3 | 3 | 61.7 ±0.3 | 20.6 | 112 | 97.2 | 100.0 | 79~80 | 1000 | 199 | ok |
| yolo26x-pose.dxnn | 1 | 3 | 37.8 ±0.3 | 37.8 | 88 | 94.7 | 100.0 | 67~75 | 1000 | 325 | ok |
| yolo26x-pose.dxnn | 2 | 3 | 34.4 ±0.6 | 17.2 | 84 | 96.4 | 100.0 | 81 | 800~1000 | 325 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-pose.dxnn | 7 | 30.6 | 7 | 31.0 |
| yolo26s-pose.dxnn | 4 | 31.7 | 4 | 31.6 |
| yolo26m-pose.dxnn | 2 | 44.0 | 2 | 44.0 |
| yolo26l-pose.dxnn | 2 | 32.7 | 2 | 32.7 |
| yolo26x-pose.dxnn | 1 | 37.7 | 1 | 37.8 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 3 | 3 | 115.9 ±0.1 | 38.6 | 370 | 44.2 | 70.5 | 62~66 | 1000 | 273 | ok |
| yolo26n-seg.dxnn | 4 | 3 | 115.7 ±0.3 | 28.9 | 380 | 44.0 | 69.7 | 69~71 | 1000 | 287 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 99.2 ±0.0 | 33.1 | 325 | 88.8 | 95.3 | 71~77 | 1000 | 289 | ok |
| yolo26s-seg.dxnn | 4 | 3 | 93.2 ±0.5 | 23.3 | 304 | 94.3 | 100.0 | 80~81 | 1000 | 303 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 55.2 ±3.7 | 27.6 | 204 | 93.7 | 100.0 | 81~82 | 600~1000 | 307 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 65.4 ±0.2 | 65.4 | 230 | 92.6 | 100.0 | 64~71 | 1000 | 283 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 52.3 ±0.1 | 52.3 | 201 | 93.7 | 100.0 | 66~74 | 1000 | 291 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 43.7 ±2.0 | 21.9 | 182 | 95.7 | 100.0 | 82~83 | 600~1000 | 312 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 27.0 ±2.2 | 27.0 | 132 | 94.7 | 100.0 | 75~82 | 600~1000 | 362 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-seg.dxnn | 2 | 3 | 86.0 ±1.6 | 43.0 | 277 | 28.5 | 90.4 | 58~60 | 1000 | 303 | ok |
| yolo26n-seg.dxnn | 3 | 3 | 86.6 ±0.1 | 28.9 | 271 | 29.2 | 91.4 | 62~64 | 1000 | 319 | ok |
| yolo26s-seg.dxnn | 2 | 3 | 85.1 ±1.3 | 42.6 | 273 | 62.8 | 95.0 | 66~69 | 1000 | 319 | ok |
| yolo26s-seg.dxnn | 3 | 3 | 85.5 ±0.5 | 28.5 | 274 | 64.0 | 95.3 | 73~75 | 1000 | 334 | ok |
| yolo26m-seg.dxnn | 2 | 3 | 54.1 ±3.8 | 27.1 | 217 | 95.1 | 100.0 | 81~82 | 400~1000 | 329 | ok |
| yolo26m-seg.dxnn | 1 | 3 | 65.4 ±0.2 | 65.4 | 238 | 93.4 | 100.0 | 64~73 | 1000 | 306 | ok |
| yolo26l-seg.dxnn | 1 | 3 | 52.1 ±0.1 | 52.1 | 203 | 94.4 | 100.0 | 66~74 | 1000 | 315 | ok |
| yolo26l-seg.dxnn | 2 | 3 | 44.5 ±1.6 | 22.2 | 187 | 96.3 | 100.0 | 82 | 600~1000 | 332 | ok |
| yolo26x-seg.dxnn | 1 | 3 | 26.8 ±2.6 | 26.8 | 133 | 94.9 | 100.0 | 75~81 | 600~1000 | 367 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-seg.dxnn | 3 | 38.6 | 2 | 43.0 |
| yolo26s-seg.dxnn | 3 | 33.1 | 2 | 42.6 |
| yolo26m-seg.dxnn | 1 | 65.4 | 1 | 65.4 |
| yolo26l-seg.dxnn | 1 | 52.3 | 1 | 52.1 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.5 ±0.0 | 37.2 | 174 | 94.8 | 100.0 | 61~64 | 1000 | 180 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.5 ±0.0 | 24.8 | 173 | 95.8 | 100.0 | 67~68 | 1000 | 194 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.5 ±0.0 | 43.5 | 129 | 94.2 | 100.0 | 58~62 | 1000 | 181 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.6 ±0.0 | 21.8 | 131 | 96.1 | 100.0 | 67~69 | 1000 | 197 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.1 | 31.9 | 115 | 94.1 | 100.0 | 64~71 | 1000 | 204 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 30.6 ±1.2 | 15.3 | 113 | 96.4 | 100.0 | 78~79 | 1000 | 220 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.4 ±0.0 | 23.4 | 94 | 95.3 | 100.0 | 66~73 | 1000 | 214 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.4 ±0.3 | 13.4 | 56 | 93.1 | 100.0 | 74~79 | 800~1000 | 334 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26n-obb.dxnn | 2 | 3 | 74.2 ±0.0 | 37.1 | 185 | 95.1 | 100.0 | 61~64 | 1000 | 175 | ok |
| yolo26n-obb.dxnn | 3 | 3 | 74.3 ±0.1 | 24.8 | 185 | 96.2 | 100.0 | 66~68 | 1000 | 190 | ok |
| yolo26s-obb.dxnn | 1 | 3 | 43.5 ±0.0 | 43.5 | 140 | 93.4 | 100.0 | 58~62 | 1000 | 180 | ok |
| yolo26s-obb.dxnn | 2 | 3 | 43.6 ±0.0 | 21.8 | 140 | 96.0 | 100.0 | 67~69 | 1000 | 197 | ok |
| yolo26m-obb.dxnn | 1 | 3 | 31.9 ±0.1 | 31.9 | 122 | 94.1 | 100.0 | 64~70 | 1000 | 201 | ok |
| yolo26m-obb.dxnn | 2 | 3 | 30.8 ±1.2 | 15.4 | 119 | 96.5 | 100.0 | 78~79 | 1000 | 226 | ok |
| yolo26l-obb.dxnn | 1 | 3 | 23.3 ±0.0 | 23.3 | 98 | 95.3 | 100.0 | 66~73 | 1000 | 212 | ok |
| yolo26x-obb.dxnn | 1 | 3 | 13.4 ±0.4 | 13.4 | 60 | 92.9 | 100.0 | 74~79 | 800~1000 | 334 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26n-obb.dxnn | 2 | 37.2 | 2 | 37.1 |
| yolo26s-obb.dxnn | 1 | 43.5 | 1 | 43.5 |
| yolo26m-obb.dxnn | 1 | 31.9 | 1 | 31.9 |

---
*Report generated by dx-benchmark tool*
