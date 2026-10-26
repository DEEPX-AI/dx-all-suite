# SPDX-License-Identifier: Apache-2.0
"""The dx-runtime unified validator is also run by the CI sub-repo gate on a
`git archive HEAD` copy of dx-runtime, where the nested submodules dx_app and
dx_stream are EMPTY directories (archive never includes submodule contents).
Checks that depend on those trees must then be reported as SKIP (submodule not
initialized) instead of FAIL — otherwise every green subrepo-gate run carries a
misleading `validate_framework.py reported failures` warning (seen 2026-09-08).
On a fully initialized tree the very same checks must still be real PASS/FAIL."""

from __future__ import annotations

import re
import io
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from .conftest import RUNTIME_ROOT

SCRIPT = RUNTIME_ROOT / ".deepx" / "scripts" / "validate_framework.py"
SUB_CHECK_MESSAGES = (
    "dx_app .deepx/ directory exists", "dx_app CLAUDE.md exists",
    "dx_stream .deepx/ directory exists", "dx_stream CLAUDE.md exists",
)


def _run(repo_root: Path) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), str(repo_root)], cwd=repo_root,
                          text=True, capture_output=True, timeout=300)


@pytest.fixture(scope="module")
def archive_copy(tmp_path_factory) -> Path:
    """dx-runtime at committed HEAD, exactly as subrepo_check.sh copies it."""
    if not SCRIPT.is_file() or not (RUNTIME_ROOT / ".git").exists():
        pytest.skip("dx-runtime not initialized here")
    dest = tmp_path_factory.mktemp("dx-runtime-archive")
    data = subprocess.run(["git", "-C", str(RUNTIME_ROOT), "archive", "--format=tar", "HEAD"],
                          check=True, capture_output=True).stdout
    with tarfile.open(fileobj=io.BytesIO(data)) as tar:
        # `filter=` exists from 3.12 (backported to 3.8.17+); the GHES runners run 3.8.10
        if hasattr(tarfile, "data_filter"):
            tar.extractall(dest, filter="data")
        else:
            tar.extractall(dest)  # trusted archive: our own git archive of HEAD
    # Test the WORKING-TREE validator (the code under test), not the one at HEAD —
    # otherwise this test can only go green after the fix has been committed.
    shutil.copyfile(SCRIPT, dest / ".deepx" / "scripts" / "validate_framework.py")
    assert (dest / ".deepx" / "scripts" / "validate_framework.py").is_file()
    assert not any((dest / "dx_app").iterdir()), "archive copy must have an EMPTY dx_app/ (gitlink only)"
    return dest


def test_archive_copy_skips_uninitialized_sub_projects(archive_copy):
    r = subprocess.run([sys.executable, str(archive_copy / ".deepx/scripts/validate_framework.py"), str(archive_copy)],
                       cwd=archive_copy, text=True, capture_output=True, timeout=300)
    out = r.stdout + r.stderr
    fails = [l for l in out.splitlines() if l.startswith("[FAIL]")]
    sub_fails = [l for l in fails if "dx_app" in l or "dx_stream" in l]
    assert not sub_fails, "uninitialized sub-projects must not FAIL:\n" + "\n".join(sub_fails)
    for msg in SUB_CHECK_MESSAGES:
        assert re.search(rf"^\[SKIP\].*{re.escape(msg)}", out, re.M), f"expected [SKIP] for {msg!r}\n{out}"
    # routing/handoff refs into dx_app/ or dx_stream/ must not be reported as missing
    assert not re.search(r"(does not exist|handoff target missing): (dx_app|dx_stream)/", out), out
    assert r.returncode == 0, f"archive-copy validation must pass (only skips), got {r.returncode}\n{out}"


def test_initialized_tree_does_not_skip_sub_projects():
    if not SCRIPT.is_file() or not (RUNTIME_ROOT / "dx_app" / ".deepx").is_dir():
        pytest.skip("dx_app not initialized here")
    out = _run(RUNTIME_ROOT).stdout
    for msg in SUB_CHECK_MESSAGES:
        assert re.search(rf"^\[PASS\].*{re.escape(msg)}", out, re.M), f"expected real [PASS] for {msg!r}\n{out}"
    assert "[SKIP]" not in out.split("=== RESULT")[0].replace("Model registry", ""), (
        "nothing should be skipped on an initialized tree:\n" + out)
