"""Pins translation-review fixes so they do not drift back.

Each test reads the shipped UI dictionary source and checks one entry. The
wrong values guarded against: es 'Sincronizar' (the verb) for the Sync
inference mode, the ko word for Undo used for Cancel run, Setup sharing the
Settings word in ko/zh/ja/es, es 'Rellenos' / zh-TW '墊片' for GStreamer
Pads, the Built badge reading "OK", the ko word for a door handle used for
Handedness, and a stage-2 message glued from two fragments that came out
scrambled in ko/ja/zh.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

DX_APP_DICT = ROOT / "dx_app/static/js/i18n.js"
MODELZOO_DICT = ROOT / "dx_modelzoo/static/js/i18n-dict-inference.js"
STREAM_DICT = ROOT / "dx_stream/static/js/stream-i18n.js"
PIPELINE_JS = ROOT / "dx_app/static/js/pipeline.js"

_PAIR = re.compile(r"""(?:'([\w-]+)'|([\w-]+))\s*:\s*'((?:[^'\\]|\\.)*)'""")


def _entry(path: Path, key: str) -> dict[str, str]:
    """Return {lang: text} for a dictionary key, single- or multi-line form."""
    src = path.read_text(encoding="utf-8")
    m = re.search(r"\n\s*" + re.escape(f"'{key}'") + r"\s*:\s*\{(.*?')\s*,?\s*\}", src, re.S)
    assert m, f"{key!r} not found in {path.relative_to(ROOT)}"
    return {(a or b): v for a, b, v in _PAIR.findall(m.group(1))}


@pytest.mark.parametrize("path", [DX_APP_DICT, MODELZOO_DICT], ids=["dx_app", "dx_modelzoo"])
def test_sync_mode_is_synchronous_in_spanish(path):
    assert _entry(path, "Sync")["es"] == "Síncrono"


def test_cancel_run_is_not_undo_in_korean():
    assert _entry(DX_APP_DICT, "Cancel run")["ko"] == "실행 중단"
    assert _entry(DX_APP_DICT, "Undo")["ko"] == "실행 취소"
    lab = (ROOT / "dx_app/static/js/lab-portal.js").read_text(encoding="utf-8")
    assert "_text('Cancel run', '실행 중단')" in lab


@pytest.mark.parametrize("path", [DX_APP_DICT, STREAM_DICT], ids=["dx_app", "dx_stream"])
def test_setup_does_not_collide_with_settings(path):
    setup = _entry(path, "Setup")
    assert setup == {**setup, "ko": "설치", "zh-CN": "安装", "zh-TW": "安裝", "es": "Instalación"}
    if path is DX_APP_DICT:  # dx_stream has no Settings entry of its own
        settings = _entry(path, "Settings")
        for lang in ("ko", "zh-CN", "zh-TW", "es"):
            assert setup[lang] != settings[lang], (lang, setup[lang])


def test_gstreamer_pads_keep_their_meaning():
    pads = _entry(STREAM_DICT, "Pads")
    assert pads["es"] == "Pads"
    assert pads["zh-TW"] == "連接埠"


def test_built_badge_says_built_not_ok():
    built = _entry(STREAM_DICT, "Built")
    assert built["ko"] == "빌드됨"
    assert built["ja"] == "ビルド済み"
    assert built["zh-CN"] == "已构建"
    assert built["zh-TW"] == "已建置"


def test_stage2_message_is_one_key_with_count_placeholder():
    key = "Running stage-2 inference on {n} detected region(s)"
    entry = _entry(DX_APP_DICT, key)
    for lang in ("ko", "ja", "zh-CN", "zh-TW", "es"):
        assert entry[lang].count("{n}") == 1, (lang, entry[lang])
    src = DX_APP_DICT.read_text(encoding="utf-8")
    assert "'Running stage-2 inference on ':" not in src
    assert "' detected region(s)':" not in src
    js = PIPELINE_JS.read_text(encoding="utf-8")
    assert "T('Running stage-2 inference on {n} detected region(s)').replace('{n}'," in js


def test_handedness_is_left_or_right_hand_in_korean():
    assert _entry(DX_APP_DICT, "Handedness")["ko"] == "왼손/오른손"
    charts = (ROOT / "shared/static/dx-charts.js").read_text(encoding="utf-8")
    assert "_t('Handedness','왼손/오른손')" in charts
