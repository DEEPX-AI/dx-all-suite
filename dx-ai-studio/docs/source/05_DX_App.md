# DX App

Run AI inference on the DEEPX NPU from your browser — pick a model, run it on images,
video, a camera or an RTSP stream, watch live results, and benchmark or compare models.

![DX App — the Models page with task filters, the model table, and the live NPU monitor.](resources/app.png)

## Using it

The module opens on a set of pages (top tabs):

- **Setup** — guided environment check; run it first so the NPU / runtime is ready.  
- **Models** — the model list across 29 AI tasks in the October 2026 reference (detection, classification, segmentation,
  pose, depth, super-resolution, 3D object detection, PPU and more), drawn from the Model
  Zoo catalogue; open a model for details or its graph. The reference contains **497
  canonical variants**, not 497 distinct architectures; counts depend on the loaded catalog.
  The Hub / Zoo's **31 UI category groups** differ from the Graph palette's **29
  canonical tasks**; this does not change the variant count.
- **Run Inference** — pick a **category → model → input**, then Run. Two tabs:  
    - **Single** — one image or video. Inputs adapt to the category: a sample image, your
      **own uploaded image**, or a video (some tasks are image-only; special inputs like 3D
      LiDAR `.bin` appear where they apply). Image runs show a **before/after compare slider**.  
    - **Continuous** — video, camera or RTSP streamed live, with several slots side by side.
      For RTSP, paste the camera's full URL (`rtsp://user:pass@cam:554/…`); an `IP:Port` with a
      stream pick still works.
      A model that takes still images only is refused with an explanation.  
- **Run Demo** — 26 ready-made demos in 12 groups on one stage: choose a demo, the input
  (image or video), C++ or Python, Sync or Async, and run. Video runs stream live with FPS.  
- **Benchmark** / **A/B Compare** — measure a model's throughput and compare models side by
  side; Benchmark can run several models in a batch and **export a report**.  
- **ModelZoo** — browse and download additional models into the app (public or air-gapped
  source, Q-Lite / Q-Pro variants, batch cart).  
- **Graph Composer** — a DX App feature for connecting sources, models, CPU operations
  and logic on a canvas, then validating, running and exporting the pipeline.
  Follow the [Graph Composer workflow](#graph-composer) below.
- **Lab** — advanced tools, each with a change preview before anything is written:  
    - **Add Model** — copies an existing example of a category (**Start from**) under a new name,
      in C++, Python or both. Run the Python copy with your own model:
      `python3 <name>_sync.py --model <your>.dxnn`. Build the C++ copy with dx_app's `build.sh`.  
    - **Create Task** — skeleton code for a new task type.  
    - **Experiment** — checks a compiled `.dxnn` on the board: reads the file, runs one inference,
      then measures throughput (FPS).  
    - **Generated Files** / **Safety Center** — what each change wrote. A change that only created new
      files can be rolled back after typing `rollback:<name>`; one that overwrote files has to be
      restored by hand.  
- **Outputs** — browse and manage saved inference results (grid / table, filters, preview).  
- **Reference** — searchable in-app feature and parameter guides.  

### First inference or demo

1. Open **Setup** and complete the environment checks. For a first demo, use **Demo
   Quick Start → Start Demo Setup**; review the installation progress and any failed step.
2. When setup is ready, choose **Try demo**, select a demo and a supported sample input,
   then run it. Alternatively, use **Run Inference → Single**, select a category, model
   and sample / uploaded image, and run.
3. Inspect the result and reported timings; saved results appear in **Outputs**.
   If a model, binary or runtime is missing, return to the named Setup step or download
   the model and retry. An error is not a completed inference.

Quick Start prepares the demo runners, their models and sample videos, not every
per-model build target. The full Setup checks the declared model set and the runners
needed by the demo and Graph workflows. Xvfb is an optional Live requirement, not a
reason to repeat the base dependency installation.

A local asset without a current Studio completion record is **unverified**, not
missing. Use **Verify** or rerun the corresponding setup step to check existing
content and finish preparation; matching files are kept. Video folders without a
completed Studio archive inventory remain unverified even if individual files have
completion records. An installed file or a ready demo set is not proof of a complete,
verified archive or a successful inference.

!!! note "Live runs"
    Continuous, Run Demo video and Graph Live draw the example's window on a virtual
    display and stream it to the browser. Their optional display requirements are listed
    under [Prerequisites](01_Installation_and_Launch.md#prerequisites).

From the Run page you can also **Export Model Package** — bundle a model's source, config,
and file (C++ / Python / both) for reuse.  

## Graph Composer {#graph-composer}

Use **DX App → Graph Composer** to build a multi-model workflow without writing the
runner yourself. It is part of DX App, not a separate Studio tool.

### Prepare and validate

1. Open **Templates** and choose a scenario, such as restricted-zone intrusion or line
   counting. Other scenarios include PPE, dwell, zone counts, gallery matching, driver
   attention, multi-camera counts and volume alerts. Engine examples are also available;
   names and descriptions follow the UI language.
2. Check the template's models in the palette. Installed models are marked; use
   **Download** for missing files. The connected dx_app must provide the graph runners
   and the required capabilities. At reference revision `2e20108a5`, **492 of 497
   canonical variants** are graph-runnable: four anomaly-detection variants are not
   graph-ready, and the LiDAR model (`sfa3d_608x608`) needs an unsupported source.
3. Select each **Source** and set its input. Start with a local sample image or video
   for **Run once**; camera and RTSP sources are for **Live**. For several sources,
   supply an input for each. File paths refer to the Studio host, not the remote browser.
4. Select nodes / connections and use the **Inspector** to change properties. The graph
   is checked after edits; use **Validate** to inspect current errors pinned to their
   node or edge. Check the NPU memory bar as well. Fix missing models, incompatible
   connections or excess memory before running; engine sharing or fewer buffers can
   reduce memory where the runner supports them.

Keyboard editing includes Tab between nodes, arrows to move, Delete, and Ctrl+Z/Y.

![DX App Graph Composer — an example graph, palette, Inspector and memory / validation status. An editable graph is not proof of a successful run.](resources/app-graph-composer.png)

### Run once and read the result

Choose **Sync / Async** and **Run once**. Watch progress, FPS and per-node time, then
inspect the rendered output and node results. Multiple sources appear as a grid.
**Layers** toggle individual node drawings without changing the graph.

For a paused video, **Layers for this frame** executes the selected input frame again
on the NPU. It does **not** restore the original tracker, zone, dwell, condition or
gallery state: track IDs, event times and results can differ from the original video.
It also needs a free NPU slot and the frame-reading dependencies.

![DX App Graph results — a real NPU run using the official YOLOv8n model in v8 .dxnn format. This example demonstrates the selected graph, not execution of all 497 catalog variants.](resources/app-graph-results.png)

### Add logic, zones and events

Connect model results to **Filter**, **Zone**, **Line crossing**, **Count**, **Dwell**,
**Condition → Event** or **Gallery match**, as offered by the installed runner.
For example, open the intrusion template, select its Zone block and choose
**Edit on the frame…**. Set a file input first; draw / adjust the polygon on its first
frame, then run a video and inspect the emitted events. A camera or RTSP URL has no
local first frame for this editor; use a representative file input to define the zone.

Line-crossing and dwell logic need detector tracking enabled. **Gallery match** needs
its gallery prepared; a gallery build uses the NPU. **User logic** passes data through
in Studio until you implement its exported C++ stub.

Filter the event list by node, event, track ID or time. Clicking an event seeks the
result video to that moment; download **JSONL** for later analysis. No events can mean
the rule was never met — check inputs, tracking and thresholds before assuming a failure.

### Live, save and export

- **Live** runs a camera, RTSP stream or looping video until **Stop**. Only one Graph
  Live runs at a time, and leaving Graph Composer stops it. Graph Run once, Graph Live,
  the Run page's Continuous / Live slots and gallery builds exclude each other.
  Multiple ordinary Continuous slots may run together; stop those slots before Graph.
- **Save / Ctrl+S** stores a project on the Studio host under
  `outputs/dx_app/graph/projects/`. Only the **latest 50 versions per project** are kept;
  use the version selector to reopen a retained version.
- **JSON export / import** transfers the editable graph definition. It is not a model
  bundle or a standalone executable project.
- **Export C++ project** first shows an export plan, then produces a **zip** containing
  a standalone CMake project, the selected engine code, `main.cpp`, `graph.json`,
  `setup.sh`, `run.sh` and a README. Model files are excluded by default;
  **Include the model files** requires all of them to be installed. Otherwise the
  exported setup downloads them. User logic becomes pass-through stubs under
  `user_logic/` that you must implement. Follow the exported README for DX-RT, CMake,
  C++17 and OpenCV requirements; export success alone does not validate another host
  or guarantee identical stateful results. The server retains the **newest five exports**
  under `outputs/dx_app/graph/exports/`; download the zip to keep a copy.

If an action is blocked, read the validation / runtime reason: prepare the missing
runner or model, correct the input / connection, reduce memory, or stop the NPU job
named by the message, then retry. Missing hardware is **not** an automatic Graph mock
mode. The **Tutorial → Graph Composer** walkthrough can show recorded results without
starting the NPU or replacing unsaved work; those previews are not your own run.

You can browse Studio without an NPU, but real inference requires the hardware and
runtime. Availability and errors are shown rather than making every page a mock demo.

!!! note "Related"
    Run the `.dxnn` files produced by **[DX Compiler](04_DX_Compiler.md)**; the same
    NPU telemetry is visualized live in **[DX Monitor](07_DX_Monitor.md)**.  
