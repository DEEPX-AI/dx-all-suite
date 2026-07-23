"""About-DEEPX news freshness sync (general-net only).

The About panel is driven by launcher/static/about-data.json, which is maintained
quarterly and therefore goes stale between releases. This module refreshes the
``news.media`` list from a live DEEPX page so the panel can stay current without a
release. It mirrors dx_modelzoo's public adapter (inject a ``fetch_text`` so it is
offline-testable) and preserves the 6-language schema the About data + i18n audit
require (auto-fetched titles are English; the other locales fall back to English until
a human translation lands, which keeps the i18n contract green).

Usage:
    python -m shared.about_sync                 # fetch + merge into about-data.json
    python -m shared.about_sync --url <news>    # override the source page
Configure the source page with DX_ABOUT_NEWS_URL. On the company network set
REQUESTS_CA_BUNDLE/SSL_CERT_FILE for TLS (the certifi vs system-CA gotcha).
This is a general-net-only feature; do not run it on the air-gapped board.
"""
from __future__ import annotations

import json
import os
import re
import ssl
from datetime import date
from pathlib import Path
from urllib.request import Request, urlopen

_LANGS = ("en", "ko", "ja", "zh-CN", "zh-TW", "es")
# deepx.ai/media/ went 404 in the mid-2026 site restructure; news lives at /category/news/.
_DEFAULT_URL = os.environ.get("DX_ABOUT_NEWS_URL", "https://deepx.ai/category/news/")
_ABOUT_DATA = Path(__file__).resolve().parent.parent / "launcher" / "static" / "about-data.json"
_BASE = "https://deepx.ai"


def _fetch_url_text(url: str, *, verify_tls: bool = True, timeout: int = 20) -> str:
    ctx = None if verify_tls else ssl._create_unverified_context()
    req = Request(url, headers={"User-Agent": "dx-ai-studio-about-sync/1.0"})
    with urlopen(req, timeout=timeout, context=ctx) as resp:  # noqa: S310 (fixed host)
        return resp.read().decode("utf-8", "replace")


def parse_news(html: str, base: str = _BASE) -> list[dict]:
    """Extract candidate news items ({title, url}) from a DEEPX listing page.

    Heuristic + resilient to markup drift: any <a> whose href or text looks news-like
    and whose visible text is a plausible headline. Deduped by URL, newest-first order
    preserved, capped."""
    items: list[dict] = []
    for m in re.finditer(r'<a\b[^>]*href="([^"#]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
        href = m.group(1).strip()
        title = re.sub(r"<[^>]+>", " ", m.group(2))
        title = re.sub(r"\s+", " ", title).strip()
        if len(title) < 15:
            continue
        blob = (href + " " + title).lower()
        if not re.search(r"/media|/news|/press|/blog|announce|award|series|partnership|deepx\.ai/[a-z]", blob):
            continue
        url = href if href.startswith("http") else base.rstrip("/") + "/" + href.lstrip("/")
        items.append({"title": title, "url": url})
    seen: set = set()
    out: list[dict] = []
    for it in items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        out.append(it)
    return out[:12]


def _to_media_entry(item: dict) -> dict:
    # English-fallback across all six locales keeps the About i18n contract satisfied.
    return {
        "title": {lang: item["title"] for lang in _LANGS},
        "source": item.get("source", "DEEPX"),
        "date": item.get("date", ""),
        "url": item["url"],
    }


def sync_about(fetch_text=None, url: str = _DEFAULT_URL, *, verify_tls: bool = True,
               about_path: Path = _ABOUT_DATA, today: str | None = None) -> dict:
    """Fetch the news page, merge new items into about-data.json ``news.media`` (dedup
    by URL, newest prepended), bump ``meta.lastVerified``. Returns a summary dict."""
    fetch_text = fetch_text or (lambda u: _fetch_url_text(u, verify_tls=verify_tls))
    items = parse_news(fetch_text(url))
    path = Path(about_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    media = data.setdefault("news", {}).setdefault("media", [])
    existing = {m.get("url") for m in media if m.get("url")}
    added = [_to_media_entry(it) for it in items if it["url"] not in existing]
    media[:0] = added  # prepend newest
    data.setdefault("meta", {})["lastVerified"] = today or date.today().isoformat()
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"fetched": len(items), "added": len(added), "total": len(media)}


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Refresh About-DEEPX news (general net).")
    ap.add_argument("--url", default=_DEFAULT_URL)
    ap.add_argument("--no-verify-tls", action="store_true")
    args = ap.parse_args(argv)
    result = sync_about(url=args.url, verify_tls=not args.no_verify_tls)
    print(f"about-sync: fetched={result['fetched']} added={result['added']} total={result['total']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
