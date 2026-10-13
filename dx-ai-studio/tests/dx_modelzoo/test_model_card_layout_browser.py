"""Seven awkward cards (long names with and without spaces, three metrics, no FPS, board table, unpublished PPU) render
without overflow or wrapped labels at 1280/1024/390 px in dark and light; so does Studio's Save as HTML card in
Korean and Spanish, whose labels are longer than the English ones."""
import pytest

pytest.importorskip("playwright.sync_api")

from dx_modelzoo.core.catalog import get_catalog  # noqa: E402
from dx_modelzoo.core.config import DATA_DIR  # noqa: E402
from dx_modelzoo.tools.export_dx_app_cards import build_outputs, write_outputs  # noqa: E402
from shared.chromium import resolve_chromium_executable  # noqa: E402
from shared.paths import DX_APP_ROOT, STUDIO_ROOT  # noqa: E402
from tests.dx_modelzoo.model_card_layout import faults  # noqa: E402

FIXED = {"yolo26-n_640x640", "yolov5-m-face_640x640", "clip-img_vit-b16-quickgelu_224x224_metaclip-fullcc",
         "yolov12-cls-n_224x224", "damoyolo-s_640x640", "yolov5-s_640x640_ppu",
         "mask-rtdetr-hgnetv2-x-6x_640x640"}   # a long unbroken model name
# Every model the current dx_app registers is published, so the unpublished layout (manifest download, catalog note)
# is drawn by taking this one's publish-table files away.
UNPUBLISHED = "yolov5-s_640x640_ppu"
pytestmark = pytest.mark.skipif(not (DX_APP_ROOT / "config" / "model_registry.json").is_file(),
                                reason="needs the dx_app checkout")


@pytest.fixture(scope="module")
def cards(tmp_path_factory):
    import shutil
    from dx_modelzoo.core.model_card import load_benchmark

    out = tmp_path_factory.mktemp("cards")
    shutil.copytree(DX_APP_ROOT / "config", out / "config")
    shutil.copytree(DX_APP_ROOT / "scripts", out / "scripts", ignore=shutil.ignore_patterns("*.py", "__pycache__"))
    for lang in ("python_example", "cpp_example"):
        for path in (DX_APP_ROOT / "src" / lang).glob("*/*/*/config.json"):
            if path.parent.name in FIXED:
                dest = out / path.parent.relative_to(DX_APP_ROOT)
                shutil.copytree(path.parent, dest)
    cat = get_catalog()
    models = [{k: v for k, v in m.items() if k not in ("artifacts", "performance")}
              if ((m.get("demo") or {}).get("python_example") or "").rstrip("/").endswith("/" + UNPUBLISHED) else m
              for m in cat["models"]]
    outputs, report = build_outputs(out, models, cat.get("categories") or {},
                               load_benchmark(STUDIO_ROOT / "dx_benchmark" / "dataset.json"), DATA_DIR, "2026-10-13",
                               only=FIXED)
    assert report["unpublished"] == [UNPUBLISHED]
    write_outputs(out, outputs)
    return sorted(out.glob("src/python_example/*/*/*/model.html"))


def test_the_fixed_cards_have_no_layout_faults(cards):
    from playwright.sync_api import sync_playwright

    assert len(cards) == len(FIXED)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
        try:
            problems = {c.parent.name: faults(browser, c) for c in cards}
        finally:
            browser.close()
    assert not {k: v for k, v in problems.items() if v}, problems


@pytest.fixture(scope="module")
def studio_cards(tmp_path_factory):
    """Studio's Save as HTML card for yolov5-m-face_640x640 in Korean and Spanish, with the labels the page sends."""
    from pathlib import PurePosixPath

    from dx_modelzoo.core.model_card_studio import category_label, studio_card
    from tests.dx_modelzoo.test_html_export import card_labels

    out = tmp_path_factory.mktemp("studio_cards")
    cat = get_catalog()
    model = next(m for m in cat["models"] if PurePosixPath(
        ((m.get("demo") or {}).get("python_example") or "").rstrip("/")).name == "yolov5-m-face_640x640")
    categories = cat.get("categories") or {}
    paths = []
    for lang in ("ko", "es"):
        payload = {"lang": lang, "labels": card_labels(lang),
                   "task_label": category_label(categories, model.get("category"), lang)}
        html, _name = studio_card(model, categories, payload, dx_app_root=DX_APP_ROOT, data_dir=DATA_DIR,
                                  benchmark_path=STUDIO_ROOT / "dx_benchmark" / "dataset.json", asof="2026-10-13")
        assert f'<html lang="{lang}">' in html and payload["labels"]["Quick start"] in html
        path = out / f"{lang}.html"
        path.write_text(html, encoding="utf-8")
        paths.append(path)
    return paths


def test_studio_cards_in_korean_and_spanish_have_no_layout_faults(studio_cards):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
        try:
            problems = {c.stem: faults(browser, c) for c in studio_cards}
        finally:
            browser.close()
    assert not {k: v for k, v in problems.items() if v}, problems
