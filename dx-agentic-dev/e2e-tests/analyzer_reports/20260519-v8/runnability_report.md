# End-User Runnability Report
> Generated: 2026-05-19T11:08:13  (status: complete)
> Sessions evaluated: 500/602  |  Mode: sample=8 (incremental, 8 reused)  |  CLI: `copilot`
> Incremental: 500 reused from existing report, 0 newly evaluated
> Sessions skipped (no artifacts to evaluate): 100/602

---

## Skipped 세션 분류 (100/602)

| 원인 | 건수 | 영향 도구·라운드·시나리오 |
|------|----:|-----------------------|
| Anthropic 5h rate limit (claude-code) | 27 | claude-code R11 suite (0s); claude-code R12 suite (0s); claude-code R13 suite (0s); claude-code R14 compiler (0s); claude-code R14 dx_app (0s); claude-code R14 dx_stream (0s); … (+21) |
| Subprocess crash (early termination) | 2 | claude-code R18 dx_stream (7s); cursor-cli R19 dx_stream_cascaded (131s) |
| Agent self-abort (mid-run termination) | 2 | claude-code R8 compiler (308s); codex-cli R15 dx_stream (593s) |
| Other / Unknown | 69 | cursor-cli R4 dx_stream_cascaded (0s); cursor-cli R4 runtime (0s); cursor-cli R4 suite (0s); cursor-cli R5 compiler (0s); cursor-cli R5 dx_app (0s); cursor-cli R5 dx_stream (0s); … (+63) |

> 분류는 휴리스틱입니다 — duration·tool 신호 기반. 정확한 원인은 해당 세션의 raw transcript를 참조하세요.

---

## 세션별 평가

### R1 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - DXNN verification was skipped due to missing NPU runtime; only ONNX verification is confirmed.
  - Compilation required a Python API workaround for NCHW/NHWC mismatch, which may confuse users unfamiliar with this pitfall.
  - README does not explicitly mention how to resolve the NPU runtime installation for full DXNN verification.
- **One-sentence verdict**: The artifact is nearly runnable for most users, but DXNN verification and NPU setup gaps may block full validation without further guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-184233_copilot_sonnet46_yolo26n_compile/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하며, 모든 필수 단계와 검증이 포함되어 있어 일반 DEEPX SDK 개발자도 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-185703_copilot_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - GStreamer plugin (`dxinfer`) and postprocess library (`libpostprocess_yolo26od.so`) are missing by default; setup.sh only warns, does not auto-install.
  - Model file (`yolo26n.dxnn`) is not present initially; setup.sh attempts download but may fail silently.
  - Python dependencies (`pydxs`, `gi`) are not always available; user must manually activate the correct venv.
- **One-sentence verdict**: The README is clear and the run flow is well-documented, but missing dependencies and non-robust setup steps mean a typical user may encounter blocking errors unless they are comfortable debugging environment issues.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-190429_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - GStreamer plugin (`dxinfer`) and required models are missing by default; setup.sh only warns, does not auto-resolve.
  - session.log shows pipeline execution fails due to missing plugins/models, so a new user will hit the same errors.
  - Model download and plugin build steps are described but not fully automated or robust to failure.
- **One-sentence verdict**:  
README is clear and comprehensive, but actual runnability is only partial due to missing plugins/models and non-fatal setup.sh, so a typical user will need to manually resolve environment gaps before successful execution.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-191258_copilot_sonnet46_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification.
  - README and scripts assume the user knows where to get `yolo26n.dxnn` and input files.
  - No explicit verification output or instructions beyond running `verify.py`.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing session.log and lack of verification evidence mean a new user may be blocked or uncertain about successful setup and execution.

[DX-AGENTIC-DEV: DONE (output-dir: N/A)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of successful setup or run is provided.
  - `setup.sh` assumes the presence of `install.sh` and `build.sh` in a parent directory, which may confuse users unfamiliar with the repo structure.
  - No explicit verification output or instructions beyond running `verify.py`.
- **One-sentence verdict**: The README and scripts are generally clear, but missing session.log and implicit setup assumptions may block a typical end-user from fully verifying or running the artifact without additional guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-192119_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 opencode-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 환경 설정부터 검증까지 단계별 안내가 완전하게 제공되어 DEEPX SDK 개발자가 문제없이 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-194136_opencode_sonnet46_yolo26n_onnx_to_dxnn/)]
To save this session as JSON, type: /export


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 opencode-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - [WARN] dx_postprocess not found for C++ postprocess variants (clearly noted, with build guidance)
- **One-sentence verdict**:  
README, setup.sh, and run.sh are clear, complete, and actionable; a typical DEEPX SDK developer can follow the instructions to install, run, and verify the artifact without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-203738_opencode_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Model and video sample paths are inconsistent or missing, leading to "No such file or directory" errors.
  - The README assumes directory structure and symlinks that may not exist for all users.
  - Error handling for missing files is present but not fully user-friendly.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing or misreferenced sample files and model path assumptions may block a typical user from running the pipeline successfully without manual intervention.

[DX-AGENTIC-DEV: DONE]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README assumes user knows how to install dx_stream and plugins; no explicit install commands.
  - Virtual environment activation path (`../../venv-dx_stream/bin/activate`) may confuse users if venv is not present or in a different location.
  - Error in session.log (`Cannot identify device '/dev/video0'`) may block users without a valid video input.
- **One-sentence verdict**: The artifact is nearly runnable for a typical DEEPX SDK developer, but clearer setup/install steps and device troubleshooting guidance are needed for a fully smooth experience.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260514-093442_copilot_gpt41_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of successful setup or run is provided.
  - No explicit verification or test output is shown to confirm the artifact works.
  - Model download relies on a nested `setup.sh` call, which may confuse some users.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack of verification output and missing session.log mean a new user cannot be fully confident the artifact works as intended.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification is provided.
  - README and scripts assume the user knows where `dx_app` lives and that all dependencies are pre-installed.
  - No explicit verification/test command or output is shown.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack verification evidence and may confuse users unfamiliar with the directory structure or missing dependencies.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and artifacts are clearly documented.
- **One-sentence verdict**:  
README.md is clear and complete, setup.sh and run.sh are robust, and verification is well-documented—an end-user can confidently install, run, and validate this session’s artifacts.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-194214_codex_gpt55_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - setup.sh does not install dependencies or create a venv; assumes dx_engine/dx_postprocess are pre-installed.
  - README lacks environment prerequisites and troubleshooting guidance.
  - No verification/test command or expected output example is provided.
- **One-sentence verdict**: The README and scripts allow a DEEPX SDK user to attempt running the app, but missing setup steps and lack of verification instructions will block most users unless they already have a fully prepared environment.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-204101_codex_gpt55_yolo26n_object_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Virtual environment activation is mentioned but not fully automated in run.sh.
  - Assumes model_list.json and model files are present/configured; errors if not.
  - Pipeline error in log (missing /dev/video0) may confuse users without a camera device.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but minor environment and device assumptions may hinder a seamless first run for some users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260514-093537_codex_cli_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Minor confusion in venv activation and model download steps (multiple venvs, unclear fallback).
  - session.log shows a syntax error in the session.json check (non-blocking, but misleading).
  - No explicit troubleshooting for missing plugins or model files beyond a warning.
- **One-sentence verdict**: The README and scripts are mostly clear and runnable for a DEEPX SDK user, but minor setup ambiguities and a session.json check error could hinder a smooth first run.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-205236_codex-cli_dx_stream_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - No explicit verification/test command or output for end-to-end inference.
  - setup.sh assumes dx_engine is already installed and importable, but does not install dependencies or create a venv.
  - README omits troubleshooting or expected output for successful runs.
- **One-sentence verdict**: The README is clear and run.sh is straightforward, but missing dependency setup and lack of verification steps may block first-time users.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260513-205443_codex_gpt55_yolo26n_detection_app/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 codex-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - No explicit verification/test command or output for actual inference (only syntax and presence checks).
  - setup.sh assumes dx_engine is already installed and importable, but does not install dependencies or check venv.
  - README omits troubleshooting or environment requirements (e.g., Python version, dependency install).
- **One-sentence verdict**: The README is clear and the run flow is mostly complete, but missing dependency setup and lack of actual inference verification may block a typical end-user.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260513-205443_codex_gpt55_yolo26n_detection_app/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `dx_engine` install requires a local wheel from another repo, not auto-installed.
  - Compilation log shows a DataLoaderError (NHWC/NCHW mismatch), but workaround is only described, not fully automated.
  - Verification (DXNN inference) is marked SKIPPED if `dx_engine` is not installed.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK user, but requires manual steps for `dx_engine` and may confuse users if the NHWC/NCHW fix is not fully automated.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-200623_copilot_sonnet46_yolo26n_onnx_to_dxnn/)]


---

---

---

---

### R2 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - setup.sh assumes model and test assets exist at hardcoded paths but does not provide download or creation steps.
  - No verification/validation script or instructions for output correctness.
  - README does not mention prerequisites (e.g., Python version, NPU driver).
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing asset setup and verification steps may block a typical end-user from running and validating the app successfully.


---

---

---

---

### R2 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Model file and GStreamer plugin (`dxinfer`) are missing by default; setup does not guarantee their presence.
  - Python venv activation for `pydxs` is required but not always auto-detected.
  - session.log shows pipeline execution failed due to missing dependencies.
- **One-sentence verdict**: The README is clear and comprehensive, but actual runnability is only partial due to missing model/plugin and venv issues that block successful execution without manual intervention.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps, caveats, and troubleshooting are clearly addressed.
- **One-sentence verdict**:  
README.md is exceptionally clear and complete, setup.sh and run.sh are robust, and session.log provides real execution evidence—any DEEPX SDK developer can reliably install, run, and verify this pipeline as described.

To save this session as HTML, type: /share html

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-204400_copilot_gpt41_dx_stream_cascaded/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification is provided.
  - README and scripts assume the user understands the dx_app directory structure and has required dependencies.
  - No explicit verification step or output sample is shown.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack of execution evidence and verification steps may hinder a new user's confidence in successful setup and operation.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-204612_copilot_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

---

---

---

### R2 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no execution evidence is available.
  - No explicit verification or test output is provided to confirm successful setup/run.
  - Assumes NPU and model assets are present or downloadable, but does not handle all failure cases.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack verification evidence and session.log, so a new user may be uncertain if the setup and run steps truly succeed.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 cursor-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 setup.sh, run.sh 모두 명확하며, end-user가 안내대로 따라 설치·실행·검증까지 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-194307_cursor_gpt51_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 cursor-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - No installation of Python dependencies or venv setup in `setup.sh`
  - No explicit verification/test step or output in README or session.log
  - Assumes `dx_engine` and `dx_postprocess` are already installed/importable
- **One-sentence verdict**: Most users can follow the README to run scripts if their environment is pre-configured, but missing dependency setup and verification steps may block first-time or unprepared users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-204219_cursor_composer_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `dxrt-cli: command not found` indicates a missing prerequisite or unclear install step.
  - README assumes venv and GStreamer plugin setup but does not detail how to create/activate venv or install dependencies.
  - Postprocess library and model path requirements are mentioned but not validated in setup.sh.
- **One-sentence verdict**: The README is clear and the setup/run scripts mostly work, but missing dependency installation and unclear venv/GStreamer setup may block a typical user.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-205101_cursor_composer_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 cursor-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh robustly ensures prerequisites, run.sh is straightforward, and session.log confirms successful execution and verification—an end-user can reliably install, run, and verify this artifact as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-205455_cursor_gpt52_yolo26n_cascaded/)]  
To save this session as HTML, type: /share html


---

---

---

---

### R1 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `setup.sh` emits warnings/errors about missing `dx_engine` wheel and invalid wheel filename, which may confuse users.
  - The README does not explain how to resolve missing `dx_engine` or where to obtain it.
  - The verification step is present, but success is not clearly shown in the provided session.log excerpt.
- **One-sentence verdict**: 기본적인 실행 흐름은 안내되어 있으나, 환경 의존성(`dx_engine` wheel) 문제로 인해 일반 사용자가 바로 성공적으로 실행하기 어렵습니다.


---

---

---

---

### R1 cursor-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `setup.sh` fails to install `dx_engine` if the wheel is missing, only warns but does not resolve the missing dependency.
  - The README does not mention how to obtain or build the required `dx_engine` wheel if absent.
  - Initial setup log shows errors/warnings that may confuse users unfamiliar with the environment.
- **One-sentence verdict**: The session is mostly runnable for experienced users, but missing `dx_engine` installation guidance and setup warnings may block less experienced users from successful execution.


---

---

---

---

### R1 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 명확하며, 모든 주요 단계(설치, 실행, 검증)가 구체적으로 안내되어 있어 DEEPX SDK 개발자가 문제없이 세션 아티팩트를 실행할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 설치·실행·검증 절차가 모두 제공되어 DEEPX SDK 개발자가 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260513-203739_claude_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and troubleshooting are clearly documented.
- **One-sentence verdict**:  
README.md provides clear, step-by-step instructions for setup, running, and verification, enabling a typical DEEPX SDK developer to successfully execute and validate the pipeline without prior session knowledge.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/<session_id>/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps, paths, and troubleshooting are clearly documented.
- **One-sentence verdict**:  
README.md is exceptionally clear, setup.sh and run.sh are robust, and session.log confirms successful execution—any DEEPX SDK developer should be able to install, run, and verify this cascaded pipeline without issue.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-210257_claude_sonnet46_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, session.log의 검증 결과도 포함되어 있어 DEEPX SDK 개발자가 안내대로 문제없이 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-211032_claude_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R1 claude-code suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (주요 문제 없음)
- **One-sentence verdict**: README가 명확하고, setup.sh와 run.sh가 완전하며, session.log로 검증까지 제공되어 DEEPX SDK 개발자가 안내대로 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-211032_claude_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Compilation failed initially due to NHWC/NCHW mismatch; workaround required Python API usage.
  - README does not mention how to resolve DataLoaderError or edit config.json for input shape.
  - session.log shows error but not final successful compilation evidence.
- **One-sentence verdict**: The README and setup scripts are clear and comprehensive, but a typical user may be blocked by the input shape config error unless they know to adjust config.json or use the Python API workaround.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-211025_opencode_sonnet46_yolo26n_onnx_to_dxnn/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - C++ postprocess variants require a manual `./build.sh` step not automated in setup.sh.
  - No explicit verification/test command or output for inference correctness.
  - NPU check (`dxrt-cli`) may be missing, causing confusion for new users.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack automated verification and require manual steps for full functionality, which may hinder a first-time user.

[DX-AGENTIC-DEV: DONE]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - None; instructions are clear, complete, and robust for a typical DEEPX SDK developer.
- **One-sentence verdict**:  
README.md provides clear, step-by-step setup and run instructions, with robust environment checks and verification evidence, ensuring a typical end-user can install, run, and validate the pipeline without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-213500_copilot_gpt41_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 opencode-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md는 단계별로 명확하며, setup.sh와 run.sh가 환경 설정 및 실행을 자동화하고, session.log에 실제 실행 증거와 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 완료할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-214617_copilot_gpt41_dx_stream_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification is provided.
  - `setup.sh` assumes the presence of `dxrt-cli` and a parent-level `setup.sh`, which may confuse users unfamiliar with the directory structure.
  - No explicit instructions for installing Python dependencies or activating a virtual environment.
- **One-sentence verdict**: The README is clear and the run scripts are mostly complete, but missing verification evidence and ambiguous setup steps may block a typical end-user.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-214744_opencode_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification.
  - `setup.sh` assumes the presence of `dxrt-cli` and a parent-level `setup.sh`, which may confuse users unfamiliar with the directory structure.
  - No explicit verification output or instructions for what to expect from `verify.py`.
- **One-sentence verdict**: The README is clear and the run instructions are mostly complete, but missing session.log and ambiguous setup steps may block a typical end-user from successful execution and verification.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-214744_opencode_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 copilot-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하고, 검증 결과와 실행 방법이 잘 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-211652_copilot_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - 모델 파일 자동 다운로드/설치가 누락되어 직접 안내만 있음 (`setup_sample_models.sh` 수동 실행 필요)
  - NPU 상태 확인 및 dxrt-cli 사용법이 간략히만 언급됨
  - 검증(verify.py 등) 실행 방법 및 결과 확인 절차가 README에 없음
- **One-sentence verdict**: 설치와 실행은 대부분 안내되어 있으나, 모델 준비와 검증 절차가 불완전해 초심자에게는 추가 안내가 필요합니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-213413_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 환경 설정, 실행, 검증까지 단계별로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치·실행·검증할 수 있습니다.

To save this session as HTML, type: /share html  
[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-214155_copilot_gpt41_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - session.log shows a pipeline parse error (`no property "num-sources" in element "dxgather"`), which may block successful execution.
  - README and setup.sh are clear, but troubleshooting for pipeline errors is not addressed.
  - Model and library checks are present, but missing libraries are only warned, not auto-resolved.
- **One-sentence verdict**: The README and scripts are clear and nearly complete, but a pipeline configuration error in execution evidence means a typical user may not achieve a successful run without manual debugging.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-215043_copilot_sonnet46_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so there is no evidence of successful execution or verification.
  - README and scripts are clear, but lack explicit verification/test instructions or output.
  - Model auto-download may fail silently; manual download fallback is not fully explained.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing session.log and verification steps mean a new user cannot fully confirm successful setup and execution without additional guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-215528_copilot_sonnet46_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so there is no evidence of successful setup or run.
  - No explicit verification/validation step or output is described or provided.
  - Model auto-download may fail silently; manual download fallback is not clearly explained in README.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack of verification evidence and missing session.log mean a new user cannot be fully confident the artifact works as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-215528_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - [WARN] in session.log: dxrtd service not running, but overall sanity check still passes.
- **One-sentence verdict**: README is clear and complete, setup.sh and run.sh are robust, and verification steps are provided—an end-user can reliably install, run, and verify this artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-211342_codex_gpt55_yolo26n_compile/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README omits explicit troubleshooting for missing model files or sample data.
  - setup.sh requires dx_engine to be pre-built, but only hints at the fix.
  - run.sh assumes model/sample paths exist; errors if not present.
- **One-sentence verdict**: The artifact is nearly runnable for a typical DEEPX SDK developer, but missing model/sample files and implicit dx_engine build steps may block first-time users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-213409_codex_gpt55_yolo26n_detection/)]


---

---

---

---

### R2 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `setup.sh` assumes presence of certain venvs and scripts that may not exist or be documented for new users.
  - Prerequisite script (`../../scripts/sanity_check.sh`) is missing, causing setup confusion.
  - No explicit verification or test output confirming end-to-end pipeline success.
- **One-sentence verdict**: The README is clear and run instructions are mostly complete, but missing prerequisite scripts and lack of verification steps mean a typical end-user may encounter setup blockers or uncertainty about successful execution.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 설치·실행·검증 절차가 모두 자동화되어 있어 DEEPX SDK 개발자가 별다른 추가 지식 없이 성공적으로 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-214903_codex_gpt55_yolo26n_cascaded)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 codex-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 상대 경로 안내(`cd ../../`)가 다소 불명확할 수 있음 (dx_app 루트 기준 명시 필요)
  - run.sh가 기본 이미지/모델 경로를 하드코딩하여, 커스텀 입력 사용 시 별도 안내 부족
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 표준적이고 검증 절차도 제공되어, 일반 DEEPX SDK 개발자가 무리 없이 실행 및 검증 가능함.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260513-215622_codex_gpt55_yolo26n_standalone_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 codex-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README assumes user knows to run from the session directory; relative paths may confuse some users.
  - Minor: The manual run examples use relative paths that could break if not run from the correct location.
- **One-sentence verdict**: The artifacts are well-structured and verifiable, with clear setup and run instructions—minor path clarifications would make it fully foolproof for all users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260513-215622_codex_gpt55_yolo26n_standalone_detection/)]
To save this session as HTML, type: /share html


---

---

---

---

### R2 cursor-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, end-user가 안내대로 설치·실행·검증을 문제없이 수행할 수 있습니다.


---

---

---

---

### R2 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 설치·실행·검증 절차가 완비되어 있어 일반 DEEPX SDK 개발자도 문제없이 실행할 수 있습니다.


---

---

---

---

### R2 cursor-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `dxrt-cli: command not found` warning in session.log (minor, does not block pipeline run)
- **One-sentence verdict**:  
README is clear and comprehensive, setup and run scripts are complete, and verification is provided—an end-user can successfully install, run, and validate this artifact.


---

---

---

---

### R2 cursor-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None; all steps, dependencies, and troubleshooting are clearly documented.
- **One-sentence verdict**: README, setup, and run scripts are comprehensive and clear—any DEEPX SDK developer can follow them to install, run, and verify the pipeline successfully.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 cursor-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, end-user가 안내대로 설치, 실행, 검증을 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-221550_cursor_composer_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 cursor-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - (none observed; all critical steps and evidence are present)
- **One-sentence verdict**:  
README.md is clear and complete, setup.sh and run.sh are robust, and session.log shows successful execution—an end-user can reliably follow these instructions to install, run, and verify the artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-221550_cursor_composer_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, 검증 절차와 실행 방법이 구체적으로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-213935_claude_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 일반 DEEPX SDK 개발자가 안내대로 setup.sh, run.sh, verify.py를 실행해 정상적으로 결과를 재현할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260513-215200_claude_sonnet46_yolo26n_inference/)]  
To save this session as HTML, type: /share html


---

---

---

---

### R2 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경 설정부터 실행, 검증까지 단계별로 안내되어 있어 일반 DEEPX SDK 개발자도 문제없이 실행할 수 있습니다.


---

---

---

---

### R2 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 매우 명확하며, 모든 주요 단계(설치, 실행, 검증)가 실제 로그와 함께 제공되어 DEEPX SDK 개발자가 문제없이 세션 아티팩트를 실행할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R2 claude-code runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - dx_engine wheel not found and not importable by default; user may need to resolve this manually.
  - README does not mention troubleshooting for missing dx_engine or how to obtain it.
  - Default model path in run.sh is hardcoded to a session-specific directory, which may not exist for all users.
- **One-sentence verdict**: The artifact is nearly runnable for a typical DEEPX SDK developer, but missing or inaccessible dx_engine and unclear model path handling may block first-time users without extra troubleshooting.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-221738_claude_sonnet46_yolo26n_object_detection/)]


---

---

---

---

### R2 claude-code suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - dx_engine is not guaranteed to be available; setup warns if missing and does not install it.
  - User may be confused if dx_engine is not importable, as no remediation steps are provided.
  - Model file path in run.sh defaults to a session-specific location, which may not exist for all users.
- **One-sentence verdict**: The README and scripts are clear and nearly complete, but missing or inaccessible dx_engine will block most users unless they already have the correct environment.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 opencode-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - None significant; all steps and caveats are clearly documented.
- **One-sentence verdict**:  
README, setup.sh, and run.sh are clear, complete, and robust—any DEEPX SDK developer can follow them to install, run, and verify the artifact without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-221136_opencode_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 opencode-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**:  
README, setup.sh, and run.sh are clear, complete, and robust; a typical DEEPX SDK developer can follow the instructions to install, run, and verify the artifact without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-223041_opencode_sonnet46_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md는 단계별로 명확하며, setup.sh와 run.sh가 환경 설정 및 실행을 자동화하고, session.log에 실제 실행 증거가 포함되어 있어 DEEPX SDK 개발자가 별다른 추가 지식 없이도 성공적으로 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 opencode-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 명확하며, 실행 및 검증 절차가 모두 제공되어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/<session_id>/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 opencode-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 모델 경로가 기본 위치에 없을 경우, 명확한 수동 다운로드/경로 지정 안내가 부족함
- **One-sentence verdict**: README와 스크립트가 명확하며, 대부분의 사용자는 안내대로 설치·실행·검증이 가능하나, 모델 파일 미존재 시 대처 안내가 약간 부족합니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-224440_opencode_sonnet46_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - setup.sh assumes NPU and dxrt-cli are available but does not guide on installing dx-runtime or dependencies if missing
  - Model download path and requirements are not fully explained for users unfamiliar with the asset structure
  - No troubleshooting section for common errors (e.g., missing model, NPU unavailable)
- **One-sentence verdict**: The README and scripts are clear for experienced DEEPX users, but setup may fail for newcomers due to missing dependency guidance and limited troubleshooting help.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-224440_opencode_sonnet46_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 일반 DEEPX SDK 개발자가 안내대로 setup.sh와 run.sh를 실행하면 정상적으로 설치, 실행, 검증까지 완료할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-222136_codex_gpt55_dx_m1_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 codex-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 설치·실행·검증 절차가 모두 충실하게 안내되어 있어 일반 DEEPX SDK 개발자도 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-224157_codex_gpt55_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - venv activation and model download are somewhat automated but may fail silently if prerequisites are missing.
  - No explicit verification/test command or output is provided in README or session.log.
  - The sanity check script is missing, leading to a failed prerequisite check.
- **One-sentence verdict**: 대부분의 사용자는 README와 스크립트로 실행까지 접근할 수 있으나, 검증 단계와 일부 환경 의존성 안내가 부족하여 완전한 신뢰성은 보장되지 않습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260513-224721_codex_gpt55_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - README could clarify the need to run `install.sh`/`build.sh` if plugins are missing.
  - Minor: venv activation is mentioned but not strictly required due to run.sh wrapping setup.
- **One-sentence verdict**: The artifact is well-structured and runnable by a typical end-user, with clear setup and run instructions and verification evidence present.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-225137_codex_gpt55_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 codex-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README could clarify model/image path defaults and troubleshooting for missing files.
- **One-sentence verdict**: The artifacts are well-structured and, with clear setup and run instructions plus verification evidence, a typical DEEPX SDK developer can successfully install, run, and validate this session.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260513-230053_codex_gpt55_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 codex-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Minor: README could clarify model/image path defaults and troubleshooting for missing files.
- **One-sentence verdict**: The session artifacts are well-structured and, with clear setup and run instructions plus verification evidence, should be runnable by any DEEPX SDK developer.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260513-230053_codex_gpt55_yolo26n_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 copilot-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh` does not actually run inference; it only checks for the model and points to manual deployment.
  - No explicit deployment or inference command for DX-M1 hardware is provided.
- **One-sentence verdict**: The session artifacts are well-documented and setup is straightforward, but deployment to hardware requires user knowledge beyond the provided scripts.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-221820_copilot_sonnet46_yolo26n_compile/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 표준 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-222942_copilot_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경 설정부터 실행, 검증까지 단계별로 안내되어 있어 DEEPX SDK 개발자가 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/<session_id>/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Model and postprocess library download steps may confuse users unfamiliar with dx_stream directory layout.
  - The README assumes the user can resolve missing GStreamer plugins and libraries without explicit troubleshooting steps.
  - The session.log shows a pipeline error on first run, though a retry appears to have fixed it (truncated evidence).
- **One-sentence verdict**: The artifact is nearly runnable by a typical DEEPX SDK developer, but minor gaps in troubleshooting guidance and initial pipeline errors may block less experienced users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-220000_copilot_sonnet46_cascaded_inference/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification is present.
  - Model download is not robust—if the parent setup.sh fails or is missing, user must manually fetch the model.
  - No explicit verification/test step or output guidance for confirming correct results.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack of verification evidence and missing session.log mean a new user may be unsure if the setup and run steps truly work as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no execution evidence is provided.
  - Model download is attempted but may fail silently; manual intervention may be required.
  - No explicit verification/test step or output is shown in README or artifacts.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack of verification output and missing session.log mean a new user may be unsure if setup and inference actually succeeded.

[DX-AGENTIC-DEV: DONE]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 cursor-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README.md is clear and detailed, setup.sh and run.sh are robust and self-explanatory, and verification is well-documented and evidenced—an end-user can reliably install, run, and verify this session without prior context.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-222737_cursor_opus47_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

---

---

---

### R3 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, dx_engine 설치 안내와 검증 결과가 session.log에 포함되어 있어 일반 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 cursor-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Minor ambiguity in venv activation for users not at repo root.
  - RTSP/headless usage is mentioned but not deeply explained.
  - Some users may need more explicit troubleshooting for missing plugins/models.
- **One-sentence verdict**: The artifact is well-structured and should be runnable by a typical DEEPX SDK developer, with clear setup, run, and verification steps, though a few advanced options could use more detail.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-095559_copilot_gpt41_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 cursor-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - No explicit troubleshooting section for common errors (e.g., missing venv or plugins).
  - README could clarify the role of `run_cascaded.sh` vs `run.sh`.
- **One-sentence verdict**: The artifact is well-structured and runnable by a typical DEEPX SDK developer, with clear setup and run steps, though minor clarifications in the README would further improve usability.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260513-225617_cursor_composer_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 cursor-cli runtime

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `compile.py` fails with `ModuleNotFoundError: No module named 'dx_com'` (dx_com not installed in venv)
  - setup.sh does not guarantee dx_com is available in the session venv
  - User cannot proceed past compilation step without manual intervention
- **One-sentence verdict**: Despite clear instructions and mostly complete setup, the session is not runnable as-is due to missing dx_com in the Python environment, blocking compilation.

[DX-AGENTIC-DEV: DONE]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 cursor-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `ModuleNotFoundError: No module named 'dx_com'` during `compile.py` execution (critical blocker)
  - README does not mention how to ensure `dx_com` is installed/available in the venv
  - Setup script attempts to activate a compiler venv, but if missing, install may not succeed for all users
- **One-sentence verdict**: The README and setup are clear and mostly complete, but a missing `dx_com` module prevents successful compilation and will block typical end-users unless they manually resolve this dependency.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-230344_cursor_composer_yolo26n_compile/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 명확하며, 실행 및 검증 절차가 완비되어 있어 DEEPX SDK 개발자가 그대로 따라 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-224130_claude_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 모델 파일이 기본 위치에 없을 경우 추가 다운로드 안내가 필요함 (경고 메시지로 안내는 충분)
  - dx_postprocess 미설치 시 일부 variant 사용 불가 (경고로 안내)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경설정 및 실행 절차가 잘 안내되어 있어 일반 DEEPX SDK 사용자가 문제없이 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-225546_claude_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this pipeline as instructed.

To save this session as HTML, type: /share html  
[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260513-230627_claude_code_gpt41_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 명확하며, 모든 필수 파일과 실행/검증 절차가 잘 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-230857_claude_sonnet46_yolo26n_cascaded/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경 설정부터 실행, 검증까지 단계별 안내가 잘 되어 있어 일반 DEEPX SDK 개발자도 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260513-231727_claude_sonnet46_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R3 claude-code suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**:  
README, setup.sh, and run.sh are clear, complete, and provide all necessary steps and verification for a typical DEEPX SDK developer to install, run, and validate the session artifacts successfully.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260513-231727_claude_sonnet46_yolo26n_object_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Minor: compile.py SameFileError in session.log, but does not block main flow.
- **One-sentence verdict**:  
README is clear, setup.sh robustly handles environment and dependencies, run.sh is simple, and verification is well-documented—an end-user can reliably install, run, and verify this artifact.

To save this session as HTML, type: /share html  
[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-231417_codex_gpt55_dxm1_yolo26n_compile/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `setup.sh` does not install or build `dx_engine`; user must manually run `./install.sh && ./build.sh` at dx_app root.
  - Model and sample data paths in `run.sh` may not exist, requiring user adjustment.
  - README omits troubleshooting for missing dependencies or model files.
- **One-sentence verdict**: Most users can follow the README to set up and run, but missing automated `dx_engine` setup and unclear model/data path handling may block less experienced users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-233305_codex_gpt55_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 codex-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 명확하며, 실행 및 검증 절차가 잘 안내되어 있어 일반 DEEPX SDK 개발자도 문제없이 설치, 실행, 검증이 가능합니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-234130_codex_gpt55_dx_m1_yolo26n_realtime_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - README assumes user knows where to find/run `run_cascaded.sh` (minor, as run.sh wraps it)
  - Prerequisite venv activation path (`../../venv-dx_stream/bin/activate`) may confuse if not present
- **One-sentence verdict**: The artifact is fully runnable by a typical DEEPX SDK developer; setup, run, and verification steps are clear and complete, with only minor clarity gaps in README pathing.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-234648_codex_gpt55_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 codex-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README omits explicit mention of activating the venv, but setup.sh handles it.
  - Default model/image paths are relative and may confuse users if directory structure differs.
  - No troubleshooting section for common errors (e.g., missing dx_engine).
- **One-sentence verdict**: The artifact is runnable by a typical end-user with clear setup and run steps, though minor clarifications in the README would further improve usability.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-235634_codex_gpt55_yolo26n_standalone_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 codex-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README does not explicitly mention activating the venv, but setup.sh handles it.
  - Default model/image paths are relative and may confuse users if directory structure differs.
  - No troubleshooting section for common errors (e.g., missing dx_engine).
- **One-sentence verdict**: The artifact is runnable by a typical end-user with clear setup and run steps, minor clarity improvements possible.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-235634_codex_gpt55_yolo26n_standalone_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 cursor-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, end-user가 안내대로 setup, 실행, 검증을 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-232550_cursor_gpt51_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 cursor-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Model file (`yolo26n.dxnn`) is missing initially; relies on auto-download, which may not always succeed or be obvious to new users.
  - README does not explicitly mention that the model will be auto-downloaded if missing.
  - C++ postprocess variants require extra build steps not covered in the main quick start.
- **One-sentence verdict**: The artifact is nearly runnable by a typical end-user, but clearer guidance on model availability and C++ postprocess setup would improve the experience.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260513-235115_cursor_composer_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 cursor-cli dx_stream

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 0
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: no
- **Key issues**:
  - README.md is missing, so no entrypoint or instructions are provided.
  - session.log is missing, so there is no evidence of successful execution or verification.
  - run.sh references a script (run_yolo26n_realtime_detection.sh) that is not included or documented.
- **One-sentence verdict**: Without a README, session log, or clear run script, a typical end-user cannot reliably install, run, or verify this artifact.

[DX-AGENTIC-DEV: DONE]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Compilation failed due to DataLoaderError (NHWC/NCHW mismatch); workaround via Python API is mentioned but not fully documented for user replication.
  - README and scripts assume presence of certain files (e.g., sample_dog.jpg, calibration images) without explicit download/setup steps.
  - The verification step is described, but success is not demonstrated in session.log.
- **One-sentence verdict**: 대부분의 설치 및 실행 절차는 명확하나, 컴파일 실패와 일부 파일 준비 미비로 인해 사용자가 즉시 성공적으로 실행하기 어렵습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-230406_opencode_sonnet46_yolo26n_onnx_to_dxnn/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 모델 파일(`yolo26n.dxnn`)과 샘플 이미지/비디오가 기본 위치에 존재하지 않음 (setup.sh에서 자동 다운로드 없음, 직접 준비 필요)
  - NPU 하드웨어 미탑재 환경에서는 실행 검증이 스킵됨 (실제 추론 결과 미확인)
- **One-sentence verdict**: README와 실행 스크립트는 매우 명확하지만, 모델/데이터 파일 부재와 NPU 미탑재 환경에서는 사용자가 직접 파일을 준비해야 하므로 완전 자동 실행은 불가합니다.

[DX-AGENTIC-DEV: DONE (output-dir: 20260513-232622_opencode_sonnet46_yolo26n_detection/)]


---

---

---

---

### R4 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, end-user가 안내대로 설치, 실행, 검증을 문제없이 수행할 수 있습니다.


---

---

---

---

### R4 opencode-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this artifact as intended.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of successful setup or run is provided.
  - If `dx_engine` is not installed, the user must manually run `../../install.sh`, which may not be obvious if directory structure differs.
  - No explicit verification or test output is shown to confirm correct installation.
- **One-sentence verdict**: The README and scripts are clear and nearly complete, but lack of verification evidence and missing session.log reduce end-user confidence in successful execution.

[DX-AGENTIC-DEV: DONE (output-dir: 20260513-234700_opencode_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no execution evidence is provided.
  - README and scripts assume presence of model/assets in relative paths, which may not exist for new users.
  - No explicit verification/test step or output sample is included.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing assets and lack of verification evidence may block a first-time user from successful execution.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260513-234700_opencode_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 opencode-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, session.log의 실행 결과도 정상적으로 제공되어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-000811_opencode_sonnet46_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and troubleshooting are clearly documented.
- **One-sentence verdict**:  
README, setup, and run scripts are clear, complete, and verifiable—any DEEPX SDK developer can follow and successfully execute this pipeline without prior session knowledge.

To save this session as HTML, type: /share html

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-100352_opencode_dx_stream_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 opencode-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (README, setup, run, 검증 모두 명확)
- **One-sentence verdict**: README와 setup.sh가 매우 상세하며, 실행 및 검증까지 단계별로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/<session_id>/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of successful execution or verification is provided.
  - `setup.sh` assumes the presence of `dxrt-cli` and a working NPU, but does not guide the user if these are missing.
  - Model/sample download may silently fail, requiring manual intervention not clearly described in README.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing verification output and fragile setup steps may block a typical user from running and validating the session without extra troubleshooting.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-002008_opencode_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of successful execution or verification.
  - `setup.sh` assumes `dxrt-cli` and other dependencies are pre-installed, but does not install or check them.
  - Model/sample download may fail silently if upstream scripts or Python modules are missing.
- **One-sentence verdict**: The README is clear and run.sh is robust, but missing session.log, incomplete setup, and lack of verification evidence mean a typical user may encounter blocking issues without further guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-002008_opencode_sonnet46_yolo26n_detection/)]


---

---

---

---

### R8 cursor-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 특별한 문제 없음. 모든 주요 단계(설치, 실행, 검증)가 명확히 안내됨.
- **One-sentence verdict**: README와 스크립트가 명확하고, 검증 결과도 제공되어 DEEPX SDK 개발자가 문제없이 설치·실행·검증할 수 있습니다.


---

---

---

---

### R8 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `app.yaml` metadata file missing (minor, does not block main flow)
- **One-sentence verdict**: The artifact is fully runnable by a typical end-user, with clear, complete setup and run instructions, and successful verification evidence; only a minor metadata warning is present.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 cursor-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and troubleshooting are clearly documented.
- **One-sentence verdict**:  
README.md is clear, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this artifact as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-003930_cursor_composer_dx_m1_yolo26n_realtime_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 cursor-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - None; all critical steps and troubleshooting are covered.
- **One-sentence verdict**: The README is clear, setup.sh robustly checks all prerequisites, run instructions are explicit, and session.log provides strong verification—an end-user can reliably install, run, and verify this artifact.

To save this session as HTML, type: /share html  
[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-004149_cursor_composer_yolo26n_cascaded/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 cursor-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 표준 DEEPX SDK 개발자가 안내대로 setup.sh와 run.sh를 실행하면 정상적으로 컴파일 및 검증을 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-004750_cursor_composer1_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 cursor-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 표준 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 따라할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-004750_cursor_composer1_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, end-user가 안내대로 setup 및 실행, 검증까지 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-000956_codex_gpt55_dxm1_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `setup.sh` assumes `dxrt-cli` and `build.sh` exist in the parent tree, but does not guide user if missing.
  - No explicit verification/test command or output for actual inference (only syntax/import checks).
  - README does not mention required model/data assets or where to obtain them.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK developer, but lacks asset guidance and verification steps, and setup may fail if dependencies are not pre-installed.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-002222_codex_gpt55_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 codex-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md는 명확하며, setup.sh와 run.sh가 완전하게 환경을 준비하고 실행을 안내하며, session.log에 실제 실행 증거가 포함되어 있어 일반 DEEPX SDK 개발자도 문제없이 설치, 실행, 검증이 가능합니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260514-003216_codex_gpt55_yolo26n_realtime_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 일반 DEEPX SDK 개발자가 안내대로 setup.sh와 run.sh를 실행하면 정상적으로 파이프라인을 구동·검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-003723_codex_gpt55_yolo26n_cascaded/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Run instructions assume the presence of model/image files at relative paths (`../../assets/models/yolo26n.dxnn`, `../../sample/img/sample_dog.jpg`), but do not explain how to obtain or prepare them.
  - No troubleshooting or environment notes for missing dependencies or path errors.
  - README does not clarify what output to expect or how to verify correct results beyond setup.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK developer, but missing guidance on required model/data files and expected outputs may block successful first use.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-004421_codex_gpt55_yolo26n_standalone_detection)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 codex-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Run instructions assume asset/sample paths exist but do not clarify how to obtain them.
  - No troubleshooting guidance for missing model/image files.
  - README omits explicit verification/test step, though session.log shows it was performed.
- **One-sentence verdict**: Most users can set up and attempt to run the app, but missing asset guidance and limited troubleshooting may block successful execution.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-004421_codex_gpt55_yolo26n_standalone_detection/)]


---

---

---

---

### R4 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, 검증 절차와 실행 로그가 완비되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 수행할 수 있습니다.


---

---

---

---

### R4 claude-code dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Requires user to manually run `dx_app`-level setup if model/sample missing (not auto-handled).
  - Assumes presence of model and sample files in parent dx_app; not self-contained.
  - No explicit troubleshooting for Python/venv or dependency issues.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but require the user to resolve missing model/sample assets in the parent dx_app, making the session only partially runnable for a new user.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md는 단계별로 명확하며, setup.sh와 run.sh가 자동 환경 감지 및 오류 안내를 제공하고, session.log에 실제 실행 증거가 포함되어 있어 DEEPX SDK 개발자가 그대로 따라 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-001808_claude_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R4 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (README, setup, run, 검증 모두 명확하게 안내됨)
- **One-sentence verdict**: README와 스크립트가 매우 상세하며, 일반 DEEPX SDK 개발자가 그대로 따라 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]  
To save this session as HTML, type: /share html


---

---

---

---

### R4 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하며, session.log에 실제 실행 및 검증 결과가 포함되어 있어, 일반 DEEPX SDK 개발자도 문제없이 설치·실행·검증이 가능합니다.


---

---

---

---

### R4 claude-code suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README, setup.sh, and run.sh are clear, complete, and verifiable; a typical DEEPX SDK developer can follow the instructions to install, run, and validate the artifact successfully.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 copilot-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 일반 DEEPX SDK 개발자가 안내대로 setup, 실행, 검증을 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260513-232053_copilot_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

---

---

---

### R5 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 일반 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 따라할 수 있습니다.


---

---

---

---

### R5 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (실행 evidence 및 경로 안내, 오류 메시지, 검증 로그 모두 제공)
- **One-sentence verdict**: README와 setup.sh, run.sh가 명확하며, session.log에 실제 실행 및 검증 evidence가 포함되어 있어 DEEPX SDK 개발자가 그대로 따라 실행 및 검증할 수 있습니다.


---

---

---

---

### R5 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 환경설치·실행·검증까지 단계별로 안내되어 있어 DEEPX SDK 개발자가 그대로 따라하면 정상적으로 파이프라인을 실행·검증할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of successful execution or verification is provided.
  - `setup.sh` assumes the presence of `dxrt-cli` and a parent `setup.sh` script, which may not exist or be documented for the user.
  - Model download and environment setup steps are not fully self-contained or robust for new users.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing execution evidence and some setup dependencies may block a typical end-user from running and verifying the artifact without additional guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-003841_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of successful setup/run/verify is provided.
  - `setup.sh` assumes the presence of `dxrt-cli` and a parent `setup.sh` for model download, which may not be obvious to new users.
  - No troubleshooting or dependency installation guidance in README/setup.sh.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing verification evidence and some setup assumptions may block first-time users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-003841_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 opencode-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and complete, setup.sh and run.sh are robust and self-explanatory, and verification steps are explicit—any DEEPX SDK developer can follow these instructions to install, run, and verify the artifact successfully.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-003730_opencode_sonnet46_yolo26n_onnx_to_dxnn/)]  
To save this session as HTML, type: /share html


---

---

---

---

### R6 opencode-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README, setup.sh, and run.sh are clear and complete; a typical DEEPX SDK developer can follow the instructions to install, run, and verify the artifact without confusion.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this pipeline as instructed.

To save this session as HTML, type: /share html  
[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-101232_opencode_cli_dx_stream/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 opencode-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README.md is clear and comprehensive, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this cascaded pipeline artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-101241_opencode_sonnet46_cascaded_inference/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no verification evidence is present.
  - `setup.sh` assumes the venv and dx_app build exist, but does not create them if missing.
  - Model download is attempted but may silently fail; user may not realize model is missing.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing verification output and fragile setup steps may block a first-time user.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-010431_opencode_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no verification evidence is present.
  - `setup.sh` assumes the venv and dx_app are already installed, but does not guide the user through missing dependency resolution.
  - Model download is attempted but may silently fail; user guidance is limited if the model is missing.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing verification output and fragile setup steps may block a typical end-user from running the app without manual troubleshooting.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-010431_opencode_sonnet46_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - None significant; all steps and contingencies are covered.
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh robustly handles environment and dependency setup, run.sh automates the workflow, and verification is explicitly provided—an end-user can reliably install, run, and validate this artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-012732_codex_gpt55_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

---

---

---

### R6 codex-cli dx_app

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 0
- **Setup completeness (1-5)**: 0
- **Run instructions completeness (1-5)**: 0
- **Verification provided (Y/N)**: no
- **Key issues**:
  - README.md, setup.sh, run.sh, and session.log are all missing.
  - No instructions or evidence for installation, execution, or verification.
  - End-user has no entrypoint or guidance to proceed.
- **One-sentence verdict**: 필수 아티팩트가 모두 누락되어 있어, 사용자는 실행 또는 검증을 전혀 진행할 수 없습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 codex-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하며, session.log에 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 진행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-015655_codex_gpt55_yolo26n_realtime_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 명확하고, 실행 및 검증 절차가 모두 제공되어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260514-020132_codex_gpt55_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 codex-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하며, 검증 로그도 제공되어 DEEPX SDK 개발자가 문제없이 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-020627_codex_gpt55_yolo26n_standalone_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 codex-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README could clarify the location of model/image assets for new users.
  - Minor: Custom input example assumes asset paths; may confuse if directory structure differs.
- **One-sentence verdict**: The artifact is fully runnable by a typical DEEPX SDK developer, with clear setup and verification, though asset path notes could be slightly improved.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-020627_codex_gpt55_yolo26n_standalone_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 copilot-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 검증 절차와 실행 방법이 잘 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-013311_copilot_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README, setup.sh, and run.sh are clear, complete, and verifiable; a typical DEEPX SDK developer can follow the instructions to install, run, and validate the artifact without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-020704_copilot_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None; all critical setup, run, and verification steps are clear and validated.
- **One-sentence verdict**:  
README, setup, and run scripts are clear, complete, and fully validated—an end-user can reliably install, run, and verify this pipeline as described.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260514-021224_copilot_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

---

---

---

### R6 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md는 단계별로 명확하며, setup.sh와 run.sh가 환경 설정과 실행을 자동화하고, session.log에 실제 실행 증거와 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no verification evidence is present.
  - README and scripts are clear, but do not mention how to obtain the model if missing (only in run.sh error).
  - No explicit verification/test step or output sample is provided.
- **One-sentence verdict**: The artifact is nearly runnable for a typical DEEPX SDK developer, but lacks verification evidence and explicit model download/setup instructions.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-022603_copilot_sonnet46_yolo26n_inference/)]


---

---

---

---

### R6 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: no
- **Key issues**:
  - session.log is missing, so no evidence of actual execution or verification is present
  - README and scripts assume model file exists but only provide a download hint if missing
  - No explicit verification/test step or output shown
- **One-sentence verdict**: The README and scripts are clear and nearly complete, but lack of session.log and verification output means a new user cannot confirm successful setup or inference without manual troubleshooting.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 cursor-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - (none significant; all critical steps and troubleshooting are covered)
- **One-sentence verdict**:  
README.md is clear and actionable, setup.sh and run.sh are robust and self-explanatory, and verification is well-documented—an end-user can reliably install, run, and validate this artifact as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-012518_cursor_composer_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경설치·실행·검증까지 단계별 안내가 완비되어 있어 일반 DEEPX SDK 개발자도 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-020905_cursor_composer_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `dxrt-cli` is not installed or not in PATH (`dxrt-cli: command not found` in session.log).
  - Some users may be confused by multiple venvs and plugin install steps.
  - Model download may fail silently; manual intervention is only briefly mentioned.
- **One-sentence verdict**: The README is clear and setup/run steps are mostly complete, but missing `dxrt-cli` and possible model/plugin install issues may block some users without further troubleshooting guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]


---

---

---

---

### R9 cursor-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (모든 주요 단계와 경로가 명확히 안내됨)
- **One-sentence verdict**: README와 setup.sh, run.sh가 명확하고 완전하며, session.log로 검증까지 제공되어 DEEPX SDK 개발자가 문제없이 실행 및 검증할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 cursor-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, 검증 절차와 로그가 잘 제공되어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-023726_cursor_composer_yolo26n_compile/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 cursor-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 표준 DEEPX SDK 개발자가 안내대로 setup, run, verify를 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-023726_cursor_composer_yolo26n_compile/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, 검증 절차와 문제 해결 안내까지 포함되어 있어 DEEPX SDK 개발자가 그대로 따라 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-013241_claude_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경설치·실행·검증까지 모든 단계가 친절하게 안내되어 있어 일반 DEEPX SDK 개발자도 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-020702_claude_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and troubleshooting are clearly documented.
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this pipeline as instructed.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 매우 명확하며, 모든 주요 단계(설치, 실행, 검증)가 실제 로그와 함께 안내되어 있어 DEEPX SDK 개발자가 문제없이 세션 아티팩트를 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-101741_claude_code_dx_stream_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경 설정부터 실행, 검증까지 단계별로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치 및 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-023208_claude_sonnet46_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R5 claude-code suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Model file path assumes `../../assets/models/yolo26n.dxnn` exists, but no guidance if missing.
  - `sanity_check.sh` path in session.log fails (`No such file or directory`), which may confuse users.
  - Some users may be unclear on how to obtain or compile the model if not present.
- **One-sentence verdict**: The artifact is nearly runnable for a typical DEEPX SDK developer, but model file location and missing sanity check script may block less experienced users without further guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-023208_claude_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Compilation failed initially due to NHWC/NCHW mismatch; workaround is mentioned in session.log but not in README.
  - README does not warn about possible input format pitfalls or how to resolve them if encountered.
  - The run.sh script expects a sample image at a specific path, which may not exist for all users.
- **One-sentence verdict**: The README and setup are clear and thorough, but a critical compilation pitfall (input format mismatch) is not surfaced in the user instructions, so a typical end-user may encounter and struggle with this error without additional guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-015239_opencode_sonnet46_yolo26n_compile/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 opencode-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README lacks explicit verification/test instructions (relies on run.sh output).
  - No sample input/output or expected result shown in README.
- **One-sentence verdict**: The artifacts are well-structured and runnable by a typical end-user, with clear setup and execution, but the README could be improved by adding explicit verification steps and sample outputs.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-021319_codex_gpt55_dx_m1_yolo26n_inference/)]  
To save this session as HTML, type: /share html


---

---

---

---

### R7 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any): 
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하며, session.log로 실행 검증까지 제공되어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.


---

---

---

---

### R7 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 상대 경로 입력 영상(`../../dx_stream/samples/videos/dogs.mp4`)이 실제 환경에서 존재하지 않거나 접근 불가 시 실행 실패 가능
  - setup.sh가 venv 생성/활성화는 안내하지만, 일부 환경에서 GStreamer 플러그인/모델 다운로드 실패 시 수동 조치 필요
  - session.log에 실제 파이프라인 실행 오류(입력 파일 접근 불가) 발생
- **One-sentence verdict**: README와 실행 스크립트는 매우 명확하나, 입력 파일 경로 문제 등으로 인해 사용자가 바로 성공적으로 실행하기는 어렵고, 환경/경로 조정이 필요합니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification is provided.
  - README does not mention how to obtain the required `yolo26n.dxnn` model file.
  - If `dx_engine` is not installed, setup.sh does not provide remediation steps.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK user, but missing session.log and unclear model acquisition instructions may block successful first use.

[DX-AGENTIC-DEV: DONE (output-dir: not specified)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no execution evidence is provided.
  - README does not mention how to obtain the required `yolo26n.dxnn` model file.
  - `run.sh` assumes model/image paths that may not exist in a fresh checkout.
- **One-sentence verdict**: The artifacts are nearly runnable for a DEEPX SDK user, but lack of verification evidence and unclear model asset instructions may block a first-time user.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Calibration dataset directory missing (`FileNotFoundError` for `/.../calibration_dataset`)
  - README does not mention calibration data preparation or required files
  - Error in session.log may block successful compilation/verification
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing calibration data setup prevents a typical user from running the full pipeline successfully.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-022150_codex_gpt55_dx_m1_yolo26n_compile/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 codex-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README does not explicitly mention where to find/download the model and sample image if missing.
  - Minor: Direct run examples assume asset paths exist; could clarify asset prerequisites.
- **One-sentence verdict**: The artifact is runnable by a typical end-user with clear setup and run instructions, though asset path prerequisites could be more explicit.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-023540_codex_gpt55_yolo26n_object_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `gi` module (PyGObject) is missing, causing pipeline.py to fail unless user installs it manually.
  - README does not mention installing system-level dependencies (e.g., `python3-gi`, GStreamer plugins).
  - Some environment activation steps may confuse users if venvs are not present or named differently.
- **One-sentence verdict**: The artifact is nearly runnable with clear instructions, but missing Python/system dependencies (notably `gi`) will block a typical user unless they troubleshoot and install them manually.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260514-024528_codex_gpt55_yolo26n_realtime_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - None observed; all required files, setup, and run instructions are present and clear.
- **One-sentence verdict**: The artifacts are well-structured and documented, enabling a typical DEEPX SDK developer to set up, run, and verify the cascaded pipeline without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-025241_codex_gpt55_yolo26n_cascaded/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `setup.sh` does not install dependencies or create a Python venv.
  - Model file presence is only checked, not ensured or downloaded.
  - `session.log` is missing, so no evidence of successful execution or verification.
- **One-sentence verdict**: The README is clear and run.sh is usable, but setup.sh lacks environment setup and verification evidence is missing, so a typical user may encounter missing dependencies or model issues.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-025845_codex_gpt55_yolo26n_standalone_detection)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 codex-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no verification evidence is provided.
  - `setup.sh` does not install dependencies or create a Python virtual environment.
  - Model file presence is only checked, not ensured or downloaded.
- **One-sentence verdict**: The README is clear and run instructions are good, but missing dependency setup and lack of verification output mean a typical user may encounter issues running or validating the artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-025845_codex_gpt55_yolo26n_standalone_detection)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 cursor-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 표준 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-025023_cursor_gpt53_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 환경 설정부터 실행, 검증까지 단계별 안내가 완벽하게 제공되어 DEEPX SDK 개발자가 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-030839_cursor_opus47_yolo26n_inference/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 cursor-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and troubleshooting are clearly documented.
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-032149_cursor_gpt52_dx_m1_yolo26n_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 cursor-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - None significant; all steps, dependencies, and troubleshooting are clearly addressed.
- **One-sentence verdict**: README, setup, and run scripts are comprehensive and clear—an end-user can reliably install, run, and verify this cascaded pipeline session without prior session knowledge.

To save this session as HTML, type: /share html  
[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-032505_cursor_gpt52_yolo26n_cascaded/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `setup.sh` expects a pre-existing compiler venv at a hardcoded path; missing it causes a hard fail with no recovery steps.
  - `run.sh` assumes `detect_yolo26n.py` exists, but this file is not listed or described in the README or file table.
  - The README omits troubleshooting for common failures (e.g., missing venv, missing files).
- **One-sentence verdict**: The session is nearly runnable for a DEEPX developer, but missing context for required files and strict venv checks may block less-experienced users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-032935_cursor_composer_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 cursor-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - No explicit troubleshooting for possible `dx_engine` import issues (only a warning).
  - The README could clarify the purpose of each step (e.g., why both `compile.py` and `verify.py` are run).
- **One-sentence verdict**: The session artifacts are well-structured and, with the provided README and robust setup.sh, a typical DEEPX SDK developer can install, run, and verify the compilation with minimal friction.

To save this session as HTML, type: /share html

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-032935_cursor_composer_yolo26n_compile/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, 검증 절차와 실행 방법이 구체적으로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-025606_claude_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README가 명확하고, setup.sh와 run.sh가 완전하며, session.log에 실행 및 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-030954_claude_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - (none significant; all requirements and steps are clearly addressed)
- **One-sentence verdict**:  
README, setup, and run scripts are clear, complete, and verifiably functional—an end-user can reliably install, run, and validate this pipeline as instructed.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/<session_id>/)]
To save this session as HTML, type: /share html


---

---

---

---

### R6 claude-code dx_stream_cascaded

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 0
- **Setup completeness (1-5)**: 0
- **Run instructions completeness (1-5)**: 0
- **Verification provided (Y/N)**: no
- **Key issues**:
  - README.md, setup.sh, run.sh, and session.log are all missing.
  - No instructions or evidence are available for the user to follow.
  - The session output is incomplete and unusable as delivered.
- **One-sentence verdict**: 필수 실행 및 안내 파일이 모두 누락되어, 사용자가 세션 산출물을 실행하거나 검증할 수 없습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, end-user가 안내대로 환경을 세팅하고 실행 및 검증까지 문제없이 진행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-033520_claude_sonnet46_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R6 claude-code suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md는 명확하며, setup.sh와 run.sh가 완전하게 환경 설정과 실행을 안내하고, session.log에 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-033520_claude_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 opencode-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README.md is clear and complete, setup.sh and run.sh are robust and self-explanatory, and verification steps are well-documented—an end-user can reliably install, run, and verify this artifact as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-030157_opencode_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 opencode-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh가 명확하고 완전하며, session.log에 실행 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-031636_opencode_sonnet46_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

---

---

---

### R8 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 설치·실행·검증 절차가 모두 구체적으로 안내되어 있어 일반 DEEPX SDK 개발자도 문제없이 세션 아티팩트를 실행할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 opencode-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README는 단계별로 명확하며, setup.sh와 run.sh가 환경 설정 및 실행을 자동화하고, session.log에 실제 실행 증거와 검증 결과가 포함되어 있어 일반 DEEPX SDK 개발자도 문제없이 설치, 실행, 검증이 가능합니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-102708_opencode_cli_dx_stream_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - No explicit verification/test command or output in README or session.log.
  - Assumes model and sample image exist at default paths, but does not guide user if missing.
  - Prerequisite steps for `dx_engine`/DX-RT install are referenced but not detailed.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK user, but lacks explicit verification steps and clearer guidance for missing model/assets, which may hinder first-time success.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - No explicit verification/test command or output (no verify.py or test evidence).
  - Assumes presence of model file and sample image at hardcoded paths, which may not exist for all users.
  - Prerequisite steps for installing `dx_engine` are referenced but not fully detailed.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but lack built-in verification and depend on external model/data availability, so a typical end-user may need minor troubleshooting to run successfully.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - session.log shows errors (KeyError: 'WORK_DIR', FileNotFoundError for yolo26n.onnx) that may confuse users or block execution
  - README does not explain how to resolve these errors or what to check if compilation fails
  - Some steps (e.g., venv activation, sanity check) are robust, but error handling is not fully user-friendly
- **One-sentence verdict**: The artifact is mostly runnable for a DEEPX SDK developer, but error messages and missing troubleshooting guidance may hinder a smooth first run.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-031323_codex_gpt55_yolo26n_compile/)]


---

---

---

---

### R8 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 모델 파일(`yolo26n.dxnn`) 및 샘플 이미지/비디오 경로가 실제로 존재하는지 불명확
  - `dx_engine` 미설치 시 안내는 있으나, 설치 방법이 README에 직접 안내되어 있지 않음
  - `app.yaml` 누락으로 일부 프레임워크 검증 경고 발생
- **One-sentence verdict**: 전반적으로 명확하고 실행 절차가 잘 안내되어 있으나, 모델/샘플 데이터 준비와 dx_engine 설치 안내가 부족해 초심자에게는 부분적으로 실행이 어려울 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - venv activation is required but not enforced in run.sh (error shown if omitted)
  - Some dependencies (e.g., pydxs) not auto-installed; user must resolve missing packages
  - Model/postprocess auto-download is attempted but may silently fail
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but require the user to manually activate the venv and resolve missing Python dependencies for successful execution.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-033956_codex_gpt55_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - None significant; all steps, environment checks, and troubleshooting are clearly covered.
- **One-sentence verdict**: README, setup, and run scripts are comprehensive and clear, enabling a typical DEEPX SDK developer to install, run, and verify the cascaded pipeline without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-102928_codex_cli_dx_stream_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - setup.sh assumes existence of `requirements.txt` in a parent directory, which may not be present or correct for this session
  - No explicit instructions for missing model/image assets if not present in the expected locations
  - The setup does not ensure all DEEPX-specific dependencies (e.g., dx_engine) are installed or built
- **One-sentence verdict**: The README and scripts are clear and mostly runnable, but setup.sh’s reliance on external files and lack of DEEPX-specific dependency handling may block a typical user without further guidance.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-035354_codex_gpt55_yolo26n_inference)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 codex-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `setup.sh` assumes `requirements.txt` exists at a relative path, but this is not mentioned in the README and may not be present.
  - The README does not clarify how to obtain the required model (`yolo26n.dxnn`) or sample image if missing.
  - The setup script attempts to source a runtime venv, but this is not explained to the user.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK developer, but missing details about model/assets acquisition and unclear setup dependencies may block a first-time user.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-035354_codex_gpt55_yolo26n_inference/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 copilot-cli compiler

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 0
- **Setup completeness (1-5)**: 0
- **Run instructions completeness (1-5)**: 0
- **Verification provided (Y/N)**: no
- **Key issues**:
  - README.md, setup.sh, and run.sh are completely missing.
  - No instructions for installation, environment setup, or execution.
  - session.log only shows partial config and validation, not user guidance.
- **One-sentence verdict**: 핵심 실행 및 설치 안내 파일이 모두 누락되어, 사용자가 세션 산출물을 실행하거나 검증할 수 없습니다.

[DX-AGENTIC-DEV: DONE]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 설치·실행·검증 절차가 모두 제공되어 DEEPX SDK 개발자가 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-033614_copilot_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and troubleshooting are clearly documented.
- **One-sentence verdict**:  
  README.md is clear, setup.sh and run.sh are robust, and session.log shows successful execution—an end-user can reliably install, run, and verify this pipeline as instructed.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/<session_id>/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README는 명확하고 단계별로 안내하며, setup.sh와 run.sh도 완전하게 구성되어 있어 DEEPX SDK 개발자가 그대로 따라 실행 및 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-035140_copilot_sonnet46_yolo26n_cascaded/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification.
  - `setup.sh` assumes a venv and model exist or can be downloaded, but does not guarantee it.
  - Verification script (`verify.py`) is referenced but not evidenced as working.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing execution evidence and fragile setup steps may block a typical end-user.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-035712_copilot_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no evidence of actual execution or verification is present.
  - `setup.sh` assumes a venv and model exist or can be downloaded, but does not guarantee this for all users.
  - Verification step is listed, but no `verify.py` output or existence is confirmed.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing session.log and weak guarantees in setup.sh mean a new user may encounter missing model or venv issues and cannot confirm verification succeeded.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-035712_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 copilot-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README가 명확하며, setup.sh와 run.sh가 완전하게 제공되어 있어 DEEPX SDK 개발자가 안내대로 설치, 실행, 검증을 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-041554_copilot_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

---

---

---

### R8 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, session.log에 실행 및 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 그대로 따라 실행 및 검증할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - None; all major steps (prereqs, setup, run, verification) are clearly covered.
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh and run.sh are robust, and session.log confirms successful execution—an end-user can reliably install, run, and verify this pipeline as instructed.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-103137_copilot_gpt41_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - None; all critical steps (venv, model, plugin, run modes) are covered with clear commands.
- **One-sentence verdict**:  
README.md is exceptionally clear and complete; a typical DEEPX SDK developer can follow it to set up, run, and verify the cascaded pipeline without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-044457_copilot_sonnet46_yolo26n_cascaded/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no verification evidence is provided.
  - `setup.sh` assumes `dxrt-cli` and model assets exist but does not install/check them.
  - Paths to test images/videos may not exist, risking run failures.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing verification output and asset checks mean a typical user may encounter setup or runtime errors.

[DX-AGENTIC-DEV: DONE]


---

---

---

---

### R8 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - session.log이 없어서 실제 실행/검증 결과가 제공되지 않음
  - setup.sh에서 dxrt-cli, 모델 파일, 테스트 이미지/비디오의 존재를 가정하지만, 준비 방법이 불명확함
  - Python 의존성 외에 DX SDK 관련 설치 안내가 부족함
- **One-sentence verdict**: README와 스크립트는 비교적 명확하지만, session.log 부재와 일부 환경/파일 준비 안내 부족으로 완전한 재현성은 보장되지 않습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하며, 검증 결과와 실행 로그도 충분히 제공되어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-041617_codex_gpt55_dx_m1_yolo26n_compile/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - dx_engine is missing from the active venv; setup.sh fails and requires manual intervention.
  - README does not warn about the need to pre-build/install dx_engine before setup.sh.
  - run.sh and README assume model and input paths exist but do not guide on obtaining them.
- **One-sentence verdict**: The README is clear and the run instructions are mostly complete, but setup.sh fails unless the user manually builds dx_engine, so a typical end-user will encounter a blocking error and need to troubleshoot before running the app.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-042925_codex_gpt55_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - venv activation and `pydxs` import are not fully automated; user must manually activate venv before running Python scripts.
  - `pipeline.py --help` fails if venv is not activated, which is not enforced in run.sh.
  - Some error messages in session.log (e.g., missing `gi` module) suggest missing dependencies or unclear setup order.
- **One-sentence verdict**: The README is clear and setup/run scripts are mostly complete, but manual venv activation and missing dependency handling may block less experienced users from running the pipeline smoothly.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-043408_codex_gpt55_yolo26n_realtime_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh robustly checks all dependencies, run.sh is straightforward, and session.log provides strong evidence—an end-user can reliably install, run, and verify this artifact as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_stream/dx-agentic-dev/20260514-043951_codex_gpt55_yolo26n_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 codex-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README does not explicitly mention where to find the model and sample image/video files (relative paths may confuse some users).
  - No troubleshooting section for common errors (e.g., missing dependencies, model file not found).
- **One-sentence verdict**: The artifact is runnable by a typical end-user with clear setup and run instructions, though minor clarifications in the README would further improve usability.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-044933_codex_gpt55_yolo26n_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 codex-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README does not explicitly mention model/sample asset prerequisites or troubleshooting for missing files.
  - setup.sh assumes the presence of a parent venv-dx-runtime, which may not exist in all setups.
  - run.sh defaults may confuse users if asset paths are missing or moved.
- **One-sentence verdict**: The artifact is runnable and well-documented for a typical DEEPX SDK developer, but could be improved with clearer asset prerequisites and troubleshooting notes.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-044933_codex_gpt55_yolo26n_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 opencode-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 환경 설정부터 실행, 검증까지 단계별로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치 및 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-040231_opencode_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - venv activation logic assumes a shared venv exists or can be created, but does not guide users if both are missing or if Python is not installed.
  - The README and scripts assume the presence of model/data assets (`yolo26n.dxnn`, sample images/videos) without explicit download/setup instructions.
  - If `dx_engine` is not importable, the error message is helpful, but the required install path (`../../install.sh ...`) may not be obvious to all users.
- **One-sentence verdict**: 대부분의 DEEPX SDK 개발자는 README와 스크립트만으로 실행할 수 있으나, 모델/데이터 자산 및 dx_engine 환경이 미설치된 경우 추가 안내가 필요합니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-041812_opencode_sonnet46_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - None significant; all steps and troubleshooting are clearly documented.
- **One-sentence verdict**: README, setup, and run scripts are clear and complete—an end-user can reliably install, run, and verify the pipeline as instructed.

[DX-AGENTIC-DEV: DONE]


---

---

---

---

### R9 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Video input path error: default video file may not exist or is misreferenced, causing pipeline failure.
  - Model download and venv activation steps are clear, but error handling for missing dependencies is limited.
  - Pipeline error in session.log ("Could not open resource for reading") may confuse users if sample video is missing.
- **One-sentence verdict**: The README and scripts are clear and comprehensive, but a missing or misreferenced sample video can block successful execution for typical users.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 opencode-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, end-user가 안내대로 setup.sh와 run.sh를 실행해 정상적으로 동작 및 검증을 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-043542_opencode_sonnet46_yolo26n_object_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 opencode-cli suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 표준 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-043542_opencode_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, end-user가 안내대로 setup.sh와 run.sh를 실행해 DXNN 컴파일 및 검증을 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-034910_claude_sonnet46_yolo26n_compile/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup.sh, run.sh가 명확하고 완전하게 안내되어 있어, 일반 DEEPX SDK 개발자도 문제없이 설치, 실행, 검증을 할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-040220_claude_sonnet46_yolo26n_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 claude-code dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Model path and venv activation steps are somewhat complex and may confuse new users.
  - Error in session.log shows pipeline failed initially due to missing model path, though later succeeded.
  - Some manual intervention may be needed if model download or plugin registration fails.
- **One-sentence verdict**: The README is clear and covers most steps, but minor path/activation pitfalls and initial pipeline errors mean a typical user may need to troubleshoot before achieving a successful run.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-103846_claude_code_dx_stream/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R7 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear, setup.sh robustly handles environment/model setup, run.sh is straightforward, and session.log confirms successful end-to-end execution—an end-user can reliably install, run, and verify this artifact as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-103855_claude_code_dx_stream_cascaded/)]  
To save this session as HTML, type: /share html


---

---

---

---

### R7 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and complete, setup.sh and run.sh are robust, and session.log confirms successful setup and inference—an end-user can reliably install, run, and verify this artifact as intended.


---

---

---

---

### R7 claude-code suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup/run 스크립트가 명확하며, session.log에 실제 실행 결과와 PASS가 모두 기록되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 copilot-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None significant; all steps and context are clear and actionable.
- **One-sentence verdict**:  
README.md is clear, setup.sh and run.sh are robust and self-contained, and verification is explicit—any DEEPX SDK developer can follow these instructions to install, run, and validate the artifact successfully.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-051554_copilot_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, end-user가 안내대로 설치 및 실행, 검증까지 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-053147_copilot_sonnet46_yolo26n_object_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues** (if any):
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경설치·실행·검증까지 단계별 안내가 완비되어 있어 일반 DEEPX SDK 개발자도 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README가 명확하고, setup.sh와 run.sh가 완전하며, session.log로 실행 검증까지 제공되어 DEEPX SDK 개발자가 그대로 따라 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `setup.sh` assumes a specific directory structure and a parent `dx_app` repo with its own `setup.sh`, which may not exist or be initialized.
  - No actual verification evidence in `session.log`; user cannot confirm artifact correctness.
  - Model and sample video paths are hardcoded and may not match all environments.
- **One-sentence verdict**: The README is clear and run.sh is usable, but setup.sh’s dependency on external scripts and missing verification evidence mean a typical user may encounter blocking issues.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-055108_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 copilot-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: no
- **Key issues**:
  - `session.log` is missing, so no execution evidence is provided.
  - README and scripts assume the user understands the directory structure (`RUNTIME_ROOT`), which may confuse some users.
  - No explicit verification step or output sample is shown.
- **One-sentence verdict**: The README and scripts are clear and mostly complete, but missing session.log and verification evidence prevent a full PASS for end-user runnability.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-055108_copilot_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, end-user가 안내대로 setup.sh와 run.sh를 실행해 DXNN 컴파일 및 검증을 문제없이 수행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-051948_codex_gpt55_yolo26n_compile/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Model and sample image paths in run.sh/README are relative and may not resolve unless run from a specific directory structure.
  - setup.sh assumes dx_engine is already built/installed; if not, user must manually run install/build in dx_app root.
  - No explicit verification/test command or output example in README; user must infer from session.log.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK developer, but path assumptions and missing explicit verification steps may block less experienced users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-054905_codex_gpt55_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `pipeline.py` and `run_yolo26n_realtime_detection.sh` are referenced but not shown; their correctness is assumed.
  - The error in session.log (`pydxs not found. Activate venv...`) suggests the venv activation may not persist or is not clearly enforced for all commands.
  - The README does not explicitly mention troubleshooting for venv or missing dependencies beyond the initial checks.
- **One-sentence verdict**: The artifact is nearly runnable by a typical end-user, with clear instructions and setup, but venv activation issues and minor troubleshooting gaps may block some users.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-055338_codex_gpt55_yolo26n_realtime_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 명확하며, 실행 및 검증 절차가 모두 제공되어 DEEPX SDK 개발자가 문제없이 세션 아티팩트를 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-060007_codex_gpt55_yolo26n_cascaded/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `dxrt-cli` prerequisite is not installed or explained; user may not know how to obtain it.
  - Model and sample image paths are relative and may not exist, causing run.sh to fail.
  - No troubleshooting or dependency version guidance for `dx_engine` import failures.
- **One-sentence verdict**: 대부분의 DEEPX SDK 개발자는 README와 스크립트만으로 실행할 수 있으나, dxrt-cli 미설치 및 샘플 경로 문제로 일부 사용자는 추가 안내가 필요합니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-060557_codex_gpt55_yolo26n_standalone_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 codex-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Prerequisite `dxrt-cli` is not installed or not found (`command not found` in session.log).
  - Model and sample image paths are relative and may not exist if user is not in the correct directory.
  - No troubleshooting guidance for missing dependencies or failed sanity check.
- **One-sentence verdict**: The README is clear and the setup/run flow is mostly complete, but missing or misconfigured prerequisites (notably `dxrt-cli`) and unclear model/image path handling may block a typical end-user from successful execution.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-060557_codex_gpt55_yolo26n_standalone_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 opencode-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README와 스크립트가 명확하며, 환경설치부터 실행, 검증까지 단계별 안내가 잘 되어 있어 DEEPX SDK 개발자가 문제없이 아티팩트를 실행·검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-052030_opencode_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Asset/model paths (`../../assets/models/yolo26n.dxnn`, etc.) are not guaranteed to exist in the session directory; no instructions to obtain or link them.
  - `dx_postprocess` dependency for C++ variants may not be available; only a warning is given, not a fix.
  - Setup does not install all required Python dependencies if using a shared venv.
- **One-sentence verdict**: The README is clear and the run.sh script works if all assets and dependencies are present, but missing asset/model files and incomplete setup steps may block a typical end-user from running the app out-of-the-box.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-055149_opencode_sonnet46_yolo26n_detection/)]


---

---

---

---

### R10 opencode-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh가 명확하고 단계별로 안내되어 있어, 일반 DEEPX SDK 개발자도 문제없이 설치, 실행, 검증을 할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Model and venv paths require careful navigation; relative pathing may confuse some users.
  - Error in session.log (`no property "num-sources" in element "dxgather"`) suggests pipeline may not run as expected.
  - Some manual steps (e.g., model download, plugin install) may fail silently or require troubleshooting.
- **One-sentence verdict**:  
README is clear and mostly complete, but a pipeline property error and some pathing assumptions mean a typical user may need to troubleshoot before successful execution.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-104256_opencode_dx_stream_cascaded/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `dxrt-cli` prerequisite is not installed or explained; command fails.
  - No troubleshooting for missing `dx_engine` or model/image files.
  - Setup assumes venvs exist or can be created, but does not guide user if Python/venv is missing.
- **One-sentence verdict**: The README is clear and the run/verify flow is mostly complete, but missing prerequisite installation steps and unclear error handling may block a typical end-user.

[DX-AGENTIC-DEV: DONE (output-dir: dx_app/dx-agentic-dev/20260514-060557_codex_gpt55_yolo26n_standalone_detection)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 opencode-cli suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - Prerequisite `dxrt-cli` is referenced but not installed or explained; command fails (`command not found`).
  - Setup does not ensure `dx_engine` is actually available—if not, user is left without a clear fix.
  - Model and sample image paths are relative and may not exist, risking run failures.
- **One-sentence verdict**: The artifact is nearly runnable for a DEEPX SDK user, but missing or unclear prerequisites and fragile path assumptions may block a first-time user without additional troubleshooting.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-060557_codex_gpt55_yolo26n_standalone_detection/)]  
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh` does not actually run inference; it only shows how to load the model in Python, leaving the user to figure out the rest.
  - README lacks explicit step-by-step instructions for running `setup.sh`, `compile.py`, and `run.sh` in order.
  - No troubleshooting or environment notes for common DX-M1 pitfalls (e.g., NPU, driver).
- **One-sentence verdict**: The artifacts are nearly runnable by a typical DEEPX SDK user, but require moderate inference experience to bridge missing steps and fully execute a test run.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-061013_copilot_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 모델 자동 다운로드가 실패할 경우 수동 다운로드 안내만 제공됨 (직접 링크 없음)
  - 샘플 이미지 경로가 고정되어 있어, 파일이 없으면 직접 준비 필요
- **One-sentence verdict**: 명확한 README와 자동화된 스크립트, 검증 로그가 제공되어 DEEPX SDK 개발자가 문제없이 설치·실행·검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-062656_copilot_sonnet46_yolo26n_object_detection/)]


---

---

---

---

### R10 copilot-cli dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh가 명확하고 단계별로 안내되어 있어, 일반 DEEPX SDK 개발자도 문제없이 설치, 실행, 검증을 할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh and run.sh are robust, and session.log confirms successful execution and verification; a typical end-user can follow the instructions to install, run, and verify the cascaded pipeline without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-104357_copilot_gpt41_dx_stream_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 copilot-cli runtime

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 0
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: no
- **Key issues**:
  - README.md is missing, so users have no entrypoint instructions.
  - session.log is missing, so there is no evidence of successful execution.
  - run.sh assumes the presence of yolo26n_sync.py and model/image files, but does not document or check their existence.
- **One-sentence verdict**: Without a README or session.log, a typical user cannot reliably install, run, or verify this artifact.

[DX-AGENTIC-DEV: DONE]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 copilot-cli suite

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 0
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: no
- **Key issues**:
  - README.md is missing, so users lack entrypoint instructions.
  - session.log is missing, so there is no evidence of successful execution.
  - run.sh assumes the presence of yolo26n_sync.py and model/image files, but does not guide the user if missing.
- **One-sentence verdict**: Without a README or session.log, a typical user cannot confidently install, run, or verify this artifact.

[DX-AGENTIC-DEV: DONE (output-dir: )]


---

---

---

---

### R8 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - None; all critical steps and troubleshooting are covered.
- **One-sentence verdict**:  
README, setup.sh, and run.sh are clear, complete, and robust—any DEEPX SDK developer can follow the instructions to install, run, and verify the artifact successfully.


---

---

---

---

### R8 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 스크립트가 명확하며, 일반 DEEPX SDK 개발자가 안내에 따라 설치, 실행, 검증을 문제없이 수행할 수 있습니다.


---

---

---

---

### R8 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues** (if any):
  - 없음 (No significant issues found)
- **One-sentence verdict**: README.md is clear and comprehensive, setup.sh and run.sh automate all required steps, and session.log provides strong verification—an end-user can reliably install, run, and verify this artifact as intended.


---

---

---

---

### R8 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md is clear and comprehensive, setup.sh and run.sh are robust and self-healing, and session.log provides strong evidence that a typical DEEPX SDK developer can install, run, and verify this artifact without confusion.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R8 claude-code suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**:  
README, setup.sh, and run.sh are clear, complete, and verifiable; a typical DEEPX SDK developer can follow the instructions to install, run, and validate the artifact without confusion.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-064639_claude_sonnet46_yolo26n_object_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: yes
- **Key issues**:
  - `dx_engine` wheel warning if missing, but clear fallback and not blocking for compilation-only use.
  - None critical; all steps and troubleshooting are well documented.
- **One-sentence verdict**: README and scripts are clear, robust, and complete—an end-user can reliably set up, run, and verify this artifact as intended.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-071419_claude_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - NPU check fails if `dxrt-cli` is missing, but fallback is explained and setup continues.
  - Model auto-download may fail silently if `APP_ROOT/setup.sh` is broken, but warning is shown.
- **One-sentence verdict**: README is clear and comprehensive; setup and run steps are straightforward, and verification is present—end-users can reliably run and validate this artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-072657_claude_sonnet46_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh가 매우 명확하며, 실행 및 검증 절차가 구체적으로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-104628_claude_code_dx_stream/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 claude-code dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Model/video paths in examples may not match actual environment, causing file-not-found errors.
  - Virtual environment activation and plugin/library checks are described, but troubleshooting steps are limited.
  - Some commands assume directory structure familiarity; relative paths may confuse new users.
- **One-sentence verdict**: The README is clear and mostly complete, but path mismatches and implicit environment assumptions may block first-time users from a smooth run without manual intervention.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-104638_claude-code_dx_stream_cascaded/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 claude-code runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `dxrt-cli` is missing, causing NPU check to fail (may confuse users).
  - No explicit verification or test output guidance in README or session.log.
  - Model download step may silently fail if `APP_ROOT/setup.sh` is missing or broken.
- **One-sentence verdict**: The README is clear and the run path is mostly automated, but missing dependencies and lack of verification steps may block a typical user from fully validating the artifact.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-074847_claude_sonnet46_yolo26n_detection/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R9 claude-code suite

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `dxrt-cli` is missing, causing NPU check to fail (may confuse users).
  - No explicit verification step or output validation in README or scripts.
  - Model download relies on `$APP_ROOT/setup.sh`, but success is not guaranteed or checked.
- **One-sentence verdict**: The README is clear and running is straightforward, but missing dependencies and lack of verification steps may block a typical user from fully validating the session.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-074847_claude_sonnet46_yolo26n_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, 검증 및 실행 절차가 구체적으로 안내되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-compiler/dx-agentic-dev/20260514-081427_claude_sonnet46_yolo26n_compile/)]
To save this session as HTML, type: /share html


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues)
- **One-sentence verdict**: README와 스크립트가 명확하며, 환경 설정·실행·검증 절차가 모두 안내되어 있어 DEEPX SDK 개발자가 문제없이 실행할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-083038_claude_sonnet46_yolo26n_object_detection/)]


---

---

---

---

### R10 claude-code dx_stream

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - 없음
- **One-sentence verdict**: README가 명확하며, setup.sh와 run.sh가 완전하게 환경을 구성하고 실행을 안내하며, session.log에 실제 실행 및 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증할 수 있습니다.


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 claude-code dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Pipeline execution fails due to `dxgather` property error (`no property "num-sources" in element "dxgather"`).
  - README assumes user can resolve missing GStreamer plugins or model files, but does not provide troubleshooting steps for pipeline errors.
  - Some path assumptions (e.g., model/video locations) may not match all user environments.
- **One-sentence verdict**: The README and setup are clear and mostly complete, but a critical pipeline error prevents successful end-to-end execution without manual debugging.

[DX-AGENTIC-DEV: DONE (output-dir: dx-agentic-dev/20260514-104740_claude_gpt41_dx_stream_cascaded/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**: README와 setup.sh, run.sh 모두 명확하며, 제공된 안내만 따라도 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증까지 완료할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-085412_claude_sonnet46_yolo26n_object_detection/)]


---

[DX-AGENTIC-DEV: START]

---

---

---

### R10 claude-code suite

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - 없음 (No significant issues found)
- **One-sentence verdict**:  
README.md는 명확하며, setup.sh와 run.sh가 완전하게 환경을 준비하고 실행할 수 있도록 안내하고, session.log에 검증 결과가 포함되어 있어 DEEPX SDK 개발자가 문제없이 설치, 실행, 검증을 할 수 있습니다.

[DX-AGENTIC-DEV: DONE (output-dir: dx-runtime/dx_app/dx-agentic-dev/20260514-085412_claude_sonnet46_yolo26n_object_detection/)]  
To save this session as HTML, type: /share html

---

---

---

### R11 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 `./calibration_dataset/0.jpeg`를 참조하는데, 이 경로는 session.log에서 `ln -sfn ../../dx_com/calibration_dataset`로 생성된 **머신 종속 심볼릭 링크**다. 다른 환경에서는 링크 대상이 존재하지 않아 `run.sh`가 즉시 실패한다.
  - README Quick Start에서 `bash run.sh`가 "inference 실행"처럼 보이지만, 실제로는 `verify.py` (ONNX vs DXNN 수치 비교)를 실행한다 — 목적이 명시되지 않아 사용자가 혼동할 수 있다.
  - `setup.sh`의 dx_engine wheel 설치 구문(`head -n 1 || true`)이 wheel 미발견 시 **silent-fail**하므로, `verify.py`에서 `dx_engine` import 오류가 발생해도 사용자가 원인을 역추적하기 어렵다.
- **One-sentence verdict**: SUITE_ROOT 감지와 venv 구성은 견고하나, `calibration_dataset` 심볼릭 링크가 머신 종속적이어서 다른 환경의 사용자는 `run.sh`를 그대로 실행할 수 없다.


---

---

---

### R11 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `session.log`에서 sanity check FAIL (`dxrt-cli: command not found`, exit 127) — dx-runtime 환경이 정상적으로 설치되지 않은 상태에서 세션이 생성됐으며, 실제 inference 실행 증거가 없음
  - `run.sh`의 `source setup.sh 2>/dev/null || true` 패턴이 setup 실패를 묵살하여, dx_engine 미설치 환경에서도 run.sh가 계속 진행되다가 원인 불명의 에러로 종료될 수 있음
  - README에 사전 요구사항(dx-runtime 빌드 완료, `venv-dx-runtime` 존재 여부) 및 예상 출력 결과가 명시되지 않아, 처음 접하는 사용자가 환경 문제인지 사용법 문제인지 구분하기 어려움

- **One-sentence verdict**: sanity check 실패로 실제 inference 실행이 검증되지 않은 채 세션이 종료됐으며, README의 사전 요구사항 누락과 run.sh의 오류 묵살 패턴으로 인해 환경이 갖춰지지 않은 사용자가 실행 실패 원인을 파악하기 어렵다.


---

---

---

### R11 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log`에 실제 파이프라인 실행 출력이 없음 — syntax check·property check만 기록되어 있고, `pipeline.py`가 NPU에서 실제로 동작했다는 증거가 없음
  - `run.sh`가 최종적으로 `run_yolo26n_realtime_detection.sh`로 위임하는데, 해당 파일의 내용이 artifacts에 포함되지 않아 사용자가 무슨 일이 일어나는지 추적하기 어려움
  - README의 "Option B: Python directly"와 "Headless Mode" 섹션이 완전히 동일한 명령을 반복하며, 상대 경로(`../../venv-dx_stream/`, `../../dx_stream/samples/`) 사용 시 session 디렉터리에서 실행해야 한다는 안내가 없어 혼란을 줌

- **One-sentence verdict**: 핵심 의존 스크립트(`run_yolo26n_realtime_detection.sh`)가 검증되지 않았고 실제 파이프라인 실행 증거가 없으므로, 환경이 이미 갖춰진 사용자는 실행 가능하나 처음 접하는 사용자는 시행착오가 필요할 것으로 예상됨.


---

---

---

### R11 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `setup.sh`의 모델 다운로드 경로가 `$DX_STREAM_ROOT/dx_stream/samples/models/`로 하드코딩되어 있으나, README의 Prerequisites는 `../../`를 기준으로 `./setup.sh --model=` 실행을 안내해 경로 불일치 가능성이 있음
  - `run.sh`가 내부적으로 `run_cascaded.sh`를 호출하지만, README의 파일 목록에는 해당 파일이 존재 표시되어 있음에도 첨부 artifact에는 포함되지 않아 end-user가 실행 시 `run_cascaded.sh not found` 오류를 겪을 수 있음
  - `session.log`에 실제 파이프라인 실행(e2e) 결과가 없고 TDD 구문 검사 수준에만 머물러 있어, 사용자가 정상 동작 여부를 확인할 증거가 부재함
- **One-sentence verdict**: 스크립트 구조와 README 옵션 설명은 충분하나, `run_cascaded.sh` artifact 누락 및 실제 실행 검증 증거 부재로 첫 실행 시 사용자가 오류를 마주칠 가능성이 높음.


---

---

---

### R11 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **Prerequisites 경로 오류**: README의 Prerequisites 섹션이 `cd dx_app`를 지시하지만, 레포 루트 기준으로는 `cd dx-runtime/dx_app`이어야 함. 처음 접하는 사용자는 잘못된 디렉토리에서 빌드를 시도하게 됨.
  - **venv 비지속 문제**: `bash setup.sh` 단독 실행 시 venv activation이 호출 셸에 전파되지 않음. `bash run.sh` 내부에서 `source setup.sh`를 호출하므로 `run.sh`를 통해 실행하면 정상 동작하지만, README의 "Direct Variant Runs" 섹션(예: `python yolo26n_sync.py ...`)을 실행하기 전에 venv를 직접 activate해야 한다는 안내가 없음.
  - **CWD 가정 미명시**: `run.sh`의 기본 경로(`../../assets/models/`)는 세션 디렉토리에서 실행할 때만 유효하지만, README에 "세션 디렉토리로 이동 후 실행" 안내가 명시적으로 없어 다른 위치에서 실행 시 `[ERROR] Model not found` 발생 가능.

- **One-sentence verdict**: `bash run.sh` 경로를 따르면 동작하지만, Prerequisites 경로 오류와 Direct Variant Runs 실행 전 venv 활성화 안내 누락으로 초심 사용자가 막힐 가능성이 있어 PARTIAL 판정.


---

---

---

### R11 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **핵심 아티팩트 생성 여부 불명확**: `session.log`에서 1차 컴파일이 `DataLoaderError`(config NHWC `(1,640,640,3)` vs 모델 NCHW `(1,3,640,640)` 불일치)로 실패한 것이 명시적으로 기록되어 있다. 이후 Python API 2차 시도 로그는 `[truncated]`로 잘려 있어, `yolo26n.dxnn`(6.7M)이 실제로 생성되었는지 검증되지 않는다.
  - **session.log 앞부분이 hand-written 형식**: `"Copied ONNX model"`, `"Symlinked 100 calibration images"` 등 첫 몇 줄은 실제 터미널 출력이 아닌 요약 문구이며, 이는 `cat << 'EOF'` 방식 금지 규칙(session.log must be real output)에 해당하는 위반 패턴이다.
  - **README의 "Verification: PASS" 표기 오류**: NPU 하드웨어가 없는 환경임을 인정하면서도 PASS를 주장한다. 규칙상 sanity check FAIL + NPU 없는 환경의 compiler-only 태스크에서 verify.py 결과는 PASS가 아닌 **SKIPPED**로 표기해야 한다. 사용자가 이 결과를 신뢰하면 실제 NPU 환경에서의 재검증을 생략할 수 있다.

- **One-sentence verdict**: setup.sh·run.sh 구조는 양호하나, 1차 컴파일 실패 후 복구 성공 여부가 로그에서 확인되지 않아 핵심 파일(`yolo26n.dxnn`) 존재가 불명확하고, session.log 위조 패턴 및 잘못된 PASS 판정으로 사용자 신뢰도가 저하된다.


---

---

---

### R11 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README의 직접 `python yolo26n_sync.py ...` 명령어에 venv 활성화 단계가 없음 — `bash run.sh`를 먼저 실행하지 않으면 `ImportError: No module named 'dx_engine'` 발생 가능
  - README의 첫 번째 sync 예제에 `--no-display` 플래그 누락 — headless/SSH 환경에서 display 에러로 실패할 수 있음 (run.sh는 정상 처리)
  - `dx_engine` 사전 빌드 필요성(prerequisite)을 README에 명시하지 않음 — 신규 사용자는 `setup.sh`의 FATAL 에러를 보기 전까지 `./install.sh && ./build.sh` 실행이 필요하다는 사실을 알 수 없음

- **One-sentence verdict**: `bash run.sh` 단일 경로는 정상 동작하지만, README의 직접 python 명령어는 venv 미활성화 및 headless 환경 미고려로 신규 사용자가 오류를 겪을 가능성이 높다.


---

---

---

### R11 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh`이 `run_yolo26n_detection.sh`을 호출하지만, 해당 파일의 내용이 아티팩트에 포함되어 있지 않아 `bash run.sh` 실행 시 즉시 실패할 가능성이 있음
  - `setup.sh`의 venv 탐색 로직이 `cd "$SCRIPT_DIR/../.."` 기반의 하드코딩된 상대 경로에 의존하며, 세션 디렉토리 깊이(`dx_stream/dx-agentic-dev/<session>/`)를 정확히 가정해야만 동작함 — SUITE_ROOT 패턴 미적용
  - 독립적인 verification 단계(예: `verify.py` 또는 headless 실행 후 결과 확인)가 README에 명시되어 있지 않아, 사용자가 성공 여부를 판단하기 어려움

- **One-sentence verdict**: `run_yolo26n_detection.sh` 파일 누락과 상대경로 취약성으로 인해 일반 사용자가 `bash run.sh` 한 줄로 실행에 성공하기 어렵지만, session.log에 실제 파이프라인 실행 증거가 있고 README 설명은 비교적 충실하여 숙련된 사용자는 수동 조정으로 실행 가능한 수준임.


---

---

---

### R11 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `run_cascaded.sh`로 단순 위임하는 thin wrapper임에도 불구하고, README Quick Start에 두 파일이 별도로 언급되어 역할 구분이 다소 혼란스러움 (어떤 파일이 진짜 entry point인지 불명확)
  - `setup.sh`에서 모델 파일 누락 시 `[WARN]`만 출력하고 통과함 — 실제 자동 다운로드 로직은 `run_cascaded.sh` 내부에 있어, `setup.sh`만 실행한 사용자는 모델 준비 상태를 정확히 알 수 없음
  - `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"`가 세션 디렉터리가 정확히 2단계 깊이에 있다는 전제에 의존 — 세션 경로가 달라지면 경로 해석 실패 가능 (SUITE_ROOT 패턴 미사용)

- **One-sentence verdict**: 파이프라인 아키텍처 다이어그램과 CLI 레퍼런스가 충실하고 session.log에 실제 실행 증거가 있어 DEEPX SDK 개발자라면 README만으로 환경 구성부터 실행까지 큰 어려움 없이 따라갈 수 있으나, 모델 자동 다운로드 흐름과 `run.sh`/`run_cascaded.sh` 간 역할 분리가 명시적으로 설명되지 않아 초기 실행 시 미세한 혼란이 발생할 수 있다.


---

---

---

### R11 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **venv 활성화 누락**: `setup.sh` 실행 후 venv를 activate하는 명령이 README의 Run 섹션에 빠져 있음. `setup.sh`는 activate 방법을 마지막에 출력하지만, README는 그 다음 바로 `python yolo26n_sync.py ...`를 실행하라고 안내 → venv 비활성 상태에서 실행 시 `dx_engine` import 실패 가능. `run.sh` 내부에도 venv activate 구문 없음.
  - **session.log 없음 (file not found)**: 실제 실행 증거가 전혀 없음. 에이전트가 아티팩트를 실제로 실행했는지 불명확하며, 사용자가 "성공 시 어떤 출력이 나오는지" 알 방법이 없음.
  - **예상 출력/검증 기준 미제공**: README에 "성공하면 bounding box N개 감지" 같은 기대 출력이 없어 사용자가 정상 동작 여부를 판단하기 어려움.

- **One-sentence verdict**: venv 활성화 단계 누락과 session.log 부재로 인해 DEEPX SDK에 친숙한 개발자라면 추론으로 실행 가능하지만, 이 세션에 처음 접하는 사용자는 첫 `python` 실행 시 환경 오류에 막힐 가능성이 높다.


---

---

---

### R11 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (부분적)

- **Key issues**:
  - **SUITE_ROOT 하드코딩 취약성**: `setup.sh`와 `run.sh` 모두 `SUITE_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"`를 사용 — HARD GATE에서 요구하는 walk-up 자동 탐지 패턴이 아니라 깊이 고정 방식. 실행 경로가 예상과 다르거나 심볼릭 링크를 포함할 경우 경로 오류 발생 가능.
  - **DXNN 검증 미완료**: `session.log`가 초기 컴파일 오류(`DataPreprocessingError: Preprocessing transform 'Resize' not found`)를 노출한 뒤 재시도 결과가 잘림(truncated). README에는 `.dxnn` 파일(6.74 MB) 존재가 언급되지만 session.log에서 성공을 직접 확인 불가. DXNN inference는 "SKIPPED"로 기록되어 실제 NPU 검증 증거 없음.
  - **`verify.py` 인터페이스 불명확**: `run.sh`가 `--onnx`, `--dxnn`, `--image` 인자로 `verify.py`를 호출하지만 해당 스크립트 내용이 포함되지 않아, 인자 호환성 및 실제 동작을 end-user가 사전 확인할 방법 없음.

- **One-sentence verdict**: ONNX 컴파일 결과물과 README 구성은 양호하지만, SUITE_ROOT 하드코딩 취약점·session.log 잘림에 의한 컴파일 성공 미검증·DXNN 검증 전면 스킵으로 인해 NPU 환경에서의 완전한 재현 가능성은 불확실하다.


---

---

---

### R11 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README에 `cd <session_dir>` 선행 지시 없음 — Quick Start 커맨드가 `../../assets/models/...` 상대 경로를 사용하는데, 사용자가 세션 디렉터리 안에서 실행해야 함을 명시하지 않음
  - `run.sh`의 venv 미발견 시 silent failure — `venv-dx-runtime`도 `.venv`도 없는 경우 오류/종료 없이 venv 미활성 상태로 계속 진행함
  - `session.log`가 `sync` variant 1개만 검증 — `async`, `sync_cpp`, `async_cpp` 3개 variant 실행 증거 없음
- **One-sentence verdict**: `setup.sh`/`run.sh` 구조와 4 variant 정의는 잘 갖춰져 있으나, README의 `cd` 안내 누락·run.sh의 venv silent failure·session.log의 단일 variant 증거만으로 인해 비숙련 사용자는 일부 환경에서 난관에 봉착할 수 있다.


---

---

---

### R11 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh`에서 `$MODEL` 경로를 검증하고 출력하지만 실제로 `run_detection.sh`에 전달하지 않음 (`bash "$SCRIPT_DIR/run_detection.sh" "$VIDEO"` — MODEL 인수 누락). 사용자가 `bash run.sh /custom/model.dxnn`으로 실행해도 `run_detection.sh` 내부의 하드코딩된 경로가 사용됨
  - `run_detection.sh`가 제공된 artifacts에 포함되지 않았고, README의 파일 목록에만 언급됨. 이 파일이 없으면 `run.sh` 실행 시 즉시 실패함
  - README의 모든 경로가 `../../`(상대 경로) 기준으로 작성되어 있고, "현재 위치 = session 디렉토리"라는 설명이 없어 처음 접하는 사용자가 혼란을 겪을 수 있음. `SUITE_ROOT` 자동 탐색 패턴 미적용

- **One-sentence verdict**: `run_detection.sh` 누락 및 `run.sh`의 model 경로 미전달 버그로 인해 README를 그대로 따라도 실제 실행이 실패할 가능성이 높음.


---

---

---

### R11 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README의 파이프라인 다이어그램이 외부 코드 블록(` ``` `) 안에 내부 ` ``` `를 중첩 사용해 마크다운 렌더러에서 다이어그램이 깨져 보임
  - `run.sh`는 `$VIDEO`만 `run_cascaded.sh`에 전달하며, secondary model 경로(`EfficientNet_Lite0.dxnn`)를 전달하지 않아 `run_cascaded.sh` 내부에서 하드코딩된 경로에 의존하게 됨 — 사용자가 커스텀 모델 경로를 지정할 방법이 없음
  - README Option C의 `../../` 상대 경로 예시가 "세션 디렉터리 기준"이라는 명시 없이 서술되어 있어, 다른 위치에서 실행하면 경로 오류 발생 가능
- **One-sentence verdict**: `setup.sh`와 `session.log`는 충실하게 작성되었으나, README의 다이어그램 렌더링 버그와 `run.sh`의 secondary model 경로 누락으로 인해 사용자가 기본 실행 이상(커스텀 모델, 경로 변경)을 시도할 경우 막힐 가능성이 있는 PARTIAL 수준의 아티팩트이다.


---

---

---

### R11 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **모델 파일 전제조건 누락**: README가 `yolo26n.dxnn`이 `../../assets/models/` 위치에 이미 존재한다고 가정하지만, 해당 파일을 어떻게 준비하는지 언급이 없음. 파일이 없으면 `run.sh`가 `[ERROR] Model not found` 로 즉시 종료됨
  - **시작 디렉토리 모호성**: Prerequisites의 `cd dx_app`과 Setup의 `cd dx_app/dx-agentic-dev/...` 모두 출발 디렉토리(dx-runtime root 가정)를 명시하지 않아 처음 접하는 사용자가 혼동할 수 있음
  - **run.sh의 묵시적 실패(silent failure)**: `source setup.sh 2>/dev/null || true` 패턴으로 인해 setup 실패 시 오류가 모두 억제되고 진행되다가, 나중에 `dx_engine` import 오류 등으로 덜 명확한 에러가 발생할 수 있음

- **One-sentence verdict**: sanity check·import chain·syntax 검증은 모두 통과되어 실행 준비는 갖춰졌으나, `yolo26n.dxnn` 모델 파일 준비 방법 미기재 및 run.sh의 silent-setup 패턴으로 인해 처음 접하는 사용자는 반드시 막히는 지점이 생긴다.


---

---

---

### R11 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **[치명적] setup.sh가 특정 이전 세션의 donor venv 경로를 하드코딩** (`20260513-225021_opencode_sonnet46_yolo26n_compile/venv/...`)하여 dx_engine을 복사함. 해당 세션 디렉터리가 없는 환경에서는 `exit 1`로 즉시 실패하며, 범용 설치 경로나 fallback이 전혀 없음
  - **run.sh가 랜덤 텐서로만 스모크 테스트** — 실제 이미지 추론은 수행하지 않아, 모델 출력의 의미 있는 검증이 부재함 (`sample_dog.jpg` 경로는 정의만 하고 사용하지 않음)
  - **verify.py가 README에 언급되어 있으나 artifacts에 포함되지 않음** — 제공된 내용만으로는 ONNX vs DXNN 수치 비교 검증 단계의 완전성을 확인 불가

- **One-sentence verdict**: README와 run.sh는 충분히 잘 작성되었으나, setup.sh가 특정 이전 세션 venv에 하드코딩 의존하는 구조적 결함으로 인해 해당 donor 경로가 존재하지 않는 환경에서는 설치 단계부터 실패하므로 일반 사용자가 독립적으로 실행하기 어렵다.


---

---

---

### R11 cursor-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - README의 Quick Start 첫 줄 `cd "$(dirname "$0")"` 은 bash 스크립트 내부에서만 동작하는 구문으로, 사용자가 터미널에 직접 입력하면 동작하지 않음 (실제 세션 디렉토리 경로가 필요)
  - 기본 모델 경로가 `../../assets/models/yolo26n.dxnn` ("relative to `dx_app`")로 설명되어 있으나, 세션 디렉토리 기준 상대경로임을 명확히 하지 않아 처음 사용자는 혼란스러울 수 있음
  - 실행 후 성공 여부를 확인하는 방법(예: 출력 이미지 경로, 검출 결과 형식)이 README에 전혀 기술되어 있지 않아 사용자가 정상 실행 여부를 판단하기 어려움

- **One-sentence verdict**: setup.sh/run.sh 품질과 세션 로그 증거는 양호하나, README Quick Start의 bash 전용 구문 오류와 실행 결과 검증 안내 누락으로 처음 사용하는 개발자가 독립적으로 실행·확인하기에는 불충분하다.


---

---

---

### R11 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (smoke test only)

- **Key issues**:
  - **`run.sh`의 빈 인자 전달 버그**: `OUTPUT`이 비어 있을 때 `exec bash ... "$INPUT" "$OUTPUT"`가 두 번째 인자로 빈 문자열(`""`)을 전달함 — wrapper 스크립트가 `$2`를 검사할 경우 오동작 가능
  - **경로 이중 중첩 의심**: `session.log`에 `dx_stream/dx_stream/samples/models/` 경로가 출력됨 — `SRC_DIR="$DX_STREAM_ROOT/dx_stream"` 패턴이 실제 디렉터리 구조와 맞지 않을 경우 다른 환경에서 재현 실패 가능
  - **smoke exit: 124 설명 부재**: README 및 session.log 어디에도 "exit 124 = 12초 타임아웃 정상 종료 = PASS"라는 설명 없음 — 처음 보는 사용자가 파이프라인 실패로 오해할 수 있음

- **One-sentence verdict**: 셋업 및 smoke 테스트는 실제로 통과했으나 `run.sh`의 빈 인자 버그와 경로 이중 중첩 위험이 다른 환경에서의 재현 신뢰도를 낮추므로 PARTIAL 판정.


---

---

---

### R11 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **모델 경로 불일치**: `setup.sh`는 모델을 `dx_stream/samples/models/`에 다운로드하지만, `session.log`의 실제 파이프라인 실행에서는 `/workspace/res/models/models-2_3_0/yolo26n.dxnn` 같은 완전히 다른 절대 경로를 사용함 — 새 사용자 환경에서는 `pipeline.py`가 잘못된 경로를 참조하여 실행 실패 가능성이 높음
  - **`run_cascaded.sh` 미검토**: `run.sh`와 README 모두 `run_cascaded.sh`에 위임하지만, 해당 파일의 내용이 아티팩트에 포함되지 않아 경로 해석 방식과 실제 동작을 확인할 수 없음
  - **`run.sh`에서 `setup.sh`를 `source`로 호출**: `setup.sh`에 `set -e`가 있는 상태에서 `source`로 불러오면 부모 셸의 오류 처리에 영향을 줄 수 있으며, 이후 `exec bash run_cascaded.sh`로 넘어가는 흐름이 예상대로 동작하지 않을 수 있음

- **One-sentence verdict**: README 구조와 실행 증거(session.log)는 양호하나, 에이전트 실행 환경의 하드코딩된 모델 경로가 setup.sh의 다운로드 경로와 불일치하여 새 사용자가 그대로 따라 실행하면 파이프라인이 실패할 가능성이 높다.


---

---

---

### R11 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 2
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README Quick Start의 `cd "$(dirname "$0")"` 는 bash 표현식이라 그대로 복사·실행하면 동작하지 않으며, `run.sh` 자체가 Quick Start에서 완전히 누락되어 있음
  - `setup.sh`는 `.deepx/tests/venv` 또는 `venv-dx-compiler-local` 중 하나가 이미 존재한다고 가정하고 진입하는데, README에 이 사전 조건(venv 생성 방법)이 전혀 기재되어 있지 않아 신규 사용자는 `ERROR: Need ... venv`에서 즉시 막힘
  - `session.log`가 컴파일 86% 시점에 잘려 있어 `yolo26n.dxnn` 생성 완료 및 `verify.py` 결과를 확인할 수 없음; `run.sh`는 `TESTS_VENV`만 시도하고 `setup.sh`의 컴파일러 venv 폴백이 없어 환경에 따라 실패 가능

- **One-sentence verdict**: venv 사전 조건과 README 진입점 오류, 컴파일 완료 미확인으로 인해 신규 사용자가 안내만으로 end-to-end 실행을 완료하기 어렵다.


---

---

---

### R11 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 별도 inference 스크립트 없이 `verify.py --image ... --dxnn ...`를 재실행하는데, README Quick Start 4단계는 "Run inference on sample image"로 표기 — 실제 동작과 설명 불일치. 또한 Step 3의 `python verify.py`(인수 없음)와 run.sh 내부의 명시적 `--image`/`--dxnn` 인수 간 사용법 불일치가 혼란을 유발할 수 있음
  - `setup.sh` Step 2에서 compiler venv를 activate한 후 Step 3에서 새로운 로컬 venv를 재생성·activate하는데, 이 새 venv에 `dx_com`이 설치되지 않음 (verify.py가 dx_engine만 사용한다면 무관하나, dx_com을 호출할 경우 ImportError 가능)
  - README "Verification Result" 섹션이 실제 `RESULT: PASS` 결과를 인라인에 표시하지 않고 "Run verify.py to see PASS/FAIL"로만 안내 — session.log에는 PASS 증거가 있으나 README에 반영 안 됨

- **One-sentence verdict**: 전체적으로 구조가 잘 갖춰진 compiler 세션으로 일반 사용자도 Quick Start를 따라 실행 가능하나, `run.sh`의 역할 설명 오류와 verify.py 호출 방식 불일치가 혼란을 줄 수 있어 소폭 개선이 필요함.


---

---

---

### R11 claude-code dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README Quick Start의 `--model /path/to/yolo26n.dxnn`가 placeholder로 남아 있어, `.dxnn` 파일을 어디서 구해야 하는지 안내가 없음. `run.sh`의 자동 탐색 기능과 일관성도 없음
  - README에 **사전 조건**(dx_engine 설치, `dx_app ./install.sh && ./build.sh` 완료 필요)이 명시되지 않아, `setup.sh` 첫 단계에서 `ERROR: dx_engine not available`로 실패할 수 있음
  - Quick Start Step 2~4는 system Python을 사용하지만, `setup.sh`가 venv를 생성하는 이유와 venv 활성화 여부가 불명확하여 Python 환경 혼란 유발 가능
- **One-sentence verdict**: session.log에 실제 실행 증거가 있고 스크립트 품질은 양호하나, README에 dx_engine 사전 조건과 모델 파일 취득 방법이 누락되어 있어 처음 접하는 사용자가 첫 단계에서 막힐 가능성이 있음.


---

---

---

### R11 claude-code dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`run.sh`가 모델 경로를 `run_detection.sh`에 전달하지 않음**: `run.sh`에서 `$MODEL` 변수를 결정한 뒤 `bash run_detection.sh "$VIDEO"`만 호출 — `$MODEL`이 누락되어 `run_detection.sh`가 자체 경로 탐색 로직을 갖지 않으면 실패할 수 있음
  - **SUITE_ROOT 미사용으로 상대경로 취약**: `setup.sh`와 `run.sh` 모두 `../..` 하드코딩 사용 (SUITE_ROOT 자동 감지 패턴 미적용). `dx_stream/dx-agentic-dev/<session>/` 이외의 환경에서 실행 시 경로 오류 발생 가능
  - **README의 상대경로(`../../`)가 현재 작업 디렉토리 가정을 공유하지 않음**: 사용자가 session 디렉토리에 `cd` 한 상태인지 `dx_stream` root인지에 따라 동일한 `../../` 경로의 의미가 달라져 혼란 유발

- **One-sentence verdict**: `session.log`에서 실제 실행 성공(exit: 0)이 확인되어 에이전트 환경에서는 동작하지만, `run.sh`의 모델 경로 미전달 버그와 SUITE_ROOT 미사용 하드코딩 상대경로로 인해 새로운 사용자 환경에서 재현 성공을 보장하기 어렵다.


---

---

---

### R11 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - `run.sh`가 `$1`(커스텀 primary model 경로)을 받지만 `run_cascaded.sh`에 전달하지 않아 사용자 지정 모델 경로가 무시됨
  - `run.sh`에서 `source setup.sh 2>/dev/null || true`로 setup 오류를 무음 처리 — 환경 문제 발생 시 사용자가 원인 파악 불가
  - README Option B/C의 venv 활성화 경로(`../../venv-dx_stream/bin/activate`)가 세션 디렉터리 기준 상대경로임을 명시하지 않아 다른 CWD에서 실행 시 실패 가능
- **One-sentence verdict**: `bash run.sh` 기본 실행 경로는 session.log의 실제 파이프라인 출력으로 검증되어 있으나, 커스텀 모델 인자 전달 버그와 setup 오류 무음 처리로 인해 고급 사용 시나리오에서 사용자가 막힐 수 있다.


---

---

---

### R11 claude-code runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **README에 `setup.sh` 실행 단계 누락**: README의 "How to Run" 섹션이 곧바로 `run.sh` / `python yolo26n_sync.py`로 진입하며, `bash setup.sh`를 먼저 실행해야 한다는 안내가 전혀 없음. 처음 보는 사용자는 venv 생성 단계를 건너뛸 가능성이 높음.
  - **`run.sh`이 venv를 활성화하지 않음**: `setup.sh`는 `$SCRIPT_DIR/venv`를 생성하지만, `run.sh`은 해당 venv를 `source .../venv/bin/activate` 없이 시스템 `python`으로 실행함. `setup.sh`로 만든 venv가 실제 런타임에서 사용되지 않는 구조적 불일치 존재.
  - **venv에 패키지 미설치 + 실제 추론 검증 없음**: `setup.sh`는 빈 venv만 생성하고 `dx_engine`, `common` 등 필수 패키지를 venv 내에 설치/링크하지 않음. `session.log`도 `--help` 출력(import 체인 확인)까지만 기록되어 있고, 실제 이미지 추론 실행 결과(`detection output`, `FPS`, `bbox` 등)가 없어 end-to-end 동작 여부를 확인할 수 없음.

- **One-sentence verdict**: README에 setup 단계가 빠져 있고, `run.sh`이 venv를 사용하지 않으며, 실제 추론 실행 증거가 없어 처음 사용하는 개발자가 그대로 따라 실행하기에는 불완전함.


---

---

---

### R12 copilot-cli compiler

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 1
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `README.md` 파일이 존재하지 않음 — 사용자가 따를 진입점 문서가 전무하며, 세션 목적·파일 목록·quick-start 단계를 전혀 알 수 없음
  - `session.log`가 중간에 잘려 있어 컴파일 최종 성공 여부(yolo26n.dxnn 생성)를 확인할 수 없음; CLI 단계에서 NHWC/NCHW 불일치 에러가 발생한 뒤 Python API로 전환했으나 결과가 기록되지 않음
  - `run.sh`가 `python verify.py`만 호출하여 실제 추론 실행이 아닌 검증만 수행하는데, `verify.py` 파일 자체가 artifact 목록에 없고 `yolo26n.dxnn`의 존재 여부도 불확실하여 실행 시 즉시 실패할 가능성이 높음

- **One-sentence verdict**: README.md 부재와 컴파일 성공 확인 불가로 인해 일반 사용자가 이 세션을 독립적으로 설치·실행·검증하는 것은 현재 상태에서 불가능하다.


---

---

---

### R12 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README의 실행 예시가 `/path/to/yolo26n.dxnn` 플레이스홀더를 사용하고 있어, 실제 모델 경로(`assets/models/yolo26n.dxnn`)를 run.sh와 README가 불일치하게 안내함
  - `setup.sh`의 모델 자동 다운로드(`python -m dx_app.tools.download_model`)가 실패할 경우 경고(WARNING)만 출력하고 계속 진행 — 모델 파일 없이 실행 시 런타임 오류 발생
  - venv 생성 없이 시스템 Python을 직접 사용 — Ubuntu 24.04+ (PEP 668) 환경에서 pip 설치 단계가 막힐 가능성 있음
- **One-sentence verdict**: 네 가지 추론 variant 모두 `--help` 및 실제 추론(smoke test)까지 통과한 고품질 아티팩트이나, 모델 파일 획득 경로가 README와 run.sh 간에 불일치하고 모델 미존재 시 setup.sh가 자동 처리에 실패해도 조용히 넘어가는 점이 첫 실행 사용자의 성공을 가로막을 수 있다.


---

---

---

### R12 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh`이 `run_detection.sh`을 호출하지만 해당 파일이 README의 Files 표에는 있어도 artifacts 목록에는 없음 — 실제로 존재하는지 확인 불가, 없으면 `run.sh` 실행 즉시 실패
  - `setup.sh`의 모델 다운로드 경로(`$DX_STREAM_ROOT/../setup.sh --model=...`)가 suite-root 기준이고, session 디렉터리 깊이에 따라 `DX_STREAM_ROOT`가 `dx-runtime/dx_stream`이 아닌 엉뚱한 경로를 가리킬 수 있음 (`../../` 하드코딩 문제, SUITE_ROOT 패턴 미준수)
  - session.log에 `pipeline.py`가 성공 실행된 증거는 있으나, `setup.sh` / `run.sh` 자체의 실행 로그가 없어 환경 설정 단계의 검증이 누락됨 (verify 단계 미완)

- **One-sentence verdict**: `pipeline.py` 직접 실행 시나리오는 동작 증거가 있으나, `run.sh` → `run_detection.sh` 경로와 하드코딩된 상대 경로 문제로 end-user의 one-command 실행은 환경에 따라 실패할 가능성이 높다.


---

---

---

### R12 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **`SRC_DIR` 경로 버그**: `setup.sh`에서 `SRC_DIR="$DX_STREAM_ROOT/dx_stream"`으로 설정하는데, `DX_STREAM_ROOT`가 이미 `dx-runtime/dx_stream/`을 가리키므로 `dx-runtime/dx_stream/dx_stream/`이 되어 존재하지 않는 경로가 됨 → 모델 다운로드 경로(`$MODEL_DIR`)와 tracker config 경로가 모두 틀림
  - **`run_cascaded.sh` 미검증**: `run.sh`가 `run_cascaded.sh`에 위임하고 README의 파일 목록에도 포함되어 있으나, 해당 파일의 내용이 artifacts에 없어 실제 파이프라인 실행 로직을 확인 불가
  - **실행 증거 부재**: `session.log`가 `py_compile`과 `--help` 출력만 포함하고 있어 GStreamer 파이프라인이 실제로 구동되었다는 증거가 없음 (기능 검증 미수행)

- **One-sentence verdict**: README 구조와 CLI 설명은 명확하지만 `setup.sh`의 경로 버그로 모델 다운로드가 실패하고 실제 파이프라인 실행 검증이 생략되어, 사용자가 즉시 실행하기에는 수동 수정이 필요한 불완전한 상태이다.


---

---

---

### R12 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`session.log` 없음 (필수 누락)**: 실행 증거가 전혀 없어 에이전트가 실제로 코드를 실행했는지 확인 불가. `session.log` 는 mandatory deliverable임에도 `(file not found)` 상태
  - **README의 `--model` 인자가 허위**: `Prerequisites` 블록에서 `bash setup.sh --model=yolo26n.dxnn` 를 안내하지만, `setup.sh` 는 CLI 인자를 전혀 파싱하지 않음 — 인자는 무시되며 모델 다운로드는 dx_app 루트 탐색 결과에만 의존
  - **루트 탐색 로직 취약**: `setup.sh` / `run.sh` 모두 `setup.sh + src/` 존재 여부로 dx_app 루트를 추정하는데, 5단계 상위 디렉토리 안에서 해당 조건을 만족하는 다른 프로젝트가 있으면 오탐 가능. 탐색 실패 시 모델 다운로드/venv 활성화 없이 silently skip됨

- **One-sentence verdict**: README 구조와 run.sh 는 상당히 잘 작성되었으나, `session.log` 누락으로 실행 증거가 없고 `--model` 인자 허위 안내 및 취약한 경로 탐색으로 인해 낯선 사용자가 설치를 완료하기까지 혼선이 예상된다.


---

---

---

### R12 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `infer_smoke.py`를 직접 호출하지만, README 파일 목록에 해당 파일이 누락되어 있음 — 파일이 세션 디렉토리에 실제로 존재하는지 확인 불가, 없을 경우 `run.sh`는 즉시 실패
  - `setup.sh`의 `dx_engine` 연결 방식이 `.deepx/tests/venv` 하위의 비표준 경로에 의존 — 해당 경로가 없으면 `verify.py`가 `ImportError`로 실패한다는 경고만 출력하고 setup은 성공으로 종료되어 사용자가 문제를 뒤늦게 발견함
  - `setup.sh` 내부에서 `sanity_check.sh`가 실행되는데, NPU 초기화 실패 시 `set -e`에 의해 환경 구성 전체가 중단될 수 있음 (비컴파일러 경로에서 hard-stop 의도된 동작이지만, 컴파일러 전용 세션에서 불필요한 차단 요인이 됨)

- **One-sentence verdict**: `verify.py`와 컴파일 로그(session.log)는 충실하게 제공되었으나, `run.sh`가 문서화되지 않은 `infer_smoke.py`에 의존하고 dx_engine 연결이 취약하여 일반 사용자가 최종 실행 단계에서 막힐 가능성이 높다.


---

---

---

### R12 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - README의 Quick start 코드 블록 첫 줄(`cd "$(dirname "$0")"`)은 셸 스크립트 내부 문법이며, 터미널에서 직접 실행하면 동작하지 않음 — 세션 디렉토리로 이동하는 방법(예: `cd /path/to/session_dir`)으로 교체하는 것이 더 명확함
  - `verify.py` 내용이 README에 `py_compile` + `--help` smoke check라고 설명되어 있으나, ONNX vs DXNN 수치 비교 없이 신택스 확인 수준에 그침 — 실제 추론 검증(numerical verify)은 포함되지 않음
  - `yolo26n.dxnn` 모델 파일이 `$DX_APP_ROOT/assets/models/`에 존재해야 하지만 README에 모델 파일 준비 방법(다운로드 또는 컴파일 명령)이 명시되어 있지 않음

- **One-sentence verdict**: setup.sh의 자동 경로 탐색과 `dx_engine` pth 브릿지 로직이 견고하고 session.log에서 실제 실행 성공이 확인되므로 전반적으로 실행 가능하나, Quick start 첫 줄 문법 오류와 모델 파일 준비 지침 누락으로 신규 사용자가 즉시 막힐 수 있다.


---

---

---

### R12 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **이중 경로 버그**: `setup.sh`와 `run.sh`의 `DX_STREAM_ROOT`가 세션 디렉터리(`dx-runtime/dx_stream/dx-agentic-dev/<session>/`)에서 `../..`으로 계산되어 `dx-runtime/dx_stream/`을 가리키고, 여기에 다시 `dx_stream/`을 붙여 `…/dx_stream/dx_stream/samples/…`라는 이중 경로가 발생함. `session.log`의 model ready 로그에서도 이 문제가 드러남 (`dx-runtime/dx_stream/dx_stream/samples/…`).
  - **모델 경로 불일치**: `setup.sh`가 체크하는 모델 경로(`dx_stream/dx_stream/samples/models/yolo26n.dxnn`)와 실제 파이프라인 실행 시 사용된 경로(`/workspace/res/models/models-2_3_0/yolo26n.dxnn`), 그리고 README에 기재된 경로(`../../dx_stream/samples/models/yolo26n.dxnn`)가 모두 달라서 새 사용자가 혼란을 겪을 수 있음.
  - **핵심 실행 스크립트 미제공**: 실제 파이프라인을 구동하는 `run_yolo26n_detection.sh`가 artifact 목록에 있으나 내용이 제공되지 않아, 경로 처리 로직의 완전한 검증이 불가능하고 사용자가 해당 스크립트 없이 `run.sh`만 실행하면 즉시 실패함.

- **One-sentence verdict**: 개발자 머신에서는 파이프라인이 실제로 동작했음이 `session.log`로 확인되지만, `DX_STREAM_ROOT` 이중 경로 버그와 모델 경로 불일치로 인해 다른 환경의 사용자가 그대로 따라 실행하면 setup 단계에서 경고 또는 오류가 발생할 가능성이 높다.


---

---

---

### R12 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **모델 경로 불일치**: `session.log`에 기록된 실제 pipeline 실행 시 모델 경로가 `/data/home/dhyang/.../workspace/res/models/models-2_3_0/yolo26n.dxnn` (절대 경로, 에이전트 로컬 전용)으로 하드코딩됨. 반면 `setup.sh`는 `dx_stream/samples/models/`를 확인/다운로드 대상으로 사용 — 두 경로가 불일치하여 타 머신에서는 모델을 찾지 못할 가능성이 높음.
  - **`run_cascaded.sh` 내용 미제공**: `run.sh`가 `run_cascaded.sh`를 호출하고 README도 핵심 파일로 명시하나, 아티팩트에 내용이 없어 경로 해결 방식 검증 불가. 유저가 직접 열어 확인해야 함.
  - **README의 실행 방법 이중화**: "How to Run" 섹션에 `bash run.sh` + `bash run_cascaded.sh` 방식과 `python3 pipeline.py` 직접 실행 방식이 병기되어 있으나, 둘의 차이·우선순위가 불분명하여 혼란 야기.

- **One-sentence verdict**: 에이전트 환경에서는 정상 실행이 확인됐으나, 하드코딩된 모델 절대 경로와 `setup.sh`의 모델 탐색 경로 불일치로 인해 다른 머신에서는 추가 수동 수정 없이 재현 실패 가능성이 높다.


---

---

---

### R12 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README 커맨드 블록에 `source /path/to/dx-compiler/venv-dx-compiler-local/bin/activate` 플레이스홀더가 그대로 남아 있어, 실제 경로를 사용자가 직접 파악해야 함 (`setup.sh`는 자동 탐지하지만 README는 수동 경로 기재)
  - `run.sh`는 `compile.py`만 실행하며 `verify.py` 단계가 빠져 있음 — "원커맨드 실행기"로서 불완전하고, README 내 파일 목록에도 `run.sh`가 누락되어 있어 사용자가 어떤 스크립트를 먼저 써야 하는지 혼란 발생
  - `session.log`가 중간 truncation되어 컴파일 완료 및 `verify.py`의 `RESULT: PASS` 출력이 확인되지 않음 — 실제 성공 여부를 end-user가 증거로 확인할 수 없음

- **One-sentence verdict**: `setup.sh`의 완성도와 sanity check 통과는 긍정적이나, README의 하드코딩 플레이스홀더·`run.sh`의 verify 단계 누락·로그 truncation으로 인해 사용자가 반드시 README를 꼼꼼히 읽고 수동으로 보완해야 하는 **PARTIAL** 수준의 실행 가능성이다.


---

---

---

### R12 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 2
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`이 실제로는 `python verify.py "$@"`만 실행함 — README의 "Quick Start: `bash run.sh`"가 마치 컴파일을 수행하는 것처럼 오해를 유발하지만, 실제 컴파일(`export_yolo26n.py` + `dxcom` 호출)은 어디에도 없음. 신규 사용자가 `bash run.sh`를 실행하면 `yolo26n.dxnn`이 없는 경우 즉시 실패함.
  - `setup.sh`이 `dx_com` 미설치 시 `WARNING`만 출력하고 종료하지 않음 — 컴파일 세션임에도 의존성 누락을 soft-warning으로만 처리해 이후 단계에서 cryptic 오류 발생 가능.
  - README의 "Generated Artifacts" 항목(`yolo26n.pt`, `yolo26n.onnx`, `yolo26n.dxnn`)이 세션 실행 중 이미 생성된 파일인지, 아니면 사용자가 직접 재생성해야 하는지 명시가 없음 — 재현 절차(export → compile 단계) 전혀 안내되지 않음.

- **One-sentence verdict**: `run.sh`이 컴파일을 수행하지 않고 `verify.py`만 호출하므로, 사전 생성된 `.dxnn` 없이 처음 실행하는 사용자는 Quick Start 단계에서 바로 실패할 것임.


---

---

---

### R12 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues** (if any):
  - `run.sh`가 `source setup.sh 2>/dev/null || true` 패턴을 사용해 `setup.sh`의 실패(예: `dx_engine` 미설치 시 `exit 1`)를 **무음으로 삼킴**. 사용자는 setup 오류 메시지를 보지 못하고 이후 python 실행 단계에서 불명확한 오류를 받음
  - README에 **전제조건(Prerequisites) 섹션 없음**. `dx_engine` 사용을 위해 `cd dx-runtime/dx_app && ./install.sh && ./build.sh`가 선행되어야 하지만 언급이 없어 신규 사용자가 막힐 가능성 높음
  - **검증(verify) 단계 없음**: `verify.py` 미포함, 기대 출력 예시도 없어 실행 성공 여부를 사용자가 스스로 판단해야 함
- **One-sentence verdict**: setup.sh와 README의 구성은 대체로 양호하나, `run.sh`의 silent failure 패턴과 prerequisites 누락으로 인해 환경 미구성 사용자가 스스로 디버깅하기 어렵다.


---

---

---

### R12 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **경로 버그 (setup.sh / run.sh)**: `DX_STREAM_ROOT`를 `$SCRIPT_DIR/../..`(= `dx-runtime/dx_stream/`)로 설정한 뒤 `$DX_STREAM_ROOT/dx_stream/samples/...`를 참조하여 `dx_stream`이 중복된다(`dx-runtime/dx_stream/dx_stream/…`). 모델 경로와 기본 비디오 경로 모두 존재하지 않는 경로를 가리켜 **`[WARN] Model not found`** 및 `[ERROR] Video not found`가 발생한다.
  - **SUITE_ROOT 미적용**: HARD GATE에서 크로스-프로젝트 참조 시 `SUITE_ROOT` 자동 탐지 패턴을 요구하지만, `../..` 하드코딩을 사용했다.
  - **실제 파이프라인 실행 증거 없음**: `session.log`에는 `py_compile`, `bash -n`, `--help`, `validate_app.py` 결과만 기록되어 있고 GStreamer 파이프라인의 실제 기동·완료 출력이 없다 — Verification 미제공.

- **One-sentence verdict**: `setup.sh`/`run.sh`의 `dx_stream` 경로 중복 버그로 인해 모델 및 비디오 파일을 찾지 못해 엔드유저가 `run.sh` 한 번으로 실행하기 어려우며, 실제 파이프라인 동작 검증도 제공되지 않는 PARTIAL 상태이다.


---

---

---

### R12 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **핵심 artifact 누락**: `run.sh`이 내부적으로 호출하는 `run_cascaded.sh`과 `pipeline.py`가 session.log나 README에 존재 여부만 언급될 뿐, 내용이 제공되지 않아 실제 실행 가능 여부를 검증할 수 없음
  - **setup.sh 모델 경로 버그**: `DX_STREAM_ROOT`가 이미 dx_stream 루트인데 모델 경로를 `$DX_STREAM_ROOT/dx_stream/samples/models/`로 체크함 → `dx_stream/dx_stream/` 이중 경로로 모델 다운로드 조건이 항상 실패하거나 잘못된 위치 참조
  - **README의 `--model` 인수가 실제 setup.sh 시그니처와 불일치**: README는 `./setup.sh --model=yolo26n.dxnn`을 직접 사용 가능한 것처럼 안내하지만, setup.sh는 `--model` 인수를 파싱하지 않고 내부적으로 상위 dx_stream의 `./setup.sh`에 위임함 — 사용자가 해당 인수를 단독으로 실행하면 동작하지 않음

- **One-sentence verdict**: 핵심 실행 파일(`run_cascaded.sh`, `pipeline.py`) 부재와 setup.sh의 모델 경로 버그로 인해 사용자가 README만 따랐을 때 첫 실행 성공을 보장할 수 없는 PARTIAL 상태임.


---

---

---

### R12 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **venv 활성화가 run.sh에 전달되지 않음**: `run.sh`이 `bash setup.sh`을 서브프로세스로 호출하므로, setup.sh 내의 `source venv/bin/activate`는 해당 서브셸 안에서만 유효하고 종료 시 사라짐. 이후 `python "$SCRIPT_DIR/yolo26n_sync.py"` 호출은 시스템 python으로 실행되어 `dx_engine` import 실패 가능성이 높음. `source "$SCRIPT_DIR/setup.sh"` 또는 venv python 경로 직접 사용으로 수정해야 함.
  - **`setup.sh` 오류 묵살**: `bash setup.sh >/dev/null 2>&1 || true` 패턴으로 setup 실패 시에도 run.sh이 계속 실행되어 사용자에게 이해하기 어려운 에러(`ModuleNotFoundError`)만 표시됨.
  - **README의 Prerequisites 경로 불명확**: `cd ../../` 등 상대 경로가 어느 디렉토리 기준인지 명시되어 있지 않고, Manual Runs 경로(`../../assets/models/yolo26n.dxnn`)도 세션 디렉토리에서 실행하는 전제가 없으면 혼란을 줌.
- **One-sentence verdict**: session.log에는 실제 추론 실행 증거(21.64ms latency, 35.3 FPS)가 있어 에이전트 환경에서는 정상 동작했으나, `run.sh`의 venv 전파 버그로 인해 일반 사용자가 `bash run.sh`만 실행했을 때 `dx_engine` import 오류로 실패할 가능성이 높다.


---

---

---

### R12 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 실질적인 추론 실행 없이 `verify.py`만 호출함 — README Quick Start의 `bash run.sh`가 "모델 실행"처럼 보이지만 실제로는 수치 비교 검증만 수행하며, 이 차이가 README에 전혀 설명되어 있지 않음
  - `setup.sh`가 `dx_com` 부재 시 경고만 출력하고 설치를 시도하지 않음 — 컴파일 재실행이 필요한 사용자는 별도로 `dx-compiler` venv를 직접 활성화해야 하지만 그 방법이 README에 누락됨
  - `setup.sh` 내 `sanity_check.sh` 실패를 `|| true`로 묵살 — NPU 하드웨어 미사용 환경에서도 "Setup complete"를 출력하며 진행되어, `verify.py`가 나중에 `dx_engine` 오류로 실패할 때 원인 파악이 어려움

- **One-sentence verdict**: 컴파일된 `.dxnn`과 `dx_engine`이 이미 설치된 환경에서는 `verify.py` 실행까지 도달할 수 있으나, `run.sh`의 역할이 모호하고 `dx_com` 미설치 시의 대응 방법이 README에 없어 처음 접하는 사용자가 독립적으로 전체 파이프라인을 재현하기 어렵다.


---

---

---

### R12 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **실제 inference 실행 증거 없음** — `session.log`(720바이트)에 syntax check와 `--help` import test만 기록되어 있고, `python yolo26n_sync.py --model ... --image ...` 실제 추론 실행 결과가 전혀 없음. session.log가 실제 커맨드 출력이 아닌 fabricated 요약처럼 보임
  - **`build.sh` 미제공** — README와 setup.sh 모두 `./build.sh`를 언급하지만 아티팩트 목록에 없어 cpp_postprocess 변형(`sync_cpp`, `async_cpp`)을 실행하려는 사용자는 진행 불가
  - **README 파일 목록에 `session.json`만 나열** — `session.log`가 누락되어 있고 반대로 `session.json`이 포함되어 있어 경미한 불일치 존재

- **One-sentence verdict**: setup/run 구조는 명확하고 import 테스트까지는 통과했으나, 실제 NPU 추론 실행 증거가 없고 C++ postprocessor 빌드 스크립트가 누락되어 완전한 실행 가능성을 보장하기 어려움.


---

---

---

### R12 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`는 `$1`(MODEL 경로)을 받아 유효성 검사까지 하지만, `run_detection.sh` 호출 시 VIDEO만 전달하고 MODEL 인자는 묵시적으로 누락됨 — 사용자가 커스텀 모델 경로를 지정해도 실제로 적용되지 않음
  - README의 모든 상대 경로(`../../`)가 세션 디렉터리 기준이라는 설명이 없어, 사용자가 다른 위치에서 실행 시 경로 오류 발생 가능
  - `setup.sh`의 모델 다운로드 폴백(`./setup.sh --model=...`)이 dx_stream 루트의 `setup.sh`가 해당 `--model` 플래그를 지원한다는 가정에 의존하며, 실패 시 `[WARN]`만 출력하고 진행함

- **One-sentence verdict**: session.log에 실제 파이프라인 실행 증거가 있어 기본 경로에서는 동작하지만, `run.sh`의 MODEL 인자 전달 누락과 상대 경로 문서화 부족으로 커스텀 환경에서 사용자가 막힐 가능성이 있다.


---

---

---

### R12 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (partial)
- **Key issues**:
  - `run.sh`가 실제 실행을 `run_cascaded.sh`에 완전히 위임하지만, `run_cascaded.sh`의 내용이 제공된 artifacts에 없어 secondary model 경로 및 postprocess lib 인자 전달 여부를 검증할 수 없음
  - `session.log`에서 첫 실행 시 `dxgather: no property "num-sources"` 오류가 발생했으며 재시도 로그는 truncated되어 최종 성공 여부를 확인할 수 없음
  - `run.sh`가 `source setup.sh 2>/dev/null || true`로 setup 실패를 무음 처리하여 사용자가 환경 문제를 인지하지 못한 채 실행을 계속할 위험이 있음

- **One-sentence verdict**: 핵심 실행 파일인 `run_cascaded.sh`의 내용 누락과 session.log의 초기 실행 오류(수정 후 성공 미확인)로 인해 사용자가 README만 보고 end-to-end로 실행을 완료하기에는 불확실성이 남아 있는 PARTIAL 수준의 artifact임.


---

---

---

### R12 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - **session.log가 fabricated** — 실제 명령 실행 출력 없이 정적 체크리스트만 포함. `python yolo26n_sync.py --help` 실행, import 검증, 실제 추론 출력이 전혀 없음. `session.log Must Be Real Output` HARD GATE 위반
  - **CLI 플래그 불일치** — README 실행 예시에서는 `--image` 플래그를 사용하지만 run.sh에서는 `--input`을 사용. 사용자가 README를 그대로 복사하면 실패할 가능성 있음
  - **run.sh가 매 실행 시 setup.sh를 source** — NPU 체크 및 모델 다운로드 로직이 매 실행 시 재수행됨. 기능상 동작하지만 비효율적이며, setup.sh의 `set -e`가 run.sh 전체 실행에 영향을 줌
- **One-sentence verdict**: README 구조는 깔끔하고 파일 목록도 완비되어 있으나, session.log가 실제 실행 증거가 없는 정적 체크리스트에 불과하고 CLI 플래그 불일치가 있어 사용자가 README를 그대로 따랐을 때 실패 위험이 존재한다.


---

---

---

### R12 claude-code compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 `verify.py`를 `--dxnn`, `--input`, `--show` 인자와 함께 호출하지만, `verify.py`가 해당 CLI 인자를 지원하는지 확인 불가 (verify.py 내용이 미제공). README Quick Start의 `python verify.py` (인자 없음)와 `run.sh`의 호출 방식이 불일치함.
  - `setup.sh`의 Step 4에서 `$RUNTIME_DIR/dx_rt/python_package/*.whl`을 `pip install`하지만, 해당 경로에 `.whl` 파일이 없을 경우 glob 미매칭으로 silently skip되어 `dx_engine` 미설치 상태로 진행될 수 있음 (glob 실패 시 에러 없음).
  - `session.log`에 `verify.py` 실행 결과("RESULT: PASS" 등)가 없어 수치 비교 검증의 성공 여부가 불명확함 — 필수 증거 누락.
- **One-sentence verdict**: setup과 컴파일은 정상 완료되었으나 `run.sh`와 `verify.py` 간 인터페이스 불일치 및 검증 실행 증거 부재로 사용자가 그대로 따라 실행하기 어려운 PARTIAL 수준이다.


---

---

---

### R12 claude-code dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `setup.sh`에서 sanity check 출력을 `| tail -3`로 파이핑 — 프레임워크 규칙에서 명시적으로 금지된 패턴이며, 실제 실패를 마스킹하고 exit code를 항상 0으로 대체함
  - `setup.sh`에 venv 생성 및 pip 의존성 설치 단계 없음 — `dx_engine`이 시스템에 사전 설치되어 있지 않으면 사용자가 어떻게 해야 할지 알 수 없음
  - README에 사전 요구사항(dx_engine import 가능 여부, yolo26n.dxnn 모델 위치) 설명 없음 — `bash run.sh`만 실행하면 된다고 안내되어 있으나 전제 조건이 명시되지 않음

- **One-sentence verdict**: run.sh 자체는 명확하고 session.log도 실제 실행 증거를 포함하고 있으나, setup.sh의 sanity check 마스킹과 venv 부재로 인해 DEEPX SDK가 사전 설치된 환경에서만 정상 작동하며 fresh 환경에서의 재현성은 보장되지 않는다.


---

---

---

### R12 claude-code dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `run_detection.sh`를 호출하나, 이 스크립트는 제공된 아티팩트 목록에 없음 (README 파일 표에는 있음) — 사용자가 내용을 확인할 수 없고, 누락 시 런처가 즉시 실패함
  - `setup.sh`의 venv fallback 로직이 로컬 venv를 새로 생성할 때 `pydxs`를 설치하지 않음 — dx_stream venv가 없는 환경에서는 `pipeline.py` 실행 시 `ImportError` 발생
  - `../..` 하드코딩 경로 사용 (SUITE_ROOT 미적용) — session.log에서 `dx_stream/dx_stream/` 이중 경로가 관찰되며, 이는 경로 계산이 취약함을 시사함 (현재 환경에서는 우연히 동작)

- **One-sentence verdict**: session.log에 실제 파이프라인 실행 증거가 있고 README 구성은 양호하나, `run_detection.sh` 누락 가능성, venv fallback 미완성, 경로 하드코딩 이슈로 인해 다른 환경의 사용자가 그대로 따라 실행하기에는 신뢰도가 낮음.


---

---

---

### R12 claude-code dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **run.sh 인자 위치 불일치 (버그)**: README는 `bash run.sh /path/to/video.mp4` 사용을 안내하지만, run.sh 내부에서 `$1`은 `PRIMARY_MODEL`로 매핑됨. 사용자가 영상 경로를 전달하면 `[ERROR] Primary model not found` 오류 발생
  - **커스텀 모델 경로 소실**: run.sh에서 커스텀 모델을 `$1/$2`로 받더라도 `run_cascaded.sh "$VIDEO"`만 호출하므로 커스텀 모델 경로가 실제 실행 스크립트에 전달되지 않음
  - **모델 다운로드 명령 검증 미흡**: Prerequisites 섹션의 `./setup.sh --model="..."` 명령이 dx_stream 루트의 setup.sh가 `--model` 플래그를 지원한다고 가정하나, 실제 인터페이스 확인 없이 문서화됨

- **One-sentence verdict**: 기본 실행(`bash run.sh` 인자 없음)과 영상 기록 옵션은 session.log로 정상 동작이 검증되었으나, README에 안내된 커스텀 비디오 경로 지정 방식이 run.sh 인자 매핑 버그로 인해 실패하므로 PARTIAL 판정.


---

---

---

### R12 claude-code runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `setup.sh`의 sanity check 판정 로직이 잘못됨 — `grep -q "PASS"` 방식은 exit code 대신 텍스트를 사용하지만, 실제 출력에 `"PASS"` 문자열만 있어도 통과 처리됨 (명세서는 "Sanity check PASSED!" 전체 문자열 기준). 더 심각한 문제는 `[ERROR]` 라인이 있어도 grep 히트가 없으면 PASS로 분기될 수 있음
  - `yolo26n.dxnn` 모델 파일에 대한 사전 준비 안내가 없음 — `run.sh`는 모델이 없으면 에러로 종료하지만, README에서 모델을 어떻게 획득/빌드하는지 설명이 누락되어 있음 (`./setup.sh --model=yolo26n.dxnn`은 실제로 존재하지 않는 명령)
  - `session.log`가 866바이트로 매우 짧으며 실제 inference 실행 증거(추론 결과, latency 등)가 없음 — syntax check와 import test만 기록되어 있어 end-to-end 동작 검증이 미완성

- **One-sentence verdict**: setup/run 스크립트 구조는 양호하나 모델 파일 획득 경로가 불명확하고 sanity check 판정 로직에 버그가 있어 NPU 환경이 다른 사용자는 setup 단계에서 막힐 가능성이 높음.


---

---

---

### R13 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **README Quick Start에 하드코딩된 절대경로**: `cd "/data/home/dhyang/github/..."` 및 `verify.py --dxnn "/data/home/dhyang/..."` 명령이 원본 머신에서만 동작 — 다른 사용자는 경로를 수동으로 수정해야 함
  - **README에 사전 요구사항(Prerequisites) 섹션 누락**: `setup.sh` 실행 전에 필요한 환경(Python 버전, DEEPX SDK 설치 여부, 저장소 클론 상태 등)에 대한 언급 없음
  - **실행 성공 기준(expected output) 미명시**: `run.sh` 실행 후 `result_yolo26n.jpg`가 생성되는 것이 성공임을 README에서 설명하지 않고, `detect_yolo26n.py`가 어떤 결과를 출력해야 하는지도 안내 없음
- **One-sentence verdict**: `setup.sh`와 `run.sh` 스크립트 자체는 SUITE_ROOT 자동 탐지 등 이식성 측면에서 잘 작성되었으나, README Quick Start의 하드코딩된 절대경로로 인해 원본 머신 외 환경에서는 수동 수정 없이 그대로 따라하기 어렵다.


---

---

---

### R13 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `setup.sh`의 fallback 경로가 깨짐: `venv-dx-runtime`을 찾지 못할 경우 local venv를 생성하지만, 그 안에서 `dx_engine`/`dx_postprocess` import를 시도 → pip로 설치 불가능한 SDK 패키지이므로 즉시 실패함
  - README에 사전 요구사항(Prerequisites) 섹션 없음: `.dxnn` 모델 파일 위치(`../../assets/models/yolo26n.dxnn`)가 이미 존재해야 하고 dx-runtime SDK가 설치되어 있어야 한다는 설명이 없어 첫 실행 시 사용자가 `[ERROR] Model not found` 또는 import 오류로 막힘
  - `session.log`에서 최초 sanity check 경로가 잘못됨(`../../scripts/` → `../scripts/`으로 수동 수정 흔적 노출): 에이전트의 경로 오류가 그대로 기록되어 있어 재현 신뢰도를 낮춤; `verify.py`도 제공되지 않아 수치 검증 불가
- **One-sentence verdict**: Quick Start 커맨드 자체는 명확하지만, dx-runtime venv 미탐지 시 setup.sh가 반드시 실패하고 사전 요구사항 안내가 없어 SDK 미숙한 사용자는 독립적으로 실행하기 어렵다.


---

---

---

### R13 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **README 경로 오류**: Option A·C의 수동 실행 예시가 `../../dx_stream/samples/videos/…`를 사용하지만, 세션 디렉터리(`dx_stream/dx-agentic-dev/<session>/`)에서 `../../`는 이미 `dx_stream/`이므로 `dx_stream/dx_stream/samples/…`로 이중 경로가 됨 — 올바른 경로는 `../../samples/videos/…`
  - **`run_yolo26n_detection.sh` 미검증**: README·run.sh가 핵심 래퍼 스크립트로 참조하지만 아티팩트 목록에만 있고 실제 내용이 평가에 포함되지 않아 동작 여부 확인 불가
  - **실제 파이프라인 실행 증거 없음**: session.log가 `--help`, 파일 존재 확인, `gst-inspect` 정도만 수행하고 실제 영상 추론 실행(smoke test) 출력이 없어 end-to-end 동작을 보장할 수 없음

- **One-sentence verdict**: `run.sh`(Option B) 경로 자동 처리는 올바르게 동작할 가능성이 높지만, README의 수동 실행 경로 오류와 핵심 래퍼 스크립트(`run_yolo26n_detection.sh`) 내용 미공개, 실제 추론 실행 증거 부재로 인해 처음 접하는 사용자가 성공적으로 완전 실행하기는 어렵다.


---

---

---

### R13 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README Prerequisites 4단계가 혼란스럽다: `cd ../..` 후 `./setup.sh --model=yolo26n.dxnn`를 호출하도록 지시하는데, 세션 폴더 내 `setup.sh`가 이 다운로드를 이미 자동으로 처리한다. 두 개의 setup.sh(세션용 vs. dx_stream 루트용)가 혼재해 사용자가 어느 것을 실행해야 할지 불명확하다.
  - `setup.sh`의 `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"` 경로가 하드코딩되어 있으며, 세션 디렉토리가 `dx_stream/dx-agentic-dev/<session>/`에 위치한다는 가정에 의존한다. 세션 경로 깊이가 달라지면 모델 경로 탐색이 실패한다.
  - `run_cascaded.sh` 파일 내용이 README에 전혀 노출되지 않아, 사용자는 해당 파일이 실제로 올바르게 동작하는지 검증할 방법이 없다. `run.sh` 의 one-command 성격이 README 앞부분에 충분히 강조되지 않고, Option A로 `run_cascaded.sh`를 직접 호출하도록 안내하고 있어 진입점이 분산된다.

- **One-sentence verdict**: `pipeline.py --help` 실행 성공 등 검증 증거는 있으나, 이중 `setup.sh` 구조와 하드코딩된 상대경로로 인해 dx_stream에 익숙하지 않은 사용자가 독립적으로 setup → run → verify를 완주하기 어렵다.


---

---

---

### R13 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `setup.sh`를 `>/dev/null 2>&1 || true`로 호출하여 setup 실패(예: `dx_engine` 미설치)가 **완전히 묵살**됨 — 사용자 입장에서 inference 실패 원인을 알 수 없음
  - README Prerequisites의 `cd ../../` 및 `./install.sh && ./build.sh`가 어느 디렉토리 기준인지 명시되어 있지 않아 (`dx_app` 루트 추정) 초보 사용자에게 혼란 유발
  - session.log에서 NPU 체크가 `dxrt-cli not found`로 **SKIP** 처리됨 — 실제 NPU 환경 유효성 미검증 상태에서 PASS 판정

- **One-sentence verdict**: 환경이 이미 올바르게 구성된 사용자라면 `bash run.sh`로 바로 실행 가능하지만, `run.sh`의 silent failure 패턴과 불명확한 Prerequisites 때문에 미숙한 사용자는 실패 원인 파악에 어려움을 겪을 가능성이 높다.


---

---

---

### R13 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **session.log가 truncated됨** — CLI 컴파일 실패(Pitfall #18 NHWC/NCHW) 후 Python API fallback으로 전환했으나 로그가 중간에 잘려 있어 `yolo26n.dxnn` 최종 생성 성공 및 `verify.py`의 `RESULT: PASS` 출력이 확인되지 않음. 증거가 불완전함.
  - **`detect_yolo26n.py` 내용 미제공** — README의 Generated Files 목록에 포함되어 있고 `run.sh`에서 직접 호출되지만, 해당 파일의 내용이 아티팩트에 포함되지 않아 사용자가 실행 시 파일 존재 여부를 별도 확인해야 함.
  - **setup.sh Step 1 silent failure 위험** — sanity check 실패 시 `||`로 install을 호출하는 구조인데, install이 실패해도 `set -e`가 적용되지 않는 흐름이어서 오류를 조용히 무시하고 이후 단계로 진행될 수 있음.
- **One-sentence verdict**: 스크립트 구조와 README 가독성은 수준급이나, session.log 증거 부재(truncated)로 컴파일 성공 여부를 독립적으로 검증할 수 없어 PARTIAL 판정.


---

---

---

### R13 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README의 Quick Start에 `cd <session_dir>` 명령이 없음 — `python yolo26n_sync.py` 실행 전 세션 디렉터리로 이동하는 단계가 누락되어, 처음 사용자는 `No such file or directory` 오류를 마주칠 가능성 높음
  - `setup.sh`는 `venv-dx-runtime` 공유 venv를 찾지 못하면 `opencv-python + numpy`만 포함한 로컬 venv를 생성한 뒤 `dx_engine` 체크에서 FATAL로 종료함 — README에 "dx-runtime venv가 먼저 필요하다"는 사전 조건 설명이 없어 사용자가 원인을 파악하기 어려움
  - C++ 변형(`sync_cpp`, `async_cpp`)은 `./build.sh`(dx_app 루트)를 먼저 실행해야 하지만, README Notes 섹션에 한 줄 언급만 있고 실제 빌드 절차(위치·명령·소요 시간)가 없어 사용자가 두 변형을 실행하기 어려움

- **One-sentence verdict**: 핵심 sync/async 변형은 dx-runtime venv만 있으면 실행 가능하지만, `cd` 누락과 사전 조건 미설명으로 인해 첫 실행 시 혼선이 예상되며 C++ 변형은 별도 빌드 안내 없이는 사용 불가하다.


---

---

---

### R13 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`../../` 하드코딩 경로 — 사용자 혼동 유발**: README의 `source ../../venv-dx_stream/bin/activate`, `cd ../../` 등이 세션 디렉터리를 기준으로 몇 단계인지 설명 없이 사용됨. `dx-runtime/dx_stream/dx-agentic-dev/<session>/` 구조를 모르는 사용자는 올바른 경로를 찾기 어려움. SUITE_ROOT 자동 감지 패턴 미적용.
  - **모델 경로 불일치**: `session.log`에는 파이프라인이 `/workspace/res/models/models-2_3_0/yolo26n.dxnn`을 사용했으나, `setup.sh`/`README`는 `dx_stream/samples/models/yolo26n.dxnn`을 기대함 — 다른 환경에서 `run.sh` 실행 시 모델 미발견으로 즉시 실패.
  - **`run.sh`가 setup 에러를 묵살**: `source "$SCRIPT_DIR/setup.sh" 2>/dev/null || true`로 venv 활성화 실패 시 에러 없이 진행 → pydxs import 실패가 늦게 발생해 원인 추적 어려움.

- **One-sentence verdict**: 파이프라인 실행 자체는 검증되었으나 하드코딩 상대 경로와 모델 경로 불일치로 인해 다른 환경의 사용자가 README만 따라 실행 성공하기 어렵다.


---

---

---

### R13 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `$1`(primary model 경로)을 받아서 `$MODEL` 변수에 저장하지만, `run_cascaded.sh`를 호출할 때 `"$VIDEO"` 인자만 전달함 — secondary model 경로는 물론 primary model 경로도 `run_cascaded.sh`로 전달되지 않아, 기본 경로(`$SRC_DIR/samples/models/`) 이외의 모델 사용 불가
  - `setup.sh`의 모델 다운로드 경로(`$SCRIPT_DIR/../..`의 `./setup.sh --model=...`)가 세션 디렉토리가 정확히 `dx_stream/dx-agentic-dev/<session>/` 2단계 깊이에 있다는 가정에 의존하며, `run_cascaded.sh` 파일 내용이 평가 범위에 포함되지 않아 실제 secondary model 경로 처리 방식 확인 불가
  - README "Option A"는 `run_cascaded.sh`를 직접 호출하도록 안내하고 Files 표는 `run.sh`를 "One-command launcher"로 설명하는데, 두 스크립트 모두 제시되어 있어 처음 보는 사용자가 어느 것을 실행해야 하는지 혼란스러울 수 있음

- **One-sentence verdict**: 파이프라인 자체는 실제 실행 증거(session.log)가 확인되고 README 품질도 양호하나, `run.sh`의 모델 경로 미전달 버그와 `run_cascaded.sh` 내용 미공개로 인해 기본 경로 밖의 모델을 사용하거나 헤드리스 환경에서 처음 실행하는 사용자는 부분적인 재작업이 필요하다.


---

---

---

### R13 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`에서 `bash setup.sh >/dev/null 2>&1 || true`로 setup 실패를 무음 무시함 — `dx_engine`이 없을 경우 setup.sh의 `exit 1`이 억제되어 inference 단계에서 불명확한 오류로 이어짐
  - `run.sh`의 `DEFAULT_MODEL` / `DEFAULT_IMAGE` 경로(`../../assets/models/...`)가 `$SCRIPT_DIR` 기준이 아닌 실행 시점의 CWD 기준 — 사용자가 세션 디렉토리 외부에서 `bash /path/to/run.sh`를 실행하면 "file not found" 오류 발생
  - README Prerequisites의 `cd ../../`가 어느 디렉토리 기준인지 명시되지 않음 (세션 디렉토리? `dx_app` 루트?) — 처음 접하는 사용자는 혼란스러울 수 있음

- **One-sentence verdict**: 세션 디렉토리 내에서 순서대로 실행하면 동작하지만, `run.sh`의 setup 오류 묵살 및 CWD 의존적 경로로 인해 환경이 조금이라도 달라지면 디버깅하기 어려운 실패가 발생할 수 있다.


---

---

---

### R13 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **파일명 불일치**: README artifacts 표에는 `yolo26n.dxnn`으로 기재되어 있으나, session.log의 실제 컴파일 출력은 `model.dxnn` (7,113,972 bytes)임. verify.py가 어느 파일명을 참조하는지에 따라 런타임 에러 발생 가능
  - **`pip install dx-com` 실패 가능성**: setup.sh가 `dx-com`을 PyPI에서 설치하려 하나, 이는 DEEPX 내부 패키지로 공개 PyPI에 존재하지 않을 가능성이 높음. 컴파일 재현 목적이 아닌 verification 전용 세션이라면 `dx-com`은 불필요하며, `dx_engine`(DXNN 추론 실행용) 설치 경로가 누락되어 있음
  - **session.log 조작 의심**: 로그가 실제 터미널 출력(`command 2>&1 | tee session.log`)이 아닌 정형화된 요약 형식으로 작성됨. 규칙상 `cat << 'EOF'` 또는 수기 요약은 금지되며, 검증 결과("PASS")의 신뢰도를 담보할 수 없음
- **One-sentence verdict**: 파일명 불일치(`yolo26n.dxnn` vs `model.dxnn`)와 내부 패키지 설치 불확실성으로 인해 사용자가 그대로 실행 시 오류가 발생할 가능성이 높으며, session.log가 실제 실행 증거로 신뢰하기 어려워 PARTIAL 판정.


---

---

---

### R13 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `session.log`의 실행 증거가 `--help` 출력 + 구문 검사만 포함 — 실제 모델 추론 실행(inference with `.dxnn`) 결과가 없음. `RESULT: PASS`는 스크립트 기동 가능 여부만 확인한 것으로, NPU 실제 동작 여부는 미검증
  - `run.sh`가 `setup.sh`를 `source … 2>/dev/null || true`로 호출 — setup 오류(예: `dx_engine` 미설치)가 묵살되어 사용자가 조용히 실패할 수 있음
  - README·`run.sh` 모두 `../../assets/models/yolo26n.dxnn` 상대 경로 의존 — 모델 파일이 해당 경로에 없으면 `[ERROR] Model not found`로 즉시 실패하며, 사용자가 모델을 직접 준비하는 방법에 대한 안내가 없음

- **One-sentence verdict**: 아티팩트 구조와 README 가독성은 양호하나, 실제 NPU 추론 실행 증거 부재 및 `run.sh`의 오류 묵살 패턴으로 인해 첫 실행 시 사용자가 원인을 파악하기 어려운 실패를 겪을 수 있어 **PARTIAL** 판정.


---

---

---

### R13 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run_yolo26n_detection.sh`이 README Quick Start에 옵션 2b로 명시되어 있으나 아티팩트 목록에 없음 — 사용자가 실행하면 파일 없음 오류 발생
  - `session.log`에는 `setup.sh` 환경 체크 결과만 있고 실제 파이프라인 실행(GStreamer 파이프라인 시작, 추론 프레임 처리) 출력이 전혀 없음 — 에이전트가 파이프라인을 실제로 실행했다는 증거 없음
  - README 섹션 2c의 `source ../../venv-dx_stream/bin/activate` 경로는 세션 디렉터리 기준으로 부정확할 수 있음 (`run.sh` 내부의 `$DX_STREAM_ROOT/venv-dx_stream` 방식을 쓰지 않음)

- **One-sentence verdict**: 환경 설정 흐름과 README 구조는 명확하지만, 파이프라인 실제 실행 증거가 session.log에 없고 참조된 `run_yolo26n_detection.sh`가 누락되어 end-user가 완전히 재현하기에 불충분하다.


---

---

---

### R13 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run_cascaded.sh`가 README 파일 목록에 포함되어 있고 `run.sh`도 이를 호출하지만, 제공된 아티팩트에 해당 파일의 내용이 없어 사용자가 직접 확인할 수 없음. session.log에서 실제 실행이 확인되므로 파일은 존재하겠지만, 평가 관점에서 누락된 핵심 진입점임.
  - README의 파이프라인 다이어그램이 코드 블록(` ``` `) 안에 또 다른 코드 블록을 중첩 사용해 마크다운 렌더링이 깨짐 — 첫 번째 Prerequisites 블록이 닫히지 않은 것처럼 보임.
  - `setup.sh`가 `../..` 하드코딩 상대경로로 dx_stream root를 찾음(SUITE_ROOT 자동탐지 패턴 미사용). session.log 경로(`dx-runtime/dx_stream/dx_stream/...`)상 현재는 동작하나, 세션 디렉터리 깊이가 달라지면 즉시 실패.

- **One-sentence verdict**: 실제 파이프라인 실행은 session.log로 증명되어 있지만, 핵심 실행 파일(`run_cascaded.sh`) 내용 미공개, 중첩 코드블록으로 인한 README 렌더링 오류, SUITE_ROOT 미사용 상대경로 등으로 인해 타 사용자가 처음부터 재현하기에는 불완전한 상태다.


---

---

---

### R13 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `setup.sh` / `run.sh` 모두 하드코딩된 상대경로 `../../..` 로 `DX_APP_ROOT`를 계산함 — 세션 디렉터리 깊이가 달라지면 즉시 깨짐 (SUITE_ROOT 자동 탐지 패턴 미적용)
  - `session.log` 파일 없음 — 에이전트가 실제로 artifact를 실행·검증했다는 증거가 전혀 없고, `verify.py`도 목록에 없어 수치 검증 불가
  - README의 수동 실행 예시(`--model /path/to/yolo26n.dxnn` 플레이스홀더)와 `run.sh`의 자동 모델 경로 처리 로직이 불일치하여 사용자 혼란 유발
- **One-sentence verdict**: 파일 구조와 아키텍처 설명은 갖추고 있으나, 경로 하드코딩 취약성·session.log 부재·verify.py 누락으로 인해 실행 재현성과 신뢰성이 불충분한 PARTIAL 수준이다.


---

---

---

### R13 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`run.sh`가 사실상 빈 껍데기**: `run.sh`는 모델 경로를 `echo`로 출력하고 `python verify.py`를 수동으로 실행하라고 안내할 뿐, 실제로 아무것도 실행하지 않는다. README Quick Start에서 `bash run.sh`를 단계로 포함시켰지만 실효성이 없어 사용자 혼란을 유발한다.
  - **`yolo26n.onnx` 전제조건 미기재**: README에 ONNX 파일이 어떻게 생성되는지(또는 이미 존재해야 하는지) 명시가 없다. 첫 실행 사용자는 `compile.py`를 직접 실행해야 하는지 알 수 없다.
  - **`setup.sh`에 `torch` 풀 설치 포함**: `pip install torch torchvision`은 ~2 GB 다운로드로 매우 느리며, calibration DataLoader 용도 외에 실제 추론 시에는 불필요할 수 있다. 설치 이유에 대한 설명이 없다.

- **One-sentence verdict**: `setup.sh` 구성과 실제 컴파일 증거(session.log)는 충실하지만, `run.sh`가 실질적인 동작을 수행하지 않고 ONNX 파일 전제조건이 미기재되어 있어 처음 접하는 사용자가 독립적으로 실행을 완료하기 어렵다.


---

---

---

### R13 cursor-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README Quick Start 첫 줄 `cd "$(dirname "$0")"` 은 스크립트 내부 관용구로, 터미널에서 인터랙티브하게 실행 시 `.`(현재 디렉터리)로 처리되어 의도와 다르게 동작할 수 있음 — `cd /path/to/session/dir`처럼 명시적 경로로 교체해야 함
  - `verify.py`가 실제 추론(inference) 결과를 검증하지 않고 `py_compile` + `--help` smoke check만 수행함 — 실제 NPU 추론이 정상 동작하는지 확인 불가
  - `setup.sh`에서 `dx_engine`을 찾지 못해도 WARNING만 출력하고 종료 코드 0으로 통과함 — 이후 `run.sh` 실행 시 ImportError로 실패할 수 있어 사전 차단이 안 됨

- **One-sentence verdict**: setup/run 구조는 견고하고 session.log에 실제 실행 증거가 있으나, README Quick Start의 셸 관용구 혼용과 shallow한 verify.py로 인해 처음 보는 사용자가 독립 실행에 어려움을 겪을 수 있어 PARTIAL 판정.


---

---

---

### R13 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`dx_stream` 이중 경로 버그**: `setup.sh`·`run.sh` 모두 `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"`로 설정하면 결과가 `dx-runtime/dx_stream/`인데, 이후 `$DX_STREAM_ROOT/dx_stream/samples/...`로 경로를 이어붙여 실제로는 `dx-runtime/dx_stream/dx_stream/samples/...`(존재하지 않는 디렉터리)를 참조함. 기본 비디오 경로 검사(`run.sh` `VIDEO` 체크)가 즉시 실패함.
  - **모델 경로 불일치**: `setup.sh`가 기대하는 모델 위치(`$DX_STREAM_ROOT/dx_stream/samples/models/yolo26n.dxnn`)와 `session.log`에서 실제 사용된 경로(`/workspace/res/models/models-2_3_0/yolo26n.dxnn`)가 전혀 다름. 신규 사용자는 수동으로 모델 경로를 찾아야 함.
  - **README에 `/path/to/dx_stream` 플레이스홀더 존재**: Prerequisites 및 Headless 실행 예제에 실제 경로 대신 미완성 플레이스홀더가 그대로 남아 있어, 사용자가 올바른 경로를 스스로 추론해야 함.

- **One-sentence verdict**: 파이프라인 자체는 에이전트 환경에서 정상 실행이 확인됐으나, `dx_stream` 이중 경로 버그와 모델 경로 불일치로 인해 신규 사용자가 `bash run.sh`만으로 즉시 실행하기는 어렵다.


---

---

---

### R13 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run_cascaded.sh`와 `pipeline.py`의 내용이 제공된 아티팩트에 포함되지 않아 존재 여부를 확인할 수 없으며, `run.sh`가 `run_cascaded.sh`를 직접 exec하므로 이 파일이 없으면 실행 불가
  - `session.log`에서 `tracker_config.json` 경로가 에이전트의 절대 경로(`/data/home/dhyang/...`)로 하드코딩되어 있어, 다른 머신에서는 동일한 오류 재발 가능성 높음
  - `setup.sh`가 `SUITE_ROOT` 패턴 대신 `../..` 상대 경로로 dx_stream 루트를 추론하는데, 디렉토리 구조가 다른 환경에서는 경로 추론 실패 위험 있음
- **One-sentence verdict**: README 구조는 명확하고 실행 증거도 있으나, 핵심 실행 파일(`run_cascaded.sh`, `pipeline.py`)의 내용 미포함 및 하드코딩된 절대 경로 문제로 타 머신에서의 재현성이 불확실하다.


---

---

---

### R13 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`이 실질적으로 아무것도 실행하지 않음 — 경로 출력 및 힌트 메시지만 표시하고 종료. 사용자가 `bash run.sh`를 실행해도 컴파일이나 검증이 수행되지 않아 기대와 크게 다름
  - `session.log`가 중간에 잘려 있어 `compile.py` 및 `verify.py`의 실제 실행 결과(`.dxnn` 생성 여부, verify PASS 여부)가 확인되지 않음 — 컴파일이 성공했다는 증거 부재
  - README Quick start에 사전 요구사항(ONNX 파일 존재 여부, `compile.py` 완료 후에야 `verify.py` 의미 있음)에 대한 안내 없음

- **One-sentence verdict**: `setup.sh`는 SUITE_ROOT 자동 탐지·venv 연결 등 구조가 탄탄하나, `run.sh`이 실질적인 실행 없이 경로만 출력하는 no-op 수준이고 session.log에 컴파일 성공 증거가 없어 end-user가 독립적으로 재현하기 어렵다.


---

---

---

### R13 claude-code compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`setup.sh` sanity check가 금지된 pipe 패턴 사용**: `bash sanity_check.sh ... | grep -q "Sanity check PASSED"` — grep의 exit code로 PASS/FAIL을 판단하기 때문에 실제 sanity check가 실패해도 PASSED로 처리될 수 있음 (HARD GATE 위반: "NEVER pipe through grep")
  - **`run.sh` vs README 불일치**: README는 `python verify.py`(인자 없음)를 안내하지만, `run.sh` 내부는 `python verify.py --dxnn "$DXNN" --image "$SAMPLE_IMAGE"`로 인자를 전달함. 또한 run.sh가 "Inference launcher"로 설명되어 있으나 실제로는 verify.py만 재실행 — 진짜 inference demo는 없음
  - **`session.log`에서 첫 번째 verify 시도 실패 기록**: `dx_engine` API 오류(`module 'dx_engine' has no attribute 'Engine'`) — 최종 PASS 전에 이 오류가 발생했으며, end-user 환경에서 동일한 dx_engine 버전 불일치 시 재현될 가능성 있음. session.log 상의 최종 성공 결과도 excerpt 내에서 truncated 상태

- **One-sentence verdict**: README와 setup.sh의 기본 흐름은 충분히 명확하지만, sanity check의 잘못된 pipe 패턴, run.sh와 README 간의 인자 불일치, dx_engine API 오류 재현 가능성으로 인해 end-user가 추가 디버깅 없이 완전히 실행하기 어려운 PARTIAL 수준이다.


---

---

---

### R13 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 5
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - `setup.sh`에 venv 생성/활성화 단계가 없어 PEP 668(Ubuntu 24.04+) 환경에서 `pip install` 없이 실행되지만, `dx_engine`은 시스템 패키지로 설치되어 있다는 전제에 의존함 — 다른 환경에서는 명시적 venv 안내가 없으면 실패 가능
  - `README.md`에 PYTHONPATH 설정 안내가 없음 (framework의 dynamic path walker에 의존하는 구조인데, 실패 시 대처 방법이 미기재)
  - `session.log`에 실제 inference 실행 출력(결과 이미지, detected object 수 등)이 없고 `--help` 출력까지만 기록되어 end-to-end 실행 성공 증거가 미흡

- **One-sentence verdict**: README·setup.sh·run.sh 모두 구조적으로 완성도가 높고 session.log에 sanity check PASS + syntax check PASS + `--help` 출력까지 확인되어 전반적으로 PASS 수준이나, 실제 inference 실행(이미지/영상 추론) 결과가 session.log에 누락되어 있어 완전한 end-to-end 검증 증거로는 부족하다.


---

---

---

### R13 claude-code dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **모델 경로 불일치**: `session.log`에서 실제 실행된 모델 경로는 `workspace/res/models/models-2_3_0/yolo26n.dxnn`이나, `run.sh`·README는 `dx_stream/samples/models/yolo26n.dxnn`을 참조함. 신규 사용자가 `bash run.sh`를 실행하면 `[ERROR] Model not found` 발생 가능성이 높음.
  - **상대 경로 의존성 취약**: `setup.sh`·`run.sh` 모두 `$(cd "$SCRIPT_DIR/../.." && pwd)`로 2단계 상위를 dx_stream root로 가정하나, 실제 세션 디렉토리 깊이(예: `dx_stream/dx-agentic-dev/<session_id>/`)와 일치하는지 README에서 명시하지 않음. 경로 계산 실패 시 자동 복구 없음.
  - **`run_yolo26n_detection.sh` 내용 미공개**: `run.sh`가 최종적으로 이 스크립트에 위임하지만 해당 스크립트의 내용은 제공되지 않았으며, README의 "Option A"도 이 스크립트를 직접 실행함. 스크립트 내부 경로 문제 발생 시 디버깅 근거 없음.
- **One-sentence verdict**: 실제 실행 증거(session.log)는 존재하고 파이프라인 성공이 확인되지만, 빌드 머신의 모델 경로와 배포 스크립트의 경로가 불일치하여 신규 사용자가 `bash run.sh` 한 번으로 재현하기 어렵다.


---

---

---

### R13 claude-code dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **상대 경로 하드코딩 (HARD GATE 위반)**: `setup.sh`와 `run.sh` 모두 `$(cd "$SCRIPT_DIR/../.." && pwd)` 방식으로 세션 디렉터리가 정확히 2단계 위에 `dx_stream` 루트가 있다고 가정함. SUITE_ROOT 자동 탐지 패턴을 사용하지 않아 디렉터리 깊이가 달라지면 모델/비디오 경로가 모두 깨짐.
  - **`run.sh` 인자 전달 버그**: `run.sh`는 `$1`을 primary model 경로로, `$2`를 video 경로로 받지만 `run_cascaded.sh`에는 `"$VIDEO"` 만 전달하고 커스텀 모델 경로는 누락됨. 또한 `source setup.sh 2>/dev/null || true` 로 venv 활성화 실패를 무음 무시해 `python3`가 시스템 Python으로 폴백될 수 있음.
  - **`run_cascaded.sh` 미제공**: README와 `run.sh`가 최종적으로 위임하는 핵심 스크립트인 `run_cascaded.sh`가 평가 아티팩트에 포함되지 않아 전체 실행 체인의 완전성을 독립적으로 검증하기 어려움 (session.log로 실행은 확인되나 재현 시 불투명).

- **One-sentence verdict**: pipeline.py 실행 자체는 session.log로 입증됐으나, 상대 경로 하드코딩과 `run.sh` 인자 버그로 인해 다른 환경에서 `bash run.sh`를 그대로 따라하면 실패할 가능성이 높아 PARTIAL 판정.


---

---

---

### R13 claude-code runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `session.log`의 sanity_check 섹션이 실제 명령 출력 대신 `"RESULT: PASS (checked earlier in this session)"` 요약 문구로 대체됨 — `session.log Must Be Real Output` 규칙 위반
  - `run.sh`에서 `source "$SCRIPT_DIR/setup.sh" 2>/dev/null || true` 패턴이 setup 오류를 무음으로 무시하여, 사용자가 dx_engine 누락 등 환경 문제를 감지하기 어려움
  - README에 명령 실행 위치(세션 디렉터리)가 명시되지 않아 상대 경로(`../../assets/models/yolo26n.dxnn`)가 혼란을 줄 수 있음

- **One-sentence verdict**: 실제 추론 실행이 성공적으로 확인되어 핵심 워크플로우는 동작하나, session.log의 sanity_check 항목 조작과 run.sh의 무음 오류 억제가 신뢰성을 저하시킴.


---

---

---

### R14 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **사전 조건 누락**: `setup.sh` Step 4에서 `dx-runtime/venv-dx-runtime/lib/.../dx_engine`이 없으면 오류 종료하나, README에 "dx-runtime venv를 먼저 빌드해야 한다"는 선행 조건이 명시되어 있지 않음. 신규 사용자는 `cd dx-runtime/dx_app && ./install.sh && ./build.sh`를 별도로 알아야 함.
  - **대용량 패키지 무경고 설치**: `setup.sh` Step 5에서 `torch torchvision`을 조용히(`--quiet`) 설치하는데, 수 GB에 달하는 패키지임에도 README에 언급 없음. 오프라인·디스크 제약 환경에서 setup 중단 가능.
  - **PASS 증거 불일치**: README의 "Latest automated run: **PASS**" 클레임을 session.log에서 직접 확인 불가 — 제공된 session.log는 compilation 로그만 담고 있으며 `verify.py` 실행 결과가 없음.

- **One-sentence verdict**: Quick start 명령(`bash setup.sh && bash run.sh`)은 간결하고 run.sh 실행 흐름도 정확하지만, `dx-runtime` 빌드 선행 조건이 README에 없어 환경이 준비되지 않은 사용자는 setup.sh에서 오류를 마주칠 가능성이 높다.


---

---

---

### R14 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 `source setup.sh 2>/dev/null || true`로 setup 오류를 조용히 무시함 — `dx_engine` 미설치 상태에서 setup 실패해도 run이 계속 진행되어 원인 불명의 ImportError가 발생할 수 있음
  - README 파일 목록에 `session.log`가 누락되어 있어 실행 증거 파일의 존재를 사용자가 알기 어려움
  - NPU 헬스 체크(`dxrt-cli -s`) 언급만 있고, 실패 시 복구 방법이 README에 없음
- **One-sentence verdict**: Quick start 3단계가 명확하고 setup/run 스크립트 모두 잘 구성되어 있어 DEEPX SDK 개발자라면 큰 어려움 없이 실행할 수 있으나, `run.sh`의 silent error suppression이 트러블슈팅을 어렵게 만드는 잠재적 함정이다.


---

---

---

### R14 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y (session.log 확인, 별도 verify.py 없음)
- **Key issues**:
  - **경로 불일치**: `session.log`의 실제 실행은 에이전트 환경의 절대 경로(`/data/home/dhyang/.../workspace/res/models/yolo26n.dxnn`)를 사용했으나, `run.sh`는 `dx_stream/samples/models/`를 기준으로 경로를 해석함 — 새 사용자 환경에서 model/video 경로가 모두 불일치할 수 있음
  - **위임 파일 불투명**: `run.sh`가 최종적으로 `run_yolo26n_detection.sh`를 호출하지만, 이 파일의 내용이 아티팩트에 포함되지 않아 실패 시 디버깅 불가
  - **모델 다운로드 경로 가정**: `setup.sh`의 `cd "$SCRIPT_DIR/../.."` 패턴이 세션 디렉터리 깊이(`dx-agentic-dev/<session>/`)를 암묵적으로 가정하며, `dx_stream root`에 `./setup.sh --model=` 인터페이스가 있음을 전제함 — 버전에 따라 다를 수 있음
- **One-sentence verdict**: 에이전트 자신의 환경에서는 성공적으로 실행됨이 확인되었으나, 새 사용자가 `bash run.sh` 한 줄로 재현하려 할 때 model/video 경로 불일치로 즉시 `[ERROR] Model not found`에 직면할 가능성이 높아 독립 재현성은 부분적(PARTIAL)으로 판단됨.


---

---

---

### R14 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **모델 경로 불일치 (Critical)**: `setup.sh`는 모델을 `dx_stream/dx_stream/samples/models/`에 준비하지만, `session.log`의 실제 파이프라인 실행은 `/workspace/res/models/models-2_3_0/` 경로를 사용했다. 즉, `setup.sh`가 준비한 경로와 `pipeline.py`가 실제로 참조한 경로가 다르며, 신규 사용자 환경에서는 모델을 찾지 못할 가능성이 높다.
  - **`run_cascaded.sh` 미제공**: `run.sh`가 핵심 위임 스크립트로 `run_cascaded.sh`를 호출하지만, 해당 파일이 artifacts 목록에 없어 내용 검증 불가. 사용자가 실행 시 `run_cascaded.sh not found` 오류를 만날 수 있다.
  - **`DX_STREAM_ROOT` 경로 이중 중첩**: `setup.sh`에서 `DX_STREAM_ROOT=$(cd "$SCRIPT_DIR/../..")`로 계산 시 `dx_stream/` 레포 루트가 되고, `SRC_DIR="$DX_STREAM_ROOT/dx_stream"`은 `dx_stream/dx_stream/`이 된다. `session.log`가 이를 확인하지만(`…/dx_stream/dx_stream/samples/models/`), README의 경로 표기(`dx_stream/samples/models/`)와 혼동을 유발한다.

- **One-sentence verdict**: README 문서화 품질은 우수하나, 실제 파이프라인이 `setup.sh`가 준비한 경로와 다른 모델 경로를 사용했고 핵심 스크립트(`run_cascaded.sh`)가 누락되어 신규 사용자가 그대로 따라 실행했을 때 성공을 보장하기 어렵다.


---

---

---

### R14 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 하드코딩된 app session 경로(`20260514-195154_cursor_composer_yolo26n_inference`)를 참조하는데, README에 해당 app session 경로 존재 여부 확인 방법이 없음 — 해당 inference session이 없으면 `run.sh`는 즉시 실패
  - `compile.py`가 백그라운드에서 실행되므로 `yolo26n.dxnn`가 아직 없을 때 `run.sh`를 실행하면 실패하지만, README에 완료 대기 방법(예: `compile.pid` 확인, `compile_out.log` 모니터링)이 명시되지 않음
  - `session.log`의 일부가 하드코딩된 절대경로(`/data/home/dhyang/...`)를 포함하여, 다른 사용자 환경에서는 참고용으로만 사용 가능하고 재현 불가

- **One-sentence verdict**: setup.sh와 verify.py는 잘 구성되어 있으나, 페어 app session 경로 하드코딩 및 컴파일 완료 대기 안내 부재로 인해 다른 환경의 사용자가 `run.sh`까지 성공적으로 실행하기 어렵다.


---

---

---

### R14 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **Quick Start의 venv 활성화 누락**: README Quick Start의 `python verify.py`는 venv 없이 실행되므로 `No module named 'onnxruntime'` 오류가 발생함. `bash setup.sh`는 내부에서 venv를 생성하지만 부모 shell에는 활성화되지 않음. Quick Start에 `source venv/bin/activate` 단계가 반드시 포함되어야 함.
  - **run.sh의 SAMPLE_IMG 빈값 전달**: 샘플 이미지가 없을 경우 WARNING만 출력하고 `--input ""`(빈 문자열)을 Python에 전달하여 스크립트가 모호한 오류로 종료됨. 이미지 미존재 시 `exit 1`로 명시적 실패 처리가 필요함.
  - **session.log 부분 조작 의심**: `18:51 $ command` 뒤에 "Session dir created" 등 수기 요약 텍스트가 혼재함. 규정상 `command 2>&1 | tee session.log` 실제 출력이어야 하며, 헤더 주석과 수동 메모는 금지 패턴에 해당함.

- **One-sentence verdict**: setup.sh·run.sh·verify.py 품질은 우수하나, Quick Start의 venv 활성화 단계 누락으로 일반 사용자가 `python verify.py`에서 막히며, session.log의 부분 조작이 감사 신뢰도를 저하시킴.


---

---

---

### R14 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `README.md`의 Direct Run Commands 섹션이 venv 활성화 없이 `python yolo26n_sync.py ...` 를 직접 나열하고 있어, `bash run.sh` 대신 직접 실행 시 `dx_engine` import 실패 가능
  - `run.sh`가 `source "$SCRIPT_DIR/setup.sh" 2>/dev/null || true` 로 setup 오류를 묵살(silent-swallow)하여, `dx_engine` 미설치 상태에서도 오류 없이 진행되다가 Python 실행 시점에 뒤늦게 실패
  - `../../assets/models/yolo26n.dxnn` 경로에 대한 사전 설명 없음 — 모델 파일이 없을 경우 어디서 얻어야 하는지(사전 컴파일 필요 여부) README에 명시되지 않아, 첫 사용자는 모델 부재로 즉시 막힘

- **One-sentence verdict**: `bash run.sh` 경로는 SUITE_ROOT 패턴·dx_engine 검증 등 핵심 안전장치를 갖추었으나, setup 오류의 묵살, Direct Run Commands의 venv 누락, 모델 파일 사전 조건 미설명으로 인해 사전 지식 없는 사용자는 시행착오를 겪을 가능성이 높다.


---

---

---

### R14 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **하드코딩된 절대 경로 노출**: `session.log`에서 실제로 성공한 파이프라인 실행은 빌드 머신의 절대 경로(`/data/home/dhyang/...`)를 사용했으며, tracker `config-file-path`도 머신 특정 경로로 하드코딩됨 — 다른 환경에서 `run_detection.sh`를 그대로 실행하면 tracker 설정 로드 실패 가능성 높음
  - **모델 경로 불일치**: `setup.sh`가 다운로드하는 모델 경로(`dx_stream/samples/models/yolo26n.dxnn`)와 실제 실행에서 사용된 모델 경로(`workspace/res/models/models-2_3_0/yolo26n.dxnn`)가 다름 — `run.sh`의 `DEFAULT_MODEL` 경로와 실제 검증 경로가 불일치
  - **`run_detection.sh` 내용 불투명 + 첫 실행 실패**: `run.sh`는 `run_detection.sh`에 완전히 위임하지만 해당 파일 내용이 README에 설명되지 않음; `session.log` 첫 번째 실행은 상대 경로(`file://../../...`) 사용으로 실패했으며, 성공한 실행은 다른 비디오 파일(`blackbox-city-road.mp4`)로 진행 — README의 기본 입력(`dogs.mp4`)과 불일치

- **One-sentence verdict**: 파이프라인 자체는 검증되었으나, 머신 특정 절대 경로(tracker config, 모델 경로)가 생성 아티팩트에 남아있어 다른 개발자가 `run.sh`를 그대로 실행하면 tracker 설정 오류나 모델 미발견 문제를 겪을 가능성이 높다.


---

---

---

### R14 opencode-cli dx_stream_cascaded

(CLI invocation failed/skipped)


---

---

---

### R14 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **플래그 불일치**: README는 `--image` / `--video` 플래그를 안내하지만 `run.sh`는 `--input` 플래그를 사용해 그대로 따라 하면 실패 가능성이 있음
  - **setup.sh Python 환경 미구성**: venv 생성이나 `pip install` 없이 모델 다운로드만 시도하며, 모델 다운로드 경로도 `../../..` 하드코딩 깊이에 의존해 세션 디렉토리 위치에 따라 실패할 수 있음
  - **session.log 없음**: 에이전트의 실행 증거가 전혀 없어 아티팩트가 실제로 검증되었는지 확인 불가

- **One-sentence verdict**: Python 의존성 설치 단계 누락, README와 run.sh 간 플래그 불일치, session.log 부재로 인해 사용자가 README만 따라가면 첫 실행에서 오류를 마주칠 가능성이 높다.


---

---

---

### R14 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 별도의 inference runner가 아닌 `verify.py`를 직접 호출함 — "실행(run)"과 "검증(verify)" 역할이 혼용되어 사용자가 혼란을 겪을 수 있음
  - README Quick Start Step 2의 `verify.py` 호출 예시에 `--dxnn yolo26n.dxnn` 플래그가 누락되어 있어 `run.sh` 내부 호출 방식과 불일치
  - `yolo26n.onnx`가 "Generated Files" 테이블에 포함되어 있으나 실제로는 사전에 준비되어야 할 소스 모델임 (사용자가 어디서 구해야 하는지 설명 없음)
- **One-sentence verdict**: SUITE_ROOT 자동 감지 및 venv 구성 등 환경 설정은 잘 갖추어져 있으나, `run.sh`와 README의 `verify.py` 호출 인수 불일치 및 소스 모델(`yolo26n.onnx`) 조달 경로 미설명으로 인해 첫 실행 시 사용자가 오류를 마주칠 가능성이 높다.


---

---

---

### R14 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `run.sh`의 `source setup.sh 2>/dev/null || true` 패턴이 setup 실패를 무시하고 진행 → `dx_engine` 미설치 시 암호적인 Python 오류로 실패
  - README에 `yolo26n.dxnn` 취득 방법 안내 없음 — 모델 파일이 없으면 어디서 구해야 하는지 (컴파일 필요 여부 등) 불명확
  - 검증 단계 부재 — README에 "실행 성공 시 기대 출력" 또는 `verify.py` 언급 없음 (session.log에는 PASS 기록 있으나 사용자에게 노출되지 않음)
- **One-sentence verdict**: 환경이 미리 갖춰진 DEEPX SDK 개발자라면 대체로 실행 가능하나, 모델 파일 부재 시 대처 방법과 무음 오류 억제 패턴으로 인해 신규 사용자는 실패 진단에 어려움을 겪을 수 있다.


---

---

---

### R14 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `../../` 상대 경로가 README 전반에 걸쳐 사용되나, **기준 디렉토리(세션 디렉토리)**를 명시하지 않아 낯선 사용자가 어디서 실행해야 하는지 혼동할 수 있음
  - `run.sh`가 `run_yolo26n.sh`에 위임하면서 MODEL 경로를 전달하지 않음 — `run_yolo26n.sh`의 독립적인 모델 경로 해석 방식이 README에 설명되어 있지 않아, 커스텀 모델 경로(`run.sh [model_path]`) 지정이 실제로 동작하지 않을 수 있음
  - `setup.sh`의 `MODEL_DIR` 경로가 `$DX_STREAM_ROOT/dx_stream/samples/models`로 구성되어 `dx_stream/` 이 이중으로 나타나는데 (`dx-runtime/dx_stream/dx_stream/…`), session.log에서는 실제로 동작하지만 레포 구조를 모르는 사용자에게는 오타처럼 보여 혼란 유발

- **One-sentence verdict**: 실제 실행 증거(session.log)와 다중 실행 모드 문서화 수준은 양호하나, 상대 경로 기준 디렉토리 불명확 및 `run.sh → run_yolo26n.sh` 위임 시 모델 경로 전달 누락으로 인해 익숙하지 않은 사용자가 독립적으로 재현하기에 일부 장벽이 존재함.


---

---

---

### R14 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `setup.sh`를 `2>/dev/null || true`로 호출하여 setup 실패(venv 없음, 모델 미존재 등)를 **조용히 무시**함 — 사용자가 오류 원인을 파악하기 어려움
  - `setup.sh`의 venv fallback(로컬 `.venv` 생성) 경로에서 `pydxs`를 설치하지 않음 — `venv-dx_stream`이 없는 신규 환경에서 `pipeline.py` 실행 시 `ImportError` 발생 가능
  - `run.sh`는 secondary model 경로를 인자로 받지 않아 `run_cascaded.sh` 내부의 하드코딩 값에 의존하므로, 모델 경로를 커스터마이즈하려면 `run_cascaded.sh`를 직접 편집해야 함

- **One-sentence verdict**: 에이전트 실행 환경(dx_stream venv + 모델 사전 설치)에서는 정상 동작이 session.log로 확인되지만, 신규 환경에서는 setup 오류 무시 및 pydxs 미설치로 인해 즉시 실행이 어려울 수 있다.


---

---

---

### R14 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (파일만 존재, 실행 증거 없음)
- **Key issues**:
  - `setup.sh`가 SUITE_ROOT 패턴 없이 하드코딩된 상대 경로(`../../../..`)로 `RUNTIME_DIR`를 계산함 — 디렉토리 깊이 오류 시 모델 다운로드 및 샘플 미디어 경로가 모두 깨짐 (HARD GATE 위반)
  - `session.log`가 존재하지 않음 — 에이전트가 실제 명령을 실행했다는 증거가 없으며, 아티팩트가 실제로 검증되었는지 확인 불가
  - `setup.sh`가 모델 다운로드를 `install.sh --model=` 또는 `dx_app/setup.sh`에 위임하지만 해당 스크립트의 존재 여부를 보장하지 않아 조용히 실패(`|| true`)하고 사용자에게 알리지 않음
- **One-sentence verdict**: README는 명확하지만, 하드코딩 경로 문제·session.log 부재·조용한 모델 다운로드 실패로 인해 처음 실행하는 사용자가 setup.sh 단계에서 막힐 가능성이 높아 **실제 실행 가능성은 불확실**하다.


---

---

---

### R14 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **venv 미활성화 문제**: Quick Start의 `python3 verify.py` 명령이 venv 활성화 없이 실행됨. `setup.sh`는 스크립트 내부에서만 venv를 activate하므로 사용자 셸에는 반영되지 않음. `source venv/bin/activate` 단계가 Quick Start에 누락되어 `onnxruntime`/`dx_engine` import 실패 가능성이 높음.
  - **혼란스러운 FAIL 결과**: README의 Verification Results에서 precompiled reference 모델이 "FAIL"로 표시되어 있음. 설명이 부족해 사용자가 세션 전체가 실패했다고 오해할 수 있음. 생성된 모델(`yolo26n.dxnn`)은 PASS임에도 최종 인상이 불명확함.
  - **`detect_yolo26n.py` 의존성 미설명**: `run.sh`가 호출하는 `detect_yolo26n.py`의 역할이 README에 설명되지 않음. 또한 입력 이미지로 `dx-runtime/dx_app/sample/img/sample_dog.jpg`를 사용하는데, 이 경로가 존재하지 않으면 `run.sh`가 실패함에도 사전 확인 안내가 없음.
- **One-sentence verdict**: `setup.sh`의 SUITE_ROOT 패턴 및 구조는 양호하나, Quick Start에서 venv 활성화 단계 누락으로 일반 사용자가 `verify.py`를 그대로 실행하면 실패할 가능성이 높아 PARTIAL 판정.


---

---

---

### R14 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - README에 **전제조건(prerequisites) 섹션 없음** — `dx_engine` 사용을 위해 `cd dx-runtime/dx_app && ./install.sh && ./build.sh`가 반드시 선행되어야 함을 README에서 안내하지 않음. `setup.sh` 실패 에러 메시지에는 힌트가 있지만 README 상단에 명시해야 함
  - **Direct Run Commands가 venv 활성화 없이 제시** — `bash setup.sh` / `bash run.sh` 경로와 달리 직접 실행 명령은 venv 활성화 없이 `python yolo26n_sync.py ...` 형태로만 제시되어, 복사 후 그대로 실행하면 `ModuleNotFoundError` 발생 가능
  - **검증(verification) 단계 없음** — `session.log`에는 sanity check/import/factory 검사가 실제로 수행되었으나, README에 사용자가 스스로 결과를 확인할 수 있는 verification 명령 또는 `verify.py` 안내가 없음
- **One-sentence verdict**: `setup.sh`/`run.sh` 구조는 견고하고 session.log도 실제 실행 증거가 있으나, README에 전제조건과 검증 단계가 빠져 있어 `dx_app` 빌드 경험이 없는 사용자는 첫 실행에서 막힐 가능성이 높다.


---

---

---

### R14 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (부분적)
- **Key issues**:
  - `run.sh`가 `MODEL_PATH_OVERRIDE` 환경변수를 설정하여 `run_yolo26n_realtime_detection.sh`에 모델 경로를 전달하나, 해당 스크립트가 이 변수를 실제로 읽는지 아티팩트 내에서 확인 불가 — `run.sh`와 `pipeline.py` 사이의 인터페이스가 불투명함
  - `session.log`가 truncated 처리되어 파이프라인 실제 실행 성공 여부를 검증할 수 없음 (artifact validation 및 sanity check 통과는 확인되나, 영상 추론 실행 결과 미제시)
  - README의 Python entrypoint에 `realpath ../../../../workspace/res/models/...` 같은 깊은 상대 경로가 하드코딩되어 있어 세션 디렉토리 위치가 다를 경우 경로 해석 실패 가능
- **One-sentence verdict**: setup.sh의 venv 자동 탐색·모델 폴백 로직은 견고하나, `run.sh → run_yolo26n_realtime_detection.sh` 위임 구조의 모델 경로 전달 방식이 불투명하고 실제 파이프라인 실행 증거가 생략되어 있어 첫 시도 성공을 보장하기 어렵다.


---

---

---

### R14 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `pydxs not found` 오류가 session.log에 기록되어 있어 `pipeline.py --help` 조차 실행 불가 — venv 활성화 없이 실행된 상태이며, README의 venv 경로(`../../venv-dx_stream/bin/activate`)가 실제 존재 여부 미확인
  - session.log의 파일 존재 확인 루프(`for f in ...`)가 빈 문자열(`""`)로 실행되어 모두 `FAIL: missing` 출력 — 검증 스크립트 자체에 버그가 있어 실제 검증 결과를 신뢰할 수 없음
  - `run.sh`이 `run_cascaded.sh`에 위임하지만 README/session.log에 `run_cascaded.sh`의 내용이 포함되지 않아 사용자가 해당 파일 존재 여부 및 인수 순서(`$VIDEO $PRIMARY_MODEL $SECONDARY_MODEL`)를 독립 검증 불가

- **One-sentence verdict**: README 구조와 실행 옵션은 명확하지만, venv 미활성화로 인한 `pydxs` 오류와 검증 스크립트의 치명적 버그로 인해 end-user가 즉시 실행 성공을 확인하기 어렵다.


---

---

---

### R14 codex-cli runtime

- **end-user runnability**: PASS
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README의 `How To Run` 섹션에 `<session_id>` 플레이스홀더가 그대로 남아 있어, 사용자가 실제 디렉토리 이름을 직접 확인해야 함 (예: `20260514-201041_codex_gpt55_yolo26n_inference`)
  - `run.sh`의 기본 모델/이미지 경로가 상대 경로(`../../assets/models/yolo26n.dxnn`)에 의존하므로, 다른 위치에서 실행 시 `[ERROR] Model not found` 발생 가능 — README에 경로 주의사항 미기재
  - `verify.py`가 README의 Generated Files 목록에 없고 실행 방법도 안내되지 않음 (session.log에서 검증 증거는 존재하나 사용자가 재현할 방법 불명확)

- **One-sentence verdict**: session.log에서 inference까지 성공적으로 실행됨이 확인되나, README의 `<session_id>` 미치환과 상대 경로 의존성으로 인해 처음 접하는 사용자는 약간의 혼란을 겪을 수 있다.


---

---

---

### R15 copilot-cli compiler

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 1
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: N
- **Key issues**:
  - **README.md 누락**: 가장 중요한 진입점 문서가 아예 존재하지 않아 사용자가 무엇을 해야 할지 알 방법이 없음
  - **session.log 미완성**: 컴파일 완료 증거(`.dxnn` 파일 생성 확인)가 없고 로그가 중간에 끊겨 있어 `yolo26n.dxnn`이 실제로 생성됐는지 불명확함. `run.sh`가 모델 파일 부재 시 즉시 실패하므로 런타임 오류 가능성 높음
  - **verify.py 미제공**: `run.sh`가 `python3 verify.py`를 호출하지만 해당 파일 내용이 아티팩트에 포함되지 않아 검증 단계 실행 여부 자체를 확인할 수 없음
- **One-sentence verdict**: README.md 전체 누락, 컴파일 완료 미확인, verify.py 부재로 인해 전형적인 사용자가 이 아티팩트를 독립적으로 설치·실행·검증하는 것은 사실상 불가능하다.


---

---

---

### R15 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `setup.sh`이 실제 Python 의존성을 설치하지 않음 — `pip install` 또는 venv 생성 없이 존재 여부만 확인함. 신규 환경에서는 `dx_engine`, `dx_stream` 등의 패키지 없이 바로 실패함. README에 `dx-runtime/dx_app/install.sh && build.sh` 선행 실행 필요성이 명시되어 있지 않음.
  - README에 실행 성공 여부 확인 방법이 없음 — 예상 출력 형식, FPS 범위, detection 결과 예시 등 verification 섹션 전무. 사용자가 실행 결과가 정상인지 판단할 기준 없음.
  - `session.log`의 inference 실행이 session 디렉토리가 아닌 `dx_app` 루트에서 수행된 것으로 보임 (`--image sample_dog.jpg` 경로 미완성) — 실제 사용자가 README 지시대로 session 디렉토리에서 실행 시 재현성 불명확.

- **One-sentence verdict**: 4개 inference variant와 파일 구조 설명은 잘 정리되어 있으나, setup.sh가 의존성 설치를 생략하고 verification 절차가 없어 초기 환경 구성 없이는 독립 실행이 어렵다.


---

---

---

### R15 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`에서 `$MODEL` 인수를 캡처하지만 `run_yolo26n_detection.sh`에 전달하지 않음 — 사용자가 커스텀 모델 경로를 지정해도 무시됨 (`bash "$SCRIPT_DIR/run_yolo26n_detection.sh" "$VIDEO"` 에서 모델 인수 누락)
  - `setup.sh`의 `DX_STREAM_ROOT`가 `../..` 하드코딩으로, README의 일부 예시도 `../../` 상대 경로를 사용 — 세션 디렉토리 깊이가 다른 환경에서 경로 오류 가능성 존재 (SUITE_ROOT 자동 감지 패턴 미사용)
  - README "Option A" 설명이 "Display output (requires X11/Wayland)"이라고 하지만, `session.log`는 `fakesink` (headless) 로 실행된 것을 보여줌 — 실제 동작과 문서 불일치로 사용자 혼란 유발 가능

- **One-sentence verdict**: 파이프라인 자체는 실제 실행이 검증되었으나(`session.log` 확인), `run.sh`에서 모델 경로가 래퍼 스크립트에 전달되지 않는 버그와 하드코딩된 상대 경로로 인해 기본 경로 외 환경에서 실행 실패 위험이 있다.


---

---

---

### R15 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh`의 로컬 venv 생성 경로에서 `pydxs` 미설치 — dx_stream 표준 venv가 없는 환경에서는 `pipeline.py` 실행 시 `ModuleNotFoundError: No module named 'pydxs'` 발생 (로컬 venv에 설치 로직 없음)
  - `run.sh`의 인자 순서(`$1` = model path, `$2` = video path)가 README의 `run_cascaded.sh` 직접 호출 예시(`bash run_cascaded.sh [video]`)와 일치하지 않아 사용자 혼란 가능
  - `source "$SCRIPT_DIR/setup.sh" 2>/dev/null || true` 패턴으로 venv 활성화 실패가 무음으로 무시됨 — 진단 메시지 없이 `pydxs` import 오류로 실패할 수 있음

- **One-sentence verdict**: session.log에서 실제 파이프라인 실행 성공이 확인되나, 표준 dx_stream venv가 없는 환경에서는 pydxs 미설치와 run.sh 인자 불일치로 인해 첫 실행에 실패할 가능성이 높다.


---

---

---

### R15 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - **session.log 없음**: 실제 실행 증거가 전혀 없음. 아티팩트가 실제로 동작했는지 확인 불가 — 세션 실패의 핵심 지표
  - **setup.sh가 환경을 실제로 구성하지 않음**: venv 생성 및 pip 의존성 설치(dx_engine, numpy 등) 없이 파일 존재 여부만 확인함. 사용자가 `./install.sh && ./build.sh`를 별도로 실행해야 하는데 README의 Prerequisites 안내가 세션 디렉터리 기준으로 모호함 (`cd ../../..` 경로 혼란)
  - **Python 환경 가정 미명시**: run.sh가 venv 활성화 없이 `python` 직접 호출 — dx_engine이 시스템 Python에 없으면 즉시 실패하나 README에 이 전제조건이 명확히 기술되지 않음

- **One-sentence verdict**: run.sh/README의 실행 명령 구조는 양호하나, session.log 부재와 setup.sh의 환경 구성 누락으로 인해 처음 사용하는 개발자가 독립적으로 실행하기 어렵다.


---

---

---

### R15 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh`에서 sanity_check 출력을 `2>/dev/null`으로 숨기고 exit code만으로 PASS/FAIL 판정 — 규칙상 exit code는 신뢰할 수 없으며 텍스트 출력으로 판단해야 함 (HARD GATE 위반)
  - `run.sh`이 `verify.py`만 실행하며 실제 커스텀 이미지 추론 방법이 README Quick Start에 명시되지 않음 — 신규 사용자가 "어떻게 내 이미지로 추론하나?"를 알 방법 없음
  - `calibration_dataset`이 `../../dx_com/calibration_dataset` 상대 심링크로 되어 있어, 해당 경로가 없는 환경(다른 머신, fresh checkout)에서 broken symlink가 될 수 있음

- **One-sentence verdict**: Quick Start 2단계 구조와 SUITE_ROOT 자동 감지 등 전반적인 완성도는 양호하나, sanity_check 출력 숨김·커스텀 이미지 추론 경로 미제공·심링크 의존성의 세 가지 문제로 인해 PASS 수준에는 미치지 못한다.


---

---

---

### R15 opencode-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - `../../assets/models/yolo26n.dxnn` 등 상대 경로가 세션 디렉터리 기준임을 README에서 명시하지 않아, 다른 위치에서 개별 명령어를 실행하면 경로 오류 발생 가능
  - `session.log`가 `tee` 캡처 형식이 아닌 섹션 헤더 구조(`=== TDD Validation Results ===`)로 작성되어 있어, 실제 터미널 출력 여부를 단독으로 확인하기 어려움 (FPS 수치는 실행 증거로 충분)
  - README Quick Start의 개별 실행 예시에서 venv 활성화 단계가 누락되어 있음 (`bash setup.sh` 실행 후 venv가 현재 셸에 적용되지 않은 상태에서 개별 `python` 명령 실행 시 실패 가능)
- **One-sentence verdict**: 4개 variant 전부 실제 FPS 수치로 검증된 견고한 아티팩트로, 일반 DEEPX 개발자가 `bash setup.sh && bash run.sh` 두 명령만으로 성공적으로 실행할 수 있다.


---

---

---

### R15 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **트래커 설정 절대 경로 하드코딩**: `session.log`에서 `pipeline.py`가 빌드 머신 고유의 절대 경로(`/data/home/dhyang/.../tracker_config.json`)를 사용하는 것이 확인됨. 다른 사용자 환경에서는 이 경로가 존재하지 않아 파이프라인 실행이 즉시 실패함. `run.sh` / `run_detection.sh`에 이에 대한 설명이나 재정의 방법이 없음.
  - **`../../` 상대 경로 의존성**: README, `setup.sh`, `run.sh` 모두 세션 디렉터리가 `dx_stream` 루트에서 정확히 2단계 아래에 있다고 가정함. 사용자가 다른 위치에서 실행하거나 디렉터리를 복사하면 경로 탐색 전체가 실패함 (SUITE_ROOT 패턴 미적용).
  - **모델 경로 불일치**: `setup.sh`는 모델을 `dx_stream/samples/models/`에 다운로드하지만, `session.log`의 실제 실행은 `/workspace/res/models/models-2_3_0/yolo26n.dxnn`을 사용함. 즉, 새 사용자가 `setup.sh`를 실행해도 `run.sh`가 가리키는 모델 위치와 다를 수 있음.

- **One-sentence verdict**: 파이프라인 자체는 빌드 머신에서 동작이 확인됐으나, 트래커 설정 절대 경로 하드코딩과 `../../` 상대 경로 의존성으로 인해 새 사용자가 README만 따라서 동일하게 실행하기 어렵다.


---

---

---

### R15 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`run_cascaded.sh` 경로 불일치**: `run.sh`은 `dx_stream/samples/models/`에서 모델을 찾지만, `session.log`의 실제 실행 기록을 보면 모델 경로가 `/workspace/res/models/models-2_3_0/`로 하드코딩되어 있음. `run_cascaded.sh` 파일(README에 핵심 파일로 명시되어 있으나 내용 미제공)이 개발자 환경의 절대 경로를 포함할 가능성이 높아, 다른 사용자 환경에서 즉시 실패함
  - **`setup.sh`의 `SRC_DIR` 경로 이중 중첩**: `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"`로 계산 후 `SRC_DIR="$DX_STREAM_ROOT/dx_stream"`을 설정 → 실질적으로 `dx-runtime/dx_stream/dx_stream/samples/models/`를 모델 경로로 사용. 이는 `session.log`에서 확인된 실제 실행 경로(`workspace/res/models/`)와 완전히 다름
  - **`../../` 상대 경로 컨텍스트 누락**: README의 여러 명령어(예: `cd ../../ && ./install.sh`, `source ../../venv-dx_stream/bin/activate`)에서 기준 디렉터리가 세션 폴더(`dx-agentic-dev/<session>/`)임을 명시하지 않아, 경험이 부족한 사용자가 혼동할 수 있음

- **One-sentence verdict**: README 구조와 setup.sh 로직은 양호하나, 실제 실행을 담당하는 `run_cascaded.sh`가 개발자 머신의 절대 경로에 의존하는 것으로 추정되어 타 환경에서의 즉시 실행은 불가능함.


---

---

---

### R15 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y (verify.py 언급만, 실행 증거 없음)
- **Key issues**:
  - **CLI 플래그 불일치**: README Quick Start는 `--image` / `--video`를 사용하지만 `run.sh`는 `--input`을 사용 — 사용자가 README를 따라 입력하면 argparse 오류 발생 가능
  - **venv / 의존성 설치 부재**: `setup.sh`에 `python -m venv`, `pip install` 단계가 없음. `dx_engine`, `numpy` 등 런타임 의존성 설치 방법이 README와 setup.sh 어디에도 명시되지 않아, 깨끗한 환경에서 바로 실행 불가
  - **session.log 없음 + 모델 경로 플레이스홀더**: 실제 실행 증거가 전혀 없고, README Quick Start Step 2가 `/path/to/yolo26n.dxnn`을 그대로 사용 — 사용자가 `setup.sh` 실행 후 실제 경로를 어떻게 알아내야 하는지 안내가 빠져 있음

- **One-sentence verdict**: venv 설치 단계 누락과 CLI 플래그 불일치, 실행 로그 부재로 인해 SDK에 익숙하지 않은 사용자가 `bash setup.sh && run.sh` 만으로 첫 실행을 성공시키기 어렵다.


---

---

---

### R15 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `setup.sh`가 `dx-runtime/venv-dx-runtime/` 경로의 runtime venv 존재를 암묵적으로 전제함 — 해당 venv가 빌드되지 않은 환경에서는 `.pth` 주입 단계(`python3 -c "import dx_engine"`)가 실패하며 사용자에게 명확한 복구 지침이 없음
  - `sanity_check.sh`를 `|| true`로 실행하여 NPU 초기화 실패를 무시함 — setup 단계는 통과하지만 이후 `verify.py`가 DXNN 추론 시 조용히 실패할 수 있음
  - `session.log`가 `dx_com.compile` 진행 중 잘려 있어 `yolo26n.dxnn` 생성 성공 여부가 확인되지 않음 — README가 해당 파일을 필수 artifact로 나열하지만 컴파일 완료 증거가 없음
- **One-sentence verdict**: Quick Start 흐름과 SUITE_ROOT 패턴은 올바르나, dx-runtime venv 미빌드 환경과 컴파일 완료 미확인 문제로 인해 새로운 사용자가 그대로 실행했을 때 `verify.py` 단계에서 실패할 가능성이 높다.


---

---

---

### R15 cursor-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - Quick start 첫 줄 `cd "$(dirname "$0")"` 는 스크립트 내부 관용구로, 터미널에서 직접 실행하면 현재 디렉토리를 변경하지 않음. 사용자는 세션 디렉토리로 이동하는 방법을 별도로 파악해야 함
  - README의 verify.py 호출(`source venv/bin/activate && python verify.py`) 시 필요한 PYTHONPATH(`DX_APP_ROOT/src/python_example`, 세션 내 `src/python_example`)가 설정되지 않아 session.log와 동일한 `ModuleNotFoundError: No module named 'common'` 재현 가능성이 높음. 해당 PYTHONPATH는 run.sh 안에서만 설정됨
  - session.log에서 verify.py가 첫 실행 시 `RESULT: FAIL`, 재시도 시 `RESULT: PASS`로 전환됐으나 수정 내용이 기록되지 않아, 현재 아티팩트 상태에서 PASS가 재현 가능한지 불명확

- **One-sentence verdict**: setup.sh와 run.sh의 완성도는 높으나, README Quick Start의 `verify.py` 실행 절차에 PYTHONPATH 누락 문제가 있고 session.log의 초기 FAIL→PASS 전환이 설명 없이 처리되어 사용자가 README만 따라갈 경우 검증 단계에서 실패할 가능성이 있음.


---

---

---

### R15 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`의 경로 계산이 `$SCRIPT_DIR/../..`에 의존하는데, 실제 디렉토리 구조가 `dx-runtime/dx_stream/dx-agentic-dev/<session>/`임을 README가 명시하지 않아 경로 오류 위험 있음
  - `setup.sh`의 모델 다운로드 fallback이 `DX_STREAM_ROOT/setup.sh`를 호출하지만, 해당 스크립트의 존재·사용법을 사전에 확인하지 않아 사일런트 실패(`[WARN] Model download failed`)로 처리됨 — 사용자는 수동 다운로드 방법을 모름
  - `--postprocess-lib` 인자가 필수(required)임에도 `run.sh` 및 `run_yolo26n_realtime_detection.sh` 래퍼가 해당 값을 어떻게 결정하는지 README에 설명 없음

- **One-sentence verdict**: Quick start(`bash run.sh`)는 dx_stream 빌드 환경이 정상일 때 동작 가능하지만, 모델 경로 미존재·postprocess-lib 자동 해결 방식 미설명으로 인해 처음 사용하는 개발자에게는 PARTIAL 수준의 실행 가능성을 제공한다.


---

---

---

### R15 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - **"How to Run" 섹션이 혼란스러움**: `bash setup.sh` → `bash run.sh` → `bash run_cascaded.sh` → `python3 pipeline.py ...` 네 가지 명령이 나열되어 있어, 어느 것이 실제 진입점인지 불명확함. `run.sh`가 `setup.sh + run_cascaded.sh`를 모두 호출하는데, README가 이를 명시적으로 안내하지 않음.
  - **`run_cascaded.sh` 미포함**: `run.sh`가 내부적으로 `run_cascaded.sh`에 위임하지만, artifacts 목록에 `run_cascaded.sh` 내용이 제공되지 않아 사용자가 스크립트 존재 여부와 동작을 확인할 수 없음.
  - **전제 조건 진입 장벽**: NPU, GStreamer 플러그인(`dxinfer`), 두 개의 postprocess `.so` 라이브러리, pydxs venv 등 다수의 외부 의존성이 필요하나, 이를 충족하지 않을 때의 복구 절차(`./install.sh && ./build.sh`)가 README에만 간략히 언급되고 실제 오류 처리는 setup.sh의 `[WARN]` 수준에 그침.
- **One-sentence verdict**: session.log에서 실제 파이프라인 실행이 검증되었고 setup.sh/run.sh 구조는 견고하나, README의 복수 실행 명령 나열과 `run_cascaded.sh` 미노출로 인해 처음 접하는 사용자가 올바른 진입점을 즉시 파악하기 어렵다.


---

---

---

### R15 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README 빠른 시작 커맨드에 `yolo26n.onnx` 사전 존재 여부에 대한 안내가 없음 — 파일이 없으면 compile.py가 실패하지만 사용자는 원인을 알 수 없음
  - `calibration_dataset` 심볼릭 링크에 대한 설명이 "dx-compiler/dx_com/calibration_dataset를 가리킨다"는 한 줄뿐이며, 링크가 실제로 존재하는지 확인하거나 생성하는 단계가 없음
  - 빠른 시작의 `bash run.sh 2>&1 | tee session.log` 명령이 기존 실행 증거 파일(`session.log`)을 덮어씀 — 아티팩트 보존 측면에서 의도치 않은 부작용
- **One-sentence verdict**: setup.sh/run.sh 품질은 양호하고 session.log는 실제 실행 증거를 담고 있으나, README에 ONNX 파일 및 calibration_dataset 심볼릭 링크 사전 조건이 명시되지 않아 초면 사용자가 첫 실행에 실패할 가능성이 있다.


---

---

---

### R15 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **Python 버전 하드코딩**: `setup.sh`에서 site-packages 경로를 `python3.12`로 고정 (`"${RUNTIME_DIR}/venv-dx-runtime/lib/python3.12/site-packages"`) — Python 3.10/3.11/3.13 환경에서 `.pth` 링크가 조용히 실패함
  - **`run.sh`가 inference가 아닌 `verify.py`만 실행**: 사용자가 "run the compiled model"을 기대하지만 `run.sh`는 `python verify.py` 한 줄만 호출 — 컴파일된 DXNN 모델을 실제 이미지로 추론하는 데모가 없음
  - **`session.log` 중간 잘림 + `yolo26n.dxnn` 생성 증거 없음**: 로그가 `calibration_dataset` 심볼릭 링크 단계에서 truncate되어 컴파일 완료(`yolo26n.dxnn` 생성)와 `verify.py` 실행 결과가 모두 누락됨
- **One-sentence verdict**: ONNX export까지의 흐름은 정상이나, Python 버전 하드코딩으로 인한 venv 연결 불안정성과 `run.sh`가 실질적인 inference 데모 없이 verify만 수행하는 구조, 그리고 컴파일 완료 증거 미제공으로 인해 일반 사용자가 end-to-end로 재현하기에는 불충분하다.


---

---

---

### R15 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log`에 실제 추론 실행(`python yolo26n_sync.py --model ... --image ...`) 결과가 없음 — syntax/import 검증만 수행되었고 end-to-end inference 성공 증거가 없음
  - `sanity_check` 단계가 상대경로 오류(`../../scripts/sanity_check.sh: No such file or directory`)로 FAIL — README에는 이 전제조건 실패에 대한 안내가 없음
  - README에 `dx_engine`/`venv-dx-runtime` 사전 필요 조건 명시 없음 — 로컬 venv를 새로 생성한 경우 `setup.sh`가 FATAL로 종료되는 상황을 사용자가 예측하기 어려움
- **One-sentence verdict**: 아티팩트 구조(SUITE_ROOT 탐지, venv 폴백, IFactory 5-method 등)는 양호하나, 실제 추론 실행 증거가 없고 `dx_engine` 전제조건이 README에 누락되어 있어 첫 사용자가 막힘 없이 실행하기까지 추가 조치가 필요하다.


---

---

---

### R15 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **핵심 실행 파일 `run_cascaded.sh` 내용 미제공**: README와 run.sh 모두 이 스크립트를 메인 실행 진입점으로 위임하지만, 아티팩트에 내용이 없고 session.log도 `bash -n`(문법 검사)만 수행했을 뿐 실제 실행 증거가 없음. 사용자가 이 파일이 실제로 동작하는지 확인할 방법이 없음.
  - **`SRC_DIR` 경로 이중 중첩 의심**: `setup.sh`에서 `DX_STREAM_ROOT="$SCRIPT_DIR/../.."` (= `dx_stream/`)로 설정 후 `SRC_DIR="$DX_STREAM_ROOT/dx_stream"` (= `dx_stream/dx_stream/`)를 구성함. 이 경로가 실제로 존재하지 않으면 모델 경로(`$SRC_DIR/samples/models/`)와 동영상 경로(`$SRC_DIR/samples/videos/`)가 전부 깨짐. `bash setup.sh`를 실제 실행한 증거도 없어 런타임에서 검증되지 않음.
  - **모델 다운로드 의존성 불투명**: README 사전 조건 섹션에서 `cd ../../ && ./setup.sh --model="yolo26n.dxnn"` 형태의 외부 스크립트를 호출하는데, 이 최상위 `setup.sh`가 해당 `--model` 플래그를 지원하는지 본 세션 아티팩트 내에서 확인 불가. 모델 없이는 파이프라인을 실행할 수 없음.

- **One-sentence verdict**: pipeline.py의 문법 검증과 `--help` 출력은 확인되었으나, 핵심 실행 진입점인 `run_cascaded.sh`의 실제 동작 증거와 모델 경로의 정상 해석 여부가 불분명하여 사용자가 README만 따라도 실행에 성공할 보장이 없다.


---

---

---

### R15 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

**Key issues**:
- **Prerequisites 지시가 불명확** — `dxrt-cli -s` 및 `cd ../../ && ./install.sh && ./build.sh` 명령이 Quick Start 전에 반드시 수행해야 하는지, 아니면 확인용인지 설명 없음. `dx_engine` import 실패 시 `setup.sh`가 `[FATAL]`로 종료되는데, 이 경우 사용자가 취해야 할 조치가 README에 없음.
- **실제 실행(E2E) 검증 없음** — `session.log`는 구문 검사(`py_compile`, `bash -n`)와 JSON 유효성 검증만 수행. `python yolo26n_sync.py`를 실제 모델로 실행한 출력이 없어, 런타임 정상 동작 여부를 확인할 수 없음.
- **상대 경로 의존성 노출** — `run.sh`의 `DEFAULT_MODEL`/`DEFAULT_IMAGE`가 `../../assets/models/` 등 하드코딩된 상대 경로를 사용하며, README에도 동일하게 기재됨. 세션 디렉터리 위치가 달라지면 경로가 깨짐 (SUITE_ROOT 패턴 미적용).

**One-sentence verdict**: 구문 검증과 스크립트 구조는 잘 갖춰져 있으나, `dx_engine` 빌드 선행 조건 안내 부재 및 실제 실행 증거 없음으로 인해 처음 접하는 사용자가 독립적으로 실행하기에는 불완전하다.


---

---

---

### R15 claude-code compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **README PASS 주장 vs session.log 불일치**: session.log 마지막 가시적 실행 결과는 `RESULT: FAIL — Output mismatch`(Top-10 avg IoU=0.000)이며, 그 이후가 `[truncated]`로 잘려 있음. README에서 `RESULT: PASS (IoU=0.974)`라고 선언하나, 제공된 session.log에서 최종 PASS 실행 근거가 보이지 않아 검증 신뢰도에 의문이 생김.
  - **`run.sh`가 추론 데모가 아닌 `verify.py`를 실행**: `run.sh`의 목적은 inference 결과를 보여주는 것이어야 하나, 실제로는 `python verify.py --dxnn ... --image ...`를 호출함. end-user는 ONNX 비교 리포트 대신 순수 추론 결과물(시각화 등)을 기대할 수 있음.
  - **`pip install torch` 포함**: `setup.sh`에서 `torch`를 설치하나 `verify.py`에는 PyTorch가 필요하지 않을 가능성이 높음. 불필요한 대용량 의존성(~2GB)으로 setup 시간이 크게 늘어남.

- **One-sentence verdict**: SUITE_ROOT 자동 탐지, venv 생성, config 구조 등 인프라 품질은 우수하나, session.log에서 최종 PASS 실행 근거가 잘려 확인 불가하여 README 검증 결과를 신뢰하기 어렵고, run.sh가 독립 추론 데모 대신 비교 스크립트를 그대로 호출하는 점이 end-user 실행성을 PARTIAL로 제한함.


---

---

---

### R15 claude-code dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **README ↔ run.sh 인자 불일치**: README는 `bash run.sh --image /path/to/image.jpg`로 안내하지만, run.sh는 `--image` 플래그를 파싱하지 않고 positional `$1`을 INPUT으로 사용함 → 사용자가 README를 그대로 따르면 `--image` 문자열이 모델 경로로 전달되어 오류 발생
  - **dx_app site-packages 주입 로직이 불안정**: `setup.sh` Step 4에서 `.pth` 파일 → `dx_engine*.so` 디렉토리 순으로 탐색 후 venv에 경로를 주입하는데, 경로를 찾지 못해도 경고 없이 조용히 스킵됨 → `dx_engine` import 실패 시 원인 파악이 어려움
  - **실제 추론 실행 증거 없음**: session.log에 TDD 문법 검사 및 `--help` 출력은 있지만, 실제 이미지에 대한 추론 실행 및 detection 결과가 없어 end-to-end 동작이 검증되지 않았음; 필수 `sanity_check.sh` 호출도 setup.sh에서 누락됨

- **One-sentence verdict**: README와 run.sh 간 인자 형식 불일치로 인해 README를 그대로 따른 사용자는 즉시 오류에 직면하며, 실제 추론 검증 증거도 없어 "동작 확인된 아티팩트"로 보기 어렵다.


---

---

---

### R15 claude-code dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`run.sh` 모델 인수 전달 버그**: `run.sh`는 `$MODEL` 인수를 검증하지만 `run_detection.sh "$VIDEO"`만 호출하여 모델 경로를 전달하지 않는다. 사용자가 커스텀 모델 경로를 지정해도 무시됨.
  - **Local venv fallback에서 `pydxs` 미설치**: 기존 `venv-dx_stream`을 찾지 못할 경우 `setup.sh`가 새 `.venv`를 생성하지만 `pydxs`를 설치하지 않아 `pipeline.py` 실행 즉시 실패. `pydxs`는 로컬 패키지라 `pip install`도 불가.
  - **session.log와 run.sh 기본 경로 불일치**: 실제 실행 시 사용된 모델/비디오 경로가 `workspace/res/...`인 반면, `run.sh`의 기본 경로는 `dx_stream/samples/...`으로 다르다. 신규 사용자 환경에서 기본값으로 실행 시 모델을 찾지 못할 가능성이 높음.

- **One-sentence verdict**: `venv-dx_stream`이 이미 존재하고 모델 파일 위치를 명시적으로 지정하는 숙련된 사용자라면 실행 가능하지만, 기본값만 따르는 일반 사용자는 경로 불일치와 `pydxs` 미설치 문제로 실행에 실패할 가능성이 높다.


---

---

---

### R15 claude-code dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - `run_cascaded.sh`의 내용이 평가 artifacts에 포함되지 않아 블랙박스 상태; `run.sh`가 이 파일에 위임하므로 파일 누락 시 즉시 실패함 (session.log가 실제 실행을 확인해 다소 완화됨)
  - `dx_stream/dx_stream/` 이중 경로 패턴(e.g. `../../dx_stream/samples/models/`)이 README와 setup.sh 전반에 걸쳐 나타나며, `dx-runtime/dx_stream/` 루트 아래 `dx_stream/` 서브디렉터리가 중첩된 구조를 처음 보는 사용자에게 혼란을 줄 수 있음
  - Option C Python 명령어의 인라인 `$(cd ../.. && pwd)` 표현식은 세션 디렉터리 외부에서 실행 시 잘못된 경로를 생성할 수 있어 copy-paste 실수 위험 존재

- **One-sentence verdict**: session.log가 실제 GStreamer cascaded 파이프라인의 end-to-end 실행을 명확히 증명하고 있어 전반적인 완성도는 높으나, `run_cascaded.sh` 미제공 및 `dx_stream/dx_stream/` 중첩 경로 패턴이 초심자에게 경미한 혼란을 줄 수 있다.


---

---

---

### R15 claude-code runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh`가 `dx_engine`의 존재만 확인하고 설치는 하지 않음 — 실패 시 `./install.sh && ./build.sh` 실행 안내 메시지만 출력하고 종료하므로, 신규 환경에서는 수동 개입이 필요함
  - README에 사전 조건(dx_engine 빌드 완료 여부, 지원 OS/하드웨어)이 명시되지 않아 첫 실행 시 실패 원인을 파악하기 어려움
  - `setup.sh`의 모델 다운로드 경로(`$DX_APP_DIR/../setup.sh`)가 존재 및 `--model` 플래그 지원 여부를 README에서 전혀 설명하지 않아, 해당 스크립트가 없는 환경에서 오류 원인 추적이 곤란함

- **One-sentence verdict**: 환경(dx_engine, suite 구조)이 이미 준비된 개발자라면 두 커맨드로 즉시 실행 가능하지만, 사전 조건 미설명으로 인해 클린 환경에서의 독립 실행은 어렵다.


---

---

---

### R16 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh`의 `pip install dx-com`은 DEEPX 사내 패키지로, 공개 PyPI에 없을 가능성이 높음. 엔드유저 환경에서 설치 실패 시 전체 플로우가 중단되며, 실패 시 대체 설치 경로(로컬 휠, 사내 레지스트리)에 대한 안내가 없음.
  - session.log에는 `"No Data Loader is specified. Use Dummy Dataloader"` 경고가 있지만, README에는 **"EMA calibration, 100 samples"** 로 기록되어 있어 calibration 품질에 대한 정보가 불일치함. 실제로는 더미 데이터로 컴파일된 것으로 보임.
  - `yolo26n.onnx` 입력 모델의 입수 방법(소스 경로, 다운로드 링크 등)이 README에 기재되지 않아, 세션 디렉터리에 파일이 없는 경우 `run.sh` 실행 전 준비 단계가 불명확함.

- **One-sentence verdict**: `setup.sh` 자체의 구조와 `run.sh` 흐름은 깔끔하나, 사내 패키지 설치 경로 미안내와 calibration 메타데이터 불일치로 인해 외부 개발자가 처음부터 독립 실행하기에는 추가 조치가 필요한 **PARTIAL** 수준임.


---

---

---

### R16 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 실제로 명령을 실행하지 않고 `echo`로 출력만 함 — "one-command runner"가 아니라 도움말 스크립트에 불과하며, 사용자가 명령을 수동으로 복사·실행해야 함
  - `setup.sh`에 Python 환경 설정(venv 생성, pip install)이 없음 — 모델 파일 다운로드만 처리하며, 새 환경의 사용자는 `dx_engine`, `numpy` 등 의존성 오류를 겪을 수 있음
  - README의 Prerequisites 섹션에 `<dx_app_root>` 플레이스홀더가 그대로 남아 있어 실제 경로를 모르는 사용자에게 혼란을 줌 (Usage 섹션은 실제 경로를 올바르게 사용)
- **One-sentence verdict**: 프레임워크 검증(11/11 PASS)과 cross-validation 실행 증거는 충실하지만, `run.sh`가 명령을 실행하지 않고 출력만 하며 Python 환경 설정이 누락되어 있어 새 사용자가 즉시 실행하기 어렵다.


---

---

---

### R16 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **모델 경로 불일치**: `run.sh`의 기본 경로는 `dx_stream/dx_stream/samples/models/yolo26n.dxnn`를 가리키지만, `session.log`의 실제 실행에서는 `/workspace/res/models/models-2_3_0/yolo26n.dxnn`을 사용했음. 새 사용자가 `run.sh`를 그대로 실행하면 `[ERROR] Model not found` 오류 발생 가능성 높음.
  - **`run_yolo26n_detection.sh` 미제공**: `run.sh`가 내부적으로 `run_yolo26n_detection.sh`를 호출하지만 해당 파일의 내용은 제공되지 않았고, `setup.sh`의 venv 폴백(로컬 `.venv` 생성)이 `pydxs`를 설치하지 않아 `pipeline.py` 실행 시 `ImportError` 발생 가능.
  - **README의 `../../` 기준 경로 모호함**: "Navigate to dx_stream root"라는 설명이 사용자가 세션 디렉토리 기준임을 명시하지 않아 처음 사용자에게 혼란 유발 가능.

- **One-sentence verdict**: 파이프라인 실행 자체는 검증되었으나(`session.log` 실증), 모델 경로 불일치와 핵심 런처 스크립트(`run_yolo26n_detection.sh`) 내용 부재로 인해 README만 보고 처음부터 실행하는 사용자는 중간에 막힐 가능성이 있음.


---

---

---

### R16 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`run.sh`가 setup.sh 오류를 무시함** — `source "$SCRIPT_DIR/setup.sh" 2>/dev/null || true` 패턴으로 venv 활성화·플러그인 확인 실패가 조용히 묻힌다. 환경이 깨져도 파이프라인 실행을 시도하므로 원인 불명의 오류가 발생할 수 있음.
  - **상대 경로(`../../`) 사용 — SUITE_ROOT 패턴 미적용** — README의 `cd ../../`, setup.sh·run.sh의 `$(cd "$SCRIPT_DIR/../.." && pwd)` 모두 디렉터리 깊이를 하드코딩함. 세션 디렉터리가 다른 위치에 복사되면 즉시 경로가 깨짐 (HARD GATE 위반).
  - **`run.sh`가 secondary 모델 경로를 `run_cascaded.sh`에 전달하지 않음** — `bash "$SCRIPT_DIR/run_cascaded.sh" "$VIDEO"`만 호출하며 secondary 모델 인자를 누락. `run_cascaded.sh` 내부에 경로가 하드코딩되어 있어야만 동작하므로 사용자가 모델 경로를 커스터마이즈할 때 진입점(run.sh)에서 설정이 적용되지 않음.

- **One-sentence verdict**: session.log에서 실제 파이프라인 실행(End of stream)이 확인되어 핵심 기능은 동작했지만, 상대 경로 하드코딩·setup 오류 묵살·secondary 모델 경로 누락으로 인해 다른 환경에서 첫 실행 성공률이 낮다.


---

---

---

### R16 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **`session.log` 없음 (MANDATORY 미충족)**: 실행 증거가 전혀 없어 에이전트가 실제로 코드를 검증했는지 확인 불가. Framework 규칙상 `session.log`는 항상 필수이며 실제 커맨드 출력이어야 함.
  - **`run.sh`에 PYTHONPATH 미설정**: `setup.sh`의 `sys.path.insert` 는 해당 셸에만 적용되고 `run.sh` 실행 시에는 전달되지 않음. `yolo26n_sync.py` 등 실행 시 `common.runner` ImportError 발생 가능성 높음.
  - **모델 부재 시 setup.sh가 WARNING만 출력하고 계속 진행**: `yolo26n.dxnn`이 없어도 setup이 성공(`exit 0`)으로 끝나, 사용자가 실제 런타임 실패 원인을 사전에 인지하지 못할 수 있음.

- **One-sentence verdict**: `session.log` 누락으로 실행 검증 근거가 없고 `run.sh`의 PYTHONPATH 전파 누락으로 실제 실행 시 ImportError가 발생할 가능성이 높아, 현재 상태로는 엔드유저가 독립적으로 성공적인 실행까지 도달하기 어렵다.


---

---

---

### R16 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 2
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 `verify.py`만 실행함 — "Quick start: `bash run.sh`"라고 안내하지만 실제로는 검증 스크립트만 돌아가며, 추론 데모 없음. Compiler-only 세션이지만 README에 이 사실이 명시되지 않아 혼동 유발
  - `verify.py`가 `sample_dog.jpg`를 사용하는 것으로 보이나, README에 해당 이미지의 출처(suite 경로) 또는 사용자가 준비해야 하는지 여부가 전혀 언급되지 않음
  - README에 사전 요구사항(Python 버전, OS, `yolo26n.onnx`/`yolo26n.dxnn` 존재 여부 확인)이 없고, `torch`/`torchvision` 대용량 패키지 설치에 대한 경고도 없음
- **One-sentence verdict**: `setup.sh`와 `verify.py` 연동은 견고하게 작성되었으나, README가 지나치게 단편적이고 `run.sh = verify.py`임을 명시하지 않아 일반 사용자가 "실행 결과"를 오해할 가능성이 높다.


---

---

---

### R16 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh`가 내부에서 `setup.sh`를 매번 `source`하므로 실행할 때마다 pip install이 재수행됨 — 기능상 문제는 없으나 체감 속도 저하 유발
  - `verify.py` 없음 — 컴파일 단계가 없는 app-only 세션이므로 필수는 아니지만, README에 "추론 성공 여부 확인 방법"이 명시되어 있지 않아 최초 실행 후 결과 해석이 모호할 수 있음
  - README의 Prerequisites 항목이 `dx_engine` 빌드 방법만 안내하고, `yolo26n.dxnn` 모델 파일이 이미 존재해야 한다는 전제를 명시하지 않음 (모델 파일 부재 시 `run.sh`가 `[ERROR] Model not found` 로 실패하며, 사용자는 어디서 모델을 구해야 하는지 알 수 없음)

- **One-sentence verdict**: setup → run 흐름이 명확하고 session.log에 실제 실행 증거가 포함되어 있어 동일 환경(venv-dx-runtime + yolo26n.dxnn 존재)에서는 즉시 재현 가능하나, 모델 파일 조달 경로 미기재로 인해 클린 환경의 사용자는 첫 실행에서 막힐 수 있다.


---

---

---

### R16 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **모델 경로 불일치**: `setup.sh`은 `$DX_STREAM_ROOT/dx_stream/samples/models/yolo26n.dxnn`를 확인하지만, `session.log`의 실제 파이프라인 실행 시에는 `/workspace/res/models/models-2_3_0/yolo26n.dxnn`을 사용했다. `setup.sh`에서 `[OK] Model` 출력이 나와도 `pipeline.py`가 다른 경로를 참조할 수 있어 end-user가 혼란을 겪을 수 있음.
  - **`run_yolo26n_realtime.sh` 미제공**: `run.sh`이 `exec bash "$SCRIPT_DIR/run_yolo26n_realtime.sh"`를 호출하고 README 파일 목록에도 기재되어 있으나, 평가 대상 artifacts에는 해당 파일 내용이 포함되지 않아 핵심 실행 스크립트의 검증이 불가능함.
  - **`../..` 하드코딩**: `setup.sh`의 `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"`는 session 디렉터리가 `dx_stream/dx-agentic-dev/<session>/` 2단계 하위에 위치한다는 가정에 의존하므로, 다른 구조의 환경에서는 경로 오류가 발생할 수 있음. (SUITE_ROOT 패턴 미적용)

- **One-sentence verdict**: README와 setup.sh의 구조는 전반적으로 명확하나, 실제 파이프라인이 사용한 모델 경로와 setup.sh이 검증하는 경로가 달라 end-user가 정상 설정 후에도 파이프라인이 다른 경로를 참조할 위험이 있어 PARTIAL 판정.


---

---

---

### R16 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `session.log`가 truncated 상태로 제공됨 — 파이프라인 문자열 구성은 확인되나 실제 실행 완료 및 inference 결과는 확인 불가
  - `run_cascaded.sh` 내용이 제공된 artifacts에 포함되지 않아 검토자(및 사용자)가 실제 실행 흐름을 독립적으로 검증할 수 없음; `run.sh`는 단순 위임(delegate)만 수행
  - `setup.sh`가 `./setup.sh --model=yolo26n.dxnn` 형태로 dx_stream 루트의 setup.sh를 호출하나, 해당 플래그 문법이 dx_stream 공식 setup.sh에서 지원되는지 README에 명시 없음 (session.log 기준으로는 동작 확인됨)
- **One-sentence verdict**: setup.sh와 모델 다운로드는 정상 동작이 session.log로 확인되지만, 핵심 실행 스크립트인 `run_cascaded.sh`의 내용이 비공개이고 로그가 truncated되어 end-user가 완전한 실행 흐름을 독립적으로 추적·검증하기 어렵다.


---

---

---

### R16 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **dx_com 링킹이 취약** — `setup.sh`가 3회 실행을 거쳐야 성공했으며, 최종적으로 링크된 경로가 테스트 하네스 내부 venv (`/.deepx/tests/venv/…`)임. 다른 사용자 환경에서는 이 경로가 존재하지 않아 `[WARN] dx_com not in venv` 상태로 남을 가능성이 높음.
  - **run.sh와 venv 불일치** — `run.sh`는 venv를 활성화하지 않고 `python3 compile.py`를 직접 호출함. `setup.sh`가 venv에 dx_com을 연결했음에도 시스템 Python으로 실행되어 venv 구성이 무의미해짐.
  - **README에 사전 요구사항 누락** — `yolo26n.onnx` 파일이 이미 디렉터리에 있어야 하며 dx_com이 시스템에 설치돼 있어야 한다는 전제조건이 명시되지 않음. 또한 Quick start의 세 번째 단계(`verify.py`) 실행 시 예상 출력에 대한 안내 없음.

- **One-sentence verdict**: 컴파일 자체는 성공했으나 dx_com 경로 의존성이 테스트 하네스 내부 venv에 묶여 있어, 동일 환경이 아닌 다른 사용자가 `bash setup.sh`만 실행했을 때 재현 성공을 보장하기 어려움.


---

---

---

### R16 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `session.log`에 중간 오류(SyntaxError, KeyError, onnx deserialization error)가 다수 포함되어 있어, 최종 PASS 여부를 모르는 사용자가 로그를 읽으면 세션 실패로 오해할 수 있음
  - `verify.py`의 cross-validation이 `dx-runtime/dx_app/assets/models/yolo26n.dxnn` 참조 파일 존재를 전제하나, README에 해당 의존성이 명시되지 않아 clean 환경에서 해당 검증 단계가 실패할 수 있음
  - `ultralytics`, `torchvision` 등 대형 의존성의 버전이 고정되지 않아(`pip install` 시 최신 버전 설치) 재현성이 불안정하며, setup.sh 실행 시간이 상당히 길어질 수 있음

- **One-sentence verdict**: SUITE_ROOT 자동 감지, 실제 session.log, 명확한 Quick Start 구조 등 핵심 품질 기준을 충족하나, 중간 오류로 가득한 session.log와 문서화되지 않은 외부 참조 파일 의존성이 clean 환경 사용자에게 혼란 및 부분 실패를 유발할 수 있어 PARTIAL로 판정한다.


---

---

---

### R16 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **Sanity check가 FAIL로 기록됨** (`dxrt-cli: command not found`): session.log에 sanity check FAIL이 명시되어 있고, `setup.sh`는 `dx_engine` import 실패 시 `exit 1`로 종료됨. 즉, 환경이 정상적으로 구성되지 않은 상태에서 생성된 세션이라 end-user가 `bash setup.sh`를 실행하면 "[FATAL] dx_engine not available" 오류로 바로 중단될 가능성이 높음.
  - **실제 inference 실행 증거 없음**: session.log는 `py_compile` 문법 검사와 artifact 존재 확인만 포함하고, `python yolo26n_sync.py` 실제 실행 결과가 없음. 검증이 불완전하여 런타임 오류 여부를 알 수 없음.
  - **README 마크다운 포맷 오류**: Quick Start 코드 블록의 닫는 ` ``` ` 이 누락되어 "Variant Commands" 섹션 전체가 Quick Start 코드 블록 안에 포함되는 렌더링 버그가 있음.

- **One-sentence verdict**: `dx_engine` 미설치 환경에서 sanity check FAIL 상태로 생성되었고 실행 증거도 없어, 사전 환경 구성 없이는 end-user가 `setup.sh` 단계에서 즉시 막힘.


---

---

---

### R16 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **README Option C의 venv 경로 하드코딩**: `source ../../venv-dx_stream/bin/activate` 는 `venv-dx_stream`이 `dx-runtime/` 바로 아래 있다고 가정하는데, 일반적인 설치 위치(`dx-runtime/dx_stream/venv-dx_stream`)와 다를 수 있음. `setup.sh`은 자동 탐색으로 올바르게 처리하지만 README의 수동 예시는 틀릴 수 있음.
  - **Pipeline 실행 출력 미확인**: `session.log`에서 `timeout 30 python3 pipeline.py ... --headless` 실행 후 실제 detection 출력이 없고, 검증은 `grep -q "Pipeline" session.log` (커맨드 라인 자체가 포함되어 있어 항상 통과)로만 이루어져 실제 파이프라인 동작 여부를 확인하기 어려움.
  - **세션 디렉터리 위치 비표준**: 아티팩트가 `dx-runtime/dx_stream/dx-agentic-dev/` 대신 `dx-runtime/dx-agentic-dev/`에 배치된 것으로 보여, README의 `cd dx-agentic-dev/...` 진입 경로가 어디서 실행해야 하는지 명시되지 않아 처음 사용자가 혼란을 겪을 수 있음.

- **One-sentence verdict**: Option A/B (`run.sh`, `run_yolo26n_detection.sh`)는 venv 자동 탐색 덕에 대부분 환경에서 동작 가능하나, Option C의 경로 하드코딩과 파이프라인 실제 실행 출력 부재로 완전한 PASS 판정은 어렵다.


---

---

---

### R16 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **모델 경로 불일치**: `session.log`에서 실제 모델 경로는 `workspace/res/models/models-2_3_0/` 인데, `setup.sh`는 `$SRC_DIR/samples/models/` (즉 `dx-runtime/dx_stream/dx_stream/samples/models/`)를 확인한다. 두 경로가 불일치하며, 새 사용자 환경에서 model 탐색/다운로드 로직이 실패할 가능성이 높다.
  - **README Prerequisites step 3의 `./setup.sh` 혼동**: `cd ../../` 후 `./setup.sh --model=...` 를 실행하라고 하는데, 이는 세션 폴더의 `setup.sh`가 아니라 상위의 다른 `setup.sh`를 가리킨다. 어느 `setup.sh`를 실행해야 하는지 명확하지 않아 사용자 혼동이 발생한다.
  - **하드코딩된 `../..` 상대 경로**: `setup.sh`의 `DX_STREAM_ROOT`가 `"$SCRIPT_DIR/../.."` (2단계 고정)로 설정되어 SUITE_ROOT 자동 탐색 패턴을 사용하지 않는다. `run_cascaded_yolo26n.sh` 내용도 제공되지 않아 해당 스크립트의 경로 처리를 검증할 수 없다.
- **One-sentence verdict**: Run 옵션 3가지와 실제 실행 로그를 갖춰 구조는 양호하나, 모델 경로 불일치와 모호한 전제조건 지침으로 인해 에이전트 실행 환경 외 새 사용자가 별도 수정 없이 성공적으로 실행하기 어렵다.


---

---

---

### R16 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **`<session_id>` 플레이스홀더 미치환**: README의 `cd dx_app/dx-agentic-dev/<session_id>` 경로가 실제 세션 ID(`20260514-232945_codex_gpt55_yolo26n_object_detection`)로 치환되지 않아 사용자가 어느 디렉토리로 이동해야 하는지 직접 찾아야 함.
  - **setup.sh 로컬 venv 폴백의 `dx_engine` 미설치**: `venv-dx-runtime`을 찾지 못할 경우 로컬 venv를 생성하지만 `pip install opencv-python numpy`만 수행 — `dx_engine`은 독점 SDK라 pip 설치 불가. 결과적으로 `[FATAL] dx_engine not available` 오류로 즉시 종료됨.
  - **검증(verify) 단계 부재**: README에 실행 성공 시 기대 출력이나 결과 확인 방법이 없고, `verify.py`도 미포함. 사용자가 정상 동작 여부를 스스로 판단해야 함.

- **One-sentence verdict**: 기존 `venv-dx-runtime`이 설치된 환경에서는 동작 가능하나, `<session_id>` 미치환과 로컬 venv의 `dx_engine` 미설치 문제로 인해 처음 접하는 사용자가 README만 보고 독립적으로 실행하기 어렵다.


---

---

---

### R16 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `detect_yolo26n.py`가 생성 파일 목록에는 기재되어 있으나, README/artifacts에 내용이 없어 파일 누락 시 `run.sh`가 즉시 실패함. 핵심 실행 파일임에도 검증 근거가 없음.
  - `calibration_dataset` 항목이 `dx_com/calibration_dataset/` 심볼릭 링크로 표기되어 있어, 원본 빌드 환경 외에서는 broken symlink가 될 가능성이 있음 (재컴파일 시 문제).
  - README Quick Start에 **세션 디렉토리로 이동하는 `cd` 명령이 없음** — 사용자가 어디서 `bash setup.sh`를 실행해야 하는지 명시되지 않아 초보 사용자가 혼란을 겪을 수 있음.

- **One-sentence verdict**: 구조와 스크립트 품질은 양호하나, 핵심 실행 파일(`detect_yolo26n.py`)의 내용 및 존재 검증이 누락되어 있어 사용자가 실제 추론 단계에서 막힐 수 있음.


---

---

---

### R16 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **전제 조건 미명시**: README에 "dx-runtime이 사전 설치되어 있어야 한다"는 prerequisite이 없음. `setup.sh`가 `dx_engine` 미설치 시 FATAL로 종료하며 `bash ../../install.sh --all ...` 명령을 출력하지만, 사용자는 `setup.sh`를 실행해봐야 이를 알 수 있음
  - **모델 파일 취득 방법 부재**: `run.sh`가 `../../assets/models/yolo26n.dxnn`을 요구하나, README에 이 파일을 어떻게 확보하는지(다운로드 명령, `dx-runtime` 자산 여부 등) 설명이 없음. 모델이 없으면 `run.sh`가 즉시 `[ERROR]`로 종료됨
  - **실제 추론 실행 증거 없음**: `session.log`는 syntax 검증(13/13)과 `--help` 출력만 기록되어 있고, 실제 NPU 또는 CPU fallback 추론 실행 결과(bbox, confidence, 처리 시간 등)가 전혀 없음 — `verify.py`도 미포함

- **One-sentence verdict**: 아티팩트 구조와 코드 품질은 양호하나, 모델 파일 취득 경로 미안내 및 실제 추론 실행 증거 부재로 인해 첫 실행 사용자가 막힐 가능성이 높다.


---

---

---

### R16 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `run_detection.sh`를 호출하지만, 해당 파일의 내용이 아티팩트에 포함되지 않음. `run.sh`는 `$VIDEO`를 전달하지만 `$MODEL` 경로를 `run_detection.sh`에 넘기지 않아 동작 불확실.
  - README의 `../../` 상대 경로 표기가 세션 디렉터리 기준인지 `dx_stream` 루트 기준인지 혼용되어 있어 처음 접하는 사용자가 올바른 기준 디렉터리를 파악하기 어려움.
  - `setup.sh`의 venv 자동 탐색 로직이 동작하지 않으면(기존 venv 없음) 빈 로컬 venv를 생성하지만 `pydxs` 설치 단계가 없어 `pipeline.py` 실행 시 `ImportError` 발생 가능.

- **One-sentence verdict**: session.log에서 실제 파이프라인 실행 성공이 확인되지만, `run_detection.sh` 미포함 및 README 상대 경로 혼용으로 인해 처음 접하는 사용자가 독립적으로 재현하기에는 불충분하다.


---

---

---

### R16 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - `run.sh`에 버그 존재: `PRIMARY_MODEL` 인자를 받아 설정하지만 실제로 `run_cascaded.sh "$VIDEO"`만 호출하여 primary model 경로 override가 `run_cascaded.sh`에 전달되지 않음. 사용자가 모델 경로를 커스텀 지정해도 무시됨.
  - README의 `cd ../../` 경로 지시가 세션 디렉터리 기준으로 설명되지 않아 혼란 유발 가능. `run.sh` vs `run_cascaded.sh` 두 진입점이 모두 나열되어 어느 것을 실행해야 하는지 불명확함.
  - `run.sh`가 `setup.sh`를 `2>/dev/null || true`로 호출하여 setup 실패(venv 없음, 플러그인 없음)가 무음 억제됨—사용자가 오류 원인을 진단하기 어려움.
- **One-sentence verdict**: 파이프라인 자체는 실제 실행 증거가 있고 README도 충실하지만, `run.sh`의 인자 전달 버그와 setup 오류 억제로 인해 커스텀 모델 경로 사용 또는 환경 문제 상황에서 사용자가 막힐 가능성이 높다.


---

---

---

### R16 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - README의 `cd dx_app/dx-agentic-dev/<session_id>` 경로에 `<session_id>` 플레이스홀더가 그대로 남아 있어, 사용자가 실제 디렉토리 이름을 직접 찾아야 함
  - `verify.py`가 없으며 `session.log`는 에이전트가 생성한 증거로만 존재 — 사용자가 직접 실행해 결과를 검증할 수 있는 단계가 없음
  - Prerequisites 섹션이 "From dx-runtime root"라고만 안내하고 정확한 경로(`dx-runtime/`)를 명시하지 않아, 이 세션 디렉토리를 처음 접하는 사용자에게 불명확함

- **One-sentence verdict**: setup.sh와 run.sh의 로직은 견고하고 session.log도 실제 실행 출력을 포함하고 있으나, README의 `<session_id>` 미치환 플레이스홀더와 사용자 실행 가능한 verification 단계 부재로 인해 완전한 end-user 실행성은 확보되지 않음.


---

---

---

### R16 claude-code compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - `run.sh`가 `verify.py`에 `--image` 인자를 전달하지만, README의 Quick Start에는 `python verify.py`만 단순 기술되어 있어 인자 없이 실행했을 때 동작 방식이 불명확함
  - README의 Quick Start 코드블록이 열린 ` ``` ` 이후 닫히지 않는 렌더링 결함 있음 (백틱 누락으로 이후 내용이 코드블록 안에 포함될 수 있음)
  - `session.log`의 "Setup Check" 항목에서 venv 경로가 `.deepx/tests/venv`로 표시되어 실제 세션 venv(`<session_dir>/venv`)와 불일치 — 사용자 혼란 유발 가능

- **One-sentence verdict**: 전반적으로 완성도 높은 세션으로 setup→run→verify 흐름이 명확하고 setup.sh의 SUITE_ROOT 자동탐지·venv 구성이 견고하나, README 코드블록 렌더링 결함과 verify.py 인자 불일치가 소소한 장애물이 될 수 있다.


---

---

---

### R16 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues** (if any):
  - `verify.py` 파일이 없음 — ONNX vs DXNN 수치 비교 검증 스크립트 누락 (Mandatory Deliverables 위반)
  - README에 `--model /path/to/yolo26n.dxnn` 형태로 경로를 직접 지정하라고 안내하지만, `run.sh`는 `$APP_ROOT/assets/models/yolo26n.dxnn`을 자동으로 사용해 불일치 발생
  - `async` variant는 `--video` 인자를 요구하는데, 샘플 이미지(`sample_dog.jpg`)로 실행하면 실패할 가능성이 있음 (이미지 파일을 비디오로 전달)
- **One-sentence verdict**: setup/run 흐름은 명확하고 session.log에 실제 실행 증거가 있어 기본 sync 실행은 가능하나, `verify.py` 누락으로 공식 mandatory deliverables 기준 미충족이며 README와 run.sh 간 모델 경로 안내 불일치가 혼란을 줄 수 있다.


---

---

---

### R16 claude-code dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **`run.sh`에 model 전달 버그**: `$MODEL` 변수를 검증한 뒤 `run_yolo26n_realtime_detection.sh "$VIDEO"`에 `$VIDEO`만 전달하고 `$MODEL`은 전달하지 않음. 모델 경로가 기본값과 다를 경우 wrapper 스크립트 내부 하드코딩 경로를 사용하게 되어 실패 가능.
  - **진입점 혼재**: README의 "Option A"는 `run_yolo26n_realtime_detection.sh`를 직접 호출하고, `run.sh`도 별도 존재하며, `setup.sh`도 독립 실행 가능 — 어떤 파일을 먼저 실행해야 하는지 명확하지 않아 신규 사용자가 혼란스러울 수 있음.
  - **상대 경로 설명 부족**: README 전반의 `../../` 경로가 "세션 디렉터리 기준"임을 명시하지 않아, 사용자가 다른 위치에서 명령 실행 시 경로 오류 발생 가능.
- **One-sentence verdict**: session.log가 실제 실행 증거를 보여 파이프라인 자체는 작동했으나, `run.sh`의 model 경로 미전달 버그와 복수 진입점 혼재로 인해 첫 시도 사용자의 독립 실행 성공률이 낮다.


---

---

---

### R16 claude-code dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `run_cascaded.sh`에 VIDEO만 전달하고 MODEL 인자를 누락함 — `$1`(모델 경로)을 받아 저장하지만 `run_cascaded.sh` 호출 시 전달하지 않아, 커스텀 모델 경로 지정이 실질적으로 동작하지 않음
  - 제공된 artifact 목록에 `run_cascaded.sh`의 내용이 포함되지 않아 실제 GStreamer 파이프라인 실행 로직을 검증할 수 없음 (README·파일 목록에는 존재한다고 명시됨)
  - README의 Prerequisites "Model Download" 단계가 `../../setup.sh --model=...` 상대 경로를 사용하는데, 사용자가 어느 위치에서 실행하느냐에 따라 동작이 달라져 혼란을 줄 수 있음

- **One-sentence verdict**: session.log에 실제 파이프라인 실행이 확인되고 README 구조도 양호하지만, `run.sh`의 모델 인자 미전달 버그와 핵심 실행 스크립트(`run_cascaded.sh`) 내용 미제공으로 인해 사용자가 커스텀 모델이나 비표준 경로 환경에서 온전히 재현하기 어렵다.


---

---

---

### R16 claude-code runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (partial)
- **Key issues**:
  - README Quick Start의 수동 `python yolo26n_sync.py` / `yolo26n_async.py` 명령에 `--headless` 플래그가 없음 — headless 서버 환경에서 display 창 열기 실패 가능. `run.sh`는 `--headless`를 올바르게 사용하지만 단계 2·3은 불일치
  - `session.log`에 실제 inference 실행 결과(detection 출력, bbox, 처리 시간 등)가 없음 — `--help` 텍스트만 캡처되어 실제 모델 동작 검증 미완
  - README에 세션 디렉토리로 `cd`하는 명령이 없음 — Quick Start의 `../../assets/models/` 상대 경로는 세션 디렉터리 기준이지만, 사용자가 다른 경로에서 실행 시 경로 오류 발생
- **One-sentence verdict**: `bash run.sh`는 경로 자동 감지로 동작할 가능성이 높지만, README의 수동 python 명령과 session.log 미검증으로 인해 headless 환경 사용자가 단계별 지침을 그대로 따랐을 때 실패할 수 있어 PARTIAL 판정.


---

---

---

### R17 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `session.log` 파일 없음 — mandatory artifact 누락. 에이전트가 실제로 컴파일을 실행했다는 증거가 없음 (`yolo26n.dxnn` 생성 여부 불명확)
  - `run.sh`의 기본 이미지 경로가 `../../../../dx-runtime/dx_app/sample/img/sample_dog.jpg` 하드코딩 — SUITE_ROOT 패턴 위반으로 디렉터리 깊이에 따라 경로 오류 발생 가능
  - `yolo26n.onnx` 소스 미명시 — README에 "Input ONNX model"로 표기만 되어 있고 어디서 구하는지 또는 세션이 제공하는지 기술 없음; `verify.py` 코드도 첨부되지 않아 내용 검증 불가

- **One-sentence verdict**: 컴파일 결과물(`yolo26n.dxnn`)의 실제 생성 증거(session.log)가 없고 run.sh의 경로가 취약하여, 다른 환경에서 end-user가 그대로 실행하면 실패할 가능성이 높음.


---

---

---

### R17 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `source setup.sh 2>/dev/null || true`로 setup.sh 실패를 무음 무시함 — dx_engine 미설치 시 run.sh가 경고 없이 진행되다가 import error로 실패함
  - README에 선행 조건(`dx_engine` 빌드 필요) 언급 없음 — 처음 사용자는 setup.sh 실행 전에 `./install.sh && ./build.sh`가 필요하다는 사실을 알 수 없음
  - 비동기/C++ postprocess 변형 4종이 README에 나열되어 있으나 session.log에는 sync 단 1회 실행 증거만 있음 — 나머지 스크립트의 실제 동작 보장 없음

- **One-sentence verdict**: 핵심 sync 경로는 실행 증거(성능 요약 포함)가 명확하고 setup.sh 로직도 견고하나, `run.sh`의 setup 오류 무시(`|| true`)와 README의 dx_engine 선행 조건 누락으로 인해 clean 환경 사용자는 원인 불명의 실패를 겪을 가능성이 있음.


---

---

---

### R17 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`run.sh`가 MODEL을 `run_yolo26n_detection.sh`에 전달하지 않음**: `run.sh`에서 `$MODEL` 변수를 확인하지만 실제 호출은 `bash run_yolo26n_detection.sh "$VIDEO"` — 모델 경로가 누락된 채로 전달되어 `run_yolo26n_detection.sh` 내부에 하드코딩된 경로에 의존하게 됨.
  - **`run.sh`의 `setup.sh` 호출이 오류를 무시**: `source setup.sh 2>/dev/null || true`로 venv 활성화 실패가 조용히 무시되어, `pydxs` 미설치 시 `ModuleNotFoundError`만 보이고 근본 원인은 숨겨짐.
  - **상대 경로(`../../`) 의존 및 디렉토리 구조 미설명**: README와 `setup.sh` 모두 세션 디렉토리가 `dx_stream` root로부터 정확히 2단계 하위에 있다고 가정하나, 이 구조를 사용자에게 명시하지 않음. 경로 계산 오류 시 모델 다운로드나 샘플 파일 접근이 실패할 수 있음.

- **One-sentence verdict**: README 구조와 실행 증거(session.log)는 양호하나, `run.sh`의 모델 경로 미전달 버그와 에러 묵살 패턴으로 인해 `run_yolo26n_detection.sh`의 모델 경로 처리 방식에 따라 첫 실행 성공이 불확실하다.


---

---

---

### R17 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **session.log에 파이프라인 실행 실패 기록** — `no property "num-sources" in element "dxgather"` 오류가 발생했고, 이후 "(fixed)" 재실행 로그는 중간에 truncate되어 최종 성공 여부를 확인할 수 없음
  - **`run_cascaded.sh` 파일 미첨부** — `run.sh`와 README 모두 `run_cascaded.sh`를 핵심 실행 파일로 참조하지만, 해당 파일의 내용이 artifacts에 없어 end-user가 독립 검증 불가
  - **`setup.sh`에서 하드코딩된 상대 경로 사용** — `$(cd "$SCRIPT_DIR/../.." && pwd)` 패턴을 사용해 `DX_STREAM_ROOT`를 산출하며, 이는 우연히 맞지만 SUITE_ROOT 자동 탐지 패턴 미준수 (HARD GATE 위반); 세션 디렉터리 깊이가 달라지면 즉시 깨짐

- **One-sentence verdict**: 실제 파일 경로가 담긴 session.log가 존재하고 README 구조도 충실하나, 핵심 실행 파일인 `run_cascaded.sh`가 누락되고 파이프라인 오류 수정 후의 최종 성공 증거가 불완전하여 end-user가 그대로 따라 실행하기에는 신뢰성이 부족하다.


---

---

---

### R17 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log` 파일 없음 — 에이전트가 실제로 코드를 실행했다는 증거가 전혀 없음. 아티팩트가 실제 동작하는지 알 수 없음
  - README에서 모델 경로를 `/path/to/yolo26n.dxnn`으로 안내하지만, `run.sh`의 기본 경로는 `../../assets/models/yolo26n.dxnn`으로 상충됨. README가 말하는 "available in `dx_stream/samples/models/`" 경로도 다르게 표기되어 혼란 유발
  - `setup.sh`이 `dx_engine` 미설치 시 `exit 1`로 중단하나, 수동 설치 가이드가 부정확한 상대경로(`$(cd "$SCRIPT_DIR/../.." && pwd)`)를 사용 — 실제 `dx_app` 루트를 가리키지 않을 수 있음

- **One-sentence verdict**: session.log 부재로 실행 증거가 없고, 모델 경로 안내가 README·run.sh·setup.sh 간에 일치하지 않아 초심자가 혼자 실행하기 어려운 PARTIAL 수준이다.


---

---

---

### R17 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **Quick Start 3번 명령 실패 위험**: README의 `python verify.py --show-result`는 `bash setup.sh` 실행 후 venv가 서브셸에서만 활성화되므로 parent shell에서 그대로 실행하면 `ModuleNotFoundError` 발생. run.sh는 내부에서 venv를 source하지만, 직접 python 호출 경로는 별도 `source venv/bin/activate` 필요 — README에 이 단계가 명시되어 있지 않음
  - **verify.py 인자 불일치**: `run.sh`는 `python verify.py --dxnn yolo26n.dxnn --image <path> --show-result`를 호출하는 반면, README Quick Start에는 `python verify.py --show-result`만 기재 — 필수 인자(`--dxnn`, `--image`) 없이 실행 시 오류 가능
  - **session.log 말미 `[truncated]`**: 컴파일 완료 전체 로그 확인 불가; 실제 출력임은 확인되나 `yolo26n.dxnn` 생성 완료 시점의 증거가 잘림
- **One-sentence verdict**: `bash run.sh` 경로는 동작 가능하나, README Quick Start 3번 명령(`python verify.py --show-result`)이 venv 활성화 누락 및 필수 인자 불일치로 그대로 따라 하면 실패하므로 end-user가 문서만 보고 전체 흐름을 완주하기 어렵다.


---

---

---

### R17 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **실제 추론 실행 증거 없음** — `session.log`에 문법 검사(`syntax_check`)와 `--help` 출력만 기록되어 있고, 실제 `yolo26n_sync.py` 추론 실행 결과(탐지 출력, 처리 시간 등)가 전혀 없음. Artifact Verification Gate의 "session.log MUST contain actual terminal command output" 위반.
  - **모델 파일 전제조건 미명시** — README에 `yolo26n.dxnn`이 `../../assets/models/` 경로에 반드시 존재해야 한다는 설명이 없음. 모델이 없으면 `run.sh`가 에러로 종료되지만 사용자 입장에서 사전 준비 사항을 알 수 없음.
  - **`setup.sh`에 sanity_check 누락** — 프레임워크 요구사항인 `bash dx-runtime/scripts/sanity_check.sh --dx_rt` 실행이 없음. 또한 `run.sh`에서 `source setup.sh 2>/dev/null || true`로 셋업 오류를 묵살하여 dx_engine 미설치 상태를 숨길 위험이 있음.

- **One-sentence verdict**: README와 run.sh의 구조는 양호하나, session.log에 실제 추론 실행 증거가 없고 모델 파일 전제조건이 문서화되지 않아 새로운 사용자가 성공적으로 실행하기 어렵다.


---

---

---

### R17 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`의 경로 계산(`../..`)이 dx_stream 하위 session 디렉터리 기준이라 실제 depth에 따라 깨질 수 있음 (SUITE_ROOT 패턴 미사용)
  - README의 `cd ../../` 지시가 실행 위치 기준 없이 기술되어 있어 혼동 유발 — session 디렉터리가 몇 단계 아래인지 명시 없음
  - `run.sh`가 내부적으로 `run_detection.sh`를 호출하지만, README "How to Run"의 Option A도 동일하게 `run_detection.sh`를 직접 호출함 — `run.sh`의 존재 이유가 불명확하고 두 파일의 역할이 중복
- **One-sentence verdict**: session.log에 실행 증거가 있어 에이전트 환경에서는 동작이 확인됐으나, 상대 경로 하드코딩과 중복 진입점으로 인해 처음 접하는 사용자가 올바른 위치에서 실행하기 어렵다.


---

---

---

### R17 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 `DX_STREAM_ROOT/dx_stream`으로 `SRC_DIR`을 구성하여 세션 디렉토리가 `dx-runtime/dx_stream/dx-agentic-dev/<session>/`에 있을 경우 `dx_stream/dx_stream` 이중 경로 버그 발생 — `DEFAULT_MODEL`, `DEFAULT_VIDEO` 모두 존재하지 않는 경로를 가리킴
  - `session.log` 1차 실행이 상대 경로 오류(`file://../../dx_stream/...`)로 실패했고, 성공한 2차 실행은 개발자 머신 전용 절대 경로(`/data/home/dhyang/github/...`)를 사용 — 다른 환경에서 그대로 재현 불가
  - `run.sh`가 `run_cascaded.sh`에 완전히 위임하지만, README의 모델 다운로드 경로(`dx_stream/samples/models/`)와 session.log의 실제 모델 경로(`workspace/res/models/`)가 불일치하여 사용자가 올바른 모델 위치를 파악하기 어려움

- **One-sentence verdict**: 구조와 문서화는 잘 갖추어졌으나, `SRC_DIR` 이중 경로 버그와 개발자 환경 전용 절대 경로 의존으로 인해 다른 머신에서 `bash run.sh` 단독 실행 시 실패할 가능성이 높다.


---

---

---

### R17 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **`run.sh`에 venv 활성화 없음** — `setup.sh`에서 venv를 찾거나 생성하지만, `run.sh`는 venv를 source하지 않고 `python`을 직접 호출한다. `dx_engine`이 시스템 Python에 없으면 즉시 ImportError로 실패한다.
  - **`session.log` 미존재** — 에이전트가 실제로 코드를 실행했다는 증거가 없다. 명세상 `session.log`는 실제 명령 출력을 포함해야 하며(heredoc 금지), 이 파일이 없으면 artifacts가 동작한다는 보장이 전혀 없다.
  - **`setup.sh` fallback의 `dx_engine` 설치 불가** — 공유 venv를 찾지 못한 경우 로컬 `.venv`를 생성하고 `opencv-python`과 `numpy`만 pip 설치한다. `dx_engine`은 private 패키지로 `pip install`로 해결되지 않으므로, 신규 환경에서는 `[FATAL] dx_engine not importable` 오류로 항상 중단된다.

- **One-sentence verdict**: `session.log` 부재로 실행 검증이 불가능하고, `run.sh`의 venv 활성화 누락으로 인해 신규 환경에서 end-user가 `bash run.sh` 한 줄만으로 성공하기 어렵다.


---

---

---

### R17 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `yolo26n.onnx`가 세션 디렉토리에 이미 존재해야 `run.sh`가 동작하지만, README에 이 파일이 사전 생성된 artifact인지 아니면 사용자가 직접 export해야 하는지 명시가 없음 (`yolo26n.pt` → ONNX 단계 안내 부재)
  - `setup.sh`가 `set -euo pipefail` 상태에서 sanity_check.sh 실패 시 즉시 중단되는데, README에 NPU 환경 미비 시 대처 방법이 없음 — 사용자가 왜 setup이 실패했는지 알기 어려움
  - `run.sh`가 실질적으로 `verify.py --onnx ... --dxnn ...`만 실행하는데, verify.py 내용과 예상 성공 출력(e.g., `RESULT: PASS`)이 README에 없어 사용자가 성공/실패를 구분하기 어려움
- **One-sentence verdict**: 아티팩트와 환경이 모두 갖춰진 개발 서버에서는 Quick Start가 동작하지만, ONNX 파일 전제조건과 NPU 장애 시 복구 안내가 없어 신규 사용자에게 PARTIAL 수준의 가이드를 제공한다.


---

---

---

### R17 cursor-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (단, smoke-test 수준)
- **Key issues**:
  - `setup.sh`이 venv를 생성하지 않고 PYTHONPATH만 설정함 — 호스트 환경에 `dx_engine`, `numpy`, `cv2`가 사전 설치되어 있지 않으면 즉시 실패하며 복구 가이드 없음
  - README의 `--model /path/to/yolo26n.dxnn`이 placeholder로만 표기되어 있고, `.dxnn` 모델 파일 획득 방법(컴파일 세션 경로, assets 위치 등)이 전혀 안내되지 않음
  - `session.log`의 검증이 `py_compile` + `--help` smoke test에 그침 — 실제 NPU 추론 실행 증거(출력 bbox, FPS 등)가 없어 end-to-end 동작 확인 불가
- **One-sentence verdict**: 환경이 이미 올바르게 구성된 개발자라면 실행 가능하지만, venv 부재·모델 경로 미안내·실질적 추론 검증 부재로 일반 사용자가 독립적으로 따라하기에는 불충분함.


---

---

---

### R17 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - **경로 가정이 깨지기 쉬움**: `run.sh`의 `DX_STREAM_ROOT`가 `../../`로 고정되어 있어 세션 디렉터리 깊이가 다를 경우 model/video 경로가 모두 잘못됨. README의 커스텀 실행 예시도 `../../dx_stream/...` 형태의 하드코딩된 상대 경로를 사용 (SUITE_ROOT 자동 감지 패턴 미적용)
  - **run.sh → run_yolo26n_realtime_detection.sh 위임 불완전**: `run.sh`는 `run_yolo26n_realtime_detection.sh`를 호출하지만, 이 스크립트의 존재나 내용이 README에 설명되어 있지 않아 사용자가 내부 동작을 추적하기 어려움; `$VIDEO` 인자도 해당 스크립트로 전달되지 않음
  - **setup.sh의 모델 다운로드 로직이 불안정**: `./setup.sh --model=...` 호출 대상 경로가 `../../`로 추정되며 실제 존재 여부가 불분명. 실패 시 `[WARN]`으로 넘어가기 때문에 모델 없이 run.sh가 실행되어 `[ERROR] Model not found`로 종료될 수 있음

- **One-sentence verdict**: 기본 경로 구조가 맞으면 동작할 수 있으나, 세션 디렉터리 깊이 가정에 의존하는 하드코딩된 상대 경로와 `run_yolo26n_realtime_detection.sh` 위임 불투명성으로 인해 다른 환경에서 재현 신뢰도가 낮다.


---

---

---

### R17 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **모델 경로 불일치**: `setup.sh`는 모델을 `dx_stream/samples/models/`에 다운로드하지만, `session.log`의 실제 파이프라인 실행에서는 `workspace/res/models/models-2_3_0/` 경로를 사용함 — 다른 머신에서 `run.sh`를 실행하면 모델을 찾지 못할 가능성이 높음
  - **`run_cascaded.sh` 내용 비공개**: `run.sh`가 실제로 위임하는 `run_cascaded.sh`의 내용이 artifacts에 없어, 모델 경로 해석 로직이 불투명함; 사용자가 어떤 경로로 모델을 조회하는지 알 수 없음
  - **하드코딩된 `../..` 깊이 가정**: `setup.sh`의 `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"` 는 세션이 정확히 2단계 깊이에 있다고 가정 — SUITE_ROOT 자동 탐지 패턴 미적용으로, 세션 디렉토리가 이동되거나 다른 레이아웃에서 실행 시 경로가 깨질 수 있음

- **One-sentence verdict**: 파이프라인 자체는 정상 실행되었으나(exit:0), 실제 실행에 사용된 모델 경로와 `setup.sh`가 준비하는 경로가 달라 신규 사용자가 `README → setup.sh → run.sh` 순서로 따라가면 모델 미발견 오류로 실패할 가능성이 있는 **조건부 실행 가능** 상태이다.


---

---

---

### R17 cursor-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `setup.sh`에서 `dx_com`을 설치하지 않음 — `compile.py`는 `dx_com`을 사용하지만 해당 패키지가 venv에 포함되지 않아 신규 환경에서 즉시 실패할 수 있음
  - dx_engine 경로 주입이 `.deepx/tests/venv/lib/python*/site-packages` glob에 의존하며, 경로가 없을 경우 **오류 없이 조용히 스킵** — 사용자는 `import dx_engine` 실패 시 원인을 추적하기 어려움
  - `session.log`가 `[truncated]`로 잘려 있어 `dx_com.compile()`이 실제로 성공하고 `yolo26n.dxnn`이 생성됐는지 확인 불가

- **One-sentence verdict**: Quick Start 3단계 구조와 SUITE_ROOT 자동 탐지는 잘 갖춰져 있으나, `dx_com` 미설치와 dx_engine 경로 무음 실패 문제로 인해 신규 환경에서 `compile.py` 실행 성공을 보장하기 어렵다.


---

---

---

### R17 claude-code compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh`가 `dx_engine`을 `.deepx/tests/venv`(내부 테스트 전용 venv)에서 링크 — 이 venv는 공개 문서화된 경로가 아니며, 해당 경로가 없으면 `verify.py`에서 `dx_engine` import가 조용히 실패함 (에러 없이 skip되어 사용자가 인지 못할 가능성)
  - 교정 데이터셋(`dx_com/calibration_dataset/` 100장 JPEG)의 준비 방법이 README에 전혀 기술되지 않아, `compile.py`를 재실행하려는 사용자가 막힘
  - `verify.py` 내용이 제공되지 않아 검증 로직의 정확성을 독립적으로 확인 불가 (session.log에 verify 실행 결과가 없음)

- **One-sentence verdict**: setup.sh와 run.sh의 구조는 양호하나 `dx_engine` 링크 경로가 내부 테스트 venv에 의존하고 calibration 데이터 준비 절차가 누락되어, 동일 환경이 사전 세팅된 개발자 외에는 완전한 재현이 어렵다.


---

---

---

### R17 claude-code dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - README Quick Start의 `python yolo26n_sync.py` 명령(step 2, 3)에 venv 활성화 단계가 없음. `setup.sh`를 실행해도 현재 셸에 venv가 활성화되지 않으므로, 사용자가 직접 `source .venv/bin/activate` 또는 `source <runtime_venv>/bin/activate`를 해야 한다는 안내가 누락됨 (`bash run.sh`인 step 4는 내부에서 처리하므로 문제없음)
  - README에 `cd <session_dir>` 지시가 없음 — 상대경로(`../../assets/models/yolo26n.dxnn`)가 세션 디렉토리 기준이라는 전제가 명시되지 않아 다른 경로에서 실행 시 `FileNotFoundError` 발생 위험
  - 사용자 관점의 명시적 검증 단계(예: 기대 출력, PASS/FAIL 판단 기준) 없음 — session.log에는 결과가 있으나 README에서 end-user가 실행 후 "성공"을 확인할 방법이 제시되어 있지 않음

- **One-sentence verdict**: `bash run.sh` 한 줄로는 동작하나, README step 2·3의 직접 `python` 호출은 venv 활성화 안내 누락 및 실행 위치 전제 미명시로 인해 익숙하지 않은 사용자에게 실패 가능성이 있다.


---

---

---

### R17 claude-code dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 모델 경로를 `$DX_STREAM_ROOT/dx_stream/samples/models/yolo26n.dxnn`으로 가정하지만, session.log의 실제 실행 경로(`workspace/res/models/models-2_3_0/yolo26n.dxnn`)와 불일치함. 다른 사용자 환경에서 `[ERROR] Model not found` 로 즉시 실패.
  - `run.sh`가 `run_yolo26n_realtime_detection.sh`를 호출하지만 해당 스크립트 내부에서 tracker_config.json 경로가 빌드 머신의 절대 경로(`/data/home/dhyang/...`)로 하드코딩되어 있을 가능성 높음 (session.log의 파이프라인 문자열에서 확인됨).
  - `setup.sh`의 모델 다운로드 로직이 `./setup.sh --model=...`를 `$SCRIPT_DIR/../..`에서 실행하는데, 해당 경로가 실제 dx_stream root인지 보장되지 않음 (세션 디렉토리 depth에 따라 달라짐).
- **One-sentence verdict**: session.log 기준으로 원본 머신에서는 정상 실행됐으나, 모델 경로 불일치와 하드코딩된 절대 경로로 인해 다른 환경에서는 추가 수작업 없이 실행하기 어렵다.


---

---

---

### R17 claude-code dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 `run_cascaded.sh "$VIDEO"` 만 넘기고 **secondary model 경로를 전달하지 않음** — cascaded 파이프라인의 핵심인 `EfficientNet_Lite0.dxnn` 경로가 run.sh → run_cascaded.sh 위임 과정에서 누락됨. README Option A(`bash run_cascaded.sh`)를 실행해도 secondary model 위치를 어떻게 지정하는지 설명 없음
  - README의 파이프라인 다이어그램 코드 블록이 \`\`\` 로 닫히지 않아 **마크다운 렌더링이 깨짐** — Configuration 테이블까지 코드 블록 안에 포함되어 가독성 저하
  - `session.log` 안 모델 경로가 `/data/home/dhyang/github/dx-all-suite-full-e2e/workspace/res/models/...`로 **개발자 머신 절대경로 하드코딩** — 다른 환경에서 참고 시 혼란 유발; `setup.sh`의 `MODEL_DIR` (`samples/models/`) 와도 경로 불일치
- **One-sentence verdict**: 파이프라인이 에이전트 환경에서 실제 실행된 증거는 충분하나, `run.sh`의 secondary model 경로 누락과 README 마크다운 오류로 인해 다른 환경의 사용자가 그대로 따라 하기는 어렵다.


---

---

---

### R17 claude-code runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (verify.py 존재 언급, 단 실행 증거 없음)
- **Key issues**:
  - **모델 파일 획득 경로 미안내**: README의 Manual Run 예시가 `/path/to/yolo26n.dxnn` placeholder를 그대로 노출하며, 실제 `.dxnn` 파일을 어디서 구하는지 설명이 없음. `run.sh` 기본값(`assets/models/yolo26n.dxnn`)도 해당 파일이 없으면 실패하나 사전 확인 없음.
  - **실제 추론 실행 증거 부재**: `session.log`에 `setup.sh` 성공과 `--help` 출력만 기록됨. `run.sh` 실행 결과(바운딩박스 출력, 이미지 저장 등 추론 성공 증거)가 없어 end-to-end 동작을 검증할 수 없음.
  - **dx-all-suite 디렉터리 구조 의존성 비명시**: `setup.sh`·`run.sh`가 SUITE_ROOT 자동 탐색에 의존하나 README에 "dx-all-suite 레포 내에서 실행해야 한다"는 사전 조건 미기재 — standalone 복사 시 `ERROR: Cannot find dx-all-suite root`로 즉시 실패.
- **One-sentence verdict**: `setup.sh` 및 venv 구성은 완성도가 높으나, 모델 파일 준비 방법 안내 부재와 실제 추론 실행 로그 누락으로 처음 접하는 사용자가 `run.sh`를 성공까지 실행하기 어렵다.


---

---

---

### R17 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - **venv 경로 불일치**: `setup.sh`은 공유 venv(`venv-dx-runtime`)를 우선 탐색·활성화하지만, `run.sh`은 `.venv` 또는 `venv` 디렉터리만 확인하므로, `setup.sh`이 shared venv를 사용한 경우 `run.sh`이 `"venv not found"` 오류로 실패할 수 있음.
  - **`compile.py` 미제공(확인 불가)**: README Quick Start의 핵심 단계(`python compile.py`)가 있지만, 제공된 artifacts 목록에 `compile.py` 파일이 없어 실제 포함 여부를 확인할 수 없음. 또한 `session.log`가 중간에 잘려 `.dxnn` 파일 생성 완료 여부가 불명확함.
  - **예상 출력 미기재**: README에 각 단계의 성공 기준(예: "RESULT: PASS"와 같은 기대 출력)이 없어, 초보 사용자가 성공/실패를 판단하기 어려움.

- **One-sentence verdict**: `setup.sh`의 SUITE_ROOT 탐색·sanity check 로직은 충실하지만, `run.sh`의 venv 탐색 경로가 `setup.sh`과 불일치하고 `compile.py` 포함 여부 및 컴파일 완료가 로그로 확인되지 않아, 그대로 따라 실행 시 실패할 가능성이 있는 **PARTIAL** 수준의 아티팩트임.


---

---

---

### R17 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - **README에 전제 조건 미기재**: `dx_engine`이 이미 빌드되어 있어야 한다는 점(`./install.sh && ./build.sh` 필요)을 README Quick Start 앞에 명시하지 않음. setup.sh는 fatal 에러로 잡아주지만, 사용자가 setup.sh를 실행하기 전까지 이 의존성을 알 수 없음.
  - **Direct Commands의 상대경로 맥락 누락**: `../../assets/models/yolo26n.dxnn` 같은 경로가 어느 디렉토리 기준인지 README에 설명 없음. 세션 디렉토리 내부에서 실행해야 한다는 안내가 빠져 있어 경로 오류 발생 가능성 있음.
  - **실제 추론 실행 증거 없음**: session.log는 sanity check PASS와 정적 문법 검사만 기록되어 있고, 실제 `yolo26n_sync.py` 실행 및 추론 결과 출력이 확인되지 않음(log truncated). `verify.py`도 부재.

- **One-sentence verdict**: setup.sh·run.sh의 구현 품질은 우수하나, README에 dx_engine 빌드 전제 조건과 상대경로 기준 디렉토리 안내가 빠져 있고 실제 추론 실행 증거가 없어 초심자 사용자가 막힐 가능성이 있다.


---

---

---

### R17 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **모델 경로 이중 중복 버그**: `setup.sh`에서 `DX_STREAM_ROOT`는 `$SCRIPT_DIR/../..` → `dx-runtime/dx_stream/`으로 계산되는데, 이후 `MODEL_PATH="$DX_STREAM_ROOT/dx_stream/samples/models/yolo26n.dxnn"`로 참조해 실제 경로가 `dx-runtime/dx_stream/dx_stream/samples/models/...`가 됨 — 경로가 존재하지 않아 모델 다운로드 로직이 무조건 `[WARN] Model still missing`으로 끝남
  - **실제 모델 경로 불일치**: session.log에서 실제 사용된 모델은 `workspace/res/models/models-2_3_0/yolo26n.dxnn`인데 README Option C 및 `setup.sh`는 `dx_stream/samples/models/`를 가리킴 — 신규 사용자가 README를 그대로 따르면 모델을 찾을 수 없음
  - **`run_yolo26n_realtime_detection.sh` 내용 미공개**: README와 `run.sh`가 위임하는 핵심 스크립트이지만 평가 아티팩트에 내용이 없어 내부 경로 처리가 검증 불가

- **One-sentence verdict**: 파이프라인 자체는 session.log에서 실제 실행이 확인되었으나, `setup.sh`의 모델 경로 이중 중복 버그와 README에 기술된 경로가 실제 실행 경로와 달라 신규 사용자가 모델 없이 `bash run.sh`만으로 end-to-end 재현에 성공하기 어렵다.


---

---

---

### R17 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh`가 `run_cascaded_yolo26n.sh`에 위임하는 구조인데, 해당 파일이 제공된 artifacts에 없음 — 실제로 파일이 없으면 `run.sh` 실행 시 즉시 실패함
  - README Prerequisites 3단계의 `cd ../../ && ./setup.sh --model=...`는 부모 디렉토리의 `setup.sh`를 참조하는데, `dx-runtime/setup.sh`가 실제로 존재하는지 불명확하며 `setup.sh` 내부의 `ensure_model`도 동일한 경로를 호출함 — 모델 다운로드 경로가 깨질 수 있음
  - `session.log`에 환경 점검(sanity check, gst-inspect, 라이브러리 목록) 결과만 있고 실제 파이프라인 실행 결과가 없음 — end-to-end 동작 증거 부재

- **One-sentence verdict**: 환경 점검과 README 구조는 양호하지만, `run_cascaded_yolo26n.sh` 누락 및 모델 다운로드 경로 불확실성으로 인해 사용자가 `run.sh`를 그대로 실행하면 실패할 가능성이 높다.


---

---

---

### R17 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `session.log`에 실제 추론 실행 결과가 없음 — `--help` 출력 및 syntax check만 기록되어 있고, 실제 `yolo26n_sync.py` 추론 실행(detection 결과, bbox 출력 등)이 없어 artifacts 동작 여부를 검증할 수 없음
  - `run.sh`가 `source "$SCRIPT_DIR/setup.sh" 2>/dev/null || true`로 setup.sh를 호출해, dx_engine 미존재 시 setup.sh의 `exit 1`이 `|| true`에 의해 무시되고 이후 `python yolo26n_sync.py`가 ImportError로 실패함 (silent failure)
  - README의 Prerequisites `cd dx_app`이 어디서 시작해야 하는지 기준 경로 미명시 (repo root인지 `dx-runtime/` 내부인지 불분명)
- **One-sentence verdict**: setup.sh의 venv 탐색 로직과 run.sh의 SUITE_ROOT 패턴은 양호하나, session.log에 실제 추론 실행 증거가 없고 `run.sh`의 `|| true` 패턴이 dx_engine 누락 오류를 무음 처리하므로 end-user가 실패 원인을 파악하기 어렵다.


---

---

---

### R18 claude-code compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 내부적으로 `python verify.py`를 호출하며 `--onnx`, `--dxnn`, `--image` 인자를 전달하지만, README의 Quick Start에는 `bash run.sh`와 `python verify.py`를 **별도 단계**로 안내 — 중복 실행 혼란 유발 가능
  - 첫 번째 `verify.py` 실행 시 `dx_engine` 미설치로 `DXNN inference failed` + `Exit code: 0` 이 발생했음 (오류 발생에도 0 반환). `session.log`에서 재시도 후 수정됨이 확인되나, 배포된 `verify.py`가 수정본인지 보장되지 않음
  - `setup.sh`의 sanity_check 판정 로직이 `grep -q "Sanity check PASSED"` 파이프 방식 사용 — 지침서에서 명시적으로 **금지된 패턴** (파이프 exit code 오염 위험)

- **One-sentence verdict**: README와 setup.sh는 전반적으로 충실하나, `run.sh`의 호출 구조 중복 및 `verify.py` 초기 오류 후 수정 여부 불명확으로 인해 최초 실행 시 사용자가 혼란을 겪을 가능성이 있어 PARTIAL 판정.


---

---

---

### R18 claude-code dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `source setup.sh 2>/dev/null || true`로 setup 실패를 무시하므로, dx_engine 미설치 상태에서 run.sh 실행 시 cryptic ImportError가 발생하며 원인 파악이 어려움
  - README Quick Start에 **사전 조건** (dx-runtime 빌드 완료, `yolo26n.dxnn` 모델 파일 존재 여부) 에 대한 안내가 없어 초기 사용자가 모델 경로 오류로 막힐 수 있음
  - `run.sh`의 dx-compiler 세션 경로 힌트(`<session>` 플레이스홀더)가 실제로 채워지지 않아 사용자가 직접 경로를 찾아야 함

- **One-sentence verdict**: 핵심 구조(setup → run → verify)가 잘 갖춰져 있고 session.log에 실제 추론 결과(RESULT: PASS)가 확인되어 전반적으로 실행 가능하지만, setup 오류 무시(`|| true`)와 사전 조건 미기재로 인해 초기 설정 단계에서 사용자가 혼란을 겪을 수 있다.

---

---

### R14 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`MODEL_DIR` 경로 이중화 버그**: `setup.sh`에서 `DX_STREAM_ROOT=$(cd "$SCRIPT_DIR/../.." && pwd)`는 `dx-runtime/dx_stream/`를 가리키는데, 이어서 `MODEL_DIR="$DX_STREAM_ROOT/dx_stream/samples/models"`로 설정하면 실제 경로가 `dx_stream/dx_stream/samples/models`(존재하지 않음)가 됨. 올바른 경로는 `$DX_STREAM_ROOT/samples/models`이어야 함.
  - **`run.sh`에서 모델 경로 미전달**: `PRIMARY_MODEL` 변수를 계산하지만 `bash run_cascaded.sh "$VIDEO"`에 전달하지 않음. 모델 경로 인자가 실질적으로 무시됨.
  - **`session.log` 실행 경로와 스크립트 경로 불일치**: 실제 실행은 `/workspace/res/models/models-2_3_0/` 절대경로로 동작했으나, `setup.sh`/`run.sh`의 모델 다운로드 경로와 다름. 신규 환경에서 `setup.sh`의 모델 존재 확인이 실패할 가능성 높음.

- **One-sentence verdict**: 파이프라인 자체는 세션 빌드 시 정상 실행됐으나, `MODEL_DIR` 이중화 버그와 `run.sh`의 모델 경로 미전달로 인해 신규 환경에서 end-user가 `run.sh` 한 번으로 성공적으로 실행하기 어려움.


---

---

### R18 cursor-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh`은 `venv-dx-compiler-local`과 `venv-dx-runtime`이 이미 존재함을 전제하지만, README에 이 사전 조건이 명시되어 있지 않음. 두 venv가 없으면 `dx_com`/`dx_engine` import가 실패하면서 setup 단계에서 막힘
  - `dx_com` 미발견 시 `WARN`만 출력하고 계속 진행하다가 마지막 `import dx_com` 체크에서 실패 — 오류 원인과 복구 방법이 setup.sh 출력에 나타나지 않아 사용자 혼란 가능
  - `session.log`가 `compile.py` 실행 도중 잘려 있어 실제 컴파일 성공 여부 및 `verify.py`의 `RESULT: PASS` 증거가 로그에서 확인 불가 (README 본문에만 결과 서술)

- **One-sentence verdict**: suite venv(`venv-dx-compiler-local`, `venv-dx-runtime`)가 미리 구축된 환경에서는 Quick Start 2단계로 실행 가능하지만, 해당 전제 조건이 README에 누락되어 있고 session.log가 불완전해 독립 재현 가능성이 낮음.


---

---

### R18 cursor-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (파일 목록에 `verify.py` 언급됨, 단 실행 방법 미기재)
- **Key issues**:
  - README에 `verify.py` 실행 방법이 없음 — 파일 목록에만 나열될 뿐, "검증하려면 `python verify.py`를 실행하라"는 지시 없음
  - `run.sh`는 `yolo26n_sync.py` 하나만 실행하지만, README는 4가지 variant(sync, async, sync C++ postprocess, async C++ postprocess)가 있다고 명시 — 나머지 3개를 실행하는 방법 미제공
  - README의 코드 블록이 중첩 backtick 형식 오류(```bash 블록 안에 다시 ``` 로 닫힘)로 렌더링 깨짐 가능성 있음
- **One-sentence verdict**: `bash setup.sh && bash run.sh`로 기본 sync 추론은 동작하지만, 나머지 variant 실행 방법과 검증 절차가 README에 빠져 있어 완전한 end-to-end 재현은 불가능하다.


---

---

### R18 cursor-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **모델 경로 불일치**: `setup.sh`는 모델을 `$DX_STREAM_ROOT/dx_stream/samples/models/yolo26n.dxnn`에 준비하지만, `session.log`의 실제 파이프라인 실행에서는 `/workspace/res/models/models-2_3_0/yolo26n.dxnn`을 사용함. 신규 사용자가 `run.sh`를 실행하면 `setup.sh`에서 준비한 모델 경로와 `pipeline.py`가 사용하는 경로가 달라 파이프라인이 실패할 수 있음
  - **`run_yolo26n_realtime_detection.sh` 내용 미공개**: `run.sh`가 이 래퍼 스크립트에 완전히 위임하는 구조인데, 해당 파일의 내용이 아티팩트에 포함되지 않아 문제 발생 시 디버깅 불가
  - **README의 수동 venv 경로(`../../venv-dx_stream`)**: `setup.sh`는 자동 감지 로직이 있어 견고하지만, README의 직접 실행 예제(`source ../../venv-dx_stream/bin/activate`)는 저장소 구조를 정확히 알아야만 동작하는 하드코딩된 상대 경로를 노출함
- **One-sentence verdict**: `session.log`에서 파이프라인 실행이 확인되었으나, 모델 경로 불일치와 핵심 래퍼 스크립트(`run_yolo26n_realtime_detection.sh`) 내용 미공개로 인해 신규 사용자가 동일 환경이 아닌 경우 첫 실행에 실패할 가능성이 높다.


---

---

### R18 cursor-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `setup.sh`의 모델 다운로드 폴백이 `DX_STREAM_ROOT/setup.sh`를 호출하는데, 이 경로(`../../setup.sh`)가 실제 존재하는지 README에 명시되어 있지 않음. 해당 파일이 없으면 setup이 조용히 실패할 수 있음
  - `session.log`에서 파이프라인이 실제로는 `workspace/res/models/models-2_3_0/` 경로의 모델을 사용했으나, `run_cascaded_yolo26n.sh`나 `pipeline.py`가 README 기준 경로(`dx_stream/samples/models/`)를 올바르게 resolve할지 불확실 — 두 경로 간 불일치가 실환경에서 혼란 유발 가능
  - 독립적인 verification 단계(예: `verify.py` 또는 파이프라인 성공 여부를 확인하는 명령)가 없고, `session.log`가 성공 증거로 제시되었지만 사용자가 직접 재현하는 방법이 README에 안내되지 않음

- **One-sentence verdict**: README와 setup.sh 구조는 대체로 양호하나, 모델 경로 불일치 및 verification 단계 부재로 인해 처음 접하는 사용자가 실행 성공 여부를 확신하기 어려운 PARTIAL 수준임.


---

---

### R18 cursor-cli runtime

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 2
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 1
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh` 파일 없음 — 필수 실행 스크립트가 아예 존재하지 않아, 컴파일 완료 후 어떻게 실행하는지 알 수 없음
  - README.md 코드 블록 형식 오류 — 닫는 ` ``` ` 누락으로 `Session:` 줄이 코드 블록 안에 포함되어 가독성 저해; `launch_compile.py` 파일 존재 여부도 명시 없음
  - `session.log`에 컴파일 완료(`yolo26n.dxnn` 생성) 및 `verify.py` 실행 증거 없음 — pip 설치 로그만 있어 아티팩트가 실제로 생성됐는지 확인 불가; `CALIB_SRC` 경로가 특정 버전(`dx_com-2.3.0`)에 하드코딩되어 환경 의존성 높음

- **One-sentence verdict**: `run.sh` 미존재, 컴파일·검증 실행 증거 부재로 end-user가 이 세션 결과물을 독립적으로 재현하는 것은 불가능하다.


---

---

### R18 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `run.sh`가 실제 추론 스크립트가 아닌 `verify.py --input`을 호출함 — "Run inference"라고 README에 명시되어 있으나 실질적으로 ONNX↔DXNN 비교 검증 스크립트가 실행됨. 순수 추론용 진입점(`<model>_sync.py` 등)이 없어 사용자가 혼란스러울 수 있음
  - `session.log` 마지막 줄 `Cross-Validation: Generated=PASS, Reference=FAIL`에 대한 설명이 README나 Notes에 전혀 없음 — 레퍼런스 컴파일 결과가 왜 FAIL인지 불명확하여 사용자가 세션 결과 전체를 불신할 위험 있음
  - `calibration_dataset/`이 symlink로만 존재하며 원본 경로가 문서화되지 않음 — 다른 머신에서 재현 시 캘리브레이션 데이터 경로가 끊겨 compile.py 재실행이 불가
- **One-sentence verdict**: 컴파일 및 검증(PASS)은 성공적으로 완료되었고 setup.sh 구조도 견고하나, `run.sh`가 추론 진입점 역할을 하지 못하고 `verify.py`로 우회되며 `Reference=FAIL` 항목에 대한 설명이 없어 숙련된 DEEPX 개발자도 아티팩트 신뢰성에 의구심을 가질 수 있다.


---

---

### R18 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `dxrt-cli -s` prerequisite가 README에 언급되지만, 실패 시 대처 방법(설치 명령 등)이 안내되어 있지 않음
  - `session.log` 내 `sanity_check` 섹션이 실제 `sanity_check.sh --dx_rt` 실행 결과가 아닌 import chain test(`--help` 출력) 결과로 대체되어 있어 엄밀한 의미의 Prerequisites 검증 증거로는 부족함
  - README의 File Structure에 `session.json`이 나열되어 있으나 내용이나 용도에 대한 설명이 없어 사용자가 참고할 수 없음

- **One-sentence verdict**: setup.sh의 venv 자동 감지, dx_engine 검증, run.sh의 SUITE_ROOT/PYTHONPATH 처리가 견고하고 실제 추론 성능 수치(38.8 FPS)를 포함한 PASS 증거가 있어 전반적으로 end-user가 그대로 따라 실행 가능한 수준이나, NPU 사전 확인 단계의 실패 가이드가 보완되면 더 완성도가 높아진다.


---

---

### R18 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 내부적으로 `run_detection.sh`를 호출하지만, README의 "Option A" 및 run.sh 자체에서 해당 파일이 session 디렉터리에 존재한다고 가정함 — `setup.sh`는 이 파일을 생성하지 않으며, README의 Files 목록에는 있으나 실제 존재 여부가 불확실해 `run.sh` 실행 시 즉시 실패할 가능성 있음
  - `setup.sh`의 모델 다운로드 경로 (`../../dx_stream/samples/models/`) 및 venv 탐색이 `../../` 상대 경로 가정에 의존하며, session 디렉터리 깊이가 다를 경우 silent fail 발생 가능 (SUITE_ROOT 패턴 미사용)
  - README의 venv 활성화 지침이 "dx_stream root에서 실행"을 전제하지만 session 디렉터리에서 직접 실행하는 사용자는 `../../venv-dx_stream` 경로가 실제로 어디를 가리키는지 파악하기 어려움

- **One-sentence verdict**: `run.sh`가 의존하는 `run_detection.sh`의 생성 여부가 불확실하고 상대 경로 가정이 취약하여, NPU 환경이 올바르게 갖춰진 사용자라도 추가 디버깅 없이 바로 실행 성공하기 어렵다.


---

---

### R18 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `setup.sh`의 경로 계산이 fragile함 — `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"`는 하드코딩된 상대 경로로, 세션 디렉터리 depth가 달라지면 dx_stream root를 잘못 가리킴 (SUITE_ROOT auto-detection 패턴 미사용)
  - `run.sh`가 `run_cascaded.sh`를 호출하지만 해당 파일이 아티팩트 목록에 없음 — `session.log`에서 `dxgather num-sources` 프로퍼티 오류(GStreamer parse 실패)가 발생했고 수정 여부가 불확실하며, `run_cascaded.sh`의 최종 상태를 README가 명시하지 않음
  - Verification 단계 부재 — 파이프라인이 실제로 정상 종료(EOS 수신, 프레임 처리 완료)했다는 증거가 `session.log`에 없고, README에도 성공 기준("출력 영상 확인", "EOS 메시지" 등)이 없어 사용자가 실행 성공 여부를 판단할 수 없음

- **One-sentence verdict**: README와 setup.sh의 구조는 읽기 쉽고 옵션도 충실하나, `run_cascaded.sh` 누락 가능성·GStreamer 파이프라인 오류 미해결 흔적·경로 fragility로 인해 첫 실행 시 사용자가 막힐 가능성이 높다.


---

---

### R18 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **경로 버그 (setup.sh / run.sh)**: `DX_APP_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"` 는 세션 디렉토리(`dx_app/dx-agentic-dev/<session>/`)에서 3단계 위인 `dx-runtime/`을 가리킴. 실제 `dx_app` 루트는 `../..`이어야 함 → 모델 경로(`$DX_APP_ROOT/models/`)가 잘못 해석되어 모델을 찾지 못하고 `[ERROR] Model not found`로 즉시 종료됨.
  - **CLI 플래그 불일치**: README Quick Start는 `--image input.jpg` / `--video input.mp4`를 사용하지만 `run.sh`는 `--input`을 사용함 → 사용자가 README를 그대로 따라 하면 argparse 오류 발생 가능.
  - **session.log 미존재 + venv 없음**: 실행 증거가 전혀 없고, `setup.sh`에 Python venv 생성·활성화 단계가 없어 의존성 설치가 보장되지 않음.

- **One-sentence verdict**: 디렉토리 경로 버그로 인해 모델을 찾지 못하고 즉시 실패하므로, 현재 상태로는 end-user가 README만으로 성공적으로 실행하기 어렵다.


---

---

### R18 opencode-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - `setup.sh` Step 1에서 `sanity_check.sh`에 `2>/dev/null` 리다이렉션 적용 — stderr 진단 메시지가 숨겨져 실패 시 원인 파악이 어려움 (DX 규정: sanity_check는 파이프/리다이렉션 없이 직접 실행해야 함)
  - `install.sh` 실행 후 sanity_check 재확인 없음 — 설치 실패 시 이후 단계가 조용히 진행될 수 있음 (silent recovery)
  - `verify.py`의 예상 출력 형식(예: `RESULT: PASS`)이 README에 명시되어 있지 않아 사용자가 성공/실패 기준을 직접 판단하기 어려움
- **One-sentence verdict**: session.log에 실제 컴파일 출력이 담겨 있고 SUITE_ROOT 패턴·venv 처리가 올바르게 구현되어 있어 전반적으로 실행 가능한 수준이나, sanity_check stderr 억제 및 설치 후 재검증 누락이 운영 환경에서 잠재적 진단 장애물이 될 수 있음.


---

---

### R18 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh`가 `setup.sh`를 `2>/dev/null || true`로 sourcing하므로, dx_engine 미설치 등 치명적 오류가 있어도 자동으로 무시된 채 진행됨 — 이후 발생하는 Python ImportError가 원인 파악을 어렵게 만듦
  - README에 NPU 하드웨어 / dx_engine 사전 설치 요구사항이 명시되어 있지 않아, 처음 접하는 사용자가 `setup.sh` 실패 원인을 알 수 없음
  - `session.log`는 431 bytes로 syntax check + import check만 기록되어 있으며, **실제 추론(inference) 실행 증거가 없음** — "verification provided: N"의 직접적 근거

- **One-sentence verdict**: setup.sh의 venv 탐색 로직과 dx_engine 검증은 잘 설계되어 있으나, run.sh의 setup 오류 묵살 패턴과 실제 추론 실행 증거 부재로 인해 end-user가 문제 발생 시 원인을 파악하기 어렵다.


---

---

### R18 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **상대경로 혼용**: README의 Prerequisites 섹션에서 `cd ../../`로 "dx_stream root"로 이동하라고 하면서, "How to Run" 섹션에서는 다시 세션 디렉터리 기준 `../../` 경로를 사용한다. 어느 디렉터리에서 명령을 실행해야 하는지 일관성이 없어 초행자에게 혼란을 준다.
  - **`run.sh`의 모델 경로 미전달 버그**: `run.sh`는 `$1`을 `MODEL`로 받지만 실제 `run_detection.sh` 호출 시 `"$VIDEO"`만 전달하고 MODEL을 넘기지 않는다. 커스텀 모델 경로를 지정해도 `run_detection.sh`에 반영되지 않는다.
  - **SUITE_ROOT 패턴 미사용**: `setup.sh`와 `run.sh` 모두 `cd "$SCRIPT_DIR/../.."` 방식의 하드코딩된 상대경로를 사용한다. 세션 디렉터리 깊이가 달라지면(cross-project 배치 등) 경로가 깨질 위험이 있다.

- **One-sentence verdict**: session.log로 실제 파이프라인 실행이 확인되고 setup.sh의 venv 자동 탐색 로직은 견고하나, README의 상대경로 혼용과 `run.sh`의 모델 인자 미전달 버그로 인해 초행 사용자가 단독으로 완전히 재현하기 어렵다.


---

---

### R18 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **session.log에 파이프라인 실행 실패 기록**: `Failed to parse pipeline: no property "num-sources" in element "dxgather"` 오류가 명시적으로 기록됨. 두 번째 재시도가 있으나 로그가 잘려 성공 여부 확인 불가 — 세션 자체가 오류 상태로 종료되었을 가능성이 높음
  - **run.sh의 파라미터 버그**: `VIDEO="${3:-$DEFAULT_VIDEO}"` (3번째 인자)로 설정하면서 `DEFAULT_SECONDARY_MODEL`은 `run_cascaded.sh`에 전달되지 않음 — 사용자가 `bash run.sh <primary> <secondary> <video>` 형식으로 호출해도 secondary model 경로가 실제 실행에 반영되지 않음
  - **setup.sh / run.sh의 상대경로(`../..`) 사용**: SUITE_ROOT 자동탐지 패턴 미적용. 세션 디렉토리 깊이가 4단계(`dx-runtime/dx_stream/dx-agentic-dev/<session>/`)임에도 `$(cd "$SCRIPT_DIR/../.." && pwd)`가 `dx_stream` 루트 대신 `dx-runtime`을 가리켜 모델 경로(`dx_stream/samples/models/`) 해석이 잘못될 수 있음

- **One-sentence verdict**: README 구성은 명확하지만, `dxgather` 속성 오류로 인한 파이프라인 실패가 session.log에 기록되어 있고 run.sh의 파라미터 전달 버그가 있어, 사용자가 수정 없이 그대로 실행하면 동일 오류에 봉착할 가능성이 높다.


---

---

### R18 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y (verify.py 참조됨, 내용 미제공)

- **Key issues**:
  - **session.log 없음**: 실행 증거가 전혀 없어 에이전트가 실제로 artifact를 실행했는지 확인 불가 — Artifact Verification Gate 위반
  - **setup.sh가 venv/pip 설치를 수행하지 않음**: 부모 디렉터리의 `setup.sh --model=yolo26n.dxnn` 호출에 전적으로 의존하며, 실패 시 `[WARN]`으로 묵살 처리됨 — 사용자는 모델이 어느 경로에 설치됐는지 알 수 없어 `--model /path/to/yolo26n.dxnn` 인자를 직접 지정할 수 없음
  - **dx_stream 실행 경로가 하드코딩된 상대 경로**: `../../../dx_stream/dx-agentic-dev/20260515-025744_.../run_yolo26n_pipeline.sh` — 실행 위치에 따라 경로가 깨지며, SUITE_ROOT 패턴이 적용되지 않음

- **One-sentence verdict**: setup.sh가 모델 경로를 확정짓지 못하고, session.log가 부재하여 실행 검증이 불가능한 상태로, 전형적인 end-user가 설명만 따라 즉시 동작시키기에는 불충분한 수준이다.


---

---

### R18 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh`에서 `export PYTHONPATH`로 설정한 값이 별도의 `bash run.sh` 프로세스에 **전달되지 않음** — `run.sh` 실행 시 dx_com/dx_engine import가 실패할 수 있음 (가장 심각한 문제)
  - README에 사전 요구사항(dxcom 설치 여부, Python 버전, venv-dx-compiler-local 존재 가정 등)이 명시되어 있지 않아 처음 사용자가 실패 원인을 파악하기 어려움
  - `setup.sh`의 `.whl` glob 패턴(`[ -f .../*.whl ]`)은 파일이 0개이거나 2개 이상일 때 불안정하게 동작함

- **One-sentence verdict**: Quick Start(`bash setup.sh && bash run.sh`)는 단계 자체는 간결하지만, PYTHONPATH 환경 변수가 서브쉘 간에 전파되지 않아 실제 사용자 환경에서 `verify.py` 실행이 실패할 가능성이 높다.


---

---

### R18 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **venv 활성화가 run.sh에 전파되지 않음**: `setup.sh`는 서브쉘에서 `source venv/bin/activate`를 실행하지만, `run.sh`가 `bash setup.sh`로 호출하면 venv 활성화가 부모 쉘에 적용되지 않는다. 이후 `python yolo26n_sync.py` 호출은 시스템 Python을 사용하므로 `dx_engine` import 실패 가능성이 높음.
  - **실제 추론 실행 증거 없음**: `session.log`에 syntax check·import check는 있으나 `python yolo26n_sync.py --model ... --image ...` 실제 실행 결과가 없음. Artifact Verification Gate 요건 미충족.
  - **README 코드 펜스 미닫힘**: README 마지막 Notes 섹션이 코드 블록 안에 포함되어 있어 렌더링 시 비정상 표시됨 (열린 `` ``` `` 에 닫힘 없음).

- **One-sentence verdict**: setup.sh→run.sh 간 venv 전파 결함과 실제 추론 실행 증거 부재로 인해 end-user가 그대로 실행 시 `dx_engine` import 오류로 실패할 가능성이 높아 PARTIAL 판정.


---

---

### R18 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **실제 파이프라인 실행 증거 없음**: `session.log`가 `pipeline.py --help`, syntax check, 플러그인 확인에 그치며, 실제 영상 프레임을 처리한 end-to-end 실행 출력이 없음. 유저가 "정말 동작하는가"를 독립적으로 확인할 수 없음.
  - **Run Option 3개로 진입점 혼란**: README가 Option A(run.sh) / Option B(run_yolo26n_realtime_detection.sh) / Option C(python3 pipeline.py 직접) 세 가지를 나열하지만, 어느 것을 먼저 시도해야 하는지 우선순위가 없음. 특히 `run.sh`가 내부적으로 `run_yolo26n_realtime_detection.sh`를 호출하므로 B와 A의 차이가 모호함.
  - **`SRC_DIR` 이중 경로 잠재 오류**: `setup.sh`에서 `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"` 후 `SRC_DIR="$DX_STREAM_ROOT/dx_stream"`으로 설정하는데, 세션 디렉터리가 `dx-runtime/dx_stream/dx-agentic-dev/<session>/`이면 `DX_STREAM_ROOT`=`dx-runtime/dx_stream/`이고 `SRC_DIR`=`dx-runtime/dx_stream/dx_stream/`이 되어 서브디렉터리 구조에 따라 모델·샘플 경로가 깨질 수 있음.

- **One-sentence verdict**: setup 자동화와 README 상세도는 양호하나, 실제 파이프라인 실행 증거가 없고 진입점이 세 갈래로 분산되어 있어 독립 실행 신뢰성이 PARTIAL에 머무름.


---

---

### R18 codex-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - `run.sh`이 내부적으로 `run_cascaded_yolo26n.sh`에 위임하는데, 이 스크립트가 artifacts 목록에 있지만 내용이 제공되지 않아 실제 위임 로직 확인 불가 (README Files 표에는 언급됨)
  - README.md의 마지막 코드 블록(Files 표)의 닫는 ` ``` `이 누락되어 마크다운 렌더링 시 깨짐
  - Prerequisites 3번 항목이 `cd ../../ && ./setup.sh --model=...`로 되어 있어 세션 디렉터리 기준 상대경로가 모호하고, `setup.sh` 내부 `ensure_model` 함수와 역할이 중복됨
- **One-sentence verdict**: 모델·플러그인·라이브러리 확인이 자동화되고 session.log에 실제 파이프라인 실행 증거가 있어 전반적으로 end-user가 따라 실행할 수 있으나, `run_cascaded_yolo26n.sh` 내용 미확인 및 README 마크다운 깨짐이 사소한 불편을 초래한다.


---

---

### R18 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `run.sh`가 `setup.sh`를 `>/dev/null 2>&1 || true`로 호출하여 setup 실패(예: dx_engine 미설치)가 **무음으로 무시**됨. 이후 python 실행에서 원인 불명 오류 발생
  - `session.log` 첫 줄에 `Date: $(date)` 가 미展開된 채로 기록됨 → heredoc 단일 따옴표 패턴(`<< 'EOF'`) 사용으로 fabrication 의심. 실제 명령 출력 캡처가 아님
  - `dxrt-cli -s` (Prerequisites 1번)가 실행 환경에서 찾을 수 없음(exit 127). README에 필수 체크로 안내하지만 실패 시 대응 방법 미제공. 또한 실제 inference 실행 결과(smoke run)가 session.log에 없어 end-to-end 검증 미완료
- **One-sentence verdict**: README·run.sh 구조는 양호하나, run.sh의 setup 오류 묵살, session.log 부분 fabrication, 실제 inference 실행 증거 부재로 사용자가 환경 문제에 봉착했을 때 스스로 진단하기 어렵다.


---

---

### R19 cursor-cli compiler

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 1
- **Setup completeness (1-5)**: 1
- **Run instructions completeness (1-5)**: 1
- **Verification provided (Y/N)**: N
- **Key issues**:
  - 세션 출력 디렉토리에 필수 파일(README.md, setup.sh, run.sh, session.log)이 **모두 존재하지 않음** — 아티팩트 자체가 생성되지 않은 상태
  - end-user가 따라야 할 설치·실행 지침이 전무하여 재현 불가
  - 세션 완료 여부 자체가 불확실 (DONE sentinel 없이 종료됐을 가능성)
- **One-sentence verdict**: 모든 필수 아티팩트가 누락되어 있어 end-user가 이 세션의 결과물을 설치하거나 실행하는 것이 **불가능**하다.


---

---

### R19 cursor-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `source setup.sh 2>/dev/null || true` 패턴으로 setup 실패를 무시함 — `dx_engine` 누락 시 setup.sh의 명확한 오류 메시지 대신 Python ImportError로 빠져나와 디버깅이 어려워짐
  - README Prerequisites의 `dxrt-cli -s` 명령이 설명 없이 언급됨 — 처음 접하는 사용자에게 불투명
  - `session.log`는 실제 실행 결과를 담고 있으나 `[truncated]`로 잘려 inference 결과 전체(bounding box 출력 등)가 확인 불가

- **One-sentence verdict**: Quick Start 3단계 흐름이 명확하고 session.log에 실제 추론 실행 증거(20.92ms inference, `--help` 출력)가 포함되어 있어 전반적으로 신뢰할 수 있는 아티팩트이나, run.sh의 setup 오류 억제 패턴이 환경 문제 발생 시 사용자 혼란을 유발할 수 있다.


---

---

### R19 copilot-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **[CRITICAL] session.log가 컴파일 오류에서 truncated**: 로그가 `DataLoaderError: The config specifies (1, 640, 640, 3), but model requires (1, 3, 640, 640)` 오류 발생 직후 `[truncated]`로 잘려 있어, README에서 주장하는 "Overall: PASS / yolo26n.dxnn 생성 완료"가 실제 성공인지 확인 불가. `yolo26n.dxnn` 파일 존재 여부가 불확실하므로 end-user가 run.sh 실행 시 파일 없음 오류 가능성 있음.
  - **README Quick Start와 run.sh 간 인터페이스 불일치**: README는 `python verify.py`(인자 없음)를 안내하나, run.sh은 `python verify.py --dxnn yolo26n.dxnn --image <경로>`로 인자를 포함해 호출함. 사용자가 README만 보고 직접 실행하면 동작이 다를 수 있음.
  - **setup.sh 내 `source venv/bin/activate`는 호출 쉘에 반영되지 않음**: `bash setup.sh` 실행 후 venv가 활성화된 상태로 남지 않아, 사용자가 별도로 `source venv/bin/activate`를 해야 함. README가 이를 안내하긴 하나, 초보 사용자는 setup.sh이 완전히 환경을 준비해 준다고 오해할 수 있음.

- **One-sentence verdict**: README와 스크립트 구성은 전반적으로 충실하나, session.log가 컴파일 오류 직후 truncated되어 핵심 산출물(yolo26n.dxnn)의 실제 생성 여부를 검증할 수 없고 README와 run.sh 간 인터페이스 불일치도 있어 **end-user가 그대로 따라할 경우 실패할 리스크가 존재한다**.


---

---

### R19 copilot-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - **모델 파일 취득 경로 불명확**: `run.sh`의 에러 메시지에는 `download_models.py --model yolo26n`가 언급되지만, README에는 모델 파일(`yolo26n.dxnn`)을 어떻게 준비하는지 명시적 안내가 없어 처음 접하는 사용자가 막힐 수 있음
  - **venv 없음 / 시스템 패키지 의존**: `setup.sh`가 venv를 생성하지 않고 `dx_engine`, `dx_postprocess`가 시스템에 이미 설치되어 있다고 가정함 — `./install.sh && ./build.sh`를 별도로 실행하지 않은 환경에서는 import 오류 발생 가능
  - **헤드리스 환경에서 display 오류 위험**: `run.sh`에 `--no-display` 플래그가 없어 GUI 없는 서버 환경에서 디스플레이 에러 발생 가능 (session.log의 cross-validation은 `--no-display`를 사용했음에도 run.sh는 미적용)
- **One-sentence verdict**: Quick Start(`bash setup.sh && bash run.sh`)는 NPU와 dx_app 빌드가 이미 완료된 환경에서는 작동하지만, 모델 파일 취득 안내 부재와 venv 미생성으로 인해 신규 환경에서는 중간 단계에서 막힐 가능성이 높다.


---

---

### R19 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

**Key issues:**
- README가 `../../` 상대 경로 명령어(venv 활성화, 모델 다운로드 등)를 실행하기 전에 **세션 디렉토리로 `cd` 하라는 안내가 없음** — 사용자가 임의의 디렉토리에서 실행하면 경로가 깨짐
- `run.sh`가 내부적으로 `run_yolo26n_detection.sh`를 호출하지만, 이 스크립트의 인자 처리 방식이 README에서 검증되지 않음 (Option C "One-command launcher"가 실제로 동작한다는 보장 부족)
- `setup.sh`의 모델 경로 탐색이 `../..` 2단계 상위 고정 가정에 의존 — 세션 디렉토리 깊이가 달라지면 모델 경로 해석 실패 가능성 있음 (단, session.log의 실제 경로로 볼 때 이번 세션은 정상 동작함)

**One-sentence verdict**: session.log에 실제 파이프라인 실행 증거가 있고 setup.sh/README 구조도 전반적으로 충실하나, **"세션 디렉토리로 먼저 이동"** 안내 누락과 `run.sh → run_yolo26n_detection.sh` 의존 관계의 불투명성 때문에 처음 접하는 사용자가 모든 옵션을 바로 성공시키기는 어렵다.


---

---

### R19 copilot-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `run.sh`가 `MODEL="${1:-...}"` 인자를 파싱하지만 실제로는 `bash run_cascaded.sh "$VIDEO"`만 호출해 모델 경로 오버라이드가 **묵살**됨 — 커스텀 모델 지정 기능이 동작하지 않음
  - `setup.sh`가 `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"` 하드코딩을 사용해 세션 디렉터리 깊이가 달라지면 모델 경로(`dx_stream/samples/models/`)가 틀어짐 (SUITE_ROOT 자동 탐지 패턴 미적용)
  - `verify.py` 미제공 — pipeline.py 실행 성공 여부를 재현 가능하게 검증할 수단이 없음; `session.log`의 실행 증거만으로는 사용자가 직접 재검증 불가
- **One-sentence verdict**: setup과 session.log 실행 증거는 충분하나, `run.sh`의 모델 인자 묵살 버그와 verify.py 부재로 인해 처음 접하는 사용자가 완전하게 실행·검증하기 어려운 **PARTIAL** 수준이다.


---

---

### R19 copilot-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - **session.log 없음**: 에이전트가 실제로 코드를 실행한 증거가 전혀 없음. 필수 아티팩트(`session.log`)가 생성되지 않아 end-user가 "이 코드가 실제로 동작하는가"를 확인할 방법이 없음.
  - **모델 파일 취득 방법 누락**: `run.sh`는 `${ASSETS_DIR}/models/yolo26n.dxnn` 경로를 기대하지만, README Quick Start에는 `.dxnn` 파일을 어떻게 준비해야 하는지 명시적 안내가 없음. `run.sh` 내부에 `download_models.py` 힌트가 있으나 README에서 언급되지 않아 사용자가 찾기 어려움.
  - **venv/pip 설치 단계 없음**: `setup.sh`가 Python 환경 설치(venv 생성, 의존성 `pip install`)를 수행하지 않고 단순 import 확인만 함. 시스템에 `dx_engine`/`dx_postprocess`가 없을 경우 `./install.sh && ./build.sh`를 실행하지만, 이 스크립트들의 위치나 사전 조건을 README에서 안내하지 않음.
- **One-sentence verdict**: 아티팩트 구조와 코드 품질은 양호하나, session.log 부재로 실행 증거가 없고 모델 파일 준비 방법이 README에서 누락되어 있어 처음 접하는 사용자가 독립적으로 실행하기 어렵다.


---

---

### R19 codex-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y (부분적)
- **Key issues**:
  - `setup.sh`의 `pip install` 목록에 `onnxscript`가 누락됨 — `session.log`에서 export 단계 중 `ModuleNotFoundError: No module named 'onnxscript'`로 실패한 것이 확인되며, 에이전트가 런타임 중 수동으로 설치했으나 `setup.sh`에 반영되지 않아 재현 시 동일한 오류 발생 가능
  - `setup.sh`의 sanity check 실패 처리가 `|| true`로 묵음 처리되어 있어, NPU 환경 문제 발생 시 사용자에게 아무런 안내 없이 진행됨
  - README의 Verification 섹션에서 레퍼런스 모델(`dx-runtime/dx_app/assets/models/yolo26n.dxnn`)이 FAIL이라고 명시되어 있어 — "무엇이 맞는 결과인지"가 불분명하고 사용자 혼란 유발 가능
- **One-sentence verdict**: `setup.sh`에 `onnxscript` 의존성이 누락되어 있어 클린 환경에서 재현 시 동일한 오류가 재발할 가능성이 높으며, 전체적인 구조는 갖추어져 있으나 신뢰도 있는 재현 가능성은 보장되지 않는다.


---

---

### R19 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - **sanity_check 실패 + 미해결**: `session.log`에서 `dxrt-cli` 및 `sanity_check.sh` 모두 `command not found` / `No such file` 로 FAIL을 기록했으나, 에이전트가 복구 조치를 취하지 않고 세션을 완료했음. README에 이에 대한 언급 없음.
  - **Python 파일 syntax check 오류**: `session.log`에서 for-loop 내 `py_compile.compile('')` 에 빈 파일명이 전달되어 4개 runner 스크립트 모두 `FileNotFoundError`로 실패. 실제 syntax 검증이 수행되지 않았음.
  - **verify.py 미포함**: 의무 deliverable인 `verify.py`가 README 파일 목록에 없고 세션 디렉터리에도 생성되지 않았음. ONNX↔DXNN 수치 비교 불가.

- **One-sentence verdict**: sanity check 실패 미복구, runner 스크립트 syntax 검증 누락, verify.py 부재로 인해 사용자가 `bash setup.sh && bash run.sh`까지는 시도할 수 있으나 실행 성공 여부를 확인할 수단이 없어 PARTIAL 판정.


---

---

### R19 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

**Key issues**:
- README의 `setup.sh` 사용법이 혼란스러움 — Prerequisites 섹션에서 `../../setup.sh --model=...`를 직접 호출하도록 안내하지만, 실제 `setup.sh`는 세션 내부에서 자동으로 이 명령을 실행하는 구조여서 중복·충돌 가능성이 있음
- `run.sh`에 위임하는 `run_yolo26n_realtime.sh`가 artifacts 목록에 있으나, README/session.log에서 그 내용이 공개되지 않아 end-user가 해당 스크립트의 동작을 검증할 수 없음
- `run.sh`의 인자 처리 구조(`$1`=모델, `$2`=입력, `$3`=출력)가 README의 `bash run.sh` 원커맨드 런처 설명과 불일치 — 인자 없이 실행 시 `INPUT_SPEC` 빈값을 `run_yolo26n_realtime.sh`에 빈 문자열로 넘기는 동작이 명문화되지 않음

**One-sentence verdict**: pipeline 실행 증거(session.log 90프레임 성공)는 충분하나, `run.sh` 인자 구조와 README 설명 간의 불일치 및 `run_yolo26n_realtime.sh` 내용 미공개로 인해 end-user가 독립적으로 실행·검증하기에는 일부 불명확한 부분이 남아 있다.


---

---

### R19 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N
- **Key issues**:
  - README Prerequisites Step 3이 `./setup.sh --model=<name>` 형식으로 부모 디렉터리의 `setup.sh`를 호출하도록 안내하지만, 세션 내 `setup.sh`는 `--model` 인자를 지원하지 않아 사용자가 혼란스러울 수 있음
  - 실제 파이프라인 실행의 핵심 진입점인 `run_cascaded_yolo26n.sh`이 파일 목록에만 언급되고 내용이 artifacts에 미포함됨 — `run.sh`가 이 파일에 전적으로 위임하므로 해당 파일 부재 시 실행 불가
  - `session.log`가 `cascaded...[truncated]`로 끊겨 파이프라인 end-to-end 실행 성공 증거가 없으며, 검증은 syntax check + `--help` 수준에 그침
- **One-sentence verdict**: 디렉터리 구조를 미리 아는 사용자라면 `run_cascaded_yolo26n.sh`이 존재할 경우 동작할 수 있으나, 이 파일의 내용이 artifacts에 없고 실제 실행 증거도 부재하여 신뢰도 있는 재현 보장이 어렵다.


---

---

### R19 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README의 `cd dx_app/dx-agentic-dev/...` Quick Start 경로가 어떤 디렉터리에서 실행해야 하는지 명시하지 않음 (dx-runtime/ 기준인지 suite root 기준인지 불명확)
  - `bash scripts/sanity_check.sh --dx_rt` Prerequisites 경로가 상대 경로인데 실행 기준 디렉터리가 누락되어 있음; GStreamer 전용 명령어인 `gst-inspect-1.0 dxinfer`가 standalone detection 앱에 불필요하게 포함됨
  - `setup.sh`에서 `venv-dx-runtime`을 찾지 못하면 로컬 venv를 생성하지만, 해당 venv에는 `dx_engine`이 없어 `[FATAL]`로 종료됨 — 사용자가 `./install.sh && ./build.sh`를 먼저 실행해야 한다는 안내가 README에 누락됨

- **One-sentence verdict**: sanity check 및 inference 실행 증거(session.log)가 실제 출력으로 확인되어 아티팩트 자체는 정상이나, README의 실행 디렉터리 명시 부재와 `dx_engine` 사전 빌드 요건 안내 누락으로 인해 초면 사용자가 독립적으로 실행하기에는 추가 안내가 필요하다.


---

---

### R19 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`run.sh`가 `verify.py`를 직접 호출함** — README Quick Start에서 `bash run.sh`는 "inference 실행"으로 설명되지만, 실제 내부는 `python3 verify.py --dxnn ... --image ...`를 실행한다. 결과적으로 `bash run.sh`와 `python3 verify.py` 두 단계가 동일한 작업을 수행하므로 사용자에게 혼란을 준다.
  - **`setup.sh`의 sanity check 실패가 무음 처리됨** — `bash sanity_check.sh ... || bash install.sh ... || true` 패턴으로 인해 dx-runtime 환경 이상이 있어도 `setup.sh`가 exit 0으로 완료된다. 사용자는 환경이 비정상이라는 사실을 모른 채 다음 단계로 진행할 수 있다.
  - **`calibration_dataset`이 symlink이며 이식성 경고 없음** — README에 symlink로 명시되어 있으나, 세션 디렉토리를 다른 위치로 복사하거나 zip으로 공유하면 symlink가 깨진다는 주의사항이 없다.

- **One-sentence verdict**: README 구조와 검증 결과는 잘 정리되어 있으나, `run.sh`가 `verify.py`를 호출하는 이중성과 setup 실패 무음 처리로 인해 처음 사용하는 개발자가 혼란을 겪을 가능성이 있어 PARTIAL 판정.


---

---

### R19 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y
- **Key issues**:
  - README Quick Start의 `cd dx_app/dx-agentic-dev/...` 경로가 어느 디렉터리 기준 상대 경로인지 명시되지 않음 (`dx-runtime/` 기준인지, repo root 기준인지 불명확)
  - Prerequisites에 `gst-inspect-1.0 dxinfer`(GStreamer 체크)가 포함되어 있으나 standalone dx_app 태스크와 무관 — 첫 사용자에게 불필요한 혼란 유발
  - `setup.sh`에서 `venv-dx-runtime`을 찾지 못할 경우 local venv를 생성하지만 `dx_engine`이 설치되지 않아 `[FATAL]`로 즉시 종료됨 — 오류 메시지에 `[HINT]`가 있으나 구체적인 복구 명령이 없어 초보자가 조치하기 어려움
- **One-sentence verdict**: `session.log`에서 sanity check PASS 및 실제 inference 성공이 확인되어 실행 환경만 갖추어져 있다면 동작 가능하지만, README의 모호한 상대 경로 기준과 불필요한 GStreamer 전제 조건이 초기 실행 장벽을 높임.


---

---

### R19 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **모델 경로 불일치**: `session.log`에서 실제 실행 시 사용된 모델 경로는 `workspace/res/models/models-2_3_0/yolo26n.dxnn`이지만, `run.sh`의 `DEFAULT_MODEL`은 `DX_STREAM_ROOT/dx_stream/samples/models/yolo26n.dxnn`을 가리킨다. `DX_STREAM_ROOT`가 세션 디렉터리 2단계 위(`dx-runtime/dx_stream/`)이면 `SRC_DIR = .../dx_stream/dx_stream/`이 되어 **이중 경로 버그**가 발생한다 — 엔드유저는 모델 not found 오류를 바로 맞이하게 된다.
  - **`run_detection.sh` 미제공**: `run.sh`의 실제 실행 진입점이 `run_detection.sh`에 위임되어 있으나, 이 스크립트는 아티팩트 목록에 있을 뿐 내용이 검증되지 않았다. 없거나 잘못된 경우 전체 실행이 차단된다.
  - **README 상대 경로 컨텍스트 누락**: 모든 `../../` 경로가 "세션 디렉터리 기준"임을 명시하지 않아, 사용자가 어느 위치에서 명령을 실행해야 하는지 불분명하다.

- **One-sentence verdict**: 파이프라인이 에이전트 환경에서는 성공적으로 실행된 증거(session.log)가 있으나, 모델 경로 이중 중첩 버그와 `run_detection.sh` 의존성으로 인해 새로운 환경에서는 엔드유저가 별도 경로 수정 없이 즉시 실행하기 어렵다.


---

---

### R19 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **상대 경로 의존성**: `setup.sh`와 `run.sh`가 `../../`(dx_stream 루트 기준) 고정 상대 경로를 사용하며, SUITE_ROOT 자동 감지 패턴을 사용하지 않아 세션 디렉토리 깊이가 다를 경우 경로가 틀림. README의 venv 활성화 경로(`../../venv-dx_stream/bin/activate`)도 동일한 취약점 존재.
  - **run.sh → run_cascaded.sh 인자 불일치**: `run.sh`는 `$MODEL`을 파싱하지만 실제 실행 시 `bash run_cascaded.sh "$VIDEO"`만 전달하고 `$MODEL`은 넘기지 않음 — 커스텀 모델 경로를 첫 번째 인자로 전달해도 무시됨.
  - **session.log에 pipeline 실패가 기록됨**: `dxgather`의 `num-sources` 프로퍼티 오류로 첫 실행이 실패했고, "fix: removed num-sources" 재시도 로그가 있음. 최종 `pipeline.py`에 이 수정이 반영되었는지 `session.log`가 잘려 있어 확인 불가.

- **One-sentence verdict**: README는 가독성이 높지만 상대 경로 의존성과 `run.sh`의 모델 인자 전달 버그, 그리고 pipeline 실패 후 수정 반영 여부가 불확실하여 초기 환경 구성 이외의 상황에서 end-user가 성공적으로 실행하기 어려울 수 있다.


---

---

### R19 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 2
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **`setup.sh`가 Python 환경(venv/pip) 구성을 수행하지 않음** — 모델 파일 존재 여부 확인 및 `dxrt-cli -s` 호출만 수행. `venv-dx_app` 생성이나 의존성 설치가 없어, dx_app 빌드(`./install.sh && ./build.sh`)가 선행 완료된 환경이 아니면 `run.sh`의 venv 활성화 단계가 조용히 스킵됨
  - **`session.log`에 실제 추론 실행 증거 없음** — verify.py의 30개 PASS는 전부 파일 존재·구문·JSON 정적 검사이며, `python3 yolo26n_sync.py --image sample.jpg` 등 실제 NPU 추론 실행 결과가 전혀 없음 (Artifact Verification Gate 위반)
  - **README에 전제 조건 누락** — `dx_app` 빌드 완료(`./install.sh && ./build.sh`), `venv-dx_app` 존재, 모델 사전 다운로드 필요성이 명시되지 않아 첫 사용자가 `run.sh` 실행 시 원인 불명의 오류에 직면할 가능성이 높음

- **One-sentence verdict**: 파일 구조와 run.sh 사용법은 명확하나, setup.sh가 Python 환경을 구성하지 않고 session.log에 실제 NPU 추론 실행 증거가 없어 독립 실행 가능성을 보장하기 어렵다.


---

---

### R20 copilot-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 5
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

**Key issues**:
- README Quick Start 2단계의 명령어(`python verify.py --image /path/to/image.jpg`)가 `--dxnn yolo26n.dxnn` 인수를 누락함 — `run.sh`의 실제 호출과 불일치. verify.py에 기본값이 없다면 명령 실패 가능성 있음
- Cross-Validation 섹션의 "Precompiled reference: FAIL" 문구가 맥락 없이 읽히면 세션 자체가 실패한 것으로 오해될 수 있음 (실제로는 생성된 모델이 더 우수하다는 설명임)
- `session.log`가 컴파일 출력만 포함하고 `verify.py` 실행 결과는 누락되어 있어, README에 기재된 PASS 증거가 로그로 뒷받침되지 않음

**One-sentence verdict**: setup.sh와 run.sh는 SUITE_ROOT 패턴과 venv를 올바르게 적용하여 완성도가 높으나, README Quick Start의 명령어 인수 누락과 session.log의 검증 출력 부재로 인해 완전한 신뢰도에 소폭 미달한다.


---

---

### R20 copilot-cli dx_app

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y
- **Key issues** (if any):
  - README의 `setup.sh` 사용법이 `bash setup.sh` 한 줄에 그치며, venv 활성화 여부를 사용자가 확인하는 방법이 안내되어 있지 않음
  - `setup.sh`에서 `dx_engine` 불가 시 출력하는 fix 경로(`cd $SCRIPT_DIR/../..`)가 모든 환경에서 정확하지 않을 수 있음 (dx_app 루트가 아닌 경우)
  - session.log의 artifacts 목록에 `yolo26n.dxnn` 파일이 없음 — README가 모델 파일이 `../../assets/models/`에 사전 존재함을 전제하나, 해당 파일 획득 방법이 명시되어 있지 않음
- **One-sentence verdict**: 실제 실행 증거(sanity check PASS, inference RESULT: PASS, 성능 수치)가 session.log에 포함되어 있고 run.sh의 4개 variant 진입점이 명확해 대부분의 사용자가 문제없이 실행할 수 있으나, `.dxnn` 모델 파일 사전 준비 안내가 빠져 있어 신규 사용자에게는 소폭 장벽이 될 수 있음.


---

---

### R20 copilot-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`의 경로 계산(`../../`)이 하드코딩되어 있어 세션 디렉터리 깊이가 다를 경우 모델/비디오 경로가 잘못 해석됨 (`dx_stream/dx-agentic-dev/<session>/` 기준이면 `../..`는 `dx_stream/` 루트가 아닌 `dx-runtime/`을 가리킬 수 있음)
  - `setup.sh`의 모델 다운로드 단계가 `../../setup.sh --model=...`를 호출하지만, 세션 루트에서 실행할 때 해당 경로가 존재하는지 README에서 사전 확인하는 안내가 없음; `run.sh`도 `run_yolo26n_detection.sh`에 위임하지만 해당 파일의 내용은 아티팩트에 포함되지 않아 사용자가 별도로 확인해야 함
  - 세션 디렉터리를 기준으로 한 상대 경로(`../../venv-dx_stream`)가 README와 `setup.sh` 간 일관성이 있으나, SUITE_ROOT 자동 감지 패턴(dx-compiler/dx-runtime 형제 탐색 루프) 대신 고정 깊이 탐색을 사용하고 있어 배포 환경에 따라 경로 오탐 위험 있음

- **One-sentence verdict**: session.log에 실제 파이프라인 실행 증거가 있고 다양한 실행 옵션을 제공하나, 상대 경로 하드코딩과 위임 스크립트(`run_yolo26n_detection.sh`) 누락으로 인해 처음 접하는 사용자가 독립 실행에 실패할 가능성이 있다.


---

---

### R20 copilot-cli dx_stream_cascaded

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 5
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 `setup.sh`를 `2>/dev/null || true`로 source — setup 실패(venv 미활성화, 모델 미존재 등)를 묵묵히 무시하고 진행하여, 사용자가 원인 파악 없이 이후 오류에 직면할 수 있음
  - README 전반의 `../../` 상대경로 안내(예: `cd ../../`, `source ../../venv-dx_stream/…`)가 세션 디렉토리 위치를 사전에 알아야만 해석 가능 — 처음 진입하는 사용자에게 혼란 유발 가능
  - `run_cascaded.sh`가 `run.sh` 및 README에서 핵심 진입점으로 참조되나, 해당 파일의 내용이 평가 artifacts에 포함되지 않아 내부 구현 및 오류 처리 수준을 독립 검증 불가

- **One-sentence verdict**: README가 파이프라인 다이어그램·다중 실행 옵션·실제 실행 로그를 포함하여 전반적으로 우수하나, `run.sh`의 setup 오류 묵살 패턴과 상대경로 중심 안내가 신규 사용자의 초기 셋업 실패 시 디버깅을 어렵게 한다.


---

---

### R20 copilot-cli runtime

- **end-user runnability**: FAIL
- **README clarity (1-5)**: 2
- **Setup completeness (1-5)**: 1
- **Run instructions completeness (1-5)**: 2
- **Verification provided (Y/N)**: N
- **Key issues**:
  - `setup.sh`, `run.sh`, `session.log` 세 파일 모두 누락 — 환경 설정 및 원클릭 실행 수단이 전혀 없음
  - README의 Prerequisites에 `./setup.sh` 실행을 언급하지만 해당 파일이 존재하지 않아 모순 발생; `.dxnn` 모델 파일 획득 방법도 명시되지 않음
  - 실행 증거(`session.log`)가 없어 아티팩트가 실제로 동작했는지 확인 불가
- **One-sentence verdict**: 필수 아티팩트(`setup.sh`, `run.sh`, `session.log`)가 모두 누락되어 사용자가 환경 구성부터 실행·검증까지의 어떤 단계도 가이드 없이 수행할 수 없으며, 이 세션은 **최소 납품 기준을 충족하지 못함**.


---

---

### R20 codex-cli compiler

- **end-user runnability**: PASS
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `setup.sh` sanity check 실패 시 `|| true`로 강제 통과 처리 — NPU 초기화 실패를 묵인하고 진행되어 사용자가 문제를 인지하지 못할 수 있음
  - `README.md` 마크다운 코드 블록 중첩 오류 — Quick Start 펜스(`` ``` ``)가 외부 코드 블록 내에 위치해 일부 렌더러에서 조기 종료됨 (파일 목록이 코드 블록 밖으로 이탈)
  - `detect_yolo26n.py`가 파일 목록에는 있으나 동작 방식·출력 형식에 대한 설명 없음 — 사용자가 결과를 해석하기 어려울 수 있음

- **One-sentence verdict**: 실제 실행 근거(session.log), 올바른 SUITE_ROOT 패턴, 실측 검증 수치(MAE)가 모두 갖춰져 있어 DEEPX SDK 개발자라면 큰 어려움 없이 재현 가능하나, 일부 사소한 스크립트·문서 결함이 있음.


---

---

### R20 codex-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - README의 Setup 섹션에 `cd dx-agentic-dev/<session_id>` placeholder가 그대로 남아 있어, 사용자가 실제 세션 디렉토리 이름을 직접 찾아야 함
  - `session.log`에서 `dxrt-cli: command not found`로 sanity check FAIL이 기록되었으나 README에 아무런 언급이 없어, 처음 접하는 사용자가 환경 문제로 오인할 수 있음
  - `run.sh`에서 `source setup.sh 2>/dev/null || true`로 setup 에러를 묵살하므로, setup 실패 시 사용자가 원인을 파악하기 어려움

- **One-sentence verdict**: 추론 실행 자체는 실제로 성공(RESULT: PASS)했으나, README의 placeholder와 sanity check 실패에 대한 안내 부재로 신규 사용자가 혼란 없이 처음부터 끝까지 따라가기 어렵다.


---

---

### R20 codex-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `run.sh`가 내부적으로 `run_yolo26n_realtime_detection.sh`를 호출하지만, README의 "One-command launcher" 섹션에는 `bash run.sh`만 안내되어 있어 사용자가 실제 래퍼 스크립트의 존재를 모르면 경로 오류 발생 가능
  - Prerequisites의 상대 경로(`cd ../../`)가 세션 디렉터리 깊이를 전제로 하여, 사용자가 다른 위치에서 실행하거나 디렉터리 구조가 다를 경우 `./install.sh`, `./setup.sh --model=` 등의 명령이 실패할 수 있음
  - 실제 파이프라인 실행(GStreamer NPU 추론)에 대한 end-to-end 검증 로그가 없고, `session.log`는 syntax check와 `--help` 수준에 머물러 있어 실제 동작 확인이 불가

- **One-sentence verdict**: 스크립트 구조와 setup 로직은 비교적 잘 갖춰져 있으나, 상대 경로 의존성과 실제 파이프라인 실행 검증 증거의 부재로 인해 사용자가 독립적으로 재현하기엔 불확실성이 남는다.


---

---

### R20 codex-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **Venv 전파 버그**: `run.sh`가 `bash setup.sh`를 서브셸로 호출하므로 `setup.sh` 내부의 `source venv/bin/activate`가 `run.sh` 셸에 전파되지 않는다. 이후 `run_cascaded.sh` 호출 시 `gi` 모듈 누락으로 실패한다. session.log에서도 동일 증상 확인 (`ModuleNotFoundError: No module named 'gi'`); 수동으로 venv를 source한 후에야 `--help`가 정상 동작함.
  - **README에 실행 위치(cd 경로) 미명시**: `../../venv-dx_stream/`, `../../dx_stream/samples/` 등 상대 경로를 사용하지만 "먼저 세션 디렉터리로 이동하라"는 안내가 없어 다른 위치에서 실행 시 경로 오류 발생.
  - **`run_cascaded.sh` 미검증**: `run.sh`와 README Option B 모두 `run_cascaded.sh`에 의존하지만 해당 파일의 내용이 아티팩트에 포함되지 않았고, venv를 자체 활성화하는지 확인 불가.

- **One-sentence verdict**: setup.sh의 환경 점검 로직은 완성도가 높지만 bash 서브셸에서의 venv 전파 버그로 인해 `run.sh` 단독 실행 시 파이프라인이 정상 구동되지 않을 가능성이 높다.


---

---

### R20 codex-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: N

- **Key issues**:
  - `sanity_check` 단계가 `dxrt-cli: command not found` (exit=127)로 **FAIL**했으나 README에 전혀 언급이 없음 — 사용자가 환경 이상 여부를 판단할 단서가 없음
  - `setup.sh`는 `dx_engine`이 없으면 FATAL로 종료되면서 `./install.sh && ./build.sh`를 실행하라는 안내를 출력하지만, README의 Prerequisites 설명이 "dx_app root에서 실행하라"는 추상적 표현에 그쳐 정확한 경로를 모르는 신규 사용자는 혼란을 겪을 수 있음
  - `verify.py` 미생성 — app-only 세션이므로 필수는 아니나, README에 결과 검증 절차(예: `--help` 출력 확인, 추론 결과 확인 방법)가 없어 성공/실패 기준이 불명확함

- **One-sentence verdict**: 추론 자체는 실제로 성공(SYNC_EXIT: 0, 49 FPS)했으나 sanity_check 실패를 README가 묵인하고 dx_engine 사전 빌드 요건 안내가 부족해, dx_app 빌드 환경을 이미 갖춘 사용자만 무난히 실행 가능한 **조건부 통과** 수준의 아티팩트이다.


---

---

### R20 opencode-cli compiler

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - **venv 활성화 누락**: README Quick Start의 `python3 verify.py` 명령은 `source venv/bin/activate` 없이 실행되므로 `No module named 'dx_engine'` / `No module named 'onnxruntime'` 로 실패할 가능성이 높음. `bash setup.sh`는 스크립트 종료 시 venv 활성화 상태가 부모 셸에 전파되지 않음.
  - **session.log 위변조 의심**: 모든 타임스탬프가 `05:48:42`로 동일하고, `PASS: session dir created, calibration symlinked, ONNX copied` 같은 줄은 실제 셸 출력이 아닌 수동 작성 형식임. `cat << 'EOF'` 패턴은 아니지만 실제 `tee` 캡처 로그 규격을 만족하지 않음 (Mandatory: `command 2>&1 | tee session.log` 위반 의심).
  - **setup.sh silent failure**: sanity_check 실패 시 `2>/dev/null`로 에러를 억제한 채 `install.sh`만 실행하고, 재확인(`sanity_check.sh` 재실행)을 수행하지 않음. 설치 후 PASS 여부를 검증하지 않아 환경 불량 상태로 진행될 수 있음.

- **One-sentence verdict**: Quick Start에 venv 활성화 단계가 누락되어 있고, session.log가 실제 캡처 증거로 신뢰하기 어려워 사용자가 그대로 따라할 경우 verify 단계에서 막힐 가능성이 있는 부분적으로 실행 가능한 세션임.


---

---

### R20 opencode-cli dx_app

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 4
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`가 4개 variant를 순차 실행하는데, C++ postprocess variant(3/4, 4/4)는 `dx_postprocess` 빌드가 필요함. `setup.sh`은 WARN만 출력하고 진행하므로 Quick Start(`bash setup.sh && bash run.sh`)를 그대로 따르면 **step 3/4에서 ImportError로 실패**. README의 Notes 섹션에 언급되어 있으나 Quick Start에 선행 조건으로 명시되지 않음.
  - `session.log`에는 sync image inference 1건(1 frame)만 기록되어 있음. async video 및 2개 C++ variant 실행 증거가 없어, **4개 variant 전체 검증 여부 불확실**.
  - `run.sh`의 venv 활성화 로직에 else 분기가 없어, `setup.sh` 미실행 시 **venv 미활성 상태로 진입할 수 있음** (setup.sh은 `.venv` 없을 경우 생성하지만 run.sh은 skip).

- **One-sentence verdict**: Quick Start 흐름이 C++ postprocess 빌드 선행 조건을 안내하지 않아 `run.sh` 실행 중 중단될 가능성이 높으며, session.log도 일부 variant만 검증된 상태라 완전한 PASS로 보기 어렵다.


---

---

### R20 opencode-cli dx_stream

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 4
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: Y

- **Key issues**:
  - `run.sh`의 경로 계산(`cd "$SCRIPT_DIR/../.."`)이 `dx_stream` 세션 디렉터리 깊이를 하드코딩 가정함 — `SUITE_ROOT` 자동탐색 패턴 미사용으로, 위치가 달라지면 model/video 경로가 깨짐
  - README의 `cd ../../` 지시는 세션 디렉터리 깊이(`dx_stream/dx-agentic-dev/<session>/`)에 대한 설명 없이 제시되어, 사용자가 어디서 실행해야 하는지 혼란 가능
  - `run.sh`가 내부에서 `run_yolo26n_detection.sh`를 호출하지만, 해당 파일의 존재 여부 확인 로직이 없어 파일 누락 시 불명확한 오류 발생

- **One-sentence verdict**: session.log에서 파이프라인 실행 성공이 확인되나, 경로 하드코딩과 README의 상대경로 설명 부족으로 다른 환경의 사용자가 그대로 따라하면 실행 실패 가능성이 있어 PARTIAL 판정.


---

---

### R20 opencode-cli dx_stream_cascaded

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 3
- **Verification provided (Y/N)**: N

- **Key issues**:
  - **모델 경로 불일치**: README/setup.sh는 `dx_stream/samples/models/`에서 모델을 찾지만, session.log는 실제로 `/workspace/res/models/models-2_3_0/`에서 로드됨. 새 사용자가 README를 따르면 모델을 찾지 못할 가능성이 높음
  - **하드코딩된 `../..` 경로**: setup.sh와 run.sh 모두 `DX_STREAM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"`를 사용하지만, 세션 디렉터리 깊이(`dx_stream/dx-agentic-dev/<session>/`)에서 `../..`는 `dx_stream/`를 가리켜 `dx-runtime/` 레벨이 아님. 지침서가 요구하는 SUITE_ROOT 자동 감지 패턴을 사용하지 않음
  - **run.sh가 setup 오류를 묵살**: `source setup.sh 2>/dev/null || true`로 setup 실패를 조용히 무시하며, 최종 실행은 내용이 공개되지 않은 `run_cascaded.sh`에 위임됨. 또한 session.log에서 파이프라인 오류 발생 시에도 exit code가 0으로 기록되어 있어 자동 검증이 불가

- **One-sentence verdict**: README 구조는 잘 갖춰져 있으나 모델 경로 불일치와 하드코딩된 상대 경로 문제로 인해 신규 사용자가 README만 따라서 성공적으로 실행하기 어려운 PARTIAL 수준의 아티팩트임.


---

---

### R20 opencode-cli runtime

- **end-user runnability**: PARTIAL
- **README clarity (1-5)**: 3
- **Setup completeness (1-5)**: 3
- **Run instructions completeness (1-5)**: 4
- **Verification provided (Y/N)**: Y

**Key issues**:
- **sanity_check FAIL (HARD GATE 미통과)**: `session.log`에서 `dxrt-cli: command not found (exit=127)` → RESULT: FAIL로 기록됨. Prerequisites HARD GATE를 통과하지 못했음에도 세션이 계속 진행되었고, inference는 성공했지만, 이 로그를 보는 사용자 입장에서는 환경이 정상인지 불분명하다.
- **venv 활성화 누락**: README의 직접 실행 예시(`python yolo26n_sync.py ...`)는 venv 활성화 없이 나열되어 있어, `dx_engine`이 시스템 Python에 없는 경우 import 에러가 발생한다. `run.sh`는 내부에서 `setup.sh`를 source하지만, README에 그 관계가 명시되지 않았다.
- **상대 경로 미설명**: `../../assets/models/yolo26n.dxnn`이 어느 기준점(세션 디렉터리 기준)에서의 경로인지 README에 언급이 없어, 위치를 모르는 사용자가 혼란을 겪을 수 있다.

**One-sentence verdict**: inference 실행 및 성능 지표는 실제로 검증되었으나, sanity_check HARD GATE 미통과 상태에서 세션이 진행된 것과 README의 venv/경로 설명 부재로 인해 사전 지식 없는 사용자가 독립적으로 재현하기엔 장벽이 있다.