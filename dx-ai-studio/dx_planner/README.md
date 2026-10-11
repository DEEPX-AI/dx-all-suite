# DX EdgeGuide

Pick the best DEEPX Edge AI product (NPU board + host) for your computer-vision
workload. Describe the workload; EdgeGuide ranks the platforms that can handle it using
real **YOLO26 benchmark** measurements, then lets you drill into a platform, compare it
with another, review the evidence, and get product info / a price quote.

## Using it

The whole thing is one page (**DX EdgeGuide**) with a four-step strip —
**Scenario → Pick → Evidence → Buy** — where panels open as you go.

**1. Describe the workload** (Requirements panel).
   - Optionally click a **Quick scenario** chip (**4-ch CCTV OD / 8-ch retail cls / 2-ch pose 30FPS**) to prefill.
   - **AI task**: Object Detection / Pose Estimation / Segmentation / OBB / Classification.
   - **Model size**: n (fastest) → x (most accurate).
   - **Operating requirements**: cameras/**channels**, **target FPS**, runtime
     (ONNX Runtime vs Native), **max latency**.
   - Click **Next — choose ranking**, choose a **ranking priority** — Most channels / Best
     Performance (camera-pipeline FPS) / Lowest Power (NPU TDP; host power not included) —
     then **Get Recommendations**. (After the first run,
     changing any input auto-refreshes the results; **Start over** clears everything.)

**2. Read the recommendations.** A verdict line shows the **Top pick** and whether your
channel/FPS target is met. Each card carries a **Measured** or **Estimated** badge and one line
saying why: "12 ch held 30.4 FPS each (measured) · 13 ch dropped to 28.1 FPS", or "≈ 6 ch
estimated from 365 FPS measured in total (tested up to 13 ch)". The benchmark measured the
stream counts around 30 FPS per channel; at other targets the channel count is estimated from
the measured total FPS (it stays nearly flat around saturation), capped at twice the highest
tested count (**Estimated+**). Notes flag an NPU that throttled during the measurement, whether
the NPU or the host (CPU / decode) was the limit, and a latency that was not measured. Click a
card (or a bar in the throughput chart) to open details.

**3. Explore / compare.** The Details panel shows key facts, platform specs, a
Performance Radar, a sortable benchmark table, and a per-model-size chart. Use
**Compare with** to line up a second platform side-by-side.

**4. Buy / contact.** Pricing is by quote — the Buy panel's **Product info** and **Request
quote** buttons go to DEEPX.

## Key features

- **Real measurements** — recommendations come from the YOLO26 benchmark matrix, not
  spec-sheet math. Channel counts are measured where a tested stream count brackets the
  target, and otherwise estimated from the measured total FPS — every card says which.
- **Open methodology** — the **How ranking works** button shows the exact formulas and a
  live summary; it also states the honest limits (figures are not a full spec sheet; power
  ranking covers the NPU only; contact DEEPX for production sizing and pricing).
- **Multi-stream evidence** — per-channel and total FPS behind each channel estimate.
- **Shareable** — the current selection is captured in the URL, so a link (e.g. arriving
  from DX Benchmark) reproduces the inputs and re-runs the recommendation.
- **AI Help** chat for follow-up questions grounded in your requirements/results.
- **6-language UI** (English / 한국어 / 日本語 / 简体中文 / 繁體中文 / Español) + a guided in-app tutorial.
