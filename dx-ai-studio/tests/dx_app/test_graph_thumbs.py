"""scripts/build_graph_thumbs.py: a template's result picture becomes a 320x180 JPEG for the palette."""
from __future__ import annotations

import io
import json
import shutil
from pathlib import Path

import pytest

from scripts import build_graph_thumbs as thumbs

Image = pytest.importorskip("PIL.Image")


def _jpeg(w, h):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), (200, 30, 30)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.mark.parametrize("w, h", [(640, 640), (1920, 1080), (480, 1200)])
def test_any_picture_becomes_a_small_16_by_9_jpeg(w, h):
    out = Image.open(io.BytesIO(thumbs.make_thumb(_jpeg(w, h))))
    assert out.format == "JPEG" and out.size == (320, 180)


def test_a_thumbnail_stays_small():
    assert len(thumbs.make_thumb(_jpeg(1920, 1080))) < 40 * 1024


def test_the_thumbnails_land_where_the_catalog_looks():
    from dx_app.core import graph_catalog
    assert graph_catalog.THUMBS_DIR.parts[-4:] == ("dx_app", "static", "img", "graph-examples")


def test_every_example_whose_models_are_installed_is_run_and_the_rest_named():
    examples = [{"id": "zone_intrusion", "logic": True, "models": ["yolov8-n_640x640"]},
                {"id": "cascade_od_attr", "logic": False, "models": ["yolov8-n_640x640", "deepmar_resnet50_224x224"]},
                {"id": "dms_headpose", "logic": False, "models": ["scrfd_500m", "headpose"]}]
    run, skipped = thumbs.plan(examples, installed={"yolov8-n_640x640", "deepmar_resnet50_224x224"})
    assert [e["id"] for e in run] == ["zone_intrusion", "cascade_od_attr"]
    assert skipped == [("dms_headpose", ["headpose", "scrfd_500m"])]
    run, skipped = thumbs.plan(examples, installed={"yolov8-n_640x640"}, only=["zone_intrusion"])
    assert [e["id"] for e in run] == ["zone_intrusion"] and skipped == []


def _png(w, h, rgb):
    buf = io.BytesIO()
    Image.new("RGB", (w, h), rgb).save(buf, format="PNG")
    return buf.getvalue()


def test_one_result_is_the_plain_thumbnail():
    one = _png(640, 360, (200, 30, 30))
    assert thumbs.tile([one]) == thumbs.make_thumb(one)


def test_two_sources_sit_side_by_side_like_the_results_view():
    out = Image.open(io.BytesIO(thumbs.tile([_png(640, 640, (200, 30, 30)), _png(1920, 1080, (30, 30, 200))])))
    assert out.format == "JPEG" and out.size == (320, 180)
    left, right = out.getpixel((40, 90)), out.getpixel((280, 90))
    assert left[0] > 150 and left[2] < 80, left
    assert right[2] > 150 and right[0] < 80, right


def test_three_or_four_sources_make_a_two_by_two_grid():
    colours = [(200, 30, 30), (30, 200, 30), (30, 30, 200)]
    out = Image.open(io.BytesIO(thumbs.tile([_png(320, 180, c) for c in colours])))
    assert out.size == (320, 180)
    assert out.getpixel((40, 40))[0] > 150       # top left: the first source
    assert out.getpixel((280, 40))[1] > 150      # top right: the second
    assert out.getpixel((40, 140))[2] > 150      # bottom left: the third
    assert max(out.getpixel((280, 140))) < 60    # bottom right: empty


def test_past_four_sources_the_first_four_are_shown():
    pics = [_png(64, 36, (200, 30, 30))] * 4 + [_png(64, 36, (30, 200, 30))]
    out = Image.open(io.BytesIO(thumbs.tile(pics)))
    assert out.getpixel((280, 140))[0] > 150


LAYERS = Path(__file__).resolve().parent / "fixtures" / "graph" / "layers"


def _run_result(outputs_dir):
    """A finished image run of two sources with --output-layers, as graph_run.result gives it."""
    d = outputs_dir / "graph" / "runs" / "r1"
    (d / "layers").mkdir(parents=True)
    u = "/outputs/graph/runs/r1/"
    rows = []
    for s in ("cam1", "cam2"):
        shutil.copy(LAYERS / "base.png", d / f"result_{s}.jpg")       # Pillow reads it by content
        shutil.copy(LAYERS / "base.png", d / "layers" / f"{s}_base.png")
        shutil.copy(LAYERS / "layer.png", d / "layers" / f"{s}_od.png")
        shutil.copy(LAYERS / "layer.png", d / "layers" / f"{s}_events.png")
        rows.append({"url": u + f"result_{s}.jpg", "kind": "image", "name": f"result_{s}.jpg", "stream": s,
                     "layers": {"base": u + f"layers/{s}_base.png", "width": 16, "height": 12, "layers": [
                         {"node": "od", "model": "yolov8-n_640x640", "url": u + f"layers/{s}_od.png"},
                         {"panel": "events", "url": u + f"layers/{s}_events.png"}]}})
    return {"ok": True, "exit_code": 0, "run_id": "r1", "outputs": rows, "frames": 2, "error_frames": 0,
            "fps": None, "avg_fps": None, "node_ms": {"od": 12.5}, "nodes": {"od": {"shape": "boxes"}},
            "errors": [], "log_tail": "a log", "elapsed": 1.2,
            "events": [{"seq": 1, "frame": 0, "time": 0, "stream": "cam2", "node": "crowded", "event": "crowded",
                        "track_id": -1, "data": {"value": 15, "threshold": 5}}],
            "event_total": 1, "event_counts": {"crowded": {"crowded": 1}}, "events_truncated": False,
            "events_url": u + "events.jsonl", "events_partial": False}


def test_the_tutorial_preview_is_the_run_with_its_pictures_beside_it(tmp_path):
    outputs, out = tmp_path / "outputs", tmp_path / "graph-tutorial"
    doc = thumbs.write_preview(_run_result(outputs), outputs, out, url="/static/img/graph-tutorial/")
    assert json.loads((out / "preview.json").read_text(encoding="utf-8")) == doc
    assert doc["preview"] is True and doc["run_id"] is None and doc["events_url"] is None and "log_tail" not in doc
    assert [o["stream"] for o in doc["outputs"]] == ["cam1", "cam2"]
    assert doc["events"][0]["event"] == "crowded" and doc["node_ms"] == {"od": 12.5} and doc["event_total"] == 1
    cam2 = doc["outputs"][1]
    assert cam2["url"] == "/static/img/graph-tutorial/cam2.jpg" and cam2["kind"] == "image"
    assert cam2["layers"]["base"] == "/static/img/graph-tutorial/cam2_base.jpg"
    assert cam2["layers"]["layers"] == [
        {"node": "od", "model": "yolov8-n_640x640", "url": "/static/img/graph-tutorial/cam2_od.png"},
        {"panel": "events", "url": "/static/img/graph-tutorial/cam2_panel-events.png"}]
    for o in doc["outputs"]:
        for u in [o["url"], o["layers"]["base"]] + [l["url"] for l in o["layers"]["layers"]]:
            assert (out / u.rsplit("/", 1)[1]).is_file(), u
    assert Image.open(out / "cam2_od.png").mode == "RGBA"


def test_the_preview_pictures_are_scaled_to_the_preview_width(tmp_path):
    outputs = tmp_path / "outputs"
    r = _run_result(outputs)
    d = outputs / "graph" / "runs" / "r1" / "layers"
    Image.new("RGB", (1920, 1080), (9, 9, 9)).save(d / "cam1_base.png")
    Image.new("RGBA", (1920, 1080), (0, 0, 0, 0)).save(d / "cam1_od.png")
    doc = thumbs.write_preview(r, outputs, tmp_path / "p")
    cam1 = doc["outputs"][0]["layers"]
    assert (cam1["width"], cam1["height"]) == (640, 360)
    assert Image.open(tmp_path / "p" / "cam1_od.png").size == (640, 360)
    assert Image.open(tmp_path / "p" / "cam1_panel-events.png").size == (640, 360), "every layer fits its base"


def test_a_preview_needs_image_results_with_layers(tmp_path):
    outputs = tmp_path / "outputs"
    r = _run_result(outputs)
    del r["outputs"][0]["layers"]
    with pytest.raises(ValueError, match="layers"):
        thumbs.write_preview(r, outputs, tmp_path / "p")


def test_writing_a_preview_replaces_only_its_own_files(tmp_path):
    outputs, out = tmp_path / "outputs", tmp_path / "p"
    out.mkdir()
    (out / "old_cam9.jpg").write_bytes(b"x")
    (out / "notes.txt").write_text("keep")
    thumbs.write_preview(_run_result(outputs), outputs, out)
    assert not (out / "old_cam9.jpg").exists() and (out / "notes.txt").read_text() == "keep"


def test_the_shipped_tutorial_preview_is_a_complete_recorded_run():
    """dx_app/static/img/graph-tutorial/ (Task 4 of the Phase 4 plan): multistream_people_count on its samples."""
    doc = json.loads((thumbs.TUTORIAL_DIR / "preview.json").read_text(encoding="utf-8"))
    assert doc["preview"] is True and doc["ok"] is True and doc["run_id"] is None
    assert [o["stream"] for o in doc["outputs"]] == ["cam1", "cam2"]
    assert all(o["layers"]["layers"] for o in doc["outputs"]), "every cell has its layers"
    assert any(e["stream"] == "cam2" and e["event"] == "crowded" for e in doc["events"])
    urls = [u for o in doc["outputs"] for u in [o["url"], o["layers"]["base"]] + [l["url"] for l in o["layers"]["layers"]]]
    for u in urls:
        assert u.startswith(thumbs.TUTORIAL_URL) and (thumbs.TUTORIAL_DIR / u[len(thumbs.TUTORIAL_URL):]).is_file(), u
    assert sum(p.stat().st_size for p in thumbs.TUTORIAL_DIR.iterdir()) < 600 * 1024


def test_the_new_templates_have_their_thumbnails():
    from dx_app.core import graph_catalog
    for ex_id in ("driver_attention", "multistream_people_count", "logistics_volume_alert"):
        assert (graph_catalog.THUMBS_DIR / f"{ex_id}.jpg").is_file(), ex_id


def test_no_pictures_make_no_thumbnail():
    with pytest.raises(ValueError):
        thumbs.tile([])


def test_a_failed_preview_keeps_the_one_before(tmp_path):
    outputs, out = tmp_path / "outputs", tmp_path / "p"
    thumbs.write_preview(_run_result(outputs), outputs, out)
    before = {p.name: p.read_bytes() for p in out.iterdir()}
    bad = _run_result(tmp_path / "outputs2")
    del bad["outputs"][1]["layers"]
    with pytest.raises(ValueError, match="layers"):
        thumbs.write_preview(bad, tmp_path / "outputs2", out)
    assert {p.name: p.read_bytes() for p in out.iterdir()} == before
    missing = _run_result(tmp_path / "outputs3")
    (tmp_path / "outputs3" / "graph" / "runs" / "r1" / "layers" / "cam2_od.png").unlink()
    with pytest.raises(FileNotFoundError):
        thumbs.write_preview(missing, tmp_path / "outputs3", out)
    assert {p.name: p.read_bytes() for p in out.iterdir()} == before


def test_layers_without_a_node_or_a_panel_keep_their_own_files(tmp_path):
    outputs = tmp_path / "outputs"
    r = _run_result(outputs)
    u = "/outputs/graph/runs/r1/layers/"
    r["outputs"][0]["layers"]["layers"] = [{"url": u + "cam1_od.png"}, {"url": u + "cam1_events.png"}]
    doc = thumbs.write_preview(r, outputs, tmp_path / "p")
    urls = [l["url"] for l in doc["outputs"][0]["layers"]["layers"]]
    assert len(set(urls)) == 2 and all((tmp_path / "p" / x.rsplit("/", 1)[1]).is_file() for x in urls)


def _banded(w, h, band):
    """A w x h gray picture with a red band `band` px tall along its top and a blue one along its bottom: an
    alert line and an event panel drawn at the frame's edges."""
    img = Image.new("RGB", (w, h), (128, 128, 128))
    img.paste((220, 0, 0), (0, 0, w, band))
    img.paste((0, 0, 220), (0, h - band, w, h))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_logistics_volume_alert_keeps_its_alert_line_and_its_event_panel():
    """Its 500x333 result has the load_high line along the top edge and the event panel along the bottom one; a
    16:9 centre crop cut both. It is shown whole, on the backdrop at its sides."""
    assert thumbs.framing("logistics_volume_alert") == "contain"
    pic = _banded(500, 333, 25)
    out = Image.open(io.BytesIO(thumbs.tile([pic], fit=thumbs.framing("logistics_volume_alert")))).convert("RGB")
    assert out.size == (320, 180)
    r, g, b = out.getpixel((160, 4))
    assert r > 180 and b < 60, (r, g, b)
    r, g, b = out.getpixel((160, 175))
    assert b > 180 and r < 60, (r, g, b)
    assert all(c < 40 for c in out.getpixel((4, 90)))          # the backdrop beside the picture
    # The centre crop the others keep loses both bands.
    cropped = Image.open(io.BytesIO(thumbs.tile([pic]))).convert("RGB")
    assert cropped.getpixel((160, 4))[0] < 180 and cropped.getpixel((160, 175))[2] < 180


def test_the_other_examples_keep_the_centre_crop():
    for ex_id in ("zone_intrusion", "logistics_volume", "driver_attention", "hand_cascade"):
        assert thumbs.framing(ex_id) == "crop"
    pic = _png(640, 640, (200, 30, 30))
    assert thumbs.tile([pic], fit="crop") == thumbs.tile([pic]) == thumbs.make_thumb(pic)
