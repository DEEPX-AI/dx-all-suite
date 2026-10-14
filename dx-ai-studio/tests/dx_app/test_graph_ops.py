"""graph_ops: the logic blocks of `--list-ops --json` (recorded from the dx_app Phase 2 plan's catalog)."""
from __future__ import annotations

import json

import pytest

from dx_app.core import graph_ops
from tests.dx_app import graph_fakes


@pytest.fixture(autouse=True)
def _fresh_cache():
    graph_ops._cache.update(key=None, value=None)
    yield
    graph_ops._cache.update(key=None, value=None)


def _ops():
    return {o["op"]: o for o in graph_ops.parse_list_ops(graph_fakes.fixture("list_ops.json"))}


def test_the_eight_logic_ops_are_kept_in_order_and_the_cpu_ops_left_out():
    ops = graph_ops.parse_list_ops(graph_fakes.fixture("list_ops.json"))
    assert [o["op"] for o in ops] == ["filter", "zone", "line", "count", "dwell", "condition", "gallery", "user"]


def test_inputs_outputs_tracking_events_and_numbers_are_dx_app_s():
    ops = _ops()
    assert ops["zone"]["inputs"] == {"min": 1, "max": 1, "accepts": [
        {"shape": "boxes", "per_crop": False}, {"shape": "obboxes", "per_crop": False},
        {"shape": "instances", "per_crop": False}]}
    assert ops["zone"]["output"] == "same" and ops["zone"]["events"] == ["enter", "exit"]
    assert ops["line"]["tracking"] is True and ops["line"]["output"] == "records"
    assert ops["line"]["numbers"] == ["in", "out", "total"]
    assert ops["count"]["inputs"]["max"] == 8
    assert {"shape": "scores", "per_crop": True} in ops["condition"]["inputs"]["accepts"]
    assert ops["condition"]["events"] == ["<event>"]


def test_params_keep_type_range_default_choices_and_help():
    zone = {p["name"]: p for p in _ops()["zone"]["params"]}
    assert zone["polygon"]["type"] == "polygon" and zone["polygon"]["required"] is True
    assert zone["polygon"]["min_points"] == 3 and "fraction 0..1" in zone["polygon"]["help"]
    assert (zone["mode"]["type"], zone["mode"]["default"], zone["mode"]["choices"]) == ("choice", "inside",
                                                                                       ["inside", "outside"])
    dwell = {p["name"]: p for p in _ops()["dwell"]["params"]}
    assert (dwell["threshold_s"]["min"], dwell["threshold_s"]["min_exclusive"], dwell["threshold_s"]["default"]) == (0, True, 10)
    assert "max" not in dwell["threshold_s"]
    line = {p["name"]: p for p in _ops()["line"]["params"]}
    assert line["line"] == {"name": "line", "type": "line", "required": True, "help": line["line"]["help"], "points": 2}
    user = {p["name"]: p for p in _ops()["user"]["params"]}
    assert user["input"]["required"] is True and "default" not in user["input"] and "boxes" in user["input"]["choices"]
    flt = {p["name"]: p for p in _ops()["filter"]["params"]}
    assert flt["classes"] == {"name": "classes", "type": "text_list", "required": False, "help": flt["classes"]["help"],
                              "default": []}


def test_odd_entries_are_read_safely():
    text = json.dumps({"ops": [
        {"op": "zone", "inputs": {"min": "1", "accepts": [{"shape": "boxes"}, {"shape": "Bad Shape"}, "x"]},
         "output": "sideways", "tracking": "yes",
         "params": [{"name": "polygon", "type": "polygon", "min_points": 1}, {"name": "bad name", "type": "number"},
                    {"name": "x", "type": "matrix", "default": 3}, {"name": "n", "type": "number", "default": "5"}]},
        {"op": "Bad-Op"}, "not an op", {"inputs": {}}, {"op": "headpose", "type": "cpu"}]})
    (zone,) = graph_ops.parse_list_ops(text)
    assert zone["inputs"] == {"min": 1, "max": 1, "accepts": [{"shape": "boxes", "per_crop": False}]}
    assert zone["output"] == "records" and zone["tracking"] is False
    assert [p["name"] for p in zone["params"]] == ["polygon", "x", "n"]
    assert zone["params"][0]["min_points"] == 3
    assert zone["params"][1]["type"] == "text" and "default" not in zone["params"][1], "a default of the wrong type is dropped"
    assert "default" not in zone["params"][2]
    with pytest.raises(ValueError):
        graph_ops.parse_list_ops('{"ops": 3}')


def test_list_ops_asks_a_build_that_has_it_once(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.P2_CLI)
    r = graph_ops.list_ops()
    assert r["error"] is None and len(r["ops"]) == 8
    n = len(graph_fakes.calls(tmp_path))
    graph_ops.list_ops()
    assert len(graph_fakes.calls(tmp_path)) == n, "cached"
    assert "--list-ops --json" in graph_fakes.calls(tmp_path)[-1]


def test_a_build_without_list_ops_offers_no_logic_and_says_why(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.JSON_CLI)
    assert graph_ops.list_ops() == {"ops": [], "error": "list_ops_unsupported"}
    assert not any("--list-ops" in c for c in graph_fakes.calls(tmp_path))


def test_unreadable_output_is_reported(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.P2_CLI.replace('cat "$FIX/list_ops.json"', 'echo "{oops"'))
    r = graph_ops.list_ops()
    assert r["ops"] == [] and r["error"].startswith("list_ops_unreadable")
