# Testing

Tests are `pytest`, organized per module under `tests/<module>/`. Config lives in
`pytest.ini` (`testpaths = tests`) and `.coveragerc` (branch coverage over all module
source, excluding `*/tests/*`, `*/.venv/*`).

Use the venv interpreter: `./.venv/bin/python -m pytest …`.

## Test layers

| Layer | What it covers | Needs |
|-------|----------------|-------|
| **Unit** | `core/` logic — catalog build, config, parsers, prompt wrapping, aggregation, ONNX surgery, accuracy math | nothing (stdlib) |
| **Contract** | `server.py` routes against a live in-process server on an `18xxx` test port; i18n key parity; tutorial 6-lang; shared base handler / chat engine | nothing |
| **i18n audit** | `tests/i18n_audit/` — copy inventory, missing-language, integrity, runtime lang-hook gaps, Spanish/stale-copy coverage | nothing |
| **Browser** | Playwright copy audit + language-switch matrix (optional; scripts under `scripts/`) | `playwright` install |
| **E2E** | real compile / real inference / real CLI agents | `dx_com`, dx-runtime, NPU, or CLIs |

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

There is no `.github/workflows/` in this repo — the real gate is `scripts/run_ci.sh`
(the parent suite's `.github/workflows/` invokes it as the closed-net PR gate). It
runs six numbered stages in order:

```bash
bash scripts/run_ci.sh
```

```
0/6  Infra + release contracts — tests/test_pytest_infra_contract.py,
     tests/shared/test_ci_contracts.py, tests/shared/test_studio_version_contracts.py,
     tests/release/
1/6  Collection gate — tests/ --collect-only, must report 0 collection errors
     (--ignore=tests/dx_stream/benchmark and the Playwright browser tests)
2/6  Launcher suite (isolated — port collision with dx_agent_dev)
3/6  Agent Dev suite (isolated — port collision with launcher)
4/6  i18n audit gate — bash scripts/i18n_audit_gate.sh
5/6  Module + shared + root contract suites (no browser) — dx_app, dx_stream,
     dx_compiler, dx_modelzoo, dx_planner, dx_benchmark, dx_monitor, shared,
     i18n_audit, tests/test_*.py
```

Extra flags: `--browser` (adds the Playwright copy/lang-switch/tutorial suites,
needs `chromium` installed), `--ux` (full UX acceptance gate, slow, release only).

Coverage is a separate, non-blocking add-on (not one of the six stages):

```bash
./.venv/bin/python -m pip install pytest-cov   # not in requirements-ci.txt
bash scripts/run_ci.sh --coverage
```

This runs `tests/shared/ tests/launcher/` with `--cov=shared --cov=launcher
--cov-config=.coveragerc` and writes `coverage.xml`.

Additional helper/manual checks, not part of `run_ci.sh`:

- `bash scripts/i18n_smoke_matrix.sh` — full i18n smoke incl. matrix.
- `bash scripts/i18n_browser_audit.sh` — optional Playwright copy audit.
- Server smoke (manual, not gated by `run_ci.sh`): confirm the launcher binds and
  prints its live banner — `./.venv/bin/python launcher/launcher.py --port 8890
  --no-browser`.
- Hardening checks: `DX_BIND_LOCAL=1 ./launcher.sh` (loopback only) and
  `DX_API_TOKEN=secret ./launcher.sh` (401 without a bearer token).

## Baseline (module suites, run separately)

- launcher ~521, dx_agent_dev ~228, dx_app ~410, dx_stream ~273 (excluding benchmark),
  dx_compiler ~161, dx_modelzoo ~325, dx_planner ~84, dx_benchmark ~50 (dropped from
  ~75 after `dx_benchmark/core/` was removed — the server is now a pure viewer),
  dx_monitor ~60, shared ~244, i18n_audit ~110 — all passing when run separately.
- `i18n_audit`: findings = 0 (~3400 records scanned).
- Browser 6-language + zoom audits: Playwright, via `bash scripts/run_ci.sh --browser`
  (`tests/i18n_audit/test_browser_copy_audit.py`, `tests/test_zoom_*.py`).
