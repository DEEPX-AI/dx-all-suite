# `showcase_repro` — Showcase 재현성 검증

각 `dx-agent-dev-showcase/<name>/`의 **verbatim 프롬프트**를 autopilot coding agent(claude-code,
cursor, …)로 재실행해, 결과가 체크인된 showcase와 *동등(equivalent)* 한지 등급 평가합니다.
답하려는 질문: "엔드유저가 showcase 프롬프트를 입력하면, 동등하고 self-contained·portable한
결과를 얻는가?"

이는 `../test_agent_e2e_scenarios/`(짧은 하드코딩 프롬프트로 에이전트 하니스 기능을 pass/fail
smoke 검사)의 **평가용 짝**입니다. 둘은 **공존**합니다 — 목적이 다름: verbatim 재현 등급 vs
기능 smoke.

## 파일
| 파일 | 역할 |
|------|------|
| `showcase_registry.py` | 단일 소스: showcase별 `prompt`(verbatim) · `route` · `checker` · `ground_truth` · `active` |
| `checks.py` | 타입별 checker(`export`/`squat`/`stretch`/`ocr`/`generic_app`/`retrain_eval`) → 3 tier(artifacts/gates/metrics) + cross-cutting **portability** gate; `evaluate_showcase()` → verdict |
| `isolation.py` | 드라이버가 쓰는 Output-Isolation guard helper(escaping-symlink + source-reference) |
| `run_repro.py` | N-showcase × M-agent 매트릭스 드라이버 → archive `report.md` + `results.json`; e2e conftest autopilot 러너 재사용; B2 Output-Isolation guard + 자동 복원 |
| `test_checks.py` | 단위 테스트 — 각 원본 showcase가 EQUIVALENT로 self-verify(checker 회귀 가드) |
| `test_repro_scenarios.py` | **얇은 pytest 래퍼**(`DX_REPRO_RUN=1`로 opt-in) — (active showcase × agent)당 1개 test가 `verdict != FAILED` assert, CI 게이팅용 |

## Verdict tier
`EQUIVALENT`(3 tier 모두 tolerance 내) · `DEGRADED`(artifacts ok, gate/metric 일부 미달) ·
`FAILED`(핵심 산출물 누락/손상) · `BLOCKED`(agent CLI 불가 — env 문제이지 재현 실패 아님).
cross-cutting **portability** gate(정적 + suite 밖 복사 실행)와 **B2 Output-Isolation
guard**(source dir 쓰기 자동 복원)가 모든 showcase에 적용됩니다.

## 한 사이클 실행
```bash
# 빠름: checker가 커밋된 원본을 여전히 인식하는지 확인
python -m pytest .deepx/e2e/showcase_repro/test_checks.py -q

# 평가 매트릭스 (실제 autopilot 실행 → archive 리포트)
python .deepx/e2e/showcase_repro/run_repro.py \
    --showcases mini-game-squat-fitness,ultralytics-yolo-deepx-export \
    --agents claude-code,cursor \
    --archive "$HOME/shared/coding_agent_diff_report/showcase_repro/<label>"
#   --dry-run  : 매트릭스만 출력, 실행 안 함
# CI 게이팅 (opt-in, heavy): DX_REPRO_RUN=1 python -m pytest .deepx/e2e/showcase_repro/test_repro_scenarios.py
```
리포트/raw 번들은 `$DX_MODEL_EVAL_ARCHIVE`(기본 `~/shared/coding_agent_diff_report`)에 저장 —
worktree 로컬 `dx-agent-dev/` 출력은 gitignore되어 cleanup 시 사라집니다.

## showcase 추가 / 갱신 (릴리즈마다)
1. `showcase_registry.py`에 항목 추가/갱신: **verbatim** 프롬프트(showcase의 `claude-code-session.md`
   에서 — 축약된 README가 아님; full 프롬프트가 입력 경로를 숨길 수 있음), `route`, `checker`,
   `active=True`. code/model 입력 경로는 **suite-root 상대**(`dx-agent-dev-showcase/<name>/sample/...`)
   로; 빌드 시점 `/tmp/...` 경로는 fresh 엔드유저에게서 깨집니다.
2. 새 앱 타입이면 `checks.py`에 `checker` 구현(ground truth는 showcase의 `report.md`/
   `metrics.json`/`session.log`에서) 후 `_CHECKERS`에 등록.
3. `test_checks.py`에 RED 단위 테스트 추가: 커밋된 원본이 EQUIVALENT로 self-verify.
4. `run_repro.py --showcases <name> --agents claude-code,cursor` 실행.

## 주의
- **기준은 self-contained & portable**: 생성된 앱은 suite 밖으로 복사해도 실행되어야 함 — pipeline
  (`./common`, fork의 `engine/`/`rapid_doc/`)을 세션 안으로 vendoring; showcase를 in-place import
  하거나 source dir을 symlink하거나 model dir을 source로 향하게 하지 말 것.
- 에이전트를 위해 **sanity/setup을 미리 실행하지 말 것** — 에이전트가 프롬프트 안에서 prereq를
  해결하는지가 검증 대상.
- **Retrain showcase**는 GPU(40-epoch train) + NPU(INT8) 필요; 각 ~1h+; "equivalent" =
  4-way 표(base/retrained × fp32-GPU/INT8-NPU mAP+FPS)가 문서화된 accuracy-gain 추세로 재현됨,
  정확한 수치 일치 아님(training은 비결정적).
- **Cross-project(suite) showcase**는 산출물을 compiler 세션 + app 세션 dir로 분할함 — 드라이버가
  cell의 output dir **합집합**으로 채점하고, 에이전트가 세션 ID를 타 에이전트명으로 오라벨해도
  mtime fallback이 dir을 복구함(따라서 진짜 미완 run은 여전히 fail, 단순 분할/오라벨은 정상 채점).
