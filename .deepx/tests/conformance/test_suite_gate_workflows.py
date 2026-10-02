# SPDX-License-Identifier: Apache-2.0
"""
Conformance tests for the suite-level harness gate workflows.

The gate is split into two files that differ ONLY in runner, token and
Python bootstrap: `dx-agent-dev-gate-ghes.yml` (closed-network GHES,
self-hosted, GH_DCI_TOKEN, system python3) and
`dx-agent-dev-gate-cloud.yml` (github.com — private mirror deepx-dhyang/* and
public DEEPX-AI/* — ubuntu-latest, GC_DCI_TOKEN, actions/setup-python). A
job-level `if: github.server_url …` guard makes exactly one of them run on a
given host, because the mirror receives BOTH files via git.
"""

from __future__ import annotations

import re

import pytest
import yaml

from .conftest import SUITE_ROOT

WORKFLOWS = SUITE_ROOT / ".github" / "workflows"

VARIANTS = {
    "ghes": {
        "file": "dx-agent-dev-gate-ghes.yml",
        "runs_on": "self-hosted",
        "token": "GH_DCI_TOKEN",
        "guard": "github.server_url != 'https://github.com'",
    },
    "cloud": {
        "file": "dx-agent-dev-gate-cloud.yml",
        "runs_on": "ubuntu-latest",
        "token": "GC_DCI_TOKEN",
        "guard": "github.server_url == 'https://github.com'",
    },
}

REQUIRED_SUBMODULES = ("dx-runtime dx-compiler", "dx_app dx_stream")
STAGES = ("check", "lint", "tests", "e2e-sh")


def _load(name: str) -> dict:
    path = WORKFLOWS / name
    if not path.is_file():
        pytest.skip(f"{name} not present yet")
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _job(doc: dict) -> dict:
    jobs = doc.get("jobs", {})
    assert list(jobs) == ["harness-gate"], f"expected exactly one job 'harness-gate', got {list(jobs)}"
    return jobs["harness-gate"]


def _runs(job: dict) -> str:
    return "\n".join(s.get("run", "") for s in job.get("steps", []) if isinstance(s, dict))


def _header(name: str) -> str:
    text = (WORKFLOWS / name).read_text(encoding="utf-8")
    return "\n".join(l for l in text.splitlines()[:25] if l.strip().startswith("#"))


@pytest.fixture(params=sorted(VARIANTS), ids=sorted(VARIANTS))
def variant(request):
    return request.param, VARIANTS[request.param]


def test_old_single_file_gates_are_gone():
    for old in ("dx-agent-dev-gate.yml", "gh-drift-check.yml"):
        assert not (WORKFLOWS / old).exists(), f"{old} must be removed (replaced by -ghes/-cloud)"


def test_file_exists(variant):
    _, v = variant
    assert (WORKFLOWS / v["file"]).is_file()


def test_triggers_and_dispatch_input(variant):
    _, v = variant
    doc = _load(v["file"])
    on = doc.get("on", doc.get(True))
    for trig in ("pull_request", "push", "workflow_dispatch"):
        assert trig in on, f"missing {trig} trigger"
    inputs = (on.get("workflow_dispatch") or {}).get("inputs", {})
    assert "mode" in inputs, "workflow_dispatch must expose a 'mode' input"
    sub = inputs["mode"]
    assert sub.get("type") == "choice"
    assert sub.get("default") == "branch-tip"
    assert sorted(sub.get("options", [])) == ["branch-tip", "pointer"]


def test_permissions_read_only(variant):
    _, v = variant
    assert _load(v["file"]).get("permissions") == {"contents": "read"}


def test_runs_on_per_variant(variant):
    _, v = variant
    assert _job(_load(v["file"])).get("runs-on") == v["runs_on"]


def test_job_guards_server_and_fork(variant):
    _, v = variant
    job_if = _job(_load(v["file"])).get("if", "")
    assert v["guard"] in job_if, f"job 'if' must contain {v['guard']!r}, got {job_if!r}"
    assert "head.repo.full_name == github.repository" in job_if, "fork-PR guard missing"


def test_token_precedence(variant):
    _, v = variant
    _load(v["file"])
    text = (WORKFLOWS / v["file"]).read_text(encoding="utf-8")
    assert f"secrets.{v['token']} || github.token" in text
    other = "GC_DCI_TOKEN" if v["token"] == "GH_DCI_TOKEN" else "GH_DCI_TOKEN"
    assert other not in text, f"{v['file']} must reference only {v['token']}"


def test_checkout_has_no_recursive_submodules(variant):
    _, v = variant
    job = _job(_load(v["file"]))
    for step in job["steps"]:
        if isinstance(step, dict) and str(step.get("uses", "")).startswith("actions/checkout"):
            with_ = step.get("with", {})
            assert with_.get("submodules") in (False, "false", None), (
                "checkout must not use submodules: true/recursive — the mirror lacks dx_fw; "
                "init the 4 required submodules explicitly instead"
            )
            assert with_.get("persist-credentials") is False
            return
    pytest.fail("no actions/checkout step")


def test_explicit_submodule_init_with_extraheader(variant):
    _, v = variant
    runs = _runs(_job(_load(v["file"])))
    assert "submodule update --init" in runs
    for group in REQUIRED_SUBMODULES:
        assert group in runs, f"expected explicit init of '{group}'"
    assert "http.extraheader" in runs
    assert not re.search(r"x-access-token:[^@\s]*@", runs), "token must never be embedded in a URL"
    assert "set -x" not in runs
    assert "branch-tip" in runs, "branch-tip mode must be handled in the init step"


def test_stages_run_through_harness_gate_sh(variant):
    _, v = variant
    runs = _runs(_job(_load(v["file"])))
    for stage in STAGES:
        assert f"harness_gate.sh {stage}" in runs, f"stage '{stage}' must be invoked via harness_gate.sh"
    assert "harness_gate.sh deps" in runs, "a deps preflight must run before the stages"


def test_header_mentions_release_excluded(variant):
    _, v = variant
    _load(v["file"])
    assert "release-excluded" in _header(v["file"])


def test_cloud_header_says_hand_committed_to_public():
    _load(VARIANTS["cloud"]["file"])
    header = _header(VARIANTS["cloud"]["file"])
    assert "DEEPX-AI" in header and "by hand" in header


def test_ghes_and_cloud_share_the_same_stage_commands():
    docs = {k: _load(v["file"]) for k, v in VARIANTS.items()}
    stage_lines = {}
    for k, doc in docs.items():
        runs = _runs(_job(doc))
        # deps bootstrap legitimately differs per variant; the pass/fail stages must not
        stage_lines[k] = sorted(
            l.strip() for l in runs.splitlines()
            if re.search(r"harness_gate\.sh (check|lint|tests|e2e-sh)\b", l)
        )
    assert stage_lines["ghes"] == stage_lines["cloud"], "the two variants must run identical gate commands"
    assert len(stage_lines["ghes"]) == len(STAGES)


def test_stages_after_check_are_gated_on_deps_success(variant):
    """`if: !cancelled()` alone keeps lint/tests/e2e-sh running after a SETUP
    failure (submodule init / Python deps), producing misleading errors such as
    "No module named pytest" (seen on the mirror, 2026-09-08). The follow-on
    stages must still run after a *drift* failure in `check`, but only when the
    deps step (id: deps) succeeded."""
    _, v = variant
    job = _job(_load(v["file"]))
    steps = [s for s in job["steps"] if isinstance(s, dict)]
    assert any(s.get("id") == "deps" and "harness_gate.sh deps" in s.get("run", "") for s in steps), (
        "the Python deps step must carry `id: deps`"
    )
    for s in steps:
        run = s.get("run", "")
        if re.search(r"harness_gate\.sh (lint|tests|e2e-sh)\b", run):
            cond = str(s.get("if", ""))
            assert "!cancelled()" in cond and "steps.deps.outcome == 'success'" in cond, (
                f"step {s.get('name')!r} must have if: !cancelled() && steps.deps.outcome == 'success', got {cond!r}"
            )


def test_python_bootstrap_provides_rich(variant):
    """`.deepx/e2e/e2e_monitor.py` / `e2e_runner.py` import `rich` inside a
    try/except, so without it the e2e unit tests die with `NameError: Table`
    (7 failures on the first green-path mirror run, 2026-09-08). Both variants
    must install / check for rich alongside jinja2, pyyaml and pytest."""
    _, v = variant
    _load(v["file"])
    text = (WORKFLOWS / v["file"]).read_text(encoding="utf-8")
    assert "rich" in text, f"{v['file']}: Python bootstrap must provide the 'rich' package"


def test_mode_step_selects_pointer_on_gitlink_change(variant):
    """Default runs validate the sub-repos at the same-name branch tip; the recorded
    pointers are checked automatically when the push / PR range changed a submodule
    gitlink (update-submodule.yml bump commits) or on explicit dispatch. The decision
    lives in gate_mode.sh so it is unit-testable; the step only fetches the base
    commit (with header auth) and forwards the event data."""
    _, v = variant
    job = _job(_load(v["file"]))
    steps = [s for s in job["steps"] if isinstance(s, dict)]
    mode = [s for s in steps if s.get("id") == "mode"]
    assert mode, "expected a step with id: mode"
    run = mode[0].get("run", "")
    env = mode[0].get("env", {})
    assert "gate_mode.sh" in run
    assert "http.extraheader" in run and "fetch" in run, "base commit must be fetched with header auth"
    assert 'mode=' in run and "GITHUB_OUTPUT" in run
    assert "github.event.before" in str(env.get("BEFORE", "")), "push base comes from github.event.before"
    assert "pull_request.base.sha" in str(env.get("BASE", "")), "PR base comes from github.event.pull_request.base.sha"
    assert "inputs.mode" in str(env.get("INPUT_MODE", ""))
    init = [s for s in steps if "submodule update --init" in s.get("run", "")]
    assert init and "steps.mode.outputs.mode" in str(init[0].get("env", {}).get("MODE", "")), (
        "init step must take MODE from steps.mode.outputs.mode"
    )
    order = [s.get("id") or s.get("name") for s in steps]
    assert order.index("mode") < order.index(init[0].get("id") or init[0].get("name"))


# ── main + dev integration view (workflow_dispatch submodule_refs) ──────────────

def _steps(v):
    return [s for s in _job(_load(v["file"]))["steps"] if isinstance(s, dict)]


def test_dispatch_input_submodule_refs(variant):
    """dx_app/dx_stream integrate on `dev` while dx-runtime/dx-all-suite integrate on
    `main`, so a main run cannot see work that is still on dev. A manual run may pin
    individual sub-repos to another branch: submodule_refs='dx_app=dev dx_stream=dev'."""
    _, v = variant
    doc = _load(v["file"])
    inputs = doc.get("on", doc.get(True))["workflow_dispatch"]["inputs"]
    assert "submodule_refs" in inputs, "workflow_dispatch must accept submodule_refs"
    assert "dx_app=dev" in inputs["submodule_refs"]["description"]
    assert inputs["submodule_refs"].get("required", False) is False


def test_init_step_honours_submodule_refs_in_branch_tip_mode(variant):
    _, v = variant
    init = [s for s in _steps(v) if "submodule update --init" in s.get("run", "")][0]
    assert "inputs.submodule_refs" in str(init.get("env", {}).get("SUBMODULE_REFS", "")), (
        "init step must receive SUBMODULE_REFS from the dispatch input"
    )
    run = init["run"]
    for needle in ("SUBMODULE_REFS", "submodule_refs override", "does not exist", "requires mode=branch-tip"):
        assert needle in run, f"init step must contain {needle!r}"


def test_how_to_fix_offers_the_dev_integration_rerun_on_a_failed_main_push(variant):
    """A red `push` run on main is expected while dx_app/dx_stream changes sit on dev.
    The failure handler must try to dispatch the same gate with
    submodule_refs='dx_app=dev dx_stream=dev' and, if the token cannot, print exactly
    how to run it (UI and gh CLI)."""
    _, v = variant
    fix = [s for s in _steps(v) if s.get("name") == "How to fix"][0]
    env = fix.get("env", {})
    assert env.get("INTEGRATION_REFS") == "dx_app=dev dx_stream=dev"
    assert "github.api_url" in str(env.get("API", ""))
    run = fix["run"]
    for needle in ("/actions/workflows/", "/dispatches", "submodule_refs", "gh workflow run", "Run workflow", "actions:write"):
        assert needle in run, f"How-to-fix must contain {needle!r}"
    assert '"$EVENT" = push' in run and '"$REF_NAME" = main' in run, "only a failed push to main triggers the follow-up"


# ── 2026-09-23 run 1830 (PR #91, runner do-rt-08_01): exit 128 in the pointer-mode listing ──

def test_pointer_mode_listing_is_not_recursive(variant):
    """`git submodule status --recursive` walked into a stale dx_fw tree left on the reused runner
    workspace and died on a broken nested .git; the informational listing must name the four
    initialised paths only."""
    _, v = variant
    runs = _runs(_job(_load(v["file"])))
    assert "submodule status --recursive" not in runs
    assert "submodule status -- dx-runtime dx-compiler" in runs
    assert "-C dx-runtime submodule status -- dx_app dx_stream" in runs


def test_mode_step_fetches_the_merge_parent_for_pull_requests(variant):
    """gate_mode.sh compares the test merge against its first parent (current base tip); the depth-1
    checkout lacks it, so the mode step must fetch it — read from the raw commit object (shallow-safe)."""
    _, v = variant
    steps = _job(_load(v["file"]))["steps"]
    mode = next(s for s in steps if s.get("id") == "mode")
    run = mode.get("run", "")
    assert "cat-file -p" in run and "parent" in run, "merge parent must be read from the raw commit object"
    assert run.count("fetch -q --depth=1 origin") >= 2, "both the base and the merge parent must be fetched"


def test_ghes_resets_the_reused_workspace_before_checkout():
    """Self-hosted runners reuse $GITHUB_WORKSPACE; actions/checkout cleans the superproject only.
    Initialised submodule trees from other jobs must be wiped before the checkout step."""
    steps = _job(_load(VARIANTS["ghes"]["file"]))["steps"]
    names = [s.get("name", "") for s in steps]
    reset = next((i for i, s in enumerate(steps) if "submodule deinit --all --force" in s.get("run", "")), None)
    assert reset is not None, "expected a workspace-reset step running `git submodule deinit --all --force`"
    checkout = next(i for i, s in enumerate(steps) if str(s.get("uses", "")).startswith("actions/checkout"))
    assert reset < checkout, f"reset must run before checkout: {names}"
    run = steps[reset]["run"]
    assert "GITHUB_WORKSPACE" in run and "rm -rf" in run and ".git/modules" in run
