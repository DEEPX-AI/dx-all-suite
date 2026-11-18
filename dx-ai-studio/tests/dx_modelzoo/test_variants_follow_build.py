"""A C++ runner built after the catalog loaded is offered without restarting dx_modelzoo.

`variants` were detected once at catalog load, so after Setup → DX-APP Build the Model Zoo still showed
python-only paths for models that now had C++ runners (and Use Default took the Python path)."""
import os
import importlib


def test_variants_follow_the_build_dir(tmp_path, monkeypatch):
    cat = importlib.import_module("dx_modelzoo.core.catalog")
    build = tmp_path / "build"
    build.mkdir()
    monkeypatch.setattr(cat, "BUILD_DIR", build)
    seen = []
    monkeypatch.setattr(cat, "_detect_inference_variants",
                        lambda mid, c, mf="": seen.append(mid) or {"cpp": ["sync"]})
    fake = {"models": [{"id": "m1", "category": "c", "model_file": "", "variants": {"python": ["sync"]}}]}
    monkeypatch.setattr(cat, "_catalog_cache", fake)
    monkeypatch.setattr(cat, "_refresh_download_flags", lambda c: None)
    now = [1000.0]
    monkeypatch.setattr(cat.time, "time", lambda: now[0])
    monkeypatch.setattr(cat, "_flags_checked_at", 0.0)
    monkeypatch.setattr(cat, "_variants_sig", cat._build_signature())

    cat.get_catalog()
    assert fake["models"][0]["variants"] == {"python": ["sync"]} and not seen   # nothing built yet

    (build / "m1_sync").write_text("")            # build.sh drops a runner → dir mtime changes
    st = build.stat()
    os.utime(build, ns=(st.st_atime_ns, st.st_mtime_ns + 10**9))
    now[0] += 5
    cat.get_catalog()
    assert fake["models"][0]["variants"] == {"cpp": ["sync"]}
