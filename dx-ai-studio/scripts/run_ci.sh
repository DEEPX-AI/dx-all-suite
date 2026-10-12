#!/usr/bin/env bash
# DX AI Studio CI runner — dx_app/run_tc.sh 패턴 (폐쇄망 self-hosted PR gate).
#
# Usage:
#   bash scripts/run_ci.sh              # blocking PR gate (default)
#   bash scripts/run_ci.sh --coverage # + Python coverage report (non-blocking threshold)
#   bash scripts/run_ci.sh --browser    # + Playwright browser/UX audits (needs chromium)
#   bash scripts/run_ci.sh --ux         # + full UX acceptance gate (slow, release only)
#   bash scripts/run_ci.sh --npu        # + real-NPU inference tier (nightly / run-npu)
#   bash scripts/run_ci.sh --visual     # + pixel visual-regression vs committed baselines
#   bash scripts/run_ci.sh --offline    # + blocking suite with external network blocked
#   bash scripts/run_ci.sh --browser --shard=1/3   # browser suites, shard 1 of 3
#
# Cross-browser is env-driven: DX_BROWSER_ENGINES=chromium,firefox[,webkit].
# Default is chromium alone so the blocking gate stays single-engine and fast.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

RUN_COVERAGE=0
RUN_BROWSER=0
RUN_UX=0
RUN_NPU=0
RUN_VISUAL=0
RUN_OFFLINE=0
SHARD_INDEX=""
SHARD_TOTAL=""

for arg in "$@"; do
  case "$arg" in
    --coverage) RUN_COVERAGE=1 ;;
    --browser) RUN_BROWSER=1 ;;
    --ux) RUN_UX=1 ;;
    --npu) RUN_NPU=1 ;;
    --visual) RUN_VISUAL=1 ;;
    --offline) RUN_OFFLINE=1 ;;
    --shard=*)
      _spec="${arg#--shard=}"
      SHARD_INDEX="${_spec%%/*}"
      SHARD_TOTAL="${_spec##*/}"
      case "$SHARD_INDEX/$SHARD_TOTAL" in
        [1-9]*/[1-9]*) ;;
        *) echo "--shard expects i/N with 1-based i (got '$_spec')" >&2; exit 2 ;;
      esac
      if [ "$SHARD_INDEX" -gt "$SHARD_TOTAL" ]; then
        echo "--shard index $SHARD_INDEX exceeds total $SHARD_TOTAL" >&2; exit 2
      fi
      ;;
    -h|--help)
      # Print the whole leading comment block, so a newly added flag shows up in
      # --help without anyone remembering to bump a hard-coded line range.
      sed -n '2,/^set -euo pipefail/p' "$0" | sed '/^set -euo pipefail/d'
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      exit 2
      ;;
  esac
done

# Prefer the project venv's interpreter if present (so no `source activate` needed);
# fall back to system python3. Test deps must already be installed there — this gate
# never pip-installs (air-gapped-safe). Export so sub-gate scripts inherit the choice.
PY="${VENV_PYTHON:-$ROOT/.venv/bin/python}"
[ -x "$PY" ] || PY=python3
export VENV_PYTHON="$PY"
if ! "$PY" -c "import pytest" 2>/dev/null; then
  echo "pytest not found in: $PY" >&2
  echo "Install test deps first (once):  $PY -m pip install -r requirements-ci.txt" >&2
  echo "(or create the venv:  python3 -m venv .venv && ./.venv/bin/pip install -r requirements-ci.txt)" >&2
  exit 1
fi

# Playwright browser suites — excluded from the default PR gate. Browser suites are
# run individually with --browser because sync Playwright owns an event loop per
# process; sharing one pytest process lets one suite contaminate another's loop.
BROWSER_TESTS=(
  tests/i18n_audit/test_browser_copy_audit.py
  tests/launcher/test_home_hierarchy_browser.py
  tests/launcher/test_home_draft_browser.py
  tests/launcher/test_home_workspace_browser.py
  tests/launcher/test_home_reattach_browser.py
  tests/launcher/test_home_density_browser.py
  tests/launcher/test_home_router_browser.py
  tests/launcher/test_home_icons_browser.py
  tests/launcher/test_boot_assets_browser.py
  tests/launcher/test_intro_stream_browser.py
  tests/launcher/test_intro_app_compile_browser.py
  tests/launcher/test_home_agent_run_browser.py
  tests/dx_agent_dev/test_attach_browser.py
  tests/dx_agent_dev/test_failed_run_badge_browser.py
  tests/launcher/test_home_stage_browser.py
  tests/launcher/test_home_widgets_browser.py
  tests/launcher/test_home_hero_browser.py
  tests/launcher/test_home_bar_browser.py
  tests/launcher/test_home_effects_browser.py
  tests/launcher/test_home_motion_browser.py
  tests/launcher/test_home_entry_browser.py
  tests/launcher/test_home_open_browser.py
  tests/launcher/test_home_tutorial_browser.py
  tests/shared/test_shared_chrome_browser.py
  tests/shared/test_text_contrast_browser.py
  tests/shared/test_accessible_names_browser.py
  tests/launcher/test_home_facts_deferred_browser.py
  tests/shared/test_browser_language_default_browser.py
  tests/dx_agent_dev/test_studio_agent_console_browser.py
  tests/launcher/test_home_studio_agent_browser.py
  tests/launcher/test_home_posters_keyboard_browser.py
  tests/shared/test_chat_settings_browser.py
  tests/dx_app/test_setup_steps_browser.py
  tests/dx_stream/test_setup_steps_browser.py
  tests/dx_compiler/test_setup_steps_browser.py
  tests/shared/test_task_icons_browser.py
  tests/dx_app/test_rundemo_cards_browser.py
  tests/dx_app/test_outputs_lang_browser.py
  tests/dx_app/test_compare_browser.py
  tests/shared/test_toolbar_lang_a11y_browser.py
  tests/shared/test_chat_widget_lang_browser.py
  tests/shared/test_chat_local_provider_browser.py
  tests/dx_stream/test_pipeline_canvas_theme_browser.py
  tests/dx_app/test_reference_browser.py
  tests/dx_stream/test_reference_browser.py
  tests/dx_stream/test_stream_audit_browser.py
  tests/dx_stream/test_dashboard_live_browser.py
  tests/test_tutorial_placement_browser.py
  tests/dx_stream/test_demo_cards_browser.py
  tests/shared/test_icon_label_browser.py
  tests/launcher/test_sdk_library_module_nav_browser.py
  tests/launcher/test_connected_browsers_browser.py
  tests/shared/test_i18n_placeholder_merge_browser.py
  tests/launcher/test_escape_layers_browser.py
  tests/shared/test_browser_runtime.py
  tests/shared/test_font_rendering_browser.py
  tests/shared/test_demo_stage_browser.py
  tests/shared/test_hw_widget_rail_browser.py
  tests/dx_app/test_catalog_task_labels_browser.py
  tests/dx_app/test_lab_flows_browser.py
  tests/dx_app/test_rtsp_address_browser.py
  tests/dx_benchmark/test_phone_layout_browser.py
  tests/dx_compiler/test_compiler_audit_browser.py
  tests/dx_compiler/test_auto_compile_model_browser.py
  tests/dx_planner/test_lang_summary_browser.py
  tests/dx_planner/test_recommend_engine_browser.py
  tests/dx_planner/test_recommend_explain_browser.py
  tests/test_catalog_virtual_scroll_browser.py
  tests/test_iframe_lang_sync_browser.py
  tests/test_toolbar_reachable_when_narrow.py
  tests/test_tutorial_stale_step.py
  tests/test_tutorial_e2e_journey.py
  tests/test_tutorial_spotlight_spot_check.py
  tests/test_ux_visual_gate.py
  tests/test_zoom_full_audit.py
  tests/test_zoom_layout_contracts.py
  tests/test_zoom_modal_audit.py
)
IGNORE_BROWSER=()
for _bt in "${BROWSER_TESTS[@]}"; do
  IGNORE_BROWSER+=(--ignore="$_bt")
done

# Pytest's --ignore does not override an explicitly supplied test path. The
# root-level glob below expands before pytest runs, so remove browser suites
# before handing root test paths to the default non-browser gate.
ROOT_TESTS=()
for _root_test in tests/test_*.py; do
  _is_browser_test=0
  for _bt in "${BROWSER_TESTS[@]}"; do
    if [[ "$_root_test" == "$_bt" ]]; then
      _is_browser_test=1
      break
    fi
  done
  if [ "$_is_browser_test" = "0" ]; then
    ROOT_TESTS+=("$_root_test")
  fi
done

echo "== CSS token ratchet =="
"$PY" scripts/css_token_gate.py || exit 1

echo "== i18n lang-span ratchet =="
"$PY" -m scripts.i18n_span_gate || exit 1

echo "== breakpoint ratchet =="
"$PY" -m scripts.breakpoint_gate || exit 1

echo "== 간격 스케일 ratchet =="
"$PY" -m scripts.spacing_scale_gate || exit 1

echo "== UI 이모지 ratchet =="
"$PY" -m scripts.emoji_gate || exit 1

echo "== 글꼴 coverage (한중일 subset) =="
"$PY" -m scripts.font_coverage_gate || exit 1

echo ""
echo "== 0/7 Infra + release contracts =="
"$PY" -m pytest \
  tests/test_pytest_infra_contract.py \
  tests/shared/test_ci_contracts.py \
  tests/shared/test_studio_version_contracts.py \
  tests/release/ \
  -q --tb=short

echo ""
echo "== 1/7 Collection gate =="
"$PY" -m pytest tests/ --collect-only -q \
  --ignore=tests/dx_stream/benchmark \
  --ignore=tests/e2e \
  "${IGNORE_BROWSER[@]}"

echo ""
echo "== 2/7 Launcher suite (isolated — port collision) =="
"$PY" -m pytest tests/launcher/ -q --tb=short "${IGNORE_BROWSER[@]}"

echo ""
echo "== 3/7 Agent Dev suite (isolated — port collision) =="
"$PY" -m pytest tests/dx_agent_dev/ -q --tb=short

echo ""
echo "== 4/7 i18n audit gate =="
bash scripts/i18n_audit_gate.sh

echo ""
# Pre-existing failures quarantined from the BLOCKING gate. Each one is a real
# content/upstream defect that needs a product decision, NOT a skip guard — so they
# are deselected here (visible, greppable, counted) instead of being silenced inside
# the test files. tests/shared/test_ci_contracts.py pins the size of this list, so it
# can only ever SHRINK. See docs/testing.md "Quarantined pre-existing failures".
# 비어 있다. 2026-09-16 에 마지막 항목(yolo26_depth legal)이 해제됐다 — 상류에
# 데이터가 없는 것이 아니라 generated_catalog.json 이 그 모델들의 공개 이전 산출물이었고,
# studio id 가 생성 id 의 해상도 접미사와 매칭되지 않았다. docs/testing.md 참조.
QUARANTINE=()

echo "== 5/7 Module + shared + root contract suites (no browser) =="
"$PY" -m pytest \
  tests/dx_app/ \
  tests/dx_stream/ \
  tests/dx_compiler/ \
  tests/dx_modelzoo/ \
  tests/dx_planner/ \
  tests/dx_benchmark/ \
  tests/dx_monitor/ \
  tests/shared/ \
  tests/i18n_audit/ \
  "${ROOT_TESTS[@]}" \
  -q \
  --ignore=tests/dx_stream/benchmark \
  --ignore=tests/e2e \
  "${IGNORE_BROWSER[@]}" \
  "${QUARANTINE[@]}" \
  --tb=short

echo ""
echo "== 6/7 Inference E2E triple gate (e2e_mock, isolated) =="
# Own pytest process on purpose: tests/e2e/conftest.py rebinds DX_APP_ROOT at
# import time (and dx_app.core.config freezes paths on first import), so sharing
# a process with the module suites would pin the wrong tree for one of them.
# Skips itself when playwright/chromium are unavailable rather than failing.
# `env -u` is load-bearing, not defensive: tests/e2e/conftest.py binds DX_APP_ROOT
# at import time and picks the NPU overlay whenever DX_E2E_NPU_MODEL is set. Running
# `run_ci.sh --npu` therefore used to fail THIS stage — the mock tier looked for its
# fixture model in the real dx_app tree ("model 'e2eyolo' is not in /api/models").
# The blocking stage must be hermetic no matter what the caller exported.
env -u DX_E2E_NPU_MODEL -u DX_E2E_NPU_MODEL_FILE -u DX_E2E_NPU_STRICT \
  "$PY" -m pytest tests/e2e/ -q --tb=short -m e2e_mock

if [ "$RUN_OFFLINE" = "1" ]; then
  echo ""
  echo "== Optional: offline contract (external network blocked) =="
  # 개발이 폐쇄망에서 일반망으로 옮겨가면서 "인터넷에 의존하는 코드를 애초에 쓸 수
  # 없다" 는 안전장치가 사라졌다. 이제 그런 코드는 PR 을 올리는 폐쇄망 PC 에서 처음
  # 드러난다 — push → pull → push → PR 왕복 뒤에. 여기서 30초에 끝낸다.
  # 고객도 폐쇄망에 배치하므로 제품 요건이기도 하다: docs/offline-contract.md
  # launcher 와 dx_agent_dev 는 각자 프로세스로 돈다 — 기본 게이트가 그러는 것과
  # 같은 이유다(포트 충돌, 그리고 dx_agent_dev 가 자기 패키지를 최상위 `core` 로
  # import 해서 다른 모듈의 `core` 와 부딪힌다).
  DX_OFFLINE_GUARD=1 "$PY" -m pytest \
    tests/dx_app/ tests/dx_stream/ tests/dx_compiler/ tests/dx_modelzoo/ \
    tests/dx_planner/ tests/dx_benchmark/ tests/dx_monitor/ \
    tests/shared/ tests/release/ tests/i18n_audit/ \
    -q --tb=short \
    --ignore=tests/dx_stream/benchmark \
    "${IGNORE_BROWSER[@]}"
  DX_OFFLINE_GUARD=1 "$PY" -m pytest tests/launcher/ -q --tb=short "${IGNORE_BROWSER[@]}"
  DX_OFFLINE_GUARD=1 "$PY" -m pytest tests/dx_agent_dev/ -q --tb=short
fi

if [ "$RUN_VISUAL" = "1" ]; then
  echo ""
  echo "== Optional: pixel visual regression =="
  # Advisory, not blocking: baselines are per-host (font rendering differs across
  # machines), so a green run only means "matches the baselines captured on THIS
  # runner". Refresh with DX_VISUAL_UPDATE=1 after an intentional design change.
  "$PY" -m pytest tests/visual/ -q --tb=short -m visual
fi

if [ "$RUN_NPU" = "1" ]; then
  echo ""
  echo "== Optional: real-NPU inference tier (e2e_npu) =="
  # DX_E2E_NPU_STRICT turns "no NPU / no model" from a skip into a failure. Asking
  # for this tier and getting a silent green would defeat the point of scheduling it.
  if [ -z "${DX_E2E_NPU_MODEL:-}" ]; then
    echo "--npu requires DX_E2E_NPU_MODEL=<registry model name>" >&2
    echo "(optionally DX_E2E_NPU_MODEL_FILE=<path to .dxnn> when it is not installed" >&2
    echo " under dx-runtime/dx_app/assets/models)" >&2
    exit 2
  fi
  DX_E2E_NPU_STRICT=1 "$PY" -m pytest tests/e2e/ -q --tb=short -m e2e_npu
fi

if [ "$RUN_COVERAGE" = "1" ]; then
  echo ""
  echo "== Optional: Python coverage (all modules) =="
  # .coveragerc declares all ten module sources, but this stanza used to measure
  # only shared+launcher — so eight modules reported as uncovered code that was in
  # fact well tested. Measure every declared source instead.
  #
  # The suites cannot share one pytest process (launcher and dx_agent_dev collide
  # on the 18xxx test ports, and tests/e2e rebinds DX_APP_ROOT), so each group runs
  # separately and appends into one data file, reported once at the end.
  # --cov=. (ONE root), not ten --cov=<pkg> flags: a per-package flag OVERRIDES
  # .coveragerc's `source`, which re-creates the ten-root problem — coverage.xml
  # then renders every module's server.py as filename="server.py" and nine files
  # collapse into one entry. With a single root the module stays in the path, so
  # the XML is usable by SonarQube and by scripts/coverage_gate.py alike.
  # The omit list in .coveragerc is what keeps tools/ and scripts/ out.
  COV_ARGS=(
    --cov=.
    --cov-config=.coveragerc
  )
  rm -f .coverage coverage.xml

  echo "-- coverage 1/4: launcher (isolated) --"
  "$PY" -m pytest tests/launcher/ -q --tb=short \
    "${COV_ARGS[@]}" --cov-report= "${IGNORE_BROWSER[@]}"

  echo "-- coverage 2/4: agent dev (isolated) --"
  "$PY" -m pytest tests/dx_agent_dev/ -q --tb=short \
    "${COV_ARGS[@]}" --cov-append --cov-report=

  echo "-- coverage 3/4: modules + shared + root --"
  "$PY" -m pytest \
    tests/dx_app/ tests/dx_stream/ tests/dx_compiler/ tests/dx_modelzoo/ \
    tests/dx_planner/ tests/dx_benchmark/ tests/dx_monitor/ tests/shared/ \
    tests/i18n_audit/ "${ROOT_TESTS[@]}" \
    -q --tb=short \
    --ignore=tests/dx_stream/benchmark --ignore=tests/e2e \
    "${IGNORE_BROWSER[@]}" "${QUARANTINE[@]}" \
    "${COV_ARGS[@]}" --cov-append --cov-report=

  echo "-- coverage 4/4: inference E2E (isolated) --"
  "$PY" -m pytest tests/e2e/ -q --tb=short -m e2e_mock \
    "${COV_ARGS[@]}" --cov-append \
    --cov-report=term-missing:skip-covered \
    --cov-report=xml:coverage.xml

  echo ""
  echo "-- coverage vs baseline --"
  # Report-only during the staged rollout; DX_COVERAGE_ENFORCE=1 turns a drop into
  # a failure once the numbers have settled.
  "$PY" scripts/coverage_gate.py
fi

if [ "$RUN_BROWSER" = "1" ]; then
  echo ""
  echo "== Optional: Playwright browser suites =="
  if ! "$PY" -c "import playwright" 2>/dev/null; then
    echo "SKIP browser (playwright not installed)" >&2
    exit 1
  fi
  # Shard by FILE, not by test: each browser suite owns a sync-Playwright event
  # loop for its whole process, so splitting a single file across workers would
  # have them fight over it. File-level shards stay process-isolated for free.
  _shard_suites=()
  for _i in "${!BROWSER_TESTS[@]}"; do
    if [ -n "$SHARD_TOTAL" ]; then
      # 0-based array index vs 1-based shard index
      if [ "$(( _i % SHARD_TOTAL ))" -ne "$(( SHARD_INDEX - 1 ))" ]; then
        continue
      fi
    fi
    _shard_suites+=("${BROWSER_TESTS[$_i]}")
  done

  if [ -n "$SHARD_TOTAL" ]; then
    echo "shard ${SHARD_INDEX}/${SHARD_TOTAL}: ${#_shard_suites[@]} of ${#BROWSER_TESTS[@]} browser suites"
    # The i18n copy audit is one indivisible job — pin it to shard 1 so it runs
    # exactly once across the matrix instead of once per shard.
    if [ "$SHARD_INDEX" = "1" ]; then
      bash scripts/i18n_browser_audit.sh
    else
      echo "SKIP i18n browser audit (runs on shard 1)"
    fi
  else
    bash scripts/i18n_browser_audit.sh
  fi

  # NOTE: these ten suites call pw.chromium.launch() directly, so they are
  # chromium-ONLY regardless of DX_BROWSER_ENGINES. Do not print the engine list
  # next to them — it would claim coverage that does not exist. Only tests/e2e is
  # engine-parameterised (see the cross-engine step below). Migrating a legacy
  # suite means swapping its fixture for tests.browser_support.launch_browser.
  # 알려진 결함은 명시적으로 안고 간다 — 블로킹 게이트의 QUARANTINE 과 같은 규율이다.
  # 목록은 tests/shared/test_ci_contracts.py 가 크기를 고정해 줄어들 수만 있고, 각
  # 항목은 docs/testing.md 에 근거와 함께 적혀 있어야 한다.
  # 비어 있다. 2026-09-15 에 세 항목이 모두 해제됐다 — 원인은 썩은 셀렉터가 아니라
  # (1) 폴링 중 교체된 스텝이 앞 스텝의 시각물을 남기던 것, (2) 의도적으로 주입한
  # 프리뷰를 존재만으로 결함으로 세던 것이었다. docs/testing.md 참조.
  BROWSER_QUARANTINE=()

  # 한 스위트가 실패해도 나머지를 마저 돈다. set -e 아래에서 pytest 를 그냥 호출하면
  # 첫 실패가 스크립트를 통째로 끝내는데, 실측해 보니 열 개 중 다섯 개만 돌고 나머지
  # 다섯 개는 상태조차 모른 채 넘어가고 있었다 — advisory 빨간불이 상시인 데다
  # 불완전하기까지 하면 새 회귀는 잡음에 묻힌다.
  _browser_failed=()
  for _bt in "${_shard_suites[@]}"; do
    echo "== Browser suite: $_bt (chromium) =="
    if ! "$PY" -m pytest "$_bt" -q --tb=short "${BROWSER_QUARANTINE[@]}"; then
      _browser_failed+=("$_bt")
    fi
  done
  if [ ${#_browser_failed[@]} -gt 0 ]; then
    echo ""
    echo "FAILED browser suites: ${_browser_failed[*]}" >&2
    exit 1
  fi

  # The genuinely cross-browser part. Pinned to shard 1 so the matrix runs it once.
  if [ -z "$SHARD_TOTAL" ] || [ "$SHARD_INDEX" = "1" ]; then
    echo "== Inference E2E triple gate across engines: ${DX_BROWSER_ENGINES:-chromium} =="
    "$PY" -m pytest tests/e2e/ -q --tb=short -m e2e_mock
  else
    echo "SKIP cross-engine E2E (runs on shard 1)"
  fi
fi

if [ "$RUN_UX" = "1" ]; then
  echo ""
  echo "== Optional: UX acceptance gate =="
  bash scripts/ux_acceptance_gate.sh
fi

echo ""
echo "run_ci.sh PASSED"
