# PDF → Markdown on the DEEPX DX-M1 NPU (RapidDoc / PP-StructureV3)

> **The story.** A user types a **short, goal-only prompt** — "build a PDF→Markdown app
> that runs on the DEEPX NPU" — naming **no toolset, no file, no repo branch, no env
> script.** From that alone, dx-agent-dev routes to the right knowledge base and generates
> a **standalone, self-contained app**: it **vendors** the RapidAI **RapidDoc** pipeline
> package (`rapid_doc`, PP-StructureV3) into the app, writes its **own entry**
> (`pdf_to_markdown.py`) that imports it, and runs **layout analysis, OCR, and table
> recognition on the DX-M1 NPU** (formula recognition on ONNX Runtime). The result turns a
> PDF (digital or scanned) into structured **Markdown + JSON** — no runtime clone of the fork.

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
| Wall-clock / turns / cost | ~12 min / 61 / ≈ $6.2 |

## The prompt

The whole point of this showcase: the prompt is **concise** and names no toolset path,
file, branch, or env script — the skill + KB routing supply all of that, including the
decision to **generate a standalone app** (not wrap the fork's demo).

```
Build a PDF-to-Markdown app whose document-parsing pipeline (layout analysis + OCR +
table/formula recognition) runs on the DEEPX DX-M1 NPU. Input a PDF (digital or scanned),
output structured Markdown (+ JSON) preserving headings and tables. Support
--parse-method auto|txt|ocr. Provide setup.sh, run.sh, a sample input PDF + its rendered
Markdown output (sample_output.md), and a README reporting NPU stage timings.
```

> **Architecture note.** RapidDoc ships its *own* NPU pipeline (PP-StructureV3 on the
> DX-M1), so this is the documented **exception** to the dx_app IFactory / SyncRunner
> pattern. The deliverable is **our own entry** (`pdf_to_markdown.py`) over the **vendored**
> `rapid_doc` package — *not* a wrapper around the fork's `demo/demo_offline.py`.

## Quick start

```bash
./setup.sh                       # venv + deps + dx_engine bridge + NPU model download
./run.sh                         # parse the bundled sample_input.pdf (auto method)
./run.sh mydoc.pdf auto          # digital PDF (text layer first, OCR fallback)
./run.sh scan.pdf  ocr           # scanned PDF (force full OCR on the NPU)
./run.sh doc.pdf   txt           # text-layer extraction only (no OCR)
```

The fork is **not** cloned at run time — `rapid_doc/` is vendored in this folder; `setup.sh`
only installs pip deps and **downloads the NPU models** (16 `.dxnn` + 8 `.onnx`, not committed).

## `--parse-method`

| Method | Behavior | Use for |
|---|---|---|
| `auto` *(default)* | Embedded text layer per page, OCR fallback where missing | digital / mixed PDFs |
| `txt`  | Text layer only, no OCR | known-digital PDFs (fastest) |
| `ocr`  | Force full OCR (det + rec) on every page on the NPU | scanned / image-only PDFs |

## Measured NPU performance

`sample_input.pdf` = `physics0409110_origin.pdf` (an English physics paper, *"High-precision
Absolute Distance and Vibration Measurement using Frequency Scanned Interferometry"*, **16
pages**, equation-heavy), produced by **this app's own `pdf_to_markdown.py`** on DX-M1
(`DXNN_DEVICES=0`, runtime 3.3.2 / FW v2.5.6). `auto` end-to-end **41.3 s** (2.58 s/page):

| Stage | Count | Avg latency | Throughput | Engine | Share |
|---|---:|---:|---:|---|---:|
| Formula recognition | 164 | 213.82 ms | 4.7 FPS | ONNX/CPU | 85.0% |
| Layout analysis | 16 | 317.42 ms | 3.2 FPS | **NPU** | 12.3% |
| Table recognition | 1 | 848.05 ms | 1.2 FPS | **NPU** | 2.1% |
| OCR det / PDF text-det | 100 | ~2–108 ms | — | **NPU** | 0.7% |

This paper is **formula-dense** (164 equation regions → 85% of the time), showcasing
formula recognition alongside NPU layout/OCR/table. Model load: 1.75 s.

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

## How it works (standalone)

1. `pdf_to_markdown.py` puts the **vendored `./rapid_doc`** on `sys.path` (no install, no
   runtime clone) and checks the DX-RT threading env.
2. Builds per-model engine configs (layout `PP-DocLayout-L`, OCR `PP-OCRv5` det+rec, table
   `UNET`, formula `PP-FormulaNet+`), pointing layout/OCR/table at the local `dxnn_models/` (NPU).
3. Runs `rapid_doc.backend.pipeline.pipeline_analyze.doc_analyze(...)` on the NPU.
4. Renders Markdown (`MakeMode.MM_MD`) + a JSON content list via `FileBasedDataWriter`.

## Reproduce

```bash
bash setup.sh        # venv + deps + dx_engine bridge + download NPU models (foreground)
bash run.sh          # parse sample_input.pdf on the NPU → output/<stem>/<method>/<stem>.md
```

> x86-64 Linux + DeepX runtime; `dx_engine` missing: `cd dx-runtime && bash install.sh --all --exclude-app --exclude-stream`.
> Models come from `setup_sample_models.sh` (prebuilt onnx+dxnn) — **not** hand-compiled with `dxcom`.

## Files

| File | Role |
|---|---|
| `pdf_to_markdown.py` | **our** standalone entry over the vendored NPU pipeline |
| `rapid_doc/` | **vendored** RapidDoc pipeline package (pure Python, ~2.5 MB) |
| `deepx_scripts/`, `setup_sample_models.sh` | DX env setup + NPU/ONNX model downloader |
| `setup.sh` | venv + `requirements.deepx.txt` + dx_engine `.pth` bridge + model download |
| `run.sh` | launcher: sources `set_env.sh`, `DXNN_DEVICES=0`, runs `pdf_to_markdown.py` |
| `sample_input.pdf` / `sample_output.md` | English physics paper + its rendered Markdown |
| `images/sample_before_after.png` | before/after: PDF page → parsed Markdown |
| `timings.md` | per-stage NPU timing report (real run) |
| `session.log` | captured real output of the inference runs |
| `claude-code-session.md` | full agent build transcript (Wall-clock + Cost) |

Korean: [`README-ko.md`](./README-ko.md).
