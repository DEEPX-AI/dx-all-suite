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
- The NPU monitor float starts folded and remembers your choice. In a module it folds into a rail button
  above Hub (a dot shows the NPU temperature state), so it no longer covers the bottom of the page.

**Remote access & security**

- Other computers pair once with a 6-digit code shown in the launcher terminal; the
  **Connected browsers** button lists and disconnects them. Module servers listen on the
  board only; no wildcard CORS; Host and Origin checks; compile paths are limited to allowed
  folders.

**Tools**

- DX App: the per-model example layout, **Run Demo** (26 demos on a shared stage), live
  Continuous runs with exact FPS, faster async runs (`DXRT_DYNAMIC_CPU_THREAD`), Model Zoo
  inference that runs each model's own example, and runner errors reported as errors.
- DX App: **Graph Composer** replaces the Lab composer: several models and logic blocks in one graph, checked as you
  edit, run once or Live with events, exported as a standalone C++ project; nine scenario templates with real NPU
  results, every template and example named in six languages, and a guided tour.
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
  applied changes stay listed in Generated Files; **Commit with git** lists the files a change wrote and
  the git commands that commit only those.
- DX App: **RTSP address** takes the camera's own URL (`rtsp://user:pass@cam:554/...`); host:port still
  works. RTSP with the Python examples runs (it used to fail with "Input file not found").
- DX Compiler: Agentic Auto Compile opens on the agent CLI's own default model, and picking a model
  updates the model-quality note.
- AI Help (chat): answers use this PC's dx_app layout and a command that runs here; **Local /
  Self-hosted** finds the models of the endpoint you type; answers through the launcher end cleanly
  instead of holding a connection open.
- DX Stream: Local (WebRTC) playback works when Setup step 6 is done; Setup now checks both of its packages
  (gstreamer1.0-nice and gir1.2-gst-plugins-bad-1.0) and names the missing one. `launcher.sh` repairs a `.venv`
  made without system site packages, which hid the GStreamer bindings from the module servers.
- DX App live RTSP and multi-slot camera runs reach the runner (they ended with "Input file not found"); several
  slots can share a camera without an MJPEG 640x480 mode. DX Stream's Pipeline Builder has a camera source (`v4l2src`).
- EdgeGuide cards show their arithmetic ("534 FPS ÷ 60 FPS = 8.9 → 8 ch", "31.7 FPS each ≥ 30 FPS target") and the
  measured NPU load next to the NPU / host limit; **How ranking works** explains the 85 % limit rule and what
  **Estimated+** means, gives every formula's meaning in your language, and its session summary no longer mixes in
  English.
- Chat answers through the coding agent you are signed in to (claude, copilot, cursor …) with no setup, the same
  agent Home and Agent Dev use; its top line always says which AI answers. Settings ask one question — a coding
  agent on this PC, your local LLM server, or a cloud API key (OpenAI, Anthropic, Google, GitHub Models, custom
  endpoint) — with temperature and the knowledge refresh under Advanced. Saving tests the connection first
  ("Save anyway" when it fails), a blank key keeps the saved one, and "Back to automatic" forgets the choice.
- A first visit opens in the browser's language (Korean, Japanese, Simplified or Traditional Chinese, Spanish;
  English otherwise) instead of always English. A language picked in the menu still wins.
- Chat says why an external API failed instead of showing the offline answer "No AI model connected" to a user who
  set a key: a rejected key, a rate limit, an unreachable host (named, within 15 s rather than 2 minutes) or the
  provider's own reason ("model not found", unsupported parameter). An error in the middle of a stream is reported
  rather than ending the answer silently. Saving in Settings shows the same reasons.
- Faster screens, especially over remote access. Large JSON answers are gzipped and revalidated (the Model Zoo
  catalog went from 2.5 MB to 127 KB, and to a 304 on a repeat visit). Home's module numbers load when home is
  shown, not on every screen. The diagram library loads only for a document with a diagram, and Agent Dev's
  showcase animations are light WebP thumbnails. A first visit now takes 0.9–1.8 MB, down from 4.5–7.3 MB
  (Agent Dev: 7 MB, down from 20.5 MB), and a repeat visit about 200 KB.
- Accessibility (axe WCAG 2 A/AA, light and dark): every form control has a name screen readers can read (model
  checkboxes, A/B Compare, Agent Dev settings, Benchmark Settings, Stream uploads). The page-tab row is a labelled
  navigation, Run Demo cards no longer put Set up inside a button, and Compiler's unavailable phase tabs say so.
  Accent text, status badges and the A/B slot badge meet 4.5:1. The notification drawer's close button was blank
  and now shows its icon. A/B Compare's Model and Language labels are translated.
- Module servers keep their errors in `~/.local/state/dx-ai-studio/logs/`; DX App no longer stops itself after
  an idle hour under the launcher.
- Home: the folded agent line names the model a run will use, and a model picked before the CLI's
  list arrives is kept.
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
