## Experimental Features — Prohibited

Do NOT offer, suggest, or implement experimental or non-existent features. This includes:
- "웹 기반 비주얼 컴패니언" (web-based visual companion)
- Local URL-based diagram viewers or dashboards
- Any feature requiring the user to open a local URL for visualization
- Any capability that does not exist in the current toolset

**Superpowers brainstorming skill override**: The superpowers `brainstorming` skill
includes a "Visual Companion" step (step 2 in its checklist). This step MUST be
SKIPPED in the DEEPX project. The visual companion does not exist in our environment.
When the brainstorming checklist says "Offer visual companion", skip it and proceed
directly to "Ask clarifying questions" (step 3).

If a feature does not exist, do not pretend it does. Stick to proven, documented
capabilities only.

**Autopilot / autonomous mode override**: When the user is absent (autopilot mode,
auto-response "work autonomously", or `--yolo` flag), the brainstorming skill's
"Ask clarifying questions" step MUST be replaced with "Make default decisions per
knowledge base rules". Do NOT call `ask_user` — skip straight to producing the
brainstorming spec using knowledge base defaults. All subsequent gates (spec review,
plan, TDD, mandatory artifacts, execution verification) still apply without exception.
