# SPDX-License-Identifier: Apache-2.0
"""
Tests for `.deepx/templates/assets/harness_bootstrap.sh` — the standalone
sub-repo harness bootstrap.

A standalone sub-repo clone (dx_app, dx_stream, dx-runtime, dx-compiler) has
no `.deepx/tools/` (the generator), no `.deepx/templates/fragments/` and no
`.deepx/tests/`, yet its generated CLAUDE.md/AGENTS.md instruct the agent to
run `dx-agent-gen generate|check` and the conformance suite. The commands all
fail, so the agent either skips verification (committing drift) or — worse —
follows the generator's current "define the variable in
_build_template_context() or fix the template/fragment name" message and
starts mutating templates.

This script closes that gap: it resolves a real dx-all-suite checkout
(explicit override -> parent-walk -> local cache -> shallow clone) into a
git-ignored `.dx-harness/`, then delegates to the already-proven
`subrepo_check.sh`. When no suite can be acquired it exits 3 (HARD GATE)
rather than letting unverified `.deepx/` edits proceed.

Scope note: `--check` deliberately runs the SAME scope as the CI
`subrepo-gate` (drift check + that repo's validate_framework.py) and NOT the
suite conformance suite, whose ~600 checks are cross-level and cannot be
satisfied when the other sub-repos are absent.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


def _find_suite_root(start: Path) -> Path:
    """Walk up looking for the dx-all-suite marker rather than assuming a
    fixed nesting depth (M8)."""
    current = start.resolve()
    marker = Path(".deepx") / "tools" / "src" / "dx_agent_dev_gen" / "cli.py"
    for _ in range(10):
        if (current / marker).is_file():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise RuntimeError(f"could not locate dx-all-suite root above {start}")


SUITE_ROOT = _find_suite_root(Path(__file__).parent)
SCRIPT = SUITE_ROOT / ".deepx" / "templates" / "assets" / "harness_bootstrap.sh"

SUBREPO_RELPATHS = [
    "dx-compiler",
    "dx-runtime",
    "dx-runtime/dx_app",
    "dx-runtime/dx_stream",
]


def deployed_bootstrap(repo_dir: Path) -> Path:
    """The generator-deployed copy inside a sub-repo.

    The script derives REPO_DIR from its own location
    (`<repo>/.deepx/scripts` -> `<repo>`), so it must be exercised from that
    deployed path, never from the canonical asset path — otherwise REPO_DIR
    resolves to the suite itself.

    Do NOT substitute the canonical asset here: the deployed copy carries the
    generated header, so overwriting it with the raw asset makes the drift
    check report CHANGED (which is the passthrough working as intended)."""
    dst = repo_dir / ".deepx" / "scripts" / "harness_bootstrap.sh"
    if not dst.is_file():
        pytest.skip(
            "harness_bootstrap.sh not deployed yet — run "
            "`bash .deepx/tools/scripts/run_all.sh generate`"
        )
    return dst


def run_script(script: Path, args, extra_env=None, timeout=300):
    """Invoke the deployed bootstrap, with DX_SUITE_DIR scrubbed so a
    developer's ambient override never masks a resolution bug."""
    env = dict(os.environ)
    env.pop("DX_SUITE_DIR", None)
    env.pop("DX_HARNESS_NO_CLONE", None)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(script), *args],
        cwd=str(script.parent),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _copy_dx_app(dst: Path) -> Path:
    src = SUITE_ROOT / "dx-runtime" / "dx_app"
    if not (src / ".deepx").is_dir():
        pytest.skip("dx_app submodule not initialised")
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src, dst, symlinks=True, ignore=shutil.ignore_patterns(".git")
    )
    return dst


@pytest.fixture
def standalone_dx_app(tmp_path):
    """A dx_app working tree with NO suite anywhere above it — the exact
    situation of `git clone dx_app && cd dx_app`."""
    repo = _copy_dx_app(tmp_path / "solo" / "dx_app")
    deployed_bootstrap(repo)   # skip early if the asset has not been generated
    return repo


@pytest.fixture
def nested_dx_app(tmp_path):
    """A dx_app sitting at its canonical path under a suite, so the parent-walk
    branch is exercised without touching the real working tree. `is_suite()`
    only requires the fragments dir plus the generator entry point, so a marker
    tree is a faithful stand-in."""
    suite = tmp_path / "fakesuite"
    (suite / ".deepx" / "templates" / "fragments").mkdir(parents=True)
    gen = suite / ".deepx" / "tools" / "src" / "dx_agent_dev_gen"
    gen.mkdir(parents=True)
    (gen / "cli.py").write_text("# marker\n", encoding="utf-8")
    repo = _copy_dx_app(suite / "dx-runtime" / "dx_app")
    deployed_bootstrap(repo)
    return suite, repo


def test_asset_exists_and_is_syntactically_valid():
    assert SCRIPT.is_file(), f"missing asset: {SCRIPT}"
    proc = subprocess.run(
        ["bash", "-n", str(SCRIPT)], capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr


def test_resolves_local_suite_by_parent_walk(nested_dx_app):
    """A sub-repo nested under a suite resolves by walking up — source must be
    'local', and nothing is cloned or cached."""
    suite, repo = nested_dx_app
    script = deployed_bootstrap(repo)
    proc = run_script(script, ["--print-suite-dir"],
                      extra_env={"DX_HARNESS_NO_CLONE": "1"})
    assert proc.returncode == 0, proc.stderr
    resolved, _, source = proc.stdout.strip().partition("\t")
    assert Path(resolved).resolve() == suite.resolve()
    assert source == "local"
    assert not (repo / ".dx-harness" / "suite").exists()


def test_explicit_suite_dir_wins_from_a_standalone_checkout(standalone_dx_app):
    script = deployed_bootstrap(standalone_dx_app)
    proc = run_script(
        script, ["--print-suite-dir", "--suite-dir", str(SUITE_ROOT)]
    )
    assert proc.returncode == 0, proc.stderr
    resolved, _, source = proc.stdout.strip().partition("\t")
    assert Path(resolved).resolve() == SUITE_ROOT.resolve()
    assert source == "explicit"


def test_env_var_suite_dir_is_honoured(standalone_dx_app):
    script = deployed_bootstrap(standalone_dx_app)
    proc = run_script(
        script, ["--print-suite-dir"],
        extra_env={"DX_SUITE_DIR": str(SUITE_ROOT)},
    )
    assert proc.returncode == 0, proc.stderr
    assert str(SUITE_ROOT) in proc.stdout


def test_offline_with_no_suite_exits_3_and_explains(standalone_dx_app):
    """No parent suite, no cache, cloning disabled -> HARD GATE stop."""
    script = deployed_bootstrap(standalone_dx_app)
    proc = run_script(script, ["--print-suite-dir"],
                      extra_env={"DX_HARNESS_NO_CLONE": "1"})
    assert proc.returncode == 3, (
        f"expected exit 3, got {proc.returncode}\n{proc.stdout}{proc.stderr}"
    )
    out = proc.stdout + proc.stderr
    assert "HARNESS BOOTSTRAP FAILED" in out
    # the message must name both escape hatches...
    assert "--suite-dir" in out
    assert "DX_SUITE_DIR" in out
    # ...and must steer away from the mistake the old diagnostic invited
    assert "FRAGMENT" in out


def test_stop_path_does_not_create_a_cache_dir(standalone_dx_app):
    """A failed acquisition must not leave a half-built .dx-harness behind."""
    script = deployed_bootstrap(standalone_dx_app)
    run_script(script, ["--print-suite-dir"],
               extra_env={"DX_HARNESS_NO_CLONE": "1"})
    leftover = standalone_dx_app / ".dx-harness" / "suite"
    assert not leftover.exists(), "STOP path left a suite cache behind"


def test_records_state_json_on_success(standalone_dx_app):
    import json

    script = deployed_bootstrap(standalone_dx_app)
    proc = run_script(
        script, ["--print-suite-dir", "--suite-dir", str(SUITE_ROOT)]
    )
    assert proc.returncode == 0, proc.stderr
    state = standalone_dx_app / ".dx-harness" / "state.json"
    assert state.is_file(), "state.json not written"
    data = json.loads(state.read_text(encoding="utf-8"))
    assert data["source"] == "explicit"
    assert data["subrepo_path"] == "dx-runtime/dx_app"


def test_infers_canonical_subrepo_path(standalone_dx_app):
    script = deployed_bootstrap(standalone_dx_app)
    proc = run_script(script, ["--suite-dir", str(SUITE_ROOT)])
    assert proc.returncode == 0, proc.stderr
    assert "dx-runtime/dx_app" in proc.stdout


def test_check_runs_the_ci_identical_verification(standalone_dx_app):
    """--check must chain into the suite's subrepo_check.sh and pass on a
    clean copy — the same scope CI's subrepo-gate runs."""
    script = deployed_bootstrap(standalone_dx_app)
    proc = run_script(
        script, ["--check", "--suite-dir", str(SUITE_ROOT)], timeout=900
    )
    out = proc.stdout + proc.stderr
    assert proc.returncode == 0, out
    assert "All generated files are up-to-date." in out


@pytest.mark.parametrize("relpath", SUBREPO_RELPATHS)
def test_cache_dir_is_gitignored_in_every_subrepo(relpath):
    """`.dx-harness/` must never reach the index of any sub-repo."""
    gitignore = SUITE_ROOT / relpath / ".gitignore"
    if not (SUITE_ROOT / relpath / ".deepx").is_dir():
        pytest.skip(f"{relpath} submodule not initialised")
    assert gitignore.is_file(), f"no .gitignore in {relpath}"
    assert ".dx-harness/" in gitignore.read_text(encoding="utf-8"), (
        f".dx-harness/ is not git-ignored in {relpath}"
    )


# ── PR #91 review r18833: a silent clone skip is indistinguishable from "no suite" ──

def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True, text=True)


def test_clone_step_explains_why_no_suite_url_could_be_derived(standalone_dx_app):
    """origin already ends in dx-all-suite (or is missing): the sed rewrite yields the same
    url, so the clone is skipped — the script must SAY so instead of falling through to the
    generic exit 3. Cloning is left enabled on purpose; nothing must be fetched."""
    script = deployed_bootstrap(standalone_dx_app)
    _git(standalone_dx_app, "init", "-q")
    _git(standalone_dx_app, "remote", "add", "origin", "file:///nowhere/dx-all-suite.git")
    proc = run_script(script, ["--print-suite-dir"])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 3, out
    assert "cannot derive a suite url" in out and "file:///nowhere/dx-all-suite.git" in out, out
    assert "HARNESS BOOTSTRAP FAILED" in out


def test_clone_step_explains_a_missing_origin(standalone_dx_app):
    script = deployed_bootstrap(standalone_dx_app)
    _git(standalone_dx_app, "init", "-q")          # a repo, but no origin at all
    proc = run_script(script, ["--print-suite-dir"])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 3, out
    assert "no remote.origin.url" in out, out


def test_clone_url_keeps_the_git_suffix_of_origin(standalone_dx_app):
    """`…/dx_app.git` must derive `…/dx-all-suite.git` (the old sed dropped the suffix)."""
    script = deployed_bootstrap(standalone_dx_app)
    _git(standalone_dx_app, "init", "-q")
    _git(standalone_dx_app, "remote", "add", "origin", "file:///nowhere/dx_app.git")
    proc = run_script(script, ["--print-suite-dir"])
    out = proc.stdout + proc.stderr
    assert proc.returncode == 3, out
    assert "acquiring: file:///nowhere/dx-all-suite.git" in out, out
