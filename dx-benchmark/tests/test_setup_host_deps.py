"""Regression tests for setup_host.sh's dependency-ensure block.

Two real field failures motivated hardening this block (2026-07-22):
  - ROCK5B: a pre-existing broken dpkg state (failing radxa-overlays DKMS build)
    made `apt-get install` return non-zero, aborting the whole script under
    `set -e` even though all 5 tools were already installed.
  - OrangePi 5 Plus: `ffmpeg` is `apt-mark hold` (likely a vendor MPP build);
    naming it in `apt-get install -y` triggered
    "Held packages were changed ... without --allow-change-held-packages".

What matters is that the TOOLS are present, not that apt succeeds. The block
must therefore: install only genuinely-missing packages (skip apt when none
missing), never abort on an unrelated apt error, and hard-fail only when a
required binary is still absent.

The tests extract the REAL block from setup_host.sh (between its markers) and
exercise it with a fake PATH, so they track the shipped script, not a copy.
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

SETUP = Path(__file__).resolve().parents[1] / "setup_host.sh"
_MARKERS = re.compile(r"# >>> bench-deps.*?>>>\n(.*?)\n# <<< bench-deps <<<", re.S)
_BASH = shutil.which("bash")

pytestmark = pytest.mark.skipif(_BASH is None, reason="bash not available")


def _block() -> str:
    m = _MARKERS.search(SETUP.read_text())
    assert m, "bench-deps markers not found in setup_host.sh"
    return m.group(1)


def _exe(path: Path, body: str) -> None:
    path.write_text(body)
    path.chmod(0o755)


def _run(tmp_path: Path, present: list[str], apt_action: str):
    """Run the extracted block with a fake PATH containing only `present` tools
    plus a fake apt-get. Returns (returncode, combined_output, apt_call_log)."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    for tool in present:
        _exe(bindir / tool, "#!/bin/sh\nexit 0\n")
    marker = tmp_path / "apt_calls"
    _exe(
        bindir / "apt-get",
        "#!/bin/sh\n"
        f'echo "$@" >> "{marker}"\n'
        '[ "$1" = update ] && exit 0\n'
        f'if [ "$1" = install ]; then\n{apt_action}\nfi\n',
    )
    block = tmp_path / "block.sh"
    block.write_text(_block())
    proc = subprocess.run(
        [_BASH, "-c", 'set -euo pipefail; source "$0"', str(block)],
        env={"PATH": str(bindir), "TIME_BIN": str(bindir / "time")},
        capture_output=True,
        text=True,
    )
    calls = marker.read_text() if marker.exists() else ""
    return proc.returncode, proc.stdout + proc.stderr, calls


def _install_jq(tmp_path: Path, exit_code: int) -> str:
    """apt action that 'installs' jq into the fake bindir, then exits `exit_code`."""
    jq = tmp_path / "bin" / "jq"
    return f"printf '#!/bin/sh\\nexit 0\\n' > '{jq}'; chmod +x '{jq}'; exit {exit_code}"


def test_setup_host_syntax_ok():
    proc = subprocess.run([_BASH, "-n", str(SETUP)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_all_present_skips_apt(tmp_path):
    # OrangePi5B held-ffmpeg case: every tool present → apt must never run.
    rc, out, calls = _run(tmp_path, ["time", "jq", "ffprobe", "curl", "tar"], "exit 0")
    assert rc == 0
    assert "skipping apt" in out
    assert calls == "", f"apt-get should not be called; got: {calls!r}"


def test_installs_only_missing_package(tmp_path):
    rc, out, calls = _run(
        tmp_path, ["time", "ffprobe", "curl", "tar"], _install_jq(tmp_path, 0)
    )
    assert rc == 0
    assert re.search(r"install .*jq", calls), f"jq not installed: {calls!r}"
    assert "ffmpeg" not in calls, f"ffmpeg must not be touched (present): {calls!r}"


def test_apt_failure_with_tool_still_missing_hard_fails(tmp_path):
    # Genuinely-absent tool that apt cannot provide → must exit non-zero.
    rc, out, _ = _run(tmp_path, ["time", "ffprobe", "curl", "tar"], "exit 100")
    assert rc != 0
    assert "still missing" in out


def test_apt_error_but_tool_present_succeeds(tmp_path):
    # ROCK5B-type: apt returns non-zero (unrelated broken/held state) but the
    # tool ends up present → verify-by-binary must let the script continue.
    rc, out, _ = _run(tmp_path, ["time", "ffprobe", "curl", "tar"], _install_jq(tmp_path, 100))
    assert rc == 0
    assert "WARNING: apt reported an error" in out
    assert "System dependencies ready" in out
