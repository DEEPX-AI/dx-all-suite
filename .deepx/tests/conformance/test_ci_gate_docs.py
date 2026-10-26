# SPDX-License-Identifier: Apache-2.0
"""The CI gate documentation must exist in EN and KO at every level and be
reachable from each level's `.deepx/README*.md`."""

from __future__ import annotations

import pytest

from .conftest import SUITE_ROOT, COMPILER_ROOT, RUNTIME_ROOT, APP_ROOT, STREAM_ROOT

SUITE_DOCS = ["ci-gates.md", "ci-gates-KO.md"]
SUB_DOCS = ["ci-subrepo-gate.md", "ci-subrepo-gate-KO.md"]
SUB_ROOTS = [
    ("compiler", COMPILER_ROOT, "dx-compiler"),
    ("runtime", RUNTIME_ROOT, "dx-runtime"),
    ("app", APP_ROOT, "dx-runtime/dx_app"),
    ("stream", STREAM_ROOT, "dx-runtime/dx_stream"),
]
STALE = ("dx-agent-dev-gate.yml", "dx-agent-dev-subrepo-gate.yml", "gh-drift-check")


@pytest.mark.parametrize("name", SUITE_DOCS)
def test_suite_doc_exists_and_covers_both_variants(name):
    p = SUITE_ROOT / ".deepx" / "docs" / name
    assert p.is_file(), f"missing {p}"
    text = p.read_text(encoding="utf-8")
    for needle in (
        "dx-agent-dev-gate-ghes.yml", "dx-agent-dev-gate-cloud.yml",
        "dx-agent-dev-subrepo-gate-ghes.yml", "dx-agent-dev-subrepo-gate-cloud.yml",
        "harness_gate.sh", "subrepo_check.sh", "GH_DCI_TOKEN", "GC_DCI_TOKEN",
        "ubuntu-latest", "self-hosted", "branch-tip", "release-excluded", "gh workflow run",
    ):
        assert needle in text, f"{name}: must mention {needle}"


@pytest.mark.parametrize("readme", ["README.md", "README-KO.md"])
def test_suite_readme_links_ci_gates_doc(readme):
    text = (SUITE_ROOT / ".deepx" / readme).read_text(encoding="utf-8")
    assert "docs/ci-gates" in text, f".deepx/{readme} must link docs/ci-gates*.md"
    for s in STALE:
        assert s not in text, f".deepx/{readme} still names the removed workflow {s}"


@pytest.mark.parametrize("label,root,subrepo_path", SUB_ROOTS, ids=[r[0] for r in SUB_ROOTS])
@pytest.mark.parametrize("name", SUB_DOCS)
def test_subrepo_doc_exists_and_is_specific(label, root, subrepo_path, name):
    if not (root / ".deepx").is_dir():
        pytest.skip(f"{label}: .deepx absent")
    p = root / ".deepx" / "docs" / name
    assert p.is_file(), f"{label}: missing {p}"
    text = p.read_text(encoding="utf-8")
    for needle in (
        "dx-agent-dev-subrepo-gate-ghes.yml", "dx-agent-dev-subrepo-gate-cloud.yml",
        "subrepo_check.sh", f"--subrepo-path {subrepo_path}", "ci-gates",
    ):
        assert needle in text, f"{label}/{name}: must mention {needle}"


@pytest.mark.parametrize("label,root,_", SUB_ROOTS, ids=[r[0] for r in SUB_ROOTS])
@pytest.mark.parametrize("readme", ["README.md", "README-KO.md"])
def test_subrepo_readme_links_doc(label, root, _, readme):
    if not (root / ".deepx").is_dir():
        pytest.skip(f"{label}: .deepx absent")
    text = (root / ".deepx" / readme).read_text(encoding="utf-8")
    assert "docs/ci-subrepo-gate" in text, f"{label}/.deepx/{readme} must link docs/ci-subrepo-gate*.md"


def test_no_stale_references_to_removed_workflows_in_deepx_docs():
    hits = []
    for root in [SUITE_ROOT] + [r[1] for r in SUB_ROOTS]:
        d = root / ".deepx"
        if not d.is_dir():
            continue
        files = list(d.glob("*.md")) + list((d / "docs").glob("*.md")) + list((d / "tools" / "scripts").glob("*.md"))
        for p in files:
            for line in p.read_text(encoding="utf-8").splitlines():
                if any(s in line for s in STALE) and "replaced" not in line and "대체" not in line:
                    hits.append(f"{p.relative_to(SUITE_ROOT)}: {line.strip()[:110]}")
    assert not hits, "stale workflow names:\n" + "\n".join(hits)
