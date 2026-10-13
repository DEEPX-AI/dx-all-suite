"""Save as HTML: the page sends its language and translated labels; the server renders the card.
Every card label is translated in all six languages exactly once across the module's dictionaries."""
import re
from pathlib import Path

from dx_modelzoo.core.model_card_labels import LABELS

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "dx_modelzoo" / "static" / "js"
LANGS = ("en", "ko", "ja", "es", "zh-CN", "zh-TW")
UNTRANSLATED = {"{metric} · {tier}"}          # symbols only


def _dict_keys(path):
    return re.findall(r"^  '((?:[^'\\]|\\.)+)':\s*\{", path.read_text(encoding="utf-8"), re.M)


def test_detail_uses_the_endpoint():
    src = (JS / "detail.js").read_text(encoding="utf-8")
    assert "_buildModelCardHtml" not in src and "_imageToDataUrl" not in src
    assert "/api/model_card/labels" in src and "'/api/model_card/' + encodeURIComponent(m.id)" in src
    assert "task_label" in src and "lang" in src


def test_every_label_is_translated_once():
    seen = {}
    for path in sorted(JS.glob("i18n-dict-*.js")):
        for key in _dict_keys(path):
            seen.setdefault(key.replace("\\'", "'"), []).append(path.name)
    missing = [k for k in LABELS if k not in UNTRANSLATED and k not in seen]
    assert not missing, missing
    twice = {k: v for k, v in seen.items() if len(v) > 1}
    assert not twice, twice


def test_the_modelcard_dict_has_all_languages():
    lines = [l for l in (JS / "i18n-dict-modelcard.js").read_text(encoding="utf-8").splitlines() if l.startswith("  '")]
    assert len(lines) >= 40
    for line in lines:
        for lang in LANGS:
            assert (f"'{lang}':" if "-" in lang else f" {lang}:") in line, (lang, line[:60])


def test_index_loads_the_modelcard_dict():
    assert "i18n-dict-modelcard.js" in (ROOT / "dx_modelzoo" / "templates" / "index.html").read_text(encoding="utf-8")
