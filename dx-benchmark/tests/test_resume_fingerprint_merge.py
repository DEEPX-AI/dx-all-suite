"""Resume-aware fingerprint scope merge.

environment.json is rewritten from only the current invocation's scope, while result
data accumulates across resumes. A partial/family-scoped resume must therefore UNION
the cumulative scope fields (benchmarked_models, families, video_infos) with the prior
fingerprint instead of overwriting them — otherwise the recorded scope shrinks below
what was actually benchmarked (the BIOSTAR `families=['multi']` / n-only bug).
"""

from benchmark.__main__ import _merge_fingerprint_scope


def _fp(models, families, vinfos):
    return {
        "benchmarked_models": [{"name": n, "size": s} for n, s in models],
        "benchmark_params": {"families": list(families)},
        "video_infos": dict(vinfos),
    }


def test_partial_family_resume_unions_scope():
    # prior: full suite (all sizes, model+e2e+multi); current: a multi-only n-scope re-run
    prior = _fp([("yolo26n.dxnn", "n"), ("yolo26s.dxnn", "s"), ("yolo26x.dxnn", "x")],
                ["model", "e2e", "multi"], {"od": {"fps": 30}})
    cur = _fp([("yolo26n.dxnn", "n")], ["multi"], {})
    _merge_fingerprint_scope(cur, prior)
    names = sorted(m["name"] for m in cur["benchmarked_models"])
    assert names == ["yolo26n.dxnn", "yolo26s.dxnn", "yolo26x.dxnn"]      # union, not shrunk
    assert cur["benchmark_params"]["families"] == ["model", "e2e", "multi"]  # canonical order
    assert cur["video_infos"] == {"od": {"fps": 30}}                      # prior group preserved


def test_current_entry_wins_on_name_conflict():
    prior = _fp([("yolo26n.dxnn", "n")], ["model"], {})
    cur = {"benchmarked_models": [{"name": "yolo26n.dxnn", "size": "n", "dxcom_version": "vNEW"}],
           "benchmark_params": {"families": ["model"]}, "video_infos": {}}
    _merge_fingerprint_scope(cur, prior)
    entries = [m for m in cur["benchmarked_models"] if m["name"] == "yolo26n.dxnn"]
    assert len(entries) == 1                          # no duplicate
    assert entries[0].get("dxcom_version") == "vNEW"  # fresh metadata kept


def test_no_prior_is_noop():
    cur = _fp([("yolo26n.dxnn", "n")], ["multi"], {})
    _merge_fingerprint_scope(cur, {})
    assert [m["name"] for m in cur["benchmarked_models"]] == ["yolo26n.dxnn"]
    assert cur["benchmark_params"]["families"] == ["multi"]
