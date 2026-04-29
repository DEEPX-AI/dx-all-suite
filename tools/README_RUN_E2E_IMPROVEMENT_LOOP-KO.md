# run-e2e-improvement-loop.sh

자가수정 Agentic E2E 테스트 루프. 4개 AI 코딩 도구를 병렬 실행하고, 비교 분석 리포트를 생성하고, 개선 사항을 자동 적용합니다. 더 이상 적용할 개선 사항이 없거나 반복 횟수 제한에 도달할 때까지 이 과정을 반복합니다.

## 동작 방식

각 iteration은 다음 4단계를 수행합니다:

```
Step 1  4개 autopilot E2E 테스트 병렬 실행
          copilot / cursor / opencode / claude_code

Step 2  생성된 아티팩트 목록 수집
          (pipeline.py, session.json, README, run script 등)

Step 3  Claude 호출 → 비교 분석 리포트 생성
          iteration-N-report.md  +  iteration-N-report-KO.md

Step 4  Claude 호출 → 테스트 파일 / SKILL.md 개선 적용
          이후: dx-agentic-gen generate 실행 (generator drift 방지)
```

**종료 조건:**
- `no_actionable_improvements` — Claude가 더 이상 적용할 개선 사항을 찾지 못한 경우
- `max_iterations_reached` — `--max-iterations` 한도에 도달한 경우

각 실행 결과는 타임스탬프 기반 디렉터리에 저장되므로 여러 번 실행해도 기존 파일이 덮어써지지 않습니다.

## 빠른 시작

```bash
# 기본 실행 (최대 5 iteration, dx_stream 시나리오)
bash tools/run-e2e-improvement-loop.sh

# 백그라운드 실행 (장시간 실행 시 권장)
bash tools/run-e2e-improvement-loop.sh &
```

## 옵션

| 옵션 | 기본값 | 설명 |
|------|--------|------|
| `--max-iterations N` | `5` | 최대 반복 횟수 |
| `--scenario KEY` | `dx_stream` | 전체 도구 테스트에 적용할 pytest `-k` 필터 |
| `--resume` | 꺼짐 | 가장 최근 실행에서 이어서 재개 |
| `--run-dir PATH` | 자동 | 타임스탬프 자동 생성 대신 특정 실행 디렉터리 지정 |
| `--claude-bin PATH` | `claude` | Claude CLI 바이너리 경로 |
| `--model MODEL` | `claude-sonnet-4-6` | 리포트 생성 및 개선 적용에 사용할 Claude 모델 |
| `--suite-root PATH` | 자동 감지 | dx-all-suite 루트 디렉터리 경로 |
| `--dry-run` | 꺼짐 | 명령어만 출력하고 실제 실행하지 않음 |
| `-h, --help` | | 도움말 표시 |

## 출력 구조

실행마다 타임스탬프 기반 하위 디렉터리가 생성됩니다:

```
doc/reports/e2e-loop/
└── YYYYMMDD-HHMMSS/
    ├── state.json                          — 루프 상태 (iteration, 적용 목록, 상태)
    ├── LOOP_SUMMARY.md                     — 전체 적용 개선 사항 최종 요약 (EN)
    ├── LOOP_SUMMARY-KO.md                  — 한국어 번역
    ├── iteration-N-copilot-pytest.log      — 도구별 pytest 원시 로그
    ├── iteration-N-cursor-pytest.log
    ├── iteration-N-opencode-pytest.log
    ├── iteration-N-claude_code-pytest.log
    ├── iteration-N-copilot-pytest.json     — 결과 요약 JSON (pass/fail/auth_error/quota_error)
    ├── iteration-N-cursor-pytest.json
    ├── iteration-N-opencode-pytest.json
    ├── iteration-N-claude_code-pytest.json
    ├── iteration-N-artifacts.txt           — dx-agentic-dev/ 생성 파일 목록
    ├── iteration-N-context.json            — 리포트 생성 시 Claude에 전달된 컨텍스트
    ├── iteration-N-report.md               — Claude가 생성한 비교 분석 리포트 (EN)
    ├── iteration-N-report-KO.md            — 한국어 번역
    ├── iteration-N-changes.md              — 해당 iteration에서 실제 변경된 내용 로그
    ├── iteration-N-result.json             — Claude의 개선 결정 (done 여부 / 적용 목록)
    └── iteration-N-improve.log             — 개선 단계의 Claude 원시 출력
```

## 주요 사용 시나리오

### iteration 횟수를 늘려서 실행

```bash
bash tools/run-e2e-improvement-loop.sh --max-iterations 10
```

### 완료된 실행 이어서 재개

`--resume`은 가장 최근 타임스탬프 실행 디렉터리를 찾아 `state.json`을 로드하고, 다음 iteration부터 재개합니다.

**주의:** 이전 실행이 `max_iterations_reached`로 종료된 경우, `--resume`만으로는 다시 시작되지 않습니다. 반드시 `--max-iterations`를 현재 iteration 수보다 크게 설정해야 합니다.

```bash
# 최신 실행에서 이어받아 총 10 iteration까지 실행
bash tools/run-e2e-improvement-loop.sh --resume --max-iterations 10
```

`improvements_applied` 이력이 유지되므로 이미 적용된 항목(R1, R2, …)은 중복 적용되지 않습니다.

### 특정 실행 디렉터리를 지정해서 재개

```bash
bash tools/run-e2e-improvement-loop.sh \
  --run-dir doc/reports/e2e-loop/2026-04-28-175036 \
  --resume \
  --max-iterations 10
```

### dry-run (실제 실행 없이 설정 확인)

```bash
bash tools/run-e2e-improvement-loop.sh --dry-run
```

## `--resume`이 하지 않는 것

`--resume`은 이전 iteration의 리포트를 재사용하지 **않습니다**. 재개된 iteration은 항상:
1. 4개 도구 테스트를 처음부터 다시 실행
2. 새 테스트 결과를 기반으로 새 비교 리포트 생성
3. 남은 개선 사항 적용

이전 실행에서 이어받는 것은 `improvements_applied` 목록뿐입니다 (중복 방지).

## 개선 카테고리

Claude는 각 권고 사항에 다음 태그 중 하나를 붙입니다:

| 태그 | 의미 |
|------|------|
| `[test_coverage]` | 테스트 assertion 추가 또는 강화 |
| `[runner_code]` | 테스트 하네스 / conftest 로직 수정 |
| `[skill_md]` | SKILL.md 템플릿 또는 규칙 업데이트 |
| `[timeout]` | 타임아웃 값 조정 |
| `[tooling]` | 계정/할당량 문제 — 코드로 수정 불가, 자동 건너뜀 |

## 종료 사유

| 사유 | 의미 |
|------|------|
| `no_actionable_improvements` | 이번 iteration에서 Claude가 적용할 개선 사항을 찾지 못함 |
| `max_iterations_reached` | `--max-iterations` 한도에 도달 |
| `report_missing` | 리포트 파일이 생성되지 않음 (Claude 오류) |
| `result_not_written` | result JSON이 작성되지 않음 (Claude 오류) |

## 환경 변수

| 변수 | 설명 |
|------|------|
| `CLAUDE_BIN` | Claude 바이너리 경로 지정 (`--claude-bin`과 동일) |
| `CLAUDE_MODEL` | 사용할 모델 지정 (`--model`과 동일) |

## 사전 요구사항

- `python3`가 PATH에 있어야 함
- `claude` CLI 인증 완료 (`claude auth login`)
- `dx-agentic-gen`이 PATH에 있어야 함 (post-improvement drift guard용)
- `tests/test.sh`가 suite root에 존재해야 함
