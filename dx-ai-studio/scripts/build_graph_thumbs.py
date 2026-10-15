"""Result thumbnails of the Graph Composer's example graphs (dx_app's samples: the templates with logic blocks and
the engine examples).

Runs each example whose models are installed once on the NPU through dx_app/core/graph_run.py (the real graph
binary, the graph's own sample input, one frame) and writes its rendered result, cropped to 16:9 and scaled to
320x180, to dx_app/static/img/graph-examples/<id>.jpg; an example with a model missing is named and left out. A
run of several sources becomes a grid, one cell per source, as the results view lays them out. The palette shows it
(graph_catalog._thumb) unless dx_app ships its own <id>.jpg next to the graph.

    .venv/bin/python -m scripts.build_graph_thumbs [--only <id> ...]
    .venv/bin/python -m scripts.build_graph_thumbs --tutorial-preview multistream_people_count

--tutorial-preview records the tutorial's result preview instead (tutorial.js, graph section): one image run of that
example with its layers, scaled down, into dx_app/static/img/graph-tutorial/ with preview.json.

Contract: tests/dx_app/test_graph_thumbs.py
"""
from __future__ import annotations

import argparse
import io
import json
import sys
import time
from pathlib import Path

SIZE = (320, 180)
QUALITY = 80
GAP = 2                       # px between the cells of a grid thumbnail
BACKDROP = (16, 16, 16)       # an empty cell of a 2x2 grid
TUTORIAL_DIR = Path(__file__).resolve().parents[1] / "dx_app" / "static" / "img" / "graph-tutorial"
TUTORIAL_URL = "/static/img/graph-tutorial/"
PREVIEW_WIDTH = 640
# What the tutorial's recorded result keeps of a run's result (graph_run.result): no run id (nothing on the server
# to inspect), no log, no events file.
_PREVIEW_KEYS = ("ok", "frames", "error_frames", "fps", "avg_fps", "node_ms", "nodes", "elapsed", "events",
                 "event_total", "event_counts")


def make_thumb(data: bytes, size=SIZE) -> bytes:
    """A JPEG of `size`, the picture cropped around its centre to that aspect."""
    from PIL import Image, ImageOps
    img = Image.open(io.BytesIO(data))
    img.load()
    out = io.BytesIO()
    ImageOps.fit(img.convert("RGB"), size, Image.Resampling.LANCZOS).save(out, format="JPEG", quality=QUALITY,
                                                                          optimize=True)
    return out.getvalue()


def tile(pictures: list, size=SIZE) -> bytes:
    """A thumbnail of a run's results laid out as the results view lays out its cells (graph-results.js): one
    picture fills it, two sit side by side, three or four make a 2x2 grid; past four, the first four. Each cell is
    its picture cropped around its centre."""
    from PIL import Image, ImageOps
    pics = list(pictures)[:4]
    if len(pics) == 1:
        return make_thumb(pics[0], size)
    cols, rows = (2, 1) if len(pics) == 2 else (2, 2)
    w, h = (size[0] - GAP * (cols - 1)) // cols, (size[1] - GAP * (rows - 1)) // rows
    canvas = Image.new("RGB", size, BACKDROP)
    for i, data in enumerate(pics):
        img = Image.open(io.BytesIO(data))
        img.load()
        cell = ImageOps.fit(img.convert("RGB"), (w, h), Image.Resampling.LANCZOS)
        canvas.paste(cell, ((i % cols) * (w + GAP), (i // cols) * (h + GAP)))
    out = io.BytesIO()
    canvas.save(out, format="JPEG", quality=QUALITY, optimize=True)
    return out.getvalue()


def _scaled(path: Path, width=PREVIEW_WIDTH):
    from PIL import Image
    img = Image.open(path)
    img.load()
    if img.width > width:
        img = img.resize((width, round(img.height * width / img.width)), Image.Resampling.LANCZOS)
    return img


def write_preview(r: dict, outputs_dir: Path, out_dir: Path = None, url: str = TUTORIAL_URL) -> dict:
    """The tutorial's recorded result (GraphRun.preview): a finished image run with layers, in graph_run.result's
    shape, its pictures scaled to PREVIEW_WIDTH and written into `out_dir` beside preview.json. The pictures and
    preview.json already there are replaced; other files are kept."""
    from PIL import Image
    out_dir = Path(out_dir or TUTORIAL_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    for p in out_dir.iterdir():
        if p.suffix in (".jpg", ".png") or p.name == "preview.json":
            p.unlink()

    def local(u):
        return Path(outputs_dir) / u[len("/outputs/"):]

    outputs = []
    for o in r.get("outputs") or []:
        lay = o.get("layers")
        if o.get("kind") != "image" or not lay:
            raise ValueError(f"{o.get('name')}: the preview needs image results with layers")
        s = o["stream"]
        _scaled(local(o["url"])).convert("RGB").save(out_dir / f"{s}.jpg", format="JPEG", quality=QUALITY,
                                                     optimize=True)
        base = _scaled(local(lay["base"])).convert("RGB")
        base.save(out_dir / f"{s}_base.jpg", format="JPEG", quality=QUALITY, optimize=True)
        rows = []
        for layer in lay.get("layers") or []:
            name = f"{s}_{layer.get('node') or 'panel-' + layer.get('panel', '')}.png"
            img = _scaled(local(layer["url"])).convert("RGBA")
            if img.size != base.size:
                img = img.resize(base.size, Image.Resampling.LANCZOS)
            img.save(out_dir / name, format="PNG", optimize=True)
            row = {k: layer[k] for k in ("node", "model", "op", "panel") if k in layer}
            row["url"] = url + name
            rows.append(row)
        outputs.append({"url": url + f"{s}.jpg", "kind": "image", "name": f"result_{s}.jpg", "stream": s,
                        "layers": {"base": url + f"{s}_base.jpg", "width": base.width, "height": base.height,
                                   "layers": rows}})
    doc = {k: r[k] for k in _PREVIEW_KEYS if k in r}
    doc.update(exit_code=0, run_id=None, outputs=outputs, errors=[], events_truncated=False, events_url=None,
               events_partial=False, preview=True)
    (out_dir / "preview.json").write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    return doc


def result_picture(output: Path) -> bytes:
    """The rendered result of a run: the image, or a video's first frame."""
    from dx_app.core import graph_frame, graph_run
    if output.suffix.lower() in graph_run._VIDEO_EXT:
        return graph_frame._video_frame(output)
    return output.read_bytes()


def run_once(graph: dict, timeout: float = 180.0) -> dict:
    from dx_app.core import graph_run
    body, code = graph_run.start(graph, frames=1)
    if code != 200:
        return {"ok": False, "errors": [{"code": body.get("error_key"), "what": body.get("error")}]}
    end = time.time() + timeout
    while time.time() < end and not graph_run.poll(body["job_id"]).get("has_result"):
        time.sleep(0.5)
    r = graph_run.result(body["job_id"])
    if r.get("running"):                    # out of time: stop it, so the next template gets the NPU
        graph_run.stop(body["job_id"])
        return {"ok": False, "errors": [{"code": "timeout", "what": f"no result after {timeout:g} s"}]}
    return r


def plan(examples: list, installed: set, only=None) -> tuple:
    """(the examples to run, [(id, its missing models)]) — `only` limits both to those ids."""
    run, skipped = [], []
    for ex in examples:
        if only and ex["id"] not in only:
            continue
        missing = sorted(m for m in ex.get("models") or [] if m not in installed)
        if missing:
            skipped.append((ex["id"], missing))
        else:
            run.append(ex)
    return run, skipped


def record_preview(example_id: str) -> int:
    """Run one example once on the NPU and keep its result as the tutorial's preview."""
    from dx_app.core import config, graph_catalog
    ex = next((e for e in graph_catalog.examples() if e["id"] == example_id), None)
    if ex is None:
        print(f"FAIL {example_id}: no such example")
        return 1
    r = run_once(ex["graph"])
    if not r.get("ok") or not r.get("outputs"):
        print(f"FAIL {example_id}: {(r.get('errors') or [{}])[0]}")
        return 1
    doc = write_preview(r, Path(config.OUTPUTS_DIR))
    size = sum(p.stat().st_size for p in TUTORIAL_DIR.iterdir())
    print(f"ok   tutorial preview from {example_id}: {len(doc['outputs'])} cells, {doc.get('event_total', 0)} events, "
          f"{size} bytes")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", default=None, help="example ids (default: every example)")
    ap.add_argument("--tutorial-preview", metavar="ID", default=None,
                    help="record the tutorial's result preview from this example instead of thumbnails")
    args = ap.parse_args(argv)
    from dx_app.core import config, graph_catalog
    if args.tutorial_preview:
        return record_preview(args.tutorial_preview)
    out_dir = graph_catalog.THUMBS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    installed = {m["name"] for m in graph_catalog.list_models(refresh=True)["models"] if m["state"] == "installed"}
    todo, skipped = plan(graph_catalog.examples(), installed, args.only)
    for ex_id, missing in skipped:
        print(f"skip {ex_id}: not installed: {', '.join(missing)}")
    failed = 0
    for ex in todo:
        r = run_once(ex["graph"])
        outputs = r.get("outputs") or []
        if not r.get("ok") or not outputs:
            failed += 1
            print(f"FAIL {ex['id']}: {(r.get('errors') or [{}])[0]}")
            continue
        pictures = [result_picture(Path(config.OUTPUTS_DIR) / o["url"][len("/outputs/"):]) for o in outputs]
        dst = out_dir / f"{ex['id']}.jpg"
        dst.write_bytes(tile(pictures))
        print(f"ok   {ex['id']}: {dst.relative_to(Path(__file__).resolve().parents[1])} ({dst.stat().st_size} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
