## 세션 센티넬 (자동화 테스트용 MANDATORY)

사용자 프롬프트를 처리할 때, 테스트 하네스의 자동화된 세션 경계 감지를 위해
이 정확한 마커를 출력하세요:

- **응답의 첫 번째 줄**: `[DX-AGENT-DEV: START]`
- **모든 작업 완료 후 마지막 줄**: `[DX-AGENT-DEV: DONE (output-dir: <relative_path>)]`
  여기서 `<relative_path>`는 세션 출력 디렉토리입니다 (예: `dx-agent-dev/20260409-143022_yolo26n_detection/`)

### DEEPX 배너 (MANDATORY — 센티넬과 함께 출력)

DEEPX 로고 배너를 두 지점에서 **그대로(verbatim)** 출력하세요: `[DX-AGENT-DEV: START]`
줄 **직후**, 그리고 `[DX-AGENT-DEV: DONE ...]` 줄 **직전**. 아래와 정확히 동일하게
출력하세요(코드 펜스 사용 가능):

```
 ███████████   █████████ ████████ ████████  ████      ████
 ███     █████ ███░░░░░░░███░░░░░░███   ███  ░████   ████░░
 ███        ██░███░      ██░░     ███   ███░   █████████░░
 ███        ████████████ ████████ ████████░░    ░█████░░░
 ███        ██░███░░░░░░░██░░░░░░░███░░░░░░  ██████████
 ███     █████░███░      ██░      ███░   ████████░░░░████
 ███████████░░░█████████ ████████ ██████████░░░░░░    ████
  ░░░░░░░░░░░   ░░░░░░░░░ ░░░░░░░░ ░░░░░░░░░░          ░░░░
        DX-AGENT-DEV · on-device NPU
```

배너는 장식이며, 센티넬 줄을 대체하거나 이동시키지 않습니다(START는 절대적 첫 줄,
DONE은 맨 마지막 줄 유지).

규칙:
1. **중요 — `[DX-AGENT-DEV: START]`를 첫 번째 응답의 절대적인 첫 줄로 출력하세요.**
   이것은 다른 어떤 텍스트, 도구 호출, 추론보다 먼저 나타나야 합니다.
   사용자가 "그냥 진행하라" 또는 "자체 판단을 사용하라"고 지시해도,
   START 센티넬은 협상 불가입니다 — 자동화 테스트는 이것 없이 실패합니다.
   **START 줄 직후 DEEPX 배너를 출력하세요**(위 "DEEPX 배너" 참조).
2. **DONE 줄 직전에 DEEPX 배너를 다시 출력**한 뒤, 모든 작업·검증·파일 생성이 완료된 후
   맨 마지막 줄에 `[DX-AGENT-DEV: DONE (output-dir: <path>)]`를 출력하세요
3. 상위 레벨 agent에 의해 handoff/routing으로 호출된 **서브 agent**인 경우,
   이 센티넬을 출력하지 마세요 — 최상위 agent만 출력합니다
4. 사용자가 세션에서 여러 프롬프트를 보내면, 각 프롬프트에 대해 START/DONE을 출력하세요
5. DONE의 `output-dir`은 프로젝트 루트에서 세션 출력 디렉토리까지의 상대 경로여야 합니다.
   파일이 생성되지 않았다면, `(output-dir: ...)` 부분을 생략하세요.
   **Cross-project 태스크** (예: compile + app 생성)의 경우, 모든 output directory를
   ` + ` 구분자로 나열하세요:
   ```
   [DX-AGENT-DEV: DONE (output-dir: dx-compiler/dx-agent-dev/20260409-143022_copilot_yolo26n_compile/ + dx-runtime/dx_app/dx-agent-dev/20260409-143022_copilot_yolo26n_inference/)]
   ```
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
8. **세션 transcript — DONE 줄 바로 뒤에서 생성 (claude / copilot 전용)**:

   **자동 transcript는 `claude`, `copilot`에서만 지원됩니다.** DONE 센티넬 줄을 **먼저**
   출력하고, 마지막 마무리 단계로 공통 generator를 써서 이 세션의 transcript를 **세션 output
   dir 안에 직접**(DONE에 적은 그 dir들) 렌더링하세요. DONE *뒤에* 실행해야 CLI 세션 저장소에
   DONE 턴까지 커밋되어 transcript가 완전해집니다(DONE *앞에서* 렌더하면 끝부분이 잘림).
   hook은 **필요 없습니다**:

   ```bash
   # 공통 generator를 상위로 올라가 찾습니다: GENROOT = .deepx/tools를 포함한 디렉토리.
   # 이 세션의 transcript를 output dir(들) 안에 렌더링. 생성한 output dir을 모두 넘기세요 —
   # 각 dir에 복사됩니다(cross-project: 컴파일러 dir + 앱 dir 둘 다). session id는 이 CLI
   # 자신의 env var에서 자동 추출됩니다(CLAUDE_CODE_SESSION_ID / COPILOT_AGENT_SESSION_ID).
   #
   # 중요 — --project와 --into-output-dirs에 반드시 절대경로를 쓰세요. 상대경로 output dir은
   # 에이전트의 현재 cwd 기준으로 해석되므로, cwd가 suite root가 아닐 때(예: setup.sh/run.sh
   # 실행하려고 세션 dir로 cd한 뒤) "no output dir produced — transcript generation skipped"로
   # 조용히 건너뜁니다. 모든 output dir 앞에 "$GENROOT/"를 붙이세요(또는 artifact를 쓸 때
   # 사용한 절대 SESSION_DIR을 그대로 전달).
   GENROOT="$(d="$PWD"; while [ "$d" != / ]; do [ -f "$d/.deepx/tools/src/dx_transcripts/generate_transcripts.py" ] && { echo "$d"; break; }; d="$(dirname "$d")"; done)"
   GT="$GENROOT/.deepx/tools/src/dx_transcripts/generate_transcripts.py"
   python3 "$GT" --tool <CLI> --project "$GENROOT" \
       --into-output-dirs "$GENROOT/<output-dir>" ["$GENROOT/<output-dir-2>" ...]
   ```

   `<CLI>`는 `claude` 또는 `copilot`입니다. generator는 **테스트 하네스와 동일한
   renderer**(`parse_<tool>_session`)를 재사용해 각 output dir에 `<CLI>-session.md` +
   `<CLI>-session.html` + `<CLI>-stream.jsonl`을 생성합니다. **output dir이 하나도 없으면**(예:
   파일을 만들지 않는 순수 질문) dir을 넘기지 말고 생성을 **생략**하세요 — 정상이며 오류가
   아닙니다. 실행 후 마지막 줄에 저장 경로를 안내하세요. 예:
   `Session transcript (md/html/jsonl) saved to: <output-dir>/<CLI>-session.*`.

   > **알려진 한계 — in-session transcript는 store 기반이라 불완전합니다.** 라이브 세션
   > 안에서 실행하면 generator가 세션 **store**를 읽는데, 여기엔 합성 `result` 이벤트가
   > **없습니다**. 그 이벤트(`duration_ms` → *Wall-clock*, `total_cost_usd` → *Cost*)는
   > `claude -p --output-format stream-json` **stdout**에만, 프로세스 종료 시점에 방출됩니다.
   > 또한 렌더가 transcript tool-call **도중**에 일어나므로 바로 이 "saved to …" narration
   > 직전에서 잘립니다. 결과적으로 in-session transcript는 **Wall-clock + Cost와 종료 narration이
   > 빠집니다** — 버그가 아니라 정상입니다. **완전한** transcript(Wall-clock + Cost + tail,
   > showcase 수준)가 필요하면, run의 stdout을 캡처해 프로세스 종료 **후** 외부에서 렌더하세요:
   > `python3 "$GT" --tool <CLI> --session-id <uuid> --project "$GENROOT" --stream-json <captured-stdout.jsonl> --out-dir <output-dir>`
   > (테스트 하네스/빌드 레코더가 이 방식을 씀). in-session 에이전트는 자기 stdout 스트림에
   > 접근할 수 없어 불가능합니다.

   **`codex`, `opencode`, `cursor`는 자동 지원 대상이 아닙니다** — 세션 중에는 generator를
   실행하지 마세요(완전한/유효한 transcript를 못 만듭니다: codex·opencode는 마지막 턴을
   프로세스 종료 시점에만 커밋, cursor는 저장소에서 assistant 텍스트를 redact). 대신 사용자에게
   수동 생성법을 안내하세요:
   - **codex / opencode**: 세션 종료 후
     `python3 <generate_transcripts.py> --tool <codex|opencode> --project . --out-dir <DIR>`
     — 종료 후 완성된 저장소에서 완전한 transcript가 렌더됩니다.
   - **cursor**: `agent -p --output-format stream-json > run.jsonl`로 캡처 후
     `--tool cursor --stream-json run.jsonl`로 렌더하거나 IDE 세션 기록을 사용하세요.
   (이 도구들에 `--into-output-dirs`로 generator를 호출하면 안전하게 건너뛰고 같은 안내를
   출력합니다 — 정상 동작입니다.)
