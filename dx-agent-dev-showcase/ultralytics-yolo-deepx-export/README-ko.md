# Ultralytics YOLO → DeepX Export — dx-agent-dev로 제작

> **Ultralytics × DEEPX 기술 통합 showcase.** 자연어 프롬프트 하나로, 코딩 에이전트
> (Claude Code / Copilot / Cursor / OpenCode / Codex)가 DEEPX knowledge base로
> 라우팅하여 **one-shot `format=deepx` export**를 수행합니다 — Ultralytics YOLO `.pt`를
> 명령 한 번으로 배포 가능한 DeepX NPU 모델(`.dxnn`)로 변환하고 inference까지 실행합니다.
>
> **이 README를 제외한 모든 파일은 에이전트가** 단일 자율 빌드 세션에서 생성했습니다
> (아래 transcript + timelapse 참고) — 수기 코드 없음.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-ultralytics-build.gif" width="430"><br><sub><b>dx-agent-dev가 이 showcase를 만드는 과정 (timelapse) — export → dx_com compile → NPU inference → verify</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-ultralytics-yolo.gif" width="360"><br><sub><b>DEEPX × Ultralytics — DX-M1 NPU 위의 YOLO (파트너 데모)</b></sub></td>
</tr></table></div>

> **에이전트가 만든 과정 보기:** [`claude-code-session.md`](./claude-code-session.md)
> (GitHub에서 렌더; `claude-code-session.html`은 로컬 브라우저; raw
> `claude-code-session.jsonl`은 stream log). DONE 센티넬의 transcript 단계가
> in-session으로 생성했습니다.

### 이 showcase 제작 메트릭

실제 build 세션 transcript(`claude-code-session.*`)에서 추출:

| 항목 | 값 |
|--------|-------|
| Coding agent | **Claude Code** (`claude` CLI, headless `-p`) |
| Model | **Claude Sonnet 4.6** (`claude-sonnet-4-6`) |
| 사람 입력 | **자연어 프롬프트 1개** — 완전 자율, 수기 코드 없음 |
| Build 소요 | **~11.6분** |
| Agent turns | **59** |
| Cost (reported) | **$2.41** |
| 사용 skill | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| 결과 | **`yolo26n.dxnn`**(6.6 MB) export + **NPU inference**(5 detections, DX-M1에서 ~23 ms) + `verify.py` **PASS** |

## 프롬프트

> 에이전트에게 준 실제 자연어 프롬프트 (verbatim):

```
Export the Ultralytics YOLO26n detection model to DeepX NPU format using the one-shot format=deepx export path, then run inference on the Ultralytics bus sample image.
```

## 에이전트의 동작 (KB 기반 워크플로)

`.deepx/`에 Ultralytics 통합 지식이 추가되어, 에이전트는 파이프라인을 지어내지 않고
이 프롬프트를 해결합니다:

1. **`/dx-skill-router`** → 모델 컴파일 task로 분류.
2. **Suite 라우팅** → `Ultralytics YOLO .pt → DeepX (format=deepx)` → `dx-compiler/CLAUDE.md`.
3. **dx-compiler 라우팅** → `Ultralytics, YOLO, .pt, format=deepx` →
   [`.deepx/toolsets/ultralytics-deepx-export.md`](../../dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md).
4. **`/dx-agent-compiler-convert` Phase 0** → YOLO **detection** + DeepX 인식 →
   수작업 PT→ONNX→`dxcom` 대신 one-shot 경로 선택.
5. **export → compile → deploy → verify** 후 아래 파일 생성.

에이전트는 KB의 hard 제약을 적용합니다: **x86-64 Linux 전용**, **detection 전용**,
**INT8 강제**, 출력은 **디렉토리**(`*_deepx_model/`), 그리고 `dx_engine` runtime은
pip가 아니라 **`dx_rt`**(`dx-runtime/install.sh --exclude-app --exclude-stream`)에서 옴.

## 파일 (모두 에이전트 생성)

| 파일 | 역할 |
|------|------|
| `export.py` | one-shot `YOLO("yolo26n.pt").export(format="deepx")` → `yolo26n_deepx_model/` |
| `infer.py` | `yolo26n_deepx_model/` 로드 후 bus 샘플로 NPU inference |
| `verify.py` | export 산출물 검증(`.dxnn` / `config.json` / `metadata.yaml`) |
| `setup.sh` | `dx_rt` venv 의존성 확인(ultralytics + dx_engine + dx_com) |
| `run.sh` | 원커맨드: export → verify → inference |
| `expected_output.txt` | 실제 run 출력(export + 5 detections + verify PASS) |

## 실행 방법

```bash
bash setup.sh     # 의존성 확인(dx_rt venv의 ultralytics + dx_engine + dx_com)
bash run.sh       # yolo26n.pt export → verify → bus.jpg inference
```

`run.sh`는 suite root를 auto-detect하고 `dx-runtime/venv-dx-runtime`을 활성화합니다.
`dx_engine`이 없으면 runtime을 빌드하세요: `cd dx-runtime && bash install.sh --all
--exclude-app --exclude-stream` (dx_rt가 `dxrt-cli` + `dx_engine` 제공; dx_app/dx_stream
불필요). [`expected_output.txt`](./expected_output.txt) 참고.

## 이 showcase의 기반 지식

| KB 산출물 | 역할 |
|---|---|
| `dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md` | `format=deepx` 권위 reference (API, args, 제약, 배포). |
| `.deepx/templates/fragments/{en,ko}/ultralytics-deepx-export.md` | 모든 플랫폼 instruction에 노출되는 one-shot 경로 요약. |
| `dx-compiler/.deepx/skills/dx-agent-compiler-convert` Phase 0 | YOLO-detection→DeepX를 one-shot 경로로 라우팅. |
| `dx-compiler/.deepx/memory/common_pitfalls.md` #25 | YOLO detection 모델을 수작업 PT→ONNX→dxcom으로 만들지 말 것. |

권위 upstream 문서: `ultralytics/docs/en/integrations/deepx.md`.
English: [`README.md`](./README.md).
