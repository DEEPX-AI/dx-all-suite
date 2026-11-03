"""DX-APP ModelZoo — browse, cart, download from DEEPX ModelZoo page."""

from shared import dxrt as _dxrt
import os, sys, json, time, threading, re, ssl
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from dx_app.core import config
from dx_app.core.config import DX_APP_ROOT, ASSETS_DIR, SCRIPTS_DIR, CONFIG_FILE, MODELS_DIR as _CFG_MODELS_DIR
from dx_app.core._html_dom import parse_html
from shared.catalog_sources import parse_test_models_conf as _shared_parse_test_models_conf
from shared.atomic_download import DownloadCancelled, asset_file_status, download_file

DEVELOPER_PORTAL = "https://developer.deepx.ai"
SDK_BASE = "https://sdk.deepx.ai"

SOURCE_PUBLIC = "public"
SOURCE_INTERNAL = "internal"
SOURCE_URLS = {
    # Public ModelZoo page (developer portal). /article/modelzoo/ 404s; /modelzoo/ is live.
    SOURCE_PUBLIC: f"{DEVELOPER_PORTAL}/modelzoo/",
    # Internal/devops publish page — air-gapped network + internal CA only.
    SOURCE_INTERNAL: "https://modelzoo-publish-api.devops.dpx.ai/publish/html",
}

# Use the configurable model directory (config.MODELS_DIR) rather than rebuilding
# ASSETS_DIR/'models' here, which would ignore the setting.
MODELS_DIR = _CFG_MODELS_DIR
QPRO_DIR = MODELS_DIR / "q-pro"
QMASTER_DIR = MODELS_DIR / "q-master"

# Tier -> (install directory, relative path written to the registry).
#
# A table rather than `chip == "qlite" and MODELS_DIR or QPRO_DIR`-style branches: those
# assume only two tiers and make the else side a default, so a mistyped chip would
# silently go to q-pro. With a table a new tier is a one-place change, and an unknown
# chip surfaces as a KeyError.
_CHIP_DIRS = {
    "qlite": (MODELS_DIR, "assets/models"),
    "qpro": (QPRO_DIR, "assets/models/q-pro"),
    "qmaster": (QMASTER_DIR, "assets/models/q-master"),
}

_dl_lock = threading.Lock()
_dl_state = {
    "running": False,
    "total": 0,
    "done": 0,
    "current": "",
    "results": [],   # [{file, status, size, error}]
    "finished": False,
    "cancel": False,
}


def _installed_status(directory, dxnn_url, json_url=None):
    """A tier is downloaded when all its files are present. Without a Studio completion record
    it is ``unverified`` (still downloaded — never shown as "not downloaded"); downloading it
    again verifies it by Content-Length and keeps a size-matching file in place."""
    urls = [url for url in (dxnn_url, json_url) if url]
    checks = [asset_file_status(directory / Path(urlparse(url).path).name) for url in urls]
    present = bool(checks) and all(check["state"] != "missing" for check in checks)
    verified = bool(checks) and all(check["ok"] for check in checks)
    state = "verified" if verified else ("unverified" if present else "missing")
    return {"exists": present, "install_state": state,
            "install_detail": "; ".join(check["detail"] for check in checks)}


def _reset_dl_state():
    _dl_state.update({
        "running": False, "total": 0, "done": 0, "current": "",
        "results": [], "finished": False, "cancel": False,
    })


def _make_opener(source):
    """urllib opener (stdlib). The internal devops host uses an internal CA, so TLS
    verification is disabled for it only — matching the old requests verify=False."""
    if source == SOURCE_INTERNAL:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return urllib.request.build_opener(urllib.request.HTTPSHandler(context=ctx))
    return urllib.request.build_opener()


def _open(opener, url, timeout):
    req = urllib.request.Request(url, headers={
        "User-Agent": "DX-APP-ModelZoo/2.0", "Accept-Encoding": "identity"})
    return opener.open(req, timeout=timeout)


def _fetch_page(source):
    return _fetch_url(source, SOURCE_URLS.get(source, SOURCE_URLS[SOURCE_INTERNAL]))


def _fetch_url(source, url):
    try:
        opener = _make_opener(source)
        # Bounded timeout: ModelZoo browses a REMOTE catalog (both sources are network hosts),
        # so on an air-gapped/offline box this request fails — cap it at 6s so the ModelZoo tab
        # surfaces a quick "failed to load" toast instead of hanging up to 30s on a dropped SYN.
        with _open(opener, url, 6) as resp:
            if resp.status != 200:
                return None, f"HTTP {resp.status}"
            return resp.read().decode("utf-8", "replace"), None
    except Exception as e:
        return None, str(e)


def _abs(href):
    return (DEVELOPER_PORTAL + href) if href.startswith("/") else href


def _leaf_labels(header_rows):
    """Leaf column labels of a (rowspan/colspan) header block: 'NPU Performance USE_ORT FPS' style."""
    occupied = {}
    for r, tr in enumerate(header_rows):
        c = 0
        for cell in tr.find_all(["th", "td"]):
            while (r, c) in occupied:
                c += 1
            text = cell.get_text(strip=True)
            rs, cs = int(cell.get("rowspan", 1) or 1), int(cell.get("colspan", 1) or 1)
            for dr in range(rs):
                for dc in range(cs):
                    occupied[(r + dr, c + dc)] = text
            c += cs
    if not occupied:
        return []
    ncols = max(c for _, c in occupied) + 1
    leaves = []
    for c in range(ncols):
        parts = []
        for r in range(len(header_rows)):
            t = occupied.get((r, c))
            if t and (not parts or parts[-1] != t):
                parts.append(t)
        leaves.append(" ".join(parts))
    return leaves


def _col_finder(leaves):
    """Return col(*labels) -> index of the first leaf whose label is one of labels (None if absent)."""
    def col(*labels):
        for label in labels:
            if label in leaves:
                return leaves.index(label)
        return None
    return col


def _parse_models(html):
    """Parse ModelZoo HTML — extract models with Q-Lite and Q-Pro info.

    Internal page uses a 3-row header:
      Row 0: Task | Name | ClassName | Dataset | InputRes | Ops | Params | License | Metric | Source | Raw(colspan=2) | NPU(colspan=8)
      Row 1:                                                                                          | Q-Lite(3) | Q-Pro(3) | Perf(2)
      Row 2:                                                                                          | Acc|DXNN|JSON | Acc|DXNN|JSON | FPS|FPS/W

    Data row = 20 cells:
      [0]Task [1]Name [2]ClassName [3]Dataset [4]InputRes
      [5]Ops [6]Params [7]License [8]Metric [9]Source(link)
      [10]RawAccuracy [11]ONNX(link)
      [12]Q-Lite Accuracy [13]Q-Lite DXNN(link) [14]Q-Lite JSON(link)
      [15]Q-Pro Accuracy  [16]Q-Pro DXNN(link)  [17]Q-Pro JSON(link)
      [18]FPS [19]FPS/Watt
    """
    soup = parse_html(html)

    def _cell_text(cell):
        """Extract cell text preserving <br> as newlines."""
        parts = []
        for child in cell.children:
            if child.name is None:  # text node
                t = child.text.strip()
                if t:
                    parts.append(t)
            elif child.name == "br":
                parts.append("\n")
            else:
                t = child.get_text(strip=True)
                if t:
                    parts.append(t)
        return "\n".join(p for p in "\n".join(parts).split("\n") if p.strip()).strip()

    models = []
    seen = set()
    current_category = "Unknown"

    for elem in soup.find_all(["h1", "h2", "h3", "h4", "table"]):
        if elem.name in ("h1", "h2", "h3", "h4"):
            current_category = elem.get_text(strip=True)
            continue

        rows = elem.find_all("tr")
        # Detect if this is the internal 20-col format:
        # check if row 1 has a cell containing "Q-Lite" or "Q-Pro"
        is_20col = False
        if len(rows) >= 3:
            row1_texts = [c.get_text(strip=True) for c in rows[1].find_all(["th", "td"])]
            if any("Q-Lite" in t or "Q-Pro" in t for t in row1_texts):
                is_20col = True

        if is_20col:
            # Each field's column is found by its header label. The publish page adds Q-Master and USE_ORT
            # columns, so a fixed index drifts. Headers without those labels (the legacy and public layouts)
            # keep the historical fixed offsets, so their columns are read exactly as before.
            leaves = _leaf_labels(rows[:3])
            first_hdr = rows[0].find_all(["th", "td"])
            hdr0 = first_hdr[0].get_text(strip=True) if first_hdr else ""
            public_layout = hdr0.replace(" ", "").lower() == "classname"
            cat = re.sub(r"\s*\(\d+\)\s*$", "", current_category).strip() if public_layout else current_category
            col = _col_finder(leaves)
            labelled = col("NPU Q-Lite DXNN") is not None
            cstart = 0 if public_layout else 2
            if labelled:
                index = {
                    "name": col("Name"), "class": col("Class Name", "Display Name"), "task": col("Task"),
                    "dataset": col("Dataset"), "input_res": col("Input Resolution"), "ops": col("Operations"),
                    "params": col("Parameters"), "license": col("License"), "metric": col("Metric"),
                    "raw_acc": col("Raw Accuracy"), "onnx": col("Raw ONNX"),
                    "ql_acc": col("NPU Q-Lite Accuracy"), "ql_dxnn": col("NPU Q-Lite DXNN"), "ql_json": col("NPU Q-Lite JSON"),
                    "qp_acc": col("NPU Q-Pro Accuracy"), "qp_dxnn": col("NPU Q-Pro DXNN"), "qp_json": col("NPU Q-Pro JSON"),
                    "qm_acc": col("NPU Q-Master Accuracy"), "qm_dxnn": col("NPU Q-Master DXNN"), "qm_json": col("NPU Q-Master JSON"),
                    "fps": col("NPU Performance FPS", "Performance FPS", "FPS"),
                    "fps_w": col("NPU Performance FPS/Watt", "Performance FPS/Watt", "FPS/Watt"),
                    "ort_fps": col("NPU Performance USE_ORT FPS"), "ort_fps_w": col("NPU Performance USE_ORT FPS/Watt"),
                }
            else:
                index = {
                    "name": 1, "class": cstart, "task": 0, "dataset": cstart + 1, "input_res": cstart + 2,
                    "ops": cstart + 3, "params": cstart + 4, "license": cstart + 5, "metric": cstart + 6,
                    "raw_acc": cstart + 8, "onnx": cstart + 9,
                    "ql_acc": cstart + 10, "ql_dxnn": cstart + 11, "ql_json": cstart + 12,
                    "qp_acc": cstart + 13, "qp_dxnn": cstart + 14, "qp_json": cstart + 15,
                    "qm_acc": None, "qm_dxnn": None, "qm_json": None,
                    "fps": cstart + 16, "fps_w": cstart + 17, "ort_fps": None, "ort_fps_w": None,
                }

            # The helpers read `cells`, which each row rebinds, so they are defined once per table.
            cells = []

            def cell(key):
                idx = index.get(key)
                return cells[idx] if idx is not None and idx < len(cells) else None

            def text(key):
                c = cell(key)
                return c.get_text(strip=True) if c is not None else ""

            def acc(key):
                c = cell(key)
                return _cell_text(c) if c is not None else ""

            def link(key):
                c = cell(key)
                a = c.find("a", href=True) if c is not None else None
                return _abs(a["href"]) if a else None

            for row in rows[3:]:
                cells = row.find_all("td")

                if not labelled and len(cells) < cstart + 16:
                    continue
                class_name = text("class")
                if public_layout:
                    name = class_name
                    task = cat
                else:
                    task = text("task")
                    name = text("name")
                if not name or name == "-":
                    continue

                ql_dxnn, ql_json = link("ql_dxnn"), link("ql_json")
                qp_dxnn, qp_json = link("qp_dxnn"), link("qp_json")
                qm_dxnn, qm_json = link("qm_dxnn"), link("qm_json")
                uid = f"{task}|{name}"
                if uid in seen:
                    continue
                seen.add(uid)

                models.append({
                    "name": name,
                    "class_name": class_name,
                    "task": task or current_category,
                    "dataset": text("dataset"),
                    "input_resolution": text("input_res"),
                    "ops": text("ops"),
                    "params": text("params"),
                    "license": text("license"),
                    "metric": acc("metric"),
                    "raw_accuracy": acc("raw_acc"),
                    "onnx_url": link("onnx"),
                    "qlite": {
                        "accuracy": acc("ql_acc"),
                        "dxnn_url": ql_dxnn,
                        "json_url": ql_json,
                        "exists": _installed_status(MODELS_DIR, ql_dxnn, ql_json)["exists"],
                    },
                    "qpro": {
                        "accuracy": acc("qp_acc"),
                        "dxnn_url": qp_dxnn,
                        "json_url": qp_json,
                        "exists": _installed_status(QPRO_DIR, qp_dxnn, qp_json)["exists"],
                    },
                    "qmaster": {
                        "accuracy": acc("qm_acc"),
                        "dxnn_url": qm_dxnn,
                        "json_url": qm_json,
                        "exists": _installed_status(QMASTER_DIR, qm_dxnn, qm_json)["exists"],
                    },
                    "fps": text("fps"),
                    "fps_per_watt": text("fps_w"),
                    "use_ort_fps": text("ort_fps"),
                    "use_ort_fps_per_watt": text("ort_fps_w"),
                })
        else:
            # Fallback: legacy format (simple .dxnn scan)
            name_col = 0
            task_col = -1
            for row in rows:
                hdr = row.find_all("th")
                if not hdr:
                    continue
                texts = [c.get_text(strip=True).lower() for c in hdr]
                if "name" in texts:
                    name_col = texts.index("name")
                if "task" in texts:
                    task_col = texts.index("task")
                break

            for row in rows:
                cells = row.find_all(["td", "th"])
                if not cells or all(c.name == "th" for c in cells):
                    continue
                if len(cells) <= name_col:
                    continue
                mname = cells[name_col].get_text(strip=True)
                if not mname or mname == "-":
                    continue
                task = current_category
                if task_col >= 0 and len(cells) > task_col:
                    t = cells[task_col].get_text(strip=True)
                    if t and t != "-":
                        task = t
                dxnn_url = json_url = None
                for c in cells:
                    # _html_dom.Node.find_all takes only a tag name (not BeautifulSoup's
                    # href=True filter); passing that filter raises TypeError (a 500)
                    # once this branch runs. Contract: tests/dx_app/test_modelzoo_legacy_parse.py
                    for a in c.find_all("a"):
                        h = a.get("href")
                        if not h:
                            continue
                        if dxnn_url is None and ".dxnn" in h:
                            dxnn_url = _abs(h)
                        if json_url is None and ".json" in h:
                            json_url = _abs(h)
                if not dxnn_url:
                    continue
                uid = f"{task}|{mname}"
                if uid in seen:
                    continue
                seen.add(uid)
                models.append({
                    "name": mname, "class_name": "", "task": task,
                    "dataset": "", "input_resolution": "", "ops": "", "params": "",
                    "license": "", "metric": "", "raw_accuracy": "",
                    "onnx_url": None,
                    "qlite": {
                        "accuracy": "",
                        "dxnn_url": dxnn_url,
                        "json_url": json_url,
                        "exists": _installed_status(MODELS_DIR, dxnn_url, json_url)["exists"],
                    },
                    "qpro": {
                        "accuracy": "", "dxnn_url": None,
                        "json_url": None, "exists": False,
                    },
                    "fps": "", "fps_per_watt": "",
                })

    return models


_cache = {"models": None, "source": None, "ts": 0}
_cache_lock = threading.Lock()
_CACHE_TTL = 300  # 5 minutes


def _tier_block(row, tier):
    """Move the payload's accuracy/artifacts into the tier block dx_app uses."""
    artifacts = row.get("artifacts") or {}
    dxnn_url = artifacts.get(f"{tier}_dxnn")
    dest_dir = _CHIP_DIRS[tier][0]
    return {
        "accuracy": (row.get("accuracy") or {}).get(tier),
        "dxnn_url": dxnn_url,
        "json_url": artifacts.get(f"{tier}_json"),
        **_installed_status(dest_dir, dxnn_url, artifacts.get(f"{tier}_json")),
    }


def _models_from_payload(html):
    """Build the model list from the public page's `window.__MODEL_ZOO_DATA__`.

    developer.deepx.ai/modelzoo/ no longer carries data rows in its table (one <table>
    with only the two header <tr>s), so a table parser finds nothing and this source
    reads the payload instead. The parser is shared with dx_modelzoo
    (shared/modelzoo_payload.py): two copies of the tier and field knowledge would
    mean only one gets fixed when the page changes again.
    """
    from shared.modelzoo_payload import parse_public_payload

    models = []
    for row in parse_public_payload(html):
        artifacts = row.get("artifacts") or {}
        models.append({
            "name": row.get("display") or row.get("name") or "",
            "class_name": row.get("name") or "",
            "task": row.get("task") or "",
            "dataset": row.get("dataset") or "",
            "input_resolution": row.get("input") or "",
            "ops": row.get("ops"),
            "params": row.get("params"),
            "license": row.get("license") or "",
            "metric": row.get("metric") or "",
            "raw_accuracy": (row.get("accuracy") or {}).get("raw"),
            "onnx_url": artifacts.get("onnx"),
            "qlite": _tier_block(row, "qlite"),
            "qpro": _tier_block(row, "qpro"),
            "qmaster": _tier_block(row, "qmaster"),
            "fps": row.get("fps"),
            "fps_per_watt": row.get("fps_per_watt"),
        })
    return models


def modelzoo_list(source="internal"):
    """Return parsed model list (cached)."""
    now = time.time()
    with _cache_lock:
        if _cache["models"] and _cache["source"] == source and now - _cache["ts"] < _CACHE_TTL:
            _refresh_exists(_cache["models"])
            return {"ok": True, "models": _cache["models"], "cached": True}

    html, err = _fetch_page(source)
    if err:
        return {"ok": False, "error": err, "models": []}

    # Each source has a different document shape: the public page is inline JSON, the
    # internal publish page a 20-column table. _parse_models only parses tables.
    if source == SOURCE_PUBLIC:
        # developer.deepx.ai/modelzoo/ wraps the catalog in a same-host iframe; read the frame's document.
        from shared.modelzoo_payload import payload_frame_url
        frame = payload_frame_url(html, SOURCE_URLS[SOURCE_PUBLIC])
        if frame:
            html, err = _fetch_url(source, frame)
            if err:
                return {"ok": False, "error": err, "models": []}
        try:
            models = _models_from_payload(html)
        except ValueError as e:
            return {"ok": False, "error": f"ModelZoo payload unreadable: {e}", "models": []}
    else:
        models = _parse_models(html)
    if not models:
        return {"ok": False, "error": "No models found — page structure may have changed", "models": []}

    _refresh_exists(models)
    with _cache_lock:
        _cache.update({"models": models, "source": source, "ts": time.time()})

    return {"ok": True, "models": models, "count": len(models), "cached": False}


def _refresh_exists(models):
    """Update 'exists' flags based on current disk state."""
    for m in models:
        for chip, (dest_dir, _rel) in _CHIP_DIRS.items():
            tier = m.get(chip)
            if not tier or not tier.get("dxnn_url"):
                continue
            tier.update(_installed_status(dest_dir, tier["dxnn_url"], tier.get("json_url")))


def _build_tasks(items):
    """items -> download task list. Starts no threads, so it can be checked directly.

    Unknown chips are refused. With `MODELS_DIR if chip == "qlite" else QPRO_DIR` a
    single typo would silently land in q-pro; a model installed in the wrong place
    shows as missing, and the user cannot tell why downloading again does not help.
    """
    tasks = []
    for item in items:
        chip = item.get("chip", "qlite")
        if chip not in _CHIP_DIRS:
            raise ValueError(
                f"unknown chip {chip!r} — expected one of {sorted(_CHIP_DIRS)}"
            )
        dest_dir = _CHIP_DIRS[chip][0]

        for kind, url in (("dxnn", item.get("dxnn_url")), ("json", item.get("json_url"))):
            if not url:
                continue
            fname = Path(urlparse(url).path).name
            tasks.append({
                "name": item["name"], "chip": chip, "type": kind,
                "url": url, "dest": dest_dir / fname,
            })
    return tasks


def modelzoo_download(items, source="internal"):
    """Start background download of selected items.

    items: [{"name": "...", "chip": "qlite"|"qpro"|"qmaster", "dxnn_url": "...", "json_url": "..."|null}, ...]
    """
    with _dl_lock:
        if _dl_state["running"]:
            return {"ok": False, "error": "Download already in progress"}

    try:
        tasks = _build_tasks(items)
    except ValueError as e:
        return {"ok": False, "error": str(e)}

    if not tasks:
        return {"ok": False, "error": "No download tasks"}

    with _dl_lock:
        _reset_dl_state()
        _dl_state["running"] = True
        _dl_state["total"] = len(tasks)
        _dl_state["finished"] = False

    threading.Thread(
        target=_download_worker, args=(tasks, source), daemon=True
    ).start()

    return {"ok": True, "total": len(tasks), "started": True}


def _ensure_dir(path):
    """Create a target dir, following symlinks. assets/models is a symlink into
    workspace/res; when its target is pruned the link goes dangling, and then
    Path.mkdir(exist_ok=True) / os.makedirs(exist_ok=True) both raise
    FileExistsError (exist_ok can't suppress it because is_dir() is False on a
    dangling link). Resolving to the real target first creates the intended dir."""
    os.makedirs(os.path.realpath(path), exist_ok=True)


def _download_worker(tasks, source):
    """Background worker — download files sequentially (with thread pool for speed)."""
    opener = None

    def _dl_one(task):
        if _dl_state["cancel"]:
            return {"file": task["dest"].name, "status": "cancelled"}

        with _dl_lock:
            _dl_state["current"] = f"{task['name']} ({task['chip']}/{task['type']})"

        dest = task["dest"]
        _ensure_dir(dest.parent)
        # If DX-RT cannot read v9 (Model Zoo 2_5_0), fetch the same file from 2_4_0 (v8). A model missing from 2_4_0
        # is not downloaded and ends with "DX-RT 3.5 required": a download would fail to run anyway.
        urls = _dxrt.download_urls(task["url"])
        last_err = None

        def validate(path):
            if task["type"] == "dxnn" and _dxrt.needs_for_file(path):
                raise ValueError("needs_dxrt")

        for url in urls:
            try:
                result = download_file(
                    url, dest, open_url=lambda value: _open(opener, value, 120),
                    cancel=lambda: _dl_state["cancel"], validate=validate,
                    skip_existing=not (task["type"] == "dxnn" and _dxrt.needs_for_file(dest)),
                )
                return {"file": dest.name, "status": "ok", "size": result.size,
                        "verification": result.verification,
                        "chip": task["chip"], "name": task["name"]}
            except DownloadCancelled:
                return {"file": dest.name, "status": "cancelled"}
            except Exception as e:
                last_err = ("needs_dxrt" if getattr(e, "code", None) == 404
                            and urls != [task["url"]] and _dxrt.is_v9_only(task["url"])
                            else str(e))
        if task["type"] == "dxnn" and last_err == "needs_dxrt":
            return {"file": dest.name, "status": "needs_dxrt", "needs_dxrt": _dxrt.NEEDS_FOR_V9,
                    "error": f"DX-RT {_dxrt.NEEDS_FOR_V9} required (this .dxnn is container v9)",
                    "chip": task["chip"], "name": task["name"]}
        return {"file": dest.name, "status": "error", "error": last_err or "download failed"}

    try:
        opener = _make_opener(source)
        # Create the model dirs up front. Do it here (not at module import) so a
        # failure surfaces as a download error and, via the finally below, never
        # leaves the state stuck "running" (which would block every later download
        # with "Download already in progress").
        for _dest_dir in {task["dest"].parent for task in tasks}:
            _ensure_dir(_dest_dir)

        with ThreadPoolExecutor(max_workers=4) as pool:
            futures = {pool.submit(_dl_one, t): t for t in tasks}
            for fut in as_completed(futures):
                res = fut.result()
                with _dl_lock:
                    _dl_state["results"].append(res)
                    _dl_state["done"] += 1
    except Exception as e:
        with _dl_lock:
            _dl_state["results"].append(
                {"file": "", "status": "error", "error": f"download failed: {e}"})
    finally:
        with _dl_lock:
            _dl_state["running"] = False
            _dl_state["finished"] = True
            _dl_state["current"] = ""

    _auto_register()

    # Invalidate cache so next list refreshes exists flags
    with _cache_lock:
        _cache["ts"] = 0


def modelzoo_status():
    """Poll download progress."""
    with _dl_lock:
        return {
            "running": _dl_state["running"],
            "total": _dl_state["total"],
            "done": _dl_state["done"],
            "current": _dl_state["current"],
            "results": list(_dl_state["results"]),
            "finished": _dl_state["finished"],
        }


def modelzoo_stop():
    """Cancel ongoing download."""
    with _dl_lock:
        if _dl_state["running"]:
            _dl_state["cancel"] = True
            return {"ok": True, "status": "cancelling"}
        return {"ok": False, "status": "not_running"}


def _auto_register():
    """After download, update test_models.conf for newly downloaded models."""
    # The per-model layout's registry already has every model, so nothing more is written to the external
    # repo's test_models.conf.
    from shared import dx_app_layout as _layout
    if _layout.detect(DX_APP_ROOT) == _layout.PER_MODEL:
        return
    try:
        from dx_app.core.models import _reload_reg

        reg_file = DX_APP_ROOT / "config" / "model_registry.json"
        registry = {}
        if reg_file.exists():
            try:
                for entry in json.loads(reg_file.read_text()):
                    registry[entry.get("dxnn_file", "").lower()] = entry
            except Exception:
                pass

        existing = {m["model_file"] for m in _shared_parse_test_models_conf(CONFIG_FILE)}

        new_entries = []
        with _dl_lock:
            for res in _dl_state["results"]:
                if res.get("status") != "ok" or not res.get("file", "").endswith(".dxnn"):
                    continue
                chip = res.get("chip", "qlite")
                if chip not in _CHIP_DIRS:
                    # _build_tasks already blocks this, but skip rather than write a bogus path
                    # to the registry: a wrong line would only ever show as "model missing".
                    continue
                fname = res["file"]
                rel_path = f"{_CHIP_DIRS[chip][1]}/{fname}"

                if rel_path in existing:
                    continue

                reg_entry = registry.get(fname.lower(), {})
                model_name = reg_entry.get("model_name", Path(fname).stem.lower())
                category = reg_entry.get("add_model_task", "object_detection")

                new_entries.append(f"{model_name}\t{category}\t{rel_path}")
                existing.add(rel_path)

        if new_entries:
            with open(CONFIG_FILE, "a") as f:
                f.write("\n# -- ModelZoo Downloads --\n")
                for entry in new_entries:
                    f.write(entry + "\n")
            print(f"[MODELZOO] Registered {len(new_entries)} new model(s) in test_models.conf")

            _reload_reg()

    except Exception as e:
        print(f"[MODELZOO] Auto-register error: {e}")
