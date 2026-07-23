#!/usr/bin/env python3
"""Quarterly About DEEPX sync — diff official sources vs about-data.json.

Usage:
  python3 scripts/quarterly_about_sync.py              # report only (default)
  python3 scripts/quarterly_about_sync.py --apply-safe # update meta + unambiguous fields
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "launcher/static/about-data.json"

USER_AGENT = "DX-AI-Studio/quarterly-about-sync"
TIMEOUT = 30


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_model_zoo(html: str) -> dict:
    count = None
    m = re.search(r"Total Models Available:\s*(\d+)", html)
    if m:
        count = m.group(1)
    as_of = None
    m = re.search(r"Generated on\s+([\d-]+)", html)
    if m:
        as_of = m.group(1)
    dx_com = None
    dx_rt = None
    m = re.search(r"SDK Version:\s*dx-com\s+(v[\d.]+),\s*dx-rt\s+(v[\d.]+)", html, re.I)
    if m:
        dx_com, dx_rt = m.group(1), m.group(2)
    return {"count": count, "asOf": as_of, "dxCom": dx_com, "dxRt": dx_rt}


def extract_sdk_release(html: str) -> dict | None:
    m = re.search(
        r"DX-All-Suite\s+(v[\d.]+)\s+Release Update",
        html,
        re.I,
    )
    if not m:
        return None
    version = m.group(1)
    summary = None
    sm = re.search(
        r"DX-All-Suite\s+v[\d.]+\s+Release Update</[^>]+>\s*<[^>]+>([^<]{20,200})",
        html,
        re.I | re.S,
    )
    if sm:
        summary = re.sub(r"\s+", " ", sm.group(1)).strip()
    return {"version": version, "summary": summary}


def extract_home_headlines(html: str) -> list[str]:
    """Best-effort: WordPress post titles from home HTML."""
    titles = re.findall(r'class="[^"]*entry-title[^"]*"[^>]*>\s*<a[^>]*>([^<]+)</a>', html)
    if not titles:
        titles = re.findall(r"<h[23][^>]*>([^<]{10,120})</h[23]>", html)
    cleaned = []
    for t in titles:
        t = re.sub(r"\s+", " ", t).strip()
        if t and t not in cleaned:
            cleaned.append(t)
    return cleaned[:12]


def extract_award_names(html: str) -> list[str]:
    names = re.findall(
        r"CES Innovation Awards|EE Times|WEF MINDS|Frost & Sullivan|Computex|VSD Innovators|Presidential Citation|What Not To Miss",
        html,
        re.I,
    )
    return list(dict.fromkeys(names))


def diff_report(data: dict, live: dict) -> dict:
    report = {"diffs": [], "live": live}
    dev = data.get("developer", {})
    mz = dev.get("modelZooSnapshot", {})
    if live.get("modelZoo", {}).get("count") and live["modelZoo"]["count"] != mz.get("count", "").replace("+", ""):
        report["diffs"].append({
            "field": "developer.modelZooSnapshot.count",
            "json": mz.get("count"),
            "live": live["modelZoo"]["count"],
        })
    if live.get("modelZoo", {}).get("asOf") and live["modelZoo"]["asOf"] != mz.get("asOf"):
        report["diffs"].append({
            "field": "developer.modelZooSnapshot.asOf",
            "json": mz.get("asOf"),
            "live": live["modelZoo"]["asOf"],
        })
    rel = dev.get("sdkRelease", {})
    if live.get("sdkRelease", {}).get("version") and live["sdkRelease"]["version"] != rel.get("version"):
        report["diffs"].append({
            "field": "developer.sdkRelease.version",
            "json": rel.get("version"),
            "live": live["sdkRelease"]["version"],
        })
    json_past = [e.get("title", {}).get("en", "") for e in data.get("news", {}).get("past", [])]
    for headline in live.get("homeHeadlines", [])[:5]:
        if not any(headline[:30] in p or p[:30] in headline for p in json_past):
            report["diffs"].append({
                "field": "news.past (missing headline)",
                "json": None,
                "live": headline[:80],
            })
    return report


def apply_safe(data: dict, live: dict) -> bool:
    changed = False
    data.setdefault("meta", {})
    data["meta"]["lastVerified"] = date.today().isoformat()
    changed = True

    mz = live.get("modelZoo", {})
    if mz.get("count"):
        dev = data.setdefault("developer", {})
        snap = dev.setdefault("modelZooSnapshot", {})
        if snap.get("count") != mz["count"]:
            snap["count"] = mz["count"]
            changed = True
        if mz.get("asOf"):
            snap["asOf"] = mz["asOf"]
            changed = True
        tech = data.setdefault("technology", {}).setdefault("sdk", {})
        for stat in tech.get("stats", []):
            if stat.get("label", {}).get("en") == "Model Zoo Models":
                val = f"{mz['count']}+" if not str(mz["count"]).endswith("+") else mz["count"]
                if stat.get("value") != val:
                    stat["value"] = val
                    changed = True

    if mz.get("dxCom") or mz.get("dxRt"):
        tech = data.setdefault("technology", {}).setdefault("sdk", {})
        versions = tech.setdefault("versions", {})
        if mz.get("dxCom") and versions.get("dxCom") != mz["dxCom"]:
            versions["dxCom"] = mz["dxCom"]
            changed = True
        if mz.get("dxRt") and versions.get("dxRt") != mz["dxRt"]:
            versions["dxRt"] = mz["dxRt"]
            changed = True

    rel = live.get("sdkRelease")
    if rel and rel.get("version"):
        dev = data.setdefault("developer", {})
        sr = dev.setdefault("sdkRelease", {})
        if sr.get("version") != rel["version"]:
            sr["version"] = rel["version"]
            changed = True
        tech = data.setdefault("technology", {}).setdefault("sdk", {})
        if tech.get("release", {}).get("version") != rel["version"]:
            tech.setdefault("release", {})["version"] = rel["version"]
            changed = True

    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Quarterly About DEEPX official-source diff")
    parser.add_argument("--apply-safe", action="store_true", help="Apply unambiguous field updates")
    parser.add_argument("--offline", action="store_true", help="Skip network (for CI smoke)")
    args = parser.parse_args()

    data = json.loads(DATA_PATH.read_text())

    if args.offline:
        print(json.dumps({"status": "offline", "message": "skipped network fetch"}, indent=2))
        return 0

    home_html = fetch("https://deepx.ai/")
    dev_html = fetch("https://developer.deepx.ai/")
    mz_html = fetch("https://developer.deepx.ai/modelzoo/")

    live = {
        "modelZoo": extract_model_zoo(mz_html),
        "sdkRelease": extract_sdk_release(dev_html),
        "homeHeadlines": extract_home_headlines(home_html),
        "awardKeywords": extract_award_names(home_html),
    }

    report = diff_report(data, live)
    report["status"] = "ok"
    report["checkedAt"] = date.today().isoformat()

    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.apply_safe:
        if apply_safe(data, live):
            DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            print(f"\nApplied safe updates to {DATA_PATH}", file=sys.stderr)
        else:
            print("\nNo safe field changes needed (meta.lastVerified still updated)", file=sys.stderr)
            data["meta"]["lastVerified"] = date.today().isoformat()
            DATA_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
