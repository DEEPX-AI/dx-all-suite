"""Codex adapter: codex exec --json -C, cwd=harness, normalize fallback."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "dx_agent_dev"))


def test_codex_registered():
    from core.adapters import get_adapter
    from core.adapters.codex import CodexAdapter
    assert get_adapter("codex") is CodexAdapter


def test_codex_build_command(tmp_path):
    from core.adapters import make_adapter
    a = make_adapter("codex", model="gpt-5-codex")
    cmd = a.build_command("build x", tmp_path, ["/harness"])
    # cmd[0] may be unresolved (shutil.which("codex") is None offline), so check membership only
    assert "exec" in cmd and "build x" in cmd
    assert "--json" in cmd
    assert "-m" in cmd and "gpt-5-codex" in cmd
    assert "-C" in cmd
    # cwd-based tool: -C points at the harness root
    assert "/harness" in cmd


def test_codex_cwd_mode_harness(tmp_path):
    from core.adapters import make_adapter
    a = make_adapter("codex")
    assert a._resolve_cwd(tmp_path, ["/harness"]) == "/harness"
    assert a._resolve_cwd(tmp_path, []) == tmp_path


def test_codex_normalize_invalid_json_falls_back_to_message():
    """A line that fails to parse falls back to a message event."""
    from core.adapters.codex import CodexAdapter
    a = CodexAdapter()
    ev = a.normalize("not json at all")
    assert ev["type"] == "message"
    assert ev["text"] == "not json at all"


def test_provisional_codex_normalize_json_maps_message():
    """Provisional fixture (the event schema is not confirmed): assistant text becomes a message."""
    from core.adapters.codex import CodexAdapter
    import json
    a = CodexAdapter()
    ev = a.normalize(json.dumps({"type": "message", "text": "hi"}))
    assert ev["type"] in {"message", "command", "log"}
    assert "text" in ev
