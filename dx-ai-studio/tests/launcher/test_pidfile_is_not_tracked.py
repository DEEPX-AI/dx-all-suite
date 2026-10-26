"""launcher/.launcher_pids must not be in the repository.

On start, _cleanup_old_pids() treats the PIDs in this file as left by a previous launcher and signals their
process groups with SIGTERM/SIGKILL. A committed copy would make the first launcher start on a fresh clone
kill unrelated processes that happen to hold the same numbers.
"""
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PIDFILE = "launcher/.launcher_pids"


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def test_pidfile_is_not_tracked():
    assert _git("ls-files", "--error-unmatch", PIDFILE).returncode != 0, (
        f"{PIDFILE} 가 git 에 추적되고 있다 — git rm --cached {PIDFILE}"
    )


def test_pidfile_is_ignored():
    assert _git("check-ignore", "-q", PIDFILE).returncode == 0, (
        f"{PIDFILE} 가 .gitignore 에 없다"
    )
