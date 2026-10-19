"""dx_agent_dev showcase catalog (9 examples, 6 languages)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "dx_agent_dev"))

LANGS = ("en", "ko", "ja", "es", "zh-CN", "zh-TW")
MEDIA_DIR = ROOT / "dx_agent_dev" / "static" / "media"


def _load():
    from core import showcases
    return showcases.load_showcases()


def test_load_showcases_returns_list():
    items = _load()
    assert isinstance(items, list) and len(items) >= 9
    first = items[0]
    for k in ("id", "title", "tagline", "media", "url", "category"):
        assert k in first, k


def test_showcase_count_is_nine():
    assert len(_load()) == 9


def test_showcase_fields_cover_six_langs():
    for sc in _load():
        for field in ("title", "tagline"):
            for lang in LANGS:
                assert lang in sc[field], (sc["id"], field, lang)


def test_showcase_media_and_url():
    for sc in _load():
        assert sc["media"].startswith("media/"), sc["id"]
        assert (MEDIA_DIR / Path(sc["media"]).name).exists(), sc["media"]
        assert sc["url"].startswith("https://"), sc["id"]


def test_showcase_thumbnails_stay_light():
    """The cards show each media at 194 px, so full-size GIFs (4-5 MB each) would make Agent Dev's first
    visit heavy. Thumbnails are 2x animated WebP with the GIF frame timing."""
    for sc in _load():
        size = (MEDIA_DIR / Path(sc["media"]).name).stat().st_size
        assert size <= 1_500_000, (sc["id"], size)
