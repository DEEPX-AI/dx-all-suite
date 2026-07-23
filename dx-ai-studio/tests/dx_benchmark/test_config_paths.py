"""Tests for benchmark result path configuration and legacy fallback."""

from unittest.mock import patch


def test_legacy_core_results_is_read_only_fallback():
    import dx_benchmark.server as server
    assert hasattr(server, "LEGACY_RESULTS_DIR")
    assert server.LEGACY_RESULTS_DIR.name == "results"
    assert server.LEGACY_RESULTS_DIR.parent.name == "dx_benchmark"


def test_iter_result_dirs_yields_canonical_first():
    """iter_result_dirs() yields RESULTS_DIR first."""
    import dx_benchmark.server as server
    dirs = list(server.iter_result_dirs())
    assert dirs[0] == server.RESULTS_DIR


def test_iter_result_dirs_yields_legacy_only_if_exists(tmp_path):
    """iter_result_dirs() yields LEGACY_RESULTS_DIR only when it exists on disk."""
    import dx_benchmark.server as server
    fake_canonical = tmp_path / "results"
    fake_canonical.mkdir()
    fake_legacy = tmp_path / "core" / "results"
    # legacy does not exist
    with patch.object(server, "RESULTS_DIR", fake_canonical), \
         patch.object(server, "LEGACY_RESULTS_DIR", fake_legacy):
        dirs = list(server.iter_result_dirs())
        assert dirs == [fake_canonical]

    # legacy exists
    fake_legacy.mkdir(parents=True)
    with patch.object(server, "RESULTS_DIR", fake_canonical), \
         patch.object(server, "LEGACY_RESULTS_DIR", fake_legacy):
        dirs = list(server.iter_result_dirs())
        assert dirs == [fake_canonical, fake_legacy]


# NOTE: runtime aggregation (_aggregate_all_result_dirs, _regenerate_dataset)
# was removed from dx_benchmark/server.py — the studio now serves the bundled
# dx_benchmark/dataset.json as-is (see tests/launcher/test_benchmark_endpoints.py).
# The aggregation-behavior tests that used to live here were dropped along
# with the functions they exercised.
