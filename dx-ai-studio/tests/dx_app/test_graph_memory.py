"""graph_memory: parse_model and dxrt-cli output (recorded) turned into a per-node NPU memory estimate."""
from __future__ import annotations

import shutil
import stat

import pytest

from dx_app.core import graph_memory
from tests.dx_app import graph_fakes

FASTDEPTH = {"total_bytes": 118262080, "buffers_bytes": 116551680, "pool": 6}
YOLO26N = {"total_bytes": 123528064, "buffers_bytes": 120109056, "pool": 6}


@pytest.fixture(autouse=True)
def _fresh_caches():
    for c in (graph_memory._hash_cache, graph_memory._mem_cache):
        c.clear()
    graph_memory._device_cache.update(at=0.0, value=None)
    yield


def _script(tmp_path, name, body):
    p = tmp_path / name
    p.write_text(f'#!/usr/bin/env bash\necho "$@" >> "{tmp_path}/{name}.calls"\n{body}\n', encoding="utf-8")
    p.chmod(p.stat().st_mode | stat.S_IXUSR)
    return str(p)


def test_parse_model_memory_lines_are_read_in_bytes():
    assert graph_memory.parse_model_text(graph_fakes.fixture("parse_model_fastdepth.txt")) == FASTDEPTH
    assert graph_memory.parse_model_text(graph_fakes.fixture("parse_model_yolo26n.txt")) == YOLO26N


def test_an_unreadable_model_has_no_figure():
    with pytest.raises(ValueError):
        graph_memory.parse_model_text(graph_fakes.fixture("parse_model_invalid.txt"))


def test_fewer_buffers_shrink_only_the_buffer_part():
    assert graph_memory.engine_bytes(FASTDEPTH) == 118262080
    # (Total - Buffers) + Buffers * 2 / 6 = 1,710,400 + 38,850,560
    assert graph_memory.engine_bytes(FASTDEPTH, 2) == 40560960


def test_device_size_from_dxrt_cli():
    assert graph_memory.parse_dxrt_status(graph_fakes.fixture("dxrt_cli_status.txt")) == int(3.92 * 1024 ** 3)
    assert graph_memory.parse_dxrt_status("no memory line") is None


def test_model_memory_runs_parse_model_once_per_file_content(tmp_path, monkeypatch):
    fix = graph_fakes.FIX / "parse_model_fastdepth.txt"
    monkeypatch.setattr(graph_memory, "parse_model_binary", lambda: _script(tmp_path, "parse_model", f'cat "{fix}"'))
    a = tmp_path / "a.dxnn"
    a.write_bytes(b"DXNN" + b"\0" * 64)
    assert graph_memory.model_memory(a) == FASTDEPTH
    b = tmp_path / "b.dxnn"
    shutil.copy(a, b)
    assert graph_memory.model_memory(b) == FASTDEPTH
    assert len((tmp_path / "parse_model.calls").read_text().splitlines()) == 1, "same content, same figure"
    (tmp_path / "empty.dxnn").write_bytes(b"")
    assert graph_memory.model_memory(tmp_path / "empty.dxnn") is None
    assert graph_memory.model_memory(tmp_path / "missing.dxnn") is None


def test_device_memory_prefers_device_status(monkeypatch):
    import shared.hardware as hw
    monkeypatch.setattr(hw, "get_hw", lambda: {"mock": False, "npus": [{"dram_total_mb": 4000.0, "dram_used_mb": 1000.0}]})
    d = graph_memory.device_memory()
    assert d == {"total_bytes": 4000 * graph_memory.MB, "used_bytes": 1000 * graph_memory.MB,
                 "free_bytes": 3000 * graph_memory.MB, "source": "device_status"}


def test_device_memory_falls_back_to_dxrt_cli(tmp_path, monkeypatch):
    import shared.hardware as hw
    monkeypatch.setattr(hw, "get_hw", lambda: {"mock": True, "npus": [{"dram_total_mb": 4000.0}]})
    fix = graph_fakes.FIX / "dxrt_cli_status.txt"
    monkeypatch.setattr(graph_memory, "dxrt_cli_binary", lambda: _script(tmp_path, "dxrt-cli", f'cat "{fix}"'))
    d = graph_memory.device_memory()
    assert (d["source"], d["total_bytes"], d["free_bytes"]) == ("dxrt_cli", int(3.92 * 1024 ** 3), int(3.92 * 1024 ** 3))


def _estimate(monkeypatch, graph, free):
    sizes = {"yolo26-n_640x640": YOLO26N, "fastdepth_224x224": FASTDEPTH}
    monkeypatch.setattr(graph_memory, "model_memory", lambda p: sizes.get(p.stem))
    monkeypatch.setattr(graph_memory, "device_memory", lambda: {"total_bytes": free, "used_bytes": 0,
                                                                 "free_bytes": free, "source": "device_status"})
    return graph_memory.estimate(graph)


def _g(od_engine=None, od2_engine=None, depth_engine=None):
    def node(i, m, e):
        n = {"id": i, "model": m}
        if e is not None:
            n["engine"] = e
        return n
    return {"nodes": [{"id": "cam", "type": "source", "uri": "x.jpg"}, node("od", "yolo26-n_640x640", od_engine),
                      node("od2", "yolo26-n_640x640", od2_engine), node("depth", "fastdepth_224x224", depth_engine),
                      {"id": "ghost", "model": "not_installed_224x224"}], "edges": []}


def test_every_node_holds_its_own_engine_by_default(monkeypatch):
    r = _estimate(monkeypatch, _g(), free=300 * graph_memory.MB)
    assert r["total_bytes"] == 2 * YOLO26N["total_bytes"] + FASTDEPTH["total_bytes"]
    assert r["nodes"]["od"]["bytes"] == r["nodes"]["od2"]["bytes"] == YOLO26N["total_bytes"]
    assert r["unknown_models"] == ["not_installed_224x224"]
    assert r["over_budget"] is True
    kinds = [(s["kind"], s["model"]) for s in r["suggestions"]]
    assert kinds[0] == ("share", "yolo26-n_640x640"), "sharing saves the most"
    assert r["suggestions"][0]["saves_bytes"] == YOLO26N["total_bytes"]
    assert ("buffers", "fastdepth_224x224") in kinds


def test_shared_engines_count_once_and_buffers_shrink_the_sum(monkeypatch):
    r = _estimate(monkeypatch, _g({"share": True}, {"share": True, "buffers": 2}, {"buffers": 2}),
                  free=4000 * graph_memory.MB)
    assert r["nodes"]["od"]["bytes"] == YOLO26N["total_bytes"], "the larger buffer count of the group wins"
    assert r["nodes"]["od2"] == {"model": "yolo26-n_640x640", "bytes": 0, "shared_with": ["od"], "buffers": 6}
    assert r["nodes"]["depth"]["bytes"] == 40560960
    assert r["total_bytes"] == YOLO26N["total_bytes"] + 40560960
    assert r["over_budget"] is False
    assert not [s for s in r["suggestions"] if s["kind"] == "share"]
