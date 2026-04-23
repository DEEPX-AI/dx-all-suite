## 브레인스토밍 — 계획 전 Spec (HARD GATE)

superpowers `brainstorming` 스킬 또는 `/dx-brainstorm-and-plan` 사용 시:

1. **Spec 문서는 MANDATORY** — `writing-plans`로 전환하기 전에, spec 문서를
   `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`에 반드시 작성해야 합니다.
   spec을 건너뛰고 바로 계획 작성으로 가는 것은 위반입니다.
2. **사용자 승인 게이트는 MANDATORY** — spec 작성 후, 계획 작성으로 진행하기 전에
   사용자가 반드시 검토하고 승인해야 합니다. 관련 없는 사용자 응답 (예: 다른 질문에
   답변)을 spec 승인으로 처리하지 마세요.
3. **계획 문서는 spec을 참조해야 합니다** — 계획 헤더에는 승인된 spec 문서에 대한
   링크가 포함되어야 합니다.
4. **`/dx-brainstorm-and-plan` 선호** — 일반 superpowers `brainstorming` 스킬 대신
   프로젝트 레벨의 brainstorming 스킬을 사용하세요. 프로젝트 레벨 스킬에는
   도메인별 질문과 사전 점검이 포함되어 있습니다.
5. **규칙 충돌 확인은 MANDATORY** — brainstorming 중, agent는 사용자 요구사항이
   HARD GATE 규칙 (IFactory 패턴, skeleton-first, Output Isolation,
   SyncRunner/AsyncRunner)과 충돌하는지 반드시 확인해야 합니다. 충돌이 감지되면,
   agent는 brainstorming 중에 이를 해결해야 합니다 — 설계 spec에서 위반 요청을
   조용히 따르지 마세요. 위의 "규칙 충돌 해결"을 참조하세요.
