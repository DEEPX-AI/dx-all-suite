"""Suffix matching between studio ids and generated catalog ids.

The generated catalog is built from the public ModelZoo, whose ids are spelled differently
from the studio's. A studio id comes from the dx_app example directory name (`yolo26_depth_n`);
the public one carries the resolution (`yolo26_depth_n_768x768`).

The `_GEN_ID_SUFFIXES` allowlist collapses only quant/instance suffixes. Leaving resolution out
is deliberate: `foo` and `foo_1280` can be different models, and collapsing blindly would attach
another model's metadata.

So the rule is "collapse a resolution suffix only when the candidate is unique". When ambiguous,
leave it empty.
"""
from __future__ import annotations


def _match(model_id, gen_map):
    """`core` is a top-level name dx_app also uses, so module-level imports shadow each other
    across a full collection (see _clear_top_level_core_imports in tests/server_helpers.py).
    Import lazily inside the test, as test_legal_enrich.py does."""
    from core.catalog import _match_generated

    return _match_generated(model_id, gen_map)


def _g(*ids):
    return {i: {"id": i} for i in ids}


def test_exact_id_wins():
    gm = _g("alexnet", "alexnet_q_pro")
    assert _match("alexnet", gm)["id"] == "alexnet"


def test_known_quant_suffix_still_matches():
    gm = _g("alexnet_q_lite")
    assert _match("alexnet", gm)["id"] == "alexnet_q_lite"


def test_unique_resolution_suffix_matches():
    """yolo26_depth_n -> yolo26_depth_n_768x768; without this match legal stays empty."""
    gm = _g("yolo26_depth_n_768x768", "unrelated_model")
    got = _match("yolo26_depth_n", gm)
    assert got is not None, "유일한 해상도 변종을 찾지 못했다"
    assert got["id"] == "yolo26_depth_n_768x768"


def test_ambiguous_resolution_suffixes_do_not_match():
    """Two candidates are not collapsed, so metadata of the wrong resolution is never attached."""
    gm = _g("foo_768x768", "foo_1280x1280")
    assert _match("foo", gm) is None


def test_non_resolution_suffix_is_not_collapsed():
    """A suffix that does not look like a resolution is not collapsed."""
    gm = _g("foo_large", "foo_v2")
    assert _match("foo", gm) is None


def test_no_candidate_returns_none():
    assert _match("missing", _g("other_224x224")) is None


def test_resolution_rule_does_not_shadow_exact_match():
    """An exact match wins even when resolution candidates exist."""
    gm = _g("foo", "foo_768x768")
    assert _match("foo", gm)["id"] == "foo"
