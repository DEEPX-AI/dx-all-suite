# 프론티어 모델 비교 평가 Runbook (현황 점검본)

> **이 워크트리(`dx-all-suite-frontier-eval`)의 목적**: 신규 프론티어 모델이 출시되었을 때,
> `e2e_runner` (autopilot E2E 실행) + `agent_analyzer` (분석)를 사용해 **기존 프론티어 모델 대비
> 성능을 비교 평가**하고 리포트를 생성한다.
>
> 본 문서는 **코드 변경 없이** 현재 도구만으로 비교 평가를 수행하는 표준 절차와, 그 과정에서
> 알아둬야 할 경로/라벨링 caveat을 정리한 *현황 점검(runbook)* 문서다. (생성기 관리 대상 아님 —
> 독립 문서) 영문판: `reference.md`.
>
> 작성: 2026-06-12 · 기준 코드: `.deepx/e2e/e2e_runner.py`, `.deepx/e2e/agent_analyzer/`

---

## 0. 한눈에 보기 — 비교 평가 1사이클

신규 모델 `NEW` 를 기존 모델 `OLD` 와 비교한다고 하면, 두 도구를 다음 순서로 쓴다.

```
①  e2e_runner.py  (모델 OLD로 N라운드)   →  run_id = RID_OLD
②  e2e_runner.py  (모델 NEW로 N라운드)   →  run_id = RID_NEW
③  analyze.py --run-id RID_OLD           →  리포트 디렉토리 REP_OLD
④  analyze.py --run-id RID_NEW           →  리포트 디렉토리 REP_NEW
⑤  build_comparison.py  REP_OLD vs REP_NEW  →  comparison.html  (side-by-side delta)
```

> 핵심: **"모델 교체"는 run 단위로 한다.** 한 run 안에서 여러 모델을 섞지 않는다 (모델 라벨이
> 섞이고 §6 caveat에 걸린다). 모델 하나당 run 하나 → run_id 하나 → 분석 리포트 하나가 기본형.

---

## 1. 도구 위치

| 도구 | 경로 | 역할 |
|------|------|------|
| E2E 실행기 | `.deepx/e2e/e2e_runner.py` | 5개 CLI 에이전트에 autopilot E2E(6시나리오)를 N라운드 실행 |
| 실행 wrapper | `.deepx/e2e/test.sh` | `agent-driven-e2e-<tool>-autopilot` 실제 테스트 호출 |
| 분석기 | `.deepx/e2e/agent_analyzer/analyze.py` | run_id별 점수화 + 리포트 생성 |
| 비교 리포트 | `.deepx/e2e/agent_analyzer/build_comparison.py` | 두 분석 리포트 디렉토리 side-by-side delta |
| 분석기 상세 문서 | `.deepx/e2e/agent_analyzer/README-KO.md` | 파이프라인/메트릭/점수식 전체 |

평가 대상 5개 tool: `claude-code` · `copilot-cli` · `cursor-cli` · `opencode-cli` · `codex-cli`
6개 시나리오: `compiler` · `dx_app` · `dx_stream` · `cascaded` · `runtime` · `suite`

---

## 2. STEP 1·2 — E2E 실행 (`e2e_runner.py`)

### 2.1 모델 지정 방법 (프론티어 비교의 핵심)

per-tool 플래그가 내부적으로 env var로 변환되어 autopilot 세션에 주입된다
(`e2e_runner.py:1896` `_MODEL_ENV_MAP`):

| CLI 플래그 | 변환되는 env var | 대상 tool |
|-----------|-----------------|-----------|
| `--claude-model X`   | `DX_AGENT_E2E_CLAUDE_CODE_MODEL=X` | claude-code |
| `--copilot-model X`  | `DX_AGENT_E2E_MODEL=X`             | copilot-cli |
| `--codex-model X`    | `DX_AGENT_E2E_MODEL=X`             | codex-cli |
| `--opencode-model X` | `DX_AGENT_E2E_OPENCODE_MODEL=X`    | opencode-cli |
| `--cursor-model X`   | `DX_AGENT_E2E_CURSOR_MODEL=X`      | cursor-cli |

> ⚠ **copilot와 codex는 동일한 `DX_AGENT_E2E_MODEL`을 공유**한다. 한 번의 호출에서
> 두 tool에 서로 다른 모델을 동시에 지정할 수 없다 (충돌). 두 tool을 모두 평가하려면 호출을
> 분리하라.
>
> 모델 id 형식은 tool마다 다르다: claude CLI는 하이픈(`claude-opus-4-8`), copilot은 점(`claude-opus-4.8`).
> cursor는 사실상 `auto`만 노출된다 (모델 고정 비교에 부적합 → §6).

### 2.2 평가 대상 tool 범위 선택 (`--tools`)

상황에 따라 범위를 좁힌다 (사용자 요구에 따라 가변):

```bash
# (a) 기존처럼 5개 도구 전체
python .deepx/e2e/e2e_runner.py --rounds 5

# (b) copilot만
python .deepx/e2e/e2e_runner.py --rounds 5 --tools copilot-cli

# (c) claude-code만
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code
```

### 2.3 모델 비교용 실제 호출 (예시: copilot에서 opus46 vs opus48)

```bash
# run A — 기존 모델
python .deepx/e2e/e2e_runner.py --rounds 5 --tools copilot-cli \
    --copilot-model claude-opus-4.6
#   → 콘솔에 [model override] DX_AGENT_E2E_MODEL=claude-opus-4.6 출력, run_id 부여됨

# run B — 신규 모델
python .deepx/e2e/e2e_runner.py --rounds 5 --tools copilot-cli \
    --copilot-model claude-opus-4.8
```

claude-code에서 비교한다면:

```bash
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code --claude-model claude-opus-4-6
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code --claude-model claude-opus-4-8
```

### 2.4 자주 쓰는 부가 옵션

| 옵션 | 의미 |
|------|------|
| `--rounds N` | 라운드(반복) 수. 분산 측정을 위해 보통 5+ |
| `--parallel` | tool 동시 실행 (기본은 sequential — duration 측정 정확도↑) |
| `--thinking` | 고추론 모드 (claude/copilot `--effort xhigh`, opencode `--variant high`, codex `reasoning_effort=xhigh`; cursor 미지원) |
| `--status` / `--list` | 진행 상태 / 과거 run 목록 |
| `--stop --run-id <id>` | **graceful 중단** (현재 라운드까지 마치고 종료 — partial 데이터 보존). `--abort`보다 선호 |
| `--resume --run-id <id> --rounds N` | 중단된 run을 target까지 이어서 실행 |
| `--redo-env-failures [--dry-run]` | env 실패(cert/SSL·codex model-refresh·copilot empty-unknown) 라운드 탐지·삭제 후 resume 재실행 |

> sequential 실행은 **round-major**(라운드 우선)로 도는 게 바람직하다 — tool quota 벽을 라운드에
> 분산하고 mid-run partial report가 가능하다.

### 실행을 안전하게 멈추기 (stale "running" 방지)

**run을 멈출 땐 항상 runner를 통해서 — 절대 강제 종료(TaskStop / `kill -9`)하지 말 것.**
- `python3 .deepx/e2e/e2e_runner.py --stop --run-id <id>` — graceful (현재 라운드 마치고 종료, state 갱신).
- `python3 .deepx/e2e/e2e_runner.py --abort --run-id <id> --force` — 즉시 종료지만 runner가 자기 state는 갱신.

**강제 종료**(SIGKILL/TaskStop)는 runner가 `state.json`을 갱신할 틈을 안 주므로 `status="running"` +
죽은 pid가 남아 → `e2e_monitor.py`가 유령 "running"을 계속 표시한다.

**강제 종료돼 stale "running"이 남은 경우 복구:** `--abort --run-id <id> --force` 실행. runner에
**dead-pid fallback**이 추가됨 — 살아있는 runner/worker가 없으면 state를 terminal(`aborted`)로
정리하고 per-tool 상태도 finalize하며 `"No live runner/worker — reconciled stale state to 'aborted' (N …)"`를
출력한다.

> Headless 하네스 주의: 일부 sandbox에선 foreground `--abort`/`--stop`이 signal 16(**exit 144**
> =128+16, SIGSTKFLT)로 죽는데, state 기록은 대개 그 전에 끝난다 — **background로 실행**한 뒤
> `state.json`의 `status`가 terminal로 바뀌었는지 재확인하라. (0라운드에서 강제 종료된 run은
> `results/<run_id>/` 디렉토리도 **없다** — runner는 라운드가 완료돼야 라운드 디렉토리를 기록.)

### 2.5 실행 결과 위치 (현재 경로)

```
dx-agent-dev/e2e-tests/results/<run_id>/<timestamp_hash>_<tool>-autopilot/
    ├── manifest.json        # exit code, artifacts, timing, 적용된 thinking env
    ├── session.log / session.json
    └── <시나리오별 생성물>   # *_sync.py, factory, *.dxnn, pipeline.py, config.json ...
runner_state/<run_id>/state.json   # tool 진행/타임스탬프/exit code
```

(`RESULTS_ROOT = REPO_ROOT/"dx-agent-dev/e2e-tests/results"`, `e2e_runner.py:84`)

---

## 3. STEP 3·4 — 분석 (`analyze.py`)

```bash
cd .deepx/e2e/agent_analyzer

# 단일 run_id 분석 → analyzer_reports/<run_id>/<ts>/
python3 analyze.py --run-id <RID_OLD>
python3 analyze.py --run-id <RID_NEW>

# 여러 run_id 묶음 분석 → analyzer_reports/multi_<sha8>/<ts>/  (+ multi_manifest.json)
# 주의: --run-id는 반복 플래그 — run_id마다 반복 (space 구분 아님)
python3 analyze.py --run-id <RID_OLD> --run-id <RID_NEW>

# tool/시나리오/라운드 필터
python3 analyze.py --run-id <RID> --tool copilot-cli --round 1 2 3 --scenario compiler dx_app
```

산출물 (디렉토리당): `analysis.{md,html,json}` · `per_session.csv` · `comprehensive_report.{md,html}`
· `dashboard.html` · (옵션) `insights.md` · `runnability_report.md` · `hypothesis.json`.

점수 차원: **Compliance / Quality / Verdict / ExecutionTrace / Runnability → Overall(가중합)** + cost(추정 USD).
상세 점수식과 파이프라인 8단계는 `agent_analyzer/README-KO.md` 참조.

> 출력 기본 위치: `<suite-root>/dx-agent-dev/e2e-tests/analyzer_reports/...` (`analyze.py:86-87`)

### 모델/CLI 정책 (insights·runnability·hypothesis 단계)

- 기본값 free: 3개 LLM stage 모두 **cursor + `auto`** (구독, `--insights` 기본).
- paid fallback: `--insights copilot --insights-model claude-sonnet-4.6 --insights-allow-paid`.
- runnability 재사용: `--existing-runnability <prev>/runnability_report.md` (느린 평가 캐시).
- LLM 호출 전부 끄기: `--insights off` (정량 리포트만).

---

## Durable output (MANDATORY) — archive root
리포트와 bundle은 반드시 durable archive에 저장해야 하며, gitignored worktree 경로
(`dx-agent-dev/e2e-tests/...`)는 worktree 정리 시 소실된다 — 실제 데이터 손실 확인됨.
- Archive root: env `DX_MODEL_EVAL_ARCHIVE`, 기본값 `$HOME/shared/coding_agent_diff_report`.
- 분석 결과를 archive에 직접 저장: `analyze.py --run-id <RID> --output-dir "$DX_MODEL_EVAL_ARCHIVE/<label>/"`.
- raw 결과 bundle: `bundle_raw_results.py --results-dir <results/<run_id>> --out "$DX_MODEL_EVAL_ARCHIVE/<label>/raw/"`.
- `analyze.py`의 built-in default(`DEFAULT_REPORTS_BASE`)는 수정하지 말고, 실행 시 override한다.

---

## Usage-limit resilience (long runs)

긴 multi-round 실행 중에 Claude session/usage limit에 걸릴 수 있다. 두 개의 레이어가 이를 방어한다.

**Layer 1 — 시나리오별 in-place polling (conftest.py, 내장, 자동)**

`conftest.py`는 이미 `_CLAUDE_QUOTA_POLL_INTERVAL` = 3600 s 간격으로 최대
`_CLAUDE_QUOTA_MAX_POLLS` = 8회(최대 8시간) polling하며, usage-limit 신호가 감지되면
현재 시나리오를 in-place로 재시도한다. 일반적인 5시간 session cap은 이 레이어가 투명하게 흡수하며
별도 조치가 필요 없다. `env_failure` 분류는 모든 poll이 소진됐을 때만 e2e_runner 출력에 나타난다.

**Layer 2 — 외부 resilient controller (`.deepx/e2e/e2e_resilient_run.py`)**

rate-limit env-failure로 끝나는 round(내부 poll 소진, 또는 더 긴 weekly cap)를 위해,
outer controller가 `--redo-env-failures`, `--resume`, reset-time 파싱을 하나의 자동 복구 루프로
묶는다:

1. 목표 round 수만큼 `e2e_runner`를 실행한다.
2. 완료된 round < 목표 AND 미달분이 rate-limit env-failure인 경우:
   - `e2e_runner --redo-env-failures --run-id <id>` 실행 — 실패 round 데이터를 삭제하고
     state를 reset해서 다음 `--resume`이 빠진 round를 채울 수 있게 한다.
   - 실패 round transcript에서 reset time을 파싱하고, reset까지 대기한다. 파싱 불가 시
     (자유 형식 "resets in ~2 hours", 불명확한 bare "resets at 3", timezone 포함 시각 등)
     `--fallback-wait`(기본 3600 s)으로 대기한다.
   - `e2e_runner --resume --run-id <id>` 실행으로 남은 round를 채운다.
   - `--max-attempts`(기본 6회)까지 반복한다.
3. 세 가지 status 중 하나를 반환한다:
   - `complete` — 목표 round 달성.
   - `incomplete-nonenv` — usage-limit이 아닌 실패로 중단; controller가 loop를 지속하지 않는다.
   - `max-attempts` — 목표 미달 상태로 loop 소진.

**사용법:**

```bash
# 기본 — 5 round, usage limit 발생 시 자동 복구
python3 .deepx/e2e/e2e_resilient_run.py \
    --tool claude-code --model <id> --rounds N

# thinking 모드 포함
python3 .deepx/e2e/e2e_resilient_run.py \
    --tool claude-code --model <id> --rounds N --thinking

# dry-run (계획된 첫 번째 커맨드 출력 후 종료)
python3 .deepx/e2e/e2e_resilient_run.py \
    --tool claude-code --model <id> --rounds N --dry-run
```

`run_model_eval.sh` wrapper도 `--dry-run`을 받아 controller에 그대로 전달한다.
Controller는 최종 `run_id`를 stderr(e2e_runner에서 forwarding)에 `run_id=<id>` 형태로 출력하며,
`grep -oP 'run_id=\K[^ ]+'`로 캡처할 수 있다.

**규칙:** multi-round 실제 실행에는 resilient controller(또는 이를 사용하는 `run_model_eval.sh`)를
우선 사용한다. 이렇게 하면 usage limit에 걸려도 자동 복구되며, 실패 round가 리포트를 오염시키지 않는다.

---

## 4. STEP 5 — 비교 리포트 (`build_comparison.py`)

두 분석 리포트 디렉토리(각각 `per_session.csv` + `comprehensive_report.html` 포함) 간 delta.

```bash
python3 build_comparison.py \
  --non-thinking-dir <REP_OLD> \
  --thinking-dir     <REP_NEW> \
  --non-thinking-run-id <RID_OLD> \
  --thinking-run-id     <RID_NEW> \
  --output <out>/comparison.html
```

출력: 단일 HTML — tool별 집계 delta 표(Compliance/Quality/ExecutionTrace/Runnability/Overall) +
(tool × 시나리오) delta 표 + 두 원본 리포트 side-by-side iframe. LLM 호출 없이 CSV 집계만.

> ⚠ **네이밍 caveat**: 플래그 이름이 `--non-thinking-dir` / `--thinking-dir`이다. 원래 *thinking
> vs non-thinking* 축으로 만들어진 도구라, 프론티어 *모델 vs 모델* 비교에 그대로 쓰면 리포트의
> 라벨이 "Thinking/Non-Thinking"으로 표기된다. 비교 자체(run A vs run B delta)는 정상 동작하지만,
> 라벨이 의도와 안 맞는다. → 라벨/축을 "모델 vs 모델"로 바꾸는 작업은 **별도 후속 작업**(사용자가
> "모델 vs 모델 비교 흐름 정비"를 선택하면 진행)으로 남겨둔다.
>
> 과거 `opus46_vs_opus48`(§7)는 build_comparison 대신 **multi-run analyze**(여러 run_id를 한
> 리포트로 묶기) 방식으로 작성되어 있다. 두 접근 모두 유효하다.

---

## 5. 과거 모델 점수 참조 위치

기존 리포트가 `~/shared/coding_agent_diff_report/` 아래에 보존되어 있어 과거 모델 점수를 참고할 수 있다.

| 디렉토리 | 내용 | run_ids (multi_manifest) |
|----------|------|--------------------------|
| `20260528-202548_v3-MULTI-15R/` | 5 tool 15라운드 종합 분석 | `20260521_202016`, `20260522_195812`, `20260526_204111` |
| `20260604-073803_v3-opus46_vs_opus48/` | opus46↔opus48 비교(copilot) | `20260526_204111`, `20260529_183101`, `20260529_231925`, `20260530_044017` (digest `946422be`) |
| (top-level) `sonnet_vs_opus_report.html`, `nth_vs_th_report.html`, `r8_vs_r9_root_cause.html` | build_comparison류 단발 비교 HTML | — |

각 디렉토리는 `analysis.{md,html,json}` · `per_session.csv` · `comprehensive_report.{md,html}` ·
`dashboard.html` · `insights.md` · `runnability_report.{md,html}` · `hypothesis.json`을 포함한다.

---

## 6. ⚠ 알려진 주의점 / 한계 (현황 점검에서 확인)

### 6.1 경로 슬러그 리브랜딩 (dx-agentic-dev → dx-agent-dev)

- 과거 세션은 슬러그가 **`dx-agentic-dev`** 였고 repo 경로도 **`dx-all-suite-full-e2e`** 였다.
  (예: 과거 리포트에 `.../dx-all-suite-full-e2e/dx-runtime/dx_app/dx-agentic-dev/2026...` 264건)
- **현재는 `dx-agent-dev/` 하위**에 e2e-tests 결과물과 보고서가 생성된다 (이 워크트리:
  `dx-all-suite-frontier-eval`). 코드의 `RESULTS_ROOT`/리포트 base도 모두 `dx-agent-dev/e2e-tests/`.
- 따라서 **과거 리포트에 적힌 경로를 그대로 따라가면 존재하지 않는다.** 과거 리포트는 *점수 참조용*
  으로만 보고, 경로는 현재 슬러그(`dx-agent-dev`)로 치환해서 해석한다.

### 6.2 모델 라벨이 `model` 컬럼에 반영 안 되는 케이스 (중요)

- `20260604-073803_v3-opus46_vs_opus48/per_session.csv`를 점검한 결과,
  **120행 전부 `model=claude-sonnet-4.6`** (config 기본값)으로 떨어져 있었다. 실제 모델 구분은
  session_id 디렉토리명(`..._opus46_...`)에만 남아 있다.
- 즉 과거 비교는 *모델별 run을 분리*해서 했지만, 분석기의 **모델 탐지가 세션에서 실제 모델을
  못 읽어 config `default_models`로 폴백**했다. CSV `model` 컬럼만 믿고 "두 모델이 섞였다/같다"고
  판단하면 안 된다.
- 비교는 **run_id(=모델) 단위로 분리**해서 수행하고, 라벨은 run_id ↔ 지정 모델 매핑을 따로 기록해
  두는 것이 안전하다. (모델 탐지/exec-scoring 정확도 개선은 별도 백로그 항목.)

### 6.3 도구별 특성

- **cursor-cli**: 실질적으로 `auto` 모델만 노출 → 특정 프론티어 모델 고정 비교에는 부적합.
  thinking 모드도 미지원.
- **copilot/codex**: `DX_AGENT_E2E_MODEL` 공유 → 한 호출에서 둘을 다른 모델로 동시 평가 불가.
- copilot `gpt-4.1`은 deprecated. 모델 id 형식(하이픈 vs 점) tool별로 다름 → 불일치 시 거부됨.

### 6.4 토큰/비용 의미론

- tool마다 `input_tokens` 의미가 다르다(Claude/Cursor=fresh, Copilot/OpenCode=total, Codex=cached 포함).
  분석기가 fresh로 정규화 후 비용 추정. 절대 비용보다 **동일 tool 내 모델 간 상대 비교**가 신뢰도 높다.

### raw 결과는 단순 복사 불가 — bundle_raw_results.py 사용 필수
`results/<run_id>/...`는 실제 output dir에 대한 SYMLINK를 담고 있으며(`conftest.py:1114`),
생성 코드는 Output Isolation에 따라 sub-project 디렉토리(`dx-runtime/dx_app/dx-agent-dev/<session>/`,
`dx-compiler/dx-agent-dev/<session>/`, …)에 분산 저장된다. `manifest.json`에는 절대 경로가 기록된다.
단순 `cp`를 쓰면 dangling link + stale 경로가 생긴다. `bundle_raw_results.py`는 symlink를
역참조하고, `manifest.relative_path`로 분산 디렉토리를 수집하며, 대용량 파일(`.dxnn`/`venv/`/`*.onnx`)을
제외하고 manifest 경로를 bundle 상대 경로로 재작성한다.
대안(불완전): `cp -rL --exclude='*.dxnn' …`.

---

## 7. 체크리스트 (프론티어 비교 1사이클 수행 시)

- [ ] 비교할 `OLD` / `NEW` 모델 id 확정 (tool별 형식 — 하이픈/점 주의)
- [ ] 평가 tool 범위 확정 (`--tools`: 5개 전체 / copilot / claude-code)
- [ ] run A (OLD), run B (NEW)를 **각각 분리 실행** → run_id 2개 기록 (run_id ↔ 모델 매핑 메모)
- [ ] 각 run_id `analyze.py --run-id ...` → 리포트 2개
- [ ] `build_comparison.py`로 delta HTML (라벨 caveat 인지) 또는 multi-run analyze
- [ ] 과거 점수는 `~/shared/coding_agent_diff_report/`에서 참조, 경로는 `dx-agent-dev`로 치환 해석
- [ ] `model` 컬럼 폴백(§6.2) 여부 확인 — run_id 기준으로 모델 귀속 판단

## 8. 복구 도구 — 시나리오 살리기, 라운드 이식, 모니터링

run이 일부 env-failed(rate-limit)/incomplete 라운드·시나리오로 끝나도 run 전체를 재실행할 필요는
없습니다. 세 도구(모두 rate-limit 복원력 내장, `.deepx/e2e/` 하위):

### `cleanup_resume_scenarios.py` — 한 라운드의 특정 시나리오만 살리기
지정 시나리오만 라운드 dir에서 삭제 → `test.sh -k`로 재실행 → **같은 라운드 dir에 병합**(in-place로
valid화). `--scenarios`로 env-failed인 것만 지정(이미 valid인 건 보존)하거나 `all`로 전체 재실행.
```bash
python3 .deepx/e2e/cleanup_resume_scenarios.py \
  --run-id <RID> --round-dir <ts_hash>_claude-code-autopilot \
  --scenarios runtime,suite --tool claude-code --model <id> [--thinking] [--dry-run]
```
- rate-limit 복원력 (삭제 → 재실행 → 여전히 env-failed면 리셋 대기 → 재시도, max-attempts).
- `runner_state/<run_id>/salvage.json` 기록 → `e2e_monitor.py`가 진행 상황 표시.
- 병합 후 scratch 라운드 dir을 `superseded__<name>`으로 rename (analyzer discovery 제외 + audit 보존).
- 주의: `incomplete` 시나리오(작업은 했으나 DONE 없음 — 예: 시나리오 timeout 초과한 컴파일)는
  **자동 retry 안 함**(env 실패가 아니라 model/timeout 행동). 필요하면 `--scenarios <name>`로 명시 재실행.

### `move_round.py` — 라운드를 run_id 간 이식
완전 valid 라운드를 한 run_id에서 다른 run_id로 이동(이동 dir의 manifest `run_id` 재작성, **양쪽
state.json 정합**, 대상 라운드 교체 옵션). 비-valid 소스 라운드는 거부(`--require-valid` 기본).
라운드 번호는 autopilot-dir timestamp 순.
```bash
python3 .deepx/e2e/move_round.py \
  --from-run-id <A> --from-round-dir <ts_hash>_claude-code-autopilot \
  --to-run-id <B> --replace-round-dir <B의 ts_hash>_claude-code-autopilot [--dry-run]
```

### 모니터링 — `e2e_monitor.py`
monitor는 validity·salvage 인지 (state "completed" ≠ "valid"):
- `python3 .deepx/e2e/e2e_monitor.py` (인자 없음, TTY) → 목록에서 run 선택 후 라이브 모니터링.
  `--list`는 effective status(salvage 활성 시 `re-running`) + `valid:X/N ⟳Ra ✗Rb` 표시.
  `--select`는 목록+선택, `--run-id <id>`는 직접 모니터링.
- 단일 뷰에 **Round Validity** 표(라운드별 `✓ valid`/`⟳ re-running`/`✗ env-failed`/`△ incomplete`)
  + per-scenario 셀(`cmp✓ app✓ str✓ csc✓ rt✓ ste⟳`) + R#↔폴더 매핑 Dir 컬럼. 라이브 루프는
  salvage 진행 중에는 계속 refresh.
