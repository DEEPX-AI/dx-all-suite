"""Supported hardware per model: DX-M1, DX-H1 Quattro (= 4 × M1, same rule as M1) and DX-M1M.

Single source is dx-modelzoo YAML `target_hardware` (DXM1-1775, next release):
    target_hardware:
      m1:  {buffer_count: 6}
      m1m: {buffer_count: 1}
Until a YAML carries it, DX-M1M is "pending" — never guessed as supported. No adapter hardcodes ["dx_m1"].
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

from dx_modelzoo.metadata.devices import processor_info

STUDIO = Path(__file__).resolve().parents[2]


def test_no_field_means_m1_and_quattro_with_m1m_pending():
    p = processor_info(None)
    assert p["supported_devices"] == ["dx_m1", "dx_h1_quattro"]
    assert p["m1m"] == {"status": "pending", "reason": None}
    assert p["status"] == "metadata_pending"


def test_m1m_key_means_supported_on_all_three():
    p = processor_info({"m1": {"buffer_count": 6}, "m1m": {"buffer_count": 1}})
    assert p["supported_devices"] == ["dx_m1", "dx_m1m", "dx_h1_quattro"]
    assert p["m1m"]["status"] == "supported" and p["status"] == "provided"


def test_field_without_m1m_means_not_supported_on_m1m():
    p = processor_info({"m1": {"buffer_count": 1}})
    assert p["supported_devices"] == ["dx_m1", "dx_h1_quattro"]
    assert p["m1m"] == {"status": "unsupported", "reason": None}


def test_explicit_unsupported_keeps_the_reason():
    p = processor_info({"m1": {}, "m1m": {"supported": False, "reason": "NPU memory"}})
    assert "dx_m1m" not in p["supported_devices"]
    assert p["m1m"] == {"status": "unsupported", "reason": "NPU memory"}


@pytest.mark.parametrize("legacy", [{"supported_devices": ["dx_m1"], "status": "provided"},
                                    {"supported_devices": [], "status": "metadata_pending"}, {}])
def test_legacy_processor_is_upgraded(legacy):
    from dx_modelzoo.metadata.devices import upgrade_processor
    p = upgrade_processor(legacy)
    assert p["supported_devices"] == ["dx_m1", "dx_h1_quattro"] and p["m1m"]["status"] == "pending"


def test_upgrade_keeps_a_target_hardware_result():
    from dx_modelzoo.metadata.devices import upgrade_processor
    done = processor_info({"m1": {}, "m1m": {}})
    assert upgrade_processor(done) == done


def test_yaml_parser_reads_target_hardware(tmp_path):
    from dx_modelzoo.metadata._yaml_parser import parse_modelzoo_yaml_file
    f = tmp_path / "realesrgan-x4_192x192.yaml"
    f.write_text("name: realesrgan-x4_192x192\ntask: super_resolution\n"
                 "target_hardware:\n  m1:\n    buffer_count: 1\n  m1m:\n    supported: false\n"
                 "    reason: \"NPU memory\"\n"
                 "profiles:\n  q-lite:\n    runtime:\n      buffer_count: 1\n")
    (fields,) = parse_modelzoo_yaml_file(f).values()
    assert fields["processor.target_hardware"] == {"m1": {"buffer_count": 1},
                                                  "m1m": {"supported": False, "reason": "NPU memory"}}


def test_yaml_parser_without_the_field_adds_nothing(tmp_path):
    from dx_modelzoo.metadata._yaml_parser import parse_modelzoo_yaml_file
    f = tmp_path / "x.yaml"
    f.write_text("name: x\ntask: classification\nprofiles:\n  q-lite:\n    runtime:\n      device: 0\n")
    (fields,) = parse_modelzoo_yaml_file(f).values()
    assert not any(k.startswith("processor.") for k in fields)


def test_adapters_have_no_device_hardcode():
    tree = ast.parse((STUDIO / "dx_modelzoo/metadata/adapters.py").read_text(encoding="utf-8"))
    consts = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant)]
    assert "dx_m1" not in consts
    assert "processor.supported_devices" not in consts


def test_merge_builds_processor_from_target_hardware():
    from dx_modelzoo.metadata.merge import merge_adapter_results
    runtime = {"adapter": "local_runtime", "ok": True, "models": {
        "a": {"display.name": "A", "display.task": "classification"},
        "b": {"display.name": "B", "display.task": "classification"}}, "warnings": [], "errors": []}
    repo = {"adapter": "local_modelzoo_repo", "ok": True, "models": {
        "a": {"processor.target_hardware": {"m1": {}, "m1m": {"buffer_count": 1}}}}, "warnings": [], "errors": []}
    out = {m["id"]: m for m in merge_adapter_results([runtime, repo])["models"]}
    assert out["a"]["processor"]["supported_devices"] == ["dx_m1", "dx_m1m", "dx_h1_quattro"]
    assert out["b"]["processor"]["m1m"]["status"] == "pending"


def test_catalog_upgrades_the_committed_generated_catalog():
    """The committed generated_catalog.json still says ["dx_m1"]; the served catalog carries the rule's shape."""
    from dx_modelzoo.core import catalog
    models = catalog.get_catalog()["models"]
    assert models
    for m in models:
        assert m["processor"]["supported_devices"][:1] == ["dx_m1"], m["id"]
        assert "dx_h1_quattro" in m["processor"]["supported_devices"]
        assert m["processor"]["m1m"]["status"] in ("pending", "supported", "unsupported")
