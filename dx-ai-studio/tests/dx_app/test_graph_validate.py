"""graph_validate: dx_app's --check output (recorded) pinned to canvas node and edge ids."""
from __future__ import annotations

import json

import pytest

from dx_app.core import graph_validate
from tests.dx_app import graph_fakes

CHECK = "/tmp/dx-graph-check/check.json"      # the path the recorded errors name


def _graph(*ids):
    return {"version": 1, "name": "g", "nodes": [{"id": i} for i in ids], "edges": []}


def _text(name, graph):
    return graph_validate.parse_check_text("", graph_fakes.fixture(name), CHECK, graph)


def test_an_edge_error_pins_the_edge():
    r = _text("check_err_edge.txt", _graph("cam", "od", "attr", "depth"))
    assert r["ok"] is False
    assert r["errors"] == [{"code": "GRAPH_EDGE", "where": 'edge "od"->"depth"', "what": '"depth" requires a full frame',
                            "how": 'remove "roi" from this edge', "node": None, "edge": "od->depth"}]


def test_a_node_error_pins_the_node():
    (e,) = _text("check_err_unknown_model.txt", _graph("cam", "od"))["errors"]
    assert (e["code"], e["node"], e["edge"]) == ("MODEL_UNKNOWN", "od", None)
    assert e["how"] == "run --list-models, or see docs/graph_models.md"
    (e,) = _text("check_err_orphan.txt", _graph("cam", "od", "lost"))["errors"]
    assert (e["code"], e["node"]) == ("GRAPH_ORPHAN", "lost")


def test_a_schema_error_names_the_graph_not_the_temporary_file():
    (e,) = _text("check_err_engine_key.txt", _graph("cam", "m"))["errors"]
    assert e["where"] == 'graph node[1] "m"' and e["node"] == "m"
    (e,) = _text("check_err_roi_typo.txt", _graph("cam", "od", "r"))["errors"]
    assert e["edge"] == "od->r" and 'did you mean "classes"' in e["how"]


def test_a_node_named_only_by_its_index_is_found_in_the_graph():
    assert graph_validate.pin('graph node[2] (model "x")', _graph("cam", "od", "cls")) == ("cls", None)
    assert graph_validate.pin('graph "person-reid"', _graph("cam")) == (None, None)


def test_a_valid_graph_lists_its_models_and_their_files():
    r = graph_validate.parse_check_text(graph_fakes.fixture("check_ok_cascade_od_attr.txt"), "", CHECK, _graph())
    assert r["ok"] is True and r["errors"] == [] and r["missing"] == []
    assert [(m["node"], m["model"], m["present"], m["file"]) for m in r["models"]] == [
        ("cam", None, None, None), ("od", "yolov8-n_640x640", True, "v9"),
        ("attr", "deepmar_resnet50_224x224", True, "v8")]


def test_a_missing_model_file_is_listed_but_is_not_an_error():
    r = graph_validate.parse_check_text(graph_fakes.fixture("check_ok_missing.txt"), "", CHECK, _graph())
    assert r["ok"] is True and r["missing"] == ["p"]
    assert {m["node"]: m["file"] for m in r["models"]}["od"] == "invalid"


def test_the_json_check_reads_the_same():
    """The JSON rows list model nodes only (no source row) with `state` and `container`."""
    ok = graph_validate.parse_check_json(graph_fakes.fixture("check_ok.json"), _graph())
    text = graph_validate.parse_check_text(graph_fakes.fixture("check_ok_cascade_od_attr.txt"), "", CHECK, _graph())
    pick = lambda rows: [(m["node"], m["model"], m["present"], m["file"]) for m in rows if m["model"]]
    assert pick(ok["models"]) == pick(text["models"]) and ok["ok"]
    err = graph_validate.parse_check_json(graph_fakes.fixture("check_err.json"), _graph())
    assert err["errors"][0]["edge"] == "od->depth" and err["ok"] is False


def test_a_file_that_cannot_load_is_an_error_on_its_node_in_json():
    r = graph_validate.parse_check_json(graph_fakes.fixture("check_err_model_load.json"), _graph("cam", "od", "p"), CHECK)
    assert (r["errors"][0]["code"], r["errors"][0]["node"]) == ("MODEL_LOAD", "od")
    assert r["missing"] == ["p"] and r["ok"] is False
    assert {m["node"]: m["present"] for m in r["models"]} == {"od": False, "p": False}


def test_validate_runs_check_and_drops_the_engine_key_this_build_does_not_know(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    g = {"version": 1, "name": "g", "nodes": [{"id": "cam", "type": "source", "uri": "x.jpg"},
                                              {"id": "od", "model": "yolov8-n_640x640", "engine": {"buffers": 2}}],
         "edges": [{"from": "cam", "to": "od"}]}
    r = graph_validate.validate(g)
    assert r["ok"] is True and r["engine_ignored"] is True and r["available"] is True
    assert not list(tmp_path.glob("check*.json")), "the temporary graph is removed"
    assert g["nodes"][1]["engine"] == {"buffers": 2}, "the caller's graph is not changed"


def test_validate_pins_the_cli_errors(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    r = graph_validate.validate(_graph("cam", "od", "depth"))
    assert r["ok"] is False and r["errors"][0]["edge"] == "od->depth"


def test_validate_with_the_json_cli(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.JSON_CLI)
    assert graph_validate.validate(_graph("cam", "od"))["ok"] is True
    assert graph_fakes.calls(tmp_path)[-1].endswith("--json")


def test_validate_without_a_binary_says_how_to_get_one(monkeypatch, tmp_path):
    from dx_app.core import graph_cli
    monkeypatch.setattr(graph_cli, "_search_dirs", lambda: [tmp_path])
    r = graph_validate.validate(_graph("cam"))
    assert r["available"] is False and r["errors"][0]["code"] == "GRAPH_BINARY_MISSING"


def test_engine_graph_keeps_the_key_only_when_the_build_supports_it():
    g = {"nodes": [{"id": "od", "model": "m", "engine": {"share": True}}], "edges": []}
    assert graph_validate.engine_graph(g, {"engine_key": True}) == g
    assert "engine" not in graph_validate.engine_graph(g, {"engine_key": False})["nodes"][0]
    assert g["nodes"][0]["engine"] == {"share": True}, "the input is not changed"


# Review fixes: unreadable JSON is a pinned Studio error, every unusable file state is surfaced, engines are kept.
@pytest.mark.parametrize("text", ['[]', '"ok"', '{"ok": false, "errors": ["boom"]}', '{"ok": true, "models": [3]}'])
def test_json_that_is_not_the_documented_shape_is_unreadable(text):
    with pytest.raises(ValueError):
        graph_validate.parse_check_json(text, _graph())


def test_validate_turns_unreadable_json_into_a_check_error(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.JSON_CLI.replace('cat "$FIX/check_ok.json"', "echo '[]'"))
    r = graph_validate.validate(_graph("cam", "od"))
    assert r["ok"] is False and r["errors"][0]["code"] == "CHECK_UNREADABLE" and r["available"] is True


def test_an_edge_without_ends_is_pinned_from_where():
    text = json.dumps({"ok": False, "errors": [{"code": "X", "where": 'node "od"', "what": "w", "how": "",
                                               "node": None, "edge": {"from": None, "to": None}}], "models": []})
    (e,) = graph_validate.parse_check_json(text, _graph("od"))["errors"]
    assert (e["node"], e["edge"]) == ("od", None)


def test_every_unusable_model_file_is_surfaced_with_its_state_and_engine():
    rows = [{"node": n, "model": "m", "file": "m.dxnn", "container": None, "state": st,
             "engine": {"buffers": 2, "share": True, "shared_with": "a" if n != "a" else None}}
            for n, st in (("a", "present"), ("b", "invalid"), ("c", "unloadable"), ("d", "unknown"), ("e", "missing"))]
    r = graph_validate.parse_check_json(json.dumps({"ok": True, "errors": [], "models": rows}), _graph())
    assert r["missing"] == ["e"]
    assert r["unusable"] == {"b": "invalid", "c": "unloadable", "d": "unknown"}
    by = {m["node"]: m for m in r["models"]}
    assert by["b"]["state"] == "invalid" and by["c"]["engine"]["shared_with"] == "a"


def test_the_text_table_names_an_invalid_file_too():
    r = graph_validate.parse_check_text(graph_fakes.fixture("check_ok_missing.txt"), "", CHECK, _graph())
    assert r["unusable"] == {"od": "invalid"} and r["missing"] == ["p"]
    assert {m["node"]: m["state"] for m in r["models"]} == {"cam": None, "od": "invalid", "p": "missing"}
