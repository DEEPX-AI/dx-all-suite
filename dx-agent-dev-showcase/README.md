# dx-agent-dev Showcases

> Real apps built on the **DEEPX NPU SDK** by an AI coding agent from a **single
> natural-language prompt** — each checked in with the prompt, measured results, a
> one-command reproduce, and the full recorded build-session transcript.

These demonstrate **dx-agent-dev (Beta)**: you describe the app/task in plain language
and the agent drives the DEEPX knowledge base end to end (brainstorm → plan → TDD →
verify). What the feature is and how it works → [Agent-Driven Development docs](../docs/source/00_Agent_Driven_Development.md).
Each card below links to that showcase's own README (full detail + transcript).

<!-- catalog -->
<!-- dx-showcase:docs:catalog:start -->
## NPU-powered AI apps (mini-games)

**Build a fully autonomous DEEPX-NPU app from natural language — in ~20 minutes, for ~$10.** Pose-driven mini-games with arcade HUDs, built end to end from a single prompt.

| Showcase | Kind | Highlight |
|---|---|---|
| [Squat-Counting Mini-Game](./mini-game-squat-fitness/README.md) | game | pose game + arcade HUD |
| [Stretching Coach Mini-Game](./mini-game-stretching-coach/README.md) | game | coach avatar + 3 stages |

### Squat-Counting Mini-Game

<a href="./mini-game-squat-fitness/README.md"><img src="../docs/source/img/dx-agent-dev-squat-gameplay.gif" height="170" align="right"></a>

Counts squat reps from knee/hip angles with an arcade HUD (reps / score / DOWN·UP·GOOD!).

**Highlight:** pose game + arcade HUD · **Claude Opus 4.8** · ≈ 12 min · ≈ $7.3 — [details →](./mini-game-squat-fitness/README.md)

<br clear="right">

### Stretching Coach Mini-Game

<a href="./mini-game-stretching-coach/README.md"><img src="../docs/source/img/dx-agent-dev-stretch-gameplay.gif" height="170" align="right"></a>

Guides 3 stretches with an animated coach avatar that demonstrates each target pose.

**Highlight:** coach avatar + 3 stages · **Claude Opus 4.8** · ≈ 15 min · ≈ $8.1 — [details →](./mini-game-stretching-coach/README.md)

<br clear="right">

## Ultralytics ecosystem integration

**Take any Ultralytics YOLO to the DEEPX NPU in one command — or retrain it for your domain — all in natural language.** `format=deepx` export + 4-way eval (base/retrained × fp32-GPU / INT8-NPU); INT8 ≈ fp32, and the domain model runs faster on the NPU.

| Showcase | Kind | Highlight |
|---|---|---|
| [Ultralytics YOLO → DeepX Export](./ultralytics-yolo-deepx-export/README.md) | export | 1-cmd .pt → .dxnn |
| [African Wildlife Monitoring](./ultralytics-retrain-eval-deepx-export-wildlife/README.md) | retrain | mAP ~0.0007→0.79, 59→80 FPS |
| [Construction PPE Safety](./ultralytics-retrain-eval-deepx-export-ppe/README.md) | retrain | mAP 0.0001→0.257, 58→80 FPS |
| [Brain-Tumor Screening](./ultralytics-retrain-eval-deepx-export-braintumor/README.md) | retrain | mAP ~0.0005→0.40, 59→83 FPS |
| [Pharmaceutical Pill Inspection](./ultralytics-retrain-eval-deepx-export-pills/README.md) | retrain | mAP ~0.001→0.75 (mAP50 0.97), 55→78 FPS |

### Ultralytics YOLO → DeepX Export

<a href="./ultralytics-yolo-deepx-export/README.md"><img src="../docs/source/img/dx-agent-dev-ultralytics-yolo.gif" height="170" align="right"></a>

Turns an Ultralytics YOLO `.pt` into a deployable DeepX NPU model (`.dxnn`) in a single `yolo export ... format=deepx` command, then runs NPU inference + verify.

**Highlight:** 1-cmd .pt → .dxnn · **Claude Sonnet 4.6** · ≈ 12 min · ≈ $2.4 — [details →](./ultralytics-yolo-deepx-export/README.md)

<br clear="right">

### African Wildlife Monitoring

<a href="./ultralytics-retrain-eval-deepx-export-wildlife/README.md"><img src="../docs/source/img/dx-agent-dev-ultralytics-wildlife-sample.jpg" height="170" align="right"></a>

Retrains `yolo26n` on `african-wildlife` (buffalo/elephant/rhino/zebra) for a safari/conservation camera; 4-way eval base/retrained × fp32/INT8.

**Highlight:** mAP ~0.0007→0.79, 59→80 FPS · **Claude Opus 4.8** · ≈ 7 min · ≈ $3.2 — [details →](./ultralytics-retrain-eval-deepx-export-wildlife/README.md)

<br clear="right">

### Construction PPE Safety

<a href="./ultralytics-retrain-eval-deepx-export-ppe/README.md"><img src="../docs/source/img/dx-agent-dev-ultralytics-ppe-sample.jpg" height="170" align="right"></a>

Retrains `yolo26n` on `construction-ppe` for a site-safety camera (helmet/vest/...); 4-way eval base/retrained × fp32/INT8.

**Highlight:** mAP 0.0001→0.257, 58→80 FPS · **Claude Opus 4.8** · ≈ 17 min · ≈ $4.0 — [details →](./ultralytics-retrain-eval-deepx-export-ppe/README.md)

<br clear="right">

### Brain-Tumor Screening

<a href="./ultralytics-retrain-eval-deepx-export-braintumor/README.md"><img src="../docs/source/img/dx-agent-dev-ultralytics-braintumor-sample.jpg" height="170" align="right"></a>

Retrains `yolo26n` on `brain-tumor` (MRI/CT) for a medical edge device; 4-way eval base/retrained × fp32/INT8.

**Highlight:** mAP ~0.0005→0.40, 59→83 FPS · **Claude Opus 4.8** · ≈ 9 min · ≈ $3.7 — [details →](./ultralytics-retrain-eval-deepx-export-braintumor/README.md)

<br clear="right">

### Pharmaceutical Pill Inspection

<a href="./ultralytics-retrain-eval-deepx-export-pills/README.md"><img src="../docs/source/img/dx-agent-dev-ultralytics-pills-sample.jpg" height="170" align="right"></a>

Retrains `yolo26n` on `medical-pills` for a pharma counting station; 4-way eval base/retrained × fp32/INT8.

**Highlight:** mAP ~0.001→0.75 (mAP50 0.97), 55→78 FPS · **Claude Opus 4.8** · ≈ 8 min · ≈ $5.1 — [details →](./ultralytics-retrain-eval-deepx-export-pills/README.md)

<br clear="right">

## PaddlePaddle ecosystem integration

**PaddleOCR (PP-OCRv5) on the DEEPX NPU — real-time video & webcam OCR from a single, concise prompt.** Baidu's PaddlePaddle OCR (text detection → orientation → recognition) running on the DX-M1 NPU.

| Showcase | Kind | Highlight |
|---|---|---|
| [Video / Webcam OCR (PP-OCRv5)](./paddleocr-video-ocr/README.md) | app | PP-OCRv5 det→cls→rec on-device (~2.8 FPS, 341 ms/frame); 14 text regions/frame; video + webcam from one --source flag |

### Video / Webcam OCR (PP-OCRv5)

<a href="./paddleocr-video-ocr/README.md"><img src="../docs/source/img/dx-agent-dev-paddleocr-gameplay.gif" height="170" align="right"></a>

Real-time text detection + recognition on the DX-M1 NPU — one code path for a video file and a live webcam, overlaying detected boxes + recognized strings.

**Highlight:** PP-OCRv5 det→cls→rec on-device (~2.8 FPS, 341 ms/frame); 14 text regions/frame; video + webcam from one --source flag · **Claude Opus 4.8** · ≈ 18 min · ≈ $12.0 — [details →](./paddleocr-video-ocr/README.md)

<br clear="right">

## RapidAI ecosystem integration

**A PDF → Markdown document-conversion app on the DEEPX NPU — from a single, concise natural-language prompt.** RapidAI's RapidDoc (PP-StructureV3): layout, OCR, tables, formulas — running PaddlePaddle-trained models on the DX-M1 NPU. A standalone, self-contained app generated from the fork's pipeline.

| Showcase | Kind | Highlight |
|---|---|---|
| [PDF → Markdown (document conversion app)](./rapiddoc-pdf2md/README.md) | app | 9-page financial report parsed on-device; standalone app — vendored rapid_doc, own entry, no fork clone; 21 headings + 9 HTML tables preserved (auto 12.6s / ocr 14.7s) |

### PDF → Markdown (document conversion app)

<a href="./rapiddoc-pdf2md/README.md"><img src="../docs/source/img/dx-agent-dev-rapiddoc-pdf2md-sample.png" height="170" align="right"></a>

Converts a PDF (digital or scanned) to structured Markdown + JSON — layout analysis, OCR, tables and formulas — on the DEEPX DX-M1 NPU via the RapidDoc fork. Supports `--parse-method auto|txt|ocr`.

**Highlight:** 9-page financial report parsed on-device; standalone app — vendored rapid_doc, own entry, no fork clone; 21 headings + 9 HTML tables preserved (auto 12.6s / ocr 14.7s) · **Claude Opus 4.8** · ≈ 12 min · ≈ $6.2 — [details →](./rapiddoc-pdf2md/README.md)

<br clear="right">
<!-- dx-showcase:docs:catalog:end -->

## Reproduce any showcase

```bash
cd dx-agent-dev-showcase/<showcase>
bash setup.sh && bash run.sh        # retrain/export showcases
# games: ./setup.sh then ./run.sh (or ./run.sh --camera 0)
```

Requires x86-64 Linux + the DeepX runtime (`dx_engine`). Per-showcase prerequisites and
the exact prompt are in each showcase's README.

> Korean: [`README-ko.md`](./README-ko.md).
