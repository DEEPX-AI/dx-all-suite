## Standalone Checkout — Harness Bootstrap (HARD GATE)

이 repo는 dx-all-suite의 sub-project이지만 **단독으로 clone**될 수도 있습니다.
단독 checkout인 경우 harness tooling이 존재하지 않습니다:

| 이 repo에 있는 것 | dx-all-suite에만 있는 것 |
|---|---|
| `.deepx/{agents,skills,templates/{en,ko},scripts,memory,instructions,toolsets}` | `.deepx/tools/` — `dx-agent-gen` generator |
| `.deepx/scripts/validate_framework.py` | `.deepx/templates/fragments/` — 공유 fragment |
| 이 instruction 파일 (이미 생성됨) | `.deepx/tests/conformance/` |

위의 Instruction File Verification Loop은 `dx-agent-gen generate` / `check`와
conformance 테스트 실행을 지시합니다. 그러나 단독 checkout에서는 **그 명령들이
동작할 수 없습니다**. 바로 이 지점에서 `.deepx/` 수정이 검증 없이 commit되어
CI에서만 발견되는 drift가 됩니다.

### 첫 `.deepx/` 수정 전에 반드시 실행

```bash
bash .deepx/scripts/harness_bootstrap.sh --check
```

이 스크립트는 다음 순서로 실제 dx-all-suite checkout을 확보합니다 — 명시적
`--suite-dir` / `$DX_SUITE_DIR`, 상위 디렉터리 탐색(일반적인 nested 구성:
다운로드 없음), 이전에 확보한 `.dx-harness/suite` 캐시, 그리고 `.dx-harness/`로
shallow clone. 확보 후에는 **CI `subrepo-gate`와 동일한 검증**을 실행합니다:
generator drift check와 이 repo의 `validate_framework.py`.

`.dx-harness/`는 git-ignore되므로 다운로드된 내용이 index에 들어가지 않습니다.

### exit 3인 경우 — STOP

exit code 3은 suite를 확보하지 못했다는 뜻입니다(로컬 suite 없음, 캐시 없음,
네트워크 불가). 이때는:

- **`**/.deepx/**` 아래 어떤 파일도 수정하지 마십시오.** generator와 fragment가
  없으면 `CLAUDE.md` / `AGENTS.md` / `.claude/` / `.github/` / `.cursor/` /
  `.opencode/`를 재생성할 수 없으므로, 모든 수정이 drift로 commit됩니다.
- **우회하지 마십시오.** 특히 generator가 `FRAGMENT` placeholder를 나열하며
  `unresolved template variables` 오류를 출력하면, 해당 fragment는 **누락된
  것이지 잘못된 것이 아닙니다**. template을 수정하거나 fragment 이름을 바꾸거나
  `_build_template_context()`에 변수를 추가하는 것은 누락된 입력을 더 심각한
  두 번째 drift로 만들어 commit하는 행위입니다.
- 상황을 그대로 알리고, 문서화된 두 가지 해결책을 제시하십시오:
  `--suite-dir /path/to/dx-all-suite`, `$DX_SUITE_DIR`, 또는 전체
  dx-all-suite checkout에서 harness 작업을 수행.

harness 이외의 작업은 영향을 받지 않습니다: application 코드, `src/`, 문서,
테스트, `dx-agent-dev/<session_id>/` 산출물은 bootstrap 실패와 무관하게 정상
진행합니다.

### 범위 안내

`--check`는 suite conformance 테스트를 의도적으로 실행하지 **않습니다**. 해당
검사들은 cross-level 검사로 5개 레벨을 상호 비교하기 때문에, 다른 sub-repo가
없는 상태에서는 만족될 수 없습니다. `subrepo-gate`와 범위를 정확히 일치시키는
것이 "로컬 통과 = CI 통과"를 보장하는 방법입니다.
