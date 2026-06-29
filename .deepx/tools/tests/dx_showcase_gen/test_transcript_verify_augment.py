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


def test_runsh_model_discovery_broken_flags_empty_default_in_assets_path(tmp_path):
    from dx_showcase_gen import verify
    run = tmp_path / "run.sh"
    run.write_text('MODEL=""\nfor c in "${DX_APP_ROOT:-}/assets/models/yolo26n-pose.dxnn"; do :; done\n')
    assert verify.runsh_model_discovery_broken(run) is True

def test_runsh_model_discovery_ok_for_suite_root_path(tmp_path):
    from dx_showcase_gen import verify
    run = tmp_path / "run.sh"
    run.write_text('RUNTIME_DIR="$SUITE_ROOT/dx-runtime"\n'
                   'DEFAULT_MODEL="$RUNTIME_DIR/dx_app/assets/models/yolo26n-pose.dxnn"\n')
    assert verify.runsh_model_discovery_broken(run) is False

def test_runsh_model_discovery_none_when_absent(tmp_path):
    from dx_showcase_gen import verify
    assert verify.runsh_model_discovery_broken(tmp_path / "nope.sh") is None

def test_setupsh_local_venv_without_bridge_flags_missing_pth(tmp_path):
    from dx_showcase_gen import verify
    s = tmp_path / "setup.sh"
    s.write_text('python3 -m venv "$LOCAL_VENV"\npip install opencv-python numpy\n'
                 'python -c "import dx_engine" || { echo FATAL; exit 1; }\n')
    assert verify.setupsh_local_venv_without_bridge(s) is True

def test_setupsh_local_venv_with_bridge_ok(tmp_path):
    from dx_showcase_gen import verify
    s = tmp_path / "setup.sh"
    s.write_text('python3 -m venv "$LOCAL_VENV"\n'
                 'echo "$RT_SP" > "$VENV_SP/dx_runtime_bridge.pth"\n')
    assert verify.setupsh_local_venv_without_bridge(s) is False

def test_setupsh_reusing_runtime_venv_ok(tmp_path):
    from dx_showcase_gen import verify
    s = tmp_path / "setup.sh"
    s.write_text('source "$RUNTIME_VENV/bin/activate"\npip install opencv-python\n')
    assert verify.setupsh_local_venv_without_bridge(s) is False

def test_scan_nonportable_flags_absolute_path_in_json(tmp_path):
    from dx_showcase_gen import artifacts
    (tmp_path / "train_result.json").write_text(
        '{"best_pt": "/data/home/x/dx-all-suite-ultralytics/dx-compiler/'
        'dx-agent-dev/20260611-101032_x/runs/train/weights/best.pt"}')
    flags = artifacts.scan_nonportable(str(tmp_path))
    assert any(f["file"].endswith("train_result.json") for f in flags)


def test_verify_showcase_fails_on_relocatability_regressions(tmp_path):
    from dx_showcase_gen import verify
    sc = tmp_path / "dx-agent-dev-showcase" / "bad"
    sc.mkdir(parents=True)
    (sc / "run.sh").write_text('for c in "${DX_APP_ROOT:-}/assets/models/m.dxnn"; do :; done\n')
    (sc / "setup.sh").write_text('python3 -m venv "$LOCAL_VENV"\n')
    (sc / "train_result.json").write_text('{"best_pt":"/data/home/x/dx-agent-dev/20260611-101032_x/best.pt"}')
    rep = verify.verify_showcase(str(sc), require_files=["run.sh", "setup.sh"])
    names = {c.name: c.ok for c in rep.checks}
    assert names.get("run.sh model discovery (dx_app asset) resolvable") is False
    assert names.get("setup.sh local venv bridges dx_engine") is False
    assert names.get("portable (no build-session/absolute paths)") is False


def test_scan_nonportable_strict_flags_build_session_path(tmp_path):
    from dx_showcase_gen import artifacts
    (tmp_path / "train_result.json").write_text(
        '{"best_pt": "/data/home/x/dx-all-suite-ultralytics/dx-compiler/'
        'dx-agent-dev/20260611-101032_x/runs/train/weights/best.pt"}')
    flags = artifacts.scan_nonportable(str(tmp_path), strict=True)
    assert any(f["file"].endswith("train_result.json") for f in flags)

def test_scan_nonportable_strict_ignores_dataset_and_worktree_paths(tmp_path):
    # a committed results.json that records a dataset val image + a current-worktree
    # output path — absolute but NOT a build-session dir → strict mode must NOT flag.
    from dx_showcase_gen import artifacts
    (tmp_path / "results.json").write_text(
        '{"source": "/data/home/dhyang/github/datasets/african-wildlife/images/val/x.jpg",'
        ' "output": "/data/home/dhyang/github/dx-all-suite-full-e2e/dx-agent-dev-showcase/wildlife/sample_detect.jpg"}')
    assert artifacts.scan_nonportable(str(tmp_path), strict=True) == []

def test_scan_nonportable_skips_ephemeral_venv_dir(tmp_path):
    # files inside .venv / venv / __pycache__ are run artifacts, never scanned (either mode).
    from dx_showcase_gen import artifacts
    venvf = tmp_path / ".venv" / "lib" / "site.py"
    venvf.parent.mkdir(parents=True)
    venvf.write_text('p = "/tmp/build-env-abc/bin/python"\n')
    assert artifacts.scan_nonportable(str(tmp_path), strict=True) == []
    assert artifacts.scan_nonportable(str(tmp_path)) == []  # broad mode skips it too

def test_scan_nonportable_broad_still_flags_home_paths(tmp_path):
    # broad (default) mode is unchanged — still flags a plain /data/home path in a script.
    from dx_showcase_gen import artifacts
    (tmp_path / "run.sh").write_text('M=/data/home/dhyang/x/model.dxnn\n')
    assert any(f["file"].endswith("run.sh") for f in artifacts.scan_nonportable(str(tmp_path)))
