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


def test_the_work_folder_is_never_above_the_suite_or_someone_elses(tmp_path, capsys):
    """The check removes its work folder: it may be neither the suite's parent nor a folder it did not make."""
    assert not check.outside_suite(SUITE_ROOT.parent) and not check.outside_suite(Path("/"))
    assert check.main(["--work", str(SUITE_ROOT.parent)]) == 1
    theirs = tmp_path / "theirs"
    theirs.mkdir()
    (theirs / "keep.txt").write_text("not the check's")
    assert check.main(["--work", str(theirs)]) == 1
    assert (theirs / "keep.txt").is_file() and "RESULT: FAIL" in capsys.readouterr().out


def test_a_crash_in_a_step_still_ends_in_a_result_line(capsys):
    def boom():
        raise FileNotFoundError("results/events.jsonl")
    with pytest.raises(check.Failed):
        check._step("compare", boom)
    assert "FAIL compare: results/events.jsonl" in capsys.readouterr().out


def test_leaks_reads_both_spellings_of_a_linked_suite(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    (tmp_path / "p").mkdir()
    (tmp_path / "p" / "a.txt").write_text("cd {}/x\n".format(real))
    assert check.leaks_of(tmp_path / "p", link) == ["a.txt"]


def test_the_studio_run_uses_the_executor_run_sh_uses():
    """run.sh with no options runs the async executor (cli::ProjectArgs); Studio's run must too."""
    import inspect
    assert 'variant="async"' in inspect.getsource(check.compare_step)
