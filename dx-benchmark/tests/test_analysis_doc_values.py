"""Gate: every number printed in `docs/ANALYSIS_EN.md` / `docs/ANALYSIS_KOR.md` must be
reproducible from the committed result JSON.

Why this exists: the analysis documents are hand-written prose wrapped around
machine-measured numbers, and values have drifted before — a coefficient-of-variation
computed with the wrong stdev convention, a clock-floor range quoted from the wrong subset
of cells, ORT gain ranges rounded by hand, a "consistent 25-35%" claim that contradicted
its own table. A wrong number in a customer-facing report is worse than a missing one, so
each table is recomputed here from `results/<env>/<run>/*_results.json` and compared with
what the document actually prints, in both languages.

Run resolution mirrors the dashboard: runs are grouped by `environment.json`'s
`dx_all_suite_version`; the highest version present is the current release (§1, §5-§8) and
the next-highest supplies the §9 trend baseline. Adding a newer release therefore re-points
this gate automatically — the documents must then be regenerated to match.
"""
import json
import re
import statistics
from decimal import Decimal, ROUND_HALF_UP
from functools import lru_cache
from pathlib import Path

import pytest

from benchmark.runner_pipeline import is_capacity_pass

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = [ROOT / "docs" / "ANALYSIS_EN.md", ROOT / "docs" / "ANALYSIS_KOR.md"]
SIZES = ["n", "s", "m", "l", "x"]
TASKS = ["object_detection", "pose_estimation", "segmentation", "oriented_bbox",
         "classification"]
M1_HOSTS = ["DX-AIPlayer-N97_M1", "OrangePi5+_M1", "ROCK5B+_M1", "RPi5B_M1"]
FAMILY_FILES = ["model_results.json", "pipeline_results.json", "multi_stream_results.json"]
# §5.1 / §7.1 / §7.2 sample specific environments; keep them next to the doc tables.
E2E_RATIO_ENVS = ["BIOSTAR_H1-Quattro", "OrangePi5+_M1", "RPi5B_M1"]
TASK_ORDER_ENVS = ["BIOSTAR_H1-Quattro", "RPi5B_M1"]
TIE_PCT = 5.0  # §7.2: "tie" = both nano and small differ by less than this


def _half_up(value, digits=0):
    """Round half away from zero — the convention the documents' prose uses."""
    quantum = Decimal(1).scaleb(-digits)
    return float(Decimal(repr(value)).quantize(quantum, rounding=ROUND_HALF_UP))


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


def _baseline():
    return _runs_by_version()[_versions()[1]]


def _threshold(env, run):
    return float(_environment(env, run).get("protocol", {}).get("fps_threshold", 30.0))


def _model_row(env, run, task, size, ort, family):
    for row in _rows(env, run, "model_results.json"):
        if (row["task"] == task and row["size"] == size
                and bool(row["use_ort"]) is ort and row["family"] == family):
            return row
    return None


def _e2e_row(env, run, task, size, ort):
    for row in _rows(env, run, "pipeline_results.json"):
        if row["task"] == task and row["size"] == size and bool(row["use_ort"]) is ort:
            return row
    return None


def _e2e_best(env, run, task, size):
    candidates = [r for r in (_e2e_row(env, run, task, size, o) for o in (True, False))
                  if r and r.get("avg_e2e_fps")]
    return max(candidates, key=lambda r: r["avg_e2e_fps"]) if candidates else None


def _capacity(env, run, task, size):
    threshold = _threshold(env, run)
    passing = [int(r.get("stream_count") or 0)
               for r in _rows(env, run, "multi_stream_results.json")
               if r["task"] == task and r["size"] == size and is_capacity_pass(r, threshold)]
    return max(passing, default=0)


def _m1_mean(size):
    current = _current()
    return statistics.mean(
        _model_row(h, current[h], "object_detection", size, False, "throughput")["fps"]
        for h in M1_HOSTS
    )


def _ort_gains(env, run, task):
    """{size: signed gain %} — positive when ORT ON wins, negative when OFF wins."""
    gains = {}
    for size in ("n", "s"):
        on = _e2e_row(env, run, task, size, True)
        off = _e2e_row(env, run, task, size, False)
        if not (on and off and on.get("avg_e2e_fps") and off.get("avg_e2e_fps")):
            continue
        a, b = on["avg_e2e_fps"], off["avg_e2e_fps"]
        gains[size] = (a / b - 1) * 100 if a >= b else -((b / a - 1) * 100)
    return gains


# ── document parsing ────────────────────────────────────────────────────────
@lru_cache(maxsize=None)
def _lines(doc):
    return tuple(Path(doc).read_text(encoding="utf-8").splitlines())


def _section(doc, heading_prefix):
    """Lines under the heading starting with `heading_prefix` (e.g. '## 5.', '### 7.2')."""
    out, inside = [], False
    for line in _lines(doc):
        if line.startswith("#"):
            if inside:
                break
            inside = line.startswith(heading_prefix)
            continue
        if inside:
            out.append(line)
    return out


def _table_rows(doc, heading_prefix, keys):
    """Table rows of a section whose first cell is in `keys`, as {key: [cells]}."""
    found = {}
    for line in _section(doc, heading_prefix):
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        key = cells[0].replace("**", "").split(" (")[0].strip()
        if key in keys:
            found[key] = cells
    return found


def _num(text):
    cleaned = (text.replace("**", "").replace("%", "").replace("×", "")
               .replace("fps", "").replace(",", "").replace("+", "")
               .replace("−", "-").strip())
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    return float(match.group()) if match else None


def _nums(text):
    return [float(x) for x in re.findall(r"\d+(?:\.\d+)?", text.replace("**", ""))]


def _skip_without_data():
    if not RESULTS.is_dir() or not _runs_by_version():
        pytest.skip("no committed results/ data to verify against")


pytestmark = pytest.mark.parametrize("doc", [str(d) for d in DOCS],
                                    ids=[d.stem for d in DOCS])


# ── §1 Executive summary ────────────────────────────────────────────────────
def test_summary_table_matches_raw_results(doc):
    """§1: `single-stream E2E fps / max channels` at nano, best ORT mode."""
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "## 1.", set(current))
    assert rows, "§1 summary table not found"
    for env, cells in rows.items():
        run = current[env]
        for index, task in enumerate(TASKS, start=1):
            cell = cells[index]
            best = _e2e_best(env, run, task, "n")
            assert best is not None, f"{env}/{task}: no nano E2E row"
            assert _num(cell.split("/")[0]) == pytest.approx(
                round(best["avg_e2e_fps"], 1), abs=0.05), f"{env} {task} fps"
            if "/" in cell:
                assert _num(cell.split("/")[1]) == _capacity(env, run, task, "n"), \
                    f"{env} {task} channels"


# ── §2.2 M1 vs M1M ──────────────────────────────────────────────────────────
def test_m1_vs_m1m_table_and_slowdown_range(doc):
    _skip_without_data()
    current = _current()
    if not {"RPi5B_M1", "RPi5B_M1M"} <= set(current):
        pytest.skip("§2.2 needs both RPi5B_M1 and RPi5B_M1M runs")
    slowdowns = {}
    for size, cells in _table_rows(doc, "### 2.2", {"m", "l", "x"}).items():
        m1 = _model_row("RPi5B_M1", current["RPi5B_M1"], "object_detection", size,
                        False, "throughput")
        m1m = _model_row("RPi5B_M1M", current["RPi5B_M1M"], "object_detection", size,
                         False, "throughput")
        assert _num(cells[1]) == pytest.approx(round(m1["fps"], 1), abs=0.05)
        assert _num(cells[2]) == pytest.approx(round(m1m["fps"], 1), abs=0.05)
        assert _num(cells[3]) == pytest.approx(round(m1m["fps"] / m1["fps"], 2), abs=0.005)
        slowdowns[size] = (1 - m1m["fps"] / m1["fps"]) * 100
    assert slowdowns, "§2.2 table not found"
    text = Path(doc).read_text(encoding="utf-8")
    low, high = _half_up(min(slowdowns.values())), _half_up(max(slowdowns.values()))
    assert f"{low:.0f}–{high:.0f}%" in text, "§2.2 slowdown range prose"
    for size, value in slowdowns.items():
        assert f"{size} −{_half_up(value):.0f}%" in text, f"§2.2 per-size slowdown ({size})"


# ── §2.3 Thermal ────────────────────────────────────────────────────────────
def test_throttle_counts_and_max_temperature(doc):
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "### 2.3", set(current))
    assert rows, "§2.3 throttle table not found"
    for env, cells in rows.items():
        run = current[env]
        for index, filename in enumerate(FAMILY_FILES, start=1):
            data = _rows(env, run, filename)
            throttled, total = (_num(x) for x in cells[index].split("/"))
            assert throttled == sum(1 for r in data if r.get("npu_throttled")), \
                f"{env} {filename} throttled count"
            assert total == len(data), f"{env} {filename} cell count"
        temps = [(r.get("npu_temp_max_c") or 0) for f in FAMILY_FILES
                 for r in _rows(env, run, f)]
        assert _num(cells[4]) == pytest.approx(max(temps), abs=0.05), f"{env} max temp"


def test_thermal_prose_statistics(doc):
    """§2.3 prose: spread medians, cell counts and clock-floor ranges."""
    _skip_without_data()
    current = _current()
    steady, throttled = [], []
    floors, model_floors = [], []
    for env, run in current.items():
        for row in _rows(env, run, "model_results.json"):
            if row.get("family") != "throughput" or not row.get("fps"):
                continue
            if row.get("fps_std") is not None:
                spread = row["fps_std"] / row["fps"] * 100
                (throttled if row.get("npu_throttled") else steady).append(spread)
            if row.get("npu_throttled") and row.get("npu_clock_mhz_min"):
                model_floors.append(row["npu_clock_mhz_min"])
        for filename in FAMILY_FILES:
            floors += [r["npu_clock_mhz_min"] for r in _rows(env, run, filename)
                       if r.get("npu_throttled") and r.get("npu_clock_mhz_min")]
    steady.sort()
    text = Path(doc).read_text(encoding="utf-8")
    p90 = steady[int(len(steady) * 0.9)]
    for expected in (
        str(len(steady)),
        str(len(throttled)),
        f"{statistics.median(steady):.2f}%",
        f"{p90:.2f}%",
        f"{statistics.median(throttled):.2f}%",
        f"{max(throttled):.1f}%",
        f"{min(floors):.0f}–{max(floors):.0f} MHz",
        f"{min(model_floors):.0f}–{max(model_floors):.0f} MHz",
    ):
        assert expected in text, f"§2.3 prose value missing: {expected}"


# ── §5 Model throughput ─────────────────────────────────────────────────────
def test_throughput_table(doc):
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "## 5.", set(current))
    assert rows, "§5 throughput table not found"
    for env, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            row = _model_row(env, current[env], "object_detection", size, False,
                             "throughput")
            assert _num(cells[index]) == pytest.approx(round(row["fps"], 1), abs=0.05), \
                f"{env} {size}"


def test_cross_host_spread_uses_population_stdev(doc):
    """§5.1: mean and coefficient of variation over the four single-M1 hosts."""
    _skip_without_data()
    current = _current()
    if not set(M1_HOSTS) <= set(current):
        pytest.skip("§5.1 needs all four single-M1 hosts")
    rows = _table_rows(doc, "### 5.1", set(SIZES))
    assert rows, "§5.1 spread table not found"
    for size, cells in rows.items():
        values = [_model_row(h, current[h], "object_detection", size, False,
                             "throughput")["fps"] for h in M1_HOSTS]
        for index, host in enumerate(M1_HOSTS):
            assert _num(cells[index + 1]) == pytest.approx(round(values[index], 1),
                                                           abs=0.05), f"{size} {host}"
        assert _num(cells[5]) == pytest.approx(round(statistics.mean(values), 1),
                                               abs=0.05), f"{size} mean"
        cv = statistics.pstdev(values) / statistics.mean(values) * 100
        assert _num(cells[6]) == pytest.approx(_half_up(cv, 1), abs=0.05), \
            f"{size} coefficient of variation (population stdev)"


def test_h1_quattro_scaling_ratio(doc):
    _skip_without_data()
    current = _current()
    if "BIOSTAR_H1-Quattro" not in current or not set(M1_HOSTS) <= set(current):
        pytest.skip("§5.2 needs the H1-Quattro run and all four single-M1 hosts")
    rows = _table_rows(doc, "### 5.2", {"m", "l", "x"})
    assert rows, "§5.2 scaling table not found"
    for size, cells in rows.items():
        h1 = _model_row("BIOSTAR_H1-Quattro", current["BIOSTAR_H1-Quattro"],
                        "object_detection", size, False, "throughput")["fps"]
        mean = _m1_mean(size)
        assert _num(cells[1]) == pytest.approx(round(h1, 1), abs=0.05), f"{size} H1"
        assert _num(cells[2]) == pytest.approx(round(mean, 1), abs=0.05), f"{size} M1 mean"
        assert _num(cells[3]) == pytest.approx(round(h1 / mean, 2), abs=0.005), \
            f"{size} ratio"


def test_task_difficulty_table(doc):
    _skip_without_data()
    current = _current()
    if not set(TASK_ORDER_ENVS) <= set(current):
        pytest.skip("§5.3 needs both reference environments")
    labels = {"Classification": "classification", "Object detection": "object_detection",
              "Pose estimation": "pose_estimation", "Segmentation": "segmentation",
              "Oriented bounding box": "oriented_bbox"}
    rows = _table_rows(doc, "### 5.3", set(labels))
    assert rows, "§5.3 task table not found"
    for label, cells in rows.items():
        task = labels[label]
        for index, env in enumerate(TASK_ORDER_ENVS, start=2):
            row = _model_row(env, current[env], task, "m", False, "throughput")
            # fps values are quoted as the tool renders them (Python round())
            assert _num(cells[index]) == pytest.approx(round(row["fps"], 1), abs=0.05), \
                f"{label} {env}"


# ── §6 Latency ──────────────────────────────────────────────────────────────
def test_latency_table_and_cpu_offload_prose(doc):
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "## 6.", set(current))
    assert rows, "§6 latency table not found"
    for env, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            row = _model_row(env, current[env], "object_detection", size, False, "latency")
            assert _num(cells[index]) == pytest.approx(round(row["total_ms"], 2),
                                                       abs=0.005), f"{env} {size}"
    text = Path(doc).read_text(encoding="utf-8")
    x86 = [e for e in current if _environment(e, current[e]).get("host", {})
           .get("arch") == "x86_64"]
    arm = [e for e in current if e not in x86]
    for group in (x86, arm):
        values = [_model_row(e, current[e], "object_detection", s, True,
                             "latency")["cpu_0_ms"]
                  for e in group for s in ("n", "m", "x")]
        values = [v for v in values if v is not None]
        if not values:
            continue
        span = f"{_half_up(min(values), 2):.2f}–{_half_up(max(values), 2):.2f} ms"
        loose = f"{_half_up(min(values), 1):.1f}–{_half_up(max(values), 1):.1f} ms"
        assert span in text or loose in text, f"§6 cpu_0_ms range missing ({span})"


# ── §7 End-to-end ───────────────────────────────────────────────────────────
def test_e2e_table_uses_the_declared_ort_mode(doc):
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "## 7.", set(current))
    assert rows, "§7 E2E table not found"
    for env, cells in rows.items():
        run = current[env]
        declared_on = cells[1].strip() == "ON"
        best = _e2e_best(env, run, "object_detection", "n")
        assert declared_on is bool(best["use_ort"]), f"{env}: declared ORT mode"
        for index, size in enumerate(SIZES, start=2):
            row = _e2e_row(env, run, "object_detection", size, declared_on)
            assert _num(cells[index]) == pytest.approx(round(row["avg_e2e_fps"], 1),
                                                       abs=0.05), f"{env} {size}"


def test_e2e_to_throughput_ratio_table(doc):
    """§7.1: `E2E ÷ throughput` and NPU utilisation, same ORT mode on both sides."""
    _skip_without_data()
    current = _current()
    if not set(E2E_RATIO_ENVS) <= set(current):
        pytest.skip("§7.1 needs the three sampled environments")
    rows = _table_rows(doc, "### 7.1", set(SIZES))
    assert rows, "§7.1 ratio table not found"
    for size, cells in rows.items():
        for index, env in enumerate(E2E_RATIO_ENVS, start=1):
            run = current[env]
            best = _e2e_best(env, run, "object_detection", size)
            throughput = _model_row(env, run, "object_detection", size,
                                    bool(best["use_ort"]), "throughput")
            ratio, util = _nums(cells[index])
            assert ratio == pytest.approx(
                _half_up(best["avg_e2e_fps"] / throughput["fps"] * 100), abs=0.5), \
                f"{env} {size} ratio"
            assert util == pytest.approx(_half_up(best["npu_total_avg_pct"]), abs=0.5), \
                f"{env} {size} NPU utilisation"


def test_ort_matrix_winner_and_gain_range(doc):
    """§7.2: winner, the nano/small gain range, and the ±5% tie rule."""
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "### 7.2", set(current))
    assert rows, "§7.2 matrix not found"
    for env, cells in rows.items():
        run = current[env]
        for index, task in enumerate(TASKS, start=1):
            gains = _ort_gains(env, run, task)
            if not gains:
                continue
            cell = cells[index].replace("**", "")
            is_tie = all(abs(g) <= TIE_PCT for g in gains.values())
            expected = ("tie" if is_tie
                        else ("ON" if statistics.mean(list(gains.values())) > 0 else "OFF"))
            printed = ("tie" if ("tie" in cell or "동등" in cell)
                       else ("ON" if cell.startswith("ON") else "OFF"))
            assert printed == expected, (
                f"{env} {task}: document says '{cell.strip()}' but recomputed "
                f"{expected} from {({k: round(v, 1) for k, v in gains.items()})}")
            if expected == "tie":
                continue
            magnitudes = sorted(abs(g) for g in gains.values())
            printed_range = _nums(cell)
            assert printed_range, f"{env} {task}: no gain range printed"
            assert printed_range[0] == pytest.approx(magnitudes[0], abs=0.05), \
                f"{env} {task}: range low end"
            assert printed_range[-1] == pytest.approx(magnitudes[-1], abs=0.05), \
                f"{env} {task}: range high end"


def test_free_accuracy_size_column(doc):
    """§7.3: largest size still within 5% of the nano end-to-end figure."""
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "### 7.3", set(current))
    assert rows, "§7.3 table not found"
    for env, cells in rows.items():
        run = current[env]
        values = {s: _e2e_best(env, run, "object_detection", s)["avg_e2e_fps"]
                  for s in SIZES}
        largest = [s for s in SIZES if values[s] >= values["n"] * 0.95][-1]
        assert cells[1].replace("**", "").strip() == largest, (
            f"{env}: document says {cells[1]!r}, recomputed {largest} from "
            f"{({k: round(v, 1) for k, v in values.items()})}")


# ── §8 Capacity ─────────────────────────────────────────────────────────────
def test_channel_capacity_table(doc):
    _skip_without_data()
    current = _current()
    rows = _table_rows(doc, "## 8.", set(current))
    assert rows, "§8 capacity table not found"
    for env, cells in rows.items():
        for index, size in enumerate(SIZES, start=1):
            assert _num(cells[index]) == _capacity(env, current[env], "object_detection",
                                                   size), f"{env} {size}"


# ── §9 Version trend ────────────────────────────────────────────────────────
def test_version_trend_table_and_change_percentages(doc):
    _skip_without_data()
    current, baseline = _current(), _baseline()
    seen = 0
    for line in _section(doc, "## 9."):
        if not line.startswith("|") or set(line) <= set("|-: "):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        env = cells[0].replace("**", "")
        if env not in current or env not in baseline or cells[1] not in SIZES:
            continue
        size = cells[1]
        old = _model_row(env, baseline[env], "object_detection", size, False, "throughput")
        new = _model_row(env, current[env], "object_detection", size, False, "throughput")
        assert _num(cells[2]) == pytest.approx(round(old["fps"], 1), abs=0.05), \
            f"{env} {size} baseline fps"
        assert _num(cells[3]) == pytest.approx(round(new["fps"], 1), abs=0.05), \
            f"{env} {size} current fps"
        change = (new["fps"] / old["fps"] - 1) * 100
        assert _num(cells[4]) == pytest.approx(_half_up(change, 1), abs=0.05), \
            f"{env} {size} change %"
        seen += 1
    assert seen >= 3, "§9 trend table not found"


def test_version_trend_prose_distribution(doc):
    """§9 prose: the median / in-band count / extremes must match the full matrix."""
    _skip_without_data()
    current, baseline = _current(), _baseline()
    heavy, light = [], []
    for env in current:
        if env not in baseline:
            continue
        for size in SIZES:
            old = _model_row(env, baseline[env], "object_detection", size, False,
                             "throughput")
            new = _model_row(env, current[env], "object_detection", size, False,
                             "throughput")
            if not (old and new and old.get("fps") and new.get("fps")):
                continue
            change = (new["fps"] / old["fps"] - 1) * 100
            (heavy if size in ("m", "l", "x") else light).append(change)
    text = Path(doc).read_text(encoding="utf-8")
    for expected in (
        f"{_half_up(statistics.median(heavy), 1):.1f}%",
        str(len(heavy)),
        str(sum(1 for c in heavy if 25 <= c <= 35)),
        f"{_half_up(max(heavy), 1):.1f}%",
        f"{_half_up(max(light), 1):.1f}%",
    ):
        assert expected in text, f"§9 prose value missing: {expected}"
