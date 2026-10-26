---
name: dx-internal-pr-review-apply
description: 'Internal skill — process the code-review comments a bot (dci) left on a GHES PR: read them (saved .mhtml or
  REST), verify each against the code, ask the developer apply/skip per item, apply the accepted ones in one commit, reply
  per thread and re-request the reviewer. Triggers (EN): "apply PR review", "handle review comments", "dci review", "PR #<n>
  review". Triggers (KO): "코드리뷰 반영", "리뷰 코멘트 처리", "PR 리뷰 결과 적용", "dci 리뷰".  <!-- KOREAN-OK: KO trigger phrases enable Korean-prompt
  auto-detection --> Explicit: /dx-internal-pr-review-apply.'
---

<!-- Thin Claude Code wrapper — canonical skill doc lives in .deepx/ -->

Read and follow the complete skill documentation at `.deepx/skills/dx-internal-pr-review-apply/SKILL.md`.
