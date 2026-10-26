"""The legacy table branch must use the in-house HTML parser's API.

`_parse_models()` looks for the 20-column layout (Q-Lite/Q-Pro group headers) first and otherwise falls back to a
loose legacy branch: "a table containing `.dxnn` links". That branch must not call `find_all("a", href=True)`,
which is BeautifulSoup syntax.

Node.find_all in `dx_app/core/_html_dom.py` is `find_all(self, names)`. `find(name, href=False)` in the same file
does take href, which makes it easy to assume find_all does too; reaching the branch then raises TypeError and the
page returns 500. The branch is reached whenever the 20-column detection fails, e.g. when a page switches to inline
JSON.
"""
from __future__ import annotations

import pytest

LEGACY_HTML = """
<html><body>
<h2>Object Detection</h2>
<table>
  <tr><th>Model</th><th>Download</th></tr>
  <tr>
    <td>yolov5s</td>
    <td>
      <a href="https://sdk.deepx.ai/modelzoo/yolov5s_512.dxnn">dxnn</a>
      <a href="https://sdk.deepx.ai/modelzoo/yolov5s_512.json">json</a>
    </td>
  </tr>
</table>
</body></html>
"""


def _parse():
    from dx_app.core.modelzoo import _parse_models

    return _parse_models(LEGACY_HTML)


def test_legacy_table_parses_without_raising():
    """A TypeError here makes the SETUP page return 500."""
    try:
        models = _parse()
    except TypeError as exc:  # pragma: no cover - reached only on a regression
        pytest.fail(f"legacy 분기가 자체 파서 문법을 어겼다: {exc}")
    assert models, "legacy 레이아웃에서 한 건도 못 읽었다"


def test_legacy_table_picks_up_both_urls():
    models = _parse()
    assert len(models) == 1
    model = models[0]
    assert model["name"] == "yolov5s"
    qlite = model.get("qlite", {})
    assert qlite.get("dxnn_url", "").endswith("yolov5s_512.dxnn")
    assert qlite.get("json_url", "").endswith("yolov5s_512.json")


def test_anchors_without_href_are_skipped():
    """An <a> without href must not crash the parser; that is what href=True guarded against."""
    from dx_app.core.modelzoo import _parse_models

    html = LEGACY_HTML.replace(
        "<td>\n      <a href=",
        "<td>\n      <a name=\"anchor\">pin</a>\n      <a href=",
    )
    models = _parse_models(html)
    assert len(models) == 1
    assert models[0]["qlite"]["dxnn_url"].endswith("yolov5s_512.dxnn")
