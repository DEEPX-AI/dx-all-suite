"""setup_data.sh must not reuse models from a different source/version (file names repeat across releases)."""
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "setup_data.sh"
BASE_URL = re.search(r'local BASE_URL="([^"]+)"', SCRIPT.read_text()).group(1)
VERSION = "9_9_9"
SOURCE = f"{BASE_URL}/{VERSION}"

pytestmark = pytest.mark.skipif(not (shutil.which("jq") and shutil.which("bash")),
                                reason="jq/bash required")


@pytest.fixture
def env(tmp_path):
    (tmp_path / "benchmark").mkdir()
    shutil.copy(SCRIPT, tmp_path / "setup_data.sh")
    (tmp_path / "benchmark" / "model_list.json").write_text(
        f'{{"version": "{VERSION}", "models": [{{"file": "m.dxnn", "task": "od", "size": "n"}}]}}')
    fakebin = tmp_path / "bin"
    fakebin.mkdir()
    calls = tmp_path / "curl.calls"
    curl = fakebin / "curl"
    curl.write_text('#!/bin/bash\nwhile [ $# -gt 0 ]; do case "$1" in -o) o="$2"; shift;; '
                    f'http*) echo "$1" >> {calls};; esac; shift; done\nprintf NEW > "$o"\n')
    curl.chmod(0o755)
    models = tmp_path / "benchmark" / "assets" / "models"
    models.mkdir(parents=True)
    return tmp_path, models, calls


def _run(root):
    return subprocess.run(["bash", str(root / "setup_data.sh"), "models"], capture_output=True,
                          text=True, env={**os.environ, "PATH": f"{root / 'bin'}:{os.environ['PATH']}"})


def _ncalls(calls):
    return len(calls.read_text().split()) if calls.exists() else 0


def test_fresh_download_writes_source_stamp(env):
    root, models, calls = env
    r = _run(root)
    assert r.returncode == 0, r.stderr
    assert (models / ".model_source").read_text().strip() == SOURCE
    assert (models / "m.dxnn").read_text() == "NEW"
    assert _ncalls(calls) == 1


def test_unstamped_existing_model_is_moved_aside_and_redownloaded(env):
    root, models, calls = env
    (models / "m.dxnn").write_text("OLD")
    assert _run(root).returncode == 0
    assert (models / ".stale" / "m.dxnn").read_text() == "OLD"
    assert (models / "m.dxnn").read_text() == "NEW"
    assert _ncalls(calls) == 1


def test_matching_stamp_keeps_models(env):
    root, models, calls = env
    (models / "m.dxnn").write_text("KEEP")
    (models / ".model_source").write_text(SOURCE + "\n")
    assert _run(root).returncode == 0
    assert (models / "m.dxnn").read_text() == "KEEP"
    assert _ncalls(calls) == 0
