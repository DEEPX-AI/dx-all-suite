# Change Log

Notable changes to the DX-AI-Studio User Manual.

## v0.1.1 hotfix / 2026-11

**Setup, Model Zoo, EdgeGuide and Hub**

- A fresh board (incl. Raspberry Pi / aarch64) is ready after one Demo Quick Start: it also prepares the Python
  inference interpreter, keeps the runtime venv through the driver step, never stops on a package dialog, and
  builds for the board's own CPU architecture. No restart is needed after Setup steps.
- Setup → **Maintenance**: Clean build, Reset and reinstall. Deep Diagnostics: **NPU sanity check**.
- Model Zoo: **Build C++ runner** for a downloaded model; new C++ runners show up without a restart.
- The NPU Linux Driver step counts as done only when the driver is installed for the next boot, not merely loaded,
  so Demo Quick Start after a reset reinstalls it instead of leaving the board without a driver after reboot.
- Setup jobs no longer overlap: a second job (e.g. a Model Zoo build during a Setup step) is refused.
- Model Zoo: *Supported hardware* in each model's Specification — DX-M1 and DX-H1 Quattro; DX-M1M per model once
  DX Model Zoo records it (until then: not confirmed yet).
- EdgeGuide: NPU memory as `dxrt-cli -s` measures it — DX-M1 3.9 GB LPDDR5 5600 Mbps, DX-M1M 1.9 GB LPDDR4 4200 Mbps,
  DX-H1 Quattro 15.7 GB LPDDR5x 6000 Mbps (4 chips). It read 1 GB for both M1 and M1M.
- **NPU Driver** in Setup's Version Info (DX App and DX Stream) shows the driver's own version (e.g. v2.7.0), not the
  DX-RT version that `dxrt-cli --version` prints.
- Hub: the *Measured on DX-M1* tour step says these are DEEPX's DX Model Zoo figures on DX-M1, not a run on this
  computer. DX App's engine-error hint points to Setup → Deep Diagnostics instead of a Mock mode DX App does not have.
- Hub: the link bar under the stage keeps room to spare, so it stays on one row (en at 1440 px, es at
  1280 px) in browsers that draw text slightly wider; before, Spanish at 1280 × 800 no longer fit one screen.
- Deep Diagnostics (DX App, DX Stream) asks DKMS for the DX-RT driver module only: 1–2 s instead of 6.5 s on a
  board with other DKMS modules and several kernels.
- DX Stream Demo Launcher follows the installed dx_stream: Secondary Inference finds the SDK's
  efficientnet-lite0_224x224 model, and the Face / Pose PPU demos the SDK no longer ships are not listed (they
  stayed "Needs setup" with nothing to install).
- Agent Dev shows a build started on Home (or Agent Dev work from Auto Compile) also when Agent Dev was opened
  earlier in the session; before, it showed it only on its first visit.
- SDK Library document viewer:
  - The DX All Suite architecture figure shows again. Images marked `#only-light` / `#only-dark` were broken;
    the viewer now shows the one for the current theme.
  - Section links (`#…`, also `## Title {#id}` headings) scroll the document; they opened the Studio again
    in a new tab. A link to a section of another document opens it at that section.
  - Links written as HTML open the document in the viewer instead of a 404 tab, also on a page that includes
    another file (the Agent-Driven Development showcase catalog).
  - Inline code shows exactly what the document wrote: `<variant>_sync.cpp` and `<dxrt/dxrt_api.h>` lost the
    part in angle brackets.
  - Links to a file the Library does not show (it lists the documents users need) or that is not a
    document (.py, .sh, a folder) read as plain text instead of a link that does nothing.
- Sample videos no longer keep their 1.2 GB archive after extraction; Setup warns below 5 GB free disk.

## v0.1.1 / 2026-10

Changes since the v0.1.0 beta manual.

**Hub and design**

- New home: a prompt box (*Describe anything. Run it on DX-M1.*) that first suggests tool
  routes or an agent plan, then waits for the user's selection; tool cards with live facts,
  a DX-M1 widget, a "Measured on
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
  Continuous runs with reported FPS, async execution options, Model Zoo
  inference that runs each model's own example, and runner errors reported as errors.
- DX App: **Graph Composer** replaces the Lab composer: several models and logic blocks in one graph, checked as you
  edit, run once or Live with events, exported as a standalone C++ project; nine scenario templates with real NPU
  results, every template and example named in six languages, and a guided tour.
- The Graph guide stays within **DX App** and explains preparation, validation, memory,
  Layers / frame re-execution, events and Live job conflicts. Project history retains
  the latest **50 versions**; editable JSON and runnable-project zip exports are distinct.
- DX Stream: Demo Launcher on the same stage with WebRTC or remote MJPEG playback; Setup as a
  step list; launches work on a board whose Stream contracts validate.
- Model Zoo: **497 canonical variants across 29 tasks** at dx_app dev `2e20108a5`,
  aligned with the Studio internal snapshot dated 2026-10-13 (348 → 497, +149).
  Counts refer to variants, not distinct architectures. Existing model example images
  are reused; catalog inclusion does not mean every variant supports Graph execution
  (**492** do at this revision).
- Model Zoo and DX App: PP-ShiTu's two mainbody detectors are listed under their own task, **Main-body
  Detection** (as on DX Model Zoo), in six languages.
- **DX Cloud** (ninth module): AWS Compiler (Marketplace subscription, compiler stacks, cloud compile with its log
  and `.dxnn` download) and AWS Greengrass (dx-runtime devices), with a numbered setup flow and guides.
- DX Compiler, DX App and DX Stream: Setup shows the next step and why a button is locked.
- SDK Library follows the suite's documentation, with List / Cabinet browsing and an
  opened-document viewer.
- More DX App controls and messages now use the selected UI language;
  Korean spacing follows Korean orthography; server errors are translated.
- DX EdgeGuide: channel counts come from the measured end-to-end pipeline throughput. They are
  measured where a tested stream count brackets your target FPS and estimated otherwise
  (capped at twice the tested count). Each card says which, and why, in one line, with notes
  for NPU throttling, whether the NPU or the host was the limit, and unmeasured latency.
  60 FPS no longer reads 0 channels almost everywhere. Best Performance ranks by camera-pipeline
  FPS; Lowest Power by NPU TDP (host power excluded).
- DX Agent Dev: a **Stop** button while an agent runs; a dropped connection no longer stays
  "Running…".
- Monitor guidance distinguishes **unavailable**, **stale** and explicit **Mock** telemetry;
  a connected browser stream alone is not proof of current NPU data.
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
- Faster screens, especially over remote access: catalog responses are compressed and
  revalidated, Home facts load when Home is shown, diagrams load when needed, and Agent
  Dev showcases use lightweight thumbnails.
- Accessibility improvements: form controls have names screen readers can read (model
  checkboxes, A/B Compare, Agent Dev settings, Benchmark Settings, Stream uploads). The page-tab row is a labelled
  navigation, Run Demo cards no longer put Set up inside a button, and Compiler's unavailable phase tabs say so.
  The notification drawer's close button now shows its icon. A/B Compare's Model and
  Language labels are translated.
- Module servers keep their errors in `~/.local/state/dx-ai-studio/logs/`; DX App no longer stops itself after
  an idle hour under the launcher.
- Home: the folded agent line names the model a run will use, and a model picked before the CLI's
  list arrives is kept.
- All modules: phone-width (390 px) layouts fixed for Setup, EdgeGuide cards, Compiler tabs,
  Benchmark Settings/Results, the Lab home and the SDK Library; dozens of mistranslations
  fixed (e.g. Setup no longer reads as Settings); the AI Help knowledge matches today's UI.

These notes describe user-facing changes and clarified workflows. They do not certify
a new NPU run, AWS deployment, screenshot capture, or documentation build on the reader's
environment.

## v0.1.0 / 2026-07

- Initial DX-AI-Studio User Manual (studio **v0.1.0**, beta): MkDocs (Material) site
  covering installation & launch, the hub, all eight tools (DX Compiler, DX App,
  DX Stream, DX Model Zoo, DX Benchmark, DX Monitor, DX EdgeGuide, DX Agent Dev), and
  the SDK Library & About views. English, with PDF export.  

!!! note  
    For per-component release notes (runtime, compiler, stream, …), see each
    sub-project's `RELEASE_NOTES.md` in the DEEPX SDK, available in the in-app
    [SDK Library](11_SDK_Library_and_About.md).
