# finegrained Performance Summary

- **Date**: 2026-06-12 13:28:07
- **Pipeline Mode**: finegrained
- **Total Files**: 1
- **Total Pages**: 9
- **Total Wall Time**: 12.72 s
- **Overall Throughput**: 0.7 pages/s

## Model Loading

| Model | Load Time |
|:---|---:|
| formula | 1.01 s |
| layout | 0.16 s |
| ocr | 0.53 s |
| table | 0.04 s |
| **Total** | **1.74 s** |

## Overall Pipeline Performance

| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |
|:---|---:|---:|---:|---:|---:|
| Layout | 9 | 289.51 ms | 3.5 FPS | 2.61 | 22.1% |
| PDF-det | 82 | 0.50 ms | 2016.0 FPS | 0.04 | 0.3% |
| Table | 13 | 703.03 ms | 1.4 FPS | 9.14 | 77.5% |

- **Total Stages**: 11.79 s

## sample_input

| Pipeline Step | Count | Avg Latency | Throughput | Time (s) | Ratio |
|:---|---:|---:|---:|---:|---:|
| Layout | 9 | 289.51 ms | 3.5 FPS | 2.61 | 22.1% |
| PDF-det | 82 | 0.50 ms | 2016.0 FPS | 0.04 | 0.3% |
| Table | 13 | 703.03 ms | 1.4 FPS | 9.14 | 77.5% |

- **Total Stage Time**: 11.79 s
- **Pages**: 9
- **Avg per Page**: 1.31 s
