# SPDX-License-Identifier: Apache-2.0
"""
Tests for the unresolved-`{{FRAGMENT:...}}` diagnostic.

In a standalone sub-repo clone the shared fragments are simply absent (they
live only in dx-all-suite), and every `{{FRAGMENT:...}}` placeholder is left
unresolved. The generator used to answer that with:

    Define the variable in _build_template_context() or fix the
    template/fragment name.

which is actively harmful here: an agent that follows it starts editing
templates or renaming fragments — turning a *missing input* into a real,
committed drift. The message must instead name the true cause and point at
the bootstrap.

The pre-existing behaviour for a genuinely wrong fragment name (fragments
directory present) must be preserved.
"""

from __future__ import annotations

import shutil
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
SRC = SUITE_ROOT / ".deepx" / "tools" / "src"


def _run_check(repo: Path):
    return subprocess.run(
        [
            sys.executable,
            "-c",
            "from dx_agent_dev_gen.cli import main; import sys; "
            "sys.exit(main(['check', '--repo', %r]))" % str(repo),
        ],
        cwd=str(repo),
        env={"PYTHONPATH": str(SRC), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=300,
    )


@pytest.fixture
def standalone_dx_app(tmp_path):
    src = SUITE_ROOT / "dx-runtime" / "dx_app"
    if not (src / ".deepx").is_dir():
        pytest.skip("dx_app submodule not initialised")
    dst = tmp_path / "solo" / "dx_app"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns(".git"))
    return dst


def test_standalone_checkout_is_told_to_bootstrap(standalone_dx_app):
    proc = _run_check(standalone_dx_app)
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, out
    assert "harness_bootstrap.sh" in out, (
        "the diagnostic must point at the bootstrap:\n" + out
    )


def test_standalone_diagnostic_does_not_suggest_editing_templates(
    standalone_dx_app,
):
    """The old text steered agents into causing a second, worse drift."""
    proc = _run_check(standalone_dx_app)
    out = proc.stdout + proc.stderr
    assert "_build_template_context" not in out, (
        "misleading hint still shown for a standalone checkout:\n" + out
    )
    assert "fix the template/fragment name" not in out


def test_standalone_diagnostic_names_the_missing_fragments_dir(
    standalone_dx_app,
):
    proc = _run_check(standalone_dx_app)
    out = proc.stdout + proc.stderr
    assert "fragments" in out
    assert "standalone" in out.lower()


def test_genuine_bad_fragment_name_keeps_the_original_hint(tmp_path):
    """When the fragments dir IS reachable, an unknown fragment name is a real
    authoring error and must still say so."""
    repo = tmp_path / "suitelike"
    # minimal repo carrying its own fragments dir so _find_fragments_dir() hits
    frag = repo / ".deepx" / "templates" / "fragments" / "en"
    frag.mkdir(parents=True)
    (frag / "real-fragment.md").write_text("content\n", encoding="utf-8")
    (repo / ".deepx" / "templates" / "fragments" / "ko").mkdir(parents=True)
    tmpl = repo / ".deepx" / "templates" / "en"
    tmpl.mkdir(parents=True)
    (tmpl / "CLAUDE.md.tmpl").write_text(
        "# T\n\n{{FRAGMENT:this-one-does-not-exist}}\n", encoding="utf-8"
    )

    proc = _run_check(repo)
    out = proc.stdout + proc.stderr
    assert proc.returncode != 0, out
    assert "this-one-does-not-exist" in out
    assert "_build_template_context" in out or "fragment name" in out
