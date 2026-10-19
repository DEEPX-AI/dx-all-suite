# 오프라인 계약

이 스튜디오의 어느 부분이 인터넷 없이 동작해야 하는가.

## 왜 이 문서가 생겼나

개발이 폐쇄망에서 일반망으로 옮겨가면서 안전장치가 하나 사라졌다. 전에는 **개발
환경 자체가 게이트**였다 — 인터넷이 없으니 인터넷에 의존하는 코드를 쓸 수가 없었다.
이제 쓸 수 있고, 처음 드러나는 곳은 PR 을 올리는 폐쇄망 PC 다.

고객도 폐쇄망에 배치한다. 그래서 이것은 개발 편의가 아니라 제품 요건이다.

문제는 경계가 코드에 흩어져 있고 어디에도 적혀 있지 않았다는 것이다:

* `shared/about_sync.py` — docstring 에 "general-net only" 라고 스스로 적어둠
* `dx_app/core/modelzoo.py:82` — "air-gapped/offline box 에서는 실패하므로 6초로 제한"
* `shared/runtime_installer.py`, `shared/chat/providers.py`,
  `dx_modelzoo/metadata/adapters.py` — 전부 외부로 나감

각 파일은 자기 사정을 안다. 그런데 **새 의존이 들어왔을 때 그것이 위반인지 판단할
근거**가 없었다. 무엇을 막을지 모르면 게이트를 만들 수 없다.

## 전제 — 확인이 필요하다

`dx_app` 은 "엣지 AI: 오프라인 운영 지원 — 인터넷 없이도 동작" 이라고 말한다
(`static/js/i18n.js:1022`). 이 문서는 그것이 **추론**을 가리킨다고 읽는다 — NPU 는
로컬에서 돌므로. 스튜디오 전체(모델 탐색·다운로드·에이전트·챗)는 인터넷이 필요한
것이 맞다고 본다.

**이 전제가 틀리면 아래 등급표 전체가 틀린다.** 숨기지 않고 여기 적어 둔다.

## 세 등급

### 필수 — 인터넷 없이 동작해야 한다

| 무엇 | 실측 (2026-09-18, 외부 소켓 차단) |
|---|---|
| 아홉 모듈 기동 + 첫 화면 | 전부 200 |
| 로컬 카탈로그 (`/api/catalog`, `/api/categories`) | 200 |
| 설치된 모델 목록, 데모 목록, 설정 상태 | 200 |
| NPU 하드웨어 상태 | 200 |
| 벤치마크 결과, 저장된 파이프라인, 쇼케이스 | 200 |
| 에이전트 모델 목록 (`/api/agent/models`) | 200 — 로컬 데이터다 |

### degrade — 없으면 **명확히** 실패해야 한다

무응답이나 무한 대기는 실패가 아니라 고장이다. 판단 가능한 응답을 줘야 한다.

| 무엇 | 실측 |
|---|---|
| ModelZoo 탐색 (`/api/modelzoo/list?source=public`) | `200 {"ok": false, "error": …}` — 옳다 |
| 아티팩트 해석 (`/api/catalog/<id>/artifacts/<kind>`) | `302 → sdk.deepx.ai` — 옳다 |

아티팩트 건은 한 번 결함으로 적었다가 정정했다. 외부 소켓을 막고 `urlopen` 으로
부르면 `URLError` 가 나서 "응답이 없다" 고 읽었는데, `urlopen` 이 리다이렉트를
따라가다 실패한 것이었다. 리다이렉트를 따라가지 않고 보면 서버는 차단 상태에서도
302 를 제대로 낸다. 인터넷 없이 CDN 에 못 닿는 것은 고장이 아니라 사실이고,
다운로드 자체는 아래 "네트워크" 등급이다.

측정 도구가 무엇을 하는지 모르면 측정값을 잘못 읽는다 — 이 문서의 실측 열을 다시
잴 때 기억할 일이다.

### 네트워크 — 인터넷이 있어야 하는 기능

없다고 결함이 아니다. 다만 **없을 때 무엇이 안 되는지 말해야** 한다.

| 무엇 | 어디 |
|---|---|
| 모델 다운로드 | `dx_app/core/modelzoo.py` (sdk.deepx.ai) |
| 카탈로그 동기화 | `dx_modelzoo/metadata/adapters.py` |
| 챗 / SDK Help | `shared/chat/providers.py` |
| About 뉴스 갱신 | `shared/about_sync.py` — 이미 "general-net only" |
| 런타임 설치 | `shared/runtime_installer.py` |
| Agent Dev 의 실제 실행 | CLI 에이전트가 각자 API 를 부른다 |

## 새 코드를 쓸 때

바깥으로 나가는 호출을 추가한다면 세 가지 중 하나를 해야 한다:

1. **필수** 경로라면 — 나가지 않는다. 로컬에 있어야 한다.
2. **degrade** 경로라면 — 실패를 잡아 판단 가능한 응답으로 바꾼다. 타임아웃을 건다.
3. **네트워크** 기능이라면 — 위 표에 한 줄 추가하고, 없을 때 화면이 무엇을 말하는지
   정한다.

## 무엇이 이것을 지키나

`run_ci.sh` 의 오프라인 스테이지가 외부 소켓을 막고 블로킹 스위트를 돌린다(약 30초).
네트워크가 **필요한** 테스트는 `OFFLINE_ALLOWED` 에 이름이 있어야 하고, 그 목록은
`tests/shared/test_ci_contracts.py` 가 줄어드는 방향으로만 허용한다 —
`QUARANTINE` / `BROWSER_QUARANTINE` 과 같은 구조다.

**테스트가 통과하는 것과 제품이 오프라인에서 동작하는 것은 다르다.** 위 등급표의
실측 열이 그 간극을 메우는 부분이고, 제품 동작이 바뀌면 그 열도 다시 재야 한다.

## 알려진 문제 — offline 스테이지가 드물게 SIGSEGV 로 죽는다

**실측 (2026-09-21)**: `bash scripts/run_ci.sh --offline` 5회 중 1회.
직접 같은 pytest 명령을 돌리면 2회 모두 깨끗했고, `run_ci.sh --offline` 를 연속
3회 돌려도 깨끗했다. 재현 조건을 아직 특정하지 못했다.

```
Fatal Python error: Segmentation fault
Current thread ...:
  shared/dx_server.py:878 in _dispatch_request     ← send_error_json(500, ...)
  shared/dx_server.py:889 in do_POST
Extension modules: greenlet._greenlet, numpy._core._multiarray_umath,
                   numpy.linalg._umath_linalg, google._upb._message
```

**어디서 나는가**: 핸들러가 예기치 못한 예외를 던져 `_dispatch_request` 의
defense-in-depth 가 500 을 되돌려 보내는 그 지점이다. 스택이 얕으므로 재귀나
스택 오버플로는 아니다. 순수 파이썬 소켓 쓰기에서 나는 segfault 이므로 C 확장
쪽(greenlet / protobuf)을 의심하고 있으나 **확인하지 못했다.**

**"offline 에서만" 은 틀렸다** [정정 2026-09-21]: 그 뒤 **기본 게이트에서도**
같은 크래시가 났다(`run_ci.sh` 기본 스테이지, exit 139). 처음 세 번이 모두
offline 이라 그렇게 적었으나 표본이 적었을 뿐이다. offline 가드가 500 경로를
더 자주 밟게 만들어 **확률을 높이는** 것은 사실로 보이나, 원인은 아니다.

빈도(2026-09-21 기준): offline 5회 중 1회, 기본 게이트 여러 회 중 1회.
직후 재실행에서는 재현되지 않았다.

**무엇이 아닌가**: 이 가드는 `3e4dea1`(2026-09-18)에서 들어왔다. 2026-09-21 의
`SAMPLE_IMAGES` 경로 수정과는 무관하다 — 문자열 두 개가 소켓 쓰기를 죽일 경로가
없고, 수정 전후로 발생 양상이 같다.

**다음에 볼 것**: `faulthandler` 를 켜 두고 반복 실행해 크래시 직전의 요청을
특정한다. 500 을 유발한 원래 예외가 로그에 `traceback.print_exc()` 로 남으므로,
크래시 난 실행의 로그에서 그 직전 트레이스백을 찾으면 어느 핸들러인지 좁혀진다.
