"""CI runner contracts — align with dx_app run_tc.sh / self-hosted gate."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

BROWSER_SUITE_PATHS = {
    "tests/i18n_audit/test_browser_copy_audit.py",
    "tests/test_toolbar_reachable_when_narrow.py",
    "tests/launcher/test_home_hierarchy_browser.py",
    "tests/launcher/test_home_draft_browser.py",
    "tests/launcher/test_home_workspace_browser.py",
    "tests/launcher/test_home_reattach_browser.py",
    "tests/launcher/test_home_density_browser.py",
    "tests/launcher/test_home_router_browser.py",
    "tests/launcher/test_home_icons_browser.py",
    "tests/launcher/test_boot_assets_browser.py",
    "tests/launcher/test_intro_stream_browser.py",
    "tests/launcher/test_intro_app_compile_browser.py",
    "tests/launcher/test_home_agent_run_browser.py",
    "tests/dx_agent_dev/test_attach_browser.py",
    "tests/dx_agent_dev/test_failed_run_badge_browser.py",
    "tests/launcher/test_home_stage_browser.py",
    "tests/launcher/test_home_widgets_browser.py",
    "tests/launcher/test_home_hero_browser.py",
    "tests/launcher/test_home_bar_browser.py",
    "tests/launcher/test_home_effects_browser.py",
    "tests/launcher/test_home_motion_browser.py",
    "tests/launcher/test_home_entry_browser.py",
    "tests/launcher/test_home_open_browser.py",
    "tests/launcher/test_home_tutorial_browser.py",
    "tests/shared/test_shared_chrome_browser.py",
    "tests/shared/test_text_contrast_browser.py",
    "tests/dx_app/test_setup_steps_browser.py",
    "tests/dx_stream/test_setup_steps_browser.py",
    "tests/dx_compiler/test_setup_steps_browser.py",
    "tests/shared/test_task_icons_browser.py",
    "tests/dx_app/test_rundemo_cards_browser.py",
    "tests/dx_app/test_outputs_lang_browser.py",
    "tests/dx_app/test_compare_browser.py",
    "tests/shared/test_toolbar_lang_a11y_browser.py",
    "tests/shared/test_chat_widget_lang_browser.py",
    "tests/shared/test_chat_local_provider_browser.py",
    "tests/dx_stream/test_pipeline_canvas_theme_browser.py",
    "tests/dx_app/test_reference_browser.py",
    "tests/dx_stream/test_reference_browser.py",
    "tests/dx_stream/test_stream_audit_browser.py",
    "tests/dx_stream/test_dashboard_live_browser.py",
    "tests/test_tutorial_placement_browser.py",
    "tests/dx_stream/test_demo_cards_browser.py",
    "tests/shared/test_icon_label_browser.py",
    "tests/launcher/test_sdk_library_module_nav_browser.py",
    "tests/launcher/test_connected_browsers_browser.py",
    "tests/shared/test_i18n_placeholder_merge_browser.py",
    "tests/launcher/test_escape_layers_browser.py",
    "tests/shared/test_browser_runtime.py",
    "tests/shared/test_font_rendering_browser.py",
    "tests/shared/test_demo_stage_browser.py",
    "tests/shared/test_hw_widget_rail_browser.py",
    "tests/dx_app/test_catalog_task_labels_browser.py",
    "tests/dx_app/test_lab_flows_browser.py",
    "tests/dx_app/test_rtsp_address_browser.py",
    "tests/dx_benchmark/test_phone_layout_browser.py",
    "tests/dx_compiler/test_compiler_audit_browser.py",
    "tests/dx_compiler/test_auto_compile_model_browser.py",
    "tests/dx_planner/test_lang_summary_browser.py",
    "tests/dx_planner/test_recommend_engine_browser.py",
    "tests/test_catalog_virtual_scroll_browser.py",
    "tests/test_iframe_lang_sync_browser.py",
    "tests/test_tutorial_stale_step.py",
    "tests/test_tutorial_e2e_journey.py",
    "tests/test_tutorial_spotlight_spot_check.py",
    "tests/test_ux_visual_gate.py",
    "tests/test_zoom_full_audit.py",
    "tests/test_zoom_layout_contracts.py",
    "tests/test_zoom_modal_audit.py",
}


def test_run_ci_script_exists_and_executable():
    script = ROOT / "scripts" / "run_ci.sh"
    assert script.is_file()
    text = script.read_text(encoding="utf-8")
    assert "tests/launcher/" in text
    assert "tests/dx_agent_dev/" in text
    assert "i18n_audit_gate.sh" in text


def test_release_ver_matches_studio_version_ssot():
    release_ver = (ROOT / "release.ver").read_text(encoding="utf-8").strip()
    studio_js = (ROOT / "shared" / "static" / "studio-version.js").read_text(encoding="utf-8")
    assert release_ver.startswith("v")
    semver = release_ver.lstrip("v")
    assert f"semver: '{semver}'" in studio_js


def test_ci_workflow_uses_self_hosted_runner():
    workflow = (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-pytest.yml"
    ).read_text(encoding="utf-8")
    assert "self-hosted" in workflow
    assert "run_ci.sh" in workflow
    assert "ubuntu-latest" not in workflow
    assert "ci-browser-smoke" not in workflow


def test_i18n_smoke_workflow_is_manual_dispatch_only():
    workflow = (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-i18n-audit.yml"
    ).read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "pull_request:" not in workflow


def test_run_ci_excludes_browser_tests_from_default_gate():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert "BROWSER_TESTS=(" in script
    missing = sorted(path for path in BROWSER_SUITE_PATHS if path not in script)
    assert not missing, f"Browser suite inventory is incomplete: {missing}"
    assert '"${IGNORE_BROWSER[@]}"' in script
    assert 'RUN_BROWSER=1' in script or "--browser" in script


def test_every_playwright_suite_is_registered_as_a_browser_suite():
    """playwright 를 쓰는 테스트 파일은 전부 BROWSER_TESTS 에 올라와 있어야 한다.

    인벤토리는 손으로 관리되는 목록이고, 지금까지 "목록의 항목이 스크립트에 있는가"
    만 검사했다. 반대 방향 — 디스크의 브라우저 스위트가 목록에 있는가 — 은 아무도
    보지 않았고, 그래서 새 브라우저 테스트가 조용히 게이트 밖에 남을 수 있었다.
    실제로 2026-09 에 두 개가 그렇게 새어 있었다(`test_tutorial_stale_step.py`,
    `test_catalog_virtual_scroll_browser.py`). 등록되지 않으면 --browser 로 돌지
    않고, 대신 기본 게이트의 공유 pytest 프로세스에서 브라우저를 띄우게 된다 —
    이 파일 맨 위 주석이 피하려던 바로 그 상황이다.
    """
    import re

    pattern = re.compile(r"importorskip\(\s*[\"']playwright|from playwright|^import playwright", re.M)
    offenders = []
    for path in sorted((ROOT / "tests").rglob("*.py")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in BROWSER_SUITE_PATHS:
            continue
        parts = path.relative_to(ROOT).parts
        # conftest / 헬퍼 / 자기 자신 / 별도 게이트로 도는 디렉토리는 제외
        if path.name in ("conftest.py", "server_helpers.py", "tutorial_e2e_runner.py"):
            continue
        if rel == "tests/shared/test_ci_contracts.py":
            continue
        if "visual" in parts or "e2e" in parts:
            continue
        if pattern.search(path.read_text(encoding="utf-8", errors="replace")):
            offenders.append(rel)
    assert not offenders, (
        "playwright 를 쓰는데 BROWSER_TESTS 에 등록되지 않았다: "
        + ", ".join(offenders)
    )


def test_run_ci_prefilters_explicit_root_browser_paths():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    stage_five = script.split('== 5/7 Module + shared + root contract suites (no browser) ==', 1)[1]

    assert "ROOT_TESTS=()" in script
    assert "for _root_test in tests/test_*.py; do" in script
    assert 'if [[ "$_root_test" == "$_bt" ]]; then' in script
    assert '"${ROOT_TESTS[@]}"' in stage_five
    assert "tests/test_*.py" not in stage_five


def test_run_ci_runs_browser_suites_in_isolated_pytest_processes():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert 'for _bt in "${BROWSER_TESTS[@]}"; do' in script
    assert '"$PY" -m pytest "$_bt" -q --tb=short' in script


def test_i18n_browser_audit_uses_test_interpreter_without_forced_browser_download():
    script = (ROOT / "scripts" / "i18n_browser_audit.sh").read_text(encoding="utf-8")
    assert '"$VENV_PYTHON" -c "import playwright"' in script
    assert "playwright install chromium" not in script


def test_ci_dependency_manifest_covers_collection_dependencies():
    manifest = ROOT / "requirements-ci.txt"
    assert manifest.is_file()

    package_names = {
        line.split(";", 1)[0].split("[", 1)[0]
        .split("<", 1)[0].split(">", 1)[0].split("=", 1)[0]
        .strip().lower()
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }

    assert {
        "pytest", "numpy", "onnx", "pillow", "playwright", "jinja2", "cffi",
        "fonttools", "brotli",
    } <= package_names


def test_run_ci_runs_inference_e2e_gate_isolated():
    """The inference triple gate blocks merges and MUST run in its own process.

    tests/e2e/conftest.py rebinds DX_APP_ROOT at import time and dx_app.core.config
    freezes its paths on first import, so sharing a pytest process with the module
    suites would pin the wrong tree for one of them.
    """
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert '"$PY" -m pytest tests/e2e/ -q --tb=short -m e2e_mock' in script, (
        "run_ci.sh must run the e2e_mock tier as a blocking stage"
    )
    stage = script.split("== 6/7 Inference E2E triple gate", 1)
    assert len(stage) == 2, "the inference E2E gate must be a numbered stage"
    # It must NOT be inside the optional --browser / --coverage / --ux blocks.
    assert script.index("== 6/7 Inference E2E triple gate") < script.index(
        'if [ "$RUN_COVERAGE" = "1" ]; then'
    ), "the inference E2E gate must be blocking, not an opt-in extra"


def test_run_ci_excludes_e2e_from_shared_process_stages():
    """The collection gate and the module stage must not import tests/e2e."""
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    collection = script.split("== 1/7 Collection gate ==", 1)[1].split("== 2/7", 1)[0]
    module_stage = script.split("== 5/7 Module", 1)[1].split("== 6/7", 1)[0]
    for name, chunk in (("collection gate", collection), ("module stage", module_stage)):
        assert "--ignore=tests/e2e" in chunk, (
            f"{name} must --ignore=tests/e2e (its conftest rebinds DX_APP_ROOT)"
        )


# Pre-existing failures deselected from the blocking gate. This list is a debt
# ledger: it may SHRINK, never grow. Adding an entry means a new regression was
# waved through, which is exactly what the gate exists to prevent.
QUARANTINED: set[str] = set()


def _quarantined_in_script() -> set:
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    block = script.split("QUARANTINE=(", 1)[1].split(")", 1)[0]
    return {
        ln.strip().removeprefix("--deselect").strip()
        for ln in block.splitlines()
        if ln.strip().startswith("--deselect")
    }


# 브라우저 스테이지의 quarantine. 블로킹 쪽과 같은 규율을 받는다 — 줄어들 수만
# 있고, 각 항목은 docs/testing.md 에 근거와 함께 적혀야 하며, 낡은 항목은 실패한다.
# 이 목록이 생기기 전에는 스테이지 전체가 advisory 였고, 그래서 빨간불이 상시
# 상태였다. 상시 빨강은 신호가 아니라 배경이라, 새 회귀가 그 안에 묻힌다.
BROWSER_QUARANTINED: set[str] = set()


def _browser_quarantined_in_script() -> set:
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    block = script.split("BROWSER_QUARANTINE=(", 1)[1].split("\n  )", 1)[0]
    return {
        ln.strip().removeprefix("--deselect").strip().strip('"')
        for ln in block.splitlines()
        if ln.strip().startswith("--deselect")
    }


def test_browser_quarantine_never_grows():
    """브라우저 쪽 부채도 늘어날 수 없다."""
    added = _browser_quarantined_in_script() - BROWSER_QUARANTINED
    assert not added, (
        "브라우저 quarantine 에 항목이 추가됐다 — 회귀가 게이트를 통과했다는 뜻이다: "
        f"{sorted(added)}"
    )


def test_browser_quarantine_entries_are_documented():
    doc = (ROOT / "docs" / "testing.md").read_text(encoding="utf-8")
    # 파라미터까지 포함한 전체 이름을 요구한다. 모듈 이름만 보면 "dx_modelzoo" 가
    # 문서 곳곳에 있어 무엇이든 통과한다 — 처음 쓸 때 실제로 그렇게 통과했다.
    undocumented = sorted(
        n for n in _browser_quarantined_in_script() if n.split("::")[-1] not in doc
    )
    assert not undocumented, (
        "docs/testing.md 에 근거가 없는 브라우저 quarantine 항목: " + str(undocumented)
    )


def test_browser_quarantine_entries_still_exist():
    for node in _browser_quarantined_in_script():
        path = ROOT / node.split("::", 1)[0]
        assert path.is_file(), f"quarantine 된 파일이 사라졌다, 목록에서 지워라: {node}"
        func = node.split("::")[-1].split("[")[0]
        assert f"def {func}(" in path.read_text(encoding="utf-8"), (
            f"quarantine 된 테스트가 사라졌다, 목록에서 지워라: {node}"
        )


def test_quarantine_list_never_grows():
    """The gate's deselect list is a debt ledger — it may shrink, never grow."""
    actual = _quarantined_in_script()
    added = actual - QUARANTINED
    assert not added, (
        "New entries added to the run_ci.sh quarantine — a regression was waved "
        f"through the blocking gate: {sorted(added)}"
    )


def test_quarantine_entries_are_documented():
    """Every quarantined test must be listed in docs/testing.md with a reason."""
    actual = _quarantined_in_script()
    doc = (ROOT / "docs" / "testing.md").read_text(encoding="utf-8")
    undocumented = sorted(n for n in actual if n.split("::")[-1] not in doc)
    assert not undocumented, (
        "Quarantined tests missing from docs/testing.md: " + str(undocumented)
    )


def test_testing_doc_describes_the_visual_suite_that_exists():
    """docs/testing.md must not drift from tests/visual/baseline_spec.py.

    It had: "each module's landing page at 1280x800" compared against
    `baselines/<engine>/<module>.png`, and 36 + 18 shots. Reality by then was
    two naming schemes, four responsive widths and 72 files — the doc was
    describing the suite as it stood two expansions earlier.

    A reader trusts a testing doc precisely when they cannot yet read the
    harness, so a stale one costs more than no doc. Pinning the numbers that
    actually changed (the widths and the total) keeps the prose honest without
    freezing how it is worded.
    """
    from tests.visual import baseline_spec as spec

    doc = (ROOT / "docs" / "testing.md").read_text(encoding="utf-8")
    section = doc.split("### Pixel visual regression", 1)[1].split("\n## ", 1)[0]

    baselines = sorted((ROOT / "tests" / "visual" / "baselines").rglob("*.png"))
    assert baselines, "no baselines on disk"
    assert str(len(baselines)) in section, (
        f"the doc does not state the real baseline count ({len(baselines)})"
    )

    for width in spec.RESPONSIVE_WIDTHS:
        assert str(width) in section, f"responsive width {width} is undocumented"

    # Both naming schemes, because a reader looking for a file needs the shape.
    assert "__<theme>__<locale>.png" in section
    assert "__w<width>.png" in section

    # The suite skips the intro on purpose; a doc that omits that oversells it.
    assert "dx-splash-seen" in section, (
        "the doc does not say the capture skips the intro, so a green visual run "
        "reads as covering an animation it never photographs"
    )


def test_quarantined_tests_still_exist():
    """A quarantined node id that no longer resolves is stale — drop it from the list."""
    for node in _quarantined_in_script():
        path = ROOT / node.split("::", 1)[0]
        assert path.is_file(), f"quarantined test file is gone, remove it: {node}"
        func = node.split("::")[-1]
        assert f"def {func}(" in path.read_text(encoding="utf-8"), (
            f"quarantined test no longer exists, remove it from run_ci.sh: {node}"
        )


def _coveragerc_sources() -> set:
    """Module names declared under [run] source in .coveragerc."""
    text = (ROOT / ".coveragerc").read_text(encoding="utf-8")
    body = text.split("source", 1)[1].split("omit", 1)[0]
    return {
        ln.strip()
        for ln in body.splitlines()
        if ln.strip() and not ln.strip().startswith(("=", "[", "#"))
    }


def test_coverage_measures_from_a_single_root_so_paths_stay_qualified():
    """coverage.xml must keep the module in every path.

    Supersedes the old "measure all ten declared sources" contract. Ten `source`
    roots (or ten `--cov=<pkg>` flags, which OVERRIDE the config) make coverage.py
    strip whichever root a file came from, so all nine modules' `server.py`
    render as filename="server.py" and collapse into ONE entry in coverage.xml —
    measured: 9 distinct files on disk and in the terminal report, 1 in the XML.
    SonarQube then attributes that entry to whichever root resolves first and
    reports the other eight at 0%.

    The fix is a single root plus relative_files, which yields
    filename="dx_app/server.py" and is also what coverage_gate.py splits on.
    """
    cfg = (ROOT / ".coveragerc").read_text(encoding="utf-8")
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")

    assert "source = ." in cfg, ".coveragerc must declare exactly one source root"
    assert "relative_files = True" in cfg, (
        "without relative_files the XML carries this machine's absolute paths, "
        "which do not resolve on the CI runner"
    )

    block = script.split("COV_ARGS=(", 1)[1].split(")", 1)[0]
    cov_flags = {tok.split("=", 1)[1] for tok in block.split() if tok.startswith("--cov=")}
    assert cov_flags == {"."}, (
        f"--cov must name the repo root and nothing else, got {sorted(cov_flags)} — "
        "a per-package flag overrides .coveragerc's source and re-creates the collapse"
    )


def test_coverage_omits_the_non_module_directories():
    """`source = .` measures everything under the root, so the non-modules must be
    named — otherwise `tools` and `scripts` appear as modules in the per-module
    baseline and the gate starts tracking things nobody ships."""
    cfg = (ROOT / ".coveragerc").read_text(encoding="utf-8")
    for path in ("tests/*", "tools/*", "scripts/*", "docs/*", "var/*", "outputs/*"):
        assert path in cfg, f".coveragerc must omit {path}"


def test_every_shipped_module_is_still_covered_by_the_baseline():
    """The single-root switch must not silently drop a module from the ledger.

    "Shipped" is taken from pyproject's package list — the actual install
    manifest — rather than "any dir with an __init__.py", which also matches
    tests/ and would demand a baseline for the test tree itself.
    """
    import json
    import tomllib

    baseline = json.loads(
        (ROOT / "config" / "coverage_baseline.json").read_text(encoding="utf-8")
    )
    with (ROOT / "pyproject.toml").open("rb") as fh:
        packages = tomllib.load(fh)["tool"]["setuptools"]["packages"]
    shipped = {pkg.split(".", 1)[0] for pkg in packages}

    missing = sorted(shipped - set(baseline))
    assert not missing, f"shipped package with no coverage baseline entry: {missing}"

    stale = sorted(set(baseline) - shipped)
    assert not stale, f"baseline tracks something that is not shipped: {stale}"


def test_coverage_uses_append_across_isolated_processes():
    """launcher/dx_agent_dev/e2e cannot share a pytest process, so coverage must append."""
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    cov_block = script.split("== Optional: Python coverage", 1)[1]
    assert cov_block.count("--cov-append") >= 3, (
        "each isolated coverage run after the first must --cov-append, "
        "otherwise it overwrites the previous run's data"
    )
    assert "scripts/coverage_gate.py" in cov_block, (
        "coverage must be compared against config/coverage_baseline.json"
    )


def test_browser_suites_support_sharding():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert "--shard=*)" in script, "run_ci.sh must accept --shard=i/N"
    assert "SHARD_TOTAL" in script and "_shard_suites" in script
    # The i18n copy audit is indivisible — it must not run once per shard.
    assert 'if [ "$SHARD_INDEX" = "1" ]; then' in script, (
        "the i18n browser audit must be pinned to one shard"
    )


def test_cross_browser_and_coverage_jobs_are_advisory():
    """Staged rollout: only the run_ci.sh gate blocks a merge for now."""
    workflow = (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-pytest.yml"
    ).read_text(encoding="utf-8")
    for job in ("cross-browser:", "visual:", "coverage:"):
        assert job in workflow, f"{job} job missing from the PR workflow"
    assert workflow.count("continue-on-error: true") == 3, (
        "exactly the three advisory jobs (cross-browser, visual, coverage) may be "
        "continue-on-error — the pytest gate must block"
    )
    # Report-only coverage stays green through a drop, which is the same as not
    # running it. Advisory means "does not block", not "does not notice".
    assert "DX_COVERAGE_ENFORCE: '1'" in workflow
    assert "DX_BROWSER_ENGINES: chromium,firefox" in workflow
    assert "playwright-traces-shard-" in workflow, (
        "failure traces must be uploaded as artifacts (Trace Viewer)"
    )


def _npu_workflow() -> str:
    return (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-npu.yml"
    ).read_text(encoding="utf-8")


def test_npu_workflow_runs_on_hardware_runner():
    workflow = _npu_workflow()
    assert "self-hosted" in workflow
    assert "run_ci.sh --npu" in workflow
    assert "ubuntu-latest" not in workflow


def test_npu_workflow_is_scheduled_and_opt_in_not_a_blocking_pr_gate():
    """The hardware tier must never gate every PR.

    One DX-M1 backs it, so making every merge depend on that board's health is
    exactly the fragility the mock tier exists to avoid. It may run on a schedule,
    on demand, and on a PR that explicitly opts in with the `run-npu` label.
    """
    workflow = _npu_workflow()
    assert "schedule:" in workflow, "the hardware tier must run on a schedule"
    assert "workflow_dispatch:" in workflow
    assert "types: [labeled]" in workflow, (
        "pull_request must be limited to `labeled`, otherwise every PR waits on the NPU"
    )
    assert "github.event.label.name == 'run-npu'" in workflow, (
        "the PR path must be gated on the opt-in label"
    )


def test_npu_workflow_serialises_on_the_single_board():
    """Two concurrent runs would contend for the one NPU."""
    workflow = _npu_workflow()
    assert "group: dx-ai-studio-npu" in workflow
    assert "cancel-in-progress: false" in workflow


def test_run_ci_npu_stage_cannot_silently_skip():
    """`--npu` must set DX_E2E_NPU_STRICT=1.

    pytest exits 0 when every test skips, so a scheduled hardware job on a board
    with a dead NPU would report green while proving nothing — the precise failure
    this tier exists to close. Strict mode turns that skip into a failure.
    """
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert "--npu) RUN_NPU=1 ;;" in script
    npu_stage = script.split('if [ "$RUN_NPU" = "1" ]; then', 1)
    assert len(npu_stage) == 2, "run_ci.sh must have an --npu stage"
    stage = npu_stage[1]
    assert "DX_E2E_NPU_STRICT=1" in stage
    assert "-m e2e_npu" in stage
    assert "DX_E2E_NPU_MODEL" in stage, "the stage must refuse to run without a model"


def test_blocking_pr_gate_does_not_depend_on_the_npu():
    """The merge-blocking workflow must stay hardware-independent."""
    workflow = (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-pytest.yml"
    ).read_text(encoding="utf-8")
    assert "--npu" not in workflow
    assert "e2e_npu" not in workflow


# --- pixel visual regression -------------------------------------------------

VISUAL_BASELINE_DIR = ROOT / "tests" / "visual" / "baselines"


def test_run_ci_has_an_advisory_visual_stage():
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    assert "--visual) RUN_VISUAL=1 ;;" in script
    assert '"$PY" -m pytest tests/visual/ -q --tb=short -m visual' in script
    # It must sit behind the flag, never in the default blocking path. The
    # blocking part is everything before the FIRST optional block.
    first_optional = min(
        script.index('if [ "$%s" = "1" ]; then' % flag)
        for flag in ("RUN_VISUAL", "RUN_NPU", "RUN_COVERAGE", "RUN_BROWSER", "RUN_UX")
    )
    default_gate = script[:first_optional]
    assert "tests/visual/" not in default_gate, (
        "the visual suite must stay opt-in — baselines are per-host, so it cannot "
        "gate a merge"
    )


def test_visual_baselines_are_committed_for_the_default_engine():
    """A suite with no baselines skips every test and reports green.

    Baselines are captured per (module, theme, locale): a single-axis set would
    let a light-theme or long-translation regression through unnoticed.
    """
    from tests.browser_support import DEFAULT_ENGINE
    from tests.visual.baseline_spec import axes, baseline_name

    engine_dir = VISUAL_BASELINE_DIR / DEFAULT_ENGINE
    assert engine_dir.is_dir(), f"no baselines for {DEFAULT_ENGINE}"
    missing = sorted(
        baseline_name(*combo)
        for combo in axes()
        if not (engine_dir / baseline_name(*combo)).is_file()
    )
    assert not missing, (
        f"axes with no {DEFAULT_ENGINE} baseline: {missing} "
        "(create with DX_VISUAL_UPDATE=1 pytest tests/visual/)"
    )


def test_visual_baselines_have_no_orphans():
    """A baseline for an axis no longer captured is never compared — drop it.

    Stale files are worse than missing ones: they look like coverage in the
    directory listing while nothing ever reads them.
    """
    from tests.visual.baseline_spec import (
        INTRO_STATES,
        axes,
        baseline_name,
        intro_baseline_name,
        responsive_axes,
        responsive_baseline_name,
    )

    expected = {baseline_name(*combo) for combo in axes()}
    expected |= {responsive_baseline_name(*combo) for combo in responsive_axes()}
    expected |= {intro_baseline_name(state) for state in INTRO_STATES}
    for engine_dir in VISUAL_BASELINE_DIR.glob("*"):
        if not engine_dir.is_dir():
            continue
        orphans = sorted(p.name for p in engine_dir.glob("*.png") if p.name not in expected)
        assert not orphans, f"{engine_dir.name}: baselines with no axis entry: {orphans}"


def test_mock_e2e_stage_is_hermetic_against_npu_env():
    """Stage 6 must ignore ambient DX_E2E_NPU_* vars.

    tests/e2e/conftest.py binds DX_APP_ROOT at import time and selects the NPU
    overlay whenever DX_E2E_NPU_MODEL is set. Without stripping them, running
    `run_ci.sh --npu` fails its own BLOCKING stage — the mock tier goes looking for
    its fixture model in the real dx_app tree ("model 'e2eyolo' is not in
    /api/models"). The blocking gate cannot depend on what the caller exported.
    """
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    stage = script.split("== 6/7 Inference E2E triple gate", 1)[1].split("if [", 1)[0]
    for var in ("DX_E2E_NPU_MODEL", "DX_E2E_NPU_MODEL_FILE", "DX_E2E_NPU_STRICT"):
        assert f"-u {var}" in stage, (
            f"the mock stage must run with {var} unset (env -u) so it stays hermetic"
        )
    assert "-m e2e_mock" in stage

# --- SonarQube ---------------------------------------------------------------


def _sonar_properties() -> dict:
    text = (ROOT / "sonar-project.properties").read_text(encoding="utf-8")
    # Join the backslash continuations the exclusion lists use.
    text = text.replace("\\\n", "")
    out = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def test_sonar_properties_never_commits_an_endpoint_or_token():
    """The host and credentials belong in secrets, not in the repo."""
    props = _sonar_properties()
    for forbidden in ("sonar.host.url", "sonar.token", "sonar.login", "sonar.password"):
        assert forbidden not in props, (
            f"{forbidden} must be passed at scan time, never committed"
        )


def test_sonar_sources_match_the_shipped_packages():
    """A module missing from sonar.sources is silently never analysed."""
    import tomllib

    props = _sonar_properties()
    with (ROOT / "pyproject.toml").open("rb") as fh:
        packages = tomllib.load(fh)["tool"]["setuptools"]["packages"]
    shipped = {pkg.split(".", 1)[0] for pkg in packages}
    declared = {s.strip() for s in props["sonar.sources"].split(",") if s.strip()}
    assert declared == shipped, (
        f"sonar.sources drifted from pyproject packages: "
        f"missing={sorted(shipped - declared)} extra={sorted(declared - shipped)}"
    )
    for src in declared:
        assert (ROOT / src).is_dir(), f"sonar.sources names a missing directory: {src}"


def test_sonar_reads_the_coverage_report_run_ci_actually_writes():
    props = _sonar_properties()
    script = (ROOT / "scripts" / "run_ci.sh").read_text(encoding="utf-8")
    report = props["sonar.python.coverage.reportPaths"]
    assert f"--cov-report=xml:{report}" in script, (
        f"sonar expects {report}, which run_ci.sh --coverage must produce"
    )


def test_sonar_carries_no_version_copy():
    """release.ver is the SSOT; a second copy here drifts silently."""
    props = _sonar_properties()
    assert "sonar.projectVersion" not in props


def test_sonar_excludes_vendored_and_generated_assets():
    """Without these the first report is thousands of findings in code nobody
    maintains, which buries the real ones."""
    props = _sonar_properties()
    exclusions = props["sonar.exclusions"]
    for pattern in ("**/static/vendor/**", "**/*.min.js", "**/static/js/i18n.js", "**/.venv/**"):
        assert pattern in exclusions, f"sonar.exclusions must cover {pattern}"


def test_sonar_workflow_is_a_noop_without_secrets():
    """Hard-coding a guessed endpoint would fail every PR; the job must skip."""
    workflow = (
        ROOT.parent / ".github" / "workflows" / "dx-ai-studio-sonar.yml"
    ).read_text(encoding="utf-8")
    assert "secrets.SONAR_HOST_URL" in workflow
    assert "secrets.SONAR_TOKEN" in workflow
    assert "enabled=false" in workflow, "the job must detect missing secrets and skip"
    assert workflow.count("steps.check.outputs.enabled == 'true'") >= 4, (
        "every step that needs the server must be gated on the secret check"
    )
    assert "continue-on-error: true" in workflow, (
        "Sonar stays advisory until its first backlog is triaged"
    )
    assert "self-hosted" in workflow and "ubuntu-latest" not in workflow
