# DX Benchmark — YOLO26 하드웨어 벤치마크 도구

## [section:overview,소개,benchmark,벤치마크] DX Benchmark 개요

DX Benchmark (Studio 경로 `/benchmark/`)는 **YOLO26 계열 모델의 NPU 하드웨어별 성능을 측정·비교하는 도구**입니다.
- **모델 크기별 비교**: n (Nano), s (Small), m (Medium), l (Large)
- **E2E 파이프라인 성능**: 전처리→추론→후처리 전 구간 FPS/Latency 측정
- **Multi-Stream 용량 테스트**: 30fps 유지 가능한 최대 스트림 수 측정
- **Version Trend**: 소프트웨어 버전별 성능 추이 비교

### 지원 하드웨어
| 보드 | 설명 |
|------|------|
| AI Box (DX-AIPlayer-N97) | DEEPX M1 NPU 탑재 미니 PC |
| ROCK5B+ | Rockchip RK3588 + DEEPX M1 |
| OrangePi5+ | Rockchip RK3588 + DEEPX M1 |
| Raspberry Pi 5 | BCM2712 + DEEPX M1 |
| Raspberry Pi 5 (M1M) | BCM2712 + DEEPX M1M |
| BIOSTAR | DEEPX H1 Quattro NPU 탑재 산업용 보드 |

(번들된 결과 폴더: `BIOSTAR_H1-Quattro`, `DX-AIPlayer-N97_M1`, `OrangePi5+_M1`, `ROCK5B+_M1`, `RPi5B_M1`, `RPi5B_M1M`)

## [section:run,실행,runner,test] 벤치마크 실행 (읽기 전용 뷰어 + CLI)

> **DX Benchmark 웹 UI는 결과를 조회하는 읽기 전용(Read-only) 대시보드입니다.** 벤치마크 자체는 앱 안에서 실행하지 않고, **독립 CLI(standalone tool)**로 수행합니다.

### CLI로 벤치마크 실행
dx-all-suite 루트의 `dx-benchmark/`에서 `./run.sh <command>`로 실행합니다 (`python3 -m benchmark`를 호출).
```bash
cd dx-benchmark
./run.sh preflight                    # 필수 도구 사전 점검 (run_model, dxrt-cli, gst-launch-1.0, gst-inspect-1.0, GNU time)
./run.sh dry-run                      # 실행 없이 벤치마크 매트릭스만 표시
./run.sh run                          # 실제 벤치마크 실행
./run.sh report <result_dir>          # 결과 폴더에서 리포트 재생성
./run.sh aggregate <results_root>     # 여러 결과 폴더 집계 → dataset.json
./run.sh dashboard <results_root>     # 결과 폴더로 정적 대시보드 생성
```

### 측정 항목
- **Model FPS / Latency**: 추론 모델 단독 성능
- **E2E FPS**: 전처리→추론→후처리 전체 파이프라인
- **Multi-Stream Capacity**: 30fps 기준 최대 병렬 스트림 수

CLI 결과는 기본적으로 `dx-benchmark/results/`에 저장됩니다. 웹 UI는 이를 자동으로 가져오지 않습니다:
- **Dashboard** 탭: DX AI Studio에 번들된 `dx_benchmark/dataset.json`을 그대로 보여줌 (런타임 집계 없음) — 새 결과를 반영하려면 `./run.sh aggregate`로 만든 dataset.json으로 교체해야 함
- **Results** 탭: DX AI Studio의 `outputs/benchmark/<hw_id>/<run_id>/` (및 번들된 `dx_benchmark/results/`)의 run 폴더를 목록으로 보여줌

## [section:dashboard,대시보드,chart,차트] Dashboard 탭

Dashboard 탭은 5개의 서브탭으로 구성됩니다: **E2E FPS Overview**, **Full Metrics**, **Detailed Data**, **Version Trend**, **ORT ON/OFF** (ONNX Runtime 사용 여부 비교).

### E2E FPS Overview 서브탭
- 환경(하드웨어)별 Run 선택 → 모델 크기(n/s/m/l/x)별 **E2E FPS** 그룹 막대 차트
- 막대 그룹 클릭 시 Host PC / NPU / Tools 환경 상세 정보 펼침

### Full Metrics 서브탭
- **좌축 (막대)**: FPS (Model Throughput / E2E FPS)
- **우축 (다이아몬드)**: Latency (ms)
- 하드웨어별 비교

### Detailed Data 서브탭
- Task(Object Detection/Pose/Segmentation/OBB/Classification)별 상세 테이블
- 컬럼: Model, Size, ORT, Latency(ms), Throughput(FPS), E2E FPS, Max Channels, NPU Temp(°C), NPU Clock(MHz), Status

### Version Trend 서브탭
- 소프트웨어 버전별 성능 추이 라인 차트
- 스냅샷 데이터 필요 (results 폴더에 복수 run_id 존재 시)

### ORT ON/OFF 서브탭
- 모델 크기별 ORT ON / ORT OFF 값과 차이(Delta, Delta %) 비교 테이블

## [section:result,결과,results,report] Results 탭

### 결과 탐색
1. **하드웨어 선택** → 해당 보드의 실행 목록 표시
2. **Run 선택** → 상세 결과 (환경정보, 모델 성능, 파이프라인 성능)
3. **REPORT.md** — 자동 생성된 마크다운 리포트 뷰어

## [section:settings,설정,config] Settings 탭 (읽기 전용)

Settings 탭은 현재 서버에 적용된 설정값을 **보여주기만 하는(read-only) 화면**입니다. 모든 입력 필드는 `readonly`이며, 웹 UI에서 값을 변경할 수 없습니다 (`POST /api/config`는 501을 반환하며 "Settings are deployment-fixed and cannot be changed at runtime" 메시지를 냅니다).

### 표시 항목
- **Path Settings**: Model Directory / Video Directory / Results Directory — 배포 시 고정, 런타임 변경 불가
- **Thermal Settings**: Cooldown Threshold(°C) / Wait Interval(초) — 배포 시 고정, 서버 시작 전 설정 파일로만 변경 가능
- **Benchmark Parameters**: Iterations / Warmup Runs / FPS Threshold — 배포 시 고정

실제 값을 바꾸려면 서버 시작 전에 설정 파일(`BenchmarkConfig`)을 수정해야 합니다.

## [section:troubleshoot,문제,error,에러] 문제 해결

### Preflight Check 실패 (`./run.sh preflight`)
- **Required tool not found**: 필수 도구가 PATH에 없음 — 출력 옆에 설치 힌트가 함께 표시됨
  - `run_model`, `dxrt-cli` → DEEPX runtime: `dx-runtime/install.sh --all`
  - `gst-launch-1.0`, `gst-inspect-1.0` → `sudo apt-get install -y gstreamer1.0-tools`
  - `time` (GNU time) → `sudo apt-get install -y time`
- **E2E prerequisite missing** (경고): `ffprobe` (`sudo apt-get install -y ffmpeg`), dxstream GStreamer 플러그인, 후처리 라이브러리 — model-level 측정은 가능, E2E/multi-stream만 불가
- **디바이스 파일 없음**: `ls /dev/dxrt*`로 확인, 없으면 NPU 드라이버 로드 확인
- **모델 파일 없음**: Settings 탭에 표시된 Model Directory 경로에 모델 파일이 있는지 확인 (경로 자체는 배포 시 고정이며 UI에서 변경 불가)

### 결과 없음 (No data)
- Dashboard는 번들된 `dx_benchmark/dataset.json`만 읽음 — 파일이 없으면 빈 데이터
- Results 탭은 `outputs/benchmark/` 와 번들된 `dx_benchmark/results/`에 run 폴더가 없으면 비어 있음
- `cd dx-benchmark && ./run.sh run`을 한 번 이상 실행해야 결과가 쌓입니다 (웹 UI 반영 방법은 위 '벤치마크 실행' 참고)

### 차트가 안 보임
- 브라우저 콘솔에서 JavaScript 에러 확인
- dataset.json 파일이 올바르게 생성되었는지 확인
