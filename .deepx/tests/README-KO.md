# DX-ALL-SUITE Agentic Development 테스트

## 📋 개요

DX-ALL-SUITE 프로젝트용 에이전트 개발 테스트 모음입니다. AI 코딩 에이전트 인프라를 검증하고,
5개 CLI 도구로 end-to-end 시나리오를 실행합니다.

제품 테스트(docker_install, local_install, getting_started)는 [`tests/README.md`](../../tests/README.md)를 참조하세요.

---

## ✅ 테스트 범주

### 1. test_agentic_scenarios — 에이전트 개발 인프라 검증
5개 프로젝트 레벨(suite, compiler, runtime, dx_app, dx_stream) 전반의 에이전트 개발 인프라를 검증합니다.

**검증 항목:**
- 가이드 문서 구조: 존재 여부, 제목, 시나리오 번호, 영문/국문 동기화
- 라우팅 일관성: CLAUDE.md, AGENTS.md, copilot-instructions.md, copilot.json, .cursorrules
- 시나리오 참조: 가이드의 agent/skill 참조가 실제 인프라와 일치하는지
- 크로스 프로젝트 시나리오: handoff 체인, 검증 스크립트, output isolation

### 2. test_agentic_e2e_scenarios — 에이전트 E2E 시나리오 테스트

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
`.deepx/tests/e2e_runner.py` 및 `.deepx/tests/e2e_monitor.py`에 위치합니다.

### e2e_runner.py

5개 도구를 병렬로 N 라운드 실행하며, 상태 추적 및 이어서 실행(resume) 기능을 제공합니다.

```bash
# 모든 도구 5 라운드 병렬 실행
python .deepx/tests/e2e_runner.py --rounds 5

# 특정 도구만 실행
python .deepx/tests/e2e_runner.py --rounds 5 --tools claude-code,copilot-cli

# Thinking / 고추론 모드 활성화 (xhigh effort)
python .deepx/tests/e2e_runner.py --rounds 5 --thinking

# Resume: 완료된 라운드 자동 감지 후 목표까지 이어서 실행
python .deepx/tests/e2e_runner.py --rounds 10 --resume

# 특정 이전 run ID로 resume
python .deepx/tests/e2e_runner.py --rounds 10 --resume --run-id 20260521_100000

# 최신 실행 상태 확인
python .deepx/tests/e2e_runner.py --status

# 특정 라운드 산출물 삭제
python .deepx/tests/e2e_runner.py --cleanup --round 3
python .deepx/tests/e2e_runner.py --cleanup --round 3 --tool claude-code
python .deepx/tests/e2e_runner.py --cleanup --round 2,3,4
```

**Thinking 모드** (도구별 env var):

| 도구 | Thinking 모드 env var |
|---|---|
| `claude-code` | `DX_AGENTIC_E2E_CLAUDE_CODE_EXTRA_ARGS=--effort xhigh` |
| `copilot-cli` | `DX_AGENTIC_E2E_COPILOT_EXTRA_ARGS=--effort xhigh` |
| `opencode-cli` | `DX_AGENTIC_E2E_OPENCODE_EXTRA_ARGS=--variant high` |
| `codex-cli` | `DX_AGENTIC_E2E_CODEX_EXTRA_ARGS=-c model_reasoning_effort="xhigh"` |
| `cursor-cli` | Thinking 모드 없음 (quota 초과 시 auto fallback) |

**State 파일** (`.deepx/tests/runner_state/<run_id>/`):
- `state.json` — 라운드 완료 상태, artifact 경로, exit code
- `logs/<tool>.log` — 도구별 전체 stdout/stderr 로그
- `latest` symlink — 최신 실행을 항상 가리킴

**Resume 로직 우선순위:**
1. `--run-id` 지정 시: 해당 state.json 로드
2. 미지정 시: `runner_state/latest` symlink로 로드
3. fallback: `dx-agentic-dev/e2e-tests/results/` 스캔하여 기존 결과로 state 구성

### e2e_monitor.py

`rich` 기반 Live TUI 모니터로 runner 진행 현황을 실시간으로 확인합니다.

```bash
# 최신 실행 실시간 모니터 (3초마다 갱신)
python .deepx/tests/e2e_monitor.py

# 특정 run 모니터
python .deepx/tests/e2e_monitor.py --run-id 20260521_100000

# 특정 도구 로그 집중 표시 (tail 30줄)
python .deepx/tests/e2e_monitor.py --tool claude-code --tail 30

# 스냅샷 1회 출력 후 종료 (실시간 갱신 없음)
python .deepx/tests/e2e_monitor.py --once
```

**모니터 화면 구성:**
- Round Progress 테이블: Done / Fail / Remaining / Status / 마지막 결과 디렉토리
- 로그 패널: 현재 실행 중인 도구의 tail 출력 (최대 3개 나란히)
- Timeline: `results/` 에 새 결과 디렉토리 생성 시 실시간 표시

---

## 🚀 빠른 시작

```bash
cd .deepx/tests

# 에이전트 인프라 검증 (199개 테스트, ~1초)
./test.sh agentic

# 에이전트 E2E 시나리오 테스트 (도구별)
./test.sh agentic-e2e-copilot-cli-autopilot     # Copilot CLI
./test.sh agentic-e2e-cursor-cli-autopilot      # Cursor CLI
./test.sh agentic-e2e-opencode-cli-autopilot    # OpenCode CLI
./test.sh agentic-e2e-claude-code-autopilot     # Claude Code CLI
./test.sh agentic-e2e-codex-cli-autopilot       # Codex CLI

# 여러 라운드 병렬 실행 (e2e_runner.py)
python .deepx/tests/e2e_runner.py --rounds 5
python .deepx/tests/e2e_runner.py --status
python .deepx/tests/e2e_monitor.py             # 별도 터미널에서 실시간 모니터링
```

---

## 📊 분석 리포트 생성

E2E 실행 완료 후 아래 명령으로 종합 분석 리포트를 생성합니다:

```bash
cd .deepx/tests/agentic_analyzer

# 기본 옵션 (가설 생성 + 정량 비교 + runnability + 정성 insight + 가설 비교 분석)
python analyze.py

# 특정 라운드만 (예: 1~5 라운드)
python analyze.py --rounds 1,2,3,4,5

# 특정 도구만
python analyze.py --tools claude-code,copilot-cli
```

---

## 🔧 환경 변수

```bash
# Claude Code CLI
export DX_AGENTIC_E2E_CLAUDE_CODE_MODEL="claude-sonnet-4-6"
export DX_AGENTIC_E2E_CLAUDE_CODE_TIMEOUT=600
export DX_AGENTIC_E2E_CLAUDE_CODE_EXTRA_ARGS="--effort xhigh"  # thinking 모드

# Copilot CLI
export DX_AGENTIC_E2E_TIMEOUT=900
export DX_AGENTIC_E2E_COPILOT_EXTRA_ARGS="--effort xhigh"  # thinking 모드

# Cursor CLI
export DX_AGENTIC_E2E_CURSOR_MODEL="claude-4.6-sonnet-medium"
export DX_AGENTIC_E2E_CURSOR_TIMEOUT=300
export CURSOR_API_KEY="your-api-key"

# OpenCode CLI
export DX_AGENTIC_E2E_OPENCODE_MODEL="github-copilot/claude-sonnet-4.6"
export DX_AGENTIC_E2E_OPENCODE_TIMEOUT=600
export DX_AGENTIC_E2E_OPENCODE_EXTRA_ARGS="--variant high"  # thinking 모드

# Codex CLI
export DX_AGENTIC_E2E_CODEX_EXTRA_ARGS='-c model_reasoning_effort="xhigh"'  # xhigh 모드
```

---

## 📁 파일 구조

```
.deepx/tests/
├── 🐍 e2e_runner.py                 # 멀티 라운드 병렬 E2E runner
├── 🐍 e2e_monitor.py                # Live TUI 모니터 (rich 기반)
├── 📁 runner_state/                 # Runner 상태 파일 (자동 생성)
│   ├── latest -> <run_id>/          # 최신 실행 symlink
│   └── <run_id>/                    # 실행별 상태 디렉토리 (YYYYMMDD_HHMMSS)
│       ├── state.json               # 라운드 완료 상태 + artifact 경로
│       └── logs/<tool>.log          # 도구별 stdout/stderr 로그
├── 🐍 test_agentic_scenarios/       # 에이전트 인프라 검증
│   ├── conftest.py
│   ├── test_guide_structure.py
│   ├── test_routing_consistency.py
│   ├── test_scenario_references.py
│   └── test_cross_project_scenarios.py
├── 🐍 test_agentic_e2e_scenarios/   # 에이전트 E2E 시나리오 테스트
│   ├── conftest.py                  # Runner, ScenarioResult, helpers
│   ├── test_dx_app_agentic_e2e.py   # dx_app — Copilot CLI
│   ├── test_dx_stream_agentic_e2e.py
│   ├── test_compiler_agentic_e2e.py
│   ├── test_runtime_agentic_e2e.py
│   ├── test_suite_agentic_e2e.py
│   ├── test_cursor_*.py             # Cursor CLI
│   ├── test_opencode_*.py           # OpenCode CLI
│   └── test_claude_code_*.py        # Claude Code CLI
├── 🔍 agentic_analyzer/             # 분석 리포트 생성기
│   ├── analyze.py                   # 메인 분석 스크립트
│   ├── lib/                         # 정량/정성 분석 라이브러리
│   └── README.md                    # 분석기 문서
├── 🔧 test.sh                       # 단일 도구 단일 라운드 실행 진입점
├── 📋 requirements.txt
├── 📋 README.md                     # 영문 문서 (이 파일의 영문 버전)
└── 📋 README-KO.md                  # 한국어 문서 (이 파일)
```

---

**총 에이전트 테스트 수:**
551개 (agentic: 199 | copilot_cli: 67 | cursor_cli: 63 | opencode_cli: 112 | claude_code_cli: 110)
