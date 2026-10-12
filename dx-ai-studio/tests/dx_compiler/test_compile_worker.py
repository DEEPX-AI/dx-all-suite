"""compile_worker — the subprocess that runs dx_com inside the compiler venv.

The worker carries two behaviours that are invisible when they break:

  * event_to_dict parses the ONNX ModelProto to a graph dict HERE, because the
    proto cannot cross the process boundary as JSON. Without it the Prepared /
    Surgery / Partition / DXNN viewer tabs silently stay empty under subprocess
    mode.
  * every event line is prefixed with EVENT_PREFIX after a leading newline,
    because dx_com writes \\r-terminated tqdm bars to the SAME stdout — a raw
    JSON line would arrive glued to progress-bar noise and fail to parse.

No dx_com, onnx or venv is required: run_compile and stdin are faked.
"""
import io
import json

import pytest

from dx_compiler.core import compile_worker as W


class _Event:
    """Stand-in for dx_com's PhaseEvent."""

    def __init__(self, phase="", metadata=None, model=None):
        self.phase = phase
        if metadata is not None:
            self.metadata = metadata
        if model is not None:
            self.model = model


class TestEventToDict:
    def test_phase_is_stringified(self):
        class _Phase:
            def __str__(self):
                return "PREPARED"

        assert W.event_to_dict(_Event(phase=_Phase()))["phase"] == "PREPARED"

    def test_missing_attributes_do_not_raise(self):
        assert W.event_to_dict(object()) == {"phase": ""}

    def test_json_safe_metadata_passes_through(self):
        got = W.event_to_dict(_Event(metadata={"n": 1, "s": "x", "l": [1, 2]}))
        assert got["metadata"] == {"n": 1, "s": "x", "l": [1, 2]}

    def test_unserialisable_metadata_is_stringified_not_dropped(self):
        """A numpy array or an ONNX node in metadata must not take the whole
        event down — the parent still needs the phase."""
        class _Weird:
            def __repr__(self):
                return "<weird>"

        got = W.event_to_dict(_Event(phase="P", metadata={"ok": 1, "bad": _Weird()}))
        assert got["metadata"]["ok"] == 1
        assert got["metadata"]["bad"] == "<weird>"
        json.dumps(got)  # the whole payload must remain serialisable

    def test_empty_metadata_is_omitted(self):
        assert "metadata" not in W.event_to_dict(_Event(metadata={}))

    def test_model_is_parsed_into_a_graph(self, monkeypatch):
        import dx_compiler.core.onnx_parser as P

        monkeypatch.setattr(P, "parse_onnx_model", lambda m: {"nodes": [{"op": "Conv"}]})
        got = W.event_to_dict(_Event(phase="SURGERY", model=object()))
        assert got["has_model"] is True
        assert got["graph"] == {"nodes": [{"op": "Conv"}]}

    def test_parse_failure_is_recorded_and_never_aborts_the_compile(self, monkeypatch):
        import dx_compiler.core.onnx_parser as P

        def _boom(_):
            raise ValueError("bad proto")

        monkeypatch.setattr(P, "parse_onnx_model", _boom)
        got = W.event_to_dict(_Event(phase="SURGERY", model=object()))
        assert got["has_model"] is True
        assert got["graph_error"] == "bad proto"
        assert "graph" not in got


def _run_main(monkeypatch, capsys, stdin_text, run_compile=None):
    """Drive main() with fake stdin and a fake run_compile; return stdout events."""
    import dx_compiler.core.compiler_bridge as B

    monkeypatch.setattr("sys.stdin", io.StringIO(stdin_text))
    if run_compile is not None:
        monkeypatch.setattr(B, "run_compile", run_compile, raising=False)
    W.main()
    out = capsys.readouterr().out
    # split("\n"), NOT splitlines(): splitlines() also breaks on the \r that tqdm
    # emits, which would hide the very gluing this module guards against.
    return [json.loads(line[len(W.EVENT_PREFIX):])
            for line in out.split("\n") if line.startswith(W.EVENT_PREFIX)]


class TestMain:
    def test_invalid_stdin_json_exits_1_with_a_message(self, monkeypatch, capsys):
        monkeypatch.setattr("sys.stdin", io.StringIO("{not json"))
        with pytest.raises(SystemExit) as exc:
            W.main()
        assert exc.value.code == 1
        payload = json.loads(capsys.readouterr().out.strip())
        assert payload["type"] == "error" and "Invalid JSON input" in payload["message"]

    def test_event_survives_a_tqdm_progress_bar_on_the_same_stream(self, monkeypatch, capsys):
        """The failure this module guards against.

        dx_com writes tqdm bars to the SAME stdout using \r and NO trailing
        newline. Without the leading "\n" the worker prints, the marker lands
        glued to the bar ("50%\r__DXEVENT__{...}") and the parent — which splits
        on \n — never sees a line that startswith EVENT_PREFIX.
        """
        import sys as _sys

        def _run(**kwargs):
            _sys.stdout.write("compiling  50%\r")   # tqdm-style, no newline
            kwargs["event_queue"].put({"type": "phase", "phase": "PREPARED"})

        monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"output_dir": "/tmp/o"})))
        import dx_compiler.core.compiler_bridge as B
        monkeypatch.setattr(B, "run_compile", _run, raising=False)
        W.main()
        out = capsys.readouterr().out

        assert "compiling  50%\r" in out, "the fake progress bar did not reach stdout"
        marker_lines = [l for l in out.split("\n") if l.startswith(W.EVENT_PREFIX)]
        assert marker_lines, (
            "no line starts with EVENT_PREFIX — the event is glued to the tqdm bar "
            "and the parent cannot parse it"
        )
        assert json.loads(marker_lines[0][len(W.EVENT_PREFIX):]) == {
            "type": "phase", "phase": "PREPARED"}

    def test_non_dict_events_go_through_event_to_dict(self, monkeypatch, capsys):
        def _run(**kwargs):
            kwargs["event_queue"].put(_Event(phase="PARTITION"))

        events = _run_main(monkeypatch, capsys, json.dumps({"output_dir": "/tmp/o"}), _run)
        assert events[0]["phase"] == "PARTITION"

    def test_done_is_always_the_last_event(self, monkeypatch, capsys):
        def _run(**kwargs):
            kwargs["event_queue"].put({"type": "phase"})

        events = _run_main(monkeypatch, capsys, json.dumps({"output_dir": "/tmp/o"}), _run)
        assert events[-1] == {"type": "done"}

    def test_compile_failure_is_reported_with_a_traceback_then_done(self, monkeypatch, capsys):
        """A crash inside the venv must reach the parent as an event, not die
        silently in a daemon thread."""
        def _run(**kwargs):
            raise RuntimeError("dx_com exploded")

        events = _run_main(monkeypatch, capsys, json.dumps({"output_dir": "/tmp/o"}), _run)
        err = [e for e in events if e.get("type") == "error"]
        assert err and err[0]["message"] == "dx_com exploded"
        assert "RuntimeError" in err[0]["traceback"]
        assert events[-1] == {"type": "done"}

    def test_params_are_forwarded_with_documented_defaults(self, monkeypatch, capsys):
        seen = {}

        def _run(**kwargs):
            seen.update(kwargs)

        _run_main(monkeypatch, capsys,
                  json.dumps({"model": "/m.onnx", "config": "/c.json",
                              "output_dir": "/out", "opt_level": 3}), _run)
        assert seen["model"] == "/m.onnx"
        assert seen["config"] == "/c.json"
        assert seen["output_dir"] == "/out"
        assert seen["opt_level"] == 3
        # Unspecified flags must default off — a stray True here would silently
        # change what the compiler does.
        for flag in ("aggressive_partitioning", "gen_log", "quant_debug",
                     "quant_diagnosis", "use_q_pro"):
            assert seen[flag] is False
        assert seen["pause_for_selection"] is False, "the worker is non-interactive"
        assert seen["event_queue"] is not None
