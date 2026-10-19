"""For tests that do not target the compile path policy — fake paths pass through unchanged.

Tests of other validation (opt_level, enhanced_scheme, preprocessings) send paths that do not exist, such as
'/tmp/a.onnx'. The path policy itself is covered by test_path_policy.py against the real functions. (A module
conftest may only set up paths — see tests/test_pytest_infra_contract.py — so the fixtures live here.)
"""
import importlib
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def compile_jobs_outside_var(monkeypatch, tmp_path):
    """The compiler these tests start keeps job folders in tmp, so no empty folders land in var/compiler/jobs."""
    monkeypatch.setenv("DX_COMPILER_JOB_ROOT", str(tmp_path / "compiler-jobs"))


@pytest.fixture(autouse=True)
def compile_paths_not_under_test(monkeypatch):
    pp = importlib.import_module("dx_compiler.core.path_policy")
    monkeypatch.setattr(pp, "check_input_file", lambda raw, field: Path(raw))
    monkeypatch.setattr(pp, "check_input_dir", lambda raw, field: Path(raw))
    monkeypatch.setattr(pp, "check_output_dir", lambda raw, field="output_dir": Path(raw))
