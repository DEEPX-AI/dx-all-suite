# dx-internal-pr-review-apply — reference

Tool: `internal/tools/pr-review-apply/pr_review_apply.py` (stdlib python3, tests under `tests/`).
Korean: `reference-KO.md`. Tool README: `internal/tools/pr-review-apply/README.md`.

## 1. Commands and what they print

| Command | Output |
|---|---|
| `fetch --mhtml F` / `fetch --pr URL` | `PR #91: 10 threads, summary by dci -> .dx-pr-review/deepx-dx-all-suite-91` |
| `show [--pending]` | header (title, head sha, url), the reviewer summary (first 40 lines), then one row per thread: `id  state  location  first line` |
| `decide --id r18833 --apply\|--skip\|--defer\|--no-action --note "…"` | `r18833: apply` — the note becomes the reply text |
| `commit-ref --sha S` | `abc1234d recorded on 5 apply decision(s)` |
| `replies` | `### r18833 (path)` + the reply body per apply/skip/defer thread (no-action and already-published skipped) |
| `publish --pr URL [--retrigger rerequest\|comment\|both\|none] [--dry-run]` | `replies=5 rerequest=1 comment=0` |
| `publish --queue` | writes `publish-queue.json` + `replies.md`, prints the command to run on the far side |
| `publish --queue-file Q` | `6 action(s) executed` |
| `probe-bot --pr URL` | JSON: `hooks[]`, `rerequest: possible\|not-subscribed\|unknown`, `comment: …`, `note` |

Exit codes: 0 ok · 2 usage/config (unknown id, no review dir, no token/gh) · non-zero from python otherwise.

## 2. State files (`.dx-pr-review/<owner>-<repo>-<n>/`, gitignored)

```jsonc
// review.json
{ "schema": 1, "source": {"kind": "mhtml", "path": "…"} | {"kind": "rest", "url": "…"},
  "pr": {"host","owner","repo","number","url","title","head_sha","head_ref","base_ref"},
  "description": {"author","created_at","body"},          // the PR body (author = PR author)
  "summary":     {"author","created_at","body"},          // the bot's top-level review comment
  "threads": [ {"id":"r18833","url","path","start","end","diff_context","author","created_at","body",
                "replies":[{"author","created_at","body"}], "resolved":false, "already_replied":false} ] }
// decisions.json
{ "r18833": {"decision":"apply","note":"…","decided_at":"2026-09-18T02:00:00Z","commit":"<sha>","published_at":"…"},
  "r18847": {"decision":"no-action","note":"praise","decided_at":"…"} }
// publish-queue.json
{ "schema":1, "store":"<dir>", "pr":{…}, "actions":[ {"kind":"reply","tid":"r18833","url":"…/pulls/91/comments/18833/replies","payload":{"body":"…"}},
                                                     {"kind":"rerequest","url":"…/pulls/91/requested_reviewers","payload":{"reviewers":["dci"]}} ] }
```

Reply bodies start with `<!-- dx-pr-review-apply r<id> -->`; `fetch --pr` marks threads that already carry
one as `already_replied`, and `decisions.json.published_at` stops a second post.

## 3. Closed-network flow (developer PC cannot reach GHES)

1. Save the PR page in Chrome as "Webpage, Single File" (`.mhtml`), copy it to the developer PC.
2. `fetch --mhtml` → triage with the developer → fix → **one commit** → `commit-ref` → `publish --queue`.
3. Developer pushes the branch to the mirror (their step).
4. Closed-network machine: `ghes-sync.sh --reviewers dci` (or `reviewers = dci` in `sync.override.conf`)
   pushes to GHES and re-requests the bot; then `publish --queue-file <copied .dx-pr-review/<dir>/publish-queue.json>`
   posts the replies (token chain: `GHES_SYNC_DST_TOKEN` > `GH_ENTERPRISE_TOKEN` > `GHES_TOKEN` > `GH_TOKEN`, else `gh api`).
5. No tooling on the far side: paste `replies.md` into the threads, click "Re-request review".

## 4. Re-trigger and `probe-bot`

The bot runs on PR open, not on push. `rerequest` sends `pull_request.review_requested` (the UI button);
`comment` posts `--comment-text` (needs an `issue_comment` subscription on the n8n hook). `probe-bot` needs
repo-admin rights (`GET /repos/{o}/{r}/hooks`): `possible` = the hook is subscribed to that event (n8n's
own filter cannot be seen), `not-subscribed` = that trigger cannot work, `unknown` = no admin access → keep `rerequest`.

## 5. Dogfood record — PR #91 (2026-09-18)

First real run of this skill; the decisions and the single fix commit are recorded in
`.dx-pr-review/deepx-dx-all-suite-91/` on the developer PC and in the commit body `fix(review): PR #91 — …`.
