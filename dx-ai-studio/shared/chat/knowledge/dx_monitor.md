# DX Monitor — NPU 하드웨어 대시보드

## [section:overview,소개,개요] DX Monitor 개요

DX Monitor (포트 8098)는 DEEPX NPU와 호스트 시스템 상태를 **실시간으로 시각화하는 하드웨어 대시보드**입니다.

- **NPU 텔레메트리**: 디바이스별 온도, 전압, 클럭, DRAM, 사용률을 실시간 차트로 표시
- **시스템 정보**: CPU 코어/부하, 메모리, 스왑, 디스크, OS/아키텍처, 가동시간(uptime)
- **버전 정보 패널**: DX-RT / DX-APP / SDK / 드라이버 버전 표시
- **런타임 이벤트 로그**: NPU 스로틀링·에러·복구 이벤트 기록
- **6개 언어 지원**: 한국어/영어/일본어/중국어 간체·번체/스페인어 UI
- NPU 미감지 시 **Mock 텔레메트리**로 자동 대체 (UI 탐색용)

## [section:usage,사용법,사용,실행] 사용 방법

1. 런처(`http://localhost:8890`)에서 **DX Monitor** 카드 클릭
2. 대시보드가 열리면 상단 상태 요약 카드와 실시간 차트가 즉시 표시됨
3. 다른 모듈(DX App, DX Benchmark 등)에서 추론/벤치마크를 실행하는 동안 이 화면을 열어두면 NPU 부하를 실시간 관찰 가능
4. 하단 **시스템 정보** 테이블에서 설치된 DX-RT/DX-APP/SDK/드라이버 버전 확인

## [section:chart,차트,모니터링,telemetry] 실시간 차트 & 텔레메트리

### 시간 범위
`Realtime`(실시간) / `5m` / `15m` / `30m` / `1h` / `All`(전체) 중 선택

### 차트 모드
| 모드 | 항목 |
|------|------|
| NPU Temp | NPU 다이 온도 (코어별) |
| Volt | NPU 공급 전압 (mV) |
| Clock | NPU 동작 클럭 (MHz) |
| NPU DRAM | NPU 전용 메모리 사용량/사용률 |
| NPU Util | NPU 사용률 |
| Core Temp | 코어별 온도 상세 |
| CPU Load | 시스템 CPU 부하 |
| Memory | 시스템 메모리 사용률 |
| CPU Cores | CPU 코어별 사용률 |
| View All | 전체 차트 동시 표시 |

- 유효하지 않은/끊긴 센서는 오해를 유발하는 0°C 대신 **"no data"**로 표시
- **NPU 토폴로지** 뷰: 디바이스 구성 및 상태 배지 표시
- SSE 스트리밍(`/api/hw_stream`)으로 1.5초 간격 실시간 갱신

## [section:sysinfo,시스템,정보,버전] 시스템 정보 & 버전 패널

| 항목 | 내용 |
|------|------|
| OS / Hostname / Arch | `platform` 모듈 기반 |
| Python / OpenCV | 설치된 버전 |
| DX-RT / DX-APP 버전 | `release.ver` 파일 기반 |
| SDK / 드라이버 / PCIe 드라이버 버전 | `dx_engine.Configuration`에서 조회 (SDK 미설치 시 "N/A") |
| Uptime | 시스템 가동 시간 |
| NPU PCIe | `lspci`에서 DEEPX 디바이스 검출 결과 |
| 메모리 / 스왑 / 디스크 | 전체·사용량·사용률(%) |

## [section:event,이벤트,로그,throttle] 런타임 이벤트 로그

- `RuntimeEventDispatcher`(dx_engine)에 핸들러를 등록해 NPU 이벤트를 버퍼링 (최대 200건)
- SDK 미설치 환경에서는 이벤트 로그가 비활성화됨(빈 목록 반환)
- 주요 이벤트 유형: `THROTTLING_NOTICE`, `THROTTLING_EMERGENCY`, `MEMORY_OVERFLOW`, `MEMORY_ALLOCATION`, `DEVICE_EVENT`, `RECOVERY_OCCURRED`, `TIMEOUT_OCCURRED` 등
- 레벨: `INFO` / `WARNING` / `ERROR` / `CRITICAL`
- `/api/events?since=<timestamp>`로 특정 시점 이후 이벤트만 조회 가능

## [section:threshold,임계치,경고] 경고 임계치

| 항목 | 경고(warn) | 위험(crit) |
|------|------------|------------|
| NPU 온도 | 70°C | 85°C |
| 코어 온도 | 70°C | 85°C |
| NPU DRAM 사용률 | 80% | 95% |
| 메모리 사용률 | 80% | 95% |
| CPU 부하 | 코어 수 × 0.8 | 코어 수 × 1.0 |

## [section:api,엔드포인트] API 엔드포인트

| 엔드포인트 | 설명 |
|------------|------|
| `/api/hw_status` | 현재 하드웨어 상태 (1회성 JSON) |
| `/api/hw_stream` | SSE 스트림 (1.5초 간격) |
| `/api/system_info` | 시스템/버전 정보 |
| `/api/events` | 런타임 이벤트 로그 조회 |
| `/api/hb` | 헬스체크 |

## [section:error,troubleshoot,문제,에러] 트러블슈팅

| 증상 | 원인 | 해결 |
|------|------|------|
| Mock 데이터만 표시됨 | dx_engine SDK 미설치/미감지 | NPU 드라이버 설치 후 재시작 (DX App/Compiler에서 설치 가능) |
| 버전이 전부 "N/A" | dx_engine.Configuration 조회 실패 | SDK 설치 확인, `dxrt-cli -s`로 하드웨어 점검 |
| 온도가 "no data" | 센서 값이 유효하지 않음(dead/invalid) | 정상 동작(오해 소지 있는 0°C 대신 표시), 하드웨어 점검 필요 시 DEEPX 문의 |
| 이벤트 로그가 비어 있음 | RuntimeEventDispatcher 미등록(SDK 없음) | dx_engine SDK 설치 필요 |
| 차트가 갱신 안 됨 | SSE 연결 끊김 | 페이지 새로고침, 네트워크/포트(8098) 확인 |
