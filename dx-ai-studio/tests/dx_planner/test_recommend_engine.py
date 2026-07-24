"""RecommendEngine logic tests (executed via Node.js VM).

Pure-benchmark redesign (2026-07-23): rankings derive ONLY from measured data.
- maxChannels = max stream_count where per_channel_fps >= targetFps AND NOT npu_throttled
- No FPS headroom, no confidenceTier/stabilityScore ranking, no CPU gate,
  no interpolated/theoretical fallback.
- sort: meets -> priority -> maxChannels -> throughput -> platform.id
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
RECOMMEND_JS = ROOT / "dx_planner/static/js/recommend.js"

_NODE_SCRIPT = r"""
const fs = require('fs');
const vm = require('vm');
const code = fs.readFileSync(process.argv[1], 'utf8').replace(/^const RecommendEngine/, 'var RecommendEngine');
const ctx = { console };
vm.createContext(ctx);
vm.runInContext(code, ctx);
const RecommendEngine = ctx.RecommendEngine;

function assert(cond, msg) {
  if (!cond) {
    console.error('FAIL:', msg);
    process.exit(1);
  }
}

// --- _calcMaxChannels: measured sustainable set, no headroom arg ---
const bench = { throughput_fps: 276, latency_ms: 10 };
const multi = [
  { stream_count: 9, per_channel_fps: 30.7, npu_throttled: false },
  { stream_count: 10, per_channel_fps: 27.6, npu_throttled: false },
];
const measured = RecommendEngine._calcMaxChannels(bench, multi, 30);
assert(measured.maxChannels === 9, 'stream9 (30.7>=30) sustainable, stream10 (27.6<30) not -> 9');
assert(measured.boundaryFlag === 'measured', 'maxChannels 9 != maxTested 10 -> measured');

// '+' when the top tested stream still sustains
const plus = RecommendEngine._calcMaxChannels(bench, [
  { stream_count: 4, per_channel_fps: 40, npu_throttled: false },
  { stream_count: 5, per_channel_fps: 33, npu_throttled: false },
], 30);
assert(plus.maxChannels === 5 && plus.boundaryFlag === '+', 'top tested stream sustains -> +');

// throttled rows are HARD-excluded even if per_channel_fps >= target
const throttled = RecommendEngine._calcMaxChannels(bench, [
  { stream_count: 5, per_channel_fps: 34.6, npu_throttled: false },
  { stream_count: 6, per_channel_fps: 28.5, npu_throttled: true },
], 30);
assert(throttled.maxChannels === 5, 'stream6 throttled excluded -> maxChannels 5');

// CPU% no longer gates: high avg_cpu_pct but not throttled and pcf>=target counts
const hicpu = RecommendEngine._calcMaxChannels(bench, [
  { stream_count: 9, per_channel_fps: 32.6, npu_throttled: false, avg_cpu_pct: 424.7 },
], 30);
assert(hicpu.maxChannels === 9, 'high CPU% but sustained -> counts (no CPU gate)');

// --- recommend(): multi-platform bug regression (OBB/m/ort, 18ch, channels) ---
function npu(model) { return { model: model, tops: 25, tdp_w: 5, dram: '1GB' }; }
const H1 = {
  id: 'biostar-h1-quattro',
  npu: npu('DX-H1'),
  host: { name: 'deepx-B650MT', cpu: 'Ryzen 9600X', ram_gb: 32, os: 'linux' },
  benchmarks: [{ task: 'oriented_bbox', size: 'm', ort: true, throughput_fps: 166.5, latency_ms: 55.42 }],
  multi_stream: [
    { task: 'oriented_bbox', size: 'm', ort: true, stream_count: 5, per_channel_fps: 34.6, npu_throttled: false },
    { task: 'oriented_bbox', size: 'm', ort: true, stream_count: 6, per_channel_fps: 28.5, npu_throttled: true },
  ],
};
const RPI = {
  id: 'rpi5b-m1',
  npu: npu('DX-M1'),
  host: { name: 'raspberrypi', cpu: 'A76', ram_gb: 8, os: 'linux' },
  benchmarks: [{ task: 'oriented_bbox', size: 'm', ort: true, throughput_fps: 39.8, latency_ms: 68.45 }],
  multi_stream: [
    { task: 'oriented_bbox', size: 'm', ort: true, stream_count: 1, per_channel_fps: 41.6, npu_throttled: false },
    { task: 'oriented_bbox', size: 'm', ort: true, stream_count: 2, per_channel_fps: 20.6, npu_throttled: false },
  ],
};
const inputs = {
  task: 'oriented_bbox', size: 'm', ort: true,
  targetFps: 30, cameras: 18, priority: 'channels', maxLatencyMs: 50,
};
const results = RecommendEngine.recommend(inputs, [RPI, H1]);
assert(results.length === 2, 'two results');
assert(results[0].platform.id === 'biostar-h1-quattro', 'TOP must be H1 (5ch), not RPi (1ch)');
assert(results[0].maxChannels === 5, 'H1 maxChannels 5 (stream6 throttled excluded)');
assert(results[0].meetsRequirement === false, 'nothing meets 18ch @ latency<=50');
assert(results[1].platform.id === 'rpi5b-m1', 'RPi second with 1ch');

// removed fields must be absent from result objects
assert(results[0].confidenceTier === undefined, 'confidenceTier removed');
assert(results[0].effectiveTargetFps === undefined, 'effectiveTargetFps removed');
assert(results[0].hostLimited === undefined, 'hostLimited removed (no CPU gate)');
assert(results[0].costPerChannelAtNeed === undefined, 'no pricing fields');

console.log('OK');
"""


def test_recommend_engine_node_logic():
    node = shutil.which("node")
    if not node:
        pytest.skip("node not available")

    proc = subprocess.run(
        [node, "-e", _NODE_SCRIPT, str(RECOMMEND_JS)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "OK" in proc.stdout


def test_recommend_engine_source_contracts():
    src = RECOMMEND_JS.read_text(encoding="utf-8")
    # New pure-benchmark logic present.
    for token in [
        "npu_throttled",          # throttle hard-exclusion
        "per_channel_fps",        # sustainable-set filter
        "case 'channels'",        # priority rank by measured channels
    ]:
        assert token in src, f"expected token {token!r} in recommend.js"
    # Removed policy layers must NOT reappear.
    for gone in [
        "fpsHeadroom", "_normalizeHeadroom", "effectiveTargetFps",
        "confidenceTier", "_interpolateCrossing", "_theoreticalFallback",
        "_rowForCameras", "_operationalLimits", "host-limited", "interpolated",
        "avg_cpu_pct", "cpuBudget", "DEFAULT_CPU_BUDGET_PCT",
        # pricing stays removed
        "costPerChannel", "price_usd",
    ]:
        assert gone not in src, f"removed token {gone!r} should be gone from recommend.js"
