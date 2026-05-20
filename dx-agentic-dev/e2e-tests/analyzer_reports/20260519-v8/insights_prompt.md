You are analyzing the results of an end-to-end test suite that evaluates multiple AI
coding agents on a set of code-generation scenarios.

INPUT BELOW:
A comprehensive Markdown report containing quantitative metrics across:
  - Multiple tools (different agentic CLI implementations)
  - Multiple rounds (independent re-runs of the same tasks)
  - Multiple scenarios (different code-generation tasks)

Each session has metrics including: Compliance %, Quality %, Verdict %,
ExecutionTrace %, Overall %, Duration, σ(Overall), Tool Calls, LOC, Token usage,
Premium Requests, Cost, Pass/Partial/Fail verdict, Sentinel emission rate,
and a Cursor-specific bias check section.

YOUR JOB:
Produce a Korean Markdown report (`insights.md`) that derives **data-driven, objective
insights** from the metrics. Do NOT assume any pre-existing findings — let the data
speak. Structure your output as follows.

## 1. 도구별 강점 / 약점 (per-tool)
For EACH tool present in the data, list:
- 3 strengths (what this tool consistently does WELL — cite specific metrics)
- 3 weaknesses (recurring issues observed — cite specific metrics)
- 1 scenario where this tool excels most (highest Overall/Verdict)
- 1 scenario where this tool struggles most (lowest Overall/Verdict)

## 2. 시나리오별 도구 추천 (per-scenario)
For EACH scenario, identify the top-performing tool by composite score, and the
worst-performing tool. Explain the gap quantitatively.

## 3. 회차간 변동성 / 학습 패턴
- Which tools have the LOWEST round-to-round σ(Overall)? Most consistent.
- Which tools show a clear improvement or regression trend across rounds?
- Are there scenario × round combinations that are systematically problematic?

## 4. Outlier / 이상점 탐지
Identify the most striking outliers in the data — sessions or tool×scenario
combinations whose metrics deviate sharply from the median. For each outlier:
- describe the deviation
- propose a plausible cause based on adjacent metrics

## 5. Cost / 효율 분석
Using the Token Usage + Premium Requests + Efficiency Index data:
- Which tool delivered the BEST cost-effectiveness (verdict achieved per token/request)?
- Are there tools whose token/request count is disproportionate to their output quality?
- For tools using identical or comparable underlying models, are there efficiency gaps?

## 6. 메트릭 신뢰성 점검
Note any metrics that appear unreliable, biased, or limited:
- Cite the bias-check section if applicable
- Identify metrics with poor cross-tool comparability (e.g., tool call counting variance)
- Flag any cases where Verdict and Overall disagree (artifact exists but score low, or vice versa)

## 7. 향후 운영 권장
Based on the data, provide actionable recommendations for future rounds.
Examples (only include if data supports them):
- Whether to deprecate/de-prioritize any tool
- Whether to change the scoring weights based on observed metric stability
- Whether to add additional scenarios or replace existing ones
- Whether to adjust timeout limits based on observed durations

OUTPUT REQUIREMENTS:
- All sections in Korean
- Cite **specific numbers** from the input data — never speculate without data backing
- Identify findings DIRECTLY from the data; do not import outside assumptions
- If the data is insufficient for a section, explicitly say so rather than guessing
- Start the output directly with the `# ` heading (no preamble)

CRITICAL OUTPUT MECHANISM:
- The stdout of your response IS the `insights.md` file. The wrapper script captures
  your stdout verbatim and writes it to the target path.
- DO NOT use the Write, Edit, or any file-creation tools. The file already has a path
  determined by the wrapper — your job is to emit the content, not to save it.
- DO NOT wrap your output in a code fence or quote block. Emit raw markdown.
- DO NOT add a trailing sentence describing what you did (e.g., "insights.md 생성 완료").
  The first line MUST be `# ` and the last line MUST be the actual final markdown content.

REPORT INPUT:
====================

# DEEPX Agentic Development — E2E Autopilot 분석 리포트

> 생성 시각: 2026-05-19T11:08:13
> 분석 대상 sessions: **602** (5 tools × 21 rounds × 6 scenarios)
> Results root: `/data/home/dhyang/github/dx-all-suite-full-e2e/dx-agentic-dev/e2e-tests/results`

## ⚠️ 주의 사항
- `cursor-cli-autopilot` → model `cursor-auto (non-standard)` (Cursor subscription cap exceeded — auto model used instead of claude-sonnet-4.6. Flagged for re-run)

## 📖 점수 산정 방식 (Quick Reference)

```
Overall % = 0.30·Compliance% + 0.20·Quality% + 0.30·ExecutionTrace% + 0.20·Runnability%
Runnability = End-user 실행 가능성 (LLM 판정) — runnability_report.md 없으면 나머지 3-factor 비례 배분
```

- **Compliance** (30%) = HARD GATE 체크 통과율 (sentinel START/DONE, output isolation, mandatory deliverables, IFactory, session_log authentic, suite dual dirs)
- **Quality** (20%) = py_compile + JSON parse + bash -n 통과율, placeholder/anti-pattern 페널티
- **ExecutionTrace** (30%) = 실제 실행 흔적 — session.log substantive + 성공 마커 + .dxnn realistic size + no failure markers
- **Runnability** (20%) = End-user가 README/setup.sh/run.sh 따라 실제 실행 가능한지 LLM 판정 (PASS/PARTIAL/FAIL + 세부 1-5점)
- **Verdict** (정보용) = 산출물 PASS/PARTIAL/FAIL 판정 — Compliance mandatory_deliverables와 중복이므로 점수 미반영, 시각화 참조용
- **Exit 0 %** = pytest 라운드 전체의 exit 코드 (라운드 단위, **시나리오 단위 ≠**). **Overall 에는 미반영** — 정보용.

## 1. 도구별 종합 점수

> ⚠️ **가성 결함(False Alarm) 제외**: 환경 문제(API rate limit, TLS error, CLI crash)로 인한 완전 실패 세션 **52건**이 점수 평균 산정 모수에서 제외되었습니다. 이 세션들은 도구 능력이 아닌 인프라 문제를 반영하므로 가성 결함으로 분류됩니다.

| 도구 | 제외 세션 수 | 원인 |
|------|----------:|------|
| claude-code | 21 | R14, R18, R19, R20 |
| cursor-cli | 30 | R4, R5, R6, R7, R19, R20 |
| opencode-cli | 1 | R5 |

| Rank | Tool | Scored/Total | Compl % | Qual % | Verdict % | Exec % | Runn % | Overall % | σ(Overall) | Avg Duration | START % | DONE % | Pass/Part/Fail | pytest Exit0 % | ⏱ Timeout | ToolCalls | LOC |
|-----:|------|------------:|-------:|------:|----------:|------:|------:|----------:|----------:|-------------:|--------:|-------:|:--------------:|---------------:|----------:|---------:|----:|
| 🥇 | **claude-code** | 99/120 | 93.2 | 98.2 | 89.9 | 44.5 | 83.2 | 77.6 | 10.6 | 8.9m | 100.0 | 92.9 | 88 / 2 / 1 | 20.0 | 1 | 69.2 | 293 |
| 🥈 | **cursor-cli** | 90/120 | 92.6 | 99.7 | 88.9 | 43.2 | 73.3 | 75.4 | 10.8 | 12.8m | 98.9 | 97.8 | 80 / 0 / 1 | 30.0 | 5 | 54.6 | 228 |
| 🥉 | **opencode-cli** | 119/120 | 92.4 | 95.9 | 91.6 | 44.0 | 69.2 | 74.0 | 10.1 | 12.0m | 100.0 | 97.5 | 109 / 0 / 0 | 75.0 | 25 | 37.5 | 522 |
| 4 | **codex-cli** | 120 | 93.0 | 97.8 | 89.2 | 40.5 | 69.3 | 73.5 | 10.6 | 12.2m | 100.0 | 95.8 | 106 / 2 / 1 | 0.0 | 44 | 45.2 | 294 |
| 5 | **copilot-cli** | 122 | 89.4 | 98.2 | 87.7 | 43.0 | 66.1 | 72.6 | 10.1 | 13.0m | 100.0 | 96.7 | 107 / 0 / 5 | 31.1 | 0 | 59.1 | 295 |

> **σ (sigma)** = stdev (낮을수록 일관성이 높음). **Exec %** = ExecutionTrace 점수 (실제 명령 실행 흔적). **⏱ Timeout** = 의심 timeout 발생 세션 수 (참고용; 점수에 페널티 없음). **Scored/Total** = 점수 산정 포함 세션 / 전체 세션 (환경 실패 제외). **START/DONE %** = sentinel 준수율 (Compliance %에 포함 반영). **Verdict %** = 정보용 (Overall 미반영).

## 2. 평가 메트릭 해설 및 시나리오별 세분화

> 각 메트릭의 정의와 측정 방법을 설명한 뒤, 바로 도구 × 시나리오별 데이터를 제시합니다.

### 2.1 Overall % (종합 점수)

```
Overall = 0.30×Compliance + 0.20×Quality + 0.30×ExecutionTrace + 0.20×Runnability
```

- Runnability 데이터가 없는 세션은 나머지 3-factor 비례 배분 (backward compatible)
- Verdict는 Compliance mandatory_deliverables와 중복이므로 점수 미반영 (정보용 매트릭스만 표시)

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **claude-code** | 87.3 | 77.7 | 74.7 | 74.3 | 81.6 | 69.4 | 77.5 |
| 🥈 | **cursor-cli** | 86.5 | 76.8 | 72.8 | 72.5 | 78.3 | 63.8 | 75.1 |
| 🥉 | **opencode-cli** | 86.0 | 75.0 | 75.4 | 73.9 | 74.5 | 59.5 | 74.1 |
| 4 | **codex-cli** | 85.6 | 68.8 | 69.7 | 73.5 | 79.3 | 63.8 | 73.5 |
| 5 | **copilot-cli** | 80.0 | 76.1 | 74.9 | 75.7 | 70.3 | 59.3 | 72.7 |

### 2.2 Compliance % (HARD GATE 체크 통과율, 가중치 30%)

- `sentinel_start` — 응답 첫 줄 `[DX-AGENTIC-DEV: START]`
- `sentinel_done` — 마지막 줄 `[DX-AGENTIC-DEV: DONE (output-dir: ...)]`
- `output_isolation_present` — 산출물이 `dx-agentic-dev/<session_id>/` 하위
- `session_id_format` — `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` 패턴
- `mandatory_deliverables` — 시나리오별 필수 파일 존재 (setup.sh, run.sh, README.md, session.log, factory, *_sync.py 등)
- `ifactory_5_methods` — dx_app factory 5-method 패턴
- `session_log_authentic` — session.log 가 hand-written heredoc 아님
- `suite_dual_session_dirs` — suite 시나리오에서 2개 별도 sub-project dir 생성 (R41 HARD GATE)

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **claude-code** | 96.5 | 99.4 | 95.3 | 95.8 | 97.9 | 73.6 | 93.1 |
| 🥈 | **codex-cli** | 100.0 | 97.0 | 93.9 | 99.2 | 99.2 | 68.6 | 93.0 |
| 🥉 | **opencode-cli** | 100.0 | 100.0 | 100.0 | 99.2 | 90.8 | 65.0 | 92.5 |
| 4 | **cursor-cli** | 97.3 | 100.0 | 97.1 | 93.3 | 100.0 | 65.7 | 92.3 |
| 5 | **copilot-cli** | 90.0 | 100.0 | 100.0 | 100.0 | 83.3 | 64.6 | 89.7 |

### 2.3 Quality % (정적 코드 품질, 가중치 20%)

- 모든 `.py` 파일 `py_compile` → 통과율
- 모든 `.json` 파일 `json.load` → 통과율
- 모든 `.sh` 파일 `bash -n` → 통과율
- **Placeholder** 페널티: `# TODO: implement`, 주석된 import, `np.zeros(...)` 등 (hit 당 5점, cap 30)
- **Direct engine use** 페널티: factory 외부 `engine.run()` — HARD GATE 위반 (hit 당 5점, cap 15)

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **cursor-cli** | 99.7 | 100.0 | 100.0 | 100.0 | 98.9 | 99.6 | 99.7 |
| 🥈 | **copilot-cli** | 96.2 | 100.0 | 100.0 | 100.0 | 95.5 | 97.6 | 98.2 |
| 🥉 | **claude-code** | 95.9 | 100.0 | 100.0 | 100.0 | 95.9 | 97.2 | 98.2 |
| 4 | **codex-cli** | 94.8 | 100.0 | 100.0 | 100.0 | 94.5 | 97.5 | 97.8 |
| 5 | **opencode-cli** | 88.3 | 99.8 | 100.0 | 100.0 | 91.8 | 95.5 | 95.9 |

### 2.4 Verdict (산출물 PASS/PARTIAL/FAIL — 정보용, Overall 미반영)

> ⚠️ Verdict는 Compliance `mandatory_deliverables`와 측정 대상이 중복되어 Overall 점수에 미반영합니다.
> 산출물 상태 시각화 용도로만 제공됩니다.

- `compiler`: PASS = `*.dxnn` + `config.json` 존재 / FAIL = `.dxnn` 미생성
- `dx_app`: PASS = factory + `*_sync.py` / PARTIAL = factory 만 / FAIL = factory 없음
- `dx_stream` / `dx_stream_cascaded`: PASS = `pipeline.py` + `run_*.sh`
- `runtime`: PASS = sub-project 출력 중 하나 이상이 형식 통과
- `suite`: PASS = dx-compiler + dx_app 둘 다 자체 dir (R41 HARD GATE)

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **opencode-cli** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 50.0 | 91.7 |
| 🥈 | **claude-code** | 94.1 | 100.0 | 94.1 | 93.8 | 100.0 | 56.2 | 89.7 |
| 🥉 | **codex-cli** | 100.0 | 95.0 | 95.0 | 100.0 | 100.0 | 45.0 | 89.2 |
| 4 | **cursor-cli** | 93.8 | 100.0 | 100.0 | 93.3 | 100.0 | 42.9 | 88.3 |
| 5 | **copilot-cli** | 75.0 | 100.0 | 100.0 | 100.0 | 100.0 | 52.4 | 87.9 |

### 2.5 ExecutionTrace % (실제 실행 흔적, 가중치 30%)

- session.log substantive (실질적 내용 포함)
- 성공 마커 존재 (compile success, inference output 등)
- .dxnn realistic size (>1KB)
- no failure markers (traceback, error 등)

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **opencode-cli** | 73.5 | 34.5 | 35.0 | 35.0 | 56.5 | 27.2 | 43.6 |
| 🥈 | **copilot-cli** | 68.8 | 35.8 | 33.2 | 35.2 | 54.8 | 30.5 | 43.0 |
| 🥉 | **codex-cli** | 72.0 | 28.0 | 27.8 | 29.0 | 57.8 | 28.5 | 40.5 |
| 4 | **claude-code** | 62.2 | 31.0 | 28.0 | 27.0 | 45.2 | 26.8 | 36.7 |
| 5 | **cursor-cli** | 61.5 | 29.8 | 25.5 | 24.0 | 37.8 | 16.0 | 32.4 |

### 2.6 Runnability % (End-user 실행 가능성, 가중치 20%)

- End-user가 README/setup.sh/run.sh 따라 실제 실행 가능한지 LLM 판정
- PASS(100)/PARTIAL(50)/FAIL(0) + 세부 1-5점 스케일
- `runnability_report.md` 없으면 나머지 3-factor 비례 배분

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **claude-code** | 86.2 | 84.9 | 81.3 | 77.3 | 80.2 | 89.2 | 83.2 |
| 🥈 | **cursor-cli** | 71.6 | 78.0 | 67.4 | 74.6 | 61.7 | 86.5 | 73.3 |
| 🥉 | **codex-cli** | 75.4 | 56.3 | 66.3 | 75.4 | 66.8 | 75.8 | 69.3 |
| 4 | **opencode-cli** | 75.6 | 73.5 | 74.7 | 68.5 | 59.5 | 63.6 | 69.2 |
| 5 | **copilot-cli** | 65.8 | 76.7 | 74.7 | 75.8 | 48.9 | 56.1 | 66.3 |

### 2.7 보조 메트릭 (Overall 점수에 미반영)

다음 메트릭은 점수 산정에 직접 포함되지 않으며, 참고 정보로 제공됩니다.

#### PASS / FAIL 비율

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **opencode-cli** | 100.0 | 100.0 | 100.0 | 100.0 | 100.0 | 50.0 | 91.7 |
| 🥈 | **claude-code** | 94.1 | 100.0 | 94.1 | 93.8 | 100.0 | 50.0 | 88.7 |
| 🥉 | **codex-cli** | 100.0 | 95.0 | 95.0 | 100.0 | 100.0 | 40.0 | 88.3 |
| 4 | **cursor-cli** | 93.8 | 100.0 | 100.0 | 93.3 | 100.0 | 42.9 | 88.3 |
| 5 | **copilot-cli** | 75.0 | 100.0 | 100.0 | 100.0 | 100.0 | 52.4 | 87.9 |

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **opencode-cli** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 |
| 🥈 | **codex-cli** | 0.0 | 5.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.8 |
| 🥉 | **claude-code** | 0.0 | 0.0 | 0.0 | 6.2 | 0.0 | 0.0 | 1.0 |
| 4 | **cursor-cli** | 6.2 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 1.0 |
| 5 | **copilot-cli** | 25.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 4.2 |

#### Duration (실행 시간)

- Claude Code: `result.duration_ms` (stream-json 최종 이벤트)
- Cursor: `result` event 의 `duration_ms`
- OpenCode: `timestamp` (Unix ms) 첫/마지막 이벤트 차이
- Copilot: events-*.jsonl 의 첫/마지막 이벤트 timestamp
- Fallback: artifact + output dir 파일 mtime 의 최대-최소 차이

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **claude-code** | 9.5m | 7.0m | 6.4m | 7.4m | 14.3m | 8.9m | 8.9m |
| 🥈 | **opencode-cli** | 32.8m | 3.9m | 3.6m | 4.2m | 18.6m | 10.0m | 12.2m |
| 🥉 | **codex-cli** | 27.4m | 9.0m | 7.2m | 7.0m | 15.2m | 7.5m | 12.2m |
| 4 | **cursor-cli** | 33.8m | 5.4m | 4.2m | 4.6m | 19.0m | 9.2m | 12.7m |
| 5 | **copilot-cli** | 28.5m | 6.1m | 5.9m | 7.0m | 19.3m | 11.3m | 13.0m |

#### Tool Calls & Python LOC

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **claude-code** | 65.5 | 73.9 | 62.3 | 67.2 | 89.6 | 57.1 | 69.3 |
| 🥈 | **copilot-cli** | 49.2 | 58.8 | 53.1 | 51.8 | 90.4 | 50.2 | 58.9 |
| 🥉 | **cursor-cli** | 65.2 | 52.4 | 35.6 | 40.9 | 92.4 | 42.0 | 54.8 |
| 4 | **codex-cli** | 53.0 | 48.0 | 45.3 | 40.4 | 59.1 | 25.2 | 45.2 |
| 5 | **opencode-cli** | 39.9 | 42.2 | 35.1 | 36.4 | 54.0 | 17.2 | 37.5 |

| Rank | Tool | compiler | dx_app | dx_stream | dx_stream_cascaded | runtime | suite | 평균 |
|-----:|------|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|-----:|
| 🥇 | **opencode-cli** | 507.1 | 288.5 | 186.7 | 245.1 | 1277.1 | 632.5 | 522.8 |
| 🥈 | **claude-code** | 254.2 | 241.9 | 144.9 | 192.6 | 583.1 | 356.7 | 295.6 |
| 🥉 | **codex-cli** | 232.4 | 228.1 | 191.4 | 228.2 | 624.0 | 260.7 | 294.2 |
| 4 | **copilot-cli** | 179.8 | 232.2 | 171.8 | 211.9 | 634.5 | 325.4 | 292.6 |
| 5 | **cursor-cli** | 220.9 | 261.4 | 189.4 | 194.9 | 342.1 | 162.8 | 228.6 |

#### Tool Calls Efficiency Index

단순 tool call 수는 효율을 직접 나타내지 않습니다. 적은 호출이 높은 성공률과 결합될 때만 의미 있습니다.

```
Efficiency Index = (Compliance% × ExecutionTrace%) / (Tool Calls + 1) × 100
```

| Rank | Tool | Avg Tool Calls | Avg Compl % | Avg Exec % | **Efficiency Index** |
|-----:|------|---------------:|------------:|-----------:|---------------------:|
| 🥇 | **opencode-cli** | 37.1 | 91.7 | 43.6 | **10482.2** |
| 🥈 | **codex-cli** | 45.2 | 93.0 | 40.5 | **8155.0** |
| 🥉 | **copilot-cli** | 59.1 | 89.4 | 43.0 | **6400.7** |
| 4 | **cursor-cli** | 40.9 | 69.5 | 32.4 | **5370.1** |
| 5 | **claude-code** | 57.1 | 76.9 | 36.7 | **4859.6** |

> **해석 유의사항**: tool call 당 작업 granularity는 도구마다 다릅니다 (Claude Code는 1 Bash에 multi-line 명령을 묶고, Copilot/OpenCode는 개별 호출로 분해). 따라서 Efficiency Index는 도구 간 상대 비교보다 동일 도구 내 회차별 추세 파악에 더 적합합니다.

#### pytest Exit 0 %

- pytest 의 round-level exit code (한 라운드에 6개 시나리오; 그 중 한 assertion 실패 시 1)
- **Overall 점수에는 미반영** (라운드 단위 → 시나리오 단위로 분해 불가). 별도 컬럼으로 표시.
- 진정한 시나리오별 pass/fail 은 Verdict 컬럼이 더 정확.

## 3. 도구별 회차별 추이

### 3.1 Overall %

| Rank | Tool | R5 | 평균 |
|-----:|------|:-----:|-----:|
| 🥇 | **claude-code** | 80.6 | 80.6 |
| 🥈 | **copilot-cli** | 76.3 | 76.3 |
| 🥉 | **codex-cli** | 76.0 | 76.0 |
| 4 | **opencode-cli** | 74.1 | 74.1 |
| 5 | **cursor-cli** | 0.0 | 0.0 |

### 3.2 Compliance %

| Rank | Tool | R5 | 평균 |
|-----:|------|:-----:|-----:|
| 🥇 | **claude-code** | 100.0 | 100.0 |
| 🥈 | **codex-cli** | 100.0 | 100.0 |
| 🥉 | **opencode-cli** | 93.8 | 93.8 |
| 4 | **copilot-cli** | 92.5 | 92.5 |
| 5 | **cursor-cli** | 0.0 | 0.0 |

### 3.3 Avg Duration

| Rank | Tool | R5 | 평균 |
|-----:|------|:-----:|-----:|
| 🥇 | **cursor-cli** | - | 12.8m |
| 🥈 | **opencode-cli** | 6.3m | 12.0m |
| 🥉 | **claude-code** | 8.6m | 8.9m |
| 4 | **codex-cli** | 17.5m | 12.2m |
| 5 | **copilot-cli** | 27.9m | 13.0m |

## 4. 회차 × 시나리오 × 도구 — Verdict 매트릭스

### compiler

| Tool | R5 |
|------|:-----:|
| **claude-code** | ✅ 91.8 |
| **codex-cli** | ✅ 86.6 |
| **copilot-cli** | ✅ 81.9 |
| **cursor-cli** | ❓ 34.3 |
| **opencode-cli** | ❓ 35.1 |

### dx_app

| Tool | R5 |
|------|:-----:|
| **claude-code** | ✅ 80.5 |
| **codex-cli** | ✅ 68.8 |
| **copilot-cli** | ✅ 75.8 |
| **cursor-cli** | ❓ 35.6 |
| **opencode-cli** | ✅ 76.7 |

### dx_stream

| Tool | R5 |
|------|:-----:|
| **claude-code** | ✅ 76.8 |
| **codex-cli** | ✅ 73.8 |
| **copilot-cli** | ✅ 75.4 |
| **cursor-cli** | ❓ 33.5 |
| **opencode-cli** | ✅ 75.4 |

### dx_stream_cascaded

| Tool | R5 |
|------|:-----:|
| **claude-code** | ✅ 76.0 |
| **codex-cli** | ✅ 72.6 |
| **copilot-cli** | ✅ 75.7 |
| **cursor-cli** | ❓ 34.9 |
| **opencode-cli** | ✅ 74.2 |

### runtime

| Tool | R5 |
|------|:-----:|
| **claude-code** | ✅ 78.5 |
| **codex-cli** | ✅ 76.4 |
| **copilot-cli** | ✅ 73.3 |
| **cursor-cli** | ❓ 32.3 |
| **opencode-cli** | ✅ 71.4 |

### suite

| Tool | R5 |
|------|:-----:|
| **claude-code** | ✅ 80.3 |
| **codex-cli** | ✅ 78.2 |
| **copilot-cli** | ✅ 75.4 |
| **cursor-cli** | ❓ 37.3 |
| **opencode-cli** | ✅ 72.9 |

## 5. 회차별 FAIL Verdict 카운트

| Rank | Tool | R5 | 합계 |
|-----:|------|:-----:|-----:|
| 🥇 | **claude-code** | 0 | **0** |
| 🥈 | **codex-cli** | 0 | **0** |
| 🥉 | **copilot-cli** | 0 | **0** |
| 4 | **cursor-cli** | 0 | **0** |
| 5 | **opencode-cli** | 0 | **0** |

## 6. 토큰 사용량 + 비용 효율성

### 6.1 비용 대비 성능 종합 판단

아래는 당사 구독 형태, 도구 사용 방법, E2E 테스트 결과를 종합한 비용 현황입니다. **일관된 기준의 도구 간 비용 비교는 현실적으로 불가능**하므로, 현황 데이터만 제시합니다.

#### A. Copilot Provider 사용 도구 (PR 단위 과금)

copilot-cli, opencode-cli, codex-cli는 GitHub Copilot backend를 사용하며, 초과 사용 시 Premium Request 단위로 과금됩니다.

| 도구 | E2E Overall | Avg PR/Session | PR 측정 방식 |
|------|----------:|---------------:|------------|
| **copilot-cli** | 72.6 | 43.6 | 관측치 (`totalPremiumRequests`) |
| **opencode-cli** | 74.0 | ~86.9 | 예측치 (token ratio 역산) |
| **codex-cli** | 73.5 | ~169.7 | 예측치 (token ratio 역산) |

> **측정 한계**: copilot-cli만 `session.shutdown.totalPremiumRequests`로 실측값을 제공합니다. opencode-cli와 codex-cli는 동일 backend를 경유하지만 PR 소비량이 stream에 노출되지 않아 token ratio 역산 또는 user-turn × multiplier 공식으로 추정해야 합니다 (§6.2 참조).

#### B. 정액 구독 도구 (한도 내 사용)

| 도구 | E2E Overall | 과금 체계 | 비고 |
|------|----------:|---------|------|
| **claude-code** | 77.6 | Anthropic Team Plan 정액 | 세션/주간 한도 내 사용, 추가 비용 없음 |
| **cursor-cli** | 75.4 | Cursor Team Plan 정액 | auto 모델 한도 내, 초과 시 제한됨 |

> **결론**: 정액 구독 도구는 토큰 사용량과 무관하게 월 고정 비용만 발생하므로, **비용 효율성은 '동일 구독 한도 내에서 더 많은 성공적 세션을 완료하는가'로 판단**하는 것이 적절합니다. E2E Overall Score가 이 기준에 가장 가까운 지표입니다.

### 6.2 Premium Request 측정 및 예측 방법론

#### 관측 현황

| 도구 | PR 관측 가능 여부 | 방식 |
|------|:--------------:|------|
| **copilot-cli** | ✅ 가능 | `session.shutdown.totalPremiumRequests` (정확도 이슈 있음 — [#1764](https://github.com/github/copilot-cli/issues/1764)) |
| **opencode-cli** | ❌ 불가 | stream에 PR 정보 미노출 |
| **codex-cli** | ❌ 불가 | stream에 PR 정보 미노출 |

> 참고: claude-code (Anthropic Team Plan), cursor-cli (Cursor Team Plan)는 PR 개념이 없는 정액 구독입니다.

#### 예측 공식 (user-turn × multiplier)

GitHub의 Premium Request 카운팅 규칙에 따르면, **사용자 프롬프트(turn)만 1회로 계산**하고 에이전트의 tool call은 카운트하지 않습니다:

```
Premium Requests ≈ Σ (user_turn_count_per_model × multiplier)
```

**2026.05 기준 모델별 Multiplier (Paid plan):**

| Model | Multiplier | 비고 |
|-------|----------:|------|
| GPT-5 mini / GPT-4.1 / GPT-4o | 0× | 무료 모델 |
| Claude Haiku 4.5, Gemini 3 Flash | 0.33× | |
| **Claude Sonnet 4.6** (E2E 기본 모델) | **1×** | |
| Claude Opus 4.5/4.6 | 3× | |
| GPT-5.5 | 7.5× | |
| Claude Opus 4.7 | 15× | |

#### 현재 예측 방식 (token ratio 역산)

본 분석기는 copilot-cli의 실측 데이터로 calibration ratio를 산출하고, opencode-cli/codex-cli에 적용합니다:

```
calibration_ratio = copilot-cli 총 (input+output) tokens / 총 premium requests
estimated_PR = (input+output) tokens / calibration_ratio
```

> ⚠ **한계**: token ratio 역산은 도구별 token 보고 의미론이 다르기 때문에 오차가 큽니다. **user-turn × multiplier 방식**이 더 정확하나, 현재 세션 파서에 user_turn_count 추출이 미구현입니다.

#### 향후 개선 계획

1. 세션 파서에 `user_turn_count` 추출 추가 (codex-cli: `conversation` events, opencode-cli: `message.user` events)
2. `Premium Requests ≈ user_turns × model_multiplier` 공식 적용
3. copilot-bridge 프록시 경유 시 정확한 카운트 수집 가능 ([xjin6/codex-copilot-bridge](https://github.com/xjin6/codex-copilot-bridge))

#### ⚠ 2026.06 과금 체계 변경 예정

GitHub는 **request-based → usage-based billing**으로 전환합니다 ([공식 블로그](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)). Premium Request Unit(PRU)이 사라지고 **GitHub AI Credits** (input/output/cached token 기반)로 변경되므로, 이후에는 token usage × 모델 단가로 비용을 산정해야 합니다.

**참고 자료:**

- [GitHub Docs — Requests in GitHub Copilot](https://docs.github.com/en/copilot/concepts/billing/copilot-requests)
- [GitHub Docs — Models and Pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
- [GitHub Blog — Moving to usage-based billing](https://github.blog/news-insights/company-news/github-copilot-is-moving-to-usage-based-billing/)
- [Monitoring your Copilot usage](https://docs.github.com/copilot/how-tos/monitoring-your-copilot-usage-and-entitlements)
- [copilot-cli #1764 — Est. 0 Premium requests](https://github.com/github/copilot-cli/issues/1764)
- [anomalyco/opencode #768 — Tracking Premium Requests](https://github.com/anomalyco/opencode/issues/768)
- [anomalyco/opencode #14539 — Tool usages consumes premium request](https://github.com/anomalyco/opencode/issues/14539)

### 6.3 도구별 누적 토큰 — Raw (전체 602 sessions 합계)

> ⚠ **토큰 의미론이 도구별로 다릅니다.** 아래 표의 수치는 각 도구 stream에서 추출한 원본(raw) 값이며, 직접 비교에는 주의가 필요합니다. 차이 원인은 §6.4에서 설명합니다.

| Tool | Sessions | Fresh Input | Output | Cache Read (raw) | Cache Write | Reasoning | Avg Output/Sess |
|------|--------:|-----------:|-------:|-----------------:|------------:|----------:|----------------:|
| **claude-code** | 93/120 | 35,668 | 270,906 | 1,154,210,861 | 27,357,187 | 0 | 2,257 |
| **codex-cli** | 105/120 | 8,106,415 | 2,118,746 | 249,568,256 | 0 | 641,562 | 17,656 |
| **copilot-cli** | 112/122 | 164,619 | 2,506,276 | 451,285,638 | 15,529,328 | 0 | 20,543 |
| **cursor-cli** | 80/120 | 10,177,591 | 1,254,186 | 259,576,223 | 528,408 | 0 | 10,451 |
| **opencode-cli** | 109/120 | 3,683,606 | 1,550,631 | 246,566,460 | 10,067,781 | 0 | 12,921 |

### 6.4 도구별 토큰 보고 의미론 차이

각 도구/provider의 stream 형식에 따라 토큰 필드의 의미가 다릅니다:

| 도구 | `input_tokens` 의미 | `cache_read` 의미 | 보정 방법 |
|------|-------------------|------------------|----------|
| **claude-code** | Fresh only (Anthropic API native) | **Per-turn SUM** — 매 turn마다 전체 캐시 컨텍스트를 재보고 → 누적 합산 시 ~100× 과대 | 마지막 turn의 cache_read가 실제 context window |
| **copilot-cli** | Fresh (total − cache_read − cache_write로 보정 완료) | Session 합계 ✅ | 이미 보정됨 |
| **codex-cli** | Fresh (total − cached로 보정 완료) | Session cached ✅ | 이미 보정됨 |
| **cursor-cli** | Fresh (Anthropic backend, result event) | Session 합계 ✅ | 보정 불필요 |
| **opencode-cli** | Per-step incremental SUM | Per-step cache SUM | provider 의존, 대체로 정상 |

> **결론**: `Fresh Input`과 `Output`은 도구 간 비교 가능합니다. `Cache Read`는 claude-code만 per-turn 합산으로 과대 보고되므로 직접 비교에 부적합합니다.

### 6.5 외부 벤치마크 기반 모델 비용 효율성 참고

도구 간 직접 비용 비교가 불가능하므로, 외부 벤치마크의 **모델별 성능 대비 비용** 데이터를 참고로 제시합니다.

#### A. Aider Polyglot Coding Benchmark (2025.11)

출처: [aider.chat/docs/leaderboards](https://aider.chat/docs/leaderboards/) — 225 exercises (C++, Go, Java, JS, Python, Rust)

| Model | Edit Accuracy | Run Cost | 비고 |
|-------|-------------:|--------:|------|
| GPT-5 (high) | 88.0% | $29.08 | 최고 정확도 |
| GPT-5 (medium) | 86.7% | $17.69 | 비용 대비 최고 효율 |
| Claude Opus 4 (no think) | 70.7% | $68.63 | 높은 비용 |
| Claude Opus 4 (32k think) | 72.0% | $65.75 | thinking 효과 미미 |
| Claude Sonnet 4 (32k think) | 61.3% | $26.58 | |
| Claude Sonnet 4 (no think) | 56.4% | $15.82 | |
| GPT-4.1 | 52.4% | $9.86 | 저비용 |
| DeepSeek-V3.2-Exp (Reasoner) | 74.2% | $1.30 | **극히 저렴** |

> ⚠ Claude Sonnet **4.6**, Opus **4.6/4.7**, GPT-5.x-**Codex** 변형은 아직 Aider 리더보드에 미등재 (2025.11 기준). 위 수치는 이전 세대 모델 기준입니다.

#### B. SWE-Bench Verified (실제 GitHub Issue 해결률)

출처: [github.com/swe-bench/experiments](https://github.com/swe-bench/experiments) — 500 issues

| Agent + Model | Resolve Rate | 날짜 |
|--------------|------------:|------|
| OpenHands + Claude Opus 4.5 | 77.6% (388/500) | 2025.11 |
| Sonar Foundation + Claude Sonnet 4.5 | 74.8% (374/500) | 2025.11 |

> SWE-bench는 2025.11부터 학술 팀 + 오픈소스 방법론만 접수하는 정책으로 변경되어, 최신 상용 모델(Sonnet 4.6, Opus 4.6/4.7)의 공식 결과는 부재합니다.

#### C. GitHub Copilot Premium Request 모델별 Multiplier (2026.06 이전)

출처: [GitHub Docs — Models and Pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)

| Model | 현재 Multiplier | 2026.06+ Multiplier |
|-------|---------------:|-------------------:|
| **Claude Sonnet 4.6** | **1×** | **9×** |
| **Claude Opus 4.6** | **3×** | **27×** |
| Claude Opus 4.7 | 15× | 27× |
| GPT-5.2-Codex | 1× | 3× |
| GPT-5.3-Codex | 1× | 6× |
| GPT-4.1 (included) | 0× | 1× |
| GPT-5 mini (included) | 0× | 0.33× |

> ⚠ **2026.06 가격 인상 예정**: Sonnet 4.6은 1× → 9×, Opus 4.6은 3× → 27×로 대폭 인상. Copilot provider 기반 도구(copilot-cli, opencode-cli, codex-cli)의 실질 비용이 크게 증가할 전망입니다.

#### D. Anthropic API Token 단가 (참고용)

| Model | Input /MTok | Output /MTok | Cache Read /MTok | Cache Write /MTok |
|-------|----------:|----------:|----------:|----------:|
| Claude Sonnet 4.6 | $3.00 | $15.00 | $0.30 | $3.75 |
| Claude Opus 4.6 | $5.00 | $25.00 | $0.50 | $6.25 |
| Claude Opus 4.7 | $5.00 | $25.00 | $0.50 | $6.25 |
| Claude Haiku 4.5 | $1.00 | $5.00 | $0.10 | $1.25 |

### 6.6 외부 Provider Usage Dashboard (실제 사용량 검증용)

| Provider | Dashboard | 비고 |
|----------|-----------|------|
| **Anthropic** | https://console.anthropic.com/settings/usage | claude-code 실사용량 |
| **GitHub Copilot** | https://github.com/organizations/`<ORG>`/settings/copilot/usage | copilot-cli PR 소비량 |
| **Cursor** | https://cursor.com/dashboard | cursor-cli 사용량 |

## 7. 세션별 상세 (전체)

> 총 602개 세션. HTML 보고서에서는 접기/펼치기로 제공됩니다.

| R | Tool | Scenario | Model | Verdict | Exec % | Runn % | ⏱ | pytest | Duration | Comp % | Qual % | Overall % | S/D | ToolCalls | LOC | PH | Eng | Reason |
|--:|------|----------|-------|:------:|------:|------:|:--:|:------:|---------:|------:|------:|---------:|:--:|---------:|---:|---:|----:|-------|
| 1 | claude-code | compiler | 4.6 | ✅ PASS | 75.0 | 86.2 |  | 0 | 2.3m | 100.0 | 100.0 | 89.8 | ✓/✓ | 69 | 167 | 0 | 0 | .dxnn + config.json present |
| 1 | claude-code | dx_app | 4.6 | ✅ PASS | 35.0 | 84.9 |  | 0 | 7.7m | 100.0 | 100.0 | 77.5 | ✓/✓ | 94 | 235 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 1 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 0 | 7.8m | 100.0 | 100.0 | 76.8 | ✓/✓ | 64 | 151 | 0 | 0 | pipeline.py + run script |
| 1 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 0 | 7.8m | 100.0 | 100.0 | 76.0 | ✓/✓ | 68 | 220 | 0 | 0 | pipeline.py + run script |
| 1 | claude-code | runtime | 4.6 | ✅ PASS | 70.0 | 80.2 |  | 0 | 18.2m | 100.0 | 100.0 | 87.0 | ✓/✓ | 93 | 565 | 0 | 0 | 3 sub-project output(s) well-formed |
| 1 | claude-code | suite | 4.6 | ✅ PASS | 70.0 | 89.2 |  | 0 | 18.2m | 100.0 | 100.0 | 88.8 | ✓/✓ | 93 | 565 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 1 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 65.0 | 75.4 |  | 1 | 55.5m | 100.0 | 95.0 | 83.6 | ✓/✓ | 54 | 185 | 0 | 1 | .dxnn + config.json present |
| 1 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 20.0 | 56.3 |  | 1 | 7.0m | 100.0 | 100.0 | 67.3 | ✓/✓ | 33 | 221 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 1 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 | ⏱ | 1 | 3.7m | 100.0 | 100.0 | 73.8 | ✓/✓ | 22 | 190 | 0 | 0 | pipeline.py + run script |
| 1 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 25.0 | 75.4 | ⏱ | 1 | 4.4m | 100.0 | 100.0 | 72.6 | ✓/✓ | 33 | 201 | 0 | 0 | pipeline.py + run script |
| 1 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 65.0 | 66.8 |  | 1 | 13.1m | 100.0 | 90.0 | 80.9 | ✓/✓ | 56 | 497 | 0 | 2 | 3 sub-project output(s) well-formed |
| 1 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 65.0 | 75.8 |  | 1 | 13.1m | 100.0 | 90.0 | 82.7 | ✓/✓ | 56 | 497 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 1 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 0 | 13.7m | 100.0 | 95.0 | 84.7 | ✓/✓ | 49 | 230 | 0 | 1 | .dxnn + config.json present |
| 1 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 0 | 7.9m | 100.0 | 100.0 | 75.8 | ✓/✓ | 65 | 215 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 1 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 20.0 | 74.7 |  | 0 | 7.7m | 100.0 | 100.0 | 70.9 | ✓/✓ | 60 | 158 | 0 | 0 | pipeline.py + run script |
| 1 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 0 | 7.1m | 100.0 | 100.0 | 75.7 | ✓/✓ | 50 | 223 | 0 | 0 | pipeline.py + run script |
| 1 | copilot-cli | runtime | 4.6 | ✅ PASS | 70.0 | 48.9 |  | 0 | 40.0m | 83.3 | 95.0 | 74.8 | ✓/✓ | 170 | 660 | 0 | 1 | 3 sub-project output(s) well-formed |
| 1 | copilot-cli | suite | 4.6 | ✅ PASS | 70.0 | 56.1 |  | 0 | 40.0m | 85.7 | 95.0 | 76.9 | ✓/✓ | 170 | 660 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 1 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 1 | 57.5m | 100.0 | 100.0 | 86.8 | ✓/✓ | 68 | 161 | 0 | 0 | .dxnn + config.json present |
| 1 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 25.0 | 78.0 |  | 1 | 5.0m | 100.0 | 100.0 | 73.1 | ✓/✓ | 46 | 221 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 1 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 1 | 3.9m | 100.0 | 100.0 | 74.0 | ✓/✓ | 33 | 192 | 0 | 0 | pipeline.py + run script |
| 1 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 25.0 | 74.6 |  | 1 | 8.2m | 100.0 | 100.0 | 72.4 | ✓/✓ | 61 | 171 | 0 | 0 | pipeline.py + run script |
| 1 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 40.0 | 61.7 |  | 1 | 25.1m | 100.0 | 100.0 | 74.3 | ✓/✓ | 134 | 337 | 0 | 0 | 1 sub-project output(s) well-formed |
| 1 | cursor-cli | suite | cursor-auto ⚠ | ✅ PASS | 40.0 | 86.5 |  | 1 | 25.1m | 100.0 | 100.0 | 79.3 | ✓/✓ | 134 | 337 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 1 | opencode-cli | compiler | 4.6 | ✅ PASS | 70.0 | 75.6 |  | 0 | 56.2m | 100.0 | 90.0 | 84.1 | ✓/✓ | 31 | 358 | 0 | 2 | .dxnn + config.json present |
| 1 | opencode-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 73.5 |  | 0 | 2.8m | 100.0 | 100.0 | 75.2 | ✓/✓ | 35 | 233 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 1 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 5.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 49 | 151 | 0 | 0 | pipeline.py + run script |
| 1 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 | ⏱ | 0 | 4.5m | 100.0 | 100.0 | 74.2 | ✓/✓ | 40 | 394 | 0 | 0 | pipeline.py + run script |
| 1 | opencode-cli | runtime | 4.6 | ✅ PASS | 65.0 | 59.5 |  | 0 | 13.0m | 83.3 | 85.0 | 73.4 | ✓/✓ | 63 | 1188 | 0 | 3 | 6 sub-project output(s) well-formed |
| 1 | opencode-cli | suite | 4.6 | ✅ PASS | 65.0 | 63.6 |  | 0 | 13.0m | 85.7 | 85.0 | 74.9 | ✓/✓ | 63 | 1188 | 0 | 3 | dual session dirs (compiler+app) with primary deliverables |
| 2 | claude-code | compiler | 4.6 | ✅ PASS | 75.0 | 86.2 |  | 1 | 13.9m | 100.0 | 95.0 | 88.8 | ✓/✓ | 43 | 242 | 0 | 1 | .dxnn + config.json present |
| 2 | claude-code | dx_app | 4.6 | ✅ PASS | 35.0 | 84.9 |  | 1 | 5.5m | 90.0 | 100.0 | 74.5 | ✓/✓ | 58 | 434 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 2 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 7.0m | 100.0 | 100.0 | 76.8 | ✓/✓ | 64 | 151 | 0 | 0 | pipeline.py + run script |
| 2 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 7.3m | 100.0 | 100.0 | 76.0 | ✓/✓ | 75 | 225 | 0 | 0 | pipeline.py + run script |
| 2 | claude-code | runtime | 4.6 | ✅ PASS | 65.0 | 80.2 |  | 1 | 15.8m | 100.0 | 90.0 | 83.5 | ✓/✓ | 105 | 870 | 0 | 2 | 3 sub-project output(s) well-formed |
| 2 | claude-code | suite | 4.6 | ✅ PASS | 65.0 | 89.2 |  | 1 | 15.8m | 100.0 | 90.0 | 85.3 | ✓/✓ | 105 | 870 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 2 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 80.0 | 75.4 |  | 1 | 19.5m | 100.0 | 90.0 | 87.1 | ✓/✓ | 43 | 241 | 0 | 2 | .dxnn + config.json present |
| 2 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 40.0 | 56.3 |  | 1 | 8.6m | 100.0 | 100.0 | 73.3 | ✓/✓ | 46 | 211 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 2 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 25.0 | 66.3 |  | 1 | 5.2m | 100.0 | 100.0 | 70.8 | ✓/✓ | 33 | 157 | 0 | 0 | pipeline.py + run script |
| 2 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 |  | 1 | 2.2m | 100.0 | 100.0 | 75.6 | ✓/✓ | 15 | 222 | 0 | 0 | pipeline.py + run script |
| 2 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 60.0 | 66.8 | ⏱ | 1 | 20.9m | 100.0 | 90.0 | 79.4 | ✓/✓ | 45 | 647 | 0 | 2 | 3 sub-project output(s) well-formed |
| 2 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 60.0 | 75.8 | ⏱ | 1 | 20.9m | 100.0 | 90.0 | 81.2 | ✓/✓ | 45 | 647 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 2 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 0 | 17.9m | 100.0 | 90.0 | 83.7 | ✓/✓ | 29 | 252 | 0 | 2 | .dxnn + config.json present |
| 2 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 0 | 6.0m | 100.0 | 100.0 | 75.8 | ✓/✓ | 53 | 213 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 2 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 20.0 | 74.7 |  | 0 | 8.0m | 100.0 | 100.0 | 70.9 | ✓/✓ | 62 | 195 | 0 | 0 | pipeline.py + run script |
| 2 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 0 | 8.6m | 100.0 | 100.0 | 75.7 | ✓/✓ | 60 | 215 | 0 | 0 | pipeline.py + run script |
| 2 | copilot-cli | runtime | 4.6 | ✅ PASS | 60.0 | 48.9 |  | 0 | 23.1m | 83.3 | 95.0 | 71.8 | ✓/✓ | 101 | 777 | 0 | 1 | 3 sub-project output(s) well-formed |
| 2 | copilot-cli | suite | 4.6 | ✅ PASS | 60.0 | 56.1 |  | 0 | 23.1m | 85.7 | 95.0 | 73.9 | ✓/✓ | 101 | 777 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 2 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 1 | 17.3m | 100.0 | 100.0 | 86.8 | ✓/✓ | 58 | 200 | 0 | 0 | .dxnn + config.json present |
| 2 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 45.0 | 78.0 |  | 1 | 5.5m | 100.0 | 100.0 | 79.1 | ✓/✓ | 59 | 281 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 2 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 1 | 4.7m | 100.0 | 100.0 | 74.0 | ✓/✓ | 53 | 197 | 0 | 0 | pipeline.py + run script |
| 2 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 1 | 5.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 41 | 228 | 0 | 0 | pipeline.py + run script |
| 2 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 60.0 | 61.7 |  | 1 | 14.3m | 100.0 | 100.0 | 80.3 | ✓/✓ | 92 | 507 | 0 | 0 | 1 sub-project output(s) well-formed |
| 2 | cursor-cli | suite | cursor-auto ⚠ | ✅ PASS | 60.0 | 86.5 |  | 1 | 14.3m | 100.0 | 100.0 | 85.3 | ✓/✓ | 92 | 507 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 2 | opencode-cli | compiler | 4.6 | ✅ PASS | 80.0 | 75.6 |  | 0 | 16.5m | 100.0 | 85.0 | 86.1 | ✓/✓ | 48 | 473 | 0 | 3 | .dxnn + config.json present |
| 2 | opencode-cli | dx_app | 4.6 | ✅ PASS | 25.0 | 73.5 |  | 0 | 4.0m | 100.0 | 100.0 | 72.2 | ✓/✓ | 42 | 254 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 2 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.4m | 100.0 | 100.0 | 75.4 | ✓/✓ | 31 | 153 | 0 | 0 | pipeline.py + run script |
| 2 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 3.4m | 100.0 | 100.0 | 74.2 | ✓/✓ | 29 | 349 | 0 | 0 | pipeline.py + run script |
| 2 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 | ⏱ | 0 | 13.5m | 83.3 | 85.0 | 71.9 | ✓/✓ | 3 | 1751 | 0 | 3 | 7 sub-project output(s) well-formed |
| 2 | opencode-cli | suite | 4.6 | ✅ PASS | 60.0 | 63.6 | ⏱ | 0 | 13.5m | 85.7 | 85.0 | 73.4 | ✓/✓ | 3 | 1751 | 0 | 3 | dual session dirs (compiler+app) with primary deliverables |
| 3 | claude-code | compiler | 4.6 | ✅ PASS | 90.0 | 86.2 |  | 1 | 14.9m | 100.0 | 100.0 | 94.2 | ✓/✓ | 70 | 245 | 0 | 0 | .dxnn + config.json present |
| 3 | claude-code | dx_app | 4.6 | ✅ PASS | 35.0 | 84.9 |  | 1 | 6.2m | 100.0 | 100.0 | 77.5 | ✓/✓ | 70 | 237 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 3 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 6.5m | 100.0 | 100.0 | 76.8 | ✓/✓ | 65 | 153 | 0 | 0 | pipeline.py + run script |
| 3 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 7.8m | 100.0 | 100.0 | 76.0 | ✓/✓ | 77 | 127 | 0 | 0 | pipeline.py + run script |
| 3 | claude-code | runtime | 4.6 | ✅ PASS | 55.0 | 80.2 |  | 1 | 17.9m | 100.0 | 90.0 | 80.5 | ✓/✓ | 87 | 701 | 0 | 2 | 3 sub-project output(s) well-formed |
| 3 | claude-code | suite | 4.6 | ✅ PASS | 55.0 | 89.2 |  | 1 | 17.9m | 100.0 | 90.0 | 82.3 | ✓/✓ | 87 | 701 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 3 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 75.0 | 75.4 |  | 1 | 18.9m | 100.0 | 95.0 | 86.6 | ✓/✓ | 46 | 206 | 0 | 1 | .dxnn + config.json present |
| 3 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 5.2m | 100.0 | 100.0 | 68.8 | ✓/✓ | 35 | 211 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 3 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 25.0 | 66.3 |  | 1 | 5.9m | 100.0 | 100.0 | 70.8 | ✓/✓ | 29 | 186 | 0 | 0 | pipeline.py + run script |
| 3 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 25.0 | 75.4 | ⏱ | 1 | 8.3m | 100.0 | 100.0 | 72.6 | ✓/✓ | 40 | 221 | 0 | 0 | pipeline.py + run script |
| 3 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 65.0 | 66.8 | ⏱ | 1 | 7.5m | 100.0 | 95.0 | 81.9 | ✓/✓ | 35 | 391 | 0 | 1 | 3 sub-project output(s) well-formed |
| 3 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 65.0 | 75.8 | ⏱ | 1 | 7.5m | 100.0 | 95.0 | 83.7 | ✓/✓ | 35 | 391 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 3 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 1 | 18.1m | 100.0 | 95.0 | 84.7 | ✓/✓ | 40 | 139 | 0 | 1 | .dxnn + config.json present |
| 3 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 1 | 4.1m | 100.0 | 100.0 | 75.8 | ✓/✓ | 47 | 213 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 3 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 5.6m | 100.0 | 100.0 | 75.4 | ✓/✓ | 52 | 195 | 0 | 0 | pipeline.py + run script |
| 3 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 9.8m | 100.0 | 100.0 | 75.7 | ✓/✓ | 64 | 205 | 0 | 0 | pipeline.py + run script |
| 3 | copilot-cli | runtime | 4.6 | ✅ PASS | 60.0 | 48.9 |  | 1 | 16.1m | 83.3 | 95.0 | 71.8 | ✓/✓ | 78 | 709 | 0 | 1 | 3 sub-project output(s) well-formed |
| 3 | copilot-cli | suite | 4.6 | ✅ PASS | 60.0 | 56.1 |  | 1 | 16.1m | 85.7 | 95.0 | 73.9 | ✓/✓ | 78 | 709 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 3 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 85.0 | 71.6 |  | 1 | 12.9m | 100.0 | 95.0 | 88.8 | ✓/✓ | 42 | 311 | 0 | 1 | .dxnn + config.json present |
| 3 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 45.0 | 78.0 |  | 1 | 5.0m | 100.0 | 100.0 | 79.1 | ✓/✓ | 52 | 281 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 3 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 | ⏱ | 1 | 3.4m | 100.0 | 100.0 | 74.0 | ✓/✓ | 33 | 185 | 0 | 0 | pipeline.py + run script |
| 3 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 | ⏱ | 1 | 3.2m | 100.0 | 100.0 | 75.4 | ✓/✓ | 33 | 236 | 0 | 0 | pipeline.py + run script |
| 3 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 50.0 | 61.7 |  | 1 | 23.0m | 100.0 | 95.0 | 76.3 | ✓/✓ | 80 | 347 | 0 | 1 | 1 sub-project output(s) well-formed |
| 3 | cursor-cli | suite | cursor-auto ⚠ | ✅ PASS | 50.0 | 86.5 |  | 1 | 23.0m | 100.0 | 95.0 | 81.3 | ✓/✓ | 80 | 347 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 3 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 0 | 16.5m | 100.0 | 85.0 | 84.6 | ✓/✓ | 40 | 574 | 0 | 3 | .dxnn + config.json present |
| 3 | opencode-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 73.5 |  | 0 | 4.3m | 100.0 | 100.0 | 76.7 | ✓/✓ | 43 | 241 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 3 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 4.2m | 100.0 | 100.0 | 75.4 | ✓/✓ | 36 | 155 | 0 | 0 | pipeline.py + run script |
| 3 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 4.6m | 100.0 | 100.0 | 74.2 | ✓/✓ | 38 | 205 | 0 | 0 | pipeline.py + run script |
| 3 | opencode-cli | runtime | 4.6 | ✅ PASS | 65.0 | 59.5 | ⏱ | 0 | 14.5m | 100.0 | 95.0 | 80.4 | ✓/✓ | 3 | 1140 | 0 | 1 | 6 sub-project output(s) well-formed |
| 3 | opencode-cli | suite | 4.6 | ✅ PASS | 65.0 | 63.6 | ⏱ | 0 | 14.5m | 100.0 | 95.0 | 81.2 | ✓/✓ | 3 | 1140 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 4 | claude-code | compiler | 4.6 | ✅ PASS | 85.0 | 86.2 |  | 1 | 8.6m | 100.0 | 95.0 | 91.8 | ✓/✓ | 55 | 199 | 0 | 1 | .dxnn + config.json present |
| 4 | claude-code | dx_app | 4.6 | ✅ PASS | 25.0 | 84.9 |  | 1 | 6.7m | 100.0 | 100.0 | 74.5 | ✓/✓ | 75 | 239 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 4 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 7.9m | 100.0 | 100.0 | 76.8 | ✓/✓ | 71 | 168 | 0 | 0 | pipeline.py + run script |
| 4 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 8.3m | 100.0 | 100.0 | 76.0 | ✓/✓ | 72 | 208 | 0 | 0 | pipeline.py + run script |
| 4 | claude-code | runtime | 4.6 | ✅ PASS | 40.0 | 80.2 |  | 1 | 1.9m | 100.0 | 100.0 | 78.0 | ✓/✓ | 98 | 225 | 0 | 0 | 2 sub-project output(s) well-formed |
| 4 | claude-code | suite | 4.6 | 🟡 PART | 40.0 | 89.2 |  | 1 | 1.9m | 85.7 | 100.0 | 75.6 | ✓/✓ | 98 | 225 | 0 | 0 | only one of (compiler, app) primary deliverables |
| 4 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 65.0 | 75.4 |  | 1 | 17.2m | 100.0 | 95.0 | 83.6 | ✓/✓ | 45 | 243 | 0 | 1 | .dxnn + config.json present |
| 4 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 9.5m | 100.0 | 100.0 | 68.8 | ✓/✓ | 49 | 219 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 4 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 20.0 | 66.3 |  | 1 | 6.0m | 100.0 | 100.0 | 69.3 | ✓/✓ | 40 | 153 | 0 | 0 | pipeline.py + run script |
| 4 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 20.0 | 75.4 | ⏱ | 1 | 6.8m | 100.0 | 100.0 | 71.1 | ✓/✓ | 34 | 221 | 0 | 0 | pipeline.py + run script |
| 4 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 40.0 | 66.8 | ⏱ | 1 | 3.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 58 | 205 | 0 | 0 | 2 sub-project output(s) well-formed |
| 4 | codex-cli | suite | gpt-5.3-codex | 🟡 PART | 40.0 | 75.8 | ⏱ | 1 | 3.1m | 85.7 | 100.0 | 72.9 | ✓/✓ | 58 | 205 | 0 | 0 | only one of (compiler, app) primary deliverables |
| 4 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 0 | 13.2m | 100.0 | 100.0 | 85.7 | ✓/✓ | 41 | 95 | 0 | 0 | .dxnn + config.json present |
| 4 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 0 | 5.3m | 100.0 | 100.0 | 75.8 | ✓/✓ | 51 | 213 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 4 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 5.6m | 100.0 | 100.0 | 75.4 | ✓/✓ | 54 | 152 | 0 | 0 | pipeline.py + run script |
| 4 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 0 | 9.5m | 100.0 | 100.0 | 75.7 | ✓/✓ | 56 | 224 | 0 | 0 | pipeline.py + run script |
| 4 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 0 | 18.9m | 83.3 | 100.0 | 71.3 | ✓/✓ | 77 | 540 | 0 | 0 | 3 sub-project output(s) well-formed |
| 4 | copilot-cli | suite | 4.6 | ✅ PASS | 55.0 | 56.1 |  | 0 | 18.9m | 85.7 | 100.0 | 73.4 | ✓/✓ | 77 | 540 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 4 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 80.0 | 71.6 |  | 1 | 25.4m | 100.0 | 100.0 | 88.3 | ✓/✓ | 76 | 176 | 0 | 0 | .dxnn + config.json present |
| 4 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 35.0 | 78.0 |  | 1 | 4.8m | 100.0 | 100.0 | 76.1 | ✓/✓ | 64 | 268 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 4 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 15.0 | 67.4 |  | 1 | 4.1m | 57.1 | 100.0 | 55.1 | ✓/✗ | 28 | 153 | 0 | 0 | pipeline.py + run script |
| 4 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ❓ UNKN | 0.0 | 74.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 4 | cursor-cli | runtime | cursor-auto ⚠ | ❓ UNKN | 0.0 | 61.7 |  | 1 | 0.0s | 0.0 | 100.0 | 32.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 4 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 0.0 | 100.0 | 37.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 4 | opencode-cli | compiler | 4.6 | ✅ PASS | 85.0 | 75.6 |  | 0 | 22.2m | 100.0 | 85.0 | 87.6 | ✓/✓ | 42 | 570 | 0 | 3 | .dxnn + config.json present |
| 4 | opencode-cli | dx_app | 4.6 | ✅ PASS | 20.0 | 73.5 |  | 0 | 3.9m | 100.0 | 100.0 | 70.7 | ✓/✓ | 36 | 258 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 4 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 4.0m | 100.0 | 100.0 | 75.4 | ✓/✓ | 38 | 153 | 0 | 0 | pipeline.py + run script |
| 4 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 4.3m | 100.0 | 100.0 | 74.2 | ✓/✓ | 32 | 368 | 0 | 0 | pipeline.py + run script |
| 4 | opencode-cli | runtime | 4.6 | ✅ PASS | 45.0 | 59.5 | ⏱ | 0 | 14.5m | 66.7 | 95.0 | 64.4 | ✓/✗ | 73 | 1083 | 0 | 1 | 6 sub-project output(s) well-formed |
| 4 | opencode-cli | suite | 4.6 | ✅ PASS | 45.0 | 63.6 | ⏱ | 0 | 14.5m | 71.4 | 95.0 | 66.7 | ✓/✗ | 73 | 1083 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 5 | claude-code | compiler | 4.6 | ✅ PASS | 85.0 | 86.2 |  | 0 | 2.1m | 100.0 | 95.0 | 91.8 | ✓/✓ | 61 | 243 | 0 | 1 | .dxnn + config.json present |
| 5 | claude-code | dx_app | 4.6 | ✅ PASS | 45.0 | 84.9 |  | 0 | 5.6m | 100.0 | 100.0 | 80.5 | ✓/✓ | 57 | 252 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 5 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 0 | 6.9m | 100.0 | 100.0 | 76.8 | ✓/✓ | 73 | 151 | 0 | 0 | pipeline.py + run script |
| 5 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 0 | 6.8m | 100.0 | 100.0 | 76.0 | ✓/✓ | 63 | 208 | 0 | 0 | pipeline.py + run script |
| 5 | claude-code | runtime | 4.6 | ✅ PASS | 45.0 | 80.2 |  | 0 | 15.0m | 100.0 | 95.0 | 78.5 | ✓/✓ | 96 | 548 | 0 | 1 | 3 sub-project output(s) well-formed |
| 5 | claude-code | suite | 4.6 | ✅ PASS | 45.0 | 89.2 |  | 0 | 15.0m | 100.0 | 95.0 | 80.3 | ✓/✓ | 96 | 548 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 5 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 75.0 | 75.4 |  | 1 | 15.3m | 100.0 | 95.0 | 86.6 | ✓/✓ | 27 | 143 | 0 | 1 | .dxnn + config.json present |
| 5 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 5.4m | 100.0 | 100.0 | 68.8 | ✓/✓ | 39 | 211 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 5 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 | ⏱ | 1 | 5.9m | 100.0 | 100.0 | 73.8 | ✓/✓ | 42 | 192 | 0 | 0 | pipeline.py + run script |
| 5 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 25.0 | 75.4 |  | 1 | 4.3m | 100.0 | 100.0 | 72.6 | ✓/✓ | 35 | 221 | 0 | 0 | pipeline.py + run script |
| 5 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 50.0 | 66.8 | ⏱ | 1 | 37.1m | 100.0 | 90.0 | 76.4 | ✓/✓ | 53 | 682 | 0 | 2 | 3 sub-project output(s) well-formed |
| 5 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 50.0 | 75.8 | ⏱ | 1 | 37.1m | 100.0 | 90.0 | 78.2 | ✓/✓ | 53 | 682 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 5 | copilot-cli | compiler | 4.6 | ✅ PASS | 80.0 | 65.8 |  | 1 | 53.9m | 85.7 | 95.0 | 81.9 | ✓/✗ | 48 | 180 | 0 | 1 | .dxnn + config.json present |
| 5 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 1 | 6.1m | 100.0 | 100.0 | 75.8 | ✓/✓ | 57 | 219 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 5 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 5.5m | 100.0 | 100.0 | 75.4 | ✓/✓ | 57 | 155 | 0 | 0 | pipeline.py + run script |
| 5 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 6.6m | 100.0 | 100.0 | 75.7 | ✓/✓ | 47 | 194 | 0 | 0 | pipeline.py + run script |
| 5 | copilot-cli | runtime | 4.6 | ✅ PASS | 65.0 | 48.9 |  | 1 | 47.7m | 83.3 | 95.0 | 73.3 | ✓/✓ | 123 | 596 | 0 | 1 | 2 sub-project output(s) well-formed |
| 5 | copilot-cli | suite | 4.6 | ✅ PASS | 65.0 | 56.1 |  | 1 | 47.7m | 85.7 | 95.0 | 75.4 | ✓/✓ | 123 | 596 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 5 | cursor-cli | compiler | cursor-auto ⚠ | ❓ UNKN | 0.0 | 71.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 5 | cursor-cli | dx_app | cursor-auto ⚠ | ❓ UNKN | 0.0 | 78.0 |  | 1 | 0.0s | 0.0 | 100.0 | 35.6 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 5 | cursor-cli | dx_stream | cursor-auto ⚠ | ❓ UNKN | 0.0 | 67.4 |  | 1 | 0.0s | 0.0 | 100.0 | 33.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 5 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ❓ UNKN | 0.0 | 74.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 5 | cursor-cli | runtime | cursor-auto ⚠ | ❓ UNKN | 0.0 | 61.7 |  | 1 | 0.0s | 0.0 | 100.0 | 32.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 5 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 0.0 | 100.0 | 37.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 5 | opencode-cli | compiler | 4.6 | ❓ UNKN | 0.0 | 75.6 |  | 1 | 0.0s | 0.0 | 100.0 | 35.1 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 5 | opencode-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 73.5 |  | 1 | 4.0m | 100.0 | 100.0 | 76.7 | ✓/✓ | 45 | 227 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 5 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 3.3m | 100.0 | 100.0 | 75.4 | ✓/✓ | 30 | 153 | 0 | 0 | pipeline.py + run script |
| 5 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 1 | 4.1m | 100.0 | 100.0 | 74.2 | ✓/✓ | 35 | 220 | 0 | 0 | pipeline.py + run script |
| 5 | opencode-cli | runtime | 4.6 | ✅ PASS | 55.0 | 59.5 | ⏱ | 1 | 10.2m | 83.3 | 90.0 | 71.4 | ✓/✓ | 8 | 1093 | 0 | 2 | 5 sub-project output(s) well-formed |
| 5 | opencode-cli | suite | 4.6 | ✅ PASS | 55.0 | 63.6 | ⏱ | 1 | 10.2m | 85.7 | 90.0 | 72.9 | ✓/✓ | 8 | 1093 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 6 | claude-code | compiler | 4.6 | ✅ PASS | 60.0 | 86.2 |  | 1 | 13.4m | 100.0 | 95.0 | 84.2 | ✓/✓ | 57 | 298 | 0 | 1 | .dxnn + config.json present |
| 6 | claude-code | dx_app | 4.6 | ✅ PASS | 45.0 | 84.9 |  | 1 | 7.1m | 100.0 | 100.0 | 80.5 | ✓/✓ | 71 | 241 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 6 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 | ⏱ | 1 | 4.9m | 100.0 | 100.0 | 76.8 | ✓/✓ | 53 | 160 | 0 | 0 | pipeline.py + run script |
| 6 | claude-code | dx_stream_cascaded | 4.6 | ❌ FAIL | 15.0 | 77.3 |  | 1 | 4.3m | 50.0 | 100.0 | 55.0 | ✓/✗ | 32 | 0 | 0 | 0 | no pipeline.py |
| 6 | claude-code | runtime | 4.6 | ✅ PASS | 45.0 | 80.2 |  | 1 | 5.4m | 83.3 | 95.0 | 73.5 | ✓/✗ | 54 | 535 | 0 | 1 | 3 sub-project output(s) well-formed |
| 6 | claude-code | suite | 4.6 | ✅ PASS | 45.0 | 89.2 |  | 1 | 5.4m | 85.7 | 95.0 | 76.1 | ✓/✗ | 54 | 535 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 6 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 80.0 | 75.4 |  | 1 | 24.3m | 100.0 | 95.0 | 88.1 | ✓/✓ | 40 | 237 | 0 | 1 | .dxnn + config.json present |
| 6 | codex-cli | dx_app | gpt-5.3-codex | ❌ FAIL | 25.0 | 56.3 |  | 1 | 4.7m | 40.0 | 100.0 | 50.8 | ✓/✓ | 31 | 235 | 0 | 0 | no factory.py found |
| 6 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 40.0 | 66.3 |  | 1 | 5.0m | 100.0 | 100.0 | 75.3 | ✓/✓ | 38 | 171 | 0 | 0 | pipeline.py + run script |
| 6 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 | ⏱ | 1 | 4.5m | 100.0 | 100.0 | 75.6 | ✓/✓ | 43 | 221 | 0 | 0 | pipeline.py + run script |
| 6 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 60.0 | 66.8 | ⏱ | 1 | 8.5m | 100.0 | 95.0 | 80.4 | ✓/✓ | 57 | 467 | 0 | 1 | 3 sub-project output(s) well-formed |
| 6 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 60.0 | 75.8 | ⏱ | 1 | 8.5m | 100.0 | 95.0 | 82.2 | ✓/✓ | 57 | 467 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 6 | copilot-cli | compiler | 4.6 | ✅ PASS | 80.0 | 65.8 |  | 1 | 35.1m | 100.0 | 100.0 | 87.2 | ✓/✓ | 53 | 158 | 0 | 0 | .dxnn + config.json present |
| 6 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 1 | 5.3m | 100.0 | 100.0 | 77.3 | ✓/✓ | 53 | 238 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 6 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 40.0 | 74.7 |  | 1 | 5.6m | 100.0 | 100.0 | 76.9 | ✓/✓ | 44 | 315 | 0 | 0 | pipeline.py + run script |
| 6 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 6.7m | 100.0 | 100.0 | 75.7 | ✓/✓ | 42 | 185 | 0 | 0 | pipeline.py + run script |
| 6 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 17.0m | 83.3 | 95.0 | 70.3 | ✓/✓ | 90 | 589 | 0 | 1 | 3 sub-project output(s) well-formed |
| 6 | copilot-cli | suite | 4.6 | ✅ PASS | 55.0 | 56.1 |  | 1 | 17.0m | 85.7 | 95.0 | 72.4 | ✓/✓ | 90 | 589 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 6 | cursor-cli | compiler | cursor-auto ⚠ | ❓ UNKN | 0.0 | 71.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 6 | cursor-cli | dx_app | cursor-auto ⚠ | ❓ UNKN | 0.0 | 78.0 |  | 1 | 0.0s | 0.0 | 100.0 | 35.6 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 6 | cursor-cli | dx_stream | cursor-auto ⚠ | ❓ UNKN | 0.0 | 67.4 |  | 1 | 0.0s | 0.0 | 100.0 | 33.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 6 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ❓ UNKN | 0.0 | 74.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 6 | cursor-cli | runtime | cursor-auto ⚠ | ❓ UNKN | 0.0 | 61.7 |  | 1 | 0.0s | 0.0 | 100.0 | 32.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 6 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 0.0 | 100.0 | 37.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 6 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 1 | 12.4m | 100.0 | 90.0 | 85.6 | ✓/✓ | 39 | 246 | 0 | 2 | .dxnn + config.json present |
| 6 | opencode-cli | dx_app | 4.6 | ✅ PASS | 45.0 | 73.5 | ⏱ | 1 | 3.8m | 100.0 | 95.0 | 77.2 | ✓/✓ | 39 | 413 | 0 | 1 | factory + sync runner (yolo26n_sync.py) |
| 6 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 3.2m | 100.0 | 100.0 | 75.4 | ✓/✓ | 30 | 155 | 0 | 0 | pipeline.py + run script |
| 6 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 1 | 5.3m | 100.0 | 100.0 | 74.2 | ✓/✓ | 40 | 216 | 0 | 0 | pipeline.py + run script |
| 6 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 |  | 1 | 42.8m | 83.3 | 85.0 | 71.9 | ✓/✓ | 98 | 1000 | 0 | 3 | 3 sub-project output(s) well-formed |
| 6 | opencode-cli | suite | 4.6 | ✅ PASS | 60.0 | 63.6 |  | 1 | 42.8m | 85.7 | 85.0 | 73.4 | ✓/✓ | 98 | 1000 | 0 | 3 | dual session dirs (compiler+app) with primary deliverables |
| 7 | claude-code | compiler | 4.6 | ✅ PASS | 85.0 | 86.2 |  | 1 | 14.6m | 100.0 | 95.0 | 91.8 | ✓/✓ | 72 | 252 | 0 | 1 | .dxnn + config.json present |
| 7 | claude-code | dx_app | 4.6 | ✅ PASS | 35.0 | 84.9 |  | 1 | 7.2m | 100.0 | 100.0 | 77.5 | ✓/✓ | 77 | 216 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 7 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 6.8m | 100.0 | 100.0 | 76.8 | ✓/✓ | 66 | 151 | 0 | 0 | pipeline.py + run script |
| 7 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 6.0m | 100.0 | 100.0 | 76.0 | ✓/✓ | 61 | 216 | 0 | 0 | pipeline.py + run script |
| 7 | claude-code | runtime | 4.6 | ✅ PASS | 40.0 | 80.2 |  | 1 | 17.2m | 100.0 | 100.0 | 78.0 | ✓/✓ | 99 | 223 | 0 | 0 | 2 sub-project output(s) well-formed |
| 7 | claude-code | suite | 4.6 | 🟡 PART | 40.0 | 89.2 |  | 1 | 17.2m | 85.7 | 100.0 | 75.6 | ✓/✓ | 99 | 223 | 0 | 0 | only one of (compiler, app) primary deliverables |
| 7 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 60.0 | 75.4 |  | 1 | 14.0m | 100.0 | 95.0 | 82.1 | ✓/✓ | 26 | 85 | 0 | 1 | .dxnn + config.json present |
| 7 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 8.2m | 100.0 | 100.0 | 68.8 | ✓/✓ | 40 | 219 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 7 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 20.0 | 66.3 |  | 1 | 6.4m | 100.0 | 100.0 | 69.3 | ✓/✓ | 32 | 181 | 0 | 0 | pipeline.py + run script |
| 7 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 20.0 | 75.4 |  | 1 | 5.7m | 100.0 | 100.0 | 71.1 | ✓/✓ | 22 | 221 | 0 | 0 | pipeline.py + run script |
| 7 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 70.0 | 66.8 |  | 1 | 8.0m | 83.3 | 95.0 | 78.4 | ✓/✓ | 61 | 678 | 0 | 1 | 3 sub-project output(s) well-formed |
| 7 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 70.0 | 75.8 |  | 1 | 8.0m | 85.7 | 95.0 | 80.9 | ✓/✓ | 61 | 678 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 7 | copilot-cli | compiler | 4.6 | ❌ FAIL | 25.0 | 65.8 |  | 1 | 47.2m | 57.1 | 100.0 | 57.8 | ✓/✗ | 33 | 0 | 0 | 0 | config.json present but no .dxnn produced |
| 7 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 1 | 8.5m | 100.0 | 100.0 | 75.8 | ✓/✓ | 78 | 265 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 7 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 6.2m | 100.0 | 100.0 | 75.4 | ✓/✓ | 53 | 151 | 0 | 0 | pipeline.py + run script |
| 7 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 5.5m | 100.0 | 100.0 | 75.7 | ✓/✓ | 54 | 216 | 0 | 0 | pipeline.py + run script |
| 7 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 12.8m | 83.3 | 95.0 | 70.3 | ✓/✓ | 86 | 645 | 0 | 1 | 3 sub-project output(s) well-formed |
| 7 | copilot-cli | suite | 4.6 | ✅ PASS | 55.0 | 56.1 |  | 1 | 12.8m | 85.7 | 95.0 | 72.4 | ✓/✓ | 86 | 645 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 7 | cursor-cli | compiler | cursor-auto ⚠ | ❓ UNKN | 0.0 | 71.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 7 | cursor-cli | dx_app | cursor-auto ⚠ | ❓ UNKN | 0.0 | 78.0 |  | 1 | 0.0s | 0.0 | 100.0 | 35.6 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 7 | cursor-cli | dx_stream | cursor-auto ⚠ | ❓ UNKN | 0.0 | 67.4 |  | 1 | 0.0s | 0.0 | 100.0 | 33.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 7 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ❓ UNKN | 0.0 | 74.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 7 | cursor-cli | runtime | cursor-auto ⚠ | ❓ UNKN | 0.0 | 61.7 |  | 1 | 0.0s | 0.0 | 100.0 | 32.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 7 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 0.0 | 100.0 | 37.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 7 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 0 | 21.4m | 100.0 | 90.0 | 85.6 | ✓/✓ | 38 | 284 | 0 | 2 | .dxnn + config.json present |
| 7 | opencode-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 73.5 |  | 0 | 3.4m | 100.0 | 100.0 | 76.7 | ✓/✓ | 44 | 305 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 7 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.9m | 100.0 | 100.0 | 75.4 | ✓/✓ | 38 | 155 | 0 | 0 | pipeline.py + run script |
| 7 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 4.4m | 100.0 | 100.0 | 74.2 | ✓/✓ | 42 | 216 | 0 | 0 | pipeline.py + run script |
| 7 | opencode-cli | runtime | 4.6 | ✅ PASS | 40.0 | 59.5 |  | 0 | 15.7m | 83.3 | 95.0 | 67.9 | ✓/✓ | 3 | 1392 | 0 | 1 | 7 sub-project output(s) well-formed |
| 7 | opencode-cli | suite | 4.6 | ✅ PASS | 40.0 | 63.6 |  | 0 | 15.7m | 85.7 | 95.0 | 69.4 | ✓/✓ | 3 | 1392 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 8 | claude-code | compiler | 4.6 | ❓ UNKN | 0.0 | 86.2 |  | 1 | 5.1m | 40.0 | 100.0 | 49.2 | ✓/✓ | 81 | 0 | 0 | 0 | no output directory linked |
| 8 | claude-code | dx_app | 4.6 | ✅ PASS | 45.0 | 84.9 |  | 1 | 6.9m | 100.0 | 100.0 | 80.5 | ✓/✓ | 74 | 216 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 8 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 7.2m | 100.0 | 100.0 | 76.8 | ✓/✓ | 57 | 151 | 0 | 0 | pipeline.py + run script |
| 8 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 10.0m | 100.0 | 100.0 | 76.0 | ✓/✓ | 88 | 195 | 0 | 0 | pipeline.py + run script |
| 8 | claude-code | runtime | 4.6 | ✅ PASS | 60.0 | 80.2 |  | 1 | 16.7m | 100.0 | 90.0 | 82.0 | ✓/✓ | 75 | 598 | 0 | 2 | 3 sub-project output(s) well-formed |
| 8 | claude-code | suite | 4.6 | ✅ PASS | 60.0 | 89.2 |  | 1 | 16.7m | 100.0 | 90.0 | 83.8 | ✓/✓ | 75 | 598 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 8 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 60.0 | 75.4 |  | 1 | 14.5m | 100.0 | 95.0 | 82.1 | ✓/✓ | 34 | 99 | 0 | 1 | .dxnn + config.json present |
| 8 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 9.9m | 100.0 | 100.0 | 68.8 | ✓/✓ | 33 | 221 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 8 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 20.0 | 66.3 | ⏱ | 1 | 8.2m | 100.0 | 100.0 | 69.3 | ✓/✓ | 44 | 192 | 0 | 0 | pipeline.py + run script |
| 8 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 |  | 1 | 7.7m | 100.0 | 100.0 | 75.6 | ✓/✓ | 36 | 221 | 0 | 0 | pipeline.py + run script |
| 8 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 60.0 | 66.8 |  | 1 | 16.8m | 100.0 | 100.0 | 81.4 | ✓/✓ | 45 | 671 | 0 | 0 | 3 sub-project output(s) well-formed |
| 8 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 60.0 | 75.8 |  | 1 | 16.8m | 100.0 | 100.0 | 83.2 | ✓/✓ | 45 | 671 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 8 | copilot-cli | compiler | 4.6 | ❌ FAIL | 75.0 | 65.8 |  | 1 | 13.0m | 85.7 | 95.0 | 80.4 | ✓/✓ | 41 | 230 | 0 | 1 | compiler artifacts missing |
| 8 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 1 | 6.8m | 100.0 | 100.0 | 77.3 | ✓/✓ | 59 | 234 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 8 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 4.7m | 100.0 | 100.0 | 75.4 | ✓/✓ | 49 | 151 | 0 | 0 | pipeline.py + run script |
| 8 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 5.0m | 100.0 | 100.0 | 75.7 | ✓/✓ | 39 | 216 | 0 | 0 | pipeline.py + run script |
| 8 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 17.3m | 83.3 | 95.0 | 70.3 | ✓/✓ | 104 | 603 | 0 | 1 | 3 sub-project output(s) well-formed |
| 8 | copilot-cli | suite | 4.6 | ✅ PASS | 55.0 | 56.1 |  | 1 | 17.3m | 85.7 | 95.0 | 72.4 | ✓/✓ | 104 | 603 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 8 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 80.0 | 71.6 |  | 0 | 17.6m | 100.0 | 100.0 | 88.3 | ✓/✓ | 64 | 250 | 0 | 0 | .dxnn + config.json present |
| 8 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 25.0 | 78.0 |  | 0 | 5.2m | 100.0 | 100.0 | 73.1 | ✓/✓ | 69 | 239 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 8 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 0 | 2.7m | 100.0 | 100.0 | 74.0 | ✓/✓ | 35 | 191 | 0 | 0 | pipeline.py + run script |
| 8 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 0 | 2.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 29 | 221 | 0 | 0 | pipeline.py + run script |
| 8 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 55.0 | 61.7 |  | 0 | 39.0m | 100.0 | 100.0 | 78.8 | ✓/✓ | 99 | 393 | 0 | 0 | 1 sub-project output(s) well-formed |
| 8 | cursor-cli | suite | cursor-auto ⚠ | ✅ PASS | 55.0 | 86.5 |  | 0 | 39.0m | 100.0 | 100.0 | 83.8 | ✓/✓ | 99 | 393 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 8 | opencode-cli | compiler | 4.6 | ✅ PASS | 90.0 | 75.6 |  | 0 | 11.9m | 100.0 | 90.0 | 90.1 | ✓/✓ | 29 | 368 | 0 | 2 | .dxnn + config.json present |
| 8 | opencode-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 73.5 |  | 0 | 4.6m | 100.0 | 100.0 | 76.7 | ✓/✓ | 48 | 251 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 8 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.5m | 100.0 | 100.0 | 75.4 | ✓/✓ | 35 | 154 | 0 | 0 | pipeline.py + run script |
| 8 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 3.9m | 100.0 | 100.0 | 74.2 | ✓/✓ | 35 | 213 | 0 | 0 | pipeline.py + run script |
| 8 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 | ⏱ | 0 | 18.6m | 100.0 | 95.0 | 78.9 | ✓/✓ | 3 | 1666 | 0 | 1 | 8 sub-project output(s) well-formed |
| 8 | opencode-cli | suite | 4.6 | ✅ PASS | 60.0 | 63.6 | ⏱ | 0 | 18.6m | 100.0 | 95.0 | 79.7 | ✓/✓ | 3 | 1666 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 9 | claude-code | compiler | 4.6 | ✅ PASS | 70.0 | 86.2 |  | 0 | 15.0m | 100.0 | 100.0 | 88.2 | ✓/✓ | 53 | 170 | 0 | 0 | .dxnn + config.json present |
| 9 | claude-code | dx_app | 4.6 | ✅ PASS | 35.0 | 84.9 |  | 0 | 7.8m | 100.0 | 100.0 | 77.5 | ✓/✓ | 85 | 224 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 9 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 0 | 7.0m | 100.0 | 100.0 | 76.8 | ✓/✓ | 79 | 154 | 0 | 0 | pipeline.py + run script |
| 9 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 0 | 6.4m | 100.0 | 100.0 | 76.0 | ✓/✓ | 53 | 191 | 0 | 0 | pipeline.py + run script |
| 9 | claude-code | runtime | 4.6 | ✅ PASS | 60.0 | 80.2 |  | 0 | 15.8m | 100.0 | 100.0 | 84.0 | ✓/✓ | 100 | 898 | 0 | 0 | 3 sub-project output(s) well-formed |
| 9 | claude-code | suite | 4.6 | ✅ PASS | 60.0 | 89.2 |  | 0 | 15.8m | 100.0 | 100.0 | 85.8 | ✓/✓ | 100 | 898 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 9 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 75.0 | 75.4 |  | 1 | 14.9m | 100.0 | 100.0 | 87.6 | ✓/✓ | 43 | 248 | 0 | 0 | .dxnn + config.json present |
| 9 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 5.2m | 100.0 | 100.0 | 70.3 | ✓/✓ | 34 | 244 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 9 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 20.0 | 66.3 |  | 1 | 5.8m | 100.0 | 100.0 | 69.3 | ✓/✓ | 32 | 188 | 0 | 0 | pipeline.py + run script |
| 9 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 20.0 | 75.4 | ⏱ | 1 | 7.4m | 100.0 | 100.0 | 71.1 | ✓/✓ | 40 | 169 | 0 | 0 | pipeline.py + run script |
| 9 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 40.0 | 66.8 | ⏱ | 1 | 24.0m | 100.0 | 100.0 | 75.4 | ✓/✓ | 50 | 464 | 0 | 0 | 3 sub-project output(s) well-formed |
| 9 | codex-cli | suite | gpt-5.3-codex | 🟡 PART | 40.0 | 75.8 | ⏱ | 1 | 24.0m | 100.0 | 100.0 | 77.2 | ✓/✓ | 50 | 464 | 0 | 0 | only one of (compiler, app) primary deliverables |
| 9 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 1 | 19.3m | 100.0 | 95.0 | 84.7 | ✓/✓ | 47 | 187 | 0 | 1 | .dxnn + config.json present |
| 9 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 1 | 7.6m | 100.0 | 100.0 | 77.3 | ✓/✓ | 67 | 238 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 9 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 5.9m | 100.0 | 100.0 | 75.4 | ✓/✓ | 61 | 155 | 0 | 0 | pipeline.py + run script |
| 9 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 5.1m | 100.0 | 100.0 | 75.7 | ✓/✓ | 41 | 215 | 0 | 0 | pipeline.py + run script |
| 9 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 12.3m | 83.3 | 95.0 | 70.3 | ✓/✓ | 62 | 551 | 0 | 1 | 3 sub-project output(s) well-formed |
| 9 | copilot-cli | suite | 4.6 | ✅ PASS | 55.0 | 56.1 |  | 1 | 12.3m | 85.7 | 95.0 | 72.4 | ✓/✓ | 62 | 551 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 9 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 1 | 41.5m | 100.0 | 100.0 | 86.8 | ✓/✓ | 60 | 176 | 0 | 0 | .dxnn + config.json present |
| 9 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 35.0 | 78.0 |  | 1 | 5.8m | 100.0 | 100.0 | 76.1 | ✓/✓ | 56 | 281 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 9 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 1 | 2.6m | 100.0 | 100.0 | 74.0 | ✓/✓ | 32 | 151 | 0 | 0 | pipeline.py + run script |
| 9 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 1 | 2.8m | 100.0 | 100.0 | 75.4 | ✓/✓ | 35 | 190 | 0 | 0 | pipeline.py + run script |
| 9 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 60.0 | 61.7 |  | 1 | 13.5m | 100.0 | 100.0 | 80.3 | ✓/✓ | 86 | 353 | 0 | 0 | 1 sub-project output(s) well-formed |
| 9 | cursor-cli | suite | cursor-auto ⚠ | ✅ PASS | 60.0 | 86.5 |  | 1 | 13.5m | 100.0 | 100.0 | 85.3 | ✓/✓ | 86 | 353 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 9 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 1 | 15.6m | 100.0 | 90.0 | 85.6 | ✓/✓ | 40 | 574 | 0 | 2 | .dxnn + config.json present |
| 9 | opencode-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 73.5 |  | 1 | 3.5m | 100.0 | 100.0 | 75.2 | ✓/✓ | 41 | 250 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 9 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 3.8m | 100.0 | 100.0 | 75.4 | ✓/✓ | 39 | 155 | 0 | 0 | pipeline.py + run script |
| 9 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 1 | 4.4m | 100.0 | 100.0 | 74.2 | ✓/✓ | 40 | 209 | 0 | 0 | pipeline.py + run script |
| 9 | opencode-cli | runtime | 4.6 | ✅ PASS | 55.0 | 59.5 | ⏱ | 1 | 40.1m | 100.0 | 95.0 | 77.4 | ✓/✓ | 3 | 1383 | 0 | 1 | 8 sub-project output(s) well-formed |
| 9 | opencode-cli | suite | 4.6 | ✅ PASS | 55.0 | 63.6 | ⏱ | 1 | 40.1m | 100.0 | 95.0 | 78.2 | ✓/✓ | 3 | 1383 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 10 | claude-code | compiler | 4.6 | ✅ PASS | 75.0 | 86.2 |  | 1 | 16.6m | 100.0 | 95.0 | 88.8 | ✓/✓ | 79 | 280 | 0 | 1 | .dxnn + config.json present |
| 10 | claude-code | dx_app | 4.6 | ✅ PASS | 35.0 | 84.9 |  | 1 | 7.9m | 100.0 | 100.0 | 77.5 | ✓/✓ | 81 | 217 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 10 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 6.8m | 100.0 | 100.0 | 76.8 | ✓/✓ | 65 | 151 | 0 | 0 | pipeline.py + run script |
| 10 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 7.6m | 100.0 | 100.0 | 76.0 | ✓/✓ | 63 | 209 | 0 | 0 | pipeline.py + run script |
| 10 | claude-code | runtime | 4.6 | ✅ PASS | 55.0 | 80.2 |  | 1 | 19.2m | 100.0 | 95.0 | 81.5 | ✓/✓ | 106 | 544 | 0 | 1 | 3 sub-project output(s) well-formed |
| 10 | claude-code | suite | 4.6 | ✅ PASS | 55.0 | 89.2 |  | 1 | 19.2m | 100.0 | 95.0 | 83.3 | ✓/✓ | 106 | 544 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 10 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 75.0 | 75.4 |  | 1 | 27.9m | 100.0 | 95.0 | 86.6 | ✓/✓ | 47 | 219 | 0 | 1 | .dxnn + config.json present |
| 10 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 5.9m | 100.0 | 100.0 | 70.3 | ✓/✓ | 40 | 235 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 10 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 25.0 | 66.3 | ⏱ | 1 | 6.7m | 100.0 | 100.0 | 70.8 | ✓/✓ | 43 | 176 | 0 | 0 | pipeline.py + run script |
| 10 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 |  | 1 | 5.0m | 100.0 | 100.0 | 75.6 | ✓/✓ | 40 | 183 | 0 | 0 | pipeline.py + run script |
| 10 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 60.0 | 66.8 | ⏱ | 1 | 11.2m | 100.0 | 95.0 | 80.4 | ✓/✓ | 44 | 512 | 0 | 1 | 3 sub-project output(s) well-formed |
| 10 | codex-cli | suite | gpt-5.3-codex | ✅ PASS | 60.0 | 75.8 | ⏱ | 1 | 11.2m | 100.0 | 95.0 | 82.2 | ✓/✓ | 44 | 512 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 10 | copilot-cli | compiler | 4.6 | ❌ FAIL | 75.0 | 65.8 |  | 1 | 18.9m | 85.7 | 100.0 | 81.4 | ✓/✓ | 61 | 166 | 0 | 0 | compiler artifacts missing |
| 10 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 1 | 6.9m | 100.0 | 100.0 | 75.8 | ✓/✓ | 67 | 263 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 10 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 4.9m | 100.0 | 100.0 | 75.4 | ✓/✓ | 52 | 151 | 0 | 0 | pipeline.py + run script |
| 10 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 7.2m | 100.0 | 100.0 | 75.7 | ✓/✓ | 50 | 201 | 0 | 0 | pipeline.py + run script |
| 10 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 15.2m | 83.3 | 95.0 | 70.3 | ✓/✓ | 76 | 803 | 0 | 1 | 3 sub-project output(s) well-formed |
| 10 | copilot-cli | suite | 4.6 | ✅ PASS | 55.0 | 56.1 |  | 1 | 15.2m | 85.7 | 95.0 | 72.4 | ✓/✓ | 76 | 803 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |
| 10 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 65.0 | 71.6 |  | 0 | 13.6m | 100.0 | 100.0 | 83.8 | ✓/✓ | 50 | 254 | 0 | 0 | .dxnn + config.json present |
| 10 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 25.0 | 78.0 |  | 0 | 9.8m | 100.0 | 100.0 | 73.1 | ✓/✓ | 55 | 281 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 10 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 0 | 2.5m | 100.0 | 100.0 | 74.0 | ✓/✓ | 36 | 181 | 0 | 0 | pipeline.py + run script |
| 10 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 0 | 2.7m | 100.0 | 100.0 | 75.4 | ✓/✓ | 44 | 224 | 0 | 0 | pipeline.py + run script |
| 10 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 55.0 | 61.7 |  | 0 | 14.5m | 100.0 | 100.0 | 78.8 | ✓/✓ | 97 | 342 | 0 | 0 | 1 sub-project output(s) well-formed |
| 10 | cursor-cli | suite | cursor-auto ⚠ | ✅ PASS | 55.0 | 86.5 |  | 0 | 14.5m | 100.0 | 100.0 | 83.8 | ✓/✓ | 97 | 342 | 0 | 0 | dual session dirs (compiler+app) with primary deliverables |
| 10 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 0 | 31.3m | 100.0 | 95.0 | 86.6 | ✓/✓ | 34 | 213 | 0 | 1 | .dxnn + config.json present |
| 10 | opencode-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 73.5 |  | 0 | 2.9m | 100.0 | 100.0 | 75.2 | ✓/✓ | 38 | 231 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 10 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.8m | 100.0 | 100.0 | 75.4 | ✓/✓ | 38 | 335 | 0 | 0 | pipeline.py + run script |
| 10 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 4.0m | 100.0 | 100.0 | 74.2 | ✓/✓ | 35 | 175 | 0 | 0 | pipeline.py + run script |
| 10 | opencode-cli | runtime | 4.6 | ✅ PASS | 40.0 | 59.5 | ⏱ | 0 | 16.8m | 100.0 | 90.0 | 71.9 | ✓/✓ | 87 | 955 | 0 | 2 | 5 sub-project output(s) well-formed |
| 10 | opencode-cli | suite | 4.6 | ✅ PASS | 40.0 | 63.6 | ⏱ | 0 | 16.8m | 100.0 | 90.0 | 72.7 | ✓/✓ | 87 | 955 | 0 | 2 | dual session dirs (compiler+app) with primary deliverables |
| 11 | claude-code | compiler | 4.6 | ✅ PASS | 90.0 | 86.2 |  | 1 | 1.3m | 100.0 | 90.0 | 92.2 | ✓/✓ | 87 | 655 | 0 | 2 | .dxnn + config.json present |
| 11 | claude-code | dx_app | 4.6 | ✅ PASS | 40.0 | 84.9 |  | 1 | 8.0m | 100.0 | 100.0 | 79.0 | ✓/✓ | 71 | 249 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 11 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 8.0m | 100.0 | 100.0 | 76.8 | ✓/✓ | 87 | 154 | 0 | 0 | pipeline.py + run script |
| 11 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 7.9m | 100.0 | 100.0 | 76.0 | ✓/✓ | 64 | 224 | 0 | 0 | pipeline.py + run script |
| 11 | claude-code | runtime | 4.6 | ✅ PASS | 65.0 | 80.2 |  | 1 | 16.8m | 100.0 | 100.0 | 85.5 | ✓/✓ | 99 | 665 | 0 | 0 | 3 sub-project output(s) well-formed |
| 11 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 40.0 | 100.0 | 49.9 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 11 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 60.0 | 75.4 |  | 1 | 22.1m | 100.0 | 100.0 | 83.1 | ✓/✓ | 52 | 209 | 0 | 0 | .dxnn + config.json present |
| 11 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 6.5m | 100.0 | 100.0 | 68.8 | ✓/✓ | 42 | 230 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 11 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 | ⏱ | 1 | 9.8m | 85.7 | 100.0 | 69.5 | ✓/✗ | 61 | 214 | 0 | 0 | pipeline.py + run script |
| 11 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 |  | 1 | 7.0m | 100.0 | 100.0 | 75.6 | ✓/✓ | 46 | 199 | 0 | 0 | pipeline.py + run script |
| 11 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 65.0 | 66.8 | ⏱ | 1 | 9.2m | 100.0 | 95.0 | 81.9 | ✓/✓ | 73 | 725 | 0 | 1 | 3 sub-project output(s) well-formed |
| 11 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.1s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 11 | copilot-cli | compiler | 4.6 | ✅ PASS | 80.0 | 65.8 |  | 1 | 27.1m | 100.0 | 90.0 | 85.2 | ✓/✓ | 76 | 467 | 0 | 2 | .dxnn + config.json present |
| 11 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 1 | 5.8m | 100.0 | 100.0 | 77.3 | ✓/✓ | 58 | 245 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 11 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 5.0m | 100.0 | 100.0 | 75.4 | ✓/✓ | 46 | 192 | 0 | 0 | pipeline.py + run script |
| 11 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 40.0 | 75.8 |  | 1 | 7.1m | 100.0 | 100.0 | 77.2 | ✓/✓ | 58 | 240 | 0 | 0 | pipeline.py + run script |
| 11 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 16.3m | 83.3 | 95.0 | 70.3 | ✓/✓ | 100 | 830 | 0 | 1 | 3 sub-project output(s) well-formed |
| 11 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 1 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 11 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 0 | 37.8m | 100.0 | 100.0 | 86.8 | ✓/✓ | 95 | 335 | 0 | 0 | .dxnn + config.json present |
| 11 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 45.0 | 78.0 |  | 0 | 3.7m | 100.0 | 100.0 | 79.1 | ✓/✓ | 50 | 227 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 11 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 | ⏱ | 0 | 3.3m | 100.0 | 100.0 | 74.0 | ✓/✓ | 37 | 224 | 0 | 0 | pipeline.py + run script |
| 11 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 0 | 6.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 48 | 191 | 0 | 0 | pipeline.py + run script |
| 11 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 45.0 | 61.7 |  | 0 | 18.5m | 100.0 | 100.0 | 75.8 | ✓/✓ | 91 | 293 | 0 | 0 | 1 sub-project output(s) well-formed |
| 11 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 0 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 11 | opencode-cli | compiler | 4.6 | ✅ PASS | 60.0 | 75.6 |  | 0 | 35.6m | 100.0 | 95.0 | 82.1 | ✓/✓ | 40 | 502 | 0 | 1 | .dxnn + config.json present |
| 11 | opencode-cli | dx_app | 4.6 | ✅ PASS | 25.0 | 73.5 |  | 0 | 4.1m | 100.0 | 100.0 | 72.2 | ✓/✓ | 51 | 250 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 11 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 2.8m | 100.0 | 100.0 | 75.4 | ✓/✓ | 32 | 153 | 0 | 0 | pipeline.py + run script |
| 11 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 3.7m | 100.0 | 100.0 | 74.2 | ✓/✓ | 38 | 196 | 0 | 0 | pipeline.py + run script |
| 11 | opencode-cli | runtime | 4.6 | ✅ PASS | 65.0 | 59.5 | ⏱ | 0 | 17.9m | 100.0 | 90.0 | 79.4 | ✓/✓ | 94 | 1309 | 0 | 2 | 6 sub-project output(s) well-formed |
| 11 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 12 | claude-code | compiler | 4.6 | ✅ PASS | 75.0 | 86.2 |  | 0 | 42.9m | 100.0 | 95.0 | 88.8 | ✓/✓ | 85 | 274 | 0 | 1 | .dxnn + config.json present |
| 12 | claude-code | dx_app | 4.6 | ✅ PASS | 20.0 | 84.9 |  | 0 | 7.4m | 100.0 | 100.0 | 73.0 | ✓/✓ | 71 | 219 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 12 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 0 | 6.1m | 100.0 | 100.0 | 76.8 | ✓/✓ | 63 | 151 | 0 | 0 | pipeline.py + run script |
| 12 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 0 | 7.2m | 100.0 | 100.0 | 76.0 | ✓/✓ | 70 | 217 | 0 | 0 | pipeline.py + run script |
| 12 | claude-code | runtime | 4.6 | ✅ PASS | 65.0 | 80.2 |  | 0 | 11.5m | 100.0 | 100.0 | 85.5 | ✓/✓ | 87 | 588 | 0 | 0 | 3 sub-project output(s) well-formed |
| 12 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 0 | 0.0s | 40.0 | 100.0 | 49.9 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 12 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 80.0 | 75.4 |  | 1 | 30.4m | 100.0 | 95.0 | 88.1 | ✓/✓ | 90 | 335 | 0 | 1 | .dxnn + config.json present |
| 12 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 9.0m | 100.0 | 100.0 | 70.3 | ✓/✓ | 57 | 231 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 12 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 20.0 | 66.3 | ⏱ | 1 | 7.1m | 100.0 | 100.0 | 69.3 | ✓/✓ | 52 | 194 | 0 | 0 | pipeline.py + run script |
| 12 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 25.0 | 75.4 |  | 1 | 7.3m | 100.0 | 100.0 | 72.6 | ✓/✓ | 37 | 200 | 0 | 0 | pipeline.py + run script |
| 12 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 60.0 | 66.8 |  | 1 | 18.2m | 100.0 | 95.0 | 80.4 | ✓/✓ | 81 | 793 | 0 | 1 | 3 sub-project output(s) well-formed |
| 12 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.1s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 12 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 1 | 33.1m | 85.7 | 90.0 | 79.4 | ✓/✓ | 48 | 328 | 0 | 2 | .dxnn + config.json present |
| 12 | copilot-cli | dx_app | 4.6 | ✅ PASS | 20.0 | 76.7 |  | 1 | 6.5m | 100.0 | 100.0 | 71.3 | ✓/✓ | 68 | 233 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 12 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 4.5m | 100.0 | 100.0 | 75.4 | ✓/✓ | 49 | 170 | 0 | 0 | pipeline.py + run script |
| 12 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 5.2m | 100.0 | 100.0 | 75.7 | ✓/✓ | 48 | 225 | 0 | 0 | pipeline.py + run script |
| 12 | copilot-cli | runtime | 4.6 | ✅ PASS | 60.0 | 48.9 |  | 1 | 13.6m | 83.3 | 95.0 | 71.8 | ✓/✓ | 77 | 743 | 0 | 1 | 3 sub-project output(s) well-formed |
| 12 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 1 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 12 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 1 | 35.8m | 100.0 | 100.0 | 86.8 | ✓/✓ | 61 | 184 | 0 | 0 | .dxnn + config.json present |
| 12 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 40.0 | 78.0 |  | 1 | 7.0m | 100.0 | 100.0 | 77.6 | ✓/✓ | 61 | 279 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 12 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 | ⏱ | 1 | 8.2m | 100.0 | 100.0 | 74.0 | ✓/✓ | 34 | 194 | 0 | 0 | pipeline.py + run script |
| 12 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 1 | 6.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 45 | 189 | 0 | 0 | pipeline.py + run script |
| 12 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 60.0 | 61.7 |  | 1 | 15.0m | 100.0 | 100.0 | 80.3 | ✓/✓ | 66 | 209 | 0 | 0 | 1 sub-project output(s) well-formed |
| 12 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 12 | opencode-cli | compiler | 4.6 | ✅ PASS | 80.0 | 75.6 |  | 0 | 35.2m | 100.0 | 90.0 | 87.1 | ✓/✓ | 47 | 646 | 0 | 2 | .dxnn + config.json present |
| 12 | opencode-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 73.5 |  | 0 | 2.8m | 100.0 | 100.0 | 75.2 | ✓/✓ | 37 | 242 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 12 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 29 | 155 | 0 | 0 | pipeline.py + run script |
| 12 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 3.7m | 100.0 | 100.0 | 74.2 | ✓/✓ | 32 | 198 | 0 | 0 | pipeline.py + run script |
| 12 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 |  | 0 | 26.1m | 100.0 | 90.0 | 77.9 | ✓/✓ | 69 | 1456 | 0 | 2 | 6 sub-project output(s) well-formed |
| 12 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 13 | claude-code | compiler | 4.6 | ✅ PASS | 70.0 | 86.2 |  | 1 | 1.5m | 100.0 | 95.0 | 87.2 | ✓/✓ | 62 | 268 | 0 | 1 | .dxnn + config.json present |
| 13 | claude-code | dx_app | 4.6 | ✅ PASS | 40.0 | 84.9 |  | 1 | 8.3m | 100.0 | 100.0 | 79.0 | ✓/✓ | 84 | 230 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 13 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 8.5m | 100.0 | 100.0 | 76.8 | ✓/✓ | 77 | 151 | 0 | 0 | pipeline.py + run script |
| 13 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 6.2m | 100.0 | 100.0 | 76.0 | ✓/✓ | 59 | 216 | 0 | 0 | pipeline.py + run script |
| 13 | claude-code | runtime | 4.6 | ✅ PASS | 45.0 | 80.2 |  | 1 | 7.0m | 83.3 | 90.0 | 72.5 | ✓/✗ | 60 | 686 | 0 | 2 | 3 sub-project output(s) well-formed |
| 13 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 20.0 | 100.0 | 43.9 | ✓/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 13 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 80.0 | 75.4 |  | 1 | 29.6m | 100.0 | 90.0 | 87.1 | ✓/✓ | 45 | 329 | 0 | 2 | .dxnn + config.json present |
| 13 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 9.5m | 100.0 | 100.0 | 70.3 | ✓/✓ | 71 | 228 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 13 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 | ⏱ | 1 | 9.9m | 85.7 | 100.0 | 69.5 | ✓/✗ | 64 | 211 | 0 | 0 | pipeline.py + run script |
| 13 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 25.0 | 75.4 |  | 1 | 7.2m | 100.0 | 100.0 | 72.6 | ✓/✓ | 48 | 201 | 0 | 0 | pipeline.py + run script |
| 13 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 60.0 | 66.8 |  | 1 | 9.9m | 100.0 | 95.0 | 80.4 | ✓/✓ | 86 | 689 | 0 | 1 | 3 sub-project output(s) well-formed |
| 13 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.2s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 13 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 1 | 45.9m | 100.0 | 100.0 | 85.7 | ✓/✓ | 70 | 180 | 0 | 0 | .dxnn + config.json present |
| 13 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 1 | 6.2m | 100.0 | 100.0 | 77.3 | ✓/✓ | 53 | 230 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 13 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 25.0 | 74.7 |  | 1 | 6.1m | 100.0 | 100.0 | 72.4 | ✓/✓ | 56 | 183 | 0 | 0 | pipeline.py + run script |
| 13 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 6.3m | 100.0 | 100.0 | 75.7 | ✓/✓ | 54 | 191 | 0 | 0 | pipeline.py + run script |
| 13 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 16.5m | 83.3 | 95.0 | 70.3 | ✓/✓ | 85 | 503 | 0 | 1 | 3 sub-project output(s) well-formed |
| 13 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 1 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 13 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 90.0 | 71.6 |  | 1 | 42.8m | 100.0 | 100.0 | 91.3 | ✓/✓ | 72 | 168 | 0 | 0 | .dxnn + config.json present |
| 13 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 50.0 | 78.0 |  | 1 | 5.5m | 100.0 | 100.0 | 80.6 | ✓/✓ | 44 | 279 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 13 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 1 | 5.2m | 100.0 | 100.0 | 74.0 | ✓/✓ | 39 | 211 | 0 | 0 | pipeline.py + run script |
| 13 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 1 | 6.3m | 100.0 | 100.0 | 75.4 | ✓/✓ | 44 | 215 | 0 | 0 | pipeline.py + run script |
| 13 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 65.0 | 61.7 |  | 1 | 15.9m | 100.0 | 100.0 | 81.8 | ✓/✓ | 68 | 251 | 0 | 0 | 1 sub-project output(s) well-formed |
| 13 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 13 | opencode-cli | compiler | 4.6 | ✅ PASS | 80.0 | 75.6 |  | 1 | 45.0m | 100.0 | 77.3 | 84.6 | ✓/✓ | 35 | 625 | 0 | 4 | .dxnn + config.json present |
| 13 | opencode-cli | dx_app | 4.6 | ✅ PASS | 25.0 | 73.5 |  | 1 | 4.0m | 100.0 | 100.0 | 72.2 | ✓/✓ | 44 | 250 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 13 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 3.9m | 100.0 | 100.0 | 75.4 | ✓/✓ | 40 | 352 | 0 | 0 | pipeline.py + run script |
| 13 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 1 | 4.0m | 100.0 | 100.0 | 74.2 | ✓/✓ | 36 | 201 | 0 | 0 | pipeline.py + run script |
| 13 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 |  | 1 | 15.6m | 100.0 | 90.0 | 77.9 | ✓/✓ | 69 | 1523 | 0 | 2 | 6 sub-project output(s) well-formed |
| 13 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 1 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | claude-code | compiler | 4.6 | ❓ UNKN | 0.0 | 86.2 |  | 1 | 0.0s | 0.0 | 100.0 | 37.2 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | claude-code | dx_app | 4.6 | ❓ UNKN | 0.0 | 84.9 |  | 1 | 0.0s | 0.0 | 100.0 | 37.0 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | claude-code | dx_stream | 4.6 | ❓ UNKN | 0.0 | 81.3 |  | 1 | 0.0s | 0.0 | 100.0 | 36.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | claude-code | dx_stream_cascaded | 4.6 | ❓ UNKN | 0.0 | 77.3 |  | 1 | 0.0s | 0.0 | 100.0 | 35.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | claude-code | runtime | 4.6 | ❓ UNKN | 0.0 | 80.2 |  | 1 | 2.0s | 0.0 | 100.0 | 36.0 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 0.0 | 100.0 | 37.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 80.0 | 75.4 |  | 1 | 30.1m | 100.0 | 90.0 | 87.1 | ✓/✓ | 67 | 429 | 0 | 2 | .dxnn + config.json present |
| 14 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 18.7m | 100.0 | 100.0 | 70.3 | ✓/✓ | 66 | 225 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 14 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 40.0 | 66.3 | ⏱ | 1 | 7.9m | 100.0 | 100.0 | 75.3 | ✓/✓ | 52 | 177 | 0 | 0 | pipeline.py + run script |
| 14 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 20.0 | 75.4 | ⏱ | 1 | 8.1m | 100.0 | 100.0 | 71.1 | ✓/✓ | 40 | 222 | 0 | 0 | pipeline.py + run script |
| 14 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 55.0 | 66.8 | ⏱ | 1 | 17.2m | 100.0 | 95.0 | 78.9 | ✓/✓ | 71 | 795 | 0 | 1 | 3 sub-project output(s) well-formed |
| 14 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.1s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 0 | 39.8m | 100.0 | 95.0 | 84.7 | ✓/✓ | 56 | 192 | 0 | 1 | .dxnn + config.json present |
| 14 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 0 | 5.3m | 100.0 | 100.0 | 77.3 | ✓/✓ | 58 | 238 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 14 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 7.7m | 100.0 | 100.0 | 75.4 | ✓/✓ | 51 | 151 | 0 | 0 | pipeline.py + run script |
| 14 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 0 | 5.3m | 100.0 | 100.0 | 75.7 | ✓/✓ | 48 | 227 | 0 | 0 | pipeline.py + run script |
| 14 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 0 | 17.2m | 83.3 | 95.0 | 70.3 | ✓/✓ | 74 | 599 | 0 | 1 | 3 sub-project output(s) well-formed |
| 14 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 0 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 0 | 31.1m | 100.0 | 100.0 | 86.8 | ✓/✓ | 65 | 175 | 0 | 0 | .dxnn + config.json present |
| 14 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 45.0 | 78.0 |  | 0 | 4.9m | 100.0 | 100.0 | 79.1 | ✓/✓ | 47 | 233 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 14 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 0 | 8.4m | 100.0 | 100.0 | 74.0 | ✓/✓ | 40 | 205 | 0 | 0 | pipeline.py + run script |
| 14 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 0 | 7.9m | 100.0 | 100.0 | 75.4 | ✓/✓ | 54 | 233 | 0 | 0 | pipeline.py + run script |
| 14 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 50.0 | 61.7 |  | 0 | 23.0m | 100.0 | 100.0 | 77.3 | ✓/✓ | 111 | 257 | 0 | 0 | 1 sub-project output(s) well-formed |
| 14 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 0 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 14 | opencode-cli | compiler | 4.6 | ✅ PASS | 80.0 | 75.6 |  | 0 | 33.9m | 100.0 | 85.0 | 86.1 | ✓/✓ | 63 | 805 | 0 | 4 | .dxnn + config.json present |
| 14 | opencode-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 73.5 |  | 0 | 6.0m | 100.0 | 100.0 | 76.7 | ✓/✓ | 58 | 471 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 14 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.7m | 100.0 | 100.0 | 75.4 | ✓/✓ | 36 | 152 | 0 | 0 | pipeline.py + run script |
| 14 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 3.9m | 100.0 | 100.0 | 74.2 | ✓/✓ | 34 | 223 | 0 | 0 | pipeline.py + run script |
| 14 | opencode-cli | runtime | 4.6 | ✅ PASS | 55.0 | 59.5 | ⏱ | 0 | 23.7m | 83.3 | 95.0 | 72.4 | ✓/✓ | 83 | 1673 | 0 | 1 | 8 sub-project output(s) well-formed |
| 14 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 15 | claude-code | compiler | 4.6 | ✅ PASS | 70.0 | 86.2 |  | 1 | 2.5m | 100.0 | 95.0 | 87.2 | ✓/✓ | 74 | 277 | 0 | 1 | .dxnn + config.json present |
| 15 | claude-code | dx_app | 4.6 | ✅ PASS | 35.0 | 84.9 |  | 1 | 7.0m | 100.0 | 100.0 | 77.5 | ✓/✓ | 69 | 213 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 15 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 6.4m | 100.0 | 100.0 | 76.8 | ✓/✓ | 59 | 151 | 0 | 0 | pipeline.py + run script |
| 15 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 9.6m | 100.0 | 100.0 | 76.0 | ✓/✓ | 89 | 190 | 0 | 0 | pipeline.py + run script |
| 15 | claude-code | runtime | 4.6 | ✅ PASS | 65.0 | 80.2 |  | 1 | 16.1m | 100.0 | 95.0 | 84.5 | ✓/✓ | 96 | 538 | 0 | 1 | 3 sub-project output(s) well-formed |
| 15 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 40.0 | 100.0 | 49.9 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 15 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 70.0 | 75.4 |  | 1 | 28.2m | 100.0 | 95.0 | 85.1 | ✓/✓ | 79 | 176 | 0 | 1 | .dxnn + config.json present |
| 15 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 17.1m | 100.0 | 100.0 | 70.3 | ✓/✓ | 71 | 235 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 15 | codex-cli | dx_stream | gpt-5.3-codex | ❓ UNKN | 0.0 | 66.3 |  | 1 | 9.9m | 20.0 | 100.0 | 39.3 | ✓/✗ | 43 | 0 | 0 | 0 | no output directory linked |
| 15 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 | ⏱ | 1 | 9.5m | 100.0 | 100.0 | 75.6 | ✓/✓ | 43 | 273 | 0 | 0 | pipeline.py + run script |
| 15 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 60.0 | 66.8 |  | 1 | 10.3m | 100.0 | 95.0 | 80.4 | ✓/✓ | 54 | 644 | 0 | 1 | 3 sub-project output(s) well-formed |
| 15 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.2s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 15 | copilot-cli | compiler | 4.6 | ❌ FAIL | 45.0 | 65.8 |  | 1 | 25.0m | 57.1 | 100.0 | 63.8 | ✓/✗ | 31 | 116 | 0 | 0 | config.json present but no .dxnn produced |
| 15 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 1 | 6.1m | 100.0 | 100.0 | 75.8 | ✓/✓ | 59 | 233 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 15 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 6.3m | 100.0 | 100.0 | 75.4 | ✓/✓ | 61 | 151 | 0 | 0 | pipeline.py + run script |
| 15 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 6.8m | 100.0 | 100.0 | 75.7 | ✓/✓ | 59 | 213 | 0 | 0 | pipeline.py + run script |
| 15 | copilot-cli | runtime | 4.6 | ✅ PASS | 40.0 | 48.9 |  | 1 | 19.3m | 83.3 | 95.0 | 65.8 | ✓/✓ | 72 | 583 | 0 | 1 | 3 sub-project output(s) well-formed |
| 15 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 1 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 15 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 1 | 37.8m | 100.0 | 100.0 | 86.8 | ✓/✓ | 64 | 247 | 0 | 0 | .dxnn + config.json present |
| 15 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 30.0 | 78.0 |  | 1 | 7.7m | 100.0 | 100.0 | 74.6 | ✓/✓ | 33 | 256 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 15 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 1 | 3.5m | 100.0 | 100.0 | 74.0 | ✓/✓ | 39 | 176 | 0 | 0 | pipeline.py + run script |
| 15 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 1 | 4.0m | 100.0 | 100.0 | 75.4 | ✓/✓ | 37 | 212 | 0 | 0 | pipeline.py + run script |
| 15 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 60.0 | 61.7 |  | 1 | 19.4m | 100.0 | 100.0 | 80.3 | ✓/✓ | 97 | 380 | 0 | 0 | 1 sub-project output(s) well-formed |
| 15 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 15 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 1 | 36.4m | 100.0 | 90.0 | 85.6 | ✓/✓ | 33 | 385 | 0 | 2 | .dxnn + config.json present |
| 15 | opencode-cli | dx_app | 4.6 | ✅ PASS | 25.0 | 73.5 |  | 1 | 4.3m | 100.0 | 100.0 | 72.2 | ✓/✓ | 46 | 244 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 15 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 3.7m | 100.0 | 100.0 | 75.4 | ✓/✓ | 34 | 152 | 0 | 0 | pipeline.py + run script |
| 15 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 1 | 4.5m | 83.3 | 100.0 | 69.2 | ✓/✗ | 43 | 218 | 0 | 0 | pipeline.py + run script |
| 15 | opencode-cli | runtime | 4.6 | ✅ PASS | 45.0 | 59.5 | ⏱ | 1 | 10.5m | 83.3 | 95.0 | 69.4 | ✓/✓ | 77 | 1175 | 0 | 1 | 4 sub-project output(s) well-formed |
| 15 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 1 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 16 | claude-code | compiler | 4.6 | ✅ PASS | 80.0 | 86.2 |  | 1 | 1.0m | 100.0 | 95.0 | 90.2 | ✓/✓ | 47 | 288 | 0 | 1 | .dxnn + config.json present |
| 16 | claude-code | dx_app | 4.6 | ✅ PASS | 25.0 | 84.9 |  | 1 | 6.5m | 100.0 | 100.0 | 74.5 | ✓/✓ | 76 | 243 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 16 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 6.5m | 100.0 | 100.0 | 76.8 | ✓/✓ | 68 | 151 | 0 | 0 | pipeline.py + run script |
| 16 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 5.8m | 100.0 | 100.0 | 76.0 | ✓/✓ | 58 | 225 | 0 | 0 | pipeline.py + run script |
| 16 | claude-code | runtime | 4.6 | ✅ PASS | 65.0 | 80.2 |  | 1 | 18.1m | 100.0 | 95.0 | 84.5 | ✓/✓ | 88 | 580 | 0 | 1 | 3 sub-project output(s) well-formed |
| 16 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 40.0 | 100.0 | 49.9 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 16 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 65.0 | 75.4 |  | 1 | 34.4m | 100.0 | 95.0 | 83.6 | ✓/✓ | 92 | 228 | 0 | 1 | .dxnn + config.json present |
| 16 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 9.5m | 100.0 | 100.0 | 68.8 | ✓/✓ | 43 | 215 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 16 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 | ⏱ | 1 | 9.8m | 85.7 | 100.0 | 69.5 | ✓/✗ | 59 | 218 | 0 | 0 | pipeline.py + run script |
| 16 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 |  | 1 | 9.2m | 83.3 | 100.0 | 70.6 | ✓/✗ | 47 | 289 | 0 | 0 | pipeline.py + run script |
| 16 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 50.0 | 66.8 | ⏱ | 1 | 16.1m | 100.0 | 95.0 | 77.4 | ✓/✓ | 88 | 680 | 0 | 1 | 3 sub-project output(s) well-formed |
| 16 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.2s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 16 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 1 | 19.8m | 100.0 | 100.0 | 85.7 | ✓/✓ | 43 | 69 | 0 | 0 | .dxnn + config.json present |
| 16 | copilot-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 76.7 |  | 1 | 6.2m | 100.0 | 100.0 | 75.8 | ✓/✓ | 70 | 215 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 16 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 6.2m | 100.0 | 100.0 | 75.4 | ✓/✓ | 51 | 159 | 0 | 0 | pipeline.py + run script |
| 16 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 7.0m | 100.0 | 100.0 | 75.7 | ✓/✓ | 47 | 226 | 0 | 0 | pipeline.py + run script |
| 16 | copilot-cli | runtime | 4.6 | ✅ PASS | 45.0 | 48.9 |  | 1 | 20.2m | 83.3 | 95.0 | 67.3 | ✓/✓ | 89 | 586 | 0 | 1 | 3 sub-project output(s) well-formed |
| 16 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 1 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 16 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 0 | 45.6m | 100.0 | 100.0 | 86.8 | ✓/✓ | 88 | 195 | 0 | 0 | .dxnn + config.json present |
| 16 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 20.0 | 78.0 |  | 0 | 5.0m | 100.0 | 100.0 | 71.6 | ✓/✓ | 54 | 239 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 16 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 0 | 4.3m | 100.0 | 100.0 | 74.0 | ✓/✓ | 30 | 186 | 0 | 0 | pipeline.py + run script |
| 16 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 0 | 3.9m | 100.0 | 100.0 | 75.4 | ✓/✓ | 49 | 185 | 0 | 0 | pipeline.py + run script |
| 16 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 55.0 | 61.7 |  | 0 | 16.8m | 100.0 | 95.0 | 77.8 | ✓/✓ | 90 | 278 | 0 | 1 | 1 sub-project output(s) well-formed |
| 16 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 0 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 16 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 0 | 49.9m | 100.0 | 85.0 | 84.6 | ✓/✓ | 48 | 946 | 0 | 5 | .dxnn + config.json present |
| 16 | opencode-cli | dx_app | 4.6 | ✅ PASS | 35.0 | 73.5 |  | 0 | 4.1m | 100.0 | 100.0 | 75.2 | ✓/✓ | 43 | 246 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 16 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.4m | 100.0 | 100.0 | 75.4 | ✓/✓ | 29 | 155 | 0 | 0 | pipeline.py + run script |
| 16 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 3.3m | 100.0 | 100.0 | 74.2 | ✓/✓ | 25 | 213 | 0 | 0 | pipeline.py + run script |
| 16 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 | ⏱ | 0 | 16.0m | 100.0 | 90.0 | 77.9 | ✓/✓ | 81 | 1307 | 0 | 2 | 6 sub-project output(s) well-formed |
| 16 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 17 | claude-code | compiler | 4.6 | ✅ PASS | 80.0 | 86.2 |  | 1 | 3.0m | 100.0 | 95.0 | 90.2 | ✓/✓ | 65 | 193 | 0 | 1 | .dxnn + config.json present |
| 17 | claude-code | dx_app | 4.6 | ✅ PASS | 45.0 | 84.9 |  | 1 | 6.1m | 100.0 | 100.0 | 80.5 | ✓/✓ | 67 | 224 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 17 | claude-code | dx_stream | 4.6 | ✅ PASS | 35.0 | 81.3 |  | 1 | 4.6m | 100.0 | 100.0 | 76.8 | ✓/✓ | 47 | 164 | 0 | 0 | pipeline.py + run script |
| 17 | claude-code | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 77.3 |  | 1 | 9.7m | 83.3 | 100.0 | 71.0 | ✓/✗ | 83 | 210 | 0 | 0 | pipeline.py + run script |
| 17 | claude-code | runtime | 4.6 | ✅ PASS | 65.0 | 80.2 |  | 1 | 16.5m | 100.0 | 100.0 | 85.5 | ✓/✓ | 90 | 566 | 0 | 0 | 3 sub-project output(s) well-formed |
| 17 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 40.0 | 100.0 | 49.9 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 17 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 80.0 | 75.4 |  | 1 | 47.9m | 100.0 | 100.0 | 89.1 | ✓/✓ | 50 | 211 | 0 | 0 | .dxnn + config.json present |
| 17 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 35.0 | 56.3 |  | 1 | 10.0m | 100.0 | 100.0 | 71.8 | ✓/✓ | 57 | 296 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 17 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 | ⏱ | 1 | 7.4m | 100.0 | 100.0 | 73.8 | ✓/✓ | 62 | 209 | 0 | 0 | pipeline.py + run script |
| 17 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 40.0 | 75.4 | ⏱ | 1 | 8.9m | 100.0 | 100.0 | 77.1 | ✓/✓ | 47 | 289 | 0 | 0 | pipeline.py + run script |
| 17 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 65.0 | 66.8 | ⏱ | 1 | 13.5m | 100.0 | 95.0 | 81.9 | ✓/✓ | 47 | 644 | 0 | 1 | 3 sub-project output(s) well-formed |
| 17 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.2s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 17 | copilot-cli | compiler | 4.6 | ❌ FAIL | 35.0 | 65.8 |  | 1 | 18.6m | 42.9 | 95.0 | 55.5 | ✓/✗ | 38 | 118 | 0 | 1 | config.json present but no .dxnn produced |
| 17 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 1 | 5.6m | 100.0 | 100.0 | 77.3 | ✓/✓ | 51 | 217 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 17 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 5.8m | 100.0 | 100.0 | 75.4 | ✓/✓ | 48 | 152 | 0 | 0 | pipeline.py + run script |
| 17 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 10.5m | 100.0 | 100.0 | 75.7 | ✓/✓ | 61 | 226 | 0 | 0 | pipeline.py + run script |
| 17 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 25.5m | 83.3 | 95.0 | 70.3 | ✓/✓ | 91 | 651 | 0 | 1 | 3 sub-project output(s) well-formed |
| 17 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 1 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 17 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 75.0 | 71.6 |  | 1 | 46.2m | 100.0 | 100.0 | 86.8 | ✓/✓ | 54 | 238 | 0 | 0 | .dxnn + config.json present |
| 17 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 35.0 | 78.0 |  | 1 | 6.4m | 100.0 | 100.0 | 76.1 | ✓/✓ | 60 | 264 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 17 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 40.0 | 67.4 | ⏱ | 1 | 3.4m | 100.0 | 100.0 | 75.5 | ✓/✓ | 37 | 178 | 0 | 0 | pipeline.py + run script |
| 17 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 1 | 4.6m | 100.0 | 100.0 | 75.4 | ✓/✓ | 58 | 197 | 0 | 0 | pipeline.py + run script |
| 17 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 55.0 | 61.7 |  | 1 | 12.3m | 100.0 | 95.0 | 77.8 | ✓/✓ | 91 | 377 | 0 | 1 | 1 sub-project output(s) well-formed |
| 17 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 17 | opencode-cli | compiler | 4.6 | ✅ PASS | 80.0 | 75.6 |  | 0 | 41.7m | 100.0 | 95.0 | 88.1 | ✓/✓ | 34 | 453 | 0 | 1 | .dxnn + config.json present |
| 17 | opencode-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 73.5 |  | 0 | 3.2m | 100.0 | 100.0 | 76.7 | ✓/✓ | 36 | 239 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 17 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 2.8m | 100.0 | 100.0 | 75.4 | ✓/✓ | 25 | 151 | 0 | 0 | pipeline.py + run script |
| 17 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 4.3m | 100.0 | 100.0 | 74.2 | ✓/✓ | 33 | 214 | 0 | 0 | pipeline.py + run script |
| 17 | opencode-cli | runtime | 4.6 | ✅ PASS | 65.0 | 59.5 | ⏱ | 0 | 14.9m | 83.3 | 100.0 | 76.4 | ✓/✓ | 78 | 816 | 0 | 0 | 4 sub-project output(s) well-formed |
| 17 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 18 | claude-code | compiler | 4.6 | ✅ PASS | 80.0 | 86.2 |  | 1 | 2.4m | 100.0 | 95.0 | 90.2 | ✓/✓ | 54 | 271 | 0 | 1 | .dxnn + config.json present |
| 18 | claude-code | dx_app | 4.6 | ✅ PASS | 45.0 | 84.9 |  | 1 | 7.2m | 100.0 | 100.0 | 80.5 | ✓/✓ | 76 | 224 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 18 | claude-code | dx_stream | 4.6 | ❓ UNKN | 0.0 | 81.3 |  | 1 | 7.4s | 20.0 | 100.0 | 42.3 | ✓/✗ | 1 | 0 | 0 | 0 | no output directory linked |
| 18 | claude-code | dx_stream_cascaded | 4.6 | ❓ UNKN | 0.0 | 77.3 |  | 1 | 0.0s | 0.0 | 100.0 | 35.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 18 | claude-code | runtime | 4.6 | ❓ UNKN | 0.0 | 80.2 |  | 1 | 2.2s | 0.0 | 100.0 | 36.0 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 18 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 0.0 | 100.0 | 37.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 18 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 80.0 | 75.4 |  | 1 | 48.0m | 100.0 | 100.0 | 89.1 | ✓/✓ | 35 | 187 | 0 | 0 | .dxnn + config.json present |
| 18 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 10.4m | 100.0 | 100.0 | 70.3 | ✓/✓ | 62 | 220 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 18 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 | ⏱ | 1 | 7.0m | 100.0 | 100.0 | 73.8 | ✓/✓ | 48 | 257 | 0 | 0 | pipeline.py + run script |
| 18 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 | ⏱ | 1 | 9.8m | 100.0 | 100.0 | 75.6 | ✓/✓ | 60 | 289 | 0 | 0 | pipeline.py + run script |
| 18 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 50.0 | 66.8 | ⏱ | 1 | 25.5m | 100.0 | 95.0 | 77.4 | ✓/✓ | 58 | 684 | 0 | 1 | 3 sub-project output(s) well-formed |
| 18 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.2s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 18 | copilot-cli | compiler | 4.6 | ✅ PASS | 70.0 | 65.8 |  | 0 | 47.0m | 100.0 | 95.0 | 83.2 | ✓/✓ | 60 | 193 | 0 | 1 | .dxnn + config.json present |
| 18 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 0 | 4.2m | 100.0 | 100.0 | 77.3 | ✓/✓ | 44 | 238 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 18 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 5.6m | 100.0 | 100.0 | 75.4 | ✓/✓ | 47 | 195 | 0 | 0 | pipeline.py + run script |
| 18 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 0 | 9.7m | 100.0 | 100.0 | 75.7 | ✓/✓ | 55 | 168 | 0 | 0 | pipeline.py + run script |
| 18 | copilot-cli | runtime | 4.6 | ✅ PASS | 60.0 | 48.9 |  | 0 | 16.1m | 83.3 | 95.0 | 71.8 | ✓/✓ | 107 | 499 | 0 | 1 | 3 sub-project output(s) well-formed |
| 18 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 0 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 18 | cursor-cli | compiler | cursor-auto ⚠ | ✅ PASS | 80.0 | 71.6 |  | 0 | 42.6m | 100.0 | 100.0 | 88.3 | ✓/✓ | 55 | 230 | 0 | 0 | .dxnn + config.json present |
| 18 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 55.0 | 78.0 |  | 0 | 2.7m | 100.0 | 100.0 | 82.1 | ✓/✓ | 45 | 319 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 18 | cursor-cli | dx_stream | cursor-auto ⚠ | ✅ PASS | 35.0 | 67.4 |  | 0 | 2.5m | 100.0 | 100.0 | 74.0 | ✓/✓ | 28 | 217 | 0 | 0 | pipeline.py + run script |
| 18 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ✅ PASS | 35.0 | 74.6 |  | 0 | 3.2m | 100.0 | 100.0 | 75.4 | ✓/✓ | 35 | 232 | 0 | 0 | pipeline.py + run script |
| 18 | cursor-cli | runtime | cursor-auto ⚠ | ✅ PASS | 45.0 | 61.7 |  | 0 | 15.9m | 100.0 | 100.0 | 75.8 | ✓/✓ | 91 | 465 | 0 | 0 | 1 sub-project output(s) well-formed |
| 18 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 0 | 0.0s | 40.0 | 100.0 | 49.3 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 18 | opencode-cli | compiler | 4.6 | ✅ PASS | 80.0 | 75.6 |  | 0 | 51.0m | 100.0 | 90.0 | 87.1 | ✓/✓ | 40 | 504 | 0 | 2 | .dxnn + config.json present |
| 18 | opencode-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 73.5 |  | 0 | 4.1m | 100.0 | 100.0 | 76.7 | ✓/✓ | 42 | 464 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 18 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.4m | 100.0 | 100.0 | 75.4 | ✓/✓ | 32 | 151 | 0 | 0 | pipeline.py + run script |
| 18 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 | ⏱ | 0 | 6.3m | 100.0 | 100.0 | 74.2 | ✓/✓ | 46 | 467 | 0 | 0 | pipeline.py + run script |
| 18 | opencode-cli | runtime | 4.6 | ✅ PASS | 55.0 | 59.5 | ⏱ | 0 | 17.0m | 83.3 | 95.0 | 72.4 | ✓/✓ | 88 | 876 | 0 | 1 | 4 sub-project output(s) well-formed |
| 18 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | claude-code | compiler | 4.6 | ❓ UNKN | 0.0 | 86.2 |  | 1 | 0.0s | 0.0 | 100.0 | 37.2 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | claude-code | dx_app | 4.6 | ❓ UNKN | 0.0 | 84.9 |  | 1 | 0.0s | 0.0 | 100.0 | 37.0 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | claude-code | dx_stream | 4.6 | ❓ UNKN | 0.0 | 81.3 |  | 1 | 0.0s | 0.0 | 100.0 | 36.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | claude-code | dx_stream_cascaded | 4.6 | ❓ UNKN | 0.0 | 77.3 |  | 1 | 0.0s | 0.0 | 100.0 | 35.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | claude-code | runtime | 4.6 | ❓ UNKN | 0.0 | 80.2 |  | 1 | 2.0s | 0.0 | 100.0 | 36.0 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 0.0 | 100.0 | 37.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 70.0 | 75.4 |  | 1 | 25.9m | 100.0 | 90.0 | 84.1 | ✓/✓ | 72 | 383 | 0 | 2 | .dxnn + config.json present |
| 19 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 30.0 | 56.3 |  | 1 | 6.3m | 100.0 | 100.0 | 70.3 | ✓/✓ | 51 | 234 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 19 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 35.0 | 66.3 |  | 1 | 8.7m | 100.0 | 100.0 | 73.8 | ✓/✓ | 55 | 278 | 0 | 0 | pipeline.py + run script |
| 19 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 35.0 | 75.4 | ⏱ | 1 | 7.5m | 100.0 | 100.0 | 75.6 | ✓/✓ | 57 | 212 | 0 | 0 | pipeline.py + run script |
| 19 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 65.0 | 66.8 | ⏱ | 1 | 20.8m | 100.0 | 90.0 | 80.9 | ✓/✓ | 59 | 693 | 0 | 2 | 3 sub-project output(s) well-formed |
| 19 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.2s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | copilot-cli | compiler | 4.6 | ✅ PASS | 60.0 | 65.8 |  | 1 | 34.1m | 100.0 | 95.0 | 80.2 | ✓/✓ | 66 | 144 | 0 | 1 | .dxnn + config.json present |
| 19 | copilot-cli | dx_app | 4.6 | ✅ PASS | 20.0 | 76.7 |  | 1 | 6.3m | 100.0 | 100.0 | 71.3 | ✓/✓ | 65 | 250 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 19 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 1 | 5.4m | 100.0 | 100.0 | 75.4 | ✓/✓ | 55 | 155 | 0 | 0 | pipeline.py + run script |
| 19 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 1 | 5.4m | 100.0 | 100.0 | 75.7 | ✓/✓ | 43 | 203 | 0 | 0 | pipeline.py + run script |
| 19 | copilot-cli | runtime | 4.6 | ✅ PASS | 55.0 | 48.9 |  | 1 | 13.2m | 83.3 | 95.0 | 70.3 | ✓/✓ | 72 | 752 | 0 | 1 | 3 sub-project output(s) well-formed |
| 19 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 1 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | cursor-cli | compiler | cursor-auto ⚠ | ❌ FAIL | 75.0 | 71.6 |  | 1 | 34.9m | 57.1 | 100.0 | 74.0 | ✓/✓ | 72 | 234 | 0 | 0 | compiler artifacts missing |
| 19 | cursor-cli | dx_app | cursor-auto ⚠ | ✅ PASS | 40.0 | 78.0 |  | 1 | 2.6m | 100.0 | 100.0 | 77.6 | ✓/✓ | 44 | 235 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 19 | cursor-cli | dx_stream | cursor-auto ⚠ | ❓ UNKN | 0.0 | 67.4 |  | 1 | 0.0s | 0.0 | 100.0 | 33.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ❓ UNKN | 0.0 | 74.6 |  | 1 | 2.2m | 0.0 | 100.0 | 34.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | cursor-cli | runtime | cursor-auto ⚠ | ❓ UNKN | 0.0 | 61.7 |  | 1 | 0.0s | 0.0 | 100.0 | 32.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 0.0 | 100.0 | 37.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 19 | opencode-cli | compiler | 4.6 | ✅ PASS | 75.0 | 75.6 |  | 0 | 52.9m | 100.0 | 85.0 | 84.6 | ✓/✓ | 39 | 596 | 0 | 3 | .dxnn + config.json present |
| 19 | opencode-cli | dx_app | 4.6 | ✅ PASS | 45.0 | 73.5 |  | 0 | 3.7m | 100.0 | 100.0 | 78.2 | ✓/✓ | 38 | 452 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 19 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 3.1m | 100.0 | 100.0 | 75.4 | ✓/✓ | 33 | 151 | 0 | 0 | pipeline.py + run script |
| 19 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 4.0m | 100.0 | 100.0 | 74.2 | ✓/✓ | 35 | 201 | 0 | 0 | pipeline.py + run script |
| 19 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 |  | 0 | 15.4m | 100.0 | 95.0 | 78.9 | ✓/✓ | 86 | 940 | 0 | 1 | 4 sub-project output(s) well-formed |
| 19 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | claude-code | compiler | 4.6 | ❓ UNKN | 0.0 | 86.2 |  | 1 | 0.0s | 0.0 | 100.0 | 37.2 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | claude-code | dx_app | 4.6 | ❓ UNKN | 0.0 | 84.9 |  | 1 | 0.0s | 0.0 | 100.0 | 37.0 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | claude-code | dx_stream | 4.6 | ❓ UNKN | 0.0 | 81.3 |  | 1 | 0.0s | 0.0 | 100.0 | 36.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | claude-code | dx_stream_cascaded | 4.6 | ❓ UNKN | 0.0 | 77.3 |  | 1 | 0.0s | 0.0 | 100.0 | 35.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | claude-code | runtime | 4.6 | ❓ UNKN | 0.0 | 80.2 |  | 1 | 1.8s | 0.0 | 100.0 | 36.0 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | claude-code | suite | 4.6 | ❓ UNKN | 0.0 | 89.2 |  | 1 | 0.0s | 0.0 | 100.0 | 37.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | codex-cli | compiler | gpt-5.3-codex | ✅ PASS | 65.0 | 75.4 |  | 1 | 30.2m | 100.0 | 90.0 | 82.6 | ✓/✓ | 74 | 255 | 0 | 2 | .dxnn + config.json present |
| 20 | codex-cli | dx_app | gpt-5.3-codex | ✅ PASS | 25.0 | 56.3 |  | 1 | 13.2m | 100.0 | 100.0 | 68.8 | ✓/✓ | 59 | 221 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 20 | codex-cli | dx_stream | gpt-5.3-codex | ✅ PASS | 20.0 | 66.3 | ⏱ | 1 | 8.1m | 100.0 | 100.0 | 69.3 | ✓/✓ | 55 | 285 | 0 | 0 | pipeline.py + run script |
| 20 | codex-cli | dx_stream_cascaded | gpt-5.3-codex | ✅ PASS | 20.0 | 75.4 | ⏱ | 1 | 8.3m | 100.0 | 100.0 | 71.1 | ✓/✓ | 45 | 290 | 0 | 0 | pipeline.py + run script |
| 20 | codex-cli | runtime | gpt-5.3-codex | ✅ PASS | 55.0 | 66.8 | ⏱ | 1 | 12.4m | 100.0 | 90.0 | 77.9 | ✓/✓ | 61 | 920 | 0 | 2 | 3 sub-project output(s) well-formed |
| 20 | codex-cli | suite | gpt-5.3-codex | ❓ UNKN | 0.0 | 75.8 |  | 1 | 0.2s | 40.0 | 100.0 | 47.1 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | copilot-cli | compiler | 4.6 | ✅ PASS | 75.0 | 65.8 |  | 0 | 28.7m | 100.0 | 100.0 | 85.7 | ✓/✓ | 54 | 153 | 0 | 0 | .dxnn + config.json present |
| 20 | copilot-cli | dx_app | 4.6 | ✅ PASS | 40.0 | 76.7 |  | 0 | 4.7m | 100.0 | 100.0 | 77.3 | ✓/✓ | 53 | 234 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 20 | copilot-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 |  | 0 | 5.2m | 100.0 | 100.0 | 75.4 | ✓/✓ | 55 | 151 | 0 | 0 | pipeline.py + run script |
| 20 | copilot-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 75.8 |  | 0 | 6.4m | 100.0 | 100.0 | 75.7 | ✓/✓ | 59 | 225 | 0 | 0 | pipeline.py + run script |
| 20 | copilot-cli | runtime | 4.6 | ✅ PASS | 65.0 | 48.9 |  | 0 | 20.5m | 83.3 | 95.0 | 73.3 | ✓/✓ | 102 | 665 | 0 | 1 | 3 sub-project output(s) well-formed |
| 20 | copilot-cli | suite | 4.6 | ❓ UNKN | 0.0 | 56.1 |  | 0 | 0.0s | 40.0 | 100.0 | 43.2 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | cursor-cli | compiler | cursor-auto ⚠ | ❓ UNKN | 0.0 | 71.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | cursor-cli | dx_app | cursor-auto ⚠ | ❓ UNKN | 0.0 | 78.0 |  | 1 | 0.0s | 0.0 | 100.0 | 35.6 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | cursor-cli | dx_stream | cursor-auto ⚠ | ❓ UNKN | 0.0 | 67.4 |  | 1 | 0.0s | 0.0 | 100.0 | 33.5 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | cursor-cli | dx_stream_cascaded | cursor-auto ⚠ | ❓ UNKN | 0.0 | 74.6 |  | 1 | 0.0s | 0.0 | 100.0 | 34.9 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | cursor-cli | runtime | cursor-auto ⚠ | ❓ UNKN | 0.0 | 61.7 |  | 1 | 0.0s | 0.0 | 100.0 | 32.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | cursor-cli | suite | cursor-auto ⚠ | ❓ UNKN | 0.0 | 86.5 |  | 1 | 0.0s | 0.0 | 100.0 | 37.3 | ✗/✗ | 0 | 0 | 0 | 0 | no output directory linked |
| 20 | opencode-cli | compiler | 4.6 | ✅ PASS | 85.0 | 75.6 |  | 0 | 38.0m | 100.0 | 85.0 | 87.6 | ✓/✓ | 39 | 512 | 0 | 4 | .dxnn + config.json present |
| 20 | opencode-cli | dx_app | 4.6 | ✅ PASS | 25.0 | 73.5 |  | 0 | 3.6m | 100.0 | 100.0 | 72.2 | ✓/✓ | 39 | 249 | 0 | 0 | factory + sync runner (yolo26n_sync.py) |
| 20 | opencode-cli | dx_stream | 4.6 | ✅ PASS | 35.0 | 74.7 | ⏱ | 0 | 4.3m | 100.0 | 100.0 | 75.4 | ✓/✓ | 48 | 443 | 0 | 0 | pipeline.py + run script |
| 20 | opencode-cli | dx_stream_cascaded | 4.6 | ✅ PASS | 35.0 | 68.5 |  | 0 | 4.2m | 100.0 | 100.0 | 74.2 | ✓/✓ | 40 | 206 | 0 | 0 | pipeline.py + run script |
| 20 | opencode-cli | runtime | 4.6 | ✅ PASS | 60.0 | 59.5 | ⏱ | 0 | 15.9m | 100.0 | 85.0 | 76.9 | ✓/✓ | 11 | 1816 | 0 | 3 | 6 sub-project output(s) well-formed |
| 20 | opencode-cli | suite | 4.6 | ❓ UNKN | 0.0 | 63.6 |  | 0 | 0.0s | 40.0 | 100.0 | 44.7 | ✓/✓ | 0 | 0 | 0 | 0 | no output directory linked |
| 21 | copilot-cli | runtime | 4.6 | ✅ PASS | 20.0 | 48.9 |  | 0 | 5.5m | 83.3 | 100.0 | 60.8 | ✓/✓ | 62 | 441 | 0 | 0 | 2 sub-project output(s) well-formed |
| 21 | copilot-cli | suite | 4.6 | ✅ PASS | 55.0 | 56.1 |  | 0 | 16.2m | 100.0 | 95.0 | 76.7 | ✓/✓ | 88 | 360 | 0 | 1 | dual session dirs (compiler+app) with primary deliverables |


====================

Emit the full markdown content of `insights.md` now (inline; no file writes).
