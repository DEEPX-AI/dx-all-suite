"""EdgeGuide RecommendEngine: runs the real recommend.js in Chromium.

Loading recommend.js into a blank page keeps the logic under test on hosts without Node.

What the engine must get right:
- 60 FPS is estimated, not 0 channels, when no row measured 60 per channel.
- A lower target (15 FPS) is estimated from the measured total, not capped at the highest tested
  stream count.
- One throttled row warns but does not zero a platform whose row holds the target.
- Missing latency is not a plain pass; "Best performance" ranks by end-to-end pipeline FPS, not
  single-model NPU FPS.
"""
from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

import pytest

pytest.importorskip("playwright.sync_api")

ROOT = Path(__file__).resolve().parents[2]
RECOMMEND_JS = ROOT / "dx_planner/static/js/recommend.js"
BENCHMARKS = ROOT / "dx_planner/static/data/benchmarks.json"


@pytest.fixture(scope="module")
def page():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    br = pw.chromium.launch(headless=True)
    pg = br.new_page()
    pg.set_content("<html><body></body></html>")
    pg.add_script_tag(content=RECOMMEND_JS.read_text(encoding="utf-8") + "\nwindow.RecommendEngine = RecommendEngine;")
    yield pg
    br.close()
    pw.stop()


def _rows(*rows, task="object_detection", size="n", ort=True):
    out = []
    for n, pcf, *rest in rows:
        throttled = rest[0] if rest else False
        npu_pct = rest[1] if len(rest) > 1 else 40.0
        out.append({"task": task, "size": size, "ort": ort, "stream_count": n, "per_channel_fps": pcf,
                    "total_fps": round(n * pcf, 1), "npu_throttled": throttled, "npu_total_avg_pct": npu_pct,
                    "fps_std": 0.5, "avg_cpu_pct": 200.0})
    return out


def _platform(pid, rows, *, latency=10.0, throughput=300.0, tdp=5, task="object_detection", size="n", ort=True):
    return {"id": pid, "npu": {"model": "DX-M1", "tops": 25, "tdp_w": tdp}, "host": {"name": pid},
            "benchmarks": [{"task": task, "size": size, "ort": ort, "latency_ms": latency,
                            "throughput_fps": throughput}],
            "multi_stream": rows}


def _inputs(**kw):
    base = {"task": "object_detection", "size": "n", "cameras": 1, "targetFps": 30,
            "priority": "channels", "ort": True, "maxLatencyMs": None}
    base.update(kw)
    return base


def _recommend(page, inputs, platforms):
    return page.evaluate("([i, p]) => RecommendEngine.recommend(i, p).map(r => ({...r, platform: r.platform.id}))",
                         [inputs, platforms])


def _one(page, rows, target, **kw):
    plat = _platform("p", rows, **{k: v for k, v in kw.items() if k in ("latency", "throughput", "tdp")})
    inputs = _inputs(targetFps=target, **{k: v for k, v in kw.items() if k in ("cameras", "maxLatencyMs")})
    return _recommend(page, inputs, [plat])[0]


def test_a_measured_boundary_is_the_answer(page):
    r = _one(page, _rows((9, 30.7), (10, 27.6)), 30)
    assert (r["maxChannels"], r["evidence"], r["boundaryFlag"]) == (9, "measured", "measured")
    assert r["why"]["kind"] == "measured" and r["why"]["atFps"] == 30.7
    assert r["why"]["nextN"] == 10 and r["why"]["nextFps"] == 27.6


def test_a_lower_target_than_measured_estimates_from_the_measured_total(page):
    # RPi5: 2 ch @ 40.1 (80.2 total), 3 ch @ 26.7 (80.1); at 15 FPS the answer is 5, not "3+"
    r = _one(page, _rows((2, 40.1), (3, 26.7)), 15)
    assert r["maxChannels"] == math.floor(80.1 / 15) == 5
    assert r["evidence"] == "estimated" and r["boundaryFlag"] == "estimated"
    assert r["why"]["kind"] == "estimated" and r["why"]["maxTested"] == 3


def test_an_estimate_never_runs_past_twice_the_tested_count(page):
    r = _one(page, _rows((14, 31.7), (15, 29.9)), 5)
    assert r["maxChannels"] == 30 and r["boundaryFlag"] == "+" and r["evidence"] == "estimated"


def test_sixty_fps_is_estimated_instead_of_zero(page):
    r = _one(page, _rows((14, 31.7), (15, 29.9)), 60)
    assert r["maxChannels"] == math.floor(min(14 * 31.7, 15 * 29.9) / 60) == 7
    assert r["evidence"] == "estimated"


def test_a_pipeline_that_cannot_feed_one_stream_is_zero(page):
    r = _one(page, _rows((1, 28.9)), 30, cameras=1)
    assert r["maxChannels"] == 0 and r["status"] == "short" and r["meetsRequirement"] is False


def test_throttling_warns_but_does_not_zero_the_platform(page):
    r = _one(page, _rows((4, 34.9, True, 93.5), (5, 25.0, True, 91.4)), 30, cameras=4)
    assert r["maxChannels"] == 4 and r["evidence"] == "measured"
    assert r["throttled"] is True and r["meetsRequirement"] is True


def test_the_bottleneck_says_whether_the_npu_or_the_host_was_saturated(page):
    assert _one(page, _rows((4, 34.9, False, 93.5), (5, 25.0, False, 91.4)), 30)["bottleneck"] == "npu"
    assert _one(page, _rows((14, 31.7, False, 25.7), (15, 29.9, False, 25.7)), 30)["bottleneck"] == "host"


def test_unknown_latency_with_a_budget_is_not_a_plain_pass(page):
    r = _one(page, _rows((9, 30.7), (10, 27.6)), 30, latency=None, maxLatencyMs=50)
    assert r["meetsLatency"] is None and r["status"] == "meets-estimated"
    over = _one(page, _rows((9, 30.7), (10, 27.6)), 30, latency=80, maxLatencyMs=50)
    assert over["meetsLatency"] is False and over["status"] == "short" and over["meetsRequirement"] is False
    unbounded = _one(page, _rows((9, 30.7), (10, 27.6)), 30, latency=None)
    assert unbounded["meetsLatency"] is True and unbounded["status"] == "meets"


def test_measured_beats_estimated_and_cool_beats_throttled(page):
    measured = _platform("measured", _rows((9, 30.7), (10, 27.6)))
    estimated = _platform("estimated", _rows((40, 25.0), (41, 24.0)))            # 30 FPS → ≈ 32 ch, estimated
    hot = _platform("hot", _rows((12, 31.0, True, 93.0), (13, 28.0, True, 93.0)))
    order = [r["platform"] for r in _recommend(page, _inputs(cameras=4), [estimated, hot, measured])]
    assert order == ["measured", "hot", "estimated"]


def test_performance_ranks_by_end_to_end_pipeline_fps_not_npu_only_fps(page):
    fast_npu = _platform("fast-npu", _rows((3, 31.0), (4, 24.0)), throughput=900.0)   # pipeline ≈ 93
    fast_pipe = _platform("fast-pipe", _rows((9, 30.7), (10, 27.6)), throughput=300.0)  # pipeline ≈ 276
    res = _recommend(page, _inputs(priority="performance"), [fast_npu, fast_pipe])
    assert [r["platform"] for r in res] == ["fast-pipe", "fast-npu"]
    assert res[0]["pipelineFps"] == pytest.approx(276.0, abs=0.2)
    assert res[0]["throughputFps"] == 300.0


def test_power_ranks_by_npu_tdp_then_fps_per_watt(page):
    a = _platform("m1", _rows((9, 30.7), (10, 27.6)), tdp=5)
    b = _platform("m1m", _rows((3, 31.0), (4, 24.0)), tdp=3)
    c = _platform("m1m-fast", _rows((6, 31.0), (7, 27.0)), tdp=3)
    order = [r["platform"] for r in _recommend(page, _inputs(priority="power"), [a, b, c])]
    assert order == ["m1m-fast", "m1m", "m1"]


def _combos():
    data = json.loads(BENCHMARKS.read_text(encoding="utf-8"))
    for p in data["platforms"]:
        groups = defaultdict(list)
        for m in p["multi_stream"]:
            groups[(m["task"], m["size"], m["ort"])].append(m)
        for key, rows in groups.items():
            yield data["platforms"], p, key, rows


@pytest.mark.parametrize("target", [15, 25, 30, 60])
def test_every_real_answer_agrees_with_every_measured_row(page, target):
    data = json.loads(BENCHMARKS.read_text(encoding="utf-8"))
    platforms = data["platforms"]
    zero_with_headroom, contradictions, checked = [], [], 0
    for task, size, ort in sorted({(m["task"], m["size"], m["ort"]) for p in platforms for m in p["multi_stream"]}):
        res = _recommend(page, _inputs(task=task, size=size, ort=ort, targetFps=target), platforms)
        for r in res:
            rows = [m for m in next(p for p in platforms if p["id"] == r["platform"])["multi_stream"]
                    if (m["task"], m["size"], m["ort"]) == (task, size, ort)]
            if not rows:
                continue
            checked += 1
            t_sat = min(m["total_fps"] for m in rows)
            if r["maxChannels"] == 0 and t_sat >= target:
                zero_with_headroom.append((r["platform"], task, size, ort))
            for m in rows:
                if m["per_channel_fps"] >= target and m["stream_count"] > r["maxChannels"]:
                    contradictions.append((r["platform"], task, size, ort, m["stream_count"], "sustains but excluded"))
    assert checked > 200
    assert not zero_with_headroom, zero_with_headroom[:5]
    assert not contradictions, contradictions[:5]
