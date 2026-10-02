# SPDX-License-Identifier: Apache-2.0
"""
Conformance tests for the sub-repo drift-gate CI workflows.

Each sub-repo (dx-compiler, dx-runtime, dx-runtime/dx_app, dx-runtime/dx_stream)
carries TWO caller workflows that differ only in runner / token / Python
bootstrap / host guard:

  dx-agent-dev-subrepo-gate-ghes.yml   self-hosted,   GH_DCI_TOKEN, system python3
  dx-agent-dev-subrepo-gate-cloud.yml  ubuntu-latest,       GC_DCI_TOKEN, actions/setup-python

Both clone dx-all-suite and run `.deepx/tools/scripts/subrepo_check.sh`
against the checkout at its canonical nested position. A job-level
`if: github.server_url …` guard makes exactly one run per host (the private
mirror deepx-dhyang/* receives both files via git).

A root whose `.github` directory is absent (submodule not initialized in this
checkout) is SKIPPED, not failed.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest
import yaml

from .conftest import COMPILER_ROOT, RUNTIME_ROOT, APP_ROOT, STREAM_ROOT

OLD_WORKFLOW_NAME = "dx-agent-dev-subrepo-gate.yml"

VARIANTS = {
    "ghes": {
        "file": "dx-agent-dev-subrepo-gate-ghes.yml",
        "runs_on": "self-hosted",
        "token": "GH_DCI_TOKEN",
        "guard": "github.server_url != 'https://github.com'",
    },
    "cloud": {
        "file": "dx-agent-dev-subrepo-gate-cloud.yml",
        "runs_on": "ubuntu-latest",
        "token": "GC_DCI_TOKEN",
        "guard": "github.server_url == 'https://github.com'",
    },
}

CASES = [
    ("compiler", COMPILER_ROOT, "dx-compiler"),
    ("runtime", RUNTIME_ROOT, "dx-runtime"),
    ("app", APP_ROOT, "dx-runtime/dx_app"),
    ("stream", STREAM_ROOT, "dx-runtime/dx_stream"),
]


def _path(root: Path, variant: str) -> Path:
    return root / ".github" / "workflows" / VARIANTS[variant]["file"]


@pytest.fixture(params=CASES, ids=[c[0] for c in CASES])
def repo_case(request):
    label, root, subrepo_path = request.param
    if not (root / ".github").is_dir():
        pytest.skip(f"{label}: .github/ absent (submodule not initialized)")
    return label, root, subrepo_path


@pytest.fixture(params=sorted(VARIANTS), ids=sorted(VARIANTS))
def variant(request):
    return request.param


@pytest.fixture
def gate(repo_case, variant):
    label, root, subrepo_path = repo_case
    path = _path(root, variant)
    if not path.is_file():
        pytest.skip(f"{label}/{variant}: workflow file not present yet")
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    return label, root, subrepo_path, variant, path, doc


def _job(doc: dict) -> dict:
    jobs = doc.get("jobs", {})
    assert list(jobs) == ["subrepo-gate"], f"expected exactly one job 'subrepo-gate', got {list(jobs)}"
    return jobs["subrepo-gate"]


def _runs(job: dict) -> str:
    return "\n".join(s.get("run", "") for s in job.get("steps", []) if isinstance(s, dict))


def _stale_hint(label: str, root: Path) -> str:
    """Appended to parity failures: in branch-tip mode a sub-repo is checked out at its
    integration branch (main, or dev for dx_app/dx_stream). When only ONE sub-repo fails
    these tests, that branch simply has not merged the workflow PR yet (GHES runs
    1748/1751: dx-runtime main) — not a defect in the files under test."""
    try:
        sha = subprocess.run(["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
                             text=True, capture_output=True, timeout=20).stdout.strip() or "?"
    except Exception:  # noqa: BLE001
        sha = "?"
    return (f" [hint: {label} is checked out at {sha}; if only this sub-repo fails, its integration branch "
            f"has not merged the gate-workflow PR yet — merge feature/dx-agent-dev there or preview with "
            f"submodule_refs='{label}=feature/dx-agent-dev']")


def test_old_single_file_workflow_is_gone(repo_case):
    label, root, _ = repo_case
    assert not (root / ".github" / "workflows" / OLD_WORKFLOW_NAME).exists(), (
        f"{label}: {OLD_WORKFLOW_NAME} must be removed (replaced by -ghes/-cloud)"
    )


def test_workflow_file_exists(repo_case, variant):
    label, root, _ = repo_case
    assert _path(root, variant).is_file(), f"{label}/{variant}: missing {_path(root, variant)}"


def test_workflow_triggers(gate):
    label, *_, doc = gate
    triggers = doc.get("on", doc.get(True))
    for trig in ("pull_request", "push", "workflow_dispatch"):
        assert trig in triggers, f"{label}: missing {trig} trigger"


def test_workflow_permissions_read_only(gate):
    label, *_, doc = gate
    assert doc.get("permissions") == {"contents": "read"}, f"{label}: permissions must be contents: read"


def test_runs_on_per_variant(gate):
    label, _, _, variant, _, doc = gate
    assert _job(doc).get("runs-on") == VARIANTS[variant]["runs_on"], f"{label}/{variant}: wrong runs-on"


def test_job_guards_server_and_fork(gate):
    label, _, _, variant, _, doc = gate
    job_if = _job(doc).get("if", "")
    assert VARIANTS[variant]["guard"] in job_if, f"{label}/{variant}: host guard missing in {job_if!r}"
    assert "head.repo.full_name == github.repository" in job_if, f"{label}: fork-PR guard missing"


def test_token_precedence(gate):
    label, _, _, variant, path, _ = gate
    text = path.read_text(encoding="utf-8")
    token = VARIANTS[variant]["token"]
    assert f"secrets.{token} || github.token" in text, f"{label}/{variant}: expected secrets.{token} || github.token"
    other = "GC_DCI_TOKEN" if token == "GH_DCI_TOKEN" else "GH_DCI_TOKEN"
    assert other not in text, f"{label}/{variant}: must reference only {token}"


def test_workflow_calls_subrepo_check_with_expected_path(gate):
    label, _, subrepo_path, _, _, doc = gate
    runs = _runs(_job(doc))
    assert "subrepo_check.sh" in runs, f"{label}: no step invokes subrepo_check.sh"
    assert f"--subrepo-path {subrepo_path}" in runs, f"{label}: expected '--subrepo-path {subrepo_path}'"
    assert "--suite-dir" in runs, f"{label}: expected --suite-dir"


def test_workflow_header_mentions_release_excluded(gate):
    label, _, _, _, path, _ = gate
    header = "\n".join(l for l in path.read_text(encoding="utf-8").splitlines()[:25] if l.strip().startswith("#"))
    assert "release-excluded" in header, f"{label}: header must mention release-excluded"


def test_clone_step_uses_http_extraheader_not_token_in_url(gate):
    label, *_, doc = gate
    runs = _runs(_job(doc))
    assert "http.extraheader" in runs, f"{label}: expected git -c http.extraheader auth"
    assert not re.search(r"x-access-token:[^@\s]*@", runs), f"{label}: token must never be embedded in the clone URL"
    assert "set -x" not in runs, f"{label}: set -x would echo the auth header"
    rm_idx = runs.find('rm -rf "$GITHUB_WORKSPACE/suite"')
    clone_idx = runs.find("clone -q --depth 1")
    assert rm_idx != -1 and clone_idx != -1 and rm_idx < clone_idx, f"{label}: rm -rf suite must precede git clone"


def test_has_always_run_cleanup_step(gate):
    label, *_, doc = gate
    steps = _job(doc).get("steps", [])
    assert any(
        isinstance(s, dict) and s.get("if") == "always()" and "rm -rf" in s.get("run", "") and "suite" in s.get("run", "")
        for s in steps
    ), f"{label}: expected an if: always() step removing the suite clone"


@pytest.mark.parametrize("variant_name", sorted(VARIANTS))
def test_all_four_workflows_identical_modulo_path(variant_name):
    """Per variant, the 4 sub-repo files are one template with only the
    sub-repo path substituted — verify they have not drifted apart."""
    entries = []
    for label, root, subrepo_path in CASES:
        path = _path(root, variant_name)
        if not (root / ".github").is_dir() or not path.is_file():
            continue
        entries.append((label, path.read_text(encoding="utf-8").replace(subrepo_path, "<SUBREPO_PATH>")))
    if len(entries) < 2:
        pytest.skip(f"{variant_name}: fewer than 2 workflow files present")
    base_label, base_text = entries[0]
    for label, text in entries[1:]:
        assert text == base_text, (
            f"{variant_name}: {label} differs from {base_label} beyond <SUBREPO_PATH>"
            + _stale_hint(label, dict((c[0], c[1]) for c in CASES)[label])
        )


def test_ghes_and_cloud_differ_only_in_expected_places():
    """Within one sub-repo, the ghes and cloud files must be identical except
    for: header comments, workflow name, job `if` (host guard), `runs-on`, the
    TOKEN secret, the Python bootstrap step(s) and the cleanup step."""
    def _norm(doc: dict) -> dict:
        job = _job(doc)
        steps = []
        for s in job.get("steps", []):
            name = str(s.get("name", ""))
            if name.startswith(("Set up Python", "Python deps", "Cleanup")):
                continue
            s = dict(s)
            if isinstance(s.get("env"), dict) and "TOKEN" in s["env"]:
                s["env"] = {**s["env"], "TOKEN": "<TOKEN>"}
            steps.append(s)
        return {
            "on": doc.get("on", doc.get(True)),
            "permissions": doc.get("permissions"),
            "concurrency": doc.get("concurrency"),
            "job_keys": sorted(k for k in job if k not in ("if", "runs-on")),
            "timeout": job.get("timeout-minutes"),
            "steps": steps,
        }
    compared = 0
    for label, root, _ in CASES:
        if not (root / ".github").is_dir():
            continue
        paths = [_path(root, v) for v in ("ghes", "cloud")]
        if not all(p.is_file() for p in paths):
            continue
        docs = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in paths]
        assert _norm(docs[0]) == _norm(docs[1]), (
            f"{label}: ghes/cloud differ beyond runner/token/guard/bootstrap/cleanup"
        )
        compared += 1
    if compared == 0:
        pytest.skip("no sub-repo has both variant files yet")


def test_ghes_python_step_checks_version_and_how_to_fix_names_tool_errors(gate):
    """GHES run 982: the self-hosted pool has Python 3.8 runners. The ghes deps
    step must print the interpreter version and fail fast below the 3.8 floor,
    and 'How to fix' must say that a Traceback / exit 2 is a tool or runner
    problem — NOT drift — so nobody 'regenerates' to fix a crash."""
    label, root, subrepo_path, variant, path, doc = gate
    if variant != "ghes":
        pytest.skip("cloud pins Python via actions/setup-python")
    steps = _job(doc)["steps"]
    deps = next(s for s in steps if str(s.get("name", "")).startswith("Python deps"))
    run = deps.get("run", "")
    assert "python3 --version" in run, f"{label}: deps step must print `python3 --version`" + _stale_hint(label, root)
    assert "(3, 8)" in run, f"{label}: deps step must gate on sys.version_info >= (3, 8)"
    fix = next(s for s in steps if s.get("name") == "How to fix")
    assert "NOT drift" in fix.get("run", ""), f"{label}: How-to-fix must distinguish tool errors from drift"


def test_clone_step_waits_for_same_name_suite_branch_and_refuses_an_old_suite(gate):
    """ghes-sync pushes nested repos first and dx-all-suite last (seconds to a minute
    later). A sub-repo gate that starts in between used to fall back to the suite's
    default branch — an OLD suite without subrepo_check.sh — and die with
    `bash: suite/.deepx/tools/scripts/subrepo_check.sh: No such file` (3 of 4 gates
    red on the first GHES sync, 2026-09-10). The clone step must (1) wait, bounded by
    SUITE_BRANCH_WAIT, for the same-name suite branch to appear and (2) if it still has
    to fall back, refuse a suite that lacks the script with an explicit ::error:: telling
    the user to sync the suite first and re-run."""
    label, root, subrepo_path, variant, path, doc = gate
    steps = _job(doc)["steps"]
    clone = next(s for s in steps if str(s.get("name", "")).startswith("Clone dx-all-suite"))
    run = clone.get("run", "")
    env = clone.get("env", {})
    assert "SUITE_BRANCH_WAIT" in env, f"{label}/{variant}: clone step must expose SUITE_BRANCH_WAIT" + _stale_hint(label, root)
    assert "SUITE_BRANCH_WAIT" in run and "sleep" in run and "ls-remote --heads" in run, (
        f"{label}/{variant}: clone step must poll ls-remote for the same-name suite branch"
    )
    assert 'suite/.deepx/tools/scripts/subrepo_check.sh' in run and "::error::" in run and "re-run" in run, (
        f"{label}/{variant}: clone step must refuse an old suite (no subrepo_check.sh) with an explicit error"
    )
