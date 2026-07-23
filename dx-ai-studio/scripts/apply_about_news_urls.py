#!/usr/bin/env python3
"""Apply official deepx.ai URLs to about-data.json news items (title substring match)."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "launcher/static/about-data.json"

URL_BY_TITLE_FRAGMENT = {
    "Tokyo Physical AI Expo": "https://deepx.ai/lets-meet-at-manufacturing-world-2026-tokyo-deepx-booth-s14-16/",
    "Manufacturing World Tokyo": "https://deepx.ai/lets-meet-at-manufacturing-world-2026-tokyo-deepx-booth-s14-16/",
    "Avnet Edge & Beyond": "https://deepx.ai/avnet-edge-beyond-tech-days-2026-10-jul-2026-24-jul-2026/",
    "AAEON": "https://deepx.ai/deepx-announces-global-physical-ai-mass-production-partnership-with-aaeon/",
    "From Startup Stage to Global Stage": "https://deepx.ai/from-startup-stage-to-global-stage-deepx-at-computex-taipei-2026/",
    "Physical AI showcase": "https://deepx.ai/lets-meet-at-computex-taipei-2026-tainex-1-4f-deepx-booth-m1311a/",
    "Impersonation and Copyright": "https://deepx.ai/notice-warning-regarding-impersonation-and-copyright-infringement-in-vietnam/",
    "Ultralytics Live Session 23": "https://deepx.ai/ultralytics-live-session-23-pioneering-innovation-in-edge-ai-with-ultralytics-and-deepx/",
    "Webinar: DEEPX & Avnet Silica": "https://deepx.ai/webinar-avnet-silica-deploy-edge-ai-at-gpu-level-performance/",
    "Hyundai Motor Group Robotics LAB": "https://deepx.ai/deepx-and-hyundai-motor-group-robotics-lab-partner-to-develop-physical-ai-compute-platform-for-robotics/",
    "Embedded World 2026": "https://deepx.ai/deepx-targets-the-european-market-at-embedded-world-2026-building-a-comprehensive-alliance-with-10-global-partners/",
    "DEEPX × Ultralytics": "https://deepx.ai/deepx-and-ultralytics-forge-strategic-alliance-to-define-the-global-standard-for-physical-ai-in-the-yolo-community/",
    "Double Honoree": "https://deepx.ai/deepx-unveils-vision-as-a-physical-ai-infrastructure-company-at-ces-2026/",
    "Physical AI briefing & DX-M2": "https://deepx.ai/ces-2026-media-briefing-deepx-unveils-physical-ai-vision-roadmap/",
    "Triple Honoree": "https://deepx.ai/company/our-story/",
}

MEDIA_URLS = {
    "EE Times": "https://deepx.ai/products/dx-m1/",
    "WEF MINDS": "https://deepx.ai/company/our-story/",
}


def apply_urls(items, fragments):
    for item in items:
        title_en = item.get("title", {})
        if isinstance(title_en, dict):
            title_en = title_en.get("en", "")
        for frag, url in fragments.items():
            if frag in title_en:
                item["url"] = url
                break


def main():
    data = json.loads(path.read_text())
    news = data["news"]
    for key in ("upcoming", "past"):
        if key in news:
            apply_urls(news[key], URL_BY_TITLE_FRAGMENT)
    for m in news.get("media", []):
        src = m.get("source", "")
        if src in MEDIA_URLS:
            m["url"] = MEDIA_URLS[src]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    print("Applied news URLs to", path)


if __name__ == "__main__":
    main()
