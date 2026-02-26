#!/bin/bash
#
# Quick Reference Card for DX-ALL-SUITE Test Suite
#
# This file provides a quick reference for common test commands.
# Copy and paste these commands as needed.
#

cat << 'EOF'
=============================================================================
DX-ALL-SUITE Test Suite - Quick Reference
=============================================================================

BASIC USAGE:
------------
# Run sanity checks only (quick validation ~5-10 seconds)
./test.sh sanity

# Run all tests (~12-20 hours)
./test.sh all

# List all available tests
./test.sh list

# Show help and usage
./test.sh help


TEST SUITE COMMANDS:
--------------------
# Docker installation tests (15 tests, ~6-8 hours)
./test.sh docker_install

# Local installation tests (48 tests, ~8-12 hours)
./test.sh local_install

# Getting-started workflow (11 tests, ~30-60 minutes)
./test.sh getting_started


COMPONENT-SPECIFIC TESTS:
-------------------------
# Run only dx-runtime tests
./test.sh docker_install -k "runtime"
./test.sh local_install -k "runtime"

# Run only dx-modelzoo tests
./test.sh docker_install -k "modelzoo"
./test.sh local_install -k "modelzoo"

# Run only dx-compiler tests
./test.sh docker_install -k "compiler"
./test.sh local_install -k "compiler"


OS-SPECIFIC TESTS:
------------------
# Run all Ubuntu tests
./test.sh docker_install -k "ubuntu"
./test.sh local_install -k "ubuntu"

# Run all Debian tests
./test.sh docker_install -k "debian"
./test.sh local_install -k "debian"

# Run specific OS version tests
./test.sh docker_install -k "24.04"
./test.sh local_install -k "ubuntu and 22.04"
./test.sh docker_install -k "debian and 12"


WORKFLOW-SPECIFIC TESTS:
------------------------
# Compiler workflow only
./test.sh getting_started -k "compiler"

# Runtime workflow only
./test.sh getting_started -k "runtime"

# Specific workflow step
./test.sh getting_started -k "test_compiler_4_model_compile"
./test.sh getting_started -k "test_runtime_3_run_example"


STAGE-SPECIFIC TESTS (local_install):
--------------------------------------
# Docker build stage only
./test.sh local_install -k "build"

# Container run stage only
./test.sh local_install -k "run"

# Installation stage only
./test.sh local_install -k "install"


REPORTING OPTIONS:
------------------
# Generate HTML report (timestamped)
./test.sh --report docker_install

# Custom HTML report filename
./test.sh --html=my_report.html local_install

# Generate JSON report (timestamped)
./test.sh --json-report getting_started

# Custom JSON report filename
./test.sh --json=my_report.json docker_install

# Multiple reports
./test.sh --report --json-report all


ADVANCED OPTIONS:
-----------------
# Verbose debug mode
./test.sh --debug local_install

# List tests without running them
./test.sh --list local_install
./test.sh --list -k "runtime and ubuntu and 24.04" docker_install

# Exclude firmware in runtime install
./test.sh --exclude-fw local_install -k "runtime"
./test.sh --exclude-fw getting_started -k "runtime"

# Use internal network settings
./test.sh --internal docker_install

# Set credentials for dx-compiler downloads from developer.deepx.ai
./test.sh --dx_username=your_username --dx_password=your_password local_install

# Clear pytest cache before running
./test.sh --cache-clear all

# Combine multiple options
./test.sh --report --debug docker_install -k "runtime"
./test.sh --internal --dx_username=admin --dx_password=secret local_install


MARKER FILTERS (-m option):
---------------------------
# Run only sanity tests
./test.sh all -m "sanity"

# Run specific test suite by marker
./test.sh all -m "docker_install"
./test.sh all -m "local_install"
./test.sh all -m "getting_started"

# Run compiler or runtime workflow tests
./test.sh getting_started -m "compiler"
./test.sh getting_started -m "runtime"

# Exclude sanity tests
./test.sh all -m "not sanity"


KEYWORD FILTERS (-k option):
----------------------------
# Combine filters with AND
./test.sh docker_install -k "runtime and ubuntu"
./test.sh local_install -k "compiler and 24.04"
./test.sh local_install -k "runtime and build"

# Combine filters with OR
./test.sh docker_install -k "runtime or compiler"

# Exclude with NOT
./test.sh docker_install -k "not debian"
./test.sh local_install -k "ubuntu and not 18.04"

# Complex expressions
./test.sh local_install -k "(runtime or modelzoo) and ubuntu and not 18.04"


DIRECT PYTEST USAGE:
--------------------
# Activate venv first
source ./venv/bin/activate

# Then use pytest directly
pytest -v                              # All tests verbose
pytest -m docker_install               # Docker install tests
pytest -m local_install                # Local install tests
pytest -m getting_started              # Getting-started tests
pytest -k "runtime and ubuntu"         # Keyword filter
pytest --collect-only                  # List tests without running
pytest -v --tb=short                   # Short traceback
pytest -x                              # Stop on first failure
pytest --lf                            # Run last failed tests
pytest --ff                            # Failed first, then others
pytest -v -s                           # No output capture

# Deactivate when done
deactivate


COMBINING OPTIONS - EXAMPLES:
------------------------------
# Docker install with HTML report
./test.sh --report docker_install

# List tests before running
./test.sh --list --internal -k "runtime and ubuntu and 24.04" local_install

# Runtime tests with verbose output
./test.sh --debug docker_install -k "runtime"

# Ubuntu 24.04 tests across all suites
./test.sh --report all -k "ubuntu and 24.04"

# Local install without firmware
./test.sh --exclude-fw local_install -k "runtime"

# Getting-started compiler workflow with JSON report
./test.sh --json=compiler_workflow.json getting_started -k "compiler"

# Local install with internal network and credentials
./test.sh --internal --dx_username=admin --dx_password=secret local_install -k "compiler"

# Sanity checks with verbose output
./test.sh --debug sanity

# Full test suite with all reports
./test.sh --report --json-report --debug all


TEST STRUCTURE SUMMARY:
-----------------------
docker_install (19 tests):
  - 4 sanity tests
  - 15 build tests (3 compiler + 6 modelzoo + 6 runtime)

local_install (48 tests):
  - 3 sanity tests
  - 15 build tests
  - 15 run tests
  - 15 install tests

getting_started (11 tests):
  - 6 compiler workflow tests
  - 5 runtime workflow tests

Total: 78 tests


FILE LOCATIONS:
---------------
Test suites:
  - test_docker_install/test_docker_install.py
  - test_local_install/test_local_install.py
  - test_getting-started/test_getting_started.py

Documentation:
  - README.md (main test suite documentation)
  - test_docker_install/README.md
  - test_local_install/README.md
  - test_getting-started/README.md

Test infrastructure:
  - test.sh (main test wrapper)
  - conftest.py (shared pytest fixtures)
  - pytest.ini (pytest configuration)
  - requirements.txt (Python dependencies)

Reports (auto-generated):
  - reports/test_report_*.html
  - reports/test_report_*.json

Virtual environment:
  - venv/ (auto-created)


TROUBLESHOOTING:
----------------
# Clean venv and reinstall
rm -rf ./venv
./test.sh sanity

# Check pytest version
source ./venv/bin/activate && pip list | grep pytest

# View full test output
./test.sh --debug docker_install

# Debug specific test
./test.sh --debug docker_install -k "test_docker_build[dx-runtime-ubuntu-24.04]"

# Clear pytest cache
./test.sh --cache-clear all

# Check what tests will run
./test.sh docker_install --collect-only
./test.sh local_install -k "runtime" --collect-only

# Run last failed tests
source ./venv/bin/activate
pytest --lf -v

# Clean up test containers (local_install)
docker ps -a | grep "dx-local-install" | awk '{print $1}' | xargs docker rm -f

# Clean up test images (local_install)
docker images | grep "dx-local-install" | awk '{print $3}' | xargs docker rmi -f

# Fix dx-compiler download failures from developer.deepx.ai
export DX_USERNAME="your_username"
export DX_PASSWORD="your_password"
./test.sh --dx_username=your_username --dx_password=your_password local_install -k "compiler"


EXPECTED EXECUTION TIMES:
-------------------------
Sanity tests:           ~5-10 seconds
docker_install:         ~6-8 hours (15 tests)
local_install:          ~8-12 hours (48 tests)
getting_started:        ~30-60 minutes (11 tests)
Full suite (all):       ~12-20 hours (78 tests)


=============================================================================
For more information, see: README.md
=============================================================================
EOF
