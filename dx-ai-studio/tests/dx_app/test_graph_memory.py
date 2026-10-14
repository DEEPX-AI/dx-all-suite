"""graph_memory: parse_model and dxrt-cli output (recorded) turned into a per-node NPU memory estimate."""
from __future__ import annotations

import json
import shutil
import stat
import subprocess

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
    monkeypatch.setattr(graph_memory, "runtime_python", lambda: None)
    fix = graph_fakes.FIX / "dxrt_cli_status.txt"
    monkeypatch.setattr(graph_memory, "dxrt_cli_binary", lambda: _script(tmp_path, "dxrt-cli", f'cat "{fix}"'))
    d = graph_memory.device_memory()
    assert (d["source"], d["total_bytes"], d["free_bytes"]) == ("dxrt_cli", int(3.92 * 1024 ** 3), int(3.92 * 1024 ** 3))



# The Studio's own venv has no dx_engine, so get_hw() is mocked there; DeviceStatus is read in the DX-RT runtime venv.
REAL_USED, REAL_FREE = 3668037632, 543043584        # one DX-M1 on 2026-10-14 (used + free = 3.92 GiB)


def _runtime(tmp_path, monkeypatch, answer, dxrt_cli=True):
    """get_hw() mocked, a runtime python found, the probe answered by `answer` (text, or an exception to raise)."""
    import shared.hardware as hw
    monkeypatch.setattr(hw, "get_hw", lambda: {"mock": True, "npus": []})
    monkeypatch.setattr(graph_memory, "runtime_python", lambda: "/fake/venv-dx-runtime/bin/python3")
    seen = []

    def runner(python):
        seen.append(python)
        if isinstance(answer, Exception):
            raise answer
        return answer
    monkeypatch.setattr(graph_memory, "_probe_runner", runner)
    fix = graph_fakes.FIX / "dxrt_cli_status.txt"
    monkeypatch.setattr(graph_memory, "dxrt_cli_binary",
                        lambda: _script(tmp_path, "dxrt-cli", f'cat "{fix}"') if dxrt_cli else None)
    return seen


def _devices(*rows):
    return json.dumps([{"id": i, "valid": v, "used": u, "free": f} for i, (v, u, f) in enumerate(rows)]) + "\n"


def test_device_memory_reads_device_status_in_the_runtime_venv(tmp_path, monkeypatch):
    seen = _runtime(tmp_path, monkeypatch, _devices((True, REAL_USED, REAL_FREE)))
    assert graph_memory.device_memory() == {"total_bytes": int(3.92 * 1024 ** 3), "used_bytes": REAL_USED,
                                            "free_bytes": REAL_FREE, "source": "device_status"}
    assert seen == ["/fake/venv-dx-runtime/bin/python3"]


def test_the_device_with_the_least_free_memory_is_the_budget_and_stale_ones_are_skipped(tmp_path, monkeypatch):
    _runtime(tmp_path, monkeypatch, _devices((True, 1000, 3000), (False, 3900, 100), (True, 2500, 1500)))
    d = graph_memory.device_memory()
    assert (d["used_bytes"], d["free_bytes"], d["source"]) == (2500, 1500, "device_status")


def test_without_dxrt_cli_the_total_is_used_plus_free(tmp_path, monkeypatch):
    _runtime(tmp_path, monkeypatch, _devices((True, REAL_USED, REAL_FREE)), dxrt_cli=False)
    assert graph_memory.device_memory()["total_bytes"] == REAL_USED + REAL_FREE


@pytest.mark.parametrize("answer", [RuntimeError("No module named 'dx_engine'"),
                                    subprocess.TimeoutExpired("python", 10), "not json\n", "[]\n",
                                    _devices((False, 1, 2))])
def test_a_failed_runtime_query_falls_back_to_the_whole_device(tmp_path, monkeypatch, answer):
    _runtime(tmp_path, monkeypatch, answer)
    d = graph_memory.device_memory()
    assert (d["source"], d["used_bytes"], d["free_bytes"]) == ("dxrt_cli", None, int(3.92 * 1024 ** 3))


def test_the_runtime_answer_is_cached_for_a_few_seconds(tmp_path, monkeypatch):
    seen = _runtime(tmp_path, monkeypatch, _devices((True, REAL_USED, REAL_FREE)))
    graph_memory.device_memory()
    graph_memory.device_memory()
    assert len(seen) == 1
    graph_memory._device_cache["at"] -= 10
    graph_memory.device_memory()
    assert len(seen) == 2


def test_the_runtime_python_is_the_dx_runtime_venv(tmp_path, monkeypatch):
    import shared.runtime as rt
    monkeypatch.setattr(rt, "runtime_venv_roots", lambda: [tmp_path / "none", tmp_path / "venv-dx-runtime"])
    assert graph_memory.runtime_python() is None
    py = tmp_path / "venv-dx-runtime" / "bin" / "python3"
    py.parent.mkdir(parents=True)
    py.write_text("")
    assert graph_memory.runtime_python() == str(py)


def test_the_probe_script_compiles_and_names_the_device_status_calls():
    compile(graph_memory.DEVICE_PROBE, "probe", "exec")
    for call in ("get_device_count", "get_current_status", "get_memory_used", "get_memory_free", "is_valid"):
        assert call in graph_memory.DEVICE_PROBE

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
