# Video / Webcam OCR on the DEEPX DX-M1 NPU (PaddleOCR · PP-OCRv5)

> **The story.** From a single, concise natural-language prompt — naming no toolset, file,
> or repo branch — dx-agent-dev builds a real-time **OCR app** on the DEEPX **DX-M1 NPU**:
> PaddleOCR **PP-OCRv5** (detection → textline-orientation → recognition) runs on the NPU,
> overlaying detected text boxes + recognized strings on every frame. One code path takes
> **both a video file and a live webcam** (`--source <path.mp4>` / `--source <camera_index>`)
> and writes an annotated output video.

<div align="center"><table><tr>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-paddleocr-gameplay.gif" width="460"><br><sub><b>per-frame NPU OCR — boxes + recognized strings + confidence</b></sub></td>
<td align="center"><img src="../../docs/source/img/dx-agent-dev-paddleocr-build.gif" width="320"><br><sub><b>dx-agent-dev building it (timelapse)</b></sub></td>
</tr></table></div>

<div align="center"><img src="./sample_detect.jpg" width="640"><br><sub><b>annotated sample frame — PP-OCRv5 det+cls+rec on the DX-M1 NPU</b></sub></div>

> **See how the agent built it:** [`claude-code-session.md`](./claude-code-session.md).

### Session metrics

| Metric | Value |
|--------|-------|
| Coding agent / model | **Claude Code** / **Claude Opus 4.8** (`claude-opus-4-8`) |
| Human input | **1 short natural-language prompt** — fully autonomous |
| KB toolsets read | `paddleocr-rapiddoc-app`, `paddlepaddle-deepx` — **discovered via routing**, not named in the prompt |
| Skills | `dx-skill-router` → `dx-agent-brainstorm` → … → `dx-agent-verify` |
| Wall-clock / turns / cost | ~18 min / 175 / ≈ $12.0 |

## The prompt

Short and goal-only — it names no toolset path or branch (only the input video); the skill
+ KB routing supply the rest (and the decision to generate a standalone app over the fork's
pipeline):

```
Build an OCR inference app whose text detection + recognition runs on the DEEPX DX-M1 NPU.
The app must accept BOTH a video file (--source <path.mp4>) and a live webcam
(--source <camera_index>), run NPU OCR on each frame, overlay the detected text boxes and
the recognized strings, and write an annotated output video (optionally show a live
window). Save one annotated sample frame as sample_detect.jpg. Validate it on the provided
demo video at dx-agent-dev-showcase/paddleocr-video-ocr/sample/ocr_demo.mp4. Provide
setup.sh, run.sh, and a short README reporting the measured per-frame latency / FPS on the NPU.
```

> **Run this prompt from the dx-all-suite root** — the sample video path is relative to the suite root, which is where DEEPX Agent-Driven Development routing starts.

> **Architecture note.** Built on **PaddleOCR-deepx** (`deepx` branch). OCR is a multi-stage
> det→cls→rec pipeline (no single `.dxnn` / dx_app registry), so this is the documented
> **exception** to the IFactory / SyncRunner pattern: `ocr_video.py` is **our own standalone
> entry** that drives the fork's vendored `engine/` pipeline as a library — it does **not**
> shell out to any fork demo.

## Measured NPU performance

Real numbers from this session's run on the bundled demo (`sample/ocr_demo.mp4`), DX-M1
(runtime 3.3.2 / FW v2.5.6), captured on the HUD + in `session.log`:

- **PP-OCRv5 on the NPU: ~2.8 FPS, ~341 ms/frame**, 14 text regions per frame (det+cls+rec).
- Detection uses ratio-bucketed models (det_v5_640/960); recognition uses width-ratio
  models (rec_v5_ratio_3/5/10/15/35) — all on the DX-M1 NPU.
- `--frame-skip N` reuses the last result between NPU runs to keep a live webcam smooth.

## Quick start

```bash
./setup.sh                       # venv + shapely/pyclipper + dx_engine bridge + download NPU models
./run.sh                         # OCR the bundled demo video → ocr_output.mp4 + sample_detect.jpg
./run.sh myclip.mp4 out.mp4      # OCR a video file
./run.sh 0 webcam_out.mp4 --show # live webcam (camera index 0) with a preview window
```

> x86-64 Linux + DeepX DX-M1 runtime. Self-contained: the fork's `engine/` pipeline is
> vendored and `sample/ocr_demo.mp4` is bundled; `setup.sh` installs deps and downloads the
> PP-OCRv5 NPU models (`fork_setup_models.sh` → `engine/model_files/`, not committed). CJK
> rendering uses an optional Noto/sim font; without it the overlay falls back to ASCII text.

## Files

| File | Purpose |
|------|---------|
| `ocr_video.py` | **our** standalone entry — `open_source` (video **or** webcam) → NPU OCR → overlay |
| `engine/` | vendored PaddleOCR-deepx pipeline (PP-OCRv5 det/cls/rec; `model_files/` downloaded by setup) |
| `fork_setup_models.sh` | downloads the PP-OCRv5 `.dxnn` models into `engine/model_files/` |
| `setup.sh` / `run.sh` | relocatable setup / one-command launcher (bundled demo by default) |
| `verify.py` | headless validation (asserts NPU detections + saves annotated output) |
| `sample/ocr_demo.mp4` | bundled demo input (text scenes: station board, café menu, label, notice) |
| `sample_detect.jpg` | annotated sample frame |
| `claude-code-session.md` | full agent build transcript (Wall-clock + Cost) |

Korean: [`README-ko.md`](./README-ko.md).
