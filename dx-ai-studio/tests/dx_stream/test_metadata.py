"""metadata.py — the parse_model wrapper contract.

get_model_metadata shells out to dx_rt's `cli.parse_model` twice: once for the
human-readable dump, once with -j to drop JSON files into a temp dir. Both calls
are wrapped in bare excepts, so a regression here fails SILENTLY — the studio
just shows empty metadata. These tests pin the contract with a fake subprocess
so they run without dx_rt installed.
"""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_stream"))


class _FakeCompleted:
    def __init__(self, stdout="", stderr=""):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = 0


@pytest.fixture()
def fake_runtime(monkeypatch):
    """Patch the dx_rt lookups so no real runtime is needed.

    The returned module also carries .set_run(fn): ALWAYS install the fake through
    it. `metadata.subprocess` is the real global subprocess module, so a plain
    `M.subprocess.run = fn` would replace subprocess.run process-wide for the rest
    of the session and never restore it.
    """
    from core import metadata as M

    monkeypatch.setattr(M, "dx_rt_cli_python", lambda: "/fake/python")
    monkeypatch.setattr(M, "dx_rt_cli_pythonpath", lambda: Path("/fake/pythonpath"))
    M.set_run = lambda fn: monkeypatch.setattr(M.subprocess, "run", fn)
    return M


@pytest.fixture()
def model_file(tmp_path):
    p = tmp_path / "model.dxnn"
    p.write_bytes(b"DXNN\x00")
    return p


class TestMetadataModule:
    def test_module_importable(self):
        from core.metadata import get_model_metadata
        assert callable(get_model_metadata)

    def test_missing_file_reports_the_path_and_never_shells_out(self, monkeypatch):
        from core import metadata as M

        def _boom(*a, **k):  # pragma: no cover - must never run
            raise AssertionError("subprocess.run called for a nonexistent model")

        monkeypatch.setattr(M.subprocess, "run", _boom)
        result = M.get_model_metadata("/nonexistent/model.dxnn")
        assert result["error"] == "Model file not found: /nonexistent/model.dxnn"


class TestRawOutput:
    def test_raw_output_concatenates_stdout_then_stderr(self, fake_runtime, model_file):
        M = fake_runtime
        M.set_run(lambda *a, **k: _FakeCompleted("OUT", "ERR"))
        assert M.get_model_metadata(str(model_file))["raw_output"] == "OUTERR"

    def test_subprocess_failure_is_reported_not_raised(self, fake_runtime, model_file):
        """A dx_rt that is missing/broken must degrade to a message, not a 500."""
        M = fake_runtime
        M.set_run(lambda *a, **k: (_ for _ in ()).throw(OSError("dx_rt is gone")))
        result = M.get_model_metadata(str(model_file))
        assert result["raw_output"].startswith("[ERROR]")
        assert "dx_rt is gone" in result["raw_output"]
        # The JSON pass shares the same broken runtime, so the keys must still exist.
        assert result["graph_info"] is None
        assert result["rmap_info"] == []

    def test_pythonpath_and_timeout_are_passed_to_the_child(self, fake_runtime, model_file):
        """PYTHONPATH is how cli.parse_model is found at all, and the timeout is what
        stops a hung parse from taking the module server down with it."""
        M = fake_runtime
        seen = []
        M.set_run(lambda *a, **k: (seen.append(k), _FakeCompleted())[1])
        M.get_model_metadata(str(model_file))
        assert seen, "subprocess.run was never called"
        for kwargs in seen:
            assert kwargs["env"]["PYTHONPATH"] == "/fake/pythonpath"
            assert kwargs["timeout"] == 30


class TestJsonExtraction:
    @staticmethod
    def _writer(files: dict):
        """Fake runner that drops *files* into the -j call's cwd."""
        def _run(cmd, **kwargs):
            if "-j" in cmd:
                for name, payload in files.items():
                    target = Path(kwargs["cwd"]) / name
                    target.write_text(
                        payload if isinstance(payload, str) else json.dumps(payload)
                    )
            return _FakeCompleted()
        return _run

    def test_graph_info_file_populates_graph_info(self, fake_runtime, model_file):
        M = fake_runtime
        M.set_run(self._writer({"model_graph_info.json": {"layers": 7}}))
        assert M.get_model_metadata(str(model_file))["graph_info"] == {"layers": 7}

    def test_rmap_info_files_accumulate_in_order_found(self, fake_runtime, model_file):
        M = fake_runtime
        M.set_run(self._writer({
            "a_rmap_info.json": {"idx": 1},
            "b_rmap_info.json": {"idx": 2},
        }))
        got = M.get_model_metadata(str(model_file))["rmap_info"]
        assert sorted(d["idx"] for d in got) == [1, 2]

    def test_unrelated_json_is_ignored(self, fake_runtime, model_file):
        """Only *graph_info* / *rmap_info* names are meaningful; anything else the
        CLI happens to emit must not be silently promoted into the payload."""
        M = fake_runtime
        M.set_run(self._writer({"something_else.json": {"x": 1}}))
        result = M.get_model_metadata(str(model_file))
        assert result["graph_info"] is None
        assert result["rmap_info"] == []

    def test_malformed_json_is_skipped_without_losing_the_good_one(self, fake_runtime, model_file):
        M = fake_runtime
        M.set_run(self._writer({
            "broken_graph_info.json": "{not json",
            "ok_rmap_info.json": {"idx": 9},
        }))
        result = M.get_model_metadata(str(model_file))
        assert result["graph_info"] is None          # the broken one is dropped
        assert result["rmap_info"] == [{"idx": 9}]   # the good one survives

    def test_temp_dir_is_cleaned_up(self, fake_runtime, model_file):
        """The JSON pass runs in a TemporaryDirectory; leaking one per call would
        slowly fill /tmp on a long-lived server."""
        M = fake_runtime
        seen = []
        M.set_run(lambda cmd, **k: (seen.append(k.get("cwd")), _FakeCompleted())[1])
        M.get_model_metadata(str(model_file))
        tmpdirs = [d for d in seen if d]
        assert tmpdirs, "the -j call must run inside a temp dir"
        for d in tmpdirs:
            assert not Path(d).exists(), f"temp dir leaked: {d}"
