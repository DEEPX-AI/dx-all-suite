"""i18n contracts: category labels translate in all 6 langs, the title carries no phonetic
stub, and a few translations keep their natural wording."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
JS = ROOT / "dx_modelzoo" / "static" / "js"


def test_locallabel_falls_back_to_dict():
    # category data only ships label_en/label_ko; _localLabel must fall back to T(label_en)
    # so ja/zh/es categories translate (card + list + chips) instead of staying English.
    #
    # There must be exactly one definition: a same-named function without the fallback in a
    # later-loaded file would silently replace it, so the declaration site is pinned too
    # (global collisions in general are checked by tests/shared/test_static_script_scope.py).
    src = (JS / "app.js").read_text(encoding="utf-8")
    body = src.split("function _localLabel(", 1)[1].split("function ", 1)[0]
    assert "T(en)" in body, "_localLabel must dict-fall-back via T() for missing languages"
    for other in ("catalog.js", "detail.js"):
        assert "function _localLabel(" not in (JS / other).read_text(encoding="utf-8"), (
            f"{other} 가 _localLabel 을 다시 선언하면 app.js 의 폴백이 조용히 덮인다"
        )


def test_no_broken_zoo_transliteration():
    # The Korean title must not spell "Zoo" as a phonetic stub (the no-transliteration
    # rule); it keeps "Model Zoo" in English.
    src = (JS / "i18n-dict-catalog.js").read_text(encoding="utf-8")
    assert "DX 모델 주 탐색기" not in src
    assert "DX Model Zoo 탐색기" in src


def test_corrected_category_translations():
    src = (JS / "i18n-dict-shared.js").read_text(encoding="utf-8")
    assert "'zh-CN': '重识别'" in src        # ReID, not 重新识别 (re-recognize)
    assert "es: 'Superresolución'" in src    # one word, standard
    assert "es: 'Incrustación'" not in src   # Embedding must not be "physical inlay"


def test_accuracy_matrix_labels_localized():
    src = (JS / "detail.js").read_text(encoding="utf-8")
    assert "escapeHtml(T(label))" in src, "Accuracy-matrix row labels must go through T()"
