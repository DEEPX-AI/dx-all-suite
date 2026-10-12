"""Behaviour contracts for home-router: the real router runs in a browser.

Only the script is injected into a blank page and its pure functions are called (no server, no page).
Sync Playwright still owns one event loop per process, so this runs isolated in the --browser stage.
Source-only contracts stay in test_home_router.py and guard the blocking gate.
"""
from __future__ import annotations

import json

import pytest

from tests.launcher.home_router_support import HERO_CHIPS, ROUTER, source  # noqa: F401

@pytest.fixture(scope="module")
def route():
    """Run the real router in a browser, with no server and no page.

    The studio ships no bundler and no JS test runner, and adding an embedded
    engine just for this would be a dependency the product does not otherwise
    need. Playwright is already here, and a pure function needs nothing but a
    blank page to run in — about two seconds for the whole module.
    """
    pytest.importorskip("playwright.sync_api")
    from playwright.sync_api import sync_playwright

    from tests.browser_support import launch_browser

    pw = sync_playwright().start()
    try:
        browser = launch_browser(pw, "chromium")
    except Exception as exc:  # engine not installed on this host
        pw.stop()
        pytest.skip(f"chromium unavailable: {type(exc).__name__}: {exc}")
    page = browser.new_page()
    page.add_script_tag(content=source())

    def _call(text, catalog=None, demos=None):
        return page.evaluate(
            "([t, c, d]) => JSON.stringify(window.DXHomeRouter.resolve(t, c, d))",
            [text, catalog or [], demos or []],
        )

    yield _call
    page.close()
    browser.close()
    pw.stop()


# ── behavioural contracts (run the real router in a browser) ────

CATALOG = [
    {"id": "yolo26n", "name": "YOLOv26n", "task": "object_detection"},
    {"id": "yolo26n_pose", "name": "YOLOv26n_Pose", "task": "pose_estimation"},
]
DEMOS = [
    {"id": 0, "name_en": "Object Detection", "category": "object_detection"},
    {"id": 4, "name_en": "Pose Estimation", "category": "pose_estimation"},
    {"id": 6, "name_en": "Semantic Segmentation", "category": "segmentation"},
]


def test_it_reads_task_channels_and_target(route):
    got = json.loads(route("4-channel CCTV, detect people, 30 FPS", CATALOG, DEMOS))
    assert got["parsed"]["task"] == "object_detection"
    assert got["parsed"]["channels"] == 4
    assert got["parsed"]["fps"] == 30
    assert got["routes"], "a matched sentence must offer somewhere to go"


def test_the_intro_stream_prompt_goes_to_stream_with_sixteen_channels(route):
    """The sentence the intro's first working scene types: home must actually take on that job."""
    got = json.loads(route("16-channel CCTV object detection", CATALOG, DEMOS))
    assert got["parsed"]["channels"] == 16
    assert any(r.get("module") == "stream" for r in got["routes"]), got["routes"]


def test_a_model_name_resolves_that_model(route):
    got = json.loads(route("run yolo26n_pose", CATALOG, DEMOS))
    assert any(r.get("model") == "YOLOv26n_Pose" for r in got["routes"])


def test_compile_routes_to_the_compiler(route):
    got = json.loads(route("compile yolo26n to DXNN", CATALOG, DEMOS))
    assert any(r.get("module") == "compiler" for r in got["routes"])


def test_a_sentence_about_nothing_we_ship_returns_no_routes(route):
    """An unmatched sentence is the agent's cue, not a bad guess."""
    got = json.loads(route("write me a haiku about the weather", CATALOG, DEMOS))
    assert got["routes"] == []
    assert got["parsed"]["task"] is None


def test_understanding_the_task_is_not_the_same_as_having_a_preset(route):
    """"Count push-ups" is pose estimation — we should say so.

    What we do not have is something to run. Reading the task and offering a
    route are separate answers, and conflating them is how a router starts
    guessing: the agent is the escalation, and it earns that by there being no
    preset, not by us failing to understand the sentence.
    """
    no_pose_demo = [d for d in DEMOS if d["category"] != "pose_estimation"]
    got = json.loads(
        route("count push-ups from a webcam and shout the number", CATALOG, no_pose_demo)
    )
    assert got["parsed"]["task"] == "pose_estimation", "we do understand it"
    assert got["parsed"]["source"] == "webcam"
    assert not [r for r in got["routes"] if r["kind"] == "run"], (
        "nothing to run means no run route — that is the agent's opening"
    )


@pytest.mark.parametrize("chip", HERO_CHIPS)
def test_each_hero_chip_resolves(route, chip):
    got = json.loads(route(chip, CATALOG, DEMOS))
    assert got["routes"], f"the hero offers {chip!r} and the router cannot honour it"


ZOO = [  # the Model Zoo's own catalogue calls the task "category"
    {"id": "yolo26n", "name": "YOLO26n", "category": "object_detection"},
    {"id": "scrfd500m", "name": "SCRFD500M", "category": "face_detection"},
    {"id": "yolov8n_seg", "name": "YOLOv8n-seg", "category": "instance_segmentation"},
    {"id": "bisenetv2", "name": "BiSeNetV2", "category": "semantic_segmentation"},
]


@pytest.mark.parametrize("text, task", [
    ("face detection on a webcam", "face_detection"),       # the longer phrase wins even though 'detection' comes first
    ("카메라로 사람 탐지", "object_detection"),
    ("웹캠으로 얼굴 탐지", "face_detection"),
    ("カメラで姿勢推定", "pose_estimation"),
    ("摄像头 目标检测", "object_detection"),
    ("segmentación de video", "segmentation"),
])
def test_the_router_reads_the_six_languages(route, text, task):
    """Korean and Japanese sentences must route by their words, not fall through to the agent every time."""
    got = json.loads(route(text, ZOO, DEMOS))
    assert got["parsed"]["task"] == task, got


def test_a_korean_source_word_is_read(route):
    got = json.loads(route("웹캠으로 얼굴 탐지", ZOO, DEMOS))
    assert got["parsed"]["source"] == "webcam"
    got = json.loads(route("IP カメラで物体検出", ZOO, DEMOS))
    assert got["parsed"]["source"] == "rtsp", "더 긴 'ip カメラ' 가 'カメラ' 를 이긴다"


def test_the_zoo_catalogue_counts_by_category(route):
    """Model Zoo's catalog gives task as category; reading it is what makes 'Pick a model' appear."""
    got = json.loads(route("segmentation", ZOO, DEMOS))
    models = [r for r in got["routes"] if r["kind"] == "models"]
    assert models and models[0]["count"] == 2, got["routes"]
    got = json.loads(route("face detection", ZOO, DEMOS))
    assert [r["count"] for r in got["routes"] if r["kind"] == "models"] == [1]


@pytest.mark.parametrize("text", ["4채널 CCTV 사람 탐지", "4 チャンネルで物体検出", "4路 目标检测", "4 canales detección"])
def test_a_channel_count_is_read_in_every_language(route, text):
    assert json.loads(route(text, ZOO, DEMOS))["parsed"]["channels"] == 4
