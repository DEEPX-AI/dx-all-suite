"""Session-summary metrics must surface which .deepx/toolsets were read."""
import json

from dx_transcripts.generate_transcripts import _session_metrics, _metrics_rows


def _stream(tmp_path, read_paths):
    lines = [{"type": "system", "subtype": "init", "model": "claude-opus-4-8"}]
    content = [{"type": "tool_use", "name": "Skill", "input": {"skill": "dx-skill-router"}}]
    content += [{"type": "tool_use", "name": "Read", "input": {"file_path": p}}
                for p in read_paths]
    lines.append({"type": "assistant", "message": {"role": "assistant", "content": content}})
    lines.append({"type": "result", "duration_ms": 1000, "total_cost_usd": 1.0,
                  "num_turns": 1, "usage": {"output_tokens": 10}})
    p = tmp_path / "s.jsonl"
    p.write_text("\n".join(json.dumps(x) for x in lines))
    return str(p)


def test_toolsets_collected_from_reads(tmp_path):
    s = _stream(tmp_path, [
        "/x/dx-compiler/.deepx/toolsets/ultralytics-train-eval.md",
        "/x/dx-compiler/.deepx/toolsets/ultralytics-deepx-export.md",
        "/x/dx-compiler/.deepx/skills/foo/SKILL.md",   # not a toolset → ignored
    ])
    m = _session_metrics(s)
    assert m["toolsets"] == ["ultralytics-train-eval", "ultralytics-deepx-export"]
    rows = dict(_metrics_rows(m))
    assert "ultralytics-train-eval" in rows["Toolsets"]


def test_kb_session_without_toolset_is_flagged(tmp_path):
    # skills used but NO toolset read (the pills case) → "none read", not omitted
    m = _session_metrics(_stream(tmp_path, []))
    assert m["toolsets"] == []
    rows = dict(_metrics_rows(m))
    assert rows["Toolsets"] == "— (none read)"
