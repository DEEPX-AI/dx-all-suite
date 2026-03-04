# Getting Started Test Suite

A pytest-based test suite for automated validation of the getting-started workflow.

## Overview

This test suite validates the complete end-to-end getting-started workflow for dx-all-suite:

### Compiler Workflow (6 tests)
1. Install dx-compiler
2. Download ONNX models
3. Setup calibration dataset
4. Setup output path
5. Compile models
6. Cleanup

### Runtime Workflow (5 tests)
1. Install dx-runtime
2. Setup input paths
3. Setup assets
4. Run inference examples
5. Cleanup

**Total: 11 tests (6 compiler + 5 runtime)**

All tests run **sequentially** to maintain proper workflow order.

## Quick Start

### 1. Run Getting-Started Tests

```bash
cd tests
./test.sh getting_started
```

### 2. Test Specific Workflows

```bash
# Compiler workflow only
./test.sh getting_started -k "compiler"

# Runtime workflow only
./test.sh getting_started -k "runtime"
```

### 3. Test Individual Steps

```bash
# Specific compiler step
./test.sh getting_started -k "test_compiler_0_install"
./test.sh getting_started -k "test_compiler_4_model_compile"

# Specific runtime step
./test.sh getting_started -k "test_runtime_0_install"
./test.sh getting_started -k "test_runtime_3_run_example"
```

### 4. Special Options

```bash
# Exclude firmware during dx-runtime install
./test.sh --exclude-fw getting_started -k "runtime"
```

## Direct pytest Usage

You can also activate the virtual environment directly and use pytest:

```bash
# Activate virtual environment
source ../venv/bin/activate

# Run pytest directly
pytest -v
pytest -k "compiler"
pytest -k "runtime"
pytest --collect-only

# Deactivate when done
deactivate
```

## Test Filtering

### Filter by Keyword (-k option)

```bash
# Workflow type
pytest -k "compiler"
pytest -k "runtime"

# Specific steps
pytest -k "install"
pytest -k "compile"
pytest -k "clean"

# Individual test
pytest -k "test_compiler_4_model_compile"
pytest -k "test_runtime_3_run_example_using_dxrt"

# Exclusion (NOT)
pytest -k "not clean"
pytest -k "compiler and not clean"
```

### Filter by Marker (-m option)

```bash
# Compiler tests only
pytest -m compiler

# Runtime tests only
pytest -m runtime
```

## Report Generation

### HTML Report

```bash
# Using test.sh (recommended)
./test.sh getting_started --report

# Direct specification
pytest --html=report.html --self-contained-html
```

**Generated at:** `tests/reports/test_report_<timestamp>.html`

### JSON Report

```bash
# Using test.sh (recommended)
./test.sh getting_started --json

# Direct specification
pytest --json-report --json-report-file=report.json
```

**Generated at:** `tests/reports/test_report_<timestamp>.json`

## Test Structure

### Compiler Tests (6 tests)

**Sequential workflow tests:**

1. `test_compiler_0_install_dx_compiler`
   - Runs: `compiler-0_install_dx-compiler.sh`
   - Purpose: Install dx-compiler environment

2. `test_compiler_1_download_onnx`
   - Runs: `compiler-1_download_onnx.sh`
   - Purpose: Download sample ONNX models

3. `test_compiler_2_setup_calibration_dataset`
   - Runs: `compiler-2_setup_calibration_dataset.sh`
   - Purpose: Prepare calibration dataset for quantization

4. `test_compiler_3_setup_output_path`
   - Runs: `compiler-3_setup_output_path.sh`
   - Purpose: Setup output directory for compiled models

5. `test_compiler_4_model_compile`
   - Runs: `compiler-4_model_compile.sh`
   - Purpose: Compile ONNX models to DXNN format

6. `test_compiler_clean`
   - Runs: `compiler-clean.sh`
   - Purpose: Cleanup compiler artifacts and outputs

### Runtime Tests (5 tests)

**Sequential workflow tests:**

1. `test_runtime_0_install_dx_runtime`
   - Runs: `runtime-0_install_dx-runtime.sh`
   - Purpose: Install dx-runtime environment
   - Supports: `--exclude-fw` flag via `DX_EXCLUDE_FW=1`

2. `test_runtime_1_setup_input_path`
   - Runs: `runtime-1_setup_input_path.sh`
   - Purpose: Setup input data paths for inference

3. `test_runtime_2_setup_assets`
   - Runs: `runtime-2_setup_assets.sh`
   - Purpose: Prepare model assets and resources

4. `test_runtime_3_run_example_using_dxrt`
   - Runs: `runtime-3_run_example_using_dxrt.sh`
   - Purpose: Execute inference example using dx-runtime

5. `test_runtime_clean`
   - Runs: `runtime-clean.sh`
   - Purpose: Cleanup runtime artifacts and outputs

## Special Features

### Firmware Exclusion

For runtime tests, you can exclude firmware installation using the `--exclude-fw` flag:

```bash
./test.sh --exclude-fw getting_started -k "runtime"
```

This sets `DX_EXCLUDE_FW=1` environment variable, which is passed to the runtime installation script.

### Sequential Execution

Unlike other test suites, getting-started tests are designed to run sequentially:
- Tests within each workflow (compiler/runtime) must execute in order
- Each test depends on the successful completion of previous steps
- Use pytest's default behavior (no parallel execution)

## Expected Execution Time

- **Single compiler test:** ~30 seconds - 10 minutes (depending on step)
- **Full compiler workflow:** ~30-60 minutes
- **Single runtime test:** ~30 seconds - 5 minutes (depending on step)
- **Full runtime workflow:** ~10-30 minutes
- **Full test suite:** ~40-90 minutes

## Workflow Scripts

All workflow scripts are located in the `getting-started/` directory:

### Compiler Scripts
```
compiler-0_install_dx-compiler.sh
compiler-1_download_onnx.sh
compiler-2_setup_calibration_dataset.sh
compiler-3_setup_output_path.sh
compiler-4_model_compile.sh
compiler-clean.sh
```

### Runtime Scripts
```
runtime-0_install_dx-runtime.sh
runtime-1_setup_input_path.sh
runtime-2_setup_assets.sh
runtime-3_run_example_using_dxrt.sh
runtime-clean.sh
```

## Troubleshooting

### Test Failures

If a test fails:
1. Check the script output in the pytest report
2. Manually run the failing script to debug:
   ```bash
   cd getting-started
   bash compiler-4_model_compile.sh
   ```
3. Review the script logs and error messages
4. Run cleanup before retrying:
   ```bash
   bash compiler-clean.sh
   bash runtime-clean.sh
   ```

### Cleanup

To manually clean up between test runs:

```bash
cd getting-started

# Clean compiler artifacts
bash compiler-clean.sh

# Clean runtime artifacts
bash runtime-clean.sh
```

## Dependencies

### Compiler Workflow Requirements
- dx-compiler installed (via `compiler-0_install_dx-compiler.sh`)
- Internet connection (for ONNX model downloads)
- Sufficient disk space for models and outputs

### Runtime Workflow Requirements
- dx-runtime installed (via `runtime-0_install_dx-runtime.sh`)
- NPU hardware (for actual inference)
- Compiled models from compiler workflow

## License

This test suite is part of the dx-all-suite project.
