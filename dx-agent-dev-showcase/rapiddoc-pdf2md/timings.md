# finegrained Performance Summary

- **Date**: 2026-06-12 14:18:54
- **Pipeline Mode**: finegrained
- **Total Files**: 1
- **Total Pages**: 16
- **Total Wall Time**: 36.94 s
- **Overall Throughput**: 0.4 pages/s

## Model Loading

| Model | Load Time |
|:---|---:|
| formula | 1.02 s |
| layout | 0.16 s |
| ocr | 0.53 s |
| table | 0.04 s |
| **Total** | **1.75 s** |

## Overall Pipeline Performance

| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |
|:---|---:|---:|---:|---:|---:|
| Layout | 16 | 311.62 ms | 3.2 FPS | 4.99 | 12.8% |
| Formula | 164 | 201.21 ms | 5.0 FPS | 33.00 | 84.5% |
| PDF-det | 99 | 1.74 ms | 574.1 FPS | 0.17 | 0.4% |
| OCR-det | 1 | 109.59 ms | 9.1 FPS | 0.11 | 0.3% |
| Table | 1 | 795.29 ms | 1.3 FPS | 0.80 | 2.0% |

- **Total Stages**: 39.06 s

## physics0409110_origin

| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |
|:---|---:|---:|---:|---:|---:|
| Layout | 16 | 311.62 ms | 3.2 FPS | 4.99 | 12.8% |
| Formula | 164 | 201.21 ms | 5.0 FPS | 33.00 | 84.5% |
| PDF-det | 99 | 1.74 ms | 574.1 FPS | 0.17 | 0.4% |
| OCR-det | 1 | 109.59 ms | 9.1 FPS | 0.11 | 0.3% |
| Table | 1 | 795.29 ms | 1.3 FPS | 0.80 | 2.0% |

- **Total Stage Time**: 39.06 s
- **Pages**: 16
- **Avg per Page**: 2.44 s
