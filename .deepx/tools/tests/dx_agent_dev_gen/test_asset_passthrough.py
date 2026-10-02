# SPDX-License-Identifier: Apache-2.0
"""
Tests for the generator's verbatim-asset passthrough.

`harness_bootstrap.sh` must exist inside every sub-repo, because a standalone
clone has no suite above it to borrow the script from. Hand-copying one file
into four repos is exactly the drift pattern this whole system exists to
prevent, so the script is authored once under
`.deepx/templates/assets/` and fanned out by `dx-agent-gen generate` like any
other multi-repo output — participating in `check` (drift) as well.

The suite itself is deliberately NOT a target: it keeps only the canonical
copy, and it never needs to bootstrap anything (it *is* the harness).
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest


def _find_suite_root(start: Path) -> Path:
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
ASSET_SRC = SUITE_ROOT / ".deepx" / "templates" / "assets" / "harness_bootstrap.sh"
ASSET_DST_REL = Path(".deepx") / "scripts" / "harness_bootstrap.sh"

SUBREPOS = [
    "dx-compiler",
    "dx-runtime",
    "dx-runtime/dx_app",
    "dx-runtime/dx_stream",
]


def _initialised(relpath: str) -> bool:
    return (SUITE_ROOT / relpath / ".deepx").is_dir()


def test_canonical_asset_exists():
    assert ASSET_SRC.is_file(), f"missing canonical asset: {ASSET_SRC}"


@pytest.mark.parametrize("relpath", SUBREPOS)
def test_asset_is_deployed_into_every_subrepo(relpath):
    if not _initialised(relpath):
        pytest.skip(f"{relpath} submodule not initialised")
    out = SUITE_ROOT / relpath / ASSET_DST_REL
    assert out.is_file(), (
        f"{relpath}: {ASSET_DST_REL} not generated — run "
        f"`bash .deepx/tools/scripts/run_all.sh generate`"
    )


@pytest.mark.parametrize("relpath", SUBREPOS)
def test_deployed_asset_body_matches_canonical(relpath):
    """The deployed copy carries a generated header, but its executable body
    must be byte-identical to the canonical source."""
    if not _initialised(relpath):
        pytest.skip(f"{relpath} submodule not initialised")
    out = SUITE_ROOT / relpath / ASSET_DST_REL
    if not out.is_file():
        pytest.skip("not generated yet (covered by the deployment test)")
    src = ASSET_SRC.read_text(encoding="utf-8")
    dst = out.read_text(encoding="utf-8")
    # strip the shebang from both, then the canonical body must appear verbatim
    src_body = src.partition("\n")[2]
    assert src_body in dst, f"{relpath}: deployed asset body drifted from canonical"


@pytest.mark.parametrize("relpath", SUBREPOS)
def test_deployed_asset_starts_with_shebang_then_generated_header(relpath):
    """A '#'-comment header, inserted AFTER the shebang — an HTML comment or a
    header above the shebang would break `bash <script>` semantics."""
    if not _initialised(relpath):
        pytest.skip(f"{relpath} submodule not initialised")
    out = SUITE_ROOT / relpath / ASSET_DST_REL
    if not out.is_file():
        pytest.skip("not generated yet (covered by the deployment test)")
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("#!"), "shebang must remain the very first line"
    header = "\n".join(lines[1:5])
    assert "AUTO-GENERATED" in header, "missing generated-file header"
    assert "<!--" not in header, "HTML comment header is invalid in a shell script"


@pytest.mark.parametrize("relpath", SUBREPOS)
def test_deployed_asset_is_syntactically_valid(relpath):
    if not _initialised(relpath):
        pytest.skip(f"{relpath} submodule not initialised")
    out = SUITE_ROOT / relpath / ASSET_DST_REL
    if not out.is_file():
        pytest.skip("not generated yet (covered by the deployment test)")
    proc = subprocess.run(["bash", "-n", str(out)], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr


def test_suite_itself_is_not_an_asset_target():
    """The suite keeps only the canonical copy — it never bootstraps itself."""
    assert not (SUITE_ROOT / ASSET_DST_REL).exists(), (
        "the suite must not receive the deployed asset"
    )


def test_missing_deployed_asset_is_reported_as_drift(tmp_path):
    """Deleting a deployed asset must make `check` fail — otherwise the
    passthrough is not really part of the drift contract."""
    if not _initialised("dx-runtime/dx_app"):
        pytest.skip("dx_app submodule not initialised")
    target = SUITE_ROOT / "dx-runtime" / "dx_app" / ASSET_DST_REL
    if not target.is_file():
        pytest.skip("not generated yet (covered by the deployment test)")

    backup = tmp_path / "harness_bootstrap.sh"
    backup.write_text(target.read_text(encoding="utf-8"), encoding="utf-8")
    target.unlink()
    try:
        proc = subprocess.run(
            [
                sys.executable,
                "-c",
                "from dx_agent_dev_gen.cli import main; import sys; "
                "sys.exit(main(['check', '--repo', %r]))"
                % str(SUITE_ROOT / "dx-runtime" / "dx_app"),
            ],
            cwd=str(SUITE_ROOT),
            env={
                "PYTHONPATH": str(SUITE_ROOT / ".deepx" / "tools" / "src"),
                # a minimal PATH on purpose (the check must not depend on the developer's shell); the
                # platform default instead of a hardcoded Linux value (PR #91 review)
                "PATH": os.defpath.lstrip(os.pathsep),
            },
            capture_output=True,
            text=True,
            timeout=300,
        )
        assert proc.returncode != 0, "check passed despite a missing generated asset"
        assert "harness_bootstrap.sh" in (proc.stdout + proc.stderr)
    finally:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(backup.read_text(encoding="utf-8"), encoding="utf-8")
