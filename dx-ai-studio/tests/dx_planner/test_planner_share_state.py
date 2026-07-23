"""dx_planner share-link + localStorage persistence tests (F-18).

Covers:
  * The generated share URL now includes `priority` and `latency` params.
  * planner.js persists inputs to localStorage and reads them back on load.
  * wizard.js `setInputs` accepts `priority` so a shared/restored priority applies.

Behavioural assertions run the real JS in a Node.js VM (like
test_recommend_engine.py); source-contract checks guard against regressions
when Node is unavailable.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
PLANNER_JS = ROOT / "dx_planner/static/js/planner.js"
WIZARD_JS = ROOT / "dx_planner/static/js/wizard.js"

_NODE_SCRIPT = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8');

const store = {};
const ctx = {
  console, URLSearchParams,
  window: {
    location: { origin: 'https://studio.example', pathname: '/planner', search: '' },
    history: { replaceState() {} },
  },
  document: {
    addEventListener() {}, querySelector() { return null; },
    querySelectorAll() { return []; }, getElementById() { return null; },
  },
  localStorage: {
    getItem(k) { return k in store ? store[k] : null; },
    setItem(k, v) { store[k] = String(v); },
    removeItem(k) { delete store[k]; },
  },
};
vm.createContext(ctx);
vm.runInContext(code, ctx);

function assert(cond, msg) {
  if (!cond) { console.error('FAIL:', msg); process.exit(1); }
}

const Runtime = ctx.window.PlannerRuntime;
assert(Runtime && typeof Runtime.buildShareUrl === 'function', 'PlannerRuntime.buildShareUrl exists');

const inputs = {
  task: 'pose_estimation', size: 'm', cameras: 2, targetFps: 30,
  ort: false, priority: 'performance', maxLatencyMs: 100,
};
const url = Runtime.buildShareUrl(inputs);
const qs = new URLSearchParams(url.split('?')[1] || '');

assert(qs.get('priority') === 'performance', 'share URL carries priority');
assert(qs.get('latency') === '100', 'share URL carries latency');
assert(qs.get('task') === 'pose_estimation', 'share URL still carries task');
assert(qs.get('ort') === 'false', 'share URL still carries ort');

console.log('OK');
"""


def _node_or_skip() -> str:
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")
    return node


def test_share_url_includes_priority_and_latency():
    node = _node_or_skip()
    proc = subprocess.run(
        [node, "-e", _NODE_SCRIPT, str(PLANNER_JS)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK" in proc.stdout


def test_planner_js_persists_and_restores_state():
    src = PLANNER_JS.read_text(encoding="utf-8")
    # localStorage persistence seam.
    assert "localStorage" in src
    assert "PLANNER_STORAGE_KEY" in src
    assert "persistPlannerState" in src
    assert "loadPersistedState" in src
    # Load path parses the previously-dropped share params.
    assert "urlParams.get('priority')" in src
    assert "urlParams.get('latency')" in src
    # Share URL builder emits both params.
    assert "params.set('priority'" in src
    assert "params.set('latency'" in src


def test_wizard_setinputs_accepts_priority():
    src = WIZARD_JS.read_text(encoding="utf-8")
    # priority must be a destructured/handled setInputs param, not silently dropped.
    assert "priority }" in src or "priority," in src
    assert "this._state.priority = priority" in src
