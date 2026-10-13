"""Six awkward cards (long name, three metrics, no FPS, board table, unpublished PPU, classification) render
without overflow or wrapped labels at 1280/1024/390 px in dark and light."""
import pytest

pytest.importorskip("playwright.sync_api")

from dx_modelzoo.core.catalog import get_catalog  # noqa: E402
from dx_modelzoo.core.config import DATA_DIR  # noqa: E402
from dx_modelzoo.tools.export_dx_app_cards import build_outputs, write_outputs  # noqa: E402
from shared.chromium import resolve_chromium_executable  # noqa: E402
from shared.paths import DX_APP_ROOT, STUDIO_ROOT  # noqa: E402
from tests.dx_modelzoo.model_card_layout import faults  # noqa: E402

FIXED = {"yolo26-n_640x640", "yolov5-m-face_640x640", "clip-img_vit-b16-quickgelu_224x224_metaclip-fullcc",
         "yolov12-cls-n_224x224", "damoyolo-s_640x640", "SCRFD500M_PPU"}
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
    outputs, _ = build_outputs(out, cat["models"], cat.get("categories") or {},
                               load_benchmark(STUDIO_ROOT / "dx_benchmark" / "dataset.json"), DATA_DIR, "2026-10-13",
                               only=FIXED)
    write_outputs(out, outputs)
    return sorted(out.glob("src/python_example/*/*/*/model.html"))


def test_six_cards_have_no_layout_faults(cards):
    from playwright.sync_api import sync_playwright

    assert len(cards) == len(FIXED)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=resolve_chromium_executable())
        try:
            problems = {c.parent.name: faults(browser, c) for c in cards}
        finally:
            browser.close()
    assert not {k: v for k, v in problems.items() if v}, problems
