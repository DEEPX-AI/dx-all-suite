## 필수 산출물

모든 컴파일 또는 앱 생성 세션은 DONE을 출력하기 전에 세션 출력 디렉토리
(`dx-agent-dev/<session_id>/`)에 다음 파일을 반드시 생성해야 합니다.
이것은 **모든 작업 유형**에 적용됩니다 — compiler-only, app-only, cross-project.

| 파일 | 목적 | 필요 시점 |
|------|------|-----------|
| `setup.sh` | 환경 설정 (sanity check, dxcom 설치, venv, pip 종속성) | 항상 |
| `run.sh` | venv 활성화와 함께 원클릭 inference 실행기 | 항상 |
| `README.md` | 세션 요약, 빠른 시작, 파일 목록 | 항상 |
| `verify.py` | ONNX vs DXNN 수치 비교 | 컴파일 포함 시 |
| `session.log` | 실제 명령 출력 로그 (직접 작성한 요약이 아님) | 항상 |
| `config.json` | dxcom 컴파일 설정 | 컴파일 포함 시 |
| `*.dxnn` | 컴파일된 모델 바이너리 | 컴파일 포함 시 |
| `*.onnx` / `*.pt` | 생성한 `.dxnn` 옆에 보존하는 원본 모델 | 컴파일 포함 시 |

이것들은 애플리케이션별 산출물 (factory/inference 패턴이 있는 Python 파일,
GStreamer pipeline 코드 등)에 추가됩니다.

각 서브 프로젝트도 agent/skill 문서에서 이러한 파일의 템플릿을 정의합니다
(예: **dx-compiler** 저장소 `.deepx/agents/` 의 dx-dxnn-compiler.md Phase 5.5).

### Cross-project suite 작업 — pre-DONE `.dxnn` 확인 (HARD GATE, REC-X4)

**컴파일이 포함된 모든 작업**에서 DONE sentinel을 출력하기 전에, `.dxnn` 파일이
compiler session 디렉토리에 존재하는지 확인하세요:

```bash
COMPILER_SESSION="<compiler_session_dir>"   # 예: dx-compiler/dx-agent-dev/20260430-..._compile
test -f "${COMPILER_SESSION}/yolo26n.dxnn" \
  || { echo "BLOCKED: yolo26n.dxnn not found — 컴파일이 아직 실행 중입니다. compile.pid가 종료될 때까지 기다리세요."; exit 1; }
```

`yolo26n.dxnn`이 없는 상태에서 DONE을 출력하면 백그라운드 컴파일이 나중에 완료되더라도
`test_dxnn_compiled`가 실패합니다 (test harness는 DONE 시점에 파일을 수집합니다).
Phase 5.8을 참조하세요: **dx-compiler** 저장소 `.deepx/agents/` 의 dx-dxnn-compiler.md.

**모든 산출물은 이번 세션이 직접 생성해야 합니다.** 다른 세션의 출력 디렉터리에서
파일을 복사해 — 다른 agent 의 것이든, 다른 회차의 것이든, 본인의 이전 세션이든 —
이번 세션의 결과물로 제출하는 것은 수정 여부와 무관하게 금지됩니다. 같은 결과에
이르는 지름길이 아닙니다: 이 디렉터리의 목적은 이번 실행이 무엇을 만들었는지
보여주는 것입니다. `session.log` 에 이미 적용되는 규칙(heredoc 금지, `echo` 금지,
손으로 쓴 요약 금지)이 표의 모든 파일에 동일하게 적용됩니다. 전제 조건이 빠졌다면
그 사실을 알리고 멈추세요 — 빌려오지 마세요.
