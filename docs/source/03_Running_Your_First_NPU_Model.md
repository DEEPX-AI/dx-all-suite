# Running Your First NPU Model

This guide covers the end-to-end practical process for running actual AI models on **DEEPX NPU** after completing all installations. By running the automation scripts in sequence, you can experience the entire pipeline from model compilation to successful inference.  

## Overall Pipeline

DEEPX NPU model deployment follows a structured 6-step workflow (Steps 0–5), from optimization (Compiler) to execution (Runtime).  

| Step | Task | Related Script | Remarks |
| :--- | :--- | :--- | :--- |
| **Step 0** | Environment Check | `compiler-0...sh`,<br>`runtime-0...sh` | Verify SDK installation and NPU driver |
| **Step 1** | Model Download | `compiler-1_download_onnx.sh` | Download original trained models (ONNX) |
| **Step 2** | Data Preparation | `compiler-2_setup_calibration_dataset.sh` | Prepare reference dataset for quantization optimization |
| **Step 3** | Path Configuration | `compiler-3_setup_output_path.sh` | Configure storage path for compiled outputs (`.dxnn`) |
| **Step 4** | NPU Compilation | `compiler-4_model_compile.sh` | Generate hardware-optimized `.dxnn` binaries |
| **Step 5** | NPU Inference | `runtime-3_run_example_using_dxrt.sh` | Execute the model on NPU and verify results |

**Directory Structure**  
Upon completion, the getting-started/ folder will be organized with symbolic links to actual data sources.  

```Plaintext 
getting-started/
├── calibration_dataset             # dx-compiler/dx_com/calibration_dataset
├── dxnn                            # dx-compiler/dx_com/output
├── forked_dx_app_example        	# Example execution target (forked)
│   ├── bin
│   │   ├── efficientnet_async
│   │   └── yolov5_async
│   │   └── yolov5face_async
│   └── sample
│       └── ILSVRC2012
└── sample_models                	# dx-compiler/dx_com/sample_models
    ├── json
    └── onnx
```

**Preparation**  
Before you begin, ensure your environment meets the following criteria:  

- **Prerequisite**: The DX-AllSuite installation **must** be fully completed.  
- **Environment Selection**  
    : **Local**: For users who have installed drivers and the SDK directly on the Host OS.  
    : **Docker**: For users working inside the container provided by the DEEPX Docker image.  
      Tip: All scripts **must** be executed inside the container (via docker exec).  

---

## DX-Compiler: AI Model Compilation Scripts Guide (Steps 0–4)

This section details the process of converting standard AI models into NPU-proprietary binaries (`.dxnn`) through a sequential workflow from Step 0 to Step 4.  

### A. Execution Order

The scripts **must** be executed in the following order within the getting-started directory.  
```Bash
./getting-started/compiler-0_install_dx-compiler.sh         # Environment Setup
./getting-started/compiler-1_download_onnx.sh               # Model Acquisition
./getting-started/compiler-2_setup_calibration_dataset.sh   # Data Preparation
./getting-started/compiler-3_setup_output_path.sh           # Path Configuration
./getting-started/compiler-4_model_compile.sh               # Final Compilation
```

### B. Common Principles & Tips

All compiler scripts follow a "smart delegation" design to keep your workflow consistent. 

- **Logic Delegation**: Actual processing is offloaded to the original scripts located in `dx-compiler/example/`.  
- **Auto-Environment Detection**: The scripts automatically identify whether they are running in a **Host** or **Docker** environment to configure paths and symbolic links.  
- **Final Asset**: Every step is a milestone toward producing the `.dxnn` file, which is the essential asset of your NPU inference.  

### C. Detailed Script Guide

**[Step 0] `compiler-0_install_dx-compiler.sh` (Package Installation)**  
Sets up the environment for the model compiler (`dxcom`).  

- **Core Function**: Installs the `dx-compiler` environment and runs a quick health check.  
- **Smart Check**: It probes for existing installations using `dxcom -v`. If it's already there, it won't waste your time with a redundant setup (unless you use the `--force` flag).  

**[Step 1] `compiler-1_download_onnx.sh` (Model Download)**  
Prepares the sample model files (`.onnx` and `.json`) for compilation.  

- **Supported Models**: `YOLOV5S-1, YOLOV5S_Face-1, MobileNetV2-1`  
- **Mapping**: Creates a symbolic link between `getting-started/sample_models` and the SDK's internal `dx-compiler/dx_com/sample_models`.  

**[Step 2] `compiler-2_setup_calibration_dataset.sh` (Calibration Data Setup)**  
Acquires a reference dataset to maintain accuracy during the model quantization process.  

- **Purpose**: Downloads and extracts representative image datasets. These are used to calibrate the model so that accuracy remains high even after optimization.  
- **Result**: Links your local `getting-started/calibration_dataset` to the SDK core.  

**[Step 3] `compiler-3_setup_output_path.sh` (Path Configuration)**  

| Environment | Physical Path (Actual Storage) | Logical Path (Access Point) |
| :--- | :--- | :--- |
| **Docker** | `${DOCKER_VOLUME_PATH}/dxnn` | `getting-started/dxnn/` |
| **Local** | `${DX_AS_PATH}/workspace/dxnn` | `getting-started/dxnn/` |

!!! note "Tip"  
    This "**Logical Path**" abstraction allows subsequent runtime scripts to look for models in the same place (`dxnn/`) regardless of whether you're running on a server or a local PC.  

**[Step 4] `compiler-4_model_compile.sh` (Execute Model Compilation)**  
The final stage where the prepared model and data are combined to generate the NPU-optimized binary.  

- **Core Action**: Invokes the `dxcom` engine to perform the following fusion:  
   : **ONNX** (The Structure) + **JSON** (The Config) + **Calibration** (The Precision) = **.dxnn** (The Optimized Binary)  
- **Output**: Your shiny new `.dxnn` files are stored in `dx-compiler/dx_com/output/` and are immediately accessible via the `getting-started/dxnn` link.  

---

## DX-Runtime: Application Execution (Application Execution Scripts Guide) (Step 0, 5)

This chapter focuses on Step 0 (Environment Setup) and Step 5 (Inference), where you deploy and run your optimized models on the actual DEEPX NPU hardware.  

### A. Full Execution Order

To ensure stable operation, execute these scripts sequentially from within the `getting-started/` directory.  
```Bash
./getting-started/runtime-0_install_dx-runtime.sh # Set up environment
./getting-started/runtime-1_setup_input_path.sh # Connect model
./getting-started/runtime-2_setup_assets.sh # Prepare resources
./getting-started/runtime-3_run_example_using_dxrt.sh # Run example
```

### B. Common Principles & Tips

All runtime scripts are engineered with the following logic to ensure a seamless deployment experience.  

- **Intelligent Diagnosis & Recovery**: Scripts automatically verify the NPU driver and installation integrity using `sanity_check.sh`. If an environment is corrupted, use `-f` or `--force` to re-initialize.  
- **Environment-Adaptive Logic**: Paths are dynamically assigned based on your Host or Docker environment. In headless (TTY) environments, the scripts automatically apply the `--no-display` flag to prevent GUI errors.  
- **Resource Delegation**: The scripts trigger `dx_app/setup.sh` to automatically populate the `forked_dx_app_example` folder with required binaries and sample data.  
- **Visual Verification**:  
   : **CLI Environment**: Includes a `fim` (fbi improved) installation routine to view result images directly in the terminal.  
   : **Docker Environment**: Since GUI output is limited, results can be retrieved using `docker cp <container_id>:/path/to/result ./local_path`.  

!!! caution "Prerequisite"  
    You **must** have successfully generated `.dxnn` files in the previous **Compiler** steps. The runtime engine cannot operate without these hardware-optimized binaries.  

### C. Detailed Script Guide

**[Step 0] `runtime-0_install_dx-runtime.sh` (Package Installation)**  
Builds the core software stack for DEEPX NPU control.  

- **Key Functions**: Installs runtime libraries and verifies driver operation.  
- **Optimization**: If `sanity_check.sh` detects that drivers are already correctly loaded, it skips redundant installation steps.  
- **Time-Saving Option**: Use `--exclude-fw` to install the software stack while skipping firmware updates (useful if your firmware is already up to date).  

**[Preparation for Step 5] `runtime-1_setup_input_path.sh` (Model Path Synchronization)**  
Synchronizes paths so that the runtime engine can load the `.dxnn` models generated during the compilation phase.  

| Environment | Physical Path (Actual Storage) | Logical Path (Access Point) |
| :--- | :--- | :--- |
| **Docker** | `${DOCKER_VOLUME_PATH}/dxnn` | `getting-started/dxnn/` |
| **Local** | `${DX_AS_PATH}/workspace/dxnn` | `getting-started/dxnn/` |

**[Preparation for Step 5] `runtime-2_setup_assets.sh` (Resource Preparation)**  
Prepare the dependency files and sample data required to run the inference example.  

- **Action**: Sequentially calls the `setup.sh` scripts within the `dx_app` and `dx_stream` directories.  
- **Note**: This script manages resources within their respective modules; it does not create redundant copies in the `forked_dx_app_example` folder.  

**[Step 5] `runtime-3_run_example_using_dxrt.sh` (Execute Example and Check Results)**  
This script loads your models onto the NPU, measures real-world performance, and generates visualized outputs across three core tasks.  

| Model | Input Data | Task | Iterations |
| :--- | :--- | :--- | :--- |
| **YOLOV5S_Face-1** | `face_sample.jpg` | [1] Face Detection | 30 |
| **YOLOV5S-1** | `1.jpg` | [2] Object Detection | 300 |
| **MobileNetV2-1** | `1.jpeg` | [3] Image Classification | 300 |

- **Result Report**: After execution is complete, the script outputs average **FPS** (Frames Per Second) and **Latency** (ms) to the terminal.  

!!! caution "Essential Check"  
    This pipeline assumes all three sample models from Step 1 were successfully compiled in Step 4.  
    - If a model is missing, you will encounter a "**File Not Found**" error during inference.  
    -	We strongly recommend compiling **all 3 models** before running this runtime script to verify the entire end-to-end process.  

Copyright © DEEPX. All rights reserved.

---
