"""Model size ordering must be version-proof.

Model file naming has changed across releases (old ``yolo26n`` / ``yolo26n-cls``
vs new ``yolo26-n_640x640`` / ``yolo26-n_224x224``) and will keep changing.
Every stored result row stamps its own ``size`` field at measurement time, so
sorting MUST prefer that stamped field and treat name parsing as a tolerant
last-resort fallback only.
"""

from benchmark.reporter import _sort_models_by_size


OLD_NAMES = ["yolo26x.dxnn", "yolo26n.dxnn", "yolo26m.dxnn", "yolo26s.dxnn", "yolo26l.dxnn"]
NEW_NAMES = [
    "yolo26-x_640x640.dxnn",
    "yolo26-n_640x640.dxnn",
    "yolo26-m_640x640.dxnn",
    "yolo26-s_640x640.dxnn",
    "yolo26-l_640x640.dxnn",
]
EXPECTED_SUFFIX_ORDER = ["n", "s", "m", "l", "x"]


def _sizes(sorted_names):
    """Map each sorted name back to its size char for assertion (both schemes)."""
    import re
    out = []
    for n in sorted_names:
        m = re.search(r"yolo26-?([nslmx])", n)
        out.append(m.group(1) if m else "?")
    return out


def test_sort_stamped_size_wins_old_names():
    size_of = {"yolo26x.dxnn": "x", "yolo26n.dxnn": "n", "yolo26m.dxnn": "m",
               "yolo26s.dxnn": "s", "yolo26l.dxnn": "l"}
    assert _sizes(_sort_models_by_size(OLD_NAMES, size_of)) == EXPECTED_SUFFIX_ORDER


def test_sort_stamped_size_wins_new_names():
    size_of = {"yolo26-x_640x640.dxnn": "x", "yolo26-n_640x640.dxnn": "n",
               "yolo26-m_640x640.dxnn": "m", "yolo26-s_640x640.dxnn": "s",
               "yolo26-l_640x640.dxnn": "l"}
    assert _sizes(_sort_models_by_size(NEW_NAMES, size_of)) == EXPECTED_SUFFIX_ORDER


def test_sort_fallback_parses_old_names_without_size_map():
    # No size map (e.g. legacy row missing the field) → tolerant name parse.
    assert _sizes(_sort_models_by_size(OLD_NAMES)) == EXPECTED_SUFFIX_ORDER


def test_sort_fallback_parses_new_names_without_size_map():
    assert _sizes(_sort_models_by_size(NEW_NAMES)) == EXPECTED_SUFFIX_ORDER


def test_sort_mixed_old_and_new_names_via_fallback():
    mixed = ["yolo26-x_640x640.dxnn", "yolo26n.dxnn", "yolo26-m_640x640.dxnn", "yolo26s.dxnn"]
    assert _sizes(_sort_models_by_size(mixed)) == ["n", "s", "m", "x"]


def test_sort_unknown_name_sinks_to_end():
    names = ["mystery-model.dxnn", "yolo26-n_640x640.dxnn"]
    out = _sort_models_by_size(names)
    assert out[0] == "yolo26-n_640x640.dxnn"
    assert out[-1] == "mystery-model.dxnn"
