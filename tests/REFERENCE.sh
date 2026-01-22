#!/bin/bash
#
# Quick Reference Card for Docker Build Tests
#
# This file provides a quick reference for common test commands.
# Copy and paste these commands as needed.
#

cat << 'EOF'
=============================================================================
Docker Build Test Suite - Quick Reference
=============================================================================

BASIC USAGE:
------------
# Run sanity checks only (quick validation)
./test.sh sanity

# Run all tests
./test.sh all

# List all available tests
./test.sh list


TARGET-SPECIFIC TESTS:
----------------------
# Run only dx-runtime tests (5 tests)
./test.sh runtime

# Run only dx-modelzoo tests (5 tests)
./test.sh modelzoo

# Run only dx-compiler tests (3 tests)
./test.sh compiler


OS-SPECIFIC TESTS:
------------------
# Run all Ubuntu tests
./test.sh ubuntu

# Run all Debian tests
./test.sh debian

# Run specific OS version tests
./test.sh ubuntu-24.04
./test.sh ubuntu-22.04
./test.sh ubuntu-20.04
./test.sh ubuntu-18.04
./test.sh debian-12


ADVANCED USAGE:
---------------
# Run with verbose output
./test.sh all -v

# Run specific test by name
./run_docker_build_tests.sh -k "test_docker_build[dx-runtime-ubuntu-24.04]"

# Run with custom pytest options
./run_docker_build_tests.sh -v -s --tb=short


REPORTING:
----------
# Generate HTML report
./test.sh report

# Generate JSON report
./test.sh json

# Custom report location
./run_docker_build_tests.sh --html=my_report.html --self-contained-html


COMBINING FILTERS:
------------------
# Run runtime tests on Ubuntu only
./run_docker_build_tests.sh -k "runtime and ubuntu"

# Run tests for 24.04 across all targets
./run_docker_build_tests.sh -k "24.04"

# Exclude specific tests
./run_docker_build_tests.sh -k "not debian"


DIRECT PYTEST USAGE:
--------------------
# Activate venv first
source ./venv/bin/activate

# Then use pytest directly
pytest -v
pytest -k "runtime"
pytest --collect-only
pytest -v --tb=short
pytest -x  # Stop on first failure

# Deactivate when done
deactivate


TEST STRUCTURE:
---------------
Sanity Tests (4 tests):
  - test_docker_build_script_exists
  - test_docker_command_available
  - test_docker_compose_command_available
  - test_project_structure

Build Tests (13 tests):
  dx-runtime:   Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12 (5 tests)
  dx-modelzoo:  Ubuntu 24.04, 22.04, 20.04, 18.04, Debian 12 (5 tests)
  dx-compiler:  Ubuntu 24.04, 22.04, 20.04 (3 tests)


FILE LOCATIONS:
---------------
Test script:          internal/tests/test_docker_build.py
Test runner:          internal/tests/run_docker_build_tests.sh
Quick commands:       internal/tests/test.sh
Test reports:         internal/tests/reports/
Virtual environment:  internal/tests/venv/


TROUBLESHOOTING:
----------------
# Clean venv and reinstall
rm -rf ./venv
./run_docker_build_tests.sh --collect-only

# Check pytest version
source ./venv/bin/activate && pip list | grep pytest

# View full test output
./run_docker_build_tests.sh -v -s

# Debug specific test
./run_docker_build_tests.sh -v -s -k "test_name_here"


=============================================================================
For more information, see: internal/tests/README_DOCKER_BUILD_TESTS.md
=============================================================================
EOF
