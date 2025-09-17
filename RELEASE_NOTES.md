# RELEASE_NOTES

## DX-All-Suite v2.0.0 / 2025-09-08

- DX-Compiler: v2.0.0
  - DX-COM: v2.0.0
  - DX-TRON: v2.0.0
- DX-Runtime: v2.0.0
  - DX_FW: v2.1.4
  - NPU Driver: v1.7.1
  - DX-RT: v3.0.0
  - DX-Stream: v2.0.0
  - DX-APP: v2.0.0

---

Here are the **DX-All-Suite v2.0.0** Release Note.

### What's New?

This release marks a significant step forward with new features and major stability improvements.

- **Performance Boost:** The new "stop & go" inference function and an increase in DMA channel threads improve processing speed, especially for large models.
- **Enhanced Stability:** Critical bug fixes, including a kernel panic and a Python compatibility error, make the platform more reliable across different environments.
- **Powerful New Tools:** The new `dxtop` monitoring tool provides real-time insights into NPU performance, while a USB inference module expands connectivity options.
- **Expanded Model Support:** The compiler now supports new operators like `ConvTranspose`, and most notably, offers partial support for Vision Transformer (ViT) models. This opens up a wider range of AI applications.

---

### Key Updates

**Performance & Efficiency:**

- Implemented a new "stop & go" inference function that splits large tiles for better performance.
- Increased the number of threads for the `DeviceOutputWorker` from 3 to 4.
- YOLO post-processing logic was updated to use a `RunAsync() + Wait()` structure to ensure correct output order.
- The default build option for DX-RT is now `USE_ORT=ON`, which enables the CPU task for `.dxnn` models by default. Add automatic handling of input dummy padding and output dummy slicing when `USE_ORT=OFF` (build-time or via InferenceOption).

**Stability & Fixes:**

- Resolved a kernel panic caused by an incorrect NPU channel number.
- Fixed a build error on Ubuntu 18.04 related to Python 3.6.9 incompatibility by adding automatic installation support for a compatible Python version (3.8.2).
- Corrected a QSPI read logic bug that could cause underflow.
- Addressed a processing delay bug in `dx-inputselector` and fixed a bug in dx_rt that affected multi-tail models.
- In DX-COM, `PPU(Post-Processing Unit)` is no longer supported, and there are no current plans to reinstate it.

**New Features & Tools:**

- Added a new USB inference module.
- Introduced a new terminal-based monitoring tool called `dxtop` for real-time NPU usage insights.
- A new `dxrt-cli --errorstat` option was added to display detailed PCIe error information.
- Support for the `Softmax`, `Slice`, and `ConvTranspose` operators was enabled.
- Partial support for Vision Transformer (ViT) models was added.
- Implemented a new uninstall script (`uninstall.sh`) for project cleanup.
- In DX-RT, add support for both .dxnn file formats: v6 (compiled with dx_com 1.40.2 or later) and v7 (compiled with dx_com 2.x.x).

For detailed updated items, refer to **each environment & module's Release Notes.**

---

## DX-All-Suite v1.0.0 Initial Release / 2025-07-23

We're excited to announce the **initial release of DX-All-Suite (DX-AS) v1.0.0!**

DX-AS is your new integrated environment, bringing together essential frameworks and tools to simplify AI model inference and compilation on DEEPX devices. While you can always install individual tools, DX-AS ensures optimal compatibility by aligning all tool versions for you.

---

### What's Included?

This initial release provides a comprehensive suite to get you started:

- **Integrated Environment:** A unified platform for all your DEEPX AI development needs.
- **Optimal Compatibility:** Pre-aligned versions of individual tools to guarantee seamless operation.

---

### Key Documentation

To help you hit the ground running, we've prepared detailed documentation:

- **Introduction:** Get a comprehensive overview of DX-AS.
- **Installation Guide:** Step-by-step instructions to set up your environment.
- **Getting Started:** A quick guide to begin using DX-AS.
- **Version Compatibility:** Information on supported versions and configurations.
- **FAQ:** Answers to commonly asked questions.

You can find all these resources and more in the `docs` directory of the repository.

---
