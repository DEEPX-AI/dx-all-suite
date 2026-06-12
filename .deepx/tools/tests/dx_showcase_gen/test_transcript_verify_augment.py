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


def test_metrics_from_stream_multiple_results(tmp_path):
    """A long/resumed `-p` session emits several result events: duration, turns and
    output_tokens are per-segment (summed); total_cost_usd is cumulative (last).
    Regression: using only the last result under-reported a 17-min build as its 3.5s
    final fragment (Wall-clock ~0.1 min, 1 turn)."""
    lines = [{"type": "system", "subtype": "init", "model": "claude-opus-4-8",
              "session_id": "abc"}]
    segs = [(720294, 70, 8.93, 49039), (320117, 38, 14.20, 20294), (3566, 1, 14.34, 162)]
    for dur, turns, cost, otok in segs:
        lines.append({"type": "result", "subtype": "success", "duration_ms": dur,
                      "num_turns": turns, "total_cost_usd": cost,
                      "usage": {"output_tokens": otok}})
    p = tmp_path / "multi.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in lines))
    m = transcript.metrics_from_stream(str(p))
    assert m["duration_ms"] == 720294 + 320117 + 3566        # summed (~17.4 min)
    assert m["num_turns"] == 70 + 38 + 1                     # summed
    assert m["output_tokens"] == 49039 + 20294 + 162         # summed
    assert m["total_cost_usd"] == 14.34                      # cumulative → last


def test_runsh_wraps_fork_demo(tmp_path):
    rs = tmp_path / "run.sh"
    # wrapping the fork's demo → flagged (FAIL the gate)
    rs.write_text("#!/bin/bash\ncd RapidDoc\npython demo/demo_offline.py in.pdf --finegrained\n")
    assert verify.runsh_wraps_fork_demo(rs) is True
    # a generated standalone entry → OK
    rs.write_text("#!/bin/bash\nsource deepx_scripts/set_env.sh 1 2 1 3 2 4\npython pdf_to_markdown.py --input x.pdf\n")
    assert verify.runsh_wraps_fork_demo(rs) is False
    # absent → skipped
    assert verify.runsh_wraps_fork_demo(tmp_path / "nope.sh") is None


def test_inject_metrics_merges_store_tokens_with_stream_cost(tmp_path):
    """A -p stream's result.usage under-reports total output on multi-segment builds; the
    session store has accurate per-message tokens/turns but no cost/wall. _inject_metrics
    must merge: store → output_tokens/turns, stream → cost/wall."""
    from dx_transcripts.generate_transcripts import _inject_metrics
    # stream: 2 result segments (final-result usage only → undercount) + cumulative cost
    stream = tmp_path / "stream.jsonl"
    stream.write_text("\n".join(json.dumps(x) for x in [
        {"type": "system", "subtype": "init", "model": "claude-opus-4-8"},
        {"type": "result", "subtype": "success", "duration_ms": 400000, "num_turns": 44,
         "total_cost_usd": 4.19, "usage": {"output_tokens": 38861}},
        {"type": "result", "subtype": "success", "duration_ms": 311000, "num_turns": 17,
         "total_cost_usd": 6.18, "usage": {"output_tokens": 12969}},
    ]))
    # store: per-message usage (accurate total) — 3 assistant msgs, 148,000 output
    store = tmp_path / "store.jsonl"
    store.write_text("\n".join(json.dumps(x) for x in [
        {"type": "assistant", "message": {"role": "assistant", "model": "claude-opus-4-8",
         "usage": {"output_tokens": 100000}, "content": [{"type": "text", "text": "a"}]}},
        {"type": "assistant", "message": {"role": "assistant",
         "usage": {"output_tokens": 40000}, "content": [{"type": "text", "text": "b"}]}},
        {"type": "assistant", "message": {"role": "assistant",
         "usage": {"output_tokens": 8000}, "content": [{"type": "text", "text": "c"}]}},
    ]))
    md = tmp_path / "out.md"; md.write_text("# T\n\nbody\n")
    written = {"md": str(md), "html": None}
    _inject_metrics(written, str(stream), store_jsonl=str(store))
    body = md.read_text()
    assert "148,000" in body          # store output_tokens (NOT the stream's 51,830)
    assert "| Agent turns | 3 |" in body   # store turn count (NOT 61)
    assert "$6.18" in body            # stream cumulative cost (store has none)
    assert "~11.8 min" in body        # stream wall (711000ms → ~11.8), store has none


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
