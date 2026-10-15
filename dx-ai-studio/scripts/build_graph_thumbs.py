"""Result thumbnails of the Graph Composer's example graphs (dx_app's samples: the templates with logic blocks and
the engine examples).

Runs each example whose models are installed once on the NPU through dx_app/core/graph_run.py (the real graph
binary, the graph's own sample input, one frame) and writes its rendered result, cropped to 16:9 and scaled to
320x180, to dx_app/static/img/graph-examples/<id>.jpg; an example with a model missing is named and left out. The
palette shows it (graph_catalog._thumb) unless dx_app ships its own <id>.jpg next to the graph.

    .venv/bin/python -m scripts.build_graph_thumbs [--only <id> ...]

Contract: tests/dx_app/test_graph_thumbs.py
"""
from __future__ import annotations

import argparse
import io
import sys
import time
from pathlib import Path

SIZE = (320, 180)
QUALITY = 80


def make_thumb(data: bytes, size=SIZE) -> bytes:
    """A JPEG of `size`, the picture cropped around its centre to that aspect."""
    from PIL import Image, ImageOps
    img = Image.open(io.BytesIO(data))
    img.load()
    out = io.BytesIO()
    ImageOps.fit(img.convert("RGB"), size, Image.Resampling.LANCZOS).save(out, format="JPEG", quality=QUALITY,
                                                                          optimize=True)
    return out.getvalue()


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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", nargs="*", default=None, help="example ids (default: every example)")
    args = ap.parse_args(argv)
    from dx_app.core import config, graph_catalog
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
        src = Path(config.OUTPUTS_DIR) / outputs[0]["url"][len("/outputs/"):]
        dst = out_dir / f"{ex['id']}.jpg"
        dst.write_bytes(make_thumb(result_picture(src)))
        print(f"ok   {ex['id']}: {dst.relative_to(Path(__file__).resolve().parents[1])} ({dst.stat().st_size} bytes)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
