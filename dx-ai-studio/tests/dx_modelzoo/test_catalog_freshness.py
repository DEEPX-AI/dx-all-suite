"""The screen that shows the catalog must say when the catalog was generated.

`generated_catalog.json` is a sync output and goes stale when it falls behind upstream; models
added meanwhile can ship without legal data, and nothing says so unless the age is visible.

The value is in the file (`generated_at`); these tests check the path that carries it to the list
view, which is where "is this whole list stale?" gets asked.

When to sync again is an operations decision and is not decided here. This contract only makes
staleness **visible**.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _catalog():
    sys.path.insert(0, str(ROOT / "dx_modelzoo"))
    from core import catalog as C

    return C.get_catalog()


def test_the_catalogue_says_when_it_was_generated():
    cat = _catalog()
    assert cat.get("generated_at"), (
        "카탈로그가 언제 만들어졌는지 말하지 않는다 — 낡아도 알 수 없다"
    )


def test_it_says_which_source_it_came_from():
    """public and internal give different data; without knowing which, the numbers cannot be read."""
    cat = _catalog()
    assert cat.get("source_profile") in ("public", "internal", "local"), cat.get("source_profile")


def test_the_value_matches_the_file_it_came_from():
    raw = json.loads((ROOT / "dx_modelzoo" / "data" / "generated_catalog.json").read_text())
    cat = _catalog()
    assert cat["generated_at"] == raw.get("generated_at"), (
        "화면이 말하는 날짜가 파일과 다르다"
    )


def test_the_api_carries_it_to_the_browser():
    """Putting the field in get_catalog() is not enough: the handler picks the fields it sends.

    Source-string checks can all pass while nothing reaches the screen, so this one goes
    through the real API.
    """
    import json
    import urllib.request

    from tests.server_helpers import start_module_server

    server, port = start_module_server("dx_modelzoo")
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/api/catalog", timeout=20) as r:
            body = json.loads(r.read().decode())
    finally:
        server.shutdown()
    assert body.get("generated_at"), "API 응답에 생성 시각이 없다"
    assert body.get("source_profile"), "API 응답에 소스가 없다"


def test_the_list_screen_shows_it():
    """The list view is where 'is the whole list stale?' gets asked, so it shows the date too."""
    src = (ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js").read_text(encoding="utf-8")
    assert "generated_at" in src, "목록 화면이 생성 시각을 쓰지 않는다"


def test_cards_use_the_curated_display_name():
    """model_catalog.json names are the id title-cased ('Regnety16Gf', '3Ddfa V2 Mobilnet0 5 120X120');
    the generated catalog's display.name is the curated one and must win."""
    from dx_modelzoo.core.catalog import _enrich_model_entry

    base = {"id": "regnety_16gf", "name": "Regnety16Gf"}
    _enrich_model_entry(base, {"display": {"name": "RegNetY-16GF", "task": "image_classification"}})
    assert base["name"] == "RegNetY-16GF"
    keep = {"id": "x", "name": "Kept"}
    _enrich_model_entry(keep, {"display": {"task": "image_classification"}})
    assert keep["name"] == "Kept"


def test_the_newer_generated_catalog_wins_over_a_stale_cache(tmp_path):
    """An older sync cache must not hide a newer generated_catalog.json with the published names."""
    import json
    import os

    from dx_modelzoo.core.catalog import load_generated_catalog

    cache, gen = tmp_path / "cache.json", tmp_path / "gen.json"
    cache.write_text(json.dumps({"schema_version": "2.0", "models": [{"id": "a", "display": {"name": "a"}}]}))
    gen.write_text(json.dumps({"schema_version": "2.0", "models": [{"id": "a", "display": {"name": "A-Net"}}]}))
    os.utime(cache, (1_000_000, 1_000_000))
    os.utime(gen, (2_000_000, 2_000_000))
    assert load_generated_catalog(cache, gen)["models"][0]["display"]["name"] == "A-Net"
    os.utime(cache, (3_000_000, 3_000_000))      # a fresher sync wins again
    assert load_generated_catalog(cache, gen)["models"][0]["display"]["name"] == "a"


def test_the_summary_sentence_uses_the_published_name():
    from dx_modelzoo.core.catalog import _enrich_summary

    m = {"id": "regnety_16gf", "name": "RegNetY-16GF",
         "description": {"en": "regnety_16gf is a classification model.", "ko": "regnety_16gf은(는) 분류 모델입니다."}}
    _enrich_summary(m)
    assert m["display"]["summary"]["en"] == "RegNetY-16GF is a classification model."
    assert m["description"]["ko"].startswith("RegNetY-16GF")


def test_run_inference_finds_examples_in_the_per_model_layout(tmp_path, monkeypatch):
    """The per-model layout has no python_example/<task>/<catalog id>/ (it is
    object_detection/yolo26/yolo26-n_640x640/). Looking there returns no variants, the panel defaults
    to an unbuilt C++ binary and Run Inference says "Binary not found"."""
    from dx_modelzoo.core import catalog
    from shared import dx_app_layout

    root = tmp_path / "dx_app"
    ex = root / "src/python_example/object_detection/yolo26/yolo26-n_640x640"
    ex.mkdir(parents=True)
    (ex / "yolo26-n_640x640_sync.py").write_text("")
    (ex / "yolo26-n_640x640_async.py").write_text("")
    (root / "bin").mkdir()
    monkeypatch.setattr(catalog, "DX_APP_ROOT", root)
    monkeypatch.setattr(catalog, "BUILD_DIR", root / "bin")
    dx_app_layout.clear_cache()
    try:
        got = catalog._detect_inference_variants("yolo26n", "object_detection", "assets/models/yolo26-n_640x640.dxnn")
    finally:
        dx_app_layout.clear_cache()
    assert got == {"python": ["sync", "async"]}


def test_the_panel_uses_the_only_path_when_no_selector_is_drawn():
    from pathlib import Path

    js = (Path(__file__).resolve().parents[2] / "dx_modelzoo/static/js/inference.js").read_text(encoding="utf-8")
    assert "(sel && sel.value) || _infDefaultPath" in js
    assert "_infDefaultPath = execOpts.length ? execOpts[0].value" in js
