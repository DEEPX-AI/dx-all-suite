"""Tests for transcript metrics, verify gate, and idempotent augmentation."""
import json
from pathlib import Path

import pytest

from dx_showcase_gen import augment, transcript, verify


def _stream(tmp_path, *, with_result=True, model="claude-opus-4-8"):
    """Minimal stream-json stdout capture: init + (optional) result event."""
    lines = [{"type": "system", "subtype": "init", "model": model,
              "session_id": "abc"}]
    if with_result:
        lines.append({"type": "result", "subtype": "success",
                      "duration_ms": 695451, "num_turns": 59,
                      "total_cost_usd": 2.41,
                      "usage": {"output_tokens": 29207}})
    p = tmp_path / "stream.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in lines))
    return str(p)


def test_metrics_from_stream_complete(tmp_path):
    m = transcript.metrics_from_stream(_stream(tmp_path))
    assert m["duration_ms"] == 695451
    assert m["total_cost_usd"] == 2.41
    assert m["model"] == "claude-opus-4-8"


def test_is_complete(tmp_path):
    assert transcript.is_complete(_stream(tmp_path, with_result=True))
    assert not transcript.is_complete(_stream(tmp_path, with_result=False))


def test_render_requires_complete(tmp_path):
    with pytest.raises(transcript.IncompleteTranscript):
        transcript.render(str(tmp_path / "out"),
                          stream_json=_stream(tmp_path, with_result=False))


def test_augment_idempotent(tmp_path):
    md = tmp_path / "README.md"
    md.write_text("# Title\n\n### Showcase 4: Foo\n\nbody\n")
    block_args = dict(path=str(md), anchor="### Showcase 4: Foo",
                      block=augment.gif_block("./x.gif", "cap"),
                      mk=augment.marker("foo"))
    assert augment.upsert_block(**block_args) is True
    once = md.read_text()
    # second run replaces, does not duplicate
    augment.upsert_block(**block_args)
    twice = md.read_text()
    assert once == twice
    assert twice.count("dx-showcase:foo:gif:start") == 1
    assert augment.has_marker(str(md), "foo")


def test_verify_flags_missing_and_wrong_model(tmp_path):
    sc = tmp_path / "sc"
    sc.mkdir()
    # only the md transcript, wrong model in stream
    (sc / "claude-code-session.md").write_text("x")
    rep = verify.verify_showcase(
        str(sc), stream_json=_stream(tmp_path, model="claude-sonnet-4-6"),
        expected_model="claude-opus-4-8", require_files=["run.sh"])
    names = {c.name: c.ok for c in rep.checks}
    assert names["model matches expected"] is False
    assert names["transcript files present"] is False      # html/jsonl missing
    assert names["artifact present: run.sh"] is False
    assert rep.passed is False
