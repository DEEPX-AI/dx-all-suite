## Artifact 검증 게이트 (HARD GATE — 모든 코드 생성)

이 게이트는 코드 artifact를 생성하는 모든 session에 적용됩니다 (compilation,
app 생성, pipeline 생성). "Internal Development" SWE Process Gates와 독립적입니다
— 그것은 dx-agentic-dev feature 작업에 적용되고, 이 게이트는 사용자 대상
deliverable에 적용됩니다.

### 이 게이트가 적용되는 경우

`dx-agentic-dev/<session_id>/`에 파일을 생성하는 모든 session은 DONE 선언 전에
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

`verify.py`는 venv를 수동으로 활성화하지 않은 상태에서 실행해 self-contained 여부를 확인해야 합니다:

```bash
python verify.py    # NOT: source venv/bin/activate && python verify.py
echo "Exit code: $?"
```

필수 동작:
1. ONNX와 DXNN 추론이 모두 성공하면 **exit code 0**
2. 추론이 하나라도 실패하면 **exit code 1** (ImportError, RuntimeError 등)
3. **Self-contained**: 호출자의 venv 활성화 없이 내부에서 필요한 site-packages를 `sys.path`에 자동 추가

verify.py가 "ONNX inference failed" 또는 "DXNN inference failed"를 출력하면서 exit 0을 반환하면 **버그**입니다. 진행 전에 exit code를 수정하세요.

일반적인 실패 원인:
- `No module named 'onnxruntime'` → verify.py가 compiler venv site-packages를 sys.path에 추가해야 함
- `No module named 'dx_engine'` → verify.py가 runtime venv site-packages를 sys.path에 추가해야 함
- "failed" 출력 후 exit 0 → 실패 분기에 `sys.exit(1)` 추가 필요

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

### Import 해석 테스트 (Python app에 MANDATORY)

모든 Python 파일 생성 후 실행:
```bash
cd <session_dir>
python -c "from factory import <Model>Factory; print('import OK')"
```

실패 시 factory가 잘못된 import 경로를 사용한 것입니다. 진행 전 수정하세요.

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

### dx-tdd 호출 (모든 코드 생성에 MANDATORY)

`/dx-tdd` skill은 모든 artifact 생성 session에서 호출되어야 합니다 — 사용자 대상
compilation, app 생성, pipeline task를 포함합니다. "internal development" task에
한정되지 않습니다.

Red-Green-Verify cycle 적용:
1. **RED**: 각 artifact가 만족해야 할 조건 정의 (문법, 실행, import)
2. **GREEN**: artifact 생성
3. **VERIFY**: 생성 직후 즉시 체크 실행

autopilot mode에서도 선택사항이 아닙니다. 코드 생성에서 dx-tdd를 건너뛰는 것은
task가 "internal development"인지 "user-facing"인지에 관계없이 session 실패
위반입니다.

**근거**: SWE Process Gates "Mandatory Skill Sequence"는 internal dx-agentic-dev
development에 한정됩니다. 이 Artifact Verification Gate는 동일한 discipline을
모든 생성된 deliverable로 확장합니다. 이것 없이는 agent가 테스트되지 않은
setup.sh, 깨진 import, 조작된 session.log 파일을 생산합니다.
