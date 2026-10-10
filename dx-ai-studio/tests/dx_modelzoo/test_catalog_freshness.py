"""카탈로그가 언제 만들어졌는지는 카탈로그를 보는 화면에서 보여야 한다.

`generated_catalog.json` 은 sync 산출물이고 상류를 따라가지 못하면 낡는다. 2026-09-16
에 그 파일이 8일 묵어 있었고, 그동안 추가된 모델 다섯 개가 legal 없이 나갔다 — 아무
화면도 "이 목록이 언제 만들어졌는지" 를 말하지 않아 조용히 흘러갔다.

값은 이미 파일에 있다(`generated_at`). 없는 것은 그것을 내보내는 경로다.
개별 모델의 상세 화면은 이미 보여주지만, 347개를 훑는 목록 화면은 보여주지 않는다 —
정작 "이 목록 전체가 낡았나" 를 물어야 하는 자리가 거기다.

언제 다시 동기화할지는 운영 판단이라 여기서 정하지 않는다. 낡았는지 **보이게** 하는
것까지가 이 계약이다.
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
    """public 과 internal 은 다른 데이터를 준다. 어느 쪽인지 모르면 수치를 해석할 수 없다."""
    cat = _catalog()
    assert cat.get("source_profile") in ("public", "internal", "local"), cat.get("source_profile")


def test_the_value_matches_the_file_it_came_from():
    raw = json.loads((ROOT / "dx_modelzoo" / "data" / "generated_catalog.json").read_text())
    cat = _catalog()
    assert cat["generated_at"] == raw.get("generated_at"), (
        "화면이 말하는 날짜가 파일과 다르다"
    )


def test_the_api_carries_it_to_the_browser():
    """get_catalog() 에 실어두는 것만으로는 닿지 않는다 — 핸들러가 필드를 골라 담는다.

    처음에 이 검사가 없어서, 서버 계약 세 건이 통과하는데 화면에는 아무것도 나오지
    않았다. 소스 문자열만 보는 검사의 한계다.
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
    """상세 화면은 이미 보여준다. 목록이야말로 '전체가 낡았나' 를 묻는 자리다."""
    src = (ROOT / "dx_modelzoo" / "static" / "js" / "catalog.js").read_text(encoding="utf-8")
    assert "generated_at" in src, "목록 화면이 생성 시각을 쓰지 않는다"


def test_cards_use_the_curated_display_name():
    """model_catalog.json names were the id title-cased ('Regnety16Gf', '3Ddfa V2 Mobilnet0 5 120X120');
    the generated catalog's display.name is the curated one (2026-10-11 matrix)."""
    from dx_modelzoo.core.catalog import _enrich_model_entry

    base = {"id": "regnety_16gf", "name": "Regnety16Gf"}
    _enrich_model_entry(base, {"display": {"name": "RegNetY-16GF", "task": "image_classification"}})
    assert base["name"] == "RegNetY-16GF"
    keep = {"id": "x", "name": "Kept"}
    _enrich_model_entry(keep, {"display": {"task": "image_classification"}})
    assert keep["name"] == "Kept"
