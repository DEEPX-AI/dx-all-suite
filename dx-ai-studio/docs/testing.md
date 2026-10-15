# Testing

Tests are `pytest`, organized per module under `tests/<module>/`. Config lives in
`pytest.ini` (`testpaths = tests`, marker registry) and `.coveragerc` (branch coverage
over all module source, excluding `*/tests/*`, `*/.venv/*`). `pytest.ini` is the single
source of truth — do not re-add `[tool.pytest.ini_options]` to `pyproject.toml`, it
loses to `pytest.ini` and silently drifts.

Use the venv interpreter: `./.venv/bin/python -m pytest …`.

## Test layers

| Layer | What it covers | Needs |
|-------|----------------|-------|
| **Unit** | `core/` logic — catalog build, config, parsers, prompt wrapping, aggregation, ONNX surgery, accuracy math | nothing (stdlib) |
| **Contract** | `server.py` routes against a live in-process server on an `18xxx` test port; i18n key parity; tutorial 6-lang; shared base handler / chat engine | nothing |
| **i18n audit** | `tests/i18n_audit/` — copy inventory, missing-language, integrity, runtime lang-hook gaps, Spanish/stale-copy coverage | nothing |
| **Browser** | Playwright copy audit + language-switch matrix (optional; scripts under `scripts/`) | `playwright` install |
| **E2E (mock)** | `tests/e2e/` inference triple gate — UI click -> `/api/run*` -> rendered result -> perf numbers, against a fixture `DX_APP_ROOT` + shell fake runner | `playwright` + a chromium |
| **E2E (NPU)** | the same triple gate against real DX-M1 inference | NPU + `DX_E2E_NPU_MODEL` |
| **E2E (other)** | real compile / real CLI agents | `dx_com`, dx-runtime, or CLIs |

Live-server tests bind a **`18xxx` port = `1` + the real port** (e.g. dx_app → 18080,
dx_agent_dev → 18099) so they never collide with a running studio instance.

## Running the suites

Run module suites **separately** — do not run `tests/launcher/` and
`tests/dx_agent_dev/` in a single pytest invocation (their live servers collide on the
`18xxx` range).

```bash
./.venv/bin/python -m pytest tests/launcher/ -q          # ~521 tests
./.venv/bin/python -m pytest tests/dx_agent_dev/ -q      # ~228 tests (run alone)
./.venv/bin/python -m pytest tests/dx_app/ -q
./.venv/bin/python -m pytest tests/dx_stream/ --ignore=tests/dx_stream/benchmark -q  # ~273
./.venv/bin/python -m pytest tests/dx_compiler/ -q
./.venv/bin/python -m pytest tests/dx_modelzoo/ -q
./.venv/bin/python -m pytest tests/dx_planner/ tests/dx_benchmark/ tests/dx_monitor/ -q
./.venv/bin/python -m pytest tests/i18n_audit/ tests/shared/ tests/release/ -q
```

### Special test areas

- **`tests/dx_stream/benchmark/`** — requires the sibling `dx-runtime/dx_stream` tree
  on `sys.path`. If absent it no-ops (skips, ~121 tests). Excluded above via `--ignore`.
- **`tests/dx_modelzoo/`** — the generated catalog is gitignored; the conftest
  bootstraps it, or generate manually:
  `./.venv/bin/python dx_modelzoo/tools/sync_metadata.py --offline`.

### Markers (`pytest.ini`)

`requires_node`, `requires_pillow`, `requires_dx_runtime`, `external`, `smoke`, `e2e`,
`help_audit`. Skip environment-dependent tests, e.g. `-m "not requires_dx_runtime"`.

## Gates

There is no `.github/workflows/` in this repo — the real gate is `scripts/run_ci.sh`.
The parent suite invokes it from `dx-all-suite/.github/workflows/dx-ai-studio-pytest.yml`,
which triggers on `pull_request` for `dx-ai-studio/**` and runs on a `self-hosted` `sdk`
runner. (The heavier i18n smoke matrix lives in `dx-ai-studio-i18n-audit.yml` and is
`workflow_dispatch`-only — too slow to block a merge.) `run_ci.sh` runs seven numbered
stages in order:

```bash
bash scripts/run_ci.sh
```

```
--   CSS token ratchet — scripts/css_token_gate.py (runs before stage 0/7)
--   i18n lang-span ratchet — scripts/i18n_span_gate.py
--   breakpoint ratchet — scripts/breakpoint_gate.py
0/7  Infra + release contracts — tests/test_pytest_infra_contract.py,
     tests/shared/test_ci_contracts.py, tests/shared/test_studio_version_contracts.py,
     tests/release/
1/7  Collection gate — tests/ --collect-only, must report 0 collection errors
     (--ignore=tests/dx_stream/benchmark, tests/e2e, and the Playwright browser tests)
2/7  Launcher suite (isolated — port collision with dx_agent_dev)
3/7  Agent Dev suite (isolated — port collision with launcher)
4/7  i18n audit gate — bash scripts/i18n_audit_gate.sh
5/7  Module + shared + root contract suites (no browser) — dx_app, dx_stream,
     dx_compiler, dx_modelzoo, dx_planner, dx_benchmark, dx_monitor, shared,
     i18n_audit, tests/test_*.py
6/7  Inference E2E triple gate — tests/e2e/ -m e2e_mock, in its OWN pytest process
     (its conftest rebinds DX_APP_ROOT at import time)
```

### Release-audit browser regressions

`tests/launcher/test_escape_layers_browser.py` deliberately delays either native
Tutorial engine to verify that background initialization cannot destroy the visible
guide or take its toolbar ownership. It also covers SDK revisits, language refresh,
About's unavailable Tutorial, and Escape closing only the topmost layer.

`tests/shared/test_text_contrast_browser.py` checks the affected enabled, default-state
small text at **4.5:1** using computed colors and alpha-composited backgrounds. It
loads the actual App, Stream, Compiler, and Benchmark styles in explicit light/dark
and system light/dark modes, including the real Lab overlay and Stream palette.
Image/gradient backgrounds are rejected, not silently counted as passing; this is
a scoped regression gate, not a claim that all Studio text or hover states meet AA.

Both suites are registered in `run_ci.sh --browser`. For focused checks, run each
in its own process:

```bash
./.venv/bin/python -m pytest tests/launcher/test_escape_layers_browser.py -q
./.venv/bin/python -m pytest tests/shared/test_text_contrast_browser.py -q
```

### The inference E2E triple gate (`tests/e2e/`)

One browser journey — open Run, pick category -> model -> sample image, click Run —
asserted on three independent layers so a regression in any one fails the gate:

1. **network** every `/api/run*` response is HTTP 200 and the terminal payload has
   `exit_code == 0` and no `error` (the UI prefers async `/api/run_async` + polling,
   with a blocking `/api/run` fallback; both are covered)
2. **render** the result image is visible AND `naturalWidth > 0` (proves the browser
   decoded the base64 JPEG — a corrupt `src` stays "visible" but is zero-wide)
3. **metrics** the FPS and Latency perf cards carry finite, in-range numbers

`tests/e2e/fake_app_root.py` builds a throwaway `DX_APP_ROOT` (registry, a stub
`.dxnn`, a sample JPEG, and a POSIX-shell fake runner). Because `DX_APP_ROOT`,
`BUILD_DIR` and `DXAPP_SAVE_IMAGE` are already env-driven, **no production code is
modified** — only the NPU binary is swapped, so the real `subprocess.Popen`, the real
`_parse_perf`, the real result-image pipeline and the real `/api/run` route all run.

#### The real-NPU tier

`DX_E2E_NPU_MODEL` is a **registry name** from dx_app's `config/test_models.conf`
(e.g. `yolov11n`), not a filename. The tier skips — with the specific reason — when
the model is unknown, `/dev/dxrt0` is absent, or no `.dxnn` can be found.

```bash
# The model is already installed (dx_app setup.sh has run): the real tree is used.
DX_E2E_NPU_MODEL=yolov11n ./.venv/bin/python -m pytest tests/e2e/ -m e2e_npu -q

# The .dxnn lives elsewhere — e.g. a ModelZoo download cache. dx_app/assets/ is
# root-owned on a provisioned board, so instead of needing sudo to drop a model in,
# the fixture builds a symlink overlay and leaves the runtime tree untouched.
DX_E2E_NPU_MODEL=yolov11n \
DX_E2E_NPU_MODEL_FILE=../workspace/res/models/yolo11-n_640x640.dxnn \
  ./.venv/bin/python -m pytest tests/e2e/ -m e2e_npu -q
```

Which root a process gets is decided ONCE at conftest import, because
`dx_app.core.config` freezes `BUILD_DIR`/`CATEGORIES` on first import. The two tiers
therefore cannot share a pytest process — run them as separate invocations, which
`run_ci.sh` already does (stage 6 is `-m e2e_mock`).

The NPU test also asserts its FPS/latency are **not** the fake runner's constants,
so a misconfiguration that silently falls back to the mock cannot report a green
"NPU verified".

Extra flags: `--browser` (adds the Playwright copy/lang-switch/tutorial suites,
needs `chromium` installed), `--ux` (full UX acceptance gate, slow, release only).

### Cross-browser

Engine selection is env-driven — `DX_BROWSER_ENGINES=chromium,firefox[,webkit]`.
The default is **chromium alone**, so the blocking gate stays single-engine and fast;
the advisory CI job opts into firefox.

> **Scope today: `tests/e2e/` only.** The ten legacy browser suites listed in
> `run_ci.sh` call `pw.chromium.launch()` inside their own fixtures, so they run on
> chromium no matter what `DX_BROWSER_ENGINES` says — the gate labels them
> `(chromium)` rather than claiming coverage they do not have. To migrate one, replace
> its fixture's `pw.chromium.launch(headless=True)` with
> `tests.browser_support.launch_browser(pw, engine)` and parameterise on
> `selected_engines()`, the way `tests/e2e/conftest.py` does. Each migrated suite
> multiplies its own runtime by the engine count, so migrate the ones where
> rendering actually differs (zoom/layout audits) before the copy audits.

```bash
DX_BROWSER_ENGINES=chromium,firefox ./.venv/bin/python -m pytest tests/e2e/ -m e2e_mock -q
```

Only chromium falls back to a host binary (`google-chrome`). Playwright ships **patched**
Firefox/WebKit builds, so a distro Firefox is not a substitute — install them with
`python -m playwright install firefox webkit`. WebKit additionally needs distro packages
(`libevent-2.1-7t64`, `libavif16`) that only root can install; without them the suite
**skips** webkit with the driver's message rather than failing.

### Sharding

`--shard=i/N` splits the browser suites by **file** (each suite owns a sync-Playwright
event loop for its whole process, so a file cannot be split across workers). The i18n
copy audit is indivisible and is pinned to shard 1.

```bash
bash scripts/run_ci.sh --browser --shard=1/3
```

### Failure traces (Trace Viewer)

`tests/e2e/` records a Playwright trace for every test and keeps it **only on failure**
(`var/e2e-traces/<test>.<engine>.trace.zip`) — keeping traces for green runs would bury
the one that matters. CI uploads them as artifacts. Open one with:

```bash
playwright show-trace var/e2e-traces/<file>.trace.zip
```

### Coverage

```bash
./.venv/bin/python -m pip install pytest-cov   # not in requirements-ci.txt
bash scripts/run_ci.sh --coverage
```

Measures **all ten** shipped packages (it used to measure only `shared` + `launcher`,
which made eight well-tested modules look uncovered). The suites cannot share one pytest
process — launcher and dx_agent_dev collide on the `18xxx` ports and `tests/e2e` rebinds
`DX_APP_ROOT` — so it runs four groups with `--cov-append` and reports once.

**One source root, not ten.** `.coveragerc` sets `source = .` with `relative_files = True`,
and `run_ci.sh` passes a single `--cov=.`. This is not cosmetic: coverage.py strips whichever
declared root a file came from, so with ten roots every module's `server.py` rendered as
`filename="server.py"` and the nine distinct files **collapsed into one entry** in
`coverage.xml` — 9 files in the terminal report, 1 in the XML. Anything consuming that XML
(SonarQube) attributes the coverage to whichever root resolves first and reports the other
eight at 0%. A single root keeps the module in the path (`dx_app/server.py`), which is also
what `coverage_gate.py` splits on. A per-package `--cov=<pkg>` flag OVERRIDES the config's
`source`, so adding one back re-creates the collapse; `tests/shared/test_ci_contracts.py`
pins this.

`scripts/coverage_gate.py` then compares against `config/coverage_baseline.json`
(0.5%p tolerance). Report-only during the staged rollout; set `DX_COVERAGE_ENFORCE=1`
to make a drop fail. Refresh the baseline with `python scripts/coverage_gate.py --update`.

Baseline (`config/coverage_baseline.json`, branch coverage over 20,146 statements
across 152 files):

| module | cover | | module | cover |
|---|---|---|---|---|
| dx_planner | 91.7% | | shared | 74.8% |
| dx_benchmark | 91.2% | | launcher | 70.7% |
| dx_monitor | 85.0% | | dx_stream | 68.7% |
| dx_modelzoo | 83.8% | | dx_app | 68.2% |
| dx_agent_dev | 79.9% | | dx_compiler | 64.5% |

`dx_compiler` is still the thinnest, but the biggest wins are now per-FILE rather than
per-module — the module averages hide a few very large, very uncovered files:

| file | cover | uncovered statements |
|---|---|---|
| `dx_compiler/server.py` | 41.4% | 384 |
| `dx_stream/server.py` | 55.1% | 365 |
| `dx_app/core/live.py` | 17.3% | 337 |
| `launcher/launcher.py` | 67.2% | 334 |
| `dx_compiler/core/compiler_service.py` | 54.8% | 296 |
| `dx_app/core/modelzoo.py` | 28.5% | 206 |

The two `server.py` files and `compiler_service.py` are request handlers and dx_com
orchestration — reachable with the fake-subprocess / live-test-server treatment already
used by `tests/dx_compiler/test_setup_service.py` and `tests/dx_stream/test_server.py`.
`dx_app/core/live.py` drives camera/RTSP capture and needs either a fake capture source or
hardware. `dx_stream/core/webrtc.py` (42.7%) needs GStreamer GI bindings, which are absent
here.

Additional helper/manual checks, not part of `run_ci.sh`:

- `bash scripts/i18n_smoke_matrix.sh` — full i18n smoke incl. matrix.
- `bash scripts/i18n_browser_audit.sh` — optional Playwright copy audit.
- Server smoke (manual, not gated by `run_ci.sh`): confirm the launcher binds and
  prints its live banner — `./.venv/bin/python launcher/launcher.py --port 8890
  --no-browser`.
- Hardening checks: `DX_BIND_LOCAL=1 ./launcher.sh` (loopback only) and
  `DX_API_TOKEN=secret ./launcher.sh` (401 without a bearer token).

## SonarQube

`sonar-project.properties` is committed; the server is not configured in it. The endpoint
and credentials for the DEEPX SonarQube are not in any repository here, so they are passed
at scan time:

```bash
sonar-scanner \
  -Dsonar.host.url="$SONAR_HOST_URL" \
  -Dsonar.token="$SONAR_TOKEN" \
  -Dsonar.projectVersion="$(cat release.ver)"
```

`.github/workflows/dx-ai-studio-sonar.yml` does exactly that and is a deliberate **no-op
until the `SONAR_HOST_URL` / `SONAR_TOKEN` secrets exist** — every step that needs the
server is gated on a secret check, so the job reports success rather than failing every PR
on a guessed endpoint. It is advisory (`continue-on-error`) because a first scan of a
codebase this size surfaces a backlog, and blocking merges on it before that is triaged
just teaches people to ignore the gate.

Notes:

- **Coverage.** Sonar reads `coverage.xml` from `run_ci.sh --coverage`. That report is only
  usable because coverage now measures from a single root — see the Coverage section above.
- **Version.** Not in the properties file: `release.ver` is the SSOT and a copy would drift.
- **Exclusions.** The studio ships ~6 MB of JS, most of it vendored (`mermaid.min.js`) or
  generated (`i18n.js` is 5,175 lines with three functions — a translation table). Scanning
  it produces thousands of findings nobody will act on and buries the real ones.
- **Contracts.** `tests/shared/test_ci_contracts.py` pins that no endpoint or token is ever
  committed, that `sonar.sources` matches pyproject's package list, and that the report path
  is the one `run_ci.sh` actually writes.

### CSS token ratchet (`scripts/css_token_gate.py`)

Module CSS must take colour from tokens, not literal hex — a literal is invisible
to the theme switch, so it silently keeps the dark value on a light page. The gate
counts raw hex per module stylesheet and compares against
`config/css_token_baseline.json`:

```bash
python scripts/css_token_gate.py          # check (exits 1 on any increase)
python scripts/css_token_gate.py --write  # re-record after a reduction
```

The baseline can only go **down**. `tests/test_css_token_gate.py` enforces both
directions: `test_no_module_exceeds_its_baseline` fails on a new literal, and
`test_baseline_has_no_stale_headroom` fails when a file improved but the baseline
was not tightened — stale headroom would silently re-admit the literals you removed.

Baseline at the time the gate landed: **244 raw hex across 12 files**
(`sdk-library.css` 95, `launcher/style.css` 52, `dx_compiler` 20, `dx_app` 20, …).
`shared/static/` is deliberately out of scope — `dx-tokens.css` is where the
palette is *supposed* to live.

### i18n lang-span ratchet (`scripts/i18n_span_gate.py`)

A translatable label used to be written six times, once per language:

```html
<span class="ko">저장</span><span class="ja">保存</span>…<span class="es">Guardar</span>
```

Most of those strings also lived in the module's `_DX_I18N_DICT`, so a phrase had
two homes free to drift — and 125 keys had. The markup now carries
`data-i18n="English key"` and the dictionary owns every translation.

```bash
python -m scripts.i18n_span_gate          # check (exits 1 on any increase)
python -m scripts.i18n_span_gate --write  # re-record after a reduction
```

29 groups remain, pinned in `config/i18n_span_baseline.json`. They stay because one
key carries two different phrases and only a person can choose: `dx_stream` 'OK' is
'정상' (a status) in the dictionary and '확인' (a button) in the markup.

`config/i18n_key_gaps.json` pins the keys a dictionary cannot fill — the launcher's
`about*` labels come from `about-deepx.js` `ABOUT_NAV_LABELS`, not from
`_DX_I18N_DICT`. A key that falls back to English silently shows English, so the
gate refuses new ones.

`scripts/migrate_i18n_spans.py` performed the move and is kept for the remainder.
It reports before it writes and never invents a translation: where markup and
dictionary disagreed and the key was used nowhere else, the dictionary was corrected
to the markup so rendering stayed byte-identical.

### Breakpoint ratchet (`scripts/breakpoint_gate.py`)

Responsive layout splits at **19 different widths** (600, 640, 700, 720, 768, 769,
900, 960, 980, 1024, 1100, 1200, 1280, 1360, 1440, 1600, 1979 …). One screen folding
at 900 next to another folding at 960 is not a decision; it is a value copied from
whichever file was open at the time.

Moving those onto a scale changes how the product renders in each band, so the gate
does **not** move them. It refuses *new* values:

```bash
python -m scripts.breakpoint_gate          # check (exits 1 on a new width)
python -m scripts.breakpoint_gate --write  # re-record after a consolidation
```

Target scale is `600 / 900 / 1200 / 1440` (`SCALE` in the gate). Consolidate onto it
one file at a time, with the responsive baselines below as the check.

### Shared component ownership

`tests/test_shared_css_foundation.py` also tracks which stylesheets redefine a
component that `shared/static/dx-components.css` owns. Two allowlists carry the
current state, and a `..._has_no_stale_entries` test forces each entry to be removed
as the migration lands, so the lint keeps catching the next regression:

- `OWNED_COMPONENT_OVERRIDES` — shared owns the selector, a module overrides it
  (`.btn`: dx_benchmark, dx_planner).
- `UNOWNED_COMPONENTS` — no shared owner yet, modules each reinvent it
  (`.card`: dx_app, dx_benchmark, dx_monitor, dx_stream).

### Global script scope (`tests/shared/test_static_script_scope.py`)

There is no bundler. A module page lists its `<script src>` tags in order and every
top-level declaration in those files lands in one global lexical scope, so two files
declaring the same name is not a style question:

- `const` / `let` / `class` — the later file fails to parse **in its entirety**
  (`SyntaxError: has already been declared`). Nothing renders from it and no Python
  test notices.
- `function` / `var` — parsing succeeds and the later definition silently wins,
  including for calls made from the earlier file.

Both happened. `METRIC_HIGHER_IS_BETTER` was declared in `catalog.js` and `detail.js`,
which killed `detail.js` outright — the whole ModelZoo detail page rendered empty while
the blocking stage stayed green. And `_localLabel` existed in both, so the ja/zh/es
category fallback that `catalog.js` carries was overwritten by `detail.js`'s copy,
which has no fallback.

The gate reads the page's script list and reports both classes. Top-level is decided
by indentation — every file here indents nested code, so a declaration at column 0 is
top-level. Shared helpers live in the module's first-loaded file (`app.js` for
ModelZoo); when two files legitimately need the same routine, that is where it goes.

Only one gate saw the dead detail page before this: the opt-in `--browser` stage, via
`tests/test_zoom_modal_audit.py`'s `detailView` emptiness check. That stage is not in
the default run, which is exactly the gap the `--browser` note below describes.

### Unified app shell (`tests/test_dx_shell.py`, `tests/shared/test_shell.py`)

`shared/static/dx-shell.css` + `shared/shell.py` render one skeleton (56px module
rail, 56px header, 42px page-tab row) that modules inherit. dx_app is the first
module on it. The contracts worth knowing about:

- The shell's markup is injected **server-side** (`DXBaseHandler.shell_spec` →
  `shared.shell.apply` inside `serve_template`), so any test that asserts on dx_app's
  header, toolbar or brand slot must read the **rendered** HTML, not the template —
  see `rendered_dx_app_index()` in `tests/test_shared_css_foundation.py`.
- Tab labels are never truncated. Overflow is a function of translation length, not
  window width (`Benchmark` is 9 characters in English and 25 in Spanish —
  `Evaluación de rendimiento`), so `shared/static/dx-tabs.js` moves whole tabs into a
  `+N` menu on both `ResizeObserver` and `dx-lang-applied`, and keeps the active tab
  in the row.
- `dx-shell.css` may not contain a literal colour; `dx-icons.svg` may not either
  (`currentColor` only) — both are theme-switch correctness, enforced by tests.

### Theme (`tests/test_dx_theme.py`)

`shared/static/dx-theme.js` holds three states — `dark`, `light`, `system` — under
`localStorage['dx-theme']`, mirroring the `dx-lang` convention. `system` removes the
`data-theme` attribute so `prefers-color-scheme` decides. `dx-theme-light.css` must
define **every** semantic token in **both** its blocks (`:root[data-theme="light"]`
and the `prefers-color-scheme` block guarded by `:not([data-theme="dark"])`); a token
present in only one block breaks solely for viewers on OS-light with no explicit
choice, which is the hardest case to notice by hand.

## Optional stages

`run_ci.sh` takes four opt-in flags. None of them run in the blocking PR gate.

| Flag | What it runs | Why it does not block |
|------|--------------|----------------------|
| `--npu` | `tests/e2e/ -m e2e_npu` — the triple gate against real DX-M1 inference | One board backs it; a merge must not depend on that board's health |
| `--visual` | `tests/visual/` — pixel diff vs committed screenshots | Baselines are per-host (font rasterisation differs) |
| `--browser` | the ten Playwright suites, shardable with `--shard=i/N` | Slow (~50 min); advisory until the engines are stable in CI. Green as of 2026-09-15 — see below |
| `--coverage` | all ten `.coveragerc` sources vs `config/coverage_baseline.json` | Staged: visible, not yet gating |

### Real-NPU tier (`--npu`)

```bash
DX_E2E_NPU_MODEL=<registry name> bash scripts/run_ci.sh --npu
# model not under dx_app/assets/models (root-owned on a board)? add:
DX_E2E_NPU_MODEL_FILE=/path/to/model.dxnn
```

`--npu` exports `DX_E2E_NPU_STRICT=1`, which turns "no NPU / no model" from a skip
into a **failure**. pytest exits 0 when everything skips, so without it a scheduled
run on a board with a dead NPU would report green while proving nothing.

`--npu` runs the blocking stages first, and stage 6 (the mock tier) is invoked with
`env -u DX_E2E_NPU_MODEL -u DX_E2E_NPU_MODEL_FILE -u DX_E2E_NPU_STRICT`. That is
load-bearing: `tests/e2e/conftest.py` binds `DX_APP_ROOT` at import time and selects
the NPU overlay whenever `DX_E2E_NPU_MODEL` is set, so without stripping them the
mock tier looks for its fixture model in the real dx_app tree and the run fails its
own blocking stage (`model 'e2eyolo' is not in /api/models`).

It runs in CI from `dx-ai-studio-npu.yml`: nightly, on `workflow_dispatch`, and on a
PR labelled `run-npu`.

### Pixel visual regression (`--visual`)

`tests/visual/` screenshots every module's landing page across four axes and
compares each against a committed baseline:

| baseline | axes | shots |
|---|---|---|
| `<engine>/<module>__<theme>__<locale>.png` | 9 modules x {dark, light} x {en, es} at 1280x800 | 36 |
| `<engine>/<module>__w<width>.png` | 9 modules x {650, 860, 1150, 1320} at dark/en | 36 |
| `<engine>/launcher__intro__<state>.png` | the intro at `hero`, `work` and `close` | 3 |
| `<engine>/<page>__<theme>__<locale>.png` | pages behind a tab (`PAGE_SPECS`): DX App's Graph Composer, its logic template page and its Export C++ project dialog x {dark, light} x {en, ko} | 12 |

87 shots. `tests/visual/baseline_spec.py` is the source of truth for the axes and
carries the reasoning for each one; do not restate the numbers here.

This is **not** what `tests/test_ux_visual_gate.py` does — that audits tutorial
spotlight geometry through the DOM. It catches "the highlight points at nothing";
it cannot catch "the header lost its border".

Determinism was measured, not assumed. With a fresh browser context per capture,
reduced motion, `animations="disabled"` and the tutorial TOC closed, repeat captures
of the same commit differ by **0 pixels** on all nine modules. Two findings shaped
the harness:

- **Reusing a browser context breaks it.** The second page in a context renders as a
  return visit (splash seen, panels remembered) — 48.8% of the launcher hub's pixels
  moved between two captures of the same commit until each got its own context.
- **Two modules need masks.** `dx_monitor`'s live telemetry drifts 0.0788%, and
  `dx_agent_dev`'s animated showcase thumbnails drift 0.97-2.16%. The latter only
  appears against a *stored* baseline — back-to-back captures agree — so it survived
  the first round of probing.

The threshold is 0.02% (`DX_VISUAL_MAX_RATIO`), chosen by measurement: at 0.1% a
global `--accent` change moved only one of nine modules past the limit. At 0.02% a
0.2px `letter-spacing` change is caught on **all nine**.

#### Axes

**Theme x locale.** A single-axis baseline could not see the token refactor:
semantic tokens and the light theme change *colour*, and translation length changes
*layout* (Benchmark -> "Evaluación de rendimiento" pushes the tab row into
overflow). `es` is the locale because its labels are the longest.

**Width.** The theme/locale shots are all captured at 1280, so moving a fold from
900 to 960 turns nothing red. `responsive_axes()` adds four widths at dark/en,
each sitting in the *middle* of a crowded band rather than on a boundary — on a
boundary a 1px difference flips the result and the gate goes flaky. Colour is not
what this axis watches, so one theme and one locale are enough.

These widths are the precondition the breakpoint ratchet was waiting on; see
`scripts/breakpoint_gate.py`.

**Page.** A page behind a tab whose content comes from data gets its own axis
(`PAGE_SPECS`, `test_module_page_matches_baseline`): the capture answers the page's
API with fixtures (the Graph Composer's catalog, check and memory would otherwise
show this host's models and NPU), opens it and waits until its data has landed.
`ko` replaces `es` here because the graph canvas draws CJK text itself.

#### The intro axis

The landing captures seed `dx-splash-seen` (`tests/visual/conftest.py`), so the
intro never runs in them. That is deliberate — pixel-diffing a running animation
is not deterministic — and it means those 72 shots say "the page after the splash
did not move" and nothing more.

`test_intro_regression.py` covers the intro separately, and it does not wait on the
sequence either. It cancels the pending timers, sets the overlay to a named state
(`hero`, `work`, `close`), and shoots with `animations="disabled"`. So what is pinned is
"the composition once hero has settled", not "the frame at 2.6s": retiming a beat
does not turn it red, changing the picture does.

Two traps, both hit while building it:

- `reduced_motion="reduce"` sends the intro down its own `is-still` path, which is
  a *different design*, and then removes the overlay after 700ms. The capture ends
  up photographing the home page.
- Leaving the timers running does the same thing more slowly. Two such captures
  agree to the pixel, so a determinism check that does not look at the image will
  happily report 0 differing pixels on two photographs of the wrong screen.

Structural contracts in `tests/launcher/test_home_portal.py` still hold the grammar
— the surface the light crosses, the cut into the app, the reduced-motion path, the
honesty of the working beat, the drawn scenes. The pixel axis catches what a
contract cannot: this session shipped a doubled X, a specular lost against a
too-bright face, and an upside-down reflection, all with the contracts green.

Refresh baselines after an intentional design change:

```bash
DX_VISUAL_UPDATE=1 ./.venv/bin/python -m pytest tests/visual/ -q
```

## Pre-commit hook

The Node-free stand-in for the ticket's Husky step. Runs in ~4s on a normal commit.

```bash
bash scripts/install-hooks.sh     # symlinks scripts/pre-commit-hook.sh
git commit --no-verify            # bypass once
```

It checks only what is proportional to the staged diff — `py_compile` on `.py`,
`json.load` on `.json`, `bash -n` on `.sh` — plus `test_pytest_infra_contract.py`
and `test_ci_contracts.py`, which are what actually break when someone edits
`run_ci.sh`, `pytest.ini` or a workflow without updating its ledger. The full gate
stays in CI.

## Quarantined pre-existing failures

**비어 있다 (2026-09-16).** 마지막 항목이 해제되어 stage 5/7 은 이제 아무것도
deselect 하지 않는다. `QUARANTINE=(...)` 구조와 `tests/shared/test_ci_contracts.py`
의 ratchet 은 남겨 둔다 — 목록은 줄어드는 방향으로만 바뀌고, 새 항목은 여기에
근거를 적어야 들어올 수 있다.

무엇이었는지, 그리고 **여기 적혀 있던 진단이 왜 틀렸는지**는 남길 값어치가 있다.

이 표에는 `test_all_models_have_complete_legal_block` 이 "yolo26-depth 계열은 dx_app
소스 트리에서 오고 ModelZoo 동기화 스냅샷에는 없다 → **상류 라이선스 데이터가 필요하다.
지어내지 말 것**" 으로 적혀 있었다. 앞의 절반은 맞고 결론은 틀렸다.

공개 ModelZoo 페이지를 열어보면 다섯 개가 전부 있다:

```
yolo26_depth_n-1   Ultralytics YOLO26-n-depth   Depth Estimation
                   source  = https://github.com/ultralytics/ultralytics
                   license = AGPL-3.0   dataset = NYUDepthv2   metric = RMSE
```

`public_modelzoo_adapter` 는 이미 이것을 정확히 뽑고 있었다. 지어낼 것이 없었고,
확인하지 않은 것이 문제였다. 실제 원인은 두 겹이다:

1. **`generated_catalog.json` 이 stale** — 2026-09-08 산출물이라 348개 중 yolo26_depth
   가 0개였다. 이 모델들이 공개되기 전에 만들어진 파일이다.
2. **재동기화만으로는 붙지 않는다** — studio id 는 `yolo26_depth_n`, 생성 id 는
   `yolo26_depth_n_768x768` 이고, `core/catalog.py:_match_generated` 의 접미사
   화이트리스트(`_q_lite` / `_q_pro` / `_q_master` / `_1`)에 해상도가 없다. 그것은
   실수가 아니라 의도였다 — 주석이 `foo` 와 `foo_1280` 을 섞지 않겠다고 적고 있다.

그래서 해상도 접미사는 **후보가 유일할 때만** 접도록 했다. 실측하면 이 규칙으로 새로
매칭되는 studio id 는 정확히 5개이고 모호 사례는 0건이다. 유일성 검사를 빼는 변이로
안전장치가 살아 있는지 확인했다 (`tests/dx_modelzoo/test_generated_id_match.py`).

재동기화는 항목 3개(`efficientnet_edgetpu_*`)를 잃는다 — 상류에서 내려간 모델이고
저장소 어디에서도 참조하지 않는다. `yolov5n6` 의 `source_url` 은 릴리스 태그에서
저장소 루트로 덜 구체적이 되는데, 이것도 상류가 바꾼 값이다. 지난 값을 손으로
고정해 두면 다음에 상류가 바뀔 때 조용히 어긋난다 — 이 버그가 정확히 그 모양이었다.

부수 효과 하나: 그 다섯 개의 `commercial_use` 가 `restricted`(license 미상 fallback)
에서 `copyleft`(실제 AGPL 분류)로 바뀐다. 같은 "쓰기 조심" 이라도 이유가 정확해진다.

### ModelZoo 의 두 소스

`dx_app/core/modelzoo.py` 는 두 소스를 다르게 판다:

| source | 무엇을 읽나 | 픽스처 |
|---|---|---|
| `public` | `window.__MODEL_ZOO_DATA__` 페이로드 | `tests/dx_modelzoo/fixtures/public_modelzoo_payload.html` |
| `internal` | devops publish 의 20칼럼 테이블 | `tests/dx_app/fixtures/internal_modelzoo_table.html` |

여기에는 한때 "사내망 호스트라 이 저장소의 게이트가 닿지 못한다" 고 적혀 있었다.
**확인하지 않고 단정한 것이었고, 틀렸다** — 이 개발 장비에서 `curl` 이 200 과 1.3MB 를
돌려준다. 2026-09-18 에 실측 응답에서 대표 구간(20칼럼 헤더 3행 + 데이터 3행)을 잘라
픽스처로 커밋했고, `tests/dx_app/test_modelzoo_internal_table.py` 가 그 모양을 고정한다.

확인하면서 드러난 두 소스의 차이:

* **티어가 다르다.** public 은 Q-Master 를 주고 internal 은 주지 않는다 — 행에
  `qmaster` 키 자체가 없다(실측: internal 496 모델 중 0 건). `_CHIP_DIRS` 와
  프론트의 `MZ_CHIPS` 는 세 티어를 순회하지만 `m.get(chip)` / `m[chip.key]` 가
  각각 None / undefined 로 떨어져 조용히 넘어간다. 우연히 맞는 것이 아니라
  계약으로 고정해 두었다.
* **없는 값의 모양이 다르다.** public 은 숫자나 `None`, internal 은 `'-'` 문자열이다.
  같은 화면이 두 소스를 쓰므로 정렬이나 계산에 넣을 때 알고 있어야 한다.
* **건수가 다르다.** internal 496, public 354. 같은 카탈로그의 다른 단면이다.

#### Quarantined browser failures

**비어 있다 (2026-09-15).** 세 항목이 모두 해제됐다. `BROWSER_QUARANTINE` 구조는
남겨 둔다 — `tests/shared/test_ci_contracts.py` 가 목록이 늘어나는 것을 막고, 각
항목이 여기 근거를 갖도록 강제한다. 지금은 브라우저 스테이지 전체가 블로킹이다.

무엇이었는지는 기록해 둘 값어치가 있다. **셀렉터 문제가 아니었다.**

`analyze_step` 의 `_renderTooltip` / `_renderTooltipFloating` 을 감싸 "이 스텝이
렌더까지 갔는가" 를 기록하니, 실패한 스텝은 전부 **렌더된 적이 없었다**:

```
dx_modelzoo  download|step1    렌더됨=False  직전렌더=download|0 anchored
dx_app       run-single|step9  렌더됨=False  직전렌더=run-single|8 anchored
             rundemo|step3     렌더됨=False  직전렌더=rundemo|2   anchored
             rundemo|step4     렌더됨=False  직전렌더=rundemo|2   anchored
```

`_showStep()` 은 타깃이 안 보이면 최대 2초 폴링한다. 그 사이 스텝이 교체되면
`_stepToken` 가드에 걸려 아무것도 렌더하지 않고 빠져나갔고, 화면에는 **앞 스텝의**
스포트라이트와 툴팁이 남았다. 러너는 350ms 만 기다리고 측정하므로, 현재 스텝의
셀렉터(실제로 없음)와 앞 스텝의 스포트라이트(active)를 함께 보고 `TARGET_MISSING`
으로 분류했다. 사용자에게도 같은 일이 일어난다 — Next 를 누르면 최대 2초간 지나간
스텝의 상자를 본다. 이제 폴링에 들어가기 전에 새 스텝을 floating 으로 먼저 띄우고,
타깃이 나타나면 anchored 로 승격한다 (`tests/test_tutorial_stale_step.py`).

네 개의 타깃은 모두 **조건부**였다 — DX App 연결, 추론 결과, 모델 설치처럼
튜토리얼이 만들어낼 수 없는 상태에서만 존재한다. 문서 전체에서 셀렉터가 0개라
"썩었다" 고 판단했다가 정정했다: `rundemo.js:205/337` 이 그것을 만들되 모델이
설치된 분기에서만 만든다. 그래서 스텝이 `optionalTarget: true` 로 선언하고, 그런
스텝만 floating 이 정상으로 취급된다. 선언하지 않은 스텝이 floating 되면 여전히
`FLOATING_FALLBACK` 으로 잡힌다 — 멀쩡한 스텝의 셀렉터를 일부러 썩혀 확인했다.

`MOCK_INJECTION` 2건은 **오탐이었다.** 이 문서에 "주입한 요소를 치우는 주인이
없다" 고 적혀 있었는데 틀렸다. `afterStep` 이 치운다 (실측: 투어 종료 후 0개).
게이트가 `[data-dxt-tutorial-mock]` 의 **존재**를 결함으로 셌는데, 그것을 스포트라이트로
가리키는 것이 바로 그 스텝의 목적이다. 잡아야 할 것은 "남는 것" 이므로 투어가 끝난
뒤에 센다 (`mock_left_over()`).

#### `--browser` was red (2026-09-15)

`run_ci.sh` without flags reports zero failures, and that sentence has been quoted
as "everything is green". It was not: the browser suites are opt-in, so nothing in
the default run executes them, and `tests/test_tutorial_e2e_journey.py` had been
failing on three of its seven modules.

**It passes end to end as of 2026-09-15 evening** — ten of ten suites, three
`test_tutorial_e2e_journey` parameters deselected into `BROWSER_QUARANTINE` above:

```
i18n_audit/test_browser_copy_audit            13 passed
launcher/test_sdk_library_module_nav_browser   4 passed
shared/test_browser_runtime                    1 passed
test_iframe_lang_sync_browser                 15 passed
test_tutorial_e2e_journey                      5 passed, 3 deselected
test_tutorial_spotlight_spot_check            11 passed
test_ux_visual_gate                          495 passed
test_zoom_full_audit                          34 passed
test_zoom_layout_contracts                   180 passed
test_zoom_modal_audit                        180 passed
```

Getting there took the stage changes described above plus one real defect the stage
alone caught: `test_zoom_modal_audit` was failing all eight of its ModelZoo
`detail-view` parameters on `detailView.innerHTML.length > 40`, because a duplicate
`const` had killed `detail.js` at parse time (see **Global script scope** above). No
other gate in the repository saw it.

The rest of this section records what the red looked like, because the shape of the
remaining quarantined failures still argues against the obvious reading.

```
dx_modelzoo   download|step1   TARGET_MISSING  '[data-model-id][data-quant]'
dx_app        run-single|step9 TARGET_MISSING  '#r-topk'
              rundemo|step3    TARGET_MISSING  '#rundemo-block-0 [data-axis="post"]'
              rundemo|step4    TARGET_MISSING  '#rundemo-block-0 button[onclick*="rundemoRun"]'
              modelzoo|step4   TARGET_MISSING  '#mz-cart'
dx_agent_dev  showcase|step2   MOCK_INJECTION  data-dxt-tutorial-mock present in DOM
              activity|step2   MOCK_INJECTION  data-dxt-tutorial-mock present in DOM
```

Pre-existing and not caused by the hub-portal work: the same three fail with that
branch's changes stashed.

What is *not* yet established is the root cause, and the categories argue against
the obvious reading. `analyze_step` already has a `FLOATING_FALLBACK` bucket, and
`tutorial-engine.js` degrades a missing target into a floating tooltip on purpose
(`target not found/visible after polling → floating tooltip`), so a step whose
control legitimately is not present should land in that bucket, not this one.
`TARGET_MISSING` means the spotlight was active and the tooltip was *not* floating
while `_queryTarget` returned nothing — a target that existed when the step opened
and vanished before the metric read, which is a different bug from a rotted
selector. At least one of the five even documents itself as conditional ("only
visible when DX App is connected").

So this needs an instrumented run per module before anything is changed. Guessing
at a selector here risks papering over a re-render race with a hard-coded target.

`MOCK_INJECTION` is a separate defect: the tutorial injects a preview element
(`data-dxt-tutorial-mock`) to spotlight a state that only exists mid-operation, and
does not always remove it.

**Resolved 2026-08-27** (removed from the quarantine): the three dx_stream/dx_modelzoo
failures all traced to one cause — dx-runtime shipped the `yolo26-depth` family
(pipeline + `libpostprocess_yolo26depth.so` + `DxOsd::draw_depth`) and the studio's
catalog never caught up. Fixed by adding the model metadata, a depth demo, and a
filename-based `input_resolution` fallback. See `dx_stream/core/models.py`,
`dx_stream/core/demos.py`, `dx_modelzoo/core/catalog.py::_enrich_input_resolution`.

Fix the defect, then delete the matching `--deselect` line — the contract test will
confirm the entry is gone.

## Baseline (module suites, run separately)

- launcher ~521, dx_agent_dev ~228, dx_app ~410, dx_stream ~273 (excluding benchmark),
  dx_compiler ~161, dx_modelzoo ~325, dx_planner ~84, dx_benchmark ~50 (dropped from
  ~75 after `dx_benchmark/core/` was removed — the server is now a pure viewer),
  dx_monitor ~60, shared ~244, i18n_audit ~110 — all passing when run separately.
- `i18n_audit`: findings = 0 (~3400 records scanned).
- Browser 6-language + zoom audits: Playwright, via `bash scripts/run_ci.sh --browser`
  (`tests/i18n_audit/test_browser_copy_audit.py`, `tests/test_zoom_*.py`).
