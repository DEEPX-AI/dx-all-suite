"""A <br> inside a table cell separates values.

Dropping <br> runs two metrics in one cell together: dncnn_15 would show "PSNRSSIM" and "32.91530.9014",
face models "AP(Easy)AP(Med)AP(Hard)" and "89.289983.063854.075".
"""
from __future__ import annotations

from dx_modelzoo.metadata import _html_parser as hp


def test_values_on_separate_lines_of_a_cell_stay_apart():
    p = hp._TableParser()
    p.feed("<table><thead><tr><th>Metric</th><th>Accuracy</th></tr></thead>"
           "<tbody><tr><td>PSNR<br>SSIM</td><td>32.9153<br/>0.9014</td></tr></tbody></table>")
    cells = [c["text"] for c in p.rows[0]]
    assert cells == ["PSNR / SSIM", "32.9153 / 0.9014"]


def test_a_cell_without_a_break_is_unchanged():
    p = hp._TableParser()
    p.feed("<table><tbody><tr><td> mAP  50-95 </td></tr></tbody></table>")
    assert p.rows[0][0]["text"] == "mAP 50-95"
