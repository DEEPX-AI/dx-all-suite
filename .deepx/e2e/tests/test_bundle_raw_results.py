import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # .deepx/e2e on path
import bundle_raw_results as brr


def _make_fake_results(tmp_path: Path):
    suite_root = tmp_path / "suite"
    sess = suite_root / "dx-runtime" / "dx_app" / "dx-agent-dev" / "20260612-000000_x"
    sess.mkdir(parents=True)
    (sess / "demo_sync.py").write_text("print('hi')\n")
    (sess / "model.dxnn").write_bytes(b"\x00" * 1024)        # large — must be excluded
    (sess / "venv").mkdir()
    (sess / "venv" / "pyvenv.cfg").write_text("home = x\n")  # excluded dir
    run_dir = suite_root / "dx-agent-dev" / "e2e-tests" / "results" / "RID"
    auto = run_dir / "ts_hash_claude-code-autopilot"
    auto.mkdir(parents=True)
    (auto / "session.log").write_text("ran\n")
    (auto / "claude-code__dx_app").symlink_to(sess)
    manifest = {
        "session_id": "RID",
        "artifacts": {
            "claude-code__dx_app": {
                "path": str(sess),
                "relative_path": str(sess.relative_to(suite_root)),
                "contents": [{"name": "demo_sync.py", "type": "file"}],
            }
        },
    }
    (auto / "manifest.json").write_text(json.dumps(manifest))
    return run_dir, suite_root


def test_bundle_is_self_contained_and_excludes_large(tmp_path):
    run_dir, suite_root = _make_fake_results(tmp_path)
    out = tmp_path / "bundle"
    report = brr.bundle(run_dir, out, suite_root=suite_root)

    auto_out = out / "results" / "ts_hash_claude-code-autopilot"
    assert (auto_out / "session.log").read_text() == "ran\n"
    gathered = out / "suite" / "dx-runtime/dx_app/dx-agent-dev/20260612-000000_x" / "demo_sync.py"
    assert gathered.is_file() and not gathered.is_symlink()
    assert gathered.read_text() == "print('hi')\n"
    assert not (out / "suite" / "dx-runtime/dx_app/dx-agent-dev/20260612-000000_x" / "model.dxnn").exists()
    assert not (out / "suite" / "dx-runtime/dx_app/dx-agent-dev/20260612-000000_x" / "venv").exists()
    dangling = [p for p in out.rglob("*") if p.is_symlink() and not p.exists()]
    assert dangling == [], f"dangling symlinks: {dangling}"
    mf = json.loads((auto_out / "manifest.json").read_text())
    assert mf["artifacts"]["claude-code__dx_app"]["path"] == "suite/dx-runtime/dx_app/dx-agent-dev/20260612-000000_x"
    assert any("model.dxnn" in e for e in report["excluded"])
