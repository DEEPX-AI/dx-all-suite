## 자율 모드 보호 (MANDATORY)

사용자가 부재 중일 때 — autopilot mode, `--yolo` 플래그, 또는 시스템 auto-response
"The user is not available to respond" — 다음 규칙이 적용됩니다:

1. **"Work autonomously"는 "묻지 않고 모든 규칙을 따르라"는 의미이지, "규칙을 건너뛰라"는 의미가 아닙니다.**
   모든 필수 게이트가 여전히 적용됩니다: brainstorming spec, 계획, TDD, 필수 산출물,
   실행 검증, 자체 검증 확인.
   **SWE Process Gates의 필수 Skill 시퀀스도 포함됩니다** — autopilot에서도
   `/dx-skill-router` → `/dx-brainstorm-and-plan` → `/dx-tdd`를 interactive mode와
   동일하게 따라야 합니다. Autopilot mode는 이 시퀀스를 면제하지 않습니다.
2. **`ask_user`를 호출하지 마세요** — knowledge base 기본값과 문서화된 모범 사례를
   사용하여 결정하세요. autopilot에서 `ask_user`를 호출하면 한 턴을 낭비하며
   auto-response는 게이트 우회 권한을 부여하지 않습니다.
3. **사용자 승인 게이트 적응** — autopilot에서는 spec을 작성하고 knowledge base에
   대해 자체 검토하면 spec 승인 게이트가 충족됩니다. spec 자체를 건너뛰지 마세요.
4. **setup.sh 우선** — 애플리케이션 코드를 작성하기 전에 인프라 산출물
   (`setup.sh`, `config.json`)을 생성하세요. 이것은 autopilot에서 특히 중요합니다.
   누락된 종속성을 잡아줄 사람이 없기 때문입니다.
5. **실행 검증은 선택 사항이 아닙니다** — 생성된 코드를 실행하고 완료를 선언하기 전에
   작동하는지 확인하세요. autopilot에서는 오류를 잡아줄 사용자가 없습니다.
6. **시간 예산 인식** — Autopilot 세션에는 시간 제약이 있을 수 있습니다.
   효율적으로 행동을 계획하세요:
   - 컴파일 (ONNX → DXNN)은 5분 이상 걸릴 수 있습니다 — 일찍 시작하세요.
   - 시간이 부족하면, 실행 검증보다 산출물 생성을 우선시하세요 — 테스트되지 않은
     완전한 파일 세트가 테스트된 부분 세트보다 낫습니다.
   - 우선순위: `setup.sh` > `run.sh` > app 코드 > `verify.py` > session.log.
   - **컴파일 병렬 워크플로우 (HARD GATE)** — bash 명령으로 `dxcom` 또는
     `dx_com.compile()`을 실행한 후, 기다리지 마세요. 즉시 모든 필수 산출물을
     생성하세요: factory, app 코드, setup.sh, run.sh, verify.py. `.dxnn` 출력은
     다른 모든 산출물이 생성된 후에만 확인하세요. **이 규칙 위반은 세션 실패입니다.**
   - **컴파일을 위한 sleep-poll 금지** — `.dxnn` 파일을 polling하기 위해 `sleep`을
     루프에서 사용하지 마세요. 금지된 패턴:
     `for i in ...; do sleep N; ls *.dxnn; done`,
     `while ! ls *.dxnn; do sleep N; done`,
     반복적인 `ls *.dxnn` / `test -f *.dxnn` 확인과 그 사이의 대기.
     대신: 다른 모든 산출물을 먼저 생성한 후, `.dxnn` 파일이 존재하는지 한 번만
     확인하세요. 아직 존재하지 않으면, 컴파일이 완료될 것이라는 가정 하에 실행
     검증으로 진행하세요.
   - **필수 산출물은 컴파일과 독립적** — `setup.sh`, `run.sh`, `verify.py`, factory,
     app 코드는 `.dxnn` 파일이 존재할 필요가 없습니다. 알려진 모델 이름
     (예: `yolo26n.dxnn`)을 플레이스홀더 경로로 사용하여 생성하세요. 실행 검증만
     실제 `.dxnn`이 필요합니다.
7. **파일 읽기 도구 호출 최소화** — 이미 컨텍스트에 로드된 instruction 파일, agent
   문서, 스킬 문서를 다시 읽지 마세요. 불필요한 `cat` / `bash` 읽기는 각각 5-15초를
   낭비합니다. 시스템 프롬프트와 대화 이력에 있는 지식을 사용하세요.
