# SPDX-License-Identifier: Apache-2.0
"""
Tests for `.deepx/tools/scripts/subrepo_check.sh` — the sub-repo standalone
drift gate (Phase 2, Task 1).

A sub-repo alone (dx-compiler, dx-runtime, dx-runtime/dx_app,
dx-runtime/dx_stream) cannot run `dx-agent-gen check` on itself: the
generator and the shared fragments live only in dx-all-suite, and
`Generator._find_fragments_dir()` only walks up parent directories looking
for `.deepx/templates/fragments` — it does not know how to fetch them. This
script places a copy of the sub-repo at its canonical nested position inside
a (real or freshly cloned) suite tree and runs the check there.

NOTE on the ambient submodule working trees under $SUITE: at the time these
tests were written, `git status --short` on dx-compiler/dx-runtime/dx_app/
dx_stream shows uncommitted generated-file changes (the committed HEAD is
stale relative to the current .deepx/ templates, but the working tree is
up-to-date). This means "archive mode" (committed HEAD) is NOT clean for
these ambient repos right now — only "worktree mode" (uncommitted-inclusive)
is. Tests that check the ambient sub-repos for cleanliness therefore pass
`--mode worktree` explicitly; tests that build their own isolated throwaway
git repos (commit-and-check) exercise the default `archive` mode.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest


def _find_suite_root(start: Path) -> Path:
    """Walk up from *start* looking for the dx-all-suite marker file, rather
    than assuming a fixed nesting depth (M8) — this test file's own depth
    under .deepx/tools/tests/ is an implementation detail, not a contract."""
    current = start.resolve()
    marker = Path(".deepx") / "tools" / "src" / "dx_agent_dev_gen" / "cli.py"
    for _ in range(10):
        if (current / marker).is_file():
            return current
        parent = current.parent
        if parent == current:
            break
        current = parent
    raise RuntimeError(
        f"could not locate dx-all-suite root above {start} "
        f"(looked for {marker})"
    )


SUITE_ROOT = _find_suite_root(Path(__file__).parent)
SCRIPT = SUITE_ROOT / ".deepx" / "tools" / "scripts" / "subrepo_check.sh"

SUBREPO_PATHS = [
    "dx-compiler",
    "dx-runtime",
    "dx-runtime/dx_app",
    "dx-runtime/dx_stream",
]


def run_script(*args: str, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPT), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def combined(result: subprocess.CompletedProcess) -> str:
    return result.stdout + result.stderr


def _git(*args: str, cwd: Path) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def _make_isolated_repo(tmp_path: Path, name: str, source: Path) -> Path:
    """Copy *source*'s WORKING TREE (not HEAD — the ambient submodule's committed
    HEAD is stale relative to the current .deepx/ templates, see module docstring)
    into a fresh standalone git repo under tmp_path, so the initial commit is
    clean/up-to-date against the current suite fragments."""
    dest = tmp_path / name
    dest.mkdir(parents=True)
    # List-based invocation (M8): the paths are passed as bash positional
    # params ($1/$2), never interpolated into the shell script text itself.
    subprocess.run(
        ["bash", "-c", 'tar -C "$1" --exclude=.git -cf - . | tar -xf - -C "$2"',
         "bash", str(source), str(dest)],
        check=True,
        capture_output=True,
        text=True,
    )
    _git("init", "-q", cwd=dest)
    _git("config", "user.email", "test@example.com", cwd=dest)
    _git("config", "user.name", "Test", cwd=dest)
    _git("add", "-A", cwd=dest)
    _git("commit", "-q", "-m", "initial", cwd=dest)
    return dest


class TestBashSyntax:
    def test_bash_syntax(self):
        proc = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        assert proc.returncode == 0, proc.stderr


class TestBadSubrepoPath:
    def test_bad_subrepo_path_exits_2(self, tmp_path):
        result = run_script(
            "--subrepo-path",
            "not-a-real-subrepo",
            "--repo-dir",
            str(SUITE_ROOT / "dx-compiler"),
            "--suite-dir",
            str(SUITE_ROOT),
            "--work",
            str(tmp_path / "work"),
        )
        assert result.returncode == 2, combined(result)


class TestSuiteUrlDerivation:
    @pytest.mark.parametrize(
        "origin,expected",
        [
            ("git@github.com:org/dx_app.git", "git@github.com:org/dx-all-suite.git"),
            ("https://h/o/dx_app.git", "https://h/o/dx-all-suite.git"),
        ],
    )
    def test_suite_url_derivation(self, tmp_path, origin, expected):
        repo = tmp_path / "repo"
        repo.mkdir()
        _git("init", "-q", cwd=repo)
        _git("remote", "add", "origin", origin, cwd=repo)
        result = run_script(
            "--print-suite-url",
            "--repo-dir",
            str(repo),
        )
        assert result.returncode == 0, combined(result)
        assert result.stdout.strip() == expected, combined(result)

    def test_derivation_uses_the_raw_origin_url_not_an_insteadof_rewrite(self, tmp_path):
        """GHES runners carry `url.https://github.com/.insteadOf git@github.com:` (credential
        manager / CI image), so `git remote get-url` returns the REWRITTEN url and the derived
        suite url silently changed scheme (run 1751). Derive from the configured value."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _git("init", "-q", cwd=repo)
        _git("remote", "add", "origin", "git@github.com:org/dx_app.git", cwd=repo)
        _git("config", "url.https://github.com/.insteadOf", "git@github.com:", cwd=repo)
        result = run_script("--print-suite-url", "--repo-dir", str(repo))
        assert result.returncode == 0, combined(result)
        assert result.stdout.strip() == "git@github.com:org/dx-all-suite.git", combined(result)


class TestAllFourSubreposCleanWithSuiteDir:
    @pytest.mark.parametrize("subrepo_path", SUBREPO_PATHS)
    def test_all_four_subrepos_clean_with_suite_dir(self, tmp_path, subrepo_path):
        result = run_script(
            "--suite-dir",
            str(SUITE_ROOT),
            "--repo-dir",
            str(SUITE_ROOT / subrepo_path),
            "--subrepo-path",
            subrepo_path,
            "--mode",
            "worktree",
            "--work",
            str(tmp_path / "work"),
        )
        assert result.returncode == 0, combined(result)
        assert "up-to-date" in result.stdout, combined(result)


class TestDriftIsDetected:
    def test_drift_is_detected(self, tmp_path):
        repo = _make_isolated_repo(tmp_path, "dx-compiler-copy", SUITE_ROOT / "dx-compiler")
        claude_md = repo / "CLAUDE.md"
        claude_md.write_text(claude_md.read_text(encoding="utf-8") + "\nDRIFTED LINE\n", encoding="utf-8")
        _git("add", "-A", cwd=repo)
        _git("commit", "-q", "-m", "drift", cwd=repo)

        result = run_script(
            "--suite-dir",
            str(SUITE_ROOT),
            "--repo-dir",
            str(repo),
            "--subrepo-path",
            "dx-compiler",
            "--work",
            str(tmp_path / "work"),
        )
        assert result.returncode == 1, combined(result)
        assert "CHANGED: CLAUDE.md" in result.stdout, combined(result)
        assert "run_all.sh generate" in combined(result)


class TestWorktreeModeSeesUncommittedChanges:
    def test_worktree_mode_sees_uncommitted_changes(self, tmp_path):
        repo = _make_isolated_repo(tmp_path, "dx-compiler-copy2", SUITE_ROOT / "dx-compiler")
        claude_md = repo / "CLAUDE.md"
        claude_md.write_text(claude_md.read_text(encoding="utf-8") + "\nUNCOMMITTED DRIFT\n", encoding="utf-8")
        # deliberately NOT committed

        result_archive = run_script(
            "--suite-dir",
            str(SUITE_ROOT),
            "--repo-dir",
            str(repo),
            "--subrepo-path",
            "dx-compiler",
            "--mode",
            "archive",
            "--work",
            str(tmp_path / "work-archive"),
        )
        assert result_archive.returncode == 0, combined(result_archive)

        result_worktree = run_script(
            "--suite-dir",
            str(SUITE_ROOT),
            "--repo-dir",
            str(repo),
            "--subrepo-path",
            "dx-compiler",
            "--mode",
            "worktree",
            "--work",
            str(tmp_path / "work-worktree"),
        )
        assert result_worktree.returncode == 1, combined(result_worktree)
        assert "CHANGED: CLAUDE.md" in result_worktree.stdout, combined(result_worktree)


def _build_fake_bare_suite(tmp_path: Path) -> Path:
    """Build a minimal fake suite (.deepx/tools/src + .deepx/templates copied
    from the real suite) on branch "main", plus a "feat-x" branch, then clone
    it --bare so it can be pulled via a file:// --suite-url. Returns the bare
    repo path."""
    fake_suite = tmp_path / "fake_suite"
    fake_suite.mkdir()
    (fake_suite / ".deepx" / "tools").mkdir(parents=True)
    (fake_suite / ".deepx" / "templates").mkdir(parents=True)
    shutil.copytree(SUITE_ROOT / ".deepx" / "tools" / "src", fake_suite / ".deepx" / "tools" / "src")
    for entry in (SUITE_ROOT / ".deepx" / "templates").iterdir():
        if entry.is_dir():
            shutil.copytree(entry, fake_suite / ".deepx" / "templates" / entry.name)
        else:
            shutil.copy2(entry, fake_suite / ".deepx" / "templates" / entry.name)

    _git("init", "-q", cwd=fake_suite)
    _git("symbolic-ref", "HEAD", "refs/heads/main", cwd=fake_suite)   # `init -b` needs git >= 2.28; GHES runners have 2.25
    _git("config", "user.email", "test@example.com", cwd=fake_suite)
    _git("config", "user.name", "Test", cwd=fake_suite)
    _git("add", "-A", cwd=fake_suite)
    _git("commit", "-q", "-m", "initial", cwd=fake_suite)
    _git("branch", "feat-x", cwd=fake_suite)
    # add a trivial extra commit on feat-x so it's distinguishable
    _git("checkout", "-q", "feat-x", cwd=fake_suite)
    (fake_suite / "MARKER.txt").write_text("feat-x\n", encoding="utf-8")
    _git("add", "-A", cwd=fake_suite)
    _git("commit", "-q", "-m", "feat-x marker", cwd=fake_suite)
    _git("checkout", "-q", "main", cwd=fake_suite)

    bare = tmp_path / "suite.git"
    _git("clone", "-q", "--bare", str(fake_suite), str(bare), cwd=tmp_path)
    _git("symbolic-ref", "HEAD", "refs/heads/main", cwd=bare)
    return bare


class TestClonePathSameNameBranchAndFallback:
    def test_clone_path_same_name_branch_and_fallback(self, tmp_path):
        bare = _build_fake_bare_suite(tmp_path)

        # Use the real dx-compiler working tree (clean against these fragments,
        # since the fake suite's fragments were freshly copied from the same
        # source that produced dx-compiler's current, up-to-date working tree).
        result_named_branch = run_script(
            "--subrepo-path",
            "dx-compiler",
            "--repo-dir",
            str(SUITE_ROOT / "dx-compiler"),
            "--suite-url",
            f"file://{bare}",
            "--suite-ref",
            "feat-x",
            "--mode",
            "worktree",
            "--work",
            str(tmp_path / "work-named"),
        )
        assert "suite ref: feat-x" in combined(result_named_branch), combined(result_named_branch)
        assert result_named_branch.returncode == 0, combined(result_named_branch)

        result_fallback = run_script(
            "--subrepo-path",
            "dx-compiler",
            "--repo-dir",
            str(SUITE_ROOT / "dx-compiler"),
            "--suite-url",
            f"file://{bare}",
            "--suite-ref",
            "nope",
            "--mode",
            "worktree",
            "--work",
            str(tmp_path / "work-fallback"),
        )
        assert "suite ref: main (fallback from nope)" in combined(result_fallback), combined(result_fallback)
        assert result_fallback.returncode == 0, combined(result_fallback)


class TestWorkReuseNeverWritesIntoRealSuite:
    """C1 regression: a stale `.deepx` symlink from a PRIOR run at the same
    --work path must never cause the next run's `ln -s` to resolve through
    it and land a new symlink inside the REAL suite's .deepx tree."""

    def test_work_reuse_twice_no_dotdeepx_leak(self, tmp_path):
        real_leak_marker = SUITE_ROOT / ".deepx" / ".deepx"
        assert not real_leak_marker.exists(), (
            "pre-existing .deepx/.deepx before this test even ran — "
            "environment already corrupted by an earlier bug"
        )

        work = tmp_path / "reused-work"
        for _ in range(2):
            result = run_script(
                "--suite-dir",
                str(SUITE_ROOT),
                "--repo-dir",
                str(SUITE_ROOT / "dx-compiler"),
                "--subrepo-path",
                "dx-compiler",
                "--mode",
                "worktree",
                "--work",
                str(work),
                "--keep",
            )
            assert result.returncode == 0, combined(result)
            assert not real_leak_marker.exists(), combined(result)


class TestWorkPathWithQuoteAndSpace:
    def test_work_path_with_quote_and_space(self, tmp_path):
        work = tmp_path / "it's a dir"
        result = run_script(
            "--suite-dir",
            str(SUITE_ROOT),
            "--repo-dir",
            str(SUITE_ROOT / "dx-compiler"),
            "--subrepo-path",
            "dx-compiler",
            "--mode",
            "worktree",
            "--work",
            str(work),
        )
        assert result.returncode == 0, combined(result)


class TestSetupErrorsExit2:
    def test_unreachable_suite_url_exits_2_with_message(self, tmp_path):
        result = run_script(
            "--subrepo-path",
            "dx-compiler",
            "--repo-dir",
            str(SUITE_ROOT / "dx-compiler"),
            "--suite-url",
            "file:///nonexistent-suite-repo-xyz.git",
            "--work",
            str(tmp_path / "work"),
        )
        assert result.returncode == 2, combined(result)
        assert "cannot reach" in combined(result).lower(), combined(result)

    def test_suite_dir_lacking_fragments_exits_2(self, tmp_path):
        fake_suite = tmp_path / "fake_suite_no_fragments"
        cli_stub = fake_suite / ".deepx" / "tools" / "src" / "dx_agent_dev_gen" / "cli.py"
        cli_stub.parent.mkdir(parents=True)
        cli_stub.write_text("", encoding="utf-8")
        # deliberately no .deepx/templates/fragments

        result = run_script(
            "--suite-dir",
            str(fake_suite),
            "--repo-dir",
            str(SUITE_ROOT / "dx-compiler"),
            "--subrepo-path",
            "dx-compiler",
            "--work",
            str(tmp_path / "work"),
        )
        assert result.returncode == 2, combined(result)
        assert "fragments" in combined(result).lower(), combined(result)

    def test_flag_without_value_exits_2(self, tmp_path):
        result = run_script("--subrepo-path")
        assert result.returncode == 2, combined(result)
        assert "requires a value" in combined(result), combined(result)

    def test_help_exits_0(self):
        result = run_script("--help")
        assert result.returncode == 0, combined(result)
        assert "subrepo_check.sh" in result.stdout, combined(result)

        result_short = run_script("-h")
        assert result_short.returncode == 0, combined(result_short)


class TestValidatorRunsWithNestedCwd:
    def test_validator_stub_reports_nested_cwd(self, tmp_path):
        repo = _make_isolated_repo(tmp_path, "dx-compiler-validator-stub", SUITE_ROOT / "dx-compiler")
        validator = repo / ".deepx" / "scripts" / "validate_framework.py"
        validator.parent.mkdir(parents=True, exist_ok=True)
        validator.write_text(
            "import os\nprint(os.getcwd())\n",
            encoding="utf-8",
        )
        # deliberately NOT committed — --mode worktree picks up the stub.

        work = tmp_path / "work"
        result = run_script(
            "--suite-dir",
            str(SUITE_ROOT),
            "--repo-dir",
            str(repo),
            "--subrepo-path",
            "dx-compiler",
            "--mode",
            "worktree",
            "--work",
            str(work),
            "--keep",
        )
        expected_cwd = str(work / "suite" / "dx-compiler")
        # Match a whole STDOUT line, not a substring: an earlier "copying ...
        # -> $NESTED" log line already contains this same path as a substring,
        # so a bare `in result.stdout` check would pass even if the validator
        # ran with the WRONG cwd (e.g. the script's own invocation directory)
        # and never actually printed its own cwd at all.
        assert expected_cwd in result.stdout.splitlines(), combined(result)


class TestTrapIsExitOnly:
    """bash re-runs an EXIT trap when the process dies from SIGINT/SIGTERM —
    it does not need (and must not have) INT/TERM in the trap's signal list.
    Trapping INT/TERM explicitly makes bash treat the handler's completion as
    "signal handled": execution RESUMES after the trap instead of the process
    dying from the signal, so the script would exit 0 on a run a user (or CI)
    killed with Ctrl-C — a successful-looking exit code for an aborted check.
    `trap cleanup EXIT` alone still fires the cleanup on SIGINT/SIGTERM (that
    is bash's documented EXIT-trap behavior) while preserving the "killed by
    signal" exit status."""

    def test_trap_line_is_exactly_exit(self):
        text = SCRIPT.read_text(encoding="utf-8")
        trap_lines = [
            line.strip() for line in text.splitlines() if line.strip().startswith("trap ")
        ]
        assert trap_lines == ["trap cleanup EXIT"], (
            f"expected exactly one trap line 'trap cleanup EXIT', got {trap_lines!r}"
        )


class TestClonePathReusedWorkDir:
    def test_clone_path_reused_work_dir_twice(self, tmp_path):
        bare = _build_fake_bare_suite(tmp_path)
        work = tmp_path / "reused-clone-work"

        for _ in range(2):
            result = run_script(
                "--subrepo-path",
                "dx-compiler",
                "--repo-dir",
                str(SUITE_ROOT / "dx-compiler"),
                "--suite-url",
                f"file://{bare}",
                "--mode",
                "worktree",
                "--work",
                str(work),
                "--keep",
            )
            assert result.returncode == 0, combined(result)


# ---------------------------------------------------------------------------
# Crash ≠ drift, and a Python-version preflight (GHES run 982, 2026-09-10: the
# generator died at import on a Python 3.8 runner and the script reported
# "Generated files are out of date").
# ---------------------------------------------------------------------------
import os as _os
import shutil as _shutil

_REAL_PYTHON3 = _shutil.which("python3")


def _fake_python3(tmp_path: Path, body: str) -> dict:
    """Install a `python3` shim at the front of PATH. *body* is the bash text
    that runs before falling through to the real interpreter."""
    d = tmp_path / "fakebin"
    d.mkdir()
    shim = d / "python3"
    shim.write_text("#!/usr/bin/env bash\n" + body + f'\nexec "{_REAL_PYTHON3}" "$@"\n')
    shim.chmod(0o755)
    return {**_os.environ, "PATH": f"{d}:{_os.environ['PATH']}"}


def _run_script_env(env: dict, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True, timeout=120, env=env)


class TestGeneratorCrashIsNotDrift:
    def test_traceback_exits_2_and_does_not_claim_drift(self, tmp_path):
        repo = _make_isolated_repo(tmp_path, "dx-compiler-copy", SUITE_ROOT / "dx-compiler")
        env = _fake_python3(
            tmp_path,
            'case "$*" in *dx_agent_dev_gen.cli*)\n'
            '  echo "Traceback (most recent call last):"\n'
            "  echo '  File \"<string>\", line 1, in <module>'\n"
            "  echo \"TypeError: 'type' object is not subscriptable\"\n"
            "  exit 1;;\n"
            "esac",
        )
        result = _run_script_env(
            env,
            "--suite-dir", str(SUITE_ROOT),
            "--repo-dir", str(repo),
            "--subrepo-path", "dx-compiler",
            "--work", str(tmp_path / "work"),
        )
        out = combined(result)
        assert result.returncode == 2, out
        assert "Traceback" in out, out                      # the crash is surfaced
        assert "NOT drift" in out, out                      # ... and named for what it is
        assert "out of date" not in out, out                # never the drift verdict
        assert "run_all.sh generate" not in out, out        # nor the regenerate hint


class TestPythonVersionPreflight:
    def test_python_older_than_3_8_exits_2(self, tmp_path):
        repo = _make_isolated_repo(tmp_path, "dx-compiler-copy", SUITE_ROOT / "dx-compiler")
        env = _fake_python3(
            tmp_path,
            'case "$*" in\n'
            '  *--version*) echo "Python 3.6.9"; exit 0;;\n'
            '  *version_info*) exit 1;;\n'
            "esac",
        )
        result = _run_script_env(
            env,
            "--suite-dir", str(SUITE_ROOT),
            "--repo-dir", str(repo),
            "--subrepo-path", "dx-compiler",
            "--work", str(tmp_path / "work"),
        )
        out = combined(result)
        assert result.returncode == 2, out
        assert ">= 3.8" in out, out
        assert "3.6.9" in out, out
        assert "out of date" not in out, out

    @pytest.mark.parametrize("remote", ["mirror", "ghes"])
    def test_derivation_falls_back_to_the_mirror_or_ghes_remote(self, tmp_path, remote):
        """Dev checkouts follow the naming convention ghes / mirror (no `origin`)."""
        repo = tmp_path / "repo"
        repo.mkdir()
        _git("init", "-q", cwd=repo)
        _git("remote", "add", remote, "https://h/o/dx_app.git", cwd=repo)
        result = run_script("--print-suite-url", "--repo-dir", str(repo))
        assert result.returncode == 0, combined(result)
        assert result.stdout.strip() == "https://h/o/dx-all-suite.git", combined(result)
