"""Card labels. English text is the key (Studio's T() dictionaries are keyed the same way); Studio's
"Save as HTML" sends the page's translations for these keys, dx_app cards use the keys as they are.

Contract: tests/dx_modelzoo/test_model_card_md.py, tests/dx_modelzoo/test_html_export.py
"""
from __future__ import annotations

from dx_modelzoo.core.model_card import FILE_ROLES

LABELS = (
    "DX-APP example", "Download {tier} DXNN", "Theme", "Quick start",
    "Run from the dx_app root after ./install.sh and ./build.sh.", "Get the model", "Copy", "Copied",
    "Performance", "{fps} FPS and {fpsw} FPS/W on DX-M1, DX Model Zoo reference measurement.",
    "Throughput for this model is not published yet. Measure it on your board:", "Measure", "Accuracy",
    "Quantization", "{dataset} · difference vs Raw below each value.", "{tier} is {drop} points below Raw on {metric}.",
    "Measured on host boards", "Board", "Throughput FPS", "Single-stream FPS", "Latency ms",
    "DX AI Studio Benchmark, {when}, DX-RT without ORT. Throughput: 5 in-flight buffers. Single-stream: 1.",
    "DX AI Studio Benchmark, DX-RT without ORT. Throughput: 5 in-flight buffers. Single-stream: 1.",
    "Numbers from the DX AI Studio catalog; this model is not in the DX Model Zoo publish table.",
    "Model", "Task", "Dataset", "Metric", "Input", "Parameters", "Operations", "Family", "Downloads", "original model",
    "Files in this example", "C++ version of this example", "Python version of this example", "Source & License",
    "Check the upstream license before commercial use.",
    "Compile it yourself: DX-COM in dx-compiler, or DX AI Studio → Compiler.",
    "Generated from the DX Model Zoo publish table (as of {date}).",
    "Generated from the DX Model Zoo publish table.", "Board measurements: DX AI Studio Benchmark, {when}.",
    "Open this model in DX AI Studio → Model Zoo for live inference and the model graph.",
    "Not published in DX Model Zoo.", "{metric} · {tier}", "Output of the {tier} model on DX-M1 · input {sample}",
) + tuple(role for _suffix, role in FILE_ROLES)
_KEYS = frozenset(LABELS)
MAX_LABEL = 300


def clean_labels(raw):
    """Keep only known keys with short string values (the payload comes from a browser)."""
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items() if k in _KEYS and isinstance(v, str) and 0 < len(v) <= MAX_LABEL}


def t(labels, key, **values):
    text = (labels or {}).get(key, key)
    try:
        return text.format(**values)
    except (KeyError, IndexError, ValueError):
        return key.format(**values)


# ── sentences that depend on what the card knows (shared by the README and the HTML card) ─────────────────

def generated_note(card, labels=None):
    """The footer's source line; the date only when the publish table has one."""
    if card["asof"]:
        return t(labels, "Generated from the DX Model Zoo publish table (as of {date}).", date=card["asof"])
    return t(labels, "Generated from the DX Model Zoo publish table.")


def boards_footer(card, labels=None):
    """The footer's benchmark month, when the card has board rows with a known date."""
    boards = card["boards"]
    if boards["rows"] and boards["measured"]:
        return t(labels, "Board measurements: DX AI Studio Benchmark, {when}.", when=boards["measured"])
    return ""


def boards_note(card, labels=None):
    """The line under the board table; the month only when the run ids carry a valid date."""
    when = card["boards"]["measured"]
    if when:
        return t(labels, "DX AI Studio Benchmark, {when}, DX-RT without ORT. Throughput: 5 in-flight buffers. "
                         "Single-stream: 1.", when=when)
    return t(labels, "DX AI Studio Benchmark, DX-RT without ORT. Throughput: 5 in-flight buffers. Single-stream: 1.")


CATALOG_NUMBERS = "Numbers from the DX AI Studio catalog; this model is not in the DX Model Zoo publish table."
