# RELEASE_NOTES

##  DX-All-Suite v2.3.1 / 2026-05-06

- DX-Compiler: v2.3.1
    - DX-COM: v2.3.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.3.1
    - DX_FW: v2.5.6
    - NPU Driver: v2.4.1
    - DX-RT: v3.3.1
    - DX-Stream: v3.0.1
    - DX-APP: v3.1.1

---

Here are the **DX-All-Suite v2.3.1** Release Note.

### What's New?

This patch release focuses on stability improvements, documentation corrections, license compliance, and firmware stability across the DX-Compiler installer, DX-Runtime, and DX-Stream modules.

- **Installer Fix (DX-Compiler)**: `uninstall.sh` now properly removes all installed packages and extracted module directories, and supports a new `--target` option for selective uninstallation.
- **Runtime Compatibility (DX-RT)**: Updated pre-built library versions (onnxruntime, openvino) for improved compatibility.

---

### Key Updates

**Stability & Fixes**

- **DX-Compiler Installer**: Fixed `uninstall.sh` not removing installed packages (`dx_com` via `pip3 uninstall`) and the `dxtron` Debian package (`apt-get remove`), and not deleting extracted `dx_com/` and `dx_tron/` directories.
- **DX-RT**: Updated pre-built onnxruntime (1.23.2 → 1.22.0) and openvino (25.4 → 25.1) for improved compatibility.
- **DX-Stream**: Fixed uninstall not removing apps build directories and pydxs build cache.

**New Features & Tools**

- **DX-Compiler Installer**: Added `--target=<dx_com|dx_tron|all>` option to `uninstall.sh` (default: `all`), consistent with `install.sh`.
- **DX-APP & DX-Stream**: Added license information for third-party models and datasets.

For detailed updated items, refer to **each environment & module's Release Notes**.

---

##  DX-All-Suite v2.3.0 / 2026-04-10

- DX-Compiler: v2.3.0
    - DX-COM: v2.3.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.3.0
    - DX_FW: v2.5.6
    - NPU Driver: v2.4.1
    - DX-RT: v3.3.0
    - DX-Stream: 3.0.0
    - DX-APP: v3.1.0

---

Here are the **DX-All-Suite v2.3.0** Release Note.  

### What's New?

This major release focuses on Runtime Efficiency, Security Hardening, and a Unified Application Architecture. Significant optimizations in the YOLO post-processing pipeline and a major overhaul of the DX-Stream architecture make this our most robust release to date.  

- **TopK-Optimized YOLO Pipeline**: DX-COM v2.3.0 introduces a high-efficiency post-processing pipeline for DFL-based YOLO models, applying TopK filtering before decoding to drastically reduce CPU overhead.  
- **Modular & Sudo-less DX-Stream (v3.0.0)**: A complete architectural refresh of the streaming module, featuring a new kernel abstraction for hardware backends and a user-friendly installation that no longer requires root privileges.  
- **Unified APP Framework**: DX-APP v3.1.0 establishes a strict 5-layer design pattern, ensuring 1:1 parity between C++ and Python implementations for seamless cross-language development.  
- **Enterprise Linux Support**: DX-COM validation has expanded to include Fedora 42–45, Red Hat 9–10, and CentOS Stream 9–10.  

---

### Key Updates

**Performance & Efficiency**  

- **DFL Post-Processing**: Optimized pipeline for YOLO models decoder reduces CPU workload by filtering candidates via TopK before bounding box decoding.  
- **NPU Latency**: Reduced inference latency for the majority of supported models through compiler optimizations.  
- **Zero-Copy Streaming**: DX-Stream now supports DMA-Buffer zero-copy in RGA and DXOSD, reducing memory bandwidth usage.  
- **CPU Acceleration**: Introduced optional build-time features for CPU-bound operation acceleration in the runtime.  

**Stability & Fixes**  

- **Hardware Compatibility**: Fixed 64-bit PCIe TLP errors on Raspberry Pi 4 and resolved ARM64 IOMMU DMA coherency bugs.  
- **Multi-Device Handling**: Fixed PPU data transfer errors and IPC exceptions occurring in multi-process/H1/multi-M.2 environments.  
- **Robustness**: Implemented DMA abnormal recovery for improved system resilience and fixed PPU safety via 2-cell memory alignment.
- **Power Saving**: Re-enabled run mode NPU and hardened devMode race.

**New Features & Tools**  

- **Expanded AI Tasks**: Added native support for Depth Estimation (FastDepth) and Image Restoration (DnCNN, Zero-DCE, ESPCN).  
- **Massive Model Zoo**: Integrated 280+ models across 17 categories with 560+ examples, supported by a new manifest-based auto-download system.  
- **Development Tools**: Added `dxtop` for No-Service Mode monitoring and new GStreamer elements (`DxScale`, `DxConvert`) for HW-accelerated scaling and color conversion.  

### Known Issues

- **PReLU Activation**: Significant FPS degradation persists in models using PReLU activation functions.  
- **Accuracy Variability**: Certain models (OSNet, RepVGGA2, YoloV9C) may show accuracy variability depending on the host CPU and calibration dataset.  


### Migration Guide

- **DX-Stream v3.0.0 (Breaking Change)**: Users must move environment variables from `/etc/profile.d/` to ~/.bashrc. Models are now managed via `dx-modelzoo`; run setup_sample_models.sh to update.  
- **DX-APP v3.1.0**: Project structures have changed to follow the 5-layer pattern. Refer to the new `src/` directory for updated implementation standards.  
- **Minimum Dependencies**: DX-RT v3.3.0 now requires NPU Driver v2.4.0+ and Firmware v2.5.2+ at a minimum.  

For detailed updated items, refer to **each environment & module's Release Notes.  

---

## DX-All-Suite v2.2.2 / 2026-02-26

- DX-Runtime: v2.2.2
    - DX-APP: v3.0.2
    - DX-STREAM: v2.2.1
- DX-Compiler v2.2.1
    - DX-COM: v2.2.1

---

Here are the **DX-All-Suite v2.2.2** Release Notes.

### What's New?

This release enhances the development experience with GPU-accelerated quantization and improved Windows platform support.

- **GPU-Accelerated Quantization**: DX-COM now supports GPU quantization via JSON configuration with automatic GPU detection, significantly speeding up the compilation process.
- **Enhanced Windows Support**: Improved Windows build stability with automated vcpkg installation and fixed compatibility issues.

---

### Key Updates

**Performance & Efficiency**

- GPU Quantization: Added `quantization_device` support in JSON configuration for CLI-based GPU quantization. Automatic GPU detection falls back to CPU when CUDA is unavailable.
- Windows Build: Automated DLL copying (dxrt, vkpkg) to dx-app/bin directory and added vcpkg installation script for streamlined Windows builds.

**Stability & Fixes**

- Fixed DXQ enhanced quantization option bugs in DX-COM.
- Fixed PPU compilation bug in Python Wheel Package for Python 3.8, 3.9, and 3.10.
- Fixed an issue where compilation proceeded without error when invalid model input names were specified.
- Removed experimental filesystem includes and updated float literals in example cpp files to resolve Windows build errors.
- Refactored apply_argmax to reduce nesting and fix gcovr warnings.

**Known Issues**

- Significant FPS degradation has been observed in models using PReLU as an activation function.

---

## DX-All-Suite v2.2.1 / 2026-02-06

- DX-Runtime: v2.2.1
    - DX-APP: v3.0.1

---

Here are the **DX-All-Suite v2.2.1** Release Note.

### What's New?

This release focuses on enhancing the YOLO ecosystem with expanded model variant support and improved flexibility in post-processing.

- **Extended YOLO26 Coverage**: Full support for YOLO26 variants including classification, pose estimation, segmentation, and oriented bounding box detection.

---

### Key Updates

**Stability & Fixes**

- Fixed hardcoded attribute size limitation in YOLO post-processing that could cause issues with models having different output configurations.

**New Features & Tools**

- Add yolov26 cls, yolo26 pose, yolo26 seg, yolo26 obb examples

---

##  DX-All-Suite v2.2.0 / 2026-01-16

- DX-Compiler: v2.2.0
    - DX-COM: v2.2.0
    - DX-TRON: v2.0.1
- DX-Runtime: v2.2.0
    - DX_FW: v2.5.0
    - NPU Driver: v2.1.0
    - DX-RT: v3.2.0
    - DX-Stream: v2.2.0
    - DX-APP: v3.0.0

---

Here are the **DX-All-Suite v2.2.0** Release Note.

### What's New?

This release introduces a **Python-Centric Ecosystem** and a **Complete Example Overhaul**, making development more intuitive and integrated.

- **Python-First Workflow**: DX-COM is now available via `pip` (Wheel), and new Python bindings (`pydxs, dx_postprocess`) allow for seamless metadata and post-processing management directly in Python.
- **Major DX-APP Refactoring (v3.0.0)**: Legacy demos have been replaced with a modern, task-oriented example system. This includes built-in support for the latest YOLO generations (v26, v10/v11/v12).
- **Expanded Hardware Acceleration**: PPU (Post-Processing Unit) support has been extended to the newest YOLO models, further offloading CPU tasks to the NPU.
- **Advanced Resource Management**: The introduction of NPU QoS (Quality of Service) and improved asynchronous handling ensures stable performance in multi-tasking environments.

---
### Key Updates

**Performance & Efficiency**  
- Extended PPU Support: Hardware-accelerated post-processing now supports YOLO26, YOLOv8, v9, v10, v11, and v12.
- PCIe DMA Optimization: Reduced CPU dependency and improved sequence efficiency for high-speed data transfer (requires DX-RT SDK v3.2.0+).
- Inference Reporting: Updated `inf_time` to include both NPU and PPU runtimes for realistic performance profiling.
- Resource Prioritization: Added QoS to the NPU Scheduler to manage execution priority effectively.
- Memory Footprint: Further reduced device memory usage for models utilizing PPU.

**Stability & Fixes**
- PCIe Stability: Added PERST# signal wait during initial boot stage to ensure reliable link establishment.
- Soft Lockup Prevention: Added sleep/reschedule logic in polling to prevent system hangs during slow hardware ACKs.
- Stream Stability: Resolved race conditions and segfaults in secondary inference modes with shared buffers.
- Model Accuracy: Fixed a known accuracy degradation issue in the DeepLabV3PlusMobilenet-1 model.
- Code Robustness: Implemented global `try-catch` handling and improved argument validation across the application layer.

**New Features & Tools**
- Installation & Deployment:
    - DX-COM Wheel: Install the compiler via `pip` for automated ML pipelines and Jupyter environments.
    - DX-TRON Debian: Added `.deb` package support for Ubuntu 20.04/22.04/24.04.
- Development Tools:
    - YOLO26 Support: Integration of the latest Ultralytics model optimized for edge deployment.
    - `RuntimeEventDispatcher`: A new centralized C++/Python singleton for handling system events, errors, and warnings.
    - `pydxs`: New Python binding for managing Stream metadata (`DXFrameMeta, DXObjectMeta,` etc.).
- Engine Capabilities: Enabled direct `.dxnn` model loading from memory buffers and per-instance I/O buffer configuration.
- Testing Infrastructure: Established a Pytest-based E2E test system for DX-APP, achieving over 93% code coverage.

**Known Issues**
- PReLU Degradation: Significant FPS drops may occur in models using PReLU activation functions.
- PPU Conversion Gap: DX-Compiler v2.2.0 does not yet support converting face/pose models to PPU format (requires v1.0.0 for these specific tasks).
- Breaking Changes: DX-APP v3.0.0 is not backward compatible with v2.x legacy demos or JSON configuration files.

**Migration Guide**
- Example Transition: Move from the `demos/` directory to the new `src/cpp_example/` and `src/python_example/` structures.
- Configuration: Replace legacy JSON config files with the new Command-Line Argument system in Python (e.g., for YOLO26 execution).
- Environment: Update your Python environment using the provided `requirements.txt` to support the new `dx_engine` and `pydxs` modules.

For detailed updated items, refer to **each environment & module's Release Notes.

---

##  DX-All-Suite v2.1.0 / 2025-11-28

- DX-Compiler: v2.1.0
    - DX-COM: v2.1.0
    - DX-TRON: v2.0.0
- DX-Runtime: v2.1.0
    - DX_FW: v2.4.0
    - NPU Driver: v1.8.0
    - DX-RT: v3.1.0
    - DX-Stream: v2.1.0
    - DX-APP: v2.1.0

---

Here are the **DX-All-Suite v2.1.0** Release Note.

### What's New?
This release marks a significant step forward with new features and major stability improvements across all core components.

- **PPU Acceleration Integrated:** The Post-Processing Unit (PPU) is fully integrated into the compiler (DX-COM), runtime (DX-RT), and streaming (DX-Stream) layers. This allows the NPU to handle NMS/bounding box decoding for models like YOLO and SCRFD, drastically reducing CPU overhead.
- **Next-Gen Model Support:** The entire stack now supports the new DXNN V8 file format and DXNNv8 PPU models (DX-RT and DX_FW), enabling the newest generation of AI applications.
- **Windows Ecosystem:** Full support for Windows 10/11 has been added to the DX-APP layer, complete with automated build scripts, making cross-platform development easier.
- **Advanced Diagnostics & Profilers:** New dedicated tools like the dxbenchmark, and GstShark integration provide comprehensive performance evaluation and optimization capabilities.

---

### Key Updates

**Performance & Efficiency**  
- PPU Integration (Full Stack): PPU functionality is reinstated in DX-COM and integrated into DX-Stream and DX-APP to offload post-processing tasks (NMS/decoding) from the CPU.
- LPDDR Stability: DX_FW reduced the LPDDR Training Margin (0.7 -> 0.62) and added enhanced margin testing logic to boost system stability.
- Runtime Performance: DX-Stream enhanced buffer processing via direct buffer manipulation and disabled synchronization in the video sink (secondary mode).
- Optimization Tools: DX-COM added the --aggressive_partitioning option and optimization level control (--opt_level {0,1}).
- Asynchronous Processing: DX-RT implemented the Asynchronous NPU Format Handler (NFH) for non-blocking inference.

**Stability & Fixes**  
- Critical Multi-Model Fixes (DX-RT): Resolved a critical bug affecting models with multi-output and multi-tail configurations and fixed several multi-tasking and CPU offloading buffer management issues.
- Pipeline Stability (DX-Stream): Fixed a critical event processing timing issue in dxinputselector that caused compositor pipeline freezes.
- LPDDR/Boot Stability (DX_FW): Fixed LPDDR frequency display issues after CPU reset, resolved PRBS training fail judge logic, and improved PCIe link-up stability (including RPi5 warm boot).
- Windows Fixes (DX-APP/DX-RT): Fixed Windows MSBuild warnings using explicit static_cast (DX-APP) and fixed Windows environment compile errors (DX-RT).
- Compiler Flexibility (DX-COM): Removed restrictions on key operators: Split, Transpose, Reshape, Flatten, and Slice.

**New Features & Tools**  
- DXNN V8 Model Support: Added support for the V8 DXNN file format and DXNNv8 PPU models across the stack.
- Windows Support (DX-APP): Added full Windows 10/11 environment support with an automated build script (build.bat).
- Advanced Diagnostics & Monitoring:
    - DX-RT: Added DX-Fit tuning toolkit, dxbenchmark (performance comparison CLI), and model voltage profiler.
    - DX-Stream: Added GstShark integration for comprehensive pipeline performance analysis.
    - DX_FW: Added Secure Debug and Model Profiling mode.
- PPU Data Types: DX-APP added support for three new PPU data types: BBOX, POSE, and FACE.
- DX_COM: Added Partial Compilation support (--compile_input_nodes/--compile_output_nodes).

**Known Issues (DX-APP / DX-COM)**
- Accuracy degradation observed in the DeepLabV3 Semantic Segmentation model.
- DX-Compiler v2.1.0 does not yet support converting face detection and pose estimation models to PPU format.

For detailed updated items, refer to **each environment & module's Release Notes.

---

##  DX-All-Suite v2.0.0 / 2025-09-08

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

**Performance & Efficiency**  
- Implemented a new "stop & go" inference function that splits large tiles for better performance.
- Increased the number of threads for the `DeviceOutputWorker` from 3 to 4.
- YOLO post-processing logic was updated to use a `RunAsync() + Wait()` structure to ensure correct output order.
- The default build option for DX-RT is now `USE_ORT=ON`, which enables the CPU task for `.dxnn` models by default. Add automatic handling of input dummy padding and output dummy slicing when `USE_ORT=OFF` (build-time or via InferenceOption). 

**Stability & Fixes**  
- Resolved a kernel panic caused by an incorrect NPU channel number.
- Fixed a build error on Ubuntu 18.04 related to Python 3.6.9 incompatibility by adding automatic installation support for a compatible Python version (3.8.2).
- Corrected a QSPI read logic bug that could cause underflow.
- Addressed a processing delay bug in `dx-inputselector` and fixed a bug in dx_rt that affected multi-tail models.
- In DX-COM, `PPU(Post-Processing Unit)` is no longer supported, and there are no current plans to reinstate it.

**New Features & Tools**  
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

* **Integrated Environment:** A unified platform for all your DEEPX AI development needs.
* **Optimal Compatibility:** Pre-aligned versions of individual tools to guarantee seamless operation.

---

### Key Documentation

To help you hit the ground running, we've prepared detailed documentation:

* **Introduction:** Get a comprehensive overview of DX-AS.
* **Installation Guide:** Step-by-step instructions to set up your environment.
* **Getting Started:** A quick guide to begin using DX-AS.
* **Version Compatibility:** Information on supported versions and configurations.
* **FAQ:** Answers to commonly asked questions.

You can find all these resources and more in the `docs` directory of the repository.

---
