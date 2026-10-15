"""graph_catalog: the palette's models (from recorded --list-models output), CPU ops and the shipped examples."""
from __future__ import annotations

import json
import os
import time

import pytest

from dx_app.core import config, graph_catalog
from tests.dx_app import graph_fakes


@pytest.fixture(autouse=True)
def _fresh_cache():
    graph_catalog._cache.update(key=None, value=None)
    yield
    graph_catalog._cache.update(key=None, value=None)


def _by_name(models):
    return {m["name"]: m for m in models}


def test_the_text_table_is_read_with_every_file_state():
    r = graph_catalog.parse_list_models_text(graph_fakes.fixture("list_models.txt"))
    m = _by_name(r["models"])
    assert len(m) == 19
    assert m["fastdepth_224x224"] == {
        "name": "fastdepth_224x224", "task": "depth_estimation", "produces": "densemap", "consumes": "full_frame",
        "input": "224x224", "published": True, "file": "v8", "needs_dxrt": None, "ready": True, "reason": "",
        "ports": {}, "state": "installed", "installed": True}
    assert m["yolo26-n_640x640"]["file"] == "v9" and m["yolo26-n_640x640"]["installed"]
    assert m["yolo26-n_640x640_pre-optimized"]["state"] == "missing"
    assert m["yolo26-s_640x640"]["state"] == "invalid"            # a 0-byte file
    assert m["patchcore_224x224"]["state"] == "not_ready"
    assert m["patchcore_224x224"]["reason"] == "anomaly detection is not graph-ready in this release"
    assert m["3ddfa-v2_mobilenet-0.5_120x120"]["ports"] == {"pose": "vector"}
    assert m["deepmar_resnet50_224x224"]["consumes"] == "either"
    assert r["aliases"] == [{"name": "deit_base384_distilled", "alias_of": "deit-b_384x384_distilled"}]


def test_a_file_this_dx_rt_cannot_load_needs_a_newer_runtime():
    line = ("yolo26-n_640x640                                   object_detection                boxes      "
            "full_frame 640x640    yes       v9 (needs DX-RT >= 3.5.0) yes")
    (m,) = graph_catalog.parse_list_models_text(line)["models"]
    assert (m["file"], m["needs_dxrt"], m["state"]) == ("v9", "3.5.0", "needs_runtime")


def test_the_json_listing_reads_the_same_as_the_table():
    """dx_app prints a list of rows (input as {width, height}, ports as [{name, shape}], aliases as alias_of rows)."""
    text = graph_catalog.parse_list_models_text(graph_fakes.fixture("list_models.txt"))
    js = graph_catalog.parse_list_models_json(graph_fakes.fixture("list_models.json"))
    assert js == text


def test_list_models_runs_the_binary_once_until_the_models_dir_changes(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    first = graph_catalog.list_models()
    assert len(first["models"]) == 19 and first["error"] is None
    n = len(graph_fakes.calls(tmp_path))
    graph_catalog.list_models()
    assert len(graph_fakes.calls(tmp_path)) == n, "cached"
    later = time.time() + 5
    os.utime(tmp_path / "models", (later, later))           # a download landed
    graph_catalog.list_models()
    assert len(graph_fakes.calls(tmp_path)) == n + 1
    assert "--model-dir" in graph_fakes.calls(tmp_path)[-1]


def test_list_models_uses_json_when_the_build_has_it(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.JSON_CLI)
    r = graph_catalog.list_models()
    assert len(r["models"]) == 19
    assert graph_fakes.calls(tmp_path)[-1].endswith("--json")


def test_no_binary_means_an_empty_catalog_that_says_why(monkeypatch, tmp_path):
    from dx_app.core import graph_cli
    monkeypatch.setattr(graph_cli, "_search_dirs", lambda: [tmp_path])
    cat = graph_catalog.catalog()
    assert cat["available"] is False and cat["models"] == [] and cat["error"] == "graph_binary_missing"


def test_missing_models_carry_a_download_link(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    link = {"name": "Ultralytics YOLO26-n", "dxnn_url": "https://example.invalid/a.dxnn", "json_url": None}
    monkeypatch.setattr(graph_catalog, "_download_index", lambda: {"yolo26-n_640x640_pre-optimized": link,
                                                                   "fastdepth_224x224": link})
    monkeypatch.setattr(graph_catalog, "examples", lambda: [])
    m = _by_name(graph_catalog.catalog()["models"])
    assert m["yolo26-n_640x640_pre-optimized"]["download"] == link
    assert m["fastdepth_224x224"]["download"] is None, "an installed model offers no download"


def test_examples_are_the_sample_graphs(tmp_path, monkeypatch):
    d = tmp_path / "src" / "cpp_example" / "multi_model_graph"
    d.mkdir(parents=True)
    g = {"version": 1, "name": "person-attributes", "nodes": [
        {"id": "cam", "type": "source", "uri": "sample/img/sample_people.jpg"},
        {"id": "od", "model": "yolov8-n_640x640"}, {"id": "attr", "model": "deepmar_resnet50_224x224"}],
        "edges": [{"from": "cam", "to": "od"}, {"from": "od", "to": "attr", "roi": {"classes": ["person"]}}]}
    (d / "cascade_od_attr.json").write_text(json.dumps(g))
    (d / "broken.json").write_text("{not json")
    monkeypatch.setattr(config, "DX_APP_ROOT", tmp_path)
    (ex,) = graph_catalog.examples()
    assert ex["id"] == "cascade_od_attr" and ex["name"] == "person-attributes"
    assert ex["models"] == ["deepmar_resnet50_224x224", "yolov8-n_640x640"]
    assert (ex["nodes"], ex["edges"]) == (3, 2) and ex["graph"] == g


def test_the_installed_dx_app_ships_nineteen_examples():
    d = config.DX_APP_ROOT / "src" / "cpp_example" / "multi_model_graph"
    if not d.is_dir():
        pytest.skip("dx_app is not checked out next to the studio")
    names = {e["name"] for e in graph_catalog.examples()}
    assert len(names) == 19 and "person-attributes" in names and "zone-intrusion" in names


def test_the_listing_maps_names_and_aliases_to_their_files():
    for r in (graph_catalog.parse_list_models_text(graph_fakes.fixture("list_models.txt")),
              graph_catalog.parse_list_models_json(graph_fakes.fixture("list_models.json"))):
        assert r["files"]["fastdepth_224x224"] == "fastdepth_224x224.dxnn"
        assert r["files"]["deit_base384_distilled"] == "deit-b_384x384_distilled.dxnn"
        assert len(r["files"]) == 20


def test_a_model_file_replaced_in_place_refreshes_the_listing(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    mdir = tmp_path / "models"
    f = mdir / "fastdepth_224x224.dxnn"
    f.write_bytes(b"")
    graph_catalog.list_models()
    n = len(graph_fakes.calls(tmp_path))
    folder = mdir.stat()
    f.write_bytes(b"DXNN" * 100)                            # a download finished into the existing file
    later = time.time() + 5
    os.utime(f, (later, later))
    os.utime(mdir, ns=(folder.st_atime_ns, folder.st_mtime_ns))
    graph_catalog.list_models()
    assert len(graph_fakes.calls(tmp_path)) == n + 1


def test_an_async_only_build_lists_models(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI, variants=("async",))
    assert len(graph_catalog.list_models()["models"]) == 19
    assert graph_catalog.catalog()["available"] is True


# Phase 2: logic blocks, templates with thumbnails, the upload limit.

def test_the_catalog_carries_logic_blocks_and_the_upload_limit(tmp_path, monkeypatch):
    from dx_app.core import graph_ops, graph_run
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.P2_CLI)
    graph_ops._cache.update(key=None, value=None)
    monkeypatch.setattr(graph_catalog, "examples", lambda: [])
    cat = graph_catalog.catalog()
    assert [o["op"] for o in cat["logic_ops"]][:3] == ["filter", "zone", "line"] and cat["logic_error"] is None
    assert cat["capabilities"]["list_ops"] is True and cat["capabilities"]["loop"] is True
    assert cat["limits"] == {"uploads_total_b64": graph_run.MAX_UPLOADS_TOTAL_B64}


def test_a_build_without_logic_blocks_says_so(tmp_path, monkeypatch):
    from dx_app.core import graph_ops
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.JSON_CLI)
    graph_ops._cache.update(key=None, value=None)
    monkeypatch.setattr(graph_catalog, "examples", lambda: [])
    cat = graph_catalog.catalog()
    assert cat["logic_ops"] == [] and cat["logic_error"] == "list_ops_unsupported"


def test_examples_with_logic_nodes_are_templates_with_a_thumbnail(tmp_path, monkeypatch):
    d = graph_fakes.install_examples(tmp_path)
    (d / "plain.json").write_text(json.dumps({"version": 1, "nodes": [{"id": "cam", "type": "source", "uri": "a"}],
                                              "edges": []}))
    (d / "line_counting.jpg").write_bytes(b"\xff\xd8")
    thumbs = tmp_path / "studio_thumbs"
    thumbs.mkdir()
    (thumbs / "loitering_dwell.jpg").write_bytes(b"\xff\xd8")
    monkeypatch.setattr(config, "DX_APP_ROOT", tmp_path)
    monkeypatch.setattr(graph_catalog, "THUMBS_DIR", thumbs)
    ex = {e["id"]: e for e in graph_catalog.examples()}
    assert ex["plain"]["logic"] is False and ex["plain"]["thumb"] is None
    zone = ex["zone_intrusion"]
    assert zone["logic"] is True and zone["ops"] == ["condition", "filter", "zone"] and zone["thumb"] is None
    assert ex["line_counting"]["thumb"] == "/file/src/cpp_example/multi_model_graph/line_counting.jpg"
    assert ex["loitering_dwell"]["thumb"] == "/static/img/graph-examples/loitering_dwell.jpg"
    assert ex["ppe_zone_check"]["models"] == ["deepmar_resnet18_224x224", "yolov8-n_640x640"]
    assert sum(e["logic"] for e in ex.values()) == 6
