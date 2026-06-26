## Artifact 검증 게이트 (HARD GATE — 모든 코드 생성)

이 게이트는 코드 artifact를 생성하는 모든 session에 적용됩니다 (compilation,
app 생성, pipeline 생성). "Internal Development" SWE Process Gates와 독립적입니다
— 그것은 dx-agent-dev feature 작업에 적용되고, 이 게이트는 사용자 대상
deliverable에 적용됩니다.

### 이 게이트가 적용되는 경우

`dx-agent-dev/<session_id>/`에 파일을 생성하는 모든 session은 DONE 선언 전에
해당 파일을 검증해야 합니다:
- Compilation session (ONNX → DXNN)
- App 생성 session (dx_app factory + runner)
- Pipeline session (dx_stream pipeline)
- Cross-project session (compile + deploy)

### 필수 검증 단계

각 artifact 생성 후 즉시 검증 (끝에 몰아서 하지 말 것):

| Artifact | 검증 명령 | 통과 조건 |
|----------|----------|-----------|
| `setup.sh` | `bash -n setup.sh && bash setup.sh` | Exit code 0, 에러 없음 |
| `run.sh` | `bash -n run.sh` | 문법 OK (전체 실행은 model 필요) |
| `verify.py` | `python verify.py; echo "exit: $?"` | Exit code 0, 출력에 "RESULT: PASS" 포함 |
| `*.py` (factory) | `python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | 문법 OK |
| `*.py` (app) | `PYTHONPATH=. python -c "import py_compile; py_compile.compile('<file>', doraise=True)"` | 문법 OK |
| `config.json` | `python -c "import json; json.load(open('config.json'))"` | 유효한 JSON |

### verify.py 실행 테스트 (MANDATORY)

`verify.py`는 `setup.sh`가 생성한 세션 venv를 활성화한 상태에서 실행해야 합니다:

```bash
source venv/bin/activate   # setup.sh가 생성한 venv 활성화
python verify.py
echo "Exit code: $?"
deactivate
```

필수 동작:
1. ONNX와 DXNN 추론이 모두 성공하면 **exit code 0**
2. 추론이 하나라도 실패하면 **exit code 1** (ImportError, RuntimeError 등)
3. **venv가 dependency 제공**: `setup.sh`가 필요한 패키지(`onnxruntime`, `numpy` 등)를
   포함한 venv를 생성합니다. `verify.py`는 검증 로직에만 집중합니다.

verify.py가 "ONNX inference failed" 또는 "DXNN inference failed"를 출력하면서 exit 0을 반환하면 **버그**입니다. 진행 전에 exit code를 수정하세요.

일반적인 실패 원인:
- `No module named 'onnxruntime'` → `setup.sh`를 먼저 실행하여 dependency가 포함된 venv 생성
- `No module named 'dx_engine'` → `setup.sh`가 runtime site-packages를 venv에 추가하는지 확인
- "failed" 출력 후 exit 0 → 실패 분기에 `sys.exit(1)` 추가 필요

### Cross-Project 경로 해석 — SUITE_ROOT (HARD GATE)

`setup.sh`, `run.sh`, 또는 생성된 script가 **자체 sub-project 외부** 경로를 참조할 때
(예: compiler session에서 `dx-runtime` 참조, app session에서 `dx-compiler` 참조),
반드시 `SUITE_ROOT` auto-detection을 사용해야 합니다 — `../../dx-runtime` 같은
하드코딩된 상대 경로는 절대 금지입니다.

**이유**: Session 디렉토리 depth가 sub-project마다 다릅니다:
- `dx-compiler/dx-agent-dev/<session>/` = suite root에서 3단계
- `dx-runtime/dx_app/dx-agent-dev/<session>/` = suite root에서 4단계
- `dx-runtime/dx_stream/dx-agent-dev/<session>/` = suite root에서 4단계

하드코딩된 `../../` 또는 `../../../` 경로는 agent가 depth를 잘못 계산하면
깨집니다 (반복적인 실패 패턴).

**필수 SUITE_ROOT 패턴** — 생성되는 모든 `setup.sh` / `run.sh`에서 사용:
```bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"

# Suite root 자동 탐지 (dx-runtime/과 dx-compiler/ 형제 디렉토리 발견 시까지 상위 탐색)
SUITE_ROOT="$SCRIPT_DIR"
while [ "$SUITE_ROOT" != "/" ]; do
    if [ -d "$SUITE_ROOT/dx-runtime" ] && [ -d "$SUITE_ROOT/dx-compiler" ]; then
        break
    fi
    SUITE_ROOT="$(dirname "$SUITE_ROOT")"
done
if [ "$SUITE_ROOT" = "/" ]; then
    echo "ERROR: Cannot find dx-all-suite root (expected dx-runtime/ and dx-compiler/ siblings)"
    exit 1
fi

RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
COMPILER_DIR="$SUITE_ROOT/dx-compiler"
```

**프로젝트 내부 상대 경로** (예: dx_app session에서 `../../assets/models/`로
`dx_app/assets/` 참조)는 단일 sub-project 내 depth가 고정이므로 허용됩니다.
단, cross-project 참조는 반드시 `$SUITE_ROOT`를 사용해야 합니다.

**금지 패턴** (생성된 `setup.sh` / `run.sh`에서):
```bash
# cross-project 참조에서 아래 모든 패턴 금지:
RUNTIME_DIR="../../dx-runtime"           # depth 가정 오류
RUNTIME_DIR="../../../dx-runtime"        # 여전히 취약
--input ../../dx-runtime/dx_app/sample/  # 인라인 하드코딩 상대 경로
REF_DXNN="../../dx-runtime/dx_app/assets/models/..."  # SUITE_ROOT 없는 cross-project
```

**올바른 패턴**:
```bash
# cross-project 참조 — 항상 SUITE_ROOT 사용
RUNTIME_DIR="$SUITE_ROOT/dx-runtime"
COMPILER_DIR="$SUITE_ROOT/dx-compiler"
--input "$SUITE_ROOT/dx-runtime/dx_app/sample/img/sample_dog.jpg"
REF_DXNN="$SUITE_ROOT/dx-runtime/dx_app/assets/models/${MODEL_NAME}.dxnn"
```

### setup.sh 실행 테스트 (MANDATORY)

`setup.sh`는 session directory에서 실행해야 합니다 (문법 체크만이 아님).
실패 시:
1. 에러 진단
2. script 수정
3. 통과할 때까지 재실행

테스트할 일반적 실패 원인:
- PEP 668 "externally-managed-environment" → venv 사용 필수
- 비공개 package에 대한 `pip install <package>` → local install 또는 사전 설치된 venv 사용
- symlink된 directory에서 상대 경로 해석 → `$(cd "$(dirname "$0")" && pwd -P)` 패턴 사용
- 누락된 dependency → `pip install` 목록 완전성 확인
- `../../`를 사용한 cross-project 경로 → 위의 SUITE_ROOT 패턴 사용

### Import 해석 테스트 (Python app에 MANDATORY)

모든 Python 파일 생성 후, **외부 PYTHONPATH 없이** session 디렉토리에서 실행:
— 이 방식은 생성된 `_sync.py`의 dynamic walker가 `src/python_example/common`을
스스로 올바르게 해석하는지 검증합니다:

```bash
cd <session_dir>
python <model>_sync.py --help 2>&1 | head -10
```

기대 결과: `--help` 출력(usage/argparse 텍스트). `ImportError: No module named 'common'`가
나타나면, `_sync.py`의 dynamic path walker가 실패한 것 — `PYTHONPATH=../../`로 우회하지 말고
`_sync.py`의 walker를 직접 수정하세요.

**금지 패턴**:
```bash
# 잘못된 방법 — agent 환경에서 통과해도 생성 코드의 broken path를 숨김
PYTHONPATH=../../ python -c "from factory import <Model>Factory; print('import OK')"
```

### session.log는 실제 출력이어야 함 (MANDATORY)

`session.log`는 실제 터미널 명령 출력을 포함해야 합니다:
```bash
command 2>&1 | tee session.log
```

다음 패턴은 session.log에 대해 금지됨:
- `cat << 'EOF' > session.log` (heredoc 조작)
- `cat << 'LOGEOF' > session.log` (heredoc 조작)
- `echo "..." > session.log` (수작업 요약)
- `printf "..." > session.log` (수작업 요약)
- 명령을 실행하지 않고 메모리에서 session.log 내용 작성

### dx-agent-tdd 및 프로세스 스킬 시퀀스 (모든 코드 생성에 MANDATORY)

완전한 프로세스 스킬 시퀀스 (`/dx-agent-brainstorm` → `/dx-swe-writing-plans`
→ `/dx-agent-tdd` → `/dx-agent-verify`)는 모든 artifact 생성 session에서
MANDATORY입니다. 전체 시퀀스 정의와 강제 규칙은 **"필수 프로세스 스킬 시퀀스 —
모든 코드 생성"** 섹션을 참조하세요.

이 Artifact Verification Gate 내에서 `/dx-agent-tdd` Red-Green-Verify cycle은
각 artifact에 적용됩니다:
1. **RED**: 각 artifact가 만족해야 할 조건 정의 (문법, 실행, import)
2. **GREEN**: artifact 생성
3. **VERIFY**: 생성 직후 즉시 체크 실행 (이 섹션 위에 정의된 verification
   command 사용)

Autopilot mode에서도 선택사항이 아닙니다. 코드 생성에서 어떤 프로세스 스킬을
건너뛰는 것은 task가 "internal development"인지 "user-facing"인지에 관계없이
session 실패 위반입니다.
