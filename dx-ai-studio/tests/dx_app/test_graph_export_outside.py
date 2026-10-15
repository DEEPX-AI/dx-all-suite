"""scripts/check_graph_export.py: a Graph Composer export built and run outside the suite (spec §12, §14).

The helpers run everywhere. The check itself builds an exported project on /dev/shm (DX_GRAPH_EXPORT_BUILD=1, about a
minute) and, with DX_GRAPH_NPU=1, runs it on the NPU and compares it with Studio's own run.
"""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

import pytest

from scripts import check_graph_export as check
from shared.paths import SUITE_ROOT


def test_leaks_names_each_text_file_that_holds_the_path(tmp_path):
    (tmp_path / "a.txt").write_text("cd /suite/x\n")
    (tmp_path / "m.dxnn").write_bytes(b"/suite/ inside a model is not a leak")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.md").write_text("clean\n")
    assert check.leaks(tmp_path, "/suite") == ["a.txt"]


def test_unzip_keeps_modes_and_refuses_an_entry_outside_its_folder(tmp_path):
    good = tmp_path / "p.zip"
    with zipfile.ZipFile(good, "w") as z:
        info = zipfile.ZipInfo("p/run.sh")
        info.external_attr = 0o755 << 16
        z.writestr(info, "echo hi\n")
    check.unzip(good, tmp_path / "out")
    assert os.access(tmp_path / "out" / "p" / "run.sh", os.X_OK)
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("../evil.sh", "x")
    with pytest.raises(check.Failed):
        check.unzip(bad, tmp_path / "out2")


def test_the_work_folder_must_be_outside_the_suite(capsys):
    assert check.outside_suite(Path("/dev/shm/gc-export-check"))
    assert not check.outside_suite(SUITE_ROOT / "dx-ai-studio" / "outputs")
    assert check.main(["--work", str(SUITE_ROOT / "tmp-export-check")]) == 1
    assert "RESULT: FAIL" in capsys.readouterr().out


def test_the_check_graph_puts_a_user_block_between_the_filter_and_the_zone():
    nodes = {n["id"]: n for n in check.CHECK_GRAPH["nodes"]}
    assert nodes["tag"]["op"] == "user" and nodes["tag"]["params"]["input"] == "boxes"
    assert {"from": "person", "to": "tag", "carry": "result"} in check.CHECK_GRAPH["edges"]
    assert {"from": "tag", "to": "zone", "carry": "result"} in check.CHECK_GRAPH["edges"]


@pytest.mark.requires_dx_runtime
@pytest.mark.skipif(os.environ.get("DX_GRAPH_EXPORT_BUILD") != "1" and os.environ.get("DX_GRAPH_NPU") != "1",
                    reason="builds an exported project; set DX_GRAPH_EXPORT_BUILD=1 (DX_GRAPH_NPU=1 also runs it)")
def test_an_export_builds_and_runs_outside_the_suite(capsys):
    args = ["--work", "/dev/shm/gc-export-check-pytest"] + (["--npu"] if os.environ.get("DX_GRAPH_NPU") == "1" else [])
    code = check.main(args)
    out = capsys.readouterr().out
    if "RESULT: SKIP" in out:
        pytest.skip(out.strip().splitlines()[-1])
    assert code == 0 and "RESULT: PASS" in out, out
    assert not Path("/dev/shm/gc-export-check-pytest").exists()
