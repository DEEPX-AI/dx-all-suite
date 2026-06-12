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
python3 analyze.py --run-id <RID_OLD> <RID_NEW>

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
