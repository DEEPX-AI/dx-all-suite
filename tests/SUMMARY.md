# Docker Build Test Suite - Project Summary

## 📋 Overview

A pytest-based test suite for automated verification of Docker image builds in the dx-all-suite project.

**Purpose:** Automatically validate that all 15 Docker image build configurations build successfully.

## 🎯 Test Scope

### Build Targets (3)

- **dx-runtime**: Runtime environment
- **dx-modelzoo**: Model repository
- **dx-compiler**: Compiler

### OS Configurations (15 combinations)

| Target | Ubuntu 24.04 | Ubuntu 22.04 | Ubuntu 20.04 | Ubuntu 18.04 | Debian 12 | Debian 13 | Total |
|--------|--------------|--------------|--------------|--------------|-----------|-----------|-------|
| dx-runtime | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 |
| dx-modelzoo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | 6 |
| dx-compiler | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | 3 |
| **Total** | **3** | **3** | **3** | **2** | **2** | **2** | **15** |

**Note:** dx-compiler supports Ubuntu only

### Test Composition

- **Sanity tests:** 4 (environment validation)
- **Build tests:** 15 (actual builds)
- **Total tests:** 19

## 📁 File Structure

```
tests/
├── 🐍 test_docker_build.py              # Main test file (pytest)
├── 🔧 run_docker_build_tests.sh         # Test execution script
├── ⚡ test.sh                           # Convenient command wrapper
├── 📖 REFERENCE.sh                      # Quick reference guide
├── 📚 README_DOCKER_BUILD_TESTS.md      # Detailed usage guide
├── 🔄 CI_CD_EXAMPLES.md                 # CI/CD integration examples
├── 📝 SUMMARY.md                        # This document
├── 📦 requirements.txt                  # Python dependencies (auto-generated)
├── 🐍 venv/                             # Python virtual environment (auto-generated)
└── 📊 reports/                          # Test reports (auto-generated)
```

## 🚀 Quick Start

### Step 1: Sanity Check (5 seconds)

```bash
cd tests
./test.sh sanity
```

### Step 2: Test Specific Targets

```bash
./test.sh runtime      # dx-runtime only (~2.5 hours)
./test.sh modelzoo     # dx-modelzoo only (~2.5 hours)
./test.sh compiler     # dx-compiler only (~1.5 hours)
```

### Step 3: Full Test Suite

```bash
./test.sh all          # All tests (~6-8 hours)
```

## 💡 Key Commands

### Basic Commands

```bash
./test.sh sanity           # ⚡ Quick validation (5 seconds)
./test.sh all              # 🔥 Full test suite (6-8 hours)
./test.sh list             # 📋 List all tests
./test.sh help             # ❓ Show help
```

### Target-Specific Execution

```bash
./test.sh runtime          # dx-runtime tests
./test.sh modelzoo         # dx-modelzoo tests
./test.sh compiler         # dx-compiler tests
```

### OS-Specific Execution

```bash
./test.sh ubuntu           # All Ubuntu
./test.sh debian           # All Debian
./test.sh ubuntu-24.04     # Ubuntu 24.04 only
./test.sh ubuntu-22.04     # Ubuntu 22.04 only
./test.sh ubuntu-20.04     # Ubuntu 20.04 only
./test.sh ubuntu-18.04     # Ubuntu 18.04 only
./test.sh debian-12        # Debian 12 only
./test.sh debian-13        # Debian 13 only
```

### Report Generation

```bash
./test.sh report           # 📊 HTML report
./test.sh json             # 📄 JSON report
```

## 🎨 Usage Examples

### Example 1: Quick Validation During Development

```bash
# Test sanity + latest version before PR
./test.sh sanity && ./test.sh ubuntu-24.04
```

### Example 2: Focused Testing on Specific Target

```bash
# After modifying runtime-related code
./test.sh runtime -v
```

### Example 3: Full Validation Before Release

```bash
# Full test suite with report generation
./test.sh report
```

### Example 4: Specific OS Versions Only

```bash
# Test only Ubuntu 24.04 and Debian 12
./run_docker_build_tests.sh -k "24.04 or 12"
```

## 📊 Expected Execution Time

| Test Type | Test Count | Expected Time | Use Case |
|-----------|------------|---------------|----------|
| Sanity | 4 | ~5 seconds | Environment validation |
| Single Build | 1 | ~10-15 minutes | Individual test |
| Runtime | 6 | ~2.5 hours | Target validation |
| Modelzoo | 6 | ~2.5 hours | Target validation |
| Compiler | 3 | ~1.5 hours | Target validation |
| Full Suite | 19 | ~6-8 hours | Complete validation |

**Note:** Times may vary based on cache state and system performance.

## 🔍 Test Details

### Sanity Tests (4 tests)

Environment and prerequisite validation:

- ✅ `test_docker_build_script_exists` - Verify docker_build.sh script exists
- ✅ `test_docker_command_available` - Check docker command availability
- ✅ `test_docker_compose_command_available` - Check docker compose availability
- ✅ `test_project_structure` - Verify required directory structure

### Build Tests (15 tests)

Actual Docker image build validation:

**dx-runtime (6 tests)**

- ✅ `test_docker_build[dx-runtime-ubuntu-24.04]`
- ✅ `test_docker_build[dx-runtime-ubuntu-22.04]`
- ✅ `test_docker_build[dx-runtime-ubuntu-20.04]`
- ✅ `test_docker_build[dx-runtime-ubuntu-18.04]`
- ✅ `test_docker_build[dx-runtime-debian-12]`
- ✅ `test_docker_build[dx-runtime-debian-13]`

**dx-modelzoo (6 tests)**

- ✅ `test_docker_build[dx-modelzoo-ubuntu-24.04]`
- ✅ `test_docker_build[dx-modelzoo-ubuntu-22.04]`
- ✅ `test_docker_build[dx-modelzoo-ubuntu-20.04]`
- ✅ `test_docker_build[dx-modelzoo-ubuntu-18.04]`
- ✅ `test_docker_build[dx-modelzoo-debian-12]`
- ✅ `test_docker_build[dx-modelzoo-debian-13]`

**dx-compiler (3 tests)**

- ✅ `test_docker_build[dx-compiler-ubuntu-24.04]`
- ✅ `test_docker_build[dx-compiler-ubuntu-22.04]`
- ✅ `test_docker_build[dx-compiler-ubuntu-20.04]`

## 🛠 Technology Stack

- **Test Framework:** pytest 7.4.3+
- **Reporting:** pytest-html, pytest-json-report
- **Languages:** Python 3.8+, Bash
- **Required Tools:** Docker, Docker Compose
- **Platform:** Ubuntu/Debian Linux

## 📚 Documentation

| Document | Description |
|----------|-------------|
| `README_DOCKER_BUILD_TESTS.md` | 📘 Detailed usage guide |
| `CI_CD_EXAMPLES.md` | 🔄 CI/CD integration examples |
| `REFERENCE.sh` | 📖 Quick command reference |
| `SUMMARY.md` | 📝 This document (project overview) |

## 🔧 Advanced Usage

### Direct pytest Usage

```bash
# Activate virtual environment
source ./venv/bin/activate

# Various filtering options
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
./run_docker_build_tests.sh --collect-only
```

#### 2. Docker Permission Error

```bash
sudo usermod -aG docker $USER
# Log out and log back in
```

#### 3. Build Timeout

Adjust timeout in `test_docker_build.py`:

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

## 🔄 CI/CD Integration

This test suite can be integrated with the following CI/CD platforms:

- ✅ GitHub Actions
- ✅ GitLab CI
- ✅ Jenkins
- ✅ Others (standard pytest compatible)

See [CI_CD_EXAMPLES.md](CI_CD_EXAMPLES.md) for detailed examples.

### Recommended CI/CD Strategy

**Pull Request:**
- ✅ Sanity tests
- ✅ Latest OS version (24.04) build
- ❌ Full test suite (save time)

**Main/Develop Branch:**
- ✅ Run full test suite
- ✅ Generate reports
- ✅ Archive artifacts

**Release:**
- ✅ Run full test suite
- ✅ Manual approval step
- ✅ Review detailed reports

## 📈 Test Coverage

| Category | Coverage |
|----------|----------|
| Build Targets | 3/3 (100%) |
| Ubuntu Versions | 4/4 (100%) |
| Debian Versions | 2/2 (100%) |
| Total Combinations | 15/15 (100%) |

## 🎯 Project Goals

- ✅ **Automation:** Eliminate manual build verification
- ✅ **Consistency:** Same validation across all OS versions
- ✅ **Reliability:** Early detection of build failures
- ✅ **Efficiency:** CI/CD pipeline integration
- ✅ **Documentation:** Clear usage instructions

## 🤝 Contribution Guide

When adding or improving tests:

1. Add new OS versions by modifying `@pytest.mark.parametrize` in `test_docker_build.py`
2. Add new targets to the same parametrize decorator
3. Verify test execution: `./test.sh sanity && ./test.sh list`
4. Update documentation: `README.md`, `SUMMARY.md`, etc.

## 📞 Support

- 📖 **Documentation:** [README_DOCKER_BUILD_TESTS.md](README_DOCKER_BUILD_TESTS.md)
- 📋 **Quick Reference:** [REFERENCE.sh](REFERENCE.sh)
- 🔄 **CI/CD Guide:** [CI_CD_EXAMPLES.md](CI_CD_EXAMPLES.md)
