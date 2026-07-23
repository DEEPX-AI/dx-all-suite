#!/usr/bin/env python3
"""Phase 3 cleanup: remove dead data, add SDK versions + developer CTAs."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / "launcher/static/about-data.json"
data = json.loads(path.read_text())


def L(en, ko=None, ja=None, zh_cn=None, zh_tw=None, es=None):
    return {
        "en": en,
        "ko": ko or en,
        "ja": ja or en,
        "zh-CN": zh_cn or en,
        "zh-TW": zh_tw or en,
        "es": es or en,
    }


data["partners"].pop("logos", None)

data["technology"]["sdk"]["versions"] = {"dxCom": "v2.3.0", "dxRt": "v3.3.0"}

data["developer"]["modelZooSnapshot"] = {"count": "271", "asOf": "2026-04-21"}
for stat in data["technology"]["sdk"]["stats"]:
    if stat.get("label", {}).get("en") == "Model Zoo Models":
        stat["value"] = "271"
desc = data["developer"]["links"][1]["desc"]
for lang in desc:
    desc[lang] = desc[lang].replace("271+", "271")

data["developer"]["ctas"] = [
    {
        "id": "schedule-meeting",
        "primary": True,
        "label": L(
            "Schedule a Meeting",
            "미팅 예약",
            "ミーティング予約",
            "预约会议",
            "預約會議",
            "Agendar reunión",
        ),
        "url": "https://deepx.ai/contact-us/sales-support/",
    },
    {
        "id": "techbridge-apply",
        "primary": False,
        "label": L(
            "Apply for TechBridge Kit",
            "TechBridge Kit 신청",
            "TechBridge Kit申請",
            "申请 TechBridge Kit",
            "申請 TechBridge Kit",
            "Solicitar TechBridge Kit",
        ),
        "url": "https://deepx.ai/buy-now/dx-techbridge-kit/",
    },
]

path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print("Phase 3 cleanup applied to", path)
