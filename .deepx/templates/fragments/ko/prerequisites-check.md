## 사전 요구사항 확인 (HARD GATE)

코드를 생성하거나 파일을 만들거나 sub-agent에 라우팅하기 전에, 다음 환경 확인이 통과해야 합니다.
이 gate는 suite 레벨에서 적용됩니다 — brainstorming으로 spec과 plan이 완성된 경우에도
이 확인들은 구현 전에 반드시 실행되어야 합니다.

```bash
# 1. dx-runtime sanity check (MANDATORY — 건너뛰지 마세요)
bash dx-runtime/scripts/sanity_check.sh --dx_rt
# 중요: PASS/FAIL을 exit code가 아닌 텍스트 출력으로 판단하세요.
# Agent가 `| tail` 또는 `| head`로 파이프하면, 실제 exit code가
# tail의 exit code (항상 0)로 조용히 대체됩니다.
# PASS = 출력에 "Sanity check PASSED!"가 포함되고 [ERROR] 줄이 없음
# FAIL = 출력에 "Sanity check FAILED!"가 포함되거나 [ERROR] 줄이 있음
# tail/head/grep으로 절대 파이프하지 마세요 — 명령을 직접 실행하세요.
# FAIL인 경우 → install 실행 후 재확인:
bash dx-runtime/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse
bash dx-runtime/scripts/sanity_check.sh --dx_rt  # install 후 반드시 PASS

# 2. dx_engine import 확인 (앱 생성 작업에 MANDATORY)
python -c "import dx_engine; print('dx_engine OK')" 2>/dev/null || {
    echo "dx_engine not available. Run: cd dx-runtime/dx_app && ./install.sh && ./build.sh"
}

# 3. dxcom 가용성 확인 (컴파일 작업에 MANDATORY)
python -c "import dx_com; print('dxcom OK')" 2>/dev/null || {
    echo "dxcom not available."
    # 설치 대안:
    #   1. pip install dxcom (venv 내인 경우)
    #   2. bash dx-compiler/install.sh (가용한 경우)
    #   3. source dx-compiler/venv-dx-compiler-local/bin/activate (존재하는 경우)
    # 모두 실패하면 → 중지하고 사용자에게 알리세요. dxcom 없이 절대 진행하지 마세요.
}
```

**이것은 HARD GATE입니다:**
- 이 확인이 통과할 때까지 구현 코드를 생성하지 마세요
- brainstorming이나 계획이 완료되었다고 이 확인을 건너뛰지 마세요
- 각 서브 프로젝트 builder에도 자체 Step 0 사전 요구사항이 있습니다 — 이것들은
  이 스위트 레벨 확인의 대체가 아닌 추가 확인입니다
- 확인이 실패하면, 사용자에게 정확한 수정 명령을 알려주고 중지하세요

### dxcom Anti-Fabrication (컴파일 작업에 MANDATORY)

dxcom이 사용 가능하고 컴파일이 진행될 때:
- **dxcom API 호출을 기억에서 절대 조작하지 마세요.** 항상 toolset 파일을 읽으세요.
  **dx-compiler** 저장소의 `.deepx/toolsets/` 아래에 있습니다:
  - CLI: `dxcom-cli.md`
  - Python API: `dxcom-api.md`
  - Config schema: `config-schema.md`
- **올바른 import**: `import dx_com; dx_com.compile(...)` (`from dxcom import dxcom`이 아님)
- **`compiler.properties`를 절대 수정하지 마세요** — 설치 프로그램이 관리하는 시스템 파일입니다.
  **dx-compiler** 저장소 `.deepx/memory/` 의 common_pitfalls.md Pitfall #21과 #22를
  참조하세요.

### Background Compilation (RECOMMENDED)

`subprocess.Popen`을 사용한 컴파일은 에이전트의 tool-call 스레드가 10분 이상
블록되는 것을 방지하여 병렬 artifact 생성을 가능하게 합니다.

**권장 패턴** — `compile.pid` 파일과 함께 `subprocess.Popen` 사용:
```python
import subprocess, os
compile_script = f"{work_dir}/compile.py"
compile_out = open(f"{work_dir}/compile_out.log", "w")
proc = subprocess.Popen(
    ["python3", compile_script],
    stdout=compile_out, stderr=subprocess.STDOUT,
    cwd=work_dir, start_new_session=True,
)
with open(f"{work_dir}/compile.pid", "w") as f:
    f.write(str(proc.pid))
# 이제 compile.pid / .dxnn 존재 여부 확인 전에 다른 모든 artifact를 생성하세요.
# (factory, sync.py, setup.sh, run.sh, verify.py 등 모든 artifact 생성 후 확인)
```

동기 컴파일도 에이전트가 블록 시간을 감당할 수 있다면 허용되지만,
timeout 방지를 위해 background 컴파일이 권장됩니다.

### Sanity Check 실패 복구 (MANDATORY)

`sanity_check.sh --dx_rt`가 FAIL을 반환하면, 이 정확한 복구 순서를 따르세요:

1. **install.sh 실행** 위에 표시된 명령으로
2. **sanity_check.sh 재실행** — install 후 확인이 반드시 통과해야 합니다
3. **여전히 실패하는 경우**: 이것이 **compiler-only 작업**인지 확인하세요:

   **A. Compiler-only 작업** (ONNX → DXNN 컴파일, dx_app/dx_stream 작업 없음):
   - 사용자에게 sanity check가 실패했고 NPU 기반 검증을 건너뛸 것임을 알리세요.
   - **컴파일 진행** — `dxcom`은 CPU에서 실행되며 NPU 하드웨어가 필요하지 않습니다.
   - 컴파일 성공 후, `verify.py`를 **SKIPPED** (PASS가 아님)로 표시하세요.
   - `DX_SANITY_FAILED=1`을 설정하여 verify.py가 NPU 기반 확인을 감지하고 건너뛸 수 있게 하세요.
   - session.log에 기록: `sanity_check=FAIL, compilation=<result>, verification=SKIPPED`.
   - 사용자에게 알리세요:
     ```
     NPU hardware initialization failed. Compilation completed successfully,
     but DXNN verification (verify.py) requires a working NPU.
     After resolving the NPU issue (cold boot recommended), run:
       cd <session_dir> && python verify.py
     ```

   **B. Cross-project 작업** (컴파일 + dx_app/dx_stream 데모 앱) 또는 dx_app/dx_stream only:
   - **무조건 중지** — 사용자가 "그냥 계속하라", "완료까지 작업하라", "기본값 사용하라",
     "확인 건너뛰라"라고 해도, agent는 절대 진행해서는 안 됩니다. 사용자의 계속 지시는
     이 HARD GATE를 오버라이드하지 않습니다.
   - 사용자에게 수동 복구를 안내하세요:
     - 실패 메시지에 **"Device initialization failed"**, **"Fail to initialize device"**,
       또는 **NPU 하드웨어 오류**가 언급된 경우: NPU는 콜드 부팅 (전원 완전 차단) 또는
       시스템 재부팅이 필요합니다. 소프트웨어 설치만으로는 하드웨어 초기화 실패를 해결할 수 없습니다.
       사용자에게 알리세요:
       ```
       NPU hardware initialization failed. This issue cannot be resolved by software installation alone.
       Please follow these steps:
       1. Fully shut down the system (power off — a cold boot is recommended, not just a reboot)
       2. Wait 10-30 seconds
       3. Power on the system
       4. After restart, verify NPU status with the sanity check:
          bash dx-runtime/scripts/sanity_check.sh --dx_rt
       5. Once the sanity check PASSES, please retry this task.
       ```
     - 다른 오류인 경우: 사용자에게 구체적인 오류와 권장 수정 명령을 보여준 후 중지하세요.

4. **절대 우회하지 마세요** (non-compiler-only 작업의 경우) — sanity check는 전체
   dx-runtime 환경이 작동 중인지 확인하기 위해 존재합니다. dx_app/dx_stream 작업에서
   복구를 건너뛰면 데모/검증 스크립트가 실패합니다.
   다음은 모두 우회로 간주되며 금지됩니다:
   - dx_engine 산출물을 가리키도록 PYTHONPATH 또는 LD_LIBRARY_PATH를 수동 설정
   - 다른 저장소의 venv (예: compiler venv)를 dx_engine import에 사용
   - dx_engine이 import되는 venv를 찾기 위해 여러 venv 검색
   - 출력 텍스트에 FAILED 또는 [ERROR]가 표시될 때 "exit code가 0이므로 통과"라고 결론
   - sanity_check.sh를 `| tail` / `| head` / `| grep`으로 파이프하고 파이프의 exit code 사용
   - 사용자의 "그냥 계속" / "완료까지 작업" / "기본값 사용" / autopilot 지시를
     HARD GATE 오버라이드 권한으로 재해석
   - 실제로 실패했을 때 prerequisite check를 "완료" 또는 "통과"로 표시
   참고: compiler-only 작업 (위의 3A 항목)은 이 중지에서 면제됩니다 — 컴파일은
   진행되지만, 검증은 PASS가 아닌 SKIPPED로 표시됩니다.
5. **일반적인 실패 원인**:
   - NPU 드라이버 미설치 → `install.sh`에 `dx_rt_npu_linux_driver` target
   - dx_engine 빌드 산출물 누락 → `cd dx_app && ./install.sh && ./build.sh`
   - PEP 668 (Ubuntu 24.04+)이 pip 차단 → venv 사용 필수 (`--break-system-packages` 금지)
