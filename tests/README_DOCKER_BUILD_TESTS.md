# Docker Build Test Suite

A pytest-based test suite for automated Docker image build verification.

## Overview

This test suite validates the following Docker image builds:

- **dx-runtime**: Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12, Debian 13 (6 tests)
- **dx-modelzoo**: Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12, Debian 13 (6 tests)
- **dx-compiler**: Ubuntu 24.04, 22.04, 20.04 (3 tests)

**Total: 15 build tests + 4 sanity tests = 19 tests**

## File Structure

```
tests/
├── test_docker_build.py              # Main pytest test file
├── run_docker_build_tests.sh         # Test execution script
├── test.sh                           # Convenient command wrapper
├── REFERENCE.sh                      # Quick reference guide
├── README_DOCKER_BUILD_TESTS.md      # This document
├── CI_CD_EXAMPLES.md                 # CI/CD integration examples
├── SUMMARY.md                        # Project overview
├── requirements.txt                  # Python dependencies (auto-generated)
├── venv/                             # Python virtual environment (auto-generated)
└── reports/                          # Test reports (auto-generated)
```

## Quick Start

### 1. Run Sanity Tests Only (Quick Validation)

```bash
cd tests
./test.sh sanity
```

### 2. Run All Tests

```bash
./test.sh all
```

### 3. Test Specific Targets

```bash
./test.sh runtime      # dx-runtime only
./test.sh modelzoo     # dx-modelzoo only
./test.sh compiler     # dx-compiler only
```

## Detailed Usage

### test.sh Commands

`test.sh` is a convenient wrapper for common test scenarios:

```bash
# Basic usage
./test.sh <command> [additional_args...]

# Available commands
./test.sh sanity           # Sanity tests only
./test.sh all              # All tests
./test.sh runtime          # dx-runtime tests
./test.sh modelzoo         # dx-modelzoo tests
./test.sh compiler         # dx-compiler tests
./test.sh ubuntu           # Ubuntu images only
./test.sh debian           # Debian images only
./test.sh ubuntu-24.04     # Ubuntu 24.04 only
./test.sh ubuntu-22.04     # Ubuntu 22.04 only
./test.sh ubuntu-20.04     # Ubuntu 20.04 only
./test.sh ubuntu-18.04     # Ubuntu 18.04 only
./test.sh debian-12        # Debian 12 only
./test.sh debian-13        # Debian 13 only
./test.sh list             # List all tests
./test.sh report           # Generate HTML report
./test.sh json             # Generate JSON report
./test.sh help             # Show help
```

### run_docker_build_tests.sh Commands

For more granular control, use directly:

```bash
# Basic usage
./run_docker_build_tests.sh [pytest_args...]

# Examples
./run_docker_build_tests.sh -v                    # Verbose output
./run_docker_build_tests.sh -k "runtime"          # Specific tests
./run_docker_build_tests.sh --collect-only        # List tests only
./run_docker_build_tests.sh -x                    # Stop on first failure
./run_docker_build_tests.sh -v -s                 # Verbose + stdout
```

### Direct pytest Usage

You can also activate the virtual environment directly and use pytest:

```bash
# Activate virtual environment
source ./venv/bin/activate

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
./run_docker_build_tests.sh -k "runtime"
./run_docker_build_tests.sh -k "modelzoo"
./run_docker_build_tests.sh -k "compiler"

# Specific OS
./run_docker_build_tests.sh -k "ubuntu"
./run_docker_build_tests.sh -k "debian"

# Specific version
./run_docker_build_tests.sh -k "24.04"
./run_docker_build_tests.sh -k "22.04"

# Combination (AND)
./run_docker_build_tests.sh -k "runtime and ubuntu"
./run_docker_build_tests.sh -k "runtime and 24.04"

# Combination (OR)
./run_docker_build_tests.sh -k "runtime or compiler"

# Exclusion (NOT)
./run_docker_build_tests.sh -k "not debian"
./run_docker_build_tests.sh -k "ubuntu and not 18.04"
```

### Filter by Marker (-m option)

```bash
# Sanity tests only
./run_docker_build_tests.sh -m sanity

# Exclude sanity tests
./run_docker_build_tests.sh -m "not sanity"
```

## Report Generation

### HTML Report

```bash
# Using test.sh (recommended)
./test.sh report

# Direct specification
./run_docker_build_tests.sh --html=report.html --self-contained-html
```

**Generated at:** `tests/reports/test_report_<timestamp>.html`

### JSON Report

```bash
# Using test.sh (recommended)
./test.sh json

# Direct specification
./run_docker_build_tests.sh --json-report --json-report-file=report.json
```

**Generated at:** `tests/reports/test_report_<timestamp>.json`

## Execution Examples

### Example 1: Quick Validation

```bash
# Run sanity tests only (~5 seconds)
./test.sh sanity
```

### Example 2: Specific Target Test

```bash
# Test dx-runtime only (~2.5 hours)
./test.sh runtime -v
```

### Example 3: Specific OS Version Test

```bash
# Test Ubuntu 24.04 only
./test.sh ubuntu-24.04 -v
```

### Example 4: Full Test with Report

```bash
# Run all tests + generate HTML report
./test.sh report
```

### Example 5: Stop on First Failure

```bash
# Stop immediately on failure
./run_docker_build_tests.sh -x -v
```

## Test Structure

### Sanity Tests (4 tests)

Pre-build environment validation:

- `test_docker_build_script_exists` - Verify docker_build.sh exists
- `test_docker_command_available` - Check docker command
- `test_docker_compose_command_available` - Check docker compose
- `test_project_structure` - Verify project structure

### Build Tests (15 tests)

Actual Docker image builds:

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

## Expected Execution Time

- **Sanity tests:** ~5 seconds
- **Single build test:** ~10-15 minutes (first build) / ~5-10 minutes (with cache)
- **Full test suite:** ~2-4 hours (without parallel execution)

## Troubleshooting

### pytest Not Found

```bash
# Recreate virtual environment
rm -rf ./venv
./run_docker_build_tests.sh --collect-only
```

### Docker Permission Error

```bash
# Add current user to docker group
sudo usermod -aG docker $USER
# Log out and log back in
```

### Test Timeout

Each build has a default 30-minute timeout. If needed, adjust the `TEST_TIMEOUT` value in `test_docker_build.py`:

```python
TEST_TIMEOUT = 1800  # 30 minutes (in seconds)
```

### Virtual Environment Issues

```bash
# Completely remove and recreate virtual environment
rm -rf ./venv
./run_docker_build_tests.sh --collect-only
```

## CI/CD Integration

For information on integrating with CI/CD pipelines, see [CI_CD_EXAMPLES.md](CI_CD_EXAMPLES.md).

Includes examples for major CI platforms:
- GitHub Actions
- GitLab CI
- Jenkins

## Additional Information

- **Quick Reference:** [REFERENCE.sh](REFERENCE.sh) - Quick command reference
- **Project Overview:** [SUMMARY.md](SUMMARY.md) - Complete project summary
- **CI/CD Examples:** [CI_CD_EXAMPLES.md](CI_CD_EXAMPLES.md) - CI/CD integration guide

## License

This test suite is part of the dx-all-suite project.
