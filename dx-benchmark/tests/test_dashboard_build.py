"""Tests for dashboard build-time cache-busting (Feature A).

The static dashboard embeds the dataset into index.html and links app.js /
styles.css as separate resources. Without cache-busting, a browser reuses the
cached copies after a rebuild, so a plain reload shows stale data (the reported
"BIOSTAR still visible" confusion). The builder stamps a content hash onto the
asset refs and emits a no-cache meta so a normal reload always reflects a rebuild.
"""
import re
from pathlib import Path

from benchmark.dashboard_builder import build_static_dashboard

_VER_RE = re.compile(r"(app\.js|styles\.css)\?v=([0-9a-f]{8})\b")


def _minimal_dataset(extra_run=None):
    runs = [{"env_id": "hwA", "run_id": "r1", "dx_all_suite_version": "v2.4.0"}]
    if extra_run:
        runs.append(extra_run)
    return {
        "meta": {"generated_at": "2026-07-23"},
        "environments": [{"env_id": "hwA", "latest_run_id": "r1"}],
        "runs": runs,
        "summaries": {"model": [], "e2e_single": [], "e2e_multi_capacity": [], "ort_delta": []},
        "history": {"model": [], "e2e_single": [], "e2e_multi_capacity": []},
        "snapshots": [],
    }


def test_asset_refs_are_cache_busted(tmp_path):
    build_static_dashboard(_minimal_dataset(), tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert "__ASSET_VER__" not in html, "build must replace the __ASSET_VER__ token"
    assert re.search(r"app\.js\?v=[0-9a-f]{8}", html), "app.js must carry a ?v=<hash>"
    assert re.search(r"styles\.css\?v=[0-9a-f]{8}", html), "styles.css must carry a ?v=<hash>"


def test_no_cache_meta_present(tmp_path):
    build_static_dashboard(_minimal_dataset(), tmp_path)
    html = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert re.search(r'http-equiv=["\']Cache-Control["\']', html, re.I), \
        "index.html must declare a Cache-Control no-cache meta so a plain reload revalidates"
    assert "no-cache" in html.lower()


def test_asset_version_is_deterministic(tmp_path):
    out1, out2 = tmp_path / "b1", tmp_path / "b2"
    build_static_dashboard(_minimal_dataset(), out1)
    build_static_dashboard(_minimal_dataset(), out2)
    v1 = _VER_RE.search((out1 / "index.html").read_text(encoding="utf-8")).group(2)
    v2 = _VER_RE.search((out2 / "index.html").read_text(encoding="utf-8")).group(2)
    assert v1 == v2, "identical input must yield identical asset hash (no git churn)"


def test_asset_version_tracks_dataset_content(tmp_path):
    out1, out2 = tmp_path / "b1", tmp_path / "b2"
    build_static_dashboard(_minimal_dataset(), out1)
    build_static_dashboard(
        _minimal_dataset(extra_run={"env_id": "hwB", "run_id": "r9", "dx_all_suite_version": "v2.4.0"}),
        out2,
    )
    v1 = _VER_RE.search((out1 / "index.html").read_text(encoding="utf-8")).group(2)
    v2 = _VER_RE.search((out2 / "index.html").read_text(encoding="utf-8")).group(2)
    assert v1 != v2, "changed dataset content must change the asset hash so browsers refetch"
