# DX App

Run AI inference on the DEEPX NPU from your browser — pick a model, run it on images,
video, a camera or an RTSP stream, watch live results, and benchmark or compare models.

![DX App — the Models page with task filters, the model table, and the live NPU monitor.](resources/app.png)

## Using it

The dashboard opens on a set of pages (top navigation):

- **Setup** — guided environment check; run it first so the NPU / runtime is ready.  
- **Models** — browse the model registry across 23 AI tasks (detection, classification,
  segmentation, pose, depth, super-resolution, 3D object detection, and more); open a
  model for details.  
- **Run** — pick a **category → model → input**, then Run. Inputs adapt to the category:
  a sample image, your **own uploaded image**, video, camera, or RTSP (some tasks are
  image-only; special inputs like 3D LiDAR `.bin` appear where they apply). The annotated
  result shows live, with a **before/after compare slider** for image runs, and multiple
  streams can run at once.  
- **Bench** / **Compare** — measure a model's throughput and compare models side by side;
  Bench can run several models in a batch and **export a report**.  
- **Model Zoo** — browse and download additional models into the app (public or air-gapped
  source, Q-Lite / Q-Pro variants, batch cart).  
- **Outputs** — browse and manage saved inference results (grid / table, filters, preview).  
- **Lab** / **Developer** — guided wizards to add a model, create a task, or extract a
  deployable package, with a change-preview + rollback safety step (advanced use).  
- **Reference** — searchable in-app feature and parameter guides.  

From the Run page you can also **Export Model Package** — bundle a model's source, config,
and file (C++ / Python / both) for reuse.  

Works **without an NPU** too — every page falls back to mock data so you can explore the UI.  

!!! note "Related"
    Run the `.dxnn` files produced by **[DX Compiler](04_DX_Compiler.md)**; the same
    NPU telemetry is visualized live in **[DX Monitor](07_DX_Monitor.md)**.  
