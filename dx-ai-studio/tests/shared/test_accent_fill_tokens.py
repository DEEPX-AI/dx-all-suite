"""흰 글자를 올리는 강조 채움은 --accent-fill 을 쓴다 (release audit 대비 점검).

어두운 테마의 --accent (#2997ff) 위 흰 글자는 3.0:1 이었다. 채움만 #0071e3 (4.7:1) 로, 밝은 테마는 --accent 그대로.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _luminance(hex_color):
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def test_dark_fill_carries_white_text_at_aa():
    tokens = (ROOT / "shared/static/dx-tokens.css").read_text(encoding="utf-8")
    fill = re.search(r"--accent-fill:(#[0-9a-fA-F]{6})", tokens).group(1)
    assert (1.05) / (_luminance(fill) + 0.05) >= 4.5


def test_light_theme_fill_follows_accent():
    light = (ROOT / "shared/static/dx-theme-light.css").read_text(encoding="utf-8")
    assert light.count("--accent-fill:var(--accent)") == 2


def test_white_text_primary_buttons_use_the_fill():
    css = {
        "shared/static/dx-demo-stage.css": [".dds-run", ".dds-fbtn.is-on"],
        "dx_agent_dev/static/css/console.css": ["#console-send"],
    }
    for path, selectors in css.items():
        src = (ROOT / path).read_text(encoding="utf-8")
        for sel in selectors:
            rule = re.search(re.escape(sel) + r"\s*\{([^}]*)\}", src).group(1)
            assert "var(--accent-fill)" in rule, (path, sel)
