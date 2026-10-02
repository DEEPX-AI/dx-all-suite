# SPDX-License-Identifier: Apache-2.0
"""Contract tests for `.deepx/tools/scripts/harness_gate.sh` — the single
entry point the CI gate workflows AND developers use to run the harness gate.
Stages `tests` / `all` are NOT executed here (they would recurse into pytest)."""

from __future__ import annotations

import subprocess
from pathlib import Path


def _suite_root(start: Path) -> Path:
    cur = start.resolve()
    marker = Path(".deepx") / "tools" / "src" / "dx_agent_dev_gen" / "cli.py"
    for _ in range(10):
        if (cur / marker).is_file():
            return cur
        cur = cur.parent
    raise RuntimeError("suite root not found")


SUITE = _suite_root(Path(__file__))
SCRIPT = SUITE / ".deepx" / "tools" / "scripts" / "harness_gate.sh"


def _run(*args: str, cwd: Path = SUITE) -> subprocess.CompletedProcess:
    return subprocess.run(["bash", str(SCRIPT), *args], cwd=cwd, text=True, capture_output=True, timeout=600)


def test_script_exists_and_is_executable():
    assert SCRIPT.is_file()
    assert SCRIPT.stat().st_mode & 0o111, "harness_gate.sh must be executable"


def test_bash_syntax():
    r = subprocess.run(["bash", "-n", str(SCRIPT)], text=True, capture_output=True)
    assert r.returncode == 0, r.stderr


def test_help_exits_zero_and_lists_stages():
    r = _run("--help")
    assert r.returncode == 0
    for stage in ("deps", "check", "lint", "tests", "e2e-sh", "all"):
        assert stage in r.stdout, f"--help must list stage '{stage}'"


def test_unknown_stage_exits_2():
    r = _run("bogus")
    assert r.returncode == 2
    assert "Usage" in (r.stdout + r.stderr)


def test_no_stage_exits_2():
    assert _run().returncode == 2


def test_deps_passes_in_this_environment():
    r = _run("deps")
    assert r.returncode == 0, r.stdout + r.stderr


def test_deps_reports_missing_module_with_hint(tmp_path):
    fake = tmp_path / "python3"
    fake.write_text("#!/usr/bin/env bash\nexit 1\n")
    fake.chmod(0o755)
    r = _run("deps", "--python", str(fake))
    assert r.returncode == 1
    out = r.stdout + r.stderr
    assert "jinja2" in out and "pytest" in out and "rich" in out


def test_check_stage_passes_through_run_all_exit_code():
    """The check stage is a thin wrapper over run_all.sh: same exit code, stage
    header printed. It deliberately does NOT assert the ambient tree is clean —
    in CI the sub-repos may be at stale pointers or uninitialized, which is a
    property of the checkout, not of this script (review finding 2026-09-09)."""
    ref = subprocess.run(["bash", str(SUITE / ".deepx/tools/scripts/run_all.sh"), "check"],
                         cwd=SUITE, text=True, capture_output=True, timeout=600)
    r = _run("check")
    assert r.returncode == ref.returncode, r.stdout + r.stderr
    assert "=== [harness-gate] check ===" in r.stdout
    if ref.returncode == 0:
        assert "All generated files are up-to-date." in r.stdout


def test_lint_stage_passes():
    r = _run("lint")
    assert r.returncode == 0, r.stdout + r.stderr
    assert "consistent" in r.stdout


def test_runs_from_any_cwd(tmp_path):
    r = _run("lint", cwd=tmp_path)
    assert r.returncode == 0, r.stdout + r.stderr


def test_deps_rejects_python_older_than_3_8(tmp_path):
    """The GHES self-hosted pool has Ubuntu 20.04 runners (python 3.8); anything
    older must be refused up front with a hint naming the floor, instead of
    crashing later inside the generator."""
    fake = tmp_path / "python3"
    fake.write_text(
        "#!/usr/bin/env bash\n"
        'case "$*" in\n'
        '  *--version*) echo "Python 3.6.9"; exit 0;;\n'
        '  *version_info*) exit 1;;\n'
        "esac\n"
        "exit 0\n"
    )
    fake.chmod(0o755)
    r = _run("deps", "--python", str(fake))
    out = r.stdout + r.stderr
    assert r.returncode == 1, out
    assert "3.8" in out, out
    assert "3.6.9" in out, out
