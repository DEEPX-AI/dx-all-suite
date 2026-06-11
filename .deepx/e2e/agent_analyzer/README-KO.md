# dx-agent-dev E2E Analyzer

> 재사용 가능한 분석 도구 — `dx-agent-dev/e2e-tests/results/` 의 autopilot 테스트 결과를
> **도구 × 회차 × 시나리오** 차원으로 평가하고, HARD GATE 준수도 / 코드 품질 / 실행 흔적 /
> runnability / 토큰 비용 / 종합 점수를 산출합니다.

---

## 1. Quick Start

### 1.1 정적 분석 (analyze.py)

```bash
cd .deepx/e2e/agent_analyzer

# 모든 회차 일괄 분석 (기본: ../results)
python3 analyze.py

# 특정 도구/회차/시나리오만
python3 analyze.py --tool claude-code copilot-cli --round 1 2 3 --scenario compiler dx_app

# 다른 results 위치
python3 analyze.py --results-root /path/to/results --output-dir ./reports/custom-run

# Runnability 평가 건너뛰기 (빠름 — 기존 runnability_report.md 재사용)
python3 analyze.py --no-insights-runnability

# Insights CLI agent / 모델 지정 (paid fallback — copilot은 점 형식 id 사용)
python3 analyze.py --insights copilot --insights-model claude-sonnet-4.6 --insights-allow-paid
```

산출물 (기본 위치 `<suite-root>/dx-agent-dev/e2e-tests/analyzer_reports/<timestamp>/`):
- `analysis.md` — 마크다운 리포트 (사람이 읽는 메인 산출물)
- `analysis.html` — analysis.md의 HTML 버전
- `analysis.json` — 머신 판독용 전체 데이터
- `per_session.csv` — 스프레드시트용 flat 표
- `comprehensive_report.md` — 통합 보고서 (analysis + insights + runnability)
- `comprehensive_report.html` — 통합 보고서 HTML 버전 (Chart.js 인터랙티브 차트 포함 — Executive Summary + 시각 비교)
- `dashboard.html` — 독립 실행형 인터랙티브 대시보드 (Chart.js — 종합 순위, 레이더, 라운드 추이, 시나리오 비교)

> **입출력 디렉토리**: 도구 코드는 `.deepx/e2e/agent_analyzer/` (git tracked)에,
> 입력(results) + 출력(analyzer_reports)은 `dx-agent-dev/e2e-tests/` (gitignored)에 위치.
> 도구는 모든 클론에 배포되고, 런타임 데이터는 로컬에 격리됩니다.

### 1.2 Agent-Driven 인사이트 도출 (insights.py)

분석 리포트(analysis.md)를 LLM agent에게 넘겨 도구별 강점/약점 분석 또는 end-user
runnability 판정을 받습니다.

```bash
# 도구별 강점/약점 인사이트 도출 (Korean markdown)
python3 insights.py --mode insights --report-dir reports/<TS>/ --cli claude

# 산출물 8개 sample의 end-user 실행 가능성 판정
python3 insights.py --mode runnability --report-dir reports/<TS>/ --cli copilot --sample 8

# 전수 runnability 평가 (모든 세션)
python3 insights.py --mode runnability --report-dir reports/<TS>/ --cli copilot --all

# 지원 CLI agents: claude / codex / copilot / cursor / opencode
# CLI 미설치 시 prompt 파일만 저장 → 수동 실행 가능
```

산출물:
- `insights_prompt.md` — agent에 전달할 prompt (CLI 실패 시에도 저장됨)
- `insights.md` — agent 응답 결과 (도구별 강점 3개, 약점 3개, 시나리오 추천, 회차 학습 패턴 등)
- `runnability_report.md` — 샘플 세션의 README/setup.sh/run.sh를 agent가 직접 읽고 end-user 실행 가능성 평가

### 1.3 가설 생성 (insights.py)

외부 benchmark(SWE-Bench, Aider, Artificial Analysis, EvalPlus)를 바탕으로
pre-experiment hypotheses를 생성하기 위해, 구조화된 prompt와 함께 LLM을 호출합니다.

```bash
# 기본 prompt template로 hypothesis.json 생성
python3 insights.py --mode hypothesis --report-dir reports/<TS>/ --cli copilot \
    --prompt prompts/hypothesis_prompt.md

# 미리 만들어 둔 hypothesis.json 직접 사용 (LLM 호출 없음)
python3 insights.py --mode hypothesis --report-dir reports/<TS>/ \
    --prompt my_hypothesis.json

# analyze.py 경유 (통합 pipeline — Stage 4.5)
python3 analyze.py --hypothesis prompts/hypothesis_prompt.md
```

산출물:
- `hypothesis.json` — benchmark reference가 포함된 구조화된 hypotheses

리포트 디렉토리에 `hypothesis.json`이 있으면:
- `comprehensive_report.md`의 **§0 실험 설계**가 purpose, benchmarks, hypotheses로 보강됩니다
- `insights.md`에 predictions vs actual data를 비교하는 **§8 가설 검증**이 추가됩니다
- `dashboard.html`에 **Hypothesis vs Actual chart**가 표시됩니다

### 1.4 CLI 플래그 참조

| 플래그 | 기본값 | 설명 |
|--------|--------|------|
| `--results-root` | `dx-agent-dev/e2e-tests/results` | results 디렉토리 경로 |
| `--config` | `./config.yaml` | 설정 파일 경로 |
| `--output-dir` | `<reports_base>/<timestamp>/` | 리포트 출력 디렉토리 |
| `--tool` | 전체 | 도구 필터 (반복 가능) |
| `--scenario` | 전체 | 시나리오 필터 (반복 가능) |
| `--round` | 전체 | 라운드 번호 필터 (반복 가능) |
| `--insights` | `auto` | Insights CLI agent: `off`, `auto`, `copilot`, `claude`, `cursor`, `opencode`, `codex` |
| `--no-insights-runnability` | (활성) | Runnability 평가 건너뛰기 |
| `--insights-model` | CLI 기본 | Insights agent 모델 override |
| `--insights-allow-paid` / `--no-insights-allow-paid` | mode별 상이 | 유료 모델 허용/차단. 기본값은 mode별로 다름: runnability=free, insights/hypothesis=paid. `--insights-model`로 유료 모델 지정 시 필수. |
| `--hypothesis` | 없음 | hypothesis prompt(.md) 또는 pre-built(.json) 경로. LLM으로 hypothesis.json을 생성하고 리포트에 §0/§8을 추가 |
| `--existing-runnability` | 없음 | 기존 `runnability_report.md` 경로 (incremental 평가용) |

### 1.5 비교 리포트 (build_comparison.py)

두 분석 리포트 디렉토리 간 side-by-side 비교 페이지를 생성합니다
(예: non-thinking vs thinking 모드, baseline vs 실험 조건):

```bash
python3 build_comparison.py \
  --non-thinking-dir <NT_리포트_dir> \
  --thinking-dir <TH_리포트_dir> \
  --non-thinking-run-id <NT_run_id> \
  --thinking-run-id <TH_run_id> \
  --output <출력_dir>/comparison.html
```

입력: 각각 `per_session.csv` + `comprehensive_report.html`를 포함하는 두 분석 리포트 디렉토리.

출력: 단일 HTML 페이지
- 도구별 집계 delta 표 (5개 metric: Compliance, Quality, ExecutionTrace, Runnability, Overall — 값 + 색상 Δ)
- (도구 × 시나리오)별 delta 표 (5도구 × 6시나리오 = 30행)
- 두 원본 `comprehensive_report.html`을 side-by-side iframe 으로 표시

LLM 호출 없음 — CSV 단순 집계만. 프롬프트/설정 변경, thinking 모드 토글,
하네스 fix 영향을 시각적으로 비교할 때 적합.

## 2. 파이프라인 단계 — `analyze.py` 실행 흐름

`python3 analyze.py` 실행 시 다음 단계가 순서대로 처리됩니다:

```
┌─────────────────────────────────────────────────────────────────────┐
│                        analyze.py Pipeline                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Stage 1: Discovery (탐색)                                          │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ discover.py: results/ 디렉토리 스캔                    │            │
│  │  → ResultDir (도구×라운드) + ScenarioRef (시나리오별)     │            │
│  │  → timestamp 정렬로 라운드 번호 자동 부여                │            │
│  │  → JSONL 파일 매칭 (도구별 패턴)                        │            │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 2: 세션별 평가 (각 ScenarioRef 대상)                         │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ 2a. session.py: transcript + JSONL 파싱               │            │
│  │     → sentinel 탐지, 모델, 소요시간, 토큰,              │            │
│  │       tool calls, premium requests                   │            │
│  │ 2b. compliance.py: HARD GATE 체크                     │            │
│  │     → sentinel, isolation, session ID, factory,      │            │
│  │       필수 파일, suite dual-dir                        │            │
│  │ 2c. quality.py: 정적 코드 품질                         │            │
│  │     → py_compile, json parse, bash -n,               │            │
│  │       placeholder/direct-engine 페널티                 │            │
│  │ 2d. functional.py: Verdict 추론                        │            │
│  │     → 시나리오별 PASS/PARTIAL/FAIL/UNKNOWN              │            │
│  │ 2e. execution.py: 실행 흔적 분석                        │            │
│  │     → session.log + compile_out.log 증거 확인           │            │
│  │                                                       │            │
│  │ ⇒ composite_score() → Overall (4-factor, Runn 미포함)  │            │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 3: 비용 추정 (post-pass)                                     │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ cost.py: 도구간 calibration                           │            │
│  │  → copilot-cli의 tokens/premium 비율 → opencode/codex │            │
│  │    premium 수 추정                                     │            │
│  │  → 토큰 × pricing table → 추정 USD                     │            │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 4: 리포트 생성                                               │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ report.py: 출력 파일 작성                              │            │
│  │  → analysis.md + analysis.html                        │  ← (A)   │
│  │  → analysis.json                                      │  ← (B)   │
│  │  → per_session.csv                                    │  ← (C)   │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 4.5: 가설 생성 (선택)                                   │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ insights.py --mode hypothesis (if --hypothesis)      │            │
│  │  → LLM이 benchmark 기반 hypotheses 생성              │            │
│  │  → hypothesis.json                                   │  ← (A½)   │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 5: Runnability 평가 (기본 활성, --no-insights-runnability로 생략 가능) │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ insights.py --mode runnability                        │            │
│  │  → LLM agent가 세션 README/setup.sh/run.sh 읽고 평가  │            │
│  │  → 점수: Verdict, README, Setup, Run, Verification    │            │
│  │  → runnability_report.md                              │  ← (D)   │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 6: Runnability 병합 (Stage 4 산출물 재작성)                  │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ runnability_parser.py: runnability 점수 파싱           │            │
│  │  → SessionEval.runnability_score에 병합                │            │
│  │  → Overall 재계산 (5-factor, Runnability 포함)         │            │
│  │  → analysis.md/html/json/csv 재작성                   │  ← (A')  │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 7: 정성 인사이트                                             │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ insights.py --mode insights                           │            │
│  │  → LLM agent가 업데이트된 analysis.md 읽음 (Runn 포함) │            │
│  │  → 도구별 강점/약점, 추천사항                           │            │
│  │  → insights.md                                        │  ← (E)   │
│  └─────────────────────────────────────────────────────┘            │
│          ↓                                                          │
│  Stage 8: 종합 보고서 조립                                          │
│  ┌─────────────────────────────────────────────────────┐            │
│  │ Part 0: 실험 설계 (experiment design — 항상 표시;      │            │
│  │         hypothesis가 있으면 보강됨)                    │            │
│  │ Part 1: Executive Summary (정렬된 도구별 순위)         │            │
│  │ Part 2: analysis.md (정량)                            │            │
│  │ Part 3: insights.md (정성, hyp 있으면 §8 gap 포함)    │            │
│  │ Part 4: runnability 요약 (간략)                        │            │
│  │  → comprehensive_report.md                            │  ← (F)   │
│  │  → comprehensive_report.html (Chart.js 차트 포함)     │  ← (G)   │
│  │  → dashboard.html (독립 인터랙티브 대시보드)           │  ← (H)   │
│  └─────────────────────────────────────────────────────┘            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 단계별 산출물 요약

| 단계 | 산출물 | 설명 |
|------|--------|------|
| 4 (A) | `analysis.md` / `analysis.html` | 메인 정량 리포트 — 도구/라운드/시나리오별 표, Overall 점수 |
| 4 (B) | `analysis.json` | 머신 판독용 전체 평가 데이터 |
| 4 (C) | `per_session.csv` | 스프레드시트 import용 flat 표 |
| 4.5 (A½) | `hypothesis.json` | 외부 benchmark 기반 pre-experiment hypotheses (선택 — `--hypothesis` 필요) |
| 5 (D) | `runnability_report.md` | LLM agent의 세션별 end-user 실행 가능성 평가 |
| 6 (A') | `analysis.md` (재작성) | Runnability 점수가 Overall에 반영된 업데이트 버전 |
| 7 (E) | `insights.md` | LLM agent의 정성 분석 (업데이트된 analysis.md 기반) |
| 8 (F) | `comprehensive_report.md` | 통합 보고서 — 실험 설계 + Executive Summary + Part 1+2+3+4 |
| 8 (G) | `comprehensive_report.html` | Chart.js 인터랙티브 차트 내장 HTML (bar, radar, trend, sentinel) |
| 8 (H) | `dashboard.html` | 독립 실행형 인터랙티브 대시보드 (Chart.js — 6종 차트, 정렬 가능 순위표) |

> **파이프라인 순서가 중요합니다**: Runnability (Stage 5)가 insights (Stage 7)보다 먼저
> 실행되어야 insights.md의 정성 분석이 Runnability가 반영된 최신 Overall 점수를 기반으로
> 작성됩니다.
>
> **Stage 5와 Stage 6의 독립성**: Stage 6 (병합)은 출력 디렉토리에
> `runnability_report.md` 파일이 존재하는지만 확인합니다 — 현재 실행에서
> Stage 5가 생성했는지 여부는 체크하지 않습니다. 따라서 다음이 가능합니다:
> 1. `--no-insights-runnability`로 Stage 5 생략
> 2. 이전 실행의 `runnability_report.md`를 출력 디렉토리에 복사
> 3. analyzer 재실행 — Stage 6이 기존 파일을 파싱하여 병합
>
> 이 방식은 비용이 큰 runnability 평가를 리포트 재생성 시 재사용할 때 유용합니다.
>
> **건너뛰기 플래그**: `--no-insights-runnability`는 Stage 5만 건너뜁니다
> (`runnability_report.md`가 존재하면 Stage 6은 실행됨).
> `--insights off`는 Stage 5–7 전체를 건너뜁니다 (리포트만, LLM 호출 없음).
>
> **Incremental runnability** (`--existing-runnability` / `--existing-report`):
> 기존 데이터셋에 새 라운드를 추가할 때 (예: 10라운드 리포트에 11-20라운드 추가),
> 이전 `runnability_report.md`를 지정하면 이미 평가된 세션을 건너뜁니다:
> ```bash
> # analyze.py 경유 (전체 pipeline — 권장; --insights 기본값은 cursor)
> python3 analyze.py results/ --insights cursor \
>     --existing-runnability path/to/old/runnability_report.md
>
> # insights.py 직접 실행
> python3 insights.py --mode runnability --report-dir reports/<ts>/ \
>     --existing-report path/to/old/runnability_report.md
> ```
> 기존 리포트를 파싱하여 유효한 평가(PASS/PARTIAL/FAIL verdict)가 있는 세션을
> 건너뛰고, 새로운 결과와 기존 결과를 병합하여 출력합니다.
> 세션 수는 `{기존 재사용} + {신규 평가}` 합계로 표시됩니다.

## 3. 의존성

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- `bash` (코드 품질 검사용 `bash -n`)

### unit-test 스위트 실행

analyzer unit test는 모두 `tests/` 아래에 있으며 `pytest.ini`(`testpaths = tests`)로
배선되어 있습니다. 전체 스위트 실행:

```bash
cd .deepx/e2e/agent_analyzer && pytest        # tests/ 자동 탐색
# 또는 어디서든:
python -m pytest .deepx/e2e/agent_analyzer/tests/ -q
```

## 4. 기본 모델 정책

analyzer는 비용과 품질의 균형을 위해 stage별로 서로 다른 기본 모델 정책을 사용합니다:

| Stage | 기본 CLI + Model | 비용 | 이유 |
|-------|-------------------|------|------|
| Runnability (Stage 5) | **cursor + `auto`** | free (구독) | 세션당 짧은 호출 1회 |
| Insights (Stage 7) | **cursor + `auto`** | free | 단일 거대 프롬프트 |
| Hypothesis (Stage 4.5) | **cursor + `auto`** | free | 단일 거대 프롬프트 |

> **모델 정책 (2026-06):** 기본값은 3개 stage 모두 **cursor + `auto`** (Composer, 구독→free) — 현재
> `--insights` 기본값. free vs paid 비교 결과 cursor `auto` 출력이 paid sonnet에 **뒤지지 않아**
> (§1–8 insights + §8 가설 검증 완비, 핵심 결론 동일) free를 디폴트로 유지.
>
> - **기본(free):** `python analyze.py --run-id ...` → 전 stage cursor `auto`. ⚠ cursor runnability는
>   ~24s/call(120세션이면 느림) + 가끔 timeout — `--existing-runnability <prev>/runnability_report.md`로
>   기존 평가 재사용 권장.
> - **Paid fallback** (cursor 불가/최대 상세 필요 시): runnability → claude-code + `claude-sonnet-4-6`
>   (하이픈; 작은 호출 다수 OK); insights/hypothesis → copilot + `claude-sonnet-4.6` (점). 단일 명령:
>   `--insights copilot --insights-model claude-sonnet-4.6 --insights-allow-paid`.
>   (claude-code `-p`는 거대 insights 프롬프트에서 **timeout(>900s)** → 거기엔 안 씀.)
>
> 참고 / gotcha:
> - `invoke_cli`가 이제 시스템 **CA bundle** env(`NODE_EXTRA_CA_CERTS` + `--use-system-ca`)와
>   `stdin=DEVNULL`을 직접 세팅 → 호출자가 env를 export하지 않아도 node CLI(cursor/copilot/opencode)가
>   headless 동작. (이전엔 cursor가 TLS로 `Connection lost, reconnecting` 실패.)
> - copilot `gpt-4.1`(구 free default)은 **deprecated** — `Model "gpt-4.1" ... is not available`.
> - cursor 모델 id = `auto`(`agent --list-models`에 노출되는 유일 id); claude CLI는 하이픈
>   (`claude-sonnet-4-6`), copilot은 점(`claude-sonnet-4.6`). 형식 불일치 시 거부됨.

`analyze.py`에서는 `--insights <cli>` + `--insights-model <model>`로 CLI/모델을,
`--insights-allow-paid` / `--no-insights-allow-paid`로 paid 여부를 override할 수 있습니다
(`insights.py`에서는 `--allow-paid` / `--no-allow-paid`).

## 5. 분석 차원

### 5.1 메트릭 Tier

| Tier | 검증 항목 | 구현 위치 |
|------|----------|----------|
| **T1 산출물** | 필수 파일 (setup.sh, run.sh, README.md, session.log, factory, *_sync.py, config.json, .dxnn 등) 존재 | `compliance.py` |
| **T2 구문** | Python `py_compile`, JSON parse, Bash `bash -n` | `quality.py` |
| **T3 준수도** | START/DONE sentinel, Session ID 포맷, Output Isolation, IFactory 5-method, suite dual-dir | `compliance.py` |
| **T4 코드 품질** | placeholder 코드(TODO/`np.zeros`/commented imports), 직접 `InferenceEngine.run()` 사용 | `quality.py` |
| **T5 시간** | stream.jsonl의 `result.duration_ms` (Claude Code/Cursor) 또는 첫/마지막 timestamp delta | `session.py` |
| **T6 Verdict (산출물 PASS)** | 시나리오 1차 산출물 존재성 PASS/PARTIAL/FAIL/UNKNOWN | `functional.py` |
| **T7 ExecutionTrace** | session.log + compile_out.log 등 실제 명령 실행 흔적 + 성공/실패 마커 | `execution.py` |
| **T9 Bias check** | Cursor auto 모델 편향 점검 (도구간 메트릭 비교 분석) | `bias_check.py` |
| **T10 Agent-Driven insight** | 2차 CLI agent 호출로 도구별 강점/약점 + end-user runnability 판정 | `insights.py` |
| **T11 비용** | 토큰 사용량 → 추정 USD 비용 + premium request calibration 기반 추정 | `cost.py` |

### 5.2 집계 차원

- **per tool** (claude-code / copilot-cli / cursor-cli / opencode-cli / codex-cli)
- **per round** (1–N — 라운드 추가 시 자동 확장)
- **per scenario** (compiler / dx_app / dx_stream / dx_stream_cascaded / runtime / suite)
- **per model** (config.yaml의 model overrides 매핑 — Cursor "auto" 같은 비표준 케이스 식별)

### 5.3 점수 계산식

```
Compliance %   = (통과 체크 수 / 전체 체크 수) × 100
Quality %      = syntax_pct − 5 × placeholder_hits − 5 × direct_engine_use (페널티 cap 적용)
Runnability %  = 0.4×Verdict(PASS=100/PARTIAL=50/FAIL=0)
               + 0.2×README(1–5 → 0–100) + 0.2×Setup(1–5 → 0–100)
               + 0.15×Run(1–5 → 0–100) + 0.05×Verification(Y=100/N=0)
Overall %      = 0.25·Compliance + 0.20·Quality + 0.10·Verdict
               + 0.25·ExecutionTrace + 0.15·Runnability
               + 2.5(START) + 2.5(DONE)
```

> **Runnability 데이터가 없는 세션**: 나머지 4-factor를 비례 배분 (backward compatible).
>
> **Verdict 가중치 10%**: 파일 존재만 확인하므로 가중치 낮음. Execution(25%)과 Runnability(15%)에 더 높은 비중.

## 6. 디렉토리 구조

```
agent_analyzer/
├── README.md                 # 영문 버전
├── README-KO.md              # 이 문서 (한국어)
├── analyze.py                # 메인 CLI 진입점 — 정적 분석 + 리포트 생성
├── insights.py               # 2차 agent-driven CLI 호출 — 도구별 강점/약점 + 산출물 runnability
├── config.yaml               # 도구/시나리오/모델/룰 정의 (코드 수정 없이 확장)
├── lib/
│   ├── discover.py           # results/ 스캔 → ResultDir + ScenarioRef 생성, 회차 grouping
│   ├── session.py            # session.md + stream.jsonl 파싱 (sentinel, model, duration, tokens, tool calls)
│   ├── compliance.py         # HARD GATE 체크 (sentinel, isolation, factory methods, suite dual-dir)
│   ├── quality.py            # 정적 코드 품질 (py_compile, JSON parse, bash -n, regex 안티패턴)
│   ├── functional.py         # Verdict 추론 (PASS/PARTIAL/FAIL) + LOC 카운트
│   ├── execution.py          # ExecutionTrace — session.log + compile_out.log 실행 흔적 분석
│   ├── cost.py               # 토큰 → USD 비용 추정 + premium request calibration
│   ├── runnability_parser.py # Runnability report 파싱 → 세션별 정량 점수 추출
│   ├── bias_check.py         # Cursor auto 모델 편향 점검 (도구간 메트릭 비교)
│   ├── aggregate.py          # SessionEval + per-tool/round/scenario 집계 + stdev
│   └── report.py             # MD + HTML + JSON + CSV 출력
└── reports/<timestamp>/      # 출력 (gitignore 권장)
    ├── analysis.md
    ├── analysis.html
    ├── analysis.json
    ├── per_session.csv
    ├── insights_prompt.md
    ├── insights.md
    ├── runnability_report.md
    ├── comprehensive_report.md
    └── comprehensive_report.html
```

## 7. 새로운 도구/모델 추가

코드 수정 **없이** `config.yaml`만 갱신하면 됩니다.

### 7.1 신규 도구 (예: OpenAI Codex CLI)

```yaml
tools:
  codex-cli:
    dir_suffix: "codex-cli-autopilot"
    artifact_prefix: "codex_cli"
    binary: "codex"
    notes: "OpenAI Codex CLI"
```

전제조건:
- result 디렉토리 명명: `<timestamp>_<hash>_codex-cli-autopilot`
- manifest.json artifacts 키 접두: `codex_cli__<scenario>`
- 시나리오 디렉토리에 `<scenario>-codex-session.md` + `*-stream.jsonl` 또는 `*-events-*.jsonl`

### 7.2 모델 매핑 변경

```yaml
default_models:
  codex-cli: "gpt-5.3-codex"

model_overrides:
  - session_id_pattern: "20260601_"
    model: "gpt-5.4-codex"
    note: "GPT-5.4 codex rollout starting Jun 1"
```

### 7.3 새 시나리오 추가

```yaml
scenarios:
  benchmark:
    description: "Performance benchmark scenario"
    expected_output_dirs: ["dx-runtime/dx_app"]
    mandatory_files:
      - "setup.sh"
      - "run.sh"
      - "benchmark.py"
      - "results.json"
    file_globs:
      - "**/results.json"
```

## 8. 누적 분석

라운드 카운팅은 **자동**입니다. 추가 라운드 결과가 `results/`에 들어가면 timestamp 순으로
정렬되어 다음 라운드 번호가 할당됩니다.

```bash
# R1~R10 완료 후 R11~R15 추가 실행 → 동일 명령으로 누적 분석
python3 analyze.py

# 라운드 그룹 비교
python3 analyze.py --round 1 2 3 4 5      # 초기 5 라운드
python3 analyze.py --round 6 7 8 9 10     # 추가 5 라운드
```

## 9. 도구별 토큰 의미론

각 도구는 토큰 사용량을 다르게 보고합니다. Analyzer는 비용 추정 전에 "fresh input tokens"
(실제 과금 대상)으로 정규화합니다:

| 도구 | `input_tokens` 의미 | 정규화 방법 |
|------|---------------------|-------------|
| **Claude Code** | NEW-only (fresh) | 그대로 사용 |
| **Cursor CLI** | NEW-only (`tokens.input`) | 그대로 사용 |
| **Copilot CLI** | TOTAL (new + cache_read + cache_write) | `raw_input − cache_read − cache_write` |
| **OpenCode** | TOTAL (copilot format) | copilot과 동일 |
| **Codex CLI** | TOTAL (cached 포함) | `max(0, input_tokens − cached_input_tokens)` |

> **Premium request 추정**: Copilot CLI는 `premium_requests`를 직접 보고합니다.
> copilot provider를 사용하는 다른 도구(OpenCode, Codex)는 copilot-cli의 관측된
> `tokens/premium-request` 비율로 calibration하여 추정합니다.

## 10. 메서드 — 어떻게 점수를 매겼나

### Compliance (HARD GATE 체크)

체크 항목 (시나리오에 따라 가변; 최대 ~8개):

1. `sentinel_start` — 응답 첫 줄에 `[DX-AGENT-DEV: START]`
2. `sentinel_done` — 마지막 줄에 `[DX-AGENT-DEV: DONE (output-dir: ...)]`
3. `output_isolation_present` — 산출물이 `dx-agent-dev/<session_id>/` 하위
4. `session_id_format` — `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` 패턴
5. `mandatory_deliverables` — 시나리오별 필수 파일 모두 존재
6. `ifactory_5_methods` — dx_app/runtime/suite의 factory가 5-method 패턴 준수
7. `session_log_authentic` — session.log가 hand-written heredoc이 아닌 실 명령 출력
8. `suite_dual_session_dirs` — suite 시나리오에서 2개 별도 sub-project dir 생성

### Quality (정적 코드 품질)

- 모든 `.py` 파일에 `py_compile` 적용 → 통과율
- 모든 `.json` 파일에 `json.load` 적용 → 통과율
- 모든 `.sh` 파일에 `bash -n` 적용 → 통과율
- **Placeholder hits** (페널티): `# TODO: implement`, 주석 처리된 `dx_engine`/`dxnn_sdk` import, `result = np.zeros(...)` 등
- **Direct engine use** (페널티): factory 외부에서 `engine.run()` / `engine.run_async()` 호출 (HARD GATE 위반)
- 페널티: hit당 5점 차감, cap 30점 (placeholder), cap 15점 (engine)

### Verdict (시나리오 1차 산출물 추론)

```
Verdict = PASS(100) / PARTIAL(50) / FAIL(0) / UNKNOWN(0)
```

- `compiler` PASS = `.dxnn` + `config.json` / FAIL = `.dxnn` 미생성
- `dx_app` PASS = factory + `*_sync.py` 둘 다 / PARTIAL = factory만
- `dx_stream` PASS = `pipeline.py` + `run_*.sh` / PARTIAL = pipeline만
- `runtime` PASS = sub-project 출력 중 하나 이상 형식 통과
- `suite` PASS = dx-compiler + dx_app 둘 다 자체 dir (R41 HARD GATE)

### Overall (composite)

```
Overall = 0.25 × Compliance% + 0.20 × Quality% + 0.10 × Verdict%
        + 0.25 × ExecutionTrace% + 0.15 × Runnability%
        + 2.5(START) + 2.5(DONE)
```

- 100점 만점 cap
- 가중치: Compliance(25%) + Execution(25%) > Quality(20%) > Runnability(15%) > Verdict(10%)
- sentinel 보너스 5점 — 자동 테스트 인프라가 의존하는 마커
- **pytest exit_status는 Overall 미포함** — 라운드 단위 (한 라운드 6 시나리오 중 어느 assertion 하나라도 실패 시 1)라 시나리오 단위 점수로 분해 불가

### 비용 추정

토큰 사용량을 config.yaml의 pricing 테이블로 변환합니다:

- **Anthropic 모델** (Claude Sonnet 4.6): input/output/cache_read/cache_write per-million 단가
- **Copilot premium requests**: request당 USD (Pro tier 기준: $0.033/req)
- **Cross-tool calibration**: copilot-cli의 관측된 `tokens/premium-request` 비율을 직접 보고하지 않는 도구들의 premium request 추정에 사용

## 11. 알려진 한계 / 향후 개선

| 한계 | 현재 상태 |
|------|----------|
| **functional verification 없음** — `verify.py`가 실제 NPU에서 통과하는지는 정적 검사만 | **개선 적용**: Verdict 컬럼 (PASS/PARTIAL/FAIL/UNKNOWN) — 1차 산출물 존재성으로 시나리오별 추론. NPU 실행 결과 수집은 별도 옵션으로 추가 가능 |
| **토큰 카운트** — 도구마다 다른 의미론 | **개선 적용**: 5개 도구 모두 정규화 완료 (fresh tokens 추출). Codex cached 차감 수정. §7 참조 |
| **시나리오별 가중치 동일** — compiler vs dx_app 난이도 차이 | 시나리오별 Verdict 분리 표 + duration으로 명시적 제공. config에서 weight 활성화 가능 |
| **시각화 없음** | 표가 콘솔/MD에서 충분히 읽히며, HTML 리포트가 스타일링된 대안 제공 |
| **드릴다운** | **개선 적용**: Round × Scenario × Tool Verdict 매트릭스 + per-session 상세 표 |
| **회차 일관성** | **개선 적용**: σ(Overall) / σ(Duration) — stdev 컬럼 추가 |
| **시나리오별 pass/fail** | **개선 적용**: Verdict 추론 — pytest round-level exit code 외에 시나리오별 PASS/PARTIAL/FAIL/UNKNOWN 도출 |
| **Codex CLI dual-JSONL** | **개선 적용**: `*-stream.jsonl`과 `*-events-*.jsonl` 패턴 모두 처리 |
| **HTML 리포트** | **개선 적용**: 모든 MD 리포트에 HTML 버전 동시 생성 |

## 12. 라이선스/소유권

내부 도구. dx-all-suite의 `dx-agent-dev` 인프라에 속함. 본 디렉토리는 dx-agent-dev/
의 일부로서 dx-all-suite repo의 `.gitignore` 정책을 따릅니다.
