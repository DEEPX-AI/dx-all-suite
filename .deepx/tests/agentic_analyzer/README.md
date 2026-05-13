# dx-agentic-dev E2E Analyzer

> 재사용 가능한 분석 도구 — `dx-agentic-dev/e2e-tests/results/` 의 autopilot 테스트 결과를
> **도구 × 회차 × 시나리오** 차원으로 평가하고, HARD GATE 준수도/코드 품질/소요 시간/실패율을
> 종합 리포트로 산출합니다.

---

## 1. Quick Start

### 1.1 정적 분석 (analyze.py)

```bash
cd .deepx/tests/agentic_analyzer

# 모든 회차 일괄 분석 (기본: ../results)
python3 analyze.py

# 특정 도구/회차/시나리오만
python3 analyze.py --tool claude-code copilot-cli --round 1 2 3 --scenario compiler dx_app

# 다른 results 위치
python3 analyze.py --results-root /path/to/results --output-dir ./reports/custom-run
```

산출물 (기본 위치 `<suite-root>/dx-agentic-dev/e2e-tests/analyzer_reports/<UTC-timestamp>/`):
- `analysis.md` — 마크다운 리포트 (사람이 읽는 메인 산출물)
- `analysis.json` — 머신 판독용 전체 데이터
- `per_session.csv` — 스프레드시트용 flat 표

> **입출력 디렉토리**: 도구 코드는 `.deepx/tests/agentic_analyzer/`(git tracked) 에,
> 입력(results) + 출력(analyzer_reports) 은 `dx-agentic-dev/e2e-tests/` (gitignored) 에 위치.
> 도구는 모든 클론에 배포되고, 런타임 데이터는 로컬에 격리됨.

### 1.2 Agentic 인사이트 도출 (insights.py)

분석 리포트(analysis.md)를 추가로 LLM agent 에게 넘겨 도구별 강점/약점 분석 또는 end-user runnability 판정을 받습니다.

```bash
# 도구별 강점/약점 인사이트 도출 (Korean markdown)
python3 insights.py --mode insights --report-dir reports/<TS>/ --cli claude

# 산출물 8개 sample 의 end-user 실행 가능성 판정
python3 insights.py --mode runnability --report-dir reports/<TS>/ --cli copilot --sample 8

# 지원 CLI agents: claude / codex / copilot / cursor / opencode
# CLI 미설치 시 prompt 파일만 저장 → 수동 실행 가능
```

산출물:
- `insights_prompt.md` — agent에 전달할 prompt (CLI 실패 시에도 저장됨)
- `insights.md` — agent 응답 결과 (도구별 강점 3개, 약점 3개, 시나리오 추천, 회차 학습 패턴 등)
- `runnability_report.md` — 샘플 세션의 README/setup.sh/run.sh 를 agent 가 직접 읽고 end-user 실행 가능성 평가

## 2. 의존성

- Python 3.10+
- PyYAML (`pip install pyyaml`)
- `bash` (코드 품질 검사용 `bash -n`)

## 3. 분석 차원

### 3.1 메트릭 Tier

| Tier | 검증 항목 | 구현 위치 |
|------|----------|----------|
| **T1 산출물** | 필수 파일 (setup.sh, run.sh, README.md, session.log, factory, *_sync.py, config.json, .dxnn 등) 존재 | `compliance.py` |
| **T2 구문** | Python `py_compile`, JSON parse, Bash `bash -n` | `quality.py` |
| **T3 준수도** | START/DONE sentinel, Session ID 포맷, Output Isolation, IFactory 5-method, suite dual-dir | `compliance.py` |
| **T4 코드 품질** | placeholder 코드(TODO/`np.zeros`/commented imports), 직접 `InferenceEngine.run()` 사용 | `quality.py` |
| **T5 시간** | stream.jsonl 의 `result.duration_ms` (Claude Code/Cursor) 또는 첫/마지막 timestamp delta | `session.py` |
| **T6 Verdict (산출물 PASS)** | 시나리오 1차 산출물 존재성 PASS/PARTIAL/FAIL/UNKNOWN | `functional.py` |
| **T7 ExecutionTrace** | session.log + compile_out.log 등 실제 명령 실행 흔적 + 성공/실패 마커 | `execution.py` |
| **T8 Pytest assertion** | (참고) pytest-json-report 데이터 (있는 경우만; Overall 미반영) | `pytest_data.py` |
| **T9 Bias check** | Cursor auto 모델 편향 점검 (도구간 메트릭 비교 분석) | `bias_check.py` |
| **T10 Agentic insight** | 2차 CLI agent 호출로 도구별 강점/약점 + end-user runnability 판정 | `insights.py` |

### 3.2 집계 차원

- **per tool** (claude-code / copilot-cli / cursor-cli / opencode-cli / codex-cli)
- **per round** (1-N — 라운드 추가 시 자동 확장)
- **per scenario** (compiler / dx_app / dx_stream / dx_stream_cascaded / runtime / suite)
- **per model** (config.yaml 의 model overrides 매핑 — Cursor "auto" 같은 비표준 케이스 식별)

### 3.3 점수 계산식

```
Compliance %   = (통과 체크 수 / 전체 체크 수) × 100
Quality %      = syntax_pct - 5 × placeholder_hits - 5 × direct_engine_use (페널티 cap 적용)
Runnability %  = 0.4×verdict(PASS=100/PARTIAL=50/FAIL=0) + 0.2×README(1-5→0-100) + 0.2×Setup(1-5→0-100) + 0.15×Run(1-5→0-100) + 0.05×Verification(Y=100/N=0)
Overall %      = 0.25·Compliance + 0.20·Quality + 0.10·Verdict + 0.25·ExecutionTrace + 0.15·Runnability + 2.5(START) + 2.5(DONE)
```

> **Runnability 데이터가 없는 세션**: 나머지 4-factor를 비례 배분 (backward compatible).
> **Verdict 가중치 10%**: 파일 존재만 확인하므로 가중치 낮음. Execution(25%)과 Runnability(15%)에 더 높은 비중.

## 4. 디렉토리 구조

```
analyzer/
├── README.md                # 이 문서
├── analyze.py               # 메인 CLI 진입점 — 정적 분석 + 리포트 생성
├── insights.py              # 2차 agentic CLI 호출 — 도구별 강점/약점 + 산출물 runnability
├── config.yaml              # 도구/시나리오/모델/룰 정의 (코드 수정 없이 확장)
├── lib/
│   ├── discover.py          # results/ 스캔 → ResultDir + ScenarioRef 생성, 회차 grouping
│   ├── session.py           # session.md + stream.jsonl 파싱 (sentinel, model, duration, tokens, tool calls)
│   ├── compliance.py        # HARD GATE 체크 (sentinel, isolation, factory methods, suite dual-dir)
│   ├── quality.py           # 정적 코드 품질 (py_compile, JSON parse, bash -n, regex 안티패턴)
│   ├── functional.py        # Verdict 추론 (PASS/PARTIAL/FAIL) + LOC 카운트
│   ├── execution.py         # ExecutionTrace — session.log + compile_out.log 실행 흔적 분석
│   ├── runnability_parser.py # Runnability report 파싱 → 세션별 정량 점수 추출
│   ├── pytest_data.py       # pytest assertion 데이터 (있다면 json-report 파싱)
│   ├── bias_check.py        # Cursor auto 모델 편향 점검 (도구간 메트릭 비교)
│   ├── aggregate.py         # SessionEval + per-tool/round/scenario 집계 + stdev
│   └── report.py            # MD + JSON + CSV 출력
└── reports/<timestamp>/     # 출력 (gitignore 권장)
    ├── analysis.md
    ├── analysis.json
    ├── per_session.csv
    ├── insights_prompt.md       # (insights mode) agent에 줄 프롬프트
    ├── insights.md              # (insights mode) agent 응답 (자동/수동)
    ├── runnability_report.md    # (runnability mode) sample 세션 end-user 실행 가능성 판정
    └── comprehensive_report.md  # analysis + insights + runnability 통합 보고서
```

## 5. 새로운 도구/모델 추가

코드 수정 **없이** `config.yaml` 만 갱신하면 됩니다.

### 5.1 신규 도구 (예: OpenAI Codex CLI)

```yaml
tools:
  codex-cli:                       # ← 새 항목 추가
    dir_suffix: "codex-cli-autopilot"
    artifact_prefix: "codex_cli"
    binary: "codex"
    notes: "OpenAI Codex CLI"
```

전제조건:
- result 디렉토리 명명: `<timestamp>_<hash>_codex-cli-autopilot`
- manifest.json artifacts 키 접두: `codex_cli__<scenario>`
- 시나리오 디렉토리에 `<scenario>-codex-session.md` + `*-stream.jsonl` 또는 `*-events-*.jsonl`

### 5.2 모델 매핑 변경

```yaml
default_models:
  codex-cli: "gpt-5.3-codex"

model_overrides:
  - session_id_pattern: "20260601_"     # 특정 날짜 이후 세션은 다른 모델
    model: "gpt-5.4-codex"
    note: "GPT-5.4 codex rollout starting Jun 1"
```

### 5.3 새 시나리오 추가

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

## 6. 누적 분석 (R1~R10)

라운드 카운팅은 **자동**입니다. 추가 라운드 결과가 `results/` 에 들어가면 timestamp 순으로
정렬되어 다음 라운드 번호가 할당됩니다.

```bash
# R1~R5 완료 후 R6~R10 추가 실행 → 동일 명령으로 누적 분석
python3 analyze.py

# 라운드 N개만 비교
python3 analyze.py --round 1 2 3 4 5    # 초기 5 라운드
python3 analyze.py --round 6 7 8 9 10   # 추가 5 라운드
# (라운드 그룹 차이 평가)
```

## 7. 알려진 한계 / 향후 개선

| 한계 | 현재 상태 / 향후 |
|------|------|
| **functional verification 없음** — `verify.py` 가 실제 NPU에서 통과하는지는 정적 검사만 | **개선 적용**: Verdict 컬럼 (PASS/PARTIAL/FAIL/UNKNOWN) — 1차 산출물 존재성으로 시나리오별 추론. NPU 실행 결과 수집은 별도 옵션으로 추가 가능 |
| **token 카운트** — Claude Code 만 정확 | 다른 도구의 stream 포맷에 토큰 메타데이터 부재 (도구 자체 한계). 현 상태에서 표시는 함 |
| **시나리오별 가중치 동일** — compiler vs dx_app 난이도 차이 | 명시적 정보로 제공 (시나리오별 Verdict 분리 표 + duration). config 에서 weight 활성화 가능 |
| **시각화 없음** | 향후 옵션 — 표가 콘솔/MD에서 충분히 읽힘 |
| **드릴다운** | **개선 적용**: §6 Round × Scenario × Tool Verdict 매트릭스 + §7 per-session 상세 표 |
| **회차 일관성** | **개선 적용**: σ(Overall) / σ(Duration) — stdev 컬럼 추가 (Q4 follow-up) |
| **시나리오별 pass/fail** | **개선 적용**: Verdict 추론 (Q1 follow-up) — pytest의 round-level exit code 외에 시나리오별 PASS/PARTIAL/FAIL/UNKNOWN 도출 |

## 8. 메서드 — 어떻게 점수 매겼나

### Compliance (HARD GATE 체크)

체크 항목 (시나리오 따라 가변; 최대 ~7개):

1. `sentinel_start` — 응답 첫 줄에 `[DX-AGENTIC-DEV: START]`
2. `sentinel_done` — 마지막 줄에 `[DX-AGENTIC-DEV: DONE (output-dir: ...)]`
3. `output_isolation_present` — 산출물이 `dx-agentic-dev/<session_id>/` 하위
4. `session_id_format` — `YYYYMMDD-HHMMSS_<agent>_<model>_<task>` 패턴
5. `mandatory_deliverables` — 시나리오별 필수 파일 모두 존재
6. `ifactory_5_methods` — dx_app/runtime/suite 의 factory가 5-method 패턴 준수
7. `session_log_authentic` — session.log 가 hand-written heredoc 이 아닌 실 명령 출력
8. `suite_dual_session_dirs` — suite 시나리오에서 2개 별도 sub-project dir 생성

### Quality (정적 코드 품질)

- 모든 `.py` 파일에 `py_compile` 적용 → 통과율
- 모든 `.json` 파일에 `json.load` 적용 → 통과율
- 모든 `.sh` 파일에 `bash -n` 적용 → 통과율
- **Placeholder hits** (페널티): `# TODO: implement`, 주석 처리된 `dx_engine`/`dxnn_sdk` import, `result = np.zeros(...)` 등
- **Direct engine use** (페널티): factory 외부에서 `engine.run()` / `engine.run_async()` 호출 (HARD GATE 위반)
- 페널티: hit 당 5점 차감, cap 30점 (placeholder), cap 15점 (engine)

### Verdict (시나리오 1차 산출물 추론)

```
Verdict = PASS(100) / PARTIAL(50) / FAIL(0) / UNKNOWN(0)
```

- `compiler` PASS = `.dxnn` + `config.json` / FAIL = `.dxnn` 미생성
- `dx_app` PASS = factory + `*_sync.py` 둘 다 / PARTIAL = factory 만
- `dx_stream` PASS = `pipeline.py` + `run_*.sh` / PARTIAL = pipeline 만
- `runtime` PASS = sub-project 출력 중 하나 이상 형식 통과
- `suite` PASS = dx-compiler + dx_app 둘 다 자체 dir (R41 HARD GATE)

### Overall (composite)

```
Overall = 0.40 × Compliance% + 0.30 × Quality% + 0.25 × Verdict% + 2.5(START) + 2.5(DONE)
```

- 100점 만점 cap
- 40:30:25 가중치 — 준수도 > 코드 품질 > Verdict (HARD GATE 가 가장 중요)
- sentinel 보너스 5점 — 자동 테스트 인프라가 의존하는 마커
- **pytest exit_status 는 Overall 미포함** — 라운드 단위 (한 라운드 6 시나리오 중 어느 assertion 하나라도 실패 시 1) 라 시나리오 단위 점수로 분해 불가

## 9. 예시 인사이트 (현재 5 라운드 기준)

- **claude-code 가 종합 1위** (98.7%) — sentinel 100%, 큰 placeholder 위반 없음
- **opencode-cli 가 종합 최저** (69.2%) — **sentinel 0%** (START/DONE 미출력) 이 주요 원인
- **cursor-cli 평균 점수 높음**(97.9%) 이지만 ⚠ "auto" 모델 사용 — Sonnet 4.6 으로 재실행 필요
- **copilot-cli 가 Exit 0 비율 1위** (80%) — 가장 안정적
- **runtime/suite 시나리오는 모든 도구에서 점수 낮음** — cross-project 라우팅 + suite dual-dir 게이트가 가장 어려움

## 10. 라이선스/소유권

내부 도구. dx-all-suite 의 `dx-agentic-dev` 인프라에 속함. 본 디렉토리는 dx-agentic-dev/
의 일부로서 dx-all-suite repo 의 `.gitignore` 정책을 따릅니다.
