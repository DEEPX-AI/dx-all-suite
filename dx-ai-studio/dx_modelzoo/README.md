# DX Model Zoo

Browse the DEEPX model catalog (340+ models, synced from the public Model Zoo) — search and filter by AI task, open a
model to see its details (accuracy, input, license/source), and use it in the other
Studio tools.

## Using it

1. **Browse or search** the catalog; filter by **category** (image classification,
   object detection, segmentation, pose, …).
2. **Open a model** to see its detail view: task, input shape, accuracy metrics, and
   legal info (license, source, copyright).
3. From here the model can be pulled into **DX App** (inference) or **DX Compiler**.

## Key features

- **340+ models** (342 in DX AI Studio; 358 on the public Model Zoo) across many vision AI tasks, with per-category filtering, search, and
  pagination.
- **Rich detail view** per model — including license/source/copyright, kept up to date
  from the public DEEPX model catalog.
- **6-language UI** (English / 한국어 / 日本語 / 简体中文 / 繁體中文 / Español).

> The catalog data is synced from https://developer.deepx.ai/modelzoo/ on general networks
> (`sync_metadata --source public`) and from the internal publish site on release builds.
> See `dx_modelzoo/scripts/sync_release_catalog.sh` and `dx_modelzoo` docs for details.
