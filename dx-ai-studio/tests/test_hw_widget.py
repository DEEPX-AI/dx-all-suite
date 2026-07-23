from __future__ import annotations

from pathlib import Path
import json
import re
import shutil
import subprocess

import pytest

ROOT = Path(__file__).resolve().parent.parent
WIDGET = ROOT / "shared" / "hw_widget" / "widget.html"


def _widget_html() -> str:
    return WIDGET.read_text(encoding="utf-8")


def _widget_script() -> str:
    match = re.search(r"<script>\s*(.*?)\s*</script>", _widget_html(), re.S)
    assert match, "widget inline script is missing"
    return match.group(1)


_JS_HARNESS = r"""
const assert = require('assert');

const storage = STORAGE_PLACEHOLDER;
global.localStorage = {
  getItem(k) { return Object.prototype.hasOwnProperty.call(storage, k) ? String(storage[k]) : null; },
  setItem(k, v) { storage[k] = String(v); },
  removeItem(k) { delete storage[k]; },
};

const elements = {};
function makeElement(id) {
  const el = {
    id,
    textContent: '',
    innerHTML: '',
    hidden: false,
    style: {},
    dataset: {},
    offsetWidth: 220,
    offsetHeight: 200,
    _handlers: {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
    addEventListener(event, cb) {
      if (!this._handlers[event]) this._handlers[event] = [];
      this._handlers[event].push(cb);
    },
    _btnCache: {},
    querySelectorAll(selector) {
      if (selector !== 'button[data-npu-idx]') return [];
      const matches = Array.from(String(this.innerHTML).matchAll(/data-npu-idx="(\d+)"/g));
      const cacheKey = selector;
      if (!this._btnCache[cacheKey]) this._btnCache[cacheKey] = {};
      const parent = this;
      matches.forEach(match => {
        const idx = match[1];
        if (!this._btnCache[cacheKey][idx]) {
          const btn = makeElement('button-' + idx);
          btn.dataset.npuIdx = idx;
          btn.parentElement = parent;
          btn.click = function() {
            const selfEvt = { target: this, currentTarget: this };
            (this._handlers['click'] || []).forEach(cb => cb.call(this, selfEvt));
            const parentEvt = { target: this, currentTarget: parent };
            (parent._handlers['click'] || []).forEach(cb => cb.call(parent, parentEvt));
          };
          this._btnCache[cacheKey][idx] = btn;
        }
      });
      return matches.map(match => this._btnCache[cacheKey][match[1]]);
    },
    getBoundingClientRect() { return { left: 0, top: 0, width: 220, height: 200 }; },
  };
  if (id === 'hf-spark-canvas') {
    el.parentElement = { offsetWidth: 180 };
    el.getContext = function() {
      return {
        clearRect() {}, beginPath() {}, moveTo() {}, lineTo() {}, stroke() {},
        set strokeStyle(v) {}, set lineWidth(v) {},
      };
    };
  }
  return el;
}

[
  'hw-float', 'hw-float-drag', 'hf-npu-selector', 'hf-npu-title',
  'hf-temp', 'hf-volt', 'hf-clock', 'hf-dram', 'hf-util',
  'hf-cpu', 'hf-mem', 'hf-disk', 'hf-status', 'hf-spark-canvas',
  'hf-spark-label', 'hf-ctemps'
].forEach(id => { elements[id] = makeElement(id); });

global.document = {
  body: { style: {} },
  getElementById(id) { return elements[id] || null; },
  addEventListener() {},
};
global.window = global;
global.window.innerWidth = 1280;
global.window.innerHeight = 800;
global.window.addEventListener = function() {};
global.window.__DX_HW_WIDGET_TEST_HOOK__ = {};
global.requestAnimationFrame = function(fn) { fn(); };
global.setTimeout = function() { return 1; };
global.clearTimeout = function() {};
global.EventSource = function() {};
global.fetch = function(url) {
  if (url === '/dx_monitor/api/system_info') {
    return Promise.resolve({ json: () => Promise.resolve({ thresholds: {
      npu_temp: { warn: 70, crit: 85 },
      npu_dram: { warn: 80, crit: 95 },
    } }) });
  }
  return Promise.reject(new Error('unexpected fetch ' + url));
};

eval(SCRIPT_PLACEHOLDER);

const hook = global.window.__DX_HW_WIDGET_TEST_HOOK__;
assert.strictEqual(typeof hook.update, 'function', 'test hook must expose update');
assert.strictEqual(typeof hook.selectNpu, 'function', 'test hook must expose selectNpu');
assert.strictEqual(typeof hook.getSelectedIdx, 'function', 'test hook must expose getSelectedIdx');

SCENARIO_PLACEHOLDER

console.log('ALL ASSERTIONS PASSED');
"""


def _run_widget_harness(tmp_path: Path, scenario: str, storage: dict[str, str] | None = None) -> str:
    node = shutil.which("node")
    if not node:
        pytest.skip("node is required for hardware widget runtime test")
    harness = (
        _JS_HARNESS
        .replace("SCRIPT_PLACEHOLDER", json.dumps(_widget_script()))
        .replace("STORAGE_PLACEHOLDER", json.dumps(storage or {}))
        .replace("SCENARIO_PLACEHOLDER", scenario)
    )
    harness_path = tmp_path / "test_hw_widget.js"
    harness_path.write_text(harness, encoding="utf-8")
    result = subprocess.run([node, str(harness_path)], capture_output=True, text=True, timeout=15)
    if result.returncode != 0:
        pytest.fail(
            f"Node.js harness failed (rc={result.returncode}):\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )
    return result.stdout


@pytest.mark.requires_node
def test_hw_widget_can_switch_between_two_npus(tmp_path):
    scenario = r"""
hook.update({
  npus: [
    { id: 0, temp_avg: 41.2, voltage_avg: 750, clock_avg: 1000, dram_pct: 20.5, utilization: [40, 60], temperatures: [41.2] },
    { id: 1, temp_avg: 66.8, voltage_avg: 760, clock_avg: 900, dram_pct: 72.4, utilization: [80, 90], temperatures: [66.8] },
  ],
  cpu_load: 1.3,
  mem_pct: 40.1,
  disk_pct: 55.2,
});
assert.strictEqual(elements['hf-npu-selector'].hidden, false);
assert(elements['hf-npu-selector'].innerHTML.includes('NPU 0'));
assert(elements['hf-npu-selector'].innerHTML.includes('NPU 1'));
assert.strictEqual(elements['hf-temp'].textContent, '41.2°C');
assert.strictEqual(elements['hf-util'].textContent, '50.0%');
assert.strictEqual(elements['hf-dram'].textContent, '20.5%');
assert.strictEqual(elements['hf-clock'].textContent, '1000 MHz');
assert.strictEqual(elements['hf-volt'].textContent, '750 mV');

const selectorButtons = elements['hf-npu-selector'].querySelectorAll('button[data-npu-idx]');
assert.strictEqual(selectorButtons.length, 2);
selectorButtons[1].click();
assert.strictEqual(storage['hw-float-npu-idx'], '1');
assert.strictEqual(elements['hf-temp'].textContent, '66.8°C');
assert.strictEqual(elements['hf-util'].textContent, '85.0%');
assert.strictEqual(elements['hf-dram'].textContent, '72.4%');
assert.strictEqual(elements['hf-cpu'].textContent, '1.3');
assert.strictEqual(elements['hf-mem'].textContent, '40.1%');
assert.strictEqual(elements['hf-disk'].textContent, '55.2%');
"""
    assert "ALL ASSERTIONS PASSED" in _run_widget_harness(tmp_path, scenario)


@pytest.mark.requires_node
def test_hw_widget_hides_selector_for_single_npu(tmp_path):
    scenario = r"""
hook.update({
  npus: [{ id: 7, temp_avg: 45, voltage_avg: 750, clock_avg: 1000, dram_pct: 12, utilization: [10] }],
  cpu_load: 0.7,
  mem_pct: 30,
  disk_pct: 40,
});
assert.strictEqual(elements['hf-npu-selector'].hidden, true);
assert.strictEqual(elements['hf-temp'].textContent, '45.0°C');
"""
    assert "ALL ASSERTIONS PASSED" in _run_widget_harness(tmp_path, scenario)


@pytest.mark.requires_node
def test_hw_widget_falls_back_when_selected_index_disappears(tmp_path):
    scenario = r"""
hook.update({
  npus: [{ id: 0, temp_avg: 44.4, voltage_avg: 750, clock_avg: 1000, dram_pct: 15, utilization: [20] }],
  cpu_load: 0.9,
  mem_pct: 35,
  disk_pct: 45,
});
assert.strictEqual(hook.getSelectedIdx(), 0);
assert.strictEqual(storage['hw-float-npu-idx'], '0');
assert.strictEqual(elements['hf-temp'].textContent, '44.4°C');
"""
    assert "ALL ASSERTIONS PASSED" in _run_widget_harness(
        tmp_path,
        scenario,
        storage={"hw-float-npu-idx": "9"},
    )


@pytest.mark.requires_node
def test_hw_widget_stale_index_multi_npu_clamps_to_zero(tmp_path):
    scenario = r"""
hook.update({
  npus: [
    { id: 0, temp_avg: 40, voltage_avg: 700, clock_avg: 900, dram_pct: 10, utilization: [30], temperatures: [40] },
    { id: 1, temp_avg: 55, voltage_avg: 720, clock_avg: 950, dram_pct: 25, utilization: [60], temperatures: [55] },
  ],
  cpu_load: 1.0,
  mem_pct: 50,
  disk_pct: 60,
});
assert.strictEqual(hook.getSelectedIdx(), 0, 'stale index must clamp to 0');
assert.strictEqual(storage['hw-float-npu-idx'], '0', 'storage must be corrected');
assert.strictEqual(elements['hf-temp'].textContent, '40.0°C', 'must show NPU 0 data');
assert.strictEqual(elements['hf-npu-selector'].hidden, false, 'selector must be visible');
const html = elements['hf-npu-selector'].innerHTML;
assert(html.includes('class="active"'), 'first button must have active class');
assert(!html.includes('data-npu-idx="1" class="active"'), 'second button must not be active');
"""
    assert "ALL ASSERTIONS PASSED" in _run_widget_harness(
        tmp_path,
        scenario,
        storage={"hw-float-npu-idx": "9"},
    )


@pytest.mark.requires_node
def test_hw_widget_unknown_npu_dram_sentinel_renders_na(tmp_path):
    scenario = r"""
hook.update({
  npus: [{ id: 0, temp_avg: 45, voltage_avg: 750, clock_avg: 1000, dram_pct: -1, utilization: [10] }],
  cpu_load: 0.7,
  mem_pct: 30,
  disk_pct: 40,
});
assert.strictEqual(elements['hf-dram'].textContent, 'N/A');
"""
    assert "ALL ASSERTIONS PASSED" in _run_widget_harness(tmp_path, scenario)


@pytest.mark.requires_node
def test_hw_widget_missing_npu_values_render_na(tmp_path):
    scenario = r"""
hook.update({
  npus: [{ id: 0, utilization: [] }],
});
assert.strictEqual(elements['hf-temp'].textContent, 'N/A');
assert.strictEqual(elements['hf-volt'].textContent, 'N/A');
assert.strictEqual(elements['hf-clock'].textContent, 'N/A');
assert.strictEqual(elements['hf-dram'].textContent, 'N/A');
assert.strictEqual(elements['hf-util'].textContent, 'N/A');
assert.strictEqual(elements['hf-cpu'].textContent, 'N/A');
assert.strictEqual(elements['hf-mem'].textContent, 'N/A');
assert.strictEqual(elements['hf-disk'].textContent, 'N/A');
"""
    assert "ALL ASSERTIONS PASSED" in _run_widget_harness(tmp_path, scenario)


def test_hw_widget_static_contracts():
    html = _widget_html()
    script = _widget_script()
    for token in ('id="hf-npu-selector"', 'id="hf-npu-section"', 'id="hf-system-section"'):
        assert token in html
    assert "hw-float-npu-idx" in script
    assert "/dx_monitor/api/system_info" in script
    assert "function _normalizeDramPct" in script
    assert "_setValue('hf-dram',_fmt(_normalizeDramPct(n.dram_pct),1,'%')" in script
    assert "_statusFor('npu_dram',_normalizeDramPct(n.dram_pct))" in script
    assert "n.dram_pct>=0?n.dram_pct:0" not in script
    assert "d.npus[0]" not in script
    for token in ("hf-cpu", "hf-mem", "hf-disk"):
        assert token in html
