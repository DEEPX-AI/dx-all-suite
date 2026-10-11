"""launcher.sh gives an old .venv the system GStreamer bindings (2026-10-11 real-use audit).

The .venv is created with --system-site-packages only when it is missing. One made by an older launcher.sh had none,
so the module servers could not import gi: DX Stream ran no in-process pipeline and Local (WebRTC) playback always
fell back to MJPEG even with gstreamer1.0-nice installed. Turning system site packages on in such a venv broke
`import cv2` (the venv's pip numpy 2.x against the system OpenCV built for numpy 1.x), so only `gi` is linked in.
"""
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SH = (Path(__file__).resolve().parents[2] / "launcher.sh").read_text(encoding="utf-8")


def _repair_block():
    return SH[SH.index("# >>> venv-repair"):SH.index("# <<< venv-repair")]


def _system_has_gi():
    return subprocess.run(["/usr/bin/python3", "-c", "import gi"], capture_output=True).returncode == 0


@pytest.mark.skipif(not Path("/usr/bin/python3").exists() or not _system_has_gi(), reason="needs system python3-gi")
def test_an_old_venv_gets_gi_and_keeps_its_own_packages(tmp_path):
    subprocess.run(["/usr/bin/python3", "-m", "venv", "--without-pip", str(tmp_path / ".venv")], check=True)
    py = tmp_path / ".venv" / "bin" / "python"
    assert subprocess.run([str(py), "-c", "import gi"], capture_output=True).returncode != 0
    subprocess.run(["bash", "-c", f'SCRIPT_DIR="{tmp_path}"\n' + _repair_block()], check=True, capture_output=True)
    ok = subprocess.run([str(py), "-c", "import gi; gi.require_version('Gst', '1.0'); from gi.repository import Gst"],
                        capture_output=True, text=True)
    assert ok.returncode == 0, ok.stderr
    cfg = (tmp_path / ".venv" / "pyvenv.cfg").read_text()
    assert "include-system-site-packages = false" in cfg   # nothing else from the system leaks in
    # a second run leaves it alone
    subprocess.run(["bash", "-c", f'SCRIPT_DIR="{tmp_path}"\n' + _repair_block()], check=True, capture_output=True)


def test_the_repair_never_turns_system_site_packages_on():
    assert "include-system-site-packages = true" not in _repair_block()
