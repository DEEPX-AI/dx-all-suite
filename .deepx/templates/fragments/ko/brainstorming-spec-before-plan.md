## 브레인스토밍 — 계획 전 Spec (HARD GATE)

**모든** brainstorming 진입점에 적용됩니다 — superpowers `brainstorming` 스킬,
`/dx-swe-brainstorm`, `/dx-agent-brainstorm`. 어느 것이 존재하는지는 레벨에 따라
다릅니다: suite 는 둘 다 제공하고, 하위 프로젝트는 `/dx-agent-brainstorm` 만
제공합니다. 어느 것을 호출했는지에 따라 spec 게이트가 면제되지 않습니다.

1. **Spec 문서는 MANDATORY** — `writing-plans`로 전환하기 전에, spec 문서를
   `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`에 반드시 작성해야 합니다.
   spec을 건너뛰고 바로 계획 작성으로 가는 것은 위반입니다.
2. **사용자 승인 게이트는 MANDATORY** — spec 작성 후, 계획 작성으로 진행하기 전에
   사용자가 반드시 검토하고 승인해야 합니다. 관련 없는 사용자 응답 (예: 다른 질문에
   답변)을 spec 승인으로 처리하지 마세요.
   **autopilot (사용자 부재, `--yolo`, 자동 응답) 에서는 spec 을 작성하고 knowledge
   base 기준으로 자체 검토하는 것으로 이 게이트가 충족됩니다** — Autopilot Mode Guard
   를 참조하세요. 검토자가 없다고 해서 spec 작성이 면제되지 않으며, 진행이 막히지도
   않습니다.
3. **계획 문서는 spec을 참조해야 합니다** — 계획 헤더에는 승인된 spec 문서에 대한
   링크가 포함되어야 합니다.
4. **프로젝트 레벨 brainstorming 스킬 선호** — suite 에서는 `/dx-swe-brainstorm`,
   하위 프로젝트에서는 `/dx-agent-brainstorm` 을 일반 superpowers `brainstorming`
   스킬 대신 사용하세요. 프로젝트 레벨 스킬에는 도메인별 질문과 사전 점검이
   포함되어 있습니다. 해당 레벨이 제공하는 스킬을 호출했다고 해서 위의 spec
   게이트가 면제되지는 않습니다.
5. **규칙 충돌 확인은 MANDATORY** — brainstorming 중, agent는 사용자 요구사항이
   HARD GATE 규칙 (IFactory 패턴, skeleton-first, Output Isolation,
   SyncRunner/AsyncRunner)과 충돌하는지 반드시 확인해야 합니다. 충돌이 감지되면,
   agent는 brainstorming 중에 이를 해결해야 합니다 — 설계 spec에서 위반 요청을
   조용히 따르지 마세요. 위의 "규칙 충돌 해결"을 참조하세요.
