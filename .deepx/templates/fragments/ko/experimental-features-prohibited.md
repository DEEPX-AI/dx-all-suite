## 실험적 기능 — 금지

실험적이거나 존재하지 않는 기능을 제안, 제공 또는 구현하지 마세요. 여기에는 다음이
포함됩니다:
- "웹 기반 비주얼 컴패니언" (web-based visual companion)
- 로컬 URL 기반 다이어그램 뷰어 또는 대시보드
- 사용자가 시각화를 위해 로컬 URL을 열어야 하는 모든 기능
- 현재 도구 세트에 존재하지 않는 모든 기능

**Superpowers brainstorming skill 오버라이드**: superpowers `brainstorming` 스킬에는
"Visual Companion" 단계 (체크리스트의 2단계)가 포함되어 있습니다. 이 단계는 DEEPX
프로젝트에서 반드시 건너뛰어야 합니다. Visual companion은 우리 환경에 존재하지 않습니다.
brainstorming 체크리스트에서 "Offer visual companion"이라고 하면, 건너뛰고
"Ask clarifying questions" (3단계)로 직접 진행하세요.

기능이 존재하지 않으면, 존재하는 척하지 마세요. 검증된, 문서화된 기능만 사용하세요.

**Autopilot / autonomous mode 오버라이드**: 사용자가 부재 중일 때 (autopilot mode,
auto-response "work autonomously", 또는 `--yolo` 플래그), brainstorming 스킬의
"Ask clarifying questions" 단계는 "knowledge base 규칙에 따라 기본 결정 내리기"로
대체되어야 합니다. `ask_user`를 호출하지 마세요 — knowledge base 기본값을 사용하여
brainstorming spec 생성으로 바로 진행하세요. 이후의 모든 게이트 (spec 리뷰, 계획,
TDD, 필수 산출물, 실행 검증)는 예외 없이 여전히 적용됩니다.
