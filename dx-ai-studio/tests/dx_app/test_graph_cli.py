"""graph_cli: finding the graph binaries, their environment, and what the build supports (recorded CLI output)."""
from __future__ import annotations

import pytest

from dx_app.core import graph_cli
from tests.dx_app import graph_fakes


def test_the_binary_is_found_in_the_search_dirs(tmp_path, monkeypatch):
    d = graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    assert graph_cli.binary("sync") == d / "multi_model_graph_sync"
    assert graph_cli.binary("async") == d / "multi_model_graph_async"


def test_a_missing_binary_is_reported(tmp_path, monkeypatch):
    monkeypatch.setattr(graph_cli, "_search_dirs", lambda: [tmp_path])
    assert graph_cli.binary("sync") is None
    with pytest.raises(graph_cli.GraphCliMissing):
        graph_cli.run(["--help"])


def test_the_environment_turns_progress_on_and_qt_off_screen():
    env = graph_cli.env()
    assert env["DXAPP_PROGRESS"] == "1"
    assert env["QT_QPA_PLATFORM"] == "offscreen"
    assert "LD_LIBRARY_PATH" in env


def test_todays_dx_app_has_neither_json_nor_the_engine_key(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    assert graph_cli.capabilities() == {"json": False, "engine_key": False, "report_timing": False,
                                        "list_ops": False, "events": False, "loop": False, "draw": False,
                                        "output_layers": False}


def test_the_planned_dx_app_has_both(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.JSON_CLI)
    assert graph_cli.capabilities() == {"json": True, "engine_key": True, "report_timing": True,
                                        "list_ops": False, "events": False, "loop": False, "draw": False,
                                        "output_layers": False}


def test_the_phase_2_dx_app_lists_ops_writes_events_and_loops(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.P2_CLI)
    assert graph_cli.capabilities() == {"json": True, "engine_key": True, "report_timing": True,
                                        "list_ops": True, "events": True, "loop": True, "draw": False,
                                        "output_layers": False}


def test_the_results_dx_app_draws_chosen_nodes_and_writes_layers(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.LAYERS_RUNNER)
    caps = graph_cli.capabilities()
    assert caps["draw"] is True and caps["output_layers"] is True and caps["events"] is True


def test_a_flag_is_found_only_as_a_whole_word(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, 'echo "  --events-dir <d>   --loop-count <n>"; exit 0')
    caps = graph_cli.capabilities()
    assert caps["events"] is False and caps["loop"] is False


def test_capabilities_are_probed_once_per_binary(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.TEXT_CLI)
    graph_cli.capabilities()
    n = len(graph_fakes.calls(tmp_path))
    graph_cli.capabilities()
    assert len(graph_fakes.calls(tmp_path)) == n == 2      # --help and one --check probe
    assert not list(tmp_path.glob("probe*.json")), "the probe graph is removed"


# Review fixes: an async-only build is still a graph build; "engine" support needs a positive answer.
def test_an_async_only_build_is_probed_and_used(tmp_path, monkeypatch):
    graph_fakes.install(tmp_path, monkeypatch, graph_fakes.JSON_CLI, variants=("async",))
    assert graph_cli.available() == ("async", tmp_path / "bin" / "multi_model_graph_async")
    assert graph_cli.capabilities()["json"] is True and graph_cli.capabilities()["engine_key"] is True


def test_no_build_at_all(tmp_path, monkeypatch):
    monkeypatch.setattr(graph_cli, "_search_dirs", lambda: [tmp_path])
    assert graph_cli.available() is None
    assert graph_cli.capabilities() == graph_cli.no_capabilities()
    assert not any(graph_cli.no_capabilities().values())


@pytest.mark.parametrize("check, expected", [
    ('echo "OK: graph \\"studio-probe\\" is valid (2 nodes, 1 edges, 1 models)"; exit 0', True),
    ('echo \'{"ok": true, "errors": []}\'; exit 0', True),
    ('echo \'ERROR [MODEL_LOAD] node "m": not a loadable .dxnn\' >&2; exit 1', True),
    ('echo \'ERROR [GRAPH_SCHEMA] graph node[1] "m" "engine": unknown key "bufers"\' >&2; exit 1', False),
    ('exit 139', False),
    ('echo "segmentation fault" >&2; exit 1', False),
    ('exit 0', False),
])
def test_the_engine_key_needs_a_positive_answer(tmp_path, monkeypatch, check, expected):
    graph_fakes.install(tmp_path, monkeypatch, f'case "$1" in --help) exit 0 ;; --check) {check} ;; esac\nexit 2')
    assert graph_cli.capabilities()["engine_key"] is expected
