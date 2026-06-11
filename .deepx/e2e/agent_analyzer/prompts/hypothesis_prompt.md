# DEEPX Agent-Driven Development E2E 실험 가설 생성

## 지시사항

아래 정보를 바탕으로 DEEPX Agent-Driven Development E2E 테스트의 실험 가설을 JSON 형식으로 생성하세요.

## 실험 배경

DEEPX는 5개의 AI 코딩 도구(Claude Code, Copilot CLI, Cursor CLI, OpenCode, Codex CLI)를
사용하여 NPU(Neural Processing Unit) 추론 앱을 자동 생성하는 "Agent-Driven Development" 워크플로우를
평가합니다. 각 도구는 동일한 6개 시나리오(compiler, app-python 4종, cross-project)를
수행하며, 규칙 준수(compliance), 코드 품질(quality), 실행 가능성(runnability)을 측정합니다.

## 참고 외부 벤치마크 (2026-05 기준 — 인라인 데이터)

가설 수립 시 아래 **임베드된 최신 수치**를 일차 근거로 사용하세요. 본 prompt 작성 시점은
2026-05-26이며, 데이터는 그때 기준 공개 leaderboard에서 채집되었습니다. 추가 검증이
필요하면 URL의 최신 자료를 함께 참조해도 됩니다.

### 1. Artificial Analysis — Intelligence Index v4.0 (May 2026)
- URL: https://artificialanalysis.ai/
- Methodology: 10개 평가(GDPval-AA, τ²-Bench Telecom, Terminal-Bench Hard, SciCode,
  AA-LCR, AA-Omniscience, IFBench, Humanity's Last Exam, GPQA Diamond, CritPt) 통합 지수
- 최신 순위 요약 (2026-05):
  - **GPT-5.5** (high): Intelligence Index 1위, Terminal-Bench 2.0 82.7% (agent-driven terminal workflows 최강)
  - **Claude Opus 4.7** (Adaptive): SWE-Bench Pro 64.3% — 복잡한 SE 1위
  - **Gemini 3.1 Pro**: GPQA Diamond 94.3% — 과학 추론 1위
  - **Claude Sonnet 4.6**: Opus 4.7 코딩 능력의 ~79.6% / 비용 20% — "best value for everyday coding"
- 핵심 시사: 본 실험은 **cursor-cli를 제외한 4개 도구가 claude-sonnet-4.6** 백엔드,
  cursor-cli는 자체 모델 **Composer 2.5** (composer25/composer25fast 변형) 사용.
  → GPT-5.5/Opus 4.7 벤치마크 절대값이 아닌, **상대적 위치(Sonnet 4.6의 instruction
  following 강점 vs Composer 2.5의 속도/비용 우위)**가 가설 근거.

<!-- ⛔ HARD-GATE — §1.5 / §1.6 RE-EDIT 금지

  §1.5는 Cursor가 **공식 공개한 정보**(블로그/회사 클레임)만 인용해야 합니다.
  과거에 "본 실험에서 80 세션 분석 결과 ~98% 관측" 같은 문장을 추가했다가 H1
  rationale에 사후 데이터가 인용되는 prior 위반이 두 번 발생했습니다. 다음
  키워드를 추가하지 마세요: "본 실험에서", "N session 분석", "관측되었", "실측",
  "observed", "Compliance ~", "Runnability ~". 가설은 결과를 모르는 상태에서
  벤치마크/공식 클레임만으로 작성되어야 합니다.

  §1.6은 Cursor가 공개한 `--list-models` 정보 + 본 실험 하네스 코드
  (`e2e_runner.py` THINKING_ENV)만 인용 — 둘 다 사전 정보입니다. "결과"
  ("관측되었더라도", "실제 효과", "stochastic variance로 확인됨" 등)을 추가하지
  마세요.
-->
### 1.5 Cursor Composer 2.5 (2026-05-26 cursor.com/blog/composer-2-5)
- URL: https://cursor.com/ko/blog/composer-2-5
- Cursor 자체 학습한 coding-specialized 모델 (sonnet-4.6 미사용)
- 회사 공식 클레임:
  - Sonnet 4.6 대비 **~2× 빠른 응답 속도** (긴 reasoning 챕터 없는 형태)
  - "frontier intelligence" 수준 — agent-driven coding 워크플로에 특화
  - **Cursor Pro 무제한 사용 가능** (API 호출 비용 없음) — 자체 호스팅
- 가용 변형: `composer-2.5`, `composer-2.5-fast` (두 가지뿐; `fast`는 reasoning이 짧은 변종)

### 1.6 Cursor CLI의 thinking 토글 한계 (잠재적 confounder)

Cursor `agent --list-models` 공식 정보:
- **Composer 2.5 계열은 thinking variant가 모델에 존재하지 않음** — `fast`는 thinking on/off가 아닌 별도 모델
- thinking variant가 있는 모델: `claude-4.6-sonnet-medium-thinking`, `claude-opus-4-7-thinking-*`, `gpt-5.3-codex-{low,high,xhigh}` 등 — Cursor의 다른 backend 옵션
- `--model auto` (quota 폴백)는 Composer 2.5 family로 떨어지므로 **thinking 토글 인자 자체가 무의미**

본 실험 하네스 (`e2e_runner.py` `THINKING_ENV`)는 4개 sonnet-4.6 도구에만 reasoning_effort
인자(--effort xhigh 등)를 적용하고 cursor-cli는 빈 dict(`{}`)로 NT와 TH 라운드에서
동일 실행. 즉 cursor의 NT(R1-R5) vs TH(R6+) 비교는 thinking 효과 분리 불가.

가설 작성 시 반드시 반영:
- "thinking 효과" 가설은 **claude-code / copilot-cli / opencode / codex-cli 4개 도구로 한정**해 해석
- cursor의 NT→TH 변화는 "thinking 모드 효과"로 해석 금지 — 모델·인자 동일

### 2. SWE-Bench Verified Leaderboard (May 2026)
- URL: https://www.swebench.com/  (live JS 페이지)
- 메트릭: real GitHub issue resolve_rate (%)
- 최신 상위 (2026-05-22 기준):
  - Claude Mythos Preview: **93.9%**
  - Claude Opus 4.7 (Adaptive): **87.6%**
  - GPT-5.3 Codex: **85.0%**
  - Claude Opus 4.5: **80.9%**
  - (claude-sonnet-4-6은 Verified 최상단 미게재 — Sonnet은 Pro보다 Verified에서 약함)
- 시사: 4개 도구의 backend인 Sonnet 4.6은 SWE-Bench Verified 최상위(Opus 4.7 / GPT-5.3)
  대비 ~10-15pt 낮은 영역으로 추정되며, 모든 도구가 동일 backend이므로
  도구 간 차이는 **모델 능력이 아닌 도구 하네스(자동 승인, instruction loop 등)에서 발생**할 가능성이 높음.

### 3. Aider Polyglot Leaderboard (live)
- URL: https://aider.chat/docs/leaderboards/
- 메트릭: 225 Exercism 문제 percent_correct + correct_edit_format
- 최신 상위:

  | 모델 | percent_correct | correct_edit_format |
  |---|---:|---:|
  | gpt-5 (high) | **88.0%** | 91.6% |
  | gpt-5 (medium) | 86.7% | 88.4% |
  | o3-pro (high) | 84.9% | 97.8% |
  | gemini-2.5-pro-preview (32k think) | 83.1% | 99.6% |
  | gpt-5 (low) | 81.3% | 86.7% |
  | o3 (high) | 81.3% | 94.7% |
  | claude-opus-4 (32k thinking) | 72.0% | **97.3%** |
  | claude-opus-4 (no think) | 70.7% | 98.7% |
  | claude-3-7-sonnet (32k thinking) | 64.9% | 97.8% |
  | claude-3-7-sonnet (no think) | 60.4% | 93.3% |
  | **claude-sonnet-4 (32k thinking)** | **61.3%** | **97.3%** |
  | **claude-sonnet-4 (no thinking)** | **56.4%** | **98.2%** |
- 핵심 시사:
  - **percent_correct**: Claude Sonnet은 GPT-5/Opus 대비 코드 정확도 ~60%대 (낮음)
  - **correct_edit_format**: Claude 계열은 97-99% — **instruction following / 형식 준수 압도적**
  - → Sonnet 4.6 기반 도구들은 "코드 자체 품질"보다 "규칙·HARD-GATE 준수"에서 강점 예상
  - → **thinking mode**가 Sonnet 4의 percent_correct를 +4.9pt 상승시킴

### 4. EvalPlus / HumanEval+ MBPP+
- URL: https://evalplus.github.io/leaderboard.html
- HumanEval 절대값 (참고):
  - Claude Sonnet 4.5: **97.6%** (2026-05-11)
  - Kimi K2 Base: EvalPlus 종합 0.803 (현재 최상위)
- 시사: HumanEval은 짧은 함수 단위 — agent-driven E2E 변별력 낮음. 보조 지표로만 활용.

## 실험에 사용된 도구-모델 조합

본 실험은 **3개 라운드 그룹 × 5개 도구**로 구성된 15라운드 (각 5개 시나리오).
도구별로 R1-R5(NT), R6-R10(TH, 기본 모델), R11-R15(TH, 상위 모델)로 backend가
변경되는 점이 핵심.

### 라운드 그룹 설계

| 그룹 | 라운드 | Mode | claude-code · copilot-cli · opencode | codex-cli | cursor-cli |
|---|---|---|---|---|---|
| **A** | R1-R5   | NT (non-thinking)            | claude-sonnet-4.6     | gpt-5.3-codex   | Composer 2.5 (auto) |
| **B** | R6-R10  | TH (reasoning xhigh)         | claude-sonnet-4.6     | gpt-5.3-codex   | Composer 2.5 (auto) |
| **C** | R11-R15 | TH + 상위 모델 업그레이드     | **claude-opus-4.6**   | **gpt-5.5**     | Composer 2.5 (auto) |

핵심 비교 축:
- **Thinking 효과 (A vs B)**: 4개 sonnet/gpt 도구의 backend는 동일 — 차이는 reasoning_effort 인자뿐
- **모델 등급 효과 (B vs C)**: thinking 인자는 동일 — Anthropic 4 도구는 sonnet→opus 업그레이드, codex는 gpt-5.3-codex→gpt-5.5
- **종합 효과 (A vs C)**: 두 변수 모두 변경 — 참고용

### 도구-Provider 통신 특징

| 도구 | Backend (A/B → C) | Provider | 통신 특징 |
|------|---|----------|---------|
| Claude Code | sonnet-4.6 → **opus-4.6** | Anthropic (direct) | 원생 stream-json, 가장 풍부한 trace |
| Copilot CLI | sonnet-4.6 → **opus-4.6** | GitHub Copilot | PR(Premium Request) 단위 과금, sentinel 풍부 |
| **Cursor CLI** | **Composer 2.5 (모든 그룹)** | Cursor | composer25/composer25fast 변형, 짧은 duration, Pro 무제한 |
| OpenCode | sonnet-4.6 → **opus-4.6** | GitHub Copilot | claude subagent 위임 패턴 |
| Codex CLI | gpt-5.3-codex → **gpt-5.5** | GitHub Copilot | NDJSON stream, sentinel 형식 차이 |

→ **가설 시 주의**:
- cursor-cli는 그룹 A·B·C 모두 Composer 2.5(auto)로 동작 — thinking/모델 비교 모두에서 confounder
- 동일 backend의 4 sonnet 도구끼리 비교가 harness 영향 측정에 적합
- C 그룹의 모델 등급 효과는 Anthropic(sonnet→opus)와 OpenAI(gpt-5.3-codex→gpt-5.5)가 독립적으로 변하므로 두 family를 분리해 해석

이 실험의 **non-thinking 라운드와 thinking 라운드** 비교가 핵심:
- thinking은 percent_correct를 일반적으로 ~5pt 상승시킴 (Aider 데이터: claude-sonnet-4 56.4 → 61.3)
- 단 duration·token cost가 ~2배 증가 — efficiency 트레이드오프

`experiment.background` 필드 작성 시 위 3-라운드 설계와 backend 전환을 반드시 명시.

## 출력 형식

아래 JSON 스키마를 **정확히** 따르세요. 추가 필드 금지.

```json
{
  "experiment": {
    "title": "DEEPX Agent-Driven Development E2E 평가",
    "purpose": "5개 AI 코딩 도구의 NPU 추론 앱 자동 생성 능력을 비교 평가",
    "background": "... (2-3문장, 왜 이 실험이 필요한지)",
    "tools": ["claude-code", "copilot-cli", "cursor-cli", "opencode", "codex-cli"]
  },
  "benchmarks": [
    {
      "name": "Aider Polyglot",
      "url": "https://aider.chat/docs/leaderboards/",
      "retrieved_date": "2026-05-26",
      "scores": {
        "claude-sonnet-4-32k-thinking": 61.3,
        "claude-sonnet-4-no-thinking": 56.4,
        "claude-opus-4-32k-thinking": 72.0,
        "gpt-5-high": 88.0
      },
      "metric": "percent_correct",
      "notes": "Claude Sonnet 4의 correct_edit_format은 97-98%로 압도적 — instruction following 강점."
    }
  ],
  "hypotheses": [
    {
      "id": "H1",
      "statement": "...",
      "rationale": "... (위 임베드된 벤치마크 수치를 직접 인용)",
      "metric": "overall_score",
      "expected_ranking": ["claude-code", "copilot-cli", "cursor-cli", "opencode", "codex-cli"],
      "confidence": "high|medium|low",
      "benchmark_basis": ["Aider Polyglot", "Artificial Analysis Intelligence Index v4.0"]
    }
  ]
}
```

## 가설 작성 가이드라인

1. **최소 5개, 권장 7개 가설** 생성
2. 각 가설은 측정 가능한 metric과 연결:
   `overall_score` · `compliance_score` · `quality_score` · `runnability_score` · `execution_score`
3. expected_ranking은 5개 도구 전체 순위를 예측
4. rationale은 **위 임베드된 수치 중 1개 이상을 직접 인용** (예: "Aider Polyglot 97.3% edit
   format이 시사하듯 Claude Sonnet 4의 instruction following이 강해 compliance에서 상위 예상")
5. confidence 수준을 high/medium/low로 표기
6. 다음 차원도 고려:
   - **그룹 A(NT, R1-R5) vs B(TH, R6-R10)**: 동일 backend에서 reasoning_effort 적용 효과
     — cursor 제외 4 도구에서만 유효
   - **그룹 B(R6-R10) vs C(R11-R15)**: 모델 등급 효과 — Anthropic 3 도구는 sonnet→opus,
     codex는 gpt-5.3-codex→gpt-5.5. cursor는 어떤 그룹에서도 모델 변화 없음
   - **그룹 A vs C**: thinking + 모델 두 변수 동시 변경 — 참고용
   - **provider 통신 특성** (Anthropic direct vs Copilot backend vs Cursor 자체)
   - **도구 자체 하네스**: 자동 승인 모드, sentinel 형식, NDJSON vs stream-json
   - **agent-driven 차원**: Terminal-Bench 2.0이 가장 이 실험과 직결 (GPT-5.5 우위)
   - **cursor-cli는 모든 라운드에서 Composer 2.5 backend** — 모든 비교에서 confounder
7. **4개 도구(claude-code/copilot-cli/opencode/codex-cli)는 sonnet-4.6 공유**,
   **cursor-cli만 Composer 2.5** — 이를 가설에 명시적으로 반영
   — 동일 backend 4개 도구 간 차이는 도구별 **하네스/통신/sentinel 특성**이 좌우.
   — cursor vs 4개 도구 간 차이에는 **모델 자체 차이**(Composer 2.5 vs Sonnet 4.6)도 포함.
   — Composer 2.5 클레임(2× 속도, Pro 무제한)을 cursor의 cost/duration 가설에 활용 가능.
8. **thinking 효과 가설은 cursor 제외**:
   — Composer 2.5에 thinking variant 자체가 없고, 하네스도 cursor의 TH 라운드에
     reasoning_effort 인자를 추가하지 않음(§1.6 참조).
   — 따라서 "thinking 모드가 X 점수를 +N pt 상승시킨다" 같은 가설의
     expected_ranking에서 cursor는 NT와 TH 모두 동일한 점수로 예상해야 함.
9. **사전 가설(prior) 원칙 — HARD GATE**:
   — rationale은 **외부 벤치마크 · 도구 통신 특성 · 모델 클레임** 등 사전에 알 수 있는
     정보만 인용. 본 실험의 결과 분석 데이터(observed compliance %, runnability %,
     session 수, 도구별 관측 점수 등)는 절대 인용 금지.
   — "X-session 분석에서 ~Y%가 관측되었다" 같은 표현은 모두 prior 가설 위반.
   — Prior는 미래 결과를 예측하는 글이지, 과거 결과를 설명하는 글이 아님.
