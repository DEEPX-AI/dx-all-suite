# dx-internal-pr-review-apply — 참고 문서

도구: `internal/tools/pr-review-apply/pr_review_apply.py` (stdlib python3, 테스트는 `tests/`).
English: `reference.md`. 도구 README: `internal/tools/pr-review-apply/README-KO.md`.

## 1. 명령과 출력

| 명령 | 출력 |
|---|---|
| `fetch --mhtml F` / `fetch --pr URL` | `PR #91: 10 threads, summary by dci -> .dx-pr-review/deepx-dx-all-suite-91` |
| `show [--pending]` | 헤더(제목, head sha, url), 봇 요약(앞 40줄), thread별 한 줄: `id  state  location  first line` |
| `decide --id r18833 --apply\|--skip\|--defer\|--no-action --note "…"` | `r18833: apply` — note가 reply 본문이 됨 |
| `commit-ref --sha S` | `abc1234d recorded on 5 apply decision(s)` |
| `replies` | apply/skip/defer thread마다 `### r18833 (path)` + reply 본문(no-action·이미 게시된 것은 제외) |
| `publish --pr URL [--retrigger rerequest\|comment\|both\|none] [--dry-run]` | `replies=5 rerequest=1 comment=0` |
| `publish --queue` | `publish-queue.json` + `replies.md` 생성, 저쪽에서 실행할 명령 출력 |
| `publish --queue-file Q` | `6 action(s) executed` |
| `probe-bot --pr URL` | JSON: `hooks[]`, `rerequest: possible\|not-subscribed\|unknown`, `comment: …`, `note` |

종료 코드: 0 정상 · 2 사용법/설정 오류(모르는 id, review dir 없음, token/gh 없음) · 그 외 python 오류.

## 2. 상태 파일 (`.dx-pr-review/<owner>-<repo>-<n>/`, gitignore)

```jsonc
// review.json
{ "schema": 1, "source": {"kind": "mhtml", "path": "…"} | {"kind": "rest", "url": "…"},
  "pr": {"host","owner","repo","number","url","title","head_sha","head_ref","base_ref"},
  "description": {"author","created_at","body"},          // PR 본문 (author = PR 작성자)
  "summary":     {"author","created_at","body"},          // 봇의 최상위 리뷰 comment
  "threads": [ {"id":"r18833","url","path","start","end","diff_context","author","created_at","body",
                "replies":[{"author","created_at","body"}], "resolved":false, "already_replied":false} ] }
// decisions.json
{ "r18833": {"decision":"apply","note":"…","decided_at":"2026-09-18T02:00:00Z","commit":"<sha>","published_at":"…"},
  "r18847": {"decision":"no-action","note":"칭찬","decided_at":"…"} }
// publish-queue.json
{ "schema":1, "store":"<dir>", "pr":{…}, "actions":[ {"kind":"reply","tid":"r18833","url":"…/pulls/91/comments/18833/replies","payload":{"body":"…"}},
                                                     {"kind":"rerequest","url":"…/pulls/91/requested_reviewers","payload":{"reviewers":["dci"]}} ] }
```

reply 본문은 `<!-- dx-pr-review-apply r<id> -->`로 시작한다. `fetch --pr`는 이미 그 표식이 있는 thread를
`already_replied`로 표시하고, `decisions.json.published_at`이 두 번째 게시를 막는다.

## 3. 폐쇄망 흐름 (개발 PC가 GHES에 닿지 않을 때)

1. Chrome에서 PR 페이지를 "웹페이지, 단일 파일"(`.mhtml`)로 저장해 개발 PC로 복사.
2. `fetch --mhtml` → 개발자와 triage → 수정 → **commit 1개** → `commit-ref` → `publish --queue`.
3. 개발자가 브랜치를 mirror에 push(개발자 몫).
4. 폐쇄망 PC: `ghes-sync.sh --reviewers dci`(또는 `sync.override.conf`의 `reviewers = dci`)가 GHES에 push하고
   봇을 재요청; 이어서 `publish --queue-file <복사한 .dx-pr-review/<dir>/publish-queue.json>`로 reply 게시
   (token 우선순위: `GHES_SYNC_DST_TOKEN` > `GH_ENTERPRISE_TOKEN` > `GHES_TOKEN` > `GH_TOKEN`, 없으면 `gh api`).
5. 저쪽에 도구가 없으면: `replies.md`를 thread에 붙여넣고 "Re-request review" 클릭.

## 4. 재트리거와 `probe-bot`

봇은 PR이 열릴 때 돌고 push에는 돌지 않는다. `rerequest`는 `pull_request.review_requested`(UI 버튼과 동일)를,
`comment`는 `--comment-text`를 보낸다(n8n hook이 `issue_comment`를 구독해야 함). `probe-bot`은 repo admin 권한
(`GET /repos/{o}/{r}/hooks`)이 필요하다: `possible` = hook이 그 이벤트를 구독(n8n 내부 필터는 알 수 없음),
`not-subscribed` = 그 트리거는 불가, `unknown` = admin 아님 → `rerequest` 유지.

## 5. Dogfood 기록 — PR #91 (2026-09-18)

이 skill의 첫 실전 실행. 결정과 단일 수정 commit은 개발 PC의 `.dx-pr-review/deepx-dx-all-suite-91/`과
commit 본문 `fix(review): PR #91 — …`에 기록되어 있다.
