"""Setup warns before a disk-heavy setup on a nearly full card.

DX-APP Dependencies runs the runtime's `apt-get upgrade` (whole system); the build and the samples follow.
A fresh Raspberry Pi setup took a 29 GB card to 97 %."""
from pathlib import Path
from dx_app.core import setup_steps

SETUP_JS = Path(__file__).resolve().parents[2] / "dx_app" / "static" / "js" / "setup.js"


def test_status_reports_free_disk():
    d = setup_steps.setup_status()["disk"]
    assert d["free_gb"] > 0 and d["min_gb"] == setup_steps.MIN_FREE_GB


def test_page_confirms_before_disk_heavy_steps():
    js = SETUP_JS.read_text(encoding="utf-8")
    body = js[js.index("async function _setupRunSequence"):]
    assert "await _setupDiskOk(" in body[:800]
    run = js[js.index("async function setupRun(stepId)"):]
    assert "await _setupDiskOk(" in run[:400]
