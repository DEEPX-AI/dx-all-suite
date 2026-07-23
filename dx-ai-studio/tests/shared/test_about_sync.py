"""About-DEEPX news sync (general-net freshness). Offline: fetch is injected."""
import json
from pathlib import Path

from shared import about_sync

_FIXTURE = """
<html><body>
  <a href="/media/deepx-wins-ee-times-award-2026/">DEEPX wins EE Times Best Product of the Year 2026</a>
  <a href="https://deepx.ai/deepx-announces-aaeon-mass-production-partnership/">DEEPX announces mass-production partnership with AAEON</a>
  <a href="/about/">About</a>            <!-- too short / not news: dropped -->
  <a href="/media/deepx-wins-ee-times-award-2026/">DEEPX wins EE Times Best Product of the Year 2026</a> <!-- dup -->
</body></html>
"""


def test_parse_news_filters_and_dedups():
    items = about_sync.parse_news(_FIXTURE)
    urls = [i["url"] for i in items]
    assert "https://deepx.ai/media/deepx-wins-ee-times-award-2026/" in urls
    assert "https://deepx.ai/deepx-announces-aaeon-mass-production-partnership/" in urls
    assert urls.count("https://deepx.ai/media/deepx-wins-ee-times-award-2026/") == 1  # deduped
    assert all("/about/" not in u for u in urls)  # non-news dropped


def test_sync_merges_preserves_schema_and_i18n(tmp_path):
    # minimal about-data.json with existing news
    about = tmp_path / "about-data.json"
    about.write_text(json.dumps({
        "news": {"media": [{"title": {l: "old" for l in about_sync._LANGS},
                            "source": "X", "date": "2024", "url": "https://deepx.ai/old/"}]},
        "meta": {"lastVerified": "2026-01-01"},
    }), encoding="utf-8")

    res = about_sync.sync_about(fetch_text=lambda u: _FIXTURE, about_path=about, today="2026-07-03")
    assert res["added"] == 2 and res["fetched"] == 2
    data = json.loads(about.read_text())
    media = data["news"]["media"]
    # newest prepended, old kept
    assert any(m["url"] == "https://deepx.ai/old/" for m in media)
    # every entry i18n-complete (6-lang) — keeps the About/i18n contract
    for m in media:
        assert set(m["title"].keys()) == set(about_sync._LANGS), m["url"]
    assert data["meta"]["lastVerified"] == "2026-07-03"

    # idempotent: re-run adds nothing (dedup by URL)
    res2 = about_sync.sync_about(fetch_text=lambda u: _FIXTURE, about_path=about, today="2026-07-03")
    assert res2["added"] == 0
