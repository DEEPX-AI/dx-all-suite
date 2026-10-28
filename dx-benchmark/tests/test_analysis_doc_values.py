"""Gate: every number printed in `docs/ANALYSIS_EN.md` / `docs/ANALYSIS_KOR.md` must be
reproducible from the committed result JSON.

Why this exists: the analysis documents are hand-written prose wrapped around
machine-measured numbers, and values have drifted before — a coefficient-of-variation
computed with the wrong stdev convention, ORT gain ranges rounded by hand, a "consistent
25-35%" claim that contradicted its own table. A wrong number in a customer-facing report
is worse than a missing one, so each table is recomputed here from
`results/<env>/<run>/*_results.json` and compared with what the document prints, in both
languages.

Tables are located by their caption (`**Table N.` in EN, `**표 N.` in KOR), so both
documents are checked by the same code. Prose figures that interpret a table are checked
as literal strings.

Run resolution mirrors the dashboard: runs are grouped by `environment.json`'s
`dx_all_suite_version`; the highest version present is the current release and the
next-highest supplies the §8 trend baseline. Adding a newer release therefore re-points
this gate automatically — the documents must then be regenerated to match.
"""
import json
import math
import re
import statistics
from collections import Counter
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path

import pytest

from benchmark.runner_pipeline import is_capacity_pass

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = [ROOT / "docs" / "ANALYSIS_EN.md", ROOT / "docs" / "ANALYSIS_KOR.md"]
SIZES = ["n", "s", "m", "l", "x"]
HEAVY = ["m", "l", "x"]
TASKS = ["object_detection", "pose_estimation", "segmentation", "oriented_bbox",
         "classification"]
VIDEO_TASKS = TASKS[:4]
TASK_LABELS = {"object_detection": "Object detection", "pose_estimation": "Pose estimation",
               "segmentation": "Segmentation", "oriented_bbox": "Oriented bounding box",
               "classification": "Classification"}
LABEL_TASKS = {v: k for k, v in TASK_LABELS.items()}
M1_HOSTS = ["DX-AIPlayer-N97_M1", "OrangePi5+_M1", "ROCK5B+_M1", "RPi5B_M1"]
FAMILY_FILES = ["model_results.json", "pipeline_results.json", "multi_stream_results.json"]
TIE_PCT = 5.0  # Table 18: "tie" = both nano and small differ by less than this


def _half_up(value, digits=0):
    """Round half away from zero — the convention the documents' prose uses."""
    quantum = Decimal(1).scaleb(-digits)
    return float(Decimal(repr(value)).quantize(quantum, rounding=ROUND_HALF_UP))


# ── result data ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=None)
def _rows(env, run, filename):
    return json.loads((RESULTS / env / run / filename).read_text())


@lru_cache(maxsize=None)
def _environment(env, run):
    return json.loads((RESULTS / env / run / "environment.json").read_text())


@lru_cache(maxsize=None)
def _runs_by_version():
    """{version: {env: latest run_id}} over every run that carries the JSON summaries."""
    by_version: dict[str, dict[str, str]] = {}
    if not RESULTS.is_dir():
        return by_version
    for env_dir in sorted(p for p in RESULTS.iterdir() if p.is_dir()):
        for run_dir in sorted(p for p in env_dir.iterdir() if p.is_dir()):
            if not all((run_dir / f).is_file() for f in FAMILY_FILES):
                continue
            env_file = run_dir / "environment.json"
            if not env_file.is_file():
                continue
            version = json.loads(env_file.read_text()).get("dx_all_suite_version")
            if not version:
                continue
            # sorted() above walks run ids chronologically → last wins
            by_version.setdefault(version, {})[env_dir.name] = run_dir.name
    return by_version


def _versions():
    ordered = sorted(_runs_by_version(), reverse=True)
    if len(ordered) < 2:
        pytest.skip("needs at least two dx-all-suite versions under results/")
    return ordered[0], ordered[1]


def _current():
    return _runs_by_version()[_versions()[0]]



def _threshold(env, run):
    return float(_environment(env, run).get("protocol", {}).get("fps_threshold", 30.0))


def _model(env, task, size, ort, family="throughput", runs=None):
    run = (runs or _current())[env]
    for row in _rows(env, run, "model_results.json"):
        if (row["task"] == task and row["size"] == size
                and bool(row["use_ort"]) is ort and row["family"] == family):
            return row
    return None


def _thr(env, task, size, ort, runs=None):
    return _model(env, task, size, ort, "throughput", runs)["fps"]


def _e2e(env, task, size, ort):
    run = _current()[env]
    for row in _rows(env, run, "pipeline_results.json"):
        if row["task"] == task and row["size"] == size and bool(row["use_ort"]) is ort:
            return row
    return None


def _e2e_best(env, task, size):
    candidates = [r for r in (_e2e(env, task, size, o) for o in (True, False))
                  if r and r.get("avg_e2e_fps")]
    return max(candidates, key=lambda r: r["avg_e2e_fps"])


def _passing(env, task, size, ort):
    run = _current()[env]
    threshold = _threshold(env, run)
    return [r for r in _rows(env, run, "multi_stream_results.json")
            if r["task"] == task and r["size"] == size and bool(r["use_ort"]) is ort
            and is_capacity_pass(r, threshold)]


def _channels(env, task, size, ort):
    return max((int(r["stream_count"]) for r in _passing(env, task, size, ort)), default=0)


def _pick(env, task, size):
    """The documents' one-mode-per-cell rule: more channels, tie → higher single-stream FPS.

    Returns (channels, single-stream E2E row) of the chosen mode.
    """
    options = []
    for ort in (True, False):
        row = _e2e(env, task, size, ort)
        options.append((_channels(env, task, size, ort), row["avg_e2e_fps"], ort, row))
    channels, _, _, row = max(options, key=lambda o: (o[0], o[1]))
    return channels, row


def _mode(row):
    return "ON" if row["use_ort"] else "OFF"


# ── document parsing ────────────────────────────────────────────────────────
@lru_cache(maxsize=None)
def _text(doc):
    return Path(doc).read_text(encoding="utf-8")


def _table(doc, number):
    """Rows of the markdown table that follows the caption `**Table N.` / `**표 N.`."""
    lines = _text(doc).splitlines()
    pattern = re.compile(rf"^\*\*(Table|표) {number}\.")
    start = next((i for i, line in enumerate(lines) if pattern.match(line)), None)
    assert start is not None, f"caption of table {number} not found"
    rows, inside = [], False
    for line in lines[start + 1:]:
        if line.startswith("|"):
            inside = True
            if set(line) <= set("|-: "):
                continue
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif inside:
            break
    assert len(rows) > 1, f"table {number} is empty"
    return rows[1:]  # drop the header row


def _keyed(doc, number, column=0):
    out = {}
    for cells in _table(doc, number):
        key = cells[column].replace("**", "").split(" (")[0].strip()
        out[key] = cells
    return out


def _num(text):
    cleaned = (text.replace("**", "").replace("%", "").replace("×", "")
               .replace("fps", "").replace(",", "").replace("+", "")
               .replace("−", "-").strip())
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group()) if match else None


def _nums(text):
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text.replace("**", ""))]


def _cell(text):
    """`493.6 / 17 (ON)` → (493.6, 17, 'ON')."""
    match = re.match(r"([\d.]+) / (\d+) \((ON|OFF)\)", text.strip())
    assert match, f"unexpected cell format: {text!r}"
    return float(match.group(1)), int(match.group(2)), match.group(3)


def _span(values, digits, suffix=""):
    low, high = _half_up(min(values), digits), _half_up(max(values), digits)
    return f"{low:.{digits}f}–{high:.{digits}f}{suffix}"


def _require(doc, *expected):
    text = _text(doc)
    for value in expected:
        assert value in text, f"{Path(doc).name}: expected '{value}' in the prose"


def _skip_without_data():
    if not RESULTS.is_dir() or not _runs_by_version():
        pytest.skip("no committed results/ data to verify against")


pytestmark = pytest.mark.parametrize("doc", [str(d) for d in DOCS],
                                    ids=[d.stem for d in DOCS])


# ── Tables 1 and 12–15: E2E FPS / channels, one ORT mode per cell ───────────
def test_headline_table_uses_one_mode_per_cell(doc):
    _skip_without_data()
    rows = _keyed(doc, 1)
    assert set(rows) == set(_current())
    for env, cells in rows.items():
        for index, task in enumerate(VIDEO_TASKS, start=1):
            fps, channels, mode = _cell(cells[index])
            want_channels, row = _pick(env, task, "n")
            assert (fps, channels, mode) == (round(row["avg_e2e_fps"], 1), want_channels,
                                             _mode(row)), f"{env} {task}"
        best = _e2e_best(env, "classification", "n")
        assert _num(cells[5]) == pytest.approx(round(best["avg_e2e_fps"], 1), abs=0.05)


@pytest.mark.parametrize("number,task", [(6, "object_detection"), (7, "pose_estimation"),
                                         (8, "segmentation"), (9, "oriented_bbox")])
def test_video_tables_use_one_mode_per_cell(doc, number, task):
    _skip_without_data()
    rows = _keyed(doc, number)
    assert set(rows) == set(_current())
    for env, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            fps, channels, mode = _cell(cells[index])
            want_channels, row = _pick(env, task, size)
            assert (fps, channels, mode) == (round(row["avg_e2e_fps"], 1), want_channels,
                                             _mode(row)), f"{env} {task} {size}"


# ── §3 NPU capability (complete model, ORT ON) ─────────────────────────────
def test_complete_model_throughput_table(doc):
    _skip_without_data()
    seen = 0
    for cells in _table(doc, 3):
        task, env = LABEL_TASKS[cells[0]], cells[1]
        for index, size in enumerate(SIZES, start=2):
            assert _num(cells[index]) == pytest.approx(
                round(_thr(env, task, size, True), 1), abs=0.05), f"{env} {task} {size}"
        seen += 1
    assert seen == len(TASKS) * len(_current())


def _module_ratios(task, sizes=("l", "x")):
    m1 = {s: [_thr(h, task, s, True) for h in M1_HOSTS] for s in sizes}
    cv = [statistics.pstdev(v) / statistics.mean(v) * 100 for v in m1.values()]
    h1 = [_thr("BIOSTAR_H1-Quattro", task, s, True) / statistics.mean(m1[s]) for s in sizes]
    m1m = [_thr("RPi5B_M1M", task, s, True) / _thr("RPi5B_M1", task, s, True) for s in sizes]
    return cv, h1, m1m


def test_module_comparison_table_and_findings(doc):
    _skip_without_data()
    rows = _keyed(doc, 4)
    all_cv, all_h1, all_m1m = [], [], []
    for label, cells in rows.items():
        cv, h1, m1m = _module_ratios(LABEL_TASKS[label])
        assert _num(cells[1]) == pytest.approx(_half_up(max(cv), 1), abs=0.05), label
        assert cells[2] == _span(h1, 2, "×"), label
        assert cells[3] == _span(m1m, 2, "×"), label
        all_cv += cv
        all_h1 += h1
        all_m1m += m1m
    assert len(rows) == len(TASKS)
    _require(doc, f"{_half_up(max(all_cv), 1):.1f}%", _span(all_h1, 2, "×"),
             _span(all_m1m, 2, "×"))


def test_section3_prose(doc):
    """§3: m is NPU-bound except on RPi5B_M1 (det/seg); n is host-dependent; order at l."""
    _skip_without_data()
    det_m = {h: _thr(h, "object_detection", "m", True) for h in M1_HOSTS}
    others = [v for h, v in det_m.items() if h != "RPi5B_M1"]
    _require(doc, f"{det_m['RPi5B_M1']:.1f}", _span(others, 1))
    _require(doc, f"{_thr('DX-AIPlayer-N97_M1', 'object_detection', 'n', True):.1f} fps",
             f"{_thr('RPi5B_M1', 'object_detection', 'n', True):.1f} fps")
    for env in _current():
        v = {t: _thr(env, t, "l", True) for t in TASKS}
        assert (v["classification"] > v["object_detection"] > v["pose_estimation"]
                > v["segmentation"] > v["oriented_bbox"]), env


# ── §6 limiting factors ─────────────────────────────────────────────────────
def test_pipeline_ceiling_table(doc):
    _skip_without_data()
    rows = _keyed(doc, 12)
    assert set(rows) == set(_current())
    utils = []
    for env, cells in rows.items():
        best = _e2e_best(env, "classification", "n")
        cores = _environment(env, _current()[env])["host"]["cpu_count"]
        assert best["decoder"] in cells[1]
        assert _num(cells[2]) == pytest.approx(round(best["avg_e2e_fps"], 1), abs=0.05)
        assert _nums(cells[3]) == [_half_up(best["avg_cpu_pct"]), cores * 100], env
        utils.append(best["npu_total_avg_pct"])
    _require(doc, f"{_half_up(min(utils)):.0f}–{_half_up(max(utils)):.0f}%")


def test_ort_on_off_ratio_table_and_prose(doc):
    _skip_without_data()
    rows = _keyed(doc, 13)
    assert set(rows) == set(_current())
    for env, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            ratio = (_thr(env, "object_detection", size, True)
                     / _thr(env, "object_detection", size, False))
            assert _num(cells[index]) == pytest.approx(round(ratio, 2), abs=0.005), \
                f"{env} {size}"
    arch = {e: _environment(e, r)["host"]["arch"] for e, r in _current().items()}
    nano = {e: _thr(e, "object_detection", "n", True) / _thr(e, "object_detection", "n", False)
            for e in arch}
    _require(doc, _span([v for e, v in nano.items() if arch[e] == "x86_64"], 2),
             _span([v for e, v in nano.items() if arch[e] != "x86_64"], 2))
    rpi = [_thr("RPi5B_M1", "object_detection", s, True) for s in ("n", "s", "m")]
    _require(doc, *(f"{v:.1f}" for v in rpi))


def test_cpu_part_latency_ranges(doc):
    _skip_without_data()
    current = _current()
    x86 = [e for e in current
           if _environment(e, current[e])["host"]["arch"] == "x86_64"]
    for group in (x86, [e for e in current if e not in x86]):
        values = [_model(e, "object_detection", s, True, "latency")["cpu_0_ms"]
                  for e in group for s in ("n", "m", "x")]
        _require(doc, _span(values, 2, " ms"))


def test_pcie_link_table_and_prose(doc):
    _skip_without_data()
    rows = _keyed(doc, 14)
    assert set(rows) == set(M1_HOSTS)
    for env, cells in rows.items():
        link = _environment(env, _current()[env])["npu"]["pcie"].split(" [")[0]
        assert cells[1].replace("×", "X") == link, env
        for index, task in enumerate(TASKS, start=2):
            assert _num(cells[index]) == pytest.approx(
                round(_thr(env, task, "n", False), 1), abs=0.05), f"{env} {task}"
    wide = [h for h in M1_HOSTS if h != "RPi5B_M1"]
    losses = [(1 - _thr("RPi5B_M1", t, "n", False) / _thr(h, t, "n", False)) * 100
              for t in ("object_detection", "segmentation") for h in wide]
    _require(doc, _span(losses, 0, "%"),
             f"{_half_up(_model('RPi5B_M1', 'object_detection', 'n', False)['npu_total_avg_pct']):.0f}%")
    for task in ("oriented_bbox", "classification"):
        values = [_thr(h, task, "n", False) for h in M1_HOSTS]
        assert statistics.pstdev(values) / statistics.mean(values) < 0.03, \
            f"{task}: claimed unaffected by the ×1 link"


def test_throttle_table(doc):
    _skip_without_data()
    rows = _keyed(doc, 15)
    assert set(rows) == set(_current())
    for env, cells in rows.items():
        run = _current()[env]
        for index, filename in enumerate(FAMILY_FILES[1:], start=1):
            data = _rows(env, run, filename)
            throttled, total = (_num(x) for x in cells[index].split("/"))
            assert throttled == sum(1 for r in data if r.get("npu_throttled")), \
                f"{env} {filename}"
            assert total == len(data), f"{env} {filename} cell count"
        temps = [(r.get("npu_temp_max_c") or 0) for f in FAMILY_FILES
                 for r in _rows(env, run, f)]
        assert _num(cells[3]) == pytest.approx(max(temps), abs=0.05), f"{env} max temp"
    throughput = [r for e, run in _current().items()
                  for r in _rows(e, run, "model_results.json") if r["family"] == "throughput"]
    assert not any(r.get("npu_throttled") for r in throughput)
    _require(doc, str(len(throughput)))
    floors = [r["npu_clock_mhz_min"] for e, run in _current().items() for f in FAMILY_FILES
              for r in _rows(e, run, f) if r.get("npu_throttled")]
    _require(doc, f"{min(floors):.0f}–{max(floors):.0f} MHz")


def test_sustained_heavy_model_table(doc):
    _skip_without_data()
    rows = _keyed(doc, 16)
    assert set(rows) == set(_current())
    for env, cells in rows.items():
        for index, task in enumerate(VIDEO_TASKS, start=1):
            _, row = _pick(env, task, "x")
            share = row["avg_e2e_fps"] / _thr(env, task, "x", True) * 100
            values = _nums(cells[index])
            assert values[0] == _half_up(share), f"{env} {task}"
            if row["npu_throttled"]:
                assert values[1:] == [row["npu_clock_mhz_min"]], f"{env} {task} clock"
            else:
                assert len(values) == 1, f"{env} {task}: unthrottled cell shows a clock"
    rock = [_pick("ROCK5B+_M1", t, "x")[1] for t in VIDEO_TASKS]
    shares = [r["avg_e2e_fps"] / _thr("ROCK5B+_M1", t, "x", True) * 100
              for t, r in zip(VIDEO_TASKS, rock)]
    _require(doc, f"{_half_up(min(shares)):.0f}–{_half_up(max(shares)):.0f}%")
    # finding 5: boards whose NPU held 1000 MHz in every x E2E cell run at ~full throughput
    steady = []
    for env in ("BIOSTAR_H1-Quattro", "RPi5B_M1"):
        for task in VIDEO_TASKS:
            _, row = _pick(env, task, "x")
            assert not row["npu_throttled"], f"{env} {task}"
            steady.append(row["avg_e2e_fps"] / _thr(env, task, "x", True) * 100)
    _require(doc, f"{_half_up(min(steady)):.0f}–{_half_up(max(steady)):.0f}%")


def test_npu_memory_table_and_claims(doc):
    _skip_without_data()
    rows = _keyed(doc, 17)
    for label, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            values = {_model(e, LABEL_TASKS[label], size, False, "latency")["npu_model_mem_bytes"]
                      for e in _current()}
            assert len(values) == 1, f"{label} {size}: differs between environments"
            assert _num(cells[index]) == _half_up(values.pop() / 2**20), f"{label} {size}"
    # shared model: no multi-stream row holds more NPU memory than one loaded model
    # (+ runtime overhead), whatever its stream count
    for env, run in _current().items():
        for row in _rows(env, run, "multi_stream_results.json"):
            model = _model(env, row["task"], row["size"], bool(row["use_ort"]), "latency")
            assert (row.get("npu_mem_max_mib") or 0) <= \
                model["npu_model_mem_bytes"] / 2**20 + 30, f"{env} {row['task']} {row['size']}"


def test_host_memory_prose(doc):
    """§4.5: RSS at the highest passing count; per-channel step over all measured counts."""
    _skip_without_data()
    tops, steps, single_chip = [], [], []
    for env, run in _current().items():
        passing, measured = {}, {}
        for row in _rows(env, run, "multi_stream_results.json"):
            if not row.get("max_rss_mib"):
                continue
            key = (row["task"], row["size"], bool(row["use_ort"]))
            point = (row["stream_count"], row["max_rss_mib"])
            measured.setdefault(key, []).append(point)
            if is_capacity_pass(row, _threshold(env, run)):
                passing.setdefault(key, []).append(point)
        for points in passing.values():
            top = max(points)[1]
            tops.append(top)
            if env != "BIOSTAR_H1-Quattro":
                single_chip.append(top)
        for points in measured.values():
            points.sort()
            steps += [(r1 - r0) / (n1 - n0) for (n0, r0), (n1, r1) in zip(points, points[1:])]
    steps.sort()
    _require(doc, f"≈{_half_up(min(tops)):.0f} MiB", f"≈{_half_up(max(tops)):.0f} MiB",
             f"{_half_up(statistics.median(steps)):.0f} MiB",
             f"{_half_up(steps[int(len(steps) * 0.9)]):.0f} MiB")
    assert max(single_chip) < 0.75 * 1024


# ── §5 video pipeline ───────────────────────────────────────────────────────
def test_npu_utilisation_table(doc):
    _skip_without_data()
    rows = _keyed(doc, 10)
    assert set(rows) == set(_current())
    nano = []
    for env, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            _, row = _pick(env, "object_detection", size)
            assert _num(cells[index]) == _half_up(row["npu_total_avg_pct"]), f"{env} {size}"
        nano.append(_pick(env, "object_detection", "n")[1]["npu_total_avg_pct"])
    _require(doc, f"{_half_up(min(nano)):.0f}–{_half_up(max(nano)):.0f}%")


def _aggregate_ratio_at_max(env, task, size):
    channels, row = _pick(env, task, size)
    top = max(_passing(env, task, size, bool(row["use_ort"])),
              key=lambda r: r["stream_count"])
    return top["avg_e2e_fps"] / row["avg_e2e_fps"], top


def test_channel_estimate_distribution(doc):
    _skip_without_data()
    rows = _keyed(doc, 11)
    diffs = {s: Counter() for s in SIZES}
    for env in _current():
        for task in VIDEO_TASKS:
            for size in SIZES:
                channels, row = _pick(env, task, size)
                diffs[size][channels - math.floor(row["avg_e2e_fps"] / 30)] += 1
    total = sum(sum(c.values()) for c in diffs.values())
    for size, cells in rows.items():
        printed = [int(_num(c)) for c in cells[1:]]
        assert printed == [diffs[size][d] for d in (0, 1, 2, -1, -2)], size
        assert sum(printed) == sum(diffs[size].values()), f"{size}: unlisted difference"
    exact = sum(c[0] for c in diffs.values())
    _require(doc, f"{exact}", f"{total}")
    pattern = rf"(?<!\d){exact}(?!\d)[^.\n]*(?<!\d){total}(?!\d)"
    reverse = rf"(?<!\d){total}(?!\d)[^.\n]*(?<!\d){exact}(?!\d)"
    assert re.search(pattern, _text(doc)) or re.search(reverse, _text(doc)), \
        "exact-estimate count"


def test_channel_estimate_prose(doc):
    _skip_without_data()
    nano_detection = [_aggregate_ratio_at_max(e, "object_detection", "n")[0]
                      for e in _current()]
    low, high = (_half_up((r - 1) * 100) for r in (min(nano_detection), max(nano_detection)))
    _require(doc, f"{low:+.0f}%".replace("-", "−"), f"{high:+.0f}%")
    light = [_aggregate_ratio_at_max(e, t, s)[0]
             for e in _current() for t in VIDEO_TASKS for s in ("n", "s")]
    _require(doc, f"{max(light):.2f}×")
    # m/l cells below the estimate: all throttled; total rate at the first failing count
    below, failing = [], []
    for env in _current():
        for task in VIDEO_TASKS:
            for size in ("m", "l"):
                channels, row = _pick(env, task, size)
                if channels >= math.floor(row["avg_e2e_fps"] / 30):
                    continue
                ort = bool(row["use_ort"])
                rows = [r for r in _rows(env, _current()[env], "multi_stream_results.json")
                        if r["task"] == task and r["size"] == size and bool(r["use_ort"]) is ort]
                first = min((r for r in rows if r["stream_count"] > channels),
                            key=lambda r: r["stream_count"])
                assert first["npu_throttled"], f"{env} {task} {size}"
                below.append(first["npu_clock_mhz_min"])
                failing.append(first["avg_e2e_fps"] / row["avg_e2e_fps"])
    _require(doc, f"{min(below):.0f}–{max(below):.0f} MHz", _span(failing, 2, "×"),
             str(len(below)))


# ── §4 latency ──────────────────────────────────────────────────────────────
def test_latency_table(doc):
    _skip_without_data()
    rows = _keyed(doc, 5)
    assert set(rows) == set(_current())
    for env, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            row = _model(env, "object_detection", size, True, "latency")
            assert _num(cells[index]) == pytest.approx(round(row["total_ms"], 2),
                                                       abs=0.005), f"{env} {size}"


def test_latency_versus_capacity_example(doc):
    _skip_without_data()
    latency = _model("DX-AIPlayer-N97_M1", "object_detection", "n", True, "latency")["total_ms"]
    _require(doc, f"{latency:.1f} ms",
             f"{_thr('DX-AIPlayer-N97_M1', 'object_detection', 'n', True):.1f} fps",
             f"≈ {_half_up(1000 / latency):.0f} fps")


# ── §7 ORT mode ─────────────────────────────────────────────────────────────
def _ort_gains(env, task):
    """{size: signed gain %} — positive when ORT ON wins, negative when OFF wins."""
    gains = {}
    for size in ("n", "s"):
        a = _e2e(env, task, size, True)["avg_e2e_fps"]
        b = _e2e(env, task, size, False)["avg_e2e_fps"]
        gains[size] = (a / b - 1) * 100 if a >= b else -((b / a - 1) * 100)
    return gains


def test_ort_matrix(doc):
    _skip_without_data()
    rows = _keyed(doc, 18)
    assert set(rows) == set(_current())
    for env, cells in rows.items():
        for index, task in enumerate(TASKS, start=1):
            gains = _ort_gains(env, task)
            cell = cells[index].replace("**", "")
            is_tie = all(abs(g) <= TIE_PCT for g in gains.values())
            expected = ("tie" if is_tie
                        else ("ON" if statistics.mean(list(gains.values())) > 0 else "OFF"))
            printed = "tie" if "tie" in cell else ("ON" if cell.startswith("ON") else "OFF")
            assert printed == expected, f"{env} {task}: {gains}"
            if expected != "tie":
                magnitudes = sorted(abs(g) for g in gains.values())
                values = _nums(cell)
                assert values[0] == pytest.approx(magnitudes[0], abs=0.05)
                assert values[-1] == pytest.approx(magnitudes[-1], abs=0.05)
    on = _e2e("OrangePi5+_M1", "object_detection", "n", True)
    off = _e2e("OrangePi5+_M1", "object_detection", "n", False)
    _require(doc, f"{_half_up((on['avg_e2e_fps'] / off['avg_e2e_fps'] - 1) * 100):.0f}%",
             f"{on['avg_e2e_fps']:.1f}", f"{off['avg_e2e_fps']:.1f}",
             f"{_half_up(off['avg_cpu_pct']):.0f}%", f"{_half_up(on['avg_cpu_pct']):.0f}%")
    rpi = [abs(g) for e in ("RPi5B_M1", "RPi5B_M1M")
           for g in _ort_gains(e, "object_detection").values()]
    assert all(g < 0 for e in ("RPi5B_M1", "RPi5B_M1M")
               for g in _ort_gains(e, "object_detection").values()), "RPi5: ORT OFF faster"
    _require(doc, f"{_half_up(min(rpi)):.0f}–{_half_up(max(rpi)):.0f}%")


# ── §8 environments ─────────────────────────────────────────────────────────
def test_environment_table(doc):
    """§9.1 (no caption number): arch, RAM, PCIe link and decoder of every environment."""
    _skip_without_data()
    lines = _text(doc).splitlines()
    for env, run in _current().items():
        info = _environment(env, run)
        line = next(l for l in lines if l.startswith(f"| **{env}** |") and "Gen3" in l)
        link = info["npu"]["pcie"].split(" [")[0].replace("X", "×")
        decoder = _e2e(env, "object_detection", "n", True)["decoder"]
        for expected in (link, decoder, info["host"]["arch"], f"{info['host']['ram_gb']} GB"):
            assert expected in line, f"{env}: {expected}"


# ── method / limitations prose ──────────────────────────────────────────────
def test_method_prose_values(doc):
    _skip_without_data()
    current = _current()
    targets = [_environment(e, r)["thermal"]["cooldown_target_c"] for e, r in current.items()]
    _require(doc, f"{min(targets):.0f}–{max(targets):.0f} °C")
    rk_spread = max(r["fps_std"] / r["fps"] * 100 for e in ("OrangePi5+_M1", "ROCK5B+_M1")
                    for r in _rows(e, current[e], "model_results.json")
                    if r["family"] == "throughput" and r["use_ort"])
    _require(doc, f"{_half_up(rk_spread, 1):.1f}%")
    winners = {s: statistics.median(r["buffer_count"] for e, run in current.items()
                                    for r in _rows(e, run, "model_results.json")
                                    if r["family"] == "throughput" and r["size"] == s)
               for s in SIZES}
    assert (winners["n"], winners["s"], winners["m"], winners["l"], winners["x"]) == \
        (6, 6, 5, 5, 4)
    for env, run in current.items():
        info = _environment(env, run)["video_infos"]
        for clip in info.values():
            _require(doc, clip["filename"], str(clip["nb_frames"]))


def test_key_findings_causes(doc):
    """The 'why' sentences of §1.2 rest on measured values."""
    heavy = [(e, t, s) for e in M1_HOSTS for t in TASKS for s in ("l", "x")]
    busy = [_model(e, t, s, True)["npu_total_avg_pct"] for e, t, s in heavy]
    cpu_part = [_model(e, t, s, True, "latency")["cpu_0_ms"] for e, t, s in heavy
                if _model(e, t, s, True, "latency")["cpu_0_ms"] is not None]
    frame_ms = [1000 / _thr(e, t, s, True) for e, t, s in heavy if t != "classification"]
    _require(doc, _span(busy, 0, "%"), _span(cpu_part, 0, " ms"), _span(frame_ms, 0, " ms"))

    for env in ("RPi5B_M1", "RPi5B_M1M"):
        assert _e2e(env, "object_detection", "n", True)["decoder"] == "avdec_h264"

    rock = [_pick("ROCK5B+_M1", t, "x")[1] for t in VIDEO_TASKS]
    assert all(r["npu_throttled"] for r in rock)
    _require(doc, _span([r["npu_clock_mhz_min"] for r in rock], 0, " MHz"))
