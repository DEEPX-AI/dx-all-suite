# DX App

Run AI inference on the DEEPX NPU from your browser — pick a model, run it on images,
video, a camera or an RTSP stream, watch live results, and benchmark or compare models.

## Using it

The module opens on a set of pages (top tabs):

- **Setup** — guided environment check; run it first so the NPU/runtime is ready.
- **Models** — browse the model registry by AI task (detection, classification,
  segmentation, pose, …); open a model to see its details.
- **Run Inference** — pick a model and an input and run it. **Single** runs one image or
  video; **Continuous** streams video / camera / RTSP live, several slots side by side (RTSP takes
  the camera's full `rtsp://` URL, or `IP:Port` with a stream pick).
- **Run Demo** — 26 ready-made demos in 12 groups on one stage (image or video, C++ or
  Python, Sync or Async).
- **Benchmark** / **A/B Compare** — measure a model’s throughput and compare models side by side.
- **ModelZoo** — download additional models into the app.
- **Graph Composer** — connect several models and logic blocks (zones, lines, counts, conditions) into one pipeline, check it, see its NPU memory, run it once or Live with its events, and keep it as a versioned project.
- **Lab** — Add Model, Create Task, Experiment and Safety Center.
- **Outputs** — browse and manage saved inference results.
- **Reference** — SDK documentation.

## Key features

- **Multiple input types** — image, video file, USB camera, and RTSP streams.
- **Live multi-stream** — several inference streams running and displaying at once.
- **Benchmark & compare** — throughput/latency numbers per model, side-by-side.
- **AI assistant** chat (floating button) for help with the workflow.
- **6-language UI** (English / 한국어 / 日本語 / 简体中文 / 繁體中文 / Español).
- Works without an NPU too (falls back to mock data for exploring the UI).
