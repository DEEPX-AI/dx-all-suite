# DEEPX Agentic Development E2E 실험 가설 생성

## 지시사항

아래 정보를 바탕으로 DEEPX Agentic Development E2E 테스트의 실험 가설을 JSON 형식으로 생성하세요.

## 실험 배경

DEEPX는 5개의 AI 코딩 도구(Claude Code, Copilot CLI, Cursor CLI, OpenCode, Codex CLI)를
사용하여 NPU(Neural Processing Unit) 추론 앱을 자동 생성하는 "Agentic Development" 워크플로우를
평가합니다. 각 도구는 동일한 6개 시나리오(compiler, app-python 4종, cross-project)를
수행하며, 규칙 준수(compliance), 코드 품질(quality), 실행 가능성(runnability)을 측정합니다.

## 참고할 외부 벤치마크

가설 수립 시 아래 벤치마크의 **최신 자료**를 참조하여 근거를 제시하세요:

1. **Artificial Analysis** (https://artificialanalysis.ai/)
   - AI 모델 Intelligence Index, coding 벤치마크 점수
2. **SWE-Bench Verified** (https://www.swebench.com/)
   - 실제 GitHub issue 해결 능력 (resolve rate %)
3. **Aider LLM Leaderboard** (https://aider.chat/docs/leaderboards/)
   - Polyglot coding benchmark (edit accuracy %)
4. **EvalPlus** (https://evalplus.github.io/leaderboard.html)
   - HumanEval+/MBPP+ pass rates (참고용, 최신 모델 데이터 부족 시 생략 가능)

## 실험에 사용된 도구-모델 조합

| 도구 | 모델 | Provider |
|------|------|----------|
| Claude Code | claude-sonnet-4-6 | Anthropic (direct) |
| Copilot CLI | claude-sonnet-4.6 | GitHub Copilot |
| Cursor CLI | claude-sonnet-4.6 | Cursor |
| OpenCode | claude-sonnet-4.6 | GitHub Copilot |
| Codex CLI | claude-sonnet-4.6 | GitHub Copilot |

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
      "name": "SWE-Bench Verified",
      "url": "https://www.swebench.com/",
      "retrieved_date": "2026-05-15",
      "scores": {
        "claude-sonnet-4-6": 70.4,
        "gpt-5": 71.8
      },
      "metric": "resolve_rate_pct",
      "notes": "..."
    }
  ],
  "hypotheses": [
    {
      "id": "H1",
      "statement": "Claude Code가 전체 종합 점수에서 1위를 차지할 것이다",
      "rationale": "... (벤치마크 근거 + 도구 특성 근거)",
      "metric": "overall_score",
      "expected_ranking": ["claude-code", "copilot-cli", "cursor-cli", "opencode", "codex-cli"],
      "confidence": "high|medium|low",
      "benchmark_basis": ["SWE-Bench Verified", "Aider Polyglot"]
    }
  ]
}
```

## 가설 작성 가이드라인

1. **최소 5개 가설** 생성 (H1~H5+)
2. 각 가설은 측정 가능한 metric과 연결 (overall_score, compliance_score, quality_score, runnability_score, execution_score)
3. expected_ranking은 5개 도구 전체 순위를 예측
4. rationale에는 반드시 1개 이상의 외부 벤치마크 데이터를 인용
5. confidence 수준을 high/medium/low로 표기
6. 도구 자체의 특성(프롬프트 전달 방식, 도구 체인, 자동 승인 모드 등)도 고려
