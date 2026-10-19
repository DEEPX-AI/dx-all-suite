# DX Model Zoo

Browse the DEEPX model catalog — search and filter by AI task, open a
model to see its details (accuracy, input, license/source), and use it in the other
Studio tools.

The October 2026 reference contains **497 canonical variants / 29 tasks**, aligned with
dx_app dev `2e20108a5` and the Studio internal snapshot dated **2026-10-13** (348 → 497,
+149 entries). Sizes, input shapes and training variants are counted separately;
497 does not mean 497 distinct architectures. Check the explorer's counts and sync
date for the source loaded by your deployment.

## Using it

1. **Browse or search** the catalog; filter by **category** (image classification,
   object detection, segmentation, pose, …).
2. **Open a model** to see its detail view: task, input shape, accuracy metrics, and
   legal info (license, source, copyright).
3. Download an available `.dxnn`, ONNX or JSON artifact; Q-Lite, Q-Pro and occasional
   Q-Master availability varies per model. Open **DX App** for inference or **DX Compiler**
   for compilation.
4. For an image-input model, expand the inference panel, choose C++ / Python and
   Sync / Async, and run a sample or uploaded image. DX App, its runtime / NPU, model
   and example binary must be ready. If unavailable, finish DX App **Setup**, prepare
   the selected model / example and retry.

For example, open a Real-ESRGAN super-resolution variant to compare the existing
before/after images, then inspect its artifact availability and metric names before
choosing a download. Reuse supplied model images rather than re-generating every model's
results. Catalog FPS / accuracy are published measurements, not guaranteed local results.

## Key features

- **497 canonical variants across 29 tasks** in the reference, with filtering, search,
  sort and card / list views.
- **Rich detail view** per model — including license/source/copyright, kept up to date
  from the public DEEPX model catalog.
- **Graph support is narrower than the catalog** — 492 variants are graph-runnable in
  the reference dx_app; four anomaly models and the LiDAR model are excluded. See the
  [DX App manual](../docs/source/05_DX_App.md#graph-composer).
- **6-language UI** (English / 한국어 / 日本語 / 简体中文 / 繁體中文 / Español).

> The catalog data is synced from https://developer.deepx.ai/modelzoo/ on general networks
> (`sync_metadata --source public`) and from the internal publish site on release builds.
> See `dx_modelzoo/scripts/sync_release_catalog.sh` and `dx_modelzoo` docs for details.
