# Local Install Test Suite

A pytest-based test suite for automated local installation verification inside Docker containers.

## Overview

This test suite validates local installation procedures for:

- **dx-runtime**: Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12, Debian 13 (6 tests)
- **dx-modelzoo**: Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12, Debian 13 (6 tests)
- **dx-compiler**: Ubuntu 24.04, 22.04, 20.04 (3 tests)

Each component undergoes three stages:
1. **Build** - Docker image creation
2. **Run** - Container startup and mounting
3. **Install** - Component installation inside container

**Total: 15 build tests + 15 run tests + 15 install tests + 3 sanity tests = 48 tests**

## Quick Start

### 1. Run Sanity Tests Only (Quick Validation)

```bash
cd tests
./test.sh local_install -k "sanity"
```

### 2. Run Local Installation Tests

```bash
./test.sh local_install
```

### 3. Test Specific Targets

```bash
./test.sh local_install -k "runtime"      # dx-runtime only
./test.sh local_install -k "modelzoo"     # dx-modelzoo only
./test.sh local_install -k "compiler"     # dx-compiler only
```

### 4. Test Specific Stages

```bash
./test.sh local_install -k "build"        # Docker build only
./test.sh local_install -k "run"          # Container run only
./test.sh local_install -k "install"      # Installation only
```

### 5. Special Options

```bash
# Exclude firmware during dx-runtime install
./test.sh --exclude-fw local_install -k "runtime"
```

## Direct pytest Usage

You can also activate the virtual environment directly and use pytest:

```bash
# Activate virtual environment
source ../venv/bin/activate

# Run pytest directly
pytest -v
pytest -k "runtime and ubuntu"
pytest --collect-only
pytest -v --tb=short

# Deactivate when done
deactivate
```

## Test Filtering

### Filter by Keyword (-k option)

```bash
# Specific target
pytest -k "runtime"
pytest -k "modelzoo"
pytest -k "compiler"

# Specific OS
pytest -k "ubuntu"
pytest -k "debian"

# Specific version
pytest -k "24.04"
pytest -k "22.04"

# Specific stage
pytest -k "build"
pytest -k "run"
pytest -k "install"

# Combination (AND)
pytest -k "runtime and ubuntu"
pytest -k "runtime and 24.04"
pytest -k "compiler and build"

# Combination (OR)
pytest -k "runtime or compiler"

# Exclusion (NOT)
pytest -k "not debian"
pytest -k "ubuntu and not 18.04"
```

### Filter by Marker (-m option)

```bash
# Sanity tests only
pytest -m sanity

# Exclude sanity tests
pytest -m "not sanity"
```

## Report Generation

### HTML Report

```bash
# Using test.sh (recommended)
./test.sh local_install --report

# Direct specification
pytest --html=report.html --self-contained-html
```

**Generated at:** `tests/reports/test_report_<timestamp>.html`

### JSON Report

```bash
# Using test.sh (recommended)
./test.sh local_install --json

# Direct specification
pytest --json-report --json-report-file=report.json
```

**Generated at:** `tests/reports/test_report_<timestamp>.json`

## Test Structure

### Sanity Tests (3 tests)

Pre-install environment validation:

- `test_docker_command_available` - Check docker command
- `test_docker_compose_command_available` - Check docker compose
- `test_project_structure` - Verify project structure

### Build Tests (15 tests)

Docker image builds for clean OS environments:

**dx-runtime (6 tests)**
- `test_docker_build[dx-runtime-ubuntu-24.04]`
- `test_docker_build[dx-runtime-ubuntu-22.04]`
- `test_docker_build[dx-runtime-ubuntu-20.04]`
- `test_docker_build[dx-runtime-ubuntu-18.04]`
- `test_docker_build[dx-runtime-debian-12]`
- `test_docker_build[dx-runtime-debian-13]`

**dx-modelzoo (6 tests)**
- `test_docker_build[dx-modelzoo-ubuntu-24.04]`
- `test_docker_build[dx-modelzoo-ubuntu-22.04]`
- `test_docker_build[dx-modelzoo-ubuntu-20.04]`
- `test_docker_build[dx-modelzoo-ubuntu-18.04]`
- `test_docker_build[dx-modelzoo-debian-12]`
- `test_docker_build[dx-modelzoo-debian-13]`

**dx-compiler (3 tests)**
- `test_docker_build[dx-compiler-ubuntu-24.04]`
- `test_docker_build[dx-compiler-ubuntu-22.04]`
- `test_docker_build[dx-compiler-ubuntu-20.04]`

### Run Tests (15 tests)

Container startup and workspace mounting:

**dx-runtime (6 tests)**
- `test_docker_run[dx-runtime-ubuntu-24.04]`
- `test_docker_run[dx-runtime-ubuntu-22.04]`
- `test_docker_run[dx-runtime-ubuntu-20.04]`
- `test_docker_run[dx-runtime-ubuntu-18.04]`
- `test_docker_run[dx-runtime-debian-12]`
- `test_docker_run[dx-runtime-debian-13]`

**dx-modelzoo (6 tests)**
- `test_docker_run[dx-modelzoo-ubuntu-24.04]`
- `test_docker_run[dx-modelzoo-ubuntu-22.04]`
- `test_docker_run[dx-modelzoo-ubuntu-20.04]`
- `test_docker_run[dx-modelzoo-ubuntu-18.04]`
- `test_docker_run[dx-modelzoo-debian-12]`
- `test_docker_run[dx-modelzoo-debian-13]`

**dx-compiler (3 tests)**
- `test_docker_run[dx-compiler-ubuntu-24.04]`
- `test_docker_run[dx-compiler-ubuntu-22.04]`
- `test_docker_run[dx-compiler-ubuntu-20.04]`

### Install Tests (15 tests)

Component installation inside containers:

**dx-runtime (6 tests)**
- `test_install_component[dx-runtime-ubuntu-24.04]`
- `test_install_component[dx-runtime-ubuntu-22.04]`
- `test_install_component[dx-runtime-ubuntu-20.04]`
- `test_install_component[dx-runtime-ubuntu-18.04]`
- `test_install_component[dx-runtime-debian-12]`
- `test_install_component[dx-runtime-debian-13]`

**dx-modelzoo (6 tests)**
- `test_install_component[dx-modelzoo-ubuntu-24.04]`
- `test_install_component[dx-modelzoo-ubuntu-22.04]`
- `test_install_component[dx-modelzoo-ubuntu-20.04]`
- `test_install_component[dx-modelzoo-ubuntu-18.04]`
- `test_install_component[dx-modelzoo-debian-12]`
- `test_install_component[dx-modelzoo-debian-13]`

**dx-compiler (3 tests)**
- `test_install_component[dx-compiler-ubuntu-24.04]`
- `test_install_component[dx-compiler-ubuntu-22.04]`
- `test_install_component[dx-compiler-ubuntu-20.04]`

## Special Features

### dx-runtime Installation

For dx-runtime tests, the installation process includes:
1. Install dx_rt_npu_linux_driver on host system
2. Install dx_rt on host system for host dxrtd service
3. Install remaining components inside container (with `--exclude-driver`)

### Firmware Exclusion

Use `--exclude-fw` flag to skip firmware installation during dx-runtime tests:

```bash
./test.sh --exclude-fw local_install -k "runtime"
```

This sets `DX_EXCLUDE_FW=1` environment variable.

## Expected Execution Time

- **Sanity tests:** ~5 seconds
- **Build tests:** ~10-15 minutes per test (first build) / ~5-10 minutes (with cache)
- **Run tests:** ~10-30 seconds per test
- **Install tests:** ~5-30 minutes per test (depending on component)
- **Full test suite:** ~8-12 hours (without parallel execution)

## Container Management

Containers are created with the following naming pattern:
```
dx-local-install-test-{os_type}-{version}
```

Examples:
- `dx-local-install-test-local-install-ubuntu-24.04`
- `dx-local-install-test-local-install-ubuntu-22.04`
- `dx-local-install-test-local-install-debian-12`

Containers persist across test runs for efficiency. To clean up:

```bash
# Stop and remove all test containers
docker ps -a | grep "dx-local-install-test" | awk '{print $1}' | xargs docker rm -f

# Remove all test images
docker images | grep "dx-local-install-test" | awk '{print $3}' | xargs docker rmi -f
```

## License

This test suite is part of the dx-all-suite project.
