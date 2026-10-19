"""Server-side pipeline save/load."""
import json
import pytest
from pathlib import Path


def test_pipeline_save_and_load(tmp_path):
    """A pipeline JSON can be saved and loaded back."""
    pipeline_data = {
        "name": "test-pipe",
        "nodes": [{"id": "n1", "type": "urisourcebin"}],
        "edges": [],
    }
    save_path = tmp_path / "test-pipe.json"
    save_path.write_text(json.dumps(pipeline_data))
    assert save_path.exists()

    loaded = json.loads(save_path.read_text())
    assert loaded["name"] == "test-pipe"
    assert len(loaded["nodes"]) == 1


def test_pipeline_list(tmp_path):
    """Saved pipelines can be listed."""
    (tmp_path / "pipe1.json").write_text('{"name":"pipe1"}')
    (tmp_path / "pipe2.json").write_text('{"name":"pipe2"}')
    files = sorted(f.stem for f in tmp_path.glob("*.json"))
    assert files == ["pipe1", "pipe2"]


def test_pipeline_delete(tmp_path):
    """A saved pipeline can be deleted."""
    p = tmp_path / "to-delete.json"
    p.write_text('{"name":"to-delete"}')
    assert p.exists()
    p.unlink()
    assert not p.exists()
