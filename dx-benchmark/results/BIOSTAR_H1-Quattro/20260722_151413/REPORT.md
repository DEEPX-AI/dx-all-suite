# YOLO26 Benchmark Report

**Generated:** 2026-07-29 10:29:14 (Local)

## Test Timing

| # | Type | Start | End | Duration |
|---|------|-------|-----|----------|
| 1 | run | 2026-07-22 15:14:13 | 2026-07-23 14:33:40 | 23h 19m 27s |

## Executive Summary

### Object Detection

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_640x640.dxnn | ON | 10.56 | 1052.6 | 496.8 | 17 |
| yolo26-n_640x640.dxnn | OFF | 10.38 | 1326.0 | 452.1 | 14 |
| yolo26-s_640x640.dxnn | ON | 16.52 | 790.3 | 494.4 | 17 |
| yolo26-s_640x640.dxnn | OFF | 16.28 | 794.0 | 447.1 | 14 |
| yolo26-m_640x640.dxnn | ON | 23.69 | 491.5 | 491.7 | 16 |
| yolo26-m_640x640.dxnn | OFF | 23.31 | 491.1 | 453.4 | 14 |
| yolo26-l_640x640.dxnn | ON | 31.24 | 372.4 | 367.8 | 12 |
| yolo26-l_640x640.dxnn | OFF | 30.80 | 372.5 | 369.3 | 12 |
| yolo26-x_640x640.dxnn | ON | 56.60 | 202.2 | 202.6 | 6 |
| yolo26-x_640x640.dxnn | OFF | 56.22 | 201.8 | 201.2 | 6 |

### Pose Estimation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-pose_640x640.dxnn | ON | 10.37 | 1220.1 | 540.4 | 19 |
| yolo26-n-pose_640x640.dxnn | OFF | 10.32 | 1174.2 | 553.9 | 20 |
| yolo26-s-pose_640x640.dxnn | ON | 16.61 | 728.5 | 540.3 | 19 |
| yolo26-s-pose_640x640.dxnn | OFF | 16.42 | 731.0 | 554.1 | 19 |
| yolo26-m-pose_640x640.dxnn | ON | 24.04 | 469.4 | 468.4 | 15 |
| yolo26-m-pose_640x640.dxnn | OFF | 24.56 | 468.6 | 467.9 | 15 |
| yolo26-l-pose_640x640.dxnn | ON | 31.52 | 356.7 | 351.4 | 11 |
| yolo26-l-pose_640x640.dxnn | OFF | 31.00 | 356.3 | 354.2 | 11 |
| yolo26-x-pose_640x640.dxnn | ON | 57.10 | 195.8 | 195.8 | 6 |
| yolo26-x-pose_640x640.dxnn | OFF | 56.97 | 195.6 | 195.8 | 6 |

### Segmentation

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-seg_640x640.dxnn | ON | 18.70 | 563.9 | 360.8 | 12 |
| yolo26-n-seg_640x640.dxnn | OFF | 18.20 | 592.9 | 319.6 | 10 |
| yolo26-s-seg_640x640.dxnn | ON | 26.54 | 569.2 | 359.7 | 12 |
| yolo26-s-seg_640x640.dxnn | OFF | 26.02 | 575.8 | 313.9 | 10 |
| yolo26-m-seg_640x640.dxnn | ON | 40.05 | 327.3 | 319.5 | 10 |
| yolo26-m-seg_640x640.dxnn | OFF | 40.11 | 321.5 | 314.9 | 10 |
| yolo26-l-seg_640x640.dxnn | ON | 47.59 | 264.1 | 263.7 | 8 |
| yolo26-l-seg_640x640.dxnn | OFF | 46.83 | 264.3 | 262.0 | 8 |
| yolo26-x-seg_640x640.dxnn | ON | 84.99 | 141.4 | 140.0 | 4 |
| yolo26-x-seg_640x640.dxnn | OFF | 84.51 | 142.1 | 141.3 | 4 |

### Oriented BBox (OBB)

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n-obb_1024x1024.dxnn | ON | 22.90 | 422.2 | 391.9 | 14 |
| yolo26-n-obb_1024x1024.dxnn | OFF | 22.59 | 424.0 | 392.9 | 14 |
| yolo26-s-obb_1024x1024.dxnn | ON | 38.19 | 264.5 | 260.5 | 8 |
| yolo26-s-obb_1024x1024.dxnn | OFF | 38.11 | 263.3 | 263.2 | 8 |
| yolo26-m-obb_1024x1024.dxnn | ON | 56.36 | 174.8 | 173.6 | 5 |
| yolo26-m-obb_1024x1024.dxnn | OFF | 55.30 | 174.4 | 175.9 | 5 |
| yolo26-l-obb_1024x1024.dxnn | ON | 74.09 | 129.5 | 129.6 | 4 |
| yolo26-l-obb_1024x1024.dxnn | OFF | 73.91 | 129.8 | 129.1 | 4 |
| yolo26-x-obb_1024x1024.dxnn | ON | 142.38 | 70.3 | 71.0 | 2 |
| yolo26-x-obb_1024x1024.dxnn | OFF | 142.07 | 70.5 | 71.0 | 2 |

### Classification

| Model | ORT | Latency (ms) | Throughput (FPS) | E2E FPS | Max Channels |
|-------|-----|:------------:|:----------------:|:-------:|:------------:|
| yolo26-n_224x224.dxnn | ON | 1.04 | 14707.2 | 763.6 | — |
| yolo26-n_224x224.dxnn | OFF | 1.02 | 14704.0 | 772.4 | — |
| yolo26-s_224x224.dxnn | ON | 1.63 | 8171.0 | 772.1 | — |
| yolo26-s_224x224.dxnn | OFF | 1.67 | 8167.0 | 773.6 | — |
| yolo26-m_224x224.dxnn | ON | 2.20 | 5478.2 | 757.6 | — |
| yolo26-m_224x224.dxnn | OFF | 2.29 | 5514.7 | 770.0 | — |
| yolo26-l_224x224.dxnn | ON | 3.45 | 3490.2 | 760.6 | — |
| yolo26-l_224x224.dxnn | OFF | 3.49 | 3512.1 | 755.1 | — |
| yolo26-x_224x224.dxnn | ON | 5.98 | 1950.4 | 742.8 | — |
| yolo26-x_224x224.dxnn | OFF | 6.07 | 1956.8 | 744.5 | — |

## Environment

| Item | Value |
|------|-------|
| Product | BIOSTAR |
| Hostname | deepx-B650MT |
| OS | Ubuntu 22.04.5 LTS |
| Kernel | 6.8.0-124-generic |
| CPU | AMD Ryzen 5 9600X 6-Core Processor |
| CPU Cores | 12 |
| RAM | 30.5 GB |
| NPU SKU | H1-Quattro |
| DX-AllSuite | v2.4.0 |
| Benchmark Tool | 0.1.0 |
| NPU RT | v3.4.0 |
| NPU RT (commit) | v3.4.0+5474c9f |
| NPU Driver (RT) | v2.5.1 |
| NPU Driver (PCIe) | v2.4.1 |
| NPU Firmware | v2.7.3 |
| NPU Memory | LPDDR5x 6000 Mbps, 3.92GiB |
| NPU Board | H1, Rev 0.0 |
| NPU PCIe | Gen3 X4 [04:00:00] |

### Tools

| Tool | Available | Version |
|------|-----------|---------|
| run_model | Yes | DXRT v3.4.0 run_model |
| dxrt-cli | Yes | unknown |
| gst-launch-1.0 | Yes | gst-launch-1.0 version 1.20.3 |
| gst-inspect-1.0 | Yes | gst-inspect-1.0 version 1.20.3 |
| time | Yes | unknown |
| ffprobe | Yes | ffprobe version 4.4.2-0ubuntu0.22.04.1 Copyright (c) 2007-20... |
| dxtop | Yes | DX-TOP 1.1.0 |

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
| Version | v1 |
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
| yolo26-n_640x640.dxnn | Object Detection | 640×640 | 117.8 | Yes | ✅ |
| yolo26-s_640x640.dxnn | Object Detection | 640×640 | 151.9 | Yes | ✅ |
| yolo26-m_640x640.dxnn | Object Detection | 640×640 | 244.6 | Yes | ✅ |
| yolo26-l_640x640.dxnn | Object Detection | 640×640 | 297.6 | Yes | ✅ |
| yolo26-x_640x640.dxnn | Object Detection | 640×640 | 528.8 | Yes | ✅ |
| yolo26-n-pose_640x640.dxnn | Pose Estimation | 640×640 | 119.8 | Yes | ✅ |
| yolo26-s-pose_640x640.dxnn | Pose Estimation | 640×640 | 157.9 | Yes | ✅ |
| yolo26-m-pose_640x640.dxnn | Pose Estimation | 640×640 | 256.7 | Yes | ✅ |
| yolo26-l-pose_640x640.dxnn | Pose Estimation | 640×640 | 309.6 | Yes | ✅ |
| yolo26-x-pose_640x640.dxnn | Pose Estimation | 640×640 | 522.6 | Yes | ✅ |
| yolo26-n-seg_640x640.dxnn | Segmentation | 640×640 | 140.2 | Yes | ✅ |
| yolo26-s-seg_640x640.dxnn | Segmentation | 640×640 | 177.9 | Yes | ✅ |
| yolo26-m-seg_640x640.dxnn | Segmentation | 640×640 | 272.8 | Yes | ✅ |
| yolo26-l-seg_640x640.dxnn | Segmentation | 640×640 | 325.8 | Yes | ✅ |
| yolo26-x-seg_640x640.dxnn | Segmentation | 640×640 | 561.1 | Yes | ✅ |
| yolo26-n-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 243.5 | Yes | ✅ |
| yolo26-s-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 379.6 | Yes | ✅ |
| yolo26-m-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 651.2 | Yes | ✅ |
| yolo26-l-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 799.0 | Yes | ✅ |
| yolo26-x-obb_1024x1024.dxnn | Oriented BBox (OBB) | 1024×1024 | 1330.5 | Yes | ✅ |
| yolo26-n_224x224.dxnn | Classification | 224×224 | 5.1 | No | — |
| yolo26-s_224x224.dxnn | Classification | 224×224 | 10.0 | No | — |
| yolo26-m_224x224.dxnn | Classification | 224×224 | 14.8 | No | — |
| yolo26-l_224x224.dxnn | Classification | 224×224 | 19.9 | No | — |
| yolo26-x_224x224.dxnn | Classification | 224×224 | 49.2 | No | — |

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
| yolo26-n_640x640.dxnn | 1052.6 ±2.1 | 8 | 296 | 68.6 | 84.0 | 46~48 | 1000 | ok |
| yolo26-s_640x640.dxnn | 790.3 ±3.8 | 7 | 194 | 93.1 | 100.0 | 56~58 | 1000 | ok |
| yolo26-m_640x640.dxnn | 491.5 ±0.6 | 4 | 112 | 90.0 | 100.0 | 59~62 | 1000 | ok |
| yolo26-l_640x640.dxnn | 372.4 ±1.1 | 4 | 83 | 90.0 | 100.0 | 59~62 | 1000 | ok |
| yolo26-x_640x640.dxnn | 202.2 ±0.5 | 4 | 44 | 89.7 | 100.0 | 60~64 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 8 | [3]:884.6 · [4]:1050.8 · [5]:1050.2 · [6]:1037.5 · [7]:1061.7 · **[8]:1063.8 ★** · [9]:1051.0 · [10]:1040.8 |
| yolo26-s_640x640.dxnn | 7 | [3]:608.0 · [4]:776.2 · [5]:784.0 · [6]:774.4 · **[7]:796.3 ★** · [8]:792.2 |
| yolo26-m_640x640.dxnn | 4 | [3]:420.2 · **[4]:491.5 ★** · [5]:486.3 · [6]:474.2 · [7]:476.6 · [8]:472.3 |
| yolo26-l_640x640.dxnn | 4 | [3]:319.0 · **[4]:369.0 ★** · [5]:356.9 · [6]:352.5 · [7]:348.3 · [8]:352.8 |
| yolo26-x_640x640.dxnn | 4 | [3]:183.2 · **[4]:202.2 ★** · [5]:195.7 · [6]:192.8 · [7]:193.4 · [8]:195.2 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_640x640.dxnn | 1326.0 ±5.6 | 5 | 237 | 90.2 | 100.0 | 54~56 | 1000 | ok |
| yolo26-s_640x640.dxnn | 794.0 ±1.6 | 8 | 129 | 89.9 | 100.0 | 56~58 | 1000 | ok |
| yolo26-m_640x640.dxnn | 491.1 ±1.4 | 4 | 74 | 90.2 | 100.0 | 59~61 | 1000 | ok |
| yolo26-l_640x640.dxnn | 372.5 ±0.8 | 4 | 55 | 91.5 | 100.0 | 59~62 | 1000 | ok |
| yolo26-x_640x640.dxnn | 201.8 ±0.3 | 4 | 29 | 90.1 | 100.0 | 60~64 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_640x640.dxnn | 5 | [3]:921.7 · [4]:1154.3 · **[5]:1314.6 ★** · [6]:1252.6 · [7]:1277.2 · [8]:1273.0 |
| yolo26-s_640x640.dxnn | 8 | [3]:615.6 · [4]:771.4 · [5]:752.7 · [6]:768.2 · [7]:789.1 · **[8]:799.0 ★** · [9]:789.3 · [10]:790.9 |
| yolo26-m_640x640.dxnn | 4 | [3]:408.5 · **[4]:493.5 ★** · [5]:474.5 · [6]:475.4 · [7]:471.6 · [8]:472.3 |
| yolo26-l_640x640.dxnn | 4 | [3]:306.4 · **[4]:372.7 ★** · [5]:353.8 · [6]:352.5 · [7]:354.2 · [8]:358.5 |
| yolo26-x_640x640.dxnn | 4 | [3]:169.4 · **[4]:199.1 ★** · [5]:194.8 · [6]:193.3 · [7]:193.1 · [8]:193.3 |


#### Pose Estimation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 1220.1 ±6.6 | 5 | 212 | 90.5 | 100.0 | 55~57 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 728.5 ±2.4 | 4 | 117 | 89.3 | 100.0 | 56~58 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 469.4 ±1.6 | 4 | 72 | 89.8 | 100.0 | 60~63 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 356.7 ±0.6 | 4 | 55 | 90.3 | 100.0 | 59~62 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 195.8 ±0.5 | 4 | 31 | 89.3 | 100.0 | 60~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 5 | [3]:912.7 · [4]:1145.5 · **[5]:1233.5 ★** · [6]:1177.5 · [7]:1169.1 · [8]:1167.6 |
| yolo26-s-pose_640x640.dxnn | 4 | [3]:596.0 · **[4]:733.9 ★** · [5]:712.1 · [6]:709.0 · [7]:728.5 · [8]:733.5 |
| yolo26-m-pose_640x640.dxnn | 4 | [3]:403.7 · **[4]:470.7 ★** · [5]:457.7 · [6]:460.3 · [7]:461.1 · [8]:465.8 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:315.0 · **[4]:352.2 ★** · [5]:341.2 · [6]:339.1 · [7]:341.7 · [8]:335.5 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:174.5 · **[4]:196.8 ★** · [5]:189.8 · [6]:188.4 · [7]:189.0 · [8]:189.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 1174.2 ±13.2 | 4 | 129 | 83.9 | 98.8 | 54~56 | 1000 | ok |
| yolo26-s-pose_640x640.dxnn | 731.0 ±3.6 | 8 | 78 | 90.3 | 100.0 | 56~58 | 1000 | ok |
| yolo26-m-pose_640x640.dxnn | 468.6 ±2.2 | 4 | 46 | 89.6 | 100.0 | 59~63 | 1000 | ok |
| yolo26-l-pose_640x640.dxnn | 356.3 ±2.1 | 4 | 35 | 89.5 | 100.0 | 59~62 | 1000 | ok |
| yolo26-x-pose_640x640.dxnn | 195.6 ±0.7 | 4 | 20 | 89.1 | 100.0 | 60~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-pose_640x640.dxnn | 4 | [3]:928.6 · **[4]:1183.4 ★** · [5]:1169.7 · [6]:1147.1 · [7]:1183.4 · [8]:1168.1 |
| yolo26-s-pose_640x640.dxnn | 8 | [3]:598.0 · [4]:731.9 · [5]:716.0 · [6]:724.6 · [7]:727.1 · **[8]:732.9 ★** · [9]:714.3 |
| yolo26-m-pose_640x640.dxnn | 4 | [3]:383.2 · **[4]:472.5 ★** · [5]:452.5 · [6]:454.5 · [7]:460.1 · [8]:460.4 |
| yolo26-l-pose_640x640.dxnn | 4 | [3]:295.0 · **[4]:357.0 ★** · [5]:340.0 · [6]:342.3 · [7]:341.5 · [8]:340.1 |
| yolo26-x-pose_640x640.dxnn | 4 | [3]:163.1 · **[4]:196.4 ★** · [5]:189.0 · [6]:187.4 · [7]:188.8 · [8]:189.1 |


#### Segmentation

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 563.9 ±1.5 | 6 | 490 | 43.0 | 72.8 | 52~53 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 569.2 ±1.4 | 6 | 486 | 89.3 | 100.0 | 57~60 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 327.3 ±2.2 | 6 | 254 | 90.3 | 100.0 | 62~66 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 264.1 ±0.3 | 4 | 197 | 90.4 | 100.0 | 61~64 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 141.4 ±0.3 | 4 | 102 | 88.7 | 100.0 | 61~65 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 6 | [3]:491.4 · [4]:561.2 · [5]:565.2 · **[6]:565.7 ★** · [7]:562.9 · [8]:562.4 |
| yolo26-s-seg_640x640.dxnn | 6 | [3]:382.1 · [4]:475.2 · [5]:549.0 · **[6]:568.8 ★** · [7]:568.7 · [8]:560.5 |
| yolo26-m-seg_640x640.dxnn | 6 | [3]:257.2 · [4]:312.6 · [5]:322.0 · **[6]:326.8 ★** · [7]:324.1 · [8]:324.6 |
| yolo26-l-seg_640x640.dxnn | 4 | [3]:217.1 · **[4]:266.0 ★** · [5]:261.8 · [6]:254.3 · [7]:254.9 · [8]:254.1 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:122.2 · **[4]:142.2 ★** · [5]:140.2 · [6]:136.8 · [7]:134.9 · [8]:135.0 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 592.9 ±1.1 | 6 | 414 | 47.8 | 72.3 | 53~55 | 1000 | ok |
| yolo26-s-seg_640x640.dxnn | 575.8 ±1.8 | 5 | 385 | 88.7 | 100.0 | 57~60 | 1000 | ok |
| yolo26-m-seg_640x640.dxnn | 321.5 ±1.6 | 8 | 206 | 91.3 | 100.0 | 63~66 | 1000 | ok |
| yolo26-l-seg_640x640.dxnn | 264.3 ±1.1 | 4 | 167 | 89.0 | 100.0 | 60~64 | 1000 | ok |
| yolo26-x-seg_640x640.dxnn | 142.1 ±0.4 | 4 | 87 | 89.9 | 100.0 | 61~65 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-seg_640x640.dxnn | 6 | [3]:540.4 · [4]:592.3 · [5]:595.7 · **[6]:597.9 ★** · [7]:594.1 · [8]:597.9 · [9]:595.2 · [10]:593.8 |
| yolo26-s-seg_640x640.dxnn | 5 | [3]:404.9 · [4]:509.4 · **[5]:577.2 ★** · [6]:576.2 · [7]:566.8 · [8]:553.8 |
| yolo26-m-seg_640x640.dxnn | 8 | [3]:262.9 · [4]:315.7 · [5]:311.5 · [6]:318.4 · [7]:322.3 · **[8]:322.8 ★** · [9]:318.6 · [10]:318.1 |
| yolo26-l-seg_640x640.dxnn | 4 | [3]:221.6 · **[4]:266.3 ★** · [5]:249.5 · [6]:255.1 · [7]:254.2 · [8]:257.5 |
| yolo26-x-seg_640x640.dxnn | 4 | [3]:124.5 · **[4]:142.1 ★** · [5]:134.4 · [6]:135.2 · [7]:135.3 · [8]:135.2 |


#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 422.2 ±1.8 | 4 | 76 | 87.2 | 100.0 | 54~56 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 264.5 ±1.1 | 4 | 46 | 89.3 | 100.0 | 56~58 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 174.8 ±0.3 | 4 | 30 | 90.6 | 100.0 | 59~63 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 129.5 ±0.5 | 4 | 23 | 89.5 | 100.0 | 58~61 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 70.3 ±0.8 | 4 | 14 | 87.4 | 100.0 | 59~63 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 4 | [3]:359.1 · **[4]:418.9 ★** · [5]:415.1 · [6]:410.9 · [7]:412.4 · [8]:412.1 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:213.9 · **[4]:262.2 ★** · [5]:250.9 · [6]:250.3 · [7]:248.7 · [8]:250.3 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:149.3 · **[4]:175.3 ★** · [5]:166.1 · [6]:169.2 · [7]:165.4 · [8]:165.5 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:110.1 · **[4]:130.0 ★** · [5]:123.0 · [6]:124.0 · [7]:123.1 · [8]:123.9 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:58.0 · **[4]:70.8 ★** · [5]:68.5 · [6]:68.0 · [7]:68.4 · [8]:68.2 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 424.0 ±1.1 | 4 | 52 | 86.4 | 100.0 | 54~56 | 1000 | ok |
| yolo26-s-obb_1024x1024.dxnn | 263.3 ±1.4 | 4 | 31 | 90.4 | 100.0 | 55~57 | 1000 | ok |
| yolo26-m-obb_1024x1024.dxnn | 174.4 ±0.2 | 4 | 20 | 90.4 | 100.0 | 59~62 | 1000 | ok |
| yolo26-l-obb_1024x1024.dxnn | 129.8 ±0.6 | 4 | 15 | 90.1 | 100.0 | 59~62 | 1000 | ok |
| yolo26-x-obb_1024x1024.dxnn | 70.5 ±1.0 | 4 | 9 | 88.2 | 100.0 | 59~62 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n-obb_1024x1024.dxnn | 4 | [3]:344.8 · **[4]:415.9 ★** · [5]:409.6 · [6]:412.7 · [7]:407.3 · [8]:411.4 |
| yolo26-s-obb_1024x1024.dxnn | 4 | [3]:212.7 · **[4]:265.1 ★** · [5]:247.8 · [6]:254.2 · [7]:251.9 · [8]:250.4 |
| yolo26-m-obb_1024x1024.dxnn | 4 | [3]:146.8 · **[4]:175.6 ★** · [5]:165.6 · [6]:165.7 · [7]:165.7 · [8]:165.3 |
| yolo26-l-obb_1024x1024.dxnn | 4 | [3]:102.1 · **[4]:130.2 ★** · [5]:124.3 · [6]:123.6 · [7]:125.4 · [8]:123.6 |
| yolo26-x-obb_1024x1024.dxnn | 4 | [3]:59.8 · **[4]:70.8 ★** · [5]:68.8 · [6]:67.8 · [7]:68.5 · [8]:68.5 |


#### Classification

**ORT = ON**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 14707.2 ±41.8 | 10 | 66 | 89.0 | 96.2 | 53~54 | 1000 | ok |
| yolo26-s_224x224.dxnn | 8171.0 ±6.8 | 10 | 35 | 91.6 | 97.4 | 55~56 | 1000 | ok |
| yolo26-m_224x224.dxnn | 5478.2 ±67.6 | 6 | 22 | 86.7 | 97.0 | 56~59 | 1000 | ok |
| yolo26-l_224x224.dxnn | 3490.2 ±16.1 | 6 | 14 | 89.3 | 98.5 | 55~57 | 1000 | ok |
| yolo26-x_224x224.dxnn | 1950.4 ±7.3 | 6 | 8 | 90.4 | 99.3 | 57~59 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 10 | [3]:9536.6 · [4]:13087.7 · [5]:13915.9 · [6]:14257.4 · [7]:13865.3 · [8]:14342.2 · [9]:14360.1 · **[10]:14781.9 ★** · [11]:14697.1 · [12]:14681.3 |
| yolo26-s_224x224.dxnn | 10 | [3]:5614.7 · [4]:7784.0 · [5]:7970.7 · [6]:7777.8 · [7]:7910.5 · [8]:8003.9 · [9]:7967.7 · **[10]:8183.6 ★** · [11]:8182.9 · [12]:8144.2 |
| yolo26-m_224x224.dxnn | 6 | [3]:4056.6 · [4]:5476.1 · [5]:5569.9 · **[6]:5584.2 ★** · [7]:5498.3 · [8]:5583.4 |
| yolo26-l_224x224.dxnn | 6 | [3]:2664.0 · [4]:3390.1 · [5]:3500.9 · **[6]:3525.9 ★** · [7]:3497.4 · [8]:3504.3 |
| yolo26-x_224x224.dxnn | 6 | [3]:1479.2 · [4]:1912.6 · [5]:1966.7 · **[6]:1976.4 ★** · [7]:1970.2 · [8]:1941.5 |


**ORT = OFF**

| Model | FPS | BC | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | Status |
|-------|-----|---|------|----------|----------|-------------|---------|--------|
| yolo26-n_224x224.dxnn | 14704.0 ±16.9 | 10 | 67 | 87.7 | 96.2 | 53~54 | 1000 | ok |
| yolo26-s_224x224.dxnn | 8167.0 ±5.4 | 10 | 35 | 89.5 | 97.3 | 54~55 | 1000 | ok |
| yolo26-m_224x224.dxnn | 5514.7 ±10.4 | 7 | 22 | 89.9 | 97.4 | 57~59 | 1000 | ok |
| yolo26-l_224x224.dxnn | 3512.1 ±16.1 | 7 | 14 | 90.1 | 98.3 | 55~57 | 1000 | ok |
| yolo26-x_224x224.dxnn | 1956.8 ±16.3 | 8 | 8 | 89.0 | 99.3 | 58~60 | 1000 | ok |

_Buffer-count sweep_ — throughput fps per `--buffer-count` (★ = winner):

| Model | BC ★ | Sweep ([bc]:fps) |
|-------|------|----------------|
| yolo26-n_224x224.dxnn | 10 | [3]:9341.6 · [4]:12939.0 · [5]:13766.6 · [6]:14038.4 · [7]:14035.7 · [8]:14185.6 · [9]:14124.3 · **[10]:14774.6 ★** · [11]:14733.3 · [12]:14742.8 |
| yolo26-s_224x224.dxnn | 10 | [3]:5734.0 · [4]:7617.9 · [5]:7770.0 · [6]:7782.7 · [7]:7949.2 · [8]:7983.9 · [9]:7847.1 · **[10]:8207.3 ★** · [11]:8203.6 · [12]:8159.7 |
| yolo26-m_224x224.dxnn | 7 | [3]:4101.1 · [4]:5499.4 · [5]:5531.2 · [6]:5529.1 · **[7]:5582.6 ★** · [8]:5528.2 |
| yolo26-l_224x224.dxnn | 7 | [3]:2661.2 · [4]:3355.1 · [5]:3498.9 · [6]:3494.9 · **[7]:3554.8 ★** · [8]:3539.4 |
| yolo26-x_224x224.dxnn | 8 | [3]:1466.6 · [4]:1917.4 · [5]:1968.0 · [6]:1975.0 · [7]:1950.9 · **[8]:1976.7 ★** · [9]:1945.8 · [10]:1961.6 |


### Latency (Single-Core, Sync)

#### Object Detection

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 94.7 ±2.1 | 10.56 | 10.29 | 0.26 | 39 | ok |
| yolo26-s_640x640.dxnn | 60.5 ±3.8 | 16.52 | 16.25 | 0.28 | 49 | ok |
| yolo26-m_640x640.dxnn | 42.2 ±0.6 | 23.69 | 23.41 | 0.28 | 49 | ok |
| yolo26-l_640x640.dxnn | 32.0 ±1.1 | 31.24 | 30.96 | 0.29 | 49 | ok |
| yolo26-x_640x640.dxnn | 17.7 ±0.5 | 56.60 | 56.27 | 0.33 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_640x640.dxnn | 96.4 ±5.6 | 10.38 | 10.38 | N/A | 50 | ok |
| yolo26-s_640x640.dxnn | 61.4 ±1.6 | 16.28 | 16.28 | N/A | 49 | ok |
| yolo26-m_640x640.dxnn | 42.9 ±1.4 | 23.31 | 23.31 | N/A | 49 | ok |
| yolo26-l_640x640.dxnn | 32.5 ±0.8 | 30.80 | 30.80 | N/A | 49 | ok |
| yolo26-x_640x640.dxnn | 17.8 ±0.3 | 56.22 | 56.22 | N/A | 50 | ok |

#### Pose Estimation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 96.4 ±6.6 | 10.37 | 10.20 | 0.18 | 49 | ok |
| yolo26-s-pose_640x640.dxnn | 60.2 ±2.5 | 16.61 | 16.39 | 0.22 | 50 | ok |
| yolo26-m-pose_640x640.dxnn | 41.6 ±1.6 | 24.04 | 23.82 | 0.22 | 50 | ok |
| yolo26-l-pose_640x640.dxnn | 31.7 ±0.6 | 31.52 | 31.25 | 0.27 | 49 | ok |
| yolo26-x-pose_640x640.dxnn | 17.5 ±0.5 | 57.10 | 56.84 | 0.26 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-pose_640x640.dxnn | 96.9 ±13.2 | 10.32 | 10.32 | N/A | 49 | ok |
| yolo26-s-pose_640x640.dxnn | 60.9 ±3.5 | 16.42 | 16.42 | N/A | 49 | ok |
| yolo26-m-pose_640x640.dxnn | 40.7 ±2.2 | 24.56 | 24.56 | N/A | 49 | ok |
| yolo26-l-pose_640x640.dxnn | 32.3 ±2.1 | 31.00 | 31.00 | N/A | 49 | ok |
| yolo26-x-pose_640x640.dxnn | 17.6 ±0.7 | 56.97 | 56.97 | N/A | 49 | ok |

#### Segmentation

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 53.5 ±1.5 | 18.70 | 18.30 | 0.39 | 49 | ok |
| yolo26-s-seg_640x640.dxnn | 37.7 ±1.4 | 26.54 | 26.15 | 0.39 | 50 | ok |
| yolo26-m-seg_640x640.dxnn | 25.0 ±2.2 | 40.05 | 39.64 | 0.41 | 50 | ok |
| yolo26-l-seg_640x640.dxnn | 21.0 ±0.3 | 47.59 | 47.19 | 0.40 | 50 | ok |
| yolo26-x-seg_640x640.dxnn | 11.8 ±0.3 | 84.99 | 84.59 | 0.40 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-seg_640x640.dxnn | 54.9 ±1.1 | 18.20 | 18.20 | N/A | 50 | ok |
| yolo26-s-seg_640x640.dxnn | 38.4 ±1.8 | 26.02 | 26.02 | N/A | 49 | ok |
| yolo26-m-seg_640x640.dxnn | 24.9 ±1.6 | 40.11 | 40.11 | N/A | 49 | ok |
| yolo26-l-seg_640x640.dxnn | 21.4 ±1.1 | 46.83 | 46.83 | N/A | 49 | ok |
| yolo26-x-seg_640x640.dxnn | 11.8 ±0.4 | 84.51 | 84.51 | N/A | 49 | ok |

#### Oriented BBox (OBB)

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 43.7 ±1.8 | 22.90 | 22.66 | 0.24 | 49 | ok |
| yolo26-s-obb_1024x1024.dxnn | 26.2 ±1.1 | 38.19 | 37.94 | 0.25 | 50 | ok |
| yolo26-m-obb_1024x1024.dxnn | 17.7 ±0.3 | 56.36 | 56.12 | 0.24 | 49 | ok |
| yolo26-l-obb_1024x1024.dxnn | 13.5 ±0.5 | 74.09 | 73.81 | 0.28 | 49 | ok |
| yolo26-x-obb_1024x1024.dxnn | 7.0 ±0.8 | 142.38 | 142.07 | 0.31 | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n-obb_1024x1024.dxnn | 44.3 ±1.1 | 22.59 | 22.59 | N/A | 50 | ok |
| yolo26-s-obb_1024x1024.dxnn | 26.2 ±1.4 | 38.11 | 38.11 | N/A | 49 | ok |
| yolo26-m-obb_1024x1024.dxnn | 18.1 ±0.2 | 55.30 | 55.30 | N/A | 49 | ok |
| yolo26-l-obb_1024x1024.dxnn | 13.5 ±0.6 | 73.91 | 73.91 | N/A | 49 | ok |
| yolo26-x-obb_1024x1024.dxnn | 7.0 ±1.0 | 142.07 | 142.07 | N/A | 49 | ok |

#### Classification

**ORT = ON**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 960.8 ±41.8 | 1.04 | 1.04 | N/A | 50 | ok |
| yolo26-s_224x224.dxnn | 615.0 ±6.8 | 1.63 | 1.63 | N/A | 49 | ok |
| yolo26-m_224x224.dxnn | 454.5 ±67.6 | 2.20 | 2.20 | N/A | 49 | ok |
| yolo26-l_224x224.dxnn | 290.1 ±16.1 | 3.45 | 3.45 | N/A | 49 | ok |
| yolo26-x_224x224.dxnn | 167.2 ±7.2 | 5.98 | 5.98 | N/A | 49 | ok |

**ORT = OFF**

| Model | FPS | Total ms | NPU ms | CPU ms | NPU Temp °C | Status |
|-------|-----|----------|--------|--------|-------------|--------|
| yolo26-n_224x224.dxnn | 977.0 ±16.9 | 1.02 | 1.02 | N/A | 49 | ok |
| yolo26-s_224x224.dxnn | 598.6 ±5.4 | 1.67 | 1.67 | N/A | 49 | ok |
| yolo26-m_224x224.dxnn | 437.0 ±10.4 | 2.29 | 2.29 | N/A | 49 | ok |
| yolo26-l_224x224.dxnn | 286.2 ±16.1 | 3.49 | 3.49 | N/A | 49 | ok |
| yolo26-x_224x224.dxnn | 164.7 ±16.2 | 6.07 | 6.07 | N/A | 49 | ok |

## E2E Pipeline (Single-Stream)

### Object Detection

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vaapidecodebin | 3455 | 3 | 496.8 ±1.4 | 6.95 | 213 | 21.2 | 77.9 | 48 | 1000 | 414 | ok |
| yolo26-s_640x640.dxnn | vaapidecodebin | 3455 | 3 | 494.4 ±1.0 | 6.99 | 213 | 41.0 | 85.4 | 50 | 1000 | 440 | ok |
| yolo26-m_640x640.dxnn | vaapidecodebin | 3455 | 3 | 491.7 ±1.0 | 7.03 | 214 | 69.8 | 99.8 | 51~52 | 1000 | 585 | ok |
| yolo26-l_640x640.dxnn | vaapidecodebin | 3455 | 3 | 367.8 ±2.4 | 9.39 | 150 | 73.5 | 100.0 | 52~53 | 1000 | 639 | ok |
| yolo26-x_640x640.dxnn | vaapidecodebin | 3455 | 3 | 202.6 ±0.1 | 17.05 | 72 | 83.1 | 100.0 | 54~56 | 1000 | 826 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | vaapidecodebin | 3455 | 3 | 452.1 ±2.6 | 7.64 | 241 | 20.0 | 82.0 | 50 | 1000 | 467 | ok |
| yolo26-s_640x640.dxnn | vaapidecodebin | 3455 | 3 | 447.1 ±4.3 | 7.73 | 237 | 37.4 | 78.5 | 50 | 1000 | 556 | ok |
| yolo26-m_640x640.dxnn | vaapidecodebin | 3455 | 3 | 453.4 ±1.5 | 7.62 | 238 | 64.5 | 89.3 | 51~52 | 1000 | 626 | ok |
| yolo26-l_640x640.dxnn | vaapidecodebin | 3455 | 3 | 369.3 ±1.9 | 9.36 | 195 | 74.0 | 100.0 | 52~53 | 1000 | 698 | ok |
| yolo26-x_640x640.dxnn | vaapidecodebin | 3455 | 3 | 201.2 ±0.2 | 17.17 | 95 | 83.6 | 100.0 | 54~57 | 1000 | 882 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_640x640.dxnn | 496.8 | 452.1 | +44.7 | +9.9% |
| yolo26-s_640x640.dxnn | 494.4 | 447.1 | +47.4 | +10.6% |
| yolo26-m_640x640.dxnn | 491.7 | 453.4 | +38.3 | +8.4% |
| yolo26-l_640x640.dxnn | 367.8 | 369.3 | -1.5 | -0.4% |
| yolo26-x_640x640.dxnn | 202.6 | 201.2 | +1.4 | +0.7% |

### Pose Estimation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 540.4 ±1.1 | 6.39 | 166 | 27.0 | 63.0 | 50 | 1000 | 380 | ok |
| yolo26-s-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 540.3 ±1.1 | 6.39 | 166 | 49.7 | 79.1 | 50~51 | 1000 | 418 | ok |
| yolo26-m-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 468.4 ±1.2 | 7.38 | 150 | 70.4 | 100.0 | 52~53 | 1000 | 568 | ok |
| yolo26-l-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 351.4 ±3.3 | 9.83 | 105 | 69.4 | 100.0 | 52~53 | 1000 | 596 | ok |
| yolo26-x-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 195.8 ±1.8 | 17.64 | 54 | 78.2 | 100.0 | 54~56 | 1000 | 787 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 553.9 ±3.3 | 6.24 | 127 | 26.5 | 62.6 | 50 | 1000 | 401 | ok |
| yolo26-s-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 554.1 ±1.7 | 6.24 | 129 | 49.1 | 78.0 | 50~51 | 1000 | 482 | ok |
| yolo26-m-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 467.9 ±0.3 | 7.38 | 116 | 70.0 | 100.0 | 52~53 | 1000 | 585 | ok |
| yolo26-l-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 354.2 ±2.4 | 9.75 | 82 | 65.8 | 100.0 | 52~53 | 1000 | 612 | ok |
| yolo26-x-pose_640x640.dxnn | vaapidecodebin | 3455 | 3 | 195.8 ±1.7 | 17.65 | 42 | 84.3 | 100.0 | 54~56 | 1000 | 801 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-pose_640x640.dxnn | 540.4 | 553.9 | -13.4 | -2.4% |
| yolo26-s-pose_640x640.dxnn | 540.3 | 554.1 | -13.8 | -2.5% |
| yolo26-m-pose_640x640.dxnn | 468.4 | 467.9 | +0.5 | +0.1% |
| yolo26-l-pose_640x640.dxnn | 351.4 | 354.2 | -2.8 | -0.8% |
| yolo26-x-pose_640x640.dxnn | 195.8 | 195.8 | +0.1 | +0.0% |

### Segmentation

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 360.8 ±0.4 | 9.58 | 517 | 20.6 | 79.7 | 50 | 1000 | 737 | ok |
| yolo26-s-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 359.7 ±0.5 | 9.61 | 510 | 41.7 | 81.5 | 51 | 1000 | 736 | ok |
| yolo26-m-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 319.5 ±3.2 | 10.81 | 397 | 78.4 | 100.0 | 53~54 | 1000 | 912 | ok |
| yolo26-l-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 263.7 ±3.8 | 13.10 | 289 | 80.8 | 100.0 | 53~55 | 1000 | 942 | ok |
| yolo26-x-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 140.0 ±0.2 | 24.68 | 143 | 86.9 | 100.0 | 56~60 | 1000 | 1152 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 319.6 ±1.9 | 10.81 | 414 | 18.6 | 72.1 | 50 | 1000 | 752 | ok |
| yolo26-s-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 313.9 ±1.0 | 11.01 | 398 | 34.5 | 72.0 | 51 | 1000 | 852 | ok |
| yolo26-m-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 314.9 ±2.2 | 10.97 | 404 | 76.0 | 100.0 | 53~54 | 1000 | 1009 | ok |
| yolo26-l-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 262.0 ±4.5 | 13.19 | 312 | 79.3 | 100.0 | 53~55 | 1000 | 1025 | ok |
| yolo26-x-seg_640x640.dxnn | vaapidecodebin | 3455 | 3 | 141.3 ±0.5 | 24.45 | 159 | 86.3 | 100.0 | 56~60 | 1000 | 1241 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-seg_640x640.dxnn | 360.8 | 319.6 | +41.2 | +12.9% |
| yolo26-s-seg_640x640.dxnn | 359.7 | 313.9 | +45.8 | +14.6% |
| yolo26-m-seg_640x640.dxnn | 319.5 | 314.9 | +4.6 | +1.4% |
| yolo26-l-seg_640x640.dxnn | 263.7 | 262.0 | +1.7 | +0.6% |
| yolo26-x-seg_640x640.dxnn | 140.0 | 141.3 | -1.4 | -1.0% |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 391.9 ±3.2 | 6.74 | 154 | 62.4 | 90.0 | 50~51 | 1000 | 541 | ok |
| yolo26-s-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 260.5 ±2.7 | 10.13 | 110 | 73.1 | 100.0 | 51~52 | 1000 | 619 | ok |
| yolo26-m-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 173.6 ±2.4 | 15.21 | 67 | 83.4 | 100.0 | 53~55 | 1000 | 678 | ok |
| yolo26-l-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 129.6 ±1.4 | 20.38 | 49 | 83.9 | 100.0 | 54~56 | 1000 | 711 | ok |
| yolo26-x-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 71.0 ±0.0 | 37.17 | 27 | 91.0 | 100.0 | 57~62 | 1000 | 917 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 392.9 ±3.9 | 6.72 | 159 | 62.6 | 89.8 | 51 | 1000 | 538 | ok |
| yolo26-s-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 263.2 ±1.1 | 10.03 | 114 | 72.6 | 100.0 | 51~52 | 1000 | 636 | ok |
| yolo26-m-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 175.9 ±0.6 | 15.00 | 71 | 84.2 | 100.0 | 53~55 | 1000 | 698 | ok |
| yolo26-l-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 129.1 ±1.0 | 20.45 | 52 | 84.8 | 100.0 | 54~57 | 1000 | 730 | ok |
| yolo26-x-obb_1024x1024.dxnn | vaapidecodebin | 2640 | 3 | 71.0 ±0.1 | 37.20 | 29 | 90.4 | 100.0 | 57~61 | 1000 | 936 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n-obb_1024x1024.dxnn | 391.9 | 392.9 | -0.9 | -0.2% |
| yolo26-s-obb_1024x1024.dxnn | 260.5 | 263.2 | -2.7 | -1.0% |
| yolo26-m-obb_1024x1024.dxnn | 173.6 | 175.9 | -2.3 | -1.3% |
| yolo26-l-obb_1024x1024.dxnn | 129.6 | 129.1 | +0.4 | +0.3% |
| yolo26-x-obb_1024x1024.dxnn | 71.0 | 71.0 | +0.0 | +0.1% |

### Classification

**ORT = ON**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vaapidecodebin | 3455 | 3 | 763.6 ±22.7 | 4.53 | 42 | 3.1 | 14.9 | 49~50 | 1000 | 238 | ok |
| yolo26-s_224x224.dxnn | vaapidecodebin | 3455 | 3 | 772.1 ±4.6 | 4.47 | 41 | 5.7 | 26.9 | 49 | 1000 | 215 | ok |
| yolo26-m_224x224.dxnn | vaapidecodebin | 3455 | 3 | 757.6 ±24.6 | 4.56 | 42 | 8.1 | 38.0 | 49~50 | 1000 | 300 | ok |
| yolo26-l_224x224.dxnn | vaapidecodebin | 3455 | 3 | 760.6 ±3.0 | 4.54 | 43 | 12.2 | 60.6 | 49~50 | 1000 | 263 | ok |
| yolo26-x_224x224.dxnn | vaapidecodebin | 3455 | 3 | 742.8 ±13.8 | 4.65 | 45 | 22.2 | 67.8 | 50 | 1000 | 398 | ok |

**ORT = OFF**

| Model | Decoder | Frames | Runs | Avg FPS | Avg Duration (s) | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|--------|------|---------|------------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_224x224.dxnn | vaapidecodebin | 3455 | 3 | 772.4 ±10.2 | 4.47 | 42 | 3.2 | 14.9 | 49~50 | 1000 | 239 | ok |
| yolo26-s_224x224.dxnn | vaapidecodebin | 3455 | 3 | 773.6 ±3.3 | 4.47 | 41 | 5.5 | 26.9 | 49~50 | 1000 | 216 | ok |
| yolo26-m_224x224.dxnn | vaapidecodebin | 3455 | 3 | 770.0 ±1.8 | 4.49 | 42 | 8.0 | 37.9 | 49~50 | 1000 | 241 | ok |
| yolo26-l_224x224.dxnn | vaapidecodebin | 3455 | 3 | 755.1 ±15.0 | 4.58 | 43 | 12.6 | 60.3 | 49~50 | 1000 | 312 | ok |
| yolo26-x_224x224.dxnn | vaapidecodebin | 3455 | 3 | 744.5 ±4.0 | 4.64 | 45 | 23.9 | 66.1 | 50 | 1000 | 350 | ok |

**ORT Comparison – E2E FPS**

| Model | ORT ON | ORT OFF | Delta | Delta % |
|-------|--------|---------|-------|---------|
| yolo26-n_224x224.dxnn | 763.6 | 772.4 | -8.9 | -1.1% |
| yolo26-s_224x224.dxnn | 772.1 | 773.6 | -1.5 | -0.2% |
| yolo26-m_224x224.dxnn | 757.6 | 770.0 | -12.4 | -1.6% |
| yolo26-l_224x224.dxnn | 760.6 | 755.1 | +5.5 | +0.7% |
| yolo26-x_224x224.dxnn | 742.8 | 744.5 | -1.7 | -0.2% |

## E2E Pipeline (Multi-Stream)

### Object Detection

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 16 | 3 | 536.6 ±0.5 | 33.5 | 294 | 31.6 | 76.4 | 51~53 | 1000 | 697 | ok |
| yolo26-n_640x640.dxnn | 17 | 3 | 533.6 ±1.3 | 31.4 | 296 | 31.3 | 79.7 | 54~55 | 1000 | 732 | ok |
| yolo26-n_640x640.dxnn | 18 | 3 | 534.2 ±1.7 | 29.7 | 295 | 31.6 | 80.6 | 55~56 | 1000 | 752 | ok |
| yolo26-s_640x640.dxnn | 16 | 3 | 531.0 ±1.4 | 33.2 | 302 | 59.9 | 88.0 | 55~59 | 1000 | 911 | ok |
| yolo26-s_640x640.dxnn | 17 | 3 | 531.2 ±0.3 | 31.2 | 301 | 60.3 | 88.3 | 61~62 | 1000 | 930 | ok |
| yolo26-s_640x640.dxnn | 18 | 3 | 531.4 ±0.1 | 29.5 | 302 | 60.4 | 88.2 | 63~64 | 1000 | 967 | ok |
| yolo26-m_640x640.dxnn | 16 | 3 | 489.3 ±0.5 | 30.6 | 279 | 95.2 | 100.0 | 67~74 | 1000 | 876 | ok |
| yolo26-m_640x640.dxnn | 17 | 3 | 488.4 ±1.4 | 28.7 | 280 | 94.2 | 100.0 | 78~80 | 1000 | 894 | ok |
| yolo26-l_640x640.dxnn | 12 | 3 | 368.0 ±0.4 | 30.7 | 175 | 95.9 | 100.0 | 67~73 | 1000 | 852 | ok |
| yolo26-l_640x640.dxnn | 13 | 3 | 367.6 ±0.6 | 28.3 | 176 | 94.9 | 100.0 | 77~79 | 1000 | 882 | ok |
| yolo26-x_640x640.dxnn | 6 | 3 | 201.1 ±0.4 | 33.5 | 79 | 95.5 | 100.0 | 69~76 | 1000 | 936 | ok |
| yolo26-x_640x640.dxnn | 7 | 3 | 194.3 ±1.0 | 27.8 | 79 | 94.4 | 100.0 | 80~81 | 800~1000 | 943 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n_640x640.dxnn | 15 | 3 | 447.7 ±0.8 | 29.9 | 253 | 25.7 | 81.5 | 51~52 | 1000 | 777 | ok |
| yolo26-n_640x640.dxnn | 14 | 3 | 444.4 ±0.8 | 31.7 | 254 | 25.7 | 80.8 | 53~54 | 1000 | 754 | ok |
| yolo26-s_640x640.dxnn | 14 | 3 | 444.1 ±1.6 | 31.7 | 254 | 48.1 | 78.1 | 54~57 | 1000 | 935 | ok |
| yolo26-s_640x640.dxnn | 15 | 3 | 442.1 ±0.5 | 29.5 | 252 | 47.8 | 77.7 | 59~60 | 1000 | 963 | ok |
| yolo26-m_640x640.dxnn | 15 | 3 | 441.2 ±1.8 | 29.4 | 251 | 82.4 | 90.7 | 65~71 | 1000 | 978 | ok |
| yolo26-m_640x640.dxnn | 14 | 3 | 439.7 ±0.5 | 31.4 | 252 | 81.9 | 90.0 | 75~77 | 1000 | 956 | ok |
| yolo26-l_640x640.dxnn | 12 | 3 | 368.9 ±0.6 | 30.7 | 221 | 95.3 | 100.0 | 67~74 | 1000 | 932 | ok |
| yolo26-l_640x640.dxnn | 13 | 3 | 368.7 ±0.2 | 28.4 | 222 | 94.5 | 100.0 | 78~80 | 800~1000 | 959 | ok |
| yolo26-x_640x640.dxnn | 6 | 3 | 200.2 ±0.5 | 33.4 | 104 | 95.3 | 100.0 | 69~76 | 1000 | 1017 | ok |
| yolo26-x_640x640.dxnn | 7 | 3 | 193.9 ±1.4 | 27.7 | 103 | 94.3 | 100.0 | 80~81 | 800~1000 | 1034 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n_640x640.dxnn | 17 | 31.4 | 14 | 31.7 |
| yolo26-s_640x640.dxnn | 17 | 31.2 | 14 | 31.7 |
| yolo26-m_640x640.dxnn | 16 | 30.6 | 14 | 31.4 |
| yolo26-l_640x640.dxnn | 12 | 30.7 | 12 | 30.7 |
| yolo26-x_640x640.dxnn | 6 | 33.5 | 6 | 33.4 |

### Pose Estimation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 18 | 3 | 586.5 ±1.0 | 32.6 | 231 | 38.2 | 76.1 | 54~56 | 1000 | 879 | ok |
| yolo26-n-pose_640x640.dxnn | 19 | 3 | 587.4 ±1.7 | 30.9 | 231 | 38.4 | 74.7 | 57~58 | 1000 | 894 | ok |
| yolo26-n-pose_640x640.dxnn | 20 | 3 | 588.6 ±1.2 | 29.4 | 231 | 38.2 | 75.8 | 59 | 1000 | 920 | ok |
| yolo26-s-pose_640x640.dxnn | 18 | 3 | 585.5 ±2.2 | 32.5 | 233 | 72.6 | 89.7 | 57~62 | 1000 | 945 | ok |
| yolo26-s-pose_640x640.dxnn | 19 | 3 | 584.1 ±1.6 | 30.7 | 234 | 72.6 | 88.9 | 64~66 | 1000 | 969 | ok |
| yolo26-s-pose_640x640.dxnn | 20 | 3 | 584.0 ±2.1 | 29.2 | 234 | 73.2 | 89.3 | 67 | 1000 | 995 | ok |
| yolo26-m-pose_640x640.dxnn | 15 | 3 | 464.2 ±0.3 | 30.9 | 178 | 93.3 | 100.0 | 67~74 | 1000 | 817 | ok |
| yolo26-m-pose_640x640.dxnn | 16 | 3 | 462.8 ±2.2 | 28.9 | 178 | 94.6 | 100.0 | 78~80 | 800~1000 | 840 | ok |
| yolo26-l-pose_640x640.dxnn | 11 | 3 | 352.0 ±0.3 | 32.0 | 122 | 94.2 | 100.0 | 66~72 | 1000 | 804 | ok |
| yolo26-l-pose_640x640.dxnn | 12 | 3 | 351.9 ±0.6 | 29.3 | 122 | 94.7 | 100.0 | 76~77 | 1000 | 822 | ok |
| yolo26-x-pose_640x640.dxnn | 6 | 3 | 194.9 ±0.1 | 32.5 | 59 | 94.9 | 100.0 | 69~74 | 1000 | 906 | ok |
| yolo26-x-pose_640x640.dxnn | 7 | 3 | 192.8 ±2.1 | 27.6 | 60 | 94.7 | 100.0 | 78~79 | 800~1000 | 916 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-pose_640x640.dxnn | 18 | 3 | 604.6 ±1.0 | 33.6 | 180 | 39.6 | 73.3 | 53~55 | 1000 | 896 | ok |
| yolo26-n-pose_640x640.dxnn | 19 | 3 | 603.9 ±0.8 | 31.8 | 180 | 39.6 | 74.2 | 56~57 | 1000 | 936 | ok |
| yolo26-n-pose_640x640.dxnn | 20 | 3 | 603.4 ±1.1 | 30.2 | 180 | 39.7 | 72.6 | 58 | 1000 | 953 | ok |
| yolo26-n-pose_640x640.dxnn | 21 | 3 | 602.6 ±2.0 | 28.7 | 180 | 39.5 | 74.9 | 59 | 1000 | 983 | ok |
| yolo26-s-pose_640x640.dxnn | 18 | 3 | 600.6 ±1.8 | 33.4 | 182 | 74.8 | 90.3 | 57~61 | 1000 | 980 | ok |
| yolo26-s-pose_640x640.dxnn | 19 | 3 | 601.4 ±1.3 | 31.6 | 182 | 75.6 | 90.5 | 64~66 | 1000 | 1002 | ok |
| yolo26-s-pose_640x640.dxnn | 20 | 3 | 599.3 ±1.2 | 30.0 | 183 | 75.1 | 89.7 | 67 | 1000 | 1031 | ok |
| yolo26-m-pose_640x640.dxnn | 15 | 3 | 464.8 ±0.3 | 31.0 | 140 | 94.8 | 100.0 | 67~73 | 1000 | 850 | ok |
| yolo26-m-pose_640x640.dxnn | 16 | 3 | 464.9 ±1.3 | 29.1 | 142 | 95.3 | 100.0 | 78~80 | 1000 | 870 | ok |
| yolo26-l-pose_640x640.dxnn | 11 | 3 | 351.9 ±0.6 | 32.0 | 97 | 94.9 | 100.0 | 65~72 | 1000 | 826 | ok |
| yolo26-l-pose_640x640.dxnn | 12 | 3 | 351.4 ±0.8 | 29.3 | 97 | 95.0 | 100.0 | 76~77 | 1000 | 847 | ok |
| yolo26-x-pose_640x640.dxnn | 6 | 3 | 195.2 ±0.1 | 32.5 | 47 | 94.1 | 100.0 | 68~74 | 1000 | 921 | ok |
| yolo26-x-pose_640x640.dxnn | 7 | 3 | 193.5 ±1.8 | 27.6 | 48 | 95.0 | 100.0 | 78~79 | 800~1000 | 937 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-pose_640x640.dxnn | 19 | 30.9 | 20 | 30.2 |
| yolo26-s-pose_640x640.dxnn | 19 | 30.7 | 19 | 31.6 |
| yolo26-m-pose_640x640.dxnn | 15 | 30.9 | 15 | 31.0 |
| yolo26-l-pose_640x640.dxnn | 11 | 32.0 | 11 | 32.0 |
| yolo26-x-pose_640x640.dxnn | 6 | 32.5 | 6 | 32.5 |

### Segmentation

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 12 | 3 | 365.1 ±1.0 | 30.4 | 601 | 27.2 | 74.3 | 53~55 | 1000 | 1136 | ok |
| yolo26-n-seg_640x640.dxnn | 13 | 3 | 365.1 ±0.7 | 28.1 | 605 | 27.2 | 75.9 | 57~58 | 1000 | 1182 | ok |
| yolo26-s-seg_640x640.dxnn | 11 | 3 | 362.8 ±1.6 | 33.0 | 593 | 53.7 | 80.4 | 57~61 | 1000 | 1163 | ok |
| yolo26-s-seg_640x640.dxnn | 12 | 3 | 362.9 ±1.4 | 30.2 | 596 | 53.3 | 79.6 | 64~65 | 1000 | 1181 | ok |
| yolo26-s-seg_640x640.dxnn | 13 | 3 | 363.5 ±1.6 | 28.0 | 598 | 53.8 | 79.4 | 66~67 | 1000 | 1234 | ok |
| yolo26-m-seg_640x640.dxnn | 10 | 3 | 316.8 ±1.8 | 31.7 | 433 | 92.5 | 100.0 | 70~79 | 800~1000 | 1126 | ok |
| yolo26-m-seg_640x640.dxnn | 11 | 3 | 288.1 ±9.2 | 26.2 | 373 | 90.8 | 100.0 | 83 | 600~1000 | 1160 | ok |
| yolo26-l-seg_640x640.dxnn | 8 | 3 | 262.2 ±1.2 | 32.8 | 312 | 94.8 | 100.0 | 69~77 | 1000 | 1126 | ok |
| yolo26-l-seg_640x640.dxnn | 9 | 3 | 252.0 ±1.7 | 28.0 | 302 | 93.4 | 100.0 | 81~83 | 800~1000 | 1158 | ok |
| yolo26-x-seg_640x640.dxnn | 4 | 3 | 139.1 ±1.2 | 34.8 | 148 | 93.7 | 100.0 | 72~78 | 800~1000 | 1245 | ok |
| yolo26-x-seg_640x640.dxnn | 5 | 3 | 128.7 ±1.1 | 25.7 | 136 | 91.5 | 100.0 | 82 | 600~1000 | 1266 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-seg_640x640.dxnn | 10 | 3 | 313.7 ±1.7 | 31.4 | 422 | 22.5 | 74.9 | 53~55 | 1000 | 1104 | ok |
| yolo26-n-seg_640x640.dxnn | 11 | 3 | 311.7 ±0.2 | 28.3 | 420 | 22.2 | 72.2 | 56 | 1000 | 1099 | ok |
| yolo26-s-seg_640x640.dxnn | 10 | 3 | 309.0 ±1.2 | 30.9 | 411 | 43.6 | 73.8 | 56~60 | 1000 | 1194 | ok |
| yolo26-s-seg_640x640.dxnn | 11 | 3 | 307.2 ±0.5 | 27.9 | 410 | 43.3 | 72.2 | 62~63 | 1000 | 1200 | ok |
| yolo26-m-seg_640x640.dxnn | 10 | 3 | 307.2 ±1.8 | 30.7 | 415 | 92.0 | 100.0 | 70~78 | 1000 | 1261 | ok |
| yolo26-m-seg_640x640.dxnn | 11 | 3 | 289.6 ±8.9 | 26.3 | 397 | 90.7 | 100.0 | 83 | 600~1000 | 1266 | ok |
| yolo26-l-seg_640x640.dxnn | 8 | 3 | 263.0 ±0.3 | 32.9 | 338 | 94.5 | 100.0 | 70~77 | 1000 | 1227 | ok |
| yolo26-l-seg_640x640.dxnn | 9 | 3 | 250.2 ±2.5 | 27.8 | 326 | 92.7 | 100.0 | 81~82 | 800~1000 | 1258 | ok |
| yolo26-x-seg_640x640.dxnn | 4 | 3 | 139.5 ±1.4 | 34.9 | 162 | 93.5 | 100.0 | 72~79 | 800~1000 | 1346 | ok |
| yolo26-x-seg_640x640.dxnn | 5 | 3 | 124.9 ±4.4 | 25.0 | 144 | 91.4 | 100.0 | 82~83 | 600~1000 | 1376 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-seg_640x640.dxnn | 12 | 30.4 | 10 | 31.4 |
| yolo26-s-seg_640x640.dxnn | 12 | 30.2 | 10 | 30.9 |
| yolo26-m-seg_640x640.dxnn | 10 | 31.7 | 10 | 30.7 |
| yolo26-l-seg_640x640.dxnn | 8 | 32.8 | 8 | 32.9 |
| yolo26-x-seg_640x640.dxnn | 4 | 34.8 | 4 | 34.9 |

### Oriented BBox (OBB)

**ORT = ON**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 13 | 3 | 422.9 ±0.5 | 32.5 | 210 | 90.8 | 100.0 | 57~61 | 1000 | 942 | ok |
| yolo26-n-obb_1024x1024.dxnn | 14 | 3 | 420.8 ±1.6 | 30.1 | 211 | 89.3 | 100.0 | 64~66 | 1000 | 930 | ok |
| yolo26-n-obb_1024x1024.dxnn | 15 | 3 | 418.0 ±0.9 | 27.9 | 209 | 89.3 | 99.3 | 67~68 | 1000 | 963 | ok |
| yolo26-s-obb_1024x1024.dxnn | 8 | 3 | 259.2 ±0.4 | 32.4 | 123 | 93.2 | 100.0 | 59~63 | 1000 | 842 | ok |
| yolo26-s-obb_1024x1024.dxnn | 9 | 3 | 258.4 ±0.5 | 28.7 | 122 | 93.0 | 100.0 | 67~68 | 1000 | 886 | ok |
| yolo26-m-obb_1024x1024.dxnn | 5 | 3 | 172.9 ±0.8 | 34.6 | 75 | 93.1 | 100.0 | 64~70 | 1000 | 787 | ok |
| yolo26-m-obb_1024x1024.dxnn | 6 | 3 | 173.3 ±0.3 | 28.9 | 75 | 95.9 | 100.0 | 75~77 | 1000 | 808 | ok |
| yolo26-l-obb_1024x1024.dxnn | 4 | 3 | 128.4 ±0.0 | 32.1 | 53 | 93.6 | 100.0 | 65~71 | 1000 | 797 | ok |
| yolo26-l-obb_1024x1024.dxnn | 5 | 3 | 128.0 ±0.7 | 25.6 | 54 | 94.9 | 100.0 | 75~77 | 1000 | 823 | ok |
| yolo26-x-obb_1024x1024.dxnn | 2 | 3 | 70.7 ±0.1 | 35.4 | 29 | 93.8 | 100.0 | 69~73 | 1000 | 949 | ok |
| yolo26-x-obb_1024x1024.dxnn | 3 | 3 | 70.3 ±0.7 | 23.4 | 29 | 94.0 | 100.0 | 78~79 | 800~1000 | 982 | ok |

**ORT = OFF**

| Model | Streams | Runs | E2E FPS | Per-Ch FPS | CPU% | NPU Avg% | NPU Max% | NPU Temp °C | NPU MHz | RSS MiB | Status |
|-------|---------|------|---------|------------|------|----------|----------|-------------|---------|---------|--------|
| yolo26-n-obb_1024x1024.dxnn | 13 | 3 | 425.8 ±1.6 | 32.8 | 218 | 92.4 | 100.0 | 57~61 | 1000 | 970 | ok |
| yolo26-n-obb_1024x1024.dxnn | 14 | 3 | 426.0 ±0.5 | 30.4 | 217 | 93.0 | 100.0 | 64~66 | 1000 | 962 | ok |
| yolo26-n-obb_1024x1024.dxnn | 15 | 3 | 420.9 ±1.6 | 28.1 | 217 | 90.1 | 100.0 | 67 | 1000 | 994 | ok |
| yolo26-s-obb_1024x1024.dxnn | 8 | 3 | 258.8 ±0.3 | 32.4 | 127 | 94.1 | 100.0 | 59~64 | 1000 | 867 | ok |
| yolo26-s-obb_1024x1024.dxnn | 9 | 3 | 260.2 ±0.3 | 28.9 | 127 | 94.1 | 100.0 | 67~68 | 1000 | 907 | ok |
| yolo26-m-obb_1024x1024.dxnn | 5 | 3 | 173.8 ±0.2 | 34.8 | 77 | 93.0 | 100.0 | 64~70 | 1000 | 808 | ok |
| yolo26-m-obb_1024x1024.dxnn | 6 | 3 | 173.5 ±0.2 | 28.9 | 78 | 95.0 | 100.0 | 74~77 | 1000 | 832 | ok |
| yolo26-l-obb_1024x1024.dxnn | 4 | 3 | 128.5 ±0.2 | 32.1 | 56 | 93.7 | 100.0 | 65~71 | 1000 | 814 | ok |
| yolo26-l-obb_1024x1024.dxnn | 5 | 3 | 128.2 ±0.1 | 25.6 | 56 | 95.1 | 100.0 | 75~77 | 1000 | 840 | ok |
| yolo26-x-obb_1024x1024.dxnn | 2 | 3 | 70.6 ±0.1 | 35.3 | 30 | 93.7 | 100.0 | 68~73 | 1000 | 969 | ok |
| yolo26-x-obb_1024x1024.dxnn | 3 | 3 | 70.4 ±0.1 | 23.5 | 30 | 95.1 | 100.0 | 77~78 | 1000 | 1000 | ok |

**Channel Capacity Summary** (max streams where per-channel FPS ≥ 30)

| Model | ORT ON Capacity | Per-Ch FPS | ORT OFF Capacity | Per-Ch FPS |
|-------|-----------------|------------|------------------|------------|
| yolo26-n-obb_1024x1024.dxnn | 14 | 30.1 | 14 | 30.4 |
| yolo26-s-obb_1024x1024.dxnn | 8 | 32.4 | 8 | 32.4 |
| yolo26-m-obb_1024x1024.dxnn | 5 | 34.6 | 5 | 34.8 |
| yolo26-l-obb_1024x1024.dxnn | 4 | 32.1 | 4 | 32.1 |
| yolo26-x-obb_1024x1024.dxnn | 2 | 35.4 | 2 | 35.3 |

---
*Report generated by dx-benchmark tool*
