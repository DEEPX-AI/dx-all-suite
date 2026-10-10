# Change Log

Notable changes to the DX-AI-Studio User Manual.

## Unreleased (since v0.1.0)

Changes since the v0.1.0 beta manual. The version number and date are set at release.

**Hub and design**

- New home: a prompt box (*Describe anything. Run it on DX-M1.*) that opens the right tool or
  runs the coding agent in place, tool cards with live facts, a DX-M1 widget, a "Measured on
  DX-M1" card and a DEEPX Developers link bar. It replaces the orbital launcher.
- Light, dark and system themes; one icon set across all modules (no emoji in the UI); real
  variable fonts with one CJK face per language.
- A new intro built from real runs and real DX-M1 footage.
- The NPU monitor float starts folded at the bottom left and remembers your choice.

**Remote access & security**

- Other computers pair once with a 6-digit code shown in the launcher terminal; the
  **Connected browsers** button lists and disconnects them. Module servers listen on the
  board only; no wildcard CORS; Host and Origin checks; compile paths are limited to allowed
  folders.

**Tools**

- DX App: the per-model example layout, **Run Demo** (26 demos on a shared stage), live
  Continuous runs with exact FPS, faster async runs (`DXRT_DYNAMIC_CPU_THREAD`), Model Zoo
  inference that runs each model's own example, and runner errors reported as errors.
- DX Stream: Demo Launcher on the same stage with WebRTC or remote MJPEG playback; Setup as a
  step list; launches work on a board whose Stream contracts validate.
- Model Zoo: nearly 500 models from the internal publish page, with real result images.
- DX Compiler, DX App and DX Stream: Setup shows the next step and why a button is locked.
- SDK Library follows the suite's documentation (190 documents, 6 shelves).
- About 370 DX App strings that were translated but never shown now appear in every language;
  Korean spacing follows Korean orthography; server errors are translated.
- DX EdgeGuide: channel counts come from the measured end-to-end pipeline throughput. They are
  measured where a tested stream count brackets your target FPS and estimated otherwise
  (capped at twice the tested count). Each card says which, and why, in one line, with notes
  for NPU throttling, whether the NPU or the host was the limit, and unmeasured latency.
  60 FPS no longer reads 0 channels almost everywhere. Best Performance ranks by camera-pipeline
  FPS; Lowest Power by NPU TDP (host power excluded).
- DX Agent Dev: a **Stop** button while an agent runs; a dropped connection no longer stays
  "Running…".
- DX Compiler: large graphs open at a readable zoom at the input node; picking a sample model
  draws its graph; Config Builder asks for the dataset folder (or Dummy Loader); a refused
  compile keeps the graph and shows the reason.
- Model Zoo: cards and details use the published model names; **Run Inference** finds each
  model's example in the per-model layout (it used to fail with "Binary not found").
- DX App Lab: **Add Model** works again — it copies an existing example of the category (*Start from*)
  and the Python copy runs on the board; **Experiment** really runs (read the model, one inference,
  throughput in FPS); **Safety Center** rolls back an applied change that only created files, and
  applied changes stay listed in Generated Files.
- All modules: phone-width (390 px) layouts fixed for Setup, EdgeGuide cards, Compiler tabs,
  Benchmark Settings/Results, the Lab home and the SDK Library; dozens of mistranslations
  fixed (e.g. Setup no longer reads as Settings); the AI Help knowledge matches today's UI.

## v0.1.0 / 2026-07

- Initial DX-AI-Studio User Manual (studio **v0.1.0**, beta): MkDocs (Material) site
  covering installation & launch, the hub, all eight tools (DX Compiler, DX App,
  DX Stream, DX Model Zoo, DX Benchmark, DX Monitor, DX EdgeGuide, DX Agent Dev), and
  the SDK Library & About views. English, with PDF export.  

!!! note  
    For per-component release notes (runtime, compiler, stream, …), see each
    sub-project's `RELEASE_NOTES.md` in the DEEPX SDK, available in the in-app
    [SDK Library](11_SDK_Library_and_About.md).
