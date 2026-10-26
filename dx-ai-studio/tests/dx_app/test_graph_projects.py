"""graph_projects: Graph Composer projects with versions in the Studio workspace (outputs/dx_app/graph/projects)."""
from __future__ import annotations

import pytest

from dx_app.core import config, graph_projects


@pytest.fixture(autouse=True)
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "OUTPUTS_DIR", tmp_path)
    return tmp_path


def _project(name="Person attributes", nodes=2):
    return {"schema": 1, "graph": {"version": 1, "name": "g", "nodes": [{"id": f"n{i}"} for i in range(nodes)],
                                   "edges": []},
            "layout": {"nodes": {"n0": {"x": 40, "y": 40}}}, "meta": {"name": name}}


def test_save_creates_a_project_named_after_it_then_adds_versions(workspace):
    body, code = graph_projects.save(_project())
    assert code == 200 and body == {"id": "person-attributes", "version": 1, "name": "Person attributes"}
    body2, _ = graph_projects.save(_project(nodes=3), "person-attributes")
    assert body2["version"] == 2
    (p,) = graph_projects.list_projects()
    assert (p["id"], p["version"], p["versions"]) == ("person-attributes", 2, 2)
    latest, _ = graph_projects.load("person-attributes")
    assert latest["version"] == 2 and len(latest["project"]["graph"]["nodes"]) == 3
    first, _ = graph_projects.load("person-attributes", "1")
    assert len(first["project"]["graph"]["nodes"]) == 2
    vs, _ = graph_projects.versions("person-attributes")
    assert [v["version"] for v in vs["versions"]] == [2, 1]
    assert (workspace / "graph" / "projects" / "person-attributes" / "versions" / "2.json").is_file()


def test_a_second_project_with_the_same_name_gets_its_own_id():
    assert graph_projects.save(_project())[0]["id"] == "person-attributes"
    assert graph_projects.save(_project())[0]["id"] == "person-attributes-2"


def test_only_the_newest_versions_are_kept(monkeypatch):
    monkeypatch.setattr(graph_projects, "MAX_VERSIONS", 3)
    for _ in range(5):
        graph_projects.save(_project(), "p")
    vs, _ = graph_projects.versions("p")
    assert [v["version"] for v in vs["versions"]] == [5, 4, 3]


@pytest.mark.parametrize("pid", ["../x", "a/b", "UPPER", ".hidden", "x" * 65])
def test_unsafe_ids_are_refused(pid):
    with pytest.raises(ValueError):
        graph_projects.load(pid)
    with pytest.raises(ValueError):
        graph_projects.delete(pid)
    with pytest.raises(ValueError):
        graph_projects.save(_project(), pid)


@pytest.mark.parametrize("project, message", [
    ({"schema": 2, "graph": {"nodes": []}}, "unsupported project schema"),
    ({"schema": 1, "graph": {"nodes": "x"}}, "the project graph is invalid"),
    ({"schema": 1, "graph": {"nodes": []}, "meta": []}, "layout and meta must be objects"),
    ({"schema": 1, "graph": {"nodes": [], "pad": "x" * (1024 * 1024)}}, "the project is too large"),
])
def test_invalid_projects_are_refused(project, message):
    body, code = graph_projects.save(project)
    assert code == 400 and body["error"] == message


def test_delete_and_missing_projects():
    graph_projects.save(_project(), "p")
    assert graph_projects.delete("p") == ({"ok": True, "id": "p"}, 200)
    assert graph_projects.load("p")[1] == 404
    assert graph_projects.delete("p")[1] == 404
    assert graph_projects.list_projects() == []


# Review fixes: a damaged project says so; a project folder that is a link is never followed.
@pytest.mark.parametrize("text", ["{not json", "[1, 2]", ""])
def test_a_corrupt_project_file_is_reported_as_corrupt(text):
    graph_projects.save(_project(), "p")
    (graph_projects.projects_dir() / "p" / "project.json").write_text(text)
    body, code = graph_projects.load("p")
    assert (code, body["error_key"]) == (422, "project_corrupt")
    (graph_projects.projects_dir() / "p" / "versions" / "1.json").write_text(text)
    assert graph_projects.load("p", "1")[1] == 422
    assert graph_projects.list_projects() == []


def test_a_linked_project_folder_is_refused_and_its_target_kept(tmp_path):
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    (elsewhere / "project.json").write_text('{"schema": 1, "graph": {"nodes": []}, "meta": {"name": "x"}}')
    graph_projects.projects_dir().mkdir(parents=True)
    (graph_projects.projects_dir() / "linked").symlink_to(elsewhere, target_is_directory=True)
    assert graph_projects.list_projects() == []
    for call in (lambda: graph_projects.load("linked"), lambda: graph_projects.versions("linked"),
                 lambda: graph_projects.delete("linked"), lambda: graph_projects.save(_project(), "linked")):
        with pytest.raises(ValueError):
            call()
    assert (elsewhere / "project.json").is_file()


def test_a_linked_project_file_is_not_read(tmp_path):
    graph_projects.save(_project(), "p")
    secret = tmp_path / "secret.json"
    secret.write_text('{"schema": 1, "graph": {"nodes": []}, "meta": {"name": "secret"}}')
    f = graph_projects.projects_dir() / "p" / "project.json"
    f.unlink()
    f.symlink_to(secret)
    assert graph_projects.load("p")[1] == 422


def test_reading_creates_no_folder(workspace):
    """Opening the page lists projects; only a save may create outputs/dx_app/graph/projects."""
    assert graph_projects.list_projects() == []
    assert graph_projects.load("p")[1] == 404 and graph_projects.versions("p")[1] == 404
    assert graph_projects.delete("p")[1] == 404
    assert not (workspace / "graph").exists()
    graph_projects.save(_project())
    assert (workspace / "graph" / "projects" / "person-attributes" / "project.json").is_file()
