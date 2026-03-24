# DX-ALL-SUITE Test Suite

## 📋 Overview

A comprehensive pytest-based test suite for automated verification of the dx-all-suite project, covering three major test categories:

**Purpose:** End-to-end validation of Docker builds, local installations, and getting-started workflows across multiple components and OS platforms.

## ✅ Test Suite Categories

This repository includes five pytest suites for CI/CD and local validation:

### 1. **test_docker_install** — Docker Image Build Validation
Validates Docker image builds using `docker_build.sh` for all supported components and OS versions.

**What it tests:**
- Builds complete Docker images for dx-compiler, dx-modelzoo, and dx-runtime
- Verifies build success across Ubuntu (24.04, 22.04, 20.04, 18.04) and Debian (12, 13)
- Uses the project's official docker build script (`docker_build.sh`)

**Total tests:** 19 (4 sanity + 15 build tests)

### 2. **test_local_install** — Local Installation Validation
Tests local installation procedures inside clean Docker containers to verify install scripts work correctly.

**What it tests:**
- Builds base OS container images (Ubuntu/Debian)
- Starts containers and mounts workspace
- Runs component install scripts (`install.sh`) inside containers
- For dx-runtime: also installs drivers and runtime on the host
- Verifies installations complete successfully without errors

**Total tests:** 48 (3 sanity + 15 build + 15 run + 15 install tests)

### 3. **test_getting_started** — End-to-End Workflow Validation
Validates the complete getting-started user workflow from compilation to execution.

**What it tests:**
- **Compiler workflow:** Install dx-compiler → Download ONNX models → Setup calibration data → Compile models → Cleanup
- **Runtime workflow:** Install dx-runtime → Setup input paths → Prepare assets → Run inference examples → Cleanup
- Sequential execution ensuring proper workflow order

**Total tests:** 11 (6 compiler + 5 runtime tests)

### 4. **test_agentic_scenarios** — Agentic Development Infrastructure Validation
Validates the agentic development infrastructure across all 5 project levels (suite, compiler, runtime, dx_app, dx_stream).

**What it tests:**
- Guide document structure: existence, headings, scenario numbering, EN/KO synchronization
- Routing consistency: CLAUDE.md, AGENTS.md, copilot-instructions.md, opencode.json, .cursorrules
- Scenario references: agent/skill references in guides match actual infrastructure
- Cross-project scenarios: handoff chains, validation scripts, output isolation

**Total tests:** 199 (186 passed, 13 skipped)

### 5. **test_agentic_e2e_scenarios** — Agentic End-to-End Copilot CLI Scenario Tests
Runs actual Copilot CLI invocations for representative scenarios from each project level, then statically verifies the generated output files.

**Two modes:**
- **autopilot** (default): Fully autonomous with `--no-ask-user`. CI/CD optimized. Runs via pytest.
- **manual**: Interactive shell-based mode (no pytest). User interacts with copilot TUI directly, then shell validates output.

**Output isolation:** Prompts do NOT specify an output directory. Each sub-project's `copilot-instructions.md` enforces Output Isolation, automatically writing generated files to `dx-agentic-dev/<session_id>/`. The test framework auto-detects new session directories by comparing pre/post snapshots of each scenario's search paths.

**What it tests:**
- **dx_app Scenario #1:** Build a yolo26n person detection app (IFactory pattern, config.json, runner)
- **dx_stream Scenario #1:** Build a detection pipeline with tracking (GStreamer elements, RTSP, tracker)
- **dx-compiler Scenario #2:** Generate compilation config for ONNX to DXNN (config.json structure)
- **dx-runtime Scenario #2:** Build standalone detection app via routing (routing verification)
- **dx-all-suite Scenario #2:** Cross-project compile + app generation (both compiler and app artifacts)

**Verification approach:** Static analysis only (file existence, Python syntax via `ast.parse`, JSON structure, required patterns). No actual HW inference.

**Total tests:** 42 (pytest: autopilot mode, shell: manual mode)
**Markers (pytest only):**
- `pytest.mark.agentic_e2e_autopilot` — fully autonomous (CI/CD)

## 🎯 Test Scope

### Build Targets (3 Components)

- **dx-compiler**: DeepX Neural Network Compiler
- **dx-modelzoo**: Model repository and training tools
- **dx-runtime**: Runtime environment with NPU driver support

### OS Configurations

#### Docker Install (15 combinations)

| Target | Ubuntu 24.04 | Ubuntu 22.04 | Ubuntu 20.04 | Ubuntu 18.04 | Debian 12 | Debian 13 | Total |
|--------|--------------|--------------|--------------|--------------|-----------|-----------|-------|
| dx-compiler | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | 3 |
| dx-modelzoo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 |
| dx-runtime | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 |
| **Total** | **3** | **3** | **3** | **2** | **2** | **2** | **15** |

**Note:** dx-compiler supports Ubuntu only (no Debian)

#### Local Install (15 combinations)

| Target | Ubuntu 24.04 | Ubuntu 22.04 | Ubuntu 20.04 | Ubuntu 18.04 | Debian 12 | Debian 13 | Total |
|--------|--------------|--------------|--------------|--------------|-----------|-----------|-------|
| dx-compiler | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | 3 |
| dx-modelzoo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 |
| dx-runtime | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 |
| **Total** | **3** | **3** | **3** | **2** | **2** | **2** | **15** |

**Note:** dx-compiler supports Ubuntu 20.04+ only (no 18.04, no Debian)

### Test Composition Summary

| Test Suite | Sanity | Build | Run | Install | Workflow | Agentic Infra | E2E Scenarios | Total |
|------------|--------|-------|-----|---------|----------|---------------|---------------|-------|
| **docker_install** | 4 | 15 | - | - | - | - | - | **19** |
| **local_install** | 3 | 15 | 15 | 15 | - | - | - | **48** |
| **getting_started** | - | - | - | - | 11 | - | - | **11** |
| **agentic** | - | - | - | - | - | 199 | - | **199** |
| **agentic_e2e** | - | - | - | - | - | - | 42 | **42** |
| **Grand Total** | **7** | **30** | **15** | **15** | **11** | **199** | **42** | **319+** |

## 📁 File Structure

```
tests/
├── 🐍 test_docker_install/          # Docker build validation tests
│   ├── test_docker_install.py       # 19 tests (4 sanity + 15 builds)
│   └── README.md                    # Docker install test documentation
├── 🐍 test_local_install/           # Local installation tests
│   ├── test_local_install.py        # 48 tests (3 sanity + 15 build + 15 run + 15 install)
│   └── README.md                    # Local install test documentation
├── 🐍 test_getting-started/         # Getting-started workflow tests
│   ├── test_getting_started.py      # 11 tests (6 compiler + 5 runtime)
│   └── README.md                    # Getting-started test documentation
├── 🐍 test_agentic_scenarios/       # Agentic infrastructure validation
│   ├── conftest.py                  # ProjectInfra dataclass, path constants, helpers
│   ├── test_guide_structure.py      # Guide existence, headings, numbering, EN/KO sync
│   ├── test_routing_consistency.py  # CLAUDE.md, AGENTS.md, copilot-instructions consistency
│   ├── test_scenario_references.py  # Agent/skill references match infrastructure
│   └── test_cross_project_scenarios.py  # Handoff chains, validation scripts
├── 🐍 test_agentic_e2e_scenarios/   # Agentic end-to-end Copilot CLI scenario tests
│   ├── conftest.py                  # CopilotRunnerAutopilot, ScenarioResult, session auto-detection, verification helpers
│   ├── test_dx_app_agentic_e2e.py   # dx_app Scenario #1 (10 tests)
│   ├── test_dx_stream_agentic_e2e.py # dx_stream Scenario #1 (8 tests)
│   ├── test_compiler_agentic_e2e.py # dx-compiler Scenario #2 (7 tests)
│   ├── test_runtime_agentic_e2e.py  # dx-runtime Scenario #2 (6 tests)
│   └── test_suite_agentic_e2e.py    # dx-all-suite Scenario #2 (7 tests)
├── 🔧 conftest.py                   # Shared pytest fixtures and utilities
├── ⚡ test.sh                       # Unified test command wrapper (main entry point)
├── 🔍 parse_copilot_session.py        # Copilot CLI events.jsonl → Markdown report parser
├── 🐳 docker/                       # Docker compose files for test containers
│   ├── docker-compose.local.install.test.yml
│   └── Dockerfile.local.install.test
├── 📖 pytest.ini                    # Pytest configuration
├── 📦 requirements.txt              # Python dependencies
├── 📝 README.md                     # This comprehensive guide
├── 🔄 CI_CD_EXAMPLES.md             # CI/CD integration examples
├── 📖 REFERENCE.sh                  # Quick command reference
├── 🐍 venv/                         # Python virtual environment (auto-created)
└── 📊 reports/                      # Test reports (auto-generated)
```

## 🚀 Quick Start

### Step 1: Sanity Check (5-10 seconds)

Quick validation that all prerequisites are met:

```bash
cd tests
./test.sh sanity
```

### Step 2: Run Specific Test Suites

```bash
# Docker installation tests (15 builds, ~6-8 hours)
./test.sh docker_install

# Local installation tests (49 tests, ~8-12 hours)
./test.sh local_install

# Getting-started workflow (11 tests, ~30-60 minutes)
./test.sh getting_started

# Agentic infrastructure validation (199 tests, ~1 second)
./test.sh agentic

# Agentic E2E Copilot CLI scenario tests (42 tests, ~3-5 minutes)
./test.sh agentic-e2e-autopilot      # Fully autonomous (CI/CD) — pytest
./test.sh agentic-e2e-manual        # Interactive (shell-based, no pytest)
```

### Step 3: Full Test Suite

```bash
./test.sh all          # All 79 tests (~12-20 hours)
```

### Step 4: Generate Reports

```bash
./test.sh --report docker_install     # HTML report
./test.sh --json getting_started      # JSON report
```

## 💡 Key Commands

### Basic Commands

```bash
./test.sh sanity           # ⚡ Quick validation (5-10 seconds)
./test.sh all              # 🔥 Full test suite (12-20 hours, 79 tests)
./test.sh list             # 📋 List all available tests
./test.sh help             # ❓ Show detailed help
```

### Test Suite Commands

```bash
./test.sh docker_install   # Docker build tests (15 tests, ~6-8 hours)
./test.sh local_install    # Local install tests (49 tests, ~8-12 hours)
./test.sh getting_started  # Getting-started workflow (11 tests, ~30-60 min)
./test.sh agentic          # Agentic infrastructure (199 tests, ~1 second)
./test.sh agentic-e2e-autopilot    # Agentic E2E fully autonomous (CI/CD)
./test.sh agentic-e2e-manual       # Agentic E2E interactive (shell-based)
```

### Advanced Options

```bash
# Report Generation
./test.sh --report <suite>           # Generate HTML report
./test.sh --html=output.html <suite> # Custom HTML filename
./test.sh --json-report <suite>      # Generate JSON report
./test.sh --json=output.json <suite> # Custom JSON filename

# Debugging & Filters
./test.sh --debug <suite>            # Enable live stdout output (DX_TEST_VERBOSE=1)
./test.sh --list <suite>             # List tests without running (--collect-only)
./test.sh -k "ubuntu and 24.04"      # Filter by keyword expression
./test.sh -m "sanity"                # Filter by marker

# Special Options
./test.sh --exclude-fw local_install           # Skip firmware in runtime install
./test.sh --internal docker_install            # Use internal network (intranet)
./test.sh --cache-clear all                    # Clear pytest cache first
```

### Keyword Filters

Use `-k` to filter tests by component, OS type, or version:

```bash
# By component
./test.sh -k "compiler" docker_install
./test.sh -k "modelzoo" local_install
./test.sh -k "runtime" all

# By OS type
./test.sh -k "ubuntu" docker_install
./test.sh -k "debian" local_install

# By OS version
./test.sh -k "24.04" docker_install
./test.sh -k "18.04" local_install

# Combined filters
./test.sh -k "runtime and ubuntu and 24.04"
./test.sh -k "(compiler or modelzoo) and debian"
```

### Marker Filters

Use `-m` to filter tests by pytest markers:

```bash
./test.sh -m "sanity"              # Only sanity checks
./test.sh -m "docker_install"      # Only docker install tests
./test.sh -m "local_install"       # Only local install tests
./test.sh -m "getting_started"     # Only getting-started tests
./test.sh -m "agentic_e2e_autopilot"       # Only fully autonomous agentic E2E
./test.sh -m "compiler"            # Compiler-related tests
./test.sh -m "runtime"             # Runtime-related tests
```

## 🎨 Usage Examples

### Example 1: Quick Validation Before Commit

```bash
# Sanity check only
./test.sh sanity
```

### Example 2: Test Specific Component on Latest OS

```bash
# Filter for runtime on Ubuntu 24.04
./test.sh -k "runtime and 24.04" docker_install
```

### Example 3: Getting-Started Workflow Validation

```bash
# Full getting-started flow with report
./test.sh --report getting_started
```

### Example 4: Local Install Tests with Debug Output

```bash
# Run local install with verbose output
./test.sh --debug local_install
```

### Example 5: Docker Build for Production Release

```bash
# All docker builds with HTML and JSON reports
./test.sh --report --json-report docker_install
```

### Example 6: Agentic E2E — Autopilot (CI/CD)

```bash
# Run all agentic E2E tests in autopilot mode (fully autonomous, --no-ask-user)
./test.sh agentic-e2e-autopilot

# Filter to compiler scenario only
./test.sh agentic-e2e-autopilot -k compiler

# With custom model and extended timeout
DX_AGENTIC_E2E_TIMEOUT=900 DX_AGENTIC_E2E_MODEL="claude-opus-4.6" \
  ./test.sh agentic-e2e-autopilot
```

### Example 7: Agentic E2E — Manual (Interactive, Shell-Based)

```bash
# Shell-based interactive mode — runs copilot TUI directly (no pytest)
# Shows scenario menu, user selects one, then interacts with copilot
./test.sh agentic-e2e-manual

# Auto-select a specific scenario via -k filter (skips menu)
./test.sh agentic-e2e-manual -k compiler
./test.sh agentic-e2e-manual -k dx_app
```

### Example 8: Internal Network Testing

```bash
# Use internal network settings (intranet)
./test.sh --internal docker_install
./test.sh --internal local_install
```

### Example 9: Specific OS Testing

```bash
# Test only Debian distributions
./test.sh -k "debian" local_install

# Test only Ubuntu 18.04 across all suites
./test.sh -k "18.04" all
```

### Example 10: List Tests Without Running

```bash
# List all tests that would run
./test.sh --list local_install

# List specific filtered tests
./test.sh --list -k "runtime and ubuntu and 24.04" local_install

# List with multiple filters
./test.sh --list --internal -m "sanity" docker_install
```

## 🤖 Agentic E2E — Copilot CLI Autonomous Execution

The agentic E2E test suite (`test_agentic_e2e_scenarios/`) runs real Copilot CLI
sessions against the dx-all-suite codebase. This section explains how autonomous
(auto-approve) execution works.

### Two Execution Modes

| Mode | Entry Point | Copilot Flags | User Interaction |
|------|-------------|---------------|------------------|
| **Autopilot** | `./test.sh agentic-e2e-autopilot` | `--yolo --no-ask-user -s` | None (fully autonomous) |
| **Manual** | `./test.sh agentic-e2e-manual` | `--yolo` | Interactive TUI |

### Copilot CLI Flags Explained

| Flag | Meaning | When Used |
|------|---------|-----------|
| `--yolo` | Alias for `--allow-all-tools --allow-all-paths --allow-all-urls` — auto-approves ALL tool calls (file writes, bash commands, web fetches) without confirmation prompts | Both modes |
| `--no-ask-user` | Disables the `ask_user` tool so the agent never blocks waiting for user input | Autopilot only |
| `-s` | Silent mode — shows only agent response, no TUI chrome | Autopilot only |
| `-p <prompt>` | Non-interactive prompt mode (agent runs and exits) | Autopilot only |
| `-i <prompt>` | Interactive prompt mode (opens TUI with initial prompt) | Manual only |
| `--share=<file>` | Saves session transcript to a file | Autopilot only |
| `--model <name>` | Selects the LLM model to use | Both modes |

### Autopilot Mode — How It Works

The `CopilotRunnerAutopilot` class in `conftest.py` constructs and executes:

```bash
copilot -p "<prompt> IMPORTANT: This is an automated test run. Do not ask
questions or present options. Proceed directly with implementation, choosing
the most appropriate approach." \
  --yolo \
  --no-ask-user \
  -s \
  --share=<session_log> \
  --model claude-sonnet-4.6
```

Key behaviors:
- **`--yolo`** auto-approves all tool calls — the agent can read/write files,
  run shell commands, and fetch URLs without human confirmation.
- **`--no-ask-user`** prevents the agent from ever asking questions — if it
  encounters an ambiguity, it must decide on its own.
- The **AUTOPILOT_DIRECTIVE** (appended to every prompt) reinforces autonomous
  behavior at the prompt level.
- The session runs with a **timeout** (default 300s, configurable via
  `DX_AGENTIC_E2E_TIMEOUT`). If the agent exceeds the timeout, the process
  is killed and the test fails.

### Manual Mode — How It Works

Manual mode opens the Copilot TUI directly:

```bash
copilot -i "<prompt>" --yolo --model claude-sonnet-4.6
```

Key behaviors:
- **`--yolo`** still auto-approves tool calls, but the user can interact
  with the agent through the TUI.
- **No `--no-ask-user`** — the agent CAN ask clarifying questions, and the
  user responds via the TUI.
- After the session, `test.sh` runs shell-based validation (file existence,
  syntax checks) on the generated artifacts.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DX_AGENTIC_E2E_MODEL` | `claude-sonnet-4.6` | LLM model for Copilot CLI |
| `DX_AGENTIC_E2E_TIMEOUT` | `300` | Timeout in seconds per scenario |
| `DX_AGENTIC_E2E_KEEP_ARTIFACTS` | `0` | Set to `1` to keep generated `dx-agentic-dev/` directories after test run |
| `DX_AGENTIC_E2E_MODE` | (set by test.sh) | `autopilot` or `manual` — set automatically by `test.sh` |

### Running with Different Models

```bash
# Claude Sonnet 4.6 (recommended)
DX_AGENTIC_E2E_MODEL="claude-sonnet-4.6" ./test.sh agentic-e2e-autopilot

# GPT-4.1 (not recommended — may fabricate APIs)
DX_AGENTIC_E2E_MODEL="gpt-4.1" DX_AGENTIC_E2E_TIMEOUT=600 \
  ./test.sh agentic-e2e-autopilot

# Claude Opus 4.6 (highest quality, slower)
DX_AGENTIC_E2E_MODEL="claude-opus-4.6" DX_AGENTIC_E2E_TIMEOUT=900 \
  ./test.sh agentic-e2e-autopilot
```

### Session Output and Artifacts

Each scenario generates artifacts in `dx-agentic-dev/<session_id>/` within
the target sub-project. The test framework auto-detects new session directories
by comparing pre/post directory snapshots.

After a test run, artifacts include:
- Generated code files (Python scripts, configs, shell scripts)
- `session.log` — command execution transcript
- Copilot session transcript (saved via `--share=<file>`)
- HTML export (if `test.sh` detects it was generated via `/share html`)

Set `DX_AGENTIC_E2E_KEEP_ARTIFACTS=1` to preserve these artifacts for debugging.
Without this flag, `test.sh` cleans up generated directories after validation.

## 📊 Expected Execution Time

| Test Suite | Test Count | Expected Time | Use Case |
|-----------|------------|---------------|----------|
| **Sanity** | 7 | ~5-10 seconds | Quick prerequisite check |
| **docker_install** | 19 | ~6-8 hours | Docker build validation |
| **local_install** | 49 | ~8-12 hours | Installation script validation |
| **getting_started** | 11 | ~30-60 minutes | End-to-end workflow |
| **agentic** | 199 | ~1 second | Agentic infrastructure validation |
| **agentic_e2e** | 42 | ~3-5 minutes | Agentic E2E Copilot CLI scenario tests |
| **Full Suite (all)** | 319 | ~12-20 hours | Complete validation |

### Per-Component Breakdown

| Component | docker_install | local_install | Total Time |
|-----------|----------------|---------------|-----------|
| dx-compiler | ~1.5 hours (3 tests) | ~2-3 hours (4 tests) | ~3.5-4.5 hours |
| dx-modelzoo | ~2.5 hours (6 tests) | ~3-4 hours (6 tests) | ~5.5-6.5 hours |
| dx-runtime | ~2.5 hours (6 tests) | ~3-5 hours (6 tests) | ~5.5-7.5 hours |

**Note:** Times may vary based on:
- Docker build cache state
- Network speed (for downloading dependencies)
- System performance (CPU, disk I/O)
- Whether using `--internal` flag (affects download sources)

## 🔍 Test Details

### Test Suite 1: docker_install (19 tests)

#### Sanity Tests (4 tests)

- ✅ `test_docker_build_script_exists` - Verify docker_build.sh exists
- ✅ `test_docker_command_available` - Check docker command
- ✅ `test_docker_compose_command_available` - Check docker compose
- ✅ `test_project_structure` - Verify project directories

#### Docker Build Tests (15 tests)

**dx-compiler (3 tests - Ubuntu only)**
- ✅ `test_docker_build[dx-compiler-ubuntu-24.04]`
- ✅ `test_docker_build[dx-compiler-ubuntu-22.04]`
- ✅ `test_docker_build[dx-compiler-ubuntu-20.04]`

**dx-modelzoo (6 tests)**
- ✅ `test_docker_build[dx-modelzoo-ubuntu-24.04]`
- ✅ `test_docker_build[dx-modelzoo-ubuntu-22.04]`
- ✅ `test_docker_build[dx-modelzoo-ubuntu-20.04]`
- ✅ `test_docker_build[dx-modelzoo-ubuntu-18.04]`
- ✅ `test_docker_build[dx-modelzoo-debian-12]`
- ✅ `test_docker_build[dx-modelzoo-debian-13]`

**dx-runtime (6 tests)**
- ✅ `test_docker_build[dx-runtime-ubuntu-24.04]`
- ✅ `test_docker_build[dx-runtime-ubuntu-22.04]`
- ✅ `test_docker_build[dx-runtime-ubuntu-20.04]`
- ✅ `test_docker_build[dx-runtime-ubuntu-18.04]`
- ✅ `test_docker_build[dx-runtime-debian-12]`
- ✅ `test_docker_build[dx-runtime-debian-13]`

---

### Test Suite 2: local_install (49 tests)

#### Sanity Tests (3 tests)

- ✅ `test_docker_command_available` - Check docker availability
- ✅ `test_docker_compose_command_available` - Check docker compose
- ✅ `test_project_structure` - Verify project structure

#### Image Build Tests (15 tests)

Validates base OS container images build successfully for local install testing.

#### Container Run Tests (15 tests)

Validates containers start successfully and are ready for installations.

#### Installation Tests (16 tests)

**dx-compiler (4 tests)**
- ✅ Ubuntu 24.04, 22.04, 20.04, 18.04

**dx-modelzoo (6 tests)**
- ✅ Ubuntu 24.04, 22.04, 20.04, 18.04
- ✅ Debian 12, 13

**dx-runtime (6 tests)**
- ✅ Ubuntu 24.04, 22.04, 20.04, 18.04
- ✅ Debian 12, 13

**Note:** dx-runtime tests also install NPU driver and runtime on the host system.

---

### Test Suite 3: getting_started (11 tests)

#### Compiler Workflow Tests (6 tests)

Sequential execution ensures proper workflow:

1. ✅ `test_compiler_0_install_dx_compiler` - Install dx-compiler
2. ✅ `test_compiler_1_download_onnx` - Download ONNX model files
3. ✅ `test_compiler_2_setup_calibration_dataset` - Prepare calibration data
4. ✅ `test_compiler_3_setup_output_path` - Create output directories
5. ✅ `test_compiler_4_model_compile` - Compile ONNX to DXNN format
6. ✅ `test_compiler_clean` - Cleanup compiler artifacts

#### Runtime Workflow Tests (5 tests)

Sequential execution ensures proper workflow:

1. ✅ `test_runtime_0_install_dx_runtime` - Install dx-runtime
2. ✅ `test_runtime_1_setup_input_path` - Prepare input paths
3. ✅ `test_runtime_2_setup_assets` - Setup model assets
4. ✅ `test_runtime_3_run_example_using_dxrt` - Execute inference examples
5. ✅ `test_runtime_clean` - Cleanup runtime artifacts

**Models tested:**
- YOLOV5S-1 (Object Detection)
- YOLOV5S_Face-1 (Face Detection)
- MobileNetV2-1 (Image Classification)

## 🛠 Technology Stack

- **Test Framework:** pytest 7.4.3+
- **Reporting:** pytest-html, pytest-json-report, pytest-timeout
- **Languages:** Python 3.8+, Bash
- **Required Tools:** Docker, Docker Compose
- **Platform:** Ubuntu/Debian Linux (tested on Ubuntu 20.04, 22.04, 24.04)

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `README.md` | This comprehensive guide (all test suites) |
| `test.sh` | Main test runner with all options |
| `parse_copilot_session.py` | Copilot CLI `events.jsonl` → Markdown report parser |
| `conftest.py` | Shared pytest fixtures and utilities |
| `pytest.ini` | ⚙️ Pytest configuration and markers |
| `README_DOCKER_BUILD_TESTS.md` | 📘 Legacy docker build guide |
| `CI_CD_EXAMPLES.md` | 🔄 CI/CD integration examples |
| `REFERENCE.sh` | 📖 Quick command reference |

## 🔧 Advanced Usage

### Direct pytest Usage

```bash
# Activate virtual environment
source ./venv/bin/activate

# Run specific test suite
pytest test_docker_install/ -v
pytest test_local_install/ -v
pytest test_getting-started/ -v

# Filter by markers
pytest -m "docker_install" -v
pytest -m "local_install and sanity" -v
pytest -m "getting_started and compiler" -v

# Filter by keywords
pytest -k "ubuntu and 24.04" -v
pytest -k "runtime" test_docker_install/ -v

# Collect tests without running
pytest --collect-only

# Stop on first failure
pytest -x

# Deactivate
deactivate
```

### Environment Variables

The test suite respects several environment variables:

```bash
# Enable internal network mode
export DX_TEST_INTERNAL=1
export USE_INTRANET="true"
export CA_FILE_NAME="intranet_CA_SSL.crt"

# Enable verbose output (live stdout streaming)
export DX_TEST_VERBOSE=1

# Enable NVIDIA GPU support (for future use)
export DX_TEST_NVIDIA_GPU=1

# Exclude firmware in runtime install
export DX_EXCLUDE_FW=1

# Clear build cache
export DX_TEST_NO_CACHE=1

# Custom volume mount path
export LOCAL_VOLUME_PATH="/path/to/dx-all-suite"

# Agentic E2E test configuration
export DX_AGENTIC_E2E_TIMEOUT=900           # Copilot CLI timeout in seconds (default: 300)
export DX_AGENTIC_E2E_MODEL="claude-opus-4.6"       # Copilot model to use (default: claude-sonnet-4.6)
export DX_AGENTIC_E2E_KEEP_ARTIFACTS=1     # Keep generated artifacts after test run

```

**Using --internal flag:**
The `--internal` flag enables internal network mode (intranet) for downloading dependencies from internal repositories. This sets:
- `DX_TEST_INTERNAL=1`
- `USE_INTRANET="true"`
- `CA_FILE_NAME="intranet_CA_SSL.crt"`

**Prerequisites for internal network:**
Before using `--internal`, you must place the SSL certificate file in the dx-all-suite root directory:

```bash
# Place the certificate in the project root
cp /path/to/your/intranet_CA_SSL.crt /path/to/dx-all-suite/intranet_CA_SSL.crt

# Verify the file exists
ls -la /path/to/dx-all-suite/intranet_CA_SSL.crt
```

The certificate file will be automatically mounted into Docker containers during builds and tests.

**Using --debug flag:**
The `--debug` flag enables verbose mode with live stdout output streaming. This sets `DX_TEST_VERBOSE=1` and allows you to see:
- Real-time command output during test execution
- Installation progress logs as they happen
- Detailed debug information for troubleshooting

Without `--debug`, output is buffered and only shown after test completion or on errors.

```bash
# Enable debug mode for live output
./test.sh --debug local_install

# Debug mode with filters
./test.sh --debug -k "runtime and ubuntu and 24.04" local_install
```

### Custom Docker Compose Configuration

Tests use docker-compose files from `tests/docker/`:
- `docker-compose.local.install.test.yml` - Base configuration
- `docker-compose.nvidia_gpu.yml` - NVIDIA GPU support (optional)
- `docker-compose.internal.yml` - Internal network settings (optional)
pytest -v                              # Run all tests
pytest -k "runtime and ubuntu"         # Conditional filter
pytest -m sanity                       # Marker filter
pytest --collect-only                  # List tests only
pytest -x                              # Stop on first failure
pytest -v -s                           # Verbose output

# Deactivate
deactivate
```

### Custom Filtering

```bash
# AND condition
./run_docker_build_tests.sh -k "runtime and ubuntu and 24.04"

# OR condition
./run_docker_build_tests.sh -k "runtime or compiler"

# NOT condition
./run_docker_build_tests.sh -k "not debian"

# Complex condition
./run_docker_build_tests.sh -k "(runtime or modelzoo) and ubuntu and not 18.04"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. pytest Not Found

```bash
rm -rf ./venv
./tests.sh all --collect-only
```

#### 2. Docker Permission Error

```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

#### 3. Build Timeout

Adjust timeout in `test_docker_build.py`, `test_local_install.py`, or `test_getting_started.py`:

```python
TEST_TIMEOUT = 3600  # Increase to 60 minutes
```

#### 4. Virtual Environment Issues

```bash
rm -rf ./venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Sudo Password Prompts During Tests

If tests fail or hang due to sudo password prompts, you can configure passwordless sudo for specific commands or the current user.

**Option 1: Passwordless sudo for current user (recommended for test environments)**

```bash
# Edit sudoers file safely
sudo visudo

# Add this line at the end (replace 'username' with your actual username)
username ALL=(ALL) NOPASSWD: ALL

# Or to allow passwordless sudo only for specific commands used by tests:
username ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/apt-get, /usr/bin/docker, /usr/bin/systemctl
```

**Option 2: Using sudoers.d directory (cleaner approach)**

```bash
# Create a new sudoers file for your user
sudo visudo -f /etc/sudoers.d/username

# Add this content (replace 'username' with your actual username):
username ALL=(ALL) NOPASSWD: ALL

# Or for specific commands only:
username ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/apt-get, /usr/bin/docker, /usr/bin/systemctl

# Set proper permissions
sudo chmod 0440 /etc/sudoers.d/username
```

**Verify configuration:**

```bash
# Test sudo without password
sudo -n true && echo "Passwordless sudo is working" || echo "Still requires password"
```

**Security Note:** For production environments, limit passwordless sudo to only necessary commands instead of `ALL`.

## 🔄 CI/CD Integration

This test suite is compatible with:

- ✅ **GitHub Actions**
- ✅ **GitLab CI**
- ✅ **Jenkins**
- ✅ **Any pytest-compatible CI/CD platform**

See [CI_CD_EXAMPLES.md](CI_CD_EXAMPLES.md) for detailed examples.

### Recommended CI/CD Strategy

**Pull Request (Fast Feedback):**
```bash
./test.sh sanity                      # Quick validation (~10 sec)
./test.sh agentic                     # Agentic infrastructure (~1 sec)
./test.sh -k "24.04" docker_install  # Latest OS only (~2 hours)
```

**Main/Develop Branch (Comprehensive):**
```bash
./test.sh --report docker_install     # Full docker builds
./test.sh --report local_install      # Full local installs
./test.sh --report getting_started    # End-to-end workflow
./test.sh agentic-e2e-autopilot            # Agentic E2E Copilot CLI scenarios
```

**Release (Full Validation):**
```bash
./test.sh --report --json-report all  # Complete suite (~12-20 hours)
# Archive HTML and JSON reports as artifacts
```

## 📈 Test Coverage

### Component Coverage

| Component | docker_install | local_install | getting_started | Total |
|-----------|----------------|---------------|-----------------|-------|
| dx-compiler | ✅ (3 OS) | ✅ (4 OS) | ✅ (workflow) | 100% |
| dx-modelzoo | ✅ (6 OS) | ✅ (6 OS) | ❌ | 100% |
| dx-runtime | ✅ (6 OS) | ✅ (6 OS) | ✅ (workflow) | 100% |

### OS Coverage

| OS Version | docker_install | local_install | Support |
|------------|----------------|---------------|---------|
| Ubuntu 24.04 | ✅ (3 comp) | ✅ (3 comp) | Full |
| Ubuntu 22.04 | ✅ (3 comp) | ✅ (3 comp) | Full |
| Ubuntu 20.04 | ✅ (3 comp) | ✅ (3 comp) | Full |
| Ubuntu 18.04 | ✅ (2 comp) | ✅ (3 comp) | Full |
| Debian 12 | ✅ (2 comp) | ✅ (2 comp) | Partial |
| Debian 13 | ✅ (2 comp) | ✅ (2 comp) | Partial |

## 🎯 Project Goals

- ✅ **Automation:** Eliminate manual validation across all combinations
- ✅ **Consistency:** Identical execution in CI and local environments
- ✅ **Reliability:** Early detection of installation and build failures
- ✅ **Traceability:** Comprehensive HTML/JSON reports for debugging
- ✅ **Efficiency:** Intelligent caching and filtering capabilities
- ✅ **Documentation:** Clear usage and troubleshooting guides

## 🤝 Contribution Guide

### Adding New Tests

1. **Add new OS version:**
   ```python
   # In test_docker_install/test_docker_install.py or test_local_install/test_local_install.py
   ("dx-runtime", "ubuntu", "26.04"),  # New OS version
   ```

2. **Verify changes:**
   ```bash
   ./test.sh list                    # Check test appears
   ./test.sh sanity                  # Verify no regressions
   ./test.sh -k "26.04" all          # Test new addition
   ```

3. **Update documentation:**
   - Update this `README.md` with new OS/component info
   - Update OS configuration tables and test counts
   - Update expected execution times

## 📞 Support & Resources

- 📝 **Comprehensive Guide:** `README.md` (this file)
- ⚡ **Quick Start:** `./test.sh help`
- 🔄 **CI/CD Examples:** [CI_CD_EXAMPLES.md](CI_CD_EXAMPLES.md)
- 📋 **Command Reference:** [REFERENCE.sh](REFERENCE.sh)

---

**Last Updated:**
2026-04-09
**Total Tests:**
319 (docker_install: 19 | local_install: 48 | getting_started: 11 | agentic: 199 | agentic_e2e: 42)
**Supported OS:**
Ubuntu 24.04, 22.04, 20.04, 18.04 | Debian 12, 13
**Components:**
dx-compiler, dx-modelzoo, dx-runtime
