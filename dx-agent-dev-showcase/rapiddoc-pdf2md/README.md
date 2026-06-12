# PDF → Markdown on the DEEPX DX-M1 NPU (RapidDoc / PP-StructureV3)

> **The story.** A user types a **short, goal-only prompt** — "build a PDF→Markdown app
> that runs on the DEEPX NPU" — naming **no toolset, no file, no repo branch, no env
> script.** From that alone, dx-agent-dev routes to the right knowledge base, clones the
> DEEPX **RapidDoc** fork, provisions the NPU models, and produces a working app that turns
> a PDF (digital or scanned) into structured **Markdown + JSON** — **layout analysis, OCR,
> and table/formula recognition all on the DX-M1 NPU** (PP-StructureV3).

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-rapiddoc-pdf2md-build.gif" width="470"><br><sub><b>dx-agent-dev building this showcase (timelapse)</b></sub></td>
<td align="center"><img src="./images/sample_before_after.png" width="470"><br><sub><b>PDF page → Markdown, parsed on the DX-M1 NPU</b></sub></td>
</tr></table></div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md).

### Session metrics

| Metric | Value |
|--------|-------|
| Coding agent / model | **Claude Code** / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 short natural-language prompt** — fully autonomous |
| KB toolsets read | `paddleocr-rapiddoc-app` — **discovered via routing**, not named in the prompt |
| Skills | `dx-skill-router` → `dx-agent-brainstorm` → `dx-swe-writing-plans` → `dx-agent-tdd` → `dx-agent-verify` |
| Wall-clock / turns / cost | ~17 min / 109 / ≈ $14.3 |

## The prompt

The whole point of this showcase: the prompt is **concise** and names no toolset path,
file, branch, or env script — the skill + KB routing supply all of that.

```
Build a PDF-to-Markdown app whose document-parsing pipeline (layout analysis + OCR +
table/formula recognition) runs on the DEEPX DX-M1 NPU. Input a PDF (digital or scanned),
output structured Markdown (+ JSON) preserving headings and tables. Support
--parse-method auto|txt|ocr. Provide setup.sh, run.sh, a sample input PDF + its rendered
Markdown output (sample_output.md), and a README reporting NPU stage timings.
```

> **Architecture note.** RapidDoc ships its *own* NPU pipeline (the PP-StructureV3 models
> run on the DX-M1 through the fork's runtime). Per the dx_app knowledge base
> (`paddleocr-rapiddoc-app.md`) this is the documented **exception** to the IFactory /
> SyncRunner pattern: the app is a thin standalone launcher that drives the fork's
> pipeline — it does not wrap a single `.dxnn` in a factory.

## Quick start

```bash
./setup.sh                          # clone fork + venv + deps + download NPU models (foreground, one-shot)
./run.sh                            # parse sample_input.pdf with --parse-method auto (default)
./run.sh --parse-method ocr         # force full-page OCR (scanned docs)
./run.sh --parse-method txt         # text-layer only (fast, digital PDFs)
./run.sh --input my.pdf --parse-method auto
```

Outputs land in `output-<method>/<doc>/<method>/`; the rendered Markdown is copied to
`./sample_output.md` and the per-stage NPU timing report to `./timings.md`.

## `--parse-method`

| Method | Behavior | Use for |
|---|---|---|
| `auto` *(default)* | Try the PDF text layer first, fall back to NPU OCR per region | Mixed / unknown PDFs |
| `txt`  | Use the embedded text layer only (no OCR) | Born-digital PDFs (fastest) |
| `ocr`  | Force full-page OCR (PP-OCRv5 det+rec) on the NPU for every page | Scanned / image-only PDFs |

## On-device pipeline (DX-M1)

`--finegrained` (default) runs a 7-stage streaming pipeline. Engine assignment:

| Stage | Engine | Device |
|---|---|---|
| Layout analysis (`pp_doclayout_l`) | dxengine | **NPU** |
| OCR detection (`ch_PP-OCRv5_server_det`) | dxengine | **NPU** |
| OCR recognition (`ch_PP-OCRv5_rec_server`) | dxengine | **NPU** |
| Table recognition (`unet` + structure) | dxengine | **NPU** |
| Formula recognition (`pp_formulanet_plus_l`) | onnxruntime | CPU |

16 `.dxnn` models are provisioned by `setup.sh` into `RapidDoc/dxnn_models/`.

## Measured NPU performance

Real numbers from this session — `sample_input.pdf` = `physics0409110_origin.pdf`
(an English physics paper, *"High-precision Absolute Distance and Vibration Measurement
using Frequency Scanned Interferometry"*, **16 pages**, equation-heavy), DX-M1,
`DXNN_DEVICES=0`, runtime 3.3.2 / FW v2.5.6. Captured in `session.log` / `timings.md`.

**End-to-end (auto, 16 pages): 36.9 s** wall, 0.4 pages/s. Per-stage on the NPU:

| Stage | Count | Avg latency | Throughput | Share |
|---|---:|---:|---:|---:|
| Formula recognition | 164 | 201.21 ms | 5.0 FPS | 84.5% |
| Layout analysis | 16 | 311.62 ms | 3.2 FPS | 12.8% |
| Table recognition | 1 | 795.29 ms | 1.3 FPS | 2.0% |
| PDF-det / OCR-det | 100 | ~2 ms | — | 0.7% |

This paper is **formula-dense** — 164 equation regions dominate (84.5%), showcasing the
pipeline's **formula recognition** alongside layout/OCR. One-time model load: 1.75 s.
(`txt` reuses the PDF text layer and is faster; `ocr` forces full-page OCR and is slower.)

## Sample output (excerpt from `sample_output.md`)

Title, authors, abstract and section headings are preserved; equations are recognized as
formula regions (rendered as cropped images in the Markdown):

```markdown
# High-precision Absolute Distance and Vibration Measurement using Frequency Scanned Interferometry

Hai-Jun Yang, Jason Deibel, Sven Nyberg, Keith Riles

Department of Physics, University of Michigan, Ann Arbor, MI 48109-1120, USA

In this paper, we report high-precision absolute distance and vibration measurements
performed with frequency scanned interferometry using a pair of single-mode optical fibers...

# 1. Introduction
# 2. Principles
# 3. Demonstration System of FSI
```

## Reproduce

```bash
bash setup.sh        # clone DEEPX-AI/RapidDoc@rapid_doc_deepx fresh + venv + deps + foreground model download
bash run.sh          # parse sample_input.pdf on the NPU → sample_output.md + timings.md
```

> x86-64 Linux + DeepX runtime; `dx_engine` missing: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.
> Models come from the fork's `./setup.sh` (prebuilt `onnx_models/` + `dxnn_models/`) —
> **not** hand-compiled with `dxcom`. The fork is cloned fresh into this dir (output
> isolation); no pre-existing user repo is reused or deleted.

## Files

| File | Purpose |
|---|---|
| `setup.sh` | Clone fork + venv + deps + foreground model download + pick sample PDF |
| `run.sh` | One-command launcher: venv + DX-RT env + `DXNN_DEVICES` + `--parse-method` |
| `sample_input.pdf` | Sample input (English physics paper, 16 pages, equation-heavy) |
| `sample_output.md` | Rendered Markdown (auto) — headings + 9 tables preserved |
| `images/sample_before_after.png` | Before/after sample: PDF page → parsed Markdown (NPU) |
| `images/*.jpg` | Formula/figure regions recognized on the NPU (referenced by `sample_output.md`) |
| `timings.md` | Per-stage NPU timing report (from the real run) |
| `session.log` | Captured real command output (setup + all runs) |
| `claude-code-session.md` | Full agent build transcript (Wall-clock + Cost) |

Korean: [`README-ko.md`](./README-ko.md).
