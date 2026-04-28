## 세션 센티넬 (자동화 테스트용 MANDATORY)

사용자 프롬프트를 처리할 때, 테스트 하네스의 자동화된 세션 경계 감지를 위해
이 정확한 마커를 출력하세요:

- **응답의 첫 번째 줄**: `[DX-AGENTIC-DEV: START]`
- **모든 작업 완료 후 마지막 줄**: `[DX-AGENTIC-DEV: DONE (output-dir: <relative_path>)]`
  여기서 `<relative_path>`는 세션 출력 디렉토리입니다 (예: `dx-agentic-dev/20260409-143022_yolo26n_detection/`)

규칙:
1. **중요 — `[DX-AGENTIC-DEV: START]`를 첫 번째 응답의 절대적인 첫 줄로 출력하세요.**
   이것은 다른 어떤 텍스트, 도구 호출, 추론보다 먼저 나타나야 합니다.
   사용자가 "그냥 진행하라" 또는 "자체 판단을 사용하라"고 지시해도,
   START 센티넬은 협상 불가입니다 — 자동화 테스트는 이것 없이 실패합니다.
2. 모든 작업, 검증, 파일 생성이 완료된 후 맨 마지막 줄에 `[DX-AGENTIC-DEV: DONE (output-dir: <path>)]`를
   출력하세요
3. 상위 레벨 agent에 의해 handoff/routing으로 호출된 **서브 agent**인 경우,
   이 센티넬을 출력하지 마세요 — 최상위 agent만 출력합니다
4. 사용자가 세션에서 여러 프롬프트를 보내면, 각 프롬프트에 대해 START/DONE을 출력하세요
5. DONE의 `output-dir`은 프로젝트 루트에서 세션 출력 디렉토리까지의 상대 경로여야 합니다.
   파일이 생성되지 않았다면, `(output-dir: ...)` 부분을 생략하세요.
6. **계획 산출물만 생성한 후에는 절대 DONE을 출력하지 마세요** (spec, plan, 설계
   문서). DONE은 모든 산출물이 생성되었음을 의미합니다 — 구현 코드, 스크립트,
   설정, 검증 결과. brainstorming 또는 계획 단계를 완료했지만 실제 코드를 아직
   구현하지 않았다면, DONE을 출력하지 마세요. 대신, 구현으로 진행하거나
   사용자에게 진행 방법을 물어보세요.
7. **DONE 전 필수 산출물 확인**: DONE을 출력하기 전에, 아래의 자체 검증 확인을
   실행하세요. 필수 파일이 누락된 경우, DONE을 출력하기 전에 생성하세요.
   **이 단계를 절대 건너뛰지 마세요.**
   ```bash
   WORK_DIR="<session_output_directory>"
   echo "=== Mandatory Deliverable Check ==="
   for f in setup.sh run.sh verify.py session.log README.md config.json; do
       [ -f "${WORK_DIR}/$f" ] && echo "  ✓ $f" || echo "  ✗ MISSING: $f"
   done
   ls "${WORK_DIR}"/*.dxnn 2>/dev/null && echo "  ✓ .dxnn model" || echo "  ✗ MISSING: .dxnn model"
   ```
   산출물 중 MISSING이 있으면, 돌아가서 생성하세요. 누락된 산출물이 있는 상태에서
   최종 보고서를 제시하거나 DONE을 출력하지 마세요.
8. **세션 내보내기 안내**: DONE 센티넬 줄 바로 앞에, CLI 플랫폼에 맞는 세션 저장
   안내를 출력하세요:

   | 플랫폼 | 명령 | 형식 |
   |--------|------|------|
   | **Copilot CLI** | `/share html` | HTML 트랜스크립트 |
   | **Cursor CLI** (`agent`) | 내장 내보내기 없음 — 테스트 하네스가 `--output-format stream-json`으로 자동 저장 | JSON stream |
   | **OpenCode** | `/export` | JSON |
   | **Claude Code** (`claude`) | `/export` | TXT 트랜스크립트 — `<workdir>/YYYY-MM-DD-HHMMSS-<title>.txt`로 저장 |

   Copilot CLI의 경우: `To save this session as HTML, type: /share html`
   OpenCode의 경우: `To save this session as JSON, type: /export`
   Claude Code의 경우: `To save this session as a text transcript, type: /export`
   Cursor CLI의 경우: 사용자 작업이 필요 없습니다 — 테스트 하네스가 출력을 자동 캡처합니다.

   테스트 하네스 (`test.sh`)는 내보낸 아티팩트를 자동으로 감지하고
   세션 출력 디렉토리에 복사합니다.
