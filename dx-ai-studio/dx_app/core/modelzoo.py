"""DX-APP ModelZoo — browse, cart, download from DEEPX ModelZoo page."""

import os, sys, json, time, threading, re, ssl
import urllib.request
from pathlib import Path
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed

from dx_app.core import config
from dx_app.core.config import DX_APP_ROOT, ASSETS_DIR, SCRIPTS_DIR, CONFIG_FILE
from dx_app.core._html_dom import parse_html
from shared.catalog_sources import parse_test_models_conf as _shared_parse_test_models_conf

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

MODELS_DIR = ASSETS_DIR / "models"
QPRO_DIR = MODELS_DIR / "q-pro"

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
    req = urllib.request.Request(url, headers={"User-Agent": "DX-APP-ModelZoo/2.0"})
    return opener.open(req, timeout=timeout)


def _fetch_page(source):
    url = SOURCE_URLS.get(source, SOURCE_URLS[SOURCE_INTERNAL])
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
            # Header row 0 distinguishes the two server-rendered layouts:
            #   internal devops page → [Task, Name, ClassName, Dataset, …]  (spec cols start at 2)
            #   public developer.deepx.ai/modelzoo/ → [Class Name, Dataset, …]  (no Task/Name;
            #     model name = Class Name, category = the section heading; spec cols start at 0)
            hdr0 = [c.get_text(strip=True) for c in rows[0].find_all(["th", "td"])]
            public_layout = bool(hdr0) and hdr0[0].replace(" ", "").lower() == "classname"
            cstart = 0 if public_layout else 2
            # public section headings carry a count suffix, e.g. "Object Detection (116)"
            cat = re.sub(r"\s*\(\d+\)\s*$", "", current_category).strip() if public_layout else current_category

            # Skip header rows (0,1,2), parse data rows
            for row in rows[3:]:
                cells = row.find_all("td")
                if len(cells) < cstart + 16:
                    continue

                class_name = cells[cstart].get_text(strip=True)
                if public_layout:
                    name = class_name
                    task = cat
                else:
                    task = cells[0].get_text(strip=True)
                    name = cells[1].get_text(strip=True)
                if not name or name == "-":
                    continue

                dataset = cells[cstart + 1].get_text(strip=True)
                input_res = cells[cstart + 2].get_text(strip=True)
                ops = cells[cstart + 3].get_text(strip=True)
                params = cells[cstart + 4].get_text(strip=True)
                license_ = cells[cstart + 5].get_text(strip=True)
                metric = _cell_text(cells[cstart + 6])
                raw_acc = _cell_text(cells[cstart + 8])

                onnx_a = cells[cstart + 9].find("a", href=True)
                onnx_url = _abs(onnx_a["href"]) if onnx_a else None

                ql_acc = _cell_text(cells[cstart + 10])
                ql_dxnn_a = cells[cstart + 11].find("a", href=True)
                ql_json_a = cells[cstart + 12].find("a", href=True)
                ql_dxnn = _abs(ql_dxnn_a["href"]) if ql_dxnn_a else None
                ql_json = _abs(ql_json_a["href"]) if ql_json_a else None

                qp_acc = _cell_text(cells[cstart + 13])
                qp_dxnn_a = cells[cstart + 14].find("a", href=True)
                qp_json_a = cells[cstart + 15].find("a", href=True)
                qp_dxnn = _abs(qp_dxnn_a["href"]) if qp_dxnn_a else None
                qp_json = _abs(qp_json_a["href"]) if qp_json_a else None

                fps = cells[cstart + 16].get_text(strip=True) if len(cells) > cstart + 16 else ""
                fps_watt = cells[cstart + 17].get_text(strip=True) if len(cells) > cstart + 17 else ""

                ql_fname = Path(urlparse(ql_dxnn).path).name if ql_dxnn else None
                qp_fname = Path(urlparse(qp_dxnn).path).name if qp_dxnn else None
                ql_exists = bool(ql_fname and (MODELS_DIR / ql_fname).exists())
                qp_exists = bool(qp_fname and (QPRO_DIR / qp_fname).exists())

                uid = f"{task}|{name}"
                if uid in seen:
                    continue
                seen.add(uid)

                models.append({
                    "name": name,
                    "class_name": class_name,
                    "task": task or current_category,
                    "dataset": dataset,
                    "input_resolution": input_res,
                    "ops": ops,
                    "params": params,
                    "license": license_,
                    "metric": metric,
                    "raw_accuracy": raw_acc,
                    "onnx_url": onnx_url,
                    "qlite": {
                        "accuracy": ql_acc,
                        "dxnn_url": ql_dxnn,
                        "json_url": ql_json,
                        "exists": ql_exists,
                    },
                    "qpro": {
                        "accuracy": qp_acc,
                        "dxnn_url": qp_dxnn,
                        "json_url": qp_json,
                        "exists": qp_exists,
                    },
                    "fps": fps,
                    "fps_per_watt": fps_watt,
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
                    for a in c.find_all("a", href=True):
                        h = a["href"]
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
                fname = Path(urlparse(dxnn_url).path).name
                models.append({
                    "name": mname, "class_name": "", "task": task,
                    "dataset": "", "input_resolution": "", "ops": "", "params": "",
                    "license": "", "metric": "", "raw_accuracy": "",
                    "onnx_url": None,
                    "qlite": {
                        "accuracy": "",
                        "dxnn_url": dxnn_url,
                        "json_url": json_url,
                        "exists": (MODELS_DIR / fname).exists(),
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

    models = _parse_models(html)
    if not models:
        return {"ok": False, "error": "No models found — page structure may have changed", "models": []}

    with _cache_lock:
        _cache.update({"models": models, "source": source, "ts": time.time()})

    return {"ok": True, "models": models, "count": len(models), "cached": False}


def _refresh_exists(models):
    """Update 'exists' flags based on current disk state."""
    for m in models:
        ql = m.get("qlite", {})
        if ql.get("dxnn_url"):
            fname = Path(urlparse(ql["dxnn_url"]).path).name
            ql["exists"] = (MODELS_DIR / fname).exists()
        qp = m.get("qpro", {})
        if qp.get("dxnn_url"):
            fname = Path(urlparse(qp["dxnn_url"]).path).name
            qp["exists"] = (QPRO_DIR / fname).exists()


def modelzoo_download(items, source="internal"):
    """Start background download of selected items.

    items: [{"name": "...", "chip": "qlite"|"qpro", "dxnn_url": "...", "json_url": "..."|null}, ...]
    """
    with _dl_lock:
        if _dl_state["running"]:
            return {"ok": False, "error": "Download already in progress"}

    tasks = []
    for item in items:
        chip = item.get("chip", "qlite")
        dest_dir = MODELS_DIR if chip == "qlite" else QPRO_DIR

        dxnn_url = item.get("dxnn_url")
        json_url = item.get("json_url")

        if dxnn_url:
            fname = Path(urlparse(dxnn_url).path).name
            tasks.append({
                "name": item["name"], "chip": chip, "type": "dxnn",
                "url": dxnn_url, "dest": dest_dir / fname,
            })
        if json_url:
            fname = Path(urlparse(json_url).path).name
            tasks.append({
                "name": item["name"], "chip": chip, "type": "json",
                "url": json_url, "dest": dest_dir / fname,
            })

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
    opener = _make_opener(source)

    def _dl_one(task):
        if _dl_state["cancel"]:
            return {"file": task["dest"].name, "status": "cancelled"}

        with _dl_lock:
            _dl_state["current"] = f"{task['name']} ({task['chip']}/{task['type']})"

        url = task["url"]
        dest = task["dest"]
        _ensure_dir(dest.parent)

        try:
            with _open(opener, url, 120) as r:
                if r.status != 200:
                    return {"file": dest.name, "status": "error", "error": f"HTTP {r.status}"}
                downloaded = 0
                with open(dest, "wb") as f:
                    while True:
                        chunk = r.read(256 * 1024)
                        if not chunk:
                            break
                        if _dl_state["cancel"]:
                            return {"file": dest.name, "status": "cancelled"}
                        f.write(chunk)
                        downloaded += len(chunk)
            return {"file": dest.name, "status": "ok", "size": downloaded,
                    "chip": task["chip"], "name": task["name"]}
        except Exception as e:
            return {"file": dest.name, "status": "error", "error": str(e)}

    try:
        # Create the model dirs up front. Do it here (not at module import) so a
        # failure surfaces as a download error and, via the finally below, never
        # leaves the state stuck "running" (which would block every later download
        # with "Download already in progress").
        _ensure_dir(MODELS_DIR)
        _ensure_dir(QPRO_DIR)

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
                fname = res["file"]
                if chip == "qlite":
                    rel_path = f"assets/models/{fname}"
                else:
                    rel_path = f"assets/models/q-pro/{fname}"

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
