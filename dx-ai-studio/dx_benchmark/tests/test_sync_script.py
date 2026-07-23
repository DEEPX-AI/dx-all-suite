import subprocess, os, json, pathlib, tempfile, shutil
SCRIPT = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "sync_from_standalone.sh"

def test_missing_source_fails():
    r = subprocess.run([str(SCRIPT), "/nonexistent/path"], capture_output=True, text=True)
    assert r.returncode != 0
    assert "not found" in (r.stderr + r.stdout).lower()

def test_copies_snapshot(tmp_path):
    src = tmp_path / "dx-benchmark"; (src / "results" / "HW/RUN").mkdir(parents=True)
    (src / "results" / "HW/RUN" / "environment.json").write_text("{}")
    (src / "results" / "dashboard").mkdir(parents=True)
    (src / "results" / "dashboard" / "dataset.json").write_text('{"dataset_version":"v2"}')
    dest = tmp_path / "studio_bench"; (dest / "scripts").mkdir(parents=True)
    shutil.copy(SCRIPT, dest / "scripts" / "sync_from_standalone.sh")
    r = subprocess.run([str(dest/"scripts"/"sync_from_standalone.sh"), str(src)], capture_output=True, text=True, cwd=dest)
    assert r.returncode == 0, r.stderr
    assert json.loads((dest/"dataset.json").read_text())["dataset_version"] == "v2"
    assert (dest/"results"/"HW"/"RUN"/"environment.json").exists()
    assert not (dest/"results"/"dashboard").exists()
