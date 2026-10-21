"""Provenance fields recorded at measurement time: model sha256 and tool commit."""
import hashlib
import subprocess

from benchmark import env_fingerprint as ef


def test_model_metadata_includes_sha256(tmp_path, monkeypatch):
    f = tmp_path / "m.dxnn"
    f.write_bytes(b"abc")
    monkeypatch.setattr(ef, "_run", lambda *a, **k: ".dxnn Format Version : v9\nDX-COM Version : v2.5.0")
    meta = ef.collect_model_metadata(f)
    assert meta["dxcom_version"] == "v2.5.0"
    assert meta["sha256"] == hashlib.sha256(b"abc").hexdigest()


def _git(cwd, *args):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True,
                   env={"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
                        "PATH": __import__("os").environ["PATH"], "HOME": str(cwd)})


def test_tool_commit_clean_dirty_and_non_git(tmp_path):
    assert ef.get_tool_commit(tmp_path) is None            # not a git repo
    _git(tmp_path, "init", "-q")
    (tmp_path / "a.py").write_text("1")
    _git(tmp_path, "add", "a.py")
    _git(tmp_path, "commit", "-q", "-m", "c")
    sha = ef.get_tool_commit(tmp_path)
    assert sha and not sha.endswith("-dirty")
    (tmp_path / "untracked.txt").write_text("x")           # untracked must not count
    assert ef.get_tool_commit(tmp_path) == sha
    (tmp_path / "a.py").write_text("2")                    # tracked change => dirty
    assert ef.get_tool_commit(tmp_path) == sha + "-dirty"
