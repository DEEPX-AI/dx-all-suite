"""Compile jobs can live outside the studio's var/ (DX_COMPILER_JOB_ROOT) — tests use it so they do not leave
empty job folders in the real var/compiler/jobs."""
from __future__ import annotations

import importlib


def test_the_job_root_follows_the_environment(tmp_path, monkeypatch):
    monkeypatch.setenv("DX_COMPILER_JOB_ROOT", str(tmp_path / "jobs"))
    svc_mod = importlib.import_module("dx_compiler.core.compiler_service")
    pp = importlib.import_module("dx_compiler.core.path_policy")
    assert svc_mod.CompilerService().job_root == (tmp_path / "jobs").resolve()
    assert pp._jobs_root() == tmp_path / "jobs"


def test_the_shared_compile_test_fixture_keeps_jobs_out_of_var():
    src = (importlib.import_module("tests.dx_compiler._compile_paths").__file__)
    text = open(src, encoding="utf-8").read()
    assert 'setenv("DX_COMPILER_JOB_ROOT"' in text
