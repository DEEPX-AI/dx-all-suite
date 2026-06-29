# Docker Build Test Suite

A pytest-based test suite for automated Docker image build verification.

## Overview

This test suite validates the following Docker image builds:

- **dx-runtime**: Ubuntu 26.04, 24.04, 22.04, 20.04, Debian 12, Debian 13 (6 tests)
- **dx-modelzoo**: Ubuntu 26.04, 24.04, 22.04, 20.04, Debian 12, Debian 13 (6 tests)
- **dx-compiler**: Ubuntu 26.04, 24.04, 22.04, 20.04, Fedora 42-45, RHEL 9-10, CentOS Stream 9-10 (12 tests)

**Total: 24 build tests + 4 sanity tests = 28 tests**

## Quick Start

### 1. Run Sanity Tests Only (Quick Validation)

```bash
cd tests
./test.sh docker_install -k "sanity"
```

### 2. Run Docker Installation Tests

```bash
./test.sh docker_install
```

### 3. Test Specific Targets

```bash
./test.sh docker_install -k "runtime"      # dx-runtime only
./test.sh docker_install -k "modelzoo"     # dx-modelzoo only
./test.sh docker_insatll -k "compiler"     # dx-compiler only
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

# Combination (AND)
pytest -k "runtime and ubuntu"
pytest -k "runtime and 24.04"

# Combination (OR)
pytest -k "runtime or compiler"

# Exclusion (NOT)
pytest -k "not debian"
pytest -k "ubuntu and not 20.04"
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
./test.sh docker_install --report

# Direct specification
pytest --html=report.html --self-contained-html
```

**Generated at:** `tests/reports/test_report_<timestamp>.html`

### JSON Report

```bash
# Using test.sh (recommended)
./test.sh json

# Direct specification
pytest --json-report --json-report-file=report.json
```

**Generated at:** `tests/reports/test_report_<timestamp>.json`

## Test Structure

### Sanity Tests (4 tests)

Pre-build environment validation:

- `test_docker_build_script_exists` - Verify docker_build.sh exists
- `test_docker_command_available` - Check docker command
- `test_docker_compose_command_available` - Check docker compose
- `test_project_structure` - Verify project structure

### Build Tests (26 tests)

Actual Docker image builds:

**dx-runtime (6 tests)**
- `test_docker_build[dx-runtime-ubuntu-26.04]`
- `test_docker_build[dx-runtime-ubuntu-24.04]`
- `test_docker_build[dx-runtime-ubuntu-22.04]`
- `test_docker_build[dx-runtime-ubuntu-20.04]`
- `test_docker_build[dx-runtime-debian-12]`
- `test_docker_build[dx-runtime-debian-13]`

**dx-modelzoo (6 tests)**
- `test_docker_build[dx-modelzoo-ubuntu-26.04]`
- `test_docker_build[dx-modelzoo-ubuntu-24.04]`
- `test_docker_build[dx-modelzoo-ubuntu-22.04]`
- `test_docker_build[dx-modelzoo-ubuntu-20.04]`
- `test_docker_build[dx-modelzoo-debian-12]`
- `test_docker_build[dx-modelzoo-debian-13]`

**dx-compiler (12 tests)**
- `test_docker_build[dx-compiler-ubuntu-26.04]`
- `test_docker_build[dx-compiler-ubuntu-24.04]`
- `test_docker_build[dx-compiler-ubuntu-22.04]`
- `test_docker_build[dx-compiler-ubuntu-20.04]`
- `test_docker_build[dx-compiler-fedora-42]`
- `test_docker_build[dx-compiler-fedora-43]`
- `test_docker_build[dx-compiler-fedora-44]`
- `test_docker_build[dx-compiler-fedora-45]`
- `test_docker_build[dx-compiler-rhel-9]`
- `test_docker_build[dx-compiler-rhel-10]`
- `test_docker_build[dx-compiler-centos-stream9]`
- `test_docker_build[dx-compiler-centos-stream10]`

## Expected Execution Time

- **Sanity tests:** ~5 seconds
- **Single build test:** ~10-15 minutes (first build) / ~5-10 minutes (with cache)
- **Full test suite:** ~2-4 hours (without parallel execution)

## License

This test suite is part of the dx-all-suite project.
