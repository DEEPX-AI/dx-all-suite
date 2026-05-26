# DEEPX Agentic Development E2E 실험 가설 생성

## 지시사항

아래 정보를 바탕으로 DEEPX Agentic Development E2E 테스트의 실험 가설을 JSON 형식으로 생성하세요.

## 실험 배경

DEEPX는 5개의 AI 코딩 도구(Claude Code, Copilot CLI, Cursor CLI, OpenCode, Codex CLI)를
사용하여 NPU(Neural Processing Unit) 추론 앱을 자동 생성하는 "Agentic Development" 워크플로우를
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
  - **GPT-5.5** (high): Intelligence Index 1위, Terminal-Bench 2.0 82.7% (agentic terminal workflows 최강)
  - **Claude Opus 4.7** (Adaptive): SWE-Bench Pro 64.3% — 복잡한 SE 1위
  - **Gemini 3.1 Pro**: GPQA Diamond 94.3% — 과학 추론 1위
  - **Claude Sonnet 4.6**: Opus 4.7 코딩 능력의 ~79.6% / 비용 20% — "best value for everyday coding"
- 핵심 시사: 본 실험은 **cursor-cli를 제외한 4개 도구가 claude-sonnet-4.6** 백엔드,
  cursor-cli는 자체 모델 **Composer 2.5** (composer25/composer25fast 변형) 사용.
  → GPT-5.5/Opus 4.7 벤치마크 절대값이 아닌, **상대적 위치(Sonnet 4.6의 instruction
  following 강점 vs Composer 2.5의 속도/비용 우위)**가 가설 근거.

### 1.5 Cursor Composer 2.5 (2026-05-26 cursor.com/blog/composer-2-5)
- URL: https://cursor.com/ko/blog/composer-2-5
- Cursor 자체 학습한 coding-specialized 모델 (sonnet-4.6 미사용)
- 회사 공식 클레임:
  - Sonnet 4.6 대비 **~2× 빠른 응답 속도** (긴 reasoning 챕터 없는 형태)
  - "frontier intelligence" 수준 — agentic coding 워크플로에 특화
  - **Cursor Pro 무제한 사용 가능** (API 호출 비용 없음) — 자체 호스팅
- 본 실험에서 80 cursor 세션 분석 결과:
  - composer25 (74%), composer25fast (20%), composer (4%), comp25 (2%)
  - **100% Composer 2.5 계열** — Sonnet 4.6 미실행
- 시사: cursor-cli의 일관된 성능(Compliance ~98%, Runnability ~95%)이 도구 하네스
  덕분인지, Composer 2.5 모델 자체 우위인지 분리 불가. 모델/하네스 교차 변수.

### 1.6 Cursor CLI의 thinking 토글 한계 (본 실험 결정적 confounder)

`agent --list-models` 실측 결과:
- **Composer 2.5 계열은 thinking variant가 모델에 존재하지 않음** (`composer-2.5`와 `composer-2.5-fast` 두 가지뿐, `fast`는 reasoning이 짧은 변종이지 thinking on/off가 아님)
- thinking variant가 있는 모델: `claude-4.6-sonnet-medium-thinking`, `claude-opus-4-7-thinking-*`, `gpt-5.3-codex-{low,high,xhigh}` 등 — Cursor의 다른 backend 옵션
- Cursor `--model auto`(quota 폴백 결과)는 Composer 2.5 family로 떨어지므로 **thinking 토글 인자 자체가 무의미**

본 실험 하네스 (`e2e_runner.py:108-115` `THINKING_ENV`):
```python
"claude-code":  --effort xhigh
"copilot-cli":  --effort xhigh
"opencode-cli": --variant high
"codex-cli":    -c model_reasoning_effort="xhigh"
"cursor-cli":   {}  # quota exceeded; auto fallback, no thinking mode
```

- 4개 sonnet-4.6 도구는 TH 라운드에서 reasoning_effort=xhigh 적용
- **cursor만 빈 dict** — TH 라운드에도 NT와 동일 인자로 실행
- 결과: **cursor의 NT(R1-R5) vs TH(R6-R10) 차이는 thinking 효과가 아닌 라운드 간 stochastic variance**

가설 작성 시 반드시 반영:
- "thinking 효과" 가설은 **claude-code / copilot-cli / opencode / codex-cli 4개 도구로 한정**해 해석
- cursor의 NT→TH 변화는 "thinking 모드 효과"로 인용 금지 — 모델 동일, 인자 동일
- cursor를 thinking 비교에 포함하려면 명시적으로 `--model claude-4.6-sonnet-medium-thinking` 강제 필요 (현재 quota 한도로 미지원)

### 2. SWE-Bench Verified Leaderboard (May 2026)
- URL: https://www.swebench.com/  (live JS 페이지)
- 메트릭: real GitHub issue resolve_rate (%)
- 최신 상위 (2026-05-22 기준):
  - Claude Mythos Preview: **93.9%**
  - Claude Opus 4.7 (Adaptive): **87.6%**
  - GPT-5.3 Codex: **85.0%**
  - Claude Opus 4.5: **80.9%**
  - (claude-sonnet-4-6은 Verified 최상단 미게재 — Sonnet은 Pro보다 Verified에서 약함)
- 시사: 본 실험 backend(Sonnet 4.6)는 SWE-Bench Verified 절대값이 ~70-75% 수준으로 추정.
  도구 간 차이는 **모델이 아닌 도구 하네스(자동 승인, instruction loop 등)에서 발생**.

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
- 시사: HumanEval은 짧은 함수 단위 — agentic E2E 변별력 낮음. 보조 지표로만 활용.

## 실험에 사용된 도구-모델 조합

**4개 도구(claude-code/copilot-cli/opencode/codex-cli)는 claude-sonnet-4.6 backend.**
**cursor-cli만 자체 모델 Composer 2.5 계열 사용 (단독 outlier).** 따라서 cursor와 그
외 도구 간 비교는 "도구 하네스" + "모델" 양쪽 차이가 섞임.

| 도구 | Backend Model | Provider | 통신 특징 |
|------|---|----------|---------|
| Claude Code | claude-sonnet-4.6 | Anthropic (direct) | 원생 stream-json, 가장 풍부한 trace |
| Copilot CLI | claude-sonnet-4.6 | GitHub Copilot | PR(Premium Request) 단위 과금, sentinel 풍부 |
| **Cursor CLI** | **Composer 2.5** (자체) | Cursor | composer25/composer25fast 변형, 짧은 duration, Pro 무제한 |
| OpenCode | claude-sonnet-4.6 | GitHub Copilot | claude subagent 위임 패턴 |
| Codex CLI | claude-sonnet-4.6 | GitHub Copilot | NDJSON stream, sentinel 형식 차이 |

→ **가설 시 주의**: cursor-cli의 성능 차이는 "모델 자체 차이"일 수 있어, 다른 도구와
직접 비교 시 confounder. 동일 backend의 4개 도구끼리 비교가 harness 영향 측정에 적합.

본 실험의 **non-thinking 라운드(R1-R5)와 thinking 라운드(R6-R10)** 비교가 핵심:
- thinking은 percent_correct를 일반적으로 ~5pt 상승시킴 (Aider 데이터)
- 단 duration·token cost가 ~2배 증가 — efficiency 트레이드오프

## 출력 형식

아래 JSON 스키마를 **정확히** 따르세요. 추가 필드 금지.

```json
{
  "experiment": {
    "title": "DEEPX Agentic Development E2E 평가",
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
   - **thinking vs non-thinking** 라운드 차이 (R6-R10 vs R1-R5) —
     **cursor 제외 4개 도구에서만** 유효 (cursor는 모델 변화 없음, §1.6 참조)
   - **provider 통신 특성** (Anthropic direct vs Copilot backend vs Cursor 자체)
   - **도구 자체 하네스**: 자동 승인 모드, sentinel 형식, NDJSON vs stream-json
   - **agentic 차원**: Terminal-Bench 2.0이 가장 본 실험과 직결 (GPT-5.5 우위)
   - **cursor-cli는 Composer 2.5 backend** (sonnet-4.6 미사용) — cursor의 점수
     차이는 모델 자체 + 하네스 차이가 섞여 있어 confounder 존재
7. **4개 도구(claude-code/copilot-cli/opencode/codex-cli)는 sonnet-4.6 공유**,
   **cursor-cli만 Composer 2.5** — 이를 가설에 명시적으로 반영
   — 동일 backend 4개 도구 간 차이는 도구별 **하네스/통신/sentinel 특성**이 좌우.
   — cursor vs 4개 도구 간 차이에는 **모델 자체 차이**(Composer 2.5 vs Sonnet 4.6)도 포함.
   — Composer 2.5 클레임(2× 속도, Pro 무제한)을 cursor의 cost/duration 가설에 활용 가능.
8. **thinking 효과 가설은 cursor 제외**:
   — Composer 2.5에 thinking variant 자체가 없고, 하네스도 cursor의 TH 라운드에
     reasoning_effort 인자를 추가하지 않음(§1.6 코드 인용).
   — 따라서 "thinking 모드가 X 점수를 +N pt 상승시킨다" 같은 가설의
     expected_ranking에서 cursor는 NT와 TH 모두 동일한 점수로 예상해야 함.
   — cursor의 NT→TH 차이가 +Δ 또는 -Δ로 관측되더라도 stochastic noise로 해석.
