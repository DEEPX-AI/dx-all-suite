---
name: dx-internal-pr-review-apply
description: >
  Internal skill — process the code-review comments a bot (dci) left on a GHES PR: read them
  (saved .mhtml or REST), verify each against the code, ask the developer apply/skip per item,
  apply the accepted ones in one commit, reply per thread and re-request the reviewer.
  Triggers (EN): "apply PR review", "handle review comments", "dci review", "PR #<n> review".
  Triggers (KO): "코드리뷰 반영", "리뷰 코멘트 처리", "PR 리뷰 결과 적용", "dci 리뷰".  <!-- KOREAN-OK: KO trigger phrases enable Korean-prompt auto-detection -->
  Explicit: /dx-internal-pr-review-apply.
---

# Skill: dx-internal-pr-review-apply

> Internal-business skill (RIGID). Drives `internal/tools/pr-review-apply/pr_review_apply.py`; the
> **judgement** (is a thread a change request or praise/info? apply or not?) is the agent's, made from
> the thread text and the current code — never from emoji or headings. Follows `dx-swe-receiving-review`:
> verify before implementing, no performative agreement. Detail: `reference.md` / `reference-KO.md`.

## Pre-flight (STOP on failure)

1. `internal/tools/pr-review-apply/` exists (internal checkout). Missing → say this skill is internal-only and stop.
2. Input: `--mhtml <file>` (offline) or `--pr <url>` (needs a GHES token or a logged-in `gh`). Ask which if neither is given.
3. `git merge-base --is-ancestor <head_sha> HEAD` — the checkout must contain the reviewed head. Otherwise STOP and say what to fetch.

## Procedure

1. `fetch` → `show`. Present the full table (summary comment + every thread, file order).
2. Triage loop — present the verified analysis of every change request first, then ask: one thread per
   question, at most four questions per prompt, most severe first (items that exist only in the summary
   comment use the id `summary`):
   - Read `path:start-end` in the **current** code. Verify the claim.
   - If it is praise/information (no change requested): `decide --id <id> --no-action --note "<why>"` and move on — **do not ask**.
   - Else present 3–5 lines: claim · what the code actually does · impact · recommendation (apply/skip) · cost.
     Then `AskUserQuestion` with options apply / skip / defer / custom instruction (shown to the developer in
     their language, e.g. 적용 / 미적용 / 보류 / 직접 지시). Record with `decide`.  <!-- KOREAN-OK: option labels the developer sees -->
   - Autopilot (user absent): take your own recommendation; defects → apply, style/comment-only → defer.
3. Apply — per accepted item: classify the file (Q1–Q3: `.deepx/` canonical → `run_all.sh generate` + `check`),
   `dx-swe-tdd` (RED first), edit, verify immediately. When a canonical asset changes (e.g.
   `.deepx/templates/assets/harness_bootstrap.sh`) the 4 sub-repos regenerate — commit those too and say so.
4. **One commit** for all accepted items: `fix(review): PR #<n> — <k> review items` with one body line per item
   `r<id> <path>:<line> — <what changed>` and the thread URL. Then `commit-ref --sha <sha>`.
5. Verify: `bash .deepx/tools/scripts/harness_gate.sh all` + the changed tool's tests. Show the output.
6. Publish: GHES reachable + token → `publish --pr <url>` (replies, then re-request `dci`). Not reachable →
   `publish --queue`, then tell the user: (a) push to mirror (their step) → on the closed-network machine
   `ghes-sync.sh` (with `reviewers = dci` it re-requests) and `publish --queue-file <path>`; or (b) paste
   `replies.md` by hand and click "Re-request review".

## Hard rules

- Never classify threads by emoji/severity markers; read the text.
- Never reply to a thread that was judged no-action.
- Never push; `git-operations-user-handles` applies.
- `.dx-pr-review/` is gitignored state — never commit it.
