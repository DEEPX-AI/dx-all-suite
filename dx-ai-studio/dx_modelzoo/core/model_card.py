"""One model card per dx_app example: the Studio catalog entry joined with dx_app's registry, the example's own
files and the benchmark runs. Plain data; model_card_md and model_card_html render it.

Contract: tests/dx_modelzoo/test_model_card.py
"""
from __future__ import annotations

import datetime as _dt
import json
import posixpath
import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

TIERS = (("raw", "Raw · ONNX"), ("qlite", "Q-Lite"), ("qpro", "Q-Pro"), ("qmaster", "Q-Master"))
LOSS_WARN_POINTS = 5.0
BOARD_NAMES = {
    "BIOSTAR_H1-Quattro": "DX-H1 Quattro · BIOSTAR",
    "DX-AIPlayer-N97_M1": "DX-M1 · AIPlayer N97",
    "OrangePi5+_M1": "DX-M1 · Orange Pi 5+",
    "ROCK5B+_M1": "DX-M1 · ROCK 5B+",
    "RPi5B_M1": "DX-M1 · Raspberry Pi 5",
    "RPi5B_M1M": "DX-M1M · Raspberry Pi 5",
}
FILE_ROLES = (
    ("_sync.py", "Python · one image, video or camera"),
    ("_async.py", "Python · pipelined, higher throughput"),
    ("_sync_cpp_postprocess.py", "Python with the C++ postprocess binding"),
    ("_async_cpp_postprocess.py", "Python async with the C++ postprocess binding"),
    ("_sync.cpp", "C++ · one image, video or camera"),
    ("_async.cpp", "C++ · pipelined, higher throughput"),
    ("config.json", "Thresholds, input size, default sample"),
    ("factory", "Pre-, post-processor and visualizer"),
)
_VERSION_DIR = re.compile(r"/(\d+)_(\d+)_(\d+)/")
# "a" before a vowel sound; a vowel letter that sounds like "y" or "w" (unified, user, European, one-stage) keeps "a".
_ARTICLE = re.compile(r"\b(a) (?=[aeiou])(?!uni|use|usu|usa|uti|ura|ure|uro|u-|eu|ewe|one\b|once|ufo|ubiq)",
                      re.IGNORECASE)
# "AP(Easy)AP(Med)AP(Hard)": one catalog name for several values, glued at ")".
_GLUED_METRICS = re.compile(r"(?<=\))(?=\S)")
# Studio's stand-in summaries, the same sentence for every model of a task (generate_catalog.py and
# metadata/merge.py): a card says nothing with them, so it uses its own fallback sentence instead.
_TEMPLATE_SUMMARIES = (re.compile(r".+ is an? [a-z0-9 ]+ model optimized for DEEPX NPU\."),
                       re.compile(r"AI model( for [a-z0-9_]+ tasks)?\."))
# A task key left in a sentence ("anomaly_detection"): letters only, so model ids such as yolov5s_ppu stay.
_TASK_KEY = re.compile(r"\b[a-z]+(?:_[a-z]+)+\b")


# ── formatting ──────────────────────────────────────────────────────────────

def fmt_num(value, digits=2):
    return "—" if value is None else f"{value:,.{digits}f}"


def fmt_fps(value):
    if value is None:
        return "—"
    return f"{value:,.0f}" if abs(value - round(value)) < 0.05 else f"{value:,.1f}"


def fmt_delta(delta):
    if round(delta, 2) == 0:
        return "±0.00"
    return f"−{-delta:.2f}" if delta < 0 else f"+{delta:.2f}"


def fmt_input(resolution):
    return " × ".join(str(resolution).split("x")) if resolution else ""


def _number(text):
    try:
        return float(str(text).replace(",", ""))
    except (TypeError, ValueError):
        return None


def public_url(url):
    """A link a dx_app reader can open: http(s) and not an internal *.dpx.ai host."""
    if not isinstance(url, str):
        return None
    parsed = urlparse(url.strip())
    host = parsed.hostname or ""
    if parsed.scheme not in ("http", "https") or not host or host == "dpx.ai" or host.endswith(".dpx.ai"):
        return None
    return url.strip()


def rel_dir(from_dir, to_dir):
    """Relative link from one dx_app dir to another, with a trailing slash."""
    return posixpath.relpath(to_dir, from_dir) + "/"


def split_values(value):
    if value in (None, "", "-", "—"):
        return []
    return [part.strip() for part in str(value).split("/") if part.strip()]


# ── pieces ──────────────────────────────────────────────────────────────────

def load_registry(dx_app_root):
    rows = json.loads((Path(dx_app_root) / "config" / "model_registry.json").read_text(encoding="utf-8"))
    return {PurePosixPath(r["dxnn_file"]).stem: r for r in rows if not r.get("alias_of")}


def _manifest_rows(dx_app_root):
    try:
        rows = json.loads((Path(dx_app_root) / "scripts" / "modelzoo_manifest.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return [r for r in rows if isinstance(r, dict) and isinstance(r.get("name"), str)] if isinstance(rows, list) else []


def load_setup_names(dx_app_root):
    """setup_sample_models.sh --models matches the manifest's name, case-insensitively. Returns (lower-cased names,
    dxnn file name -> manifest name)."""
    rows = _manifest_rows(dx_app_root)
    by_file = {PurePosixPath(urlparse(r["dxnn_url"]).path).name: r["name"]
               for r in rows if isinstance(r.get("dxnn_url"), str)}
    return {r["name"].lower() for r in rows}, by_file


def load_manifest_urls(dx_app_root):
    """Lower-cased dxnn file name -> the manifest's dxnn_url: what setup_sample_models.sh downloads."""
    return {PurePosixPath(urlparse(r["dxnn_url"]).path).name.lower(): r["dxnn_url"]
            for r in _manifest_rows(dx_app_root) if isinstance(r.get("dxnn_url"), str)}


def manifest_url_for(manifest_urls, registry_row):
    return manifest_urls.get(PurePosixPath(registry_row["dxnn_file"]).name.lower())


def catalog_date(generated_at, tz=None):
    """The catalog's generated_at (UTC ISO) as a local YYYY-MM-DD, or None. tz: the zone (default: this host's)."""
    text = str(generated_at or "")
    if not text:
        return None
    try:
        when = _dt.datetime.fromisoformat(text)
    except ValueError:
        return text[:10]
    if when.tzinfo is None:
        return when.date().isoformat()
    return when.astimezone(tz).date().isoformat()


def load_dead_links(dx_app_root):
    """The download URLs the last --verify-links export found dead (config/model_cards.json), or None without an
    index."""
    try:
        index = json.loads((Path(dx_app_root) / "config" / "model_cards.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    links = index.get("dead_links") if isinstance(index, dict) else None
    return {u for u in links if isinstance(u, str)} if isinstance(links, list) else set()


def drop_dead_links(cards, url_ok, threads=8):
    """Take the dead download links off the cards. url_ok: callable url -> (alive, status), asked once per URL. A tier
    whose dxnn is dead goes; a dead json, onnx or manifest download becomes None. Returns (["variant: url (status)",
    ...], sorted dead URLs)."""
    from concurrent.futures import ThreadPoolExecutor

    urls = sorted({u for card in cards for u in _card_urls(card)})
    with ThreadPoolExecutor(max_workers=threads) as pool:
        result = dict(zip(urls, pool.map(url_ok, urls)))
    lines = []
    for card in cards:
        def alive(url, variant=card["variant"]):
            if not url:
                return url
            ok, status = result[url]
            if not ok:
                lines.append(f"{variant}: {url} ({status})")
            return url if ok else None

        links = card["downloads"]
        links["onnx"] = alive(links.get("onnx"))
        if links.get("manifest") and not alive(links["manifest"]["dxnn"]):
            links["manifest"] = None
        tiers = []
        for tier in links["tiers"]:
            if alive(tier["dxnn"]):
                tiers.append(dict(tier, json=alive(tier.get("json"))))
            elif tier.get("json"):
                alive(tier["json"])
        links["tiers"] = tiers
    return lines, sorted(u for u, (ok, _status) in result.items() if not ok)


def known_dead(dead):
    """url_ok for drop_dead_links from a stored set of dead URLs (no network)."""
    return lambda url: (url not in dead, "dead at the last --verify-links")


def _card_urls(card):
    links = card["downloads"]
    urls = [links.get("onnx"), (links.get("manifest") or {}).get("dxnn")]
    for tier in links["tiers"]:
        urls += [tier["dxnn"], tier.get("json")]
    return [u for u in urls if u]


def load_benchmark(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    return ((data.get("summaries") or {}).get("model")) or []


def accuracy_table(model):
    spec = model.get("specification") or {}
    metric = spec.get("metric")
    metric = metric.get("name") if isinstance(metric, dict) else metric
    names = split_values(metric)
    evaluation = model.get("evaluation") or {}
    tiers = {key: [_number(v) for v in split_values((evaluation.get(key) or {}).get("accuracy"))] for key, _ in TIERS}
    count = max((len(v) for v in tiers.values() if any(x is not None for x in v)), default=0)
    metrics = names or ["Accuracy"]
    if len(metrics) == 1 and count > 1:
        parts = [p.strip() for p in _GLUED_METRICS.split(metrics[0]) if p.strip()]
        metrics = parts if len(parts) <= count else metrics
    metrics += [f"Metric {i}" for i in range(len(metrics) + 1, count + 1)]
    raw = tiers["raw"]
    rows, warnings = [], []
    for key, label in TIERS:
        values = tiers[key]
        if not any(v is not None for v in values):
            continue
        values = (values + [None] * len(metrics))[:len(metrics)]
        cells = []
        for i, value in enumerate(values):
            base = raw[i] if key != "raw" and i < len(raw) else None
            # From the shown (2-decimal) values, so the delta matches the numbers next to it.
            delta = None
            if value is not None and base is not None:
                delta = round(round(value, 2) - round(base, 2), 2) + 0.0
            cells.append({"value": value, "delta": delta})
            if delta is not None and -delta > LOSS_WARN_POINTS:
                warnings.append({"tier": label, "metric": metrics[i], "drop": round(-delta, 2)})
        rows.append({"tier": key, "label": label, "cells": cells})
    mismatch = count > 0 and len(names) != count and (bool(names) or count > 1)
    return {"metrics": metrics, "rows": rows, "warnings": warnings, "metric_count_mismatch": mismatch,
            "metric_counts": {"names": len(names), "values": count}}


def compiler_version(url):
    match = _VERSION_DIR.search(url or "")
    return ".".join(match.groups()) if match else None


def downloads(model):
    artifacts = model.get("artifacts") or {}

    def url(key):
        item = artifacts.get(key)
        return public_url(item.get("remote_url") if isinstance(item, dict) else item)

    tiers = []
    for key, label in TIERS[1:]:
        dxnn = url(f"{key}_dxnn")
        if dxnn:
            tiers.append({"tier": key, "label": label, "compiler": compiler_version(dxnn),
                          "dxnn": dxnn, "json": url(f"{key}_json")})
    return {"onnx": url("onnx"), "tiers": tiers}


def _template_summary(text):
    from dx_modelzoo.metadata.merge import _EDITORIAL_BY_TASK
    return text in _EDITORIAL_BY_TASK.values() or any(p.fullmatch(text) for p in _TEMPLATE_SUMMARIES)


def summary(model, lang="en"):
    """The catalog's summary for the card, or "" when it is one of Studio's per-task stand-ins."""
    text = ((model.get("display") or {}).get("summary")) or model.get("description") or ""
    english = text.get("en") if isinstance(text, dict) else text
    if _template_summary(str(english or "").strip()):
        return ""
    if isinstance(text, dict):
        text = text.get(lang) or text.get("en") or ""
    text = str(text).strip()
    if lang != "en":
        return text
    text = _TASK_KEY.sub(lambda m: m.group(0).replace("_", " "), text)
    return _ARTICLE.sub(lambda m: m.group(1) + "n ", text)


def board_rows(benchmark_rows, variant):
    want = f"{variant}.dxnn"
    newest = {}
    for row in benchmark_rows:
        if row.get("model") != want or row.get("use_ort") is not False or row.get("status") not in (None, "ok"):
            continue
        key = (row.get("env_id"), row.get("family"))
        if key not in newest or str(row.get("run_id")) > str(newest[key].get("run_id")):
            newest[key] = row
    rows, run_ids = [], []
    for env_id, board in BOARD_NAMES.items():
        thr, lat = newest.get((env_id, "throughput")), newest.get((env_id, "latency"))
        if not thr or not lat or thr.get("fps") is None or lat.get("fps") is None:
            continue
        latency = lat.get("latency_ms")
        rows.append({"board": board, "throughput_fps": round(thr["fps"], 1), "single_fps": round(lat["fps"], 1),
                     "latency_ms": round(latency, 1) if latency is not None else None})
        run_ids += [str(thr.get("run_id") or ""), str(lat.get("run_id") or "")]
    measured = None
    stamps = [r[:8] for r in run_ids if r[:8].isdigit()]
    if stamps:
        try:
            measured = _dt.datetime.strptime(max(stamps), "%Y%m%d").strftime("%B %Y")
        except ValueError:
            measured = None
    return {"rows": rows, "measured": measured}


def example_files(example_dir, variant):
    folder = Path(example_dir)
    if not folder.is_dir():
        return []
    present = {p.name: p for p in folder.iterdir()}
    out = []
    for suffix, role in FILE_ROLES:
        name = suffix if suffix in ("config.json", "factory") else variant + suffix
        if name in present:
            out.append({"name": name + ("/" if present[name].is_dir() else ""), "role": role})
    return out


def commands(card):
    variant, sample = card["variant"], card["sample"]
    script = f"{card['paths']['python']}/{variant}_sync.py"
    model = f"assets/models/{variant}.dxnn"
    py_in = f" \\\n  --image {sample}" if sample else ""
    cpp_in = f" \\\n  -i {sample}" if sample else ""
    return {
        # setup_sample_models.sh fetches only the model; setup.sh would also re-download the sample videos.
        "get": f"# from the dx_app root\n./setup_sample_models.sh --models {card['setup_name']}",
        "python": f"python {script} \\\n  --model {model}{py_in}",
        "cpp": f"./build.sh --target {variant}_sync   # once\n./bin/{variant}_sync \\\n  -m {model}{cpp_in}",
        "measure": f"python {script} \\\n  --model {model}{py_in} \\\n  --loop 100 --no-display",
    }


# ── the card ────────────────────────────────────────────────────────────────

def build_card(model, registry_row, dx_app_root, *, asof, benchmark_rows=(), task_label=None, lang="en",
               setup_name=None, manifest_url=None):
    """asof: the publish table's date, or None when it is unknown (the footer then leaves the date out).
    setup_name: the name dx_app's setup_sample_models.sh --models knows (its manifest); defaults to the registry name.
    manifest_url: the manifest's dxnn_url (manifest_url_for); listed only on a card the publish table has no files
    for, so its Downloads match what the quick start fetches."""
    variant = PurePosixPath(registry_row["dxnn_file"]).stem
    task, family = registry_row["task"], registry_row["family"]
    py_dir = f"src/python_example/{task}/{family}/{variant}"
    cpp_dir = f"src/cpp_example/{task}/{family}/{variant}"
    root = Path(dx_app_root)
    try:
        config = json.loads((root / py_dir / "config.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        config = {}
    spec = model.get("specification") or {}
    legal = model.get("legal") or {}
    perf = model.get("performance") or {}
    task_label = task_label or task.replace("_", " ").title()
    dataset = spec.get("dataset")
    links = downloads(model)
    published = bool(links["tiers"] or links["onnx"])
    fallback = None if published else public_url(manifest_url)
    links["manifest"] = {"dxnn": fallback, "compiler": compiler_version(fallback)} if fallback else None
    if published:
        name = (model.get("display") or {}).get("name") or model.get("name") or variant
        text = summary(model, lang)
    else:
        # Not in the publish table: Studio's display name and summary are made up from the file name.
        name, text = registry_row.get("original_name") or variant, ""
    # An empty summary leaves the lede to model_card_labels.lede, which the page can translate.
    return {
        "variant": variant,
        "zoo_id": model.get("id"),
        "zoo_name": registry_row.get("model_name") or variant,
        "setup_name": setup_name or registry_row.get("model_name") or variant,
        "zoo_task": (model.get("display") or {}).get("publish_task") or (model.get("display") or {}).get("task"),
        "family": family,
        "task": task,
        "task_label": task_label,
        "name": name,
        "summary": text,
        "published": published,
        "input": spec.get("input_resolution"),
        "dataset": dataset,
        "params": _number(spec.get("parameters")),
        "ops": _number(spec.get("operations")),
        "accuracy": accuracy_table(model),
        "fps": _number(perf.get("fps")),
        "fps_per_watt": _number(perf.get("fps_per_watt")),
        "boards": board_rows(benchmark_rows, variant),
        "downloads": links,
        "license": legal.get("license"),
        "license_text": legal.get("license_text"),
        "copyright": legal.get("copyright"),
        "source": public_url(legal.get("source_url")),
        "sample": config.get("default_image") or config.get("default_video") or "",
        "paths": {"python": py_dir, "cpp": cpp_dir},
        "files": {"python": example_files(root / py_dir, variant), "cpp": example_files(root / cpp_dir, variant)},
        "has_cpp": (root / cpp_dir).is_dir(),
        "has_image": False,
        "asof": asof,
    }
