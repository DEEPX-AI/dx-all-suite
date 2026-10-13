"""Card labels. English text is the key (Studio's T() dictionaries are keyed the same way); Studio's
"Save as HTML" sends the page's translations for these keys, dx_app cards use the keys as they are.

Contract: tests/dx_modelzoo/test_model_card_md.py, tests/dx_modelzoo/test_html_export.py
"""
from __future__ import annotations

import string

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


_FORMATTER = string.Formatter()


def _fields(text):
    """The replacement fields of text as (name, conversion, spec) tuples; None when it does not parse."""
    try:
        return [(name, conv, spec) for _lit, name, spec, conv in _FORMATTER.parse(text) if name is not None]
    except ValueError:
        return None


def _safe(key, value):
    """Every field in value is a bare placeholder of key: no conversion, no format spec (a width spec
    would let one request expand to any size), no positional, indexed or attribute access."""
    fields = _fields(value)
    if fields is None:
        return False
    allowed = {name for name, _conv, _spec in _fields(key)}
    return all(name in allowed and name.isidentifier() and conv is None and not spec for name, conv, spec in fields)


def clean_labels(raw):
    """Keep only known keys with short string values that use the key's own placeholders (the payload comes
    from a browser)."""
    if not isinstance(raw, dict):
        return {}
    return {k: v for k, v in raw.items()
            if k in _KEYS and isinstance(v, str) and 0 < len(v) <= MAX_LABEL and _safe(k, v)}


def t(labels, key, **values):
    text = (labels or {}).get(key, key)
    try:
        return text.format(**values)
    except Exception:  # noqa: BLE001 — a bad translation must never break the card; English is always valid
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
