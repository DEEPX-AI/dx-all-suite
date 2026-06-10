# Ultralytics YOLO → DeepX Export — built by dx-agentic-dev

> **Showcase of the Ultralytics × DEEPX technical integration.** From a single
> natural-language prompt, a coding agent (Claude Code / Copilot / Cursor /
> OpenCode / Codex) routes to the DEEPX knowledge base and drives the **one-shot
> `format=deepx` export** — turning an Ultralytics YOLO `.pt` into a deployable
> DeepX NPU model (`.dxnn`) in a single command, then running inference on it.

This folder is **self-contained**: the two scripts below run on any x86-64 Linux
host with `pip` — no checkout of dx-all-suite required.

<div align="center">
<img src="../../docs/source/img/dx-agentic-dev-ultralytics-build.gif" width="760"><br>
<sub><b>dx-agentic-dev building this showcase (timelapse) — export → compile → NPU inference → verify</b></sub>
</div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md)
> (renders on GitHub; `claude-code-session.html` opens in a local browser; raw
> `claude-code-session.jsonl` is the stream log).

### How this showcase was built — session metrics

Captured from the real build session transcript (`claude-code-session.*`):

| Metric | Value |
|--------|-------|
| Coding agent | **Claude Code** (`claude` CLI, headless `-p`) |
| Model | **Claude Sonnet 4.6** (`claude-sonnet-4-6`) |
| Human input | **1 natural-language prompt** — fully autonomous, no hand-written code |
| Build wall-clock | **≈ 10 min** |
| Agent turns | **110** |
| Skills used | `dx-skill-router` → `dx-agentic-brainstorm` → `dx-swe-writing-plans` → `dx-agentic-tdd` → `dx-agentic-verify` |
| Result | Exported **`yolo26n.dxnn`** (6.6 MB) + **NPU inference** (6 detections, 22.6 ms on DX-M1) + `verify.py` **PASS** (PT=5/DeepX=6, classes match) |

## The prompt

```
Export my Ultralytics YOLO26n detection model to DeepX NPU format,
then run inference on the bus sample image.
```

## What the agent does (KB-driven workflow)

With the Ultralytics integration knowledge added to `.deepx/`, the agent resolves
this prompt **without fabricating a pipeline**:

1. **`/dx-skill-router`** → classifies the task as model compilation.
2. **Suite routing** → `Ultralytics YOLO .pt → DeepX (format=deepx)` row points to
   `dx-compiler/CLAUDE.md`.
3. **dx-compiler routing** → `Ultralytics, YOLO, .pt, format=deepx` row →
   [`.deepx/toolsets/ultralytics-deepx-export.md`](../../dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md).
4. **`/dx-agentic-compiler-convert` Phase 0** → recognises a YOLO **detection**
   model targeting DeepX and selects the **one-shot path** instead of the manual
   PT→ONNX→`dxcom` pipeline.
5. **Export** → `yolo export model=yolo26n.pt format=deepx` → `yolo26n_deepx_model/`.
6. **Deploy** → `YOLO("yolo26n_deepx_model")` runs inference on the `dx_engine` runtime.

The agent knows the integration's hard constraints from the KB: **x86-64 Linux
only**, **detection models only**, **INT8 enforced**, and that the output is a
**directory** (`*_deepx_model/`), not a bare `.dxnn`.

## Run it

```bash
# 1. Export the YOLO .pt to a DeepX model directory (x86-64 Linux only)
bash export_deepx.sh                 # creates ./yolo26n_deepx_model/

# 2. Run inference on the exported DeepX model
python3 predict_deepx.py             # prints detections on the bus sample
```

`export_deepx.sh` creates a venv, installs `ultralytics` (which pulls `dx_com` on
first export), and runs the one-shot export. `predict_deepx.py` loads the exported
`yolo26n_deepx_model/` and runs detection on the Ultralytics bus sample.

> **Deployment prerequisite (NPU present but no dx-runtime).** Step 1 (export)
> auto-installs `dx_com` via pip. Step 2 (inference) needs the **DeepX runtime**
> (`dxrt-cli` + `dx_engine`), which Ultralytics auto-installs **only on Debian
> Trixie/arm64**. On x86-64, step 2 raises
> `OSError: dx_engine is not installed. … Please install dx_engine manually and try
> again` — and here "install manually" means **install the `dx_rt` runtime** (do NOT
> `pip install dx_engine`):
> ```bash
> bash dx-runtime/scripts/sanity_check.sh --dx_rt          # judge by TEXT output
> bash dx-runtime/install.sh --all --exclude-app --exclude-stream --skip-uninstall --venv-reuse
> # dx_rt provides dxrt-cli + dx_engine; dx_app/dx_stream are NOT needed (skip → faster).
> ```
> An NPU "Device initialization failed" needs a **cold boot** (full power cycle).
> `predict_deepx.py` detects this error and prints the same recovery steps.

## Expected output

See [`expected_output.txt`](./expected_output.txt) for the produced model-directory
tree and a sample detection summary.

## Knowledge base behind this showcase

| KB artifact | Role |
|---|---|
| `dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md` | Authoritative `format=deepx` reference (API, args, constraints, deploy). |
| `.deepx/templates/fragments/{en,ko}/ultralytics-deepx-export.md` | One-shot path blurb surfaced in every platform's instructions. |
| `dx-compiler/.deepx/skills/dx-agentic-compiler-convert` Phase 0 | Routes YOLO-detection→DeepX to the one-shot path. |
| `dx-compiler/.deepx/memory/common_pitfalls.md` #25 | Don't hand-roll PT→ONNX→dxcom for a YOLO detection model. |
| Suite + dx-compiler routing tables | `Ultralytics / YOLO / format=deepx` → dx-compiler. |

Authoritative upstream doc: `ultralytics/docs/en/integrations/deepx.md`.

Korean: [`README-ko.md`](./README-ko.md).
