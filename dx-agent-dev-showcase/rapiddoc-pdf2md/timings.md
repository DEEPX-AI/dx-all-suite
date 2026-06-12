# RapidDoc PDF->Markdown — NPU Performance Summary

- **Date**: 2026-06-12 15:03:20
- **Pipeline Mode**: finegrained
- **Files**: 1 (physics0409110_origin)
- **Total Pages**: 16
- **Wall Time**: 38.94 s
- **Throughput**: 0.41 pages/s

## Model Loading

| Model | Load Time |
|:---|---:|
| formula | 1.02 s |
| layout | 0.15 s |
| ocr | 0.55 s |
| table | 0.04 s |

## Per-Stage Performance (NPU pipeline)

| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |
|:---|---:|---:|---:|---:|---:|
| Layout (NPU) | 16 | 317.42 ms | 3.2 FPS | 5.08 | 12.3% |
| Formula (ONNX/CPU) | 164 | 213.82 ms | 4.7 FPS | 35.07 | 85.0% |
| PDF text-det | 99 | 1.62 ms | 616.5 FPS | 0.16 | 0.4% |
| OCR det (NPU) | 1 | 108.18 ms | 9.2 FPS | 0.11 | 0.3% |
| Table (NPU) | 1 | 848.05 ms | 1.2 FPS | 0.85 | 2.1% |

- **Total Stage Time**: 41.26 s
- **Avg per Page**: 2.58 s
