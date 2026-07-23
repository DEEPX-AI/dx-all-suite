#!/usr/bin/env python3
"""Enhance about-data.json with user-centric sections (official sources only)."""
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


data["meta"] = {
    "lastVerified": "2026-06-21",
    "updateCadence": "quarterly",
    "sources": ["https://deepx.ai", "https://developer.deepx.ai"],
    "quarterlyChecklist": [
        "news.upcoming + news.past from deepx.ai/home and /category/news/",
        "investment.awards from home Award section",
        "developer.sdkRelease + modelZooSnapshot from developer portal",
        "technology.sdk.stats version from DX-All-Suite release notes",
        "company.timeline from our-story year blocks",
        "products specs from dx-m1 / dx-h1 product pages",
        "partners.distribution + ecosystem from official press only",
    ],
}

data["developer"] = {
    "title": L(
        "Developer Hub",
        "개발자 허브",
        "開発者ハブ",
        "开发者中心",
        "開發者中心",
        "Centro para desarrolladores",
    ),
    "subtitle": L(
        "Start with official tools — model catalog, SDK, hardware, and support.",
        "공식 도구로 시작하세요 — 모델 카탈로그, SDK, 하드웨어, 지원.",
        "公式ツールから始めましょう — モデルカタログ、SDK、ハードウェア、サポート。",
        "从官方工具开始 — 模型目录、SDK、硬件与支持。",
        "從官方工具開始 — 模型目錄、SDK、硬體與支援。",
        "Empiece con herramientas oficiales: catálogo, SDK, hardware y soporte.",
    ),
    "supportEmail": "tech_support@deepx.ai",
    "links": [
        {
            "id": "portal",
            "icon": "🌐",
            "label": L("Developer Portal", "개발자 포털", "開発者ポータル", "开发者门户", "開發者入口", "Portal de desarrolladores"),
            "desc": L("Docs, downloads, community", "문서·다운로드·커뮤니티", "ドキュメント・ダウンロード", "文档、下载与社区", "文件、下載與社群", "Documentación y descargas"),
            "url": "https://developer.deepx.ai/",
        },
        {
            "id": "modelzoo",
            "icon": "📦",
            "label": L("Model Zoo", "Model Zoo", "Model Zoo", "Model Zoo", "Model Zoo", "Model Zoo"),
            "desc": L("271+ verified ONNX models", "271+ 검증 ONNX 모델", "271+検証済みONNXモデル", "271+ 已验证 ONNX 模型", "271+ 已驗證 ONNX 模型", "271+ modelos ONNX verificados"),
            "url": "https://developer.deepx.ai/modelzoo/",
        },
        {
            "id": "dxnn",
            "icon": "⚙️",
            "label": L("DXNN SDK", "DXNN SDK", "DXNN SDK", "DXNN SDK", "DXNN SDK", "DXNN SDK"),
            "desc": L("ONNX → DX-COM → DX-RT pipeline", "ONNX → DX-COM → DX-RT 파이프라인", "ONNX → DX-COM → DX-RT", "ONNX → DX-COM → DX-RT 流程", "ONNX → DX-COM → DX-RT 流程", "Flujo ONNX → DX-COM → DX-RT"),
            "url": "https://deepx.ai/products/dxnn-sdk/",
        },
        {
            "id": "shop",
            "icon": "🛒",
            "label": L("Shop Hardware", "하드웨어 구매", "ハードウェア購入", "购买硬件", "購買硬體", "Comprar hardware"),
            "desc": L("Modules, kits, systems", "모듈·키트·시스템", "モジュール・キット", "模组、套件与系统", "模組、套件與系統", "Módulos, kits y sistemas"),
            "url": "https://deepx.ai/",
        },
        {
            "id": "techbridge",
            "icon": "🔬",
            "label": L("DX-TechBridge Kit", "DX-TechBridge Kit", "DX-TechBridge Kit", "DX-TechBridge Kit", "DX-TechBridge Kit", "DX-TechBridge Kit"),
            "desc": L("Evaluate chips before deployment", "배포 전 칩 평가", "導入前のチップ評価", "部署前芯片评估", "部署前晶片評估", "Evalúe chips antes del despliegue"),
            "url": "https://deepx.ai/buy-now/dx-techbridge-kit/",
        },
    ],
    "sdkRelease": {
        "version": "v2.3.0",
        "summary": L(
            "Runtime efficiency, security hardening, unified application architecture.",
            "런타임 효율, 보안 강화, 통합 애플리케이션 아키텍처.",
            "ランタイム効率、セキュリティ強化、統合アプリアーキテクチャ。",
            "运行时效率、安全加固与统一应用架构。",
            "執行階段效率、安全強化與統一應用架構。",
            "Eficiencia runtime, seguridad reforzada, arquitectura unificada.",
        ),
    },
    "modelZooSnapshot": {"count": "271+", "asOf": "2026-04-21"},
}

data["contact"] = {
    "email": "tech_support@deepx.ai",
    "portalUrl": "https://developer.deepx.ai/",
    "label": L("Technical Support", "기술 지원", "技術サポート", "技术支持", "技術支援", "Soporte técnico"),
}

data["products"]["useCases"] = [
    {"icon": "📹", "title": L("Edge Camera Systems", "엣지 카메라", "エッジカメラ", "边缘摄像系统", "邊緣攝影系統", "Cámaras en el borde"),
     "desc": L("Real-time surveillance without cloud latency", "클라우드 지연 없는 실시간 영상 분석", "クラウド遅延のないリアルタイム監視", "无云端延迟的实时安防", "無雲端延遲的即時安防", "Vigilancia en tiempo real sin latencia cloud")},
    {"icon": "🏭", "title": L("Smart Factory", "스마트 팩토리", "スマートファクトリー", "智能工厂", "智慧工廠", "Fábrica inteligente"),
     "desc": L("On-site quality control in harsh environments", "가혹 환경에서의 현장 품질 검사", "過酷環境でのオンサイト品質検査", "恶劣环境下的现场质检", "惡劣環境下的現場品檢", "Control de calidad in situ")},
    {"icon": "🤖", "title": L("Robotics", "로보틱스", "ロボティクス", "机器人", "機器人", "Robótica"),
     "desc": L("Extended battery life for autonomous missions", "자율 임무를 위한 배터리 수명 연장", "自律ミッション向け長時間バッテリー", "自主任务的长续航", "自主任務的長續航", "Misiones autónomas con mayor autonomía")},
    {"icon": "🏙️", "title": L("Smart Cities", "스마트 시티", "スマートシティ", "智慧城市", "智慧城市", "Ciudades inteligentes"),
     "desc": L("Local traffic and crowd analytics", "로컬 교통·군중 분석", "ローカル交通・群衆分析", "本地交通与人群分析", "本地交通與人群分析", "Analítica local de tráfico y multitudes")},
    {"icon": "🚗", "title": L("Smart Mobility", "스마트 모빌리티", "スマートモビリティ", "智能出行", "智能出行", "Movilidad inteligente"),
     "desc": L("ADAS without network dependency", "네트워크 독립 ADAS", "ネットワーク非依存ADAS", "不依赖网络的ADAS", "不依賴網路的ADAS", "ADAS sin dependencia de red")},
    {"icon": "🛸", "title": L("Drones", "드론", "ドローン", "无人机", "無人機", "Drones"),
     "desc": L("Lightweight vision AI for aerial control", "경량 비전 AI 비행 제어", "軽量ビジョンAI飛行制御", "轻量视觉AI飞行控制", "輕量視覺AI飛行控制", "Visión IA ligera para vuelo")},
    {"icon": "🖥️", "title": L("Edge Computing", "엣지 컴퓨팅", "エッジコンピューティング", "边缘计算", "邊緣運算", "Computación en el borde"),
     "desc": L("High inference with minimal power at the edge", "최소 전력의 고성능 엣지 추론", "最小電力の高性能エッジ推論", "边缘低功耗高性能推理", "邊緣低功耗高效能推理", "Inferencia de alto rendimiento en el borde")},
    {"icon": "🛍️", "title": L("Smart Retail", "스마트 리테일", "スマートリテール", "智能零售", "智慧零售", "Retail inteligente"),
     "desc": L("In-store analytics with privacy on-device", "온디바이스 프라이버시 매장 분석", "オンデバイスプライバシー店舗分析", "设备端隐私店内分析", "裝置端隱私店內分析", "Analítica en tienda con privacidad local")},
]

data["technology"]["sdk"]["startHere"] = {
    "url": "https://developer.deepx.ai/",
    "label": L("Start on Developer Portal", "Developer Portal에서 시작", "Developer Portalで開始", "前往开发者门户", "前往開發者入口", "Empezar en Developer Portal"),
}
data["technology"]["sdk"]["release"] = data["developer"]["sdkRelease"]

data["distribution"] = {
    "title": L("Where to Buy", "구매 채널", "購入チャネル", "购买渠道", "購買渠道", "Dónde comprar"),
    "channels": [
        {"name": "Digi-Key", "region": L("Global e-commerce", "글로벌 이커머스", "グローバルEC", "全球电商", "全球電商", "E-commerce global"), "url": "https://www.digikey.com/"},
        {"name": "Avnet Silica", "region": L("EMEA distribution", "EMEA 유통", "EMEA流通", "EMEA分销", "EMEA分銷", "Distribución EMEA"), "url": "https://www.avnet.com/"},
    ],
}

data["partners"]["alliance"] = {
    "title": L("Open-Source Physical AI Alliance", "오픈소스 Physical AI Alliance", "オープンソースPhysical AI Alliance", "开源 Physical AI 联盟", "開源 Physical AI 聯盟", "Alianza Physical AI open source"),
    "desc": L(
        "Native edge deployment paths for framework developers — Ultralytics YOLO (format=deepx) and Baidu PaddlePaddle.",
        "프레임워크 개발자용 네이티브 엣지 배포 — Ultralytics YOLO (format=deepx), Baidu PaddlePaddle.",
        "フレームワーク開発者向けネイティブエッジデプロイ — Ultralytics YOLO、Baidu PaddlePaddle。",
        "面向框架开发者的原生边缘部署 — Ultralytics YOLO 与 Baidu PaddlePaddle。",
        "面向框架開發者的原生邊緣部署 — Ultralytics YOLO 與 Baidu PaddlePaddle。",
        "Despliegue nativo en el borde para desarrolladores de frameworks.",
    ),
    "members": ["Ultralytics", "Baidu PaddlePaddle"],
}

data["partners"]["distribution"] = [
    {"name": "Digi-Key", "role": L("Global e-commerce", "글로벌 이커머스", "グローバルEC", "全球电商", "全球電商", "E-commerce global")},
    {"name": "Avnet Silica", "role": L("EMEA franchise", "EMEA 프랜차이즈", "EMEAフランチャイズ", "EMEA特许经营", "EMEA特許經營", "Franquicia EMEA")},
    {"name": "WPG", "role": L("Global distribution", "글로벌 유통", "グローバル流通", "全球分销", "全球分銷", "Distribución global")},
]

data["partners"]["ecosystem"] = [
    "Hyundai", "AWS", "Baidu", "LG U+", "POSCO DX", "Wind River",
    "Ultralytics", "AAEON", "Renesas", "Raspberry Pi", "Naver Cloud",
]

old_events = data["news"].get("events", [])
data["news"]["upcoming"] = [
    {
        "title": L("Manufacturing World Tokyo 2026 — Booth S14-16", "Manufacturing World Tokyo 2026 — 부스 S14-16", "Manufacturing World Tokyo 2026 — ブース S14-16", "Manufacturing World Tokyo 2026 — 展位 S14-16", "Manufacturing World Tokyo 2026 — 展位 S14-16", "Manufacturing World Tokyo 2026 — stand S14-16"),
        "date": "2026.07", "type": "event", "location": L("Tokyo Big Sight", "東京ビッグサイト", "東京ビッグサイト", "东京Big Sight", "東京Big Sight", "Tokyo Big Sight"),
    },
    {
        "title": L("Avnet Edge & Beyond Tech Days 2026", "Avnet Edge & Beyond Tech Days 2026", "Avnet Edge & Beyond Tech Days 2026", "Avnet Edge & Beyond Tech Days 2026", "Avnet Edge & Beyond Tech Days 2026", "Avnet Edge & Beyond Tech Days 2026"),
        "date": "2026.07", "type": "event", "location": L("Jul 10 – 24, 2026", "2026.07.10 – 24", "2026年7月10–24日", "2026年7月10–24日", "2026年7月10–24日", "10–24 jul 2026"),
    },
    {
        "title": L("COMPUTEX TAIPEI 2026", "COMPUTEX TAIPEI 2026", "COMPUTEX TAIPEI 2026", "COMPUTEX TAIPEI 2026", "COMPUTEX TAIPEI 2026", "COMPUTEX TAIPEI 2026"),
        "date": "2026.06", "type": "event", "location": L("Taipei Nangang Exhibition Center", "台北南港展覽館", "台北南港展示場", "台北南港展览馆", "台北南港展覽館", "Taipei Nangang"),
    },
    {
        "title": L("Webinar: DEEPX & Avnet Silica — Edge AI at GPU-level performance", "웨비나: DEEPX & Avnet Silica — GPU급 엣지 AI", "ウェビナー: DEEPX & Avnet Silica", "网络研讨会：DEEPX与Avnet Silica", "網路研討會：DEEPX與Avnet Silica", "Webinar: DEEPX y Avnet Silica"),
        "date": "2026.02", "type": "webinar", "location": L("Online", "온라인", "オンライン", "线上", "線上", "En línea"),
    },
]

data["news"]["past"] = old_events
data["news"].pop("events", None)

data["investment"]["showRounds"] = False

path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print("Enhanced", path)
