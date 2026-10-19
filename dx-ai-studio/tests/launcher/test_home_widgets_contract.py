"""The two widgets beside the stage: contracts on data paths and selection."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
STATIC = ROOT / "launcher" / "static"
HTML = (STATIC / "index.html").read_text(encoding="utf-8")
FRAME = (STATIC / "launcher-app-frame.js").read_text(encoding="utf-8")


def _widgets() -> str:
    path = STATIC / "home-widgets.js"
    assert path.is_file(), "launcher/static/home-widgets.js 가 없다"
    return path.read_text(encoding="utf-8")


def test_the_widget_script_is_served_and_loaded_after_the_sections():
    launcher = (ROOT / "launcher" / "launcher.py").read_text(encoding="utf-8")
    assert 'path == "/home-widgets.js"' in launcher
    assert HTML.index('src="/home-sections.js"') < HTML.index('src="/home-widgets.js"')


def test_the_device_widget_rides_the_shared_stream_not_a_new_poll():
    """Device values are already broadcast by startSharedHwStream over SSE (3 s poll without it). A widget with
    its own poll would ask the same device twice."""
    js = _widgets()
    assert "dx-hw-data" in js
    assert not re.search(r"setInterval\([^)]*\n?[^)]*hw_status", js), "위젯이 hw_status 를 주기로 묻는다"


def test_one_owner_paints_the_device():
    """No old painter: a 15 s poll and the stream must not take turns overwriting the same chip."""
    assert "function refreshHeroDevice" not in FRAME
    assert "_paintDeviceFacts" not in FRAME
    assert "refreshHeroDevice" not in FRAME


def test_the_headline_is_the_nano_model_of_each_task_named_by_id():
    """Picking the fastest model overall gives numbers from different tasks that cannot be compared.
    The ids are listed explicitly rather than guessed from name patterns, so what gets picked is readable."""
    js = _widgets()
    pairs = re.findall(r"\['(\w+)',\s*'(\w+)'\]", js[js.index("HEADLINE"):js.index("];", js.index("HEADLINE"))])
    assert pairs == [
        ("object_detection", "yolo26n"),
        ("instance_segmentation", "yolo26n_seg"),
        ("pose_estimation", "yolo26n_pose"),
        ("classification", "yolo26n_cls"),
        ("obb_detection", "yolo26n_obb"),
        ("depth_estimation", "yolo26_depth_n"),
    ]


def test_the_sections_hand_the_catalogue_over_instead_of_a_second_fetch():
    sections = (STATIC / "home-sections.js").read_text(encoding="utf-8")
    assert "dx-home-catalog" in sections
    assert "/zoo/api/catalog" not in _widgets(), "위젯이 카탈로그를 다시 받는다"


def test_the_widgets_open_their_modules_without_inline_handlers():
    """Same rule as the cards: open through a delegated listener (test_home_cards_use_delegated_routing_not_inline_onclick)."""
    device = HTML[HTML.index('id="homeDevice"'):HTML.index('id="studioGrid"')]
    assert "onclick" not in device
    js = _widgets()
    assert "'dx_monitor'" in js and "'benchmark'" in js


_KEYS = ["No DX-M1 connected", "Object Detection", "Instance Segmentation", "Pose Estimation",
         "Classification", "OBB Detection", "Depth Estimation"]


@pytest.mark.parametrize("key", _KEYS)
def test_new_words_speak_all_six_languages(key):
    m = re.search(r"'" + re.escape(key) + r"':\s*\{([^}]*)\}", HTML)
    assert m, f"사전에 {key!r} 가 없다"
    for lang in ("ko", "ja", "es", "'zh-CN'", "'zh-TW'"):
        assert re.search(r"(?:^|[\s,{])" + re.escape(lang) + r"\s*:", m.group(1)), (key, lang)


def test_task_words_are_the_ones_the_model_zoo_already_uses():
    """Terms must not diverge per module: reuse the Model Zoo dictionary's translations."""
    zoo = (ROOT / "dx_modelzoo" / "static" / "js" / "i18n-dict-shared.js").read_text(encoding="utf-8")
    for key in _KEYS[1:]:
        ours = re.search(r"'" + re.escape(key) + r"':\s*\{([^}]*)\}", HTML).group(1)
        theirs = re.search(r"['\"]" + re.escape(key) + r"['\"]\s*:\s*\{([^}]*)\}", zoo).group(1)
        ko_ours = re.search(r"ko:\s*'([^']*)'", ours).group(1)
        ko_theirs = re.search(r"ko['\"]?\s*:\s*['\"]([^'\"]*)['\"]", theirs).group(1)
        assert ko_ours == ko_theirs, (key, ko_ours, ko_theirs)
