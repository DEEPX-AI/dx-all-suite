# DX-ALL-SUITE Agent-Driven Development 테스트

## 📋 개요

DX-ALL-SUITE 프로젝트용 에이전트 개발 테스트 모음입니다. AI 코딩 에이전트 인프라를 검증하고,
5개 CLI 도구로 end-to-end 시나리오를 실행합니다.

제품 테스트(docker_install, local_install, getting_started)는 [`tests/README.md`](../../tests/README.md)를 참조하세요.

---

## ✅ 테스트 범주

### 1. conformance — 에이전트 개발 인프라 검증
5개 프로젝트 레벨(suite, compiler, runtime, dx_app, dx_stream) 전반의 에이전트 개발 인프라를 검증합니다.

**검증 항목:**
- 가이드 문서 구조: 존재 여부, 제목, 시나리오 번호, 영문/국문 동기화
- 라우팅 일관성: CLAUDE.md, AGENTS.md, copilot-instructions.md, copilot.json, .cursorrules
- 시나리오 참조: 가이드의 agent/skill 참조가 실제 인프라와 일치하는지
- 크로스 프로젝트 시나리오: handoff 체인, 검증 스크립트, output isolation

### 2. test_agent_e2e_scenarios — 에이전트 E2E 시나리오 테스트

5개 CLI 도구(Copilot CLI, Cursor CLI, OpenCode CLI, Claude Code CLI, Codex CLI)로
실제 에이전트 호출을 실행하고 생성된 출력 파일을 정적으로 검증합니다.

**자율 실행(autopilot) 모드:**
- `copilot autopilot`: Copilot CLI (`copilot`) 완전 자율 실행, `--no-ask-user`
- `cursor autopilot`: Cursor CLI (`agent -p --force`) 완전 자율 실행
- `opencode autopilot`: OpenCode CLI (`opencode run --format json`) 완전 자율 실행
- `claude-code autopilot`: Claude Code CLI (`claude -p --dangerously-skip-permissions`) 완전 자율 실행
- `codex autopilot`: Codex CLI 완전 자율 실행

**6개 시나리오:**
- **dx_app Scenario #1:** yolo26n 사람 감지 앱 빌드 (IFactory 패턴, config.json, runner)
- **dx_stream Scenario #1:** 추적 포함 감지 파이프라인 빌드 (GStreamer elements, RTSP, tracker)
- **dx-compiler Scenario #2:** ONNX → DXNN 컴파일 config 생성 (config.json 구조)
- **dx-runtime Scenario #2:** 라우팅을 통한 독립 감지 앱 빌드 (라우팅 검증)
- **dx-all-suite Scenario #2:** 크로스 프로젝트 컴파일 + 앱 생성 (컴파일러와 앱 산출물 모두)
- **dx_stream Cascaded Scenario:** 계단식 파이프라인 시나리오 (OpenCode/Claude Code)

**검증 방식:** 정적 분석만 사용 (파일 존재 여부, `ast.parse`로 Python 문법, JSON 구조, 필수 패턴). 실제 HW 추론 없음.

---

## 🔄 E2E Runner & Monitor

여러 라운드를 병렬로 실행하고 진행 현황을 모니터링하는 재사용 가능한 도구입니다.
`.deepx/e2e/e2e_runner.py` 및 `.deepx/e2e/e2e_monitor.py`에 위치합니다.

### e2e_runner.py

5개 도구를 N 라운드 실행하며, 상태 추적, 중단/재개, 상세 상태 확인 기능을 제공합니다.
기본은 **순차(sequential) 실행** (한 번에 한 도구) — 도구별 duration이 NPU/CPU 경합 없이
단독 실행 baseline에 가깝게 측정됩니다. throughput이 더 중요한 경우 `--parallel`로 도구 간
동시 실행 모드로 전환 가능합니다.

`--rounds`는 **필수 옵션**입니다 (조회/제어 명령은 예외).

```bash
# 모든 도구 5 라운드 순차 실행 (기본)
python .deepx/e2e/e2e_runner.py --rounds 5

# 병렬 실행 — 5개 도구 동시 실행 (빠른 batch, 측정값은 경합으로 왜곡 가능)
python .deepx/e2e/e2e_runner.py --rounds 5 --parallel

# 특정 도구만 실행
python .deepx/e2e/e2e_runner.py --rounds 5 --tools claude-code,copilot-cli

# Thinking / 고추론 모드 활성화 (xhigh effort)
python .deepx/e2e/e2e_runner.py --rounds 5 --thinking

# Resume: 완료된 라운드 자동 감지 후 목표까지 이어서 실행
python .deepx/e2e/e2e_runner.py --rounds 10 --resume

# 특정 이전 run ID로 resume
python .deepx/e2e/e2e_runner.py --rounds 10 --resume --run-id 20260521_100000

# Run ID 목록 조회
python .deepx/e2e/e2e_runner.py --list

# 상세 상태 확인 (mode/라운드/시나리오별 timing 포함)
python .deepx/e2e/e2e_runner.py --status
python .deepx/e2e/e2e_runner.py --status --run-id 20260521_135734

# Graceful 중단 (현재 라운드 완료 후 종료)
python .deepx/e2e/e2e_runner.py --stop

# 즉시 중단 (진행중 라운드 결과물 삭제)
python .deepx/e2e/e2e_runner.py --abort
python .deepx/e2e/e2e_runner.py --abort --force   # 확인 프롬프트 생략

# 특정 라운드 산출물 삭제
python .deepx/e2e/e2e_runner.py --cleanup --round 3
python .deepx/e2e/e2e_runner.py --cleanup --round 3 --tool claude-code
python .deepx/e2e/e2e_runner.py --cleanup --round 2,3,4
```

**Sequential vs Parallel 비교:**

| 모드 | 도구 동시 실행 수 | 사용 사례 |
|------|------------------|----------|
| (기본) | 1 | NPU/CPU 경합 제거. 도구별 정확한 측정/분석 필요 시 |
| `--parallel` | N (도구 개수, e.g. 5) | 빠른 batch 실행. 신뢰성보다 throughput |

`--status` 결과의 `Mode:` 필드와 `state.json`의 `"mode"` 필드로 어떤 모드로 실행됐는지 확인 가능합니다.

**시나리오별 timeout** (도구 subprocess의 `subprocess.run(timeout=...)` 한도):

| 시나리오 | 기본값 | 환경변수 override |
|---------|--------|------------------|
| compiler           | 1800s (30m) | `DX_TIMEOUT_COMPILER` |
| dx_app             | 900s (15m)  | `DX_TIMEOUT_DX_APP` |
| dx_stream          | 900s (15m)  | `DX_TIMEOUT_DX_STREAM` |
| dx_stream_cascaded | 1200s (20m) | `DX_TIMEOUT_DX_STREAM_CASCADED` |
| runtime            | 1200s (20m) | `DX_TIMEOUT_RUNTIME` |
| suite              | 2400s (40m) | `DX_TIMEOUT_SUITE` |
| (fallback)         | 7200s       | `DX_E2E_TIMEOUT` |

기본값은 **sequential 실행 baseline 기준**으로 설정되어 있습니다. 병렬 모드는 NPU/CPU 경합으로 인해 더 긴 시간이 필요할 수 있어, 필요 시 환경변수로 늘려서 사용하세요:
```bash
DX_TIMEOUT_COMPILER=3600 DX_TIMEOUT_SUITE=4800 python .deepx/e2e/e2e_runner.py --rounds 5
```

**중단 및 재개:**

| 명령 | 동작 | 자식 프로세스 | 진행중 라운드 결과물 |
|------|------|--------------|---------------------|
| `--stop` | Graceful — 현재 라운드 완료 후 종료 | 자연 종료 대기 | 유지 |
| `--abort` | Immediate — 즉시 종료 | SIGTERM 전송 | 삭제 |
| `--resume --rounds N` | 완료된 라운드 이후부터 N까지 이어 실행 | — | — |

중단 후 재개 예시:
- `--stop` → 각 도구 현재 라운드 완료 → `--resume --rounds 10` → 남은 라운드 실행
- `--abort` → 진행중 라운드 삭제 → `--resume --rounds 10` → 미완료 라운드부터 재실행

**Thinking 모드** (도구별 env var):

| 도구 | Thinking 모드 env var |
|---|---|
| `claude-code` | `DX_AGENT_E2E_CLAUDE_CODE_EXTRA_ARGS=--effort xhigh` |
| `copilot-cli` | `DX_AGENT_E2E_COPILOT_EXTRA_ARGS=--effort xhigh` |
| `opencode-cli` | `DX_AGENT_E2E_OPENCODE_EXTRA_ARGS=--variant high` |
| `codex-cli` | `DX_AGENT_E2E_CODEX_EXTRA_ARGS=-c model_reasoning_effort="xhigh"` |
| `cursor-cli` | Thinking 모드 없음 (quota 초과 시 auto fallback) |

**State 파일** (`.deepx/e2e/runner_state/<run_id>/`):
- `state.json` — 라운드 완료 상태, timing, artifact 경로, exit code, PID
- `logs/<tool>.log` — 도구별 전체 stdout/stderr 로그
- `STOP` / `ABORT` — sentinel 파일 (--stop/--abort 시 생성)
- `latest` symlink — 최신 실행을 항상 가리킴

**state.json 구조:**
```json
{
  "run_id": "20260521_135734",
  "created_at": "2026-05-21T04:57:34Z",
  "target_rounds": 5,
  "thinking": true,
  "mode": "parallel",
  "runner_pid": 67890,
  "tools": ["claude-code", "copilot-cli", ...],
  "tool_states": {
    "claude-code": {
      "completed": [
        {"round": 1, "exit_code": 0, "start_utc": "...", "end_utc": "...", "result_dir_name": "..."}
      ],
      "in_progress": {"round": 2, "start_utc": "..."},
      "pid": 12345,
      "status": "running"
    }
  }
}
```

**Resume 로직 우선순위:**
1. `--run-id` 지정 시: 해당 state.json 로드
2. 미지정 시: `runner_state/latest` symlink로 로드
3. fallback: 새 run_id로 빈 state 생성 (legacy flat results는 `migrate_results_to_run_id.py`로 이주 후 사용)

### results/ 디렉터리 레이아웃 (run-id 기반)

각 run의 결과물은 run-id 디렉터리 아래에 격리됩니다 — run 간 결과가 섞이지 않아 분석 정합성이 보장됩니다.

```
dx-agent-dev/e2e-tests/results/
├── 20260521_135734/                       ← e2e_runner의 run_id
│   ├── 20260521_174857_e25076_claude-code-autopilot/
│   │   ├── manifest.json
│   │   ├── SUMMARY.md
│   │   └── ...
│   └── 20260521_155006_824828_copilot-cli-autopilot/
├── 20260520_193327/                       ← 다른 run
│   └── ...
├── manual/                                ← 수동 pytest 실행 (DX_RUN_ID 미설정)
│   └── 20260519_103045_xxxxxx_claude-code-autopilot/
└── legacy/                                ← 기존 flat 결과를 마이그레이션
    └── 20260511_194755_d31c86_cursor-cli-autopilot/
```

**구분 메커니즘:** `e2e_runner.py`가 subprocess 실행 시 `DX_RUN_ID=<run_id>` env를 전파 → `conftest.py:pytest_sessionfinish`가 이를 읽어 `results/<run_id>/` 아래에 결과 디렉터리 생성. 수동 pytest 실행(env 미설정)은 `results/manual/`로 분리.

### 기존 flat results/ 마이그레이션

```bash
# Dry-run으로 이동 계획 미리보기
python .deepx/e2e/migrate_results_to_run_id.py

# 실제 이동 (run-id 매칭 + 미매칭 → legacy/)
python .deepx/e2e/migrate_results_to_run_id.py --apply

# 미매칭은 legacy/로 옮기지 않고 그대로 두기
python .deepx/e2e/migrate_results_to_run_id.py --apply --skip-legacy
```

스크립트는 `runner_state/*/state.json`의 `completed[*].result_dir_name`을 통해 매핑을 구성하며, 매칭되지 않은 디렉터리는 `legacy/`로 이동합니다. 분석기는 두 레이아웃을 모두 지원하므로 마이그레이션은 권장 사항이지 필수가 아닙니다.

### e2e_monitor.py

`rich` 기반 Live TUI 모니터로 runner 진행 현황을 실시간으로 확인합니다.

```bash
# 최신 실행 실시간 모니터 (progress table만, 로그 없음)
python .deepx/e2e/e2e_monitor.py

# 특정 run 모니터
python .deepx/e2e/e2e_monitor.py --run-id 20260521_100000

# 모든 도구 로그 표시
python .deepx/e2e/e2e_monitor.py --tool all

# 특정 도구 로그 집중 표시 + 시나리오 timing (tail 30줄)
python .deepx/e2e/e2e_monitor.py --tool claude-code --tail 30

# Run ID 목록 조회
python .deepx/e2e/e2e_monitor.py --list

# 스냅샷 1회 출력 후 종료 (실시간 갱신 없음)
python .deepx/e2e/e2e_monitor.py --once
```

**`--tool` 옵션:**

| 옵션 | 동작 |
|------|------|
| (미지정) | Progress table만 표시, 로그 패널 없음 |
| `--tool all` | 5개 도구 전체 tail 로그 표시 |
| `--tool <name>` | 해당 도구만 tail 로그 + 시나리오별 timing 표시 |

**모니터 화면 구성:**
- Round Progress 테이블: Done / Fail / Remaining / Status / Timing / Scenarios
- Timing 컬럼: 현재 라운드 시작시간 + 경과시간 (예: `R3 14:30 (42m+)`)
- 시나리오 아이콘: ✓(완료) ▶(진행중) ·(대기)
- 로그 패널 (`--tool` 지정 시): 도구별 실시간 tail 출력
- 시나리오 timing 패널 (`--tool <name>` 시): 시나리오별 시작/종료/duration

---

## 🚀 빠른 시작

```bash
cd .deepx/e2e

# 에이전트 인프라 검증 (~704개 테스트, ~1초)
./test.sh agent-driven

# 에이전트 E2E 시나리오 테스트 (도구별)
./test.sh agent-driven-e2e-copilot-cli-autopilot     # Copilot CLI
./test.sh agent-driven-e2e-cursor-cli-autopilot      # Cursor CLI
./test.sh agent-driven-e2e-opencode-cli-autopilot    # OpenCode CLI
./test.sh agent-driven-e2e-claude-code-autopilot     # Claude Code CLI
./test.sh agent-driven-e2e-codex-cli-autopilot       # Codex CLI

# 여러 라운드 병렬 실행 (e2e_runner.py)
python .deepx/e2e/e2e_runner.py --rounds 5
python .deepx/e2e/e2e_runner.py --status
python .deepx/e2e/e2e_monitor.py             # 별도 터미널에서 실시간 모니터링
```

---

## 📊 분석 리포트 생성

E2E 실행 완료 후 아래 명령으로 종합 분석 리포트를 생성합니다:

```bash
cd .deepx/e2e/agent_analyzer

# 기본 옵션 — 모든 run_id 합산 (가설 생성 + 정량 비교 + runnability + 정성 insight + 가설 비교)
#   출력: analyzer_reports/_all/<timestamp>/
python analyze.py

# 단일 run-id만 분석
#   출력: analyzer_reports/<run_id>/<timestamp>/
python analyze.py --run-id 20260521_135734

# 여러 run-id 합산 분석 (서로 다른 batch를 한 리포트로 통합)
#   출력: analyzer_reports/multi_<sha8>/<timestamp>/  (+ multi_manifest.json)
python analyze.py --run-id 20260521_135734 --run-id 20260520_193327

# 특정 라운드/도구 필터와 조합
python analyze.py --run-id 20260521_135734 --round 1 --round 2
python analyze.py --tool claude-code,copilot-cli
```

**analyzer_reports/ 디렉터리 레이아웃:**

```
dx-agent-dev/e2e-tests/analyzer_reports/
├── _all/<timestamp>/                     ← --run-id 미지정 (모든 run 합산)
├── 20260521_135734/<timestamp>/          ← --run-id 단일
├── multi_a3f2b1c4/<timestamp>/           ← --run-id 다중 (SHA-8 해시)
│   └── multi_manifest.json               ← 포함된 run-id 목록
```

**라운드 인덱싱:** 라운드 인덱스는 `(run_id, tool)` 단위로 1부터 부여됩니다. 서로 다른 run의 R1은 충돌하지 않으며, 다중 run-id 합산 리포트에서는 per-session 상세 표에 `Run` 컬럼이 자동으로 추가됩니다.

---

## 🔧 환경 변수

```bash
# Claude Code CLI
export DX_AGENT_E2E_CLAUDE_CODE_MODEL="claude-sonnet-4-6"
export DX_AGENT_E2E_CLAUDE_CODE_TIMEOUT=600
export DX_AGENT_E2E_CLAUDE_CODE_EXTRA_ARGS="--effort xhigh"  # thinking 모드

# Copilot CLI
export DX_AGENT_E2E_TIMEOUT=900
export DX_AGENT_E2E_COPILOT_EXTRA_ARGS="--effort xhigh"  # thinking 모드

# Cursor CLI
export DX_AGENT_E2E_CURSOR_MODEL="claude-4.6-sonnet-medium"
export DX_AGENT_E2E_CURSOR_TIMEOUT=300
export CURSOR_API_KEY="your-api-key"

# OpenCode CLI
export DX_AGENT_E2E_OPENCODE_MODEL="github-copilot/claude-sonnet-4.6"
export DX_AGENT_E2E_OPENCODE_TIMEOUT=600
export DX_AGENT_E2E_OPENCODE_EXTRA_ARGS="--variant high"  # thinking 모드

# Codex CLI
export DX_AGENT_E2E_CODEX_EXTRA_ARGS='-c model_reasoning_effort="xhigh"'  # xhigh 모드
```

---

## 📁 파일 구조

```
.deepx/
├── tests/                          # ← suite conformance (이 README)
│   ├── conftest.py                 # 마커 등록 + collect_ignore
│   └── conformance/                # KB / 생성물 정책 검사 (~700, CLI/NPU 불필요)
│       ├── conftest.py             # ProjectInfra/GuidePair, 경로 상수, helper
│       ├── test_guide_structure.py · test_routing_consistency.py
│       ├── test_scenario_references.py · test_instruction_sync.py
│       ├── test_sdk_grounding.py · test_forbidden_patterns.py
│       └── test_cross_project_scenarios.py · test_e2e_suite_structure.py
│
├── e2e/                            # ← end-to-end 하니스 (위 섹션들)
│   ├── e2e_runner.py · e2e_monitor.py · migrate_results_to_run_id.py · _cli_env.py · test.sh
│   ├── runner_state/               # 실행별 상태 (자동 생성, gitignored)
│   ├── test_agent_e2e_scenarios/ # 5 CLI ~586 — conftest + test_<cli>_<scenario>.py
│   ├── agent_analyzer/           # run-id 인지 결과 분석기 (lib/ + tests/)
│   └── tests/test_e2e_runner_env_redo.py
│
└── tools/                          # ← 툴링 패키지 (tools/README.md 참조)
    ├── src/{dx_agent_dev_gen, dx_transcripts}     # 제너레이터 + 공유 transcript lib
    └── tests/{dx_agent_dev_gen, dx_transcripts}   # src/ 미러
```

> 세션 파서 + transcript 렌더러(`parse_*_session`, `generate_transcripts`, …)는
> 이제 `.deepx/tools/src/`의 `dx_transcripts` 패키지에 있습니다(sentinel·e2e 하니스·analyzer 공유).

---

**총 에이전트 테스트 수:**
~1279개 (agent-driven: ~704 | copilot_cli: ~114 | cursor_cli: ~113 | opencode_cli: ~116 | claude_code_cli: ~116 | codex_cli: ~116) — 정확한 수치는 `pytest --collect-only -q`로 확인
