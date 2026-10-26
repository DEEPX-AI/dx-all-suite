# SPDX-License-Identifier: Apache-2.0
"""Contract tests for `.deepx/tools/scripts/gate_mode.sh` — decides how the suite
harness gate checks out the sub-repos:

  branch-tip  (default) same-name branch tip, default branch if absent
  pointer     the commits recorded by the suite commit (integration truth)

pointer is chosen automatically when the pushed / PR'd range changed a submodule
gitlink (e.g. update-submodule.yml's `ci(...): Update dx-runtime` commit), or on
workflow_dispatch with --input-mode pointer."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


def _suite_root(start: Path) -> Path:
    cur = start.resolve()
    marker = Path(".deepx") / "tools" / "src" / "dx_agent_dev_gen" / "cli.py"
    for _ in range(10):
        if (cur / marker).is_file():
            return cur
        cur = cur.parent
    raise RuntimeError("suite root not found")


SCRIPT = _suite_root(Path(__file__)) / ".deepx" / "tools" / "scripts" / "gate_mode.sh"


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], check=True, text=True, capture_output=True).stdout.strip()


@pytest.fixture(scope="module")
def repo(tmp_path_factory) -> dict:
    """A: file → B: gitlink `sub` added (pointer change) → C: file edited (no gitlink change)."""
    r = tmp_path_factory.mktemp("gate-mode-repo")
    _git(r, "init", "-q"); _git(r, "symbolic-ref", "HEAD", "refs/heads/main")   # `init -b` needs git >= 2.28; GHES runners have 2.25
    _git(r, "config", "user.email", "t@example.com"); _git(r, "config", "user.name", "t")
    (r / "README.md").write_text("a\n"); _git(r, "add", "README.md"); _git(r, "commit", "-q", "-m", "A")
    a = _git(r, "rev-parse", "HEAD")
    fake_sha = "1" * 40
    _git(r, "update-index", "--add", "--cacheinfo", f"160000,{fake_sha},sub")
    _git(r, "commit", "-q", "-m", "B: bump sub")
    b = _git(r, "rev-parse", "HEAD")
    (r / "README.md").write_text("c\n"); _git(r, "add", "README.md"); _git(r, "commit", "-q", "-m", "C")
    c = _git(r, "rev-parse", "HEAD")
    return {"path": r, "a": a, "b": b, "c": c}


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd, text=True, capture_output=True, timeout=60)


def _kv(out: str) -> dict:
    return dict(l.split("=", 1) for l in out.splitlines() if "=" in l)


def test_script_exists_and_bash_syntax():
    assert SCRIPT.is_file()
    assert subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True).returncode == 0


def test_help():
    r = _run("--help")
    assert r.returncode == 0 and "branch-tip" in r.stdout and "pointer" in r.stdout


def test_gitlink_change_selects_pointer(repo):
    r = _run("--event", "push", "--from", repo["a"], "--to", repo["b"], "--repo", str(repo["path"]))
    assert r.returncode == 0, r.stderr
    kv = _kv(r.stdout)
    assert kv["mode"] == "pointer" and "sub" in kv["reason"]


def test_no_gitlink_change_selects_branch_tip(repo):
    kv = _kv(_run("--event", "pull_request", "--from", repo["b"], "--to", repo["c"], "--repo", str(repo["path"])).stdout)
    assert kv["mode"] == "branch-tip"


def test_range_spanning_a_gitlink_change_selects_pointer(repo):
    kv = _kv(_run("--event", "push", "--from", repo["a"], "--to", repo["c"], "--repo", str(repo["path"])).stdout)
    assert kv["mode"] == "pointer"


@pytest.mark.parametrize("base", ["", "0" * 40])
def test_missing_or_zero_base_defaults_to_branch_tip(repo, base):
    kv = _kv(_run("--event", "push", "--from", base, "--to", repo["c"], "--repo", str(repo["path"])).stdout)
    assert kv["mode"] == "branch-tip" and "no base" in kv["reason"]


def test_unknown_base_defaults_to_branch_tip_with_reason(repo):
    kv = _kv(_run("--event", "push", "--from", "f" * 40, "--to", repo["c"], "--repo", str(repo["path"])).stdout)
    assert kv["mode"] == "branch-tip" and "not available" in kv["reason"]


@pytest.mark.parametrize("m", ["pointer", "branch-tip"])
def test_dispatch_passes_input_through(repo, m):
    kv = _kv(_run("--event", "workflow_dispatch", "--input-mode", m, "--repo", str(repo["path"])).stdout)
    assert kv["mode"] == m and "workflow_dispatch" in kv["reason"]


def test_dispatch_without_input_defaults_to_branch_tip(repo):
    kv = _kv(_run("--event", "workflow_dispatch", "--repo", str(repo["path"])).stdout)
    assert kv["mode"] == "branch-tip"


def test_bad_input_mode_exits_2(repo):
    assert _run("--event", "workflow_dispatch", "--input-mode", "bogus", "--repo", str(repo["path"])).returncode == 2


def test_unknown_flag_exits_2():
    assert _run("--nope").returncode == 2


# ── pull_request: compare against the test merge's FIRST PARENT, not the stale base.sha ──
# 2026-09-23 (PR #91 on GHES): `pull_request.base.sha` is the base tip when the PR was last updated;
# the test merge is built on the CURRENT base tip. Everything main did in between (update-submodule
# bumps) landed in `base.sha..merge` and flipped the mode to pointer although the PR touched no gitlink.

@pytest.fixture(scope="module")
def pr_repo(tmp_path_factory) -> dict:
    """main: A → B (main bumps gitlink `sub`).  feature (from A): F (README only) / G (bumps `sub2`).
    M  = merge(B, F): PR changed no gitlink, main did.   M2 = merge(B, G): the PR bumped a gitlink."""
    r = tmp_path_factory.mktemp("gate-mode-pr")
    _git(r, "init", "-q"); _git(r, "symbolic-ref", "HEAD", "refs/heads/main")
    _git(r, "config", "user.email", "t@example.com"); _git(r, "config", "user.name", "t")
    (r / "README.md").write_text("a\n"); _git(r, "add", "README.md"); _git(r, "commit", "-q", "-m", "A")
    a = _git(r, "rev-parse", "HEAD")
    _git(r, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},sub"); _git(r, "commit", "-q", "-m", "B: main bumps sub")
    b = _git(r, "rev-parse", "HEAD")
    _git(r, "checkout", "-q", "-b", "feature", a)
    (r / "README.md").write_text("f\n"); _git(r, "add", "README.md"); _git(r, "commit", "-q", "-m", "F: docs only")
    _git(r, "checkout", "-q", "-b", "merge1", b); _git(r, "merge", "-q", "--no-ff", "-m", "M", "feature")
    m = _git(r, "rev-parse", "HEAD")
    _git(r, "checkout", "-q", "-b", "feature2", a)
    _git(r, "update-index", "--add", "--cacheinfo", f"160000,{'2' * 40},sub2"); _git(r, "commit", "-q", "-m", "G: PR bumps sub2")
    _git(r, "checkout", "-q", "-b", "merge2", b); _git(r, "merge", "-q", "--no-ff", "-m", "M2", "feature2")
    m2 = _git(r, "rev-parse", "HEAD")
    _git(r, "checkout", "-q", "main")
    return {"path": r, "a": a, "b": b, "m": m, "m2": m2}


def test_pr_ignores_gitlink_bumps_made_by_the_base_since_base_sha(pr_repo):
    """base.sha = A (stale), merge = M whose first parent is B: main bumped `sub`, the PR did not."""
    kv = _kv(_run("--event", "pull_request", "--from", pr_repo["a"], "--to", pr_repo["m"], "--repo", str(pr_repo["path"])).stdout)
    assert kv["mode"] == "branch-tip", kv
    assert "parent" in kv["reason"] and pr_repo["b"][:7] in kv["reason"], kv


def test_pr_that_bumps_a_gitlink_itself_still_selects_pointer(pr_repo):
    kv = _kv(_run("--event", "pull_request", "--from", pr_repo["a"], "--to", pr_repo["m2"], "--repo", str(pr_repo["path"])).stdout)
    assert kv["mode"] == "pointer" and "sub2" in kv["reason"] and "sub " not in kv["reason"] + " ", kv


def test_push_event_still_uses_the_given_range(pr_repo):
    """push has no test merge; before..sha stays authoritative (main's own bump → pointer)."""
    kv = _kv(_run("--event", "push", "--from", pr_repo["a"], "--to", pr_repo["b"], "--repo", str(pr_repo["path"])).stdout)
    assert kv["mode"] == "pointer"


def test_pr_without_a_merge_commit_falls_back_to_the_given_base(repo):
    """--to is a plain commit (single parent): keep the base.sha range, say why."""
    kv = _kv(_run("--event", "pull_request", "--from", repo["a"], "--to", repo["b"], "--repo", str(repo["path"])).stdout)
    assert kv["mode"] == "pointer" and "sub" in kv["reason"]
